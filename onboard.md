# Complete Company Onboarding Workflow v2
## From Website Files to Full XynergyOS Operation

**Version:** 2.0 - Enhanced with GitHub CI/CD, Staging, Cost Tracking, and Presets  
**Date:** October 2025

---

## ENHANCED ONBOARDING WIZARD

### Website Source Options (Updated)

```typescript
interface CompanyOnboardingForm {
  // ... previous fields ...
  
  // Website Source (EXPANDED)
  website_source: 
    | 'xynergy_generated'      // NEW: Pull from Internal LLM generation
    | 'upload_files'            // Upload Next.js project
    | 'github_repo'             // Connect GitHub (with CI/CD)
    | 'from_template';          // Future: Use starter template
  
  // If xynergy_generated
  generated_site_id?: string;   // Select from recent generations
  
  // If github_repo
  github_config?: {
    repo_url: string;           // e.g., "github.com/clearforge/connectforge"
    branch_production: string;  // Default: "main"
    branch_staging: string;     // Default: "staging"
    auto_deploy: boolean;       // Auto-deploy on push
    access_token?: string;      // GitHub PAT for private repos
  };
  
  // Staging environment
  enable_staging: boolean;      // Default: true
  staging_subdomain?: string;   // Default: "staging.{domain}"
  
  // ASO Preset (NEW)
  aso_preset: 
    | 'minimal'      // Basic tracking only
    | 'standard'     // Balanced features
    | 'aggressive'   // All features, short delays
    | 'custom';      // User configures everything
  
  // ... rest of fields ...
}
```

---

## ASO FEATURE PRESETS

### Preset Configurations

```typescript
const ASO_PRESETS = {
  minimal: {
    name: "Minimal Launch",
    description: "Basic tracking, no social, delayed content generation",
    config: {
      social_monitoring: {
        enabled: false,
        delay_until_days: null
      },
      competitive_tracking: {
        enabled: true,
        frequency: 'weekly'
      },
      content_generation: {
        enabled: true,
        delay_until_threshold: {
          min_traffic: 500,      // Wait for more data
          min_keywords: 50
        }
      },
      budget: {
        monthly_external_api_limit: 25.00
      },
      notifications: {
        daily_briefing: true,
        opportunity_alerts: false,  // Only major opportunities
        competitive_alerts: false
      }
    }
  },
  
  standard: {
    name: "Standard Launch",
    description: "Balanced approach, 30-day delays for social and content",
    config: {
      social_monitoring: {
        enabled: true,
        delay_until_days: 30
      },
      competitive_tracking: {
        enabled: true,
        frequency: 'daily'
      },
      content_generation: {
        enabled: true,
        delay_until_threshold: {
          min_traffic: 100,
          min_keywords: 20
        }
      },
      budget: {
        monthly_external_api_limit: 50.00
      },
      notifications: {
        daily_briefing: true,
        opportunity_alerts: true,
        competitive_alerts: true
      }
    }
  },
  
  aggressive: {
    name: "Aggressive Launch",
    description: "All features active, minimal delays, maximum intelligence",
    config: {
      social_monitoring: {
        enabled: true,
        delay_until_days: 7        // Start quickly
      },
      competitive_tracking: {
        enabled: true,
        frequency: 'daily',
        deep_analysis: true          // More comprehensive tracking
      },
      content_generation: {
        enabled: true,
        delay_until_threshold: {
          min_traffic: 50,           // Start earlier
          min_keywords: 10
        }
      },
      budget: {
        monthly_external_api_limit: 100.00
      },
      notifications: {
        daily_briefing: true,
        opportunity_alerts: true,
        competitive_alerts: true,
        real_time_alerts: true       // Immediate notifications
      }
    }
  },
  
  custom: {
    name: "Custom Configuration",
    description: "Configure all settings manually",
    config: null  // User fills out all fields
  }
};
```

---

## UPDATED ONBOARDING UI

