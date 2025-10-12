"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const serviceRouter_1 = require("../services/serviceRouter");
const cacheService_1 = require("../services/cacheService");
const circuitBreaker_1 = require("../utils/circuitBreaker");
const errorHandler_1 = require("../middleware/errorHandler");
const router = (0, express_1.Router)();
/**
 * GET /metrics
 * Get all system metrics
 */
router.get('/', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const cache = (0, cacheService_1.getCacheService)();
    const circuitBreakers = (0, circuitBreaker_1.getCircuitBreakerRegistry)();
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
            cacheStats: serviceRouter_1.serviceRouter.getCacheStats(),
            circuitStats: serviceRouter_1.serviceRouter.getCircuitStats(),
        },
    };
    res.json(metrics);
}));
/**
 * GET /metrics/cache
 * Get cache-specific metrics
 */
router.get('/cache', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const cache = (0, cacheService_1.getCacheService)();
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
router.post('/cache/reset', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const cache = (0, cacheService_1.getCacheService)();
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
router.delete('/cache', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const cache = (0, cacheService_1.getCacheService)();
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
router.get('/circuit-breakers', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const registry = (0, circuitBreaker_1.getCircuitBreakerRegistry)();
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
router.post('/circuit-breakers/reset', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const registry = (0, circuitBreaker_1.getCircuitBreakerRegistry)();
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
router.delete('/cache/:serviceName', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const { serviceName } = req.params;
    const keysDeleted = await serviceRouter_1.serviceRouter.invalidateServiceCache(serviceName);
    res.json({
        message: `Cache invalidated for ${serviceName}`,
        keysDeleted,
        timestamp: new Date().toISOString(),
    });
}));
exports.default = router;
//# sourceMappingURL=metrics.js.map