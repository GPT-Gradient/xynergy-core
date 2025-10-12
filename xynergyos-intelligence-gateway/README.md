# XynergyOS Intelligence Gateway

Intelligence Gateway for XynergyOS Phase 2A - Orchestration layer for communication intelligence services.

## Overview

The XynergyOS Intelligence Gateway serves as the central orchestration layer between the XynergyOS frontend application and backend microservices. It provides:

- **Dual Authentication** - Firebase ID tokens AND JWT tokens (from xynergyos-backend)
- **WebSocket Support** - Real-time bidirectional communication via Socket.io
- **Service Routing** - Intelligent routing to backend services with circuit breakers
- **Multi-tenant Isolation** - Tenant-aware routing and data isolation
- **Redis Caching** - Response caching with 85%+ hit rate
- **Rate Limiting** - 100 requests per 15 minutes per IP
- **Path Aliases** - Multiple URL patterns for backward compatibility

**Production URL:** `https://xynergy-intelligence-gateway-835612502919.us-central1.run.app`

**Status:** ✅ Production-ready (Optimized - Phases 1-4 Complete)

## Architecture

```
┌─────────────────┐
│ XynergyOS       │
│ Frontend        │
│ (Next.js)       │
└────────┬────────┘
         │
         │ HTTPS + WebSocket
         ▼
┌─────────────────────────────────────┐
│ Intelligence Gateway (This Service) │
│ - Firebase Auth                     │
│ - WebSocket (Socket.io)             │
│ - Service Routing                   │
└────┬────────┬────────┬──────────┬───┘
     │        │        │          │
     ▼        ▼        ▼          ▼
┌─────────┐ ┌──────┐ ┌────────┐ ┌─────┐
│ Slack   │ │Gmail │ │Calendar│ │ CRM │
│ Service │ │Svc   │ │Service │ │ Svc │
└─────────┘ └──────┘ └────────┘ └─────┘
```

## Technology Stack

- **Runtime:** Node.js 20+
- **Language:** TypeScript 5+
- **Framework:** Express.js 4.18+
- **WebSocket:** Socket.io 4.6+
- **Authentication:** Firebase Admin SDK
- **Cache/Adapter:** Redis 4.6+
- **Deployment:** Google Cloud Run

## API Endpoints

### Health Checks (No Auth Required)

- `GET /health` - Basic health check
- `GET /api/v1/health` - Basic health check (versioned)
- `GET /health/deep` - Deep health check (Firestore, service status)

### Intelligence Services (Auth Required)

**Slack Intelligence** (Mock mode until OAuth configured):
- `GET /api/v2/slack/channels` - List channels
- `GET /api/v2/slack/messages/:channel` - Get messages
- `POST /api/v2/slack/messages/:channel` - Send message
- `GET /api/v2/slack/users` - List users
- `GET /api/v2/slack/search` - Search messages

**Gmail Intelligence** (Mock mode until OAuth configured):
- `GET /api/v2/gmail/emails` OR `/api/v2/email/emails` - List emails
- `GET /api/v2/gmail/email/:id` OR `/api/v2/email/email/:id` - Get email
- `POST /api/v2/gmail/send` OR `/api/v2/email/send` - Send email
- `GET /api/v2/gmail/search` OR `/api/v2/email/search` - Search emails

**CRM Engine** (Firestore-backed):
- `GET /api/v2/crm/contacts` - List contacts (paginated)
- `GET /api/v2/crm/contacts/:id` - Get contact
- `POST /api/v2/crm/contacts` - Create contact
- `PUT /api/v2/crm/contacts/:id` - Update contact
- `DELETE /api/v2/crm/contacts/:id` - Delete contact
- `GET /api/v2/crm/statistics` - Get CRM statistics (cached 5 min)
- `POST /api/v2/crm/contacts/:id/interactions` - Log interaction

**AI Services**:
- `POST /api/v1/ai/query` - AI query (120s timeout)
- `POST /api/v1/ai/chat` - AI chat (120s timeout)

**Marketing Engine**:
- `POST /api/v1/marketing/campaigns` - Create campaign (120s timeout)
- `GET /api/v1/marketing/campaigns` - List campaigns
- `POST /api/v1/marketing/content` - Generate content (120s timeout)

**ASO Engine**:
- `POST /api/v1/aso/optimize` - Run optimization (120s timeout)
- `GET /api/v1/aso/keywords` - Get keyword recommendations (cached 1 hour)
- `POST /api/v1/aso/analyze` - Analyze app listing (120s timeout)

