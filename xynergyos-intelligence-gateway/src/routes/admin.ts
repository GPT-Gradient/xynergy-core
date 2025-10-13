import { Router, Response } from 'express';
import { AuthenticatedRequest, authenticateRequest } from '../middleware/auth';
import { getCacheService } from '../services/cacheService';
import { getCircuitBreakerRegistry } from '../utils/circuitBreaker';
import { asyncHandler } from '../middleware/errorHandler';
import { logger } from '../utils/logger';

const router = Router();

// Apply authentication to all admin routes
router.use(authenticateRequest);

/**
 * Admin role check middleware
 * Ensures user has admin role before accessing admin endpoints
 */
const requireAdmin = (req: AuthenticatedRequest, res: Response, next: Function) => {
  const user = req.user;

  if (!user || !user.roles || !user.roles.includes('admin')) {
    logger.warn('Admin access denied', {
      userId: user?.uid,
      roles: user?.roles,
      path: req.path,
    });

    return res.status(403).json({
      error: {
        code: 'FORBIDDEN',
        message: 'Admin access required',
        requestId: req.headers['x-request-id'] || 'unknown',
        timestamp: new Date().toISOString(),
      },
    });
  }

  next();
};

// Apply admin check to all routes
router.use(requireAdmin);

/**
 * GET /api/v1/admin/monitoring/cost
 * Get cost monitoring metrics
 */
router.get(
  '/monitoring/cost',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    logger.info('Fetching cost metrics', { userId: req.user!.uid });

    // Placeholder cost metrics
    // Future: Integrate with GCP Billing API for real cost data
    const costMetrics = {
      timestamp: new Date().toISOString(),
      period: 'current_month',
      total_cost: 2456.78,
      currency: 'USD',
      breakdown: {
        cloud_run: {
          cost: 1234.56,
          percentage: 0.502,
          services: [
            {
              name: 'xynergyos-intelligence-gateway',
              cost: 456.78,
              requests: 1250000,
              cpu_hours: 156.5,
            },
            {
              name: 'slack-intelligence-service',
              cost: 234.89,
              requests: 450000,
              cpu_hours: 89.2,
            },
            {
              name: 'gmail-intelligence-service',
              cost: 198.45,
              requests: 380000,
              cpu_hours: 76.8,
            },
            {
              name: 'crm-engine',
              cost: 344.44,
              requests: 620000,
              cpu_hours: 125.3,
            },
          ],
        },
        firestore: {
          cost: 345.67,
          percentage: 0.141,
          reads: 2500000,
          writes: 450000,
          deletes: 25000,
        },
        redis: {
          cost: 123.45,
          percentage: 0.050,
          memory_gb: 2,
          cache_hits: 8950000,
          cache_misses: 450000,
        },
        networking: {
          cost: 289.12,
          percentage: 0.118,
          egress_gb: 1250,
          ingress_gb: 980,
        },
        storage: {
          cost: 89.34,
          percentage: 0.036,
          cloud_storage_gb: 450,
        },
        other: {
          cost: 374.64,
          percentage: 0.153,
          services: ['Cloud Build', 'Artifact Registry', 'Logging', 'Monitoring'],
        },
      },
      comparison: {
        previous_month: 2234.12,
        change_percent: 9.96,
        trend: 'increasing',
      },
      projections: {
        end_of_month: 2890.45,
        confidence: 0.85,
      },
      optimization_opportunities: [
        {
          service: 'xynergyos-intelligence-gateway',
          recommendation: 'Reduce memory allocation from 512Mi to 384Mi',
          potential_savings: 45.67,
          savings_percent: 10,
        },
        {
          service: 'redis',
          recommendation: 'Increase cache TTL to reduce Firestore reads',
          potential_savings: 67.89,
          savings_percent: 19.6,
        },
      ],
    };

    res.json({
      success: true,
      data: costMetrics,
    });
  })
);

/**
 * GET /api/v1/admin/monitoring/circuit-breakers
 * Get circuit breaker status and metrics
 */
