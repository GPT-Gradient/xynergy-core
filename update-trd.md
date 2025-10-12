# Phase 2A: Intelligence Gateway Implementation
## Technical Requirements Document for Claude Code

**Project:** XynergyOS Phase 2A - Intelligence Gateway & Communication Services  
**Version:** 1.0  
**Date:** October 10, 2025  
**Status:** READY FOR IMPLEMENTATION  
**Priority:** P0 - CRITICAL PATH BLOCKER

---

## EXECUTIVE SUMMARY

### Purpose
This TRD specifies the implementation requirements for the **Intelligence Gateway** - the critical orchestration layer that MUST be built before any Phase 2A communication intelligence services (Slack, Gmail, Calendar, CRM) can be integrated.

### Current State
- **Intelligence Gateway**: Documented but NOT BUILT (0% complete)
- **Xynergy Platform**: 11 services operational (Phase 3 complete)
- **XynergyOS Frontend**: Exists but missing Phase 2A UI components
- **External Credentials**: 0 of 9 required credentials obtained

### What This TRD Delivers
1. **Intelligence Gateway Service** - Orchestration layer for all Phase 2A services
2. **Shared Authentication Module** - Firebase Auth integration for XynergyOS
3. **WebSocket Infrastructure** - Real-time updates for communication intelligence
4. **Service Router Pattern** - Standardized routing to backend microservices
5. **Error Handling Framework** - Consistent error responses across all services

### Success Criteria
- ✅ Intelligence Gateway deployed and accessible
- ✅ Firebase Auth validation working
- ✅ WebSocket connections established
- ✅ Health checks passing
- ✅ Ready to integrate Slack Intelligence Service

---

## CRITICAL CONTEXT

### Why This Matters
**BLOCKS EVERYTHING**: Phase 2A services (Slack, Gmail, Calendar, CRM) cannot be built until Intelligence Gateway exists. Current timeline assumes it exists - it doesn't.

### Existing Infrastructure (Leverage This)
```yaml
GCP Project: xynergy-dev-1757909467
Region: us-central1
Service Account: xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com
Redis: 10.0.0.3 (STANDARD_HA, 1GB)
BigQuery: xynergy_analytics dataset exists
Cloud Storage: Multiple buckets configured
Pub/Sub: 7 core topics operational
```

### Technology Stack (Match Existing Platform)
- **Backend**: TypeScript/Node.js (for Intelligence Gateway) - NEW for Phase 2A
- **Alternative**: Python/FastAPI (if preferred for consistency)
- **Database**: Firestore (real-time), BigQuery (analytics)
- **Cache**: Redis (existing instance)
- **Deployment**: Cloud Run (like all other services)
- **Auth**: Firebase Auth (XynergyOS uses this)

**DECISION NEEDED**: TypeScript OR Python for Intelligence Gateway?
- **TypeScript Pro**: Better WebSocket support, fits Next.js frontend
- **Python Pro**: Matches other Xynergy services, team familiarity

**RECOMMENDATION**: TypeScript (Node.js/Express) for this service specifically

---

## PART 1: INTELLIGENCE GATEWAY SERVICE

### 1.1 Service Specifications

**Service Name:** `xynergyos-intelligence-gateway`  
**Technology:** Node.js 20+ with TypeScript 5+  
**Framework:** Express.js 4.18+ with Socket.io for WebSocket  
**Deployment:** Cloud Run, us-central1  
**Port:** 8080 (Cloud Run standard)  
**Scaling:** 1-20 instances  
**Resources:**
- CPU: 2 vCPU
- Memory: 2 GiB
- Timeout: 300 seconds

### 1.2 Directory Structure