```
┌─────────────────────────────────────────────────────────────┐
│ Create New Company                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Company Name: [ConnectForge_________________]              │
│ Domain:       [connectforge.com_____________]              │
│ ○ Purchase new domain  ○ Already own this domain          │
│                                                             │
│ ─── Website Source ───                                     │
│ ○ Pull from Xynergy-generated site                         │
│   └─ Select site: [Recent Generation #847 ▼]             │
│                                                             │
│ ○ Connect GitHub repository (with CI/CD)                   │
│   └─ Repository: [github.com/clearforge/connectforge]     │
│   └─ Production branch: [main__]                           │
│   └─ Staging branch:    [staging]                          │
│   └─ ☑ Auto-deploy on push                                │
│                                                             │
│ ○ Upload website files (Next.js project)                   │
│   └─ [Choose Files...]                                     │
│                                                             │
│ ○ Start from template (coming soon)                        │
│                                                             │
│ ─── Environment Configuration ───                          │
│ ☑ Enable staging environment                               │
│   └─ Staging URL: [staging.connectforge.com]              │
│                                                             │
│ ─── ASO Configuration ───                                  │
│ Preset: [Standard Launch ▼]                               │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Standard Launch                                     │   │
│ │                                                     │   │
│ │ • Daily competitive tracking                       │   │
│ │ • Social monitoring (starts in 30 days)           │   │
│ │ • Content generation (after 100 sessions)          │   │
│ │ • Monthly budget: $50                              │   │
│ │ • Daily briefings + alerts                         │   │
│ │                                                     │   │
│ │ [Change to Custom Configuration...]                │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ Target Keywords (3-5 recommended):                         │
│ [business connectivity_____________________]               │
│ [enterprise integration____________________]               │
│ [digital transformation____________________]               │
│                                                             │
│ Competitors (optional, can add later):                     │
│ [Add competitor...]                                        │
│                                                             │
│            [Cancel]  [Create Company →]                    │
└─────────────────────────────────────────────────────────────┘
```

---

## XYNERGY-GENERATED SITE INTEGRATION

### How Xynergy-Generated Sites Work

When you use the Internal LLM to generate a site (like for RankRight), it's stored temporarily:

```typescript
// After Internal LLM generates a complete Next.js site
interface GeneratedSite {
  generation_id: string;
  generated_at: Timestamp;
  generated_by: string;          // user_id
  project_files: {
    path: string;                // Cloud Storage path
    file_count: number;
    total_size: number;
  };
  metadata: {
    purpose: string;             // "ConnectForge company website"
    framework: "nextjs";
    template_used?: string;
    ai_model: "internal_llm";
    generation_cost: number;
  };
  status: "generated" | "deployed" | "archived";
}

// Stored in: Cloud Storage
// Path: gs://xynergy-generated-sites/{generation_id}/
// Files: Complete Next.js project ready to deploy
```

### Selection Process

**When you choose "Pull from Xynergy-generated site":**

```typescript
async function getRecentGeneratedSites(): Promise<GeneratedSite[]> {
  // Get sites generated in last 30 days, not yet deployed
  const sites = await firestore
    .collection('generated_sites')
    .where('status', '==', 'generated')
    .where('generated_at', '>', thirtyDaysAgo)
    .orderBy('generated_at', 'desc')
    .limit(20)
    .get();
  
  return sites.docs.map(doc => ({
    ...doc.data(),
    preview_url: `gs://xynergy-generated-sites/${doc.id}/preview.png`
  }));
}

