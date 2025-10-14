# Xynergy Platform - Pre-Production Implementation Roadmap

**Date:** October 13, 2025
**Phase:** Pre-Production Readiness
**Timeline:** 8 Weeks (October 14 - December 8, 2025)
**Status:** Planning → Implementation Ready

---

## Executive Summary

This roadmap implements the requirements defined in the Pre-Production Requirements Document, advancing the Xynergy platform from functional (100% healthy services) to enterprise-ready with unified observability, automated CI/CD, consolidated services, and enhanced developer experience.

**Current State:** 41/41 services healthy, production-ready dev environment
**Target State:** Enterprise-ready platform with observability, automation, and scalability

---

## Implementation Timeline

### Week 1-2: Observability Foundation (Oct 14-27)
**Priority:** P1
**Owner:** DevOps / GCP Admin

#### Week 1: Monitoring Workspace Setup
- [ ] Create GCP Monitoring Workspace: `xynergy-observability`
- [ ] Enable Cloud Logging API
- [ ] Enable Cloud Trace API
- [ ] Enable Cloud Profiler API
- [ ] Configure log retention policies (30 days dev, 90 days prod)
- [ ] Set up log sinks for BigQuery analytics

**Deliverables:**
- Monitoring workspace operational
- All APIs enabled
- Log retention configured

#### Week 2: Metrics & Exporters
- [ ] Deploy Prometheus exporters to FastAPI services (27 services)
- [ ] Deploy Prometheus exporters to Node.js services (9 services)
- [ ] Configure custom metrics:
  - API latency (p50, p95, p99)
  - Redis cache hit/miss ratio
  - Pub/Sub queue depth
  - Firestore operation latency
  - BigQuery query performance
- [ ] Set up error rate tracking per service
- [ ] Configure alert policies:
  - Latency > 500ms
  - Error rate > 3%
  - Service down (health check fails)

**Deliverables:**
- 41 services exporting metrics
- Custom metrics dashboard
- Alert policies active

**Technical Approach:**
```python
# FastAPI Prometheus Integration
from prometheus_client import Counter, Histogram, make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

# Add to each FastAPI app
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

### Week 2-3: CI/CD Automation (Oct 21 - Nov 3)
**Priority:** P1
**Owner:** DevOps

#### Cloud Build Templates
- [ ] Create base `cloudbuild-python.yaml` template
- [ ] Create base `cloudbuild-typescript.yaml` template
- [ ] Implement build stages:
  1. Lint (ESLint for TS, Black/Flake8 for Python)
  2. Test (pytest for Python, Jest for TypeScript)
  3. Docker build
  4. Push to Artifact Registry
  5. Deploy to Cloud Run
  6. Health check verification
  7. Slack notification

**Python Template Structure:**
```yaml
# cloudbuild-python.yaml
steps:
  # Stage 1: Lint
  - name: python:3.11-slim
    entrypoint: pip
    args: ['install', 'black', 'flake8']
  - name: python:3.11-slim
    entrypoint: black
    args: ['--check', '.']

  # Stage 2: Test
  - name: python:3.11-slim
    entrypoint: pip
    args: ['install', '-r', 'requirements.txt']
  - name: python:3.11-slim
    entrypoint: pytest
    args: ['tests/', '--cov', '--cov-report=term']

  # Stage 3: Build
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-platform/${_SERVICE_NAME}:${SHORT_SHA}', '.']

  # Stage 4: Push
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-platform/${_SERVICE_NAME}:${SHORT_SHA}']

  # Stage 5: Deploy
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}'
      - '--image=us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-platform/${_SERVICE_NAME}:${SHORT_SHA}'
      - '--region=us-central1'
      - '--set-env-vars=XYNERGY_ENV=${_ENVIRONMENT},MOCK_MODE=${_MOCK_MODE}'
      - '--service-account=xynergy-platform-sa@${PROJECT_ID}.iam.gserviceaccount.com'

  # Stage 6: Verify
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: bash
    args:
      - '-c'
      - |
        SERVICE_URL=$(gcloud run services describe ${_SERVICE_NAME} --region=us-central1 --format='value(status.url)')
        curl -f $SERVICE_URL/health || exit 1

  # Stage 7: Notify
  - name: 'gcr.io/cloud-builders/curl'
    entrypoint: bash
    args:
      - '-c'
      - |
        curl -X POST ${_SLACK_WEBHOOK} -H 'Content-Type: application/json' -d '{
          "text": "✅ Deployed ${_SERVICE_NAME} (${SHORT_SHA}) to ${_ENVIRONMENT}"
        }'

