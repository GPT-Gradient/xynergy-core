# Dev/Production Separation Strategy

**Date:** October 13, 2025
**Status:** Recommended Implementation Plan

---

## Executive Summary

This document outlines the strategy for separating development and production environments for the XynergyOS Intelligence Gateway and related services. The approach ensures clean separation, allows testing with mock data in dev, and provides a production-ready environment from ground zero.

---

## Current State Analysis

### What You Have Now
- **Single GCP Project:** `xynergy-dev-1757909467`
- **Single Gateway Deployment:** Serving all traffic
- **Mixed Data:** Some placeholder, some real Firestore data
- **No Environment Separation:** Dev and prod share resources

### Issues with Current Setup
1. Testing affects production data
2. Can't safely experiment with new features
3. No rollback strategy
4. Cost tracking is mixed
5. Can't have different configurations for dev/prod

---

## Recommended Architecture

### Option 1: Two GCP Projects (RECOMMENDED)

This is the cleanest and most industry-standard approach.

```
Development Environment:
├── GCP Project: xynergy-dev-1757909467
├── Services: *-dev (e.g., xynergyos-intelligence-gateway-dev)
├── Firestore: Development data
├── Redis: Development cache
├── Mock Mode: Enabled for external APIs
└── Cost: Separate billing

Production Environment:
├── GCP Project: xynergy-prod-XXXXXXX (new)
├── Services: *-prod (e.g., xynergyos-intelligence-gateway-prod)
├── Firestore: Production data (fresh start)
├── Redis: Production cache
├── Mock Mode: Disabled (real APIs)
└── Cost: Separate billing
```

**Pros:**
- ✅ Complete isolation (data, costs, resources)
- ✅ Different IAM permissions
- ✅ Can't accidentally affect production
- ✅ Clean cost tracking
- ✅ Industry standard

**Cons:**
- ❌ Need second GCP project (easy to create)
- ❌ Slightly higher management overhead
- ❌ Double the Cloud Run services (but can scale to zero)

---

### Option 2: Same Project, Different Service Names

Keep both environments in the same GCP project but with different service names and configurations.

```
xynergy-dev-1757909467:
├── Development Services:
│   ├── xynergyos-intelligence-gateway-dev
│   ├── slack-intelligence-service-dev
│   └── gmail-intelligence-service-dev
│
├── Production Services:
│   ├── xynergyos-intelligence-gateway
│   ├── slack-intelligence-service
│   └── gmail-intelligence-service
│
└── Firestore Collections:
    ├── users_dev / users
    ├── projects_dev / projects
    └── tasks_dev / tasks
```

**Pros:**
- ✅ Simpler to manage (one project)
- ✅ Shared infrastructure (Redis can be reused)
- ✅ No need to create new project

**Cons:**
- ❌ Mixed cost tracking
- ❌ Potential for accidentally using wrong environment
- ❌ Shared IAM permissions
- ❌ Risk of data leakage between environments

---

## Recommended Approach: Option 1 (Two Projects)

### Step-by-Step Implementation Plan

#### Phase 1: Create Production GCP Project

```bash
# 1. Create new GCP project
gcloud projects create xynergy-prod-$(date +%s) \
  --name="Xynergy Production" \
  --organization=YOUR_ORG_ID

# 2. Link billing account
gcloud billing projects link xynergy-prod-XXXXXXX \
  --billing-account=XXXXXX-XXXXXX-XXXXXX

# 3. Enable required APIs
gcloud services enable run.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  redis.googleapis.com \
  --project=xynergy-prod-XXXXXXX
```

#### Phase 2: Rename Existing Services (Dev)

Keep your current project as the **development** environment and rename services to indicate this:

```bash
# Current services stay in xynergy-dev-1757909467
# No changes needed - this becomes your dev environment
```

#### Phase 3: Environment-Specific Configuration

**Update config.ts to support environment variables:**

