"use strict";
/**
 * Permission Checking Middleware
 * RBAC enforcement with wildcard support and Redis caching
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.invalidatePermissionCache = invalidatePermissionCache;
exports.checkPermission = checkPermission;
exports.checkPermissionForUser = checkPermissionForUser;
exports.getUserPermissionsForTenant = getUserPermissionsForTenant;
const logger_1 = require("../utils/logger");
const firestore_1 = require("firebase-admin/firestore");
/**
 * Check if permission matches with wildcard support
 *
 * Examples:
 * - Exact match: 'crm.read' matches 'crm.read' ✅
 * - Wildcard: 'crm.*' matches 'crm.read' ✅
 * - Wildcard: 'crm.*' matches 'crm.write' ✅
 * - Super wildcard: '*' matches everything ✅
 * - No match: 'crm.read' does not match 'crm.write' ❌
 */
function permissionMatches(required, userPermission) {
    // Super wildcard matches everything
    if (userPermission === '*') {
        return true;
    }
    // Exact match
    if (required === userPermission) {
        return true;
    }
    // Wildcard match (e.g., 'crm.*' matches 'crm.read')
    if (userPermission.endsWith('.*')) {
        const prefix = userPermission.slice(0, -2); // Remove '.*'
        return required.startsWith(prefix + '.');
    }
    return false;
}
/**
 * Get user permissions for tenant (direct Firestore lookup)
 */
async function getUserPermissions(userId, tenantId) {
    try {
        logger_1.logger.debug('Fetching user permissions from Firestore', { userId, tenantId });
        const db = (0, firestore_1.getFirestore)();
        const userDoc = await db.collection('users').doc(userId).get();
        if (!userDoc.exists) {
            return [];
        }
        const userData = userDoc.data();
        const tenantRole = userData?.tenantRoles?.[tenantId];
        if (!tenantRole || !tenantRole.permissions) {
            return [];
        }
        const permissions = Array.isArray(tenantRole.permissions)
            ? tenantRole.permissions
            : [];
        return permissions;
    }
    catch (error) {
        logger_1.logger.error('Error fetching user permissions', { userId, tenantId, error });
        return [];
    }
}
/**
 * Check if user has required permission(s)
 */
async function hasPermission(userId, tenantId, requiredPermissions, requireAll = false) {
    try {
        const userPermissions = await getUserPermissions(userId, tenantId);
        if (userPermissions.length === 0) {
            return {
                allowed: false,
                reason: 'User has no permissions for this tenant',
            };
        }
        // Check each required permission
        const matches = requiredPermissions.map(required => userPermissions.some(userPerm => permissionMatches(required, userPerm)));
        if (requireAll) {
            // AND logic: All permissions must match
            const allowed = matches.every(m => m);
            return {
                allowed,
                reason: allowed
                    ? undefined
                    : `Missing one or more required permissions: ${requiredPermissions.join(', ')}`,
            };
        }
        else {
            // OR logic: At least one permission must match
            const allowed = matches.some(m => m);
            return {
                allowed,
                reason: allowed
                    ? undefined
                    : `Missing any of required permissions: ${requiredPermissions.join(', ')}`,
            };
        }
    }
    catch (error) {
        logger_1.logger.error('Error checking permission', { userId, tenantId, error });
        return {
            allowed: false,
            reason: 'Error checking permissions',
        };
    }
}
/**
 * Log permission check to audit service
 */
async function auditPermissionCheck(userId, tenantId, permission, allowed, reason, requestId) {
    try {
        // TODO: Send to audit service via Pub/Sub
        // For now, just log it
        logger_1.logger.info('Permission check', {
            userId,
            tenantId,
            permission,
            allowed,
            reason,
            requestId,
            action: 'permission.check',
            timestamp: new Date().toISOString(),
        });
    }
    catch (error) {
        logger_1.logger.error('Error auditing permission check', { error });
    }
}
/**
 * Invalidate permission cache for user
 * Call this after role/permission changes
 * (No-op without cache - permissions fetched fresh each time)
 */
