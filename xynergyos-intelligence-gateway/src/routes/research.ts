import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { enforceTenant, TenantRequest } from '../middleware/tenantEnforcement';
import { checkPermission } from '../middleware/checkPermission';
import { serviceRouter } from '../services/serviceRouter';
import { logger } from '../utils/logger';

const router = Router();

// Apply authentication and tenant enforcement to all research routes
router.use(authenticateRequest);
router.use(enforceTenant);

/**
 * GET /api/v1/research-sessions
 * List all research sessions
 * Permission: research.read
 */
router.get('/',
  checkPermission('research.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Fetching research sessions via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('researchCoordinator', '/api/v1/research/sessions', {
      method: 'GET',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
      },
      params: req.query,
      cache: true,
      cacheTtl: 60,
    });

    res.json(result);
  })
);

/**
 * POST /api/v1/research-sessions
 * Create a new research session
 * Permission: research.write
 */
router.post('/',
  checkPermission('research.write'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Creating research session via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('researchCoordinator', '/api/v1/research/sessions', {
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
 * GET /api/v1/research-sessions/:id
 * Get a specific research session
 * Permission: research.read
 */
router.get('/:id',
  checkPermission('research.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { id } = req.params;

    logger.info('Fetching research session via gateway', {
      sessionId: id,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('researchCoordinator', `/api/v1/research/sessions/${id}`, {
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
 * PATCH /api/v1/research-sessions/:id
 * Update a research session
 * Permission: research.write
 */
router.patch('/:id',
  checkPermission('research.write'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { id } = req.params;

    logger.info('Updating research session via gateway', {
      sessionId: id,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('researchCoordinator', `/api/v1/research/sessions/${id}`, {
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
 * POST /api/v1/research-sessions/:id/complete
 * Complete a research session
 * Permission: research.write
 */
router.post('/:id/complete',
  checkPermission('research.write'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { id } = req.params;

    logger.info('Completing research session via gateway', {
      sessionId: id,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('researchCoordinator', `/api/v1/research/sessions/${id}/complete`, {
      method: 'POST',
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
 * DELETE /api/v1/research-sessions/:id
 * Delete a research session
 * Permission: research.delete
 */
router.delete('/:id',
  checkPermission('research.delete'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { id } = req.params;

    logger.info('Deleting research session via gateway', {
      sessionId: id,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('researchCoordinator', `/api/v1/research/sessions/${id}`, {
      method: 'DELETE',
      headers: {
        Authorization: req.headers.authorization!,
        'X-Tenant-Id': req.tenantId,
      },
    });

    res.status(204).send();
  })
);

export default router;
