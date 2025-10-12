/**
 * Redis Client for OAuth state and token caching
 */

import Redis from 'ioredis';
import { logger } from './logger';
import { OAuthState } from '../types';

const REDIS_HOST = process.env.REDIS_HOST || '10.229.184.219';
const REDIS_PORT = parseInt(process.env.REDIS_PORT || '6379', 10);

// TTL values
const STATE_TTL = 15 * 60; // 15 minutes for OAuth state
const TOKEN_CACHE_TTL = 15 * 60; // 15 minutes for token cache

class RedisClient {
  private client: Redis;
  private isConnected = false;

  constructor() {
    this.client = new Redis({
      host: REDIS_HOST,
      port: REDIS_PORT,
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        logger.warn('Redis connection retry', { attempt: times, delay });
        return delay;
      },
      maxRetriesPerRequest: 3,
    });

    this.client.on('connect', () => {
      logger.info('Redis connected', { host: REDIS_HOST, port: REDIS_PORT });
      this.isConnected = true;
    });

    this.client.on('error', (error) => {
      logger.error('Redis error', { error });
      this.isConnected = false;
    });

    this.client.on('close', () => {
      logger.warn('Redis connection closed');
      this.isConnected = false;
    });
  }

  /**
   * Store OAuth state with TTL
   */
  async storeState(state: string, data: OAuthState): Promise<void> {
    try {
      const key = `oauth:state:${state}`;
      await this.client.setex(key, STATE_TTL, JSON.stringify(data));
      logger.debug('OAuth state stored', { state, expiresIn: STATE_TTL });
    } catch (error) {
      logger.error('Error storing OAuth state', { error, state });
      throw error;
    }
  }

  /**
   * Retrieve and delete OAuth state (one-time use)
   */
  async getState(state: string): Promise<OAuthState | null> {
    try {
      const key = `oauth:state:${state}`;
      const data = await this.client.get(key);

      if (!data) {
        logger.warn('OAuth state not found or expired', { state });
        return null;
      }

      // Delete state after retrieval (one-time use)
      await this.client.del(key);

      const stateData: OAuthState = JSON.parse(data);
      logger.debug('OAuth state retrieved and deleted', { state });
      return stateData;
    } catch (error) {
      logger.error('Error retrieving OAuth state', { error, state });
      throw error;
    }
  }

  /**
   * Cache decrypted access token
   */
  async cacheToken(connectionId: string, accessToken: string): Promise<void> {
    try {
      const key = `oauth:token:${connectionId}`;
      await this.client.setex(key, TOKEN_CACHE_TTL, accessToken);
      logger.debug('Token cached', { connectionId, ttl: TOKEN_CACHE_TTL });
    } catch (error) {
      logger.error('Error caching token', { error, connectionId });
      // Don't throw - caching is optional
    }
  }

  /**
   * Get cached token
   */
  async getCachedToken(connectionId: string): Promise<string | null> {
    try {
      const key = `oauth:token:${connectionId}`;
      const token = await this.client.get(key);

      if (token) {
        logger.debug('Token cache hit', { connectionId });
      } else {
        logger.debug('Token cache miss', { connectionId });
      }

      return token;
    } catch (error) {
      logger.error('Error getting cached token', { error, connectionId });
      return null; // Return null on error - will fetch from Firestore
    }
  }

  /**
   * Invalidate cached token
   */
  async invalidateToken(connectionId: string): Promise<void> {
    try {
      const key = `oauth:token:${connectionId}`;
      await this.client.del(key);
      logger.debug('Token cache invalidated', { connectionId });
    } catch (error) {
      logger.error('Error invalidating token cache', { error, connectionId });
      // Don't throw - cache invalidation is best-effort
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.ping();
      return true;
    } catch (error) {
      logger.error('Redis health check failed', { error });
      return false;
    }
  }

  /**
   * Get connection status
   */
  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  /**
   * Close connection
   */
  async close(): Promise<void> {
    await this.client.quit();
    logger.info('Redis connection closed');
  }
}

export const redisClient = new RedisClient();