// When selected for deployment
async function deployGeneratedSite(generationId: string, tenantId: string) {
  // Copy files from Cloud Storage to working directory
  const sourcePath = `gs://xynergy-generated-sites/${generationId}`;
  const workingPath = `/tmp/${tenantId}-deployment`;
  
  await copyFromCloudStorage(sourcePath, workingPath);
  
  // Continue with normal deployment process
  // (inject analytics, build Docker, deploy to Cloud Run, etc.)
  
  // Mark site as deployed
  await firestore.collection('generated_sites').doc(generationId).update({
    status: 'deployed',
    deployed_to: tenantId,
    deployed_at: Timestamp.now()
  });
}
```

---

## GITHUB CI/CD INTEGRATION

### Setup Process

**Step 1: Connect Repository**

```typescript
async function setupGitHubCICD(tenantId: string, config: GitHubConfig) {
  const { repo_url, branch_production, branch_staging, access_token } = config;
  
  // Parse GitHub URL
  const [owner, repo] = parseGitHubUrl(repo_url); // e.g., "clearforge", "connectforge"
  
  // Store connection info
  await firestore.collection('tenants').doc(tenantId).update({
    'deployment.github': {
      owner,
      repo,
      branch_production,
      branch_staging,
      access_token_secret: await storeInSecretManager(access_token),
      connected_at: Timestamp.now()
    }
  });
  
  // Create Cloud Build triggers
  await createProductionTrigger(tenantId, owner, repo, branch_production);
  await createStagingTrigger(tenantId, owner, repo, branch_staging);
  
  return { success: true };
}
```

**Step 2: Cloud Build Triggers**

**Production Trigger (cloudbuild-production.yaml):**
```yaml
name: deploy-${TENANT_ID}-production
description: Auto-deploy to production on push to main

# Trigger on push to main branch
trigger:
  github:
    owner: clearforge
    name: connectforge
    push:
      branch: ^main$

# Build and deploy
steps:
  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website:${SHORT_SHA}'
      - '-t'
      - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website:latest'
      - '.'
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website:${SHORT_SHA}'
  
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website:latest'
  
  # Deploy to Cloud Run (Production)
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${TENANT_ID}-website'
      - '--image'
      - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website:${SHORT_SHA}'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'TENANT_ID=${TENANT_ID},ENVIRONMENT=production'
      - '--set-secrets'
      - 'GATEWAY_API_KEY=gateway-api-key-${TENANT_ID}:latest'
  
  # Update deployment record in Firestore
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: bash
    args:
      - '-c'
      - |
        gcloud firestore documents update tenants/${TENANT_ID} \
          --update-mask deployment.last_production_deploy \
          --field-data '{"last_production_deploy":{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","commit":"${SHORT_SHA}","branch":"main"}}'

substitutions:
  _TENANT_ID: 'connectforge_001'

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'N1_HIGHCPU_8'

images:
  - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website:${SHORT_SHA}'
  - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website:latest'
```

**Staging Trigger (cloudbuild-staging.yaml):**
```yaml
name: deploy-${TENANT_ID}-staging
description: Auto-deploy to staging on push to staging branch

# Trigger on push to staging branch
trigger:
  github:
    owner: clearforge
    name: connectforge
    push:
      branch: ^staging$

# Build and deploy
steps:
  # Build Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website-staging:${SHORT_SHA}'
      - '-t'
      - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website-staging:latest'
      - '.'
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website-staging:${SHORT_SHA}'
  
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website-staging:latest'
  
  # Deploy to Cloud Run (Staging)
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${TENANT_ID}-website-staging'
      - '--image'
      - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website-staging:${SHORT_SHA}'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'TENANT_ID=${TENANT_ID},ENVIRONMENT=staging'
      - '--set-secrets'
      - 'GATEWAY_API_KEY=gateway-api-key-${TENANT_ID}:latest'

substitutions:
  _TENANT_ID: 'connectforge_001'

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: 'N1_HIGHCPU_8'

images:
  - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website-staging:${SHORT_SHA}'
  - 'gcr.io/xynergy-dev-1757909467/${TENANT_ID}-website-staging:latest'
```

**Step 3: GitHub Webhook**

When triggers are created, Cloud Build automatically sets up GitHub webhooks. The flow:

```
Developer pushes to "main" branch
  ↓
