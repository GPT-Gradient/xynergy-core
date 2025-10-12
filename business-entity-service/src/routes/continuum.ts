/**
 * Continuum Management Routes
 */

import { Router, Request, Response } from 'express';
import { ContinuumService } from '../services/continuumService';
import { logger } from '../utils/logger';

const router = Router();
const continuumService = new ContinuumService();

/**
 * GET /api/v1/continuum/slots
 * Get current state of all 6 Continuum slots
 */
router.get('/slots', async (req: Request, res: Response) => {
  try {
    const slots = await continuumService.getSlots();

    res.json({
      success: true,
      data: slots,
    });
  } catch (error: any) {
    logger.error('Error in GET /continuum/slots', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'SLOTS_FETCH_FAILED',
        message: error.message || 'Failed to fetch Continuum slots',
      },
    });
  }
});

/**
 * POST /api/v1/continuum
 * Create new Continuum project
 */
router.post('/', async (req: Request, res: Response) => {
  try {
    const { name, description, continuumGeneration, features, metadata, createdBy } = req.body;

    if (!name || !description || !createdBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'name, description, and createdBy are required',
        },
      });
    }

    const entity = await continuumService.createContinuumProject({
      name,
      description,
      category: 'continuum',
      continuumGeneration: continuumGeneration || 1,
      features,
      metadata,
      createdBy,
    });

    res.status(201).json({
      success: true,
      data: entity,
    });
  } catch (error: any) {
    logger.error('Error in POST /continuum', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'CONTINUUM_CREATION_FAILED',
        message: error.message || 'Failed to create Continuum project',
      },
    });
  }
});

/**
 * POST /api/v1/continuum/:id/graduate
 * Graduate a Continuum project
 */
router.post('/:id/graduate', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { reason, notes, graduatedBy } = req.body;

    if (!graduatedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'graduatedBy is required',
        },
      });
    }

    const entity = await continuumService.graduateProject({
      entityId: id,
      reason,
      notes,
      graduatedBy,
    });

    res.json({
      success: true,
      data: entity,
      message: 'Project graduated successfully',
    });
  } catch (error: any) {
    logger.error('Error in POST /continuum/:id/graduate', { error, id: req.params.id });

    const statusCode = error.message.includes('not found') ? 404 : 400;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'ENTITY_NOT_FOUND' : 'GRADUATION_FAILED',
        message: error.message || 'Failed to graduate project',
      },
    });
  }
});

/**
 * POST /api/v1/continuum/:id/onboard
 * Onboard a pending Continuum project to active slot
 */
router.post('/:id/onboard', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { targetSlot, notes, onboardedBy } = req.body;

    if (!onboardedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'onboardedBy is required',
        },
      });
    }

    const entity = await continuumService.onboardProject({
      entityId: id,
      targetSlot,
      notes,
      onboardedBy,
    });

    res.json({
      success: true,
      data: entity,
      message: 'Project onboarded successfully',
    });
  } catch (error: any) {
    logger.error('Error in POST /continuum/:id/onboard', { error, id: req.params.id });

    const statusCode = error.message.includes('not found') ? 404 : 400;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'ENTITY_NOT_FOUND' : 'ONBOARDING_FAILED',
        message: error.message || 'Failed to onboard project',
      },
    });
  }
});

/**
 * GET /api/v1/continuum/generations
 * Get all generations summary
 */
router.get('/generations', async (req: Request, res: Response) => {
  try {
    const generations = await continuumService.getGenerations();

    res.json({
      success: true,
      data: generations,
    });
  } catch (error: any) {
    logger.error('Error in GET /continuum/generations', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'GENERATIONS_FETCH_FAILED',
        message: error.message || 'Failed to fetch generations',
      },
    });
  }
});

/**
 * GET /api/v1/continuum/generations/:generation
 * Get all projects in a specific generation
 */
router.get('/generations/:generation', async (req: Request, res: Response) => {
  try {
    const generation = parseInt(req.params.generation);

    if (isNaN(generation) || generation < 1) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid generation number',
        },
      });
    }

    const projects = await continuumService.getByGeneration(generation);

    res.json({
      success: true,
      data: projects,
      count: projects.length,
    });
  } catch (error: any) {
    logger.error('Error in GET /continuum/generations/:generation', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'GENERATION_FETCH_FAILED',
        message: error.message || 'Failed to fetch generation projects',
      },
    });
  }
});

export default router;
