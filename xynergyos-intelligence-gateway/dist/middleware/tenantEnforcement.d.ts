/**
 * Tenant Enforcement Middleware
 * Validates user has access to requested tenant and enforces tenant isolation
 */
import { Response, NextFunction } from 'express';
import { AuthenticatedRequest } from './auth';
export interface TenantRequest extends AuthenticatedRequest {
    tenantId: string;
    isSuperAdmin: boolean;
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
export declare function enforceTenant(req: AuthenticatedRequest, res: Response, next: NextFunction): Promise<void>;
/**
 * Optional tenant enforcement (doesn't fail if no tenant access)
 * Useful for endpoints that can work without tenant context
 */
export declare function optionalTenantEnforcement(req: AuthenticatedRequest, res: Response, next: NextFunction): Promise<void>;
/**
 * Tenant switching endpoint handler
 * Allows users to switch their active tenant
 */
export declare function switchTenant(req: AuthenticatedRequest, res: Response): Promise<void>;
//# sourceMappingURL=tenantEnforcement.d.ts.map