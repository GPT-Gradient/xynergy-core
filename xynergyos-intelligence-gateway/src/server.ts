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
import authRoutes from './routes/auth';
import profileRoutes from './routes/profile';
import oauthRoutes from './routes/oauth';
import integrationsRoutes from './routes/integrations';
import slackRoutes from './routes/slack';
import gmailRoutes from './routes/gmail';
import crmRoutes from './routes/crm';
import aiRoutes from './routes/ai';
import marketingRoutes from './routes/marketing';
import asoRoutes from './routes/aso';
import memoryRoutes from './routes/memory';
import researchRoutes from './routes/research';
import calendarRoutes from './routes/calendar';
import intelligenceRoutes from './routes/intelligence';
import adminRoutes from './routes/admin';
import projectsRoutes from './routes/projects';

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

    // Authentication (no auth middleware - these endpoints create tokens)
    this.app.use('/api/v1/auth', authRoutes);

    // User Profile (authenticated)
    this.app.use('/api/v1/profile', profileRoutes);

    // OAuth and Integrations Management (authenticated)
    this.app.use('/api/v1/oauth', oauthRoutes);
    this.app.use('/api/v1/integrations', integrationsRoutes);

    // Intelligence Gateway routes (with path aliases for frontend compatibility)
    // Original paths: /api/xynergyos/v2/*
    this.app.use('/api/xynergyos/v2/slack', slackRoutes);
    this.app.use('/api/xynergyos/v2/gmail', gmailRoutes);
    this.app.use('/api/xynergyos/v2/crm', crmRoutes);
    // this.app.use('/api/xynergyos/v2/calendar', calendarRoutes); // TODO: Create calendar service

    // Path aliases for frontend: /api/v2/*
    this.app.use('/api/v2/slack', slackRoutes);
    this.app.use('/api/v2/gmail', gmailRoutes);
    this.app.use('/api/v2/email', gmailRoutes); // Frontend uses "email" instead of "gmail"
    this.app.use('/api/v2/crm', crmRoutes);
    this.app.use('/api/v2/calendar', calendarRoutes);

    // Platform service routes (v1 API)
    this.app.use('/api/v1/ai', aiRoutes);
    this.app.use('/api/v1/marketing', marketingRoutes);
    this.app.use('/api/v1/aso', asoRoutes);
    this.app.use('/api/v1/memory', memoryRoutes);
    this.app.use('/api/v1/research-sessions', researchRoutes);
    this.app.use('/api/v1/intelligence', intelligenceRoutes);

    // Admin and Projects routes (authenticated)
    this.app.use('/api/v1/admin', adminRoutes);
    this.app.use('/api/v1/projects', projectsRoutes);

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
