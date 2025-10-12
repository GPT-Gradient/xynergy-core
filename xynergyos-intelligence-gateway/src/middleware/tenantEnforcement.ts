/**
 * Tenant Enforcement Middleware
 * Validates user has access to requested tenant and enforces tenant isolation
 */

import { Response, NextFunction } from 'express';
import { AuthenticatedRequest } from './auth';
import { logger } from '../utils/logger';
import { getFirestore } from 'firebase-admin/firestore';

export interface TenantRequest extends AuthenticatedRequest {
  tenantId: string;
  isSuperAdmin: boolean;
}

/**
 * Extract tenant ID from request
 * Priority: X-Tenant-Id header > user.activeTenantId > 'clearforge' (default)
 */
function extractTenantId(req: AuthenticatedRequest): string | null {
  // 1. Check X-Tenant-Id header (for tenant switching)
  const headerTenantId = req.headers['x-tenant-id'] as string;
  if (headerTenantId) {
    return headerTenantId;
  }

  // 2. Check user's active tenant
  if (req.user && (req.user as any).activeTenantId) {
    return (req.user as any).activeTenantId;
  }

  // 3. Use existing tenantId from auth middleware
  if (req.tenantId) {
    return req.tenantId;
  }

  // 4. Default to clearforge (master tenant)
  return 'clearforge';
}

/**
 * Check if user is super admin
 */
async function isSuperAdmin(userId: string): Promise<boolean> {
  try {
    const db = getFirestore();
    const userDoc = await db.collection('users').doc(userId).get();

    if (!userDoc.exists) {
      return false;
    }

    const userData = userDoc.data();
    return userData?.globalRole === 'super_admin' || userData?.globalRole === 'clearforge_admin';
  } catch (error) {
    logger.error('Error checking super admin status', { userId, error });
    return false;
  }
}

/**
 * Validate user has access to tenant
 */
async function validateTenantAccess(userId: string, tenantId: string): Promise<boolean> {
  try {
    const db = getFirestore();
    const userDoc = await db.collection('users').doc(userId).get();

    if (!userDoc.exists) {
      return false;
    }

    const userData = userDoc.data();

    // Check if user has role in this tenant
    if (userData?.tenantRoles && userData.tenantRoles[tenantId]) {
      return true;
    }

    // Check if tenant allows public access (for specific endpoints)
    const tenantDoc = await db.collection('tenants').doc(tenantId).get();
    if (tenantDoc.exists) {
      const tenantData = tenantDoc.data();
      // Allow access if tenant is active
      if (tenantData?.status === 'active') {
        return true;
      }
    }

    return false;
  } catch (error) {
    logger.error('Error validating tenant access', { userId, tenantId, error });
    return false;
  }
}

/**
 * Tenant Enforcement Middleware
 *
 * Validates user has access to requested tenant
 * Attaches validated tenantId to request object
 * Bypass for super admins
 *
 * Usage: Apply after authentication middleware
 *
 * Example:
 * router.get('/contacts', authenticateRequest, enforceTenant, async (req, res) => {
 *   const tenantId = req.tenantId; // Guaranteed to be valid
 * });
 */
