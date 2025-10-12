"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const auth_1 = require("../middleware/auth");
const serviceRouter_1 = require("../services/serviceRouter");
const logger_1 = require("../utils/logger");
const errorHandler_2 = require("../middleware/errorHandler");
const websocket_1 = require("../services/websocket");
const router = (0, express_1.Router)();
// Apply authentication to all Slack routes
router.use(auth_1.authenticateRequest);
/**
 * GET /api/xynergyos/v2/slack/channels
 * List all Slack channels
 */
router.get('/channels', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching Slack channels via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('slackIntelligence', '/api/v1/slack/channels', {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
        },
        cache: true,
        cacheTtl: 300, // Cache for 5 minutes
    });
    res.json(result);
}));
/**
 * GET /api/xynergyos/v2/slack/channels/:channelId/messages
 * Get messages from a Slack channel
 */
router.get('/channels/:channelId/messages', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { channelId } = req.params;
    const limit = req.query.limit || '20';
    logger_1.logger.info('Fetching Slack channel messages via gateway', {
        channelId,
        limit,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('slackIntelligence', `/api/v1/slack/channels/${channelId}/messages?limit=${limit}`, {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
        },
        cache: true,
        cacheTtl: 60, // Cache for 1 minute
    });
    res.json(result);
}));
/**
 * POST /api/xynergyos/v2/slack/channels/:channelId/messages
 * Post a message to a Slack channel
 */
router.post('/channels/:channelId/messages', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { channelId } = req.params;
    const { text, blocks } = req.body;
    if (!text || typeof text !== 'string') {
        throw new errorHandler_2.ValidationError('Message text is required');
    }
    logger_1.logger.info('Posting message to Slack channel via gateway', {
        channelId,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('slackIntelligence', `/api/v1/slack/channels/${channelId}/messages`, {
        method: 'POST',
        headers: {
            Authorization: req.headers.authorization,
        },
        data: { text, blocks },
    });
    // Broadcast WebSocket event for real-time updates
    const ws = (0, websocket_1.getWebSocketService)();
    ws.broadcast(req.tenantId || 'clearforge', 'slack', 'message:sent', {
        channelId,
        text,
        userId: req.user?.uid,
        timestamp: new Date().toISOString(),
    });
    res.json(result);
}));
/**
 * GET /api/xynergyos/v2/slack/users
 * List all Slack users
 */
router.get('/users', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching Slack users via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('slackIntelligence', '/api/v1/slack/users', {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
        },
        cache: true,
        cacheTtl: 600, // Cache for 10 minutes
    });
    res.json(result);
}));
/**
 * GET /api/xynergyos/v2/slack/users/:userId
 * Get Slack user info
 */
router.get('/users/:userId', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { userId } = req.params;
    logger_1.logger.info('Fetching Slack user info via gateway', {
        targetUserId: userId,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('slackIntelligence', `/api/v1/slack/users/${userId}`, {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
        },
        cache: true,
        cacheTtl: 600,
    });
    res.json(result);
}));
/**
 * GET /api/xynergyos/v2/slack/search
 * Search Slack messages
 */
router.get('/search', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const query = req.query.q;
    const count = req.query.count || '20';
    if (!query) {
        throw new errorHandler_2.ValidationError('Search query (q) is required');
    }
    logger_1.logger.info('Searching Slack messages via gateway', {
        query,
        count,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('slackIntelligence', `/api/v1/slack/search?q=${encodeURIComponent(query)}&count=${count}`, {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
        },
        cache: true,
        cacheTtl: 120, // Cache search results for 2 minutes
    });
    res.json(result);
}));
/**
 * GET /api/xynergyos/v2/slack/status
 * Get Slack connection status
 */
router.get('/status', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Checking Slack status via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('slackIntelligence', '/api/v1/slack/status', {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
        },
    });
    res.json(result);
}));
exports.default = router;
//# sourceMappingURL=slack.js.map