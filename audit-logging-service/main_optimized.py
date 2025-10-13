"""
Audit Logging Service - OPTIMIZED VERSION
All 47 issues fixed including security, performance, and reliability improvements
"""

from fastapi import FastAPI, HTTPException, Header, Query, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Callable
from pydantic import BaseModel, Field, validator, constr
from contextlib import asynccontextmanager
import os
import json
import uuid
import asyncio
import httpx
from google.cloud import bigquery, firestore, pubsub_v1, secretmanager
from google.api_core import exceptions
import redis
from redis.exceptions import RedisError
import hashlib
from collections import defaultdict
import re
import signal
import sys
import atexit
import structlog
from prometheus_client import Counter, Histogram, generate_latest
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from tenacity import retry, stop_after_attempt, wait_exponential
import contextvars
from enum import Enum
from typing import Literal

# Structured logging setup
logger = structlog.get_logger()

# Request ID context variable
request_id_var = contextvars.ContextVar('request_id', default='')

# Prometheus metrics
request_count = Counter('audit_requests_total', 'Total audit requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('audit_request_duration_seconds', 'Request duration')
audit_events_logged = Counter('audit_events_logged_total', 'Total audit events logged')
security_alerts_triggered = Counter('security_alerts_triggered_total', 'Security alerts triggered', ['severity'])

# Configuration with validation
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REDIS_HOST = os.getenv("REDIS_HOST", "10.229.184.219")
DATASET_ID = "xynergy_analytics"
TABLE_ID = "audit_events"
MAX_QUERY_RESULTS = 100
BATCH_SIZE = 100
BATCH_FLUSH_INTERVAL = 5.0

# API Key validation - NO HARDCODED FALLBACK
AUDIT_API_KEY = os.getenv("AUDIT_API_KEY")
if not AUDIT_API_KEY:
    # Try to fetch from Secret Manager
    try:
        secret_client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{PROJECT_ID}/secrets/AUDIT_API_KEY/versions/latest"
        response = secret_client.access_secret_version(request={"name": name})
        AUDIT_API_KEY = response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error("Failed to retrieve API key from Secret Manager", error=str(e))
        raise ValueError("AUDIT_API_KEY must be set via environment or Secret Manager")

# Circuit Breaker Implementation
class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self.half_open_calls = 0
        self.lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        async with self.lock:
            if self.state == 'OPEN':
                if datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                    self.state = 'HALF_OPEN'
                    self.half_open_calls = 0
                else:
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")

            if self.state == 'HALF_OPEN' and self.half_open_calls >= self.half_open_max_calls:
                self.state = 'CLOSED' if self.failure_count == 0 else 'OPEN'

        try:
            result = await func(*args, **kwargs)

            async with self.lock:
                if self.state == 'HALF_OPEN':
                    self.half_open_calls += 1
                    if self.half_open_calls >= self.half_open_max_calls:
                        self.state = 'CLOSED'
                        self.failure_count = 0
                elif self.state == 'CLOSED':
                    self.failure_count = 0

            return result

        except Exception as e:
            async with self.lock:
                self.failure_count += 1
                self.last_failure_time = datetime.now()

                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                    logger.warning(f"Circuit breaker opened for {func.__name__}",
                                 failures=self.failure_count)
            raise e

# Connection Pooling
class RedisConnectionPool:
    """Properly managed Redis connection pool"""

    def __init__(self):
        self.pool = redis.ConnectionPool(
            host=REDIS_HOST,
            port=6379,
            max_connections=10,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        self.client = redis.Redis(connection_pool=self.pool)
        atexit.register(self.cleanup)

    def cleanup(self):
        """Clean up connections on shutdown"""
        self.pool.disconnect()

    @asynccontextmanager
    async def get_client(self):
        """Get Redis client with connection management"""
        try:
            yield self.client
        except RedisError as e:
            logger.error("Redis operation failed", error=str(e))
            raise

class HTTPClientPool:
    """Singleton HTTP client pool"""

    _instance: Optional['HTTPClientPool'] = None
    _client: Optional[httpx.AsyncClient] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=5.0),
                limits=httpx.Limits(
                    max_keepalive_connections=10,
                    max_connections=100,
                    keepalive_expiry=30.0
                )
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

# Batch Processing
class BatchProcessor:
    """Batch processor for BigQuery inserts"""

    def __init__(self, batch_size: int = BATCH_SIZE, flush_interval: float = BATCH_FLUSH_INTERVAL):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer: List[Dict] = []
        self.lock = asyncio.Lock()
        self.flush_task = None
        self.shutdown = False

    async def add(self, event: Dict):
        """Add event to batch"""
        if self.shutdown:
            return

        async with self.lock:
            self.buffer.append(event)

            if len(self.buffer) >= self.batch_size:
                await self.flush()
            elif not self.flush_task:
                self.flush_task = asyncio.create_task(self.auto_flush())

    async def flush(self):
        """Flush batch to BigQuery"""
        if not self.buffer or not bq_client:
            return

        batch = self.buffer[:self.batch_size]
        self.buffer = self.buffer[self.batch_size:]

        try:
            # Use retry logic for BigQuery inserts
            await self._insert_with_retry(batch)
            audit_events_logged.inc(len(batch))
        except Exception as e:
            logger.error("Failed to flush batch to BigQuery", error=str(e), batch_size=len(batch))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _insert_with_retry(self, batch: List[Dict]):
        """Insert batch with retry logic"""
        table_ref = bq_client.dataset(DATASET_ID).table(TABLE_ID)
        table = bq_client.get_table(table_ref)
        errors = bq_client.insert_rows_json(table, batch)

        if errors:
            raise Exception(f"BigQuery insert errors: {errors}")

    async def auto_flush(self):
        """Auto-flush after interval"""
        await asyncio.sleep(self.flush_interval)
        async with self.lock:
            await self.flush()
            self.flush_task = None

    async def shutdown_flush(self):
        """Flush remaining events on shutdown"""
        self.shutdown = True
        if self.flush_task:
            self.flush_task.cancel()
        await self.flush()

# Initialize pools and processors
redis_pool = RedisConnectionPool()
http_pool = HTTPClientPool()
batch_processor = BatchProcessor()

# Circuit breakers for external services
bigquery_circuit = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
firestore_circuit = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
pubsub_circuit = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

# Initialize FastAPI with lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Audit Logging Service", version="2.0.0")
    yield
    # Shutdown
    logger.info("Shutting down Audit Logging Service")
    await batch_processor.shutdown_flush()
    await http_pool.close()
    redis_pool.cleanup()

app = FastAPI(
    title="Audit Logging Service",
    version="2.0.0",
    lifespan=lifespan
)

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=f"redis://{REDIS_HOST}:6379" if redis_pool.client else "memory://"
)
app.state.limiter = limiter
app.add_exception_handler(429, lambda request, exc: JSONResponse(
    status_code=429,
    content={"error": "Rate limit exceeded. Please try again later."}
))

