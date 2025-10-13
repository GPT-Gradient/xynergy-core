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
// Apply authentication and tenant enforcement to all memory routes
router.use(auth_1.authenticateRequest);
router.use(tenantEnforcement_1.enforceTenant);
/**
 * GET /api/v1/memory/items
 * List all memory items
 * Permission: memory.read
 */
router.get('/items', (0, checkPermission_1.checkPermission)('memory.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching memory items via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('memoryService', '/api/v1/memory/items', {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        params: req.query,
        cache: true,
        cacheTtl: 60, // Cache for 1 minute
    });
    res.json(result);
}));
/**
 * POST /api/v1/memory/items
 * Create a new memory item
 * Permission: memory.write
 */
router.post('/items', (0, checkPermission_1.checkPermission)('memory.write'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Creating memory item via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('memoryService', '/api/v1/memory/items', {
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
 * GET /api/v1/memory/items/:id
 * Get a specific memory item
 * Permission: memory.read
 */
router.get('/items/:id', (0, checkPermission_1.checkPermission)('memory.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    logger_1.logger.info('Fetching memory item via gateway', {
        memoryId: id,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('memoryService', `/api/v1/memory/items/${id}`, {
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
 * PATCH /api/v1/memory/items/:id
 * Update a memory item
 * Permission: memory.write
 */
router.patch('/items/:id', (0, checkPermission_1.checkPermission)('memory.write'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    logger_1.logger.info('Updating memory item via gateway', {
        memoryId: id,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('memoryService', `/api/v1/memory/items/${id}`, {
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
 * DELETE /api/v1/memory/items/:id
 * Delete a memory item
 * Permission: memory.delete
 */
router.delete('/items/:id', (0, checkPermission_1.checkPermission)('memory.delete'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    logger_1.logger.info('Deleting memory item via gateway', {
        memoryId: id,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('memoryService', `/api/v1/memory/items/${id}`, {
        method: 'DELETE',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
    });
    res.status(204).send();
}));
/**
 * POST /api/v1/memory/search
 * Search memory items
 * Permission: memory.read
 */
router.post('/search', (0, checkPermission_1.checkPermission)('memory.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Searching memory items via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('memoryService', '/api/v1/memory/search', {
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
 * GET /api/v1/memory/stats
 * Get memory statistics
 * Permission: memory.read
 */
router.get('/stats', (0, checkPermission_1.checkPermission)('memory.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching memory stats via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('memoryService', '/api/v1/memory/stats', {
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
exports.default = router;
//# sourceMappingURL=memory.js.map