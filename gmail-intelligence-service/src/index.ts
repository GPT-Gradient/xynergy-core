import dotenv from 'dotenv';
import { Server } from './server';
import { logger } from './utils/logger';

// Load environment variables
dotenv.config();

// Start server
async function main(): Promise<void> {
  try {
    logger.info('Starting Gmail Intelligence Service...');
    const server = new Server();
    await server.start();
  } catch (error: any) {
    logger.error('Failed to start Gmail Intelligence Service', { error: error.message, stack: error.stack });
    process.exit(1);
  }
}

main();
