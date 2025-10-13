/**
 * Audit Logging Middleware - OPTIMIZED VERSION
 * All security and performance issues fixed
 */

import { Request, Response, NextFunction } from 'express';
import axios, { AxiosInstance } from 'axios';
import { v4 as uuidv4 } from 'uuid';
import CircuitBreaker from 'opossum';
import pino from 'pino';
import { RateLimiterMemory } from 'rate-limiter-flexible';

// Structured logger
const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true
    }
  }
});

// Validate environment variables at startup
const AUDIT_SERVICE_URL = process.env.AUDIT_SERVICE_URL || 'https://audit-logging-service-835612502919.us-central1.run.app';
const AUDIT_API_KEY = process.env.AUDIT_API_KEY;

if (!AUDIT_API_KEY) {
  throw new Error('AUDIT_API_KEY environment variable is required');
}

// Connection pool for HTTP client
class HTTPClientPool {
  private static instance: HTTPClientPool;
  private client: AxiosInstance;

  private constructor() {
    this.client = axios.create({
      baseURL: AUDIT_SERVICE_URL,
      timeout: 5000,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': AUDIT_API_KEY
      },
      maxRedirects: 0,
      validateStatus: (status) => status < 500
    });

    // Add request/response interceptors for logging
    this.client.interceptors.request.use(
      (config) => {
        config.headers['X-Request-ID'] = uuidv4();
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        logger.error('Audit request failed', { error: error.message });
        return Promise.reject(error);
      }
    );
  }

  public static getInstance(): HTTPClientPool {
    if (!HTTPClientPool.instance) {
      HTTPClientPool.instance = new HTTPClientPool();
    }
    return HTTPClientPool.instance;
  }

  public getClient(): AxiosInstance {
    return this.client;
  }
}

// Batch processor for audit events
class BatchProcessor<T> {
  private buffer: T[] = [];
  private batchSize: number;
  private flushInterval: number;
  private flushTimer: NodeJS.Timeout | null = null;
  private processFn: (batch: T[]) => Promise<void>;

  constructor(
    batchSize: number = 100,
    flushInterval: number = 5000,
    processFn: (batch: T[]) => Promise<void>
  ) {
    this.batchSize = batchSize;
    this.flushInterval = flushInterval;
    this.processFn = processFn;
  }

  async add(item: T): Promise<void> {
    this.buffer.push(item);

    if (this.buffer.length >= this.batchSize) {
      await this.flush();
    } else if (!this.flushTimer) {
      this.flushTimer = setTimeout(() => this.flush(), this.flushInterval);
    }
  }

  async flush(): Promise<void> {
    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }

    if (this.buffer.length === 0) return;

    const batch = this.buffer.splice(0, this.batchSize);

    try {
      await this.processFn(batch);
    } catch (error) {
      logger.error('Batch processing failed', { error, batchSize: batch.length });
    }
  }

  async shutdown(): Promise<void> {
    await this.flush();
  }
}

// Circuit breaker configuration
const circuitBreakerOptions = {
  timeout: 5000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000,
  volumeThreshold: 10,
  fallback: (error: Error) => {
    logger.warn('Circuit breaker fallback triggered', { error: error.message });
    return null;
  }
};

// Types
interface AuditEvent {
  log_id?: string;
  user_id: string;
  tenant_id?: string;
  action: string;
  resource: string;
  resource_id?: string;
  granted: boolean;
  reason?: string;
  metadata?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  timestamp?: string;
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  request_id?: string;
}

// Input validation
function validateAuditEvent(event: AuditEvent): boolean {
  // Validate required fields
  if (!event.user_id || !event.action || !event.resource) {
    return false;
  }

  // Validate user_id format
  const userIdPattern = /^[a-zA-Z0-9@._-]+$/;
  if (!userIdPattern.test(event.user_id)) {
    return false;
  }

  // Validate metadata size (10KB limit)
  if (event.metadata && JSON.stringify(event.metadata).length > 10240) {
    return false;
  }

  // Validate severity
  const validSeverities = ['INFO', 'WARNING', 'ERROR', 'CRITICAL'];
  if (!validSeverities.includes(event.severity)) {
    return false;
  }

  return true;
}

