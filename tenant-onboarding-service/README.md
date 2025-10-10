# Tenant Onboarding Service

Complete company onboarding workflow automation for XynergyOS platform. This service handles the entire process from form submission to fully operational tenant with website deployment, analytics setup, ASO initialization, and cost tracking.

## Overview

The Tenant Onboarding Service automates the complex multi-step process of bringing new companies onto the Xynergy platform, reducing manual setup time from hours to minutes.

**Key Features:**
- **Multiple Website Sources**: Xynergy-generated sites, GitHub repositories, or manual uploads
- **GitHub CI/CD Integration**: Automatic deployments on git push with Cloud Build triggers
- **Dual Environments**: Production and staging deployments for each tenant
- **ASO Presets**: Minimal, Standard, Aggressive, or Custom configurations
- **Cost Tracking**: Per-tenant GCP spend monitoring with budget alerts
- **Admin Dashboard**: Centralized management of all companies

## Architecture

```
┌────────────────────────────────────────────────────┐
│ Onboarding Wizard (Form Submission)                │
└─────────────────┬──────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────┐
│ Tenant Onboarding Service (This Service)          │
├────────────────────────────────────────────────────┤
│                                                    │
│  1. Create Tenant Record (Firestore)              │
│  2. Configure DNS (SiteGround API)                │
│  3. Deploy Website (Production + Staging)         │
│  4. Setup Analytics (GA4, Search Console)         │
│  5. Initialize ASO (ASO Engine integration)       │
│  6. Configure Access (Firebase Auth)              │
│                                                    │
└───┬────────────────────────────┬───────────────────┘
    │                            │
    │                            │
    ▼                            ▼
┌────────────┐          ┌─────────────────┐
│ GitHub     │          │ Cloud Storage   │
│ Cloud Build│          │ Generated Sites │
│ Triggers   │          │ Tenant Websites │
└────────────┘          └─────────────────┘
    │                            │
    └──────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│ Cloud Run Deployments                  │
│ - {tenant}-website (production)        │
│ - {tenant}-website-staging (staging)   │
└────────────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────┐
│ Cost Tracking (BigQuery)               │
│ - Per-tenant billing labels            │
│ - Daily cost aggregation               │
│ - Budget monitoring & alerts           │
└────────────────────────────────────────┘
```

## Features

### 1. ASO Presets

Pre-configured feature sets for different deployment scenarios:

**Minimal** ($25/month budget)
- Basic tracking only
- Weekly competitive analysis
- No social monitoring
- Delayed content generation (500+ sessions)

**Standard** ($50/month budget) - *Recommended*
- Daily competitive tracking
- Social monitoring (starts after 30 days)
- Content generation (after 100 sessions)
- Full briefings and alerts

**Aggressive** ($100/month budget)
- All features active immediately
- Deep competitive analysis
- Social monitoring (starts after 7 days)
- Real-time alerts
- Content generation (after 50 sessions)

**Custom**
- Configure all settings manually
- Set your own thresholds and delays

### 2. Website Sources

**Xynergy-Generated Sites**
- Pull directly from Internal LLM generation
- Select from recent generations (last 30 days)
- Automatic deployment from Cloud Storage

**GitHub Repository**
- Connect your own GitHub repo
- Automatic CI/CD with Cloud Build triggers
- Separate production (main) and staging (staging) branches
- Auto-deploy on push to either branch

**Manual Upload**
- Upload Next.js project files
- Extract and deploy automatically

**Templates** (Coming Soon)
- Start from pre-built templates
- Customize before deployment

### 3. Staging Environments

Every tenant gets TWO Cloud Run services:

**Production** (`{tenant}-website`)
- 1Gi RAM, 1 CPU
- 0-10 instances
- Custom domain mapping
- Full resource allocation

**Staging** (`{tenant}-website-staging`)
- 512Mi RAM, 1 CPU
- 0-3 instances (cost optimization)
- Staging subdomain (staging.{domain})
- Test changes before production

**Promotion Workflow:**
- Test changes on staging
- Click "Promote to Production" in admin panel
- Staging image deployed to production
- Zero manual steps required

### 4. GitHub CI/CD

Automatic deployment pipeline for connected GitHub repositories:

