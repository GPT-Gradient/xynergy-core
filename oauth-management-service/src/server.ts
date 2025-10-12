/**
 * OAuth Management Service
 * Main server file
 */

import express, { Request, Response } from 'express';
import cors from 'cors';
import * as admin from 'firebase-admin';
import { logger } from './utils/logger';
import { kmsService } from './utils/kms';
import { redisClient } from './utils/redis';
import { startTokenRefreshJob, stopTokenRefreshJob } from './jobs/tokenRefreshJob';
import { startHealthCheckJob, stopHealthCheckJob } from './jobs/healthCheckJob';

// Import routes
import oauthRoutes from './routes/oauth';
import tokenRoutes from './routes/tokens';
import adminRoutes from './routes/admin';

const app = express();
const PORT = process.env.PORT || 8080;

// Initialize Firebase Admin
if (!admin.apps.length) {
  admin.initializeApp({
    projectId: process.env.PROJECT_ID || 'xynergy-dev-1757909467',
  });
}

// Middleware
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true,
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req: Request, res: Response, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info('HTTP request', {
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration,
    });
  });

  next();
});

// Health check endpoint
app.get('/health', async (req: Request, res: Response) => {
  try {
    // Check Redis connection
    const redisHealthy = await redisClient.healthCheck();

    const health = {
      status: 'healthy',
      service: 'oauth-management-service',
      timestamp: new Date().toISOString(),
      redis: redisHealthy ? 'connected' : 'disconnected',
    };

    res.json(health);
  } catch (error: any) {
    logger.error('Health check failed', { error });
    res.status(503).json({
      status: 'unhealthy',
      error: error.message,
    });
  }
});

// Mount routes
app.use('/api/v1/oauth', oauthRoutes);
app.use('/api/v1/tokens', tokenRoutes);
app.use('/api/v1/admin', adminRoutes);

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({
    error: 'Not found',
    path: req.path,
  });
});

// Error handler
app.use((err: Error, req: Request, res: Response, next: any) => {
  logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
  });

  res.status(500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined,
  });
});

// Startup sequence
async function startServer() {
  try {
    logger.info('Starting OAuth Management Service...');

    // Start HTTP server first (for health checks)
    app.listen(PORT, () => {
      logger.info('OAuth Management Service started', {
        port: PORT,
        environment: process.env.NODE_ENV || 'development',
        projectId: process.env.PROJECT_ID || 'xynergy-dev-1757909467',
      });
    });

    // Initialize KMS in background (non-blocking)
    logger.info('Initializing KMS configuration...');
    kmsService.ensureKeyExists()
      .then(() => kmsService.testEncryption())
      .then(() => {
        logger.info('KMS initialization successful');
      })
      .catch((error) => {
        logger.warn('KMS initialization failed (service will continue without encryption)', { error });
      });

    // Start background jobs
    logger.info('Starting background jobs...');
    startTokenRefreshJob();
    startHealthCheckJob();
  } catch (error) {
    logger.error('Failed to start server', { error });
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully...');

  // Stop background jobs
  stopTokenRefreshJob();
  stopHealthCheckJob();

  // Close Redis connection
  await redisClient.close();

  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, shutting down gracefully...');

  // Stop background jobs
  stopTokenRefreshJob();
  stopHealthCheckJob();

  // Close Redis connection
  await redisClient.close();

  process.exit(0);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught exception', { error });
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled rejection', { reason, promise });
  process.exit(1);
});

// Start the server
startServer();
