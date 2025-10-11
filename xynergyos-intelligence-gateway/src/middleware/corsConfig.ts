import cors, { CorsOptions } from 'cors';
import { Request } from 'express';
import { appConfig } from '../config/config';
import { logger } from '../utils/logger';

/**
 * Enhanced CORS configuration with dynamic origin checking
 * NEVER uses wildcard origins for security
 */

// Check if origin is allowed
const isOriginAllowed = (origin: string | undefined): boolean => {
  if (!origin) {
    // Allow requests with no origin (e.g., mobile apps, Postman)
    return true;
  }

  // Check exact matches
  if (appConfig.cors.origins.includes(origin)) {
    return true;
  }

  // Check wildcard patterns (e.g., "https://*.xynergyos.com")
  for (const allowedOrigin of appConfig.cors.origins) {
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
const corsOptions: CorsOptions = {
  origin: (origin, callback) => {
    if (isOriginAllowed(origin)) {
      callback(null, true);
    } else {
      logger.warn('CORS blocked request from origin', { origin });
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

export const corsMiddleware = cors(corsOptions);

// Log CORS configuration on startup
export const logCorsConfig = (): void => {
  logger.info('CORS configuration loaded', {
    allowedOrigins: appConfig.cors.origins,
    credentials: true,
  });
};
