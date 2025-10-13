# XynergyOS Platform - Quick Reference

**Platform-Wide Deployment Orchestration**

---

## 📋 Quick Commands

### Deploy Entire Platform
```bash
# Dev
./scripts/deploy-platform.sh -e dev

# Prod (with confirmation)
./scripts/deploy-platform.sh -e prod
```

### Deploy Service Group
```bash
# Available groups: core_infrastructure, intelligence_gateway, ai_services,
#                   data_analytics, business_operations, user_services

./scripts/deploy-platform.sh -e dev -g intelligence_gateway
./scripts/deploy-platform.sh -e prod -g core_infrastructure
```

### Deploy Single Service
```bash
./scripts/deploy-platform.sh -e dev -s xynergyos-intelligence-gateway
./scripts/deploy-platform.sh -e prod -s xynergyos-intelligence-gateway
```

### Check Platform Health
```bash
# Basic health check
./scripts/platform-health.sh -e dev

# With endpoint tests
./scripts/platform-health.sh -e prod -c

# Verbose with details
./scripts/platform-health.sh -e prod -c -v
```

### Traffic Rollout (Production)
```bash
# Gradual rollout
./scripts/rollout-traffic.sh -e prod -s <service> -t 10   # 10%
./scripts/rollout-traffic.sh -e prod -s <service> -t 50   # 50%
./scripts/rollout-traffic.sh -e prod -s <service> -t 100  # 100%
```

### Rollback Service
```bash
# Interactive (shows menu)
./scripts/rollback-service.sh -e prod -s <service>

# Specific revision
./scripts/rollback-service.sh -e prod -s <service> -r <revision>
```

### Dry Run (Test)
```bash
# See what would be deployed without deploying
./scripts/deploy-platform.sh -e prod --dry-run
./scripts/deploy-platform.sh -e prod -g intelligence_gateway --dry-run
```

---

## 🏗️ Service Groups

| Group | Services | Priority |
|-------|----------|----------|
| **core_infrastructure** | system-runtime, security-governance, tenant-management, secrets-config, permission-service | 1 |
| **intelligence_gateway** | xynergyos-intelligence-gateway, slack-intelligence-service, gmail-intelligence-service, calendar-intelligence-service, crm-engine | 2 |
| **ai_services** | ai-routing-engine, internal-ai-service-v2, ai-assistant, xynergy-competency-engine | 3 |
| **data_analytics** | analytics-data-layer, analytics-aggregation-service, fact-checking-layer, audit-logging-service | 4 |
| **business_operations** | marketing-engine, content-hub, project-management, qa-engine, scheduler-automation-engine, aso-engine, research-coordinator | 5 |
| **user_services** | platform-dashboard, executive-dashboard, conversational-interface-service, oauth-management-service, beta-program-service, business-entity-service | 6 |

---

## 🌐 Environment URLs

### Development Services
All dev services: `https://<service-name>-vgjxy554mq-uc.a.run.app`

Key services:
- Gateway: `https://xynergyos-intelligence-gateway-vgjxy554mq-uc.a.run.app`
- Slack: `https://slack-intelligence-service-vgjxy554mq-uc.a.run.app`
- Gmail: `https://gmail-intelligence-service-vgjxy554mq-uc.a.run.app`
- CRM: `https://crm-engine-vgjxy554mq-uc.a.run.app`

### Production Services (when deployed)
All prod services: `https://<service-name>-prod-vgjxy554mq-uc.a.run.app`

Key services:
- Gateway: `https://xynergyos-intelligence-gateway-prod-vgjxy554mq-uc.a.run.app`
- Slack: `https://slack-intelligence-service-prod-vgjxy554mq-uc.a.run.app`
- Gmail: `https://gmail-intelligence-service-prod-vgjxy554mq-uc.a.run.app`
- CRM: `https://crm-engine-prod-vgjxy554mq-uc.a.run.app`

---

## 📊 Monitoring Commands

### View Service Logs
```bash
gcloud run services logs read <service-name> \
  --region=us-central1 \
  --project=xynergy-dev-1757909467 \
  --limit=50
```

### List All Services
```bash
# Dev services
gcloud run services list --region=us-central1 --filter="NOT metadata.name~-prod$"

# Prod services
gcloud run services list --region=us-central1 --filter="metadata.name~-prod$"
```

### Check Service Status
```bash
gcloud run services describe <service-name> \
  --region=us-central1 \
  --format="table(status.conditions.type,status.conditions.status)"
```

### View Traffic Allocation
```bash
gcloud run services describe <service-name> \
  --region=us-central1 \
  --format="table(status.traffic.revisionName,status.traffic.percent)"
```

### List Revisions
```bash
gcloud run revisions list \
  --service=<service-name> \
  --region=us-central1 \
  --format="table(metadata.name,metadata.creationTimestamp,status.conditions[0].status)"
```

---

## 🔧 Common Workflows

### Deploy New Feature to Dev
```bash
# 1. Make code changes
# 2. Test locally
cd <service-directory>
npm run dev  # or python main.py

# 3. Deploy to dev
cd /Users/sesloan/Dev/xynergy-core
./scripts/deploy-platform.sh -e dev -s <service-name>

# 4. Test in dev
curl https://<service-name>-vgjxy554mq-uc.a.run.app/health
```

