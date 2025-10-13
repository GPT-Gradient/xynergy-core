# OAuth Configuration Guide

**Purpose:** Enable real data from Slack, Gmail, and Calendar services
**Status:** Services work in mock mode - OAuth enables real data
**Timeline:** 4-6 hours per service

---

## Overview

Currently, Slack, Gmail, and Calendar services return mock data. Configuring OAuth will enable them to access real data from external APIs.

**Services Requiring OAuth:**
- ✅ CRM - Uses Firestore (no OAuth needed)
- ✅ Memory - Uses Firestore (no OAuth needed)
- ✅ Research - Uses Firestore (no OAuth needed)
- 🟡 Slack - Needs Slack OAuth
- 🟡 Gmail - Needs Google OAuth
- 🟡 Calendar - Needs Google OAuth (same as Gmail)

---

## Slack OAuth Setup

### Step 1: Create Slack App (30 minutes)

1. **Go to Slack API Portal**
   - Visit: https://api.slack.com/apps
   - Click "Create New App"
   - Choose "From scratch"

2. **Configure Basic Information**
   - App Name: `XynergyOS Intelligence`
   - Workspace: Select your Slack workspace
   - Click "Create App"

3. **Configure OAuth & Permissions**
   - Navigate to "OAuth & Permissions" in left sidebar
   - Scroll to "Redirect URLs"
   - Add: `https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/oauth/callback`
   - Click "Save URLs"

4. **Add OAuth Scopes**
   Under "Bot Token Scopes", add:
   ```
   channels:read       - View basic channel information
   channels:history    - View messages in public channels
   chat:write         - Send messages
   users:read         - View people in the workspace
   search:read        - Search workspace content
   ```

5. **Install App to Workspace**
   - Scroll to top of "OAuth & Permissions"
   - Click "Install to Workspace"
   - Click "Allow"
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)

6. **Get App Credentials**
   - Go to "Basic Information" in left sidebar
   - Under "App Credentials", note:
     - Client ID
     - Client Secret
     - Signing Secret

### Step 2: Store Credentials in Secret Manager (15 minutes)

```bash
# Store Slack Bot Token
echo -n "xoxb-your-token-here" | \
  gcloud secrets create SLACK_BOT_TOKEN \
  --data-file=- \
  --project xynergy-dev-1757909467

# Store Client ID
echo -n "your-client-id" | \
  gcloud secrets create SLACK_CLIENT_ID \
  --data-file=- \
  --project xynergy-dev-1757909467

# Store Client Secret
echo -n "your-client-secret" | \
  gcloud secrets create SLACK_CLIENT_SECRET \
  --data-file=- \
  --project xynergy-dev-1757909467

# Store Signing Secret
echo -n "your-signing-secret" | \
  gcloud secrets create SLACK_SIGNING_SECRET \
  --data-file=- \
  --project xynergy-dev-1757909467

# Grant service account access
gcloud secrets add-iam-policy-binding SLACK_BOT_TOKEN \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project xynergy-dev-1757909467

# Repeat for other secrets...
```

### Step 3: Update Slack Intelligence Service (1 hour)

**File:** `slack-intelligence-service/src/config/config.ts`

```typescript
// Add Slack credentials
export const slackConfig = {
  botToken: process.env.SLACK_BOT_TOKEN,
  clientId: process.env.SLACK_CLIENT_ID,
  clientSecret: process.env.SLACK_CLIENT_SECRET,
  signingSecret: process.env.SLACK_SIGNING_SECRET,
  mockMode: !process.env.SLACK_BOT_TOKEN, // Auto-detect
};
```

**File:** `slack-intelligence-service/src/services/slackClient.ts`

Replace mock implementation with real Slack Web API:

