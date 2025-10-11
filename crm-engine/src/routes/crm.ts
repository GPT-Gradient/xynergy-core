import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { crmService } from '../services/crmService';
import { logger } from '../utils/logger';
import { ValidationError } from '../middleware/errorHandler';
import { CreateContactDTO, UpdateContactDTO, CreateInteractionDTO, ContactSearchQuery } from '../types/crm';

const router = Router();

// Apply authentication to all CRM routes
router.use(authenticateRequest);

/**
 * GET /api/v1/crm/contacts
 * List/search contacts
 */
router.get('/contacts', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const query: ContactSearchQuery = {
    query: req.query.q as string,
    type: req.query.type as any,
    relationshipType: req.query.relationshipType as any,
    status: req.query.status as any,
    ownerId: req.query.ownerId as string,
    limit: parseInt(req.query.limit as string) || 50,
    offset: parseInt(req.query.offset as string) || 0,
  };

  logger.info('Searching contacts', {
    userId: req.user?.uid,
    query,
    requestId: req.requestId,
  });

  const result = await crmService.searchContacts(req.tenantId!, query);

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
router.post('/contacts', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const data: CreateContactDTO = req.body;

  if (!data.name) {
    throw new ValidationError('Contact name is required');
  }

  logger.info('Creating contact', {
    userId: req.user?.uid,
    name: data.name,
    requestId: req.requestId,
  });

  const contact = await crmService.createContact(
    req.tenantId!,
    req.user!.uid,
    req.user!.email || '',
    data
  );

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
router.get('/contacts/:contactId', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { contactId } = req.params;

  logger.info('Getting contact', {
    contactId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const contact = await crmService.getContact(req.tenantId!, contactId);

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
router.patch('/contacts/:contactId', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { contactId } = req.params;
  const data: UpdateContactDTO = req.body;

  logger.info('Updating contact', {
    contactId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const contact = await crmService.updateContact(
    req.tenantId!,
    contactId,
    req.user!.uid,
    data
  );

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
router.delete('/contacts/:contactId', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { contactId } = req.params;

  logger.info('Deleting contact', {
    contactId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  await crmService.deleteContact(req.tenantId!, contactId, req.user!.uid);

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
router.get('/contacts/:contactId/interactions', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { contactId } = req.params;
  const limit = parseInt(req.query.limit as string) || 50;

  logger.info('Getting contact interactions', {
    contactId,
    limit,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const interactions = await crmService.getContactInteractions(req.tenantId!, contactId, limit);

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
router.post('/interactions', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const data: CreateInteractionDTO = req.body;

  if (!data.contactId || !data.type) {
    throw new ValidationError('contactId and type are required');
  }

  logger.info('Creating interaction', {
    contactId: data.contactId,
    type: data.type,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const interaction = await crmService.createInteraction(req.tenantId!, data);

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
router.get('/contacts/:contactId/notes', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { contactId } = req.params;

  logger.info('Getting contact notes', {
    contactId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const notes = await crmService.getContactNotes(req.tenantId!, contactId);

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
router.post('/contacts/:contactId/notes', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { contactId } = req.params;
  const { content, tags } = req.body;

  if (!content) {
    throw new ValidationError('Note content is required');
  }

  logger.info('Creating contact note', {
    contactId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const note = await crmService.createNote(
    req.tenantId!,
    contactId,
    req.user!.uid,
    req.user!.email || '',
    req.user!.name || '',
    content,
    tags || []
  );

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
router.get('/statistics', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Getting CRM statistics', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const stats = await crmService.getStatistics(req.tenantId!);

  res.json({
    success: true,
    data: stats,
    timestamp: new Date().toISOString(),
  });
}));

export default router;
