import express, { Application } from 'express';
import helmet from 'helmet';
import compression from 'compression';
import { createServer, Server as HttpServer } from 'http';
import { appConfig } from './config/config';
import { initializeFirebase } from './config/firebase';
import { errorHandler } from './middleware/errorHandler';
import { logger } from './utils/logger';
import { initializeWebSocket, getWebSocketService } from './services/websocket';
import { initializeCacheService } from './services/cacheService';

// Import middleware
import { requestIdMiddleware } from './middleware/requestId';
import { corsMiddleware, logCorsConfig } from './middleware/corsConfig';
import { requestLogger } from './middleware/requestLogger';
import { generalRateLimit } from './middleware/rateLimit';

// Import routes
import healthRoutes from './routes/health';
import metricsRoutes from './routes/metrics';
import slackRoutes from './routes/slack';
import gmailRoutes from './routes/gmail';

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
    // Request ID (must be first to tag all logs)
    this.app.use(requestIdMiddleware);

    // Security headers
    this.app.use(helmet());

    // CORS - Enhanced with dynamic origin checking
    this.app.use(corsMiddleware);

    // Rate limiting - Applied globally
    this.app.use(generalRateLimit);

    // Compression
    this.app.use(compression());

    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Enhanced request logging with request ID and timing
    this.app.use(requestLogger);
  }

  private initializeRoutes(): void {
    // Health checks
    this.app.use('/api/v1/health', healthRoutes);
    this.app.use('/health', healthRoutes);

    // Metrics and monitoring
    this.app.use('/api/v1/metrics', metricsRoutes);
    this.app.use('/metrics', metricsRoutes);

    // Phase 2A routes
    this.app.use('/api/xynergyos/v2/slack', slackRoutes);
    this.app.use('/api/xynergyos/v2/gmail', gmailRoutes);
    // this.app.use('/api/xynergyos/v2/calendar', calendarRoutes);
    // this.app.use('/api/xynergyos/v2/crm', crmRoutes);

    // 404 handler
    this.app.use((req, res) => {
      res.status(404).json({
        error: 'Not Found',
        message: `Route ${req.method} ${req.path} not found`,
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

      // Log CORS configuration
      logCorsConfig();

      // Initialize Cache Service (optional - graceful degradation if Redis unavailable)
      try {
        await initializeCacheService();
        logger.info('Cache service initialized');
      } catch (error: any) {
        logger.warn('Cache service unavailable, continuing without caching', { error: error.message });
      }

      // Initialize WebSocket
      initializeWebSocket(this.httpServer);
      logger.info('WebSocket initialized');

      // Start server
      this.httpServer.listen(appConfig.port, () => {
        logger.info('Server started', {
          port: appConfig.port,
          environment: appConfig.nodeEnv,
          service: 'xynergyos-intelligence-gateway',
          features: [
            'Firebase Auth',
            'WebSocket (Socket.io)',
            'Redis Adapter',
            'Rate Limiting',
            'Request ID Tracking',
            'Enhanced CORS',
            'Redis Caching',
            'Circuit Breakers',
            'Metrics API',
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
      // Clean up WebSocket connections
      const ws = getWebSocketService();
      ws.cleanup().then(() => {
        this.httpServer.close(() => {
          logger.info('Server stopped');
          resolve();
        });
      });
    });
  }
}
