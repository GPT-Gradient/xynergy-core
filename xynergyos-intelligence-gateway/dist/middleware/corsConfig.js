"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.logCorsConfig = exports.corsMiddleware = void 0;
const cors_1 = __importDefault(require("cors"));
const config_1 = require("../config/config");
const logger_1 = require("../utils/logger");
/**
 * Enhanced CORS configuration with dynamic origin checking
 * NEVER uses wildcard origins for security
 */
// Check if origin is allowed
const isOriginAllowed = (origin) => {
    if (!origin) {
        // Allow requests with no origin (e.g., mobile apps, Postman)
        return true;
    }
    // Check exact matches
    if (config_1.appConfig.cors.origins.includes(origin)) {
        return true;
    }
    // Check wildcard patterns (e.g., "https://*.xynergyos.com")
    for (const allowedOrigin of config_1.appConfig.cors.origins) {
        if (allowedOrigin.includes('*')) {
            const pattern = allowedOrigin
                .replace(/\./g, '\\.')
                .replace(/\*/g, '.*');
            const regex = new RegExp(`^${pattern}$`);
            if (regex.test(origin)) {
                return true;
            }
        }
    }
    return false;
};
// CORS options with dynamic origin checking
const corsOptions = {
    origin: (origin, callback) => {
        if (isOriginAllowed(origin)) {
            callback(null, true);
        }
        else {
            logger_1.logger.warn('CORS blocked request from origin', { origin });
            callback(new Error('Not allowed by CORS'));
        }
    },
    credentials: true, // Allow cookies and authorization headers
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
    allowedHeaders: [
        'Content-Type',
        'Authorization',
        'X-Request-ID',
        'X-Tenant-ID',
    ],
    exposedHeaders: ['X-Request-ID', 'RateLimit-Limit', 'RateLimit-Remaining'],
    maxAge: 3600, // Cache preflight requests for 1 hour
    optionsSuccessStatus: 204, // Success status for OPTIONS requests
};
exports.corsMiddleware = (0, cors_1.default)(corsOptions);
// Log CORS configuration on startup
const logCorsConfig = () => {
    logger_1.logger.info('CORS configuration loaded', {
        allowedOrigins: config_1.appConfig.cors.origins,
        credentials: true,
    });
};
exports.logCorsConfig = logCorsConfig;
//# sourceMappingURL=corsConfig.js.map