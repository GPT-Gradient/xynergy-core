import { Request, Response, NextFunction } from 'express';
declare global {
    namespace Express {
        interface Request {
            requestId?: string;
        }
    }
}
/**
 * Middleware to generate and attach a unique request ID to each request
 * Request ID is used for tracing requests through logs
 */
export declare const requestIdMiddleware: (req: Request, res: Response, next: NextFunction) => void;
//# sourceMappingURL=requestId.d.ts.map