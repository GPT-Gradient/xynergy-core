import { Request, Response, NextFunction } from 'express';
import { getFirebaseAuth } from '../config/firebase';
import { logger } from '../utils/logger';
import jwt from 'jsonwebtoken';

export interface AuthenticatedRequest extends Request {
  user?: {
    uid: string;
    email?: string;
    name?: string;
    roles?: string[];
  };
  tenantId?: string;
}

interface JWTPayload {
  user_id?: string;
  userId?: string;
  sub?: string;
  tenant_id?: string;
  tenantId?: string;
  email?: string;
  roles?: string[];
  [key: string]: any;
}

/**
 * Dual authentication middleware supporting both Firebase and JWT tokens
 * Priority: Try Firebase first, fall back to JWT
 */
export const authenticateRequest = async (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
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
      const decodedToken = await getFirebaseAuth().verifyIdToken(token);

      req.user = {
        uid: decodedToken.uid,
        email: decodedToken.email,
        name: decodedToken.name,
        roles: (decodedToken as any).roles || [],
      };

      req.tenantId = 'clearforge';

      logger.info('Request authenticated via Firebase', {
        userId: req.user.uid,
        email: req.user.email,
        path: req.path,
      });

      next();
      return;
    } catch (firebaseError) {
      // Firebase failed, try JWT
      logger.debug('Firebase auth failed, attempting JWT', { error: firebaseError });
    }

    // Try JWT authentication
    const jwtSecret = process.env.JWT_SECRET;
    if (!jwtSecret) {
      logger.error('JWT_SECRET not configured');
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
      const decoded = jwt.verify(token, jwtSecret) as JWTPayload;

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

      logger.info('Request authenticated via JWT', {
        userId: req.user.uid,
        email: req.user.email,
        tenantId: req.tenantId,
        path: req.path,
      });

      next();
      return;
    } catch (jwtError) {
      logger.error('JWT authentication failed', { error: jwtError });
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
  } catch (error) {
    logger.error('Authentication error', { error });

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

// Optional authentication (for public endpoints)
export const optionalAuth = async (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    next();
    return;
  }

  try {
    const token = authHeader.split('Bearer ')[1];
    const decodedToken = await getFirebaseAuth().verifyIdToken(token);

    req.user = {
      uid: decodedToken.uid,
      email: decodedToken.email,
      name: decodedToken.name,
      roles: (decodedToken as any).roles || [],
    };

    req.tenantId = 'clearforge';
  } catch (error) {
    logger.warn('Optional auth failed, continuing unauthenticated', { error });
  }

  next();
};