```typescript
// src/config/config.ts
export const appConfig: Config = {
  // Environment
  nodeEnv: process.env.NODE_ENV || 'development',
  environment: process.env.XYNERGY_ENV || 'dev', // NEW: 'dev' or 'prod'

  // Project
  gcpProjectId: process.env.GCP_PROJECT_ID ||
    (process.env.XYNERGY_ENV === 'prod'
      ? 'xynergy-prod-XXXXXXX'
      : 'xynergy-dev-1757909467'),

  // Mock mode (auto-disable in production)
  mockMode: process.env.MOCK_MODE === 'true' ||
    process.env.XYNERGY_ENV !== 'prod',

  // Firebase (different projects)
  firebase: {
    projectId: process.env.FIREBASE_PROJECT_ID ||
      (process.env.XYNERGY_ENV === 'prod'
        ? 'xynergy-prod-XXXXXXX'
        : 'xynergy-dev-1757909467'),
  },

  // Service URLs (environment-specific)
  services: {
    slackIntelligence: process.env.SLACK_INTELLIGENCE_URL ||
      (process.env.XYNERGY_ENV === 'prod'
        ? 'https://slack-intelligence-service-prod-hash.us-central1.run.app'
        : 'https://slack-intelligence-service-835612502919.us-central1.run.app'),
    // ... other services
  },

  // CORS (environment-specific)
  cors: {
    origins: process.env.XYNERGY_ENV === 'prod'
      ? [
          'https://app.xynergyos.com',
          'https://xynergyos.com',
          'https://*.xynergyos.com',
        ]
      : [
          'http://localhost:3000',
          'http://localhost:5173',
          'https://dev.xynergyos.com',
        ],
  },
};
```

#### Phase 4: Create Environment Files

**Create environment configuration files:**

```bash
# .env.dev (checked into repo - safe defaults)
NODE_ENV=development
XYNERGY_ENV=dev
GCP_PROJECT_ID=xynergy-dev-1757909467
MOCK_MODE=true
SLACK_CLIENT_ID=dev-client-id
SLACK_CLIENT_SECRET=dev-secret
# ... other dev configs

# .env.prod (NOT checked into repo - use Secret Manager)
NODE_ENV=production
XYNERGY_ENV=prod
GCP_PROJECT_ID=xynergy-prod-XXXXXXX
MOCK_MODE=false
SLACK_CLIENT_ID=prod-client-id
SLACK_CLIENT_SECRET=prod-secret
# ... other prod configs
```

#### Phase 5: Update Deployment Scripts

**Create deployment script for each environment:**

```bash
# scripts/deploy-dev.sh
#!/bin/bash
set -e

echo "Deploying to DEVELOPMENT environment..."

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
SERVICE_NAME="xynergyos-intelligence-gateway"

# Build
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-services/${SERVICE_NAME}:dev \
  --project ${PROJECT_ID}

# Deploy with dev environment variables
gcloud run deploy ${SERVICE_NAME} \
  --image us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-services/${SERVICE_NAME}:dev \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --set-env-vars="XYNERGY_ENV=dev,MOCK_MODE=true" \
  --set-secrets="JWT_SECRET=jwt-secret-dev:latest" \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --allow-unauthenticated

echo "✅ Deployed to DEV: https://${SERVICE_NAME}-${PROJECT_ID}.${REGION}.run.app"
```

```bash
# scripts/deploy-prod.sh
#!/bin/bash
set -e

echo "⚠️  Deploying to PRODUCTION environment..."
echo "This will affect production users!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Deployment cancelled"
  exit 1
fi

PROJECT_ID="xynergy-prod-XXXXXXX"
REGION="us-central1"
SERVICE_NAME="xynergyos-intelligence-gateway"

# Build (use :prod tag)
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-services/${SERVICE_NAME}:prod \
  --project ${PROJECT_ID}

# Deploy with prod environment variables
gcloud run deploy ${SERVICE_NAME} \
  --image us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-services/${SERVICE_NAME}:prod \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --set-env-vars="XYNERGY_ENV=prod,MOCK_MODE=false" \
  --set-secrets="JWT_SECRET=jwt-secret-prod:latest,SLACK_CLIENT_SECRET=slack-secret-prod:latest" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 50 \
  --allow-unauthenticated

echo "✅ Deployed to PROD: https://${SERVICE_NAME}-${PROJECT_ID}.${REGION}.run.app"
```

#### Phase 6: CI/CD Pipeline (Recommended)

**Use Cloud Build for automated deployments:**

