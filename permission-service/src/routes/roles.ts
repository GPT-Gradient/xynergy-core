/**
 * Role Management Routes
 * API endpoints for assigning and managing user roles
 */

import { Router, Request, Response } from 'express';
import { getFirestore, FieldValue } from 'firebase-admin/firestore';
import { logger } from '../utils/logger';
import { invalidateCache } from '../services/cache';

const router = Router();

/**
 * POST /api/v1/permissions/roles/assign
 * Assign role to user for tenant
 */
router.post('/assign', async (req: Request, res: Response) => {
  try {
    const { userId, tenantId, role, permissions, grantedBy } = req.body;

    if (!userId || !tenantId || !role || !permissions || !grantedBy) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'INVALID_REQUEST',
          message: 'userId, tenantId, role, permissions, and grantedBy are required',
        },
      });
    }

    const db = getFirestore();

    // Update user's tenant roles
    await db.collection('users').doc(userId).set(
      {
        tenantRoles: {
          [tenantId]: {
            role,
            permissions,
            grantedAt: new Date().toISOString(),
            grantedBy,
          },
        },
      },
      { merge: true }
    );

    // Invalidate permission cache
    await invalidateCache(`permissions:${userId}:${tenantId}`);

    logger.info('Role assigned', {
      userId,
      tenantId,
      role,
      grantedBy,
    });

    res.json({
      success: true,
      data: {
        message: 'Role assigned successfully',
      },
    });
  } catch (error) {
    logger.error('Error assigning role', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'ASSIGN_ERROR',
        message: 'Error assigning role',
      },
    });
  }
});

/**
 * DELETE /api/v1/permissions/roles/:userId/:tenantId
 * Remove role from user for tenant
 */
router.delete('/:userId/:tenantId', async (req: Request, res: Response) => {
  try {
    const { userId, tenantId } = req.params;

    const db = getFirestore();

    // Remove tenant role
    await db.collection('users').doc(userId).update({
      [`tenantRoles.${tenantId}`]: FieldValue.delete(),
    });

    // Invalidate permission cache
    await invalidateCache(`permissions:${userId}:${tenantId}`);

    logger.info('Role removed', {
      userId,
      tenantId,
    });

    res.json({
      success: true,
      data: {
        message: 'Role removed successfully',
      },
    });
  } catch (error) {
    logger.error('Error removing role', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'REMOVE_ERROR',
        message: 'Error removing role',
      },
    });
  }
});

/**
 * GET /api/v1/permissions/roles/:userId
 * Get all roles for user across all tenants
 */
router.get('/:userId', async (req: Request, res: Response) => {
  try {
    const { userId } = req.params;

    const db = getFirestore();
    const userDoc = await db.collection('users').doc(userId).get();

    if (!userDoc.exists) {
      return res.status(404).json({
        success: false,
        error: {
          code: 'USER_NOT_FOUND',
          message: 'User not found',
        },
      });
    }

    const userData = userDoc.data();

    res.json({
      success: true,
      data: {
        globalRole: userData?.globalRole || null,
        tenantRoles: userData?.tenantRoles || {},
      },
    });
  } catch (error) {
    logger.error('Error fetching user roles', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'FETCH_ERROR',
        message: 'Error fetching roles',
      },
    });
  }
});

export default router;