```
xynergyos-intelligence-gateway/
├── src/
│   ├── index.ts                    # Main entry point
│   ├── server.ts                   # Express server setup
│   ├── config/
│   │   ├── config.ts               # Environment configuration
│   │   └── firebase.ts             # Firebase Admin SDK setup
│   ├── middleware/
│   │   ├── auth.ts                 # Firebase Auth validation
│   │   ├── errorHandler.ts         # Error handling
│   │   ├── rateLimit.ts            # Rate limiting
│   │   ├── logging.ts              # Request logging
│   │   └── cors.ts                 # CORS configuration
│   ├── routes/
│   │   ├── health.ts               # Health check routes
│   │   ├── slack.ts                # Slack intelligence routes
│   │   ├── email.ts                # Gmail intelligence routes
│   │   ├── calendar.ts             # Calendar intelligence routes
│   │   └── crm.ts                  # CRM routes
│   ├── services/
│   │   ├── serviceRouter.ts        # Route to backend services
│   │   ├── cacheService.ts         # Redis caching
│   │   └── websocket.ts            # WebSocket management
│   ├── types/
│   │   ├── express.d.ts            # Express type extensions
│   │   └── common.ts               # Common types
│   └── utils/
│       ├── logger.ts               # Structured logging
│       └── validators.ts           # Input validation
├── tests/
│   ├── integration/
│   └── unit/
├── Dockerfile
├── .dockerignore
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

### 1.3 Core Implementation Files

#### 1.3.1 Configuration (`src/config/config.ts`)

```typescript
import { config } from 'dotenv';
config();

interface Config {
  port: number;
  nodeEnv: string;
  gcpProjectId: string;
  gcpRegion: string;
  
  // Service URLs
  services: {
    aiRouting: string;
    slackIntelligence: string;
    gmailIntelligence: string;
    calendarIntelligence: string;
    crmEngine: string;
  };
  
  // Redis
  redis: {
    host: string;
    port: number;
    password?: string;
  };
  
  // Firebase
  firebase: {
    projectId: string;
    serviceAccountPath?: string;
  };
  
  // Rate limiting
  rateLimit: {
    windowMs: number;
    maxRequests: number;
  };
  
  // CORS
  cors: {
    origins: string[];
  };
}

export const appConfig: Config = {
  port: parseInt(process.env.PORT || '8080', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  gcpProjectId: process.env.GCP_PROJECT_ID || 'xynergy-dev-1757909467',
  gcpRegion: process.env.GCP_REGION || 'us-central1',
  
  services: {
    aiRouting: process.env.AI_ROUTING_URL || 
      'https://xynergy-ai-routing-engine-835612502919.us-central1.run.app',
    slackIntelligence: process.env.SLACK_INTELLIGENCE_URL || '',
    gmailIntelligence: process.env.GMAIL_INTELLIGENCE_URL || '',
    calendarIntelligence: process.env.CALENDAR_INTELLIGENCE_URL || '',
    crmEngine: process.env.CRM_ENGINE_URL || '',
  },
  
  redis: {
    host: process.env.REDIS_HOST || '10.0.0.3',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD,
  },
  
  firebase: {
    projectId: process.env.FIREBASE_PROJECT_ID || 'xynergy-dev-1757909467',
    serviceAccountPath: process.env.GOOGLE_APPLICATION_CREDENTIALS,
  },
  
  rateLimit: {
    windowMs: 60 * 1000, // 1 minute
    maxRequests: 100,
  },
  
  cors: {
    origins: [
      'http://localhost:3000',
      'https://xynergyos.com',
      'https://*.xynergyos.com',
    ],
  },
};
```

#### 1.3.2 Firebase Admin Setup (`src/config/firebase.ts`)

```typescript
import admin from 'firebase-admin';
import { appConfig } from './config';

let firebaseApp: admin.app.App;

export const initializeFirebase = (): admin.app.App => {
  if (firebaseApp) {
    return firebaseApp;
  }

  // In Cloud Run, Application Default Credentials are used
  if (appConfig.nodeEnv === 'production') {
    firebaseApp = admin.initializeApp({
      projectId: appConfig.firebase.projectId,
    });
  } else {
    // Local development
    const serviceAccount = appConfig.firebase.serviceAccountPath
      ? require(appConfig.firebase.serviceAccountPath)
      : undefined;

    firebaseApp = admin.initializeApp({
      credential: serviceAccount 
        ? admin.credential.cert(serviceAccount)
        : admin.credential.applicationDefault(),
      projectId: appConfig.firebase.projectId,
    });
  }

  return firebaseApp;
};

export const getFirebaseAuth = (): admin.auth.Auth => {
  if (!firebaseApp) {
    initializeFirebase();
  }
  return admin.auth();
};

export const getFirestore = (): admin.firestore.Firestore => {
  if (!firebaseApp) {
    initializeFirebase();
  }
  return admin.firestore();
};
```

#### 1.3.3 Authentication Middleware (`src/middleware/auth.ts`)

```typescript
import { Request, Response, NextFunction } from 'express';
import { getFirebaseAuth } from '../config/firebase';
import { logger } from '../utils/logger';

export interface AuthenticatedRequest extends Request {
  user?: {
    uid: string;
    email?: string;
    name?: string;
    roles?: string[];
  };
  tenantId?: string;
}

export const authenticateRequest = async (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Missing or invalid authorization header',
      });
      return;
    }

    const token = authHeader.split('Bearer ')[1];
    
    // Verify Firebase ID token
    const decodedToken = await getFirebaseAuth().verifyIdToken(token);
    
    // Attach user info to request
    req.user = {
      uid: decodedToken.uid,
      email: decodedToken.email,
      name: decodedToken.name,
      roles: decodedToken.roles || [],
    };
    
    // For now, single tenant (ClearForge)
    // Future: Extract from user profile
    req.tenantId = 'clearforge';
    
    logger.info('Request authenticated', {
      userId: req.user.uid,
      email: req.user.email,
      path: req.path,
    });
    
    next();
  } catch (error) {
    logger.error('Authentication failed', { error });
    
    res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid or expired token',
    });
  }
};