```yaml
# cloudbuild-dev.yaml
steps:
  # Install dependencies
  - name: 'node:20'
    entrypoint: npm
    args: ['ci']

  # Run tests
  - name: 'node:20'
    entrypoint: npm
    args: ['test']

  # Build TypeScript
  - name: 'node:20'
    entrypoint: npm
    args: ['run', 'build']

  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/xynergy-services/xynergyos-intelligence-gateway:dev',
      '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/xynergy-services/xynergyos-intelligence-gateway:$SHORT_SHA',
      '.'
    ]

  # Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '--all-tags', 'us-central1-docker.pkg.dev/$PROJECT_ID/xynergy-services/xynergyos-intelligence-gateway']

  # Deploy to Cloud Run (dev)
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'xynergyos-intelligence-gateway'
      - '--image=us-central1-docker.pkg.dev/$PROJECT_ID/xynergy-services/xynergyos-intelligence-gateway:$SHORT_SHA'
      - '--region=us-central1'
      - '--set-env-vars=XYNERGY_ENV=dev,MOCK_MODE=true'

options:
  machineType: 'E2_HIGHCPU_8'
```

```yaml
# cloudbuild-prod.yaml
steps:
  # Install dependencies
  - name: 'node:20'
    entrypoint: npm
    args: ['ci']

  # Run tests
  - name: 'node:20'
    entrypoint: npm
    args: ['test']

  # Build TypeScript
  - name: 'node:20'
    entrypoint: npm
    args: ['run', 'build']

  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: [
      'build',
      '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/xynergy-services/xynergyos-intelligence-gateway:prod',
      '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/xynergy-services/xynergyos-intelligence-gateway:$TAG_NAME',
      '.'
    ]

  # Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '--all-tags', 'us-central1-docker.pkg.dev/$PROJECT_ID/xynergy-services/xynergyos-intelligence-gateway']

  # Deploy to Cloud Run (prod)
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'xynergyos-intelligence-gateway'
      - '--image=us-central1-docker.pkg.dev/$PROJECT_ID/xynergy-services/xynergyos-intelligence-gateway:$TAG_NAME'
      - '--region=us-central1'
      - '--set-env-vars=XYNERGY_ENV=prod,MOCK_MODE=false'
      - '--no-traffic'  # Deploy without traffic for gradual rollout

options:
  machineType: 'E2_HIGHCPU_8'
```

**Setup triggers:**

```bash
# Dev: Auto-deploy on push to main branch
gcloud builds triggers create github \
  --name="dev-deploy-gateway" \
  --repo-name="xynergy-core" \
  --repo-owner="your-org" \
  --branch-pattern="^main$" \
  --build-config="xynergyos-intelligence-gateway/cloudbuild-dev.yaml" \
  --project=xynergy-dev-1757909467

# Prod: Manual trigger or deploy on git tags (v1.0.0, v1.0.1, etc.)
gcloud builds triggers create github \
  --name="prod-deploy-gateway" \
  --repo-name="xynergy-core" \
  --repo-owner="your-org" \
  --tag-pattern="^v[0-9]+\.[0-9]+\.[0-9]+$" \
  --build-config="xynergyos-intelligence-gateway/cloudbuild-prod.yaml" \
  --project=xynergy-prod-XXXXXXX
```

---

## Development Workflow

### Daily Development Flow

```bash
# 1. Make changes locally
git checkout -b feature/new-feature
# ... make changes ...

# 2. Test locally
npm run dev
# Test with http://localhost:8080

# 3. Deploy to dev environment
git push origin feature/new-feature
git checkout main
git merge feature/new-feature
git push origin main
# Automatically deploys to dev via Cloud Build trigger

# 4. Test in dev environment
curl https://xynergyos-intelligence-gateway-dev.run.app/health

# 5. When ready for production, create a release tag
git tag -a v1.2.3 -m "Release v1.2.3: Add new feature"
git push origin v1.2.3
# Automatically deploys to prod via Cloud Build trigger
```

### Feature Testing Flow

```
Developer → Local Testing (localhost)
    ↓
Push to Branch → Auto-deploy to Dev
    ↓
QA Testing in Dev Environment
    ↓
Merge to Main → Confirm in Dev
    ↓
Create Git Tag → Auto-deploy to Prod
    ↓
Gradual Traffic Migration (0% → 25% → 50% → 100%)
    ↓
Production Live
```

---

## Mock vs Real Data Strategy

### Development Environment (Mock Mode)

```typescript
// In services, check environment
export class SlackService {
  constructor() {
    this.mockMode = appConfig.mockMode || !this.hasOAuthCredentials();
  }

  async listChannels(userId: string): Promise<Channel[]> {
    if (this.mockMode) {
      // Return mock data
      return [
        { id: 'C123', name: 'general', is_member: true },
        { id: 'C456', name: 'random', is_member: true },
      ];
    }

    // Real implementation
    const client = await this.getUserClient(userId);
    const result = await client.conversations.list();
    return result.channels || [];
  }
}
```

