"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.asyncHandler = exports.errorHandler = exports.ServiceUnavailableError = exports.ConflictError = exports.NotFoundError = exports.ForbiddenError = exports.UnauthorizedError = exports.ValidationError = exports.AppError = void 0;
const logger_1 = require("../utils/logger");
/**
 * Custom error classes
 */
class AppError extends Error {
    statusCode;
    message;
    isOperational;
    constructor(statusCode, message, isOperational = true) {
        super(message);
        this.statusCode = statusCode;
        this.message = message;
        this.isOperational = isOperational;
        Object.setPrototypeOf(this, AppError.prototype);
    }
}
exports.AppError = AppError;
class ValidationError extends AppError {
    constructor(message) {
        super(400, message);
    }
}
exports.ValidationError = ValidationError;
class UnauthorizedError extends AppError {
    constructor(message = 'Unauthorized') {
        super(401, message);
    }
}
exports.UnauthorizedError = UnauthorizedError;
class ForbiddenError extends AppError {
    constructor(message = 'Forbidden') {
        super(403, message);
    }
}
exports.ForbiddenError = ForbiddenError;
class NotFoundError extends AppError {
    constructor(message = 'Resource not found') {
        super(404, message);
    }
}
exports.NotFoundError = NotFoundError;
class ConflictError extends AppError {
    constructor(message) {
        super(409, message);
    }
}
exports.ConflictError = ConflictError;
class ServiceUnavailableError extends AppError {
    constructor(message = 'Service temporarily unavailable') {
        super(503, message);
    }
}
exports.ServiceUnavailableError = ServiceUnavailableError;
/**
 * Global error handler middleware
 */
const errorHandler = (err, req, res, next) => {
    if (err instanceof AppError) {
        logger_1.logger.error('Application error', {
            statusCode: err.statusCode,
            message: err.message,
            requestId: req.requestId,
            path: req.path,
            method: req.method,
        });
        res.status(err.statusCode).json({
            error: err.message,
            statusCode: err.statusCode,
            requestId: req.requestId,
            timestamp: new Date().toISOString(),
        });
    }
    else {
        logger_1.logger.error('Unexpected error', {
            error: err.message,
            stack: err.stack,
            requestId: req.requestId,
            path: req.path,
            method: req.method,
        });
        res.status(500).json({
            error: 'Internal server error',
            statusCode: 500,
            requestId: req.requestId,
            timestamp: new Date().toISOString(),
        });
    }
};
exports.errorHandler = errorHandler;
/**
 * Async handler wrapper to catch promise rejections
 */
const asyncHandler = (fn) => {
    return (req, res, next) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
};
exports.asyncHandler = asyncHandler;
//# sourceMappingURL=errorHandler.js.map