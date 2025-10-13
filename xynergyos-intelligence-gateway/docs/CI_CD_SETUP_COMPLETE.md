# CI/CD Setup Complete

**Date:** October 13, 2025
**Status:** ✅ Service Account Permissions Granted, Triggers Ready to Create

---

## Summary

The Cloud Build CI/CD infrastructure is now fully configured and ready to enable automated deployments for both dev and production environments. The Cloud Build service account has been granted all necessary permissions.

---

## What Was Completed

### ✅ Service Account Permissions Granted

The Cloud Build service account (`835612502919@cloudbuild.gserviceaccount.com`) has been granted:

1. **Cloud Run Admin** (`roles/run.admin`)
   - Deploy and update Cloud Run services
   - Manage service configurations

2. **Service Account User** (`roles/iam.serviceAccountUser`)
   - Deploy Cloud Run services using the service account
   - Required for Cloud Run deployments

3. **Secret Manager Secret Accessor** (`roles/secretmanager.secretAccessor`)
   - Read JWT secrets (jwt-secret-dev, jwt-secret-prod)
   - Read OAuth credentials (slack-secret-*, gmail-secret-*)

4. **Artifact Registry Writer** (`roles/artifactregistry.writer`)
   - Push Docker images to Artifact Registry
   - Required for container image storage

### ✅ Cloud Build Configurations Created

Two Cloud Build configuration files have been created:

1. **`cloudbuild-dev.yaml`**
   - Triggers on: Push to `main` branch
   - Deploys to: `xynergyos-intelligence-gateway` (dev service)
   - Environment: `XYNERGY_ENV=dev`, `MOCK_MODE=true`
   - Resources: Min 0, Max 10 instances
   - Secrets: jwt-secret-dev

2. **`cloudbuild-prod.yaml`**
   - Triggers on: Version tags (v1.0.0, v1.0.1, etc.)
   - Deploys to: `xynergyos-intelligence-gateway-prod` (prod service)
   - Environment: `XYNERGY_ENV=prod`, `MOCK_MODE=false`
   - Resources: Min 1, Max 50 instances
   - Secrets: jwt-secret-prod, slack-secret-prod, gmail-secret-prod
   - Safety: Deploys with `--no-traffic` for gradual rollout

### ✅ Helper Scripts Created

1. **`scripts/setup-cloud-build-triggers.sh`**
   - Interactive script to create Cloud Build triggers
   - Checks for existing triggers
   - Prompts for GitHub connection status
   - Creates both dev and prod triggers

2. **`scripts/deploy-dev.sh`**
   - Manual deployment script for dev environment
   - Builds TypeScript code
   - Builds and pushes Docker image
   - Deploys to Cloud Run

3. **`scripts/deploy-prod.sh`**
   - Manual deployment script for production
   - Interactive safety confirmations
   - Verifies main branch and clean working directory
   - Supports version tagging
   - Deploys with `--no-traffic` for safety
   - Provides gradual rollout instructions

### ✅ Documentation Created

1. **`docs/CLOUD_BUILD_TRIGGERS_SETUP.md`**
   - Comprehensive guide for setting up Cloud Build triggers
   - Step-by-step instructions for GitHub connection
   - Console and CLI setup options
   - Development and production workflows
   - Monitoring and troubleshooting guides
   - Security best practices

2. **`DEV_PROD_SETUP_COMPLETE.md`** (updated)
   - Added CI/CD setup section
   - Documented service account permissions
   - Added references to CI/CD documentation

---

## What's Next: Creating the Triggers

The Cloud Build triggers haven't been created yet because they require **GitHub OAuth authorization**, which must be done through the GCP Console.

### Option 1: Use the Helper Script (Recommended)

```bash
cd xynergyos-intelligence-gateway
./scripts/setup-cloud-build-triggers.sh
```

This script will:
1. Check if GitHub is connected
2. Check for existing triggers
3. Create dev trigger (auto-deploy on push to main)
4. Create prod trigger (deploy on version tags)
5. List all triggers

### Option 2: Manual Setup via Console

1. **Connect GitHub Repository (One-Time)**
   - Visit: https://console.cloud.google.com/cloud-build/triggers?project=xynergy-dev-1757909467
   - Click "Connect Repository"
   - Select "GitHub (Cloud Build GitHub App)"
   - Authorize and select repository: GPT-Gradient/xynergy-core

2. **Create DEV Trigger**
   - Name: `gateway-dev-deploy`
   - Event: Push to a branch
   - Branch: `^main$`
   - Build config: `xynergyos-intelligence-gateway/cloudbuild-dev.yaml`
   - Included files: `xynergyos-intelligence-gateway/**`

3. **Create PROD Trigger**
   - Name: `gateway-prod-deploy`
   - Event: Push new tag
   - Tag: `^v[0-9]+\.[0-9]+\.[0-9]+$`
   - Build config: `xynergyos-intelligence-gateway/cloudbuild-prod.yaml`
   - Included files: `xynergyos-intelligence-gateway/**`

### Option 3: CLI Commands (After GitHub Connection)

