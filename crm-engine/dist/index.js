"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const server_1 = require("./server");
const logger_1 = require("./utils/logger");
// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    logger_1.logger.error('Uncaught exception', { error: error.message, stack: error.stack });
    process.exit(1);
});
// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    logger_1.logger.error('Unhandled rejection', { reason, promise });
    process.exit(1);
});
// Start server
const server = new server_1.Server();
server.start();
// Graceful shutdown
const gracefulShutdown = async () => {
    logger_1.logger.info('Received shutdown signal, gracefully shutting down...');
    await server.stop();
    process.exit(0);
};
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);
//# sourceMappingURL=index.js.map