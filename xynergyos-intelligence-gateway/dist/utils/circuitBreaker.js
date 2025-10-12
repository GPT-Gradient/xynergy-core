"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getCircuitBreakerRegistry = exports.CircuitBreakerRegistry = exports.CircuitBreaker = exports.CircuitState = void 0;
const logger_1 = require("./logger");
/**
 * Circuit Breaker Pattern Implementation
 * Prevents cascading failures by stopping requests to failing services
 */
var CircuitState;
(function (CircuitState) {
    CircuitState["CLOSED"] = "CLOSED";
    CircuitState["OPEN"] = "OPEN";
    CircuitState["HALF_OPEN"] = "HALF_OPEN"; // Testing if service recovered
})(CircuitState || (exports.CircuitState = CircuitState = {}));
class CircuitBreaker {
    name;
    options;
    state = CircuitState.CLOSED;
    failures = 0;
    successes = 0;
    totalRequests = 0;
    lastFailureTime = null;
    nextAttemptTime = null;
    failureTimestamps = [];
    constructor(name, options = {
        failureThreshold: 5,
        successThreshold: 2,
        timeout: 60000,
        monitoringPeriod: 60000,
    }) {
        this.name = name;
        this.options = options;
        logger_1.logger.info('Circuit breaker initialized', {
            name,
            failureThreshold: options.failureThreshold,
            timeout: options.timeout,
        });
    }
    /**
     * Execute a function with circuit breaker protection
     */
    async execute(fn) {
        this.totalRequests++;
        // Check if circuit is open
        if (this.state === CircuitState.OPEN) {
            if (this.nextAttemptTime && Date.now() < this.nextAttemptTime) {
                logger_1.logger.warn('Circuit breaker is OPEN, rejecting request', {
                    name: this.name,
                    nextAttempt: new Date(this.nextAttemptTime).toISOString(),
                });
                throw new Error(`Circuit breaker [${this.name}] is OPEN`);
            }
            // Timeout elapsed, transition to HALF_OPEN
            this.state = CircuitState.HALF_OPEN;
            this.successes = 0;
            logger_1.logger.info('Circuit breaker transitioning to HALF_OPEN', {
                name: this.name,
            });
        }
        try {
            const result = await fn();
            // Success - record it
            this.onSuccess();
            return result;
        }
        catch (error) {
            // Failure - record it
            this.onFailure();
            throw error;
        }
    }
    /**
     * Record a successful execution
     */
    onSuccess() {
        this.failures = 0;
        this.failureTimestamps = [];
        if (this.state === CircuitState.HALF_OPEN) {
            this.successes++;
            if (this.successes >= this.options.successThreshold) {
                this.state = CircuitState.CLOSED;
                this.successes = 0;
                this.nextAttemptTime = null;
                logger_1.logger.info('Circuit breaker CLOSED - service recovered', {
                    name: this.name,
                });
            }
        }
    }
    /**
     * Record a failed execution
     */
    onFailure() {
        const now = Date.now();
        this.failures++;
        this.lastFailureTime = now;
        this.failureTimestamps.push(now);
        // Remove old timestamps outside monitoring period
        const cutoff = now - this.options.monitoringPeriod;
        this.failureTimestamps = this.failureTimestamps.filter(t => t > cutoff);
        logger_1.logger.warn('Circuit breaker recorded failure', {
            name: this.name,
            failures: this.failureTimestamps.length,
            threshold: this.options.failureThreshold,
        });
        // Check if we should open the circuit
        if (this.state === CircuitState.HALF_OPEN ||
            this.failureTimestamps.length >= this.options.failureThreshold) {
            this.state = CircuitState.OPEN;
            this.nextAttemptTime = now + this.options.timeout;
            this.successes = 0;
            logger_1.logger.error('Circuit breaker OPENED', {
                name: this.name,
                failures: this.failures,
                nextAttempt: new Date(this.nextAttemptTime).toISOString(),
            });
        }
    }
    /**
     * Manually reset the circuit breaker to CLOSED
     */
    reset() {
        this.state = CircuitState.CLOSED;
        this.failures = 0;
        this.successes = 0;
        this.failureTimestamps = [];
        this.lastFailureTime = null;
        this.nextAttemptTime = null;
        logger_1.logger.info('Circuit breaker manually reset', { name: this.name });
    }
    /**
     * Get current circuit breaker statistics
     */
    getStats() {
        return {
            state: this.state,
            failures: this.failureTimestamps.length,
            successes: this.successes,
            totalRequests: this.totalRequests,
            lastFailureTime: this.lastFailureTime,
            nextAttemptTime: this.nextAttemptTime,
        };
    }
    /**
     * Get current state
     */
    getState() {
        return this.state;
    }
    /**
     * Check if circuit is open
     */
    isOpen() {
        return this.state === CircuitState.OPEN;
    }
    /**
     * Check if circuit is closed (normal operation)
     */
    isClosed() {
        return this.state === CircuitState.CLOSED;
    }
    /**
     * Check if circuit is half-open (testing recovery)
     */
    isHalfOpen() {
        return this.state === CircuitState.HALF_OPEN;
    }
}
exports.CircuitBreaker = CircuitBreaker;
/**
 * Circuit Breaker Registry
 * Manages multiple circuit breakers for different services
 */
class CircuitBreakerRegistry {
    breakers = new Map();
    /**
     * Get or create a circuit breaker for a service
     */
    getBreaker(name, options) {
        if (!this.breakers.has(name)) {
            this.breakers.set(name, new CircuitBreaker(name, options));
        }
        return this.breakers.get(name);
    }
    /**
     * Get statistics for all circuit breakers
     */
    getAllStats() {
        const stats = {};
        for (const [name, breaker] of this.breakers.entries()) {
            stats[name] = breaker.getStats();
        }
        return stats;
    }
    /**
     * Reset all circuit breakers
     */
    resetAll() {
        for (const breaker of this.breakers.values()) {
            breaker.reset();
        }
        logger_1.logger.info('All circuit breakers reset');
    }
    /**
     * Get count of open circuits
     */
    getOpenCount() {
        let count = 0;
        for (const breaker of this.breakers.values()) {
            if (breaker.isOpen()) {
                count++;
            }
        }
        return count;
    }
}
exports.CircuitBreakerRegistry = CircuitBreakerRegistry;
// Singleton instance
let registry;
const getCircuitBreakerRegistry = () => {
    if (!registry) {
        registry = new CircuitBreakerRegistry();
    }
    return registry;
};
exports.getCircuitBreakerRegistry = getCircuitBreakerRegistry;
//# sourceMappingURL=circuitBreaker.js.map