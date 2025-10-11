import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { serviceRouter } from '../services/serviceRouter';
import { logger } from '../utils/logger';

const router = Router();

// Apply authentication to all CRM routes
router.use(authenticateRequest);

/**
 * GET /api/xynergyos/v2/crm/contacts
 * List all CRM contacts
 */
router.get('/contacts', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Fetching CRM contacts via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callCRMService('/api/v1/crm/contacts', {
    method: 'GET',
    headers: {
      Authorization: req.headers.authorization!,
    },
    cache: true,
    cacheTtl: 60, // Cache for 1 minute
  } as any);

  res.json(result);
}));

/**
 * POST /api/xynergyos/v2/crm/contacts
 * Create a new contact
 */
router.post('/contacts', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Creating CRM contact via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callCRMService('/api/v1/crm/contacts', {
    method: 'POST',
    headers: {
      Authorization: req.headers.authorization!,
    },
    data: req.body,
  });

  res.status(201).json(result);
}));

/**
 * GET /api/xynergyos/v2/crm/contacts/:contactId
 * Get a specific contact
 */
router.get('/contacts/:contactId', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { contactId } = req.params;

  logger.info('Fetching CRM contact by ID via gateway', {
    contactId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callCRMService(`/api/v1/crm/contacts/${contactId}`, {
    method: 'GET',
    headers: {
      Authorization: req.headers.authorization!,
    },
    cache: true,
    cacheTtl: 60,
  } as any);

  res.json(result);
}));

/**
 * PATCH /api/xynergyos/v2/crm/contacts/:contactId
 * Update a contact
 */
router.patch('/contacts/:contactId', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { contactId } = req.params;

  logger.info('Updating CRM contact via gateway', {
    contactId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callCRMService(`/api/v1/crm/contacts/${contactId}`, {
    method: 'PATCH',
    headers: {
      Authorization: req.headers.authorization!,
    },
    data: req.body,
  });

  res.json(result);
}));

/**
 * DELETE /api/xynergyos/v2/crm/contacts/:contactId
 * Delete a contact
 */
router.delete('/contacts/:contactId', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { contactId } = req.params;

  logger.info('Deleting CRM contact via gateway', {
    contactId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  await serviceRouter.callCRMService(`/api/v1/crm/contacts/${contactId}`, {
    method: 'DELETE',
    headers: {
      Authorization: req.headers.authorization!,
    },
  });

  res.status(204).send();
}));

/**
 * GET /api/xynergyos/v2/crm/contacts/:contactId/interactions
 * Get contact interactions
 */
router.get('/contacts/:contactId/interactions', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  const { contactId } = req.params;

  logger.info('Fetching CRM contact interactions via gateway', {
    contactId,
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callCRMService(`/api/v1/crm/contacts/${contactId}/interactions`, {
    method: 'GET',
    headers: {
      Authorization: req.headers.authorization!,
    },
  });

  res.json(result);
}));

/**
 * POST /api/xynergyos/v2/crm/interactions
 * Log a new interaction
 */
router.post('/interactions', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Logging CRM interaction via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callCRMService('/api/v1/crm/interactions', {
    method: 'POST',
    headers: {
      Authorization: req.headers.authorization!,
    },
    data: req.body,
  });

  res.status(201).json(result);
}));

/**
 * GET /api/xynergyos/v2/crm/statistics
 * Get CRM statistics
 */
router.get('/statistics', asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
  logger.info('Fetching CRM statistics via gateway', {
    userId: req.user?.uid,
    requestId: req.requestId,
  });

  const result = await serviceRouter.callCRMService('/api/v1/crm/statistics', {
    method: 'GET',
    headers: {
      Authorization: req.headers.authorization!,
    },
    cache: true,
    cacheTtl: 300, // Cache for 5 minutes
  } as any);

  res.json(result);
}));

export default router;
