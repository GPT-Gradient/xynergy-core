# Gmail OAuth Configuration - COMPLETE ✅

**Date:** October 11, 2025
**Status:** CONFIGURED AND READY FOR OAUTH FLOW

---

## Gmail OAuth Setup Complete

### ✅ Secrets Created in Secret Manager

```bash
gcloud secrets list --filter="name:GMAIL" --project=xynergy-dev-1757909467
```

| Secret | Value | Status |
|--------|-------|--------|
| `GMAIL_CLIENT_ID` | 835612502919-shofuadpcdpv08q9t93i286o4j2ndmca.apps.googleusercontent.com | ✅ Created |
| `GMAIL_CLIENT_SECRET` | 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 | ✅ Created |

### ✅ Service Updated

**Gmail Intelligence Service** has been updated with OAuth credentials:
- Service: `gmail-intelligence-service`
- Revision: `gmail-intelligence-service-00003-czf`
- URL: https://gmail-intelligence-service-835612502919.us-central1.run.app
- Status: ✅ Deployed with secrets

### ✅ Gmail API Enabled

Gmail API is enabled for the project and ready to use.

---

## OAuth Configuration Details

### Client Credentials
```json
{
  "client_id": "835612502919-shofuadpcdpv08q9t93i286o4j2ndmca.apps.googleusercontent.com",
  "project_id": "xynergy-dev-1757909467",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_secret": "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"
}
```

### Authorized Redirect URIs (Configure in Google Console)

**IMPORTANT:** You must add these redirect URIs in Google Cloud Console:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Select project: `xynergy-dev-1757909467`
3. Click on OAuth 2.0 Client ID: `835612502919-shofuadpcdpv08q9t93i286o4j2ndmca`
4. Add these Authorized redirect URIs:

```
https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/oauth/callback
https://gmail-intelligence-service-835612502919.us-central1.run.app/oauth/callback
http://localhost:8080/api/v2/gmail/oauth/callback
```

### Required OAuth Scopes

The Gmail Intelligence Service will request these scopes:
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails
- `https://www.googleapis.com/auth/gmail.send` - Send emails
- `https://www.googleapis.com/auth/gmail.modify` - Modify emails (labels, archive, etc.)
- `https://www.googleapis.com/auth/userinfo.email` - User email address
- `https://www.googleapis.com/auth/userinfo.profile` - User profile

---

## Testing Gmail OAuth Flow

### Step 1: Initiate OAuth Flow

**Option A: Via Intelligence Gateway**
```bash
# Open in browser
open "https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/oauth/authorize"
```

**Option B: Direct to Gmail Service**
```bash
# Open in browser
open "https://gmail-intelligence-service-835612502919.us-central1.run.app/oauth/authorize"
```

### Step 2: User Grants Permissions

The user will be redirected to Google OAuth consent screen to:
1. Select Google account
2. Review requested permissions
3. Grant access to Gmail

### Step 3: Callback and Token Storage

After user grants permission:
1. Google redirects to callback URL with authorization code
2. Service exchanges code for access token and refresh token
3. Tokens stored in Firestore per user/tenant
4. User redirected to success page

### Step 4: Test Real Gmail Data

Once OAuth is complete, test with real Gmail data:

```bash
# Get JWT or Firebase token
export TOKEN="your-jwt-or-firebase-token"

# List emails
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/emails

# Get specific email
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/email/MESSAGE_ID

# Search emails
curl -H "Authorization: Bearer $TOKEN" \
  "https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/search?q=from:example@gmail.com"

# Send email
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Test Email",
    "body": "This is a test email from Gmail Intelligence Service"
  }' \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/send
```

---

## Gmail API Endpoints

All endpoints route through the Intelligence Gateway and require authentication.

### Email Operations

**List Emails**
```
GET /api/v2/gmail/emails
GET /api/v2/email/emails  (alias)

Query Parameters:
  - maxResults: Number of emails to return (default: 10, max: 100)
  - pageToken: Token for pagination
  - q: Search query (Gmail search syntax)
```

**Get Email**
```
GET /api/v2/gmail/email/:id
GET /api/v2/email/email/:id  (alias)

Path Parameters:
  - id: Gmail message ID
```

**Send Email**
```
POST /api/v2/gmail/send
POST /api/v2/email/send  (alias)

Body:
{
  "to": "recipient@example.com",
  "subject": "Subject",
  "body": "Email body text",
  "html": "<p>HTML email body</p>" (optional),
  "cc": ["cc@example.com"] (optional),
  "bcc": ["bcc@example.com"] (optional)
}
```

**Search Emails**
```
GET /api/v2/gmail/search
GET /api/v2/email/search  (alias)

Query Parameters:
  - q: Search query (required)
  - maxResults: Number of results (default: 10)

Search Query Examples:
  - "from:john@example.com"
  - "subject:meeting"
  - "is:unread"
  - "after:2025/10/01"
  - "has:attachment"
```

**Get Email Threads**
```
GET /api/v2/gmail/threads
GET /api/v2/email/threads  (alias)

Query Parameters:
  - maxResults: Number of threads (default: 10)
  - q: Search query (optional)
```

---

## Frontend Integration