GitHub webhook triggers Cloud Build
  ↓
Cloud Build executes cloudbuild-production.yaml
  ↓
Docker image built and pushed
  ↓
Cloud Run service updated
  ↓
Production site automatically updated
  ↓
Firestore deployment record updated
  ↓
Notification sent (optional)
```

---

## STAGING ENVIRONMENT SETUP

### Infrastructure for Staging

**Each company gets TWO Cloud Run services:**

```typescript
async function setupStagingEnvironment(tenantId: string, domain: string) {
  // 1. Deploy production service (already done in main flow)
  const productionService = `${tenantId}-website`;
  const productionDomain = domain; // e.g., connectforge.com
  
  // 2. Deploy staging service
  const stagingService = `${tenantId}-website-staging`;
  const stagingDomain = `staging.${domain}`; // e.g., staging.connectforge.com
  
  // Deploy staging with same configuration as production
  await deployToCloudRun({
    serviceName: stagingService,
    image: `gcr.io/xynergy-dev-1757909467/${stagingService}:latest`,
    region: 'us-central1',
    envVars: {
      TENANT_ID: tenantId,
      ENVIRONMENT: 'staging',
      GATEWAY_URL: 'https://intelligence-gateway.run.app'
    },
    labels: {
      tenant_id: tenantId,
      environment: 'staging',
      cost_center: 'clearforge_services'
    },
    // Staging gets fewer resources
    memory: '512Mi',
    cpu: '1',
    minInstances: 0,  // Can scale to zero
    maxInstances: 3
  });
  
  // 3. Configure staging subdomain DNS
  await configureDNS(stagingDomain, stagingService);
  
  // 4. Update tenant record
  await firestore.collection('tenants').doc(tenantId).update({
    'deployment.staging': {
      service_name: stagingService,
      domain: stagingDomain,
      enabled: true,
      created_at: Timestamp.now()
    }
  });
  
  return {
    production_url: `https://${productionDomain}`,
    staging_url: `https://${stagingDomain}`
  };
}
```

### Staging DNS Configuration

**SiteGround DNS for staging subdomain:**
```typescript
await siteGroundAPI.addDNSRecords(domain, [
  // Staging subdomain
  { type: 'A', name: 'staging', value: '216.239.32.21' },
  { type: 'A', name: 'staging', value: '216.239.34.21' },
  { type: 'A', name: 'staging', value: '216.239.36.21' },
  { type: 'A', name: 'staging', value: '216.239.38.21' },
  // IPv6 for staging
  { type: 'AAAA', name: 'staging', value: '2001:4860:4802:32::15' },
  { type: 'AAAA', name: 'staging', value: '2001:4860:4802:34::15' },
  // ... more IPv6 records
]);
```

### Promotion Flow (Staging → Production)

**XynergyOS Admin Panel:**
```
┌─────────────────────────────────────────────────────┐
│ Deployments: ConnectForge                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│ PRODUCTION                                          │
│ URL: https://connectforge.com                       │
│ Version: main@a3f5d9c (deployed 2 hours ago)       │
│ Status: ● Healthy                                   │
│                                                     │
│ ─────────────────────────────────────────────────  │
│                                                     │
│ STAGING                                             │
│ URL: https://staging.connectforge.com               │
│ Version: staging@b7e2f1a (deployed 15 min ago)     │
│ Status: ● Healthy                                   │
│                                                     │
│ Changes in staging:                                │
│ • Updated hero section copy                         │
│ • Added new service page                            │
│ • Fixed mobile menu bug                             │
│                                                     │
│       [View Staging] [Promote to Production]        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**When "Promote to Production" clicked:**
```typescript
async function promoteToProduction(tenantId: string) {
  // Get staging image
  const stagingImage = await getCurrentStagingImage(tenantId);
  
  // Tag staging image as production
  await docker.tag(
    stagingImage,
    `gcr.io/xynergy-dev-1757909467/${tenantId}-website:promoted-${Date.now()}`
  );
  
  // Deploy to production
  await gcloud.run.deploy(`${tenantId}-website`, {
    image: stagingImage,
    region: 'us-central1'
  });
  
  // Log promotion
  await logDeployment(tenantId, 'production', {
    promoted_from: 'staging',
    staging_commit: await getStagingCommit(tenantId),
    promoted_by: getCurrentUserId(),
    promoted_at: Timestamp.now()
  });
}
```

