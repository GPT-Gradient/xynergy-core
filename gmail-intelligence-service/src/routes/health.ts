import { Router, Request, Response } from 'express';
import { asyncHandler } from '../middleware/errorHandler';
import { getFirestore } from '../config/firebase';
import { gmailService } from '../services/gmailService';
import { logger } from '../utils/logger';

const router = Router();

router.get('/', asyncHandler(async (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'gmail-intelligence-service',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    mode: gmailService.isInMockMode() ? 'mock' : 'production',
  });
}));

router.get('/deep', asyncHandler(async (req: Request, res: Response) => {
  const checks: any = {
    service: { status: 'healthy', name: 'gmail-intelligence-service' },
  };

  try {
    const firestore = getFirestore();
    await firestore.collection('_health_check').doc('test').get();
    checks.firebase = { status: 'healthy', firestoreConnected: true };
  } catch (error: any) {
    checks.firebase = { status: 'degraded', firestoreConnected: false };
  }

  // Check Gmail API configuration (not per-user since health check is public)
  checks.gmail = {
    status: gmailService.isInMockMode() ? 'degraded' : 'healthy',
    configured: !gmailService.isInMockMode(),
    mockMode: gmailService.isInMockMode(),
    note: 'Health check does not test per-user OAuth tokens',
  };

  const allHealthy = Object.values(checks).every((check: any) => check.status === 'healthy');

  res.json({
    status: allHealthy ? 'healthy' : 'degraded',
    service: 'gmail-intelligence-service',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    checks,
  });
}));

export default router;
