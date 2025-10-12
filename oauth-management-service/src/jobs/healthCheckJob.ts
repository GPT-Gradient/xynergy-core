/**
 * Health Check Job
 * Runs every hour to check health of all active connections
 */

import { HealthService } from '../services/healthService';
import { logger } from '../utils/logger';

const healthService = new HealthService();

// Run every hour
const JOB_INTERVAL = 60 * 60 * 1000;

let jobTimer: NodeJS.Timeout | null = null;

/**
 * Execute health check job
 */
async function executeJob(): Promise<void> {
  try {
    logger.info('Health check job started');

    const results = await healthService.checkAllConnections();

    const summary = {
      total: results.length,
      healthy: results.filter(r => r.status === 'healthy').length,
      unhealthy: results.filter(r => r.status === 'unhealthy').length,
    };

    logger.info('Health check job completed', summary);
  } catch (error) {
    logger.error('Health check job failed', { error });
  }
}

/**
 * Start health check job
 */
export function startHealthCheckJob(): void {
  if (jobTimer) {
    logger.warn('Health check job already running');
    return;
  }

  logger.info('Starting health check job', { interval: JOB_INTERVAL });

  // Run after 5 minutes on startup (give time for service to stabilize)
  setTimeout(executeJob, 5 * 60 * 1000);

  // Then run every hour
  jobTimer = setInterval(executeJob, JOB_INTERVAL);
}

/**
 * Stop health check job
 */
export function stopHealthCheckJob(): void {
  if (jobTimer) {
    clearInterval(jobTimer);
    jobTimer = null;
    logger.info('Health check job stopped');
  }
}
