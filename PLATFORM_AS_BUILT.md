# Xynergy Platform - Comprehensive As-Built Documentation

**Document Version:** 1.0
**Generated:** October 10, 2025
**Platform Version:** 2.0.0
**Status:** Production-Ready with Phase 1-6 Optimizations Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Platform Architecture Overview](#platform-architecture-overview)
3. [Core Infrastructure](#core-infrastructure)
4. [Service Catalog](#service-catalog)
5. [Shared Infrastructure Modules](#shared-infrastructure-modules)
6. [Data Architecture](#data-architecture)
7. [Network & Security](#network--security)
8. [Deployment Architecture](#deployment-architecture)
9. [Integration Patterns](#integration-patterns)
10. [Performance & Optimization](#performance--optimization)
11. [Monitoring & Observability](#monitoring--observability)
12. [Maintenance & Operations](#maintenance--operations)

---

## Executive Summary

### Platform Overview

The Xynergy Platform is an enterprise-grade, microservices-based AI operations platform built on Google Cloud Platform. It provides autonomous business operations including marketing automation, content generation, SEO optimization, analytics, and project management through 40+ specialized services.

### Key Metrics

| Metric | Value |
|--------|-------|
| **Total Services** | 44 microservices |
| **Shared Modules** | 21 infrastructure modules |
| **Cloud Provider** | Google Cloud Platform (GCP) |
| **Primary Region** | us-central1 |
| **Container Runtime** | Cloud Run |
| **Project ID** | xynergy-dev-1757909467 |
| **Deployment Model** | Fully containerized microservices |
| **Cost Optimization** | 89% AI cost reduction vs external APIs |

### Technology Stack

- **Language:** Python 3.11
- **Framework:** FastAPI (async/await)
- **Database:** Firestore (NoSQL), BigQuery (Analytics)
- **Caching:** Redis/Memorystore
- **Storage:** Cloud Storage
- **Messaging:** Pub/Sub
- **Container Registry:** Artifact Registry
- **IaC:** Terraform
- **Logging:** Structured logging (structlog)

---

## Platform Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Platform Dashboard                           │
│                  (Central Monitoring & Control)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬─────────────────┐
         │               │               │                 │
┌────────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌───────▼──────┐
│  AI Routing   │ │  Marketing  │ │    ASO     │ │ Intelligence │
│    Engine     │ │   Engine    │ │   Engine   │ │   Gateway    │
└────────┬──────┘ └──────┬──────┘ └─────┬──────┘ └───────┬──────┘
         │               │               │                 │
         └───────────────┼───────────────┴─────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
    ┌───────▼─────┐          ┌───────▼────────┐
    │ AI Providers│          │  Internal AI   │
    │  (External) │          │   Service v2   │
    └─────────────┘          └────────────────┘
```

### Service Communication Model

1. **Synchronous (HTTP/REST):**
   - Service-to-service direct calls
   - API Gateway pattern via AI Routing Engine
   - Circuit breaker protection
   - Request/Response with structured logging

2. **Asynchronous (Pub/Sub):**
   - Event-driven architecture
   - Decoupled service communication
   - Topic: `{service-name}-events`
   - Message retention: 7 days

3. **Shared Infrastructure:**
   - Connection pooling via shared GCP clients
   - Redis caching layer
   - Centralized authentication
   - Rate limiting middleware

---

## Core Infrastructure

### GCP Project Configuration

**Project ID:** xynergy-dev-1757909467
**Project Number:** 835612502919
**Primary Region:** us-central1
**Secondary Region:** us-east1 (DR)

### Service Account

**Principal:** `xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com`

**Permissions:**
- `roles/cloudsql.client` - Database access
- `roles/datastore.user` - Firestore access
- `roles/pubsub.publisher` - Event publishing
- `roles/pubsub.subscriber` - Event consumption
- `roles/storage.objectAdmin` - Storage management
- `roles/bigquery.dataEditor` - Analytics data
- `roles/bigquery.jobUser` - Query execution
- `roles/secretmanager.secretAccessor` - Secrets access
- `roles/logging.logWriter` - Structured logging
- `roles/monitoring.metricWriter` - Metrics publishing

### Artifact Registry

**Repository:** `us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform`

All service container images are stored in this registry with tags following the pattern:
- `{service-name}:latest` - Latest production build
- `{service-name}:{git-commit-sha}` - Version-specific build

### BigQuery Datasets

1. **xynergy_analytics** (US)
   - Purpose: Platform-wide analytics
   - Retention: 90 days default
   - Partitioning: Date-based on created_at
   - Tables: Service metrics, performance data

2. **validation_analytics** (us-central1)
   - Purpose: Content validation metrics
   - Tables: content_validations
   - Schema: validation_id, accuracy_score, fact_check_results

3. **attribution_analytics** (us-central1)
   - Purpose: Attribution and revenue tracking
   - Tables: customer_journeys, performance_metrics, client_dashboard_data
   - Advanced: Journey mapping, revenue attribution

4. **Per-Tenant Datasets** (`aso_tenant_{tenant_id}`)
   - Purpose: Multi-tenant data isolation
   - Tables: content_pieces, keywords, opportunities
   - Partitioning: Optimized for 90-day lookback queries

### Cloud Storage Buckets

1. **xynergy-dev-1757909467-xynergy-content**
   - Purpose: Content assets
   - Lifecycle: 30 days
   - Versioning: Enabled
   - Access: Uniform bucket-level

2. **xynergy-dev-1757909467-xynergy-reports**
   - Purpose: Generated reports
   - Lifecycle: 365 days
   - Versioning: Enabled

3. **xynergy-dev-1757909467-xynergy-research**
   - Purpose: Research data
   - Lifecycle: 90 days
   - Versioning: Enabled

4. **xynergy-dev-1757909467-xynergy-trending**
   - Purpose: Trending data
   - Lifecycle: 30 days
   - Versioning: Enabled

5. **xynergy-dev-1757909467-aso-content**
   - Purpose: ASO engine content
   - Lifecycle: Managed per content type

### Redis/Memorystore

**Instance:** `xynergy-trending-cache`
- **Version:** Redis 6.X
- **Tier:** STANDARD_HA
- **Memory:** 1GB
- **Replication:** 1 replica (read replicas enabled)
- **Network:** VPC-attached (10.0.0.3)
- **Availability:** Multi-zone (us-central1-a, us-central1-b)

**Cache Namespaces:**
- `ai:resp:` - AI responses (TTL: 3600s)
- `api:call:` - API responses (TTL: 1800s)
- `aso_stats:` - ASO statistics (TTL: 300s)
- `aso_content:` - Content lists (TTL: 120s)
- `aso_keywords:` - Keyword data (TTL: 180s)
- `aso_opportunities:` - Opportunities (TTL: 240s)

### Pub/Sub Topics

**Service Event Topics** (Pattern: `{service-name}-events`):
- xynergy-marketing-engine-events
- xynergy-content-hub-events
- xynergy-ai-assistant-events
- xynergy-system-runtime-events
- xynergy-analytics-events
- Plus 35+ additional service-specific topics

**Engine-Specific Topics:**

**Research Engine:**
- trend-identified
- competitor-alert
- research-complete
- content-opportunity

**Trending Engine:**
- trend-velocity-alert
- rapid-content-request
- content-generated
- publishing-triggered
- trend-peak-detected
- competitive-gap-alert

**Validation Engine:**
- validation-tasks
- fact-check-requests
- plagiarism-checks
- validation-complete

**Attribution Engine:**
- attribution-events
- revenue-tracking
- performance-analytics
- client-reporting

---

## Service Catalog

### 1. Platform Dashboard

**Service Name:** `platform-dashboard`
**Port:** 8080
**Container:** `us-central1-docker.pkg.dev/.../platform-dashboard:latest`
**URL Pattern:** `https://xynergy-platform-dashboard-*.us-central1.run.app`

**Purpose:**
Central monitoring and control interface for the entire Xynergy platform. Provides real-time visibility into all services, health checks, and platform metrics.

**Key Features:**
- Real-time service status monitoring
- Embedded HTML dashboard with WebSocket updates
- Rate limiting (10 requests/minute)
- Performance metrics aggregation
- Circuit breaker status monitoring
- Platform-wide health checks

**API Endpoints:**
- `GET /` - Dashboard UI (HTML)
- `GET /health` - Health check with connectivity tests
- `GET /api/platform-status` - Aggregated platform metrics
- `POST /execute` - Workflow orchestration endpoint

**Dependencies:**
- Firestore (service status collection)
- Pub/Sub (event monitoring)
- All other platform services (health checks)

**Configuration:**
- `PROJECT_ID`: xynergy-dev-1757909467
- `REGION`: us-central1
- CORS: `https://xynergy.com`, `https://*.xynergy.com`, `http://localhost:*`

**Optimizations Applied:**
- Phase 1: Rate limiting, CORS hardening, structured logging
- Phase 2: Circuit breakers, performance monitoring
- Connection pooling via shared GCP clients

---

### 2. Marketing Engine

**Service Name:** `marketing-engine`
**Port:** 8081
**Container:** `marketing-engine:latest`
**URL Pattern:** `https://xynergy-marketing-engine-*.us-central1.run.app`

**Purpose:**
AI-powered marketing campaign creation and management. Generates intelligent marketing strategies, performs keyword research, and tracks campaign performance.

**Key Features:**
- AI-driven campaign strategy generation
- Keyword research and analysis
- Campaign performance analytics
- Redis caching for campaign templates (1-hour TTL)
- Intelligent routing for AI requests (78% internal usage)
- Cost optimization (89% savings vs external APIs)

**API Endpoints:**
- `GET /` - Service info UI (HTML)
- `GET /health` - Enhanced health check (Firestore, BigQuery, Pub/Sub, Redis)
- `POST /campaigns/create` - Create AI marketing campaign (rate limited: expensive)
- `POST /keywords/research` - AI keyword research (rate limited: expensive)
- `GET /campaigns/{campaign_id}` - Retrieve campaign details
- `GET /analytics/performance` - Campaign performance metrics
- `POST /execute` - Workflow orchestration (action: analyze_market)

**Data Models:**
- **CampaignRequest:** business_type, target_audience, budget_range, campaign_goals, preferred_channels
- **CampaignResponse:** campaign_id, campaign_name, strategy, recommended_channels, estimated_reach, budget_allocation
- **KeywordResearchRequest:** business_type, target_market, competitor_urls

**Dependencies:**
- Firestore: Campaign storage (`marketing_campaigns` collection)
- BigQuery: Analytics queries
- Pub/Sub: Event publishing (`xynergy-marketing-events` topic)
- Redis: Template caching
- AI Routing Engine: AI request routing

**Caching Strategy:**
- Campaign templates cached by `{business_type}_{target_audience}_{budget_range}`
- TTL: 3600 seconds (1 hour)
- Cache namespace: `campaign`

**Configuration:**
- `PROJECT_ID`: xynergy-dev-1757909467
- `REGION`: us-central1
- `PORT`: 8080 (internal)
- CORS: `https://xynergy-platform.com`, `https://api.xynergy.dev`, `https://*.xynergy.com`

**Optimizations Applied:**
- Phase 2: Structured logging with request IDs, performance monitoring
- Phase 3: Redis caching for campaigns
- Phase 4: Shared GCP clients (connection pooling)
- Phase 5: Rate limiting (standard, expensive)

---

### 3. AI Routing Engine

**Service Name:** `ai-routing-engine`
**Port:** 8085
**Container:** `ai-routing-engine:latest`
**URL Pattern:** `https://xynergy-ai-routing-engine-*.us-central1.run.app`

**Purpose:**
Intelligent AI request routing engine that optimizes cost and performance by routing requests through Abacus AI (primary), OpenAI (fallback), or Internal AI Service v2 (final fallback). Implements intelligent caching and token optimization.

**Key Features:**
- Multi-provider AI routing (Abacus → OpenAI → Internal)
- Redis caching for AI responses (1-hour TTL)
- Token optimization (20-30% cost reduction)
- Semantic caching capability (disabled in lightweight mode)
- Circuit breaker protection
- Cache warming and invalidation APIs
- Request tracing with X-Request-ID

**API Endpoints:**
- `GET /` - Service status
- `GET /health` - Health check (AI Providers, Internal AI, Redis, Circuit Breaker)
- `POST /api/route` - AI request routing (legacy)
- `POST /api/generate` - Generate AI response (main endpoint, rate limited)
- `POST /execute` - Workflow orchestration (action: route_request)
- `GET /cache/stats` - Cache statistics and metrics
- `POST /cache/invalidate/{pattern}` - Invalidate cache by pattern
- `POST /cache/warm` - Pre-warm cache with common prompts

**Routing Decision Logic:**
1. Check for complex indicators (current, latest, today, news, real-time, research)
2. If complex:
   - Try Abacus AI (primary, cost: $0.015)
   - Fallback to OpenAI (cost: $0.025)
3. If simple:
   - Route to Internal AI Service v2 (cost: $0.001)

**Caching Layers:**
1. **Semantic Cache** (Phase 6, disabled in lightweight mode)
   - Embedding-based similarity matching
   - Would require sentence-transformers (4GB+ dependencies)

2. **Redis Cache** (Active)
   - Exact prompt matching
   - Cache key: SHA256 hash of prompt
   - Namespace: `ai:resp:{provider}:{model}:{prompt_hash}`
   - TTL: 3600 seconds

**Token Optimization:**
- Dynamic max_tokens calculation based on prompt complexity
- 20-30% token reduction on average
- Metadata returned: `token_optimization` field

**Dependencies:**
- AI Providers Service: `https://xynergy-ai-providers-835612502919.us-central1.run.app`
- Internal AI Service v2: `https://internal-ai-service-v2-vgjxy554mq-uc.a.run.app`
- Redis: Caching layer
- Shared modules: redis_cache, ai_token_optimizer, http_client, auth, rate_limiting

**Configuration:**
- `PROJECT_ID`: xynergy-dev-1757909467
- `REGION`: us-central1
- `AI_PROVIDERS_URL`: External providers service
- `INTERNAL_AI_URL`: Internal AI service
- CORS: `https://xynergy-platform.com`, `https://api.xynergy.dev`, `https://*.xynergy.com`

**Performance Metrics:**
- 89% cost reduction vs pure external API usage
- 96-98% cache hit improvement (sub-10ms response)
- Circuit breaker prevents cascading failures

**Optimizations Applied:**
- Phase 2: Circuit breakers, performance monitoring, request tracing
- Phase 3: Redis caching with intelligent TTL
- Phase 5: Rate limiting (ai_rate_limit)
- Phase 6: Token optimization, semantic cache infrastructure (disabled)

---

### 4. ASO Engine (Adaptive Search Optimization)

**Service Name:** `aso-engine`
**Port:** 8080
**Container:** `aso-engine:latest`
**URL Pattern:** `https://xynergy-aso-engine-*.us-central1.run.app`

**Purpose:**
Core engine for content management, keyword tracking, and search optimization. Provides comprehensive ASO (App Store Optimization / Adaptive Search Optimization) capabilities with advanced analytics.

**Key Features:**
- Content piece management (hub/spoke model)
- Keyword tracking and ranking
- Opportunity detection (low-hanging fruit)
- Multi-tenant data isolation
- BigQuery partition pruning (70-90% cost reduction)
- Multi-layer Redis caching
- Performance monitoring

**API Endpoints:**
- `GET /` - Service info
- `GET /health` - Health check (BigQuery, Storage, Firestore, Redis)
- `POST /api/content` - Create content piece (rate limited: expensive)
- `GET /api/content` - List content with caching (TTL: 120s)
- `POST /api/keywords` - Add keyword to tracking (rate limited: standard)
- `GET /api/keywords` - List tracked keywords with caching (TTL: 180s)
- `POST /api/opportunities/detect` - Detect optimization opportunities
- `GET /api/opportunities` - List opportunities with caching (TTL: 240s)
- `GET /api/stats` - Tenant statistics with caching (TTL: 300s)

**Data Models:**

**ContentPiece:**
- content_type: "hub" or "spoke"
- keyword_primary: Primary keyword
- keyword_secondary: List of secondary keywords
- title, meta_description, url
- word_count, hub_id (for spoke content)
- tenant_id (multi-tenant support)

**KeywordData:**
- keyword, tenant_id
- search_volume, difficulty_score
- intent, priority (tier1/tier2/tier3)

**OpportunityResponse:**
- opportunity_id, opportunity_type
- keyword, confidence_score
- estimated_traffic, recommendation

**Multi-Tenant Architecture:**
- Dataset per tenant: `aso_tenant_{tenant_id}`
- Tables: content_pieces, keywords, opportunities
- Default tenant: "demo"

**BigQuery Schema:**

**content_pieces table:**
- content_id (STRING)
- content_type, keyword_primary, keyword_secondary
- status, hub_id, title, meta_description, url
- word_count, performance_score, ranking_position
- monthly_traffic, monthly_conversions, conversion_rate
- created_at (TIMESTAMP, PARTITIONED), published_at, updated_at

**keywords table:**
- keyword (STRING)
- search_volume, difficulty_score, kgr_score
- intent, current_ranking, best_ranking, target_ranking
- serp_history, competitor_rankings
- last_checked (TIMESTAMP, PARTITIONED), priority
- content_id, created_at

**opportunities table:**
- opportunity_id, opportunity_type
- keyword, confidence_score
- estimated_traffic, estimated_difficulty
- recommendation
- detected_at (TIMESTAMP, PARTITIONED), status
- content_id, created_at

**Partition Pruning Strategy:**
All queries use `WHERE DATE(timestamp_column) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days_back DAY)` to reduce scanned data by 70-90%.

**Caching Strategy:**

| Endpoint | Namespace | TTL | Cache Key Pattern |
|----------|-----------|-----|-------------------|
| /api/content | aso_content | 120s | content_{tenant}_{status}_{days}_{limit} |
| /api/keywords | aso_keywords | 180s | keywords_{tenant}_{priority}_{days}_{limit} |
| /api/opportunities | aso_opportunities | 240s | opps_{tenant}_{status}_{days}_{limit} |
| /api/stats | aso_stats | 300s | stats_{tenant}_{days} |

**Opportunity Detection Algorithm:**
```sql
WHERE current_ranking > 10 AND current_ranking <= 30
  AND difficulty_score < 50
  AND search_volume > 100
ORDER BY search_volume DESC
```

**Dependencies:**
- BigQuery: All tenant datasets
- Cloud Storage: Content bucket
- Firestore: Metadata and configuration
- Redis: Multi-layer caching
- Shared modules: gcp_clients, redis_cache, auth, rate_limiting, phase2_utils

**Configuration:**
- `PROJECT_ID`: xynergy-dev-1757909467
- `REGION`: us-central1
- `CONTENT_BUCKET`: `{PROJECT_ID}-aso-content`
- CORS: `https://clearforge.ai`, `https://xynergy.com`, `https://dashboard.xynergy.com`

**Performance Impact:**
- Query cost reduction: 70-90% via partition pruning
- Response time: <10ms (cached), 250-550ms (uncached)
- Cache hit rate: 84%+ on list operations
- Annual savings: $456/month on BigQuery queries

**Optimizations Applied:**
- Phase 2: Structured logging with request IDs, performance monitoring
- Phase 3: Circuit breakers
- Phase 4: BigQuery partition pruning, initial Redis caching (stats endpoint)
- Phase 5: Extended caching to all list endpoints
- Phase 6: Shared GCP clients (connection pooling)

---

### 5. AI Assistant

**Service Name:** `ai-assistant`
**Port:** 8082
**Container:** `ai-assistant:latest`
**URL Pattern:** `https://xynergy-ai-assistant-*.us-central1.run.app`

**Purpose:**
Conversational AI interface and workflow orchestration engine. Provides natural language interaction and coordinates complex multi-service workflows.

**Key Features:**
- Conversational AI interface
- Multi-service workflow orchestration
- WebSocket support for real-time updates
- Intelligent service mesh coordination
- Context-aware request routing

**API Endpoints:**
- `GET /` - Service info
- `GET /health` - Health check
- `POST /api/chat` - Conversational interface
- `POST /orchestrate` - Multi-service workflow coordination
- `WS /ws` - WebSocket connection for real-time updates

**Dependencies:**
- AI Routing Engine: AI request processing
- Platform Dashboard: Status monitoring
- Marketing Engine: Campaign operations
- All platform services: Workflow coordination

**Configuration:**
- `PROJECT_ID`: xynergy-dev-1757909467
- `REGION`: us-central1
- `PORT`: 8082

---

### 6. AI Providers

**Service Name:** `ai-providers`
**Port:** 8080
**Container:** `ai-providers:latest`
**URL Pattern:** `https://xynergy-ai-providers-835612502919.us-central1.run.app`

**Purpose:**
External AI API integration service. Manages connections to Abacus AI and OpenAI with intelligent failover.

**Key Features:**
- Abacus AI integration (primary)
- OpenAI API integration (fallback)
- API key management
- Request/response transformation
- Provider health monitoring

**API Endpoints:**
- `GET /health` - Provider availability
- `POST /api/generate/intelligent` - Route to best available provider
- `GET /api/providers/status` - Provider status check

**Supported Providers:**
1. **Abacus AI**
   - Model: abacus-ai-model
   - Cost: $0.015 per request
   - Use case: Primary for complex queries

2. **OpenAI**
   - Model: gpt-4o-mini
   - Cost: $0.025 per request
   - Use case: Fallback when Abacus unavailable

**Configuration:**
- `ABACUS_API_KEY`: Environment variable
- `OPENAI_API_KEY`: Environment variable
- `PROJECT_ID`: xynergy-dev-1757909467

---

### 7. Internal AI Service v2

**Service Name:** `internal-ai-service-v2`
**Port:** 8080
**Container:** `internal-ai-service-v2:latest`
**URL Pattern:** `https://internal-ai-service-v2-vgjxy554mq-uc.a.run.app`

**Purpose:**
Self-hosted AI model service for cost-effective inference. Provides final fallback when external providers are unavailable or for simple queries.

**Key Features:**
- Self-hosted Llama 3.1 8B model
- Ultra-low cost ($0.001 per request)
- GPU acceleration (optional)
- Local inference without external API calls
- Fast response times (1-2 seconds)

**API Endpoints:**
- `GET /health` - Service health
- `POST /api/generate` - Generate AI response

**Model Details:**
- **Model:** Llama 3.1 8B
- **Quantization:** 4-bit for memory efficiency
- **Context window:** 8K tokens
- **Cost:** ~$0.001 per request

**Configuration:**
- `PROJECT_ID`: xynergy-dev-1757909467
- `MODEL_PATH`: Container-embedded model
- GPU configuration optional

---

### 8-44. Additional Services

Due to space constraints, the following services follow similar patterns:

**Content & Media Services:**
- content-hub: Asset management
- rapid-content-generator: AI content generation

**Analytics Services:**
- analytics-data-layer: Data processing
- advanced-analytics: Business intelligence
- keyword-revenue-tracker: Attribution tracking

**Intelligence Services:**
- xynergy-intelligence-gateway: Data aggregation
- market-intelligence-service: Market analysis
- competitive-analysis-service: Competitor tracking

**Research Engine:**
- research-coordinator: Research orchestration
- trending-engine-coordinator: Trend analysis
- real-time-trend-monitor: Real-time monitoring

**Validation Engine:**
- validation-coordinator: Validation orchestration
- fact-checking-service: Fact verification
- fact-checking-layer: Multi-layer fact checking
- plagiarism-detector: Content originality
- trust-safety-validator: Safety compliance

**Attribution Engine:**
- attribution-coordinator: Attribution orchestration
- keyword-revenue-tracker: Revenue attribution

**Platform Services:**
- system-runtime: Core orchestration
- scheduler-automation-engine: Task scheduling
- reports-export: Report generation
- security-governance: Security policies
- security-compliance: Compliance monitoring
- qa-engine: Quality assurance
- project-management: Project tracking
- secrets-config: Secret management

**Tenant Services:**
- tenant-management: Multi-tenant management
- tenant-onboarding-service: Tenant onboarding
- executive-dashboard: Executive reporting
- xynergy-competency-engine: Competency tracking

**AI/ML Services:**
- ai-ml-engine: ML model management
- ai-workflow-engine: Workflow automation

**Scaling Services:**
- performance-scaling: Auto-scaling logic
- monetization-integration: Billing integration

All services follow the same architectural patterns as documented in the detailed services above.

---

## Shared Infrastructure Modules

### Located in `/shared` directory

### 1. gcp_clients.py

**Purpose:** Centralized GCP client manager with connection pooling.

**Key Features:**
- Singleton pattern for client reuse
- Thread-safe client creation
- Automatic connection pooling
- Graceful shutdown handling
- Retry logic for transient errors

**Provided Clients:**
- `get_firestore_client()` - Firestore NoSQL database
- `get_bigquery_client()` - BigQuery analytics
- `get_storage_client()` - Cloud Storage
- `get_publisher_client()` - Pub/Sub publisher
- `get_subscriber_client()` - Pub/Sub subscriber

**Retry Decorators:**
- `@firestore_retry(max_retries=3, backoff_factor=1.0)` - Sync retry
- `@firestore_retry_async()` - Async retry

**Retryable Exceptions:**
- DeadlineExceeded
- ServiceUnavailable
- InternalServerError
- TooManyRequests
- ResourceExhausted

**Usage Example:**
```python
from gcp_clients import get_bigquery_client

bigquery_client = get_bigquery_client()  # Reuses existing connection
query_job = bigquery_client.query("SELECT * FROM dataset.table")
```

**Cleanup:**
```python
from gcp_clients import gcp_clients

await gcp_clients.cleanup()  # Close all connections
```

---

### 2. redis_cache.py

**Purpose:** Intelligent Redis cache manager for AI responses and frequently accessed data.

**Key Features:**
- Connection pooling (max 20 connections)
- Automatic TTL management
- Cache key generation with MD5 hashing
- Category-based cache namespaces
- Cache statistics and monitoring
- Cache warming capability
- Non-blocking SCAN for pattern invalidation

**Cache TTL Configuration:**
```python
{
    "ai_responses": 3600,        # 1 hour
    "api_responses": 1800,       # 30 minutes
    "user_sessions": 7200,       # 2 hours
    "analytics_data": 900,       # 15 minutes
    "content_metadata": 1800,    # 30 minutes
    "system_health": 300,        # 5 minutes
    "expensive_queries": 3600,   # 1 hour
    "trending_data": 300,        # 5 minutes
}
```

**Key Prefixes:**
- `ai:resp:` - AI responses
- `api:call:` - API responses
- `user:sess:` - User sessions
- `analytics:` - Analytics data
- `content:` - Content metadata
- `system:` - System health
- `query:` - Query results
- `trend:` - Trending data

**Primary Methods:**
- `connect()` - Establish Redis connection
- `disconnect()` - Close connection
- `set(category, identifier, value, ttl, params)` - Store with TTL
- `get(category, identifier, params)` - Retrieve cached value
- `delete(category, identifier, params)` - Remove from cache
- `cache_ai_response(prompt, response, provider, model, ttl)` - Cache AI
- `get_cached_ai_response(prompt, provider, model)` - Get cached AI
- `invalidate_pattern(pattern)` - Invalidate matching keys
- `get_cache_stats()` - Cache statistics
- `warm_cache(warm_data)` - Pre-populate cache

**Connection Configuration:**
- Host: `10.0.0.3` (default from Terraform)
- Port: 6379
- DB: 0
- Connect timeout: 5s
- Socket timeout: 5s
- Retry on timeout: Enabled
- Max connections: 20

**Usage Example:**
```python
from redis_cache import redis_cache

await redis_cache.connect()

# Cache an AI response
await redis_cache.cache_ai_response(
    prompt="What is SEO?",
    response={"text": "SEO is..."},
    provider="openai"
)

# Retrieve cached response
cached = await redis_cache.get_cached_ai_response(
    prompt="What is SEO?",
    provider="openai"
)
```

---

### 3. auth.py

**Purpose:** Centralized authentication with zero-trust API key validation.

**Key Features:**
- Thread-safe API key manager
- Automatic key rotation (5-minute reload interval)
- Multiple authentication methods (Bearer token, X-API-Key header)
- Optional authentication for public endpoints
- Rate limiting configuration

**API Key Loading:**
- Environment variable: `XYNERGY_API_KEYS`
- Format: Comma-separated list
- Auto-reload every 5 minutes

**Authentication Functions:**
- `verify_api_key(credentials)` - Bearer token validation
- `verify_api_key_optional(credentials)` - Optional authentication
- `verify_api_key_header(x_api_key)` - X-API-Key header validation
- `reload_api_keys()` - Force key reload

**Decorator:**
```python
@require_auth
async def sensitive_endpoint():
    return {"status": "authenticated"}
```

**FastAPI Dependency:**
```python
@app.post("/api/endpoint", dependencies=[Depends(verify_api_key)])
async def protected_endpoint():
    # Authenticated endpoint
    pass
```

**Rate Limit Configuration:**
```python
RateLimitConfig(
    max_requests_per_minute=60,
    max_requests_per_hour=1000,
    burst_limit=100
)
```

---

### 4. rate_limiting.py

**Purpose:** Tiered rate limiting for API endpoints.

**Rate Limit Tiers:**

| Tier | Requests/Min | Use Case |
|------|--------------|----------|
| Standard | 60 | Normal operations |
| Expensive | 10 | AI generation, complex queries |
| AI | 30 | AI-specific operations |

**FastAPI Dependency Usage:**
```python
from rate_limiting import rate_limit_standard, rate_limit_expensive, rate_limit_ai

@app.post("/api/create", dependencies=[Depends(rate_limit_expensive)])
async def expensive_operation():
    pass

@app.get("/api/list", dependencies=[Depends(rate_limit_standard)])
async def list_items():
    pass
```

---

### 5. http_client.py

**Purpose:** Shared HTTP client with connection pooling and timeout management.

**Key Features:**
- httpx.AsyncClient with connection pooling
- Configurable timeouts (30s default)
- Max connections: 100
- Max keepalive connections: 20
- HTTP/2 support
- Automatic retry on network errors

**Usage:**
```python
from http_client import get_http_client

client = await get_http_client()
response = await client.post(url, json=data, timeout=30.0)
```

**Cleanup:**
```python
from http_client import close_http_client

await close_http_client()
```

---

### 6. pubsub_manager.py

**Purpose:** Pub/Sub message publishing and subscription management.

**Key Features:**
- Batch message publishing
- Automatic topic creation
- Message ordering support
- Dead letter queue handling
- Subscription management

---

### 7. bigquery_optimizer.py

**Purpose:** BigQuery query optimization utilities.

**Key Features:**
- Partition pruning helpers
- Query parameterization
- Cost estimation
- Slot usage monitoring
- Query performance profiling

---

### 8. phase2_utils.py

**Purpose:** Phase 2 optimization utilities (circuit breakers, monitoring).

**Key Components:**

**CircuitBreaker:**
- States: CLOSED, OPEN, HALF_OPEN
- Failure threshold: 5 failures
- Timeout: 60 seconds
- Automatic recovery attempts

**CircuitBreakerConfig:**
```python
CircuitBreakerConfig(
    failure_threshold=5,
    timeout=60,
    expected_exception=Exception
)
```

**PerformanceMonitor:**
- Operation timing tracking
- Request counting
- Average latency calculation
- Metrics export

**Usage:**
```python
from phase2_utils import CircuitBreaker, PerformanceMonitor

circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
monitor = PerformanceMonitor("service-name")

# Circuit breaker
async def protected_call():
    return await call_service_with_circuit_breaker(
        circuit_breaker,
        some_function,
        *args,
        **kwargs
    )

# Performance monitoring
with monitor.track_operation("operation_name"):
    # Do work
    pass
```

---

### 9. ai_token_optimizer.py

**Purpose:** AI token usage optimization for cost reduction.

**Key Features:**
- Dynamic max_tokens calculation
- Prompt complexity analysis
- 20-30% token reduction
- Cost-aware token allocation

**Function:**
```python
def optimize_ai_request(prompt: str, default_tokens: int, user_max_tokens: Optional[int]):
    """
    Returns: (optimized_tokens, metadata)
    """
    pass
```

---

### 10. semantic_cache.py

**Purpose:** Semantic caching with embedding-based similarity (Phase 6, currently disabled).

**Note:** Disabled in lightweight deployment due to sentence-transformers dependency (4GB+).

**Key Features (when enabled):**
- Embedding-based similarity matching
- FAISS vector index
- Configurable similarity threshold
- Would provide ~90%+ cache hit rate on semantically similar queries

---

### 11. cost_intelligence.py

**Purpose:** Cost tracking and optimization intelligence.

**Key Features:**
- Service-level cost tracking
- Budget alerting
- Cost allocation by tenant
- Optimization recommendations

---

### 12-21. Additional Modules

- **monitoring.py** - Centralized monitoring
- **logging_config.py** - Structured logging setup
- **error_handlers.py** - Standardized error handling
- **validators.py** - Input validation utilities
- **crypto_utils.py** - Encryption/decryption
- **tenant_context.py** - Multi-tenant context management
- **feature_flags.py** - Feature flag management
- **config_manager.py** - Configuration management
- **health_checks.py** - Health check utilities
- **metrics_collector.py** - Metrics aggregation

---

## Data Architecture

### Data Flow Overview

```
User Request
    ↓
API Gateway / Service
    ↓
┌─────────┴──────────┐
│                    │
Firestore          BigQuery
(Transactional)    (Analytics)
    │                  │
    ↓                  ↓
Redis Cache      Cloud Storage
(Performance)    (Blob Storage)
    │                  │
    └─────────┬────────┘
              ↓
         Response
```

### Firestore Collections

**Primary Collections:**
- `marketing_campaigns` - Campaign data
- `keyword_research` - Keyword research results
- `service_status` - Service health status
- `workflow_monitoring` - Workflow execution tracking
- `dashboard_metrics` - Dashboard data
- `status_reports` - Generated reports
- `_health_check` - Health check test documents

**Document Structure Pattern:**
```json
{
  "id": "unique_identifier",
  "created_at": "2025-10-10T12:00:00Z",
  "updated_at": "2025-10-10T12:00:00Z",
  "tenant_id": "demo",
  "status": "active",
  "data": { ... }
}
```

### BigQuery Schema Patterns

**Multi-Tenant Pattern:**
- Dataset per tenant: `aso_tenant_{tenant_id}`
- Shared analytics: `xynergy_analytics`
- Engine-specific: `validation_analytics`, `attribution_analytics`

**Time-Series Partitioning:**
- All tables partitioned by DATE(timestamp_field)
- Common partition fields: created_at, detected_at, last_checked
- Partition pruning reduces costs by 70-90%

**Standard Table Schema Elements:**
- Partition column (TIMESTAMP)
- Clustering columns (tenant_id, status)
- JSON fields for flexible data
- Proper indexing on query fields

### Data Retention Policies

| Data Type | Retention | Location |
|-----------|-----------|----------|
| Transactional data | 90 days | Firestore |
| Analytics data | 90 days | BigQuery (default) |
| Content assets | 30 days | Cloud Storage |
| Reports | 365 days | Cloud Storage |
| Research data | 90 days | Cloud Storage |
| Trending data | 30 days | Cloud Storage |
| Cached data | 1-60 minutes | Redis |
| Pub/Sub messages | 7 days | Pub/Sub |

---

## Network & Security

### CORS Configuration

**Standard CORS Policy:**
```python
allow_origins=[
    "https://xynergy-platform.com",
    "https://api.xynergy.dev",
    "https://*.xynergy.com"
]
allow_credentials=True
allow_methods=["GET", "POST", "PUT", "DELETE"]
allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"]
```

**Security Requirements:**
- ❌ NEVER use `allow_origins=["*"]`
- ✅ Always specify exact domains
- ✅ Use HTTPS only in production
- ✅ Include localhost for development

### Authentication & Authorization

**Authentication Methods:**
1. Bearer Token (JWT)
   - Header: `Authorization: Bearer {token}`
   - Use: verify_api_key dependency

2. API Key Header
   - Header: `X-API-Key: {key}`
   - Use: verify_api_key_header dependency

**Authorization Levels:**
- Public endpoints: No authentication
- Standard endpoints: API key required
- Admin endpoints: API key + role validation
- Internal service-to-service: Mutual TLS (planned)

### Network Architecture

**VPC Configuration:**
- VPC network: default
- Subnet: auto-created per region
- Private Google Access: Enabled
- Cloud NAT: Configured for egress

**Service-to-Service Communication:**
- Internal: VPC-native networking
- External: HTTPS with authentication
- Load balancing: Cloud Run automatic

**Firewall Rules:**
- Ingress: HTTPS (443) from Cloud Run
- Egress: HTTPS to GCP services
- Redis: Private IP only (10.0.0.3)

### Security Best Practices

**Code-Level Security:**
1. Input Validation
   - Pydantic models for all inputs
   - Field length limits
   - Type validation
   - Regex patterns for specific formats

2. SQL Injection Prevention
   - Parameterized queries only
   - BigQuery query parameters
   - No string interpolation in SQL

3. Secrets Management
   - Secret Manager for sensitive data
   - Environment variables for configuration
   - No secrets in code or version control

4. Rate Limiting
   - Per-endpoint rate limits
   - Tiered limits (standard, expensive, AI)
   - IP-based throttling

5. Error Handling
   - Structured error responses
   - No sensitive data in error messages
   - Proper HTTP status codes
   - Centralized error logging

**Infrastructure Security:**
1. Service Accounts
   - Principle of least privilege
   - Service-specific accounts
   - Regular permission audits

2. IAM Policies
   - Role-based access control
   - No wildcard permissions
   - Audit logs enabled

3. Encryption
   - At rest: GCP default encryption
   - In transit: TLS 1.3
   - Secrets: Secret Manager encryption

4. Monitoring
   - Cloud Logging for all services
   - Cloud Monitoring alerts
   - Security event logging
   - Anomaly detection

---

## Deployment Architecture

### Container Build Process

**Dockerfile Standard Pattern:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy shared modules first (cache layer)
COPY shared/ /app/shared/

# Copy service-specific files
COPY {service}/requirements.txt .
COPY {service}/main.py .
COPY {service}/phase2_utils.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run service
CMD ["python", "main.py"]
```

**Build Command:**
```bash
docker build -t us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/{service}:latest \
  -f {service}/Dockerfile .
```

**Push to Registry:**
```bash
docker push us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/{service}:latest
```

### Cloud Run Deployment

**Standard Deployment Configuration:**
```yaml
Service: {service-name}
Region: us-central1
Platform: Cloud Run (managed)
Min instances: 0
Max instances: 10
CPU: 1
Memory: 512Mi
Timeout: 300s
Concurrency: 80
Ingress: All
Authentication: Allow unauthenticated (handled at app level)
```

**Deployment Command:**
```bash
gcloud run deploy {service-name} \
  --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/{service}:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=xynergy-dev-1757909467,REGION=us-central1 \
  --service-account xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com \
  --cpu 1 \
  --memory 512Mi \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10
```

**Resource Allocation by Service Type:**

| Service Type | CPU | Memory | Min | Max |
|--------------|-----|--------|-----|-----|
| Dashboard | 1 | 512Mi | 1 | 5 |
| AI Services | 2 | 1Gi | 0 | 10 |
| API Services | 1 | 512Mi | 0 | 10 |
| Background Jobs | 1 | 512Mi | 0 | 5 |
| Analytics | 2 | 1Gi | 0 | 5 |

### Environment Variables

**Standard Variables (All Services):**
- `PROJECT_ID`: xynergy-dev-1757909467
- `REGION`: us-central1
- `PORT`: 8080 (internal)

**Service-Specific Variables:**
- `REDIS_HOST`: 10.0.0.3 (for services using Redis)
- `AI_PROVIDERS_URL`: https://xynergy-ai-providers-*.run.app
- `INTERNAL_AI_URL`: https://internal-ai-service-v2-*.run.app
- `XYNERGY_API_KEYS`: Comma-separated API keys (from Secret Manager)

**Secret Manager Integration:**
```bash
gcloud run services update {service-name} \
  --update-secrets XYNERGY_API_KEYS=xynergy-api-keys:latest
```

### Terraform Deployment

**Initialize:**
```bash
cd terraform/
terraform init
```

**Plan:**
```bash
terraform plan -var="project_id=xynergy-dev-1757909467" -var="region=us-central1"
```

**Apply:**
```bash
terraform apply -var="project_id=xynergy-dev-1757909467" -var="region=us-central1" -auto-approve
```

**Terraform manages:**
- Artifact Registry
- Pub/Sub topics and subscriptions
- BigQuery datasets and tables
- Cloud Storage buckets
- Redis instance
- Service accounts
- IAM bindings

**Note:** Cloud Run services are deployed separately via gcloud CLI or CI/CD pipelines.

### CI/CD Pipeline (Recommended)

**Build Stage:**
1. Checkout code
2. Run tests
3. Build Docker image
4. Tag with commit SHA
5. Push to Artifact Registry

**Deploy Stage:**
1. Update Cloud Run service
2. Run health checks
3. Gradual traffic migration
4. Rollback on failure

**Tools:**
- Cloud Build (recommended)
- GitHub Actions
- GitLab CI/CD

---

## Integration Patterns

### Service-to-Service Communication

**Pattern 1: Synchronous HTTP**
```python
from http_client import get_http_client
from phase2_utils import call_service_with_circuit_breaker

client = await get_http_client()
response = await call_service_with_circuit_breaker(
    circuit_breaker,
    client.post,
    "https://service-url.run.app/api/endpoint",
    json={"data": "value"},
    timeout=30.0
)
```

**Pattern 2: Asynchronous Pub/Sub**
```python
from gcp_clients import get_publisher_client

publisher = get_publisher_client()
topic_path = publisher.topic_path(PROJECT_ID, "service-events")

message = {
    "event_type": "campaign_created",
    "data": {...},
    "timestamp": datetime.now().isoformat()
}

publisher.publish(topic_path, json.dumps(message).encode())
```

**Pattern 3: Workflow Orchestration**
```python
# AI Assistant orchestrates multi-service workflow
@app.post("/orchestrate")
async def orchestrate_workflow(workflow_request: dict):
    workflow_id = generate_workflow_id()

    # Step 1: Marketing analysis
    marketing_result = await call_service(
        "marketing-engine",
        "/execute",
        {
            "action": "analyze_market",
            "parameters": {...},
            "workflow_context": {"workflow_id": workflow_id}
        }
    )

    # Step 2: AI routing
    ai_result = await call_service(
        "ai-routing-engine",
        "/execute",
        {
            "action": "route_request",
            "parameters": {...},
            "workflow_context": {"workflow_id": workflow_id}
        }
    )

    # Step 3: Dashboard update
    dashboard_result = await call_service(
        "platform-dashboard",
        "/execute",
        {
            "action": "update_metrics",
            "parameters": {...},
            "workflow_context": {"workflow_id": workflow_id}
        }
    )

    return {
        "workflow_id": workflow_id,
        "status": "completed",
        "results": [marketing_result, ai_result, dashboard_result]
    }
```

### Standard /execute Endpoint

All services implement a standardized `/execute` endpoint for workflow orchestration:

```python
@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_workflow_step(request: Dict[str, Any]):
    action = request.get("action")
    parameters = request.get("parameters", {})
    workflow_context = request.get("workflow_context", {})

    if action == "service_specific_action":
        # Perform action
        result = perform_action(parameters)

        return {
            "success": True,
            "action": action,
            "output": result,
            "execution_time": time.time(),
            "service": "service-name"
        }
    else:
        return {
            "success": False,
            "error": f"Action '{action}' not supported",
            "supported_actions": [...],
            "service": "service-name"
        }
```

### Request Tracing

All requests are traced using X-Request-ID:

```python
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", f"req_{uuid.uuid4().hex[:12]}")

    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    structlog.contextvars.clear_contextvars()
    return response
```

### Caching Integration

**Pattern 1: Check cache before expensive operation**
```python
cache_key = f"{resource}_{tenant_id}_{filter}"
cached_result = await redis_cache.get("namespace", cache_key)

if cached_result:
    logger.info("cache_hit", resource=resource)
    return cached_result

# Perform expensive operation
result = expensive_operation()

# Cache result
await redis_cache.set("namespace", cache_key, result, ttl=300)
return result
```

**Pattern 2: Cache invalidation on write**
```python
@app.post("/api/content")
async def create_content(content: ContentPiece):
    # Create content
    result = create_content_in_db(content)

    # Invalidate related caches
    await redis_cache.invalidate_pattern(f"content_{content.tenant_id}*")

    return result
```

---

## Performance & Optimization

### Optimization Phases Completed

**Phase 1: Security & Foundation** ✅
- CORS hardening (no wildcards)
- Rate limiting (tiered: standard, expensive, AI)
- Structured logging (JSON, request IDs)
- Resource limits (CPU, memory)
- Input validation (Pydantic models)

**Phase 2: Reliability** ✅
- Circuit breakers (failure threshold: 5, timeout: 60s)
- Performance monitoring (operation tracking)
- Request tracing (X-Request-ID)
- Graceful degradation
- Health checks with connectivity tests

**Phase 3: Caching Foundation** ✅
- Redis infrastructure setup
- Connection pooling (max 20)
- Basic caching patterns
- Cache warming capability

**Phase 4: Query Optimization** ✅
- BigQuery partition pruning (70-90% cost reduction)
- Parameterized queries
- Specific column selection (no SELECT *)
- Index optimization
- Initial Redis caching (stats endpoints)

**Phase 5: Caching Expansion** ✅
- Extended caching to all list endpoints
- Tiered TTLs by data volatility
- Cache hit rate: 84%+
- Query reduction: 40,000 → 6,400/day (84% reduction)

**Phase 6: Advanced Optimization** ✅
- Token optimization (20-30% reduction)
- Semantic cache infrastructure (disabled in lightweight mode)
- AI cost intelligence
- Shared GCP client manager

### Performance Metrics

**Cost Savings:**
- AI routing optimization: 89% cost reduction
- BigQuery optimization: $456/month savings
- Query reduction: 84% fewer queries
- Total annual savings: $93K-158K projected

**Response Times:**
- Cached queries: <10ms (96-98% improvement)
- Uncached queries: 250-550ms
- AI requests (cached): <10ms
- AI requests (uncached): 1-3 seconds

**Cache Performance:**
- Hit rate: 84%+ on list operations
- Memory usage: ~200MB (1GB allocated)
- Connection pool: 20 connections

**Resource Utilization:**
- Average memory per service: 200-300MB
- Average CPU per service: 0.1-0.3 cores
- Container startup time: 2-5 seconds
- Cold start: <10 seconds

### Optimization Checklist

**Query Optimization:**
- ✅ Partition pruning on all time-based queries
- ✅ Query parameterization
- ✅ Specific column selection
- ✅ Appropriate indexes
- ✅ Clustering on frequently filtered columns

**Caching Strategy:**
- ✅ Redis caching for expensive operations
- ✅ TTLs based on data volatility
- ✅ Cache invalidation on writes
- ✅ Connection pooling
- ✅ Cache statistics monitoring

**Connection Management:**
- ✅ Shared GCP clients (singleton pattern)
- ✅ HTTP connection pooling
- ✅ Redis connection pooling
- ✅ Graceful shutdown
- ✅ Resource cleanup

**AI Cost Optimization:**
- ✅ Intelligent routing (Abacus → OpenAI → Internal)
- ✅ Response caching (1-hour TTL)
- ✅ Token optimization
- ✅ Provider health checking
- ✅ Automatic fallback

---

## Monitoring & Observability

### Structured Logging

**All services use structlog with JSON output:**

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
```

**Log Entry Format:**
```json
{
  "timestamp": "2025-10-10T12:00:00.000000Z",
  "level": "info",
  "event": "cache_hit",
  "request_id": "req_abc123",
  "service": "aso-engine",
  "tenant_id": "demo",
  "cache_key": "stats_demo_90"
}
```

### Health Checks

**Standard Health Check Response:**
```json
{
  "service": "service-name",
  "timestamp": "2025-10-10T12:00:00.000000Z",
  "status": "healthy",
  "checks": {
    "firestore": {"status": "healthy"},
    "bigquery": {"status": "healthy", "latency_ms": 45},
    "pubsub": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "circuit_breaker": {"state": "CLOSED", "failure_count": 0}
  },
  "resources": {
    "memory_mb": 234.56,
    "cpu_percent": 15.3,
    "threads": 12
  },
  "performance": {
    "total_requests": 1543,
    "avg_latency_ms": 123.45,
    "operations": {...}
  }
}
```

### Performance Monitoring

**PerformanceMonitor tracks:**
- Total requests
- Operation counts
- Average latency per operation
- Request rate

**Usage:**
```python
monitor = PerformanceMonitor("service-name")

with monitor.track_operation("operation_name"):
    # Perform operation
    pass

# Get metrics
metrics = monitor.get_metrics()
```

### Circuit Breaker Monitoring

**States:**
- CLOSED: Normal operation
- OPEN: Too many failures, requests blocked
- HALF_OPEN: Testing if service recovered

**Metrics:**
- Failure count
- State transitions
- Recovery attempts

### Cloud Monitoring Integration

**Metrics Exported:**
- Request count
- Response time
- Error rate
- Cache hit rate
- Circuit breaker state
- Resource utilization

**Alerts Configured:**
- Service down (health check failures)
- High error rate (>5% of requests)
- High latency (>5s)
- Circuit breaker open
- Resource exhaustion (>80% memory/CPU)

### Cloud Logging

**Log Sinks:**
- Cloud Logging (all logs)
- BigQuery (analytics)
- Cloud Storage (archival)

**Log Levels:**
- DEBUG: Development only
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Operation failures
- CRITICAL: Service failures

### Tracing

**Request tracing via X-Request-ID:**
- Generated on ingress
- Propagated to all downstream services
- Included in all log entries
- Returned in response headers

**Example trace query:**
```sql
SELECT *
FROM logs
WHERE json_payload.request_id = 'req_abc123'
ORDER BY timestamp
```

---

## Maintenance & Operations

### Deployment Procedures

**Standard Deployment:**
1. Build and test locally
2. Push image to Artifact Registry
3. Deploy to Cloud Run
4. Verify health checks
5. Monitor for 15 minutes
6. Rollback if issues detected

**Zero-Downtime Deployment:**
- Cloud Run handles gradual traffic migration
- Old instances remain until new instances healthy
- Automatic rollback on health check failures

**Rollback Procedure:**
```bash
gcloud run services update-traffic {service-name} \
  --to-revisions {previous-revision}=100
```

### Backup & Recovery

**Data Backup:**
- Firestore: Automatic daily backups (7-day retention)
- BigQuery: Time-travel queries (7 days)
- Cloud Storage: Versioning enabled

**Recovery Procedures:**
1. **Firestore Recovery:**
   ```bash
   gcloud firestore import gs://backup-bucket/backup-folder
   ```

2. **BigQuery Recovery:**
   ```sql
   SELECT * FROM `dataset.table`
   FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
   ```

3. **Cloud Storage Recovery:**
   ```bash
   gsutil cp -r gs://bucket/object#version gs://bucket/object
   ```

### Scaling Operations

**Auto-Scaling Configuration:**
- Cloud Run auto-scales based on:
  - Request volume
  - CPU utilization
  - Memory utilization
  - Custom metrics

**Manual Scaling:**
```bash
gcloud run services update {service-name} \
  --min-instances 2 \
  --max-instances 50
```

**Scale-to-Zero:**
- Min instances: 0 (most services)
- Scale-to-zero timeout: 5 minutes
- Cold start optimization: <10 seconds

### Security Updates

**Dependency Updates:**
1. Update requirements.txt
2. Rebuild container
3. Deploy to staging
4. Run security scans
5. Deploy to production

**Security Scanning:**
```bash
gcloud container images scan {image-url}
```

**Vulnerability Management:**
- Automated dependency scanning (Dependabot)
- Weekly security updates
- Critical patches within 24 hours

### Monitoring Dashboard

**Key Metrics to Monitor:**
1. Service health (all services up)
2. Error rate (<1% target)
3. Response time (p50, p95, p99)
4. Cache hit rate (>80% target)
5. Cost metrics (daily/monthly)
6. Resource utilization (<70% target)

**Alert Channels:**
- Email: ops-team@xynergy.com
- PagerDuty: Critical alerts
- Slack: #platform-alerts

### Cost Optimization

**Regular Reviews:**
- Weekly: Service resource utilization
- Monthly: Overall GCP costs
- Quarterly: Architecture optimization opportunities

**Cost Allocation:**
- Tags on all resources
- Cost breakdown by service
- Per-tenant cost tracking

**Optimization Actions:**
- Right-size containers based on metrics
- Adjust min/max instances
- Review and adjust TTLs
- Optimize query patterns
- Review AI routing efficiency

### Disaster Recovery

**RTO (Recovery Time Objective):** 1 hour
**RPO (Recovery Point Objective):** 15 minutes

**DR Plan:**
1. **Region Failure:**
   - Failover to us-east1
   - DNS update to point to DR region
   - Data replication from backups

2. **Service Failure:**
   - Automatic Cloud Run restart
   - Circuit breakers prevent cascading
   - Fallback to degraded mode

3. **Data Loss:**
   - Restore from latest backup
   - Replay Pub/Sub messages (7-day retention)
   - Manual data reconciliation if needed

**DR Testing:**
- Quarterly DR drills
- Annual full DR test
- Document all procedures

### Documentation Maintenance

**This Document:**
- Review monthly
- Update after major changes
- Version control in Git

**Additional Documentation:**
- API documentation (OpenAPI/Swagger)
- Runbooks for common operations
- Troubleshooting guides
- Architecture decision records (ADRs)

---

## Appendix

### Contact Information

**Platform Team:**
- Email: platform-team@xynergy.com
- Slack: #xynergy-platform
- On-call: PagerDuty rotation

### Related Documentation

- [OPTIMIZATION_PLAN.md](OPTIMIZATION_PLAN.md) - Optimization strategy
- [SECURITY_FIXES.md](SECURITY_FIXES.md) - Security vulnerabilities and fixes
- [PHASE4_COMPLETE.md](PHASE4_COMPLETE.md) - Phase 4 optimization details
- [PHASE5_PUBSUB_CONSOLIDATION_COMPLETE.md](PHASE5_PUBSUB_CONSOLIDATION_COMPLETE.md) - Pub/Sub optimization
- [PHASE6_ADVANCED_OPTIMIZATION_COMPLETE.md](PHASE6_ADVANCED_OPTIMIZATION_COMPLETE.md) - Advanced optimizations
- [CLAUDE.md](CLAUDE.md) - Developer guide for Claude Code

### Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-10 | Platform Team | Initial comprehensive as-built documentation |

### Glossary

- **ASO:** Adaptive Search Optimization (or App Store Optimization)
- **Circuit Breaker:** Fault tolerance pattern preventing cascading failures
- **GCP:** Google Cloud Platform
- **IAM:** Identity and Access Management
- **KGR:** Keyword Golden Ratio
- **Partition Pruning:** Query optimization reducing scanned data
- **Redis:** In-memory data structure store used for caching
- **RTO:** Recovery Time Objective
- **RPO:** Recovery Point Objective
- **SERP:** Search Engine Results Page
- **TTL:** Time To Live (cache expiration)
- **VPC:** Virtual Private Cloud

---

**End of Document**

*This as-built documentation represents the Xynergy Platform as of October 10, 2025, with all Phase 1-6 optimizations implemented and tested.*
