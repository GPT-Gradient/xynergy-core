/**
 * User Management Routes (Admin)
 */

import { Router, Request, Response } from 'express';
import { UserService } from '../services/userService';
import { logger } from '../utils/logger';

const router = Router();
const userService = new UserService();

/**
 * POST /api/v1/users
 * Create new user
 */
router.post('/', async (req: Request, res: Response) => {
  try {
    const { email, name, password, globalRole, tenantId, role, permissions, createdBy } = req.body;

    if (!email || !name || !createdBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'email, name, and createdBy are required',
        },
      });
    }

    const user = await userService.createUser({
      email,
      name,
      password,
      globalRole,
      tenantId,
      role,
      permissions,
      createdBy,
    });

    res.status(201).json({
      success: true,
      data: user,
    });
  } catch (error: any) {
    logger.error('Error in POST /users', { error });

    // Handle Firebase Auth errors
    if (error.code === 'auth/email-already-exists') {
      return res.status(409).json({
        success: false,
        error: {
          code: 'EMAIL_ALREADY_EXISTS',
          message: 'A user with this email already exists',
        },
      });
    }

    res.status(500).json({
      success: false,
      error: {
        code: 'USER_CREATION_FAILED',
        message: error.message || 'Failed to create user',
      },
    });
  }
});

/**
 * GET /api/v1/users
 * List all users
 */
router.get('/', async (req: Request, res: Response) => {
  try {
    const limit = req.query.limit ? parseInt(req.query.limit as string) : 100;

    const users = await userService.listUsers(limit);

    res.json({
      success: true,
      data: users,
      count: users.length,
    });
  } catch (error: any) {
    logger.error('Error in GET /users', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'USER_LIST_FAILED',
        message: error.message || 'Failed to list users',
      },
    });
  }
});

/**
 * GET /api/v1/users/:id
 * Get user by ID
 */
router.get('/:id', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;

    const user = await userService.getUser(id);

    res.json({
      success: true,
      data: user,
    });
  } catch (error: any) {
    logger.error('Error in GET /users/:id', { error, id: req.params.id });

    const statusCode = error.message === 'User not found' ? 404 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'USER_NOT_FOUND' : 'USER_FETCH_FAILED',
        message: error.message || 'Failed to fetch user',
      },
    });
  }
});

/**
 * POST /api/v1/users/:id/tenants
 * Assign user to tenant with role
 */
router.post('/:id/tenants', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { tenantId, role, permissions, grantedBy } = req.body;

    if (!tenantId || !role || !grantedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'tenantId, role, and grantedBy are required',
        },
      });
    }

    await userService.assignTenant({
      userId: id,
      tenantId,
      role,
      permissions: permissions || [],
      grantedBy,
    });

    res.json({
      success: true,
      message: 'User assigned to tenant successfully',
    });
  } catch (error: any) {
    logger.error('Error in POST /users/:id/tenants', { error, id: req.params.id });

    const statusCode = error.message.includes('not found') ? 404 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'NOT_FOUND' : 'TENANT_ASSIGNMENT_FAILED',
        message: error.message || 'Failed to assign tenant',
      },
    });
  }
});

/**
 * DELETE /api/v1/users/:id/tenants/:tenantId
 * Remove user from tenant
 */
router.delete('/:id/tenants/:tenantId', async (req: Request, res: Response) => {
  try {
    const { id, tenantId } = req.params;
    const { removedBy } = req.body;

    if (!removedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'removedBy is required',
        },
      });
    }

    await userService.removeTenant({
      userId: id,
      tenantId,
      removedBy,
    });

    res.json({
      success: true,
      message: 'User removed from tenant successfully',
    });
  } catch (error: any) {
    logger.error('Error in DELETE /users/:id/tenants/:tenantId', { error, id: req.params.id });

    const statusCode = error.message === 'User not found' ? 404 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'USER_NOT_FOUND' : 'TENANT_REMOVAL_FAILED',
        message: error.message || 'Failed to remove tenant',
      },
    });
  }
});

/**
 * PATCH /api/v1/users/:id/global-role
 * Update user's global role
 */
router.patch('/:id/global-role', async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { globalRole, updatedBy } = req.body;

    if (!globalRole || !updatedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'VALIDATION_ERROR',
          message: 'globalRole and updatedBy are required',
        },
      });
    }

    await userService.updateGlobalRole(id, globalRole, updatedBy);

    res.json({
      success: true,
      message: 'Global role updated successfully',
    });
  } catch (error: any) {
    logger.error('Error in PATCH /users/:id/global-role', { error, id: req.params.id });

    const statusCode = error.message === 'User not found' ? 404 : 500;
    res.status(statusCode).json({
      success: false,
      error: {
        code: statusCode === 404 ? 'USER_NOT_FOUND' : 'ROLE_UPDATE_FAILED',
        message: error.message || 'Failed to update global role',
      },
    });
  }
});

export default router;
