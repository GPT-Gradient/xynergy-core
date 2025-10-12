import { Request, Response, NextFunction } from 'express';
/**
 * Authenticated request interface
 */
export interface AuthenticatedRequest extends Request {
    user?: {
        uid: string;
        email?: string;
        name?: string;
        roles?: string[];
    };
    tenantId?: string;
    requestId?: string;
}
/**
 * Firebase Auth middleware
 * Validates Firebase ID tokens from Authorization header
 */
export declare const authenticateRequest: (req: AuthenticatedRequest, res: Response, next: NextFunction) => Promise<void>;
/**
 * Optional auth middleware - allows requests with or without token
 */
export declare const optionalAuth: (req: AuthenticatedRequest, res: Response, next: NextFunction) => Promise<void>;
//# sourceMappingURL=auth.d.ts.map