substitutions:
  _SERVICE_NAME: service-name
  _ENVIRONMENT: dev
  _MOCK_MODE: 'true'
  _SLACK_WEBHOOK: ${SLACK_WEBHOOK_URL}

options:
  logging: CLOUD_LOGGING_ONLY
```

#### GitHub Integration
- [ ] Connect GitHub repository to Cloud Build
- [ ] Create triggers for branches:
  - `main` → dev environment
  - `staging` → staging environment
  - `v*` tags → production environment
- [ ] Configure build triggers for all 41 services
- [ ] Set up Artifact Registry retention policies (keep last 10 images)
- [ ] Implement rollback triggers for failed deployments

**Deliverables:**
- CI/CD templates for Python and TypeScript
- 41 Cloud Build triggers configured
- GitHub integration active
- Slack notifications working

---

### Week 3-4: Authentication Unification (Oct 28 - Nov 10)
**Priority:** P1
**Owner:** Platform / Security

#### Design xynergy-auth Service
- [ ] Create new TypeScript service: `xynergy-auth`
- [ ] Implement unified token validation
- [ ] Consolidate Firebase + JWT logic
- [ ] Add RBAC (Role-Based Access Control)
- [ ] Create middleware packages for FastAPI and Express

**Service Architecture:**
```typescript
// xynergy-auth/src/index.ts
import express from 'express';
import { initializeApp } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import jwt from 'jsonwebtoken';

const app = express();
const db = getFirestore();

// Token validation endpoint
app.post('/api/v1/auth/validate', async (req, res) => {
  const { token, token_type } = req.body;

  try {
    if (token_type === 'firebase') {
      const decodedToken = await admin.auth().verifyIdToken(token);
      const user = await getUserWithRoles(decodedToken.uid);
      return res.json({ valid: true, user });
    }

    if (token_type === 'jwt') {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const user = await getUserWithRoles(decoded.user_id);
      return res.json({ valid: true, user });
    }

    return res.status(400).json({ valid: false, error: 'Unknown token type' });
  } catch (error) {
    return res.status(401).json({ valid: false, error: error.message });
  }
});

// RBAC check endpoint
app.post('/api/v1/auth/check-permission', async (req, res) => {
  const { user_id, tenant_id, permission } = req.body;

  const userDoc = await db.collection('tenants').doc(tenant_id)
    .collection('users').doc(user_id).get();

  const roles = userDoc.data()?.roles || [];
  const hasPermission = await checkRolePermissions(roles, permission);

  res.json({ allowed: hasPermission });
});
```

**Firestore Schema:**
```javascript
// tenants/{tenant_id}/users/{user_id}
{
  "email": "user@example.com",
  "roles": ["user", "editor"],
  "created_at": "2025-10-13T00:00:00Z"
}

// roles/{role_id}
{
  "name": "editor",
  "permissions": [
    "content:read",
    "content:write",
    "projects:read"
  ],
  "description": "Content editor role"
}
```

#### Create Middleware Packages
- [ ] Python middleware: `xynergy-auth-middleware` (PyPI package)
- [ ] TypeScript middleware: `@xynergy/auth-middleware` (npm package)
- [ ] Integrate into all 41 services

**Python Middleware:**
```python
# xynergy-auth-middleware/xynergy_auth/middleware.py
from fastapi import Request, HTTPException
import httpx