---

## COST TRACKING SYSTEM

### GCP Resource Labeling

**All resources created for a tenant get labeled:**

```typescript
const RESOURCE_LABELS = {
  tenant_id: tenantId,                    // e.g., "connectforge_001"
  company_name: companyName,              // e.g., "connectforge"
  cost_center: 'clearforge_services',     // All your companies
  environment: 'production' | 'staging',
  service_type: 'website' | 'analytics' | 'aso' | 'storage'
};

// Applied to:
// - Cloud Run services
// - Cloud Storage buckets
// - BigQuery tables
// - Firestore collections (via metadata)
// - Pub/Sub topics
// - Cloud Scheduler jobs
```

### Cost Data Collection

**Daily Cost Export Job:**
```typescript
// Cloud Function triggered daily at 1 AM
export async function collectCostData() {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  
  // Query BigQuery billing export
  const query = `
    SELECT
      labels.value AS tenant_id,
      labels_2.value AS environment,
      labels_3.value AS service_type,
      service.description AS service_name,
      sku.description AS sku_description,
      SUM(cost) AS total_cost,
      SUM(usage.amount) AS usage_amount,
      usage.unit AS usage_unit,
      DATE(usage_start_time) AS usage_date
    FROM
      \`xynergy-dev-1757909467.billing_export.gcp_billing_export_v1_*\`
    LEFT JOIN UNNEST(labels) AS labels ON labels.key = 'tenant_id'
    LEFT JOIN UNNEST(labels) AS labels_2 ON labels_2.key = 'environment'
    LEFT JOIN UNNEST(labels) AS labels_3 ON labels_3.key = 'service_type'
    WHERE
      DATE(usage_start_time) = DATE('${formatDate(yesterday)}')
      AND labels.value IS NOT NULL
    GROUP BY
      tenant_id, environment, service_type, service_name, sku_description, usage_amount, usage_unit, usage_date
  `;
  
  const [rows] = await bigQuery.query(query);
  
  // Store in Firestore for quick access
  for (const row of rows) {
    await firestore.collection('tenant_costs').add({
      tenant_id: row.tenant_id,
      environment: row.environment,
      service_type: row.service_type,
      service_name: row.service_name,
      sku_description: row.sku_description,
      cost: row.total_cost,
      usage_amount: row.usage_amount,
      usage_unit: row.usage_unit,
      date: Timestamp.fromDate(new Date(row.usage_date)),
      created_at: Timestamp.now()
    });
  }
}
```

### Cost Dashboard in XynergyOS

**XynergyOS Finance Panel:**
```typescript
interface CostDashboard {
  tenant_id: string;
  current_month: {
    total_cost: number;
    breakdown: {
      cloud_run: number;           // Website hosting
      bigquery: number;            // ASO analytics
      storage: number;             // File storage
      networking: number;          // Bandwidth
      other: number;
    };
    
    // By environment
    production_cost: number;
    staging_cost: number;
    
    // Trends
    daily_average: number;
    projected_month_end: number;
    vs_last_month: {
      change: number;
      percent: number;
    };
  };
  
  // Historical data
  last_6_months: Array<{
    month: string;
    total_cost: number;
    breakdown: { [service: string]: number };
  }>;
  
  // Budget tracking
  budget: {
    monthly_limit: number;
    current_spend: number;
    remaining: number;
    percent_used: number;
    on_track: boolean;
  };
  
