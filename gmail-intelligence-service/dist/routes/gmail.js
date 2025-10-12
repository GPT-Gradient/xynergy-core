"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const auth_1 = require("../middleware/auth");
const gmailService_1 = require("../services/gmailService");
const logger_1 = require("../utils/logger");
const errorHandler_2 = require("../middleware/errorHandler");
const router = (0, express_1.Router)();
// Apply authentication to all Gmail routes
router.use(auth_1.authenticateRequest);
/**
 * GET /api/v1/gmail/messages
 * List messages in inbox
 */
router.get('/messages', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const maxResults = parseInt(req.query.maxResults) || 20;
    const query = req.query.q;
    logger_1.logger.info('Fetching Gmail messages', {
        userId: req.user?.uid,
        maxResults,
        query,
        requestId: req.requestId,
    });
    const messages = await gmailService_1.gmailService.listMessages(maxResults, query);
    res.json({
        success: true,
        data: {
            messages,
            count: messages.length,
            mockMode: gmailService_1.gmailService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/gmail/messages/:messageId
 * Get message details
 */
router.get('/messages/:messageId', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { messageId } = req.params;
    logger_1.logger.info('Fetching Gmail message', {
        messageId,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const message = await gmailService_1.gmailService.getMessage(messageId);
    res.json({
        success: true,
        data: {
            message,
            mockMode: gmailService_1.gmailService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * POST /api/v1/gmail/messages
 * Send email
 */
router.post('/messages', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { to, subject, body, cc, bcc } = req.body;
    if (!to || !subject || !body) {
        throw new errorHandler_2.ValidationError('to, subject, and body are required');
    }
    logger_1.logger.info('Sending Gmail message', {
        to,
        subject,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await gmailService_1.gmailService.sendMessage(to, subject, body, cc, bcc);
    res.json({
        success: true,
        data: {
            messageId: result.id,
            mockMode: gmailService_1.gmailService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/gmail/search
 * Search messages
 */
router.get('/search', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const query = req.query.q;
    const maxResults = parseInt(req.query.maxResults) || 20;
    if (!query) {
        throw new errorHandler_2.ValidationError('Search query (q) is required');
    }
    logger_1.logger.info('Searching Gmail messages', {
        query,
        maxResults,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const messages = await gmailService_1.gmailService.searchMessages(query, maxResults);
    res.json({
        success: true,
        data: {
            query,
            messages,
            count: messages.length,
            mockMode: gmailService_1.gmailService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/gmail/threads/:threadId
 * Get email thread
 */
router.get('/threads/:threadId', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { threadId } = req.params;
    logger_1.logger.info('Fetching Gmail thread', {
        threadId,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const thread = await gmailService_1.gmailService.getThread(threadId);
    res.json({
        success: true,
        data: {
            thread,
            mockMode: gmailService_1.gmailService.isInMockMode(),
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/gmail/status
 * Get Gmail connection status
 */
router.get('/status', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const status = await gmailService_1.gmailService.testConnection();
    res.json({
        success: true,
        data: {
            connected: status.ok,
            email: status.email,
            mockMode: gmailService_1.gmailService.isInMockMode(),
            error: status.error,
        },
        timestamp: new Date().toISOString(),
    });
}));
exports.default = router;
//# sourceMappingURL=gmail.js.map