# Intelligence Gateway - Technical Requirements Document

**Project:** XynergyOS Phase 2A - Intelligence Gateway Service  
**Version:** 2.0  
**Date:** October 11, 2025  
**Status:** READY FOR IMPLEMENTATION  
**Priority:** P0 - CRITICAL PATH BLOCKER  
**For:** Claude Code Implementation

---

## EXECUTIVE SUMMARY

### Purpose
The Intelligence Gateway is the critical orchestration layer that routes all XynergyOS frontend requests to appropriate backend microservices. This service **MUST** be built before any Phase 2A communication intelligence features can be developed.

### Critical Context
- **Current State:** Documented but NOT BUILT (0% complete)
- **Blocks:** All Phase 2A services (Slack, Gmail, Calendar, CRM)
- **Timeline Impact:** Delays entire Phase 2A by 4 weeks minimum
- **Priority:** P0 - Highest priority blocker

### What This Service Delivers
1. Unified API gateway for all XynergyOS operations
2. Firebase Authentication integration
3. Real-time WebSocket infrastructure for live updates
4. Service routing to 15+ backend microservices
5. Rate limiting, caching, and error handling
6. Health monitoring and observability

### Success Criteria
- Service deployed and accessible at designated Cloud Run URL
- Firebase Auth token validation working
- WebSocket connections stable and authenticated
- Health checks passing (basic and deep)
- Service routing to existing backend services functional
- Ready to integrate Phase 2A services when they're built

---

## TABLE OF CONTENTS

