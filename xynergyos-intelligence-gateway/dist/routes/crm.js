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
// Apply authentication and tenant enforcement to all CRM routes
router.use(auth_1.authenticateRequest);
router.use(tenantEnforcement_1.enforceTenant);
/**
 * GET /api/xynergyos/v2/crm/contacts
 * List all CRM contacts
 * Permission: crm.read
 */
router.get('/contacts', (0, checkPermission_1.checkPermission)('crm.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching CRM contacts via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callCRMService('/api/v1/crm/contacts', {
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
 * POST /api/xynergyos/v2/crm/contacts
 * Create a new contact
 * Permission: crm.write or crm.create
 */
router.post('/contacts', (0, checkPermission_1.checkPermission)(['crm.write', 'crm.create']), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Creating CRM contact via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callCRMService('/api/v1/crm/contacts', {
        method: 'POST',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        data: req.body,
    });
    res.status(201).json(result);
}));
/**
 * GET /api/xynergyos/v2/crm/contacts/:contactId
 * Get a specific contact
 * Permission: crm.read
 */
router.get('/contacts/:contactId', (0, checkPermission_1.checkPermission)('crm.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { contactId } = req.params;
    logger_1.logger.info('Fetching CRM contact by ID via gateway', {
        contactId,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callCRMService(`/api/v1/crm/contacts/${contactId}`, {
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
 * PATCH /api/xynergyos/v2/crm/contacts/:contactId
 * Update a contact
 * Permission: crm.write or crm.update
 */
router.patch('/contacts/:contactId', (0, checkPermission_1.checkPermission)(['crm.write', 'crm.update']), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { contactId } = req.params;
    logger_1.logger.info('Updating CRM contact via gateway', {
        contactId,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callCRMService(`/api/v1/crm/contacts/${contactId}`, {
        method: 'PATCH',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        data: req.body,
    });
    res.json(result);
}));
/**
 * DELETE /api/xynergyos/v2/crm/contacts/:contactId
 * Delete a contact
 * Permission: crm.delete
 */
router.delete('/contacts/:contactId', (0, checkPermission_1.checkPermission)('crm.delete'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { contactId } = req.params;
    logger_1.logger.info('Deleting CRM contact via gateway', {
        contactId,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    await serviceRouter_1.serviceRouter.callCRMService(`/api/v1/crm/contacts/${contactId}`, {
        method: 'DELETE',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
    });
    res.status(204).send();
}));
/**
 * GET /api/xynergyos/v2/crm/contacts/:contactId/interactions
 * Get contact interactions
 * Permission: crm.read
 */
router.get('/contacts/:contactId/interactions', (0, checkPermission_1.checkPermission)('crm.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { contactId } = req.params;
    logger_1.logger.info('Fetching CRM contact interactions via gateway', {
        contactId,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callCRMService(`/api/v1/crm/contacts/${contactId}/interactions`, {
        method: 'GET',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
    });
    res.json(result);
}));
/**
 * POST /api/xynergyos/v2/crm/interactions
 * Log a new interaction
 * Permission: crm.write
 */
router.post('/interactions', (0, checkPermission_1.checkPermission)('crm.write'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Logging CRM interaction via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callCRMService('/api/v1/crm/interactions', {
        method: 'POST',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
        data: req.body,
    });
    res.status(201).json(result);
}));
/**
 * GET /api/xynergyos/v2/crm/statistics
 * Get CRM statistics
 * Permission: crm.read
 */
router.get('/statistics', (0, checkPermission_1.checkPermission)('crm.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching CRM statistics via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callCRMService('/api/v1/crm/statistics', {
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
//# sourceMappingURL=crm.js.map