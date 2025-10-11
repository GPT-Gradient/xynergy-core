import { Router, Request, Response } from 'express';
import { getFirestore } from '../config/firebase';
import { logger } from '../utils/logger';
import { appConfig } from '../config/config';

const router = Router();

// Basic health check
router.get('/', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'xynergyos-intelligence-gateway',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

// Deep health check
router.get('/deep', async (req: Request, res: Response) => {
  const checks: any = {
    timestamp: new Date().toISOString(),
    service: 'xynergyos-intelligence-gateway',
    status: 'healthy',
    checks: {},
  };

  // Check Firestore
  try {
    const db = getFirestore();
    await db.collection('_health_check').doc('test').set({
      timestamp: new Date(),
    });
    checks.checks.firestore = 'healthy';
  } catch (error) {
    checks.checks.firestore = 'unhealthy';
    checks.status = 'degraded';
    logger.error('Firestore health check failed', { error });
  }

  // Check service configuration
  checks.checks.services = {
    aiRouting: appConfig.services.aiRouting ? 'configured' : 'not_configured',
    slackIntelligence: appConfig.services.slackIntelligence ? 'configured' : 'not_configured',
    gmailIntelligence: appConfig.services.gmailIntelligence ? 'configured' : 'not_configured',
    calendarIntelligence: appConfig.services.calendarIntelligence ? 'configured' : 'not_configured',
    crmEngine: appConfig.services.crmEngine ? 'configured' : 'not_configured',
  };

  const statusCode = checks.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(checks);
});

export default router;
