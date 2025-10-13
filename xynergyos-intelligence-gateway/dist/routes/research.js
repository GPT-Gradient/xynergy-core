"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const auth_1 = require("../middleware/auth");
const tenantEnforcement_1 = require("../middleware/tenantEnforcement");
const checkPermission_1 = require("../middleware/checkPermission");
const serviceRouter_1 = require("../services/serviceRouter");
const logger_1 = require("../utils/logger");
const router = (0, express_1.Router)();
// Apply authentication and tenant enforcement to all research routes
router.use(auth_1.authenticateRequest);
router.use(tenantEnforcement_1.enforceTenant);
/**
 * GET /api/v1/research-sessions
 * List all research sessions
 * Permission: research.read
 */
router.get('/', (0, checkPermission_1.checkPermission)('research.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching research sessions via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('researchCoordinator', '/api/v1/research/sessions', {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        params: req.query,
        cache: true,
        cacheTtl: 60,
    });
    res.json(result);
}));
/**
 * POST /api/v1/research-sessions
 * Create a new research session
 * Permission: research.write
 */
router.post('/', (0, checkPermission_1.checkPermission)('research.write'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Creating research session via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('researchCoordinator', '/api/v1/research/sessions', {
        method: 'POST',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
            'Content-Type': 'application/json',
        },
        data: req.body,
    });
    res.status(201).json(result);
}));
/**
 * GET /api/v1/research-sessions/:id
 * Get a specific research session
 * Permission: research.read
 */
router.get('/:id', (0, checkPermission_1.checkPermission)('research.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    logger_1.logger.info('Fetching research session via gateway', {
        sessionId: id,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('researchCoordinator', `/api/v1/research/sessions/${id}`, {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        cache: true,
        cacheTtl: 60,
    });
    res.json(result);
}));
/**
 * PATCH /api/v1/research-sessions/:id
 * Update a research session
 * Permission: research.write
 */
router.patch('/:id', (0, checkPermission_1.checkPermission)('research.write'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    logger_1.logger.info('Updating research session via gateway', {
        sessionId: id,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('researchCoordinator', `/api/v1/research/sessions/${id}`, {
        method: 'PATCH',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
            'Content-Type': 'application/json',
        },
        data: req.body,
    });
    res.json(result);
}));
/**
 * POST /api/v1/research-sessions/:id/complete
 * Complete a research session
 * Permission: research.write
 */
router.post('/:id/complete', (0, checkPermission_1.checkPermission)('research.write'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    logger_1.logger.info('Completing research session via gateway', {
        sessionId: id,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('researchCoordinator', `/api/v1/research/sessions/${id}/complete`, {
        method: 'POST',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
            'Content-Type': 'application/json',
        },
        data: req.body,
    });
    res.json(result);
}));
/**
 * DELETE /api/v1/research-sessions/:id
 * Delete a research session
 * Permission: research.delete
 */
router.delete('/:id', (0, checkPermission_1.checkPermission)('research.delete'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    logger_1.logger.info('Deleting research session via gateway', {
        sessionId: id,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('researchCoordinator', `/api/v1/research/sessions/${id}`, {
        method: 'DELETE',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
    });
    res.status(204).send();
}));
exports.default = router;
//# sourceMappingURL=research.js.map