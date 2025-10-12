"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.initializeCacheService = exports.getCacheService = exports.CacheService = void 0;
const redis_1 = require("redis");
const config_1 = require("../config/config");
const logger_1 = require("../utils/logger");
class CacheService {
    client = null;
    connected = false;
    cacheHits = 0;
    cacheMisses = 0;
    async connect() {
        if (this.connected) {
            return;
        }
        try {
            this.client = (0, redis_1.createClient)({
                url: `redis://${config_1.appConfig.redis.host}:${config_1.appConfig.redis.port}`,
                password: config_1.appConfig.redis.password,
                socket: {
                    connectTimeout: 5000,
                    reconnectStrategy: false, // Don't reconnect on failure
                },
            });
            this.client.on('error', (error) => {
                // Silently log errors during initial connection attempts
                logger_1.logger.debug('Redis cache client error (degraded mode active)', { error: error.message });
            });
            this.client.on('connect', () => {
                logger_1.logger.info('Redis cache client connected');
            });
            await this.client.connect();
            this.connected = true;
            logger_1.logger.info('Redis cache service initialized', {
                host: config_1.appConfig.redis.host,
                port: config_1.appConfig.redis.port,
            });
        }
        catch (error) {
            logger_1.logger.warn('Redis unavailable, running in degraded mode (no caching)', {
                error: error.message,
                host: config_1.appConfig.redis.host
            });
            this.connected = false;
            // Clean up the client to prevent error spam
            if (this.client) {
                try {
                    await this.client.disconnect();
                }
                catch (e) {
                    // Ignore disconnect errors
                }
                this.client = null;
            }
        }
    }
    async disconnect() {
        if (this.client && this.connected) {
            await this.client.quit();
            this.connected = false;
            logger_1.logger.info('Redis cache client disconnected');
        }
    }
    /**
     * Get value from cache
     */
    async get(key) {
        if (!this.connected || !this.client) {
            logger_1.logger.warn('Cache not connected, returning null');
            return null;
        }
        try {
            const value = await this.client.get(key);
            if (value) {
                this.cacheHits++;
                logger_1.logger.debug('Cache hit', { key, hits: this.cacheHits });
                return JSON.parse(value);
            }
            else {
                this.cacheMisses++;
                logger_1.logger.debug('Cache miss', { key, misses: this.cacheMisses });
                return null;
            }
        }
        catch (error) {
            logger_1.logger.error('Cache get error', { key, error });
            return null;
        }
    }
    /**
     * Set value in cache
     */
    async set(key, value, options = {}) {
        if (!this.connected || !this.client) {
            logger_1.logger.warn('Cache not connected, skipping set');
            return false;
        }
        try {
            const ttl = options.ttl || 300; // Default 5 minutes
            const serialized = JSON.stringify(value);
            await this.client.setEx(key, ttl, serialized);
            // Store tags for invalidation
            if (options.tags && options.tags.length > 0) {
                for (const tag of options.tags) {
                    await this.client.sAdd(`tag:${tag}`, key);
                    await this.client.expire(`tag:${tag}`, ttl);
                }
            }
            logger_1.logger.debug('Cache set', { key, ttl, tags: options.tags });
            return true;
        }
        catch (error) {
            logger_1.logger.error('Cache set error', { key, error });
            return false;
        }
    }
    /**
     * Delete value from cache
     */
    async delete(key) {
        if (!this.connected || !this.client) {
            return false;
        }
        try {
            await this.client.del(key);
            logger_1.logger.debug('Cache delete', { key });
            return true;
        }
        catch (error) {
            logger_1.logger.error('Cache delete error', { key, error });
            return false;
        }
    }
    /**
     * Invalidate all cache entries with a specific tag
     */
    async invalidateTag(tag) {
        if (!this.connected || !this.client) {
            return 0;
        }
        try {
            const keys = await this.client.sMembers(`tag:${tag}`);
            if (keys.length > 0) {
                await this.client.del(keys);
                await this.client.del(`tag:${tag}`);
                logger_1.logger.info('Cache tag invalidated', { tag, keysDeleted: keys.length });
                return keys.length;
            }
            return 0;
        }
        catch (error) {
            logger_1.logger.error('Cache tag invalidation error', { tag, error });
            return 0;
        }
    }
    /**
     * Get cache statistics
     */
    getStats() {
        const total = this.cacheHits + this.cacheMisses;
        const hitRate = total > 0 ? (this.cacheHits / total) * 100 : 0;
        return {
            hits: this.cacheHits,
            misses: this.cacheMisses,
            hitRate: Math.round(hitRate * 100) / 100,
        };
    }
    /**
     * Reset cache statistics
     */
    resetStats() {
        this.cacheHits = 0;
        this.cacheMisses = 0;
        logger_1.logger.info('Cache statistics reset');
    }
    /**
     * Check if cache is connected
     */
    isConnected() {
        return this.connected;
    }
    /**
     * Get the Redis client instance (for sharing with rate limiter)
     */
    getClient() {
        if (!this.connected || !this.client) {
            throw new Error('Redis client not connected');
        }
        return this.client;
    }
    /**
     * Flush all cache entries (use with caution!)
     */
    async flushAll() {
        if (!this.connected || !this.client) {
            return false;
        }
        try {
            await this.client.flushDb();
            logger_1.logger.warn('Cache flushed - all entries deleted');
            return true;
        }
        catch (error) {
            logger_1.logger.error('Cache flush error', { error });
            return false;
        }
    }
    /**
     * Get or set pattern - fetch from cache or compute and cache
     */
    async getOrSet(key, fetcher, options = {}) {
        // Try to get from cache
        const cached = await this.get(key);
        if (cached !== null) {
            return cached;
        }
        // Cache miss - fetch data
        const data = await fetcher();
        // Cache the result
        await this.set(key, data, options);
        return data;
    }
}
exports.CacheService = CacheService;
// Singleton instance
let cacheService;
const getCacheService = () => {
    if (!cacheService) {
        cacheService = new CacheService();
    }
    return cacheService;
};
exports.getCacheService = getCacheService;
const initializeCacheService = async () => {
    const cache = (0, exports.getCacheService)();
    await cache.connect();
    return cache;
};
exports.initializeCacheService = initializeCacheService;
//# sourceMappingURL=cacheService.js.map