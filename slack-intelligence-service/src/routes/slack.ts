import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { slackService } from '../services/slackService';
import { logger } from '../utils/logger';
import { ValidationError } from '../middleware/errorHandler';

const router = Router();

// Apply authentication to all Slack routes
router.use(authenticateRequest);

/**
 * GET /api/v1/slack/channels
 * List all channels in the workspace
 */
router.get('/channels', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Fetching Slack channels', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const channels = await slackService.listChannels();

  res.json({
    success: true,
    data: {
      channels,
      count: channels.length,
      mockMode: slackService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /api/v1/slack/channels/:channelId/messages
 * Get messages from a specific channel
 */
router.get('/channels/:channelId/messages', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { channelId } = req.params;
  const limit = parseInt(req.query.limit as string) || 20;

  if (limit < 1 || limit > 100) {
    throw new ValidationError('Limit must be between 1 and 100');
  }

  logger.info('Fetching channel messages', {
    channelId,
    limit,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const messages = await slackService.getChannelHistory(channelId, limit);

  res.json({
    success: true,
    data: {
      channelId,
      messages,
      count: messages.length,
      mockMode: slackService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * POST /api/v1/slack/channels/:channelId/messages
 * Post a message to a channel
 */
router.post('/channels/:channelId/messages', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { channelId } = req.params;
  const { text, blocks } = req.body;

  if (!text || typeof text !== 'string') {
    throw new ValidationError('Message text is required');
  }

  logger.info('Posting message to Slack channel', {
    channelId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await slackService.postMessage(channelId, text, blocks);

  res.json({
    success: true,
    data: {
      channelId,
      messageTs: result.ts,
      mockMode: slackService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /api/v1/slack/users
 * List all users in the workspace
 */
router.get('/users', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Fetching Slack users', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const users = await slackService.listUsers();

  res.json({
    success: true,
    data: {
      users,
      count: users.length,
      mockMode: slackService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /api/v1/slack/users/:userId
 * Get info about a specific user
 */
router.get('/users/:userId', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { userId } = req.params;

  logger.info('Fetching Slack user info', {
    targetUserId: userId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const user = await slackService.getUserInfo(userId);

  res.json({
    success: true,
    data: {
      user,
      mockMode: slackService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /api/v1/slack/search
 * Search messages in the workspace
 */
router.get('/search', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const query = req.query.q as string;
  const count = parseInt(req.query.count as string) || 20;

  if (!query) {
    throw new ValidationError('Search query (q) is required');
  }

  if (count < 1 || count > 100) {
    throw new ValidationError('Count must be between 1 and 100');
  }

  logger.info('Searching Slack messages', {
    query,
    count,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const results = await slackService.searchMessages(query, count);

  res.json({
    success: true,
    data: {
      query,
      results,
      mockMode: slackService.isInMockMode(),
    },
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /api/v1/slack/status
 * Get Slack connection status
 */
router.get('/status', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const status = await slackService.testConnection();

  res.json({
    success: true,
    data: {
      connected: status.ok,
      team: status.team,
      mockMode: slackService.isInMockMode(),
      error: status.error,
    },
    timestamp: new Date().toISOString(),
  });
}));

export default router;
