"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.requestLogger = void 0;
const logger_1 = require("../utils/logger");
/**
 * Enhanced request logging middleware with detailed context
 */
const requestLogger = (req, res, next) => {
    const startTime = Date.now();
    // Log incoming request
    logger_1.logger.info('Incoming request', {
        requestId: req.requestId,
        method: req.method,
        path: req.path,
        query: req.query,
        ip: req.ip,
        userAgent: req.headers['user-agent'],
        userId: req.user?.uid,
        tenantId: req.tenantId,
    });
    // Capture response on finish
    res.on('finish', () => {
        const duration = Date.now() - startTime;
        const logLevel = res.statusCode >= 400 ? 'warn' : 'info';
        logger_1.logger[logLevel]('Request completed', {
            requestId: req.requestId,
            method: req.method,
            path: req.path,
            statusCode: res.statusCode,
            duration: `${duration}ms`,
            userId: req.user?.uid,
            tenantId: req.tenantId,
        });
    });
    next();
};
exports.requestLogger = requestLogger;
//# sourceMappingURL=requestLogger.js.map