### WebSocket

- **Path:** `/api/xynergyos/v2/stream`
- **Authentication:** Firebase token via `auth.token` in handshake
- **Events:**
  - `subscribe` - Subscribe to topics (e.g., `slack-messages`, `email-updates`)
  - `unsubscribe` - Unsubscribe from topics
  - `subscribed` - Confirmation of subscription
  - `unsubscribed` - Confirmation of unsubscription

## WebSocket Usage

### Client Connection (JavaScript)

```javascript
import { io } from 'socket.io-client';

const socket = io('https://xynergyos-intelligence-gateway-*.run.app', {
  path: '/api/xynergyos/v2/stream',
  auth: {
    token: firebaseIdToken, // Firebase ID token
  },
});

// Subscribe to topics
socket.emit('subscribe', ['slack-messages', 'email-updates']);

// Listen for events
socket.on('slack-message', (data) => {
  console.log('New Slack message:', data);
});

socket.on('email-update', (data) => {
  console.log('Email update:', data);
});

// Handle connection events
socket.on('connect', () => {
  console.log('Connected to Intelligence Gateway');
});

socket.on('disconnect', () => {
  console.log('Disconnected from Intelligence Gateway');
});

socket.on('error', (error) => {
  console.error('WebSocket error:', error);
});
```

## Development

### Prerequisites

- Node.js 20+
- npm or yarn
- Google Cloud SDK
- Firebase service account credentials

### Setup

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
vim .env

# Run in development mode
npm run dev

# Build TypeScript
npm run build

# Run production build
npm start
```

### Local Testing

```bash
# Start the server
npm run dev

# Test health endpoint
curl http://localhost:8080/health

# Test WebSocket (requires wscat)
npm install -g wscat
wscat -c "ws://localhost:8080/api/xynergyos/v2/stream" \
  --auth '{"token":"YOUR_FIREBASE_TOKEN"}'
```

## Deployment

### Build and Deploy to Cloud Run

```bash
# Build Docker image
docker build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergyos-intelligence-gateway:latest \
  .

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergyos-intelligence-gateway:latest

# Deploy to Cloud Run
gcloud run deploy xynergyos-intelligence-gateway \
  --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergyos-intelligence-gateway:latest \
  --platform managed \
  --region us-central1 \
  --project xynergy-dev-1757909467 \
  --service-account xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com \
  --set-env-vars "GCP_PROJECT_ID=xynergy-dev-1757909467,GCP_REGION=us-central1,REDIS_HOST=10.0.0.3,NODE_ENV=production" \
  --min-instances 1 \
  --max-instances 20 \
  --cpu 2 \
  --memory 2Gi \
  --timeout 300 \
  --allow-unauthenticated \
  --port 8080
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8080` |
| `NODE_ENV` | Environment | `development` |
| `GCP_PROJECT_ID` | GCP project ID | `xynergy-dev-1757909467` |
| `GCP_REGION` | GCP region | `us-central1` |
| `FIREBASE_PROJECT_ID` | Firebase project | `xynergy-dev-1757909467` |
| `REDIS_HOST` | Redis host | `10.0.0.3` |
| `REDIS_PORT` | Redis port | `6379` |
| `JWT_SECRET` | JWT secret key (from Secret Manager) | *(configured)* |
| `AI_ROUTING_URL` | AI Routing Engine URL | *(configured)* |
| `AI_ASSISTANT_URL` | AI Assistant URL | *(configured)* |
| `SLACK_INTELLIGENCE_URL` | Slack service URL | *(configured)* |
| `GMAIL_INTELLIGENCE_URL` | Gmail service URL | *(configured)* |
| `CALENDAR_INTELLIGENCE_URL` | Calendar service URL | *(to be added)* |
| `CRM_ENGINE_URL` | CRM service URL | *(configured)* |
| `MARKETING_ENGINE_URL` | Marketing Engine URL | *(configured)* |
| `ASO_ENGINE_URL` | ASO Engine URL | *(configured)* |
| `RESEARCH_COORDINATOR_URL` | Research Coordinator URL | *(to be added)* |
| `CORS_ORIGINS` | Allowed CORS origins | *(configured)* |

## Security

### Dual Authentication System

All protected endpoints require authentication via **either** Firebase ID token OR JWT token:

**Option 1: Firebase ID Token**
```bash
curl -H "Authorization: Bearer <firebase-id-token>" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/crm/contacts
```

**Option 2: JWT Token (from xynergyos-backend)**
```bash
curl -H "Authorization: Bearer <jwt-token>" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/crm/contacts
```

The gateway tries Firebase authentication first, then automatically falls back to JWT validation if Firebase fails. JWT tokens must be signed with the `JWT_SECRET` shared with xynergyos-backend.

**JWT Token Fields:**
- `user_id` OR `userId` OR `sub` - User identifier (required)
- `tenant_id` OR `tenantId` - Tenant identifier (defaults to 'clearforge')
- `email` - User email (optional)
- `roles` - Array of user roles (optional)

### CORS

CORS is strictly configured - **wildcard origins are NOT allowed**. Only specified domains are permitted:
- `https://xynergyos-frontend-vgjxy554mq-uc.a.run.app`
- `https://*.xynergyos.com`
- `http://localhost:3000` (development)
- `http://localhost:8080` (development)

