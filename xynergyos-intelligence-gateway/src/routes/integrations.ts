import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { tokenManager } from '../services/tokenManager';
import { logger } from '../utils/logger';
import * as crypto from 'crypto';

const router = Router();

// Apply authentication to all integration routes
router.use(authenticateRequest);

/**
 * Integration Management Routes
 *
 * Provides unified interface for managing OAuth integrations.
 * Wraps existing OAuth routes with frontend-expected API.
 */

// Available OAuth providers configuration
const AVAILABLE_PROVIDERS = [
  {
    id: 'slack',
    name: 'Slack',
    description: 'Connect your Slack workspace',
    category: 'communication',
    icon: 'slack',
    scopes: ['channels:read', 'channels:history', 'chat:write', 'users:read', 'search:read'],
    configured: !!process.env.SLACK_CLIENT_ID && !!process.env.SLACK_CLIENT_SECRET,
  },
  {
    id: 'gmail',
    name: 'Gmail',
    description: 'Connect your Gmail account',
    category: 'communication',
    icon: 'gmail',
    scopes: ['gmail.readonly', 'gmail.send', 'gmail.modify'],
    configured: !!process.env.GMAIL_CLIENT_ID && !!process.env.GMAIL_CLIENT_SECRET,
  },
  {
    id: 'calendar',
    name: 'Google Calendar',
    description: 'Connect your Google Calendar',
    category: 'productivity',
    icon: 'calendar',
    scopes: ['calendar', 'calendar.events'],
    configured: !!process.env.GMAIL_CLIENT_ID && !!process.env.GMAIL_CLIENT_SECRET,
  },
];

/**
 * GET /api/v1/integrations/available
 * List available OAuth providers
 */
router.get(
  '/available',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    logger.info('Fetching available integrations', {
      userId: req.user?.uid,
    });

    res.json({
      success: true,
      providers: AVAILABLE_PROVIDERS,
    });
  })
);

/**
 * GET /api/v1/integrations/list
 * List user's connected integrations
 */
router.get(
  '/list',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;

    logger.info('Fetching user integrations', { userId });

    try {
      const tokens = await tokenManager.listUserTokens(userId);

      const integrations = tokens.map((token) => ({
        id: `${userId}_${token.service}`,
        provider: token.service,
        status: 'connected',
        connected_at: token.expiresAt ? new Date(token.expiresAt.getTime() - 86400000).toISOString() : new Date().toISOString(),
        expires_at: token.expiresAt?.toISOString(),
        is_expired: token.expiresAt ? new Date() >= token.expiresAt : false,
      }));

      res.json({
        success: true,
        integrations,
      });
    } catch (error: any) {
      logger.error('Failed to list integrations', { error: error.message, userId });
      res.status(500).json({
        success: false,
        error: 'Failed to list integrations',
      });
    }
  })
);

/**
 * POST /api/v1/integrations/connect
 * Initiate OAuth flow for a provider
 *
 * Body: { provider: string, redirect_uri?: string }
 * Response: { authorization_url: string, state: string }
 */
router.post(
  '/connect',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const { provider, redirect_uri } = req.body;
    const userId = req.user!.uid;

    if (!provider) {
      return res.status(400).json({
        success: false,
        error: 'Provider is required',
      });
    }

    // Validate provider
    const providerConfig = AVAILABLE_PROVIDERS.find((p) => p.id === provider);
    if (!providerConfig) {
      return res.status(400).json({
        success: false,
        error: 'Invalid provider',
      });
    }

    if (!providerConfig.configured) {
      return res.status(503).json({
        success: false,
        error: `${providerConfig.name} OAuth not configured`,
      });
    }

    logger.info('Initiating OAuth flow', { userId, provider });

    const state = crypto.randomBytes(32).toString('hex');

    let authUrl: string;

    // Generate authorization URL based on provider
    switch (provider) {
      case 'slack': {
        const clientId = process.env.SLACK_CLIENT_ID;
        const callbackUri = redirect_uri || `${process.env.API_BASE_URL}/api/v1/integrations/callback`;
        const scopes = providerConfig.scopes.join(',');

        authUrl =
          `https://slack.com/oauth/v2/authorize?` +
          `client_id=${clientId}&` +
          `scope=${scopes}&` +
          `redirect_uri=${encodeURIComponent(callbackUri)}&` +
          `state=${state}&` +
          `user_scope=`;
        break;
      }

      case 'gmail':
      case 'calendar': {
        const clientId = process.env.GMAIL_CLIENT_ID;
        const callbackUri = redirect_uri || `${process.env.API_BASE_URL}/api/v1/integrations/callback`;
        const scopes = providerConfig.scopes.map((s) =>
          s.includes('://') ? s : `https://www.googleapis.com/auth/${s}`
        ).join(' ');

        authUrl =
          `https://accounts.google.com/o/oauth2/v2/auth?` +
          `client_id=${clientId}&` +
          `redirect_uri=${encodeURIComponent(callbackUri)}&` +
          `response_type=code&` +
          `scope=${encodeURIComponent(scopes)}&` +
          `access_type=offline&` +
          `prompt=consent&` +
          `state=${state}`;
        break;
      }

      default:
        return res.status(400).json({
          success: false,
          error: 'Provider not supported',
        });
    }

    res.json({
      success: true,
      authorization_url: authUrl,
      state,
      provider,
    });
  })
);

