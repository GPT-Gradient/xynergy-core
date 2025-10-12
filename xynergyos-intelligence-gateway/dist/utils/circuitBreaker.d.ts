/**
 * Circuit Breaker Pattern Implementation
 * Prevents cascading failures by stopping requests to failing services
 */
export declare enum CircuitState {
    CLOSED = "CLOSED",// Normal operation
    OPEN = "OPEN",// Failing, reject requests
    HALF_OPEN = "HALF_OPEN"
}
export interface CircuitBreakerOptions {
    failureThreshold: number;
    successThreshold: number;
    timeout: number;
    monitoringPeriod: number;
}
export interface CircuitBreakerStats {
    state: CircuitState;
    failures: number;
    successes: number;
    totalRequests: number;
    lastFailureTime: number | null;
    nextAttemptTime: number | null;
}
export declare class CircuitBreaker {
    private name;
    private options;
    private state;
    private failures;
    private successes;
    private totalRequests;
    private lastFailureTime;
    private nextAttemptTime;
    private failureTimestamps;
    constructor(name: string, options?: CircuitBreakerOptions);
    /**
     * Execute a function with circuit breaker protection
     */
    execute<T>(fn: () => Promise<T>): Promise<T>;
    /**
     * Record a successful execution
     */
    private onSuccess;
    /**
     * Record a failed execution
     */
    private onFailure;
    /**
     * Manually reset the circuit breaker to CLOSED
     */
    reset(): void;
    /**
     * Get current circuit breaker statistics
     */
    getStats(): CircuitBreakerStats;
    /**
     * Get current state
     */
    getState(): CircuitState;
    /**
     * Check if circuit is open
     */
    isOpen(): boolean;
    /**
     * Check if circuit is closed (normal operation)
     */
    isClosed(): boolean;
    /**
     * Check if circuit is half-open (testing recovery)
     */
    isHalfOpen(): boolean;
}
/**
 * Circuit Breaker Registry
 * Manages multiple circuit breakers for different services
 */
export declare class CircuitBreakerRegistry {
    private breakers;
    /**
     * Get or create a circuit breaker for a service
     */
    getBreaker(name: string, options?: CircuitBreakerOptions): CircuitBreaker;
    /**
     * Get statistics for all circuit breakers
     */
    getAllStats(): Record<string, CircuitBreakerStats>;
    /**
     * Reset all circuit breakers
     */
    resetAll(): void;
    /**
     * Get count of open circuits
     */
    getOpenCount(): number;
}
export declare const getCircuitBreakerRegistry: () => CircuitBreakerRegistry;
//# sourceMappingURL=circuitBreaker.d.ts.map