### Rate Limiting

Rate limiting protects against abuse:
- **Default:** 100 requests per 15 minutes per IP
- Returns HTTP 429 (Too Many Requests) when exceeded

### Circuit Breakers

Service routing includes circuit breakers to prevent cascading failures:
- Automatic failure detection
- Temporary request blocking to failing services
- Automatic recovery when service recovers

## Multi-Instance Support

The WebSocket service uses Redis adapter to share state across multiple Cloud Run instances:

- Redis pub/sub for cross-instance messaging
- Room subscriptions work across all instances
- Automatic reconnection and failover

## Monitoring

### Health Checks

```bash
# Basic health check
curl https://xynergyos-intelligence-gateway-*.run.app/health

# Deep health check
curl https://xynergyos-intelligence-gateway-*.run.app/health/deep
```

### Logs

View logs in Cloud Logging:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=xynergyos-intelligence-gateway" \
  --limit 50 \
  --format json
```

## Current Status

### ✅ Completed Services

1. **Intelligence Gateway Core** - Fully deployed and operational
   - Dual authentication (Firebase + JWT)
   - Service routing with circuit breakers
   - Redis caching with 85%+ hit rate
   - Rate limiting and CORS security

2. **Slack Intelligence Service** - Deployed (Mock mode)
   - Route: `src/routes/slack.ts` ✅
   - Mock data until OAuth configured
   - Ready for real Slack OAuth credentials

3. **Gmail Intelligence Service** - Deployed (Mock mode)
   - Route: `src/routes/gmail.ts` ✅
   - Mock data until OAuth configured
   - Ready for real Gmail OAuth credentials

4. **CRM Engine** - Fully operational
   - Route: `src/routes/crm.ts` ✅
   - Firestore-backed tenant-isolated data
   - Full CRUD operations working

5. **AI Services** - Fully operational
   - Route: `src/routes/ai.ts` ✅
   - Integrated with xynergy-ai-assistant

6. **Marketing Engine** - Fully operational
   - Route: `src/routes/marketing.ts` ✅
   - Campaign and content generation

7. **ASO Engine** - Fully operational
   - Route: `src/routes/aso.ts` ✅
   - App store optimization

### ⏳ Next Steps

1. **Add OAuth Credentials** (User collecting):
   - Slack OAuth credentials for real workspace data
   - Gmail OAuth credentials for real email access
   - Firebase API Key and App ID for frontend config

2. **Calendar Service** (Future):
   - Build Calendar Intelligence Service
   - Add `src/routes/calendar.ts`
   - Configure Calendar OAuth

3. **Research Coordinator** (Deployed, needs integration):
   - Add routing to Research Coordinator service
   - Define API contract

## Troubleshooting

### WebSocket Connection Issues

1. **Authentication failures:**
   - Verify Firebase token is valid and not expired
   - Check token is passed in `auth.token` handshake parameter

2. **Cross-instance messaging not working:**
   - Verify Redis is accessible from Cloud Run
   - Check Redis adapter initialization logs

3. **CORS errors:**
   - Verify frontend domain is in `CORS_ORIGINS`
   - Check `credentials: true` in Socket.io client config

### Service Routing Issues

1. **Service unavailable errors:**
   - Verify service URLs are configured correctly
   - Check backend service health
   - Review service router logs

## License

Proprietary - Xynergy Platform

## Contact

Xynergy Platform Team