async function invalidatePermissionCache(userId, tenantId) {
    logger_1.logger.info('Permission cache invalidation requested (no-op without cache)', { userId, tenantId });
}
/**
 * Permission Checking Middleware Factory
 *
 * Creates middleware that checks if user has required permission(s)
 *
 * @param permissions - Single permission or array of permissions
 * @param options - Configuration options
 *
 * Usage:
 * // Single permission
 * router.get('/contacts',
 *   authenticateRequest,
 *   enforceTenant,
 *   checkPermission('crm.read'),
 *   handler
 * );
 *
 * // Multiple permissions (OR logic - any permission works)
 * router.post('/contacts',
 *   authenticateRequest,
 *   enforceTenant,
 *   checkPermission(['crm.create', 'crm.*']),
 *   handler
 * );
 *
 * // Multiple permissions (AND logic - all required)
 * router.delete('/contacts/:id',
 *   authenticateRequest,
 *   enforceTenant,
 *   checkPermission(['crm.delete', 'crm.admin'], { requireAll: true }),
 *   handler
 * );
 */
function checkPermission(permissions, options = {}) {
    const requiredPermissions = Array.isArray(permissions) ? permissions : [permissions];
    const { requireAll = false, skipAudit = false } = options;
    return async (req, res, next) => {
        try {
            // Ensure user is authenticated
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
            // Ensure tenant is set
            if (!req.tenantId) {
                res.status(400).json({
                    success: false,
                    error: {
                        code: 'TENANT_REQUIRED',
                        message: 'Tenant context required',
                    },
                });
                return;
            }
            const userId = req.user.uid;
            const tenantId = req.tenantId;
            // Super admin bypass
            if (req.isSuperAdmin) {
                logger_1.logger.debug('Super admin bypassing permission check', {
                    userId,
                    tenantId,
                    permissions: requiredPermissions,
                    requestId: req.requestId,
                });
                if (!skipAudit) {
                    await auditPermissionCheck(userId, tenantId, requiredPermissions.join(','), true, 'Super admin bypass', req.requestId);
                }
                next();
                return;
            }
            // Check permissions
            const result = await hasPermission(userId, tenantId, requiredPermissions, requireAll);
            if (!skipAudit) {
                await auditPermissionCheck(userId, tenantId, requiredPermissions.join(','), result.allowed, result.reason, req.requestId);
            }
            if (!result.allowed) {
                logger_1.logger.warn('Permission denied', {
                    userId,
                    tenantId,
                    permissions: requiredPermissions,
                    reason: result.reason,
                    requestId: req.requestId,
                });
                res.status(403).json({
                    success: false,
                    error: {
                        code: 'PERMISSION_DENIED',
                        message: result.reason || 'Permission denied',
                        requiredPermissions,
                    },
                });
                return;
            }
            // Permission granted
            logger_1.logger.debug('Permission granted', {
                userId,
                tenantId,
                permissions: requiredPermissions,
                requestId: req.requestId,
            });
            next();
        }
        catch (error) {
            logger_1.logger.error('Error in permission check middleware', {
                error,
                userId: req.user?.uid,
                tenantId: req.tenantId,
                permissions: requiredPermissions,
                requestId: req.requestId,
            });
            res.status(500).json({
                success: false,
                error: {
                    code: 'PERMISSION_CHECK_ERROR',
                    message: 'Error checking permissions',
                },
            });
        }
    };
}
/**
 * Check permission programmatically (not middleware)
 * Useful for conditional logic within route handlers
 */
async function checkPermissionForUser(userId, tenantId, permission) {
    const permissions = Array.isArray(permission) ? permission : [permission];
    const result = await hasPermission(userId, tenantId, permissions, false);
    return result.allowed;
}
/**
 * Get all permissions for user in tenant
 */
async function getUserPermissionsForTenant(userId, tenantId) {
    return getUserPermissions(userId, tenantId);
}
//# sourceMappingURL=checkPermission.js.map