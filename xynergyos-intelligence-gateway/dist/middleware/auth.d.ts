import { Request, Response, NextFunction } from 'express';
export interface AuthenticatedRequest extends Request {
    user?: {
        uid: string;
        email?: string;
        name?: string;
        roles?: string[];
    };
    tenantId?: string;
}
/**
 * Dual authentication middleware supporting both Firebase and JWT tokens
 * Priority: Try Firebase first, fall back to JWT
 */
export declare const authenticateRequest: (req: AuthenticatedRequest, res: Response, next: NextFunction) => Promise<void>;
export declare const optionalAuth: (req: AuthenticatedRequest, res: Response, next: NextFunction) => Promise<void>;
//# sourceMappingURL=auth.d.ts.map