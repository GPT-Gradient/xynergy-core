/**
 * Permission Checking Middleware
 * RBAC enforcement with wildcard support and Redis caching
 */
interface PermissionCheckOptions {
    requireAll?: boolean;
    skipAudit?: boolean;
}
/**
 * Invalidate permission cache for user
 * Call this after role/permission changes
 * (No-op without cache - permissions fetched fresh each time)
 */
export declare function invalidatePermissionCache(userId: string, tenantId?: string): Promise<void>;
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
export declare function checkPermission(permissions: string | string[], options?: PermissionCheckOptions): any;
/**
 * Check permission programmatically (not middleware)
 * Useful for conditional logic within route handlers
 */
export declare function checkPermissionForUser(userId: string, tenantId: string, permission: string | string[]): Promise<boolean>;
/**
 * Get all permissions for user in tenant
 */
export declare function getUserPermissionsForTenant(userId: string, tenantId: string): Promise<string[]>;
export {};
//# sourceMappingURL=checkPermission.d.ts.map