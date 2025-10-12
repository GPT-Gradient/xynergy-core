/**
 * Phase Transition Routes
 */

import { Router, Request, Response } from 'express';
import { PhaseTransitionService } from '../services/phaseTransitionService';
import { logger } from '../utils/logger';

const router = Router();
const phaseService = new PhaseTransitionService();

/**
 * GET /api/v1/beta/projects/:id/phase-status
 * Check if project can transition to next phase
 */
router.get('/:id/phase-status', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    const status = await phaseService.checkTransitionCriteria(id);

    res.json({
      success: true,
      data: status,
    });
  } catch (error: any) {
    logger.error('Error in GET /projects/:id/phase-status', { error });

    const statusCode = error.message === 'Project not found' ? 404 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'PROJECT_NOT_FOUND' : 'PHASE_STATUS_FAILED',
        message: error.message || 'Failed to check phase status',
      },
    });
  }
});

/**
 * POST /api/v1/beta/projects/:id/transition
 * Transition project to next phase (admin)
 */
router.post('/:id/transition', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { newPhase, triggeredBy, reason, notifyUsers } = req.body;

    if (!newPhase || !triggeredBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'newPhase and triggeredBy are required',
        },
      });
    }

    const result = await phaseService.transitionPhase({
      projectId: id,
      newPhase,
      triggeredBy,
      reason,
      notifyUsers: notifyUsers !== false, // Default to true
    });

    res.json({
      success: true,
      data: result,
      message: `Transitioned from ${result.oldPhase} to ${result.newPhase}. Updated ${result.usersUpdated} users.`,
    });
  } catch (error: any) {
    logger.error('Error in POST /projects/:id/transition', { error });

    const statusCode = error.message.includes('not found') ? 404 : 400;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'PROJECT_NOT_FOUND' : 'TRANSITION_FAILED',
        message: error.message || 'Failed to transition phase',
      },
    });
  }
});

/**
 * POST /api/v1/beta/projects/:id/rollback
 * Rollback phase transition (admin, emergency use)
 */
router.post('/:id/rollback', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { rolledBackBy } = req.body;

    if (!rolledBackBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'rolledBackBy is required',
        },
      });
    }

    const result = await phaseService.rollbackTransition(id, rolledBackBy);

    res.json({
      success: true,
      data: result,
      message: result.message,
    });
  } catch (error: any) {
    logger.error('Error in POST /projects/:id/rollback', { error });

    const statusCode = error.message.includes('not found') ? 404 : 400;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'PROJECT_NOT_FOUND' : 'ROLLBACK_FAILED',
        message: error.message || 'Failed to rollback transition',
      },
    });
  }
});

/**
 * GET /api/v1/beta/phases/stats
 * Get statistics for all phases
 */
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const stats = await phaseService.getPhaseStats();

    res.json({
      success: true,
      data: stats,
    });
  } catch (error: any) {
    logger.error('Error in GET /phases/stats', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'PHASE_STATS_FAILED',
        message: error.message || 'Failed to fetch phase stats',
      },
    });
  }
});

export default router;
