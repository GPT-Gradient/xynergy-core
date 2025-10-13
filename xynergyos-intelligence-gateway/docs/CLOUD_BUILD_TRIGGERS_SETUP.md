# Cloud Build Triggers Setup Guide

This guide walks through setting up automated CI/CD deployments using Cloud Build triggers for the Intelligence Gateway.

## Overview

We have two Cloud Build configurations:
- **cloudbuild-dev.yaml** - Deploys to dev environment on push to `main` branch
- **cloudbuild-prod.yaml** - Deploys to prod environment on version tags (e.g., `v1.0.0`)

## Prerequisites

1. **GitHub Repository Connected to Cloud Build**
   - The GitHub app must be installed and connected to your GCP project
   - This requires one-time OAuth authorization through the GCP Console

2. **Required GCP APIs Enabled**
   ```bash
   gcloud services enable cloudbuild.googleapis.com \
     cloudrun.googleapis.com \
     artifactregistry.googleapis.com \
     --project=xynergy-dev-1757909467
   ```

3. **Service Account Permissions**
   The Cloud Build service account needs:
   - Cloud Run Admin
   - Service Account User
   - Secret Manager Secret Accessor

## Step 1: Connect GitHub Repository (One-Time Setup)

### Via GCP Console (Recommended)

1. Go to [Cloud Build Triggers Console](https://console.cloud.google.com/cloud-build/triggers?project=xynergy-dev-1757909467)

2. Click **"Connect Repository"** or **"Create Trigger"**

3. Select **"GitHub (Cloud Build GitHub App)"**

4. Click **"Authenticate"** and authorize the Cloud Build app

5. Select the repository: **GPT-Gradient/xynergy-core**

6. Click **"Connect"**

### Via gcloud CLI (Alternative)

After manual GitHub authorization in the console, you can manage triggers via CLI.

## Step 2: Create DEV Trigger (Auto-deploy on push to main)

### Via GCP Console

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers?project=xynergy-dev-1757909467)

2. Click **"Create Trigger"**

3. Configure the trigger:
   ```
   Name: gateway-dev-deploy
   Description: Auto-deploy Intelligence Gateway to DEV on push to main

   Event: Push to a branch
   Repository: GPT-Gradient/xynergy-core
   Branch: ^main$

   Build Configuration: Cloud Build configuration file (yaml or json)
   Cloud Build configuration file location: xynergyos-intelligence-gateway/cloudbuild-dev.yaml

   Advanced (Optional):
   - Included files filter: xynergyos-intelligence-gateway/**
   ```

4. Click **"Create"**

### Via gcloud CLI (After GitHub is connected)

```bash
gcloud builds triggers create github \
  --name="gateway-dev-deploy" \
  --description="Auto-deploy Intelligence Gateway to DEV on push to main" \
  --repo-name="xynergy-core" \
  --repo-owner="GPT-Gradient" \
  --branch-pattern="^main$" \
  --build-config="xynergyos-intelligence-gateway/cloudbuild-dev.yaml" \
  --included-files="xynergyos-intelligence-gateway/**" \
  --project=xynergy-dev-1757909467
```

## Step 3: Create PROD Trigger (Deploy on version tags)

### Via GCP Console

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers?project=xynergy-dev-1757909467)

2. Click **"Create Trigger"**

3. Configure the trigger:
   ```
   Name: gateway-prod-deploy
   Description: Deploy Intelligence Gateway to PROD on version tags

   Event: Push new tag
   Repository: GPT-Gradient/xynergy-core
   Tag: ^v[0-9]+\.[0-9]+\.[0-9]+$

   Build Configuration: Cloud Build configuration file (yaml or json)
   Cloud Build configuration file location: xynergyos-intelligence-gateway/cloudbuild-prod.yaml

   Advanced (Optional):
   - Included files filter: xynergyos-intelligence-gateway/**
   ```

4. Click **"Create"**

### Via gcloud CLI (After GitHub is connected)

```bash
gcloud builds triggers create github \
  --name="gateway-prod-deploy" \
  --description="Deploy Intelligence Gateway to PROD on version tags" \
  --repo-name="xynergy-core" \
  --repo-owner="GPT-Gradient" \
  --tag-pattern="^v[0-9]+\\.[0-9]+\\.[0-9]+$" \
  --build-config="xynergyos-intelligence-gateway/cloudbuild-prod.yaml" \
  --included-files="xynergyos-intelligence-gateway/**" \
  --project=xynergy-dev-1757909467
```

## Step 4: Grant Service Account Permissions

The Cloud Build service account needs permissions to deploy to Cloud Run and access secrets:

```bash
PROJECT_ID="xynergy-dev-1757909467"
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Grant Cloud Run Admin
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/run.admin"

# Grant Service Account User (to deploy as service)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/iam.serviceAccountUser"

# Grant Secret Manager Secret Accessor
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

# Grant Artifact Registry Writer (for pushing images)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/artifactregistry.writer"
```

## Step 5: Verify Triggers

### List Triggers
```bash
gcloud builds triggers list --project=xynergy-dev-1757909467
```

### Test DEV Trigger (Simulate)
```bash
gcloud builds triggers run gateway-dev-deploy \
  --branch=main \
  --project=xynergy-dev-1757909467
```

### Test PROD Trigger (Simulate)
```bash
gcloud builds triggers run gateway-prod-deploy \
  --tag=v1.0.0 \
  --project=xynergy-dev-1757909467
```

## Workflow After Setup

### Development Workflow (Auto-deploy to DEV)