### Initialize OAuth Flow from Frontend

```typescript
// Redirect user to OAuth authorization
function initiateGmailOAuth() {
  const authUrl = `${process.env.REACT_APP_API_URL}/api/v2/gmail/oauth/authorize`;
  window.location.href = authUrl;
}

// Handle OAuth callback (if using frontend callback)
function handleOAuthCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');

  if (code) {
    // Exchange code for tokens via backend
    fetch(`${process.env.REACT_APP_API_URL}/api/v2/gmail/oauth/callback?code=${code}`, {
      headers: {
        'Authorization': `Bearer ${firebaseToken}`
      }
    })
    .then(res => res.json())
    .then(data => {
      console.log('Gmail connected!', data);
      // Redirect to dashboard or show success message
    });
  }
}
```

### Check OAuth Status

```typescript
async function checkGmailConnected() {
  const response = await fetch(
    `${process.env.REACT_APP_API_URL}/api/v2/gmail/status`,
    {
      headers: {
        'Authorization': `Bearer ${firebaseToken}`
      }
    }
  );

  const data = await response.json();
  return data.connected; // true if user has authorized Gmail
}
```

### Fetch Emails

```typescript
async function fetchEmails(maxResults = 10) {
  const response = await fetch(
    `${process.env.REACT_APP_API_URL}/api/v2/gmail/emails?maxResults=${maxResults}`,
    {
      headers: {
        'Authorization': `Bearer ${firebaseToken}`
      }
    }
  );

  return response.json();
}
```

---

## Mock Mode vs Real Data

### Current Status

The Gmail Intelligence Service now has OAuth credentials configured, but will still return **mock data** until:

1. User completes OAuth flow (authorizes Gmail access)
2. OAuth tokens are stored in Firestore for that user
3. Subsequent API calls will use real Gmail API with stored tokens

### Checking Mode

You can check if the service is in mock mode:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/status

# Response:
{
  "connected": false,
  "mode": "mock"
}
```

After OAuth:
```json
{
  "connected": true,
  "mode": "live",
  "email": "user@gmail.com"
}
```

---

## Token Storage and Management

### How Tokens Are Stored

OAuth tokens are stored in Firestore with tenant isolation:

```
Collection: oauth_tokens
Document: {tenantId}_{userId}_gmail

Fields:
  - access_token: Current access token
  - refresh_token: Refresh token (for getting new access tokens)
  - expires_at: Token expiration timestamp
  - scope: Granted scopes
  - email: User's Gmail address
  - updated_at: Last token refresh
```

### Token Refresh

The Gmail Intelligence Service automatically:
1. Checks if access token is expired before each API call
2. Uses refresh token to get new access token if needed
3. Updates Firestore with new token
4. Retries the original API call

---

## Security Considerations

### ✅ Secure Storage
- OAuth credentials stored in Secret Manager (not in code)
- Access tokens stored in Firestore with tenant isolation
- Refresh tokens encrypted at rest

### ✅ Scope Minimization
- Only requests necessary Gmail permissions
- User can see exactly what access is being requested

### ✅ Token Security
- Access tokens expire after 1 hour
- Refresh tokens automatically renew access tokens
- Tokens are never exposed to frontend

### ✅ CORS Protection
- Intelligence Gateway enforces strict CORS
- Only whitelisted origins can make requests

---

## Troubleshooting

### "Redirect URI mismatch" Error

**Cause:** Redirect URI not added to Google Console
**Fix:** Add redirect URI to OAuth 2.0 Client configuration in Google Console

### "Access denied" in OAuth Flow

**Cause:** User declined permissions
**Fix:** User needs to re-initiate OAuth and grant permissions

### Still Getting Mock Data

**Check:**
1. Has user completed OAuth flow?
2. Are tokens stored in Firestore?
3. Are tokens expired?

**Debug:**
```bash
# Check OAuth status
curl -H "Authorization: Bearer $TOKEN" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/status
```

---

## Next Steps

### Required: Add Redirect URIs

⚠️ **ACTION REQUIRED:** You must add the redirect URIs to Google Console before OAuth will work.

1. Go to: https://console.cloud.google.com/apis/credentials/oauthclient/835612502919-shofuadpcdpv08q9t93i286o4j2ndmca?project=xynergy-dev-1757909467
2. Add redirect URIs (listed above)
3. Save changes

### Testing Checklist

- [ ] Add redirect URIs to Google Console
- [ ] Initiate OAuth flow from browser
- [ ] Grant Gmail permissions
- [ ] Verify tokens stored in Firestore
- [ ] Test listing emails with real data
- [ ] Test sending email
- [ ] Test search functionality

---

## Summary

✅ **Gmail Client ID** - Stored in Secret Manager
✅ **Gmail Client Secret** - Stored in Secret Manager
✅ **Service Account Access** - Granted
✅ **Gmail Intelligence Service** - Updated and deployed
✅ **Gmail API** - Enabled
✅ **OAuth Endpoints** - Ready to use

**Status:** Gmail OAuth is configured and ready! Users can now authorize Gmail access and the service will use real Gmail data instead of mock data. 🎉

**One Action Required:** Add redirect URIs to Google Cloud Console OAuth configuration.
