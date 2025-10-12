/**
 * Beta User Dashboard Routes
 */

import { Router, Request, Response } from 'express';
import { LifetimeAccessService } from '../services/lifetimeAccessService';
import { logger } from '../utils/logger';

const router = Router();
const lifetimeAccessService = new LifetimeAccessService();

/**
 * GET /api/v1/beta/users/:id/benefits
 * Get user's beta benefits
 */
router.get('/:id/benefits', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    const benefits = await lifetimeAccessService.getUserBenefits(id);

    res.json({
      success: true,
      data: benefits,
    });
  } catch (error: any) {
    logger.error('Error in GET /users/:id/benefits', { error });

    const statusCode = error.message === 'User not found' ? 404 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'USER_NOT_FOUND' : 'BENEFITS_FETCH_FAILED',
        message: error.message || 'Failed to fetch user benefits',
      },
    });
  }
});

/**
 * GET /api/v1/beta/users/:id/projects
 * Get projects user has lifetime access to
 */
router.get('/:id/projects', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    const projects = await lifetimeAccessService.getUserProjects(id);

    res.json({
      success: true,
      data: projects,
      count: projects.length,
    });
  } catch (error: any) {
    logger.error('Error in GET /users/:id/projects', { error });

    const statusCode = error.message === 'User not found' ? 404 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'USER_NOT_FOUND' : 'PROJECTS_FETCH_FAILED',
        message: error.message || 'Failed to fetch user projects',
      },
    });
  }
});

/**
 * GET /api/v1/beta/stats
 * Get beta program statistics
 */
router.get('/stats', async (req: Request, res: Response) => {
  try {
    const stats = await lifetimeAccessService.getBetaUserStats();

    res.json({
      success: true,
      data: stats,
    });
  } catch (error: any) {
    logger.error('Error in GET /beta/stats', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'STATS_FETCH_FAILED',
        message: error.message || 'Failed to fetch beta stats',
      },
    });
  }
});

/**
 * POST /api/v1/beta/access/grant-all
 * Grant lifetime access to new project for all beta users (admin)
 */
router.post('/access/grant-all', async (req: Request, res: Response) => {
  try {
    const { projectId, grantedBy, notifyUsers } = req.body;

    if (!projectId || !grantedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'projectId and grantedBy are required',
        },
      });
    }

    const result = await lifetimeAccessService.grantAccessToAllBetaUsers({
      projectId,
      grantedBy,
      notifyUsers: notifyUsers !== false, // Default to true
    });

    res.json({
      success: true,
      data: result,
      message: `Lifetime access granted to ${result.usersUpdated} beta users`,
    });
  } catch (error: any) {
    logger.error('Error in POST /access/grant-all', { error });

    const statusCode = error.message === 'Project not found' ? 404 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'PROJECT_NOT_FOUND' : 'ACCESS_GRANT_FAILED',
        message: error.message || 'Failed to grant lifetime access',
      },
    });
  }
});

export default router;
