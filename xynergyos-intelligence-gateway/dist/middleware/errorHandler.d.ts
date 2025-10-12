import { Request, Response, NextFunction } from 'express';
export interface AppError extends Error {
    statusCode?: number;
    isOperational?: boolean;
    details?: any;
}
export declare class ValidationError extends Error implements AppError {
    details?: any | undefined;
    statusCode: number;
    isOperational: boolean;
    constructor(message: string, details?: any | undefined);
}
export declare class UnauthorizedError extends Error implements AppError {
    statusCode: number;
    isOperational: boolean;
    constructor(message?: string);
}
export declare class NotFoundError extends Error implements AppError {
    statusCode: number;
    isOperational: boolean;
    constructor(message?: string);
}
export declare class ServiceUnavailableError extends Error implements AppError {
    statusCode: number;
    isOperational: boolean;
    constructor(message?: string);
}
export declare const errorHandler: (err: AppError, req: Request, res: Response, next: NextFunction) => void;
export declare const asyncHandler: (fn: (req: Request, res: Response, next: NextFunction) => Promise<any>) => (req: Request, res: Response, next: NextFunction) => void;
//# sourceMappingURL=errorHandler.d.ts.map