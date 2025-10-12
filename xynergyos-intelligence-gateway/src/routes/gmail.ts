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

// Apply authentication and tenant enforcement to all Gmail routes
router.use(authenticateRequest);
router.use(enforceTenant);

/**
 * GET /api/xynergyos/v2/gmail/messages
 * List Gmail messages
 * Permission: gmail.read
 */
router.get('/messages',
  checkPermission('gmail.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const maxResults = req.query.maxResults || '20';
    const query = req.query.q as string;

    logger.info('Fetching Gmail messages via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      maxResults,
      query,
      requestId: req.requestId,
    });

    const queryString = query ? `?maxResults=${maxResults}&q=${encodeURIComponent(query)}` : `?maxResults=${maxResults}`;

    const result = await serviceRouter.callService('gmailIntelligence',
      `/api/v1/gmail/messages${queryString}`,
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
 * GET /api/xynergyos/v2/gmail/messages/:messageId
 * Get Gmail message details
 * Permission: gmail.read
 */
router.get('/messages/:messageId',
  checkPermission('gmail.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { messageId } = req.params;

    logger.info('Fetching Gmail message via gateway', {
      messageId,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('gmailIntelligence',
      `/api/v1/gmail/messages/${messageId}`,
      {
        method: 'GET',
        headers: {
          Authorization: req.headers.authorization!,
          'X-Tenant-Id': req.tenantId,
        },
        cache: true,
        cacheTtl: 300, // Cache for 5 minutes (messages don't change)
      }
    );

    res.json(result);
  })
);

/**
 * POST /api/xynergyos/v2/gmail/messages
 * Send an email
 * Permission: gmail.write
 */
router.post('/messages',
  checkPermission('gmail.write'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { to, subject, body, cc, bcc } = req.body;

    if (!to || !subject || !body) {
      throw new ValidationError('to, subject, and body are required');
    }

    logger.info('Sending Gmail message via gateway', {
      to,
      subject,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('gmailIntelligence',
      '/api/v1/gmail/messages',
      {
        method: 'POST',
        headers: {
          Authorization: req.headers.authorization!,
          'X-Tenant-Id': req.tenantId,
        },
        data: { to, subject, body, cc, bcc },
      }
    );

    // Broadcast WebSocket event for real-time updates
    const ws = getWebSocketService();
    ws.broadcast(req.tenantId, 'gmail', 'email:sent', {
      to,
      subject,
      userId: req.user?.uid,
      timestamp: new Date().toISOString(),
    });

    res.json(result);
  })
);

/**
 * GET /api/xynergyos/v2/gmail/search
 * Search Gmail messages
 * Permission: gmail.read
 */
router.get('/search',
  checkPermission('gmail.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const query = req.query.q as string;
    const maxResults = req.query.maxResults || '20';

    if (!query) {
      throw new ValidationError('Search query (q) is required');
    }

    logger.info('Searching Gmail messages via gateway', {
      query,
      maxResults,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('gmailIntelligence',
      `/api/v1/gmail/search?q=${encodeURIComponent(query)}&maxResults=${maxResults}`,
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
 * GET /api/xynergyos/v2/gmail/threads/:threadId
 * Get email thread
 * Permission: gmail.read
 */
router.get('/threads/:threadId',
  checkPermission('gmail.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { threadId } = req.params;

    logger.info('Fetching Gmail thread via gateway', {
      threadId,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('gmailIntelligence',
      `/api/v1/gmail/threads/${threadId}`,
      {
        method: 'GET',
        headers: {
          Authorization: req.headers.authorization!,
          'X-Tenant-Id': req.tenantId,
        },
        cache: true,
        cacheTtl: 300, // Cache for 5 minutes
      }
    );

    res.json(result);
  })
);

/**
 * GET /api/xynergyos/v2/gmail/status
 * Get Gmail connection status
 * Permission: gmail.read
 */
router.get('/status',
  checkPermission('gmail.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Checking Gmail status via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('gmailIntelligence',
      '/api/v1/gmail/status',
      {
        method: 'GET',
        headers: {
          Authorization: req.headers.authorization!,
          'X-Tenant-Id': req.tenantId,
        },
        cache: false, // Don't cache status checks
      }
    );

    res.json(result);
  })
);

export default router;