async def verify_token(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://xynergy-auth.run.app/api/v1/auth/validate",
            json={"token": token, "token_type": "jwt"}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

        return response.json()["user"]

# Usage in FastAPI services
from xynergy_auth.middleware import verify_token
from fastapi import Depends

@app.get("/api/v1/resource")
async def get_resource(user = Depends(verify_token)):
    # user is authenticated
    return {"message": f"Hello {user['email']}"}
```

**Deliverables:**
- xynergy-auth service deployed
- Python middleware package published
- TypeScript middleware package published
- 41 services integrated with unified auth

---

### Week 3: Secrets Migration (Oct 28 - Nov 3)
**Priority:** P1
**Owner:** Platform / DevOps

#### Secret Manager Migration
- [ ] Audit all `.env` files across 41 services
- [ ] Create secret naming convention: `XYN_[SERVICE]_[NAME]`
- [ ] Create secrets in GCP Secret Manager:

**Secret Inventory:**
```bash
# Authentication
XYN_AUTH_JWT_SECRET_DEV
XYN_AUTH_JWT_SECRET_PROD
XYN_AUTH_FIREBASE_KEY_DEV
XYN_AUTH_FIREBASE_KEY_PROD

# AI Services (per service)
XYN_AI_OPENAI_API_KEY
XYN_AI_GOOGLE_STUDIO_KEY
XYN_AI_ABACUS_API_KEY

# OAuth (per service, per env)
XYN_SLACK_CLIENT_ID_DEV
XYN_SLACK_CLIENT_SECRET_DEV
XYN_SLACK_CLIENT_ID_PROD
XYN_SLACK_CLIENT_SECRET_PROD
XYN_GMAIL_CLIENT_ID_DEV
XYN_GMAIL_CLIENT_SECRET_DEV
XYN_GMAIL_CLIENT_ID_PROD
XYN_GMAIL_CLIENT_SECRET_PROD

# Email Services
XYN_EMAIL_MAILJET_API_KEY
XYN_EMAIL_MAILJET_SECRET_KEY
XYN_EMAIL_SENDGRID_API_KEY

# Database
XYN_DB_POSTGRES_CONNECTION_STRING_DEV
XYN_DB_POSTGRES_CONNECTION_STRING_PROD

# Redis
XYN_REDIS_PASSWORD_DEV
XYN_REDIS_PASSWORD_PROD
```

#### Update Cloud Run Deployments
```bash
# Example: Update service with secrets
gcloud run services update xynergy-ai-routing-engine \
  --region us-central1 \
  --set-secrets XYN_AI_OPENAI_API_KEY=XYN_AI_OPENAI_API_KEY:latest,\
                XYN_AI_GOOGLE_STUDIO_KEY=XYN_AI_GOOGLE_STUDIO_KEY:latest
```

- [ ] Update all 41 services to use `--set-secrets`
- [ ] Remove all `.env` files from repositories
- [ ] Update `.gitignore` to prevent future `.env` commits
- [ ] Document secret access process in developer guide

**Deliverables:**
- All secrets migrated to Secret Manager
- 41 services using Secret Manager
- `.env` files removed from git history
- Secret management documentation updated

---

### Week 4: Service Consolidation (Nov 4-10)
**Priority:** P2
**Owner:** Platform / AI Core

#### Audit Duplicate Services
**Current Redundancies:**
1. `ai-routing-engine` vs `xynergy-ai-routing-engine`
2. `marketing-engine` vs `xynergy-marketing-engine`
3. `xynergy-intelligence-gateway` vs `xynergyos-intelligence-gateway`
4. `xynergy-internal-ai-service` vs `internal-ai-service-v2`

#### Consolidation Plan
- [ ] Merge `ai-routing-engine` → `xynergy-ai-routing-engine` (keep xynergy- prefix)
- [ ] Merge `marketing-engine` → `xynergy-marketing-engine`
- [ ] Keep `xynergyos-intelligence-gateway` (TypeScript), deprecate `xynergy-intelligence-gateway` (Python)
- [ ] Merge `xynergy-internal-ai-service` → `internal-ai-service-v2` (v2 has better model support)

**Expected Service Count After Consolidation:** 37 services (from 41)

#### Create xynergy-common Package
- [ ] Create Python package: `xynergy-common`
- [ ] Create TypeScript package: `@xynergy/common`

**Package Structure:**
```
xynergy-common/
├── xynergy_common/
│   ├── __init__.py
│   ├── redis/
│   │   ├── __init__.py
│   │   ├── client.py         # Shared Redis client with connection pooling
│   │   └── cache.py           # Caching decorators
│   ├── logging/
│   │   ├── __init__.py
│   │   ├── logger.py          # Structured logging setup
│   │   └── formatters.py      # JSON log formatting
│   ├── auth/
│   │   ├── __init__.py
│   │   └── middleware.py      # Auth middleware
│   ├── http/
│   │   ├── __init__.py
│   │   ├── client.py          # HTTP client with retry logic
│   │   └── circuit_breaker.py # Circuit breaker implementation
│   ├── pubsub/
│   │   ├── __init__.py
│   │   └── publisher.py       # Pub/Sub publishing utilities
│   └── firestore/
│       ├── __init__.py
│       └── client.py          # Shared Firestore client
├── tests/
├── setup.py
└── README.md
```

**Deliverables:**
- 4 duplicate services consolidated
- xynergy-common Python package published
- @xynergy/common TypeScript package published
- All services migrated to use common packages

---

### Week 5-6: Developer Tools CLI (Nov 11-24)
**Priority:** P2
**Owner:** Developer Experience

#### Build xynergy-devtools CLI
- [ ] Create CLI using Python Click
- [ ] Implement commands:

**Command Specifications:**

```bash
# 1. Setup - Configure local environment
xynergy setup
  --project PROJECT_ID      # GCP project to use
  --env [dev|staging|prod]  # Environment to configure

# Actions:
# - Authenticate with gcloud
# - Configure default project/region
# - Download necessary secrets
# - Create local .xynergy/config.yaml
# - Verify service connectivity

# 2. Run - Launch service locally
xynergy run SERVICE_NAME
  --mock              # Run with mock mode
  --port PORT         # Override default port
  --env-file PATH     # Custom env file

# Actions:
# - Load service configuration
# - Set environment variables
# - Start service with hot reload
# - Open browser to service URL

# 3. Status - Check service health
xynergy status
  --service SERVICE_NAME    # Check specific service
  --all                     # Check all services
  --format [table|json]     # Output format

# Actions:
# - Query /health endpoints
# - Show revision numbers
# - Display memory/CPU usage
# - Indicate traffic allocation

# 4. Logs - Tail service logs
xynergy logs SERVICE_NAME
  --follow           # Stream logs in real-time
  --lines N          # Number of lines to show
  --level [info|error|debug]  # Filter by log level
  --filter PATTERN   # Grep pattern for logs

# Actions:
# - Query Cloud Logging
# - Format logs for readability
# - Color-code by severity
# - Support regex filtering

# 5. Deploy - Trigger deployment
xynergy deploy SERVICE_NAME
  --target [dev|staging|prod]
  --tag TAG_NAME           # Use specific image tag
  --no-traffic             # Deploy without routing traffic
  --wait                   # Wait for deployment to complete

# Actions:
# - Trigger Cloud Build
# - Monitor build progress
# - Verify deployment success
# - Show service URL

# 6. Test - Run service tests
xynergy test SERVICE_NAME
  --unit               # Run unit tests only
  --integration        # Run integration tests
  --coverage           # Generate coverage report

# Actions:
# - Run pytest or Jest
# - Display results
# - Generate coverage HTML
# - Fail on coverage < threshold

# 7. Secrets - Manage secrets
xynergy secrets list SERVICE_NAME
xynergy secrets get SECRET_NAME
xynergy secrets set SECRET_NAME VALUE
xynergy secrets rotate SECRET_NAME

# Actions:
# - Interact with Secret Manager
# - Update Cloud Run services
# - Verify secret propagation

# 8. DB - Database management
xynergy db shell              # Open Firestore shell
xynergy db migrate            # Run migrations
xynergy db backup             # Create backup
xynergy db restore BACKUP_ID  # Restore from backup

# Actions:
# - Connect to Firestore
# - Execute queries
# - Manage data

# 9. Cache - Redis management
xynergy cache flush [SERVICE]  # Clear cache
xynergy cache stats            # Show cache statistics
xynergy cache keys PATTERN     # List keys matching pattern

# Actions:
# - Connect to Redis
# - Execute Redis commands
# - Display metrics

# 10. Docs - Open documentation
xynergy docs                   # Open developer portal
xynergy docs api SERVICE       # Open API docs for service
xynergy docs arch              # Open architecture diagrams
```

**Installation:**
```bash
pip install xynergy-devtools

# Initialize
xynergy setup --project xynergy-dev-1757909467 --env dev
```

**Deliverables:**
- xynergy-devtools CLI published to PyPI
- All 10 commands implemented
- Documentation for each command
- Video tutorial for onboarding

---

### Week 6-7: Documentation Portal (Nov 18 - Dec 1)
**Priority:** P2
**Owner:** Documentation Lead

#### Consolidate Documentation
- [ ] Create `/docs` directory in root repository
- [ ] Migrate all README.md files
- [ ] Consolidate CLAUDE.md files
- [ ] Generate OpenAPI/Swagger docs for all APIs

**Documentation Structure:**
```
/docs
├── index.md                      # Landing page
├── getting-started/
│   ├── overview.md
│   ├── architecture.md
│   ├── quick-start.md
│   └── prerequisites.md
├── developer-guide/
│   ├── local-setup.md
│   ├── creating-services.md
│   ├── testing-guide.md
│   ├── debugging.md
│   └── best-practices.md
├── api-reference/
│   ├── authentication.md
│   ├── intelligence-gateway/
│   │   ├── overview.md
│   │   ├── slack.md
│   │   ├── gmail.md
│   │   ├── calendar.md
│   │   └── crm.md
│   ├── ai-services/
│   ├── analytics/
│   └── business-operations/
├── infrastructure/
│   ├── gcp-setup.md
│   ├── redis.md
│   ├── firestore.md
│   ├── secrets.md
│   └── monitoring.md
├── operations/
│   ├── deployment.md
│   ├── monitoring.md
│   ├── troubleshooting.md
│   └── runbooks/
│       ├── service-down.md
│       ├── high-latency.md
│       └── database-issues.md
└── architecture/
    ├── system-overview.md
    ├── service-mesh.md
    ├── data-flow.md
    ├── security.md
    └── diagrams/
```

#### Generate API Documentation
- [ ] Install FastAPI OpenAPI generators
- [ ] Install TypeDoc for TypeScript services
- [ ] Generate API docs for all 37 services
- [ ] Host on GitHub Pages or Cloud Storage

**Static Site Generation:**
```bash
# Use MkDocs or Docusaurus
mkdocs build
mkdocs serve

# Deploy to Cloud Storage
gsutil rsync -r site/ gs://xynergy-docs/
gsutil web set -m index.html gs://xynergy-docs
```

**Deliverables:**
- Unified documentation portal
- API documentation for 37 services
- Developer onboarding guide
- Troubleshooting runbooks
- Architecture diagrams

---

### Week 7-8: Testing & Validation (Nov 25 - Dec 8)
**Priority:** P1
**Owner:** QA / Security

#### Load Testing with k6
- [ ] Install k6
- [ ] Create load test scripts for each service group
- [ ] Define baseline metrics:
  - Average response time ≤ 300ms
  - Error rate ≤ 1%
  - Throughput ≥ 100 RPS per service

**k6 Test Script Example:**
```javascript
// load-tests/intelligence-gateway.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up
    { duration: '5m', target: 100 },  // Steady state
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% under 500ms
    http_req_failed: ['rate<0.01'],     // Error rate < 1%
  },
};