### Production Environment (Real Data)

```typescript
// Mock mode is disabled
// All API calls use real credentials
// Firestore has real user data
// OAuth tokens are real and encrypted
```

---

## Secret Management

### Use GCP Secret Manager (Recommended)

**Development Secrets:**
```bash
# Store dev secrets
echo -n "dev-jwt-secret-12345" | gcloud secrets create jwt-secret-dev \
  --data-file=- \
  --project=xynergy-dev-1757909467

echo -n "dev-slack-secret" | gcloud secrets create slack-secret-dev \
  --data-file=- \
  --project=xynergy-dev-1757909467
```

**Production Secrets:**
```bash
# Store prod secrets (different values!)
echo -n "prod-jwt-secret-67890-STRONG-SECURE" | gcloud secrets create jwt-secret-prod \
  --data-file=- \
  --project=xynergy-prod-XXXXXXX

echo -n "prod-slack-secret-REAL" | gcloud secrets create slack-secret-prod \
  --data-file=- \
  --project=xynergy-prod-XXXXXXX
```

**Reference secrets in Cloud Run:**
```bash
gcloud run services update xynergyos-intelligence-gateway \
  --set-secrets="JWT_SECRET=jwt-secret-prod:latest" \
  --set-secrets="SLACK_CLIENT_SECRET=slack-secret-prod:latest" \
  --project=xynergy-prod-XXXXXXX
```

---

## Database Separation

### Firestore Collections

**Development (xynergy-dev-1757909467):**
- Keep existing collections
- Use for testing and development
- Can reset data anytime
- No impact on production

**Production (xynergy-prod-XXXXXXX):**
- Fresh Firestore instance
- Start from ground zero
- Real user data only
- Proper backup strategy

### Redis Caching

**Option A: Separate Redis Instances**
```bash
# Dev Redis
gcloud redis instances create redis-dev \
  --size=1 \
  --region=us-central1 \
  --project=xynergy-dev-1757909467

# Prod Redis
gcloud redis instances create redis-prod \
  --size=2 \
  --region=us-central1 \
  --tier=standard-ha \
  --project=xynergy-prod-XXXXXXX
```

**Option B: Shared Redis with Key Prefixes**
```typescript
// Use different key prefixes
const cacheKey = `${appConfig.environment}:user:${userId}`;
// Dev: "dev:user:123"
// Prod: "prod:user:123"
```

---

## Cost Optimization

### Development Environment
- **Cloud Run:** Scale to zero when not in use
- **Min Instances:** 0 (no minimum)
- **Max Instances:** 5 (limit costs)
- **Redis:** Smaller instance (1GB)

### Production Environment
- **Cloud Run:** Keep warm with min instances
- **Min Instances:** 1-2 (fast response)
- **Max Instances:** 50 (handle traffic)
- **Redis:** Standard HA (2GB+)

### Estimated Costs

**Development:**
- Cloud Run: ~$50-100/month (mostly idle)
- Redis: ~$50/month (basic tier)
- Firestore: ~$20/month (low usage)
- **Total:** ~$120-170/month

**Production:**
- Cloud Run: ~$300-500/month (active)
- Redis: ~$200/month (HA tier)
- Firestore: ~$100/month (real usage)
- **Total:** ~$600-800/month

---

## Migration Plan

### Week 1: Setup Infrastructure
1. ✅ Create production GCP project
2. ✅ Enable required APIs
3. ✅ Create Artifact Registry
4. ✅ Setup Redis (optional)
5. ✅ Configure IAM permissions

### Week 2: Update Code
1. ✅ Add environment configuration
2. ✅ Update config.ts with environment logic
3. ✅ Add mock mode checks to services
4. ✅ Create deployment scripts
5. ✅ Test locally with different env vars

### Week 3: Deploy & Test
1. ✅ Deploy to dev environment (test current behavior)
2. ✅ Deploy to prod environment (fresh start)
3. ✅ Setup Cloud Build triggers
4. ✅ Test full workflow (dev → prod)
5. ✅ Document process

### Week 4: Production Go-Live
1. ✅ Configure production OAuth apps
2. ✅ Setup production domain (app.xynergyos.com)
3. ✅ Migrate any critical data (if needed)
4. ✅ Enable monitoring and alerting
5. ✅ Go live!

