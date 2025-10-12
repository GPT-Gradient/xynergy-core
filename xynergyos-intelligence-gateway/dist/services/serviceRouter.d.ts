import { AxiosRequestConfig } from 'axios';
declare class ServiceRouter {
    private clients;
    private circuitBreakers;
    private cache;
    constructor();
    private initializeClients;
    callService<T = any>(serviceName: string, endpoint: string, options?: AxiosRequestConfig & {
        cache?: boolean;
        cacheTtl?: number;
    }): Promise<T>;
    /**
     * Get circuit breaker statistics for all services
     */
    getCircuitStats(): Record<string, import("../utils/circuitBreaker").CircuitBreakerStats>;
    /**
     * Get cache statistics
     */
    getCacheStats(): {
        hits: number;
        misses: number;
        hitRate: number;
    };
    /**
     * Invalidate cache for a specific service
     */
    invalidateServiceCache(serviceName: string): Promise<number>;
    callAIRouting(prompt: string, options?: any): Promise<any>;
    callSlackService(endpoint: string, options?: AxiosRequestConfig): Promise<any>;
    callGmailService(endpoint: string, options?: AxiosRequestConfig): Promise<any>;
    callCalendarService(endpoint: string, options?: AxiosRequestConfig): Promise<any>;
    callCRMService(endpoint: string, options?: AxiosRequestConfig): Promise<any>;
}
export declare const serviceRouter: ServiceRouter;
export {};
//# sourceMappingURL=serviceRouter.d.ts.map