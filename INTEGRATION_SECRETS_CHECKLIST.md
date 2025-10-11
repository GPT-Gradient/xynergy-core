# Platform Integration - Secrets Collection Checklist

**Created:** October 10, 2025
**Purpose:** Collect all required API keys, secrets, and credentials for platform integration
**Status:** 🔴 COLLECTING

---

## 1. AUTHENTICATION SECRETS

### JWT Secret (Priority: P0 - CRITICAL)
**Service:** Intelligence Gateway + All TypeScript services
**Purpose:** Validate JWT tokens from frontend

- [ ] **JWT_SECRET**
  - **Current Location:** Check `xynergyos-backend` environment variables
  - **How to Get:**
    ```bash
    gcloud run services describe xynergyos-backend \
      --region us-central1 \
      --format="value(spec.template.spec.containers[0].env)" \
      | grep JWT_SECRET_KEY
    ```
  - **Expected Format:** Base64 string or long hex string
  - **Example:** `8f4a9e2b7c1d5f3a6e8b9c4d2f7a1e5b3c6d8f4a9e2b7c1d5f3a6e8b9c4d2f7a`
  - **Secret Manager Command:**
    ```bash
    echo -n "YOUR_JWT_SECRET_HERE" | gcloud secrets create JWT_SECRET --data-file=-
    ```

---

## 2. SLACK OAUTH CREDENTIALS ✅ COMPLETE

### Status: CONFIGURED AND DEPLOYED

### Completed Secrets
- ✅ **SLACK_CLIENT_ID:** `9675918053013.9709558335008`
  - Stored in Secret Manager: `SLACK_CLIENT_ID`
  - Service account access granted

- ✅ **SLACK_CLIENT_SECRET:** `488dfbc5d5f8605192b657f6a56943e5`
  - Stored in Secret Manager: `SLACK_CLIENT_SECRET`
  - Service account access granted

- ✅ **SLACK_SIGNING_SECRET:** `4c6b950b7084d78d002e4ddba3d50ed4`
  - Stored in Secret Manager: `SLACK_SIGNING_SECRET`
  - Service account access granted

### Slack App Details
- **App ID:** A09LVGE9V08
- **Verification Token:** M59rzvpyYVZ6k9pLU7XakJDL
- **Manage App:** https://api.slack.com/apps/A09LVGE9V08

### Service Status
- ✅ Slack Intelligence Service updated with OAuth credentials
- ✅ Service URL: https://slack-intelligence-service-835612502919.us-central1.run.app
- ✅ Ready for OAuth flow

### ⚠️ Action Required: Configure Slack App

**You must configure redirect URLs and scopes in Slack App:**

1. **Add Redirect URLs:** https://api.slack.com/apps/A09LVGE9V08/oauth
   ```
   https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/oauth/callback
   https://slack-intelligence-service-835612502919.us-central1.run.app/oauth/callback
   http://localhost:8080/api/v2/slack/oauth/callback
   ```

2. **Add Bot Token Scopes:** https://api.slack.com/apps/A09LVGE9V08/oauth (scroll to Scopes)
   - `channels:read` - View basic channel information
   - `channels:history` - View messages in public channels
   - `chat:write` - Send messages
   - `users:read` - View users in workspace
   - `users:read.email` - View email addresses

3. **Reinstall App** (if previously installed) to apply new scopes

**Complete documentation:** `SLACK_OAUTH_COMPLETE.md`

---

## 3. GMAIL/GOOGLE OAUTH CREDENTIALS ✅ COMPLETE

### Status: CONFIGURED AND DEPLOYED

### Completed Secrets
- ✅ **GMAIL_CLIENT_ID:** `835612502919-shofuadpcdpv08q9t93i286o4j2ndmca.apps.googleusercontent.com`
  - Stored in Secret Manager: `GMAIL_CLIENT_ID`
  - Service account access granted

- ✅ **GMAIL_CLIENT_SECRET:** `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`
  - Stored in Secret Manager: `GMAIL_CLIENT_SECRET`
  - Service account access granted

### Service Status
- ✅ Gmail Intelligence Service updated with OAuth credentials
- ✅ Gmail API enabled
- ✅ Service URL: https://gmail-intelligence-service-835612502919.us-central1.run.app
- ✅ Ready for OAuth flow

### ⚠️ Action Required: Add Redirect URIs

**You must add these redirect URIs in Google Cloud Console:**

1. Go to: https://console.cloud.google.com/apis/credentials/oauthclient/835612502919-shofuadpcdpv08q9t93i286o4j2ndmca?project=xynergy-dev-1757909467
2. Click "ADD URI" under "Authorized redirect URIs"
3. Add these URLs:
   ```
   https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/oauth/callback
   https://gmail-intelligence-service-835612502919.us-central1.run.app/oauth/callback
   http://localhost:8080/api/v2/gmail/oauth/callback
   ```