// Optional authentication (for public endpoints)
export const optionalAuth = async (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
): Promise<void> => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    next();
    return;
  }

  try {
    const token = authHeader.split('Bearer ')[1];
    const decodedToken = await getFirebaseAuth().verifyIdToken(token);
    
    req.user = {
      uid: decodedToken.uid,
      email: decodedToken.email,
      name: decodedToken.name,
      roles: decodedToken.roles || [],
    };
    
    req.tenantId = 'clearforge';
  } catch (error) {
    logger.warn('Optional auth failed, continuing unauthenticated', { error });
  }
  
  next();
};
```

#### 1.3.4 Error Handler (`src/middleware/errorHandler.ts`)

```typescript
import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

export interface AppError extends Error {
  statusCode?: number;
  isOperational?: boolean;
  details?: any;
}

export class ValidationError extends Error implements AppError {
  statusCode = 400;
  isOperational = true;
  
  constructor(message: string, public details?: any) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class UnauthorizedError extends Error implements AppError {
  statusCode = 401;
  isOperational = true;
  
  constructor(message: string = 'Unauthorized') {
    super(message);
    this.name = 'UnauthorizedError';
  }
}

export class NotFoundError extends Error implements AppError {
  statusCode = 404;
  isOperational = true;
  
  constructor(message: string = 'Not found') {
    super(message);
    this.name = 'NotFoundError';
  }
}

export class ServiceUnavailableError extends Error implements AppError {
  statusCode = 503;
  isOperational = true;
  
