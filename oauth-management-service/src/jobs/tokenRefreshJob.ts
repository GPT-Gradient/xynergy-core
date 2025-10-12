/**
 * Token Refresh Job
 * Runs every 30 minutes to refresh expiring tokens
 */

import { TokenService } from '../services/tokenService';
import { logger } from '../utils/logger';

const tokenService = new TokenService();

// Run every 30 minutes
const JOB_INTERVAL = 30 * 60 * 1000;

let jobTimer: NodeJS.Timeout | null = null;

/**
 * Execute token refresh job
 */
async function executeJob(): Promise<void> {
  try {
    logger.info('Token refresh job started');

    const results = await tokenService.refreshExpiringTokens();

    const summary = {
      total: results.length,
      successful: results.filter(r => r.success).length,
      failed: results.filter(r => !r.success).length,
    };

    logger.info('Token refresh job completed', summary);
  } catch (error) {
    logger.error('Token refresh job failed', { error });
  }
}

/**
 * Start token refresh job
 */
export function startTokenRefreshJob(): void {
  if (jobTimer) {
    logger.warn('Token refresh job already running');
    return;
  }

  logger.info('Starting token refresh job', { interval: JOB_INTERVAL });

  // Run immediately on startup
  executeJob();

  // Then run every 30 minutes
  jobTimer = setInterval(executeJob, JOB_INTERVAL);
}

/**
 * Stop token refresh job
 */
export function stopTokenRefreshJob(): void {
  if (jobTimer) {
    clearInterval(jobTimer);
    jobTimer = null;
    logger.info('Token refresh job stopped');
  }
}
