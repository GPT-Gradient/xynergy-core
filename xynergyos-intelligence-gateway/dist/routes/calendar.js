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
// Apply authentication and tenant enforcement to all calendar routes
router.use(auth_1.authenticateRequest);
router.use(tenantEnforcement_1.enforceTenant);
/**
 * GET /api/v2/calendar/events
 * List calendar events
 * Permission: calendar.read
 */
router.get('/events', (0, checkPermission_1.checkPermission)('calendar.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Fetching calendar events via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('calendarIntelligence', '/api/v1/calendar/events', {
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
 * GET /api/v2/calendar/events/:id
 * Get a specific event
 * Permission: calendar.read
 */
router.get('/events/:id', (0, checkPermission_1.checkPermission)('calendar.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    logger_1.logger.info('Fetching calendar event via gateway', {
        eventId: id,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('calendarIntelligence', `/api/v1/calendar/events/${id}`, {
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
 * POST /api/v2/calendar/events
 * Create a new event
 * Permission: calendar.write
 */
router.post('/events', (0, checkPermission_1.checkPermission)('calendar.write'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Creating calendar event via gateway', {
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('calendarIntelligence', '/api/v1/calendar/events', {
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
 * PATCH /api/v2/calendar/events/:id
 * Update an event
 * Permission: calendar.write
 */
router.patch('/events/:id', (0, checkPermission_1.checkPermission)('calendar.write'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    logger_1.logger.info('Updating calendar event via gateway', {
        eventId: id,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('calendarIntelligence', `/api/v1/calendar/events/${id}`, {
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
 * DELETE /api/v2/calendar/events/:id
 * Delete an event
 * Permission: calendar.delete
 */
router.delete('/events/:id', (0, checkPermission_1.checkPermission)('calendar.delete'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { id } = req.params;
    logger_1.logger.info('Deleting calendar event via gateway', {
        eventId: id,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('calendarIntelligence', `/api/v1/calendar/events/${id}`, {
        method: 'DELETE',
        headers: {
            Authorization: req.headers.authorization,
            'X-Tenant-Id': req.tenantId,
        },
    });
    res.status(204).send();
}));
/**
 * GET /api/v2/calendar/prep/:eventId
 * Get meeting prep information
 * Permission: calendar.read
 */
router.get('/prep/:eventId', (0, checkPermission_1.checkPermission)('calendar.read'), (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { eventId } = req.params;
    logger_1.logger.info('Fetching meeting prep via gateway', {
        eventId,
        userId: req.user?.uid,
        tenantId: req.tenantId,
        requestId: req.requestId,
    });
    const result = await serviceRouter_1.serviceRouter.callService('calendarIntelligence', `/api/v1/calendar/prep/${eventId}`, {
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
//# sourceMappingURL=calendar.js.map