import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { gmailService } from '../services/gmailService';
import { logger } from '../utils/logger';
import { ValidationError } from '../middleware/errorHandler';

const router = Router();

// Apply authentication to all Gmail routes
router.use(authenticateRequest);

/**
 * GET /api/v1/gmail/messages
 * List messages in inbox
 */
router.get('/messages', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const maxResults = parseInt(req.query.maxResults as string) || 20;
  const query = req.query.q as string;

  logger.info('Fetching Gmail messages', {
    userId: req.user?.uid,
    maxResults,
    query,
    requestId: req.requestId,
  });

  const messages = await gmailService.listMessages(maxResults, query);

  res.json({
    success: true,
    data: {
      messages,
      count: messages.length,
      mockMode: gmailService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /api/v1/gmail/messages/:messageId
 * Get message details
 */
router.get('/messages/:messageId', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { messageId } = req.params;

  logger.info('Fetching Gmail message', {
    messageId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const message = await gmailService.getMessage(messageId);

  res.json({
    success: true,
    data: {
      message,
      mockMode: gmailService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * POST /api/v1/gmail/messages
 * Send email
 */
router.post('/messages', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { to, subject, body, cc, bcc } = req.body;

  if (!to || !subject || !body) {
    throw new ValidationError('to, subject, and body are required');
  }

  logger.info('Sending Gmail message', {
    to,
    subject,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await gmailService.sendMessage(to, subject, body, cc, bcc);

  res.json({
    success: true,
    data: {
      messageId: result.id,
      mockMode: gmailService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /api/v1/gmail/search
 * Search messages
 */
router.get('/search', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const query = req.query.q as string;
  const maxResults = parseInt(req.query.maxResults as string) || 20;

  if (!query) {
    throw new ValidationError('Search query (q) is required');
  }

  logger.info('Searching Gmail messages', {
    query,
    maxResults,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const messages = await gmailService.searchMessages(query, maxResults);

  res.json({
    success: true,
    data: {
      query,
      messages,
      count: messages.length,
      mockMode: gmailService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /api/v1/gmail/threads/:threadId
 * Get email thread
 */
router.get('/threads/:threadId', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { threadId } = req.params;

  logger.info('Fetching Gmail thread', {
    threadId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const thread = await gmailService.getThread(threadId);

  res.json({
    success: true,
    data: {
      thread,
      mockMode: gmailService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /api/v1/gmail/status
 * Get Gmail connection status
 */
router.get('/status', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const status = await gmailService.testConnection();

  res.json({
    success: true,
    data: {
      connected: status.ok,
      email: status.email,
      mockMode: gmailService.isInMockMode(),
      error: status.error,
    },
    timestamp: new Date().toISOString(),
  });
}));

export default router;
