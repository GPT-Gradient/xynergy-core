/**
 * Entity Management Routes
 */

import { Router, Request, Response } from 'express';
import { EntityService } from '../services/entityService';
import { logger } from '../utils/logger';

const router = Router();
const entityService = new EntityService();

/**
 * POST /api/v1/entities
 * Create new business entity
 */
router.post('/', async (req: Request, res: Response) => {
  try {
    const { name, description, category, continuumGeneration, features, metadata, createdBy } = req.body;

    if (!name || !description || !category || !createdBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'name, description, category, and createdBy are required',
        },
      });
    }

    const entity = await entityService.createEntity({
      name,
      description,
      category,
      continuumGeneration,
      features,
      metadata,
      createdBy,
    });

    res.status(201).json({
      success: true,
      data: entity,
    });
  } catch (error: any) {
    logger.error('Error in POST /entities', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'ENTITY_CREATION_FAILED',
        message: error.message || 'Failed to create entity',
      },
    });
  }
});

/**
 * GET /api/v1/entities
 * List all entities with optional filters
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    const { category, status, lifecycleState, limit } = req.query;

    const entities = await entityService.listEntities({
      category: category as string,
      status: status as string,
      lifecycleState: lifecycleState as string,
      limit: limit ? parseInt(limit as string) : undefined,
    });

    res.json({
      success: true,
      data: entities,
      count: entities.length,
    });
  } catch (error: any) {
    logger.error('Error in GET /entities', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'ENTITY_LIST_FAILED',
        message: error.message || 'Failed to list entities',
      },
    });
  }
});

/**
 * GET /api/v1/entities/:id
 * Get entity by ID
 */
router.get('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    const entity = await entityService.getEntity(id);

    if (!entity) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'ENTITY_NOT_FOUND',
          message: 'Entity not found',
        },
      });
    }

    res.json({
      success: true,
      data: entity,
    });
  } catch (error: any) {
    logger.error('Error in GET /entities/:id', { error, id: req.params.id });
    res.status(500).json({
      success: false,
      error: {
        code: 'ENTITY_FETCH_FAILED',
        message: error.message || 'Failed to fetch entity',
      },
    });
  }
});

/**
 * PATCH /api/v1/entities/:id
 * Update entity
 */
router.patch('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { name, description, lifecycleState, status, features, metadata, updatedBy } = req.body;

    if (!updatedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'updatedBy is required',
        },
      });
    }

    const entity = await entityService.updateEntity(id, {
      name,
      description,
      lifecycleState,
      status,
      features,
      metadata,
      updatedBy,
    });

    res.json({
      success: true,
      data: entity,
    });
  } catch (error: any) {
    logger.error('Error in PATCH /entities/:id', { error, id: req.params.id });

    const statusCode = error.message === 'Entity not found' ? 404 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'ENTITY_NOT_FOUND' : 'ENTITY_UPDATE_FAILED',
        message: error.message || 'Failed to update entity',
      },
    });
  }
});

/**
 * DELETE /api/v1/entities/:id
 * Archive entity (soft delete)
 */
router.delete('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { archivedBy } = req.body;

    if (!archivedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'archivedBy is required',
        },
      });
    }

    await entityService.archiveEntity(id, archivedBy);

    res.json({
      success: true,
      message: 'Entity archived successfully',
    });
  } catch (error: any) {
    logger.error('Error in DELETE /entities/:id', { error, id: req.params.id });

    const statusCode = error.message === 'Entity not found' ? 404 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'ENTITY_NOT_FOUND' : 'ENTITY_ARCHIVE_FAILED',
        message: error.message || 'Failed to archive entity',
      },
    });
  }
});

export default router;
