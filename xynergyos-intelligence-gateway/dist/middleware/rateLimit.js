"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.websocketRateLimit = exports.authRateLimit = exports.generalRateLimit = void 0;
const express_rate_limit_1 = __importDefault(require("express-rate-limit"));
const config_1 = require("../config/config");
const logger_1 = require("../utils/logger");
const cacheService_1 = require("../services/cacheService");
// Reuse existing cache service Redis client (no duplicate connections)
const cache = (0, cacheService_1.getCacheService)();
// Custom key generator (IP + user ID if authenticated)
const keyGenerator = (req) => {
    const ip = req.ip || req.socket.remoteAddress || 'unknown';
    const userId = req.user?.uid;
    return userId ? `${userId}` : `${ip}`;
};
// Standard rate limit message
const rateLimitMessage = {
    error: 'Too Many Requests',
    message: 'You have exceeded the rate limit. Please try again later.',
};
// General API rate limit (100 requests per minute)
exports.generalRateLimit = (0, express_rate_limit_1.default)({
    windowMs: config_1.appConfig.rateLimit.windowMs,
    max: config_1.appConfig.rateLimit.maxRequests,
    message: rateLimitMessage,
    keyGenerator,
    standardHeaders: true, // Return rate limit info in `RateLimit-*` headers
    legacyHeaders: false, // Disable `X-RateLimit-*` headers
    handler: (req, res) => {
        logger_1.logger.warn('Rate limit exceeded', {
            ip: req.ip,
            path: req.path,
            userId: req.user?.uid,
        });
        res.status(429).json(rateLimitMessage);
    },
});
// Strict rate limit for authentication endpoints (10 per minute)
exports.authRateLimit = (0, express_rate_limit_1.default)({
    windowMs: 60 * 1000, // 1 minute
    max: 10,
    message: {
        error: 'Too Many Requests',
        message: 'Too many authentication attempts. Please try again later.',
    },
    keyGenerator,
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req, res) => {
        logger_1.logger.warn('Auth rate limit exceeded', {
            ip: req.ip,
            path: req.path,
        });
        res.status(429).json({
            error: 'Too Many Requests',
            message: 'Too many authentication attempts. Please try again later.',
        });
    },
});
// WebSocket connection rate limit (20 per minute per IP)
exports.websocketRateLimit = (0, express_rate_limit_1.default)({
    windowMs: 60 * 1000,
    max: 20,
    message: {
        error: 'Too Many Requests',
        message: 'Too many WebSocket connection attempts. Please try again later.',
    },
    keyGenerator,
    standardHeaders: true,
    legacyHeaders: false,
});
// Note: Redis client cleanup handled by cacheService.disconnect()
// No separate cleanup needed since we're reusing the cache service client
//# sourceMappingURL=rateLimit.js.map