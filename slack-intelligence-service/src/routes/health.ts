import { Router, Request, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { appConfig } from '../config/config';
import { getFirestore } from '../config/firebase';
import { slackService } from '../services/slackService';
import { logger } from '../utils/logger';

const router = Router();

/**
 * GET /health
 * Basic health check
 */
router.get('/', asyncHandler(async (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: appConfig.serviceName,
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    mode: slackService.isInMockMode() ? 'mock' : 'production',
  });
}));

/**
 * GET /health/deep
 * Deep health check with dependency validation
 */
router.get('/deep', asyncHandler(async (req: Request, res: Response) => {
  const checks: any = {
    service: {
      status: 'healthy',
      name: appConfig.serviceName,
    },
  };

  // Check Firebase/Firestore
  try {
    const firestore = getFirestore();
    const testDoc = await firestore.collection('_health_check').doc('test').get();
    checks.firebase = {
      status: 'healthy',
      firestoreConnected: true,
    };
  } catch (error: any) {
    logger.warn('Firestore health check failed', { error: error.message });
    checks.firebase = {
      status: 'degraded',
      firestoreConnected: false,
      error: error.message,
    };
  }

  // Check Slack API configuration (not per-user since health check is public)
  checks.slack = {
    status: slackService.isInMockMode() ? 'degraded' : 'healthy',
    configured: !slackService.isInMockMode(),
    mockMode: slackService.isInMockMode(),
    note: 'Health check does not test per-user OAuth tokens',
  };

  // Determine overall status
  const allHealthy = Object.values(checks).every(
    (check: any) => check.status === 'healthy'
  );

  res.json({
    status: allHealthy ? 'healthy' : 'degraded',
    service: appConfig.serviceName,
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    checks,
  });
}));

export default router;
