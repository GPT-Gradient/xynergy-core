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

// Connection limits for DoS protection
const MAX_CONNECTIONS_PER_USER = 5;
const MAX_TOTAL_CONNECTIONS = 1000;
const CONNECTION_TIMEOUT = 300000; // 5 minutes
const HEARTBEAT_INTERVAL = 25000; // 25 seconds
const HEARTBEAT_TIMEOUT = 60000; // 60 seconds

export class WebSocketService {
  private io: SocketIOServer;
  private redisClient?: any;
  private redisPubClient?: any;
  private redisSubClient?: any;
  private connections: Map<string, Set<Socket>> = new Map();
  private connectionTimestamps: Map<string, number> = new Map();

  constructor(httpServer: HttpServer) {
    this.io = new SocketIOServer(httpServer, {
      cors: {
        origin: appConfig.cors.origins,
        methods: ['GET', 'POST'],
        credentials: true,
      },
      path: '/api/xynergyos/v2/stream',
      maxHttpBufferSize: 1e6, // 1MB max message size
      pingTimeout: HEARTBEAT_TIMEOUT,
      pingInterval: HEARTBEAT_INTERVAL,
      transports: ['websocket', 'polling'],
    });

    this.setupMiddleware();
    this.setupHandlers();
    this.initializeRedisAdapter();
    this.startConnectionCleanup();
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
      const userId = socket.userId || socket.id;

      // Check per-user limit
      const userConnections = this.connections.get(userId) || new Set();
      if (userConnections.size >= MAX_CONNECTIONS_PER_USER) {
        logger.warn('Max connections per user exceeded', {
          userId,
          currentConnections: userConnections.size,
        });
        socket.emit('error', {
          code: 'MAX_CONNECTIONS_EXCEEDED',
          message: 'Maximum connections per user reached',
        });
        socket.disconnect();
        return;
      }

      // Check global limit
      const totalConnections = Array.from(this.connections.values())
        .reduce((sum, set) => sum + set.size, 0);
      if (totalConnections >= MAX_TOTAL_CONNECTIONS) {
        logger.warn('Max total connections exceeded', { totalConnections });
        socket.emit('error', {
          code: 'SERVICE_CAPACITY_EXCEEDED',
          message: 'Service at maximum capacity',
        });
        socket.disconnect();
        return;
      }

      // Track connection
      userConnections.add(socket);
      this.connections.set(userId, userConnections);
      this.connectionTimestamps.set(socket.id, Date.now());

      logger.info('WebSocket connected', {
        userId: socket.userId,
        socketId: socket.id,
        totalConnections: totalConnections + 1,
      });

      // Auto-disconnect stale connections
      const timeoutId = setTimeout(() => {
        if (socket.connected) {
          logger.info('Disconnecting stale connection', {
            userId,
            socketId: socket.id,
          });
          socket.emit('timeout', { message: 'Connection timeout' });
          socket.disconnect();
        }
      }, CONNECTION_TIMEOUT);

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
        clearTimeout(timeoutId);
        userConnections.delete(socket);
        this.connectionTimestamps.delete(socket.id);
        if (userConnections.size === 0) {
          this.connections.delete(userId);
        }

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

  private startConnectionCleanup(): void {
    // Periodic cleanup of orphaned connections
    setInterval(() => {
      const now = Date.now();
      let cleaned = 0;

      for (const [socketId, timestamp] of this.connectionTimestamps.entries()) {
        if (now - timestamp > CONNECTION_TIMEOUT) {
          logger.warn('Cleaning up orphaned connection', { socketId });
          this.connectionTimestamps.delete(socketId);
          cleaned++;
        }
      }

      if (cleaned > 0) {
        logger.info('Orphaned connection cleanup completed', { cleaned });
      }
    }, 60000); // Every minute
  }

  getConnectionStats() {
    const totalConnections = Array.from(this.connections.values())
      .reduce((sum, set) => sum + set.size, 0);

    return {
      totalConnections,
      uniqueUsers: this.connections.size,
      maxConnectionsPerUser: MAX_CONNECTIONS_PER_USER,
      maxTotalConnections: MAX_TOTAL_CONNECTIONS,
      utilizationPercentage: (totalConnections / MAX_TOTAL_CONNECTIONS) * 100,
    };
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
