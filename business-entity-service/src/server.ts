/**
 * Business Entity Service - Main Server
 * Manages business entities, Continuum slots, and user administration
 */

import express from 'express';
import cors from 'cors';
import { initializeApp, cert } from 'firebase-admin/app';
import { logger } from './utils/logger';

// Import routes
import entitiesRouter from './routes/entities';
import continuumRouter from './routes/continuum';
import usersRouter from './routes/users';

const PORT = process.env.PORT || 8080;
const app = express();

// Initialize Firebase Admin
try {
  // Check if running in production (Cloud Run sets NODE_ENV=production)
  if (process.env.NODE_ENV === 'production') {
    initializeApp();
    logger.info('Firebase initialized with default credentials');
  } else {
    // Local development - use service account
    const serviceAccount = require('../serviceAccountKey.json');
    initializeApp({
      credential: cert(serviceAccount),
    });
    logger.info('Firebase initialized with service account');
  }
} catch (error) {
  logger.error('Failed to initialize Firebase', { error });
  process.exit(1);
}

// Middleware
app.use(cors());
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
  const requestId = req.headers['x-request-id'] || `req_${Date.now()}`;
  logger.info('Incoming request', {
    method: req.method,
    path: req.path,
    requestId,
  });
  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'business-entity-service',
    timestamp: new Date().toISOString(),
  });
});

// API Routes
app.use('/api/v1/entities', entitiesRouter);
app.use('/api/v1/continuum', continuumRouter);
app.use('/api/v1/users', usersRouter);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: {
      code: 'NOT_FOUND',
      message: `Route ${req.method} ${req.path} not found`,
    },
  });
});

// Error handler
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
  });

  res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: process.env.NODE_ENV === 'production'
        ? 'An unexpected error occurred'
        : err.message,
    },
  });
});

// Start server
app.listen(PORT, () => {
  logger.info(`Business Entity Service listening on port ${PORT}`);
  logger.info('Environment', { env: process.env.NODE_ENV || 'development' });
});
