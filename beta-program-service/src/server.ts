/**
 * Beta Program Service - Main Server
 * Manages beta application workflow, lifetime access, and phase transitions
 */

import express from 'express';
import cors from 'cors';
import { initializeApp, cert } from 'firebase-admin/app';
import { logger } from './utils/logger';

// Import routes
import applicationsRouter from './routes/applications';
import usersRouter from './routes/users';
import phasesRouter from './routes/phases';

const PORT = process.env.PORT || 8080;
const app = express();

// Initialize Firebase Admin
try {
  if (process.env.NODE_ENV === 'production') {
    initializeApp();
    logger.info('Firebase initialized with default credentials');
  } else {
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
    service: 'beta-program-service',
    timestamp: new Date().toISOString(),
  });
});

// API Routes
app.use('/api/v1/beta/applications', applicationsRouter);
app.use('/api/v1/beta/users', usersRouter);
app.use('/api/v1/beta/projects', phasesRouter);
app.use('/api/v1/beta/phases', phasesRouter);

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
  logger.info(`Beta Program Service listening on port ${PORT}`);
  logger.info('Environment', { env: process.env.NODE_ENV || 'development' });
});
