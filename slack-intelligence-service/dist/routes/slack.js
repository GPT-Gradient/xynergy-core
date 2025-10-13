"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const auth_1 = require("../middleware/auth");
const slackService_1 = require("../services/slackService");
const logger_1 = require("../utils/logger");
const errorHandler_2 = require("../middleware/errorHandler");
const router = (0, express_1.Router)();
// Apply authentication to all Slack routes
router.use(auth_1.authenticateRequest);
/**
 * GET /api/v1/slack/channels
 * List all channels in the workspace
 */
router.get('/channels', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    logger_1.logger.info('Fetching Slack channels', {
        userId,
        requestId: req.requestId,
    });
    const channels = await slackService_1.slackService.listChannels(userId);
    res.json({
        success: true,
        data: {
            channels,
            count: channels.length,
            mockMode: slackService_1.slackService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/slack/channels/:channelId/messages
 * Get messages from a specific channel
 */
router.get('/channels/:channelId/messages', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const { channelId } = req.params;
    const limit = parseInt(req.query.limit) || 20;
    if (limit < 1 || limit > 100) {
        throw new errorHandler_2.ValidationError('Limit must be between 1 and 100');
    }
    logger_1.logger.info('Fetching channel messages', {
        channelId,
        limit,
        userId,
        requestId: req.requestId,
    });
    const messages = await slackService_1.slackService.getChannelHistory(userId, channelId, limit);
    res.json({
        success: true,
        data: {
            channelId,
            messages,
            count: messages.length,
            mockMode: slackService_1.slackService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * POST /api/v1/slack/channels/:channelId/messages
 * Post a message to a channel
 */
router.post('/channels/:channelId/messages', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const { channelId } = req.params;
    const { text, blocks } = req.body;
    if (!text || typeof text !== 'string') {
        throw new errorHandler_2.ValidationError('Message text is required');
    }
    logger_1.logger.info('Posting message to Slack channel', {
        channelId,
        userId,
        requestId: req.requestId,
    });
    const result = await slackService_1.slackService.postMessage(userId, channelId, text, blocks);
    res.json({
        success: true,
        data: {
            channelId,
            messageTs: result.ts,
            mockMode: slackService_1.slackService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/slack/users
 * List all users in the workspace
 */
router.get('/users', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    logger_1.logger.info('Fetching Slack users', {
        userId,
        requestId: req.requestId,
    });
    const users = await slackService_1.slackService.listUsers(userId);
    res.json({
        success: true,
        data: {
            users,
            count: users.length,
            mockMode: slackService_1.slackService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/slack/users/:userId
 * Get info about a specific user
 */
router.get('/users/:slackUserId', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const { slackUserId } = req.params;
    logger_1.logger.info('Fetching Slack user info', {
        slackUserId,
        userId,
        requestId: req.requestId,
    });
    const user = await slackService_1.slackService.getUserInfo(userId, slackUserId);
    res.json({
        success: true,
        data: {
            user,
            mockMode: slackService_1.slackService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/slack/search
 * Search messages in the workspace
 */
router.get('/search', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const query = req.query.q;
    const count = parseInt(req.query.count) || 20;
    if (!query) {
        throw new errorHandler_2.ValidationError('Search query (q) is required');
    }
    if (count < 1 || count > 100) {
        throw new errorHandler_2.ValidationError('Count must be between 1 and 100');
    }
    logger_1.logger.info('Searching Slack messages', {
        query,
        count,
        userId,
        requestId: req.requestId,
    });
    const results = await slackService_1.slackService.searchMessages(userId, query, count);
    res.json({
        success: true,
        data: {
            query,
            results,
            mockMode: slackService_1.slackService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/slack/status
 * Get Slack connection status
 */
router.get('/status', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const userId = req.user.uid;
    const status = await slackService_1.slackService.testConnection(userId);
    res.json({
        success: true,
        data: {
            connected: status.ok,
            team: status.team,
            mockMode: slackService_1.slackService.isInMockMode(),
            error: status.error,
        },
        timestamp: new Date().toISOString(),
    });
}));
exports.default = router;
//# sourceMappingURL=slack.js.map