export default function () {
  const url = 'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app';
  const params = {
    headers: {
      'Authorization': `Bearer ${__ENV.TEST_TOKEN}`,
    },
  };

  // Test health endpoint
  let res = http.get(`${url}/health`, params);
  check(res, {
    'health check succeeds': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });

  // Test API endpoints
  res = http.get(`${url}/api/v2/slack/channels`, params);
  check(res, {
    'slack channels API succeeds': (r) => r.status === 200,
    'response has data': (r) => JSON.parse(r.body).channels !== undefined,
  });

  sleep(1);
}
```

**Run Tests:**
```bash
k6 run --vus 100 --duration 10m load-tests/intelligence-gateway.js
```

#### Security Testing with OWASP ZAP
- [ ] Install OWASP ZAP
- [ ] Configure for API scanning
- [ ] Run automated security scans
- [ ] Generate security reports

**ZAP Command:**
```bash
# Active scan
zap-cli quick-scan -s all --spider \
  https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app

# Generate report
zap-cli report -o security-report.html -f html
```

#### Automated Testing Pipeline
- [ ] Create GitHub Action for monthly regression tests
- [ ] Store test results in `/qa/reports/`
- [ ] Set up automated notifications for failures

**GitHub Action:**
```yaml
name: Monthly Load & Security Tests

