/**
 * OAuth Routes
 * Public OAuth flow endpoints
 */

import { Router, Request, Response } from 'express';
import { OAuthService } from '../services/oauthService';
import { logger } from '../utils/logger';
import { GenerateOAuthUrlRequest, OAuthCallbackRequest } from '../types';

const router = Router();
const oauthService = new OAuthService();

/**
 * POST /api/v1/oauth/authorize
 * Generate OAuth authorization URL
 */
router.post('/authorize', async (req: Request, res: Response) => {
  try {
    const request: GenerateOAuthUrlRequest = req.body;

    // Validate request
    if (!request.userId || !request.tenantId || !request.provider) {
      return res.status(400).json({
        error: 'Missing required fields: userId, tenantId, provider',
      });
    }

    if (!['slack', 'gmail'].includes(request.provider)) {
      return res.status(400).json({
        error: 'Invalid provider. Must be "slack" or "gmail"',
      });
    }

    const result = await oauthService.generateAuthUrl(request);

    res.json(result);
  } catch (error: any) {
    logger.error('Error in /authorize endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to generate OAuth URL' });
  }
});

/**
 * GET /api/v1/oauth/callback
 * Handle OAuth callback (redirect from provider)
 */
router.get('/callback', async (req: Request, res: Response) => {
  try {
    const { code, state, error } = req.query;

    // Check for OAuth errors
    if (error) {
      logger.warn('OAuth callback error', { error });
      return res.status(400).send(`
        <html>
          <head><title>OAuth Failed</title></head>
          <body>
            <h1>OAuth Authorization Failed</h1>
            <p>Error: ${error}</p>
            <p>You can close this window and try again.</p>
          </body>
        </html>
      `);
    }

    // Validate required parameters
    if (!code || !state) {
      return res.status(400).json({
        error: 'Missing required parameters: code and state',
      });
    }

    const request: OAuthCallbackRequest = {
      code: code as string,
      state: state as string,
    };

    const result = await oauthService.handleCallback(request);

    // Return success page
    res.send(`
      <html>
        <head><title>OAuth Success</title></head>
        <body>
          <h1>Authorization Successful!</h1>
          <p>Your ${result.provider} account (${result.email}) has been connected.</p>
          <p>Connection ID: ${result.connectionId}</p>
          <p>You can close this window and return to the application.</p>
          <script>
            // Post message to parent window if opened in popup
            if (window.opener) {
              window.opener.postMessage({
                type: 'oauth_success',
                provider: '${result.provider}',
                connectionId: '${result.connectionId}',
              }, '*');
            }
          </script>
        </body>
      </html>
    `);
  } catch (error: any) {
    logger.error('Error in /callback endpoint', { error });
    res.status(500).send(`
      <html>
        <head><title>OAuth Error</title></head>
        <body>
          <h1>Authorization Error</h1>
          <p>${error.message || 'An unexpected error occurred'}</p>
          <p>You can close this window and try again.</p>
        </body>
      </html>
    `);
  }
});

/**
 * GET /api/v1/oauth/connections
 * List user's OAuth connections
 */
router.get('/connections', async (req: Request, res: Response) => {
  try {
    const { userId, tenantId, provider, status } = req.query;

    if (!userId || !tenantId) {
      return res.status(400).json({
        error: 'Missing required query parameters: userId, tenantId',
      });
    }

    // TODO: Get connections from Firestore
    // For now, return placeholder
    res.json({
      connections: [],
      total: 0,
    });
  } catch (error: any) {
    logger.error('Error in /connections endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to list connections' });
  }
});

export default router;
