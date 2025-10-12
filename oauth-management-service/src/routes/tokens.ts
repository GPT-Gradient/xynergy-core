/**
 * Token Routes
 * Internal API for services to get OAuth tokens
 */

import { Router, Request, Response } from 'express';
import { TokenService } from '../services/tokenService';
import { logger } from '../utils/logger';
import { GetTokenRequest } from '../types';

const router = Router();
const tokenService = new TokenService();

/**
 * POST /api/v1/tokens/get
 * Get access token for a user's OAuth connection (internal use)
 */
router.post('/get', async (req: Request, res: Response) => {
  try {
    const request: GetTokenRequest = req.body;

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

    const result = await tokenService.getToken(request);

    res.json(result);
  } catch (error: any) {
    logger.error('Error in /tokens/get endpoint', { error });

    if (error.message.includes('No active OAuth connection found')) {
      return res.status(404).json({ error: error.message });
    }

    res.status(500).json({ error: error.message || 'Failed to get token' });
  }
});

/**
 * POST /api/v1/tokens/refresh/:connectionId
 * Manually refresh a token (admin use)
 */
router.post('/refresh/:connectionId', async (req: Request, res: Response) => {
  try {
    const { connectionId } = req.params;

    if (!connectionId) {
      return res.status(400).json({ error: 'Missing connectionId' });
    }

    const result = await tokenService.refreshToken(connectionId);

    if (!result.success) {
      return res.status(500).json({
        error: result.error || 'Token refresh failed',
      });
    }

    res.json(result);
  } catch (error: any) {
    logger.error('Error in /tokens/refresh endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to refresh token' });
  }
});

/**
 * POST /api/v1/tokens/revoke/:connectionId
 * Revoke an OAuth connection
 */
router.post('/revoke/:connectionId', async (req: Request, res: Response) => {
  try {
    const { connectionId } = req.params;
    const { revokedBy, reason } = req.body;

    if (!connectionId) {
      return res.status(400).json({ error: 'Missing connectionId' });
    }

    if (!revokedBy) {
      return res.status(400).json({ error: 'Missing revokedBy field' });
    }

    await tokenService.revokeConnection(connectionId, revokedBy, reason);

    res.json({
      success: true,
      message: 'Connection revoked successfully',
    });
  } catch (error: any) {
    logger.error('Error in /tokens/revoke endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to revoke connection' });
  }
});

export default router;
