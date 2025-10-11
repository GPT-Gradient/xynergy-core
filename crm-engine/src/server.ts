import express, { Application, Request, Response } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import { createServer, Server as HttpServer } from 'http';
import { appConfig } from './config/config';
import { initializeFirebase } from './config/firebase';
import { errorHandler } from './middleware/errorHandler';
import { logger } from './utils/logger';
import { randomUUID } from 'crypto';

// Import routes
import healthRoutes from './routes/health';
import crmRoutes from './routes/crm';

export class Server {
  private app: Application;
  private httpServer: HttpServer;

  constructor() {
    this.app = express();
    this.httpServer = createServer(this.app);

    this.initializeMiddleware();
    this.initializeRoutes();
    this.initializeErrorHandling();
  }

  private initializeMiddleware(): void {
    // Request ID middleware (must be first)
    this.app.use((req, res, next) => {
      const requestId = (req.headers['x-request-id'] as string) || randomUUID();
      (req as any).requestId = requestId;
      res.setHeader('X-Request-ID', requestId);
      next();
    });

    // Security headers
    this.app.use(helmet());

    // CORS
    this.app.use(cors({
      origin: appConfig.cors.origins,
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-ID'],
    }));

    // Compression
    this.app.use(compression());

    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Request logging
    this.app.use((req, res, next) => {
      const startTime = Date.now();

      logger.info('Incoming request', {
        requestId: (req as any).requestId,
        method: req.method,
        path: req.path,
        ip: req.ip,
      });

      res.on('finish', () => {
        const duration = Date.now() - startTime;
        logger.info('Request completed', {
          requestId: (req as any).requestId,
          statusCode: res.statusCode,
          duration: `${duration}ms`,
        });
      });

      next();
    });
  }

  private initializeRoutes(): void {
    // Health checks
    this.app.use('/health', healthRoutes);
    this.app.use('/api/v1/health', healthRoutes);

    // CRM routes
    this.app.use('/api/v1/crm', crmRoutes);

    // Root endpoint
    this.app.get('/', (req: Request, res: Response) => {
      res.json({
        service: appConfig.serviceName,
        version: '1.0.0',
        status: 'operational',
        endpoints: [
          'GET /health',
          'GET /health/deep',
          'GET /api/v1/crm/contacts',
          'POST /api/v1/crm/contacts',
          'GET /api/v1/crm/contacts/:contactId',
          'PATCH /api/v1/crm/contacts/:contactId',
          'DELETE /api/v1/crm/contacts/:contactId',
          'GET /api/v1/crm/contacts/:contactId/interactions',
          'POST /api/v1/crm/interactions',
          'GET /api/v1/crm/contacts/:contactId/notes',
          'POST /api/v1/crm/contacts/:contactId/notes',
          'GET /api/v1/crm/statistics',
        ],
        documentation: 'https://docs.xynergyos.com/crm-engine',
        timestamp: new Date().toISOString(),
      });
    });

    // 404 handler
    this.app.use((req: Request, res: Response) => {
      res.status(404).json({
        error: 'Not Found',
        message: `Route ${req.method} ${req.path} not found`,
        requestId: (req as any).requestId,
        timestamp: new Date().toISOString(),
      });
    });
  }

  private initializeErrorHandling(): void {
    this.app.use(errorHandler);
  }

  async start(): Promise<void> {
    try {
      // Initialize Firebase
      initializeFirebase();
      logger.info('Firebase initialized');

      // Start server
      this.httpServer.listen(appConfig.port, () => {
        logger.info('Server started', {
          port: appConfig.port,
          environment: appConfig.nodeEnv,
          service: appConfig.serviceName,
          features: [
            'Firebase Auth',
            'Firestore CRM Data',
            'Contact Management',
            'Interaction Tracking',
            'Notes & Tasks',
            'Statistics & Analytics',
          ],
        });
      });
    } catch (error) {
      logger.error('Failed to start server', { error });
      process.exit(1);
    }
  }

  async stop(): Promise<void> {
    return new Promise((resolve) => {
      this.httpServer.close(() => {
        logger.info('Server stopped');
        resolve();
      });
    });
  }
}
