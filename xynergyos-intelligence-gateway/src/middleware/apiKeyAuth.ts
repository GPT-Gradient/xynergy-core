import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

const VALID_API_KEY = process.env.GATEWAY_API_KEY;

/**
 * Middleware to validate API key for public routes
 * Used for website form submissions and other public-facing endpoints
 */
export function validateApiKey(req: Request, res: Response, next: NextFunction): void {
  const apiKey = req.headers['x-api-key'] as string;

  if (!apiKey) {
    logger.warn('API key validation failed: Missing API key', {
      ip: req.ip,
      path: req.path,
    });
    res.status(401).json({
      success: false,
      error: 'Missing API key'
    });
    return;
  }

  if (apiKey !== VALID_API_KEY) {
    logger.warn('API key validation failed: Invalid API key', {
      ip: req.ip,
      path: req.path,
    });
    res.status(401).json({
      success: false,
      error: 'Invalid API key'
    });
    return;
  }

  logger.debug('API key validated successfully', {
    path: req.path,
  });

  next();
}