4. Click "SAVE"

**Complete documentation:** `GMAIL_OAUTH_COMPLETE.md`

### Google API Scopes Required
These will be requested during OAuth flow:
- [x] `https://www.googleapis.com/auth/gmail.readonly` - Read emails
- [x] `https://www.googleapis.com/auth/gmail.send` - Send emails
- [x] `https://www.googleapis.com/auth/gmail.modify` - Modify emails
- [x] `https://www.googleapis.com/auth/calendar` - Calendar access (for future calendar service)

### Google OAuth Redirect URLs
Add these to GCP Console → Credentials → OAuth 2.0 Client → Authorized redirect URIs:
```
https://xynergy-intelligence-gateway-vgjxy554mq-uc.a.run.app/api/v2/gmail/oauth/callback
https://xynergy-intelligence-gateway-vgjxy554mq-uc.a.run.app/api/v2/calendar/oauth/callback
```

### Google APIs to Enable
Run these commands:
```bash
gcloud services enable gmail.googleapis.com --project=xynergy-dev-1757909467
gcloud services enable calendar-json.googleapis.com --project=xynergy-dev-1757909467
```

---

## 4. FIREBASE CONFIGURATION ✅ COMPLETE

### Status: CONFIGURED AND READY

### Completed Values
- ✅ **FIREBASE_API_KEY:** `AIzaSyDV3dfxDiqBpNi3IWpKH8nZ3jr4kSpXxDw`
  - Stored in Secret Manager: `FIREBASE_API_KEY`
  - Safe for frontend code
  - Frontend Env Var: `REACT_APP_FIREBASE_API_KEY`

- ✅ **FIREBASE_APP_ID:** `1:835612502919:web:700fd8d6f2e5843c3b4122`
  - Stored in Secret Manager: `FIREBASE_APP_ID`
  - Safe for frontend code
  - Frontend Env Var: `REACT_APP_FIREBASE_APP_ID`

- ✅ **FIREBASE_PROJECT_ID:** `xynergy-dev-1757909467`
- ✅ **FIREBASE_AUTH_DOMAIN:** `xynergy-dev-1757909467.firebaseapp.com`
- ✅ **FIREBASE_STORAGE_BUCKET:** `xynergy-dev-1757909467.firebasestorage.app`
- ✅ **FIREBASE_MESSAGING_SENDER_ID:** `835612502919`
- ✅ **FIREBASE_MEASUREMENT_ID:** `G-YTWVDK6Q42`

### Frontend Config Files Created
- ✅ `.env.production` - Production configuration
- ✅ `.env.development` - Development configuration
- ✅ Complete documentation: `FIREBASE_CONFIG_COMPLETE.md`

---

## 5. FRONTEND ENVIRONMENT VARIABLES

### Complete Configuration File
Once you collect the above, provide this to frontend team:

```bash
# .env.production

# API Endpoints
REACT_APP_API_URL=https://xynergy-intelligence-gateway-vgjxy554mq-uc.a.run.app
REACT_APP_WS_URL=wss://xynergy-intelligence-gateway-vgjxy554mq-uc.a.run.app

# Firebase Configuration
REACT_APP_FIREBASE_PROJECT_ID=xynergy-dev-1757909467
REACT_APP_FIREBASE_API_KEY=[FROM FIREBASE CONSOLE]
REACT_APP_FIREBASE_AUTH_DOMAIN=xynergy-dev-1757909467.firebaseapp.com
REACT_APP_FIREBASE_APP_ID=[FROM FIREBASE CONSOLE]

# Optional: Feature flags
REACT_APP_ENABLE_MOCK_MODE=false
REACT_APP_ENABLE_WEBSOCKETS=true
```

---

## 6. CORS ORIGINS CONFIGURATION

### Current Approved Origins
These should already be configured, but verify:

```bash
# Development
http://localhost:3000

# Production Frontend
https://xynergyos-frontend-vgjxy554mq-uc.a.run.app

# Wildcard for subdomains (if using custom domain)
https://*.xynergyos.com
```

### Verification Command
```bash
gcloud run services describe xynergy-intelligence-gateway \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)" \
  | grep CORS_ORIGINS
```

---

## 7. SECRET MANAGER PERMISSIONS

### Verify Service Account Has Access
Run this to ensure Cloud Run services can read secrets:

