"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.logResponse = exports.logRequest = exports.logger = void 0;
const winston_1 = __importDefault(require("winston"));
const config_1 = require("../config/config");
const logLevel = config_1.appConfig.nodeEnv === 'production' ? 'info' : 'debug';
/**
 * Structured logger using Winston
 * Formats logs as JSON for Cloud Logging compatibility
 */
exports.logger = winston_1.default.createLogger({
    level: logLevel,
    format: winston_1.default.format.combine(winston_1.default.format.timestamp(), winston_1.default.format.errors({ stack: true }), winston_1.default.format.json()),
    defaultMeta: {
        service: config_1.appConfig.serviceName,
        environment: config_1.appConfig.nodeEnv,
    },
    transports: [
        new winston_1.default.transports.Console({
            format: winston_1.default.format.combine(winston_1.default.format.colorize(), winston_1.default.format.printf(({ timestamp, level, message, ...meta }) => {
                const metaStr = Object.keys(meta).length ? JSON.stringify(meta, null, 2) : '';
                return `${timestamp} [${level}]: ${message} ${metaStr}`;
            })),
        }),
    ],
});
/**
 * Log HTTP request
 */
const logRequest = (req, duration) => {
    exports.logger.info('HTTP Request', {
        method: req.method,
        path: req.path,
        requestId: req.requestId,
        userId: req.user?.uid,
        duration: duration ? `${duration}ms` : undefined,
    });
};
exports.logRequest = logRequest;
/**
 * Log HTTP response
 */
const logResponse = (req, res, duration) => {
    exports.logger.info('HTTP Response', {
        method: req.method,
        path: req.path,
        requestId: req.requestId,
        statusCode: res.statusCode,
        duration: `${duration}ms`,
    });
};
exports.logResponse = logResponse;
//# sourceMappingURL=logger.js.map