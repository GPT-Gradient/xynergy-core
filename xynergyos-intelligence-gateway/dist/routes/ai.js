"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const auth_1 = require("../middleware/auth");
const serviceRouter_1 = require("../services/serviceRouter");
const logger_1 = require("../utils/logger");
const router = (0, express_1.Router)();
// Apply authentication to all AI routes
router.use(auth_1.authenticateRequest);
/**
 * POST /api/v1/ai/query
 * Query the AI Assistant
 */
router.post('/query', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('AI query via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('aiAssistant', '/query', {
        method: 'POST',
        headers: {
            Authorization: req.headers.authorization,
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
router.post('/chat', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('AI chat via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('aiAssistant', '/chat', {
        method: 'POST',
        headers: {
            Authorization: req.headers.authorization,
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
router.get('/history', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching AI history via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('aiAssistant', '/history', {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
        },
        cache: true,
        cacheTtl: 60,
    });
    res.json(result);
}));
exports.default = router;
//# sourceMappingURL=ai.js.map