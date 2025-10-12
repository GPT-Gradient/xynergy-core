"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const auth_1 = require("../middleware/auth");
const crmService_1 = require("../services/crmService");
const logger_1 = require("../utils/logger");
const errorHandler_2 = require("../middleware/errorHandler");
const router = (0, express_1.Router)();
// Apply authentication to all CRM routes
router.use(auth_1.authenticateRequest);
/**
 * GET /api/v1/crm/contacts
 * List/search contacts
 */
router.get('/contacts', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const query = {
        query: req.query.q,
        type: req.query.type,
        relationshipType: req.query.relationshipType,
        status: req.query.status,
        ownerId: req.query.ownerId,
        limit: parseInt(req.query.limit) || 50,
        offset: parseInt(req.query.offset) || 0,
    };
    logger_1.logger.info('Searching contacts', {
        userId: req.user?.uid,
        query,
        requestId: req.requestId,
    });
    const result = await crmService_1.crmService.searchContacts(req.tenantId, query);
    res.json({
        success: true,
        data: result,
        timestamp: new Date().toISOString(),
    });
}));
/**
 * POST /api/v1/crm/contacts
 * Create new contact
 */
router.post('/contacts', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const data = req.body;
    if (!data.name) {
        throw new errorHandler_2.ValidationError('Contact name is required');
    }
    logger_1.logger.info('Creating contact', {
        userId: req.user?.uid,
        name: data.name,
        requestId: req.requestId,
    });
    const contact = await crmService_1.crmService.createContact(req.tenantId, req.user.uid, req.user.email || '', data);
    res.status(201).json({
        success: true,
        data: { contact },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/crm/contacts/:contactId
 * Get contact details
 */
router.get('/contacts/:contactId', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { contactId } = req.params;
    logger_1.logger.info('Getting contact', {
        contactId,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const contact = await crmService_1.crmService.getContact(req.tenantId, contactId);
    res.json({
        success: true,
        data: { contact },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * PATCH /api/v1/crm/contacts/:contactId
 * Update contact
 */
router.patch('/contacts/:contactId', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { contactId } = req.params;
    const data = req.body;
    logger_1.logger.info('Updating contact', {
        contactId,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const contact = await crmService_1.crmService.updateContact(req.tenantId, contactId, req.user.uid, data);
    res.json({
        success: true,
        data: { contact },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * DELETE /api/v1/crm/contacts/:contactId
 * Delete (archive) contact
 */
router.delete('/contacts/:contactId', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { contactId } = req.params;
    logger_1.logger.info('Deleting contact', {
        contactId,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    await crmService_1.crmService.deleteContact(req.tenantId, contactId, req.user.uid);
    res.json({
        success: true,
        message: 'Contact archived successfully',
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/crm/contacts/:contactId/interactions
 * Get contact interactions
 */
router.get('/contacts/:contactId/interactions', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { contactId } = req.params;
    const limit = parseInt(req.query.limit) || 50;
    logger_1.logger.info('Getting contact interactions', {
        contactId,
        limit,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const interactions = await crmService_1.crmService.getContactInteractions(req.tenantId, contactId, limit);
    res.json({
        success: true,
        data: {
            interactions,
            count: interactions.length,
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * POST /api/v1/crm/interactions
 * Create interaction
 */
router.post('/interactions', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const data = req.body;
    if (!data.contactId || !data.type) {
        throw new errorHandler_2.ValidationError('contactId and type are required');
    }
    logger_1.logger.info('Creating interaction', {
        contactId: data.contactId,
        type: data.type,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const interaction = await crmService_1.crmService.createInteraction(req.tenantId, data);
    res.status(201).json({
        success: true,
        data: { interaction },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/crm/contacts/:contactId/notes
 * Get contact notes
 */
router.get('/contacts/:contactId/notes', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { contactId } = req.params;
    logger_1.logger.info('Getting contact notes', {
        contactId,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const notes = await crmService_1.crmService.getContactNotes(req.tenantId, contactId);
    res.json({
        success: true,
        data: {
            notes,
            count: notes.length,
        },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * POST /api/v1/crm/contacts/:contactId/notes
 * Create note for contact
 */
router.post('/contacts/:contactId/notes', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { contactId } = req.params;
    const { content, tags } = req.body;
    if (!content) {
        throw new errorHandler_2.ValidationError('Note content is required');
    }
    logger_1.logger.info('Creating contact note', {
        contactId,
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const note = await crmService_1.crmService.createNote(req.tenantId, contactId, req.user.uid, req.user.email || '', req.user.name || '', content, tags || []);
    res.status(201).json({
        success: true,
        data: { note },
        timestamp: new Date().toISOString(),
    });
}));
/**
 * GET /api/v1/crm/statistics
 * Get CRM statistics
 */
router.get('/statistics', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    logger_1.logger.info('Getting CRM statistics', {
        userId: req.user?.uid,
        requestId: req.requestId,
    });
    const stats = await crmService_1.crmService.getStatistics(req.tenantId);
    res.json({
        success: true,
        data: stats,
        timestamp: new Date().toISOString(),
    });
}));
exports.default = router;
//# sourceMappingURL=crm.js.map