"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getWebSocketService = exports.initializeWebSocket = exports.WebSocketService = void 0;
const socket_io_1 = require("socket.io");
const redis_1 = require("redis");
const redis_adapter_1 = require("@socket.io/redis-adapter");
const firebase_1 = require("../config/firebase");
const logger_1 = require("../utils/logger");
const config_1 = require("../config/config");
// Connection limits for DoS protection
const MAX_CONNECTIONS_PER_USER = 5;
const MAX_TOTAL_CONNECTIONS = 1000;
const CONNECTION_TIMEOUT = 300000; // 5 minutes
const HEARTBEAT_INTERVAL = 25000; // 25 seconds
const HEARTBEAT_TIMEOUT = 60000; // 60 seconds
class WebSocketService {
    io;
    redisClient;
    redisPubClient;
    redisSubClient;
    connections = new Map();
    connectionTimestamps = new Map();
    constructor(httpServer) {
        this.io = new socket_io_1.Server(httpServer, {
            cors: {
                origin: config_1.appConfig.cors.origins,
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
    async initializeRedisAdapter() {
        try {
            // Create Redis clients for Socket.io adapter
            const redisUrl = `redis://${config_1.appConfig.redis.host}:${config_1.appConfig.redis.port}`;
            this.redisPubClient = (0, redis_1.createClient)({ url: redisUrl });
            this.redisSubClient = this.redisPubClient.duplicate();
            await Promise.all([
                this.redisPubClient.connect(),
                this.redisSubClient.connect(),
            ]);
            // Set up Redis adapter for multi-instance WebSocket support
            this.io.adapter((0, redis_adapter_1.createAdapter)(this.redisPubClient, this.redisSubClient));
            logger_1.logger.info('Redis adapter initialized for WebSocket', {
                host: config_1.appConfig.redis.host,
                port: config_1.appConfig.redis.port,
            });
        }
        catch (error) {
            logger_1.logger.error('Failed to initialize Redis adapter', { error });
            logger_1.logger.warn('WebSocket will run without Redis adapter (single instance only)');
        }
    }
    setupMiddleware() {
        // Authentication middleware
        this.io.use(async (socket, next) => {
            try {
                const token = socket.handshake.auth.token;
                if (!token) {
                    return next(new Error('Authentication token required'));
                }
                const decodedToken = await (0, firebase_1.getFirebaseAuth)().verifyIdToken(token);
                socket.userId = decodedToken.uid;
                socket.tenantId = 'clearforge'; // Single tenant for now
                logger_1.logger.info('WebSocket authenticated', {
                    userId: socket.userId,
                    socketId: socket.id,
                });
                next();
            }
            catch (error) {
                logger_1.logger.error('WebSocket authentication failed', { error });
                next(new Error('Authentication failed'));
            }
        });
    }
    setupHandlers() {
        this.io.on('connection', (socket) => {
            const userId = socket.userId || socket.id;
            // Check per-user limit
            const userConnections = this.connections.get(userId) || new Set();
            if (userConnections.size >= MAX_CONNECTIONS_PER_USER) {
                logger_1.logger.warn('Max connections per user exceeded', {
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
                logger_1.logger.warn('Max total connections exceeded', { totalConnections });
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
            logger_1.logger.info('WebSocket connected', {
                userId: socket.userId,
                socketId: socket.id,
                totalConnections: totalConnections + 1,
            });
            // Auto-disconnect stale connections
            const timeoutId = setTimeout(() => {
                if (socket.connected) {
                    logger_1.logger.info('Disconnecting stale connection', {
                        userId,
                        socketId: socket.id,
                    });
                    socket.emit('timeout', { message: 'Connection timeout' });
                    socket.disconnect();
                }
            }, CONNECTION_TIMEOUT);
            // Subscribe to topics
            socket.on('subscribe', (topics) => {
                topics.forEach(topic => {
                    const room = `${socket.tenantId}:${topic}`;
                    socket.join(room);
                    logger_1.logger.info('Subscribed to topic', {
                        userId: socket.userId,
                        topic,
                        room,
                    });
                });
                socket.emit('subscribed', { topics });
            });
            // Unsubscribe from topics
            socket.on('unsubscribe', (topics) => {
                topics.forEach(topic => {
                    const room = `${socket.tenantId}:${topic}`;
                    socket.leave(room);
                    logger_1.logger.info('Unsubscribed from topic', {
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
                logger_1.logger.info('WebSocket disconnected', {
                    userId: socket.userId,
                    socketId: socket.id,
                });
            });
            // Handle errors
            socket.on('error', (error) => {
                logger_1.logger.error('WebSocket error', {
                    userId: socket.userId,
                    socketId: socket.id,
                    error,
                });
            });
        });
    }
    startConnectionCleanup() {
        // Periodic cleanup of orphaned connections
        setInterval(() => {
            const now = Date.now();
            let cleaned = 0;
            for (const [socketId, timestamp] of this.connectionTimestamps.entries()) {
                if (now - timestamp > CONNECTION_TIMEOUT) {
                    logger_1.logger.warn('Cleaning up orphaned connection', { socketId });
                    this.connectionTimestamps.delete(socketId);
                    cleaned++;
                }
            }
            if (cleaned > 0) {
                logger_1.logger.info('Orphaned connection cleanup completed', { cleaned });
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
    broadcast(tenantId, topic, event, data) {
        const room = `${tenantId}:${topic}`;
        this.io.to(room).emit(event, data);
        logger_1.logger.debug('WebSocket broadcast', {
            tenantId,
            topic,
            event,
            room,
        });
    }
    // Send to specific user
    sendToUser(userId, event, data) {
        const sockets = Array.from(this.io.sockets.sockets.values());
        const userSockets = sockets.filter(s => s.userId === userId);
        userSockets.forEach(socket => {
            socket.emit(event, data);
        });
        logger_1.logger.debug('WebSocket sent to user', {
            userId,
            event,
            socketCount: userSockets.length,
        });
    }
    async cleanup() {
        logger_1.logger.info('Cleaning up WebSocket service');
        if (this.redisPubClient) {
            await this.redisPubClient.quit();
        }
        if (this.redisSubClient) {
            await this.redisSubClient.quit();
        }
        logger_1.logger.info('WebSocket cleanup complete');
    }
}
exports.WebSocketService = WebSocketService;
let websocketService;
const initializeWebSocket = (httpServer) => {
    websocketService = new WebSocketService(httpServer);
    return websocketService;
};
exports.initializeWebSocket = initializeWebSocket;
const getWebSocketService = () => {
    if (!websocketService) {
        throw new Error('WebSocket service not initialized');
    }
    return websocketService;
};
exports.getWebSocketService = getWebSocketService;
//# sourceMappingURL=websocket.js.map