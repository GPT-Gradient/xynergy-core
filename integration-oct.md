# Xynergy Platform - Integration Requirements TRD
## Technical Requirements Document for Backend Platform Changes

**Project:** XynergyOS Platform Integration  
**Version:** 1.0  
**Date:** October 13, 2025  
**Status:** READY FOR IMPLEMENTATION  
**Priority:** P0 - CRITICAL BLOCKER

---

## EXECUTIVE SUMMARY

### Purpose
This TRD specifies all backend platform changes required to enable XynergyOS frontend-backend integration. Currently, the frontend and backend cannot communicate due to authentication mismatches, API path differences, and missing services.

### Current State Assessment
**Frontend Status:**
- ✅ Fully built and production-ready
- ✅ 30+ pages and components complete
- ✅ Expects 40+ API endpoints
- 🔴 **BLOCKED:** Cannot connect to backend

**Backend Status:**
- ✅ 48 microservices deployed (30 operational)
- ✅ Intelligence Gateway deployed and optimized
- ✅ Slack/Gmail services deployed (mock mode)
- 🔴 **GAPS:** Missing authentication layer, API path mismatches, missing services

### Integration Gaps Identified

| Gap Area | Impact | Priority |
|----------|--------|----------|
| Authentication mismatch (JWT vs Firebase) | BLOCKS ALL requests | P0 |
| API path differences (`/api/v1/*` vs `/api/v2/*`) | 404 errors on all endpoints | P0 |
| Missing Calendar Service | Calendar features broken | P0 |
| Missing Memory Service | Memory management broken | P0 |
| Research Coordinator not deployed | Research features broken | P0 |
| OAuth not configured | Mock data only (no real Slack/Gmail) | P1 |
| No integration tests | No validation of connectivity | P1 |
| Missing monitoring | Can't detect integration issues | P2 |

### What This TRD Delivers

**Phase 1: Critical Connectivity (Week 1)**
1. Authentication strategy implementation
2. API endpoint audit and mapping
3. Gateway route standardization

**Phase 2: Missing Services (Week 2)**
4. Calendar Intelligence Service deployment
5. Memory Service deployment
6. Research Coordinator deployment

**Phase 3: Production Data (Week 3)**
7. Slack OAuth configuration
8. Gmail OAuth configuration
9. Remove mock mode

**Phase 4: Validation (Week 4)**
10. Integration test suite
11. Monitoring dashboard
12. Production readiness validation

---

## PROBLEM STATEMENT

### What Went Wrong
Frontend was developed assuming the backend had:
- JWT authentication in the Intelligence Gateway
- Consistent `/api/v1/` and `/api/v2/` paths
- Calendar, Memory, and Research services deployed
- Real OAuth for Slack and Gmail

**Reality:** None of these exist. Services are deployed but inaccessible to the frontend.

### Why This Matters
**User Impact:** XynergyOS cannot launch. Zero features work.  
**Business Impact:** 3+ months of frontend work is blocked.  
**Technical Debt:** Each day delayed increases integration complexity.

---

## SECTION 1: AUTHENTICATION STRATEGY

### REQUIREMENT 1.1: Choose Authentication Approach

**Problem:** Frontend uses Firebase Auth. Intelligence Gateway has no authentication.

**Decision Required:** Choose ONE of these approaches:

#### Option A: Add JWT to Intelligence Gateway (RECOMMENDED)
**What Changes:**
- Intelligence Gateway validates Firebase ID tokens
- Extracts user ID from token
- Passes user context to backend services
- Frontend code stays unchanged

