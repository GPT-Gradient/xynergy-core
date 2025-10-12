"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.requestIdMiddleware = void 0;
const crypto_1 = require("crypto");
/**
 * Middleware to generate and attach a unique request ID to each request
 * Request ID is used for tracing requests through logs
 */
const requestIdMiddleware = (req, res, next) => {
    // Check if request ID already exists in header (from load balancer or proxy)
    const existingRequestId = req.headers['x-request-id'];
    // Use existing or generate new UUID
    const requestId = existingRequestId || (0, crypto_1.randomUUID)();
    // Attach to request object
    req.requestId = requestId;
    // Set response header so client can reference this request
    res.setHeader('X-Request-ID', requestId);
    next();
};
exports.requestIdMiddleware = requestIdMiddleware;
//# sourceMappingURL=requestId.js.map