router.get(
  '/monitoring/circuit-breakers',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    logger.info('Fetching circuit breaker metrics', { userId: req.user!.uid });

    const registry = getCircuitBreakerRegistry();
    const circuitBreakers = registry.getAllStats();

    const metrics = {
      timestamp: new Date().toISOString(),
      summary: {
        total: Object.keys(circuitBreakers).length,
        open: registry.getOpenCount(),
        half_open: Object.values(circuitBreakers).filter((cb: any) => cb.state === 'half-open').length,
        closed: Object.values(circuitBreakers).filter((cb: any) => cb.state === 'closed').length,
      },
      breakers: Object.entries(circuitBreakers).map(([name, stats]: [string, any]) => ({
        name,
        state: stats.state,
        failure_count: stats.failures,
        success_count: stats.successes,
        last_failure_time: stats.lastFailureTime,
        next_attempt_time: stats.nextAttempt,
        total_requests: stats.failures + stats.successes,
        failure_rate: stats.failures + stats.successes > 0
          ? (stats.failures / (stats.failures + stats.successes) * 100).toFixed(2)
          : '0.00',
      })),
      alerts: Object.entries(circuitBreakers)
        .filter(([_, stats]: [string, any]) => stats.state === 'open')
        .map(([name, stats]: [string, any]) => ({
          service: name,
          message: `Circuit breaker open - service unavailable`,
          severity: 'critical',
          since: stats.lastFailureTime,
        })),
    };

    res.json({
      success: true,
      data: metrics,
    });
  })
);

/**
 * GET /api/v1/admin/monitoring/resources
 * Get resource utilization metrics
 */
router.get(
  '/monitoring/resources',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    logger.info('Fetching resource metrics', { userId: req.user!.uid });

    const cache = getCacheService();
    const cacheStats = cache.getStats();

    // Placeholder resource metrics
    // Future: Integrate with GCP Monitoring API for real resource data
    const resourceMetrics = {
      timestamp: new Date().toISOString(),
      services: [
        {
          name: 'xynergyos-intelligence-gateway',
          status: 'healthy',
          instances: 3,
          cpu: {
            usage_percent: 45.2,
            limit_millicores: 1000,
            actual_millicores: 452,
          },
          memory: {
            usage_percent: 62.8,
            limit_mb: 512,
            actual_mb: 321,
          },
          requests: {
            current_rps: 125.5,
            avg_latency_ms: 89,
            p95_latency_ms: 245,
            p99_latency_ms: 467,
          },
        },
        {
          name: 'slack-intelligence-service',
          status: 'healthy',
          instances: 2,
          cpu: {
            usage_percent: 32.1,
            limit_millicores: 1000,
            actual_millicores: 321,
          },
          memory: {
            usage_percent: 48.5,
            limit_mb: 256,
            actual_mb: 124,
          },
          requests: {
            current_rps: 45.2,
            avg_latency_ms: 156,
            p95_latency_ms: 312,
            p99_latency_ms: 589,
          },
        },
        {
          name: 'gmail-intelligence-service',
          status: 'healthy',
          instances: 2,
          cpu: {
            usage_percent: 28.7,
            limit_millicores: 1000,
            actual_millicores: 287,
          },
          memory: {
            usage_percent: 41.3,
            limit_mb: 256,
            actual_mb: 106,
          },
          requests: {
            current_rps: 38.6,
            avg_latency_ms: 178,
            p95_latency_ms: 356,
            p99_latency_ms: 623,
          },
        },
        {
          name: 'crm-engine',
          status: 'healthy',
          instances: 2,
          cpu: {
            usage_percent: 35.8,
            limit_millicores: 1000,
            actual_millicores: 358,
          },
          memory: {
            usage_percent: 52.1,
            limit_mb: 256,
            actual_mb: 133,
          },
          requests: {
            current_rps: 67.3,
            avg_latency_ms: 134,
            p95_latency_ms: 289,
            p99_latency_ms: 512,
          },
        },
      ],
      cache: {
        status: cache.isConnected() ? 'healthy' : 'disconnected',
        ...cacheStats,
        hit_rate: cacheStats.hits + cacheStats.misses > 0
          ? ((cacheStats.hits / (cacheStats.hits + cacheStats.misses)) * 100).toFixed(2)
          : '0.00',
      },
      database: {
        name: 'Firestore',
        status: 'healthy',
        connections: 15,
        avg_query_time_ms: 23,
        slow_queries: 3,
      },
    };

    res.json({
      success: true,
      data: resourceMetrics,
    });
  })
);

