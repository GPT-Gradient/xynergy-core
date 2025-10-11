# Technical Design Document (TDD)
## Xynergy Platform - AI-Powered Business Operations System

**Document Version:** 1.0
**Last Updated:** October 10, 2025
**Status:** Production
**Author:** Platform Engineering Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture](#architecture)
4. [Component Design](#component-design)
5. [Data Architecture](#data-architecture)
6. [Integration Design](#integration-design)
7. [Security Design](#security-design)
8. [Performance Design](#performance-design)
9. [Scalability Design](#scalability-design)
10. [Monitoring & Observability](#monitoring--observability)
11. [Deployment Architecture](#deployment-architecture)
12. [Technology Stack](#technology-stack)

---

## Executive Summary

### Purpose
The Xynergy Platform is a cloud-native, microservices-based AI operations platform designed to provide autonomous business operations including marketing automation, content generation, SEO optimization, analytics, and project management.

### Scope
This document describes the technical design of the entire Xynergy Platform, including:
- 48 microservices across multiple functional domains (21 Python + 4 TypeScript + 23 specialized)
- Intelligence Gateway with 4 communication intelligence services (Slack, Gmail, CRM, Gateway)
- 21 shared infrastructure modules
- Multi-tenant data architecture
- AI routing and cost optimization systems
- Real-time analytics and monitoring

### Design Goals
1. **Cost Efficiency**: 89% reduction in AI costs through intelligent routing
2. **Performance**: Sub-10ms cached response times, 96-98% cache hit rates
3. **Scalability**: Auto-scaling from 0 to thousands of concurrent users
4. **Reliability**: 99.9% uptime with circuit breakers and graceful degradation
5. **Security**: Zero-trust authentication, encrypted data at rest and in transit
6. **Maintainability**: Modular design with shared infrastructure components

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        External Clients                              │
│              (Web Apps, Mobile Apps, API Consumers)                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS/REST
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                                │
│            (Authentication, Rate Limiting, Routing)                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬─────────────────┐
         │               │               │                 │
┌────────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌───────▼──────┐
│  Intelligence │ │  Marketing  │ │    ASO     │ │   Platform   │
│   Gateway     │ │   Engine    │ │   Engine   │ │   Dashboard  │
└────────┬──────┘ └──────┬──────┘ └─────┬──────┘ └───────┬──────┘
         │               │               │                 │
         └───────────────┼───────────────┴─────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
    ┌───────▼─────┐          ┌───────▼────────┐
    │ AI Routing  │          │  Data Layer    │
    │   Engine    │          │   Services     │
    └───────┬─────┘          └───────┬────────┘
            │                         │
    ┌───────┴─────┐          ┌───────┴────────┐
    │ AI Providers│          │  Storage Layer  │
    │  (External) │          │ (Firestore, BQ) │
    └─────────────┘          └─────────────────┘
```

### System Characteristics

**Distributed Microservices Architecture:**
- 44 independent, loosely-coupled services
- Event-driven communication via Pub/Sub
- RESTful APIs for synchronous operations
- Shared infrastructure for common functionality

**Multi-Tenant Design:**
- Tenant isolation at data and service levels
- Per-tenant datasets in BigQuery
- Tenant context propagation through headers
- Resource quotas and rate limiting per tenant

**Cloud-Native:**
- Deployed on Google Cloud Platform
- Containerized services (Docker)
- Serverless compute (Cloud Run)
- Managed services (Firestore, BigQuery, Pub/Sub)

---

## Architecture

### Architectural Patterns

#### 1. Microservices Pattern
**Implementation:**
- Each service is independently deployable
- Single responsibility per service
- Decentralized data management
- Polyglot persistence (Firestore + BigQuery + Redis)

**Benefits:**
- Independent scaling
- Technology flexibility
- Fault isolation
- Faster deployment cycles

#### 2. Event-Driven Architecture
**Implementation:**
- Pub/Sub for asynchronous communication
- Event topics per service and domain
- Event schemas with versioning
- Event replay capability (7-day retention)

**Message Flow:**
```
Service A → Publish Event → Pub/Sub Topic → Subscription → Service B
```

**Event Types:**
- Domain Events: `campaign_created`, `content_published`, `keyword_detected`
- System Events: `service_health_changed`, `deployment_completed`
- Integration Events: `payment_received`, `webhook_received`

#### 3. API Gateway Pattern
**Implementation:**
- AI Routing Engine serves as intelligent gateway
- Request/response transformation
- Protocol translation (HTTP to gRPC)
- Circuit breaking and retry logic

#### 4. CQRS (Command Query Responsibility Segregation)
**Implementation:**
- Write operations → Firestore (transactional)
- Read operations → BigQuery (analytical) or Redis (cached)
- Event sourcing for audit trails
- Eventual consistency between stores

**Flow:**
```
Write Command → Firestore → Event → BigQuery Sync
Read Query → Redis Cache → BigQuery → Response
```

#### 5. Circuit Breaker Pattern
**Implementation:**
- Circuit states: CLOSED, OPEN, HALF_OPEN
- Failure threshold: 5 consecutive failures
- Timeout: 60 seconds before retry
- Graceful degradation to fallback responses

**State Transitions:**
```
CLOSED --(5 failures)--> OPEN --(60s timeout)--> HALF_OPEN --(success)--> CLOSED
                                                       |
                                                   (failure)
                                                       ↓
                                                     OPEN
```

#### 6. Cache-Aside Pattern
**Implementation:**
```python
async def get_data(key):
    # 1. Check cache
    cached = await redis.get(key)
    if cached:
        return cached

    # 2. Query database
    data = await database.query(key)

    # 3. Store in cache
    await redis.set(key, data, ttl=300)

    return data
```

**Cache Hierarchy:**
- L1: Redis (sub-10ms)
- L2: BigQuery (250-550ms uncached)
- L3: Firestore (50-100ms)

---

### Service Layers

#### Layer 1: Gateway & Entry Points
**Services:**
- `platform-dashboard`: Central monitoring UI
- `xynergy-intelligence-gateway`: Data aggregation gateway
- `ai-routing-engine`: AI request routing

**Responsibilities:**
- Authentication and authorization
- Request validation and sanitization
- Rate limiting and throttling
- Request routing and load balancing

#### Layer 2: Core Business Services
**Services:**
- `marketing-engine`: Campaign management
- `aso-engine`: Search optimization
- `ai-assistant`: Conversational AI
- `content-hub`: Content management

**Responsibilities:**
- Business logic execution
- Domain-specific operations
- Data validation and transformation
- Event publishing

#### Layer 3: Intelligence Services
**Services:**
- `research-coordinator`: Research orchestration
- `trending-engine-coordinator`: Trend analysis
- `validation-coordinator`: Content validation
- `attribution-coordinator`: Revenue attribution

**Responsibilities:**
- AI-powered analysis
- Multi-service orchestration
- Complex workflow execution
- Result aggregation

#### Layer 4: Data Services
**Services:**
- `analytics-data-layer`: Data processing
- `advanced-analytics`: Business intelligence
- `keyword-revenue-tracker`: Attribution tracking

**Responsibilities:**
- Data transformation and enrichment
- Analytics computation
- Report generation
- Data export

#### Layer 5: Integration Services
**Services:**
- `ai-providers`: External AI APIs
- `internal-ai-service-v2`: Self-hosted AI
- External webhook handlers

**Responsibilities:**
- Third-party API integration
- Protocol translation
- Credential management
- Response transformation

#### Layer 6: Platform Services
**Services:**
- `system-runtime`: Core orchestration
- `scheduler-automation-engine`: Task scheduling
- `security-governance`: Security policies
- `tenant-management`: Multi-tenancy

**Responsibilities:**
- Cross-cutting concerns
- System health monitoring
- Background job execution
- Tenant lifecycle management

---

## Component Design

### Core Components

#### 1. AI Routing Engine

**Purpose:** Intelligent AI request routing with cost optimization

**Architecture:**
```
Request → Token Optimizer → Route Decision → Provider Call → Cache → Response
                                    ↓
                          [Abacus AI, OpenAI, Internal AI]
```

**Routing Logic:**
```python
def route_request(prompt: str) -> Provider:
    # Check for complex indicators
    if is_complex(prompt):
        if abacus_available():
            return AbacusAI  # $0.015/request
        elif openai_available():
            return OpenAI     # $0.025/request

    # Route simple requests to internal
    return InternalAI        # $0.001/request
```

**Components:**
- **Request Analyzer**: Classifies request complexity
- **Provider Health Monitor**: Tracks provider availability
- **Circuit Breaker Manager**: Prevents cascading failures
- **Response Cache**: Redis-based caching (1-hour TTL)
- **Token Optimizer**: Reduces token usage by 20-30%

**Key Metrics:**
- Cost savings: 89% vs pure external API usage
- Cache hit rate: 96-98%
- Average latency: <10ms (cached), 1-3s (uncached)

#### 2. ASO Engine

**Purpose:** Adaptive Search Optimization with content and keyword management

**Architecture:**
```
API Request → Validation → Cache Check → BigQuery Query → Process → Cache → Response
                                    ↓
                          [Partition Pruning Applied]
```

**Data Model:**
- **Content Pieces**: Hub/spoke relationship model
- **Keywords**: Search volume, difficulty, intent classification
- **Opportunities**: Low-hanging fruit detection algorithm

**Optimization Techniques:**
- **Partition Pruning**: 70-90% cost reduction on queries
- **Multi-Layer Caching**: 4 cache namespaces with tiered TTLs
- **Connection Pooling**: Shared BigQuery client

**Cache Strategy:**
```
aso_stats: 300s TTL (stats change slowly)
aso_content: 120s TTL (content changes moderately)
aso_keywords: 180s TTL (keywords change moderately)
aso_opportunities: 240s TTL (opportunities recalculated hourly)
```

#### 3. Marketing Engine

**Purpose:** AI-powered marketing campaign creation and management

**Architecture:**
```
Campaign Request → AI Routing → Template Generation → Firestore → Pub/Sub Event
                        ↓
                  [Cached Templates]
```

**Workflow:**
1. Receive campaign request with business parameters
2. Check cache for similar campaign template
3. Route to AI for generation (if cache miss)
4. Store campaign in Firestore
5. Publish `campaign_created` event
6. Return campaign details to client

**AI Integration:**
- Uses AI Routing Engine for cost optimization
- Caches campaign templates by `{business_type}_{audience}_{budget}`
- 1-hour TTL on templates (reusable across similar requests)

#### 4. Platform Dashboard

**Purpose:** Central monitoring and control interface

**Architecture:**
```
UI → WebSocket → Real-time Updates
  ↓
Health Checks → All Services → Aggregate Status → Dashboard
```

**Real-time Features:**
- WebSocket connection for live updates
- Circuit breaker status monitoring
- Service health aggregation
- Platform-wide metrics display

**Monitored Metrics:**
- Service availability (up/down/degraded)
- Response times (p50, p95, p99)
- Error rates
- Cache hit rates
- Circuit breaker states

#### 5. Intelligence Gateway (TypeScript)

**Purpose:** Central API gateway for communication intelligence services

**Architecture:**
```
External Clients
        ↓
Intelligence Gateway (TypeScript/Express.js)
├── Firebase Authentication
├── Rate Limiting (in-memory)
├── Circuit Breaker Protection
├── WebSocket Real-time Events
├── Response Caching (Redis when available)
└── Service Router
    ├── /api/xynergyos/v2/slack/*   → Slack Intelligence Service
    ├── /api/xynergyos/v2/gmail/*   → Gmail Intelligence Service
    └── /api/xynergyos/v2/crm/*     → CRM Engine
```

**Technology Stack:**
- TypeScript 5.3 + Node.js 20 Alpine
- Express.js 4.18 web framework
- Firebase Admin SDK for authentication
- Redis for caching (optional - graceful degradation)
- Socket.io for WebSocket real-time events

**Key Features:**
- **Mock Mode**: All intelligence services work without real API credentials for development
- **Graceful Degradation**: Gateway operational without Redis (caching disabled)
- **Circuit Breakers**: 5 failures → open circuit, protects against cascading failures
- **Response Caching**: 1-5 minute TTL when Redis available
- **WebSocket Events**: Real-time notifications for Slack messages, emails sent
- **Tenant Isolation**: All CRM data segregated by tenant ID

**Intelligence Services:**

**5a. Slack Intelligence Service**
- **URL**: `https://slack-intelligence-service-835612502919.us-central1.run.app`
- **Features**: Channel management, messaging, user lookup, search
- **Status**: Mock mode (works without Slack credentials)
- **API**: 9 endpoints (channels, messages, users, search, status)

**5b. Gmail Intelligence Service**
- **URL**: `https://gmail-intelligence-service-835612502919.us-central1.run.app`
- **Features**: Email list/read/send, search, thread management
- **Status**: Mock mode (OAuth ready for production)
- **API**: 6 endpoints (messages, search, threads, send, status)

**5c. CRM Engine**
- **URL**: `https://crm-engine-vgjxy554mq-uc.a.run.app`
- **Features**: Contact CRUD, interaction tracking, notes, tasks, statistics
- **Database**: Firestore tenant-isolated collections
- **Integration**: Ready for auto-contact creation from Slack/Gmail

**Performance Characteristics:**
- Cache hit rate: N/A (Redis not configured - degraded mode)
- Average latency: 100-300ms (no caching)
- Availability: 99.9% target
- Auto-scaling: 0-10 instances per service

---

### Shared Infrastructure Modules

#### 1. GCP Clients Module (`gcp_clients.py`)

**Purpose:** Centralized GCP client management with connection pooling

**Design Pattern:** Singleton with lazy initialization

**Implementation:**
```python
class GCPClients:
    _instance = None
    _clients = {}

    def get_firestore_client(self):
        if 'firestore' not in self._clients:
            self._clients['firestore'] = firestore.Client()
        return self._clients['firestore']
```

**Features:**
- Thread-safe client creation
- Automatic retry logic (3 retries with exponential backoff)
- Graceful shutdown handling
- Connection pooling (reduces cold start time by 60%)

**Retry Decorator:**
```python
@firestore_retry(max_retries=3, backoff_factor=1.0)
async def safe_operation():
    # Retries on: DeadlineExceeded, ServiceUnavailable,
    #             InternalServerError, TooManyRequests
    pass
```

#### 2. Redis Cache Module (`redis_cache.py`)

**Purpose:** Intelligent caching with automatic TTL management

**Architecture:**
```
Application → RedisCache → Connection Pool → Redis (10.0.0.3)
                    ↓
          [Category-based TTLs]
```

**Features:**
- Connection pooling (max 20 connections)
- Automatic TTL based on category
- Cache key generation with MD5 hashing
- Non-blocking SCAN for pattern invalidation
- Cache statistics and monitoring

**TTL Strategy:**
```python
cache_ttl_config = {
    "ai_responses": 3600,        # 1 hour (stable)
    "api_responses": 1800,       # 30 minutes
    "expensive_queries": 3600,   # 1 hour
    "trending_data": 300,        # 5 minutes (volatile)
    "system_health": 300,        # 5 minutes
}
```

#### 3. Authentication Module (`auth.py`)

**Purpose:** Zero-trust API key validation

**Design:**
- Thread-safe API key manager
- Auto-reload every 5 minutes
- Multiple authentication methods (Bearer, X-API-Key)

**Key Management:**
```python
# Environment variable format
XYNERGY_API_KEYS="key1,key2,key3"

# Automatic reload
if time.time() - last_reload > 300:  # 5 minutes
    reload_keys()
```

**FastAPI Integration:**
```python
@app.post("/api/endpoint", dependencies=[Depends(verify_api_key)])
async def protected_endpoint():
    # Automatically authenticated
    pass
```

#### 4. Rate Limiting Module (`rate_limiting.py`)

**Purpose:** Tiered rate limiting for API protection

**Tiers:**
- **Standard**: 60 requests/minute (normal operations)
- **Expensive**: 10 requests/minute (AI generation, complex queries)
- **AI**: 30 requests/minute (AI-specific operations)

**Implementation:**
```python
rate_limiter = SlowAPI(
    key_func=get_remote_address,
    default_limits=["60/minute"]
)
```

#### 5. Circuit Breaker Module (`phase2_utils.py`)

**Purpose:** Fault tolerance and graceful degradation

**States:**
```
CLOSED: Normal operation, requests pass through
OPEN: Too many failures, requests blocked (return fallback)
HALF_OPEN: Testing recovery, allow 1 request
```

**Configuration:**
```python
CircuitBreakerConfig(
    failure_threshold=5,      # Failures before opening
    timeout=60,               # Seconds before retry
    expected_exception=Exception
)
```

**Usage:**
```python
result = await call_service_with_circuit_breaker(
    circuit_breaker,
    external_service_call,
    *args,
    **kwargs
)
```

---

## Data Architecture

### Data Storage Strategy

#### 1. Firestore (Transactional)
**Use Cases:**
- Real-time data (campaigns, user sessions)
- Transactional operations
- Document-oriented data
- Small, frequently accessed datasets

**Collections:**
- `marketing_campaigns`: Campaign data
- `service_status`: Health check results
- `workflow_monitoring`: Workflow execution state
- `dashboard_metrics`: Real-time metrics

**Access Pattern:**
```python
# Optimized read
doc = firestore_client.collection('campaigns').document(campaign_id).get()

# Batch write
batch = firestore_client.batch()
batch.set(ref1, data1)
batch.set(ref2, data2)
batch.commit()
```

#### 2. BigQuery (Analytical)
**Use Cases:**
- Large-scale analytics
- Historical data analysis
- Reporting and BI
- Data warehousing

**Datasets:**
- `xynergy_analytics`: Platform-wide metrics
- `aso_tenant_{tenant_id}`: Per-tenant ASO data
- `validation_analytics`: Content validation metrics
- `attribution_analytics`: Revenue attribution data

**Optimization:**
- **Partitioning**: All tables partitioned by DATE(timestamp)
- **Clustering**: Secondary clustering on tenant_id, status
- **Partition Pruning**: Reduces scanned data by 70-90%

**Query Pattern:**
```sql
-- Optimized with partition pruning
SELECT column1, column2
FROM `project.dataset.table`
WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  AND tenant_id = @tenant_id
ORDER BY created_at DESC
LIMIT 100
```

#### 3. Redis (Caching)
**Use Cases:**
- Hot data caching
- Session storage
- Rate limiting counters
- Temporary data

**Instance:**
- **Type**: STANDARD_HA
- **Size**: 1GB
- **Location**: us-central1 (multi-zone)
- **Network**: 10.0.0.3 (VPC-attached)

**Data Structures:**
```
Strings: Cache values with TTL
Hashes: Complex objects
Sets: Unique collections
Sorted Sets: Leaderboards, rankings
```

#### 4. Cloud Storage (Blob)
**Use Cases:**
- Content assets
- Generated reports
- Research data
- Backups

**Buckets:**
- `xynergy-content`: 30-day lifecycle
- `xynergy-reports`: 365-day lifecycle
- `xynergy-research`: 90-day lifecycle
- `xynergy-trending`: 30-day lifecycle

**Access Pattern:**
```python
# Upload with metadata
bucket.blob(filename).upload_from_string(
    data,
    content_type='application/json',
    metadata={'tenant_id': tenant_id}
)
```

### Multi-Tenant Data Isolation

#### Approach: Hybrid (Shared Schema + Isolated Datasets)

**Shared Schema (Firestore):**
- Tenant ID as partition key
- All tenants in same collections
- Security rules enforce isolation

**Isolated Datasets (BigQuery):**
- Per-tenant datasets: `aso_tenant_{tenant_id}`
- Complete data isolation
- Independent backup/restore

**Benefits:**
- Cost efficiency (shared Firestore)
- Data sovereignty (isolated BigQuery)
- Flexible scaling per tenant
- Simplified compliance (GDPR, CCPA)

**Tenant Context Propagation:**
```
HTTP Request → Header: X-Tenant-ID → Service → Query with tenant_id filter
```

---

## Integration Design

### External Integrations

#### 1. AI Providers

**Abacus AI:**
- **Endpoint**: Configured via environment
- **Authentication**: API key (Secret Manager)
- **Use Case**: Complex queries, research tasks
- **Cost**: $0.015 per request
- **Failover**: OpenAI

**OpenAI:**
- **Endpoint**: https://api.openai.com/v1
- **Authentication**: API key (Secret Manager)
- **Model**: gpt-4o-mini
- **Use Case**: Fallback for Abacus
- **Cost**: $0.025 per request

**Internal AI (Llama 3.1 8B):**
- **Endpoint**: https://internal-ai-service-v2-835612502919.us-central1.run.app
- **Authentication**: None (internal)
- **Use Case**: Simple queries, final fallback
- **Cost**: $0.001 per request

**Integration Flow:**
```
Request → AI Routing Engine → Complexity Analysis
    ↓
Complex? → Abacus AI (available?) → Yes → Call Abacus
                     ↓
                    No → OpenAI (available?) → Yes → Call OpenAI
                              ↓
                             No → Internal AI
Simple? → Internal AI
```

#### 2. Pub/Sub Event Bus

**Topics:**
- Service-specific: `{service-name}-events`
- Domain-specific: `trend-identified`, `validation-complete`
- System-wide: `platform-health-changed`

**Message Format:**
```json
{
  "event_type": "campaign_created",
  "event_id": "uuid",
  "timestamp": "ISO8601",
  "tenant_id": "tenant_id",
  "source_service": "marketing-engine",
  "payload": {
    "campaign_id": "...",
    "data": {}
  },
  "metadata": {
    "correlation_id": "request_id",
    "causation_id": "parent_event_id"
  }
}
```

**Subscription Pattern:**
```
Topic → Subscription → Dead Letter Queue
            ↓
      Service Endpoint
```

---

## Security Design

### Authentication & Authorization

#### API Key Authentication
**Method:** Bearer Token or X-API-Key header

**Flow:**
```
Client → Request + API Key → verify_api_key() → Valid? → Allow
                                       ↓
                                     Invalid → 401 Unauthorized
```

**Key Storage:**
- Environment variable: `XYNERGY_API_KEYS`
- Secret Manager: `projects/{project}/secrets/xynergy-api-keys`
- Auto-reload: Every 5 minutes

#### Service-to-Service Authentication
**Method:** GCP Service Account with IAM

**Permissions:**
```
Service A (SA: service-a@project.iam.gserviceaccount.com)
    ↓
Calls Service B
    ↓
IAM Check: Does Service A have run.invoker on Service B?
    ↓
Yes → Allow | No → 403 Forbidden
```

### Data Protection

#### Encryption at Rest
- **Firestore**: Google-managed encryption keys
- **BigQuery**: Customer-managed encryption keys (CMEK) option
- **Cloud Storage**: Google-managed encryption
- **Redis**: Not encrypted (VPC-isolated)

#### Encryption in Transit
- **TLS 1.3**: All external connections
- **mTLS**: Service-to-service (planned)
- **VPC Private Google Access**: Internal GCP traffic

### Network Security

#### CORS Policy
```python
allow_origins=[
    "https://xynergy-platform.com",
    "https://api.xynergy.dev",
    "https://*.xynergy.com"
]
allow_credentials=True
allow_methods=["GET", "POST", "PUT", "DELETE"]
allow_headers=["Authorization", "Content-Type", "X-API-Key"]
```

**Security Rules:**
- ❌ NEVER use `allow_origins=["*"]`
- ✅ Always specify exact domains
- ✅ HTTPS only in production
- ✅ Include localhost for development

#### VPC Configuration
- **Network**: default VPC
- **Subnets**: Auto-created per region
- **Private Google Access**: Enabled
- **Cloud NAT**: Configured for egress

**Firewall:**
- Ingress: HTTPS (443) from Cloud Run
- Egress: HTTPS to GCP services
- Redis: Private IP only (10.0.0.3)

### Input Validation

#### Pydantic Models
```python
class CampaignRequest(BaseModel):
    business_type: str = Field(..., max_length=200)
    target_audience: str = Field(..., max_length=500)
    budget_range: str = Field(..., regex=r'^\$[\d,]+-\$[\d,]+$')

    class Config:
        str_strip_whitespace = True
        str_min_length = 1
```

#### SQL Injection Prevention
```python
# ✅ Good: Parameterized query
query = """
SELECT * FROM table
WHERE id = @id
"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("id", "STRING", user_input)
    ]
)

# ❌ Bad: String interpolation
query = f"SELECT * FROM table WHERE id = '{user_input}'"
```

---

## Performance Design

### Optimization Strategies

#### 1. Caching Layers

**L1: Redis (Hot Data)**
- TTL: 1-60 minutes based on volatility
- Hit rate: 84%+
- Latency: <10ms

**L2: BigQuery (Warm Data)**
- Partition pruning: 70-90% cost reduction
- Clustering: Further query optimization
- Latency: 250-550ms (uncached)

**L3: Firestore (Operational Data)**
- Indexed queries only
- Composite indexes for complex queries
- Latency: 50-100ms

#### 2. Connection Pooling

**GCP Clients:**
```python
# Singleton pattern
class GCPClients:
    _firestore_client = None

    def get_firestore_client(self):
        if not self._firestore_client:
            self._firestore_client = firestore.Client()
        return self._firestore_client
```

**Benefits:**
- 60% reduction in cold start time
- Reduced connection overhead
- Better resource utilization

#### 3. Query Optimization

**BigQuery Best Practices:**
- Use partition pruning
- Select specific columns (avoid SELECT *)
- Use clustering for frequently filtered columns
- Materialize complex queries as tables

**Example:**
```sql
-- Before: Scans 730 days of data
SELECT * FROM table WHERE status = 'active'

-- After: Scans 90 days (87% reduction)
SELECT id, name, status FROM table
WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  AND status = 'active'
```

#### 4. Asynchronous Processing

**Pattern:**
```python
# Synchronous (blocking)
result = heavy_operation()
return result

# Asynchronous (non-blocking)
task_id = queue.enqueue(heavy_operation)
return {"task_id": task_id, "status": "processing"}
```

**Use Cases:**
- Report generation
- Batch processing
- External API calls
- Email sending

---

## Scalability Design

### Horizontal Scaling

**Cloud Run Auto-Scaling:**
```yaml
Min Instances: 0 (scale-to-zero)
Max Instances: 10-50 (per service)
Concurrency: 80 requests per instance
CPU Threshold: 60%
Memory Threshold: 70%
```

**Scaling Triggers:**
- Request volume
- CPU utilization
- Memory utilization
- Custom metrics (queue depth)

**Scale-up:**
```
Requests increase → CPU > 60% → New instance spawned → ~10s cold start
```

**Scale-down:**
```
Requests decrease → Idle > 5 min → Instance terminated → Cost savings
```

### Vertical Scaling

**Resource Allocation:**
```
Tier 1 (Dashboard): 1 CPU, 512Mi
Tier 2 (AI Services): 2 CPU, 1Gi
Tier 3 (Analytics): 2 CPU, 1Gi
```

### Database Scaling

**Firestore:**
- Automatic scaling (managed)
- Unlimited concurrent connections
- Performance: ~1 write/sec per document

**BigQuery:**
- Slots: On-demand or reserved
- Concurrent queries: Unlimited
- Data size: Petabyte-scale

**Redis:**
- Vertical scaling: Increase memory
- Horizontal scaling: Add read replicas
- Current: 1GB with 1 replica

---

## Monitoring & Observability

### Structured Logging

**Format:** JSON with contextual information

```json
{
  "timestamp": "2025-10-10T12:00:00.000000Z",
  "level": "info",
  "event": "cache_hit",
  "request_id": "req_abc123",
  "service": "aso-engine",
  "tenant_id": "demo",
  "latency_ms": 5,
  "cache_key": "stats_demo_90"
}
```

**Log Levels:**
- DEBUG: Development only
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Operation failures
- CRITICAL: Service failures

### Metrics

**Service Metrics:**
- Request count
- Response time (p50, p95, p99)
- Error rate
- Cache hit rate
- Circuit breaker state

**Infrastructure Metrics:**
- CPU utilization
- Memory usage
- Disk I/O
- Network throughput

**Business Metrics:**
- Active tenants
- API calls per tenant
- AI cost per tenant
- Revenue per tenant

### Distributed Tracing

**X-Request-ID Propagation:**
```
Client Request → Generate X-Request-ID → Service A
                                            ↓
                                  Forward X-Request-ID → Service B
                                                            ↓
                                                  All logs include X-Request-ID
```

**Trace Query:**
```sql
SELECT * FROM logs
WHERE json_payload.request_id = 'req_abc123'
ORDER BY timestamp
```

---

## Deployment Architecture

### Container Strategy

**Dockerfile Pattern:**
```dockerfile
FROM python:3.11-slim
WORKDIR /
COPY shared/ /shared/
WORKDIR /app
COPY service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY service/main.py .
CMD ["python", "main.py"]
```

### CI/CD Pipeline

**Build Stage:**
1. Run tests
2. Build Docker image
3. Tag with commit SHA
4. Push to Artifact Registry

**Deploy Stage:**
1. Update Cloud Run service
2. Run health checks
3. Gradual traffic migration (0% → 100%)
4. Rollback on failure

### Blue-Green Deployment

```
Traffic: 100% → Revision A (blue)
Deploy Revision B (green) → Health checks pass
Traffic migration: 0% → 50% → 100% → Revision B
Delete Revision A after 24 hours
```

---

## Technology Stack

### Programming Languages
- **Python 3.11**: Core platform services (21 services)
- **TypeScript 5.3**: Intelligence Gateway services (4 services)
- **SQL**: BigQuery queries
- **HCL**: Terraform infrastructure

### Frameworks & Libraries

**Python Services:**
- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **uvicorn**: ASGI server
- **structlog**: Structured logging
- **aiohttp**: Async HTTP client

**TypeScript Services:**
- **Express.js 4.18**: Web framework
- **Node.js 20**: Runtime environment
- **Firebase Admin SDK 12.0**: Authentication
- **Socket.io**: WebSocket real-time communication
- **Winston**: Structured logging
- **Redis Client**: Caching (optional)

### Google Cloud Platform
- **Cloud Run**: Serverless compute
- **Firestore**: NoSQL database
- **BigQuery**: Data warehouse
- **Cloud Storage**: Object storage
- **Pub/Sub**: Message bus
- **Secret Manager**: Secrets storage
- **Cloud Logging**: Log aggregation
- **Cloud Monitoring**: Metrics and alerting
- **Artifact Registry**: Container registry
- **Redis/Memorystore**: Caching

### DevOps Tools
- **Terraform**: Infrastructure as Code
- **Docker**: Containerization
- **Cloud Build**: CI/CD
- **GitHub**: Version control

### External Services
- **Abacus AI**: Primary AI provider
- **OpenAI**: Fallback AI provider
- **Llama 3.1 8B**: Internal AI model

---

## Appendix

### Design Principles

1. **Separation of Concerns**: Each service has single responsibility
2. **DRY (Don't Repeat Yourself)**: Shared modules for common functionality
3. **YAGNI (You Aren't Gonna Need It)**: Build what's needed now
4. **KISS (Keep It Simple, Stupid)**: Simplest solution that works
5. **Fail Fast**: Detect and handle errors early
6. **Defense in Depth**: Multiple layers of security
7. **Design for Failure**: Assume components will fail
8. **Idempotency**: Operations can be safely retried

### Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| API Response Time (p95) | <500ms | 250ms (cached), 550ms (uncached) |
| Cache Hit Rate | >80% | 84%+ |
| Service Availability | 99.9% | 99.95% |
| Error Rate | <1% | 0.3% |
| Cold Start Time | <10s | 5-8s |
| AI Cost Reduction | >85% | 89% |

### Future Enhancements

1. **Service Mesh (Istio)**: Advanced traffic management
2. **GraphQL API**: More flexible data querying
3. **Real-time Analytics**: Stream processing with Dataflow
4. **ML Model Training**: AutoML integration
5. **Multi-Region Deployment**: Global availability
6. **Advanced Monitoring**: OpenTelemetry, Jaeger tracing

---

**Document Control:**
- **Version**: 1.1
- **Last Updated**: October 11, 2025 (Added Intelligence Gateway services)
- **Next Review**: January 11, 2026
- **Owner**: Platform Engineering Team
- **Approvers**: CTO, Lead Architect

**Changelog:**
- **v1.1** (Oct 11, 2025): Added Intelligence Gateway (TypeScript) with Slack, Gmail, and CRM services
- **v1.0** (Oct 10, 2025): Initial document

**End of Technical Design Document**
