# Xynergy Platform - Frontend Integration Requirements

**Project:** XynergyOS Frontend Integration  
**Version:** 1.0  
**Date:** October 11, 2025  
**Status:** READY FOR IMPLEMENTATION  
**Priority:** P0 - CRITICAL BLOCKER

---

## EXECUTIVE SUMMARY

### Purpose
Enable XynergyOS frontend to successfully connect to and communicate with the Xynergy Platform backend services.

### Current State
- Frontend: Fully built UI, cannot connect to backend
- Backend: 30 services deployed, not accessible to frontend
- Integration: 0% functional

### Success Criteria
- Frontend can authenticate users
- Frontend can fetch data from all backend services
- Real-time WebSocket connections work
- All frontend features have corresponding backend endpoints

---

## 1. AUTHENTICATION INTEGRATION

### Requirement: Unified Authentication Strategy

**Problem:** Frontend uses JWT authentication, Intelligence Gateway expects Firebase tokens.

**Decision Required:** Choose ONE authentication approach for the entire platform.

#### Option A: Add JWT Support to Intelligence Gateway (RECOMMENDED)

**Requirements:**
1. Intelligence Gateway must accept JWT tokens in addition to Firebase tokens
2. JWT validation must extract user ID and tenant ID
3. JWT tokens must be issued by a designated authentication service
4. Token format must match frontend expectations:
   - Header: `Authorization: Bearer {jwt_token}`
   - Token contains: `user_id`, `tenant_id`, `email`, `roles`

**Services Affected:**
- `xynergyos-intelligence-gateway` - Add JWT validation middleware

**Implementation Requirements:**
- JWT secret must be stored in Secret Manager
- Token expiration must be configurable (default: 24 hours)
- Refresh token support must be implemented
- Invalid/expired tokens must return 401 with clear error message

#### Option B: Frontend Adopts Firebase Authentication

**Requirements:**
1. Frontend must be updated to use Firebase Authentication SDK
2. Intelligence Gateway configuration remains unchanged
3. Firebase project credentials must be provided to frontend team

**Services Affected:**
- No backend changes required

**Decision Deadline:** Before any other work begins

---

## 2. API ENDPOINT STANDARDIZATION

### Requirement: Consistent API Path Structure

**Problem:** Frontend expects different API paths than backend provides.

**Required Changes:**

#### 2.1 Intelligence Gateway Route Consistency

**Current Backend Paths:**
- `/api/xynergyos/v2/slack/*`
- `/api/xynergyos/v2/gmail/*`
- `/api/xynergyos/v2/crm/*`

**Frontend Expects:**
- `/api/v2/slack/*`
- `/api/v2/email/*` (not gmail)
- `/api/v2/crm/*`

**Requirement:** Intelligence Gateway must accept BOTH path formats and route correctly:
- Accept: `/api/v2/*` OR `/api/xynergyos/v2/*`
- Route to appropriate backend service
- Maintain backward compatibility

#### 2.2 Legacy Backend Endpoints

**Frontend expects these endpoints to exist:**

| Endpoint Pattern | Purpose | Current Status | Required Action |
|------------------|---------|----------------|-----------------|
| `/api/v1/auth/login` | User authentication | Unknown | Verify exists or create |
| `/api/v1/auth/register` | User registration | Unknown | Verify exists or create |
| `/api/v1/dashboard/metrics` | Dashboard data | Unknown | Verify exists or create |
| `/api/v1/projects/*` | Project management | Likely exists | Verify path compatibility |
| `/api/v1/financial/*` | Financial data | Likely exists | Verify path compatibility |
| `/api/v1/ai/query` | AI Assistant | Unknown | Create route to AI Assistant service |

**Requirement:** Audit `xynergyos-backend` service and document all available endpoints.

**Deliverable:** Complete API endpoint mapping document showing:
- What frontend requests
- What backend provides
- Any gaps or mismatches

---

## 3. MISSING BACKEND SERVICES

### Requirement: Deploy Services Frontend Depends On

#### 3.1 Calendar Intelligence Service

**Status:** NOT FOUND in backend report  
**Frontend Usage:** Communication intelligence features, calendar events

**Requirements:**
1. Service must be created if it doesn't exist
2. Must integrate with Google Calendar API
3. Must provide endpoints:
   - `GET /api/v2/calendar/events` - List calendar events
   - `GET /api/v2/calendar/events/:id` - Get event details
   - `POST /api/v2/calendar/events` - Create event
4. Must route through Intelligence Gateway
5. Must support OAuth 2.0 authentication with Google