  // Cost optimization suggestions
  optimizations: Array<{
    recommendation: string;
    potential_savings: number;
    effort: 'low' | 'medium' | 'high';
  }>;
}
```

**UI Component:**
```
┌─────────────────────────────────────────────────────┐
│ Cost Dashboard: ConnectForge                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│ CURRENT MONTH (October 2025)                       │
│ ┌─────────────────────────────────────────────┐   │
│ │  Total Spend: $23.45                        │   │
│ │  Budget:      $100.00                       │   │
│ │  Remaining:   $76.55 (77%)                  │   │
│ │  ████████░░ On Track ✓                      │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ BREAKDOWN BY SERVICE                               │
│ ┌─────────────────────────────────────────────┐   │
│ │ Cloud Run (Website)      $12.30  (52%)      │   │
│ │ BigQuery (Analytics)      $6.75  (29%)      │   │
│ │ Storage                   $2.85  (12%)      │   │
│ │ Networking                $1.55   (7%)      │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ENVIRONMENT SPLIT                                  │
│ Production: $18.20 (78%)  |  Staging: $5.25 (22%) │
│                                                     │
│ COST TREND                                         │
│ [Line chart showing daily costs over last 30 days] │
│                                                     │
│ OPTIMIZATION OPPORTUNITIES                         │
│ ┌─────────────────────────────────────────────┐   │
│ │ 💡 Scale staging to zero when not in use   │   │
│ │    Potential savings: $2-3/month            │   │
│ │    Effort: Low                              │   │
│ │    [Apply Optimization]                     │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│     [View Detailed Report] [Set Budget Alert]      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Cost Alerts

**Automatic Budget Monitoring:**
```typescript
// Cloud Function triggered hourly
export async function checkCostBudgets() {
  const tenants = await getAllActiveTenants();
  
  for (const tenant of tenants) {
    const currentSpend = await getCurrentMonthSpend(tenant.tenant_id);
    const budget = tenant.cost_tracking?.monthly_budget || 100;
    const percentUsed = (currentSpend / budget) * 100;
    
    // Alert at 50%, 75%, 90%, 100%
    const alertThresholds = [50, 75, 90, 100];
    
    for (const threshold of alertThresholds) {
      if (percentUsed >= threshold && !hasAlertBeenSent(tenant.tenant_id, threshold)) {
        await sendCostAlert({
          tenant_id: tenant.tenant_id,
          threshold: threshold,
          current_spend: currentSpend,
          budget: budget,
          percent_used: percentUsed,
          projected_end_of_month: projectMonthEndSpend(currentSpend)
        });
        
        await markAlertSent(tenant.tenant_id, threshold);
      }
    }
  }
}
```

---

## COMPLETE DEPLOYMENT TIMELINE

### From Form Submit to Fully Operational

**Minutes 0-1: Initial Setup**
- ✅ Tenant record created with ASO preset applied
- ✅ Cost tracking labels configured
- ✅ Initial budget set

**Minutes 1-3: Domain & DNS**
- ⏳ Domain purchased via SiteGround (if needed)
- ⏳ DNS records configured for production
- ⏳ DNS records configured for staging subdomain

**Minutes 3-15: Website Deployment**

**If Xynergy-Generated:**
- ⏳ Copy files from Cloud Storage
- ⏳ Inject analytics and ASO code
- ⏳ Build Docker images (production + staging)
- ⏳ Deploy to Cloud Run (both environments)

**If GitHub Repo:**
- ⏳ Clone repository
- ⏳ Create Cloud Build triggers (production + staging)
- ⏳ Trigger initial builds
- ⏳ Deploy to Cloud Run (both environments)

**If Upload:**
- ⏳ Extract files
- ⏳ Validate Next.js project
- ⏳ Build and deploy

**Minutes 15-17: Analytics & Tracking**
- ⏳ GA4 property created
- ⏳ Search Console connected
- ⏳ Cost tracking initialized
- ⏳ First cost data point logged

