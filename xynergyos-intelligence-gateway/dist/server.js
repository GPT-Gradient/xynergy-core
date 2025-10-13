"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Server = void 0;
const express_1 = __importDefault(require("express"));
const helmet_1 = __importDefault(require("helmet"));
const compression_1 = __importDefault(require("compression"));
const http_1 = require("http");
const config_1 = require("./config/config");
const firebase_1 = require("./config/firebase");
const errorHandler_1 = require("./middleware/errorHandler");
const logger_1 = require("./utils/logger");
const websocket_1 = require("./services/websocket");
const cacheService_1 = require("./services/cacheService");
// Import middleware
const requestId_1 = require("./middleware/requestId");
const corsConfig_1 = require("./middleware/corsConfig");
const requestLogger_1 = require("./middleware/requestLogger");
const rateLimit_1 = require("./middleware/rateLimit");
// Import routes
const health_1 = __importDefault(require("./routes/health"));
const metrics_1 = __importDefault(require("./routes/metrics"));
const auth_1 = __importDefault(require("./routes/auth"));
const profile_1 = __importDefault(require("./routes/profile"));
const oauth_1 = __importDefault(require("./routes/oauth"));
const integrations_1 = __importDefault(require("./routes/integrations"));
const slack_1 = __importDefault(require("./routes/slack"));
const gmail_1 = __importDefault(require("./routes/gmail"));
const crm_1 = __importDefault(require("./routes/crm"));
const ai_1 = __importDefault(require("./routes/ai"));
const marketing_1 = __importDefault(require("./routes/marketing"));
const aso_1 = __importDefault(require("./routes/aso"));
const memory_1 = __importDefault(require("./routes/memory"));
const research_1 = __importDefault(require("./routes/research"));
const calendar_1 = __importDefault(require("./routes/calendar"));
const intelligence_1 = __importDefault(require("./routes/intelligence"));
const admin_1 = __importDefault(require("./routes/admin"));
const projects_1 = __importDefault(require("./routes/projects"));
class Server {
    app;
    httpServer;
    constructor() {
        this.app = (0, express_1.default)();
        this.httpServer = (0, http_1.createServer)(this.app);
        this.initializeMiddleware();
        this.initializeRoutes();
        this.initializeErrorHandling();
    }
    initializeMiddleware() {
        // Request ID (must be first to tag all logs)
        this.app.use(requestId_1.requestIdMiddleware);
        // Security headers
        this.app.use((0, helmet_1.default)());
        // CORS - Enhanced with dynamic origin checking
        this.app.use(corsConfig_1.corsMiddleware);
        // Rate limiting - Applied globally
        this.app.use(rateLimit_1.generalRateLimit);
        // Compression
        this.app.use((0, compression_1.default)());
        // Body parsing
        this.app.use(express_1.default.json({ limit: '10mb' }));
        this.app.use(express_1.default.urlencoded({ extended: true, limit: '10mb' }));
        // Enhanced request logging with request ID and timing
        this.app.use(requestLogger_1.requestLogger);
    }
    initializeRoutes() {
        // Health checks
        this.app.use('/api/v1/health', health_1.default);
        this.app.use('/health', health_1.default);
        // Metrics and monitoring
        this.app.use('/api/v1/metrics', metrics_1.default);
        this.app.use('/metrics', metrics_1.default);
        // Authentication (no auth middleware - these endpoints create tokens)
        this.app.use('/api/v1/auth', auth_1.default);
        // User Profile (authenticated)
        this.app.use('/api/v1/profile', profile_1.default);
        // OAuth and Integrations Management (authenticated)
        this.app.use('/api/v1/oauth', oauth_1.default);
        this.app.use('/api/v1/integrations', integrations_1.default);
        // Intelligence Gateway routes (with path aliases for frontend compatibility)
        // Original paths: /api/xynergyos/v2/*
        this.app.use('/api/xynergyos/v2/slack', slack_1.default);
        this.app.use('/api/xynergyos/v2/gmail', gmail_1.default);
        this.app.use('/api/xynergyos/v2/crm', crm_1.default);
        // this.app.use('/api/xynergyos/v2/calendar', calendarRoutes); // TODO: Create calendar service
        // Path aliases for frontend: /api/v2/*
        this.app.use('/api/v2/slack', slack_1.default);
        this.app.use('/api/v2/gmail', gmail_1.default);
        this.app.use('/api/v2/email', gmail_1.default); // Frontend uses "email" instead of "gmail"
        this.app.use('/api/v2/crm', crm_1.default);
        this.app.use('/api/v2/calendar', calendar_1.default);
        // Platform service routes (v1 API)
        this.app.use('/api/v1/ai', ai_1.default);
        this.app.use('/api/v1/marketing', marketing_1.default);
        this.app.use('/api/v1/aso', aso_1.default);
        this.app.use('/api/v1/memory', memory_1.default);
        this.app.use('/api/v1/research-sessions', research_1.default);
        this.app.use('/api/v1/intelligence', intelligence_1.default);
        // Admin and Projects routes (authenticated)
        this.app.use('/api/v1/admin', admin_1.default);
        this.app.use('/api/v1/projects', projects_1.default);
        // 404 handler
        this.app.use((req, res) => {
            res.status(404).json({
                error: 'Not Found',
                message: `Route ${req.method} ${req.path} not found`,
            });
        });
    }
    initializeErrorHandling() {
        this.app.use(errorHandler_1.errorHandler);
    }
    async start() {
        try {
            // Initialize Firebase
            (0, firebase_1.initializeFirebase)();
            logger_1.logger.info('Firebase initialized');
            // Log CORS configuration
            (0, corsConfig_1.logCorsConfig)();
            // Initialize Cache Service (optional - graceful degradation if Redis unavailable)
            try {
                await (0, cacheService_1.initializeCacheService)();
                logger_1.logger.info('Cache service initialized');
            }
            catch (error) {
                logger_1.logger.warn('Cache service unavailable, continuing without caching', { error: error.message });
            }
            // Initialize WebSocket
            (0, websocket_1.initializeWebSocket)(this.httpServer);
            logger_1.logger.info('WebSocket initialized');
            // Start server
            this.httpServer.listen(config_1.appConfig.port, () => {
                logger_1.logger.info('Server started', {
                    port: config_1.appConfig.port,
                    environment: config_1.appConfig.nodeEnv,
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
        }
        catch (error) {
            logger_1.logger.error('Failed to start server', { error });
            process.exit(1);
        }
    }
    async stop() {
        return new Promise((resolve) => {
            // Clean up WebSocket connections
            const ws = (0, websocket_1.getWebSocketService)();
            ws.cleanup().then(() => {
                this.httpServer.close(() => {
                    logger_1.logger.info('Server stopped');
                    resolve();
                });
            });
        });
    }
}
exports.Server = Server;
//# sourceMappingURL=server.js.map