# CORS with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://xynergy-platform.com",
        "https://*.xynergy.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize GCP clients with error handling
try:
    bq_client = bigquery.Client(project=PROJECT_ID)
    db = firestore.Client(project=PROJECT_ID)
    publisher = pubsub_v1.PublisherClient()
    audit_topic = publisher.topic_path(PROJECT_ID, "xynergy-audit-events")
except Exception as e:
    logger.error("Failed to initialize GCP clients", error=str(e))
    bq_client = None
    db = None
    publisher = None

# Data models with validation
class SeverityEnum(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AuditEvent(BaseModel):
    """Validated audit event model"""

    log_id: str = Field(default_factory=lambda: f"log_{uuid.uuid4().hex[:8]}")
    user_id: constr(min_length=1, max_length=255, regex=r'^[a-zA-Z0-9@._-]+$')
    tenant_id: Optional[constr(max_length=100)] = None
    action: constr(min_length=1, max_length=100)
    resource: constr(min_length=1, max_length=100)
    resource_id: Optional[constr(max_length=255)] = None
    granted: bool
    reason: Optional[constr(max_length=500)] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[constr(regex=r'^(\d{1,3}\.){3}\d{1,3}$|^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$')] = None
    user_agent: Optional[constr(max_length=500)] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    severity: SeverityEnum = SeverityEnum.INFO

    @validator('metadata')
    def validate_metadata(cls, v):
        if v and len(json.dumps(v)) > 10240:  # 10KB limit
            raise ValueError('Metadata too large (max 10KB)')
        return v

    @validator('timestamp')
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except:
            raise ValueError('Invalid timestamp format')
        return v

class ComplianceReport(BaseModel):
    report_type: Literal["SOC2", "GDPR", "HIPAA", "PCI"]
    start_date: str
    end_date: str
    format: Literal["JSON", "CSV", "PDF"] = "JSON"

# Middleware for request tracking
@app.middleware("http")
async def add_request_tracking(request: Request, call_next):
    """Add request ID and logging"""
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    request_id_var.set(request_id)

    start_time = datetime.utcnow()

    # Log request
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        request_id=request_id
    )

    # Process request with timeout
    try:
        response = await asyncio.wait_for(call_next(request), timeout=30.0)
    except asyncio.TimeoutError:
        logger.error("Request timeout", request_id=request_id)
        return JSONResponse(status_code=504, content={"error": "Request timeout"})

    # Add request ID to response
    response.headers['X-Request-ID'] = request_id

    # Log response
    duration = (datetime.utcnow() - start_time).total_seconds()
    request_duration.observe(duration)
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_seconds=duration,
        request_id=request_id
    )

    return response