1. Make changes to code
2. Commit and push to `main` branch:
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin main
   ```
3. **Cloud Build automatically triggers** and deploys to DEV
4. Monitor build: https://console.cloud.google.com/cloud-build/builds?project=xynergy-dev-1757909467
5. Service updates automatically: https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app

### Production Workflow (Tag-based deployment)

1. Ensure main branch is stable and tested in DEV
2. Create and push a version tag:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0 - Initial production release"
   git push origin v1.0.0
   ```
3. **Cloud Build automatically triggers** and deploys to PROD (no traffic)
4. Monitor build: https://console.cloud.google.com/cloud-build/builds?project=xynergy-dev-1757909467
5. Manually test the new revision (see output from build)
6. Gradually roll out traffic:
   ```bash
   # Get latest revision
   LATEST_REVISION=$(gcloud run services describe xynergyos-intelligence-gateway-prod \
     --region=us-central1 \
     --project=xynergy-dev-1757909467 \
     --format="value(status.latestCreatedRevisionName)")

   # Roll out 10%
   gcloud run services update-traffic xynergyos-intelligence-gateway-prod \
     --to-revisions=${LATEST_REVISION}=10 \
     --region=us-central1 \
     --project=xynergy-dev-1757909467

   # Monitor, then roll out 50%
   gcloud run services update-traffic xynergyos-intelligence-gateway-prod \
     --to-revisions=${LATEST_REVISION}=50 \
     --region=us-central1 \
     --project=xynergy-dev-1757909467

   # Finally, roll out 100%
   gcloud run services update-traffic xynergyos-intelligence-gateway-prod \
     --to-latest \
     --region=us-central1 \
     --project=xynergy-dev-1757909467
   ```

## Monitoring Builds

### View Build History
```bash
gcloud builds list --project=xynergy-dev-1757909467 --limit=10
```

### View Build Logs
```bash
# Get build ID from list above
gcloud builds log <BUILD_ID> --project=xynergy-dev-1757909467
```

### View in Console
https://console.cloud.google.com/cloud-build/builds?project=xynergy-dev-1757909467

## Troubleshooting

### Trigger Not Firing

1. **Check trigger configuration:**
   ```bash
   gcloud builds triggers describe gateway-dev-deploy --project=xynergy-dev-1757909467
   ```

2. **Verify branch/tag pattern matches:**
   - DEV trigger: Branch must be exactly `main`
   - PROD trigger: Tag must match `v1.0.0`, `v2.3.5`, etc.

3. **Check included files filter:**
   - Changes must be in `xynergyos-intelligence-gateway/` directory
   - If you change files outside this directory, trigger won't fire

4. **Manually trigger build:**
   ```bash
   gcloud builds triggers run gateway-dev-deploy --branch=main --project=xynergy-dev-1757909467
   ```

### Build Fails

1. **Check build logs:**
   ```bash
   gcloud builds log <BUILD_ID> --project=xynergy-dev-1757909467 --stream
   ```

2. **Common issues:**
   - Missing dependencies in package.json
   - TypeScript compilation errors (run `npm run build` locally)
   - Missing secrets in Secret Manager
   - Insufficient service account permissions

3. **Test locally:**
   ```bash
   cd xynergyos-intelligence-gateway
   npm ci
   npm run build
   docker build -t test-image .
   ```

### Deployment Fails

1. **Check Cloud Run service logs:**
   ```bash
   gcloud run services logs read xynergyos-intelligence-gateway \
     --project=xynergy-dev-1757909467 \
     --region=us-central1 \
     --limit=50
   ```

2. **Verify secrets exist:**
   ```bash
   gcloud secrets list --project=xynergy-dev-1757909467
   ```

3. **Check service account has permissions:**
   ```bash
   gcloud projects get-iam-policy xynergy-dev-1757909467 \
     --flatten="bindings[].members" \
     --filter="bindings.members:*cloudbuild*"
   ```

## Security Considerations

1. **Branch Protection:**
   - Enable branch protection for `main` in GitHub
   - Require PR reviews before merging
   - Only merge to main after testing

2. **Tag Protection:**
   - Only create version tags from main branch
   - Use semantic versioning (v1.0.0, v1.0.1, etc.)
   - Never force-push tags

3. **Secrets Management:**
   - Never commit secrets to repository
   - Use GCP Secret Manager for all sensitive values
   - Rotate secrets regularly

4. **Service Account Permissions:**
   - Use principle of least privilege
   - Regularly audit permissions
   - Enable audit logging for Cloud Build

## Disabling Auto-Deploy (If Needed)

If you need to temporarily disable auto-deploy:

```bash
# Disable DEV trigger
gcloud builds triggers update gateway-dev-deploy \
  --disabled \
  --project=xynergy-dev-1757909467

# Re-enable later
gcloud builds triggers update gateway-dev-deploy \
  --no-disabled \
  --project=xynergy-dev-1757909467
```

## Cost Considerations

- **Cloud Build:** First 120 build-minutes/day are free, then $0.003/build-minute
- **Build Time:** ~3-5 minutes per build for this service
- **Storage:** Container images stored in Artifact Registry (~$0.10/GB/month)
- **Estimated Cost:** ~$5-10/month with typical development activity

## Next Steps

1. **Connect GitHub repository** (one-time setup via console)
2. **Create triggers** (via console or CLI)
3. **Grant service account permissions** (run the permission commands)
4. **Test with a commit** to main branch
5. **Monitor the build** in Cloud Build console
6. **Verify deployment** at the service URL

## References

- [Cloud Build Triggers Documentation](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers)
- [Cloud Build GitHub App](https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github)
- [Cloud Run Continuous Deployment](https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build)
