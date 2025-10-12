/**
 * Permission & RBAC Service
 * Manages permissions, roles, and access control for Xynergy Platform
 */

import express, { Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { initializeApp, cert } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import permissionRoutes from './routes/permissions';
import roleRoutes from './routes/roles';
import templateRoutes from './routes/templates';
import { errorHandler } from './middleware/errorHandler';
import { logger } from './utils/logger';

const app = express();
const PORT = process.env.PORT || 8080;

// Initialize Firebase Admin
try {
  // Check if running in GCP (will use default credentials)
  if (process.env.GOOGLE_APPLICATION_CREDENTIALS || process.env.GCLOUD_PROJECT) {
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
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGINS?.split(',') || '*',
  credentials: true,
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request ID middleware
app.use((req: any, res, next) => {
  req.requestId = req.headers['x-request-id'] || `req_${Date.now()}_${Math.random().toString(36).substring(7)}`;
  next();
});

// Health check
app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'permission-service',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// Routes
app.use('/api/v1/permissions', permissionRoutes);
app.use('/api/v1/permissions/roles', roleRoutes);
app.use('/api/v1/permissions/templates', templateRoutes);

// Error handling
app.use(errorHandler);

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    error: {
      code: 'NOT_FOUND',
      message: 'Endpoint not found',
    },
  });
});

// Start server
app.listen(PORT, () => {
  logger.info(`Permission service listening on port ${PORT}`);
  logger.info('Environment:', process.env.NODE_ENV || 'development');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

export default app;
