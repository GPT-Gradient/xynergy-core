"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.optionalAuth = exports.authenticateRequest = void 0;
const firebase_1 = require("../config/firebase");
const logger_1 = require("../utils/logger");
const errorHandler_1 = require("./errorHandler");
/**
 * Firebase Auth middleware
 * Validates Firebase ID tokens from Authorization header
 */
const authenticateRequest = async (req, res, next) => {
    try {
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            throw new errorHandler_1.UnauthorizedError('Missing or invalid authorization header');
        }
        const token = authHeader.split('Bearer ')[1];
        try {
            const decodedToken = await (0, firebase_1.getFirebaseAuth)().verifyIdToken(token);
            req.user = {
                uid: decodedToken.uid,
                email: decodedToken.email,
                name: decodedToken.name,
                roles: decodedToken.roles || [],
            };
            // Set tenant ID (default to clearforge for now)
            req.tenantId = decodedToken.tenantId || 'clearforge';
            logger_1.logger.debug('Request authenticated', {
                userId: req.user.uid,
                email: req.user.email,
                requestId: req.requestId,
            });
            next();
        }
        catch (error) {
            logger_1.logger.warn('Token verification failed', {
                error: error.message,
                requestId: req.requestId,
            });
            throw new errorHandler_1.UnauthorizedError('Invalid or expired token');
        }
    }
    catch (error) {
        next(error);
    }
};
exports.authenticateRequest = authenticateRequest;
/**
 * Optional auth middleware - allows requests with or without token
 */
const optionalAuth = async (req, res, next) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return next();
    }
    try {
        const token = authHeader.split('Bearer ')[1];
        const decodedToken = await (0, firebase_1.getFirebaseAuth)().verifyIdToken(token);
        req.user = {
            uid: decodedToken.uid,
            email: decodedToken.email,
            name: decodedToken.name,
            roles: decodedToken.roles || [],
        };
        req.tenantId = decodedToken.tenantId || 'clearforge';
    }
    catch (error) {
        logger_1.logger.debug('Optional auth: token invalid, continuing without auth');
    }
    next();
};
exports.optionalAuth = optionalAuth;
//# sourceMappingURL=auth.js.map