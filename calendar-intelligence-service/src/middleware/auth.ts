import { Request, Response, NextFunction } from 'express';
import { getFirebaseAuth } from '../config/firebase';
import { logger } from '../utils/logger';
import { UnauthorizedError } from './errorHandler';

/**
 * Authenticated request interface
 */
export interface AuthenticatedRequest extends Request {
  user?: {
    uid: string;
    email?: string;
    name?: string;
    roles?: string[];
  };
  tenantId?: string;
  requestId?: string;
}

/**
 * Firebase Auth middleware
 * Validates Firebase ID tokens from Authorization header
 */
export const authenticateRequest = async (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new UnauthorizedError('Missing or invalid authorization header');
    }

    const token = authHeader.split('Bearer ')[1];

    try {
      const decodedToken = await getFirebaseAuth().verifyIdToken(token);

      req.user = {
        uid: decodedToken.uid,
        email: decodedToken.email,
        name: decodedToken.name,
        roles: (decodedToken as any).roles || [],
      };

      // Set tenant ID (default to clearforge for now)
      req.tenantId = (decodedToken as any).tenantId || 'clearforge';

      logger.debug('Request authenticated', {
        userId: req.user.uid,
        email: req.user.email,
        requestId: req.requestId,
      });

      next();
    } catch (error: any) {
      logger.warn('Token verification failed', {
        error: error.message,
        requestId: req.requestId,
      });
      throw new UnauthorizedError('Invalid or expired token');
    }
  } catch (error) {
    next(error);
  }
};

/**
 * Optional auth middleware - allows requests with or without token
 */
export const optionalAuth = async (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return next();
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
    req.tenantId = (decodedToken as any).tenantId || 'clearforge';
  } catch (error) {
    logger.debug('Optional auth: token invalid, continuing without auth');
  }

  next();
};
