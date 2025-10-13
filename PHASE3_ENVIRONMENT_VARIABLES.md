# Phase 3: Required Environment Variables

**Date:** October 13, 2025

This document describes the environment variables required for Phase 3 OAuth Token Usage implementation.

---

## Critical: Token Encryption Key

### `TOKEN_ENCRYPTION_KEY`

**Required for:** Both Slack Intelligence Service and Gmail Intelligence Service

**Purpose:** Encrypts/decrypts user OAuth tokens stored in Firestore using AES-256-GCM

**Format:** 64-character hexadecimal string (32 bytes)

**Generate:**
```bash
# Generate a new encryption key
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Example:**
```
TOKEN_ENCRYPTION_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

**Security:**
- ⚠️ **CRITICAL**: Keep this secret secure
- Store in Google Secret Manager, not in code
- Use the same key across all services that share token storage
- If lost, all stored OAuth tokens become unreadable (users must reconnect)

**Setting in Cloud Run:**
```bash
# For Slack Intelligence Service
gcloud run services update slack-intelligence-service \
  --region us-central1 \
  --project xynergy-dev-1757909467 \
  --set-env-vars="TOKEN_ENCRYPTION_KEY=your-generated-key-here"

# For Gmail Intelligence Service
gcloud run services update gmail-intelligence-service \
  --region us-central1 \
  --project xynergy-dev-1757909467 \
  --set-env-vars="TOKEN_ENCRYPTION_KEY=your-generated-key-here"
```

**Using Google Secret Manager (Recommended):**
```bash
# Create secret
echo -n "your-generated-key-here" | gcloud secrets create token-encryption-key \
  --data-file=- \
  --project xynergy-dev-1757909467

# Grant access to service accounts
gcloud secrets add-iam-policy-binding token-encryption-key \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project xynergy-dev-1757909467

# Update Cloud Run to use secret
gcloud run services update slack-intelligence-service \
  --region us-central1 \
  --project xynergy-dev-1757909467 \
  --update-secrets="TOKEN_ENCRYPTION_KEY=token-encryption-key:latest"
```

---

## OAuth App Credentials

### Slack OAuth Credentials

**Required for:** Slack Intelligence Service

**Variables:**
```bash
SLACK_CLIENT_ID=your-slack-app-client-id
SLACK_CLIENT_SECRET=your-slack-app-client-secret
SLACK_SIGNING_SECRET=your-slack-signing-secret  # For webhook verification
```

**Where to get:**
1. Go to https://api.slack.com/apps
2. Select your app
3. Navigate to "Basic Information"
4. Copy Client ID and Client Secret
5. Copy Signing Secret

**OAuth Scopes Required:**
- `channels:read` - Read public channel info
- `channels:history` - Read messages from public channels
- `chat:write` - Post messages
- `users:read` - Read user information
- `search:read` - Search workspace

### Gmail OAuth Credentials

**Required for:** Gmail Intelligence Service

**Variables:**
```bash
GMAIL_CLIENT_ID=your-google-oauth-client-id
GMAIL_CLIENT_SECRET=your-google-oauth-client-secret
GMAIL_REDIRECT_URI=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v1/oauth/gmail/callback
```

**Where to get:**
1. Go to https://console.cloud.google.com/apis/credentials
2. Select project: `xynergy-dev-1757909467`
3. Create OAuth 2.0 Client ID (or use existing)
4. Application type: Web application
5. Add authorized redirect URIs
6. Copy Client ID and Client Secret

**OAuth Scopes Required:**
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails
- `https://www.googleapis.com/auth/gmail.send` - Send emails
- `https://www.googleapis.com/auth/gmail.modify` - Modify emails (labels, etc.)

---

## Deprecated Environment Variables

### `SLACK_BOT_TOKEN` (Deprecated)

**Status:** ⚠️ **DEPRECATED** as of Phase 3

**Previously:** Used as shared bot token for all users (security issue)

**Now:** Services use per-user OAuth tokens from Firestore

**Action:** Can be removed from environment, or kept for backward compatibility (not accessed by service)

---

## Firebase / Firestore

### Firestore Authentication

**Required for:** Both services (to access Firestore for token retrieval)

**Variables:**
```bash
FIREBASE_PROJECT_ID=xynergy-dev-1757909467
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Note:** Cloud Run services typically use default service account credentials automatically. Only needed for local development.

---

## Environment Variable Summary

### Slack Intelligence Service - Required
```bash
# Critical
TOKEN_ENCRYPTION_KEY=<64-char-hex>

# OAuth Credentials
SLACK_CLIENT_ID=<your-client-id>
SLACK_CLIENT_SECRET=<your-client-secret>
SLACK_SIGNING_SECRET=<your-signing-secret>

# Firebase (usually auto-configured on Cloud Run)
FIREBASE_PROJECT_ID=xynergy-dev-1757909467
```

### Gmail Intelligence Service - Required
```bash
# Critical
TOKEN_ENCRYPTION_KEY=<64-char-hex>

# OAuth Credentials
GMAIL_CLIENT_ID=<your-client-id>
GMAIL_CLIENT_SECRET=<your-client-secret>
GMAIL_REDIRECT_URI=<your-redirect-uri>

# Firebase (usually auto-configured on Cloud Run)
FIREBASE_PROJECT_ID=xynergy-dev-1757909467
```

---

## Deployment Checklist

- [ ] Generate `TOKEN_ENCRYPTION_KEY` (same key for both services)
- [ ] Store encryption key in Google Secret Manager
- [ ] Configure Slack OAuth app and get credentials
- [ ] Configure Google OAuth app and get credentials
- [ ] Set environment variables in Cloud Run services
- [ ] Remove or document `SLACK_BOT_TOKEN` as deprecated
- [ ] Verify services can access Firestore
- [ ] Test OAuth flow end-to-end
- [ ] Verify per-user token retrieval works

---

## Security Best Practices

1. **Never commit secrets to git**
2. **Use Google Secret Manager for production**
3. **Rotate encryption key periodically** (requires users to reconnect)
4. **Limit OAuth scopes** to minimum required permissions
5. **Monitor OAuth token usage** in logs
6. **Implement token refresh** before expiry (future enhancement)

---

## Troubleshooting

### "OAuth not configured" error
- Check that `SLACK_CLIENT_ID` / `GMAIL_CLIENT_ID` are set
- Check that `SLACK_CLIENT_SECRET` / `GMAIL_CLIENT_SECRET` are set
- Verify environment variables are loaded in Cloud Run

### "Slack/Gmail not connected" error
- User has not completed OAuth flow
- User needs to connect account in Settings > Integrations
- Check that OAuth token exists in Firestore: `oauth_tokens/{userId}_slack`

### "Invalid encrypted data format" error
- `TOKEN_ENCRYPTION_KEY` mismatch between services
- Token was encrypted with different key
- Ensure same key is used across all services

### "Token expired" error
- OAuth token has expired
- User needs to reconnect account
- Future: Implement automatic token refresh

---

## Next Steps

After Phase 3 deployment, verify:

1. Services start without errors
2. Health checks pass
3. Users can connect OAuth accounts
4. Per-user tokens are retrieved correctly
5. API calls use user's personal tokens
6. Different users see different data

Then proceed to **Phase 4: Integrations Management** to create unified integration management interface.
