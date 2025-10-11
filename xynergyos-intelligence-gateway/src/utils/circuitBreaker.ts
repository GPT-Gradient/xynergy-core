import { logger } from './logger';

/**
 * Circuit Breaker Pattern Implementation
 * Prevents cascading failures by stopping requests to failing services
 */

export enum CircuitState {
  CLOSED = 'CLOSED',     // Normal operation
  OPEN = 'OPEN',         // Failing, reject requests
  HALF_OPEN = 'HALF_OPEN' // Testing if service recovered
}

export interface CircuitBreakerOptions {
  failureThreshold: number;    // Number of failures before opening (default: 5)
  successThreshold: number;    // Number of successes to close from half-open (default: 2)
  timeout: number;             // Time in ms before attempting reset (default: 60000)
  monitoringPeriod: number;    // Time window for counting failures (default: 60000)
}

export interface CircuitBreakerStats {
  state: CircuitState;
  failures: number;
  successes: number;
  totalRequests: number;
  lastFailureTime: number | null;
  nextAttemptTime: number | null;
}

export class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failures: number = 0;
  private successes: number = 0;
  private totalRequests: number = 0;
  private lastFailureTime: number | null = null;
  private nextAttemptTime: number | null = null;
  private failureTimestamps: number[] = [];

  constructor(
    private name: string,
    private options: CircuitBreakerOptions = {
      failureThreshold: 5,
      successThreshold: 2,
      timeout: 60000,
      monitoringPeriod: 60000,
    }
  ) {
    logger.info('Circuit breaker initialized', {
      name,
      failureThreshold: options.failureThreshold,
      timeout: options.timeout,
    });
  }

  /**
   * Execute a function with circuit breaker protection
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    this.totalRequests++;

    // Check if circuit is open
    if (this.state === CircuitState.OPEN) {
      if (this.nextAttemptTime && Date.now() < this.nextAttemptTime) {
        logger.warn('Circuit breaker is OPEN, rejecting request', {
          name: this.name,
          nextAttempt: new Date(this.nextAttemptTime).toISOString(),
        });
        throw new Error(`Circuit breaker [${this.name}] is OPEN`);
      }

      // Timeout elapsed, transition to HALF_OPEN
      this.state = CircuitState.HALF_OPEN;
      this.successes = 0;
      logger.info('Circuit breaker transitioning to HALF_OPEN', {
        name: this.name,
      });
    }

    try {
      const result = await fn();

      // Success - record it
      this.onSuccess();

      return result;
    } catch (error) {
      // Failure - record it
      this.onFailure();

      throw error;
    }
  }

  /**
   * Record a successful execution
   */
  private onSuccess(): void {
    this.failures = 0;
    this.failureTimestamps = [];

    if (this.state === CircuitState.HALF_OPEN) {
      this.successes++;

      if (this.successes >= this.options.successThreshold) {
        this.state = CircuitState.CLOSED;
        this.successes = 0;
        this.nextAttemptTime = null;

        logger.info('Circuit breaker CLOSED - service recovered', {
          name: this.name,
        });
      }
    }
  }

  /**
   * Record a failed execution
   */
  private onFailure(): void {
    const now = Date.now();
    this.failures++;
    this.lastFailureTime = now;
    this.failureTimestamps.push(now);

    // Remove old timestamps outside monitoring period
    const cutoff = now - this.options.monitoringPeriod;
    this.failureTimestamps = this.failureTimestamps.filter(t => t > cutoff);

    logger.warn('Circuit breaker recorded failure', {
      name: this.name,
      failures: this.failureTimestamps.length,
      threshold: this.options.failureThreshold,
    });

    // Check if we should open the circuit
    if (
      this.state === CircuitState.HALF_OPEN ||
      this.failureTimestamps.length >= this.options.failureThreshold
    ) {
      this.state = CircuitState.OPEN;
      this.nextAttemptTime = now + this.options.timeout;
      this.successes = 0;

      logger.error('Circuit breaker OPENED', {
        name: this.name,
        failures: this.failures,
        nextAttempt: new Date(this.nextAttemptTime).toISOString(),
      });
    }
  }

  /**
   * Manually reset the circuit breaker to CLOSED
   */
  reset(): void {
    this.state = CircuitState.CLOSED;
    this.failures = 0;
    this.successes = 0;
    this.failureTimestamps = [];
    this.lastFailureTime = null;
    this.nextAttemptTime = null;

    logger.info('Circuit breaker manually reset', { name: this.name });
  }

  /**
   * Get current circuit breaker statistics
   */
  getStats(): CircuitBreakerStats {
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
  getState(): CircuitState {
    return this.state;
  }

  /**
   * Check if circuit is open
   */
  isOpen(): boolean {
    return this.state === CircuitState.OPEN;
  }

  /**
   * Check if circuit is closed (normal operation)
   */
  isClosed(): boolean {
    return this.state === CircuitState.CLOSED;
  }

  /**
   * Check if circuit is half-open (testing recovery)
   */
  isHalfOpen(): boolean {
    return this.state === CircuitState.HALF_OPEN;
  }
}

/**
 * Circuit Breaker Registry
 * Manages multiple circuit breakers for different services
 */
export class CircuitBreakerRegistry {
  private breakers: Map<string, CircuitBreaker> = new Map();

  /**
   * Get or create a circuit breaker for a service
   */
  getBreaker(name: string, options?: CircuitBreakerOptions): CircuitBreaker {
    if (!this.breakers.has(name)) {
      this.breakers.set(name, new CircuitBreaker(name, options));
    }

    return this.breakers.get(name)!;
  }

  /**
   * Get statistics for all circuit breakers
   */
  getAllStats(): Record<string, CircuitBreakerStats> {
    const stats: Record<string, CircuitBreakerStats> = {};

    for (const [name, breaker] of this.breakers.entries()) {
      stats[name] = breaker.getStats();
    }

    return stats;
  }

  /**
   * Reset all circuit breakers
   */
  resetAll(): void {
    for (const breaker of this.breakers.values()) {
      breaker.reset();
    }

    logger.info('All circuit breakers reset');
  }

  /**
   * Get count of open circuits
   */
  getOpenCount(): number {
    let count = 0;
    for (const breaker of this.breakers.values()) {
      if (breaker.isOpen()) {
        count++;
      }
    }
    return count;
  }
}

// Singleton instance
let registry: CircuitBreakerRegistry;

export const getCircuitBreakerRegistry = (): CircuitBreakerRegistry => {
  if (!registry) {
    registry = new CircuitBreakerRegistry();
  }
  return registry;
};