on:
  schedule:
    - cron: '0 0 1 * *'  # Run on 1st of every month
  workflow_dispatch:      # Manual trigger

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install k6
        run: |
          sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      - name: Run load tests
        run: k6 run load-tests/intelligence-gateway.js
        env:
          TEST_TOKEN: ${{ secrets.TEST_TOKEN }}
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: test-results/

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: OWASP ZAP Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app'
      - name: Upload scan results
        uses: actions/upload-artifact@v3
        with:
          name: zap-scan-results
          path: zap-scan-results/
```

**Deliverables:**
- k6 load test scripts for all service groups
- OWASP ZAP security scan configuration
- GitHub Action for monthly tests
- Test result reports in `/qa/reports/`
- Baseline metrics documented

---

### Week 8: Infrastructure Standardization (Dec 2-8)
**Priority:** P2
**Owner:** DevOps

#### Terraform Module Refactoring
- [ ] Audit existing Terraform configuration
- [ ] Create standardized module naming:
  - `xynergy-core-networking`
  - `xynergy-core-monitoring`
  - `xynergy-core-security`
  - `xynergy-service-template`
- [ ] Implement consistent tagging:

```hcl
# Standard tags for all resources
locals {
  common_tags = {
    environment = var.environment
    service     = var.service_name
    owner       = "platform-team"
    version     = var.service_version
    managed_by  = "terraform"
    project     = "xynergy-platform"
  }
}
```

#### IAM Policy Baseline
- [ ] Create service account module
- [ ] Define baseline permissions per service type
- [ ] Document IAM best practices

```hcl
# modules/service-account/main.tf
resource "google_service_account" "service" {
  account_id   = "${var.service_name}-sa"
  display_name = "${var.service_name} Service Account"
  description  = "Service account for ${var.service_name}"
}

