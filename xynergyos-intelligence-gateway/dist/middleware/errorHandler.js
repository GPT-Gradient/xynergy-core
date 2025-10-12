"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.asyncHandler = exports.errorHandler = exports.ServiceUnavailableError = exports.NotFoundError = exports.UnauthorizedError = exports.ValidationError = void 0;
const logger_1 = require("../utils/logger");
class ValidationError extends Error {
    details;
    statusCode = 400;
    isOperational = true;
    constructor(message, details) {
        super(message);
        this.details = details;
        this.name = 'ValidationError';
    }
}
exports.ValidationError = ValidationError;
class UnauthorizedError extends Error {
    statusCode = 401;
    isOperational = true;
    constructor(message = 'Unauthorized') {
        super(message);
        this.name = 'UnauthorizedError';
    }
}
exports.UnauthorizedError = UnauthorizedError;
class NotFoundError extends Error {
    statusCode = 404;
    isOperational = true;
    constructor(message = 'Not found') {
        super(message);
        this.name = 'NotFoundError';
    }
}
exports.NotFoundError = NotFoundError;
class ServiceUnavailableError extends Error {
    statusCode = 503;
    isOperational = true;
    constructor(message = 'Service temporarily unavailable') {
        super(message);
        this.name = 'ServiceUnavailableError';
    }
}
exports.ServiceUnavailableError = ServiceUnavailableError;
const errorHandler = (err, req, res, next) => {
    const statusCode = err.statusCode || 500;
    const isOperational = err.isOperational || false;
    const isDevelopment = process.env.NODE_ENV !== 'production';
    // Log full error details (including stack trace)
    logger_1.logger.error('Request error', {
        error: err.message,
        stack: err.stack,
        statusCode,
        isOperational,
        path: req.path,
        method: req.method,
        userId: req.user?.uid,
        requestId: req.headers['x-request-id'],
    });
    // Build error response (NO stack trace in production)
    const errorResponse = {
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
    }
    else if (isOperational && err.details) {
        // Only include details for operational errors in production
        errorResponse.error.details = err.details;
    }
    res.status(statusCode).json(errorResponse);
};
exports.errorHandler = errorHandler;
// Async error wrapper
const asyncHandler = (fn) => {
    return (req, res, next) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
};
exports.asyncHandler = asyncHandler;
//# sourceMappingURL=errorHandler.js.map