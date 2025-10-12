# Intelligence Gateway - Implementation Requirements
**For: Claude Code in Platform Folder**

## OVERVIEW

Build a new TypeScript/Node.js service called `xynergyos-intelligence-gateway` that acts as the API gateway for:
1. ClearForge Website (public, unauthenticated routes)
2. XynergyOS Application (authenticated, Firebase Auth routes)
3. Real-time WebSocket communication

This service routes requests to existing backend services and handles authentication centrally.

---

## TECHNICAL SPECIFICATIONS

**Service Name:** `xynergyos-intelligence-gateway`
**Technology:** Node.js 20 + TypeScript 5 + Express.js + Socket.io
**Port:** 8080
**Deployment:** Google Cloud Run
**Region:** us-central1
**Project:** xynergy-dev-1757909467
**Service Account:** xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com

**Resources:**
- CPU: 2 vCPU
- Memory: 2Gi
- Min Instances: 1
- Max Instances: 20
- Timeout: 300s

---

## REQUIRED ENDPOINTS

### PUBLIC ROUTES (No Authentication)

These routes are for the ClearForge marketing website:

```typescript
// Beta Program Applications
POST /api/public/beta
Body: {
  company_name: string;
  contact_name: string;
  email: string;
  industry: string;
  phone?: string;
  website?: string;
  goals: string;
  interests?: string[];
  referred_by?: string;
}
Response: { success: boolean; application_id: string; message: string; }

// Contact Form Submissions
POST /api/public/contact
Body: {
  name: string;
  email: string;
  message: string;
  phone?: string;
  company?: string;
}
Response: { success: boolean; submission_id: string; message: string; }

// ASO Opportunities
GET /api/public/aso/opportunities?limit=10
Response: {
  opportunities: Array<{
    keyword: string;
    search_volume: number;
    difficulty: number;
    opportunity_score: number;
  }>;
}
```

### AUTHENTICATED ROUTES (Requires Firebase Auth)

These routes are for the XynergyOS application (Phase 2A - future):

```typescript
// Slack Intelligence
GET /api/v2/slack/intelligence/pending
GET /api/v2/slack/intelligence/:id
POST /api/v2/slack/responses
POST /api/v2/slack/intelligence/:id/dismiss

// Gmail Intelligence  
GET /api/v2/email/intelligence/pending
GET /api/v2/email/intelligence/:id
POST /api/v2/email/responses

// Calendar
GET /api/v2/calendar/events
GET /api/v2/calendar/today

// CRM
GET /api/v2/crm/contacts
POST /api/v2/crm/contacts
GET /api/v2/crm/contacts/:id
PATCH /api/v2/crm/contacts/:id
```

### WEBSOCKET

```typescript
// WebSocket connection for real-time updates
WS /api/v2/stream
- Requires Firebase Auth token in query: ?token=xxx
- Emits: slack_update, email_update, calendar_update, crm_update
- Receives: subscribe, unsubscribe
```

### HEALTH CHECKS

```typescript
GET /health
Response: { status: "healthy", service: "xynergyos-intelligence-gateway", version: "1.0.0" }

GET /health/deep
Response: { 
  status: "healthy",
  checks: {
    firestore: "healthy",
    redis: "healthy", 
    aiRouting: "healthy"
  }
}
```

---

## DIRECTORY STRUCTURE

Create this structure in `platform/xynergyos-intelligence-gateway/`:

```
xynergyos-intelligence-gateway/
├── src/
│   ├── index.ts                    # Entry point
│   ├── server.ts                   # Express setup
│   ├── config/
│   │   ├── config.ts               # Environment config
│   │   └── firebase.ts             # Firebase Admin SDK
│   ├── middleware/
│   │   ├── auth.ts                 # Firebase Auth middleware
│   │   ├── rateLimit.ts            # Rate limiting
│   │   ├── errorHandler.ts         # Error handling
│   │   └── cors.ts                 # CORS config
│   ├── routes/
│   │   ├── health.ts               # Health check routes
│   │   ├── public.ts               # Public routes (website)
│   │   ├── slack.ts                # Slack routes (future)
│   │   ├── email.ts                # Email routes (future)
│   │   ├── calendar.ts             # Calendar routes (future)
│   │   └── crm.ts                  # CRM routes (future)
│   ├── services/
│   │   ├── serviceRouter.ts        # Routes to backend services
│   │   ├── websocket.ts            # WebSocket management
│   │   └── redis.ts                # Redis client
│   └── utils/
│       ├── logger.ts               # Winston logger
│       └── validators.ts           # Input validation
├── tests/
│   ├── integration/
│   └── unit/
├── Dockerfile
├── .dockerignore
├── package.json
├── tsconfig.json
└── .env.example
```

---

## AUTHENTICATION STRATEGY

**Two Authentication Modes:**