# Baseline permissions
resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.service.email}"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.service.email}"
}
```

#### Terraform Validation Pipeline
- [ ] Add `terraform validate` to GitHub Actions
- [ ] Add `terraform fmt -check` to CI
- [ ] Implement `terraform plan` on pull requests

**GitHub Action:**
```yaml
name: Terraform Validation

on:
  pull_request:
    paths:
      - 'terraform/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
      - name: Terraform Format Check
        run: terraform fmt -check -recursive
      - name: Terraform Init
        run: terraform init
      - name: Terraform Validate
        run: terraform validate
      - name: Terraform Plan
        run: terraform plan
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
```

**Deliverables:**
- Refactored Terraform modules
- Standardized naming and tagging
- IAM policy baseline
- Terraform validation pipeline
- Infrastructure documentation

---

## Grafana Dashboards

### Dashboard 1: Platform Overview
**Panels:**
1. Total Services (gauge)
2. Healthy Services (percentage)
3. Total Requests/sec (graph)
4. Average Response Time (graph)
5. Error Rate (graph)
6. Top 10 Slowest Endpoints (table)

### Dashboard 2: Service Health
**Panels:**
1. Service Status (status map)
2. CPU Usage per Service (heatmap)
3. Memory Usage per Service (heatmap)
4. Request Rate per Service (graph)
5. Error Rate per Service (graph)

### Dashboard 3: Infrastructure
**Panels:**
1. Redis Hit/Miss Ratio (gauge)
2. Redis Memory Usage (graph)
3. Firestore Operations/sec (graph)
4. Pub/Sub Queue Depth (graph)
5. BigQuery Query Performance (histogram)

### Dashboard 4: AI Services
**Panels:**
1. AI Request Rate (graph)
2. Model Inference Time (histogram)
3. AI Provider Distribution (pie chart)
4. Token Usage (graph)
5. AI Cost per Hour (graph)

**Dashboard Export:**
```json
{
  "dashboard": {
    "title": "Xynergy Platform Overview",
    "panels": [...],
    "refresh": "30s",
    "tags": ["xynergy", "platform", "overview"]
  }
}
```

---

## Success Metrics

### Technical Metrics
| Metric | Current | Target | Achieved |
|--------|---------|--------|----------|
| Services with observability | 0/41 (0%) | 41/41 (100%) | ⏳ |
| Automated deployments | 0/41 (0%) | 41/41 (100%) | ⏳ |
| Unified authentication | Partial | Complete | ⏳ |
| Secrets in Secret Manager | 31/~100 (31%) | 100/100 (100%) | ⏳ |
| Duplicate services | 41 | 37 (-4) | ⏳ |
| CLI onboarding time | N/A | ≤ 10 minutes | ⏳ |
| Documentation coverage | ~60% | 100% | ⏳ |
| Load test coverage | 0% | 100% | ⏳ |
| Security scan coverage | 0% | 100% | ⏳ |

### Operational Metrics
- **Mean Time to Deploy (MTTD):** < 5 minutes (automated)
- **Mean Time to Recovery (MTTR):** < 15 minutes
- **Deployment Frequency:** 10+ per day
- **Change Failure Rate:** < 5%

### Developer Experience Metrics
- **Onboarding Time:** ≤ 10 minutes (via CLI)
- **Time to First Deployment:** ≤ 30 minutes
- **Documentation Accessibility:** All docs searchable and linked

---

## Risk Management

### High Risks
1. **Service Consolidation Breaking Changes**
   - **Mitigation:** Thorough testing, gradual rollout, rollback plan
   - **Owner:** Platform Team

2. **Auth Service Single Point of Failure**
   - **Mitigation:** High availability deployment, caching, fallback logic
   - **Owner:** Security Team

3. **Secrets Migration Downtime**
   - **Mitigation:** Blue-green deployment, test in staging first
   - **Owner:** DevOps

### Medium Risks
1. **CI/CD Pipeline Complexity**
   - **Mitigation:** Start simple, iterate, comprehensive testing
   - **Owner:** DevOps

2. **Developer CLI Adoption**
   - **Mitigation:** Great UX, documentation, video tutorials
   - **Owner:** DevEx Team

---

## Dependencies & Prerequisites

### External Dependencies
- GCP APIs enabled (Monitoring, Logging, Trace)
- GitHub repository connected to Cloud Build
- Slack webhook for notifications
- Artifact Registry configured

### Internal Dependencies
- All 41 services healthy (✅ COMPLETE)
- Service accounts configured (✅ COMPLETE)
- Infrastructure operational (✅ COMPLETE)

---

## Post-Implementation Checklist

### Week 9: Validation & Documentation
- [ ] All acceptance criteria met
- [ ] Load testing passed with baseline metrics
- [ ] Security scans passed with no critical issues
- [ ] Documentation portal published
- [ ] Developer onboarding tested with new team member
- [ ] Runbooks tested for common scenarios
- [ ] Monitoring dashboards reviewed by ops team

### Week 10: Knowledge Transfer
- [ ] Team training on new tools and processes
- [ ] Recorded video tutorials
- [ ] Q&A sessions
- [ ] Updated runbooks
- [ ] Handoff to operations team

---

## Appendix

### A. Tool Versions
```
Python: 3.11
Node.js: 20
TypeScript: 5.3
Terraform: 1.5+
k6: latest
OWASP ZAP: latest
```

### B. Naming Conventions
**Services:** `xynergy-[functional-area]-[service-type]`
**Secrets:** `XYN_[SERVICE]_[NAME]_[ENV]`
**Terraform Modules:** `xynergy-[type]-[name]`
**Docker Images:** `us-central1-docker.pkg.dev/PROJECT/xynergy-platform/SERVICE:TAG`

### C. Contact Information
**Platform Team:** platform@xynergy.com
**DevOps:** devops@xynergy.com
**Security:** security@xynergy.com
**Documentation:** docs@xynergy.com

---

**Document Version:** 1.0
**Last Updated:** October 13, 2025
**Next Review:** Weekly during implementation phase
