import { createClient, RedisClientType } from 'redis';
import { appConfig } from '../config/config';
import { logger } from '../utils/logger';

/**
 * Redis Cache Service
 * Provides caching layer for service responses and frequently accessed data
 */

export interface CacheOptions {
  ttl?: number; // Time to live in seconds (default: 300)
  tags?: string[]; // Cache tags for bulk invalidation
}

export class CacheService {
  private client: RedisClientType | null = null;
  private connected: boolean = false;
  private cacheHits: number = 0;
  private cacheMisses: number = 0;

  async connect(): Promise<void> {
    if (this.connected) {
      return;
    }

    try {
      this.client = createClient({
        url: `redis://${appConfig.redis.host}:${appConfig.redis.port}`,
        password: appConfig.redis.password,
        socket: {
          connectTimeout: 5000,
          reconnectStrategy: false, // Don't reconnect on failure
        },
      });

      this.client.on('error', (error) => {
        // Silently log errors during initial connection attempts
        logger.debug('Redis cache client error (degraded mode active)', { error: error.message });
      });

      this.client.on('connect', () => {
        logger.info('Redis cache client connected');
      });

      await this.client.connect();
      this.connected = true;

      logger.info('Redis cache service initialized', {
        host: appConfig.redis.host,
        port: appConfig.redis.port,
      });
    } catch (error: any) {
      logger.warn('Redis unavailable, running in degraded mode (no caching)', {
        error: error.message,
        host: appConfig.redis.host
      });
      this.connected = false;
      // Clean up the client to prevent error spam
      if (this.client) {
        try {
          await this.client.disconnect();
        } catch (e) {
          // Ignore disconnect errors
        }
        this.client = null;
      }
    }
  }

  async disconnect(): Promise<void> {
    if (this.client && this.connected) {
      await this.client.quit();
      this.connected = false;
      logger.info('Redis cache client disconnected');
    }
  }

  /**
   * Get value from cache
   */
  async get<T>(key: string): Promise<T | null> {
    if (!this.connected || !this.client) {
      logger.warn('Cache not connected, returning null');
      return null;
    }

    try {
      const value = await this.client.get(key);

      if (value) {
        this.cacheHits++;
        logger.debug('Cache hit', { key, hits: this.cacheHits });
        return JSON.parse(value) as T;
      } else {
        this.cacheMisses++;
        logger.debug('Cache miss', { key, misses: this.cacheMisses });
        return null;
      }
    } catch (error) {
      logger.error('Cache get error', { key, error });
      return null;
    }
  }

  /**
   * Set value in cache
   */
  async set(key: string, value: any, options: CacheOptions = {}): Promise<boolean> {
    if (!this.connected || !this.client) {
      logger.warn('Cache not connected, skipping set');
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

      logger.debug('Cache set', { key, ttl, tags: options.tags });
      return true;
    } catch (error) {
      logger.error('Cache set error', { key, error });
      return false;
    }
  }

  /**
   * Delete value from cache
   */
  async delete(key: string): Promise<boolean> {
    if (!this.connected || !this.client) {
      return false;
    }

    try {
      await this.client.del(key);
      logger.debug('Cache delete', { key });
      return true;
    } catch (error) {
      logger.error('Cache delete error', { key, error });
      return false;
    }
  }

  /**
   * Invalidate all cache entries with a specific tag
   */
  async invalidateTag(tag: string): Promise<number> {
    if (!this.connected || !this.client) {
      return 0;
    }

    try {
      const keys = await this.client.sMembers(`tag:${tag}`);

      if (keys.length > 0) {
        await this.client.del(keys);
        await this.client.del(`tag:${tag}`);
        logger.info('Cache tag invalidated', { tag, keysDeleted: keys.length });
        return keys.length;
      }

      return 0;
    } catch (error) {
      logger.error('Cache tag invalidation error', { tag, error });
      return 0;
    }
  }

  /**
   * Get cache statistics
   */
  getStats(): { hits: number; misses: number; hitRate: number } {
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
  resetStats(): void {
    this.cacheHits = 0;
    this.cacheMisses = 0;
    logger.info('Cache statistics reset');
  }

  /**
   * Check if cache is connected
   */
  isConnected(): boolean {
    return this.connected;
  }

  /**
   * Flush all cache entries (use with caution!)
   */
  async flushAll(): Promise<boolean> {
    if (!this.connected || !this.client) {
      return false;
    }

    try {
      await this.client.flushDb();
      logger.warn('Cache flushed - all entries deleted');
      return true;
    } catch (error) {
      logger.error('Cache flush error', { error });
      return false;
    }
  }

  /**
   * Get or set pattern - fetch from cache or compute and cache
   */
  async getOrSet<T>(
    key: string,
    fetcher: () => Promise<T>,
    options: CacheOptions = {}
  ): Promise<T> {
    // Try to get from cache
    const cached = await this.get<T>(key);
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

// Singleton instance
let cacheService: CacheService;

export const getCacheService = (): CacheService => {
  if (!cacheService) {
    cacheService = new CacheService();
  }
  return cacheService;
};

export const initializeCacheService = async (): Promise<CacheService> => {
  const cache = getCacheService();
  await cache.connect();
  return cache;
};