```
Developer pushes to "staging" branch
  ↓
GitHub webhook triggers Cloud Build
  ↓
Docker image built: {tenant}-website-staging:abc123
  ↓
Deployed to Cloud Run (staging)
  ↓
Firestore deployment record updated
  ↓
Staging environment live in 5-10 minutes
```

Same process for production (main branch).

### 5. Cost Tracking

Per-tenant cost monitoring with BigQuery billing export:

**What's Tracked:**
- Cloud Run hosting costs
- BigQuery analytics costs
- Cloud Storage costs
- Networking/bandwidth costs

**Cost Dashboard Includes:**
- Current month spend vs budget
- Breakdown by service type
- Production vs staging costs
- Daily average and month-end projection
- Historical trends (last 6 months)
- Optimization recommendations

**Budget Alerts:**
- 50% of budget consumed
- 75% of budget consumed
- 90% of budget consumed
- 100% of budget consumed

## API Endpoints

### Health & Status

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "tenant-onboarding-service",
  "version": "1.0.0",
  "dependencies": {
    "firestore": "healthy",
    "storage": "healthy"
  }
}
```

### ASO Presets

#### `GET /v1/aso-presets`
Get all available ASO presets.

**Response:**
```json
{
  "presets": [
    {
      "id": "minimal",
      "name": "Minimal Launch",
      "description": "Basic tracking, no social, delayed content generation",
      "config": { ... }
    },
    ...
  ]
}
```

#### `GET /v1/aso-presets/{preset_id}`
Get specific preset details.

### Onboarding

#### `POST /v1/onboarding/start`
Start onboarding process for a new company.

**Request Body:**
```json
{
  "company_name": "ConnectForge",
  "domain": "connectforge.com",
  "purchase_domain": false,
  "website_source": "github_repo",
  "github_config": {
    "repo_url": "github.com/clearforge/connectforge",
    "branch_production": "main",
    "branch_staging": "staging",
    "auto_deploy": true
  },
  "enable_staging": true,
  "aso_preset": "standard",
  "target_keywords": [
    "business connectivity",
    "enterprise integration"
  ],
  "contact_name": "John Doe",
  "contact_email": "john@connectforge.com",
  "monthly_budget": 100.0
}
```

**Response:**
```json
{
  "tenant_id": "connectforge_001",
  "status": "onboarding_started",
  "message": "Onboarding workflow initiated. This will take approximately 20 minutes.",
  "progress_url": "/v1/onboarding/progress/connectforge_001",
  "estimated_completion": "2025-10-09T11:00:00Z"
}
```

#### `GET /v1/onboarding/progress/{tenant_id}`
Get onboarding progress for a tenant.

**Response:**
```json
{
  "tenant_id": "connectforge_001",
  "status": "website_deployed",
  "current_step": 3,
  "steps_completed": [
    "tenant_record_created",
    "dns_configured",
    "github_cicd_configured",
    "website_deployed"
  ],
  "production_url": "https://connectforge.com",
  "staging_url": "https://staging.connectforge.com",
  "started_at": "2025-10-09T10:40:00Z",
  "estimated_completion": "2025-10-09T11:00:00Z"
}
```

### Tenant Management

#### `GET /v1/tenants`
List all tenants.

**Query Parameters:**
- `status` (optional): Filter by status (active, pending, failed)
- `limit` (optional): Max results (default: 50)

**Response:**
```json
{
  "tenants": [
    {
      "tenant_id": "connectforge_001",
      "company_name": "ConnectForge",
      "domain": "connectforge.com",
      "status": "active",
      "aso_preset": "standard",
      "created_at": "2025-10-09T10:40:00Z"
    }
  ],
  "total": 1
}
```

#### `GET /v1/tenants/{tenant_id}`
Get detailed tenant information.

#### `PUT /v1/tenants/{tenant_id}`
Update tenant configuration.

**Request Body:**
```json
{
  "target_keywords": ["new keyword", "another keyword"],
  "cost_tracking.monthly_budget": 150.0
}
```

#### `DELETE /v1/tenants/{tenant_id}?confirm=true`
Delete a tenant (soft delete).

### Deployments

#### `GET /v1/tenants/{tenant_id}/deployments`
Get tenant deployment information.

**Response:**
```json
{
  "tenant_id": "connectforge_001",
  "company_name": "ConnectForge",
  "domain": "connectforge.com",
  "production_url": "https://connectforge.com",
  "staging_url": "https://staging.connectforge.com",
  "github_enabled": true,
  "production_version": "main@a3f5d9c",
  "staging_version": "staging@b7e2f1a"
}
```

#### `POST /v1/deployments/{tenant_id}/promote`
Promote staging deployment to production.

**Request Body:**
```json
{
  "tenant_id": "connectforge_001",
  "promoted_by": "john@clearforge.ai",
  "notes": "Tested new hero section, looks good"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Staging successfully promoted to production",
  "promotion_details": {
    "status": "promoted",
    "production_url": "https://connectforge.com",
    "promoted_at": "2025-10-09T11:30:00Z"
  }
}
```

### Cost Tracking

#### `GET /v1/costs/{tenant_id}`
Get cost dashboard for a tenant.

**Response:**
```json
{
  "tenant_id": "connectforge_001",
  "company_name": "ConnectForge",
  "current_month": {
    "total_cost": 23.45,
    "breakdown": {
      "cloud_run": 12.30,
      "bigquery": 6.75,
      "storage": 2.85,
      "networking": 1.55
    },
    "production_cost": 18.20,
    "staging_cost": 5.25,
    "daily_average": 0.78,
    "projected_month_end": 24.00
  },
  "budget": {
    "monthly_limit": 100.00,
    "current_spend": 23.45,
    "remaining": 76.55,
    "percent_used": 23.45,
    "on_track": true
  },
  "optimizations": [
    {
      "recommendation": "Scale staging to zero when not in use",
      "potential_savings": 2.63,
      "effort": "low"
    }
  ]
}
```

#### `GET /v1/costs/summary`
Get cost summary for all tenants.

**Response:**
```json
{
  "total_tenants": 15,
  "total_cost_mtd": 412.85,
  "total_budget": 1500.00,
  "percent_of_budget": 27.5,
  "tenants": [
    {
      "tenant_id": "connectforge_001",
      "company_name": "ConnectForge",
      "cost_mtd": 23.45,
      "budget": 100.00,
      "percent_used": 23.45
    },
    ...
  ]
}
```

### Admin Dashboard

#### `GET /v1/admin/dashboard`
Get admin dashboard with all companies overview.

**Response:**
```json
{
  "companies": [
    {
      "tenant_id": "connectforge_001",
      "company_name": "ConnectForge",
      "domain": "connectforge.com",
      "status": "active",
      "created_at": "2025-10-09T10:40:00Z",
      "cost_mtd": 23.45,
      "budget": 100.00,
      "aso_preset": "standard",
      "staging_enabled": true,
      "github_enabled": true
    }
  ],
  "total_companies": 1,
  "total_cost_mtd": 23.45
}
```

### Generated Sites

#### `GET /v1/generated-sites`
List recently generated sites available for deployment.

**Response:**
```json
{
  "generated_sites": [
    {
      "generation_id": "gen_20251009_abc123",
      "generated_at": "2025-10-09T09:30:00Z",
      "metadata": {
        "purpose": "ConnectForge company website",
        "framework": "nextjs",
        "ai_model": "internal_llm"
      },
      "status": "generated"
    }
  ],
  "total": 1
}
```

## Deployment

### Prerequisites

1. GCP project configured
2. Cloud Run API enabled
3. Cloud Build API enabled
4. BigQuery billing export configured
5. Firestore collections created

### Environment Variables

```bash
GOOGLE_CLOUD_PROJECT=xynergy-dev-1757909467
ENVIRONMENT=production
```

### Deploy to Cloud Run

```bash
cd tenant-onboarding-service
chmod +x deploy.sh
./deploy.sh
```

### Firestore Collections

Required collections:

- `tenants` - Tenant configuration and status
- `onboarding_progress` - Onboarding workflow tracking
- `deployments` - Deployment information
- `deployment_promotions` - Promotion history
- `generated_sites` - Xynergy-generated sites catalog
- `tenant_costs` - Daily cost data cache

### BigQuery Setup

Enable billing export to BigQuery:

1. Go to Cloud Console → Billing → Billing Export
2. Enable "Detailed usage cost" export
3. Dataset: `billing_export`
4. Table prefix: `gcp_billing_export_v1`

## Usage Examples

### Example 1: Onboard New Company with GitHub Repo

```bash
curl -X POST "https://tenant-onboarding-service-xxx.run.app/v1/onboarding/start" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ConnectForge",
    "domain": "connectforge.com",
    "website_source": "github_repo",
    "github_config": {
      "repo_url": "github.com/clearforge/connectforge",
      "branch_production": "main",
      "branch_staging": "staging",
      "auto_deploy": true
    },
    "enable_staging": true,
    "aso_preset": "standard",
    "target_keywords": ["business connectivity"],
    "contact_name": "John Doe",
    "contact_email": "john@connectforge.com",
    "monthly_budget": 100.0
  }'