### 1. Public Routes (Website)
- No Firebase Auth required
- Rate limiting by IP: 5 requests/minute
- Simple validation of input fields

```typescript
// Middleware
app.post('/api/public/beta', 
  rateLimitByIP(5, 60000), // 5 req/min
  validateBetaInput,
  handleBetaApplication
);
```

### 2. Authenticated Routes (XynergyOS)
- Requires Firebase Auth ID token
- Token passed in Authorization header: `Bearer <token>`
- Validates token with Firebase Admin SDK
- Extracts user ID and tenant ID from token

```typescript
// Middleware
app.get('/api/v2/slack/intelligence/pending',
  requireFirebaseAuth, // Validates token
  handleSlackIntelligence
);
```

---

## SERVICE ROUTING CONFIGURATION

The gateway routes to these existing backend services:

```typescript
// Environment variables for backend service URLs
AI_ROUTING_URL=https://xynergy-ai-routing-engine-835612502919.us-central1.run.app
MARKETING_ENGINE_URL=https://xynergy-marketing-engine-835612502919.us-central1.run.app
ASO_ENGINE_URL=https://xynergy-aso-engine-835612502919.us-central1.run.app
PLATFORM_DASHBOARD_URL=https://xynergy-platform-dashboard-835612502919.us-central1.run.app

// Future Phase 2A services (not built yet)
SLACK_INTELLIGENCE_URL=
GMAIL_INTELLIGENCE_URL=
CALENDAR_INTELLIGENCE_URL=
CRM_ENGINE_URL=
```

**Routing Logic:**

```typescript
// Public routes route to existing services:
POST /api/public/beta → Marketing Engine → Store in Firestore
POST /api/public/contact → Marketing Engine → Send notification
GET /api/public/aso/opportunities → ASO Engine → Return data

// Authenticated routes route to Phase 2A services (future):
GET /api/v2/slack/* → Slack Intelligence Service
GET /api/v2/email/* → Gmail Intelligence Service
GET /api/v2/calendar/* → Calendar Intelligence Service
GET /api/v2/crm/* → CRM Engine
```

---

## KEY IMPLEMENTATION REQUIREMENTS

### 1. Rate Limiting (In-Memory)
- Track requests per IP address
- 5 requests per minute for public routes
- Use Map with cleanup interval
- Return 429 Too Many Requests when exceeded

### 2. Error Handling
- Catch all errors and return consistent format
- Log errors with Winston
- Never expose internal error details to clients
- Return appropriate HTTP status codes

### 3. Firebase Auth Integration
- Initialize Firebase Admin SDK with service account
- Verify ID tokens on authenticated routes
- Extract uid, email, tenantId from decoded token
- Return 401 Unauthorized for invalid tokens

### 4. Service Communication
- Use Axios for HTTP requests to backend services
- Implement retry logic (2 retries with exponential backoff)
- Set timeout: 30 seconds
- Handle service unavailable errors gracefully

### 5. WebSocket Setup
- Use Socket.io for WebSocket server
- Authenticate connections via Firebase token in query string
- Support room-based subscriptions (per user)
- Emit events: slack_update, email_update, calendar_update
- Use Redis adapter for multi-instance support

### 6. Logging
- Use Winston for structured logging
- Log levels: error, warn, info, debug
- Include request ID, user ID, timestamp
- Log to console (Cloud Run captures stdout)

### 7. CORS Configuration
- Allow origins: localhost:3000 (dev), clearforge website, xynergyos frontend
- Allow methods: GET, POST, PATCH, DELETE
- Allow credentials: true
- Allow headers: Authorization, Content-Type

---

## ENVIRONMENT VARIABLES

Create `.env.example`:

```bash
# Server
PORT=8080
NODE_ENV=development

# GCP
GCP_PROJECT_ID=xynergy-dev-1757909467
GCP_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Firebase
FIREBASE_PROJECT_ID=xynergy-dev-1757909467

# Redis
REDIS_HOST=10.0.0.3
REDIS_PORT=6379
REDIS_PASSWORD=

# Backend Service URLs
AI_ROUTING_URL=https://xynergy-ai-routing-engine-835612502919.us-central1.run.app
MARKETING_ENGINE_URL=https://xynergy-marketing-engine-835612502919.us-central1.run.app
ASO_ENGINE_URL=https://xynergy-aso-engine-835612502919.us-central1.run.app
SLACK_INTELLIGENCE_URL=
GMAIL_INTELLIGENCE_URL=
CALENDAR_INTELLIGENCE_URL=
CRM_ENGINE_URL=

# CORS
CORS_ORIGINS=http://localhost:3000,https://clearforge-website-835612502919.us-central1.run.app
```

---

## DOCKERFILE

Multi-stage build for optimized image:

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json tsconfig.json ./
RUN npm ci
COPY src ./src
RUN npm run build