```typescript
import { WebClient } from '@slack/web-api';
import { slackConfig } from '../config/config';

export class SlackClient {
  private client: WebClient;

  constructor() {
    if (slackConfig.mockMode) {
      // Keep mock mode for development
      this.client = null as any;
    } else {
      this.client = new WebClient(slackConfig.botToken);
    }
  }

  async getChannels() {
    if (slackConfig.mockMode) {
      return this.getMockChannels();
    }

    const result = await this.client.conversations.list({
      types: 'public_channel,private_channel',
      limit: 100,
    });

    return result.channels;
  }

  async getMessages(channelId: string) {
    if (slackConfig.mockMode) {
      return this.getMockMessages(channelId);
    }

    const result = await this.client.conversations.history({
      channel: channelId,
      limit: 50,
    });

    return result.messages;
  }

  // Keep mock methods for fallback...
}
```

### Step 4: Deploy Updated Service (30 minutes)

```bash
cd slack-intelligence-service

# Install Slack SDK
npm install @slack/web-api

# Build
npm run build

# Deploy with secrets
gcloud run deploy slack-intelligence-service \
  --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-services/slack-intelligence-service:latest \
  --region us-central1 \
  --project xynergy-dev-1757909467 \
  --platform managed \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 1 \
  --set-secrets="SLACK_BOT_TOKEN=SLACK_BOT_TOKEN:latest,SLACK_CLIENT_ID=SLACK_CLIENT_ID:latest,SLACK_CLIENT_SECRET=SLACK_CLIENT_SECRET:latest,SLACK_SIGNING_SECRET=SLACK_SIGNING_SECRET:latest"
```

### Step 5: Test (15 minutes)

```bash
# Get Firebase token
export TOKEN="your-firebase-token"

# Test Slack channels (should return real data)
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/channels

# Response should NOT have "mock: true"
# Should show real Slack channels
```

**Slack OAuth Complete!** ✅

---

## Gmail OAuth Setup

### Step 1: Enable Gmail API (10 minutes)

```bash
# Enable Gmail API
gcloud services enable gmail.googleapis.com \
  --project=xynergy-dev-1757909467
```

### Step 2: Create OAuth Credentials (20 minutes)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com
   - Select project: `xynergy-dev-1757909467`

2. **Navigate to APIs & Services > Credentials**
   - Click "Create Credentials"
   - Select "OAuth 2.0 Client ID"

3. **Configure OAuth Consent Screen** (if not done)
   - User Type: Internal (or External for public)
   - App name: `XynergyOS Intelligence`
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"

4. **Add Scopes**
   - Add scopes:
     ```
     https://www.googleapis.com/auth/gmail.readonly
     https://www.googleapis.com/auth/gmail.send
     https://www.googleapis.com/auth/gmail.modify
     ```
   - Click "Update"

5. **Create OAuth Client**
   - Application type: "Web application"
   - Name: `XynergyOS Gmail Integration`
   - Authorized redirect URIs:
     ```
     https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/oauth/callback
     ```
   - Click "Create"
   - Copy Client ID and Client Secret

### Step 3: Store Credentials (15 minutes)

```bash
# Store Gmail OAuth credentials
echo -n "your-client-id.apps.googleusercontent.com" | \
  gcloud secrets create GMAIL_CLIENT_ID \
  --data-file=- \
  --project xynergy-dev-1757909467

echo -n "your-client-secret" | \
  gcloud secrets create GMAIL_CLIENT_SECRET \
  --data-file=- \
  --project xynergy-dev-1757909467

# Grant access
gcloud secrets add-iam-policy-binding GMAIL_CLIENT_ID \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project xynergy-dev-1757909467

gcloud secrets add-iam-policy-binding GMAIL_CLIENT_SECRET \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project xynergy-dev-1757909467
```

### Step 4: Update Gmail Service (1 hour)

**File:** `gmail-intelligence-service/src/config/config.ts`

```typescript
export const gmailConfig = {
  clientId: process.env.GMAIL_CLIENT_ID,
  clientSecret: process.env.GMAIL_CLIENT_SECRET,
  redirectUri: `${process.env.API_BASE_URL}/api/v2/gmail/oauth/callback`,
  mockMode: !process.env.GMAIL_CLIENT_ID,
};
```

**File:** `gmail-intelligence-service/src/services/gmailClient.ts`