**Minutes 17-18: ASO Initialization**
- ⏳ Tenant added to ASO Engine
- ⏳ Initial keyword research queued
- ⏳ Competitive tracking scheduled (based on preset)
- ⏳ Feature delays configured

**Minutes 18-20: Access & Notifications**
- ⏳ Firebase user created
- ⏳ XynergyOS access configured
- ⏳ Welcome email sent with credentials
- ✅ Status: "active"

**Hours 0-48: Intelligence Gathering**
- ⏳ Keyword expansion
- ⏳ Competitor analysis
- ⏳ Website crawling
- ⏳ Performance baseline

**Hour 48: Fully Operational**
- ✅ First intelligence briefing
- ✅ All features active or scheduled
- ✅ Cost tracking reporting
- ✅ CI/CD pipeline ready (if GitHub)

---

## POST-DEPLOYMENT DEVELOPER WORKFLOW

### Using GitHub CI/CD

**Day-to-Day Development:**

```bash
# Clone repo
git clone https://github.com/clearforge/connectforge.git
cd connectforge

# Make changes locally
# ... edit files ...

# Test locally
npm run dev

# Commit changes
git add .
git commit -m "Updated hero section"

# Deploy to staging
git push origin staging

# Wait 5-10 minutes for automatic deployment
# Visit https://staging.connectforge.com to review

# If looks good, merge to production
git checkout main
git merge staging
git push origin main

# Wait 5-10 minutes for automatic production deployment
# Visit https://connectforge.com to see live changes
```

**Automatic Notifications (Optional):**
```typescript
// After successful deployment, send Slack notification
await slack.send({
  channel: '#deployments',
  text: `✅ ConnectForge staging deployed
  Commit: b7e2f1a
  Author: John Doe
  Changes: Updated hero section
  URL: https://staging.connectforge.com`
});
```

---

## ADMIN CONTROL PANEL

### Managing All Companies

**XynergyOS Admin Dashboard:**
```
┌─────────────────────────────────────────────────────────────┐
│ ClearForge Companies                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [+ Create New Company]          [View Cost Report]         │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ ConnectForge                                         │   │
│ │ connectforge.com | ● Active | Deployed 15 days ago  │   │
│ │                                                      │   │
│ │ Cost MTD: $23.45 / $100 budget (23%)                │   │
│ │ ASO: Standard preset | Social active in 15 days     │   │
│ │ Deployments: Prod ✓ | Staging ✓ | GitHub CI/CD ✓   │   │
│ │                                                      │   │
│ │ [View Dashboard] [Manage] [View Costs]              │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Project NEXUS                                        │   │
│ │ projectnexus.com | ● Active | Deployed 45 days ago  │   │
│ │                                                      │   │
│ │ Cost MTD: $67.20 / $150 budget (45%)                │   │
│ │ ASO: Aggressive preset | All features active        │   │
│ │ Deployments: Prod ✓ | Staging ✓ | Manual uploads   │   │
│ │                                                      │   │
│ │ [View Dashboard] [Manage] [View Costs]              │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ TOTAL COSTS THIS MONTH: $412.85                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## SUMMARY: WHAT YOU GET

✅ **Automated Onboarding**: 20-minute setup from form to deployment  
✅ **Multiple Website Sources**: Xynergy-generated, GitHub, or manual upload  
✅ **GitHub CI/CD**: Automatic deployments on git push  
✅ **Staging Environments**: Test changes before production  
✅ **ASO Presets**: Minimal, Standard, Aggressive, or Custom  
✅ **Cost Tracking**: Per-company GCP spend broken down by service  
✅ **Budget Monitoring**: Alerts at 50%, 75%, 90%, 100% of budget  
✅ **XynergyOS Integration**: Full intelligence dashboard for each company  
✅ **Intelligent Feature Delays**: Social/content generation activate when ready  

---

**Ready to implement?** Want me to detail any specific piece further?