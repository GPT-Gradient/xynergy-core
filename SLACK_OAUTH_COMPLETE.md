# Slack OAuth Configuration - COMPLETE ✅

**Date:** October 11, 2025
**Status:** CONFIGURED AND READY FOR OAUTH FLOW

---

## Slack OAuth Setup Complete

### ✅ Secrets Created in Secret Manager

```bash
gcloud secrets list --filter="name:SLACK" --project=xynergy-dev-1757909467
```

| Secret | Value | Status |
|--------|-------|--------|
| `SLACK_CLIENT_ID` | 9675918053013.9709558335008 | ✅ Created |
| `SLACK_CLIENT_SECRET` | 488dfbc5d5f8605192b657f6a56943e5 | ✅ Created |
| `SLACK_SIGNING_SECRET` | 4c6b950b7084d78d002e4ddba3d50ed4 | ✅ Created |

### ✅ Service Updated

**Slack Intelligence Service** has been updated with OAuth credentials:
- Service: `slack-intelligence-service`
- Revision: `slack-intelligence-service-00003-w2j`
- URL: https://slack-intelligence-service-835612502919.us-central1.run.app
- Status: ✅ Deployed with secrets

---

## Slack App Configuration

### App Details
```
App ID: A09LVGE9V08
Client ID: 9675918053013.9709558335008
Client Secret: 488dfbc5d5f8605192b657f6a56943e5
Signing Secret: 4c6b950b7084d78d002e4ddba3d50ed4
Verification Token: M59rzvpyYVZ6k9pLU7XakJDL
```

### Slack App Console
**Manage your app at:** https://api.slack.com/apps/A09LVGE9V08

---

## Required Slack Configuration

### 1. OAuth & Permissions - Redirect URLs

**IMPORTANT:** Add these redirect URLs to your Slack App:

1. Go to: https://api.slack.com/apps/A09LVGE9V08/oauth
2. Under "Redirect URLs", click "Add New Redirect URL"
3. Add these URLs:

```
https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/oauth/callback
https://slack-intelligence-service-835612502919.us-central1.run.app/oauth/callback
http://localhost:8080/api/v2/slack/oauth/callback
```

4. Click "Save URLs"

### 2. OAuth & Permissions - Scopes

Your Slack app needs these **Bot Token Scopes**:

**Required Scopes:**
- `channels:read` - View basic channel information
- `channels:history` - View messages in public channels
- `chat:write` - Send messages as @your_app
- `users:read` - View users in workspace
- `users:read.email` - View email addresses of users

**Recommended Additional Scopes:**
- `groups:read` - View basic private channel information
- `groups:history` - View messages in private channels (if invited)
- `im:read` - View direct messages with your app
- `im:history` - View direct message history
- `search:read` - Search workspace messages

**How to add scopes:**
1. Go to: https://api.slack.com/apps/A09LVGE9V08/oauth
2. Scroll to "Scopes" section
3. Under "Bot Token Scopes", click "Add an OAuth Scope"
4. Add each scope from the list above

### 3. Event Subscriptions (Optional - for real-time events)

If you want real-time Slack events (messages, reactions, etc.):

1. Go to: https://api.slack.com/apps/A09LVGE9V08/event-subscriptions
2. Toggle "Enable Events" to ON
3. Set Request URL to:
   ```
   https://slack-intelligence-service-835612502919.us-central1.run.app/slack/events
   ```
4. Under "Subscribe to bot events", add:
   - `message.channels` - Message posted to public channel
   - `message.groups` - Message posted to private channel
   - `message.im` - Message sent to app
5. Click "Save Changes"

---

## Testing Slack OAuth Flow

### Step 1: Initiate OAuth Flow

**Option A: Via Intelligence Gateway**
```bash
# Open in browser
open "https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/oauth/authorize"
```

**Option B: Direct to Slack Service**
```bash
# Open in browser
open "https://slack-intelligence-service-835612502919.us-central1.run.app/oauth/authorize"
```

### Step 2: User Authorizes Workspace

The user will be redirected to Slack to:
1. Select their Slack workspace
2. Review requested permissions
3. Click "Allow" to grant access

### Step 3: Callback and Token Storage

After authorization:
1. Slack redirects to callback URL with authorization code
2. Service exchanges code for bot token
3. Token stored in Firestore per workspace/tenant
4. User redirected to success page

### Step 4: Test Real Slack Data

Once OAuth is complete, test with real Slack data:

```bash
# Get JWT or Firebase token
export TOKEN="your-jwt-or-firebase-token"

# List channels
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/channels

# Get messages from a channel
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/messages/CHANNEL_ID

# Send a message
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello from Slack Intelligence Service!",
    "channel": "CHANNEL_ID"
  }' \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/messages

# Search messages
curl -H "Authorization: Bearer $TOKEN" \
  "https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/search?q=important"

# List users
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/users
```

---

## Slack API Endpoints

All endpoints route through the Intelligence Gateway and require authentication.

### Channel Operations

**List Channels**
```
GET /api/v2/slack/channels

Response:
{
  "channels": [
    {
      "id": "C123456",
      "name": "general",
      "is_private": false,
      "num_members": 25
    }
  ]
}
```

**Get Channel Info**
```
GET /api/v2/slack/channels/:channelId

Response:
{
  "id": "C123456",
  "name": "general",
  "topic": "Company announcements",
  "purpose": "General discussions",
  "num_members": 25
}
```

### Message Operations

**Get Messages**
```
GET /api/v2/slack/messages/:channelId

Query Parameters:
  - limit: Number of messages (default: 20, max: 100)
  - oldest: Start from this timestamp
  - latest: End at this timestamp

Response:
{
  "messages": [
    {
      "ts": "1234567890.123456",
      "user": "U123456",
      "text": "Hello team!",
      "channel": "C123456"
    }
  ]
}
```

**Send Message**
```
POST /api/v2/slack/messages/:channelId

Body:
{
  "text": "Message text",
  "thread_ts": "1234567890.123456" (optional - for replies),
  "blocks": [...] (optional - for rich formatting)
}

Response:
{
  "ok": true,
  "ts": "1234567890.123456",
  "channel": "C123456"
}
```

**Search Messages**
```
GET /api/v2/slack/search

Query Parameters:
  - q: Search query (required)
  - count: Number of results (default: 20)

Response:
{
  "messages": [
    {
      "text": "Matching message",
      "user": "U123456",
      "channel": "C123456",
      "ts": "1234567890.123456"
    }
  ]
}
```

### User Operations

**List Users**
```
GET /api/v2/slack/users

Response:
{
  "users": [
    {
      "id": "U123456",
      "name": "john.doe",
      "real_name": "John Doe",
      "email": "john@example.com",
      "is_bot": false
    }
  ]
}
```

**Get User Info**
```
GET /api/v2/slack/users/:userId

Response:
{
  "id": "U123456",
  "name": "john.doe",
  "real_name": "John Doe",
  "email": "john@example.com",
  "title": "Software Engineer"
}
```

---

## Frontend Integration

### Initialize OAuth Flow from Frontend

```typescript
// Redirect user to Slack OAuth authorization
function initiateSlackOAuth() {
  const authUrl = `${process.env.REACT_APP_API_URL}/api/v2/slack/oauth/authorize`;
  window.location.href = authUrl;
}

// Handle OAuth callback (if using frontend callback)
function handleSlackOAuthCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');

  if (code) {
    // Exchange code for tokens via backend
    fetch(`${process.env.REACT_APP_API_URL}/api/v2/slack/oauth/callback?code=${code}`, {
      headers: {
        'Authorization': `Bearer ${firebaseToken}`
      }
    })
    .then(res => res.json())
    .then(data => {
      console.log('Slack connected!', data);
      // Redirect to dashboard or show success message
    });
  }
}
```

### Check Slack Connection Status

```typescript
async function checkSlackConnected() {
  const response = await fetch(
    `${process.env.REACT_APP_API_URL}/api/v2/slack/status`,
    {
      headers: {
        'Authorization': `Bearer ${firebaseToken}`
      }
    }
  );

  const data = await response.json();
  return data.connected; // true if workspace is authorized
}
```

### Fetch Slack Channels

```typescript
async function fetchSlackChannels() {
  const response = await fetch(
    `${process.env.REACT_APP_API_URL}/api/v2/slack/channels`,
    {
      headers: {
        'Authorization': `Bearer ${firebaseToken}`
      }
    }
  );

  return response.json();
}
```

### Send Slack Message

```typescript
async function sendSlackMessage(channelId: string, text: string) {
  const response = await fetch(
    `${process.env.REACT_APP_API_URL}/api/v2/slack/messages/${channelId}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${firebaseToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text })
    }
  );

  return response.json();
}
```

---

## Mock Mode vs Real Data

### Current Status

The Slack Intelligence Service now has OAuth credentials configured, but will still return **mock data** until:

1. User completes OAuth flow (authorizes Slack workspace)
2. Bot token is stored in Firestore for that workspace
3. Subsequent API calls will use real Slack API with stored token

### Checking Mode

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/status

# Response (before OAuth):
{
  "connected": false,
  "mode": "mock"
}

# Response (after OAuth):
{
  "connected": true,
  "mode": "live",
  "workspace": "Your Workspace Name",
  "team_id": "T123456"
}
```