**Alternative:** If service exists but wasn't documented, deploy it.

#### 3.2 Memory Service

**Status:** NOT FOUND in backend report  
**Frontend Usage:** Memory management features (5 different views)

**Frontend Expects:**
- `GET /api/v1/memory/items` - List memory items
- `POST /api/v1/memory/items` - Create memory
- `PATCH /api/v1/memory/items/:id` - Update memory
- `POST /api/v1/memory/search` - Search memories

**Requirements:**
1. Create Memory Service if it doesn't exist
2. Implement Firestore storage for memory items
3. Support tenant isolation
4. Provide search functionality
5. Integrate with AI Assistant for intelligent memory creation

**Decision Required:** Does Memory Service exist under a different name?

#### 3.3 Research Coordinator

**Status:** Code exists but NOT DEPLOYED  
**Frontend Usage:** Research sessions feature

**Requirements:**
1. Deploy `research-coordinator` service to Cloud Run
2. Verify endpoints match frontend expectations:
   - `GET /api/v1/research-sessions` - List sessions
   - `POST /api/v1/research-sessions` - Create session
   - `GET /api/v1/research-sessions/:id` - Get session
   - `POST /api/v1/research-sessions/:id/complete` - Complete session
3. Configure Firestore collections for session storage
4. Enable WebSocket support for real-time updates

---

## 4. OAUTH CONFIGURATION

### Requirement: Production OAuth Credentials

**Problem:** Slack and Gmail services running in mock mode (fake data).

#### 4.1 Slack OAuth Configuration

**Requirements:**
1. Create Slack App in Slack App Directory
2. Configure OAuth scopes:
   - `channels:read` - Read channel information
   - `channels:history` - Read message history
   - `chat:write` - Send messages
   - `users:read` - Read user information
   - `search:read` - Search messages
3. Add OAuth redirect URL: `https://xynergyos-intelligence-gateway-vgjxy554mq-uc.a.run.app/api/v2/slack/oauth/callback`
4. Store Slack credentials in Secret Manager:
   - `SLACK_CLIENT_ID`
   - `SLACK_CLIENT_SECRET`
   - `SLACK_SIGNING_SECRET`
5. Update `slack-intelligence-service` to use real API calls instead of mock data
6. Remove or disable mock mode in production

#### 4.2 Gmail OAuth Configuration

**Requirements:**
1. Enable Gmail API in Google Cloud Console (project: xynergy-dev-1757909467)
2. Create OAuth 2.0 credentials (Web application type)
3. Configure authorized redirect URIs: `https://xynergyos-intelligence-gateway-vgjxy554mq-uc.a.run.app/api/v2/gmail/oauth/callback`
4. Configure OAuth scopes:
   - `https://www.googleapis.com/auth/gmail.readonly` - Read emails
   - `https://www.googleapis.com/auth/gmail.send` - Send emails
   - `https://www.googleapis.com/auth/gmail.modify` - Modify emails
5. Store Gmail credentials in Secret Manager:
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`
6. Update `gmail-intelligence-service` to use real Gmail API instead of mock data
7. Implement token refresh logic for expired OAuth tokens

#### 4.3 Google Calendar OAuth Configuration

**Requirements:**
1. Enable Google Calendar API in Google Cloud Console
2. Use same OAuth credentials as Gmail (Web application type)
3. Add Calendar API scope: `https://www.googleapis.com/auth/calendar`
4. Calendar Intelligence Service must use these credentials

---

## 5. INTELLIGENCE GATEWAY ROUTING

### Requirement: Gateway Must Route to All Required Services

**Current Routes (Verified):**
- `/api/xynergyos/v2/slack/*` → `slack-intelligence-service`
- `/api/xynergyos/v2/gmail/*` → `gmail-intelligence-service`
- `/api/xynergyos/v2/crm/*` → `crm-engine`

**Required New Routes:**

| Frontend Path | Backend Service | Current Status |
|---------------|----------------|----------------|
| `/api/v2/calendar/*` | `calendar-intelligence-service` | Service missing |
| `/api/v1/ai/query` | `xynergy-ai-assistant` | Route missing |
| `/api/v1/memory/*` | `memory-service` | Service missing |
| `/api/v1/research-sessions/*` | `research-coordinator` | Route missing |
| `/api/v1/aso/*` | `aso-engine` | Route missing |
| `/api/v1/marketing/*` | `marketing-engine` | Route missing |

