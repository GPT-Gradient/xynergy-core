import { Router, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { enforceTenant, TenantRequest } from '../middleware/tenantEnforcement';
import { checkPermission } from '../middleware/checkPermission';
import { serviceRouter } from '../services/serviceRouter';
import { logger } from '../utils/logger';

const router = Router();

// Apply authentication and tenant enforcement to all memory routes
router.use(authenticateRequest);
router.use(enforceTenant);

/**
 * GET /api/v1/memory/items
 * List all memory items
 * Permission: memory.read
 */
router.get('/items',
  checkPermission('memory.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Fetching memory items via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('memoryService', '/api/v1/memory/items', {
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
 * POST /api/v1/memory/items
 * Create a new memory item
 * Permission: memory.write
 */
router.post('/items',
  checkPermission('memory.write'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Creating memory item via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('memoryService', '/api/v1/memory/items', {
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
 * GET /api/v1/memory/items/:id
 * Get a specific memory item
 * Permission: memory.read
 */
router.get('/items/:id',
  checkPermission('memory.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { id } = req.params;

    logger.info('Fetching memory item via gateway', {
      memoryId: id,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('memoryService', `/api/v1/memory/items/${id}`, {
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
 * PATCH /api/v1/memory/items/:id
 * Update a memory item
 * Permission: memory.write
 */
router.patch('/items/:id',
  checkPermission('memory.write'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { id } = req.params;

    logger.info('Updating memory item via gateway', {
      memoryId: id,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('memoryService', `/api/v1/memory/items/${id}`, {
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
 * DELETE /api/v1/memory/items/:id
 * Delete a memory item
 * Permission: memory.delete
 */
router.delete('/items/:id',
  checkPermission('memory.delete'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    const { id } = req.params;

    logger.info('Deleting memory item via gateway', {
      memoryId: id,
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('memoryService', `/api/v1/memory/items/${id}`, {
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
 * POST /api/v1/memory/search
 * Search memory items
 * Permission: memory.read
 */
router.post('/search',
  checkPermission('memory.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Searching memory items via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('memoryService', '/api/v1/memory/search', {
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
 * GET /api/v1/memory/stats
 * Get memory statistics
 * Permission: memory.read
 */
router.get('/stats',
  checkPermission('memory.read'),
  asyncHandler(async (req: TenantRequest, res: Response) => {
    logger.info('Fetching memory stats via gateway', {
      userId: req.user?.uid,
      tenantId: req.tenantId,
      requestId: req.requestId,
    });

    const result = await serviceRouter.callService('memoryService', '/api/v1/memory/stats', {
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
