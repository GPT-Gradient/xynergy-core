import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { enforceTenant, TenantRequest } from '../middleware/tenantEnforcement';
import { checkPermission } from '../middleware/checkPermission';
import { serviceRouter } from '../services/serviceRouter';
import { logger } from '../utils/logger';
import { ValidationError } from '../middleware/errorHandler';
import { getWebSocketService } from '../services/websocket';

const router = Router();

// Apply authentication and tenant enforcement to all Slack routes
router.use(authenticateRequest);
router.use(enforceTenant);

/**
 * GET /api/xynergyos/v2/slack/channels
 * List all Slack channels
 * Permission: slack.read
 */
router.get('/channels',
  checkPermission('slack.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Fetching Slack channels via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('slackIntelligence', '/api/v1/slack/channels', {
      method: 'GET',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
      },
      cache: true,
      cacheTtl: 300, // Cache for 5 minutes
    });

    res.json(result);
  })
);

/**
 * GET /api/xynergyos/v2/slack/channels/:channelId/messages
 * Get messages from a Slack channel
 * Permission: slack.read
 */
router.get('/channels/:channelId/messages',
  checkPermission('slack.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { channelId } = req.params;
    const limit = req.query.limit || '20';

    logger.info('Fetching Slack channel messages via gateway', {
      channelId,
      limit,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('slackIntelligence',
      `/api/v1/slack/channels/${channelId}/messages?limit=${limit}`,
      {
        method: 'GET',
        headers: {
          Authorization: req.headers.authorization!,
          'X-Tenant-Id': req.tenantId,
        },
        cache: true,
        cacheTtl: 60, // Cache for 1 minute
      }
    );

    res.json(result);
  })
);

/**
 * POST /api/xynergyos/v2/slack/channels/:channelId/messages
 * Post a message to a Slack channel
 * Permission: slack.write
 */
router.post('/channels/:channelId/messages',
  checkPermission('slack.write'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { channelId } = req.params;
    const { text, blocks } = req.body;

    if (!text || typeof text !== 'string') {
      throw new ValidationError('Message text is required');
    }

    logger.info('Posting message to Slack channel via gateway', {
      channelId,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('slackIntelligence',
      `/api/v1/slack/channels/${channelId}/messages`,
      {
        method: 'POST',
        headers: {
          Authorization: req.headers.authorization!,
          'X-Tenant-Id': req.tenantId,
        },
        data: { text, blocks },
      }
    );

    // Broadcast WebSocket event for real-time updates
    const ws = getWebSocketService();
    ws.broadcast(req.tenantId, 'slack', 'message:sent', {
      channelId,
      text,
      userId: req.user?.uid,
      timestamp: new Date().toISOString(),
    });

    res.json(result);
  })
);

/**
 * GET /api/xynergyos/v2/slack/users
 * List all Slack users
 * Permission: slack.read
 */
router.get('/users',
  checkPermission('slack.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Fetching Slack users via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('slackIntelligence','/api/v1/slack/users', {
      method: 'GET',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
      },
      cache: true,
      cacheTtl: 600, // Cache for 10 minutes
    });

    res.json(result);
  })
);

/**
 * GET /api/xynergyos/v2/slack/users/:userId
 * Get Slack user info
 * Permission: slack.read
 */
router.get('/users/:userId',
  checkPermission('slack.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { userId } = req.params;

    logger.info('Fetching Slack user info via gateway', {
      targetUserId: userId,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('slackIntelligence',`/api/v1/slack/users/${userId}`, {
      method: 'GET',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
      },
      cache: true,
      cacheTtl: 600,
    });

    res.json(result);
  })
);

/**
 * GET /api/xynergyos/v2/slack/search
 * Search Slack messages
 * Permission: slack.read
 */
router.get('/search',
  checkPermission('slack.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const query = req.query.q as string;
    const count = req.query.count || '20';

    if (!query) {
      throw new ValidationError('Search query (q) is required');
    }

    logger.info('Searching Slack messages via gateway', {
      query,
      count,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('slackIntelligence',
      `/api/v1/slack/search?q=${encodeURIComponent(query)}&count=${count}`,
      {
        method: 'GET',
        headers: {
          Authorization: req.headers.authorization!,
          'X-Tenant-Id': req.tenantId,
        },
        cache: true,
        cacheTtl: 120, // Cache search results for 2 minutes
      }
    );

    res.json(result);
  })
);

/**
 * GET /api/xynergyos/v2/slack/status
 * Get Slack connection status
 * Permission: slack.read
 */
router.get('/status',
  checkPermission('slack.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Checking Slack status via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('slackIntelligence','/api/v1/slack/status', {
      method: 'GET',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
      },
    });

    res.json(result);
  })
);

export default router;