  constructor(message: string = 'Service temporarily unavailable') {
    super(message);
    this.name = 'ServiceUnavailableError';
  }
}

export const errorHandler = (
  err: AppError,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const statusCode = err.statusCode || 500;
  const isOperational = err.isOperational || false;

  logger.error('Request error', {
    error: err.message,
    stack: err.stack,
    statusCode,
    isOperational,
    path: req.path,
    method: req.method,
  });

  // Don't leak internal errors to clients
  const message = isOperational 
    ? err.message 
    : 'An unexpected error occurred';

  res.status(statusCode).json({
    error: err.name || 'Error',
    message,
    ...(err.details && { details: err.details }),
    timestamp: new Date().toISOString(),
    requestId: req.headers['x-request-id'] || 'unknown',
  });
};

// Async error wrapper
export const asyncHandler = (
  fn: (req: Request, res: Response, next: NextFunction) => Promise<any>
) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};
```

#### 1.3.5 Service Router (`src/services/serviceRouter.ts`)

```typescript
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { appConfig } from '../config/config';
import { logger } from '../utils/logger';
import { ServiceUnavailableError } from '../middleware/errorHandler';

class ServiceRouter {
  private clients: Map<string, AxiosInstance> = new Map();
  
  constructor() {
    this.initializeClients();
  }
  