---

## Token Storage and Management

### How Tokens Are Stored

Slack OAuth tokens are stored in Firestore with tenant isolation:

```
Collection: oauth_tokens
Document: {tenantId}_{userId}_slack

Fields:
  - access_token: Bot token (xoxb-...)
  - team_id: Slack workspace ID
  - team_name: Slack workspace name
  - scope: Granted scopes
  - bot_user_id: Bot user ID in workspace
  - updated_at: Last token update
```

### Token Refresh

Slack bot tokens do not expire unless:
- User uninstalls the app
- App credentials are regenerated
- Workspace admin revokes access

The service automatically handles token validation and will re-request OAuth if token is invalid.

---

## WebSocket Events (Real-time Updates)

Once event subscriptions are configured, the Intelligence Gateway can push real-time Slack events via WebSocket:

### Subscribe to Slack Events

```typescript
import { io } from 'socket.io-client';

const socket = io(process.env.REACT_APP_WS_URL, {
  path: '/api/xynergyos/v2/stream',
  auth: {
    token: firebaseToken
  }
});

// Subscribe to Slack events
socket.emit('subscribe', ['slack-messages']);

// Listen for new Slack messages
socket.on('slack-message', (data) => {
  console.log('New Slack message:', data);
  // {
  //   type: 'message',
  //   channel: 'C123456',
  //   user: 'U123456',
  //   text: 'Hello!',
  //   ts: '1234567890.123456'
  // }
});
```

---

## Security Considerations

### ✅ Secure Storage
- OAuth credentials stored in Secret Manager (not in code)
- Bot tokens stored in Firestore with tenant isolation
- Signing secret used to verify webhook requests

### ✅ Scope Minimization
- Only request necessary Slack permissions
- User can see exactly what access is being requested

### ✅ Webhook Verification
- All webhook events verified with signing secret
- Prevents spoofed webhook requests

### ✅ CORS Protection
- Intelligence Gateway enforces strict CORS
- Only whitelisted origins can make requests

---

## Troubleshooting

### "Redirect URI mismatch" Error

**Cause:** Redirect URI not added to Slack App configuration
**Fix:** Add redirect URIs to OAuth & Permissions in Slack App settings

### "Missing scopes" Error

**Cause:** Required scopes not added to Bot Token Scopes
**Fix:** Add required scopes in OAuth & Permissions

### Still Getting Mock Data

**Check:**
1. Has user completed OAuth flow?
2. Is bot token stored in Firestore?
3. Are scopes sufficient for the operation?

**Debug:**
```bash
# Check Slack connection status
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/status
```

### Webhook Events Not Received

**Check:**
1. Event Subscriptions enabled in Slack App?
2. Request URL verified successfully?
3. Correct events subscribed?

---

## Next Steps

### Required: Configure Slack App

⚠️ **ACTION REQUIRED:** You must configure redirect URLs and scopes in Slack App:

1. **Add Redirect URLs:** https://api.slack.com/apps/A09LVGE9V08/oauth
2. **Add Bot Token Scopes:** https://api.slack.com/apps/A09LVGE9V08/oauth (scroll to Scopes)
3. **Optional - Event Subscriptions:** https://api.slack.com/apps/A09LVGE9V08/event-subscriptions

### Testing Checklist

- [ ] Add redirect URLs to Slack App
- [ ] Add required bot token scopes
- [ ] Reinstall app to workspace (to apply new scopes)
- [ ] Initiate OAuth flow from browser
- [ ] Authorize workspace
- [ ] Verify bot token stored in Firestore
- [ ] Test listing channels with real data
- [ ] Test sending message
- [ ] Test search functionality
- [ ] Optional: Configure event subscriptions for real-time updates

---

## Summary

✅ **Slack Client ID** - Stored in Secret Manager
✅ **Slack Client Secret** - Stored in Secret Manager
✅ **Slack Signing Secret** - Stored in Secret Manager
✅ **Service Account Access** - Granted
✅ **Slack Intelligence Service** - Updated and deployed
✅ **OAuth Endpoints** - Ready to use

**Status:** Slack OAuth is configured and ready! Users can now authorize their Slack workspace and the service will use real Slack data instead of mock data. 🎉

**Actions Required:**
1. Add redirect URLs to Slack App
2. Add bot token scopes to Slack App
3. Reinstall app to apply new scopes (if previously installed)
