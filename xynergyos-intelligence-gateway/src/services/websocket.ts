import { Server as HttpServer } from 'http';
import { Server as SocketIOServer, Socket } from 'socket.io';
import { createClient } from 'redis';
import { createAdapter } from '@socket.io/redis-adapter';
import { getFirebaseAuth } from '../config/firebase';
import { logger } from '../utils/logger';
import { appConfig } from '../config/config';

interface AuthenticatedSocket extends Socket {
  userId?: string;
  tenantId?: string;
}

export class WebSocketService {
  private io: SocketIOServer;
  private redisClient?: any;
  private redisPubClient?: any;
  private redisSubClient?: any;

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
    this.initializeRedisAdapter();
  }

  private async initializeRedisAdapter(): Promise<void> {
    try {
      // Create Redis clients for Socket.io adapter
      const redisUrl = `redis://${appConfig.redis.host}:${appConfig.redis.port}`;

      this.redisPubClient = createClient({ url: redisUrl });
      this.redisSubClient = this.redisPubClient.duplicate();

      await Promise.all([
        this.redisPubClient.connect(),
        this.redisSubClient.connect(),
      ]);

      // Set up Redis adapter for multi-instance WebSocket support
      this.io.adapter(createAdapter(this.redisPubClient, this.redisSubClient));

      logger.info('Redis adapter initialized for WebSocket', {
        host: appConfig.redis.host,
        port: appConfig.redis.port,
      });
    } catch (error) {
      logger.error('Failed to initialize Redis adapter', { error });
      logger.warn('WebSocket will run without Redis adapter (single instance only)');
    }
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

        socket.emit('subscribed', { topics });
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

        socket.emit('unsubscribed', { topics });
      });

      // Handle disconnect
      socket.on('disconnect', () => {
        logger.info('WebSocket disconnected', {
          userId: socket.userId,
          socketId: socket.id,
        });
      });

      // Handle errors
      socket.on('error', (error) => {
        logger.error('WebSocket error', {
          userId: socket.userId,
          socketId: socket.id,
          error,
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

  async cleanup(): Promise<void> {
    logger.info('Cleaning up WebSocket service');

    if (this.redisPubClient) {
      await this.redisPubClient.quit();
    }
    if (this.redisSubClient) {
      await this.redisSubClient.quit();
    }

    logger.info('WebSocket cleanup complete');
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
