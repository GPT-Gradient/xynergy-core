import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { appConfig } from '../config/config';
import { logger } from '../utils/logger';
import { ServiceUnavailableError } from '../middleware/errorHandler';
import { getCircuitBreakerRegistry } from '../utils/circuitBreaker';
import { getCacheService } from './cacheService';

class ServiceRouter {
  private clients: Map<string, AxiosInstance> = new Map();
  private circuitBreakers = getCircuitBreakerRegistry();
  private cache = getCacheService();

  constructor() {
    this.initializeClients();
  }

  private initializeClients(): void {
    const services = appConfig.services;

    Object.entries(services).forEach(([name, url]) => {
      if (!url) {
        logger.warn(`Service ${name} not configured`);
        return;
      }

      const client = axios.create({
        baseURL: url,
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      // Add request interceptor for logging
      client.interceptors.request.use((config) => {
        logger.debug(`Calling service ${name}`, {
          url: config.url,
          method: config.method,
        });
        return config;
      });

      // Add response interceptor for error handling
      client.interceptors.response.use(
        (response) => response,
        (error) => {
          logger.error(`Service ${name} error`, {
            url,
            error: error.message,
            status: error.response?.status,
          });
          throw error;
        }
      );

      this.clients.set(name, client);
    });

    logger.info('Service clients initialized', {
      services: Array.from(this.clients.keys()),
    });
  }

  async callService<T = any>(
    serviceName: string,
    endpoint: string,
    options: AxiosRequestConfig & { cache?: boolean; cacheTtl?: number } = {}
  ): Promise<T> {
    const client = this.clients.get(serviceName);

    if (!client) {
      throw new ServiceUnavailableError(
        `Service ${serviceName} is not configured`
      );
    }

    // Generate cache key
    const cacheKey = `service:${serviceName}:${endpoint}:${JSON.stringify(options.data || {})}`;

    // Check cache if enabled
    if (options.cache && options.method === 'GET' || !options.method) {
      const cached = await this.cache.get<T>(cacheKey);
      if (cached) {
        logger.debug('Service response from cache', { serviceName, endpoint });
        return cached;
      }
    }

    // Get circuit breaker for this service
    const breaker = this.circuitBreakers.getBreaker(serviceName, {
      failureThreshold: 5,
      successThreshold: 2,
      timeout: 60000,
      monitoringPeriod: 60000,
    });

    try {
      // Execute with circuit breaker protection
      const response = await breaker.execute(async () => {
        return await client.request({
          url: endpoint,
          ...options,
        });
      });

      const data = response.data;

      // Cache successful GET requests
      if (options.cache && (options.method === 'GET' || !options.method)) {
        await this.cache.set(cacheKey, data, {
          ttl: options.cacheTtl || 300,
          tags: [serviceName],
        });
      }

      return data;
    } catch (error: any) {
      logger.error(`Failed to call ${serviceName}`, {
        endpoint,
        error: error.message,
        circuitState: breaker.getState(),
      });
      throw new ServiceUnavailableError(
        `Failed to communicate with ${serviceName}: ${error.message}`
      );
    }
  }

  /**
   * Get circuit breaker statistics for all services
   */
  getCircuitStats() {
    return this.circuitBreakers.getAllStats();
  }

  /**
   * Get cache statistics
   */
  getCacheStats() {
    return this.cache.getStats();
  }

  /**
   * Invalidate cache for a specific service
   */
  async invalidateServiceCache(serviceName: string): Promise<number> {
    return await this.cache.invalidateTag(serviceName);
  }

  // Convenience methods
  async callAIRouting(prompt: string, options: any = {}): Promise<any> {
    return this.callService('aiRouting', '/generate', {
      method: 'POST',
      data: { prompt, ...options },
    });
  }

  async callSlackService(endpoint: string, options: AxiosRequestConfig = {}): Promise<any> {
    return this.callService('slackIntelligence', endpoint, options);
  }

  async callGmailService(endpoint: string, options: AxiosRequestConfig = {}): Promise<any> {
    return this.callService('gmailIntelligence', endpoint, options);
  }

  async callCalendarService(endpoint: string, options: AxiosRequestConfig = {}): Promise<any> {
    return this.callService('calendarIntelligence', endpoint, options);
  }

  async callCRMService(endpoint: string, options: AxiosRequestConfig = {}): Promise<any> {
    return this.callService('crmEngine', endpoint, options);
  }
}

export const serviceRouter = new ServiceRouter();