**Requirements:**
1. Add routes to Intelligence Gateway for all services above
2. Implement proper authentication for each route
3. Apply appropriate rate limiting per service
4. Configure circuit breakers for external service calls
5. Enable response caching where appropriate (5-minute TTL)

---

## 6. WEBSOCKET REQUIREMENTS

### Requirement: Real-Time Event Support

**Current Status:** Intelligence Gateway has `/socket.io` endpoint with authentication.

**Required Events (Frontend Expects):**

#### Slack Events:
- `slack:new_message` - New Slack message received
- `slack:intelligence_updated` - AI analysis complete
- `slack:response_sent` - Message sent successfully

#### Email Events:
- `email:new_message` - New email received
- `email:intelligence_updated` - AI analysis complete
- `email:response_sent` - Email sent successfully

#### Calendar Events:
- `calendar:event_added` - New calendar event
- `calendar:prep_ready` - Meeting prep generated

#### CRM Events:
- `crm:contact_created` - New contact added
- `crm:interaction_logged` - Interaction recorded

#### Workflow Events:
- `workflow:update` - Workflow progress update

**Requirements:**
1. Verify all events above are emitted by respective services
2. Intelligence Gateway must subscribe to service events via Pub/Sub
3. Gateway must broadcast events to connected WebSocket clients
4. Events must be filtered by user/tenant (no cross-tenant leakage)
5. Connection limits remain: 5 per user, 1000 total

---

## 7. ERROR HANDLING & VALIDATION

### Requirement: Consistent Error Response Format

**Frontend Expects:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

**Requirements:**
1. All services must return errors in this format
2. HTTP status codes must be correct (401, 404, 500, etc.)
3. Error codes must be consistent across services
4. Stack traces must never be exposed in production
5. Request IDs must be included for tracing

**Common Error Codes:**
- `AUTHENTICATION_REQUIRED` - No token provided
- `INVALID_TOKEN` - Token is invalid or expired
- `FORBIDDEN` - User lacks permission
- `NOT_FOUND` - Resource doesn't exist
- `VALIDATION_ERROR` - Invalid input
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `SERVICE_UNAVAILABLE` - Backend service down

---

## 8. CORS CONFIGURATION

### Requirement: Frontend Origin Whitelisting

**Frontend URLs:**
- Development: `http://localhost:3000`
- Production: `https://xynergyos-frontend-vgjxy554mq-uc.a.run.app`
- Custom domain (if exists): `https://app.xynergyos.com`

**Requirements:**
1. Intelligence Gateway must allow CORS from frontend origins
2. Credentials must be allowed (cookies, auth headers)
3. All HTTP methods must be allowed (GET, POST, PUT, PATCH, DELETE)
4. Preflight requests (OPTIONS) must be handled
5. No wildcard origins in production (`*` is forbidden)

---

## 9. HEALTH CHECK REQUIREMENTS

### Requirement: Frontend-Accessible Health Checks

**Purpose:** Frontend needs to verify backend connectivity before attempting operations.

**Requirements:**
1. All services must have `/health` endpoint (no auth required)
2. Intelligence Gateway must have `/health/deep` endpoint showing:
   - Gateway status
   - All downstream service statuses
   - Redis connectivity
   - Firebase connectivity
3. Health checks must return within 5 seconds
4. Response format:
   ```json
   {
     "status": "healthy" | "degraded" | "unhealthy",
     "services": {
       "slack": "healthy",
       "gmail": "healthy",
       "crm": "healthy"
     },
     "timestamp": "ISO-8601"
   }
   ```

---

## 10. DEPLOYMENT REQUIREMENTS

### Requirement: Frontend Environment Configuration

**Frontend Needs These Values:**

| Variable | Description | Source |
|----------|-------------|--------|
| `REACT_APP_API_URL` | Intelligence Gateway URL | Cloud Run service URL |
| `REACT_APP_WS_URL` | WebSocket URL | Same as API URL with `wss://` |
| `REACT_APP_FIREBASE_PROJECT_ID` | Firebase project | `xynergy-dev-1757909467` |
| `REACT_APP_FIREBASE_API_KEY` | Firebase API key | Firebase Console |
| `REACT_APP_FIREBASE_AUTH_DOMAIN` | Firebase auth domain | Firebase Console |
| `REACT_APP_FIREBASE_APP_ID` | Firebase app ID | Firebase Console |

**Requirements:**
1. Document correct values for each environment variable
2. Provide to frontend team for configuration
3. Verify URLs are accessible (no authentication required for public endpoints)

---