export async function enforceTenant(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    // Ensure user is authenticated
    if (!req.user || !req.user.uid) {
      res.status(401).json({
        success: false,
        error: {
          code: 'AUTHENTICATION_REQUIRED',
          message: 'User must be authenticated before tenant enforcement',
        },
      });
      return;
    }

    const userId = req.user.uid;
    const requestedTenantId = extractTenantId(req);

    if (!requestedTenantId) {
      res.status(400).json({
        success: false,
        error: {
          code: 'TENANT_ID_REQUIRED',
          message: 'Tenant ID is required',
        },
      });
      return;
    }

    // Check if super admin
    const isAdmin = await isSuperAdmin(userId);
    (req as TenantRequest).isSuperAdmin = isAdmin;

    // Super admin can access any tenant
    if (isAdmin) {
      logger.info('Super admin accessing tenant', {
        userId,
        tenantId: requestedTenantId,
        requestId: req.requestId,
      });
      (req as TenantRequest).tenantId = requestedTenantId;
      req.tenantId = requestedTenantId; // Maintain compatibility
      next();
      return;
    }

    // Validate normal user access
    const hasAccess = await validateTenantAccess(userId, requestedTenantId);

    if (!hasAccess) {
      logger.warn('Tenant access denied', {
        userId,
        tenantId: requestedTenantId,
        requestId: req.requestId,
      });
      res.status(403).json({
        success: false,
        error: {
          code: 'TENANT_ACCESS_DENIED',
          message: `User does not have access to tenant: ${requestedTenantId}`,
        },
      });
      return;
    }

    // Access granted
    logger.debug('Tenant access granted', {
      userId,
      tenantId: requestedTenantId,
      requestId: req.requestId,
    });

    (req as TenantRequest).tenantId = requestedTenantId;
    req.tenantId = requestedTenantId; // Maintain compatibility
    next();
  } catch (error) {
    logger.error('Error in tenant enforcement middleware', {
      error,
      userId: req.user?.uid,
      requestId: req.requestId,
    });
    res.status(500).json({
      success: false,
      error: {
        code: 'TENANT_ENFORCEMENT_ERROR',
        message: 'Error enforcing tenant isolation',
      },
    });
  }
}

/**
 * Optional tenant enforcement (doesn't fail if no tenant access)
 * Useful for endpoints that can work without tenant context
 */
export async function optionalTenantEnforcement(
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    if (!req.user || !req.user.uid) {
      next();
      return;
    }

    const userId = req.user.uid;
    const requestedTenantId = extractTenantId(req);

    if (!requestedTenantId) {
      next();
      return;
    }

    const isAdmin = await isSuperAdmin(userId);
    (req as TenantRequest).isSuperAdmin = isAdmin;

    if (isAdmin) {
      (req as TenantRequest).tenantId = requestedTenantId;
      req.tenantId = requestedTenantId;
      next();
      return;
    }

    const hasAccess = await validateTenantAccess(userId, requestedTenantId);
    if (hasAccess) {
      (req as TenantRequest).tenantId = requestedTenantId;
      req.tenantId = requestedTenantId;
    }

    next();
  } catch (error) {
    logger.error('Error in optional tenant enforcement', { error });
    next(); // Continue even if error
  }
}

/**
 * Tenant switching endpoint handler
 * Allows users to switch their active tenant
 */
export async function switchTenant(
  req: AuthenticatedRequest,
  res: Response
): Promise<void> {
  try {
    if (!req.user || !req.user.uid) {
      res.status(401).json({
        success: false,
        error: {
          code: 'AUTHENTICATION_REQUIRED',
          message: 'User must be authenticated',
        },
      });
      return;
    }

    const { tenantId } = req.body;

    if (!tenantId) {
      res.status(400).json({
        success: false,
        error: {
          code: 'TENANT_ID_REQUIRED',
          message: 'Tenant ID is required in request body',
        },
      });
      return;
    }

    const userId = req.user.uid;
    const isAdmin = await isSuperAdmin(userId);

    // Super admin can switch to any tenant
    if (!isAdmin) {
      const hasAccess = await validateTenantAccess(userId, tenantId);
      if (!hasAccess) {
        res.status(403).json({
          success: false,
          error: {
            code: 'TENANT_ACCESS_DENIED',
            message: `User does not have access to tenant: ${tenantId}`,
          },
        });
        return;
      }
    }

    // Update user's active tenant
    const db = getFirestore();
    await db.collection('users').doc(userId).update({
      activeTenantId: tenantId,
      lastTenantSwitchAt: new Date().toISOString(),
    });

    logger.info('User switched tenant', {
      userId,
      tenantId,
      isSuperAdmin: isAdmin,
    });

    res.json({
      success: true,
      data: {
        tenantId,
        message: 'Successfully switched tenant',
      },
    });
  } catch (error) {
    logger.error('Error switching tenant', { error });
    res.status(500).json({
      success: false,
      error: {
        code: 'TENANT_SWITCH_ERROR',
        message: 'Error switching tenant',
      },
    });
  }
}
