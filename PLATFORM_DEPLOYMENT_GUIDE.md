# XynergyOS Platform-Wide Deployment Guide

**Date:** October 13, 2025
**Status:** ✅ Complete and Ready to Use

---

## Executive Summary

The XynergyOS platform now has complete orchestrated deployment capabilities across **40+ services** with dev/prod environment separation. This guide covers deploying individual services, service groups, or the entire platform.

**Key Capabilities:**
- Deploy entire platform or specific service groups
- Automated environment detection (dev/prod)
- Gradual traffic rollout for production
- Quick rollback capabilities
- Platform-wide health monitoring
- CI/CD integration ready

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Service Manifest](#service-manifest)
3. [Deployment Scripts](#deployment-scripts)
4. [Usage Examples](#usage-examples)
5. [Traffic Management](#traffic-management)
6. [Monitoring & Health](#monitoring--health)
7. [Rollback Procedures](#rollback-procedures)
8. [CI/CD Integration](#cicd-integration)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Environment Strategy

**Same-Project, Different-Service Approach:**
```
xynergy-dev-1757909467 (Single GCP Project)
│
├── Dev Services (40+ services)
│   ├── Mock mode enabled
│   ├── Min 0 instances (scale to zero)
│   ├── dev_ Firestore collections
│   └── dev: Redis key prefix
│
└── Prod Services (40+ services with -prod suffix)
    ├── Mock mode disabled
    ├── Min 1+ instances (always available)
    ├── prod_ Firestore collections
    └── prod: Redis key prefix
```

### Service Groups

Services are organized into 6 priority groups for coordinated deployment:

**Priority 1: Core Infrastructure**
- system-runtime
- security-governance
- tenant-management
- secrets-config
- permission-service

**Priority 2: Intelligence Gateway**
- xynergyos-intelligence-gateway
- slack-intelligence-service
- gmail-intelligence-service
- calendar-intelligence-service
- crm-engine

**Priority 3: AI Services**
- ai-routing-engine
- internal-ai-service-v2
- ai-assistant
- xynergy-competency-engine

**Priority 4: Data & Analytics**
- analytics-data-layer
- analytics-aggregation-service
- fact-checking-layer
- audit-logging-service

**Priority 5: Business Operations**
- marketing-engine
- content-hub
- project-management
- qa-engine
- scheduler-automation-engine
- aso-engine
- research-coordinator

**Priority 6: User Services**
- platform-dashboard
- executive-dashboard
- conversational-interface-service
- oauth-management-service
- beta-program-service
- business-entity-service

---

## Service Manifest

All platform services are defined in **`platform-services.yaml`** with:
- Service type (Python/TypeScript)
- Path to service directory
- Dev/prod configurations
- Resource allocations
- Environment variables
- Secret mappings

**Example Service Definition:**
```yaml
services:
  xynergyos-intelligence-gateway:
    type: typescript
    path: ./xynergyos-intelligence-gateway
    description: "Central API gateway"
    dev:
      name: xynergyos-intelligence-gateway
      memory: 512Mi
      cpu: 1
      min_instances: 0
      max_instances: 10
      env_vars:
        XYNERGY_ENV: dev
        MOCK_MODE: "true"
      secrets:
        JWT_SECRET: jwt-secret-dev:latest
    prod:
      name: xynergyos-intelligence-gateway-prod
      memory: 512Mi
      cpu: 1
      min_instances: 1
      max_instances: 50
      env_vars:
        XYNERGY_ENV: prod
        MOCK_MODE: "false"
      secrets:
        JWT_SECRET: jwt-secret-prod:latest
```

---

## Deployment Scripts

### Main Deployment Script: `scripts/deploy-platform.sh`

**Purpose:** Orchestrate deployment of services to dev or prod

**Features:**
- Deploy all services or specific groups
- Deploy individual services
- Dry-run mode for testing
- Parallel deployment (experimental)
- Production safety checks
- Progress tracking

**Usage:**
```bash
./scripts/deploy-platform.sh -e <environment> [options]
```

### Traffic Rollout Script: `scripts/rollout-traffic.sh`

**Purpose:** Gradually roll out traffic to new revisions

**Usage:**
```bash
./scripts/rollout-traffic.sh -e <env> -s <service> -t <percentage>
```

### Rollback Script: `scripts/rollback-service.sh`

**Purpose:** Quickly rollback to previous revision

**Usage:**
```bash
./scripts/rollback-service.sh -e <env> -s <service>
```

### Health Check Script: `scripts/platform-health.sh`

**Purpose:** Monitor platform health across all services

**Usage:**
```bash
./scripts/platform-health.sh -e <env> [--check-endpoints] [--verbose]
```

---

## Usage Examples

### Example 1: Deploy All Services to Dev

```bash
# Deploy entire platform to dev
./scripts/deploy-platform.sh -e dev

# Services deploy in priority order:
# 1. Core Infrastructure
# 2. Intelligence Gateway
# 3. AI Services
# 4. Data & Analytics
# 5. Business Operations
# 6. User Services
```

**Expected Output:**
```
======================================
XynergyOS Platform Deployment
======================================

Environment: DEV
Services to deploy: 40

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Deploying: system-runtime
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏗️  Building Docker image...
🚀 Deploying to Cloud Run...
✅ Successfully deployed system-runtime

[... continues for all services ...]

Deployment Summary
Total Services: 40
Successful: 40
Failed: 0
Duration: 1200s
```

### Example 2: Deploy Service Group to Production

```bash
# Deploy Intelligence Gateway services to prod
./scripts/deploy-platform.sh -e prod -g intelligence_gateway

# Confirms deployment:
# Are you absolutely sure? (type 'yes' to continue): yes

# Deploys:
# - xynergyos-intelligence-gateway-prod
# - slack-intelligence-service-prod
# - gmail-intelligence-service-prod
# - calendar-intelligence-service-prod
# - crm-engine-prod
```

**Production Deployment Notes:**
- All services deploy with `--no-traffic`
- Requires manual traffic rollout
- Safer deployment process

### Example 3: Deploy Single Service

```bash
# Deploy specific service to dev
./scripts/deploy-platform.sh -e dev -s xynergyos-intelligence-gateway

# Or to prod
./scripts/deploy-platform.sh -e prod -s xynergyos-intelligence-gateway
```

### Example 4: Dry Run (Test Without Deploying)

```bash
# See what would be deployed
./scripts/deploy-platform.sh -e prod --dry-run

# Shows all services that would be deployed without actually deploying
```

### Example 5: Gradual Production Rollout

```bash
# Step 1: Deploy to prod (no traffic)
./scripts/deploy-platform.sh -e prod -s xynergyos-intelligence-gateway

# Step 2: Test the new revision
curl https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app/health

# Step 3: Roll out 10% traffic
./scripts/rollout-traffic.sh -e prod -s xynergyos-intelligence-gateway -t 10

# Step 4: Monitor metrics, then roll out more
./scripts/rollout-traffic.sh -e prod -s xynergyos-intelligence-gateway -t 50

# Step 5: Full cutover
./scripts/rollout-traffic.sh -e prod -s xynergyos-intelligence-gateway -t 100
```

### Example 6: Rollback Production Service

```bash
# Interactive rollback (shows menu of revisions)
./scripts/rollback-service.sh -e prod -s xynergyos-intelligence-gateway

# Or rollback to specific revision
./scripts/rollback-service.sh -e prod -s xynergyos-intelligence-gateway -r <revision-name>
```

### Example 7: Platform Health Check

```bash
# Check dev platform health
./scripts/platform-health.sh -e dev

# Check prod with endpoint tests
./scripts/platform-health.sh -e prod --check-endpoints

# Verbose output with revision info
./scripts/platform-health.sh -e prod --verbose --check-endpoints
```

**Example Output:**
```
╔════════════════════════════════════════╗
║   XynergyOS Platform Health Check     ║
╚════════════════════════════════════════╝

Environment: PROD
Found 40 services

━━━ Core Infrastructure ━━━
✅ xynergy-system-runtime-prod              Ready
✅ xynergy-security-governance-prod         Ready
✅ xynergy-tenant-management-prod           Ready

━━━ Intelligence Gateway ━━━
✅ xynergyos-intelligence-gateway-prod      Ready • /health OK
✅ slack-intelligence-service-prod          Ready • /health OK

[... continues ...]

╔════════════════════════════════════════╗
║         Health Check Summary           ║
╚════════════════════════════════════════╝

Total Services:     40
Healthy:            38
Unhealthy:           2
Unknown:             0

Platform Health: 95% ✅
```

---

## Traffic Management

### Gradual Rollout Strategy

**Recommended Production Rollout:**

1. **Deploy with no traffic** (automatic with prod deployments)
2. **Test new revision** using direct URL
3. **10% rollout** - Monitor for 15-30 minutes
4. **50% rollout** - Monitor for 15-30 minutes
5. **100% rollout** - Full cutover

**Commands:**
```bash
# 10% traffic
./scripts/rollout-traffic.sh -e prod -s <service> -t 10

# Monitor logs
gcloud run services logs read <service>-prod --region=us-central1 --limit=100

# Check metrics in Cloud Console
# https://console.cloud.google.com/run?project=xynergy-dev-1757909467

# 50% traffic
./scripts/rollout-traffic.sh -e prod -s <service> -t 50

# Monitor again...

# 100% traffic
./scripts/rollout-traffic.sh -e prod -s <service> -t 100
```

### Traffic Splitting

You can maintain multiple revisions with traffic splits:

```bash
# 80% to new revision, 20% to old (canary)
gcloud run services update-traffic <service>-prod \
  --to-revisions=new-revision=80,old-revision=20 \
  --region=us-central1
```

---

## Monitoring & Health

### Platform Health Checks

```bash
# Quick health check
./scripts/platform-health.sh -e prod

# Detailed health with endpoint tests
./scripts/platform-health.sh -e prod -c -v
```

### Service Logs

```bash
# View logs for specific service
gcloud run services logs read <service-name> \
  --region=us-central1 \
  --project=xynergy-dev-1757909467 \
  --limit=50

# Stream live logs
gcloud run services logs read <service-name> \
  --region=us-central1 \
  --log-filter="severity>=WARNING" \
  --limit=100
```

### Metrics Dashboard

Access Cloud Run metrics:
```
https://console.cloud.google.com/run?project=xynergy-dev-1757909467
```

Key metrics to monitor:
- Request count
- Request latency
- Error rate
- Instance count
- Memory/CPU usage

---

## Rollback Procedures

### Quick Rollback

```bash
# Interactive rollback (shows menu)
./scripts/rollback-service.sh -e prod -s <service>

# Select previous revision from menu
# Confirms rollback
# Routes 100% traffic to selected revision
```

### Manual Rollback

```bash
# List revisions
gcloud run revisions list \
  --service=<service>-prod \
  --region=us-central1 \
  --format="table(metadata.name,status.conditions[0].lastTransitionTime)"

# Rollback to specific revision
gcloud run services update-traffic <service>-prod \
  --to-revisions=<previous-revision>=100 \
  --region=us-central1
```

### Platform-Wide Rollback

If multiple services need rollback:

```bash
# Rollback entire service group
for service in xynergyos-intelligence-gateway slack-intelligence-service gmail-intelligence-service; do
  ./scripts/rollback-service.sh -e prod -s $service
done
```

---

## CI/CD Integration

### Cloud Build Platform Deployment

**File:** `cloudbuild-platform-dev.yaml`

Builds and deploys Intelligence Gateway services on push to main:
- xynergyos-intelligence-gateway
- slack-intelligence-service
- gmail-intelligence-service
- crm-engine

**Setup Trigger:**
```bash
gcloud builds triggers create github \
  --name="platform-dev-deploy" \
  --repo-name="xynergy-core" \
  --repo-owner="GPT-Gradient" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild-platform-dev.yaml" \
  --project=xynergy-dev-1757909467
```

### Individual Service Triggers

Each service can have its own trigger:
- Trigger only when service directory changes
- Faster builds (only affected service)
- Independent deployments

**Example:**
```bash
gcloud builds triggers create github \
  --name="gateway-dev-deploy" \
  --repo-name="xynergy-core" \
  --repo-owner="GPT-Gradient" \
  --branch-pattern="^main$" \
  --build-config="xynergyos-intelligence-gateway/cloudbuild-dev.yaml" \
  --included-files="xynergyos-intelligence-gateway/**" \
  --project=xynergy-dev-1757909467
```

---

## Best Practices

### Development Workflow

1. **Develop locally** with mock data
   ```bash
   cd <service-directory>
   npm run dev  # or python main.py
   ```

2. **Test locally** before deploying

3. **Deploy to dev** for integration testing
   ```bash
   ./scripts/deploy-platform.sh -e dev -s <service>
   ```

4. **Verify in dev environment**

5. **Deploy to prod** when stable
   ```bash
   ./scripts/deploy-platform.sh -e prod -s <service>
   ```

6. **Gradually roll out** traffic

### Production Deployment Checklist

- [ ] Service tested in dev environment
- [ ] Code reviewed and merged to main
- [ ] Version tag created (optional but recommended)
- [ ] Deploy to prod with --no-traffic
- [ ] Test new revision using direct URL
- [ ] Check logs for errors
- [ ] Roll out 10% traffic
- [ ] Monitor metrics for 15+ minutes
- [ ] Roll out 50% traffic
- [ ] Monitor metrics for 15+ minutes
- [ ] Roll out 100% traffic
- [ ] Monitor for issues
- [ ] Document deployment in changelog

### Service Configuration

**Always Include:**
- Environment detection (XYNERGY_ENV)
- Mock mode support for dev
- Proper Firestore collection prefixes
- Proper Redis key prefixes
- Health check endpoints
- Structured logging
- Error handling

### Security Best Practices

- Use Secret Manager for all secrets
- Separate secrets per environment
- Never commit secrets to Git
- Use least-privilege IAM permissions
- Enable VPC connectors for private resources
- Implement proper authentication/authorization

---

## Troubleshooting

### Service Won't Deploy

**Problem:** Deployment fails with error

**Solutions:**
1. Check service directory exists
2. Verify Dockerfile is present
3. Test build locally:
   ```bash
   cd <service-directory>
   docker build -t test-image .
   ```
4. Check Cloud Build logs
5. Verify service account has permissions

### Traffic Rollout Fails

**Problem:** Can't update traffic allocation

**Solutions:**
1. Verify revision exists:
   ```bash
   gcloud run revisions list --service=<service>-prod --region=us-central1
   ```
2. Check service is deployed
3. Verify you're using correct service name (with -prod suffix for prod)

### Service Unhealthy

**Problem:** Health check reports service unhealthy

**Solutions:**
1. Check service logs:
   ```bash
   gcloud run services logs read <service> --region=us-central1 --limit=50
   ```
2. Verify environment variables are set correctly
3. Check secrets are accessible
4. Verify VPC connector (if needed)
5. Check Firestore/Redis connectivity

### Platform Health Check Shows Errors

**Problem:** Multiple services reporting unhealthy

**Solutions:**
1. Run verbose health check:
   ```bash
   ./scripts/platform-health.sh -e prod -v -c
   ```
2. Check for platform-wide issues (Firestore, Redis, etc.)
3. Check GCP service status
4. Review recent deployments
5. Consider rollback if after deployment

---

## Cost Optimization

### Development Environment

- Min instances: 0 (scale to zero)
- Services idle → no cost
- Only pay for active usage
- Estimated: $50-100/month with typical dev usage

### Production Environment

- Min instances: 1+ (always available)
- Higher resource allocations
- More instances for scaling
- Estimated: $500-1000/month for 40 services

### Cost Reduction Strategies

1. **Right-size resources** based on actual usage
2. **Adjust min instances** for less-used services
3. **Use Cloud Scheduler** to stop dev services overnight
4. **Monitor and optimize** heavy consumers
5. **Implement caching** to reduce compute

---

## Support & Resources

### Documentation

- **Main Setup Guide:** `/DEV_PROD_SETUP_COMPLETE.md`
- **Service Manifest:** `/platform-services.yaml`
- **Gateway Setup:** `/xynergyos-intelligence-gateway/SETUP_SUMMARY.md`
- **CI/CD Guide:** `/xynergyos-intelligence-gateway/docs/CLOUD_BUILD_TRIGGERS_SETUP.md`

### Scripts

- **Platform Deployment:** `/scripts/deploy-platform.sh`
- **Traffic Rollout:** `/scripts/rollout-traffic.sh`
- **Service Rollback:** `/scripts/rollback-service.sh`
- **Health Check:** `/scripts/platform-health.sh`

### GCP Console Links

- **Cloud Run Services:** https://console.cloud.google.com/run?project=xynergy-dev-1757909467
- **Cloud Build:** https://console.cloud.google.com/cloud-build/builds?project=xynergy-dev-1757909467
- **Secret Manager:** https://console.cloud.google.com/security/secret-manager?project=xynergy-dev-1757909467
- **Firestore:** https://console.cloud.google.com/firestore?project=xynergy-dev-1757909467

---

## Summary

The XynergyOS platform now has enterprise-grade deployment orchestration with:

✅ **40+ services** ready for coordinated deployment
✅ **Service grouping** for logical deployment order
✅ **Dev/prod separation** with data isolation
✅ **Gradual rollout** for safe production deployments
✅ **Quick rollback** capabilities
✅ **Platform health monitoring**
✅ **CI/CD integration** ready
✅ **Comprehensive documentation**

You can now deploy individual services, service groups, or the entire platform with confidence!
