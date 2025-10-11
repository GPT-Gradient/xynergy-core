import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { serviceRouter } from '../services/serviceRouter';
import { logger } from '../utils/logger';

const router = Router();

// Apply authentication to all AI routes
router.use(authenticateRequest);

/**
 * POST /api/v1/ai/query
 * Query the AI Assistant
 */
router.post('/query', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('AI query via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callService('aiAssistant', '/query', {
    method: 'POST',
    headers: {
      Authorization: req.headers.authorization!,
    },
    data: req.body,
    timeout: 120000, // 2 minutes for AI processing
  });

  res.json(result);
}));

/**
 * POST /api/v1/ai/chat
 * Chat with AI Assistant
 */
router.post('/chat', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('AI chat via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callService('aiAssistant', '/chat', {
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
 * GET /api/v1/ai/history
 * Get AI conversation history
 */
router.get('/history', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Fetching AI history via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callService('aiAssistant', '/history', {
    method: 'GET',
    headers: {
      Authorization: req.headers.authorization!,
    },
    cache: true,
    cacheTtl: 60,
  });

  res.json(result);
}));

export default router;
