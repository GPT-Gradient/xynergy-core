"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const dotenv_1 = __importDefault(require("dotenv"));
const server_1 = require("./server");
const logger_1 = require("./utils/logger");
// Load environment variables
dotenv_1.default.config();
// Start server
async function main() {
    try {
        logger_1.logger.info('Starting Calendar Intelligence Service...');
        const server = new server_1.Server();
        await server.start();
    }
    catch (error) {
        logger_1.logger.error('Failed to start Calendar Intelligence Service', { error: error.message, stack: error.stack });
        process.exit(1);
    }
}
main();
//# sourceMappingURL=index.js.map