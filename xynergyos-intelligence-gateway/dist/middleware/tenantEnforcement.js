"use strict";
/**
 * Tenant Enforcement Middleware
 * Validates user has access to requested tenant and enforces tenant isolation
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.enforceTenant = enforceTenant;
exports.optionalTenantEnforcement = optionalTenantEnforcement;
exports.switchTenant = switchTenant;
const logger_1 = require("../utils/logger");
const firestore_1 = require("firebase-admin/firestore");
/**
 * Extract tenant ID from request
 * Priority: X-Tenant-Id header > user.activeTenantId > 'clearforge' (default)
 */
function extractTenantId(req) {
    // 1. Check X-Tenant-Id header (for tenant switching)
    const headerTenantId = req.headers['x-tenant-id'];
    if (headerTenantId) {
        return headerTenantId;
    }
    // 2. Check user's active tenant
    if (req.user && req.user.activeTenantId) {
        return req.user.activeTenantId;
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
async function isSuperAdmin(userId) {
    try {
        const db = (0, firestore_1.getFirestore)();
        const userDoc = await db.collection('users').doc(userId).get();
        if (!userDoc.exists) {
            return false;
        }
        const userData = userDoc.data();
        return userData?.globalRole === 'super_admin' || userData?.globalRole === 'clearforge_admin';
    }
    catch (error) {
        logger_1.logger.error('Error checking super admin status', { userId, error });
        return false;
    }
}
/**
 * Validate user has access to tenant
 */
async function validateTenantAccess(userId, tenantId) {
    try {
        const db = (0, firestore_1.getFirestore)();
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
    }
    catch (error) {
        logger_1.logger.error('Error validating tenant access', { userId, tenantId, error });
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
async function enforceTenant(req, res, next) {
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
        req.isSuperAdmin = isAdmin;
        // Super admin can access any tenant
        if (isAdmin) {
            logger_1.logger.info('Super admin accessing tenant', {
                userId,
                tenantId: requestedTenantId,
                requestId: req.requestId,
            });
            req.tenantId = requestedTenantId;
            req.tenantId = requestedTenantId; // Maintain compatibility
            next();
            return;
        }
        // Validate normal user access
        const hasAccess = await validateTenantAccess(userId, requestedTenantId);
        if (!hasAccess) {
            logger_1.logger.warn('Tenant access denied', {
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
        logger_1.logger.debug('Tenant access granted', {
            userId,
            tenantId: requestedTenantId,
            requestId: req.requestId,
        });
        req.tenantId = requestedTenantId;
        req.tenantId = requestedTenantId; // Maintain compatibility
        next();
    }
    catch (error) {
        logger_1.logger.error('Error in tenant enforcement middleware', {
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
async function optionalTenantEnforcement(req, res, next) {
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
        req.isSuperAdmin = isAdmin;
        if (isAdmin) {
            req.tenantId = requestedTenantId;
            req.tenantId = requestedTenantId;
            next();
            return;
        }
        const hasAccess = await validateTenantAccess(userId, requestedTenantId);
        if (hasAccess) {
            req.tenantId = requestedTenantId;
            req.tenantId = requestedTenantId;
        }
        next();
    }
    catch (error) {
        logger_1.logger.error('Error in optional tenant enforcement', { error });
        next(); // Continue even if error
    }
}
/**
 * Tenant switching endpoint handler
 * Allows users to switch their active tenant
 */
async function switchTenant(req, res) {
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
        const db = (0, firestore_1.getFirestore)();
        await db.collection('users').doc(userId).update({
            activeTenantId: tenantId,
            lastTenantSwitchAt: new Date().toISOString(),
        });
        logger_1.logger.info('User switched tenant', {
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
    }
    catch (error) {
        logger_1.logger.error('Error switching tenant', { error });
        res.status(500).json({
            success: false,
            error: {
                code: 'TENANT_SWITCH_ERROR',
                message: 'Error switching tenant',
            },
        });
    }
}
//# sourceMappingURL=tenantEnforcement.js.map