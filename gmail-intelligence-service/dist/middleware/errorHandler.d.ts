import { Request, Response, NextFunction } from 'express';
/**
 * Custom error classes
 */
export declare class AppError extends Error {
    statusCode: number;
    message: string;
    isOperational: boolean;
    constructor(statusCode: number, message: string, isOperational?: boolean);
}
export declare class ValidationError extends AppError {
    constructor(message: string);
}
export declare class UnauthorizedError extends AppError {
    constructor(message?: string);
}
export declare class ForbiddenError extends AppError {
    constructor(message?: string);
}
export declare class NotFoundError extends AppError {
    constructor(message?: string);
}
export declare class ConflictError extends AppError {
    constructor(message: string);
}
export declare class ServiceUnavailableError extends AppError {
    constructor(message?: string);
}
/**
 * Global error handler middleware
 */
export declare const errorHandler: (err: Error | AppError, req: Request, res: Response, next: NextFunction) => void;
/**
 * Async handler wrapper to catch promise rejections
 */
export declare const asyncHandler: (fn: (req: Request, res: Response, next: NextFunction) => Promise<any>) => (req: Request, res: Response, next: NextFunction) => void;
//# sourceMappingURL=errorHandler.d.ts.map