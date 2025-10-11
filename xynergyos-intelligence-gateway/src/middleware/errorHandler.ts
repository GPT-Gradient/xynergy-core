import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

export interface AppError extends Error {
  statusCode?: number;
  isOperational?: boolean;
  details?: any;
}

export class ValidationError extends Error implements AppError {
  statusCode = 400;
  isOperational = true;

  constructor(message: string, public details?: any) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class UnauthorizedError extends Error implements AppError {
  statusCode = 401;
  isOperational = true;

  constructor(message: string = 'Unauthorized') {
    super(message);
    this.name = 'UnauthorizedError';
  }
}

export class NotFoundError extends Error implements AppError {
  statusCode = 404;
  isOperational = true;

  constructor(message: string = 'Not found') {
    super(message);
    this.name = 'NotFoundError';
  }
}

export class ServiceUnavailableError extends Error implements AppError {
  statusCode = 503;
  isOperational = true;

  constructor(message: string = 'Service temporarily unavailable') {
    super(message);
    this.name = 'ServiceUnavailableError';
  }
}

export const errorHandler = (
  err: AppError,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const statusCode = err.statusCode || 500;
  const isOperational = err.isOperational || false;
  const isDevelopment = process.env.NODE_ENV !== 'production';

  // Log full error details (including stack trace)
  logger.error('Request error', {
    error: err.message,
    stack: err.stack,
    statusCode,
    isOperational,
    path: req.path,
    method: req.method,
    userId: (req as any).user?.uid,
    requestId: req.headers['x-request-id'],
  });

  // Build error response (NO stack trace in production)
  const errorResponse: any = {
    error: {
      code: err.name || 'INTERNAL_ERROR',
      message: isDevelopment
        ? err.message
        : isOperational
        ? err.message
        : 'An unexpected error occurred',
      requestId: req.headers['x-request-id'] || 'unknown',
      timestamp: new Date().toISOString(),
    },
  };

  // Only include technical details in development
  if (isDevelopment) {
    errorResponse.error.stack = err.stack;
    if (err.details) {
      errorResponse.error.details = err.details;
    }
  } else if (isOperational && err.details) {
    // Only include details for operational errors in production
    errorResponse.error.details = err.details;
  }

  res.status(statusCode).json(errorResponse);
};

// Async error wrapper
export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};
