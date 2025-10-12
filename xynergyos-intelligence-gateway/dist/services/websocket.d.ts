import { Server as HttpServer } from 'http';
export declare class WebSocketService {
    private io;
    private redisClient?;
    private redisPubClient?;
    private redisSubClient?;
    private connections;
    private connectionTimestamps;
    constructor(httpServer: HttpServer);
    private initializeRedisAdapter;
    private setupMiddleware;
    private setupHandlers;
    private startConnectionCleanup;
    getConnectionStats(): {
        totalConnections: number;
        uniqueUsers: number;
        maxConnectionsPerUser: number;
        maxTotalConnections: number;
        utilizationPercentage: number;
    };
    broadcast(tenantId: string, topic: string, event: string, data: any): void;
    sendToUser(userId: string, event: string, data: any): void;
    cleanup(): Promise<void>;
}
export declare const initializeWebSocket: (httpServer: HttpServer) => WebSocketService;
export declare const getWebSocketService: () => WebSocketService;
//# sourceMappingURL=websocket.d.ts.map