```typescript
import { google } from 'googleapis';
import { gmailConfig } from '../config/config';

export class GmailClient {
  private gmail: any;

  constructor(accessToken: string) {
    if (gmailConfig.mockMode) {
      this.gmail = null;
    } else {
      const oauth2Client = new google.auth.OAuth2(
        gmailConfig.clientId,
        gmailConfig.clientSecret,
        gmailConfig.redirectUri
      );
      oauth2Client.setCredentials({ access_token: accessToken });
      this.gmail = google.gmail({ version: 'v1', auth: oauth2Client });
    }
  }

  async getMessages() {
    if (gmailConfig.mockMode) {
      return this.getMockMessages();
    }

    const response = await this.gmail.users.messages.list({
      userId: 'me',
      maxResults: 50,
    });

    return response.data.messages;
  }

  // Additional methods...
}
```

### Step 5: Deploy (30 minutes)

```bash
cd gmail-intelligence-service

# Install googleapis
npm install googleapis

# Build and deploy
npm run build

gcloud run deploy gmail-intelligence-service \
  --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-services/gmail-intelligence-service:latest \
  --region us-central1 \
  --project xynergy-dev-1757909467 \
  --set-secrets="GMAIL_CLIENT_ID=GMAIL_CLIENT_ID:latest,GMAIL_CLIENT_SECRET=GMAIL_CLIENT_SECRET:latest"
```

### Step 6: Test (15 minutes)

```bash
# Test Gmail messages
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/email/messages

# Should return real Gmail data
```

**Gmail OAuth Complete!** ✅

---

## Calendar OAuth Setup

### Step 1: Enable Calendar API (10 minutes)

```bash
# Enable Google Calendar API
gcloud services enable calendar-json.googleapis.com \
  --project=xynergy-dev-1757909467
```

### Step 2: Add Calendar Scope (5 minutes)

**Use the same OAuth credentials as Gmail:**
1. Go to Google Cloud Console
2. Edit the existing OAuth client
3. Add scope: `https://www.googleapis.com/auth/calendar`
4. Save

No new credentials needed - Calendar uses the same OAuth client as Gmail!

### Step 3: Update Calendar Service (45 minutes)

**File:** `calendar-intelligence-service/src/config/config.ts`

```typescript
export const calendarConfig = {
  clientId: process.env.GMAIL_CLIENT_ID, // Reuse Gmail OAuth
  clientSecret: process.env.GMAIL_CLIENT_SECRET,
  redirectUri: `${process.env.API_BASE_URL}/api/v2/calendar/oauth/callback`,
  mockMode: !process.env.GMAIL_CLIENT_ID,
};
```

**File:** `calendar-intelligence-service/src/services/calendarClient.ts`

```typescript
import { google } from 'googleapis';
import { calendarConfig } from '../config/config';

export class CalendarClient {
  private calendar: any;

  constructor(accessToken: string) {
    if (calendarConfig.mockMode) {
      this.calendar = null;
    } else {
      const oauth2Client = new google.auth.OAuth2(
        calendarConfig.clientId,
        calendarConfig.clientSecret,
        calendarConfig.redirectUri
      );
      oauth2Client.setCredentials({ access_token: accessToken });
      this.calendar = google.calendar({ version: 'v3', auth: oauth2Client });
    }
  }

  async getEvents() {
    if (calendarConfig.mockMode) {
      return this.getMockEvents();
    }

    const response = await this.calendar.events.list({
      calendarId: 'primary',
      timeMin: new Date().toISOString(),
      maxResults: 50,
      singleEvents: true,
      orderBy: 'startTime',
    });

    return response.data.items;
  }

  // Additional methods...
}
```

### Step 4: Deploy (30 minutes)

```bash
cd calendar-intelligence-service

# Install googleapis (if not already)
npm install googleapis

# Build and deploy
npm run build

gcloud run deploy calendar-intelligence-service \
  --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-services/calendar-intelligence-service:latest \
  --region us-central1 \
  --project xynergy-dev-1757909467 \
  --set-secrets="GMAIL_CLIENT_ID=GMAIL_CLIENT_ID:latest,GMAIL_CLIENT_SECRET=GMAIL_CLIENT_SECRET:latest"
```

