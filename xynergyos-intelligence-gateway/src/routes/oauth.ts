import { Router, Request, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { tokenManager } from '../services/tokenManager';
import { logger } from '../utils/logger';
import * as crypto from 'crypto';

const router = Router();

// Apply authentication to all OAuth routes
router.use(authenticateRequest);

/**
 * Slack OAuth Flow
 */

// Step 1: Initiate Slack OAuth
router.get(
  '/slack/start',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const state = crypto.randomBytes(32).toString('hex');

    // Store state in session or temporary storage for CSRF protection
    // For now, we'll send it as a parameter

    const clientId = process.env.SLACK_CLIENT_ID;
    if (!clientId) {
      return res.status(503).json({
        success: false,
        error: 'Slack OAuth not configured',
      });
    }

    const redirectUri = `${process.env.API_BASE_URL}/api/v1/oauth/slack/callback`;

    const scopes = [
      'channels:read',
      'channels:history',
      'chat:write',
      'users:read',
      'search:read',
    ].join(',');

    const authUrl =
      `https://slack.com/oauth/v2/authorize?` +
      `client_id=${clientId}&` +
      `scope=${scopes}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `state=${state}&` +
      `user_scope=`;

    logger.info('Slack OAuth initiated', {
      userId: req.user?.uid,
      state,
    });

    res.json({
      success: true,
      data: {
        authUrl,
        state,
      },
    });
  })
);

// Step 2: Handle Slack OAuth callback
router.get(
  '/slack/callback',
  asyncHandler(async (req: Request, res: Response) => {
    const { code, state, error } = req.query;

    if (error) {
      logger.error('Slack OAuth error', { error });
      return res.redirect(`/oauth/error?service=slack&error=${error}`);
    }

    if (!code) {
      return res.redirect('/oauth/error?service=slack&error=no_code');
    }

    try {
      // Exchange code for token
      const response = await fetch('https://slack.com/api/oauth.v2.access', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          client_id: process.env.SLACK_CLIENT_ID!,
          client_secret: process.env.SLACK_CLIENT_SECRET!,
          code: code as string,
          redirect_uri: `${process.env.API_BASE_URL}/api/v1/oauth/slack/callback`,
        }),
      });

      const data = await response.json() as any;

      if (!data.ok) {
        logger.error('Slack token exchange failed', { error: data.error });
        return res.redirect(`/oauth/error?service=slack&error=${data.error}`);
      }

      // Extract user ID from the access token response
      // In a real implementation, get this from the authenticated session
      const userId = data.authed_user?.id || 'user_from_session';
      const tenantId = data.team?.id || 'default_tenant';

      // Store the token
      await tokenManager.storeToken(userId, tenantId, 'slack', data.access_token, {
        refreshToken: data.refresh_token,
        expiresIn: data.expires_in,
        scopes: data.scope?.split(',') || [],
        metadata: {
          teamId: data.team?.id,
          teamName: data.team?.name,
          botUserId: data.bot_user_id,
        },
      });

      logger.info('Slack OAuth completed', {
        userId,
        teamId: data.team?.id,
      });

      // Redirect to success page
      res.redirect('/oauth/success?service=slack');
    } catch (error) {
      logger.error('Slack OAuth callback error', { error });
      res.redirect('/oauth/error?service=slack&error=server_error');
    }
  })
);

/**
 * Gmail OAuth Flow
 */

// Step 1: Initiate Gmail OAuth
router.get(
  '/gmail/start',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const state = crypto.randomBytes(32).toString('hex');

    const clientId = process.env.GMAIL_CLIENT_ID;
    if (!clientId) {
      return res.status(503).json({
        success: false,
        error: 'Gmail OAuth not configured',
      });
    }

    const redirectUri = `${process.env.API_BASE_URL}/api/v1/oauth/gmail/callback`;

    const scopes = [
      'https://www.googleapis.com/auth/gmail.readonly',
      'https://www.googleapis.com/auth/gmail.send',
      'https://www.googleapis.com/auth/gmail.modify',
    ].join(' ');

    const authUrl =
      `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${clientId}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `response_type=code&` +
      `scope=${encodeURIComponent(scopes)}&` +
      `access_type=offline&` +
      `prompt=consent&` +
      `state=${state}`;

    logger.info('Gmail OAuth initiated', {
      userId: req.user?.uid,
      state,
    });

    res.json({
      success: true,
      data: {
        authUrl,
        state,
      },
    });
  })
);