```

### Example 2: Check Onboarding Progress

```bash
curl "https://tenant-onboarding-service-xxx.run.app/v1/onboarding/progress/connectforge_001"
```

### Example 3: Get Cost Dashboard

```bash
curl "https://tenant-onboarding-service-xxx.run.app/v1/costs/connectforge_001"
```

### Example 4: Promote Staging to Production

```bash
curl -X POST "https://tenant-onboarding-service-xxx.run.app/v1/deployments/connectforge_001/promote" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "connectforge_001",
    "promoted_by": "john@clearforge.ai",
    "notes": "Tested new features, ready for production"
  }'
```

## Workflow Timeline

**From form submit to fully operational:**

- **Minutes 0-1**: Tenant record created, ASO preset applied
- **Minutes 1-3**: DNS configured (if purchasing domain)
- **Minutes 3-15**: Website deployed (both environments)
- **Minutes 15-17**: Analytics and tracking setup
- **Minutes 17-18**: ASO initialization
- **Minutes 18-20**: Access configuration and notifications
- **Hours 0-48**: Intelligence gathering (automatic)
- **Hour 48**: First intelligence briefing delivered

**Total active work time:** ~20 minutes
**Total time to fully operational:** 24-48 hours

## Cost Optimization

### Resource Labeling

All GCP resources are labeled for cost tracking:

```
tenant_id: {tenant_id}
company_name: {sanitized_name}
cost_center: clearforge_services
environment: production|staging
service_type: website|analytics|aso|storage
```

### Automatic Optimization Suggestions

The service analyzes costs and provides recommendations:

- Scale staging to zero when idle
- Optimize Cloud Run instance configuration
- Enable Cloud CDN for static assets
- Adjust BigQuery query patterns

### Budget Alerts

Automatic alerts at 50%, 75%, 90%, 100% of budget.

## Security Considerations

- GitHub access tokens stored in Secret Manager
- Tenant data isolated in Firestore
- Service accounts with minimal permissions
- CORS restricted to clearforge.ai and xynergyos.com domains
- Non-root container user

## Monitoring

### Logs

Structured JSON logging with Cloud Logging:

```json
{
  "event": "onboarding_started",
  "tenant_id": "connectforge_001",
  "company_name": "ConnectForge",
  "timestamp": "2025-10-09T10:40:00Z"
}
```

### Metrics

Monitor via Cloud Run metrics:
- Request count by endpoint
- Onboarding success/failure rate
- Average onboarding duration
- Cost tracking accuracy

## Troubleshooting

### Onboarding Stuck

Check onboarding progress:
```bash
curl "/v1/onboarding/progress/{tenant_id}"
```

Look for failed steps and error messages.

### GitHub Triggers Not Working

1. Verify GitHub webhook configuration
2. Check Cloud Build trigger status
3. Verify access token in Secret Manager
4. Check Cloud Build logs

### Cost Data Not Showing

1. Verify BigQuery billing export is enabled
2. Check resource labels are applied
3. Wait 24 hours for first data
4. Verify Firestore cost cache collection

## Future Enhancements

- SiteGround API integration for domain purchases
- Automated DNS configuration
- GA4 property auto-creation
- Search Console auto-connection
- Slack/Teams notifications
- Multi-region deployment support
- Custom domain SSL automation

## Support

For issues or questions:
- Check logs in Cloud Logging
- Review Firestore tenant record
- Contact: team@clearforge.ai

## License

Internal Xynergy Platform service - Proprietary