/**
 * GET /api/v1/integrations/callback
 * Handle OAuth callback
 *
 * Query: code, state, provider, redirect_uri, error
 * Response: { success: boolean, integration_id: string, provider: string }
 */
router.get(
  '/callback',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const { code, state, error: oauthError, provider: queryProvider } = req.query;

    // Determine provider from query or state
    const provider = queryProvider as string || 'slack'; // Default to slack for backward compatibility

    if (oauthError) {
      logger.error('OAuth callback error', { error: oauthError, provider });
      return res.redirect(`/settings/integrations?error=${oauthError}&provider=${provider}`);
    }

    if (!code) {
      return res.redirect(`/settings/integrations?error=no_code&provider=${provider}`);
    }

    // For now, delegate to the existing OAuth callback handlers
    // In a production system, you'd want to handle this more elegantly
    const callbackUrl = provider === 'slack'
      ? `/api/v1/oauth/slack/callback?code=${code}&state=${state}`
      : `/api/v1/oauth/${provider}/callback?code=${code}&state=${state}`;

    logger.info('OAuth callback received, forwarding', {
      provider,
      hasCode: !!code,
      hasState: !!state,
    });

    // Redirect to the provider-specific callback handler
    // This maintains backward compatibility with existing OAuth routes
    res.redirect(callbackUrl);
  })
);

/**
 * DELETE /api/v1/integrations/:id
 * Disconnect an integration
 *
 * Query: revoke_token (optional)
 * Response: { success: boolean }
 */
router.delete(
  '/:id',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const { id } = req.params;
    const { revoke_token } = req.query;
    const userId = req.user!.uid;

    // Integration ID format: {userId}_{service}
    const service = id.split('_').pop() as 'slack' | 'gmail' | 'calendar';

    if (!['slack', 'gmail', 'calendar'].includes(service)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid integration ID',
      });
    }

    logger.info('Disconnecting integration', {
      userId,
      service,
      integrationId: id,
      revokeToken: !!revoke_token,
    });

    try {
      // Delete token from Firestore
      await tokenManager.deleteToken(userId, service);

      // TODO: If revoke_token=true, make API call to revoke the token with the provider
      // For now, just deleting from our database is sufficient

      logger.info('Integration disconnected', { userId, service });

      res.json({
        success: true,
        message: `${service} disconnected successfully`,
      });
    } catch (error: any) {
      logger.error('Failed to disconnect integration', {
        error: error.message,
        userId,
        service,
      });
      res.status(500).json({
        success: false,
        error: 'Failed to disconnect integration',
      });
    }
  })
);

/**
 * POST /api/v1/integrations/sync/:provider
 * Trigger data sync for a provider
 *
 * Query: integration_id
 * Response: { success: boolean }
 */
router.post(
  '/sync/:provider',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const { provider } = req.params;
    const { integration_id } = req.query;
    const userId = req.user!.uid;

    logger.info('Sync requested', {
      userId,
      provider,
      integrationId: integration_id,
    });

    // Verify integration exists
    const hasToken = await tokenManager.hasValidToken(
      userId,
      provider as 'slack' | 'gmail' | 'calendar'
    );

    if (!hasToken) {
      return res.status(404).json({
        success: false,
        error: 'Integration not found or expired',
      });
    }

    // TODO: Implement actual sync logic based on provider
    // For now, just return success
    logger.info('Sync triggered', { userId, provider });

    res.json({
      success: true,
      message: `${provider} sync triggered`,
      sync_status: 'queued',
    });
  })
);

/**
 * GET /api/v1/integrations/:id/status
 * Get integration status
 */
router.get(
  '/:id/status',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const { id } = req.params;
    const userId = req.user!.uid;

    const service = id.split('_').pop() as 'slack' | 'gmail' | 'calendar';

    if (!['slack', 'gmail', 'calendar'].includes(service)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid integration ID',
      });
    }

    logger.info('Checking integration status', { userId, service });

    try {
      const hasToken = await tokenManager.hasValidToken(userId, service);

      res.json({
        success: true,
        status: hasToken ? 'connected' : 'disconnected',
        provider: service,
      });
    } catch (error: any) {
      logger.error('Failed to check integration status', {
        error: error.message,
        userId,
        service,
      });
      res.status(500).json({
        success: false,
        error: 'Failed to check integration status',
      });
    }
  })
);

export default router;
