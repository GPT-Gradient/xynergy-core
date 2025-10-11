import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { serviceRouter } from '../services/serviceRouter';
import { logger } from '../utils/logger';

const router = Router();

// Apply authentication to all ASO routes
router.use(authenticateRequest);

/**
 * POST /api/v1/aso/optimize
 * Run ASO optimization
 */
router.post('/optimize', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Running ASO optimization via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callService('asoEngine', '/optimize', {
    method: 'POST',
    headers: {
      Authorization: req.headers.authorization!,
    },
    data: req.body,
    timeout: 120000,
  });

  res.json(result);
}));

/**
 * GET /api/v1/aso/keywords
 * Get keyword recommendations
 */
router.get('/keywords', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Fetching ASO keywords via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callService('asoEngine', '/keywords', {
    method: 'GET',
    headers: {
      Authorization: req.headers.authorization!,
    },
    params: req.query,
    cache: true,
    cacheTtl: 3600, // Cache for 1 hour
  });

  res.json(result);
}));

/**
 * GET /api/v1/aso/analysis
 * Get ASO analysis
 */
router.get('/analysis', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Fetching ASO analysis via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callService('asoEngine', '/analyze', {
    method: 'GET',
    headers: {
      Authorization: req.headers.authorization!,
    },
    params: req.query,
  });

  res.json(result);
}));

export default router;