```bash
PROJECT_ID="xynergy-dev-1757909467"
PROJECT_NUMBER="835612502919"
SERVICE_ACCOUNT="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 8. DEPLOYMENT CHECKLIST

### After All Secrets Are Created

- [ ] **Update Intelligence Gateway**
  ```bash
  gcloud run services update xynergy-intelligence-gateway \
    --update-secrets=JWT_SECRET=JWT_SECRET:latest \
    --region=us-central1 \
    --project=xynergy-dev-1757909467
  ```

- [ ] **Update Slack Intelligence Service**
  ```bash
  gcloud run services update slack-intelligence-service \
    --update-secrets=SLACK_BOT_TOKEN=SLACK_BOT_TOKEN:latest \
    --update-secrets=SLACK_CLIENT_ID=SLACK_CLIENT_ID:latest \
    --update-secrets=SLACK_CLIENT_SECRET=SLACK_CLIENT_SECRET:latest \
    --update-secrets=SLACK_SIGNING_SECRET=SLACK_SIGNING_SECRET:latest \
    --region=us-central1 \
    --project=xynergy-dev-1757909467
  ```

- [ ] **Update Gmail Intelligence Service**
  ```bash
  gcloud run services update gmail-intelligence-service \
    --update-secrets=GMAIL_CLIENT_ID=GMAIL_CLIENT_ID:latest \
    --update-secrets=GMAIL_CLIENT_SECRET=GMAIL_CLIENT_SECRET:latest \
    --region=us-central1 \
    --project=xynergy-dev-1757909467
  ```

---

## 9. TESTING CHECKLIST

### After Secrets Are Deployed

- [ ] Test JWT authentication
  ```bash
  # Get JWT token from xynergyos-backend login endpoint
  # Test gateway with JWT token
  curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    https://xynergy-intelligence-gateway-vgjxy554mq-uc.a.run.app/api/v2/crm/contacts
  ```

- [ ] Test Slack OAuth flow
  ```bash
  # Visit OAuth URL in browser
  open "https://xynergy-intelligence-gateway-vgjxy554mq-uc.a.run.app/api/v2/slack/oauth/authorize"
  ```

- [ ] Test Gmail OAuth flow
  ```bash
  # Visit OAuth URL in browser
  open "https://xynergy-intelligence-gateway-vgjxy554mq-uc.a.run.app/api/v2/gmail/oauth/authorize"
  ```

- [ ] Test real Slack data
  ```bash
  curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    https://xynergy-intelligence-gateway-vgjxy554mq-uc.a.run.app/api/v2/slack/channels
  ```

- [ ] Test real Gmail data
  ```bash
  curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
    https://xynergy-intelligence-gateway-vgjxy554mq-uc.a.run.app/api/v2/gmail/messages
  ```

---

## 10. QUICK REFERENCE COMMANDS

### View All Secrets
```bash
gcloud secrets list --project=xynergy-dev-1757909467
```

### View Secret Value (for debugging)
```bash
gcloud secrets versions access latest --secret="JWT_SECRET" --project=xynergy-dev-1757909467
```

### Delete Secret (if you need to recreate)
```bash
gcloud secrets delete SECRET_NAME --project=xynergy-dev-1757909467
```

### Grant Service Account Access to Specific Secret
```bash
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=xynergy-dev-1757909467
```

---

## SUMMARY

**Total Secrets to Collect:** 9
- 1 JWT Secret (from existing backend)
- 5 Slack credentials (from Slack App)
- 2 Gmail credentials (from GCP Console)
- 2 Firebase values (from Firebase Console)

**Estimated Time:** 30-45 minutes
- 5 min: Extract JWT secret from xynergyos-backend
- 15 min: Create and configure Slack app
- 10 min: Create Google OAuth credentials
- 5 min: Get Firebase configuration
- 10 min: Add all secrets to Secret Manager

**Priority Order:**
1. JWT_SECRET (blocker for all authentication)
2. Firebase values (blocker for frontend deployment)
3. Slack credentials (needed for real data)
4. Gmail credentials (needed for real data)

---

**STATUS TRACKING:**

- [x] Section 1: JWT Secret - ✅ COMPLETE
- [x] Section 2: Slack OAuth - ✅ COMPLETE (Need to configure Slack App)
- [x] Section 3: Gmail OAuth - ✅ COMPLETE (Redirect URIs added)
- [x] Section 4: Firebase Config - ✅ COMPLETE
- [x] Section 5: Frontend Env File Created - ✅ COMPLETE
- [x] Section 8: All Secrets Deployed - ✅ COMPLETE
- [ ] Section 9: All Tests Passing - ⏳ TESTING PHASE (Ready for OAuth flows)

**Status:** 🎉 ALL SECRETS CONFIGURED! Ready for Slack App configuration and OAuth testing.
