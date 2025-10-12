"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.optionalAuth = exports.authenticateRequest = void 0;
const firebase_1 = require("../config/firebase");
const logger_1 = require("../utils/logger");
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
/**
 * Dual authentication middleware supporting both Firebase and JWT tokens
 * Priority: Try Firebase first, fall back to JWT
 */
const authenticateRequest = async (req, res, next) => {
    try {
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            res.status(401).json({
                error: {
                    code: 'AUTHENTICATION_REQUIRED',
                    message: 'Missing or invalid authorization header',
                    requestId: req.headers['x-request-id'] || 'unknown',
                    timestamp: new Date().toISOString(),
                },
            });
            return;
        }
        const token = authHeader.split('Bearer ')[1];
        // Try Firebase authentication first
        try {
            const decodedToken = await (0, firebase_1.getFirebaseAuth)().verifyIdToken(token);
            req.user = {
                uid: decodedToken.uid,
                email: decodedToken.email,
                name: decodedToken.name,
                roles: decodedToken.roles || [],
            };
            req.tenantId = 'clearforge';
            logger_1.logger.info('Request authenticated via Firebase', {
                userId: req.user.uid,
                email: req.user.email,
                path: req.path,
            });
            next();
            return;
        }
        catch (firebaseError) {
            // Firebase failed, try JWT
            logger_1.logger.debug('Firebase auth failed, attempting JWT', { error: firebaseError });
        }
        // Try JWT authentication
        const jwtSecret = process.env.JWT_SECRET;
        if (!jwtSecret) {
            logger_1.logger.error('JWT_SECRET not configured');
            res.status(500).json({
                error: {
                    code: 'CONFIGURATION_ERROR',
                    message: 'Authentication service misconfigured',
                    requestId: req.headers['x-request-id'] || 'unknown',
                    timestamp: new Date().toISOString(),
                },
            });
            return;
        }
        try {
            const decoded = jsonwebtoken_1.default.verify(token, jwtSecret);
            // Extract user ID (handle multiple possible field names)
            const userId = decoded.user_id || decoded.userId || decoded.sub;
            if (!userId) {
                throw new Error('JWT token missing user ID');
            }
            // Extract tenant ID (handle multiple possible field names)
            const tenantId = decoded.tenant_id || decoded.tenantId || 'clearforge';
            req.user = {
                uid: userId,
                email: decoded.email,
                name: decoded.name,
                roles: decoded.roles || [],
            };
            req.tenantId = tenantId;
            logger_1.logger.info('Request authenticated via JWT', {
                userId: req.user.uid,
                email: req.user.email,
                tenantId: req.tenantId,
                path: req.path,
            });
            next();
            return;
        }
        catch (jwtError) {
            logger_1.logger.error('JWT authentication failed', { error: jwtError });
            res.status(401).json({
                error: {
                    code: 'INVALID_TOKEN',
                    message: 'Invalid or expired token',
                    requestId: req.headers['x-request-id'] || 'unknown',
                    timestamp: new Date().toISOString(),
                },
            });
            return;
        }
    }
    catch (error) {
        logger_1.logger.error('Authentication error', { error });
        res.status(401).json({
            error: {
                code: 'AUTHENTICATION_ERROR',
                message: 'Authentication failed',
                requestId: req.headers['x-request-id'] || 'unknown',
                timestamp: new Date().toISOString(),
            },
        });
    }
};
exports.authenticateRequest = authenticateRequest;
// Optional authentication (for public endpoints)
const optionalAuth = async (req, res, next) => {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        next();
        return;
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
        req.tenantId = 'clearforge';
    }
    catch (error) {
        logger_1.logger.warn('Optional auth failed, continuing unauthenticated', { error });
    }
    next();
};
exports.optionalAuth = optionalAuth;
//# sourceMappingURL=auth.js.map