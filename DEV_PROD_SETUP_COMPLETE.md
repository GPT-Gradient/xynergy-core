# Dev/Production Environment Setup - COMPLETE

**Date:** October 13, 2025
**Status:** ✅ Fully Configured and Ready to Use

---

## Executive Summary

The XynergyOS Intelligence Gateway now has complete dev/production environment separation using a **same-project, different-service** approach. This setup allows safe development with mock data while maintaining a separate production environment with real data and OAuth credentials.

**Key Achievement:** Complete environment separation within a single GCP project, with environment-specific configurations, secrets, caching, and deployment workflows.

---

## Architecture Overview

```
xynergy-dev-1757909467 (Single GCP Project)
│
├── Development Services
│   ├── xynergyos-intelligence-gateway (current)
│   ├── slack-intelligence-service
│   ├── gmail-intelligence-service
│   └── crm-engine
│
├── Production Services
│   ├── xynergyos-intelligence-gateway-prod (new)
│   ├── slack-intelligence-service-prod (future)
│   ├── gmail-intelligence-service-prod (future)
│   └── crm-engine-prod (future)
│
├── Firestore Collections
│   ├── dev_users, dev_projects, dev_tasks, dev_notifications
│   └── prod_users, prod_projects, prod_tasks, prod_notifications
│
├── Redis Cache
│   ├── dev:* keys (development cache)
│   └── prod:* keys (production cache)
│
└── Secret Manager
    ├── jwt-secret-dev, slack-secret-dev, gmail-secret-dev
    └── jwt-secret-prod, slack-secret-prod, gmail-secret-prod
```

---

## What Was Implemented

### 1. Environment Detection System

**Updated `/src/config/config.ts`:**
- Added `environment` field: 'dev' | 'prod' | 'local'
- Added `mockMode` boolean (auto-enabled in dev, disabled in prod)
- Added `firestore.collectionPrefix` (dev_ or prod_)
- Added `redis.keyPrefix` (dev: or prod:)
- Environment-specific CORS origins
- Environment-specific rate limits
- Startup logging with environment info

**Environment Detection Logic:**
```typescript
// Detects from XYNERGY_ENV environment variable
const environment = process.env.XYNERGY_ENV || 'dev';

// Mock mode automatically enabled in dev
const mockMode = environment !== 'prod';

// Collection prefix for Firestore
collectionPrefix: environment === 'prod' ? 'prod_' : 'dev_'

// Redis key prefix
keyPrefix: environment === 'prod' ? 'prod:' : 'dev:'
```

### 2. Cloud Build CI/CD Setup

**Created:**
- `cloudbuild-dev.yaml` - Auto-deploy to dev on push to main
- `cloudbuild-prod.yaml` - Deploy to prod on version tags
- `scripts/setup-cloud-build-triggers.sh` - Helper script to create triggers
- `docs/CLOUD_BUILD_TRIGGERS_SETUP.md` - Comprehensive CI/CD documentation

**Service Account Permissions Granted:**
- Cloud Run Admin - Deploy services
- Service Account User - Deploy as service
- Secret Manager Secret Accessor - Access secrets
- Artifact Registry Writer - Push container images

**Triggers:**
- **DEV:** Automatically deploys on push to `main` branch
- **PROD:** Deploys on version tags matching `v1.0.0`, `v2.3.5`, etc.

### 3. Environment Files

**Created:**
- `.env.local` - For local development (git-ignored)
- `.env.dev.example` - Example dev environment config
- `.env.prod.example` - Example prod environment config
- Updated `.gitignore` - Prevents committing secrets

**Local Development (.env.local):**
```bash
XYNERGY_ENV=local
MOCK_MODE=true
JWT_SECRET=local-dev-secret
```

**Dev Deployment (set in Cloud Run):**
```bash
XYNERGY_ENV=dev
MOCK_MODE=true
# Secrets from Secret Manager
```

**Prod Deployment (set in Cloud Run):**
```bash
XYNERGY_ENV=prod
MOCK_MODE=false
# Secrets from Secret Manager
```

### 3. Deployment Scripts

**Created `scripts/deploy-dev.sh`:**
- Builds and deploys to development service
- Uses `dev` image tags
- Sets XYNERGY_ENV=dev, MOCK_MODE=true
- Min instances: 0 (scale to zero)
- Max instances: 10

**Created `scripts/deploy-prod.sh`:**
- Interactive confirmation prompts
- Verifies git branch (must be main)
- Verifies clean working directory
- Uses version tags (v1.0.0)
- Sets XYNERGY_ENV=prod, MOCK_MODE=false
- Min instances: 1 (always warm)
- Max instances: 50
- Deploys with --no-traffic for gradual rollout

