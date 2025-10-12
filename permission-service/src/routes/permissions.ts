/**
 * Permission Routes
 * API endpoints for permission validation and management
 */

import { Router, Request, Response } from 'express';
import { getFirestore } from 'firebase-admin/firestore';
import { logger } from '../utils/logger';
import { getCacheService } from '../services/cache';

const router = Router();

/**
 * POST /api/v1/permissions/validate
 * Validate if user has permission for tenant
 */
router.post('/validate', async (req: Request, res: Response) => {
  try {
    const { userId, tenantId, permission } = req.body;

    if (!userId || !tenantId || !permission) {
      return res.status(400).json({
        success: false,
        error: {
          code: 'INVALID_REQUEST',
          message: 'userId, tenantId, and permission are required',
        },
      });
    }

    const db = getFirestore();
    const cache = getCacheService();
    const cacheKey = `permissions:${userId}:${tenantId}`;

    // Try cache first
    let permissions: string[] = [];
    const cached = await cache.get(cacheKey);

    if (cached) {
      permissions = JSON.parse(cached);
      logger.debug('Permission cache hit', { userId, tenantId });
    } else {
      // Fetch from Firestore
      const userDoc = await db.collection('users').doc(userId).get();

      if (!userDoc.exists) {
        return res.json({
          success: true,
          data: {
            allowed: false,
            reason: 'User not found',
          },
        });
      }

      const userData = userDoc.data();

      // Check super admin
      if (userData?.globalRole === 'super_admin' || userData?.globalRole === 'clearforge_admin') {
        return res.json({
          success: true,
          data: {
            allowed: true,
            reason: 'Super admin bypass',
          },
        });
      }

      // Get tenant permissions
      const tenantRole = userData?.tenantRoles?.[tenantId];
      permissions = tenantRole?.permissions || [];

      // Cache for 5 minutes
      await cache.set(cacheKey, JSON.stringify(permissions), 300);
    }

    // Check permission with wildcard support
    const allowed = checkPermission(permission, permissions);

    logger.info('Permission validation', {
      userId,
      tenantId,
      permission,
      allowed,
    });

    res.json({
      success: true,
      data: {
        allowed,
        reason: allowed ? undefined : 'Permission denied',
      },
    });
  } catch (error) {
    logger.error('Error validating permission', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Error validating permission',
      },
    });
  }
});

/**
 * GET /api/v1/permissions/user/:userId/tenant/:tenantId
 * Get all permissions for user in tenant
 */
router.get('/user/:userId/tenant/:tenantId', async (req: Request, res: Response) => {
  try {
    const { userId, tenantId } = req.params;

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
    const tenantRole = userData?.tenantRoles?.[tenantId];

    if (!tenantRole) {
      return res.json({
        success: true,
        data: {
          permissions: [],
          role: null,
        },
      });
    }

    res.json({
      success: true,
      data: {
        permissions: tenantRole.permissions || [],
        role: tenantRole.role,
        grantedAt: tenantRole.grantedAt,
        grantedBy: tenantRole.grantedBy,
      },
    });
  } catch (error) {
    logger.error('Error fetching user permissions', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'FETCH_ERROR',
        message: 'Error fetching permissions',
      },
    });
  }
});

/**
 * Helper function to check permission with wildcard support
 */
function checkPermission(required: string, userPermissions: string[]): boolean {
  return userPermissions.some(perm => {
    // Super wildcard
    if (perm === '*') return true;

    // Exact match
    if (perm === required) return true;

    // Wildcard match
    if (perm.endsWith('.*')) {
      const prefix = perm.slice(0, -2);
      return required.startsWith(prefix + '.');
    }

    return false;
  });
}

export default router;