# Production stage
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
ENV NODE_ENV=production PORT=8080
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD node -e "require('http').get('http://localhost:8080/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"
CMD ["node", "dist/index.js"]
```

---

## DEPLOYMENT COMMANDS

```bash
# Build and push
docker build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergyos-intelligence-gateway:latest .

docker push us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergyos-intelligence-gateway:latest

# Deploy to Cloud Run
gcloud run deploy xynergyos-intelligence-gateway \
  --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergyos-intelligence-gateway:latest \
  --platform managed \
  --region us-central1 \
  --project xynergy-dev-1757909467 \
  --service-account xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com \
  --set-env-vars "GCP_PROJECT_ID=xynergy-dev-1757909467,GCP_REGION=us-central1,REDIS_HOST=10.0.0.3,REDIS_PORT=6379" \
  --min-instances 1 \
  --max-instances 20 \
  --cpu 2 \
  --memory 2Gi \
  --timeout 300 \
  --allow-unauthenticated \
  --port 8080

# Verify
curl https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/health
```

---

## CRITICAL IMPLEMENTATION NOTES

### For Public Routes (Priority 1)

**Immediate needs for ClearForge website:**

1. **POST /api/public/beta** 
   - Store in Firestore collection: `beta_applications`
   - Send notification to team (email or Slack)
   - Return application_id

2. **POST /api/public/contact**
   - Store in Firestore collection: `contact_submissions`
   - Send notification to team
   - Return submission_id

3. **GET /api/public/aso/opportunities**
   - Call ASO Engine: GET /api/v1/opportunities
   - Transform and return data
   - Cache in Redis for 1 hour

### For Authenticated Routes (Priority 2 - Future)

Build structure but stub out with 501 Not Implemented:

```typescript
app.get('/api/v2/slack/intelligence/pending', requireAuth, (req, res) => {
  res.status(501).json({ 
    error: 'Not Implemented',
    message: 'Slack Intelligence Service not yet deployed'
  });
});
```

This allows frontend development to proceed while backend services are built.

---

## TESTING REQUIREMENTS

### Unit Tests
- Test rate limiter logic
- Test Firebase Auth token validation
- Test service router error handling
- Test input validators

### Integration Tests
- Test health endpoints
- Test public routes with mock backend services
- Test authentication flow
- Test WebSocket connections

### Manual Testing
```bash
# Test health
curl https://localhost:8080/health

# Test beta application (rate limit 5x)
for i in {1..6}; do
  curl -X POST http://localhost:8080/api/public/beta \
    -H "Content-Type: application/json" \
    -d '{"company_name":"Test","contact_name":"User","email":"test@example.com","industry":"Tech","goals":"Test"}' 
done
# 6th request should return 429

# Test WebSocket
npm install -g wscat
wscat -c ws://localhost:8080/api/v2/stream?token=TEST_TOKEN
```

---

## PHASE 1 DELIVERABLE

**Build this first (1-2 weeks):**

1. ✅ Basic Express server with TypeScript
2. ✅ Health check endpoints
3. ✅ Firebase Auth middleware (structure ready, can test later)
4. ✅ Rate limiting middleware
5. ✅ Error handling middleware
6. ✅ CORS configuration
7. ✅ Public routes (beta, contact, aso)
8. ✅ Service router to Marketing Engine and ASO Engine
9. ✅ Logging with Winston
10. ✅ Dockerfile and deployment
11. ✅ Basic WebSocket setup (structure only)

**Stub out for later (Phase 2A):**
- Slack, Email, Calendar, CRM routes (return 501)
- Full WebSocket event handling
- Redis caching (optional for now)

---

## SUCCESS CRITERIA

**The gateway is ready when:**

1. Health check returns 200 OK
2. Can submit beta application and receive application_id
3. Can submit contact form and receive submission_id
4. Can retrieve ASO opportunities
5. Rate limiting blocks 6th request in 1 minute
6. Invalid Firebase token returns 401
7. Service is deployed to Cloud Run and accessible
8. Logs appear in Cloud Logging
9. Returns proper error messages for all error cases

---

## QUESTIONS TO RESOLVE

**Before starting implementation:**

1. ✅ Confirmed: Use TypeScript/Node.js (not Python)
2. ❓ Where exactly should beta applications be stored in Firestore?
   - Suggested: `beta_applications` collection
3. ❓ How should team notifications work?
   - Email? Slack webhook? Both?
4. ❓ Should ASO Engine route be `/api/v1/opportunities` or different?
5. ✅ Confirmed: Start with in-memory rate limiting (not Redis)

---

## EXPECTED TIMELINE

- **Week 1:** Core setup, auth, routing, public endpoints
- **Week 2:** Testing, deployment, debugging, documentation

---

This document provides everything needed to implement the Intelligence Gateway service. Start with Phase 1 deliverables and build incrementally.