### 4. Cloud Build CI/CD

**Created `cloudbuild-dev.yaml`:**
- Triggers on push to main branch
- Builds and deploys to dev automatically
- Tags: dev, dev-{commit}, dev-{build-id}

**Created `cloudbuild-prod.yaml`:**
- Triggers on git tags (v1.0.0, v1.0.1, etc.)
- Runs tests before deployment
- Tags: prod, {version}, prod-{commit}
- Deploys with --no-traffic for safety
- Requires manual traffic migration

### 5. GCP Secret Manager

**Development Secrets:**
```bash
jwt-secret-dev       ✅ Created
slack-secret-dev     ✅ Created (placeholder)
gmail-secret-dev     ✅ Created (placeholder)
```

**Production Secrets:**
```bash
jwt-secret-prod      ✅ Created (strong random)
slack-secret-prod    ✅ Created (needs real value)
gmail-secret-prod    ✅ Created (needs real value)
```

### 6. Cache Service Updates

**Updated `/src/services/cacheService.ts`:**
- Added environment prefix to all cache keys
- Dev uses: `dev:service:endpoint:params`
- Prod uses: `prod:service:endpoint:params`
- Complete cache isolation between environments

---

## How To Use

### Local Development

```bash
cd xynergyos-intelligence-gateway

# Copy environment template
cp .env.local .env

# Install dependencies
npm install

# Run locally
npm run dev

# Your service is now running with:
# - Environment: LOCAL
# - Mock Mode: ENABLED
# - Port: 8080
```

### Deploy to Development

```bash
cd xynergyos-intelligence-gateway

# Option 1: Manual deployment
./scripts/deploy-dev.sh

# Option 2: Auto-deploy via Git
git add .
git commit -m "feat: add new feature"
git push origin main
# Cloud Build automatically deploys to dev
```

### Deploy to Production

```bash
cd xynergyos-intelligence-gateway

# Ensure you're on main branch
git checkout main
git pull

# Create a version tag
git tag -a v1.0.0 -m "Release v1.0.0: Initial production release"
git push origin v1.0.0

# Cloud Build automatically:
# 1. Builds the image
# 2. Deploys to prod with NO TRAFFIC
# 3. Outputs instructions for traffic migration

# Manually migrate traffic (gradual rollout)
gcloud run services update-traffic xynergyos-intelligence-gateway-prod \
  --to-revisions=LATEST=10 \
  --region=us-central1

# If all looks good, continue
gcloud run services update-traffic xynergyos-intelligence-gateway-prod \
  --to-latest \
  --region=us-central1
```

---

## Environment URLs

### Development
- **Gateway:** https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
- **Purpose:** Testing, development, experiments
- **Data:** Mock/test data (dev_ collections)
- **OAuth:** Dev credentials (or mock mode)
- **Cache:** dev:* keys

### Production
- **Gateway:** https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app (after first deploy)
- **Purpose:** Real users, production traffic
- **Data:** Real data (prod_ collections)
- **OAuth:** Real production credentials
- **Cache:** prod:* keys

---

## Data Isolation

### Firestore Collections

**Development:**
```
dev_users
dev_projects
dev_tasks
dev_notifications
dev_oauth_tokens
```

**Production:**
```
prod_users
prod_projects
prod_tasks
prod_notifications
prod_oauth_tokens
```

### Redis Cache Keys

**Development:**
```
dev:slack:channels:user123
dev:gmail:messages:user456
dev:crm:contacts:user789
```

**Production:**
```
prod:slack:channels:user123
prod:gmail:messages:user456
prod:crm:contacts:user789
```

**Complete cache isolation - dev and prod never share cache entries.**

---

## Secret Management

### Viewing Secrets

```bash
# List all secrets
gcloud secrets list --project=xynergy-dev-1757909467

# View dev JWT secret
gcloud secrets versions access latest --secret=jwt-secret-dev --project=xynergy-dev-1757909467

# View prod JWT secret
gcloud secrets versions access latest --secret=jwt-secret-prod --project=xynergy-dev-1757909467
```

### Updating Secrets

```bash
# Update Slack production secret with real OAuth secret
echo -n "YOUR-REAL-SLACK-SECRET" | gcloud secrets versions add slack-secret-prod \
  --data-file=- \
  --project=xynergy-dev-1757909467

# Update Gmail production secret
echo -n "YOUR-REAL-GMAIL-SECRET" | gcloud secrets versions add gmail-secret-prod \
  --data-file=- \
  --project=xynergy-dev-1757909467
```

### Best Practices

