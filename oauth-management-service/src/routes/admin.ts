/**
 * Admin Routes
 * Admin dashboard endpoints for monitoring OAuth connections
 */

import { Router, Request, Response } from 'express';
import { getFirestore } from 'firebase-admin/firestore';
import { HealthService } from '../services/healthService';
import { TokenService } from '../services/tokenService';
import { logger } from '../utils/logger';
import { OAuthConnection } from '../types';

const router = Router();
const healthService = new HealthService();
const tokenService = new TokenService();

/**
 * GET /api/v1/admin/stats
 * Get OAuth connection statistics
 */
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const db = getFirestore();

    // Get all connections
    const allConnections = await db.collection('oauth_connections').get();

    const stats = {
      totalConnections: allConnections.size,
      activeConnections: 0,
      expiredConnections: 0,
      revokedConnections: 0,
      errorConnections: 0,
      byProvider: {
        slack: { total: 0, active: 0, expired: 0 },
        gmail: { total: 0, active: 0, expired: 0 },
      },
    };

    for (const doc of allConnections.docs) {
      const connection = doc.data() as OAuthConnection;

      // Count by status
      if (connection.status === 'active') {
        stats.activeConnections++;
      } else if (connection.status === 'expired') {
        stats.expiredConnections++;
      } else if (connection.status === 'revoked') {
        stats.revokedConnections++;
      } else if (connection.status === 'error') {
        stats.errorConnections++;
      }

      // Count by provider
      if (connection.provider === 'slack') {
        stats.byProvider.slack.total++;
        if (connection.status === 'active') {
          stats.byProvider.slack.active++;
        } else if (connection.status === 'expired') {
          stats.byProvider.slack.expired++;
        }
      } else if (connection.provider === 'gmail') {
        stats.byProvider.gmail.total++;
        if (connection.status === 'active') {
          stats.byProvider.gmail.active++;
        } else if (connection.status === 'expired') {
          stats.byProvider.gmail.expired++;
        }
      }
    }

    res.json(stats);
  } catch (error: any) {
    logger.error('Error in /admin/stats endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to get stats' });
  }
});

/**
 * GET /api/v1/admin/connections
 * List all OAuth connections (with filters)
 */
router.get('/connections', async (req: Request, res: Response) => {
  try {
    const { provider, status, userId, tenantId, limit = '50' } = req.query;
    const db = getFirestore();

    let query: any = db.collection('oauth_connections');

    // Apply filters
    if (provider) {
      query = query.where('provider', '==', provider);
    }
    if (status) {
      query = query.where('status', '==', status);
    }
    if (userId) {
      query = query.where('userId', '==', userId);
    }
    if (tenantId) {
      query = query.where('tenantId', '==', tenantId);
    }

    // Apply limit
    query = query.limit(parseInt(limit as string, 10));

    const querySnapshot = await query.get();

    const connections = querySnapshot.docs.map((doc: any) => {
      const data = doc.data() as OAuthConnection;
      // Remove encrypted tokens from response
      return {
        ...data,
        encryptedAccessToken: '[REDACTED]',
        encryptedRefreshToken: data.encryptedRefreshToken ? '[REDACTED]' : undefined,
      };
    });

    res.json({
      connections,
      total: connections.length,
    });
  } catch (error: any) {
    logger.error('Error in /admin/connections endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to list connections' });
  }
});

/**
 * GET /api/v1/admin/connections/:id
 * Get connection details
 */
router.get('/connections/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const db = getFirestore();

    const connectionDoc = await db.collection('oauth_connections').doc(id).get();

    if (!connectionDoc.exists) {
      return res.status(404).json({ error: 'Connection not found' });
    }

    const connection = connectionDoc.data() as OAuthConnection;

    // Remove encrypted tokens from response
    const safeConnection = {
      ...connection,
      encryptedAccessToken: '[REDACTED]',
      encryptedRefreshToken: connection.encryptedRefreshToken ? '[REDACTED]' : undefined,
    };

    res.json(safeConnection);
  } catch (error: any) {
    logger.error('Error in /admin/connections/:id endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to get connection' });
  }
});

/**
 * POST /api/v1/admin/health/check/:id
 * Manually check health of a connection
 */
router.post('/health/check/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    const result = await healthService.checkConnectionHealth(id);

    res.json(result);
  } catch (error: any) {
    logger.error('Error in /admin/health/check endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to check health' });
  }
});

/**
 * POST /api/v1/admin/health/check-all
 * Check health of all active connections
 */
router.post('/health/check-all', async (req: Request, res: Response) => {
  try {
    const results = await healthService.checkAllConnections();

    const summary = {
      total: results.length,
      healthy: results.filter(r => r.status === 'healthy').length,
      unhealthy: results.filter(r => r.status === 'unhealthy').length,
      results,
    };

    res.json(summary);
  } catch (error: any) {
    logger.error('Error in /admin/health/check-all endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to check all connections' });
  }
});

/**
 * GET /api/v1/admin/health/stats
 * Get health statistics
 */
router.get('/health/stats', async (req: Request, res: Response) => {
  try {
    const stats = await healthService.getHealthStats();
    res.json(stats);
  } catch (error: any) {
    logger.error('Error in /admin/health/stats endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to get health stats' });
  }
});

/**
 * POST /api/v1/admin/refresh/expiring
 * Manually trigger refresh of expiring tokens
 */
router.post('/refresh/expiring', async (req: Request, res: Response) => {
  try {
    const results = await tokenService.refreshExpiringTokens();

    const summary = {
      total: results.length,
      successful: results.filter(r => r.success).length,
      failed: results.filter(r => !r.success).length,
      results,
    };

    res.json(summary);
  } catch (error: any) {
    logger.error('Error in /admin/refresh/expiring endpoint', { error });
    res.status(500).json({ error: error.message || 'Failed to refresh expiring tokens' });
  }
});

export default router;