**Implementation:**
```typescript
// Intelligence Gateway - JWT validation middleware
import * as admin from 'firebase-admin';

async function authenticateRequest(req, res, next) {
  const token = req.headers.authorization?.split('Bearer ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  try {
    const decodedToken = await admin.auth().verifyIdToken(token);
    req.user = {
      uid: decodedToken.uid,
      email: decodedToken.email,
      tenant_id: decodedToken.tenant_id
    };
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

**Pros:**
- No frontend changes
- Centralized auth in gateway
- Easier to debug
- Faster to implement

**Cons:**
- Gateway becomes authentication dependency
- Slight latency overhead

#### Option B: Frontend Adopts Backend Auth
**What Changes:**
- Frontend removes Firebase Auth
- Frontend adopts platform's authentication system
- Major refactor of frontend auth code

**Pros:**
- Consistent auth across platform
- No gateway auth dependency

**Cons:**
- Major frontend refactor (2+ weeks)
- Breaks existing frontend code
- Higher risk

**RECOMMENDATION:** **Option A** - Add JWT validation to Intelligence Gateway.

### REQUIREMENT 1.2: Implement Chosen Strategy

**Tasks for Option A (Recommended):**

1. **Install Firebase Admin SDK in Intelligence Gateway**
   ```bash
   npm install firebase-admin
   ```

2. **Configure Firebase project credentials**
   - Store Firebase service account in Secret Manager
   - Load credentials on gateway startup

3. **Add authentication middleware**
   - Create JWT validation function
   - Apply to all `/api/v2/*` routes
   - Extract user context (uid, email, tenant_id)

4. **Test authentication**
   - Valid token → 200 OK with data
   - Invalid token → 401 Unauthorized
   - Missing token → 401 Unauthorized
   - Expired token → 401 Unauthorized

5. **Document frontend token format**
   ```
   Authorization: Bearer <FIREBASE_ID_TOKEN>
   ```

**Acceptance Criteria:**
- ✅ Frontend can authenticate with existing Firebase tokens
- ✅ Invalid tokens return 401
- ✅ User context available to all backend services
- ✅ No changes required to frontend code

---

## SECTION 2: API ENDPOINT STANDARDIZATION

### REQUIREMENT 2.1: Gateway Route Consistency

**Problem:** Frontend expects `/api/v2/slack/*` but gateway serves `/api/xynergyos/v2/slack/*`

**Solution:** Intelligence Gateway must accept BOTH path formats.

**Implementation:**

```typescript
// Intelligence Gateway - Route aliasing
app.use('/api/v2/*', (req, res, next) => {
  // Rewrite to internal path
  req.url = `/api/xynergyos/v2${req.path.substring(7)}`;
  next();
});

// OR use path mapping
const routes = {
  '/api/v2/slack': 'slack-intelligence-service',
  '/api/v2/email': 'gmail-intelligence-service', // Note: email not gmail
  '/api/v2/calendar': 'calendar-intelligence-service',
  '/api/v2/crm': 'crm-engine',
  '/api/v1/memory': 'memory-service',
  '/api/v1/ai/query': 'ai-assistant-service'
};
```

**Tasks:**

1. **Add route aliases in gateway**
   - Map `/api/v1/*` to appropriate services
   - Map `/api/v2/*` to appropriate services
   - Maintain backward compatibility

2. **Email vs Gmail path fix**
   - Frontend expects `/api/v2/email/*`
   - Backend has `/api/v2/gmail/*`
   - **Solution:** Gateway routes both to same service

3. **Test all path variations**
   - `/api/v1/auth/login` works
   - `/api/v2/slack/messages` works
   - `/api/v2/email/messages` works (routes to Gmail service)

**Acceptance Criteria:**
- ✅ Frontend paths work without changes
- ✅ Backward compatibility maintained
- ✅ All services reachable via standard paths

### REQUIREMENT 2.2: Audit Existing Backend Endpoints

**Problem:** Don't know what endpoints exist in `xynergyos-backend` service.

**Tasks:**

1. **Document xynergyos-backend endpoints**
   - Review code for all route definitions
   - Test each endpoint
   - Document request/response formats

2. **Create API mapping document**
   
   | Frontend Expects | Backend Provides | Status | Action |
   |------------------|------------------|--------|--------|
   | `/api/v1/auth/login` | ? | Unknown | Audit |
   | `/api/v1/dashboard/metrics` | ? | Unknown | Audit |
   | `/api/v1/projects/*` | ? | Likely exists | Verify |
   | `/api/v1/ai/query` | Exists | ✅ | Route via gateway |

3. **Identify gaps**
   - Missing endpoints → Create stubs
   - Mismatched formats → Add transformation
   - Wrong paths → Add aliases

**Deliverable:** Complete API Endpoint Mapping Document

**Acceptance Criteria:**
- ✅ Every frontend endpoint mapped to backend
- ✅ Gaps documented with solutions
- ✅ Format mismatches identified

---

## SECTION 3: MISSING BACKEND SERVICES

### REQUIREMENT 3.1: Calendar Intelligence Service

**Status:** NOT FOUND in backend audit  
**Frontend Impact:** Calendar features completely broken

**Options:**

**Option A: Service Exists Under Different Name**
- Search for services with calendar functionality
- Check if functionality exists in another service
- Redeploy or reconfigure

**Option B: Build New Service**
- Clone Gmail Intelligence Service as template
- Integrate Google Calendar API
- Deploy to Cloud Run

**Implementation Steps (assuming Option B):**

1. **Create Calendar Intelligence Service**
   ```
   Service: calendar-intelligence-service
   Base on: gmail-intelligence-service (similar OAuth pattern)
   APIs: Google Calendar API
   ```

2. **Required Endpoints:**
   ```
   GET /api/v2/calendar/events - List events
   GET /api/v2/calendar/events/:id - Get event details
   POST /api/v2/calendar/events - Create event
   PATCH /api/v2/calendar/events/:id - Update event
   DELETE /api/v2/calendar/events/:id - Delete event
   GET /api/v2/calendar/prep/:eventId - Get meeting prep
   ```

3. **OAuth Configuration:**
   - Enable Google Calendar API
   - Use same OAuth as Gmail
   - Add scope: `https://www.googleapis.com/auth/calendar`

4. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy calendar-intelligence-service \
     --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/calendar-intelligence-service:latest \
     --region us-central1 \
     --service-account xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com
   ```

5. **Add route in Intelligence Gateway:**
   ```typescript
   routes['/api/v2/calendar'] = 'calendar-intelligence-service';
   ```

**Acceptance Criteria:**
- ✅ Service deployed and accessible
- ✅ OAuth working with Google Calendar
- ✅ All required endpoints implemented
- ✅ Routed through Intelligence Gateway
- ✅ Frontend can fetch/create events

### REQUIREMENT 3.2: Memory Service

**Status:** NOT FOUND in backend audit  
**Frontend Impact:** Living Memory features broken (5 view types)

**Frontend Expects:**
```
GET /api/v1/memory/items - List all memories
POST /api/v1/memory/items - Create memory
GET /api/v1/memory/items/:id - Get memory
PATCH /api/v1/memory/items/:id - Update memory
DELETE /api/v1/memory/items/:id - Delete memory
POST /api/v1/memory/search - Search memories
GET /api/v1/memory/stats - Get statistics
```

**Implementation:**

1. **Check if functionality exists elsewhere**
   - Search for "memory" in all services
   - Check if Living Memory is part of another service
   - Review AI Assistant for memory management

2. **If building new service:**

   ```typescript
   // Memory Service - Core implementation
   interface Memory {
     id: string;
     tenant_id: string;
     user_id: string;
     content: string;
     type: 'note' | 'task' | 'decision' | 'insight';
     metadata: {
       source?: string;
       project_id?: string;
       tags?: string[];
     };
     created_at: Date;
     updated_at: Date;
   }
   
   // Storage: Firestore collection "memories"
   // Index: tenant_id, user_id, created_at
   ```

3. **Semantic Search Implementation:**
   - Generate embeddings for memory content (OpenAI Embeddings)
   - Store vectors in Firestore or vector database
   - Implement similarity search

4. **Deploy service:**
   ```bash
   gcloud run deploy memory-service \
     --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/memory-service:latest \
     --region us-central1
   ```

**Acceptance Criteria:**
- ✅ All CRUD operations working
- ✅ Search functionality implemented
- ✅ Tenant isolation enforced
- ✅ Frontend can use all 5 view types

### REQUIREMENT 3.3: Research Coordinator

**Status:** Code exists, NOT DEPLOYED  
**Frontend Impact:** Research sessions features broken

**Implementation:**

1. **Deploy existing service:**
   ```bash
   gcloud run deploy research-coordinator \
     --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/research-coordinator:latest \
     --region us-central1 \
     --service-account xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com
   ```

2. **Verify endpoints match frontend expectations:**
   ```
   GET /api/v1/research-sessions - List sessions
   POST /api/v1/research-sessions - Create session
   GET /api/v1/research-sessions/:id - Get session
   PATCH /api/v1/research-sessions/:id - Update session
   POST /api/v1/research-sessions/:id/complete - Complete session
   DELETE /api/v1/research-sessions/:id - Delete session
   ```

3. **Configure Firestore collections:**
   - Collection: `research_sessions`
   - Fields: id, tenant_id, user_id, topic, status, findings, created_at

4. **Add route in Intelligence Gateway:**
   ```typescript
   routes['/api/v1/research-sessions'] = 'research-coordinator';
   ```

5. **Enable WebSocket events:**
   - `research:session_started`
   - `research:finding_added`
   - `research:session_completed`

**Acceptance Criteria:**
- ✅ Service deployed successfully
- ✅ All endpoints working
- ✅ WebSocket events broadcasting
- ✅ Frontend research features functional

---

## SECTION 4: OAUTH CONFIGURATION

### REQUIREMENT 4.1: Slack OAuth Setup

**Status:** Service deployed in MOCK MODE - no real data

**Implementation Steps:**

1. **Create Slack App**
   - Go to https://api.slack.com/apps
   - Create new app
   - Configure OAuth scopes:
     - `channels:read` - Read channel info
     - `channels:history` - Read messages
     - `chat:write` - Send messages
     - `users:read` - Read user info
     - `search:read` - Search messages

2. **Configure Redirect URL:**
   ```
   https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/oauth/callback
   ```

3. **Store credentials in Secret Manager:**
   ```bash
   echo -n "xoxb-your-slack-token" | gcloud secrets create SLACK_CLIENT_ID --data-file=-
   echo -n "your-secret" | gcloud secrets create SLACK_CLIENT_SECRET --data-file=-
   echo -n "your-signing-secret" | gcloud secrets create SLACK_SIGNING_SECRET --data-file=-
   ```

4. **Update slack-intelligence-service:**
   - Remove mock mode flag
   - Configure to use real Slack API
   - Implement token refresh logic

5. **Test OAuth flow:**
   - User initiates connection
   - Redirect to Slack OAuth
   - Callback receives code
   - Exchange code for token
   - Store token encrypted
   - Fetch real Slack data

**Acceptance Criteria:**
- ✅ OAuth flow completes successfully
- ✅ Real Slack messages appear in frontend
- ✅ Token refresh working
- ✅ No mock data

### REQUIREMENT 4.2: Gmail OAuth Setup

**Status:** Service deployed in MOCK MODE - no real data

**Implementation Steps:**

1. **Enable Gmail API:**
   ```bash
   gcloud services enable gmail.googleapis.com --project=xynergy-dev-1757909467
   ```

2. **Create OAuth credentials:**
   - Console: APIs & Services > Credentials
   - Create OAuth 2.0 Client ID
   - Application type: Web application
   - Authorized redirect URIs:
     ```
     https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/oauth/callback
     ```

3. **Configure OAuth scopes:**
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`

4. **Store credentials:**
   ```bash
   echo -n "your-client-id" | gcloud secrets create GMAIL_CLIENT_ID --data-file=-
   echo -n "your-client-secret" | gcloud secrets create GMAIL_CLIENT_SECRET --data-file=-
   ```

5. **Update gmail-intelligence-service:**
   - Remove mock mode
   - Configure Gmail API client
   - Implement OAuth token storage
   - Add token refresh logic

6. **Test with real Gmail account:**
   - Complete OAuth flow
   - Fetch real emails
   - Verify AI analysis works
   - Test email sending

**Acceptance Criteria:**
- ✅ OAuth flow working
- ✅ Real Gmail messages fetched
- ✅ Email sending works
- ✅ Token refresh implemented
- ✅ No mock data

---

## SECTION 5: INTELLIGENCE GATEWAY ENHANCEMENTS

### REQUIREMENT 5.1: Add Missing Routes

**Current Routes (Working):**
```typescript
✅ /api/xynergyos/v2/slack/* → slack-intelligence-service
✅ /api/xynergyos/v2/gmail/* → gmail-intelligence-service
✅ /api/xynergyos/v2/crm/* → crm-engine
```

**Required New Routes:**

| Frontend Path | Backend Service | Priority |
|---------------|----------------|----------|
| `/api/v2/calendar/*` | calendar-intelligence-service | P0 |
| `/api/v1/memory/*` | memory-service | P0 |
| `/api/v1/research-sessions/*` | research-coordinator | P0 |
| `/api/v1/ai/query` | ai-assistant-service | P0 |
| `/api/v1/aso/*` | aso-engine | P1 |
| `/api/v1/marketing/*` | marketing-engine | P1 |

**Implementation:**

```typescript
// Intelligence Gateway - Enhanced routing
const serviceMap = {
  // Phase 2A Communication Services
  '/api/v2/slack': 'slack-intelligence-service',
  '/api/v2/email': 'gmail-intelligence-service', // Note: maps to gmail
  '/api/v2/calendar': 'calendar-intelligence-service',
  '/api/v2/crm': 'crm-engine',
  
  // Core Services
  '/api/v1/memory': 'memory-service',
  '/api/v1/research-sessions': 'research-coordinator',
  '/api/v1/ai/query': 'ai-assistant-service',
  
  // Platform Services
  '/api/v1/aso': 'aso-engine',
  '/api/v1/marketing': 'marketing-engine',
  '/api/v1/projects': 'project-management-service',
  '/api/v1/financial': 'financial-analytics-service',
  
  // Legacy paths (for backward compatibility)
  '/api/xynergyos/v2/slack': 'slack-intelligence-service',
  '/api/xynergyos/v2/gmail': 'gmail-intelligence-service',
};

app.use(async (req, res, next) => {
  // Find matching service
  const service = findMatchingService(req.path, serviceMap);
  
  if (!service) {
    return res.status(404).json({ error: 'Service not found' });
  }
  
  // Route to service
  await proxyRequest(req, res, service);
});
```

**Acceptance Criteria:**
- ✅ All frontend paths route correctly
- ✅ Backward compatibility maintained
- ✅ 404s only for truly missing endpoints

### REQUIREMENT 5.2: WebSocket Event Broadcasting

**Frontend Expects Real-Time Events:**

```typescript
// Events frontend is listening for
socket.on('slack:new_message', handler);
socket.on('slack:intelligence_updated', handler);
socket.on('email:new_message', handler);
socket.on('email:intelligence_updated', handler);
socket.on('calendar:event_added', handler);
socket.on('calendar:prep_ready', handler);
socket.on('crm:contact_created', handler);
socket.on('crm:interaction_logged', handler);
socket.on('workflow:update', handler);
```

**Implementation:**

1. **Backend services emit events to Pub/Sub:**
   ```python
   # In slack-intelligence-service
   publisher.publish('xynergyos-events', {
     'event': 'slack:new_message',
     'tenant_id': tenant_id,
     'data': message_data
   })
   ```

2. **Intelligence Gateway subscribes to events:**
   ```typescript
   // Gateway subscribes to Pub/Sub topic
   subscription.on('message', (message) => {
     const event = JSON.parse(message.data);
     
     // Broadcast to connected WebSocket clients
     io.to(event.tenant_id).emit(event.event, event.data);
     
     message.ack();
   });
   ```

3. **Test event flow:**
   - Backend service → Pub/Sub → Gateway → Frontend
   - Verify tenant isolation
   - Confirm no event leakage between tenants

**Acceptance Criteria:**
- ✅ All backend events reach frontend
- ✅ Tenant isolation enforced
- ✅ No cross-tenant event leakage
- ✅ WebSocket connections stable

---

## SECTION 6: CONFIGURATION & ENVIRONMENT

### REQUIREMENT 6.1: Frontend Environment Variables

**Frontend needs these values:**

```env
# Authentication
REACT_APP_FIREBASE_API_KEY=<firebase-api-key>
REACT_APP_FIREBASE_AUTH_DOMAIN=<project-id>.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=<project-id>

# API Endpoints
REACT_APP_API_BASE_URL=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
REACT_APP_WS_URL=wss://xynergyos-intelligence-gateway-835612502919.us-central1.run.app

# Feature Flags (optional)
REACT_APP_ENABLE_SLACK=true
REACT_APP_ENABLE_GMAIL=true
REACT_APP_ENABLE_CALENDAR=true
```

**Deliverable:** Document these values and provide to frontend team.

### REQUIREMENT 6.2: CORS Configuration

**Problem:** Frontend origin not allowed by backend.

**Solution:** Configure CORS in Intelligence Gateway.

```typescript
// Intelligence Gateway - CORS config
import cors from 'cors';

const allowedOrigins = [
  'https://xynergyos-frontend-835612502919.us-central1.run.app',
  'http://localhost:3000', // Development
  'http://localhost:3001', // Alternative dev port
];

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
```

**Acceptance Criteria:**
- ✅ Frontend can make API calls
- ✅ Credentials included in requests
- ✅ No CORS errors in browser console

---

## SECTION 7: INTEGRATION TESTING

### REQUIREMENT 7.1: Create Integration Test Suite

**Purpose:** Validate frontend-backend connectivity works end-to-end.

**Test Categories:**

1. **Authentication Tests**
   ```typescript
   describe('Authentication', () => {
     it('should login with valid credentials', async () => {
       const response = await api.post('/api/v1/auth/login', {
         email: 'test@example.com',
         password: 'test123'
       });
       expect(response.status).toBe(200);
       expect(response.data.token).toBeDefined();
     });
     
     it('should reject invalid token', async () => {
       const response = await api.get('/api/v2/slack/messages', {
         headers: { Authorization: 'Bearer invalid-token' }
       });
       expect(response.status).toBe(401);
     });
   });
   ```

2. **CRM Tests**
   ```typescript
   describe('CRM', () => {
     it('should list contacts', async () => {
       const response = await authenticatedApi.get('/api/v2/crm/contacts');
       expect(response.status).toBe(200);
       expect(Array.isArray(response.data)).toBe(true);
     });
     
     it('should create contact', async () => {
       const response = await authenticatedApi.post('/api/v2/crm/contacts', {
         name: 'Test Contact',
         email: 'test@example.com'
       });
       expect(response.status).toBe(201);
       expect(response.data.id).toBeDefined();
     });
   });
   ```

3. **Communication Tests**
   ```typescript
   describe('Communication', () => {
     it('should fetch Slack messages', async () => {
       const response = await authenticatedApi.get('/api/v2/slack/messages');
       expect(response.status).toBe(200);
     });
     
     it('should fetch Gmail messages', async () => {
       const response = await authenticatedApi.get('/api/v2/email/messages');
       expect(response.status).toBe(200);
     });
   });
   ```

4. **WebSocket Tests**
   ```typescript
   describe('WebSocket', () => {
     it('should connect successfully', (done) => {
       const socket = io(WS_URL, {
         auth: { token: validToken }
       });
       
       socket.on('connect', () => {
         expect(socket.connected).toBe(true);
         socket.disconnect();
         done();
       });
     });
     
     it('should receive real-time events', (done) => {
       const socket = io(WS_URL, { auth: { token: validToken } });
       
       socket.on('slack:new_message', (data) => {
         expect(data).toBeDefined();
         socket.disconnect();
         done();
       });
       
       // Trigger event in backend
       triggerSlackMessage();
     });
   });
   ```

**Test Infrastructure:**

```bash
# Run integration tests
npm run test:integration

# Run against staging
API_URL=https://staging-gateway.com npm run test:integration

# Run against production (smoke tests only)
API_URL=https://prod-gateway.com npm run test:integration:smoke
```

**Acceptance Criteria:**
- ✅ All critical paths tested
- ✅ Tests run in CI/CD
- ✅ >80% pass rate required for deploy
- ✅ Tests run against staging before production

---

## SECTION 8: MONITORING & OBSERVABILITY

### REQUIREMENT 8.1: Integration Health Dashboard

**Purpose:** Monitor frontend-backend connection health in production.

**Metrics to Track:**

1. **Request Metrics:**
   - Total requests per endpoint
   - Error rate by endpoint
   - Response latency (p50, p95, p99)
   - Requests by frontend origin

2. **Authentication Metrics:**
   - Login success rate
   - Token validation failures
   - Authentication latency

3. **WebSocket Metrics:**
   - Active connections
   - Connection duration
   - Disconnection rate
   - Events broadcast per minute

4. **Service Health:**
   - Service availability (200 vs 5xx)
   - Circuit breaker states
   - Dependency health (Slack, Gmail, Calendar)

**Implementation:**

```typescript
// Intelligence Gateway - Metrics collection
import { collectDefaultMetrics, Counter, Histogram } from 'prom-client';

const requestCounter = new Counter({
  name: 'gateway_requests_total',
  help: 'Total requests',
  labelNames: ['method', 'path', 'status', 'origin']
});

const requestDuration = new Histogram({
  name: 'gateway_request_duration_seconds',
  help: 'Request duration',
  labelNames: ['method', 'path'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

app.use((req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    
    requestCounter.inc({
      method: req.method,
      path: req.path,
      status: res.statusCode,
      origin: req.headers.origin
    });
    
    requestDuration.observe({
      method: req.method,
      path: req.path
    }, duration);
  });
  
  next();
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(register.metrics());
});
```

**Dashboard Configuration:**

```yaml
# Cloud Monitoring Dashboard
dashboard:
  name: "XynergyOS Integration Health"
  widgets:
    - title: "Request Rate"
      type: line_chart
      metric: gateway_requests_total
      
    - title: "Error Rate"
      type: line_chart
      metric: gateway_requests_total
      filter: status>=400
      
    - title: "Response Latency"
      type: line_chart
      metric: gateway_request_duration_seconds
      percentiles: [50, 95, 99]
      
    - title: "WebSocket Connections"
      type: gauge
      metric: gateway_websocket_connections
      
    - title: "Service Health"
      type: table
      metrics:
        - gateway_service_availability
        - gateway_circuit_breaker_state
```

### REQUIREMENT 8.2: Alerting Rules

**Critical Alerts (Page immediately):**
- Error rate > 10% for 5 minutes
- All services returning 5xx
- WebSocket disconnection rate > 50%
- Authentication failure rate > 25%

**Warning Alerts (Slack notification):**
- Error rate > 5% for 10 minutes
- Response latency p95 > 2 seconds
- Single service unavailable

**Implementation:**

```bash
# Create alerting policy
gcloud alpha monitoring policies create \
  --notification-channels=<channel-id> \
  --display-name="Integration Error Rate" \
  --condition-display-name="Error rate >10%" \
  --condition-threshold-value=0.10 \
  --condition-threshold-duration=300s
```

**Acceptance Criteria:**
- ✅ Dashboard shows real-time metrics
- ✅ Alerts configured and tested
- ✅ Team receives notifications
- ✅ Runbook created for common issues

---

## SECTION 9: DEPLOYMENT PLAN

### Phase 1: Authentication & Routes (Week 1)

**Day 1-2: Authentication**
- [ ] Decide on authentication approach (JWT vs Firebase)
- [ ] Implement JWT validation in Intelligence Gateway
- [ ] Test authentication flow end-to-end
- [ ] Document for frontend team

**Day 3-4: Route Standardization**
- [ ] Audit xynergyos-backend endpoints
- [ ] Create API mapping document
- [ ] Add route aliases in gateway
- [ ] Test all frontend paths

**Day 5: Validation**
- [ ] Integration test suite (basic)
- [ ] Frontend can authenticate
- [ ] Frontend can hit all endpoints (even if stubbed)

### Phase 2: Missing Services (Week 2)

**Day 1-2: Calendar Service**
- [ ] Determine if service exists (search codebase)
- [ ] If missing, create service (clone Gmail template)
- [ ] Deploy to Cloud Run
- [ ] Add route in gateway
- [ ] Test endpoints

**Day 3: Memory Service**
- [ ] Check if functionality exists elsewhere
- [ ] If missing, create service
- [ ] Implement Firestore storage
- [ ] Deploy and route

**Day 4: Research Coordinator**
- [ ] Deploy existing service
- [ ] Verify endpoints
- [ ] Enable WebSocket events
- [ ] Test integration

**Day 5: Validation**
- [ ] All services accessible
- [ ] Integration tests passing
- [ ] Frontend features working (mock data okay)

### Phase 3: OAuth & Production Data (Week 3)

**Day 1-2: Slack OAuth**
- [ ] Create Slack app
- [ ] Configure OAuth
- [ ] Store credentials in Secret Manager
- [ ] Update service to use real API
- [ ] Test OAuth flow

**Day 3-4: Gmail OAuth**
- [ ] Enable Gmail API
- [ ] Create OAuth credentials
- [ ] Configure service
- [ ] Test with real Gmail

**Day 5: Validation**
- [ ] Remove all mock modes
- [ ] Verify real data flowing
- [ ] Test end-to-end with production APIs

### Phase 4: Testing & Monitoring (Week 4)

**Day 1-2: Integration Tests**
- [ ] Expand test coverage
- [ ] Add WebSocket tests
- [ ] Test error scenarios
- [ ] Integrate into CI/CD

**Day 3-4: Monitoring**
- [ ] Deploy metrics collection
- [ ] Create dashboard
- [ ] Configure alerts
- [ ] Test alerting

**Day 5: Production Readiness**
- [ ] Load testing
- [ ] Security review
- [ ] Documentation complete
- [ ] Runbook created
- [ ] GO/NO-GO decision

---

## SECTION 10: SUCCESS CRITERIA

### Integration Complete When:

**Authentication:**
- ✅ Frontend can login with Firebase Auth
- ✅ Token validation working in gateway
- ✅ User context passed to all services
- ✅ Invalid tokens rejected (401)

**API Connectivity:**
- ✅ All 40+ frontend endpoints working
- ✅ No 404 errors for expected paths
- ✅ API responses in expected format
- ✅ Error handling consistent

**Services:**
- ✅ Calendar Intelligence Service deployed and working
- ✅ Memory Service deployed and working
- ✅ Research Coordinator deployed and working
- ✅ All services routed through gateway

**OAuth:**
- ✅ Slack OAuth flow working
- ✅ Gmail OAuth flow working
- ✅ Real data from Slack (no mocks)
- ✅ Real data from Gmail (no mocks)
- ✅ Token refresh implemented

**Real-Time:**
- ✅ WebSocket connections stable
- ✅ Events broadcasting correctly
- ✅ Tenant isolation enforced
- ✅ No cross-tenant leakage

**Quality:**
- ✅ Integration tests passing (>80%)
- ✅ Monitoring dashboard operational
- ✅ Alerts configured and tested
- ✅ Documentation complete

**User Experience:**
- ✅ All 30+ frontend pages load
- ✅ No console errors
- ✅ Features functional end-to-end
- ✅ Performance acceptable (<1s load time)

---

## SECTION 11: RISKS & MITIGATION

### Risk 1: OAuth Approval Delays
**Impact:** Can't use real Slack/Gmail data  
**Probability:** Medium  
**Mitigation:**
- Apply for OAuth immediately (don't wait)
- Continue development with mock data
- Have approval process documentation ready

**Contingency:** Launch with limited OAuth (read-only) then expand.

### Risk 2: Service Discovery Issues
**Impact:** Calendar/Memory services might not exist  
**Probability:** High for Calendar, Medium for Memory  
**Mitigation:**
- Audit codebase immediately (Week 1, Day 1)
- Have service templates ready
- Allocate time for new service development

**Contingency:** Build new services if not found (included in timeline).

### Risk 3: Authentication Integration Complexity
**Impact:** JWT integration takes longer than expected  
**Probability:** Low  
**Mitigation:**
- Choose simpler option (JWT in gateway)
- Have Firebase Admin SDK docs ready
- Allocate extra day for testing

**Contingency:** Option B (frontend change) as fallback.

### Risk 4: WebSocket Scaling Issues
**Impact:** Connections drop under load  
**Probability:** Low  
**Mitigation:**
- Load test early
- Use Redis pub/sub for multi-instance support
- Monitor connection count

**Contingency:** Increase gateway instances, add connection pooling.

### Risk 5: API Format Mismatches
**Impact:** Frontend expects different data shape  
**Probability:** Medium  
**Mitigation:**
- Create transformation layer in gateway
- Document all format differences
- Test with frontend team early

**Contingency:** Add API versioning, support both formats temporarily.

---

## SECTION 12: ROLLBACK PLAN

### If Integration Fails After Deployment

**Immediate Rollback (< 5 minutes):**
1. Revert Intelligence Gateway to previous version
2. Restore previous routing configuration
3. Re-enable mock mode in services
4. Notify frontend team

**Partial Rollback (< 15 minutes):**
1. Keep authentication changes
2. Revert specific service deployments
3. Use feature flags to disable broken features
4. Continue investigation

**Full System Rollback (< 30 minutes):**
1. Revert all backend changes
2. Restore previous gateway version
3. Frontend continues with mock data
4. Schedule post-mortem

### Rollback Decision Criteria

**Immediate rollback if:**
- Error rate > 25% for 5 minutes
- All services returning 5xx
- Complete authentication failure
- Data corruption detected

**Partial rollback if:**
- Single service failure
- Performance degradation > 3x
- OAuth issues (not critical)
- Non-critical features broken

**Continue forward if:**
- Error rate < 10%
- Individual endpoint issues (can be patched)
- Performance within acceptable range
- User experience acceptable

---

## SECTION 13: DELIVERABLES

### Documentation

1. **API Endpoint Mapping** - Complete mapping of frontend to backend
2. **Authentication Guide** - How frontend authenticates
3. **Environment Variables** - All config values for frontend
4. **OAuth Setup Guide** - Instructions for Slack/Gmail
5. **Integration Test Documentation** - How to run tests
6. **Monitoring Runbook** - How to read dashboard, respond to alerts
7. **Troubleshooting Guide** - Common issues and solutions

### Code

1. **Intelligence Gateway Updates** - JWT auth, routes, WebSocket
2. **Calendar Intelligence Service** - New or deployed existing
3. **Memory Service** - New or deployed existing
4. **Research Coordinator Deployment** - Deployed and configured
5. **Integration Test Suite** - Automated tests in CI/CD
6. **Monitoring Configuration** - Dashboard and alerts

### Deployment

1. **All services deployed to Cloud Run**
2. **OAuth configured and tested**
3. **Secrets stored in Secret Manager**
4. **CI/CD pipeline updated**
5. **Staging environment validated**
6. **Production deployment checklist**

---

## SECTION 14: POST-INTEGRATION TASKS

### Week 5: Optimization

- [ ] Monitor performance metrics
- [ ] Optimize slow endpoints
- [ ] Adjust caching strategies
- [ ] Fine-tune rate limits

### Week 6: Enhancement

- [ ] Add more integration tests
- [ ] Improve error messages
- [ ] Enhance monitoring dashboards
- [ ] Document lessons learned

### Ongoing

- [ ] Weekly integration health review
- [ ] Monthly OAuth token audit
- [ ] Quarterly security review
- [ ] Continuous performance optimization

---

## APPENDIX A: TECHNOLOGY STACK

### Intelligence Gateway
- **Runtime:** Node.js 20 or Python 3.11
- **Framework:** Express.js or FastAPI
- **Auth:** Firebase Admin SDK
- **WebSocket:** Socket.io or python-socketio
- **Metrics:** Prometheus client
- **Deployment:** Cloud Run

### Missing Services (if building new)
- **Framework:** Match existing services (FastAPI for Python)
- **Database:** Firestore
- **Storage:** Cloud Storage
- **Auth:** Service-to-service via service account
- **Deployment:** Cloud Run

### Testing
- **Framework:** Jest (Node) or pytest (Python)
- **Integration Tests:** Supertest or httpx
- **Load Testing:** k6 or Locust
- **CI/CD:** GitHub Actions

---

## APPENDIX B: CONTACT & SUPPORT

### Project Contacts

**Technical Lead:** [TBD]  
**Frontend Lead:** [TBD]  
**Backend Lead:** [TBD]  
**DevOps:** [TBD]  

### Resources

**Documentation:** /project-docs/integration/  
**Code Repository:** https://github.com/[org]/xynergy-platform  
**Issue Tracker:** [Link]  
**Slack Channel:** #xynergyos-integration  

### Support Escalation

**P0 Issues (Integration blocked):**
1. Post in #xynergyos-integration
2. Page on-call engineer
3. Escalate to Technical Lead within 30 minutes

**P1 Issues (Features broken):**
1. Post in #xynergyos-integration
2. Create GitHub issue
3. Assign to relevant team

**P2 Issues (Non-critical):**
1. Create GitHub issue
2. Add to sprint backlog
3. Prioritize in planning

---

## DOCUMENT METADATA

**Version:** 1.0  
**Date:** October 13, 2025  
**Type:** Integration Requirements (Backend Focus)  
**Timeline:** 4 weeks  
**Based On:** Frontend Integration Requirements Report  
**Status:** Ready for implementation  

**Change History:**
- 2025-10-13 v1.0: Initial version based on integration review

**Approval Required From:**
- [ ] Technical Lead
- [ ] Frontend Lead
- [ ] Backend Lead
- [ ] Product Owner

---

**This document provides complete backend platform requirements to enable XynergyOS frontend-backend integration. Implementation focus is on connecting existing systems and filling critical gaps - not building new features.**

**All referenced services exist except Calendar and Memory services. Timeline assumes Calendar/Memory can be created if missing. OAuth is the main external dependency.**

**Integration is the critical path. Until complete, XynergyOS cannot launch.**