## 11. SERVICE DISCOVERY

### Requirement: API Documentation Endpoint

**Purpose:** Frontend needs to discover available endpoints dynamically.

**Requirements:**
1. Intelligence Gateway must expose `/api/info` endpoint (no auth)
2. Response must include:
   - Available routes
   - API version
   - Service status
   - Required authentication type
3. Frontend can use this for feature flags (hide UI if service unavailable)

**Example Response:**
```json
{
  "version": "2.0.0",
  "authentication": "firebase",
  "services": {
    "slack": { "available": true, "status": "operational" },
    "gmail": { "available": true, "status": "operational" },
    "calendar": { "available": false, "status": "not_deployed" },
    "crm": { "available": true, "status": "operational" }
  }
}
```

---

## 12. TESTING REQUIREMENTS

### Requirement: Integration Test Suite

**Purpose:** Verify frontend-backend integration works before deployment.

**Requirements:**
1. Create integration tests for all critical endpoints
2. Test authentication flow end-to-end
3. Test WebSocket connection and events
4. Test error handling (401, 404, 500 responses)
5. Test CORS configuration
6. Tests must be automated and run in CI/CD

**Minimum Test Coverage:**
- Authentication: Login, token refresh, logout
- CRM: List contacts, create contact, update contact
- Communication: Slack messages, Gmail messages
- Real-time: WebSocket connection, event broadcast

---

## 13. MONITORING REQUIREMENTS

### Requirement: Integration Monitoring

**Purpose:** Track frontend-backend connection health in production.

**Requirements:**
1. Log all requests from frontend (identified by User-Agent or custom header)
2. Track metrics:
   - Request count by endpoint
   - Error rate by endpoint
   - Response latency percentiles (p50, p95, p99)
   - Authentication failure rate
   - WebSocket connection count and duration
3. Set up alerts:
   - Error rate > 5% for 5 minutes
   - Auth failure rate > 10% for 5 minutes
   - WebSocket disconnection rate > 20%
4. Dashboard showing integration health

---

## IMPLEMENTATION PRIORITY

### Phase 1: Basic Connectivity (CRITICAL)
1. Choose authentication strategy (JWT vs Firebase)
2. Implement authentication in Intelligence Gateway
3. Audit and document existing endpoints
4. Add missing routes to Intelligence Gateway
5. Configure CORS for frontend origins
6. Verify health checks work

### Phase 2: Missing Services (HIGH)
7. Deploy Calendar Intelligence Service (or create if missing)
8. Deploy Research Coordinator
9. Create Memory Service (or identify existing equivalent)
10. Route all services through Intelligence Gateway

### Phase 3: Production Data (HIGH)
11. Configure Slack OAuth credentials
12. Configure Gmail OAuth credentials
13. Remove mock mode from services
14. Test with real data

### Phase 4: Real-Time & Polish (MEDIUM)
15. Verify WebSocket events work
16. Implement integration tests
17. Set up monitoring and alerts
18. Document frontend environment variables

---

## SUCCESS VALIDATION

### Integration is Complete When:

✅ Frontend can login and receive valid auth token  
✅ Frontend can fetch dashboard metrics  
✅ Frontend can list Slack messages (real data, not mock)  
✅ Frontend can list Gmail messages (real data, not mock)  
✅ Frontend can list CRM contacts  
✅ Frontend can create/update CRM contacts  
✅ WebSocket connection stays alive and receives events  
✅ All 30+ frontend pages load without 404 errors  
✅ Health check shows all services healthy  
✅ Integration tests pass in CI/CD  

---

## DELIVERABLES

1. **Authentication Implementation** - Working JWT or Firebase auth
2. **Complete API Mapping Document** - Every frontend endpoint mapped to backend
3. **Missing Services Deployed** - Calendar, Memory, Research (if needed)
4. **OAuth Configuration Complete** - Slack and Gmail using real APIs
5. **Integration Test Suite** - Automated tests verifying connectivity
6. **Monitoring Dashboard** - Showing integration health metrics
7. **Frontend Environment Config** - Documented values for all variables

---

## CRITICAL NOTES

- **No Code Changes Required in Frontend** (except auth if switching to Firebase)
- **Focus is on Backend Configuration and Deployment**
- **Services Exist, They Just Need to be Connected Properly**
- **OAuth is the Main Gap for Production Data**
- **Testing is Critical - Zero Test Coverage Currently**

---

**END OF REQUIREMENTS**

This document provides everything needed for backend implementation. Frontend team should receive environment configuration once backend is ready.
