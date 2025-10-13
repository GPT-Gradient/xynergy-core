# Intelligence Gateway - Dev/Prod Setup Summary

**Status:** ✅ Complete and Ready to Use
**Date:** October 13, 2025

---

## Quick Links

- **Main Documentation:** `/DEV_PROD_SETUP_COMPLETE.md`
- **CI/CD Setup:** `docs/CLOUD_BUILD_TRIGGERS_SETUP.md`
- **CI/CD Status:** `docs/CI_CD_SETUP_COMPLETE.md`

---

## What's Been Set Up

### ✅ Environment Separation

**Three Environments:**
1. **Local** - Development on your machine (mock mode)
2. **Dev** - Cloud Run service for testing (mock mode)
3. **Prod** - Cloud Run service for real users (real OAuth)

**Data Isolation:**
- Firestore: `dev_*` and `prod_*` collections
- Redis: `dev:*` and `prod:*` key prefixes
- Secrets: Separate jwt/oauth secrets per environment

### ✅ Configuration Files

```
xynergyos-intelligence-gateway/
├── .env.local              # Local dev config (git-ignored)
├── .env.dev.example        # Dev environment template
├── .env.prod.example       # Prod environment template
├── cloudbuild-dev.yaml     # Auto-deploy on main push
├── cloudbuild-prod.yaml    # Deploy on version tags
└── src/config/config.ts    # Environment detection logic
```

### ✅ Deployment Scripts

```
scripts/
├── deploy-dev.sh                    # Manual dev deployment
├── deploy-prod.sh                   # Manual prod deployment (with safety checks)
└── setup-cloud-build-triggers.sh   # Create CI/CD triggers
```

### ✅ Documentation

```
docs/
├── CLOUD_BUILD_TRIGGERS_SETUP.md   # Complete CI/CD guide
└── CI_CD_SETUP_COMPLETE.md         # Setup completion status
```

### ✅ GCP Infrastructure

**Secrets Created:**
- `jwt-secret-dev` - Dev JWT secret
- `jwt-secret-prod` - Prod JWT secret
- `slack-secret-dev` - Dev Slack OAuth (placeholder)
- `slack-secret-prod` - Prod Slack OAuth (placeholder)
- `gmail-secret-dev` - Dev Gmail OAuth (placeholder)
- `gmail-secret-prod` - Prod Gmail OAuth (placeholder)

**Service Account Permissions:**
- Cloud Run Admin
- Service Account User
- Secret Manager Secret Accessor
- Artifact Registry Writer

---

## How to Use

### Local Development

```bash
# 1. Copy example environment file
cp .env.local.example .env.local

# 2. Start development server
npm run dev

# 3. Test locally
curl http://localhost:8080/health
```

### Deploy to Dev

**Option 1: Manual Deployment**
```bash
./scripts/deploy-dev.sh
```

**Option 2: Automatic (after triggers setup)**
```bash
git add .
git commit -m "feat: new feature"
git push origin main
# Auto-deploys to dev!
```

### Deploy to Prod

**Option 1: Manual Deployment**
```bash
./scripts/deploy-prod.sh
```

**Option 2: Automatic (after triggers setup)**
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
# Auto-deploys to prod (no traffic)
```

---

## Service URLs

**Development:**
- URL: `https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app`
- Mock Mode: ✅ Enabled
- Environment: `dev`

**Production:**
- URL: `https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app`
- Mock Mode: ❌ Disabled
- Environment: `prod`

---

## Next Steps

### 1. Setup CI/CD (Optional but Recommended)

```bash
cd xynergyos-intelligence-gateway
./scripts/setup-cloud-build-triggers.sh
```

This requires one-time GitHub OAuth connection via GCP Console.

### 2. Deploy Production Service (First Time)

```bash
./scripts/deploy-prod.sh
```

Or create a version tag:
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 3. Update Production OAuth Secrets (When Ready)

```bash
# Slack OAuth
echo -n "YOUR-REAL-SLACK-CLIENT-SECRET" | \
  gcloud secrets versions add slack-secret-prod --data-file=-

# Gmail OAuth
echo -n "YOUR-REAL-GMAIL-CLIENT-SECRET" | \
  gcloud secrets versions add gmail-secret-prod --data-file=-
```

### 4. Apply to Other Services

The same pattern can be applied to:
- `slack-intelligence-service`
- `gmail-intelligence-service`
- `crm-engine`

---

## Environment Detection

The system automatically detects the environment from the `XYNERGY_ENV` variable:

```typescript
// Local development
XYNERGY_ENV=local → mockMode=true, dev_ collections, dev: cache

// Dev deployment
XYNERGY_ENV=dev → mockMode=true, dev_ collections, dev: cache

// Prod deployment
XYNERGY_ENV=prod → mockMode=false, prod_ collections, prod: cache
```

---

## Key Features

### ✅ Automatic Environment Detection
- Based on `XYNERGY_ENV` variable
- Mock mode auto-enabled in dev/local
- Different collection prefixes per environment

### ✅ Data Isolation
- Firestore collections are completely separate
- Redis cache keys are completely separate
- No risk of dev data leaking into prod

### ✅ Safe Production Deployments
- Deploys with `--no-traffic` flag
- Manual gradual rollout (10% → 50% → 100%)
- Easy rollback to previous revision

### ✅ CI/CD Ready
- Auto-deploy dev on push to main
- Auto-deploy prod on version tags
- Service account permissions already granted

### ✅ Cost Optimized
- Dev: Min 0 instances (scales to zero)
- Prod: Min 1 instance (always available)
- Cloud Build: Within free tier for typical usage

---

## Troubleshooting

### Service Not Starting

Check environment variables:
```bash
gcloud run services describe xynergyos-intelligence-gateway \
  --region=us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

### Wrong Environment Detected

Check logs for startup message:
```bash
gcloud logging read "resource.labels.service_name=xynergyos-intelligence-gateway AND textPayload:Environment" --limit=5
```

### Cache Not Working

Verify Redis connection:
```bash
# Get VPC connector status
gcloud compute networks vpc-access connectors describe redis-connector --region=us-central1

# Check service has VPC connector
gcloud run services describe xynergyos-intelligence-gateway \
  --region=us-central1 \
  --format="value(spec.template.metadata.annotations['run.googleapis.com/vpc-access-connector'])"
```

### Secrets Not Loading

Verify secrets exist and are accessible:
```bash
# List secrets
gcloud secrets list --filter="name:jwt-secret OR name:slack-secret OR name:gmail-secret"

# Test secret access
gcloud secrets versions access latest --secret=jwt-secret-dev
```

---

## Support

For detailed documentation, see:
- **Dev/Prod Strategy:** `/DEV_PROD_SETUP_COMPLETE.md`
- **CI/CD Setup:** `docs/CLOUD_BUILD_TRIGGERS_SETUP.md`
- **CI/CD Status:** `docs/CI_CD_SETUP_COMPLETE.md`

For issues or questions, refer to the troubleshooting sections in each document.

---

## Summary

**Everything is ready!** You can now:
1. Develop locally with mock data
2. Deploy to dev for testing
3. Deploy to prod for real users
4. (Optional) Setup CI/CD for automatic deployments

The setup provides complete environment separation while keeping everything in one GCP project for simplicity and cost efficiency.
