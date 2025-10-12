"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Server = void 0;
const express_1 = __importDefault(require("express"));
const helmet_1 = __importDefault(require("helmet"));
const cors_1 = __importDefault(require("cors"));
const compression_1 = __importDefault(require("compression"));
const http_1 = require("http");
const config_1 = require("./config/config");
const firebase_1 = require("./config/firebase");
const errorHandler_1 = require("./middleware/errorHandler");
const logger_1 = require("./utils/logger");
const crypto_1 = require("crypto");
// Import routes
const health_1 = __importDefault(require("./routes/health"));
const crm_1 = __importDefault(require("./routes/crm"));
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
        // Request ID middleware (must be first)
        this.app.use((req, res, next) => {
            const requestId = req.headers['x-request-id'] || (0, crypto_1.randomUUID)();
            req.requestId = requestId;
            res.setHeader('X-Request-ID', requestId);
            next();
        });
        // Security headers
        this.app.use((0, helmet_1.default)());
        // CORS
        this.app.use((0, cors_1.default)({
            origin: config_1.appConfig.cors.origins,
            credentials: true,
            methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
            allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-ID'],
        }));
        // Compression
        this.app.use((0, compression_1.default)());
        // Body parsing
        this.app.use(express_1.default.json({ limit: '10mb' }));
        this.app.use(express_1.default.urlencoded({ extended: true, limit: '10mb' }));
        // Request logging
        this.app.use((req, res, next) => {
            const startTime = Date.now();
            logger_1.logger.info('Incoming request', {
                requestId: req.requestId,
                method: req.method,
                path: req.path,
                ip: req.ip,
            });
            res.on('finish', () => {
                const duration = Date.now() - startTime;
                logger_1.logger.info('Request completed', {
                    requestId: req.requestId,
                    statusCode: res.statusCode,
                    duration: `${duration}ms`,
                });
            });
            next();
        });
    }
    initializeRoutes() {
        // Health checks
        this.app.use('/health', health_1.default);
        this.app.use('/api/v1/health', health_1.default);
        // CRM routes
        this.app.use('/api/v1/crm', crm_1.default);
        // Root endpoint
        this.app.get('/', (req, res) => {
            res.json({
                service: config_1.appConfig.serviceName,
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
        this.app.use((req, res) => {
            res.status(404).json({
                error: 'Not Found',
                message: `Route ${req.method} ${req.path} not found`,
                requestId: req.requestId,
                timestamp: new Date().toISOString(),
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
            // Start server
            this.httpServer.listen(config_1.appConfig.port, () => {
                logger_1.logger.info('Server started', {
                    port: config_1.appConfig.port,
                    environment: config_1.appConfig.nodeEnv,
                    service: config_1.appConfig.serviceName,
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
        }
        catch (error) {
            logger_1.logger.error('Failed to start server', { error });
            process.exit(1);
        }
    }
    async stop() {
        return new Promise((resolve) => {
            this.httpServer.close(() => {
                logger_1.logger.info('Server stopped');
                resolve();
            });
        });
    }
}
exports.Server = Server;
//# sourceMappingURL=server.js.map