1. **Never commit secrets to git** - Use Secret Manager
2. **Different secrets for dev/prod** - Never reuse
3. **Rotate regularly** - Update production secrets quarterly
4. **Use strong secrets in prod** - At least 64 characters
5. **Placeholder secrets in dev** - Don't need to be secure

---

## Mock Mode Behavior

### Development (Mock Mode Enabled)

```typescript
// Services return mock data
slackService.listChannels() → Returns hardcoded channels
gmailService.listMessages() → Returns sample emails
crmService.listContacts() → Returns test contacts

// No real API calls
// No OAuth required
// Safe for testing
```

### Production (Mock Mode Disabled)

```typescript
// Services use real APIs
slackService.listChannels() → Calls Slack API with user's OAuth token
gmailService.listMessages() → Calls Gmail API with user's OAuth token
crmService.listContacts() → Queries Firestore with real data

// Real OAuth required
// Real API calls
// Real billing
```

---

## Deployment Workflow Examples

### Example 1: Adding a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/new-intelligence-api

# 2. Make changes
# ... edit code ...

# 3. Test locally
npm run dev
curl http://localhost:8080/api/v1/intelligence/new-endpoint

# 4. Commit and push
git add .
git commit -m "feat: add new intelligence endpoint"
git push origin feature/new-intelligence-api

# 5. Merge to main
git checkout main
git merge feature/new-intelligence-api
git push origin main

# 6. Auto-deploys to DEV via Cloud Build

# 7. Test in dev environment
curl https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v1/intelligence/new-endpoint

# 8. When ready for production, create tag
git tag -a v1.1.0 -m "Release v1.1.0: Add new intelligence endpoint"
git push origin v1.1.0

# 9. Cloud Build auto-deploys to PROD (no traffic)

# 10. Gradually roll out production traffic
gcloud run services update-traffic xynergyos-intelligence-gateway-prod --to-latest --region=us-central1
```

### Example 2: Hotfix for Production

```bash
# 1. Create hotfix branch from production tag
git checkout v1.0.0
git checkout -b hotfix/critical-bug

# 2. Fix the bug
# ... edit code ...

# 3. Test locally
npm run dev

# 4. Commit fix
git add .
git commit -m "fix: resolve critical authentication bug"

# 5. Merge to main
git checkout main
git merge hotfix/critical-bug
git push origin main

# 6. Create patch version tag
git tag -a v1.0.1 -m "Release v1.0.1: Fix authentication bug"
git push origin v1.0.1

# 7. Auto-deploys to prod
# Follow gradual rollout process
```

---

## Monitoring and Observability

### Check Current Environment

```bash
# Dev service
curl https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/health

# Prod service
curl https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app/health

# Look for environment info in logs
gcloud logging read "resource.type=cloud_run_revision AND textPayload:\"Environment:\"" --limit=1
```

### View Logs

```bash
# Dev logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=xynergyos-intelligence-gateway" --limit=50

# Prod logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=xynergyos-intelligence-gateway-prod" --limit=50
```

### Metrics

```bash
# Dev service metrics
gcloud monitoring timeseries list \
  --filter='metric.type="run.googleapis.com/request_count" AND resource.labels.service_name="xynergyos-intelligence-gateway"' \
  --format=json

# Prod service metrics
gcloud monitoring timeseries list \
  --filter='metric.type="run.googleapis.com/request_count" AND resource.labels.service_name="xynergyos-intelligence-gateway-prod"' \
  --format=json
```

---

## Rollback Procedures

### Rollback Development

```bash
# List recent revisions
gcloud run revisions list \
  --service=xynergyos-intelligence-gateway \
  --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic xynergyos-intelligence-gateway \
  --to-revisions=xynergyos-intelligence-gateway-00025-np8=100 \
  --region=us-central1
```

### Rollback Production

```bash
# List recent revisions
gcloud run revisions list \
  --service=xynergyos-intelligence-gateway-prod \
  --region=us-central1

# Rollback to previous version
gcloud run services update-traffic xynergyos-intelligence-gateway-prod \
  --to-revisions=xynergyos-intelligence-gateway-prod-00001-xyz=100 \
  --region=us-central1

# Or deploy specific version tag
gcloud run deploy xynergyos-intelligence-gateway-prod \
  --image=us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-services/xynergyos-intelligence-gateway:v1.0.0 \
  --region=us-central1