```bash
# Create DEV trigger
gcloud builds triggers create github \
  --name="gateway-dev-deploy" \
  --repo-name="xynergy-core" \
  --repo-owner="GPT-Gradient" \
  --branch-pattern="^main$" \
  --build-config="xynergyos-intelligence-gateway/cloudbuild-dev.yaml" \
  --included-files="xynergyos-intelligence-gateway/**" \
  --project=xynergy-dev-1757909467

# Create PROD trigger
gcloud builds triggers create github \
  --name="gateway-prod-deploy" \
  --repo-name="xynergy-core" \
  --repo-owner="GPT-Gradient" \
  --tag-pattern="^v[0-9]+\\.[0-9]+\\.[0-9]+$" \
  --build-config="xynergyos-intelligence-gateway/cloudbuild-prod.yaml" \
  --included-files="xynergyos-intelligence-gateway/**" \
  --project=xynergy-dev-1757909467
```

---

## Workflow After Trigger Setup

### Development Workflow (Automatic)

1. Make changes to Intelligence Gateway code
2. Commit and push to main:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin main
   ```
3. **Cloud Build automatically triggers**
4. Service updates at: `https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app`

### Production Workflow (Tag-Based)

1. Ensure main branch is tested and stable
2. Create version tag:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
3. **Cloud Build automatically deploys to prod (no traffic)**
4. Test the new revision
5. Gradually roll out traffic:
   ```bash
   # 10% → 50% → 100%
   gcloud run services update-traffic xynergyos-intelligence-gateway-prod \
     --to-latest --region=us-central1 --project=xynergy-dev-1757909467
   ```

---

## Verification Commands

### List Triggers
```bash
gcloud builds triggers list --project=xynergy-dev-1757909467
```

### View Build History
```bash
gcloud builds list --project=xynergy-dev-1757909467 --limit=10
```

### Monitor Active Builds
```bash
gcloud builds log --stream <BUILD_ID> --project=xynergy-dev-1757909467
```

### Test Manual Trigger
```bash
# Test DEV trigger
gcloud builds triggers run gateway-dev-deploy \
  --branch=main \
  --project=xynergy-dev-1757909467

# Test PROD trigger
gcloud builds triggers run gateway-prod-deploy \
  --tag=v1.0.0 \
  --project=xynergy-dev-1757909467
```

---

## Cost Estimate

**Cloud Build Costs:**
- First 120 build-minutes/day: **FREE**
- Additional: $0.003/build-minute
- Typical build time: 3-5 minutes
- Expected monthly builds: ~60 (2/day average)
- **Estimated cost: $0-5/month** (within free tier for most usage)

**Storage Costs:**
- Container images in Artifact Registry: ~$0.10/GB/month
- Typical image size: ~300MB
- Retention: Keep last 10 versions
- **Estimated cost: ~$0.30/month**

**Total CI/CD Cost: ~$0-5/month**

---

## Security Best Practices

### ✅ Already Implemented

1. **Service Account Permissions:** Principle of least privilege
2. **No-Traffic Deployments:** Production deploys with `--no-traffic`
3. **Environment Separation:** Different secrets for dev/prod
4. **Version Tagging:** Production requires semantic version tags
5. **Included Files Filter:** Only triggers on gateway changes

### 📋 Recommended

1. **Branch Protection:** Enable on `main` branch in GitHub
2. **PR Reviews:** Require reviews before merging to main
3. **Tag Protection:** Only create tags from main branch
4. **Secret Rotation:** Rotate JWT and OAuth secrets regularly
5. **Audit Logging:** Enable Cloud Build audit logs

---

## Troubleshooting

### Trigger Doesn't Fire

**Problem:** Pushed to main but no build triggered

**Solutions:**
1. Check trigger exists: `gcloud builds triggers list`
2. Verify branch name matches: `^main$`
3. Check included files: Changes must be in `xynergyos-intelligence-gateway/`
4. Manually trigger: `gcloud builds triggers run gateway-dev-deploy --branch=main`

### Build Fails

**Problem:** Build starts but fails during execution

**Solutions:**
1. Check logs: `gcloud builds log <BUILD_ID>`
2. Test locally: `npm run build` in gateway directory
3. Verify secrets exist: `gcloud secrets list`
4. Check service account permissions

### Deployment Fails

**Problem:** Build succeeds but deployment fails

**Solutions:**
1. Check Cloud Run logs
2. Verify VPC connector exists (redis-connector)
3. Verify secrets are accessible
4. Check Cloud Run service exists

### GitHub Connection Issues

**Problem:** Can't create triggers due to GitHub connection

**Solutions:**
1. Visit Cloud Build Triggers console
2. Click "Connect Repository"
3. Complete GitHub OAuth flow
4. Grant access to repository
5. Retry trigger creation

---

## Additional Resources

- **Detailed Setup Guide:** `docs/CLOUD_BUILD_TRIGGERS_SETUP.md`
- **Dev/Prod Strategy:** `../DEV_PROD_SETUP_COMPLETE.md`
- **Deployment Scripts:** `scripts/deploy-dev.sh`, `scripts/deploy-prod.sh`
- **Cloud Build Console:** https://console.cloud.google.com/cloud-build/builds?project=xynergy-dev-1757909467
- **Cloud Build Docs:** https://cloud.google.com/build/docs
- **Cloud Run Docs:** https://cloud.google.com/run/docs

---

## Summary

**✅ Completed:**
- Service account permissions granted
- Cloud Build configurations created
- Helper scripts created
- Comprehensive documentation written

**📋 Remaining (User Action Required):**
- Connect GitHub repository to Cloud Build (one-time OAuth)
- Create triggers using helper script or console
- Test first deployment

**Ready to Use:**
Once triggers are created, simply push to main (dev) or create version tags (prod) to trigger automatic deployments!