### Production Deployment Workflow
```bash
# 1. Deploy with no traffic
./scripts/deploy-platform.sh -e prod -s <service>

# 2. Test new revision
SERVICE_URL=$(gcloud run services describe <service>-prod --region=us-central1 --format="value(status.url)")
curl ${SERVICE_URL}/health

# 3. Gradual rollout
./scripts/rollout-traffic.sh -e prod -s <service> -t 10
# Wait 15 minutes, monitor metrics

./scripts/rollout-traffic.sh -e prod -s <service> -t 50
# Wait 15 minutes, monitor metrics

./scripts/rollout-traffic.sh -e prod -s <service> -t 100
# Monitor for issues

# 4. If issues occur, rollback
./scripts/rollback-service.sh -e prod -s <service>
```

### Update Multiple Related Services
```bash
# Deploy service group
./scripts/deploy-platform.sh -e prod -g intelligence_gateway

# Then roll out traffic for each service individually
for service in xynergyos-intelligence-gateway slack-intelligence-service gmail-intelligence-service; do
  echo "Rolling out ${service}..."
  ./scripts/rollout-traffic.sh -e prod -s ${service} -t 10
  sleep 60
done
```

---

## 🚨 Emergency Procedures

### Quick Rollback All Services in a Group
```bash
# Rollback intelligence gateway services
for service in xynergyos-intelligence-gateway slack-intelligence-service gmail-intelligence-service crm-engine; do
  echo "Rolling back ${service}..."
  ./scripts/rollback-service.sh -e prod -s ${service} -r $(gcloud run revisions list --service=${service}-prod --region=us-central1 --format="value(metadata.name)" --sort-by="~metadata.creationTimestamp" | sed -n 2p)
done
```

### Platform-Wide Health Check
```bash
# Quick check
./scripts/platform-health.sh -e prod

# If unhealthy services found, check logs
gcloud run services logs read <unhealthy-service> --region=us-central1 --limit=100
```

### Stop All Dev Services (Cost Savings)
```bash
# Scale all dev services to zero
for service in $(gcloud run services list --region=us-central1 --filter="NOT metadata.name~-prod$" --format="value(metadata.name)"); do
  gcloud run services update $service --region=us-central1 --min-instances=0 --quiet
done
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `platform-services.yaml` | Service manifest with all configurations |
| `scripts/deploy-platform.sh` | Main deployment orchestration script |
| `scripts/rollout-traffic.sh` | Traffic management script |
| `scripts/rollback-service.sh` | Service rollback script |
| `scripts/platform-health.sh` | Platform health monitoring |
| `PLATFORM_DEPLOYMENT_GUIDE.md` | Comprehensive deployment guide |
| `DEV_PROD_SETUP_COMPLETE.md` | Dev/prod setup documentation |

---

## 🔐 Secret Management

### List Secrets
```bash
gcloud secrets list --filter="name:(jwt-secret OR slack-secret OR gmail-secret)"
```

### Update Secret
```bash
# Development secret
echo -n "new-secret-value" | gcloud secrets versions add <secret-name>-dev --data-file=-

# Production secret
echo -n "new-secret-value" | gcloud secrets versions add <secret-name>-prod --data-file=-
```

### View Secret Access
```bash
gcloud secrets describe <secret-name>-prod --format="table(name,replication.automatic)"
```

---

## 💰 Cost Estimates

### Development (40 services)
- Min instances: 0 (scale to zero)
- Estimated cost: **$50-100/month**
- Only pay for active usage

### Production (40 services)
- Min instances: 1+ (always available)
- Higher resource allocations
- Estimated cost: **$500-1000/month**

### Cost Optimization
```bash
# Check instance usage
for service in $(gcloud run services list --region=us-central1 --format="value(metadata.name)"); do
  echo "=== $service ==="
  gcloud run services describe $service --region=us-central1 --format="value(spec.template.spec.containers[0].resources)"
done
```

---

## 🔗 Quick Links

- **Cloud Run Console:** https://console.cloud.google.com/run?project=xynergy-dev-1757909467
- **Cloud Build:** https://console.cloud.google.com/cloud-build/builds?project=xynergy-dev-1757909467
- **Secret Manager:** https://console.cloud.google.com/security/secret-manager?project=xynergy-dev-1757909467
- **Firestore:** https://console.cloud.google.com/firestore?project=xynergy-dev-1757909467
- **Logs Explorer:** https://console.cloud.google.com/logs/query?project=xynergy-dev-1757909467

---

## ❓ Getting Help

### View Script Help
```bash
./scripts/deploy-platform.sh --help
./scripts/rollout-traffic.sh --help
./scripts/rollback-service.sh --help
./scripts/platform-health.sh --help
```

### Documentation
- Full guide: `PLATFORM_DEPLOYMENT_GUIDE.md`
- Dev/prod setup: `DEV_PROD_SETUP_COMPLETE.md`
- Gateway setup: `xynergyos-intelligence-gateway/SETUP_SUMMARY.md`

### Troubleshooting
1. Check service logs
2. Verify environment variables
3. Check secret access
4. Review recent deployments
5. Run platform health check

---

**Last Updated:** October 13, 2025
**Platform Version:** 1.0
**Total Services:** 40+