/**
 * GET /api/v1/admin/monitoring/health
 * Get overall system health status
 */
router.get(
  '/monitoring/health',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    logger.info('Fetching system health', { userId: req.user!.uid });

    const cache = getCacheService();
    const registry = getCircuitBreakerRegistry();

    const healthStatus = {
      timestamp: new Date().toISOString(),
      overall_status: 'healthy',
      components: {
        gateway: {
          status: 'healthy',
          uptime_seconds: process.uptime(),
          version: '1.0.0',
        },
        cache: {
          status: cache.isConnected() ? 'healthy' : 'degraded',
          connected: cache.isConnected(),
          message: cache.isConnected() ? 'Redis operational' : 'Redis disconnected, using in-memory fallback',
        },
        circuit_breakers: {
          status: registry.getOpenCount() === 0 ? 'healthy' : 'degraded',
          open_count: registry.getOpenCount(),
          message: registry.getOpenCount() === 0
            ? 'All circuit breakers closed'
            : `${registry.getOpenCount()} circuit breaker(s) open`,
        },
        services: [
          {
            name: 'slack-intelligence-service',
            status: 'healthy',
            url: 'https://slack-intelligence-service-835612502919.us-central1.run.app',
          },
          {
            name: 'gmail-intelligence-service',
            status: 'healthy',
            url: 'https://gmail-intelligence-service-835612502919.us-central1.run.app',
          },
          {
            name: 'crm-engine',
            status: 'healthy',
            url: 'https://crm-engine-vgjxy554mq-uc.a.run.app',
          },
        ],
      },
      recent_incidents: [],
      maintenance_windows: [],
    };

    // Determine overall status based on components
    const hasOpenCircuitBreakers = registry.getOpenCount() > 0;
    const cacheDisconnected = !cache.isConnected();

    if (hasOpenCircuitBreakers) {
      healthStatus.overall_status = 'degraded';
    }

    res.json({
      success: true,
      data: healthStatus,
    });
  })
);

/**
 * GET /api/v1/admin/users
 * List all users (admin only)
 */
router.get(
  '/users',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const { limit = '50', offset = '0', role, search } = req.query;

    logger.info('Fetching users list', {
      userId: req.user!.uid,
      limit,
      offset,
      role,
      search,
    });

    // Placeholder user list
    // Future: Query Firestore users collection with filters
    const users = [
      {
        userId: 'a8d72329-0c36-4d79-a27a-6b8bf5e690ab',
        email: 'p5test@xynergy.com',
        username: 'p5test',
        fullName: 'Phase 5 Test',
        roles: ['user'],
        isActive: true,
        createdAt: '2025-10-13T19:50:04.000Z',
        lastLogin: '2025-10-13T19:50:04.000Z',
      },
      {
        userId: 'b1259bc4-06fa-43be-90da-1844f587cf23',
        email: 'phase4test@xynergy.com',
        username: 'phase4test',
        fullName: 'Phase 4 Test',
        roles: ['user'],
        isActive: true,
        createdAt: '2025-10-13T18:42:54.000Z',
        lastLogin: '2025-10-13T18:42:54.000Z',
      },
    ];

    res.json({
      success: true,
      data: users,
      meta: {
        total: users.length,
        limit: parseInt(limit as string),
        offset: parseInt(offset as string),
      },
    });
  })
);

/**
 * PATCH /api/v1/admin/users/:userId
 * Update user (admin only)
 */
router.patch(
  '/users/:userId',
  asyncHandler(async (req: AuthenticatedRequest, res: Response) => {
    const { userId } = req.params;
    const updates = req.body;

    logger.info('Updating user', {
      adminId: req.user!.uid,
      targetUserId: userId,
      updates,
    });

    // Placeholder user update
    // Future: Update Firestore users collection
    res.json({
      success: true,
      message: `User ${userId} updated successfully`,
      data: {
        userId,
        ...updates,
        updatedAt: new Date().toISOString(),
      },
    });
  })
);

export default router;
