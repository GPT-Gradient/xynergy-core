import express, { Application, Request, Response } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import { createServer, Server as HttpServer } from 'http';
import { initializeFirebase } from './config/firebase';
import { errorHandler } from './middleware/errorHandler';
import { logger } from './utils/logger';
import { randomUUID } from 'crypto';
import healthRoutes from './routes/health';
import calendarRoutes from './routes/calendar';

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
    this.app.use((req, res, next) => {
      const requestId = (req.headers['x-request-id'] as string) || randomUUID();
      (req as any).requestId = requestId;
      res.setHeader('X-Request-ID', requestId);
      next();
    });
    this.app.use(helmet());
    this.app.use(cors({ origin: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'], credentials: true }));
    this.app.use(compression());
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use((req, res, next) => {
      const startTime = Date.now();
      res.on('finish', () => {
        logger.info('Request completed', {
          requestId: (req as any).requestId,
          method: req.method,
          path: req.path,
          statusCode: res.statusCode,
          duration: `${Date.now() - startTime}ms`,
        });
      });
      next();
    });
  }

  private initializeRoutes(): void {
    this.app.use('/health', healthRoutes);
    this.app.use('/api/v1/health', healthRoutes);
    this.app.use('/api/v1/calendar', calendarRoutes);
    this.app.get('/', (req: Request, res: Response) => {
      res.json({
        service: 'calendar-intelligence-service',
        version: '1.0.0',
        status: 'operational',
        endpoints: [
          'GET /health',
          'GET /api/v1/calendar/events',
          'GET /api/v1/calendar/events/:id',
          'POST /api/v1/calendar/events',
          'PATCH /api/v1/calendar/events/:id',
          'DELETE /api/v1/calendar/events/:id',
          'GET /api/v1/calendar/prep/:eventId',
        ],
        timestamp: new Date().toISOString(),
      });
    });
    this.app.use((req: Request, res: Response) => {
      res.status(404).json({ error: 'Not Found', message: `Route ${req.method} ${req.path} not found` });
    });
  }

  private initializeErrorHandling(): void {
    this.app.use(errorHandler);
  }

  async start(): Promise<void> {
    try {
      initializeFirebase();
      logger.info('Firebase initialized');
      this.httpServer.listen(parseInt(process.env.PORT || '8080'), () => {
        logger.info('Server started', { port: process.env.PORT || 8080, service: 'calendar-intelligence-service' });
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