---

## Monitoring & Observability

### Development Environment
- **Logging:** Standard Cloud Logging
- **Metrics:** Basic Cloud Monitoring
- **Alerting:** None (optional)

### Production Environment
- **Logging:** Structured logging with error tracking
- **Metrics:** Comprehensive Cloud Monitoring
- **Alerting:** PagerDuty/Slack for critical errors
- **Uptime Checks:** Every 1 minute
- **Error Reporting:** Cloud Error Reporting

### Recommended Alerts (Production Only)

```bash
# Alert on high error rate
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s \
  --project=xynergy-prod-XXXXXXX

# Alert on service down
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Service Down" \
  --condition-threshold-value=1 \
  --condition-threshold-duration=60s \
  --project=xynergy-prod-XXXXXXX
```

---

## Rollback Strategy

### If Production Deployment Fails

```bash
# Option 1: Rollback to previous revision
gcloud run services update-traffic xynergyos-intelligence-gateway \
  --to-revisions=xynergyos-intelligence-gateway-00025-np8=100 \
  --project=xynergy-prod-XXXXXXX

# Option 2: Deploy specific tag
gcloud run deploy xynergyos-intelligence-gateway \
  --image=us-central1-docker.pkg.dev/xynergy-prod-XXXXXXX/xynergy-services/xynergyos-intelligence-gateway:v1.0.0 \
  --project=xynergy-prod-XXXXXXX
```

### Gradual Rollout Strategy

```bash
# Deploy new version without traffic
gcloud run deploy xynergyos-intelligence-gateway \
  --image=...new-image... \
  --no-traffic \
  --tag=canary \
  --project=xynergy-prod-XXXXXXX

# Test canary URL
curl https://canary---xynergyos-intelligence-gateway-xyz.run.app/health

# Gradually increase traffic
gcloud run services update-traffic xynergyos-intelligence-gateway \
  --to-revisions=canary=10 \
  --project=xynergy-prod-XXXXXXX

# If good, continue
gcloud run services update-traffic xynergyos-intelligence-gateway \
  --to-revisions=canary=50 \
  --project=xynergy-prod-XXXXXXX

# If good, full rollout
gcloud run services update-traffic xynergyos-intelligence-gateway \
  --to-latest \
  --project=xynergy-prod-XXXXXXX
```

---

## Recommended: Start with Option 1 (Two Projects)

### Why This Is Best

1. **Clean Separation:** No risk of dev affecting prod
2. **Independent Scaling:** Different configs for each
3. **Cost Visibility:** Know exactly what prod costs
4. **Security:** Different IAM, different secrets
5. **Industry Standard:** How most companies do it

### Quick Start Commands

```bash
# 1. Create prod project
gcloud projects create xynergy-prod-$(date +%s) --name="Xynergy Production"

# 2. Get project ID
PROD_PROJECT=$(gcloud projects list --filter="name:Xynergy\ Production" --format="value(projectId)")
echo "Production Project: $PROD_PROJECT"

# 3. Enable billing
gcloud billing projects link $PROD_PROJECT --billing-account=YOUR-BILLING-ACCOUNT

# 4. Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com firestore.googleapis.com --project=$PROD_PROJECT

# 5. Deploy first service to prod
cd xynergyos-intelligence-gateway
gcloud builds submit --tag us-central1-docker.pkg.dev/$PROD_PROJECT/xynergy-services/xynergyos-intelligence-gateway:v1.0.0 --project=$PROD_PROJECT
gcloud run deploy xynergyos-intelligence-gateway --image us-central1-docker.pkg.dev/$PROD_PROJECT/xynergy-services/xynergyos-intelligence-gateway:v1.0.0 --region us-central1 --set-env-vars="XYNERGY_ENV=prod,MOCK_MODE=false" --project=$PROD_PROJECT
```

---

## Summary

**Recommended Approach:** Two GCP Projects (Option 1)

**Key Benefits:**
- ✅ Complete isolation
- ✅ Safe testing in dev
- ✅ Clean production from ground zero
- ✅ Different configurations per environment
- ✅ Industry standard approach

**Next Steps:**
1. Create production GCP project
2. Update code with environment config
3. Create deployment scripts
4. Setup CI/CD with Cloud Build
5. Deploy to both environments
6. Test full workflow

**Timeline:** 2-3 weeks for complete setup

Would you like me to help you implement any specific part of this strategy?
