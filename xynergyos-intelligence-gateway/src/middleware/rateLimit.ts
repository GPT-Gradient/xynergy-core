import rateLimit from 'express-rate-limit';
import { Request } from 'express';
import { createClient } from 'redis';
import { appConfig } from '../config/config';
import { logger } from '../utils/logger';

// Redis client for distributed rate limiting
let redisClient: any = null;

const initializeRedisClient = async () => {
  if (redisClient) {
    return redisClient;
  }

  try {
    redisClient = createClient({
      url: `redis://${appConfig.redis.host}:${appConfig.redis.port}`,
    });

    await redisClient.connect();
    logger.info('Redis client connected for rate limiting');
    return redisClient;
  } catch (error) {
    logger.error('Failed to connect Redis for rate limiting', { error });
    return null;
  }
};

// Initialize Redis client
initializeRedisClient();

// Custom key generator (IP + user ID if authenticated)
const keyGenerator = (req: Request): string => {
  const ip = req.ip || req.socket.remoteAddress || 'unknown';
  const userId = (req as any).user?.uid;
  return userId ? `${userId}` : `${ip}`;
};

// Standard rate limit message
const rateLimitMessage = {
  error: 'Too Many Requests',
  message: 'You have exceeded the rate limit. Please try again later.',
};

// General API rate limit (100 requests per minute)
export const generalRateLimit = rateLimit({
  windowMs: appConfig.rateLimit.windowMs,
  max: appConfig.rateLimit.maxRequests,
  message: rateLimitMessage,
  keyGenerator,
  standardHeaders: true, // Return rate limit info in `RateLimit-*` headers
  legacyHeaders: false, // Disable `X-RateLimit-*` headers
  handler: (req, res) => {
    logger.warn('Rate limit exceeded', {
      ip: req.ip,
      path: req.path,
      userId: (req as any).user?.uid,
    });
    res.status(429).json(rateLimitMessage);
  },
});

// Strict rate limit for authentication endpoints (10 per minute)
export const authRateLimit = rateLimit({
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
    logger.warn('Auth rate limit exceeded', {
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
export const websocketRateLimit = rateLimit({
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

// Cleanup function for Redis client
export const cleanupRateLimitRedis = async (): Promise<void> => {
  if (redisClient) {
    await redisClient.quit();
    logger.info('Rate limit Redis client closed');
  }
};