### Step 5: Test (15 minutes)

```bash
# Test Calendar events
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/calendar/events

# Should return real calendar events
```

**Calendar OAuth Complete!** ✅

---

## OAuth Flow Implementation

For user-facing OAuth (connecting user accounts):

### 1. Initiate OAuth Flow

```typescript
// Frontend initiates OAuth
const authUrl = `${API_BASE_URL}/api/v2/slack/oauth/start`;
window.location.href = authUrl;

// Backend /oauth/start endpoint
app.get('/oauth/start', (req, res) => {
  const authUrl = `https://slack.com/oauth/v2/authorize?` +
    `client_id=${SLACK_CLIENT_ID}&` +
    `scope=channels:read,channels:history,chat:write&` +
    `redirect_uri=${REDIRECT_URI}`;
  res.redirect(authUrl);
});
```

### 2. Handle OAuth Callback

```typescript
// Backend /oauth/callback endpoint
app.get('/oauth/callback', async (req, res) => {
  const { code } = req.query;

  // Exchange code for token
  const response = await fetch('https://slack.com/api/oauth.v2.access', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: SLACK_CLIENT_ID,
      client_secret: SLACK_CLIENT_SECRET,
      code,
      redirect_uri: REDIRECT_URI,
    }),
  });

  const data = await response.json();

  // Store access token in Firestore (per user)
  await storeUserToken(req.user.uid, data.access_token);

  // Redirect back to app
  res.redirect('/dashboard?oauth=success');
});
```

### 3. Use Stored Token

```typescript
// When making API calls
const userToken = await getUserToken(userId);
const client = new WebClient(userToken);
const channels = await client.conversations.list();
```

---

## Verification Checklist

### Slack OAuth ✅
- [ ] Slack app created
- [ ] OAuth scopes configured
- [ ] Credentials stored in Secret Manager
- [ ] Service updated with real API calls
- [ ] Service deployed with secrets
- [ ] Real Slack data returned
- [ ] No "mock: true" in responses

### Gmail OAuth ✅
- [ ] Gmail API enabled
- [ ] OAuth credentials created
- [ ] Scopes configured
- [ ] Credentials stored in Secret Manager
- [ ] Service updated with Gmail API
- [ ] Service deployed with secrets
- [ ] Real Gmail data returned
- [ ] No "mock: true" in responses

### Calendar OAuth ✅
- [ ] Calendar API enabled
- [ ] Calendar scope added to OAuth
- [ ] Service updated with Calendar API
- [ ] Service deployed with secrets
- [ ] Real calendar data returned
- [ ] No "mock: true" in responses

---

## Troubleshooting

### Common Issues

**"Invalid OAuth scopes"**
- Solution: Review scopes in Google Cloud Console
- Ensure all required scopes are added

**"Redirect URI mismatch"**
- Solution: Verify redirect URI exactly matches in:
  - OAuth consent screen
  - Service code
  - Cloud Run URL

**"Token expired"**
- Solution: Implement token refresh
- Store refresh token in Firestore
- Refresh before token expiry

**"Service still returns mock data"**
- Solution: Check environment variables are set
- Verify secrets are mounted correctly
- Check service logs for errors

---

## Timeline Summary

| Service | Setup Time | Value |
|---------|-----------|-------|
| Slack OAuth | 4-6 hours | Real workspace data |
| Gmail OAuth | 4-6 hours | Real email data |
| Calendar OAuth | 3-4 hours | Real calendar data |
| **Total** | **11-16 hours** | **Full production data** |

---

## Next Steps After OAuth

1. **Remove Mock Data Completely**
   - Delete mock response functions
   - Remove `mock: true` flags
   - Clean up test data

2. **Implement Token Refresh**
   - Add refresh token storage
   - Implement auto-refresh
   - Handle token expiry gracefully

3. **Add Error Handling**
   - Handle API rate limits
   - Handle OAuth errors
   - Implement retry logic

4. **Monitor OAuth Health**
   - Track token refresh success rate
   - Monitor API call failures
   - Alert on OAuth errors

---

**OAuth Configuration is optional but highly valuable for production deployments!**
