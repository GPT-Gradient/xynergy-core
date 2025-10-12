"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.serviceRouter = void 0;
const axios_1 = __importDefault(require("axios"));
const config_1 = require("../config/config");
const logger_1 = require("../utils/logger");
const errorHandler_1 = require("../middleware/errorHandler");
const circuitBreaker_1 = require("../utils/circuitBreaker");
const cacheService_1 = require("./cacheService");
class ServiceRouter {
    clients = new Map();
    circuitBreakers = (0, circuitBreaker_1.getCircuitBreakerRegistry)();
    cache = (0, cacheService_1.getCacheService)();
    constructor() {
        this.initializeClients();
    }
    initializeClients() {
        const services = config_1.appConfig.services;
        Object.entries(services).forEach(([name, url]) => {
            if (!url) {
                logger_1.logger.warn(`Service ${name} not configured`);
                return;
            }
            const client = axios_1.default.create({
                baseURL: url,
                timeout: 30000, // Default 30s timeout
                headers: {
                    'Content-Type': 'application/json',
                    'Accept-Encoding': 'gzip, deflate',
                },
                decompress: true, // Auto-decompress responses
                maxContentLength: 10 * 1024 * 1024, // 10MB max response
                maxBodyLength: 10 * 1024 * 1024, // 10MB max request
            });
            // Add request interceptor for logging and per-request timeouts
            client.interceptors.request.use((config) => {
                // AI endpoints get longer timeout (120s)
                if (config.url?.includes('/ai/') || config.url?.includes('/generate')) {
                    config.timeout = 120000;
                }
                logger_1.logger.debug(`Calling service ${name}`, {
                    url: config.url,
                    method: config.method,
                    timeout: config.timeout,
                });
                return config;
            });
            // Add response interceptor for error handling
            client.interceptors.response.use((response) => response, (error) => {
                logger_1.logger.error(`Service ${name} error`, {
                    url,
                    error: error.message,
                    status: error.response?.status,
                });
                throw error;
            });
            this.clients.set(name, client);
        });
        logger_1.logger.info('Service clients initialized', {
            services: Array.from(this.clients.keys()),
        });
    }
    async callService(serviceName, endpoint, options = {}) {
        const client = this.clients.get(serviceName);
        if (!client) {
            throw new errorHandler_1.ServiceUnavailableError(`Service ${serviceName} is not configured`);
        }
        // Generate cache key
        const cacheKey = `service:${serviceName}:${endpoint}:${JSON.stringify(options.data || {})}`;
        // Check cache if enabled
        if (options.cache && options.method === 'GET' || !options.method) {
            const cached = await this.cache.get(cacheKey);
            if (cached) {
                logger_1.logger.debug('Service response from cache', { serviceName, endpoint });
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
            // Execute with circuit breaker protection and request cancellation
            const response = await breaker.execute(async () => {
                // Add AbortController for clean cancellation
                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), options.timeout || 30000);
                try {
                    return await client.request({
                        url: endpoint,
                        ...options,
                        signal: controller.signal,
                    });
                }
                finally {
                    clearTimeout(timeout);
                }
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
        }
        catch (error) {
            logger_1.logger.error(`Failed to call ${serviceName}`, {
                endpoint,
                error: error.message,
                circuitState: breaker.getState(),
            });
            throw new errorHandler_1.ServiceUnavailableError(`Failed to communicate with ${serviceName}: ${error.message}`);
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
    async invalidateServiceCache(serviceName) {
        return await this.cache.invalidateTag(serviceName);
    }
    // Convenience methods
    async callAIRouting(prompt, options = {}) {
        return this.callService('aiRouting', '/generate', {
            method: 'POST',
            data: { prompt, ...options },
        });
    }
    async callSlackService(endpoint, options = {}) {
        return this.callService('slackIntelligence', endpoint, options);
    }
    async callGmailService(endpoint, options = {}) {
        return this.callService('gmailIntelligence', endpoint, options);
    }
    async callCalendarService(endpoint, options = {}) {
        return this.callService('calendarIntelligence', endpoint, options);
    }
    async callCRMService(endpoint, options = {}) {
        return this.callService('crmEngine', endpoint, options);
    }
}
exports.serviceRouter = new ServiceRouter();
//# sourceMappingURL=serviceRouter.js.map