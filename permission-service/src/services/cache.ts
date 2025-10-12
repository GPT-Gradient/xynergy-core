/**
 * Cache Service
 * Redis caching for permissions
 */

import { createClient, RedisClientType } from 'redis';
import { logger } from '../utils/logger';

class CacheService {
  private client: RedisClientType | null = null;
  private isConnected = false;

  async connect(): Promise<void> {
    try {
      const redisHost = process.env.REDIS_HOST || 'localhost';
      const redisPort = parseInt(process.env.REDIS_PORT || '6379', 10);

      this.client = createClient({
        socket: {
          host: redisHost,
          port: redisPort,
        },
      });

      this.client.on('error', (err) => {
        logger.error('Redis client error', { error: err });
        this.isConnected = false;
      });

      this.client.on('connect', () => {
        logger.info('Redis client connected');
        this.isConnected = true;
      });

      await this.client.connect();
    } catch (error) {
      logger.error('Failed to connect to Redis', { error });
      // Continue without cache
      this.client = null;
    }
  }

  async get(key: string): Promise<string | null> {
    if (!this.client || !this.isConnected) {
      return null;
    }

    try {
      return await this.client.get(key);
    } catch (error) {
      logger.error('Error getting from cache', { key, error });
      return null;
    }
  }

  async set(key: string, value: string, ttl?: number): Promise<void> {
    if (!this.client || !this.isConnected) {
      return;
    }

    try {
      if (ttl) {
        await this.client.setEx(key, ttl, value);
      } else {
        await this.client.set(key, value);
      }
    } catch (error) {
      logger.error('Error setting cache', { key, error });
    }
  }

  async del(key: string): Promise<void> {
    if (!this.client || !this.isConnected) {
      return;
    }

    try {
      await this.client.del(key);
    } catch (error) {
      logger.error('Error deleting from cache', { key, error });
    }
  }

  async disconnect(): Promise<void> {
    if (this.client && this.isConnected) {
      await this.client.disconnect();
      this.isConnected = false;
      logger.info('Redis client disconnected');
    }
  }
}

const cacheService = new CacheService();

// Auto-connect on module load
cacheService.connect().catch(err => {
  logger.warn('Failed to auto-connect to Redis', { error: err });
});

export function getCacheService(): CacheService {
  return cacheService;
}

export async function invalidateCache(key: string): Promise<void> {
  await cacheService.del(key);
}
