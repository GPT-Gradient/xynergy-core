"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const auth_1 = require("../middleware/auth");
const serviceRouter_1 = require("../services/serviceRouter");
const logger_1 = require("../utils/logger");
const router = (0, express_1.Router)();
// Apply authentication to all ASO routes
router.use(auth_1.authenticateRequest);
/**
 * POST /api/v1/aso/optimize
 * Run ASO optimization
 */
router.post('/optimize', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Running ASO optimization via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('asoEngine', '/optimize', {
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
 * GET /api/v1/aso/keywords
 * Get keyword recommendations
 */
router.get('/keywords', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching ASO keywords via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('asoEngine', '/keywords', {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
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
router.get('/analysis', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching ASO analysis via gateway', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('asoEngine', '/analyze', {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
        },
        params: req.query,
    });
    res.json(result);
}));
exports.default = router;
//# sourceMappingURL=aso.js.map