"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const server_1 = require("./server");
const logger_1 = require("./utils/logger");
const server = new server_1.Server();
// Graceful shutdown
const shutdown = async (signal) => {
    logger_1.logger.info(`${signal} received, shutting down gracefully`);
    try {
        await server.stop();
        process.exit(0);
    }
    catch (error) {
        logger_1.logger.error('Error during shutdown', { error });
        process.exit(1);
    }
};
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
// Unhandled errors
process.on('unhandledRejection', (reason, promise) => {
    logger_1.logger.error('Unhandled Rejection', { reason, promise });
});
process.on('uncaughtException', (error) => {
    logger_1.logger.error('Uncaught Exception', { error });
    process.exit(1);
});
// Start server
server.start().catch((error) => {
    logger_1.logger.error('Fatal error during startup', { error });
    process.exit(1);
});
//# sourceMappingURL=index.js.map