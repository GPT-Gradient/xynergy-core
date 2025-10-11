import { Router, Request, Response } from 'express';
import { serviceRouter } from '../services/serviceRouter';
import { getCacheService } from '../services/cacheService';
import { getCircuitBreakerRegistry } from '../utils/circuitBreaker';
import { asyncHandler } from '../middleware/errorHandler';

const router = Router();

/**
 * GET /metrics
 * Get all system metrics
 */
router.get('/', asyncHandler(async (req: Request, res: Response) => {
  const cache = getCacheService();
  const circuitBreakers = getCircuitBreakerRegistry();

  const metrics = {
    timestamp: new Date().toISOString(),
    cache: {
      connected: cache.isConnected(),
      stats: cache.getStats(),
    },
    circuitBreakers: {
      stats: circuitBreakers.getAllStats(),
      openCount: circuitBreakers.getOpenCount(),
    },
    service: {
      cacheStats: serviceRouter.getCacheStats(),
      circuitStats: serviceRouter.getCircuitStats(),
    },
  };

  res.json(metrics);
}));

/**
 * GET /metrics/cache
 * Get cache-specific metrics
 */
router.get('/cache', asyncHandler(async (req: Request, res: Response) => {
  const cache = getCacheService();

  const cacheMetrics = {
    timestamp: new Date().toISOString(),
    connected: cache.isConnected(),
    ...cache.getStats(),
  };

  res.json(cacheMetrics);
}));

/**
 * POST /metrics/cache/reset
 * Reset cache statistics
 */
router.post('/cache/reset', asyncHandler(async (req: Request, res: Response) => {
  const cache = getCacheService();
  cache.resetStats();

  res.json({
    message: 'Cache statistics reset',
    timestamp: new Date().toISOString(),
  });
}));

/**
 * DELETE /metrics/cache
 * Flush all cache entries
 */
router.delete('/cache', asyncHandler(async (req: Request, res: Response) => {
  const cache = getCacheService();
  const flushed = await cache.flushAll();

  res.json({
    message: flushed ? 'Cache flushed successfully' : 'Cache flush failed',
    success: flushed,
    timestamp: new Date().toISOString(),
  });
}));

/**
 * GET /metrics/circuit-breakers
 * Get circuit breaker statistics
 */
router.get('/circuit-breakers', asyncHandler(async (req: Request, res: Response) => {
  const registry = getCircuitBreakerRegistry();

  const circuitMetrics = {
    timestamp: new Date().toISOString(),
    openCount: registry.getOpenCount(),
    breakers: registry.getAllStats(),
  };

  res.json(circuitMetrics);
}));

/**
 * POST /metrics/circuit-breakers/reset
 * Reset all circuit breakers
 */
router.post('/circuit-breakers/reset', asyncHandler(async (req: Request, res: Response) => {
  const registry = getCircuitBreakerRegistry();
  registry.resetAll();

  res.json({
    message: 'All circuit breakers reset',
    timestamp: new Date().toISOString(),
  });
}));

/**
 * DELETE /metrics/cache/:serviceName
 * Invalidate cache for a specific service
 */
router.delete('/cache/:serviceName', asyncHandler(async (req: Request, res: Response) => {
  const { serviceName } = req.params;
  const keysDeleted = await serviceRouter.invalidateServiceCache(serviceName);

  res.json({
    message: `Cache invalidated for ${serviceName}`,
    keysDeleted,
    timestamp: new Date().toISOString(),
  });
}));

export default router;