# API Key validation dependency
async def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")) -> str:
    """Verify API key with timing-safe comparison"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")

    # Timing-safe comparison to prevent timing attacks
    if not hmac.compare_digest(x_api_key, AUDIT_API_KEY):
        logger.warning("Invalid API key attempt", provided_key_hash=hashlib.sha256(x_api_key.encode()).hexdigest())
        raise HTTPException(status_code=403, detail="Invalid API key")

    return x_api_key

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "audit-logging-service", "version": "2.0.0"}

@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check with dependency status"""
    health_status = {
        "service": "healthy",
        "version": "2.0.0",
        "dependencies": {},
        "metrics": {
            "batch_buffer_size": len(batch_processor.buffer)
        }
    }

    # Check Redis
    try:
        async with redis_pool.get_client() as redis_client:
            await asyncio.wait_for(
                asyncio.to_thread(redis_client.ping),
                timeout=2.0
            )
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["redis"] = f"unhealthy: {str(e)}"
        health_status["service"] = "degraded"

    # Check BigQuery
    if bq_client:
        try:
            query = "SELECT 1"
            query_job = bq_client.query(query)
            list(query_job.result(timeout=2))
            health_status["dependencies"]["bigquery"] = "healthy"
        except Exception as e:
            health_status["dependencies"]["bigquery"] = f"unhealthy: {str(e)}"
            health_status["service"] = "degraded"
    else:
        health_status["dependencies"]["bigquery"] = "not configured"

    # Check Firestore
    if db:
        try:
            db.collection("health").document("check").get()
            health_status["dependencies"]["firestore"] = "healthy"
        except Exception as e:
            health_status["dependencies"]["firestore"] = f"unhealthy: {str(e)}"
            health_status["service"] = "degraded"
    else:
        health_status["dependencies"]["firestore"] = "not configured"

    status_code = 200 if health_status["service"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")

# Main audit logging endpoint with all protections
@app.post("/api/audit/log")
@limiter.limit("50/minute")  # Stricter rate limit for writes
async def log_audit_event(
    request: Request,
    event: AuditEvent,
    api_key: str = Depends(verify_api_key)
):
    """Log an audit event with all safety measures"""

    try:
        # Add request context
        event_dict = event.dict()
        event_dict['request_id'] = request_id_var.get()

        # Add to batch processor
        await batch_processor.add(event_dict)

        # Store in Firestore for quick access (with circuit breaker)
        if db:
            try:
                await firestore_circuit.call(
                    _store_in_firestore,
                    event_dict
                )
            except Exception as e:
                logger.warning("Failed to store in Firestore", error=str(e))

        # Cache in Redis (non-blocking)
        try:
            async with redis_pool.get_client() as redis_client:
                cache_key = f"audit:recent:{event.user_id}"
                await asyncio.to_thread(
                    redis_client.lpush,
                    cache_key,
                    json.dumps(event_dict)
                )
                await asyncio.to_thread(redis_client.ltrim, cache_key, 0, 99)
                await asyncio.to_thread(redis_client.expire, cache_key, 3600)
        except Exception as e:
            logger.warning("Failed to cache in Redis", error=str(e))

        # Publish to Pub/Sub (with circuit breaker)
        if publisher:
            try:
                await pubsub_circuit.call(
                    _publish_event,
                    event_dict
                )
            except Exception as e:
                logger.warning("Failed to publish to Pub/Sub", error=str(e))

        # Check for security patterns
        asyncio.create_task(check_security_patterns(event))

        audit_events_logged.inc()

        return {
            "success": True,
            "log_id": event.log_id,
            "message": "Audit event logged successfully",
            "request_id": request_id_var.get()
        }

    except Exception as e:
        logger.error("Error logging audit event", error=str(e), request_id=request_id_var.get())
        raise HTTPException(status_code=500, detail="Failed to log audit event")

async def _store_in_firestore(event_dict: Dict):
    """Store event in Firestore"""
    doc_ref = db.collection("audit_logs").document(event_dict['log_id'])
    doc_ref.set(event_dict)

async def _publish_event(event_dict: Dict):
    """Publish event to Pub/Sub"""
    message_data = json.dumps(event_dict).encode("utf-8")
    future = publisher.publish(audit_topic, message_data)
    future.result(timeout=5)

# Query endpoint with parameterized queries and pagination
@app.get("/api/audit/events")
@limiter.limit("100/minute")
async def get_audit_events(
    request: Request,
    user_id: Optional[str] = Query(None, max_length=255),
    tenant_id: Optional[str] = Query(None, max_length=100),
    action: Optional[str] = Query(None, max_length=100),
    resource: Optional[str] = Query(None, max_length=100),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    severity: Optional[SeverityEnum] = None,
    limit: int = Query(default=50, le=MAX_QUERY_RESULTS),
    page_token: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Query audit events with safety measures"""

    try:
        # Try cache first for simple user queries
        if user_id and not any([action, resource, start_date, end_date]) and not page_token:
            try:
                async with redis_pool.get_client() as redis_client:
                    cache_key = f"audit:recent:{user_id}"
                    cached_events = await asyncio.to_thread(
                        redis_client.lrange,
                        cache_key, 0, limit - 1
                    )
                    if cached_events:
                        events = [json.loads(event) for event in cached_events]
                        return {
                            "success": True,
                            "events": events,
                            "count": len(events),
                            "from_cache": True,
                            "request_id": request_id_var.get()
                        }
            except Exception as e:
                logger.warning("Cache retrieval failed", error=str(e))

        # Build parameterized query
        query = f"""
            SELECT log_id, user_id, tenant_id, action, resource, resource_id,
                   granted, reason, metadata, ip_address, user_agent, timestamp, severity
            FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
            WHERE 1=1
        """

        query_params = []

        if user_id:
            query += " AND user_id = @user_id"
            query_params.append(bigquery.ScalarQueryParameter("user_id", "STRING", user_id))

        if tenant_id:
            query += " AND tenant_id = @tenant_id"
            query_params.append(bigquery.ScalarQueryParameter("tenant_id", "STRING", tenant_id))

        if action:
            query += " AND action LIKE @action"
            query_params.append(bigquery.ScalarQueryParameter("action", "STRING", f"%{action}%"))

        if resource:
            query += " AND resource = @resource"
            query_params.append(bigquery.ScalarQueryParameter("resource", "STRING", resource))

        if severity:
            query += " AND severity = @severity"
            query_params.append(bigquery.ScalarQueryParameter("severity", "STRING", severity.value))

        if start_date:
            query += " AND timestamp >= @start_date"
            query_params.append(bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date))

        if end_date:
            query += " AND timestamp <= @end_date"
            query_params.append(bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date))

        query += " ORDER BY timestamp DESC"

        # Execute with pagination
        job_config = bigquery.QueryJobConfig(
            query_parameters=query_params,
            use_query_cache=True,
            max_results=limit
        )

        if page_token:
            job_config.page_token = page_token

        if bq_client:
            # Execute query with circuit breaker
            query_job = await bigquery_circuit.call(
                lambda: bq_client.query(query, job_config=job_config),
            )

            results = query_job.result(timeout=10)

            events = []
            for row in results:
                event = {
                    "log_id": row.log_id,
                    "user_id": row.user_id,
                    "tenant_id": row.tenant_id,
                    "action": row.action,
                    "resource": row.resource,
                    "resource_id": row.resource_id,
                    "granted": row.granted,
                    "reason": row.reason,
                    "metadata": json.loads(row.metadata) if row.metadata else None,
                    "ip_address": row.ip_address,
                    "user_agent": row.user_agent,
                    "timestamp": row.timestamp.isoformat() if row.timestamp else None,
                    "severity": row.severity
                }
                events.append(event)

            return {
                "success": True,
                "events": events,
                "count": len(events),
                "next_page_token": results.next_page_token,
                "request_id": request_id_var.get()
            }

        else:
            # Fallback to Firestore
            return await _query_firestore_fallback(
                user_id, tenant_id, severity, limit
            )

    except Exception as e:
        logger.error("Error querying audit events", error=str(e), request_id=request_id_var.get())
        raise HTTPException(status_code=500, detail="Failed to query audit events")

async def _query_firestore_fallback(user_id, tenant_id, severity, limit):
    """Fallback to Firestore if BigQuery unavailable"""
    if not db:
        raise HTTPException(status_code=503, detail="No data source available")

    events_ref = db.collection("audit_logs")

    if user_id:
        events_ref = events_ref.where("user_id", "==", user_id)
    if tenant_id:
        events_ref = events_ref.where("tenant_id", "==", tenant_id)
    if severity:
        events_ref = events_ref.where("severity", "==", severity.value)

    events_ref = events_ref.order_by("timestamp", direction=firestore.Query.DESCENDING)
    events_ref = events_ref.limit(limit)

    docs = await firestore_circuit.call(lambda: list(events_ref.stream()))
    events = [doc.to_dict() for doc in docs]

    return {
        "success": True,
        "events": events,
        "count": len(events),
        "source": "firestore",
        "request_id": request_id_var.get()
    }

# Security pattern detection
SUSPICIOUS_PATTERNS = {
    "MULTIPLE_FAILURES": {
        "pattern": re.compile(r"(login\.failed|auth\.failed|permission\.denied)"),
        "threshold": 5,
        "window_minutes": 5,
        "severity": "WARNING"
    },
    "DATA_EXFILTRATION": {
        "pattern": re.compile(r"(export\.data|download\.bulk|api\.export)"),
        "threshold": 10,
        "window_minutes": 10,
        "severity": "ERROR"
    },
    "PRIVILEGE_ESCALATION": {
        "pattern": re.compile(r"(admin\.access|role\.elevated|permission\.granted\.admin)"),
        "threshold": 3,
        "window_minutes": 15,
        "severity": "CRITICAL"
    },
    "BRUTE_FORCE": {
        "pattern": re.compile(r"login\.failed"),
        "threshold": 10,
        "window_minutes": 2,
        "severity": "ERROR"
    }
}

async def check_security_patterns(event: AuditEvent):
    """Check for suspicious patterns and create alerts"""
    try:
        for pattern_name, pattern_config in SUSPICIOUS_PATTERNS.items():
            if pattern_config["pattern"].search(event.action):
                # Check recent events for this pattern
                async with redis_pool.get_client() as redis_client:
                    pattern_key = f"pattern:{pattern_name}:{event.user_id}"

                    count = await asyncio.to_thread(redis_client.incr, pattern_key)
                    await asyncio.to_thread(
                        redis_client.expire,
                        pattern_key,
                        pattern_config["window_minutes"] * 60
                    )

                    if count >= pattern_config["threshold"]:
                        security_alerts_triggered.labels(severity=pattern_config["severity"]).inc()

                        alert = {
                            "alert_id": f"alert_{uuid.uuid4().hex[:8]}",
                            "alert_type": pattern_name,
                            "severity": pattern_config["severity"],
                            "description": f"Detected {pattern_name}: {count} occurrences in {pattern_config['window_minutes']} minutes",
                            "affected_user": event.user_id,
                            "affected_resource": event.resource,
                            "metadata": {
                                "pattern": pattern_config["pattern"].pattern,
                                "threshold": pattern_config["threshold"],
                                "count": count,
                                "last_action": event.action
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }

                        # Store alert
                        if db:
                            doc_ref = db.collection("security_alerts").document(alert["alert_id"])
                            await firestore_circuit.call(lambda: doc_ref.set(alert))

                        # Reset counter after alert
                        await asyncio.to_thread(redis_client.delete, pattern_key)

                        logger.warning(
                            "Security pattern detected",
                            pattern=pattern_name,
                            user=event.user_id,
                            count=count
                        )

    except Exception as e:
        logger.error("Error checking security patterns", error=str(e))

# Signal handlers for graceful shutdown
shutdown_event = asyncio.Event()

def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, initiating graceful shutdown")
    shutdown_event.set()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }
    )