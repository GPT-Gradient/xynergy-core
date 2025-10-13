"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const auth_1 = require("../middleware/auth");
const tenantEnforcement_1 = require("../middleware/tenantEnforcement");
const checkPermission_1 = require("../middleware/checkPermission");
const serviceRouter_1 = require("../services/serviceRouter");
const logger_1 = require("../utils/logger");
const errorHandler_2 = require("../middleware/errorHandler");
const websocket_1 = require("../services/websocket");
const router = (0, express_1.Router)();
// Apply authentication and tenant enforcement to all Gmail routes
router.use(auth_1.authenticateRequest);
router.use(tenantEnforcement_1.enforceTenant);
/**
 * GET /api/xynergyos/v2/gmail/messages
 * List Gmail messages
 * Permission: gmail.read
 */
router.get('/messages', (0, checkPermission_1.checkPermission)('gmail.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const maxResults = req.query.maxResults || '20';
    const query = req.query.q;
    logger_1.logger.info('Fetching Gmail messages via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        maxResults,
        query,
        requestId: req.requestId,
    });
    const queryString = query ? `?maxResults=${maxResults}&q=${encodeURIComponent(query)}` : `?maxResults=${maxResults}`;
    const result = await serviceRouter_1.serviceRouter.callService('gmailIntelligence', `/api/v1/gmail/messages${queryString}`, {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        cache: true,
        cacheTtl: 60, // Cache for 1 minute
    });
    res.json(result);
}));
/**
 * GET /api/xynergyos/v2/gmail/messages/:messageId
 * Get Gmail message details
 * Permission: gmail.read
 */
router.get('/messages/:messageId', (0, checkPermission_1.checkPermission)('gmail.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { messageId } = req.params;
    logger_1.logger.info('Fetching Gmail message via gateway', {
        messageId,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('gmailIntelligence', `/api/v1/gmail/messages/${messageId}`, {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        cache: true,
        cacheTtl: 300, // Cache for 5 minutes (messages don't change)
    });
    res.json(result);
}));
/**
 * POST /api/xynergyos/v2/gmail/messages
 * Send an email
 * Permission: gmail.write
 */
router.post('/messages', (0, checkPermission_1.checkPermission)('gmail.write'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { to, subject, body, cc, bcc } = req.body;
    if (!to || !subject || !body) {
        throw new errorHandler_2.ValidationError('to, subject, and body are required');
    }
    logger_1.logger.info('Sending Gmail message via gateway', {
        to,
        subject,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('gmailIntelligence', '/api/v1/gmail/messages', {
        method: 'POST',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        data: { to, subject, body, cc, bcc },
    });
    // Broadcast WebSocket event for real-time updates
    const ws = (0, websocket_1.getWebSocketService)();
    ws.broadcast(req.tenantId, 'gmail', 'email:sent', {
        to,
        subject,
        userId: req.user?.uid,
        timestamp: new Date().toISOString(),
    });
    res.json(result);
}));
/**
 * GET /api/xynergyos/v2/gmail/search
 * Search Gmail messages
 * Permission: gmail.read
 */
router.get('/search', (0, checkPermission_1.checkPermission)('gmail.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const query = req.query.q;
    const maxResults = req.query.maxResults || '20';
    if (!query) {
        throw new errorHandler_2.ValidationError('Search query (q) is required');
    }
    logger_1.logger.info('Searching Gmail messages via gateway', {
        query,
        maxResults,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('gmailIntelligence', `/api/v1/gmail/search?q=${encodeURIComponent(query)}&maxResults=${maxResults}`, {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        cache: true,
        cacheTtl: 60, // Cache for 1 minute
    });
    res.json(result);
}));
/**
 * GET /api/xynergyos/v2/gmail/threads/:threadId
 * Get email thread
 * Permission: gmail.read
 */
router.get('/threads/:threadId', (0, checkPermission_1.checkPermission)('gmail.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { threadId } = req.params;
    logger_1.logger.info('Fetching Gmail thread via gateway', {
        threadId,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('gmailIntelligence', `/api/v1/gmail/threads/${threadId}`, {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        cache: true,
        cacheTtl: 300, // Cache for 5 minutes
    });
    res.json(result);
}));
/**
 * GET /api/xynergyos/v2/gmail/status
 * Get Gmail connection status
 * Permission: gmail.read
 */
router.get('/status', (0, checkPermission_1.checkPermission)('gmail.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Checking Gmail status via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('gmailIntelligence', '/api/v1/gmail/status', {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        cache: false, // Don't cache status checks
    });
    res.json(result);
}));
exports.default = router;
//# sourceMappingURL=gmail.js.map