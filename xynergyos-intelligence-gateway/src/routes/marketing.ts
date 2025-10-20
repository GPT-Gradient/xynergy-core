import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { serviceRouter } from '../services/serviceRouter';
import { logger } from '../utils/logger';

const router = Router();

// Apply authentication to all Marketing routes
router.use(authenticateRequest);

/**
 * POST /api/v1/marketing/campaign
 * Create marketing campaign
 */
router.post('/campaign', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Creating marketing campaign via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callService('marketingEngine', '/campaigns/create', {
    method: 'POST',
    headers: {
      Authorization: req.headers.authorization!,
    },
    data: req.body,
    timeout: 120000, // 2 minutes for AI content generation
  });

  res.json(result);
}));

/**
 * GET /api/v1/marketing/campaigns
 * List marketing campaigns
 */
router.get('/campaigns', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Fetching marketing campaigns via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callService('marketingEngine', '/campaigns', {
    method: 'GET',
    headers: {
      Authorization: req.headers.authorization!,
    },
    cache: true,
    cacheTtl: 300,
  });

  res.json(result);
}));

/**
 * POST /api/v1/marketing/content
 * Generate marketing content
 */
router.post('/content', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Generating marketing content via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callService('marketingEngine', '/generate-content', {
    method: 'POST',
    headers: {
      Authorization: req.headers.authorization!,
    },
    data: req.body,
    timeout: 120000,
  });

  res.json(result);
}));

export default router;
