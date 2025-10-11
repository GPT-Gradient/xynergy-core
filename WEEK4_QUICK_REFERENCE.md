# Week 4 Quick Reference - Slack Intelligence Service

## Service URLs

**Slack Intelligence Service:**
- URL: https://slack-intelligence-service-835612502919.us-central1.run.app
- Health: https://slack-intelligence-service-835612502919.us-central1.run.app/health
- Status: ✅ Deployed & Operational (Mock Mode)

**Intelligence Gateway:**
- URL: https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
- Current Revision: 00002-4ff (Week 2)
- Slack Routes: Code complete, pending VPC connector deployment

## Quick Test Commands

```bash
# Health check
curl https://slack-intelligence-service-835612502919.us-central1.run.app/health

# List endpoints
curl https://slack-intelligence-service-835612502919.us-central1.run.app/

# Deep health check
curl https://slack-intelligence-service-835612502919.us-central1.run.app/health/deep

# List channels (requires Firebase token)
curl -H "Authorization: Bearer <token>" \
  https://slack-intelligence-service-835612502919.us-central1.run.app/api/v1/slack/channels

# Get channel messages
curl -H "Authorization: Bearer <token>" \
  https://slack-intelligence-service-835612502919.us-central1.run.app/api/v1/slack/channels/C001/messages

# Search messages
curl -H "Authorization: Bearer <token>" \
  "https://slack-intelligence-service-835612502919.us-central1.run.app/api/v1/slack/search?q=test"
```

## API Endpoints

| Endpoint | Method | Auth | Cache TTL |
|----------|--------|------|-----------|
| `/health` | GET | No | - |
| `/health/deep` | GET | No | - |
| `/api/v1/slack/channels` | GET | Yes | 5 min |
| `/api/v1/slack/channels/:id/messages` | GET | Yes | 1 min |
| `/api/v1/slack/channels/:id/messages` | POST | Yes | - |
| `/api/v1/slack/users` | GET | Yes | 10 min |
| `/api/v1/slack/users/:id` | GET | Yes | 10 min |
| `/api/v1/slack/search?q=...` | GET | Yes | 2 min |
| `/api/v1/slack/status` | GET | Yes | - |

## Mock Data

**Channels:**
- C001: #general (42 members)
- C002: #engineering (15 members)
- C003: #marketing (8 members)

**Users:**
- U001: Alice Johnson (alice@example.com)
- U002: Bob Smith (bob@example.com)
- U003: Charlie Brown (charlie@example.com)

## Configuration

**Enable Real Slack (Optional):**
```bash
# Set environment variables
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_SIGNING_SECRET=your-secret-here

# Redeploy
gcloud run deploy slack-intelligence-service \
  --set-env-vars "SLACK_BOT_TOKEN=...,SLACK_SIGNING_SECRET=..."
```

## Architecture

```
Frontend → Intelligence Gateway → Slack Service → Slack API (or Mock)
                                                ↓
                                          Firebase Auth
                                          Redis Cache
                                          WebSocket Events
```

## Status

- ✅ Slack Service: Deployed & Tested
- ✅ Gateway Code: Complete
- ⏳ Gateway Deployment: Pending VPC connector
- ✅ Mock Mode: Working
- ⏳ Production Mode: Awaiting credentials

## Next Steps

1. Configure VPC connector for Gateway Redis access
2. Redeploy Gateway with Slack routes
3. Test end-to-end: Frontend → Gateway → Slack Service
4. Obtain Slack credentials for real workspace
5. Move to Week 5: Gmail Intelligence Service