1. [Service Specifications](#service-specifications)
2. [Functional Requirements](#functional-requirements)
3. [Authentication & Authorization](#authentication--authorization)
4. [WebSocket Requirements](#websocket-requirements)
5. [Service Routing](#service-routing)
6. [API Contract](#api-contract)
7. [Error Handling](#error-handling)
8. [Performance Requirements](#performance-requirements)
9. [Security Requirements](#security-requirements)
10. [Monitoring & Observability](#monitoring--observability)
11. [Deployment Requirements](#deployment-requirements)
12. [Dependencies & Integration](#dependencies--integration)
13. [Implementation Priorities](#implementation-priorities)

---

## SERVICE SPECIFICATIONS

### Technology Stack

**Recommended:** TypeScript/Node.js  
**Rationale:**
- Superior WebSocket support via Socket.io
- Aligns with Next.js frontend (TypeScript consistency)
- Modern async/await patterns
- Strong typing for safety
- Faster prototyping for orchestration layer

**Alternative:** Python/FastAPI (acceptable if team preference)

### Runtime Environment

**Platform:** Google Cloud Run  
**Region:** us-central1  
**Project:** xynergy-dev-1757909467  
**Service Account:** xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com

### Resource Allocation

- **CPU:** 2 vCPU minimum
- **Memory:** 2 GiB minimum
- **Instances:** 
  - Minimum: 1 (always warm)
  - Maximum: 20 (auto-scale)
- **Timeout:** 300 seconds
- **Port:** 8080 (Cloud Run standard)
- **Concurrency:** 80 requests per instance

### Service Naming

**Service Name:** `xynergyos-intelligence-gateway`  
**Expected URL:** `https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app`  
**Container Image:** `us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergyos-intelligence-gateway:latest`

---

## FUNCTIONAL REQUIREMENTS

### FR-1: Request Routing

**Requirement:** The gateway SHALL route incoming HTTP requests to appropriate backend microservices based on URL path patterns.

**Details:**
- Parse incoming request path
- Match against routing table configuration
- Forward request to target service with original headers (except sensitive ones)
- Return response to client
- Handle timeouts and retries

**Routing Patterns:**
- `/api/v2/slack/*` → Slack Intelligence Service (future)
- `/api/v2/email/*` → Gmail Intelligence Service (future)
- `/api/v2/calendar/*` → Calendar Intelligence Service (future)
- `/api/v2/crm/*` → CRM Engine (future)
- `/api/v2/memory/*` → Living Memory Service (existing)
- `/api/v1/*` → Legacy Xynergy Platform services (existing)

### FR-2: Authentication Validation

**Requirement:** The gateway SHALL validate Firebase Authentication tokens for protected routes.

**Details:**
- Extract Bearer token from Authorization header
- Verify token using Firebase Admin SDK
- Decode token to extract user ID, email, tenant ID
- Attach user context to request for downstream services
- Return 401 Unauthorized for invalid/expired tokens
- Support token refresh flow

### FR-3: WebSocket Management

**Requirement:** The gateway SHALL provide WebSocket connections for real-time updates.

**Details:**
- Accept WebSocket upgrade requests at `/api/xynergyos/v2/stream`
- Authenticate connection via token in handshake
- Support topic-based subscriptions (e.g., "slack", "email", "calendar")
- Broadcast updates to subscribed clients
- Handle connection lifecycle (connect, subscribe, unsubscribe, disconnect)
- Support room-based isolation by tenant ID

### FR-4: Health Monitoring

**Requirement:** The gateway SHALL expose health check endpoints.

**Details:**
- **Basic Health:** `/health` - Returns 200 OK if service is running
- **Deep Health:** `/health/deep` - Checks connectivity to:
  - Firebase Auth
  - Redis cache
  - At least 3 downstream services
  - Returns detailed status for each dependency

### FR-5: Rate Limiting

**Requirement:** The gateway SHALL enforce rate limits to prevent abuse.

**Details:**
- **Public Routes:** 5 requests per minute per IP address
- **Authenticated Routes:** 100 requests per minute per user
- Return 429 Too Many Requests when limit exceeded
- Include retry-after header
- Use in-memory tracking (Phase 1), Redis-backed (Phase 2)

### FR-6: Request/Response Transformation

**Requirement:** The gateway SHALL transform requests and responses as needed for service compatibility.

**Details:**
- Add standardized headers (X-Tenant-ID, X-User-ID, X-Request-ID)
- Normalize error responses to consistent format
- Add CORS headers for browser requests
- Compress responses (gzip/brotli) when client supports
- Handle multipart/form-data for file uploads

### FR-7: Caching

**Requirement:** The gateway SHALL cache responses to reduce backend load.

**Details:**
- Cache GET requests only
- Use Redis for distributed caching
- TTL configuration per route pattern
- Cache invalidation via Pub/Sub events
- Skip cache for user-specific data
- Cache-Control header respect

---

## AUTHENTICATION & AUTHORIZATION

### AUTH-1: Firebase Integration

**Requirement:** Integrate Firebase Admin SDK for token validation.

**Details:**
- Initialize Admin SDK with service account credentials
- Use `verifyIdToken()` for validation
- Extract custom claims if present
- Support both ID tokens and refresh tokens
- Handle token expiration gracefully

### AUTH-2: Protected Routes

**Requirement:** Define which routes require authentication.

**Protected Routes:**
- All `/api/v2/*` routes (XynergyOS features)
- All `/api/v1/*` routes (Xynergy Platform features)

**Public Routes:**
- `/health` and `/health/deep`
- `/api/public/*` (website routes)
- Any route explicitly marked public in configuration

### AUTH-3: Service-to-Service Authentication

**Requirement:** Authenticate requests from gateway to backend services.

**Details:**
- Use service account credentials for authentication
- Include Authorization header with service account token
- Rotate tokens before expiration
- Support mutual TLS if backend services require

### AUTH-4: Tenant Isolation

**Requirement:** Ensure requests are isolated by tenant ID.

**Details:**
- Extract tenant ID from Firebase token custom claims
- Default to "clearforge" for single-tenant phase
- Add X-Tenant-ID header to all downstream requests
- Validate user has access to requested resources

---

## WEBSOCKET REQUIREMENTS

### WS-1: Connection Establishment

**Requirement:** Accept and authenticate WebSocket connections.

**Details:**
- Listen for upgrade requests at `/api/xynergyos/v2/stream`
- Require Firebase token in handshake (auth.token)
- Validate token before accepting connection
- Assign connection to user-specific namespace
- Support multiple simultaneous connections per user

### WS-2: Topic Subscriptions

**Requirement:** Allow clients to subscribe to specific update topics.

**Details:**
- Support subscription message: `{type: 'subscribe', topics: ['slack', 'email']}`
- Create rooms based on pattern: `{tenantId}:{topic}`
- Join client socket to requested rooms
- Support unsubscribe message
- Auto-cleanup on disconnect

### WS-3: Event Broadcasting

**Requirement:** Broadcast events to subscribed clients.

**Details:**
- Accept events from backend services (via HTTP POST to gateway)
- Determine target room based on tenant and topic
- Emit event to all sockets in room
- Include event metadata (timestamp, source service)
- Support both broadcast (all users) and unicast (specific user)

### WS-4: Connection Management

**Requirement:** Handle connection lifecycle and failures.

**Details:**
- Auto-reconnect support with exponential backoff
- Heartbeat/ping-pong to detect dead connections
- Timeout idle connections after 5 minutes
- Log connection events (connect, disconnect, error)
- Track active connection count for monitoring

### WS-5: Scalability

**Requirement:** Support WebSocket across multiple Cloud Run instances.

**Details:**
- Use Redis Pub/Sub adapter for Socket.io
- Share connection state across instances
- Ensure events reach clients regardless of which instance they're connected to
- Test with 2+ instances running simultaneously

---

## SERVICE ROUTING

### SR-1: Service Registry

**Requirement:** Maintain configuration of all backend services.

**Details:**
- Store service URLs in environment variables
- Service names: aiRouting, slackIntelligence, gmailIntelligence, calendarIntelligence, crmEngine, marketingEngine, asoEngine, etc.
- Support service discovery via configuration
- Allow runtime configuration updates without redeployment

### SR-2: Request Forwarding

**Requirement:** Forward requests to target services with proper headers.

**Details:**
- Preserve original HTTP method (GET, POST, PATCH, DELETE)
- Forward query parameters unchanged
- Forward request body for POST/PATCH/PUT
- Add X-User-ID, X-Tenant-ID, X-Request-ID headers
- Remove sensitive headers (Authorization replaced with service token)
- Set timeout of 30 seconds per request

### SR-3: Response Handling

**Requirement:** Process responses from backend services.

**Details:**
- Return status code from backend service
- Forward response headers (except internal ones)
- Return response body unchanged
- Handle streaming responses if needed
- Log response time and status

### SR-4: Retry Logic

**Requirement:** Retry failed requests to backend services.

**Details:**
- Retry on 5xx errors and network failures
- Maximum 2 retries with exponential backoff
- Do NOT retry on 4xx errors (client errors)
- Do NOT retry on write operations (POST/PATCH/DELETE)
- Log retry attempts

### SR-5: Circuit Breaker (Optional Phase 2)

**Requirement:** Prevent cascading failures from unhealthy services.

**Details:**
- Track failure rate per backend service
- Open circuit after 50% failure rate over 10 requests
- Return 503 Service Unavailable when circuit is open
- Attempt to close circuit after 30 seconds
- Log circuit state changes

---

## API CONTRACT

### API-1: Health Endpoints

**GET /health**
- **Authentication:** None required
- **Response:** 200 OK with `{status: "healthy", service: "xynergyos-intelligence-gateway", version: "1.0.0", timestamp: ISO8601}`
- **Purpose:** Kubernetes/Cloud Run liveness probe

**GET /health/deep**
- **Authentication:** None required
- **Response:** 200 OK with detailed status of all dependencies
- **Purpose:** Readiness probe and detailed diagnostics

### API-2: Public Routes (Website)

**POST /api/public/beta**
- **Authentication:** None (rate limited by IP)
- **Input:** `{name, email, company, interest_level, comments}`
- **Action:** Forward to Marketing Engine, store in Firestore
- **Response:** `{application_id, status: "submitted"}`

**POST /api/public/contact**
- **Authentication:** None (rate limited by IP)
- **Input:** `{name, email, subject, message}`
- **Action:** Forward to Marketing Engine, send notification
- **Response:** `{submission_id, status: "received"}`

**GET /api/public/aso/opportunities**
- **Authentication:** None (public data)
- **Action:** Forward to ASO Engine
- **Response:** Array of opportunity objects

### API-3: Authenticated Routes (XynergyOS)

**Pattern:** `/api/v2/{service}/{resource}`

**Examples:**
- `GET /api/v2/slack/intelligence/pending` → Slack Intelligence Service
- `GET /api/v2/email/intelligence/pending` → Gmail Intelligence Service
- `GET /api/v2/calendar/events` → Calendar Intelligence Service
- `GET /api/v2/crm/contacts` → CRM Engine
- `GET /api/v2/memory/entries` → Living Memory Service

**Authentication:** Firebase Auth required (Bearer token)  
**Headers Required:** `Authorization: Bearer {firebase_token}`  
**Headers Added:** `X-User-ID`, `X-Tenant-ID`, `X-Request-ID`

### API-4: WebSocket Endpoint

**WS /api/xynergyos/v2/stream**
- **Authentication:** Firebase token in handshake `{auth: {token: "..."}}`
- **Messages:**
  - Client → Server: `{type: "subscribe", topics: ["slack", "email"]}`
  - Client → Server: `{type: "unsubscribe", topics: ["slack"]}`
  - Server → Client: `{event: "slack_update", data: {...}, timestamp: ISO8601}`

---

## ERROR HANDLING

### ERR-1: Standard Error Format

**Requirement:** All errors SHALL follow consistent format.

**Format:**
```typescript
{
  error: {
    code: "AUTH_TOKEN_INVALID",
    message: "User-friendly error message",
    details?: "Additional technical details (only in dev)",
    requestId: "uuid",
    timestamp: "ISO8601"
  }
}
```

### ERR-2: HTTP Status Codes

**Requirement:** Use appropriate status codes.

**Mapping:**
- 200: Successful request
- 201: Resource created
- 400: Invalid input (validation failure)
- 401: Authentication required/failed
- 403: Forbidden (authenticated but no permission)
- 404: Resource not found
- 429: Rate limit exceeded
- 500: Internal server error
- 502: Bad gateway (backend service error)
- 503: Service unavailable (circuit breaker open)
- 504: Gateway timeout (backend service timeout)

### ERR-3: Error Logging

**Requirement:** Log all errors with context.

**Details:**
- Use structured logging (JSON format)
- Include: error message, stack trace, request ID, user ID, endpoint, timestamp
- Severity levels: ERROR (client errors 4xx), CRITICAL (server errors 5xx)
- Send to Cloud Logging
- Never log sensitive data (tokens, passwords, PII)

### ERR-4: Graceful Degradation

**Requirement:** Handle service failures gracefully.

**Details:**
- Return cached data if available when backend fails
- Return partial results if some services fail
- Provide meaningful error messages to clients
- Don't crash the gateway on single service failure

---

## PERFORMANCE REQUIREMENTS

### PERF-1: Response Time

**Requirement:** The gateway SHALL meet latency targets.

**Targets:**
- Health check: < 50ms (p95)
- Authenticated requests: < 200ms (p95) excluding backend service time
- Public routes: < 300ms (p95) total
- WebSocket connection establishment: < 500ms
- WebSocket message delivery: < 100ms

### PERF-2: Throughput

**Requirement:** Support concurrent request load.

**Targets:**
- 100 requests/second minimum (single instance)
- 1000 requests/second with auto-scaling
- 500 simultaneous WebSocket connections per instance
- 10,000 total WebSocket connections across instances

### PERF-3: Resource Utilization

**Requirement:** Efficient use of compute resources.

**Targets:**
- CPU utilization < 70% under normal load
- Memory utilization < 80% under normal load
- Cold start time < 5 seconds
- Instance ready for traffic within 10 seconds

### PERF-4: Caching

**Requirement:** Cache responses to reduce backend load.

**Targets:**
- Cache hit rate > 60% for cacheable requests
- Cache response time < 10ms
- TTL configuration per route (default 5 minutes)

---

## SECURITY REQUIREMENTS

### SEC-1: Transport Security

**Requirement:** All communication SHALL use encryption.

**Details:**
- HTTPS only (Cloud Run enforces TLS 1.2+)
- WSS (WebSocket over TLS) only
- No plaintext HTTP supported
- HSTS headers enabled

### SEC-2: Input Validation

**Requirement:** Validate all inputs before processing.

**Details:**
- Validate JSON payloads against schema
- Sanitize string inputs (prevent injection)
- Validate content-type headers
- Reject requests exceeding size limits (10MB default)
- Validate email formats, URLs, etc.

### SEC-3: Header Security

**Requirement:** Include security headers in responses.

**Headers Required:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: default-src 'self'`

### SEC-4: CORS Configuration

**Requirement:** Configure CORS appropriately.

**Details:**
- Allow origins: `https://xynergyos.clearforgetech.com` (production), `http://localhost:3000` (dev)
- Allow methods: GET, POST, PATCH, DELETE, OPTIONS
- Allow headers: Authorization, Content-Type
- Allow credentials: true
- Max age: 86400 seconds

### SEC-5: Secret Management

**Requirement:** Handle secrets securely.

**Details:**
- Store Firebase service account in Google Secret Manager
- Store API keys in Secret Manager
- Never log secrets or tokens
- Rotate credentials every 90 days
- Use environment variables for non-sensitive config

---

## MONITORING & OBSERVABILITY

### MON-1: Structured Logging

**Requirement:** Log all significant events in structured format.

**Details:**
- Use JSON format for all logs
- Include: timestamp, severity, message, requestId, userId, endpoint, latency, statusCode
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Send to Cloud Logging
- Sample INFO logs at 10% in production

### MON-2: Metrics

**Requirement:** Export metrics for monitoring.

**Details:**
- Request count by endpoint, status code
- Request latency (p50, p95, p99)
- Error rate by endpoint
- Active WebSocket connections count
- Rate limit hits
- Cache hit/miss rate
- Upstream service latency
- Circuit breaker state changes

### MON-3: Tracing

**Requirement:** Support distributed tracing.

**Details:**
- Generate X-Request-ID for each request
- Propagate request ID to downstream services
- Use Cloud Trace for distributed tracing
- Sample 10% of requests in production

### MON-4: Alerting

**Requirement:** Alert on critical conditions.

**Alerts:**
- Error rate > 5% for 5 minutes
- p95 latency > 1 second for 5 minutes
- Health check failures
- Instance restart/crash
- Rate limit threshold approaching (80% of limit)
- WebSocket connection failures > 10% for 5 minutes

---

## DEPLOYMENT REQUIREMENTS

### DEP-1: Container Image

**Requirement:** Build production-ready Docker image.

**Details:**
- Multi-stage build for smaller image size
- Node.js 20 LTS base image (or Python 3.11 if using FastAPI)
- Non-root user for security
- Include only production dependencies
- Health check command in Dockerfile
- Optimized layer caching

### DEP-2: Environment Configuration

**Requirement:** Support multiple environments.

**Environments:**
- **Development:** Local with Docker, connects to dev services
- **Staging:** Cloud Run staging environment
- **Production:** Cloud Run production environment

**Configuration via:**
- Environment variables (non-sensitive)
- Secret Manager (sensitive)
- Cloud Run service configuration

### DEP-3: Continuous Deployment

**Requirement:** Automated deployment pipeline.

**Details:**
- Build triggered on merge to main branch
- Run tests before deployment
- Build Docker image
- Push to Artifact Registry
- Deploy to Cloud Run
- Run smoke tests
- Rollback on failure

### DEP-4: Zero-Downtime Deployment

**Requirement:** Deploy without service interruption.

**Details:**
- Cloud Run gradual rollout (100% to new version over 5 minutes)
- Health checks must pass before traffic switches
- Keep old version running until new version healthy
- Automatic rollback if health checks fail

---

## DEPENDENCIES & INTEGRATION

### DEP-1: Firebase Admin SDK

**Purpose:** Token validation and user management  
**Version:** Latest stable  
**Configuration:** Service account JSON from Secret Manager  
**Integration Points:** Authentication middleware

### DEP-2: Redis

**Purpose:** Caching and WebSocket state sharing  
**Instance:** 10.0.0.3:6379 (existing)  
**Configuration:** STANDARD_HA, 1GB  
**Integration Points:** Cache service, Socket.io adapter

### DEP-3: Backend Microservices

**Existing Services:**
- AI Routing Engine
- Marketing Engine
- ASO Engine
- Platform Dashboard
- Cost Intelligence Engine
- Anomaly Detection Engine
- ML Training Service
- Notification Service
- Analytics Service
- Security Scanner
- API Rate Limiter

**Future Services (Phase 2A):**
- Slack Intelligence Service
- Gmail Intelligence Service
- Calendar Intelligence Service
- CRM Engine

**Integration:** HTTP/HTTPS requests with service account authentication

### DEP-4: Cloud Logging

**Purpose:** Centralized logging  
**Configuration:** Automatic via Cloud Run  
**Integration Points:** Winston logger (Node.js) or standard logging (Python)

### DEP-5: Cloud Trace

**Purpose:** Distributed tracing  
**Configuration:** Automatic via Cloud Run  
**Integration Points:** OpenTelemetry instrumentation

---

## IMPLEMENTATION PRIORITIES

### Phase 1: Minimum Viable Gateway (P0 - Week 1-2)

**MUST HAVE:**
1. Express server setup (or FastAPI if Python)
2. Health check endpoints (/health, /health/deep)
3. Firebase Auth middleware
4. Public routes (beta, contact, aso)
5. Service router to Marketing Engine and ASO Engine
6. Error handling middleware
7. CORS configuration
8. Request logging
9. Dockerfile and Cloud Run deployment
10. Basic WebSocket infrastructure (connection handling)

**SUCCESS:** Gateway deployed, public routes working, health checks passing

### Phase 2: Enhanced Features (P1 - Week 3-4)

**SHOULD HAVE:**
1. Full WebSocket implementation (topics, subscriptions, broadcasting)
2. Redis caching for GET requests
3. Rate limiting (in-memory → Redis-backed)
4. Deep health checks (verify downstream services)
5. Retry logic for backend requests
6. Enhanced monitoring (metrics export)
7. Integration tests
8. Load testing

**SUCCESS:** WebSocket working, caching operational, ready for Phase 2A services

### Phase 3: Advanced Features (P2 - Future)

**NICE TO HAVE:**
1. Circuit breaker pattern
2. Request throttling per user
3. Advanced caching strategies
4. GraphQL support (if needed)
5. API versioning support
6. Request/response transformation rules
7. Mock service mode for testing
8. Admin API for configuration

**SUCCESS:** Production-hardened, optimized for scale

---

## VALIDATION & TESTING

### Test Coverage Requirements

**Unit Tests:**
- All middleware functions
- Authentication logic
- Service router
- Error handling
- Input validation
- Coverage target: >80%

**Integration Tests:**
- Health endpoints
- Public routes end-to-end
- Firebase Auth flow
- WebSocket connection and subscriptions
- Backend service routing
- Error scenarios

**Load Tests:**
- 100 req/s sustained for 10 minutes
- 500 WebSocket connections
- Rate limiting behavior
- Auto-scaling verification

### Acceptance Criteria

**The Intelligence Gateway is COMPLETE when:**

1. ✅ Deployed to Cloud Run at expected URL
2. ✅ Health checks return 200 OK
3. ✅ Can submit beta application successfully
4. ✅ Can submit contact form successfully
5. ✅ Can retrieve ASO opportunities
6. ✅ Firebase Auth validates tokens correctly
7. ✅ Invalid tokens return 401
8. ✅ Rate limiting blocks 6th request in 1 minute
9. ✅ WebSocket connections authenticate and stay alive
10. ✅ Logs appear in Cloud Logging
11. ✅ Metrics appear in Cloud Monitoring
12. ✅ Service router can reach 3+ backend services
13. ✅ Error responses follow standard format
14. ✅ Zero-downtime deployment works
15. ✅ Documentation complete (README, API docs)

---

## CRITICAL DECISIONS NEEDED

**Before Implementation Begins:**

1. **Technology Choice:** TypeScript/Node.js OR Python/FastAPI?
   - **Recommendation:** TypeScript (better WebSocket support)
   
2. **Minimal vs Full Gateway:** Build minimal (P0 only) or include P1 features?
   - **Recommendation:** Start minimal (P0), iterate to P1
   
3. **Firestore Collections:** Where to store beta applications and contact submissions?
   - **Recommendation:** `beta_applications` and `contact_submissions`
   
4. **Notification Method:** Email, Slack webhook, or both for contact/beta submissions?
   - **Recommendation:** Slack webhook for immediate notification
   
5. **ASO Endpoint Path:** Exact path on ASO Engine?
   - **Action:** Verify with ASO Engine documentation

---

## TIMELINE ESTIMATE

**Recommended Schedule:**

- **Week 1:** Setup, authentication, public routes, basic routing, deployment
- **Week 2:** WebSocket, testing, debugging, documentation, production ready
- **Week 3-4:** Phase 2A services can begin development (parallel)

**Critical Path:**
This service blocks ALL Phase 2A work. Any delay here delays the entire Phase 2A by the same amount.

---

## APPENDIX: GLOSSARY

- **Intelligence Gateway:** Orchestration layer routing XynergyOS requests to backend services
- **WebSocket:** Persistent bidirectional communication protocol
- **Firebase Auth:** Google's authentication and identity service
- **Cloud Run:** Google's serverless container platform (managed Kubernetes)
- **Circuit Breaker:** Pattern to prevent cascading failures
- **Tenant:** Isolated customer environment (currently only "clearforge")
- **Service Account:** Machine identity for Google Cloud authentication
- **Rate Limiting:** Restrict number of requests per time period
- **Redis:** In-memory data structure store (cache and message broker)

---

**This TRD provides complete requirements. Claude Code should design implementation architecture and code based on these requirements.**