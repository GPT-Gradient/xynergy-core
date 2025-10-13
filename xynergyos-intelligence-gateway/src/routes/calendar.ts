import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { enforceTenant, TenantRequest } from '../middleware/tenantEnforcement';
import { checkPermission } from '../middleware/checkPermission';
import { serviceRouter } from '../services/serviceRouter';
import { logger } from '../utils/logger';

const router = Router();

// Apply authentication and tenant enforcement to all calendar routes
router.use(authenticateRequest);
router.use(enforceTenant);

/**
 * GET /api/v2/calendar/events
 * List calendar events
 * Permission: calendar.read
 */
router.get('/events',
  checkPermission('calendar.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Fetching calendar events via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('calendarIntelligence', '/api/v1/calendar/events', {
      method: 'GET',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
      },
      params: req.query,
      cache: true,
      cacheTtl: 60, // Cache for 1 minute
    });

    res.json(result);
  })
);

/**
 * GET /api/v2/calendar/events/:id
 * Get a specific event
 * Permission: calendar.read
 */
router.get('/events/:id',
  checkPermission('calendar.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { id } = req.params;

    logger.info('Fetching calendar event via gateway', {
      eventId: id,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('calendarIntelligence', `/api/v1/calendar/events/${id}`, {
      method: 'GET',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
      },
      cache: true,
      cacheTtl: 60,
    });

    res.json(result);
  })
);

/**
 * POST /api/v2/calendar/events
 * Create a new event
 * Permission: calendar.write
 */
router.post('/events',
  checkPermission('calendar.write'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Creating calendar event via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('calendarIntelligence', '/api/v1/calendar/events', {
      method: 'POST',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
        'Content-Type': 'application/json',
      },
      data: req.body,
    });

    res.status(201).json(result);
  })
);

/**
 * PATCH /api/v2/calendar/events/:id
 * Update an event
 * Permission: calendar.write
 */
router.patch('/events/:id',
  checkPermission('calendar.write'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { id } = req.params;

    logger.info('Updating calendar event via gateway', {
      eventId: id,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('calendarIntelligence', `/api/v1/calendar/events/${id}`, {
      method: 'PATCH',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
        'Content-Type': 'application/json',
      },
      data: req.body,
    });

    res.json(result);
  })
);

/**
 * DELETE /api/v2/calendar/events/:id
 * Delete an event
 * Permission: calendar.delete
 */
router.delete('/events/:id',
  checkPermission('calendar.delete'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { id } = req.params;

    logger.info('Deleting calendar event via gateway', {
      eventId: id,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('calendarIntelligence', `/api/v1/calendar/events/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
      },
    });

    res.status(204).send();
  })
);

/**
 * GET /api/v2/calendar/prep/:eventId
 * Get meeting prep information
 * Permission: calendar.read
 */
router.get('/prep/:eventId',
  checkPermission('calendar.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { eventId } = req.params;

    logger.info('Fetching meeting prep via gateway', {
      eventId,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('calendarIntelligence', `/api/v1/calendar/prep/${eventId}`, {
      method: 'GET',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
      },
      cache: true,
      cacheTtl: 300, // Cache for 5 minutes
    });

    res.json(result);
  })
);

export default router;
