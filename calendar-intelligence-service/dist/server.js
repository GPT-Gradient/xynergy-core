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
const firebase_1 = require("./config/firebase");
const errorHandler_1 = require("./middleware/errorHandler");
const logger_1 = require("./utils/logger");
const crypto_1 = require("crypto");
const health_1 = __importDefault(require("./routes/health"));
const calendar_1 = __importDefault(require("./routes/calendar"));
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
        this.app.use((req, res, next) => {
            const requestId = req.headers['x-request-id'] || (0, crypto_1.randomUUID)();
            req.requestId = requestId;
            res.setHeader('X-Request-ID', requestId);
            next();
        });
        this.app.use((0, helmet_1.default)());
        this.app.use((0, cors_1.default)({ origin: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'], credentials: true }));
        this.app.use((0, compression_1.default)());
        this.app.use(express_1.default.json({ limit: '10mb' }));
        this.app.use((req, res, next) => {
            const startTime = Date.now();
            res.on('finish', () => {
                logger_1.logger.info('Request completed', {
                    requestId: req.requestId,
                    method: req.method,
                    path: req.path,
                    statusCode: res.statusCode,
                    duration: `${Date.now() - startTime}ms`,
                });
            });
            next();
        });
    }
    initializeRoutes() {
        this.app.use('/health', health_1.default);
        this.app.use('/api/v1/health', health_1.default);
        this.app.use('/api/v1/calendar', calendar_1.default);
        this.app.get('/', (req, res) => {
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
        this.app.use((req, res) => {
            res.status(404).json({ error: 'Not Found', message: `Route ${req.method} ${req.path} not found` });
        });
    }
    initializeErrorHandling() {
        this.app.use(errorHandler_1.errorHandler);
    }
    async start() {
        try {
            (0, firebase_1.initializeFirebase)();
            logger_1.logger.info('Firebase initialized');
            this.httpServer.listen(parseInt(process.env.PORT || '8080'), () => {
                logger_1.logger.info('Server started', { port: process.env.PORT || 8080, service: 'calendar-intelligence-service' });
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