// Step 2: Handle Gmail OAuth callback
router.get(
  '/gmail/callback',
  asyncHandler(async (req: Request, res: Response) => {
    const { code, state, error } = req.query;

    if (error) {
      logger.error('Gmail OAuth error', { error });
      return res.redirect(`/oauth/error?service=gmail&error=${error}`);
    }

    if (!code) {
      return res.redirect('/oauth/error?service=gmail&error=no_code');
    }

    try {
      // Exchange code for token
      const response = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          client_id: process.env.GMAIL_CLIENT_ID!,
          client_secret: process.env.GMAIL_CLIENT_SECRET!,
          code: code as string,
          redirect_uri: `${process.env.API_BASE_URL}/api/v1/oauth/gmail/callback`,
          grant_type: 'authorization_code',
        }),
      });

      const data = await response.json() as any;

      if (!data.access_token) {
        logger.error('Gmail token exchange failed', { error: data.error });
        return res.redirect(`/oauth/error?service=gmail&error=${data.error}`);
      }

      // Get user ID from authenticated session
      // For now, using placeholder - in production, extract from session/JWT
      const userId = 'user_from_session';
      const tenantId = 'tenant_from_session';

      // Store the token
      await tokenManager.storeToken(userId, tenantId, 'gmail', data.access_token, {
        refreshToken: data.refresh_token,
        expiresIn: data.expires_in,
        scopes: data.scope?.split(' ') || [],
        metadata: {
          tokenType: data.token_type,
        },
      });

      logger.info('Gmail OAuth completed', { userId });

      // Redirect to success page
      res.redirect('/oauth/success?service=gmail');
    } catch (error) {
      logger.error('Gmail OAuth callback error', { error });
      res.redirect('/oauth/error?service=gmail&error=server_error');
    }
  })
);

/**
 * Calendar OAuth Flow (uses same Google OAuth as Gmail)
 */

// Step 1: Initiate Calendar OAuth
router.get(
  '/calendar/start',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const state = crypto.randomBytes(32).toString('hex');

    const clientId = process.env.GMAIL_CLIENT_ID; // Reuse Gmail OAuth
    if (!clientId) {
      return res.status(503).json({
        success: false,
        error: 'Calendar OAuth not configured',
      });
    }

    const redirectUri = `${process.env.API_BASE_URL}/api/v1/oauth/calendar/callback`;

    const scopes = [
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.events',
    ].join(' ');

    const authUrl =
      `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${clientId}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `response_type=code&` +
      `scope=${encodeURIComponent(scopes)}&` +
      `access_type=offline&` +
      `prompt=consent&` +
      `state=${state}`;

    logger.info('Calendar OAuth initiated', {
      userId: req.user?.uid,
      state,
    });

    res.json({
      success: true,
      data: {
        authUrl,
        state,
      },
    });
  })
);

// Step 2: Handle Calendar OAuth callback
router.get(
  '/calendar/callback',
  asyncHandler(async (req: Request, res: Response) => {
    const { code, state, error } = req.query;

    if (error) {
      logger.error('Calendar OAuth error', { error });
      return res.redirect(`/oauth/error?service=calendar&error=${error}`);
    }

    if (!code) {
      return res.redirect('/oauth/error?service=calendar&error=no_code');
    }

    try {
      // Exchange code for token
      const response = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          client_id: process.env.GMAIL_CLIENT_ID!,
          client_secret: process.env.GMAIL_CLIENT_SECRET!,
          code: code as string,
          redirect_uri: `${process.env.API_BASE_URL}/api/v1/oauth/calendar/callback`,
          grant_type: 'authorization_code',
        }),
      });

      const data = await response.json() as any;

      if (!data.access_token) {
        logger.error('Calendar token exchange failed', { error: data.error });
        return res.redirect(`/oauth/error?service=calendar&error=${data.error}`);
      }

      // Get user ID from authenticated session
      const userId = 'user_from_session';
      const tenantId = 'tenant_from_session';

      // Store the token
      await tokenManager.storeToken(userId, tenantId, 'calendar', data.access_token, {
        refreshToken: data.refresh_token,
        expiresIn: data.expires_in,
        scopes: data.scope?.split(' ') || [],
        metadata: {
          tokenType: data.token_type,
        },
      });

      logger.info('Calendar OAuth completed', { userId });

      // Redirect to success page
      res.redirect('/oauth/success?service=calendar');
    } catch (error) {
      logger.error('Calendar OAuth callback error', { error });
      res.redirect('/oauth/error?service=calendar&error=server_error');
    }
  })
);

/**
 * Token Management Endpoints
 */

// Get user's connected services
router.get(
  '/connections',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;

    const tokens = await tokenManager.listUserTokens(userId);

    res.json({
      success: true,
      data: {
        connections: tokens.map((token) => ({
          service: token.service,
          expiresAt: token.expiresAt?.toISOString(),
          isExpired: token.expiresAt ? new Date() >= token.expiresAt : false,
        })),
      },
    });
  })
);

// Disconnect a service
router.delete(
  '/:service/disconnect',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const service = req.params.service as 'slack' | 'gmail' | 'calendar';

    if (!['slack', 'gmail', 'calendar'].includes(service)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid service',
      });
    }

    await tokenManager.deleteToken(userId, service);

    logger.info('OAuth connection removed', { userId, service });

    res.json({
      success: true,
      message: `${service} disconnected successfully`,
    });
  })
);

// Check OAuth status for a service
router.get(
  '/:service/status',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const userId = req.user!.uid;
    const service = req.params.service as 'slack' | 'gmail' | 'calendar';

    if (!['slack', 'gmail', 'calendar'].includes(service)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid service',
      });
    }

    const hasToken = await tokenManager.hasValidToken(userId, service);

    res.json({
      success: true,
      data: {
        service,
        connected: hasToken,
      },
    });
  })
);

export default router;