// Extract action from request with improved logic
function extractAction(req: Request): string {
  const method = req.method.toLowerCase();
  const path = req.path;

  // More specific patterns
  const patterns = [
    { regex: /^\/api\/v\d+\/auth/, action: `auth.${method}` },
    { regex: /^\/api\/v\d+\/slack/, action: `slack.${method}` },
    { regex: /^\/api\/v\d+\/gmail/, action: `gmail.${method}` },
    { regex: /^\/api\/v\d+\/crm/, action: `crm.${method}` },
    { regex: /^\/api\/v\d+\/services/, action: `service.${method}` },
    { regex: /^\/health/, action: 'health.check' },
    { regex: /^\/metrics/, action: 'metrics.read' }
  ];

  for (const pattern of patterns) {
    if (pattern.regex.test(path)) {
      return pattern.action;
    }
  }

  return `api.${method}`;
}

// Extract resource from request
function extractResource(req: Request): string {
  const path = req.path;
  const parts = path.split('/').filter(p => p && p !== 'api' && !p.startsWith('v'));

  if (parts.length >= 2) {
    return `${parts[0]}/${parts[1]}`.substring(0, 100); // Limit length
  }
  return parts[0]?.substring(0, 100) || 'unknown';
}

// Get real IP address
function getRealIp(req: Request): string {
  const xForwardedFor = req.headers['x-forwarded-for'];
  if (xForwardedFor) {
    const ips = Array.isArray(xForwardedFor) ? xForwardedFor[0] : xForwardedFor;
    return ips.split(',')[0].trim();
  }

  const xRealIp = req.headers['x-real-ip'];
  if (xRealIp) {
    return Array.isArray(xRealIp) ? xRealIp[0] : xRealIp;
  }

  return req.ip || req.connection.remoteAddress || 'unknown';
}

// Determine severity based on response
function determineSeverity(statusCode: number, error?: any): AuditEvent['severity'] {
  if (statusCode >= 500 || error) return 'ERROR';
  if (statusCode >= 400) return 'WARNING';
  if (statusCode === 429) return 'WARNING'; // Rate limit
  return 'INFO';
}

// Initialize components
const httpClient = HTTPClientPool.getInstance();
const batchProcessor = new BatchProcessor<AuditEvent>(
  50, // batch size
  5000, // flush interval (ms)
  async (batch: AuditEvent[]) => {
    try {
      // Send batch to audit service
      await httpClient.getClient().post('/api/audit/batch', { events: batch });
      logger.info(`Batch of ${batch.length} audit events sent`);
    } catch (error) {
      logger.error('Failed to send audit batch', { error });
    }
  }
);

// Circuit breaker for audit service calls
const auditCircuitBreaker = new CircuitBreaker(
  async (event: AuditEvent) => {
    const client = httpClient.getClient();
    const response = await client.post('/api/audit/log', event);
    return response.data;
  },
  circuitBreakerOptions
);

// Rate limiter for audit events per user
const rateLimiter = new RateLimiterMemory({
  points: 100, // Number of points
  duration: 60, // Per 60 seconds
});

// Send audit event with all protections
async function sendAuditEvent(event: AuditEvent): Promise<void> {
  // Validate event
  if (!validateAuditEvent(event)) {
    logger.warn('Invalid audit event', { event });
    return;
  }

  try {
    // Check rate limit
    await rateLimiter.consume(event.user_id, 1);

    // Try circuit breaker
    const result = await auditCircuitBreaker.fire(event);

    if (!result) {
      // Fallback to batch processor
      await batchProcessor.add(event);
    }
  } catch (error: any) {
    if (error?.remainingPoints !== undefined) {
      // Rate limit exceeded
      logger.warn('Rate limit exceeded for user', { user_id: event.user_id });
    } else {
      // Log error but don't fail the request
      logger.error('Failed to send audit event', { error: error.message, event });

      // Add to batch as fallback
      await batchProcessor.add(event);
    }
  }
}