```

---

## Cost Estimates

### Development Environment
- **Cloud Run:** ~$20-50/month (scales to zero when idle)
- **Firestore:** ~$10/month (test data, low volume)
- **Redis:** Shared with prod (~$0 additional)
- **Cloud Build:** ~$10/month (free tier covers most)
- **Total:** ~$40-70/month

### Production Environment
- **Cloud Run:** ~$200-400/month (min 1 instance, real traffic)
- **Firestore:** ~$50-100/month (real user data)
- **Redis:** ~$100/month (shared, mostly prod usage)
- **Cloud Build:** ~$5/month (infrequent deployments)
- **Total:** ~$355-605/month

**Combined Total:** ~$395-675/month

---

## Setup Cloud Build Triggers (Optional)

To enable automatic deployments, setup Cloud Build triggers:

**✅ Service Account Permissions Already Granted:**
- Cloud Run Admin
- Service Account User
- Secret Manager Secret Accessor
- Artifact Registry Writer

**Setup Triggers:**

```bash
# Run the helper script (recommended)
cd xynergyos-intelligence-gateway
./scripts/setup-cloud-build-triggers.sh

# Or manually create triggers via console:
# Visit: https://console.cloud.google.com/cloud-build/triggers?project=xynergy-dev-1757909467
# Follow instructions in: docs/CLOUD_BUILD_TRIGGERS_SETUP.md
```

**Note:** GitHub repository must be connected to Cloud Build first (one-time OAuth authorization through GCP Console).

**For detailed CI/CD setup instructions, see:**
`xynergyos-intelligence-gateway/docs/CLOUD_BUILD_TRIGGERS_SETUP.md`

---

## Next Steps

### 1. First Production Deployment

```bash
# Deploy prod service for the first time
cd xynergyos-intelligence-gateway
./scripts/deploy-prod.sh

# Or create a version tag
git tag -a v1.0.0 -m "Release v1.0.0: Initial production release"
git push origin v1.0.0
```

### 2. Update Production OAuth Secrets

```bash
# Get your real Slack OAuth credentials from https://api.slack.com/apps
# Update the secret
echo -n "YOUR-REAL-SLACK-CLIENT-SECRET" | gcloud secrets versions add slack-secret-prod --data-file=-

# Get your real Gmail OAuth credentials from https://console.cloud.google.com/apis/credentials
# Update the secret
echo -n "YOUR-REAL-GMAIL-CLIENT-SECRET" | gcloud secrets versions add gmail-secret-prod --data-file=-
```

### 3. Configure Production Domain

```bash
# Map custom domain to prod service
gcloud run services update xynergyos-intelligence-gateway-prod \
  --add-custom-domain app.xynergyos.com \
  --region=us-central1
```

### 4. Setup Monitoring Alerts

```bash
# Alert on production errors
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Prod Gateway Errors" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s
```

### 5. Deploy Other Services

Repeat the process for other services:
- slack-intelligence-service
- gmail-intelligence-service
- crm-engine

---

## Troubleshooting

### Problem: Service won't start

**Check logs:**
```bash
gcloud logging read "resource.labels.service_name=xynergyos-intelligence-gateway AND severity>=ERROR" --limit=10
```

### Problem: Environment variable not set

**Check service config:**
```bash
gcloud run services describe xynergyos-intelligence-gateway --region=us-central1 --format=yaml | grep -A 20 "env:"
```

### Problem: Secret not accessible

**Grant service account access:**
```bash
gcloud secrets add-iam-policy-binding jwt-secret-prod \
  --member=serviceAccount:835612502919-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Problem: Can't distinguish dev from prod

**Check startup logs:**
```bash
gcloud logging read "resource.labels.service_name=xynergyos-intelligence-gateway AND textPayload:\"Environment:\"" --limit=1
```

---

## Success Criteria

✅ **All Complete:**
1. ✅ Environment detection in config.ts
2. ✅ Mock mode toggle working
3. ✅ Firestore collection prefixes (dev_/prod_)
4. ✅ Redis key prefixes (dev:/prod:)
5. ✅ Environment files created
6. ✅ Deployment scripts created
7. ✅ Cloud Build configurations created
8. ✅ Secret Manager setup (dev & prod)
9. ✅ Cache service updated with prefixes
10. ✅ CORS separated by environment
11. ✅ Rate limits differentiated
12. ✅ Complete documentation

**Status:** ✅ READY FOR USE

---

## Summary

You now have a complete dev/production separation setup that allows:

✅ **Safe Development** - Test with mock data, can't affect production
✅ **Clean Separation** - Different services, collections, cache keys
✅ **Easy Deployment** - Simple scripts for both environments
✅ **Gradual Rollouts** - Deploy prod without traffic, then migrate gradually
✅ **Secret Management** - Different secrets for dev and prod
✅ **Cost Tracking** - Separate services = separate cost attribution
✅ **CI/CD Ready** - Cloud Build triggers for auto-deployment

**Next:** Deploy your first production service and start using real OAuth credentials!
