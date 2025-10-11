import { Request, Response, NextFunction } from 'express';
import { randomUUID } from 'crypto';

// Extend Express Request type to include requestId
declare global {
  namespace Express {
    interface Request {
      requestId?: string;
    }
  }
}

/**
 * Middleware to generate and attach a unique request ID to each request
 * Request ID is used for tracing requests through logs
 */
export const requestIdMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  // Check if request ID already exists in header (from load balancer or proxy)
  const existingRequestId = req.headers['x-request-id'] as string;

  // Use existing or generate new UUID
  const requestId = existingRequestId || randomUUID();

  // Attach to request object
  req.requestId = requestId;

  // Set response header so client can reference this request
  res.setHeader('X-Request-ID', requestId);

  next();
};
