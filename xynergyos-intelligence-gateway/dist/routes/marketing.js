"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const auth_1 = require("../middleware/auth");
const serviceRouter_1 = require("../services/serviceRouter");
const logger_1 = require("../utils/logger");
const router = (0, express_1.Router)();
// Apply authentication to all Marketing routes
router.use(auth_1.authenticateRequest);
/**
 * POST /api/v1/marketing/campaign
 * Create marketing campaign
 */
router.post('/campaign', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Creating marketing campaign via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('marketingEngine', '/generate-campaign', {
        method: 'POST',
        headers: {
            Authorization: req.headers.authorization,
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
router.get('/campaigns', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching marketing campaigns via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('marketingEngine', '/campaigns', {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
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
router.post('/content', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Generating marketing content via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('marketingEngine', '/generate-content', {
        method: 'POST',
        headers: {
            Authorization: req.headers.authorization,
        },
        data: req.body,
        timeout: 120000,
    });
    res.json(result);
}));
exports.default = router;
//# sourceMappingURL=marketing.js.map