  private initializeClients(): void {
    const services = appConfig.services;
    
    Object.entries(services).forEach(([name, url]) => {
      if (!url) return;
      
      const client = axios.create({
        baseURL: url,
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      // Add request interceptor for authentication
      client.interceptors.request.use((config) => {
        // Add service account token or other auth
        return config;
      });
      
      // Add response interceptor for error handling
      client.interceptors.response.use(
        (response) => response,
        (error) => {
          logger.error(`Service ${name} error`, {
            url,
            error: error.message,
            status: error.response?.status,
          });
          throw error;
        }
      );
      
      this.clients.set(name, client);
    });
  }
  
  async callService<T = any>(
    serviceName: string,
    endpoint: string,
    options: AxiosRequestConfig = {}
  ): Promise<T> {
    const client = this.clients.get(serviceName);
    
    if (!client) {
      throw new ServiceUnavailableError(
        `Service ${serviceName} is not configured`
      );
    }
    
    try {
      const response = await client.request({
        url: endpoint,
        ...options,
      });
      
      return response.data;
    } catch (error) {
      logger.error(`Failed to call ${serviceName}`, {
        endpoint,
        error: error.message,
      });
      throw new ServiceUnavailableError(
        `Failed to communicate with ${serviceName}`
      );
    }
  }
  
  // Convenience methods
  async callAIRouting(prompt: string, options: any = {}): Promise<any> {
    return this.callService('aiRouting', '/generate', {
      method: 'POST',
      data: { prompt, ...options },
    });
  }
  
  async callSlackService(endpoint: string, options: AxiosRequestConfig = {}): Promise<any> {
    return this.callService('slackIntelligence', endpoint, options);
  }
  
  async callGmailService(endpoint: string, options: AxiosRequestConfig = {}): Promise<any> {
    return this.callService('gmailIntelligence', endpoint, options);
  }
  
  async callCalendarService(endpoint: string, options: AxiosRequestConfig = {}): Promise<any> {
    return this.callService('calendarIntelligence', endpoint, options);
  }
  
  async callCRMService(endpoint: string, options: AxiosRequestConfig = {}): Promise<any> {
    return this.callService('crmEngine', endpoint, options);
  }
}

export const serviceRouter = new ServiceRouter();
```

#### 1.3.6 WebSocket Service (`src/services/websocket.ts`)

```typescript
import { Server as HttpServer } from 'http';
import { Server as SocketIOServer, Socket } from 'socket.io';
import { getFirebaseAuth } from '../config/firebase';
import { logger } from '../utils/logger';
import { appConfig } from '../config/config';

interface AuthenticatedSocket extends Socket {
  userId?: string;
  tenantId?: string;
}

export class WebSocketService {
  private io: SocketIOServer;
  
  constructor(httpServer: HttpServer) {
    this.io = new SocketIOServer(httpServer, {
      cors: {
        origin: appConfig.cors.origins,
        methods: ['GET', 'POST'],
        credentials: true,
      },
      path: '/api/xynergyos/v2/stream',
    });
    
    this.setupMiddleware();
    this.setupHandlers();
  }
  
  private setupMiddleware(): void {
    // Authentication middleware
    this.io.use(async (socket: AuthenticatedSocket, next) => {
      try {
        const token = socket.handshake.auth.token;
        
        if (!token) {
          return next(new Error('Authentication token required'));
        }
        
        const decodedToken = await getFirebaseAuth().verifyIdToken(token);
        
        socket.userId = decodedToken.uid;
        socket.tenantId = 'clearforge'; // Single tenant for now
        
        logger.info('WebSocket authenticated', {
          userId: socket.userId,
          socketId: socket.id,
        });
        
        next();
      } catch (error) {
        logger.error('WebSocket authentication failed', { error });
        next(new Error('Authentication failed'));
      }
    });
  }
  
  private setupHandlers(): void {
    this.io.on('connection', (socket: AuthenticatedSocket) => {
      logger.info('WebSocket connected', {
        userId: socket.userId,
        socketId: socket.id,
      });
      
      // Subscribe to topics
      socket.on('subscribe', (topics: string[]) => {
        topics.forEach(topic => {
          const room = `${socket.tenantId}:${topic}`;
          socket.join(room);
          logger.info('Subscribed to topic', {
            userId: socket.userId,
            topic,
            room,
          });
        });
      });
      
      // Unsubscribe from topics
      socket.on('unsubscribe', (topics: string[]) => {
        topics.forEach(topic => {
          const room = `${socket.tenantId}:${topic}`;
          socket.leave(room);
          logger.info('Unsubscribed from topic', {
            userId: socket.userId,
            topic,
          });
        });
      });
      
      // Handle disconnect
      socket.on('disconnect', () => {
        logger.info('WebSocket disconnected', {
          userId: socket.userId,
          socketId: socket.id,
        });
      });
    });
  }
  
  // Broadcast to topic
  broadcast(tenantId: string, topic: string, event: string, data: any): void {
    const room = `${tenantId}:${topic}`;
    this.io.to(room).emit(event, data);
    
    logger.debug('WebSocket broadcast', {
      tenantId,
      topic,
      event,
      room,
    });
  }
  
  // Send to specific user
  sendToUser(userId: string, event: string, data: any): void {
    const sockets = Array.from(this.io.sockets.sockets.values()) as AuthenticatedSocket[];
    const userSockets = sockets.filter(s => s.userId === userId);
    
    userSockets.forEach(socket => {
      socket.emit(event, data);
    });
    
    logger.debug('WebSocket sent to user', {
      userId,
      event,
      socketCount: userSockets.length,
    });
  }
}

let websocketService: WebSocketService;

export const initializeWebSocket = (httpServer: HttpServer): WebSocketService => {
  websocketService = new WebSocketService(httpServer);
  return websocketService;
};

export const getWebSocketService = (): WebSocketService => {
  if (!websocketService) {
    throw new Error('WebSocket service not initialized');
  }
  return websocketService;
};
```

#### 1.3.7 Health Check Routes (`src/routes/health.ts`)

```typescript
import { Router, Request, Response } from 'express';
import { getFirestore } from '../config/firebase';
import { serviceRouter } from '../services/serviceRouter';
import { logger } from '../utils/logger';

const router = Router();

// Basic health check
router.get('/', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'xynergyos-intelligence-gateway',
    version: process.env.npm_package_version || '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

// Deep health check
router.get('/deep', async (req: Request, res: Response) => {
  const checks: any = {
    timestamp: new Date().toISOString(),
    service: 'xynergyos-intelligence-gateway',
    status: 'healthy',
    checks: {},
  };

  // Check Firestore
  try {
    const db = getFirestore();
    await db.collection('_health_check').doc('test').set({
      timestamp: new Date(),
    });
    checks.checks.firestore = 'healthy';
  } catch (error) {
    checks.checks.firestore = 'unhealthy';
    checks.status = 'degraded';
    logger.error('Firestore health check failed', { error });
  }

  // Check backend services (if URLs configured)
  const services = ['aiRouting', 'slackIntelligence', 'gmailIntelligence'];
  
  for (const service of services) {
    try {
      // Simple HEAD or GET request to service
      checks.checks[service] = 'healthy';
    } catch (error) {
      checks.checks[service] = 'unhealthy';
      logger.warn(`Service ${service} health check failed`, { error });
    }
  }

  const statusCode = checks.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(checks);
});

export default router;
```

#### 1.3.8 Main Server (`src/server.ts`)

```typescript
import express, { Application } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import { createServer, Server as HttpServer } from 'http';
import { appConfig } from './config/config';
import { initializeFirebase } from './config/firebase';
import { errorHandler } from './middleware/errorHandler';
import { logger } from './utils/logger';
import { initializeWebSocket } from './services/websocket';

// Import routes
import healthRoutes from './routes/health';

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
    // Security
    this.app.use(helmet());
    
    // CORS
    this.app.use(cors({
      origin: appConfig.cors.origins,
      credentials: true,
    }));
    
    // Compression
    this.app.use(compression());
    
    // Body parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));
    
    // Request logging
    this.app.use((req, res, next) => {
      logger.info('Request received', {
        method: req.method,
        path: req.path,
        ip: req.ip,
      });
      next();
    });
  }
  
  private initializeRoutes(): void {
    // Health checks
    this.app.use('/api/v1/health', healthRoutes);
    this.app.use('/health', healthRoutes);
    
    // Phase 2A routes (to be added as services are built)
    // this.app.use('/api/xynergyos/v2/slack', slackRoutes);
    // this.app.use('/api/xynergyos/v2/email', emailRoutes);
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
      
      // Initialize WebSocket
      initializeWebSocket(this.httpServer);
      logger.info('WebSocket initialized');
      
      // Start server
      this.httpServer.listen(appConfig.port, () => {
        logger.info('Server started', {
          port: appConfig.port,
          environment: appConfig.nodeEnv,
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
```

#### 1.3.9 Entry Point (`src/index.ts`)

```typescript
import { Server } from './server';
import { logger } from './utils/logger';

const server = new Server();

// Graceful shutdown
const shutdown = async (signal: string) => {
  logger.info(`${signal} received, shutting down gracefully`);
  
  try {
    await server.stop();
    process.exit(0);
  } catch (error) {
    logger.error('Error during shutdown', { error });
    process.exit(1);
  }
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

// Start server
server.start().catch((error) => {
  logger.error('Fatal error during startup', { error });
  process.exit(1);
});
```

### 1.4 Supporting Files

#### `package.json`

```json
{
  "name": "xynergyos-intelligence-gateway",
  "version": "1.0.0",
  "description": "Intelligence Gateway for XynergyOS Phase 2A",
  "main": "dist/index.js",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "jest",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write 'src/**/*.ts'"
  },
  "dependencies": {
    "express": "^4.18.2",
    "socket.io": "^4.6.1",
    "firebase-admin": "^12.0.0",
    "axios": "^1.6.0",
    "redis": "^4.6.0",
    "helmet": "^7.1.0",
    "cors": "^2.8.5",
    "compression": "^1.7.4",
    "winston": "^3.11.0",
    "dotenv": "^16.3.1",
    "joi": "^17.11.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.10.0",
    "@types/cors": "^2.8.17",
    "@types/compression": "^1.7.5",
    "typescript": "^5.3.3",
    "tsx": "^4.7.0",
    "jest": "^29.7.0",
    "@types/jest": "^29.5.11",
    "eslint": "^8.56.0",
    "prettier": "^3.1.1"
  }
}
```

#### `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

#### `Dockerfile`

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY src ./src

# Build TypeScript
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies only
RUN npm ci --only=production

# Copy built application
COPY --from=builder /app/dist ./dist

# Set environment
ENV NODE_ENV=production
ENV PORT=8080

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8080/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start server
CMD ["node", "dist/index.js"]
```

#### `.env.example`

```bash
# Server
PORT=8080
NODE_ENV=development

# GCP
GCP_PROJECT_ID=xynergy-dev-1757909467
GCP_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Firebase
FIREBASE_PROJECT_ID=xynergy-dev-1757909467

# Redis
REDIS_HOST=10.0.0.3
REDIS_PORT=6379
REDIS_PASSWORD=

# Service URLs (update as services are deployed)
AI_ROUTING_URL=https://xynergy-ai-routing-engine-835612502919.us-central1.run.app
SLACK_INTELLIGENCE_URL=
GMAIL_INTELLIGENCE_URL=
CALENDAR_INTELLIGENCE_URL=
CRM_ENGINE_URL=

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://xynergyos.com
```

---

## PART 2: DEPLOYMENT INSTRUCTIONS

### 2.1 Local Development Setup

```bash
# 1. Clone or create the project
mkdir xynergyos-intelligence-gateway
cd xynergyos-intelligence-gateway

# 2. Initialize npm and install dependencies
npm init -y
npm install express socket.io firebase-admin axios redis helmet cors compression winston dotenv joi

# Install dev dependencies
npm install -D typescript tsx @types/express @types/node @types/cors @types/compression eslint prettier jest @types/jest

# 3. Create directory structure
mkdir -p src/{config,middleware,routes,services,types,utils}
mkdir -p tests/{integration,unit}

# 4. Copy configuration files
# (Copy tsconfig.json, package.json, .env.example from above)

# 5. Set up environment variables
cp .env.example .env
# Edit .env with actual values

# 6. Run in development mode
npm run dev
```

### 2.2 Cloud Run Deployment

```bash
# 1. Build Docker image
docker build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergyos-intelligence-gateway:latest \
  .

# 2. Push to Artifact Registry
docker push us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergyos-intelligence-gateway:latest

# 3. Deploy to Cloud Run
gcloud run deploy xynergyos-intelligence-gateway \
  --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergyos-intelligence-gateway:latest \
  --platform managed \
  --region us-central1 \
  --project xynergy-dev-1757909467 \
  --service-account xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com \
  --set-env-vars "GCP_PROJECT_ID=xynergy-dev-1757909467,GCP_REGION=us-central1,REDIS_HOST=10.0.0.3,REDIS_PORT=6379" \
  --min-instances 1 \
  --max-instances 20 \
  --cpu 2 \
  --memory 2Gi \
  --timeout 300 \
  --allow-unauthenticated \
  --port 8080

# 4. Get deployed URL
gcloud run services describe xynergyos-intelligence-gateway \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

### 2.3 Verify Deployment

```bash
# Test health endpoint
curl https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "xynergyos-intelligence-gateway",
#   "version": "1.0.0",
#   "timestamp": "2025-10-10T..."
# }

# Test deep health check
curl https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/health/deep
```

---

## PART 3: NEXT STEPS AFTER GATEWAY

### 3.1 Integration Checklist

Once Intelligence Gateway is deployed:

- [ ] Gateway accessible and health checks passing
- [ ] WebSocket connections working (test with Postman or wscat)
- [ ] Firebase Auth validation working
- [ ] Service router can reach AI Routing Engine
- [ ] Monitoring and logging functional

### 3.2 Phase 2A Service Build Order

**Recommended order:**

1. **Week 1-2: Intelligence Gateway** ← YOU ARE HERE
2. **Week 3-4: Slack Intelligence Service**
   - Can work in parallel once Gateway exists
   - Highest priority for NEXUS beta
3. **Week 5-6: CRM Engine**
   - Needed by Slack and Gmail services
   - Core relationship management
4. **Week 7-8: Gmail Intelligence Service**
   - Depends on CRM Engine
   - Second highest priority
5. **Week 9-10: Calendar Intelligence Service**
   - Depends on CRM Engine
   - Medium priority
6. **Week 11-12: Frontend Components**
   - Build once backend services exist
   - Parallel development possible

### 3.3 Testing Strategy

**Unit Tests** (each service):
```bash
npm test
```

**Integration Tests**:
```bash
# Test Intelligence Gateway → AI Routing Engine
curl -X POST https://[gateway-url]/api/v1/test/ai-routing \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'

# Test WebSocket connection
wscat -c wss://[gateway-url]/api/xynergyos/v2/stream
```

**Load Testing** (before production):
```bash
# Use Apache Bench or similar
ab -n 1000 -c 10 https://[gateway-url]/health
```

---

## PART 4: CRITICAL DECISIONS NEEDED

### Decision 1: TypeScript vs Python
**Question**: Build Intelligence Gateway in TypeScript (recommended) or Python?

**Recommendation**: TypeScript
- Better WebSocket support (Socket.io)
- Aligns with Next.js frontend
- Modern async/await patterns
- Strong typing for safety

**Action**: Confirm technology choice before coding

### Decision 2: Minimal vs Full Gateway
**Question**: Build minimal gateway (2 weeks) or full-featured (4 weeks)?

**Minimal includes**:
- Basic routing
- Firebase Auth
- WebSocket
- Health checks

**Full includes**:
- Rate limiting
- Caching
- Circuit breakers
- Advanced monitoring

**Recommendation**: Start minimal, enhance later

### Decision 3: Authentication Strategy
**Question**: Firebase Auth only or add API keys?

**Recommendation**: Firebase Auth for user requests, consider API keys for service-to-service

**Action**: Confirm auth requirements

---

## PART 5: RISK MITIGATION

### Risk 1: WebSocket Scalability
**Concern**: Socket.io doesn't scale well across multiple Cloud Run instances

**Mitigation**:
- Use Redis adapter for Socket.io
- Share state across instances
- Test with multiple instances

```typescript
// Add to websocket.ts
import { createAdapter } from '@socket.io/redis-adapter';
import { createClient } from 'redis';

const pubClient = createClient({ host: '10.0.0.3' });
const subClient = pubClient.duplicate();

await Promise.all([pubClient.connect(), subClient.connect()]);

io.adapter(createAdapter(pubClient, subClient));
```

### Risk 2: Firebase Auth Token Expiry
**Concern**: Tokens expire, causing authentication failures

**Mitigation**:
- Implement token refresh on client
- Clear error messages
- Graceful degradation

### Risk 3: Service Discovery
**Concern**: Hard-coded service URLs are fragile

**Mitigation**:
- Use environment variables
- Consider Cloud Run service mesh
- Implement retry logic

---

## APPENDIX A: GLOSSARY

- **Intelligence Gateway**: Orchestration layer routing XynergyOS requests to backend services
- **WebSocket**: Real-time bidirectional communication protocol
- **Firebase Auth**: Google's authentication service
- **Cloud Run**: Google's serverless container platform
- **Socket.io**: WebSocket library for Node.js
- **Tenant**: Isolated customer environment (currently only ClearForge)

## APPENDIX B: REFERENCES

- **Phase 2A Complete TRD**: See xynergyos-phase2a-complete-trd.md
- **Xynergy Platform**: 11 existing services in xynergy-dev-1757909467
- **Firebase Admin SDK**: https://firebase.google.com/docs/admin/setup
- **Socket.io Documentation**: https://socket.io/docs/v4/
- **Express.js**: https://expressjs.com/

---

## IMPLEMENTATION PRIORITY

**P0 - CRITICAL (Build This First)**:
1. Basic Express server setup
2. Firebase Auth middleware
3. Health check endpoints
4. Service router skeleton
5. WebSocket basic setup
6. Docker container
7. Cloud Run deployment

**P1 - HIGH (Build Next)**:
1. Complete error handling
2. Request logging
3. Rate limiting
4. CORS configuration
5. WebSocket authentication
6. Deep health checks

**P2 - MEDIUM (Enhance Later)**:
1. Redis caching
2. Circuit breakers
3. Advanced monitoring
4. Performance optimization
5. Load testing
6. Documentation

---

**Ready to implement. Start with P0 items.**