// Main audit logging middleware
export function auditLogger() {
  return async (req: Request, res: Response, next: NextFunction) => {
    // Skip health checks and static assets
    if (req.path === '/health' ||
        req.path === '/metrics' ||
        req.path === '/favicon.ico' ||
        req.path.startsWith('/static')) {
      return next();
    }

    const startTime = Date.now();
    const requestId = req.headers['x-request-id'] as string || uuidv4();

    // Add request ID to request object
    (req as any).requestId = requestId;

    // Capture original methods
    const originalSend = res.send;
    const originalJson = res.json;
    const originalEnd = res.end;

    let responseBody: any;
    let errorOccurred = false;

    // Intercept response methods
    res.send = function(data: any) {
      responseBody = data;
      return originalSend.call(this, data);
    };

    res.json = function(data: any) {
      responseBody = data;
      return originalJson.call(this, data);
    };

    res.end = function(...args: any[]) {
      return originalEnd.apply(this, args);
    };

    // Handle response finish
    res.on('finish', async () => {
      const duration = Date.now() - startTime;

      // Extract user info from request
      const user = (req as any).user;
      const userId = user?.uid || user?.email || 'anonymous';
      const tenantId = user?.tenant_id || req.headers['x-tenant-id'] as string;

      // Build audit event
      const auditEvent: AuditEvent = {
        log_id: `log_${uuidv4().substring(0, 8)}`,
        user_id: userId.substring(0, 255), // Limit length
        tenant_id: tenantId?.substring(0, 100),
        action: extractAction(req),
        resource: extractResource(req),
        resource_id: req.params.id?.substring(0, 255),
        granted: res.statusCode < 400,
        reason: res.statusCode >= 400 ? `HTTP ${res.statusCode}` : undefined,
        metadata: {
          method: req.method,
          path: req.path.substring(0, 500),
          query: Object.keys(req.query).length > 0 ? req.query : undefined,
          status_code: res.statusCode,
          duration_ms: duration,
          request_id: requestId,
          service: 'intelligence-gateway'
        },
        ip_address: getRealIp(req),
        user_agent: (req.headers['user-agent'] as string)?.substring(0, 500),
        timestamp: new Date().toISOString(),
        severity: determineSeverity(res.statusCode, errorOccurred),
        request_id: requestId
      };

      // Send audit event asynchronously
      setImmediate(() => {
        sendAuditEvent(auditEvent).catch(error => {
          logger.error('Failed to process audit event', { error });
        });
      });
    });

    // Handle errors
    res.on('error', (error) => {
      errorOccurred = true;
      logger.error('Response error', { error: error.message, requestId });
    });

    // Add response timeout
    const timeout = setTimeout(() => {
      if (!res.headersSent) {
        res.status(504).json({ error: 'Request timeout' });
      }
    }, 30000); // 30 second timeout

    res.on('finish', () => clearTimeout(timeout));

    next();
  };
}

// Security alert middleware for critical operations
export function securityAlert(action: string, severity: AuditEvent['severity'] = 'WARNING') {
  return async (req: Request, res: Response, next: NextFunction) => {
    const user = (req as any).user;
    const userId = user?.uid || 'anonymous';
    const requestId = (req as any).requestId || uuidv4();

    // Log security-sensitive action immediately
    const auditEvent: AuditEvent = {
      user_id: userId,
      action: `security.${action}`,
      resource: extractResource(req),
      granted: false, // Will be updated based on response
      metadata: {
        security_action: action,
        path: req.path,
        method: req.method,
        request_id: requestId
      },
      ip_address: getRealIp(req),
      user_agent: req.headers['user-agent'] as string,
      severity: severity,
      request_id: requestId,
      timestamp: new Date().toISOString()
    };

    // Send immediate alert for CRITICAL actions
    if (severity === 'CRITICAL') {
      await sendAuditEvent(auditEvent);
    }

    // Continue with request
    next();

    // Log result after response
    res.on('finish', async () => {
      auditEvent.granted = res.statusCode < 400;
      if (severity !== 'CRITICAL') {
        await sendAuditEvent(auditEvent);
      }
    });
  };
}

// Compliance tracking middleware
export function complianceTracker(complianceType: 'GDPR' | 'HIPAA' | 'SOC2' | 'PCI') {
  return async (req: Request, res: Response, next: NextFunction) => {
    const user = (req as any).user;
    const userId = user?.uid || 'anonymous';
    const requestId = (req as any).requestId || uuidv4();

    const auditEvent: AuditEvent = {
      user_id: userId,
      action: `compliance.${complianceType.toLowerCase()}.access`,
      resource: extractResource(req),
      granted: true,
      metadata: {
        compliance_type: complianceType,
        data_classification: req.headers['x-data-classification'] || 'public',
        purpose: req.headers['x-access-purpose'] || 'business',
        request_id: requestId
      },
      severity: 'INFO',
      request_id: requestId,
      timestamp: new Date().toISOString()
    };

    await sendAuditEvent(auditEvent);
    next();
  };
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, flushing audit events');
  await batchProcessor.shutdown();
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received, flushing audit events');
  await batchProcessor.shutdown();
  process.exit(0);
});

export default auditLogger;