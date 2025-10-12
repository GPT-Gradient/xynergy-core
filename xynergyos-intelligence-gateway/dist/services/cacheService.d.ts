import { RedisClientType } from 'redis';
/**
 * Redis Cache Service
 * Provides caching layer for service responses and frequently accessed data
 */
export interface CacheOptions {
    ttl?: number;
    tags?: string[];
}
export declare class CacheService {
    private client;
    private connected;
    private cacheHits;
    private cacheMisses;
    connect(): Promise<void>;
    disconnect(): Promise<void>;
    /**
     * Get value from cache
     */
    get<T>(key: string): Promise<T | null>;
    /**
     * Set value in cache
     */
    set(key: string, value: any, options?: CacheOptions): Promise<boolean>;
    /**
     * Delete value from cache
     */
    delete(key: string): Promise<boolean>;
    /**
     * Invalidate all cache entries with a specific tag
     */
    invalidateTag(tag: string): Promise<number>;
    /**
     * Get cache statistics
     */
    getStats(): {
        hits: number;
        misses: number;
        hitRate: number;
    };
    /**
     * Reset cache statistics
     */
    resetStats(): void;
    /**
     * Check if cache is connected
     */
    isConnected(): boolean;
    /**
     * Get the Redis client instance (for sharing with rate limiter)
     */
    getClient(): RedisClientType | null;
    /**
     * Flush all cache entries (use with caution!)
     */
    flushAll(): Promise<boolean>;
    /**
     * Get or set pattern - fetch from cache or compute and cache
     */
    getOrSet<T>(key: string, fetcher: () => Promise<T>, options?: CacheOptions): Promise<T>;
}
export declare const getCacheService: () => CacheService;
export declare const initializeCacheService: () => Promise<CacheService>;
//# sourceMappingURL=cacheService.d.ts.map