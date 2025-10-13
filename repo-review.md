# Repository Technical Review

## Git
- Remotes:
  - origin	https://github.com/GPT-Gradient/xynergy-core.git (fetch)
  - origin	https://github.com/GPT-Gradient/xynergy-core.git (push)
- Last commit: 15e5dd47 2025-10-13 00:51:08 -0400 GPT-Gradient feat: Phase 8 Security & Performance Optimization Complete

## Basic Structure (depth 2)
.
├── .DS_Store
├── .env.development
├── .env.production
├── .gitignore
├── advanced-analytics
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   ├── requirements.txt
│   ├── tenant_data_utils.py
│   └── tenant_utils.py
├── AI_CONFIGURATION.md
├── ai-assistant
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── ai-ml-engine
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── shared
├── ai-providers
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── ai-routing-engine
│   ├── ai_token_optimizer.py
│   ├── auth.py
│   ├── deploy.sh
│   ├── Dockerfile
│   ├── Dockerfile.optimized
│   ├── gcp_clients.py
│   ├── http_client.py
│   ├── main.py
│   ├── phase2_utils.py
│   ├── rate_limiting.py
│   ├── redis_cache.py
│   └── requirements.txt
├── ai-workflow-engine
│   ├── main.py
│   ├── phase2_utils.py
│   ├── requirements.txt
│   ├── tenant_data_utils.py
│   └── tenant_utils.py
├── analytics-aggregation-service
│   ├── cloudbuild.yaml
│   ├── Dockerfile
│   ├── Dockerfile.optimized
│   ├── main_optimized.py
│   ├── main.py
│   ├── requirements_optimized.txt
│   └── requirements.txt
├── analytics-data-layer
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── API_INTEGRATION_GUIDE.md
├── ARCHITECTURE.md
├── archive
│   ├── deployment-scripts
│   ├── documentation
│   ├── phase-reports
│   ├── phase8-optimization
│   ├── README.md
│   ├── templates
│   └── utilities
├── aso-engine
│   ├── deploy.sh
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── attribution-coordinator
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── audit-logging-service
│   ├── cloudbuild.yaml
│   ├── Dockerfile
│   ├── Dockerfile.optimized
│   ├── main_optimized.py
│   ├── main.py
│   ├── requirements_optimized.txt
│   └── requirements.txt
├── automated-publisher
│   └── main.py
├── BACKEND_PRODUCTION_AUDIT_REPORT.md
├── beta-program-service
│   ├── .dockerignore
│   ├── .gitignore
│   ├── Dockerfile
│   ├── package-lock.json
│   ├── package.json
│   ├── src
│   └── tsconfig.json
├── business-entity-service
│   ├── .dockerignore
│   ├── .gitignore
│   ├── Dockerfile
│   ├── package-lock.json
│   ├── package.json
│   ├── README.md
│   ├── src
│   └── tsconfig.json
├── CLAUDE.md
├── client_secret_835612502919-shofuadpcdpv08q9t93i286o4j2ndmca.apps.googleusercontent.com.json
├── cloudbuild-marketing.yaml
├── CODE_REVIEW_FIXES_COMPLETE.md
├── competitive-analysis-service
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── COMPREHENSIVE_CODE_REVIEW_REPORT_NOV_2025.md
├── COMPREHENSIVE_CODE_REVIEW_REPORT.md
├── content-hub
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── COST_OPTIMIZATION_TRACKING.md
├── crm-engine
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── package-lock.json
│   ├── package.json
│   ├── src
│   └── tsconfig.json
├── CURRENT_STATE_OCTOBER_2025.md
├── DEPLOYMENT_COMPLETE.md
├── DEPLOYMENT_GUIDE.md
├── Dockerfile.marketing-engine
├── docs
│   ├── .DS_Store
│   ├── 3D Topology.png
│   ├── ADR
│   ├── ALL_REMAINING_DOCUMENTATION.md
│   ├── ARCHITECTURE_DECISION_RECORDS.md
│   ├── DATA_MODEL_SCHEMA.md
│   ├── exec dashboard.png
│   ├── infrastructure page scroll issue.png
│   ├── PERFORMANCE_OPTIMIZATION_GUIDE.md
│   ├── PLATFORM_OVERVIEW_FOR_NEW_EMPLOYEES.md
│   ├── SECURITY_ARCHITECTURE.md
│   ├── strange space at scroll.png
│   └── TECHNICAL_DESIGN_DOCUMENT.md
├── executive-dashboard
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── fact-checking-layer
│   ├── deploy.sh
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── fact-checking-service
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── FIREBASE_CONFIG_COMPLETE.md
├── FRONTEND_BACKEND_INTEGRATION_ASSESSMENT.md
├── FRONTEND_BACKEND_MISMATCH_CRITICAL.md
├── GATEWAY_DEPLOYMENT_COMPLETE.md
├── GMAIL_OAUTH_COMPLETE.md
├── gmail-intelligence-service
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── package-lock.json
│   ├── package.json
│   ├── src
│   └── tsconfig.json
├── INFRASTRUCTURE_STATUS_REPORT.md
├── INTEGRATION_DEPLOYMENT_SUMMARY.md
├── INTEGRATION_SECRETS_CHECKLIST.md
├── INTEGRATION_STATUS_SUMMARY.md
├── INTELLIGENCE_GATEWAY_IMPLEMENTATION_PLAN.md
├── INTELLIGENCE_GATEWAY_OPTIMIZATION_PLAN.md
├── intelligence-gateway-trd.md
├── intelligence-gateway.md
├── internal-ai-service
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── internal-ai-service-v2
│   ├── deploy.sh
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── JWT_AUTH_COMPLETE.md
├── keyword-revenue-tracker
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── LOCAL_INTEGRATION_ANALYSIS.md
├── market-intelligence-service
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── marketing-engine
│   ├── .gcloudignore
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── monetization-integration
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   ├── requirements.txt
│   ├── tenant_data_utils.py
│   └── tenant_utils.py
├── monitoring
│   ├── alert_policies.sh
│   ├── dashboard_config.json
│   └── README.md
├── oauth-management-service
│   ├── .dockerignore
│   ├── .gitignore
│   ├── Dockerfile
│   ├── package-lock.json
│   ├── package.json
│   ├── src
│   └── tsconfig.json
├── OPERATIONAL_LAYER_DEPLOYMENT_STATUS.md
├── OPERATIONAL_LAYER_PHASE1_COMPLETE.md
├── OPERATIONAL_LAYER_PHASE1_FINAL.md
├── OPERATIONAL_LAYER_PHASE1_IMPLEMENTATION.md
├── OPERATIONAL_LAYER_PHASE2_COMPLETE.md
├── OPERATIONAL_LAYER_PHASE3_COMPLETE.md
├── operational-layer.md
├── OPTIMIZATION_COMPLETE_FINAL_STATUS.md
├── OPTIMIZATION_COMPLETE.md
├── performance-scaling
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── shared
├── permission-service
│   ├── .env.example
│   ├── Dockerfile
│   ├── package-lock.json
│   ├── package.json
│   ├── README.md
│   ├── src
│   └── tsconfig.json
├── PHASE1_OPTIMIZATION_COMPLETE.md
├── PHASE3_COMPLETE.md
├── PHASE4_COMPLETE.md
├── PHASE6_DEPLOYMENT_INSTRUCTIONS.md
├── PHASES_1-4_COMPLETE_SUMMARY.md
├── plagiarism-detector
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── PLATFORM_AS_BUILT.md
├── PLATFORM_INTEGRATION_COMPLETE.md
├── platform-dashboard
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── platform-integration-trd.md
├── project-management
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── project-state.md
├── qa-engine
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── QUICK_REFERENCE.md
├── rapid-content-generator
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── README_OPTIMIZATION.md
├── README.md
├── real-time-trend-monitor
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── repo-review.md
├── reports-export
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── research-coordinator
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── scheduler-automation-engine
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── schemas
│   ├── competitor_content.json
│   ├── competitor_profiles.json
│   ├── content_performance.json
│   ├── content_pieces.json
│   ├── cost_tracking.json
│   ├── cross_client_patterns.json
│   ├── keyword_data.json
│   ├── keywords.json
│   ├── llm_interactions.json
│   ├── opportunities.json
│   ├── performance_predictions.json
│   ├── serp_data.json
│   └── verified_facts.json
├── scripts
│   └── init-operational-layer-database.ts
├── secrets-config
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── SECURITY_FIXES.md
├── security-compliance
│   ├── main.py
│   └── requirements.txt
├── security-governance
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── setup_infrastructure.sh
├── shared
│   ├── ai_token_optimizer.py
│   ├── anomaly_detection.py
│   ├── auth.py
│   ├── bigquery_optimizer.py
│   ├── container_optimizer.py
│   ├── cost_intelligence.py
│   ├── deployment_automation.py
│   ├── exceptions.py
│   ├── gcp_clients.py
│   ├── http_client.py
│   ├── memory_monitor.py
│   ├── monitoring_system.py
│   ├── pubsub_manager.py
│   ├── rate_limiting.py
│   ├── redis_cache.py
│   ├── scaling_optimizer.py
│   ├── semantic_cache.py
│   ├── standard_layout.css
│   ├── tenant_data_utils.py
│   ├── tenant_utils.py
│   ├── tracing.py
│   └── workflow_orchestrator.py
├── SLACK_OAUTH_COMPLETE.md
├── slack-intelligence-service
│   ├── .dockerignore
│   ├── .env.example
│   ├── Dockerfile
│   ├── package-lock.json
│   ├── package.json
│   ├── src
│   └── tsconfig.json
├── system-runtime
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── TECHNICAL_INTEGRATION_REPORT.md
├── tenant-management
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   ├── requirements.txt
│   ├── tenant_data_utils.py
│   └── tenant_utils.py
├── tenant-onboarding-service
│   ├── app
│   ├── deploy.sh
│   ├── Dockerfile
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── README.md
│   ├── requirements.txt
│   └── templates
├── terraform
│   ├── .terraform.lock.hcl
│   └── main.tf
├── test-jwt-auth.js
├── trending-engine-coordinator
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── trust-safety-validator
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── update-trd.md
├── validation-coordinator
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── WEEK1_INTELLIGENCE_GATEWAY_COMPLETE.md
├── WEEK2_INTELLIGENCE_GATEWAY_COMPLETE.md
├── WEEK3_INTELLIGENCE_GATEWAY_COMPLETE.md
├── WEEK4_QUICK_REFERENCE.md
├── WEEK4_SLACK_INTELLIGENCE_COMPLETE.md
├── WEEK5-6_CRM_ENGINE_COMPLETE.md
├── WEEK7-8_GMAIL_INTELLIGENCE_COMPLETE.md
├── XYNERGY_API_INTEGRATION_GUIDE.md
├── XYNERGY_CREDENTIALS_AUDIT_REPORT.md
├── xynergy_info_gathering.md
├── XYNERGY_SDK_README.md
├── xynergy-competency-engine
│   ├── adaptive_workflow.py
│   ├── collective_intelligence.py
│   ├── Dockerfile
│   ├── main.py
│   ├── phase2_utils.py
│   └── requirements.txt
├── xynergy-intelligence-gateway
│   ├── app
│   ├── deploy.sh
│   ├── Dockerfile
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── README.md
│   ├── requirements.txt
│   └── TESTING_GUIDE.md
└── xynergyos-intelligence-gateway
    ├── .dockerignore
    ├── .env.example
    ├── Dockerfile
    ├── IMPLEMENTATION_COMPLETE_SUMMARY.md
    ├── package-lock.json
    ├── package.json
    ├── README.md
    ├── src
    ├── tests
    └── tsconfig.json

81 directories, 364 files

## Detected Tech & Framework Signals
- Terraform

## API Surface (routes/endpoints)

## Environment Variables (names only)
  - AI_ROUTING_URL
  - CALENDAR_INTELLIGENCE_URL
  - CORS_ORIGINS
  - CRM_ENGINE_URL
  - FIREBASE_PROJECT_ID
  - GCLOUD_PROJECT
  - GCP_PROJECT_ID
  - GCP_REGION
  - GMAIL_INTELLIGENCE_URL
  - GOOGLE_APPLICATION_CREDENTIALS
  - LOG_LEVEL
  - NODE_ENV
  - PORT
  - RATE_LIMIT_MAX_REQUESTS
  - RATE_LIMIT_WINDOW_MS
  - REACT_APP_API_URL
  - REACT_APP_FIREBASE_API_KEY
  - REACT_APP_FIREBASE_APP_ID
  - REACT_APP_FIREBASE_AUTH_DOMAIN
  - REACT_APP_FIREBASE_MEASUREMENT_ID
  - REACT_APP_FIREBASE_MESSAGING_SENDER_ID
  - REACT_APP_FIREBASE_PROJECT_ID
  - REACT_APP_FIREBASE_STORAGE_BUCKET
  - REACT_APP_WS_URL
  - REDIS_HOST
  - REDIS_PASSWORD
  - REDIS_PORT
  - SLACK_EVENTS_TOPIC
  - SLACK_INTELLIGENCE_URL

## External Calls (domains)
  - None found

## Build & Deploy Signals
### Terraform files
  - ./terraform/main.tf

## Frontend Signals
  - None detected

## Backend Signals
  - None detected

## Data & Schema Signals
  - ./slack-intelligence-service/dist/middleware/auth.js
  - ./slack-intelligence-service/dist/config/firebase.d.ts.map
  - ./slack-intelligence-service/dist/config/config.d.ts
  - ./slack-intelligence-service/dist/config/config.js
  - ./slack-intelligence-service/dist/config/firebase.js.map
  - ./slack-intelligence-service/dist/config/firebase.d.ts
  - ./slack-intelligence-service/dist/config/firebase.js
  - ./slack-intelligence-service/dist/server.js
  - ./slack-intelligence-service/dist/routes/health.js
  - ./slack-intelligence-service/node_modules/node-forge/LICENSE
  - ./slack-intelligence-service/node_modules/node-forge/lib/jsbn.js
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/MREVRANGE_WITHLABELS.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/MREVRANGE.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/GET.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/INCRBY.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/DECRBY.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/MGET.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/RANGE.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/index.js
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/DEL.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/QUERYINDEX.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/REVRANGE.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/QUERYINDEX.js
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/MGET_WITHLABELS.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/index.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/MRANGE.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/dist/commands/MRANGE_WITHLABELS.d.ts
  - ./slack-intelligence-service/node_modules/@redis/time-series/README.md
  - ./slack-intelligence-service/node_modules/@redis/time-series/package.json
  - ./slack-intelligence-service/node_modules/@redis/graph/dist/graph.d.ts
  - ./slack-intelligence-service/node_modules/@redis/graph/dist/commands/QUERY.d.ts
  - ./slack-intelligence-service/node_modules/@redis/graph/dist/commands/RO_QUERY.d.ts
  - ./slack-intelligence-service/node_modules/@redis/graph/dist/commands/index.d.ts
  - ./slack-intelligence-service/node_modules/@redis/graph/README.md
  - ./slack-intelligence-service/node_modules/@redis/graph/package.json
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/top-k/QUERY.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/top-k/QUERY.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/top-k/ADD.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/top-k/COUNT.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/top-k/COUNT.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/top-k/ADD.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/BYRANK.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/MERGE.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/CDF.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/MIN.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/MAX.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/TRIMMED_MEAN.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/QUANTILE.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/BYREVRANK.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/CREATE.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/ADD.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/INFO.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/RANK.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/index.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/MERGE.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/RESET.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/t-digest/REVRANK.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/LOADCHUNK.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/MADD.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/MEXISTS.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/EXISTS.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/ADD.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/MEXISTS.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/ADD.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/MADD.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/INSERT.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/EXISTS.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/bloom/INSERT.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/ADDNX.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/INSERTNX.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/LOADCHUNK.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/DEL.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/INSERTNX.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/EXISTS.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/index.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/ADD.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/DEL.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/ADDNX.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/ADD.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/index.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/INSERT.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/EXISTS.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/cuckoo/INSERT.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/count-min-sketch/QUERY.d.ts
  - ./slack-intelligence-service/node_modules/@redis/bloom/dist/commands/count-min-sketch/QUERY.js
  - ./slack-intelligence-service/node_modules/@redis/bloom/README.md
  - ./slack-intelligence-service/node_modules/@redis/bloom/package.json
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/DICTDEL.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/SYNUPDATE.js
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/DICTADD.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/SEARCH.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/AGGREGATE.js
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/DICTADD.js
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/index.js
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/CREATE.js
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/SUGDEL.js
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/DICTDEL.js
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/INFO.js
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/AGGREGATE.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/CURSOR_READ.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/CURSOR_DEL.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/PROFILE_SEARCH.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/INFO.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/SYNUPDATE.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/SEARCH_NOCONTENT.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/index.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/AGGREGATE_WITHCURSOR.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/dist/commands/SUGDEL.d.ts
  - ./slack-intelligence-service/node_modules/@redis/search/README.md
  - ./slack-intelligence-service/node_modules/@redis/search/package.json
  - ./slack-intelligence-service/node_modules/@redis/json/dist/commands/MSET.d.ts
  - ./slack-intelligence-service/node_modules/@redis/json/dist/commands/GET.d.ts
  - ./slack-intelligence-service/node_modules/@redis/json/dist/commands/GET.js
  - ./slack-intelligence-service/node_modules/@redis/json/README.md
  - ./slack-intelligence-service/node_modules/@redis/json/package.json
  - ./slack-intelligence-service/node_modules/@redis/client/dist/package.json
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/cluster/cluster-slots.d.ts
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/cluster/index.js
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/cluster/index.d.ts
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/cluster/cluster-slots.js
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/commands/GEOSEARCHSTORE.js
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/commands/generic-transformers.js
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/commands/CLUSTER_NODES.js
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/commands/ZRANGESTORE.js
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/client/pub-sub.js
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/client/index.js
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/client/RESP2/decoder.js
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/client/index.d.ts
  - ./slack-intelligence-service/node_modules/@redis/client/README.md
  - ./slack-intelligence-service/node_modules/@redis/client/package.json
  - ./slack-intelligence-service/node_modules/farmhash-modern/bin/nodejs/farmhash_modern.js
  - ./slack-intelligence-service/node_modules/farmhash-modern/bin/bundler/farmhash_modern_bg.js
  - ./slack-intelligence-service/node_modules/farmhash-modern/README.md
  - ./slack-intelligence-service/node_modules/farmhash-modern/package.json
  - ./slack-intelligence-service/node_modules/farmhash-modern/lib/index.d.mts
  - ./slack-intelligence-service/node_modules/farmhash-modern/lib/index.d.cts
  - ./slack-intelligence-service/node_modules/farmhash-modern/lib/index.js
  - ./slack-intelligence-service/node_modules/farmhash-modern/lib/index.cjs
  - ./slack-intelligence-service/node_modules/farmhash-modern/lib/index.mjs
  - ./slack-intelligence-service/node_modules/farmhash-modern/lib/index.d.ts
  - ./slack-intelligence-service/node_modules/farmhash-modern/lib/browser.js
  - ./slack-intelligence-service/node_modules/farmhash-modern/lib/browser.d.ts
  - ./slack-intelligence-service/node_modules/dotenv/README.md
  - ./slack-intelligence-service/node_modules/resolve/lib/core.json
  - ./slack-intelligence-service/node_modules/@opentelemetry/api/LICENSE
  - ./slack-intelligence-service/node_modules/express/History.md
  - ./slack-intelligence-service/node_modules/express/package.json
  - ./slack-intelligence-service/node_modules/redis/dist/index.js
  - ./slack-intelligence-service/node_modules/redis/dist/index.d.ts
  - ./slack-intelligence-service/node_modules/redis/README.md
  - ./slack-intelligence-service/node_modules/redis/package.json
  - ./slack-intelligence-service/node_modules/gaxios/LICENSE
  - ./slack-intelligence-service/node_modules/typescript/lib/typesMap.json
  - ./slack-intelligence-service/node_modules/typescript/lib/typescript.js
  - ./slack-intelligence-service/node_modules/typescript/lib/_tsc.js
  - ./slack-intelligence-service/node_modules/typescript/LICENSE.txt
  - ./slack-intelligence-service/node_modules/typescript/ThirdPartyNoticeText.txt
  - ./slack-intelligence-service/node_modules/baseline-browser-mapping/LICENSE.txt
  - ./slack-intelligence-service/node_modules/json-bigint/lib/stringify.js
  - ./slack-intelligence-service/node_modules/json-bigint/lib/parse.js
  - ./slack-intelligence-service/node_modules/keyv/README.md
  - ./slack-intelligence-service/node_modules/keyv/package.json
  - ./slack-intelligence-service/node_modules/keyv/src/index.js
  - ./slack-intelligence-service/node_modules/keyv/src/index.d.ts
  - ./slack-intelligence-service/node_modules/eslint-visitor-keys/LICENSE
  - ./slack-intelligence-service/node_modules/@humanwhocodes/config-array/LICENSE
  - ./slack-intelligence-service/node_modules/@humanwhocodes/module-importer/LICENSE
  - ./slack-intelligence-service/node_modules/mime-types/node_modules/mime-db/db.json
  - ./slack-intelligence-service/node_modules/google-auth-library/LICENSE
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/types/firestore.d.ts
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/LICENSE
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/README.md
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/build/src/transaction.js
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/build/src/backoff.js
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/build/src/rate-limiter.d.ts
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/build/src/rate-limiter.js
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/build/src/index.js
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/build/src/bulk-writer.js
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/build/src/bulk-writer.d.ts
  - ./slack-intelligence-service/node_modules/@google-cloud/firestore/build/src/index.d.ts
  - ./slack-intelligence-service/node_modules/@google-cloud/promisify/LICENSE
  - ./slack-intelligence-service/node_modules/@google-cloud/projectify/LICENSE
  - ./slack-intelligence-service/node_modules/@google-cloud/storage/LICENSE
  - ./slack-intelligence-service/node_modules/@google-cloud/paginator/LICENSE
  - ./slack-intelligence-service/node_modules/.package-lock.json
  - ./slack-intelligence-service/node_modules/long/LICENSE
  - ./slack-intelligence-service/node_modules/doctrine/LICENSE
  - ./slack-intelligence-service/node_modules/doctrine/LICENSE.closure-compiler
  - ./slack-intelligence-service/node_modules/ecdsa-sig-formatter/LICENSE
  - ./slack-intelligence-service/node_modules/is-core-module/test/index.js
  - ./slack-intelligence-service/node_modules/is-core-module/CHANGELOG.md
  - ./slack-intelligence-service/node_modules/is-core-module/core.json
  - ./slack-intelligence-service/node_modules/firebase-admin/LICENSE
  - ./slack-intelligence-service/node_modules/firebase-admin/CHANGELOG.md
  - ./slack-intelligence-service/node_modules/firebase-admin/node_modules/@types/node/sqlite.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/node_modules/@types/node/process.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/node_modules/@types/node/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/node_modules/@types/node/ts5.6/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/README.md
  - ./slack-intelligence-service/node_modules/firebase-admin/package.json
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/database/database.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/database/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/database/database-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/database/database.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/database/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/database/database-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/credential/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/credential/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/default-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/credential-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/core.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/credential-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/lifecycle.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/credential.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/firebase-app.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/credential-factory.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/core.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/firebase-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/firebase-app.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/credential.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/credential-factory.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/firebase-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app/lifecycle.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/firestore/firestore-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/firestore/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/firestore/firestore-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/firestore/firestore-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/firestore/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/firestore/firestore-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/token-verifier.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/token-verifier.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/project-config.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/tenant-manager.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/auth-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/auth-config.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/tenant.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/project-config-manager.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/base-auth.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/auth.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/action-code-settings-builder.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/project-config-manager.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/token-generator.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/user-record.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/tenant.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/user-record.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/tenant-manager.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/identifier.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/auth-api-request.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/auth-config.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/auth-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/auth-api-request.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/project-config.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/auth.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/token-generator.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/action-code-settings-builder.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/base-auth.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/user-import-builder.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/identifier.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/auth/user-import-builder.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/app-metadata.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management-api-request-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/android-app.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/ios-app.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/ios-app.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management-api-request-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/app-metadata.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/android-app.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/jwt.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/error.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/crypto-signer.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/api-request.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/validator.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/crypto-signer.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/error.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/deep-copy.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/validator.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/jwt.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/deep-copy.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/utils/api-request.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/token-verifier.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/token-verifier.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-api-client-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-api.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/token-generator.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-api-client-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-api.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/token-generator.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-api.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/condition-evaluator-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/internal/value-impl.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/internal/value-impl.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-api-client-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/condition-evaluator-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-api.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-api-client-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/firebase-namespace-api.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/storage/storage-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/storage/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/storage/utils.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/storage/storage-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/storage/utils.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/storage/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/storage/storage.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/storage/storage.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/extensions/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions-api.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions-api-client-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions-api.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions-api-client-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/extensions/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/installations/installations-request-handler.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/installations/installations-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/installations/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/installations/installations-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/installations/installations.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/installations/installations-request-handler.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/installations/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/installations/installations.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/default-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/instance-id/instance-id-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/instance-id/instance-id.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/instance-id/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/instance-id/instance-id.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/instance-id/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/instance-id/instance-id-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/firebase-namespace-api.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc-utils.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/eventarc/cloudevent.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/eventarc/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc-client-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc-utils.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/eventarc/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc-client-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/eventarc/cloudevent.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/functions/functions.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/functions/functions-api-client-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/functions/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/functions/functions-api.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/functions/functions-api.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/functions/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/functions/functions.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/functions/functions-api-client-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect-api-client-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect-api.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/data-connect/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect-api.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect-api-client-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/data-connect/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-utils.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/machine-learning/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-utils.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-api-client.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-api-client.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/machine-learning/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/batch-request-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/batch-request-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-errors-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-api-request-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-api-request-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-errors-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-api.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-api.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-namespace.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-api-client-internal.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/security-rules/index.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-namespace.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-api-client-internal.js
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/security-rules/index.d.ts
  - ./slack-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-internal.js
  - ./slack-intelligence-service/node_modules/gcp-metadata/LICENSE
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/index.cjs.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/index.cjs.js
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/index.esm2017.js
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/index.esm5.js
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/index.node.esm.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/test/exp/integration.test.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/test/helpers/syncpoint-util.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/index.node.esm.js
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/core/AuthTokenProvider.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/core/util/validation.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/core/storage/DOMStorageWrapper.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/core/AppCheckTokenProvider.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/core/view/EventRegistration.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/internal/index.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/api/OnDisconnect.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/api/Reference.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/api/Database.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/api/Reference_impl.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/index.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/index.standalone.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/test/exp/integration.test.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/test/helpers/syncpoint-util.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/index.node.cjs.js
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/private.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/index.esm5.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/index.standalone.js
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/index.esm2017.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/public.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/internal.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/index.node.cjs.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/core/AuthTokenProvider.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/core/util/validation.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/core/storage/DOMStorageWrapper.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/core/AppCheckTokenProvider.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/core/view/EventRegistration.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/internal/index.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/api/OnDisconnect.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/api/Reference.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/api/Database.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/api/Reference_impl.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/dist/src/index.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database/README.md
  - ./slack-intelligence-service/node_modules/@firebase/database/package.json
  - ./slack-intelligence-service/node_modules/@firebase/logger/dist/index.cjs.js.map
  - ./slack-intelligence-service/node_modules/@firebase/logger/dist/index.cjs.js
  - ./slack-intelligence-service/node_modules/@firebase/logger/dist/esm/index.esm2017.js
  - ./slack-intelligence-service/node_modules/@firebase/logger/dist/esm/index.esm5.js
  - ./slack-intelligence-service/node_modules/@firebase/logger/dist/esm/index.esm5.js.map
  - ./slack-intelligence-service/node_modules/@firebase/logger/dist/esm/index.esm2017.js.map
  - ./slack-intelligence-service/node_modules/@firebase/logger/README.md
  - ./slack-intelligence-service/node_modules/@firebase/logger/package.json
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/standalone/package.json
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/index.esm2017.js
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/index.esm5.js
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/test/helpers/util.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.node.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/onDisconnect.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/Reference.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/Database.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/internal.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.standalone.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/index.js
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/index.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/index.standalone.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/test/helpers/util.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/index.node.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/onDisconnect.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/Reference.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/Database.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/internal.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/index.standalone.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/index.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/index.js
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/index.esm5.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/index.standalone.js
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/index.esm2017.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/dist/index.js.map
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/README.md
  - ./slack-intelligence-service/node_modules/@firebase/database-compat/package.json
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/index.cjs.js.map
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/index.cjs.js
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/index.esm2017.js
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/index.esm5.js
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/node-esm/index.node.esm.js.map
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/node-esm/index.node.esm.js
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/node-esm/src/emulator.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/util-public.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/index.node.cjs.js
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/index.esm5.js.map
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/index.esm2017.js.map
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/util.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/index.node.cjs.js.map
  - ./slack-intelligence-service/node_modules/@firebase/util/dist/src/emulator.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/util/README.md
  - ./slack-intelligence-service/node_modules/@firebase/util/package.json
  - ./slack-intelligence-service/node_modules/@firebase/app-check-interop-types/README.md
  - ./slack-intelligence-service/node_modules/@firebase/app-check-interop-types/package.json
  - ./slack-intelligence-service/node_modules/@firebase/app-check-interop-types/index.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/component/dist/index.cjs.js.map
  - ./slack-intelligence-service/node_modules/@firebase/component/dist/index.cjs.js
  - ./slack-intelligence-service/node_modules/@firebase/component/dist/test/util.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/component/dist/esm/index.esm2017.js
  - ./slack-intelligence-service/node_modules/@firebase/component/dist/esm/index.esm5.js
  - ./slack-intelligence-service/node_modules/@firebase/component/dist/esm/test/util.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/component/dist/esm/index.esm5.js.map
  - ./slack-intelligence-service/node_modules/@firebase/component/dist/esm/index.esm2017.js.map
  - ./slack-intelligence-service/node_modules/@firebase/component/dist/esm/src/types.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/component/dist/src/types.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/component/README.md
  - ./slack-intelligence-service/node_modules/@firebase/component/package.json
  - ./slack-intelligence-service/node_modules/@firebase/app-types/private.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/app-types/README.md
  - ./slack-intelligence-service/node_modules/@firebase/app-types/package.json
  - ./slack-intelligence-service/node_modules/@firebase/app-types/index.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/auth-interop-types/README.md
  - ./slack-intelligence-service/node_modules/@firebase/auth-interop-types/package.json
  - ./slack-intelligence-service/node_modules/@firebase/auth-interop-types/index.d.ts
  - ./slack-intelligence-service/node_modules/@firebase/database-types/README.md
  - ./slack-intelligence-service/node_modules/@firebase/database-types/package.json
  - ./slack-intelligence-service/node_modules/@firebase/database-types/index.d.ts
  - ./slack-intelligence-service/node_modules/proto3-json-serializer/LICENSE
  - ./slack-intelligence-service/node_modules/teeny-request/LICENSE
  - ./slack-intelligence-service/node_modules/@grpc/grpc-js/LICENSE
  - ./slack-intelligence-service/node_modules/@grpc/grpc-js/proto/protoc-gen-validate/LICENSE
  - ./slack-intelligence-service/node_modules/@grpc/grpc-js/proto/xds/LICENSE
  - ./slack-intelligence-service/node_modules/@grpc/grpc-js/node_modules/@grpc/proto-loader/LICENSE
  - ./slack-intelligence-service/node_modules/@grpc/proto-loader/LICENSE
  - ./slack-intelligence-service/node_modules/cluster-key-slot/README.md
  - ./slack-intelligence-service/node_modules/cluster-key-slot/package.json
  - ./slack-intelligence-service/node_modules/cluster-key-slot/lib/index.js
  - ./slack-intelligence-service/node_modules/cluster-key-slot/index.d.ts
  - ./slack-intelligence-service/node_modules/google-logging-utils/LICENSE
  - ./slack-intelligence-service/node_modules/readable-stream/CONTRIBUTING.md
  - ./slack-intelligence-service/node_modules/human-signals/LICENSE
  - ./slack-intelligence-service/node_modules/mime-db/db.json
  - ./slack-intelligence-service/package-lock.json
  - ./slack-intelligence-service/package.json
  - ./slack-intelligence-service/src/middleware/auth.ts
  - ./slack-intelligence-service/src/config/firebase.ts
  - ./slack-intelligence-service/src/config/config.ts
  - ./slack-intelligence-service/src/server.ts
  - ./slack-intelligence-service/src/routes/health.ts
  - ./terraform/main.tf
  - ./INTEGRATION_SECRETS_CHECKLIST.md
  - ./project-state.md
  - ./gmail-intelligence-service/dist/firebase.d.ts.map
  - ./gmail-intelligence-service/dist/middleware/auth.js
  - ./gmail-intelligence-service/dist/config/firebase.d.ts.map
  - ./gmail-intelligence-service/dist/config/config.d.ts
  - ./gmail-intelligence-service/dist/config/config.js
  - ./gmail-intelligence-service/dist/config/firebase.js.map
  - ./gmail-intelligence-service/dist/config/firebase.d.ts
  - ./gmail-intelligence-service/dist/config/firebase.js
  - ./gmail-intelligence-service/dist/server.js
  - ./gmail-intelligence-service/dist/config.d.ts
  - ./gmail-intelligence-service/dist/config.js
  - ./gmail-intelligence-service/dist/firebase.js.map
  - ./gmail-intelligence-service/dist/firebase.d.ts
  - ./gmail-intelligence-service/dist/firebase.js
  - ./gmail-intelligence-service/dist/routes/health.js
  - ./gmail-intelligence-service/node_modules/node-forge/LICENSE
  - ./gmail-intelligence-service/node_modules/node-forge/lib/jsbn.js
  - ./gmail-intelligence-service/node_modules/farmhash-modern/bin/nodejs/farmhash_modern.js
  - ./gmail-intelligence-service/node_modules/farmhash-modern/bin/bundler/farmhash_modern_bg.js
  - ./gmail-intelligence-service/node_modules/farmhash-modern/README.md
  - ./gmail-intelligence-service/node_modules/farmhash-modern/package.json
  - ./gmail-intelligence-service/node_modules/farmhash-modern/lib/index.d.mts
  - ./gmail-intelligence-service/node_modules/farmhash-modern/lib/index.d.cts
  - ./gmail-intelligence-service/node_modules/farmhash-modern/lib/index.js
  - ./gmail-intelligence-service/node_modules/farmhash-modern/lib/index.cjs
  - ./gmail-intelligence-service/node_modules/farmhash-modern/lib/index.mjs
  - ./gmail-intelligence-service/node_modules/farmhash-modern/lib/index.d.ts
  - ./gmail-intelligence-service/node_modules/farmhash-modern/lib/browser.js
  - ./gmail-intelligence-service/node_modules/farmhash-modern/lib/browser.d.ts
  - ./gmail-intelligence-service/node_modules/dotenv/README.md
  - ./gmail-intelligence-service/node_modules/@opentelemetry/api/LICENSE
  - ./gmail-intelligence-service/node_modules/express/History.md
  - ./gmail-intelligence-service/node_modules/express/package.json
  - ./gmail-intelligence-service/node_modules/gaxios/LICENSE
  - ./gmail-intelligence-service/node_modules/typescript/lib/typesMap.json
  - ./gmail-intelligence-service/node_modules/typescript/lib/typescript.js
  - ./gmail-intelligence-service/node_modules/typescript/lib/_tsc.js
  - ./gmail-intelligence-service/node_modules/typescript/LICENSE.txt
  - ./gmail-intelligence-service/node_modules/typescript/ThirdPartyNoticeText.txt
  - ./gmail-intelligence-service/node_modules/json-bigint/lib/stringify.js
  - ./gmail-intelligence-service/node_modules/json-bigint/lib/parse.js
  - ./gmail-intelligence-service/node_modules/mime-types/node_modules/mime-db/db.json
  - ./gmail-intelligence-service/node_modules/encoding-japanese/encoding.js
  - ./gmail-intelligence-service/node_modules/encoding-japanese/src/util.js
  - ./gmail-intelligence-service/node_modules/google-auth-library/LICENSE
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/types/firestore.d.ts
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/LICENSE
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/README.md
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/build/src/transaction.js
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/build/src/backoff.js
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/build/src/rate-limiter.d.ts
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/build/src/rate-limiter.js
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/build/src/index.js
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/build/src/bulk-writer.js
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/build/src/bulk-writer.d.ts
  - ./gmail-intelligence-service/node_modules/@google-cloud/firestore/build/src/index.d.ts
  - ./gmail-intelligence-service/node_modules/@google-cloud/promisify/LICENSE
  - ./gmail-intelligence-service/node_modules/@google-cloud/projectify/LICENSE
  - ./gmail-intelligence-service/node_modules/@google-cloud/storage/LICENSE
  - ./gmail-intelligence-service/node_modules/@google-cloud/paginator/LICENSE
  - ./gmail-intelligence-service/node_modules/.package-lock.json
  - ./gmail-intelligence-service/node_modules/long/LICENSE
  - ./gmail-intelligence-service/node_modules/ecdsa-sig-formatter/LICENSE
  - ./gmail-intelligence-service/node_modules/firebase-admin/LICENSE
  - ./gmail-intelligence-service/node_modules/firebase-admin/CHANGELOG.md
  - ./gmail-intelligence-service/node_modules/firebase-admin/node_modules/@types/node/sqlite.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/node_modules/@types/node/process.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/node_modules/@types/node/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/node_modules/@types/node/ts5.6/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/README.md
  - ./gmail-intelligence-service/node_modules/firebase-admin/package.json
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/database/database.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/database/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/database/database-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/database/database.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/database/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/database/database-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/credential/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/credential/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/default-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/credential-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/core.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/credential-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/lifecycle.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/credential.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/firebase-app.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/credential-factory.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/core.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/firebase-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/firebase-app.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/credential.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/credential-factory.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/firebase-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app/lifecycle.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/firestore/firestore-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/firestore/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/firestore/firestore-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/firestore/firestore-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/firestore/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/firestore/firestore-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/token-verifier.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/token-verifier.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/project-config.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/tenant-manager.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/auth-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/auth-config.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/tenant.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/project-config-manager.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/base-auth.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/auth.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/action-code-settings-builder.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/project-config-manager.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/token-generator.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/user-record.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/tenant.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/user-record.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/tenant-manager.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/identifier.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/auth-api-request.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/auth-config.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/auth-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/auth-api-request.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/project-config.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/auth.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/token-generator.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/action-code-settings-builder.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/base-auth.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/user-import-builder.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/identifier.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/auth/user-import-builder.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/app-metadata.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management-api-request-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/android-app.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/ios-app.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/ios-app.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management-api-request-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/app-metadata.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/android-app.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/project-management/project-management-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/jwt.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/error.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/crypto-signer.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/api-request.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/validator.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/crypto-signer.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/error.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/deep-copy.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/validator.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/jwt.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/deep-copy.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/utils/api-request.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/token-verifier.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/token-verifier.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-api-client-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-api.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/token-generator.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-api-client-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check-api.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/token-generator.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/app-check/app-check.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-api.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/condition-evaluator-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/internal/value-impl.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/internal/value-impl.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-api-client-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/condition-evaluator-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-api.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/remote-config/remote-config-api-client-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/firebase-namespace-api.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/storage/storage-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/storage/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/storage/utils.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/storage/storage-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/storage/utils.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/storage/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/storage/storage.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/storage/storage.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/extensions/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions-api.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions-api-client-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions-api.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions-api-client-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/extensions/extensions.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/extensions/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/installations/installations-request-handler.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/installations/installations-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/installations/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/installations/installations-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/installations/installations.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/installations/installations-request-handler.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/installations/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/installations/installations.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/default-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/instance-id/instance-id-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/instance-id/instance-id.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/instance-id/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/instance-id/instance-id.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/instance-id/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/instance-id/instance-id-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/firebase-namespace-api.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc-utils.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/eventarc/cloudevent.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/eventarc/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc-client-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc-utils.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/eventarc/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/eventarc/eventarc-client-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/eventarc/cloudevent.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/functions/functions.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/functions/functions-api-client-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/functions/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/functions/functions-api.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/functions/functions-api.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/functions/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/functions/functions.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/functions/functions-api-client-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect-api-client-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect-api.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/data-connect/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect-api.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/data-connect/data-connect-api-client-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/data-connect/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-utils.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/machine-learning/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-utils.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-api-client.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-api-client.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/machine-learning/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/batch-request-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/batch-request-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-errors-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-api-request-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-api-request-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-errors-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-api.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/messaging/messaging-api.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-namespace.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-api-client-internal.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/security-rules/index.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-namespace.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-api-client-internal.js
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/security-rules/index.d.ts
  - ./gmail-intelligence-service/node_modules/firebase-admin/lib/security-rules/security-rules-internal.js
  - ./gmail-intelligence-service/node_modules/gcp-metadata/LICENSE
  - ./gmail-intelligence-service/node_modules/googleapis/LICENSE
  - ./gmail-intelligence-service/node_modules/googleapis/CHANGELOG.md
  - ./gmail-intelligence-service/node_modules/googleapis/README.md
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/billingbudgets/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/billingbudgets/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/dataflow/v1b3.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/cloudfunctions/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/cloudfunctions/v1beta2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/datastream/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/datastream/v1alpha1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasedynamiclinks/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasedynamiclinks/v1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasedynamiclinks/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasedynamiclinks/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/aiplatform/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/aiplatform/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/sqladmin/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/sqladmin/v1beta4.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/discoveryengine/v1beta.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/discoveryengine/v1alpha.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/sheets/v4.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/identitytoolkit/v2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/securitycenter/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/securitycenter/v1beta2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/securitycenter/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/redis/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/redis/v1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/redis/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/redis/v1beta1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/redis/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/redis/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/dataplex/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/analyticshub/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/analyticshub/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/accessapproval/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/accessapproval/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/healthcare/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/healthcare/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryconnection/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryconnection/v1beta1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryconnection/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryconnection/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/fcmdata/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasedatabase/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasedatabase/v1beta.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasedatabase/v1beta.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasedatabase/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseappdistribution/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseappdistribution/v1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseappdistribution/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseappdistribution/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryreservation/v1alpha2.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryreservation/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryreservation/v1alpha2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryreservation/v1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryreservation/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryreservation/v1beta1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryreservation/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigqueryreservation/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/retail/v2alpha.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/retail/v2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/retail/v2beta.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigquery/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigquery/v2.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigquery/v2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigquery/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseappcheck/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseappcheck/v1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseappcheck/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseappcheck/v1beta.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseappcheck/v1beta.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseappcheck/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasehosting/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasehosting/v1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasehosting/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasehosting/v1beta1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasehosting/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasehosting/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/datamigration/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/datamigration/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/testing/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/container/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/container/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/cloudtrace/v2beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebase/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebase/v1beta1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebase/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebase/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/cloudasset/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/cloudasset/v1p7beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/compute/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/compute/beta.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/compute/alpha.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/ml/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/contentwarehouse/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/analyticsadmin/v1alpha.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/analyticsadmin/v1beta.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/analyticsadmin/v1beta.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/analyticsadmin/v1alpha.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/fcm/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasestorage/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasestorage/v1beta.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasestorage/v1beta.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebasestorage/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/servicecontrol/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/servicecontrol/v2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/datalabeling/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/dlp/v2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/pubsub/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/alloydb/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/alloydb/v1beta.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/alloydb/v1alpha.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseml/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseml/v1beta2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseml/v1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseml/v1beta2.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseml/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaseml/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/run/v2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/dataform/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/logging/v2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigquerydatatransfer/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigquerydatatransfer/v1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigquerydatatransfer/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/bigquerydatatransfer/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/datacatalog/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/datacatalog/v1beta1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/analytics/v3.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaserules/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaserules/v1.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaserules/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/firebaserules/index.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/dataproc/v1.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/dataproc/v1beta2.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/apis/sql/v1beta4.d.ts
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/index.js
  - ./gmail-intelligence-service/node_modules/googleapis/build/src/index.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/index.cjs.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/index.cjs.js
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/index.esm2017.js
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/index.esm5.js
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/index.node.esm.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/test/exp/integration.test.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/test/helpers/syncpoint-util.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/index.node.esm.js
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/core/AuthTokenProvider.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/core/util/validation.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/core/storage/DOMStorageWrapper.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/core/AppCheckTokenProvider.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/core/view/EventRegistration.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/internal/index.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/api/OnDisconnect.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/api/Reference.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/api/Database.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/api/Reference_impl.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/node-esm/src/index.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/index.standalone.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/test/exp/integration.test.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/test/helpers/syncpoint-util.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/index.node.cjs.js
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/private.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/index.esm5.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/index.standalone.js
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/index.esm2017.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/public.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/internal.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/index.node.cjs.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/core/AuthTokenProvider.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/core/util/validation.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/core/storage/DOMStorageWrapper.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/core/AppCheckTokenProvider.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/core/view/EventRegistration.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/internal/index.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/api/OnDisconnect.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/api/Reference.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/api/Database.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/api/Reference_impl.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/dist/src/index.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database/README.md
  - ./gmail-intelligence-service/node_modules/@firebase/database/package.json
  - ./gmail-intelligence-service/node_modules/@firebase/logger/dist/index.cjs.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/logger/dist/index.cjs.js
  - ./gmail-intelligence-service/node_modules/@firebase/logger/dist/esm/index.esm2017.js
  - ./gmail-intelligence-service/node_modules/@firebase/logger/dist/esm/index.esm5.js
  - ./gmail-intelligence-service/node_modules/@firebase/logger/dist/esm/index.esm5.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/logger/dist/esm/index.esm2017.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/logger/README.md
  - ./gmail-intelligence-service/node_modules/@firebase/logger/package.json
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/standalone/package.json
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/index.esm2017.js
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/index.esm5.js
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/test/helpers/util.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.node.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/onDisconnect.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/Reference.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/Database.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/internal.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.standalone.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/index.js
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/node-esm/index.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/index.standalone.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/test/helpers/util.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/index.node.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/onDisconnect.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/Reference.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/Database.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/internal.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/index.standalone.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/database-compat/src/index.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/index.js
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/index.esm5.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/index.standalone.js
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/index.esm2017.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/dist/index.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/README.md
  - ./gmail-intelligence-service/node_modules/@firebase/database-compat/package.json
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/index.cjs.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/index.cjs.js
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/index.esm2017.js
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/index.esm5.js
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/node-esm/index.node.esm.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/node-esm/index.node.esm.js
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/node-esm/src/emulator.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/util-public.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/index.node.cjs.js
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/index.esm5.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/index.esm2017.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/util.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/index.node.cjs.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/util/dist/src/emulator.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/util/README.md
  - ./gmail-intelligence-service/node_modules/@firebase/util/package.json
  - ./gmail-intelligence-service/node_modules/@firebase/app-check-interop-types/README.md
  - ./gmail-intelligence-service/node_modules/@firebase/app-check-interop-types/package.json
  - ./gmail-intelligence-service/node_modules/@firebase/app-check-interop-types/index.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/component/dist/index.cjs.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/component/dist/index.cjs.js
  - ./gmail-intelligence-service/node_modules/@firebase/component/dist/test/util.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/component/dist/esm/index.esm2017.js
  - ./gmail-intelligence-service/node_modules/@firebase/component/dist/esm/index.esm5.js
  - ./gmail-intelligence-service/node_modules/@firebase/component/dist/esm/test/util.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/component/dist/esm/index.esm5.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/component/dist/esm/index.esm2017.js.map
  - ./gmail-intelligence-service/node_modules/@firebase/component/dist/esm/src/types.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/component/dist/src/types.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/component/README.md
  - ./gmail-intelligence-service/node_modules/@firebase/component/package.json
  - ./gmail-intelligence-service/node_modules/@firebase/app-types/private.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/app-types/README.md
  - ./gmail-intelligence-service/node_modules/@firebase/app-types/package.json
  - ./gmail-intelligence-service/node_modules/@firebase/app-types/index.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/auth-interop-types/README.md
  - ./gmail-intelligence-service/node_modules/@firebase/auth-interop-types/package.json
  - ./gmail-intelligence-service/node_modules/@firebase/auth-interop-types/index.d.ts
  - ./gmail-intelligence-service/node_modules/@firebase/database-types/README.md
  - ./gmail-intelligence-service/node_modules/@firebase/database-types/package.json
  - ./gmail-intelligence-service/node_modules/@firebase/database-types/index.d.ts
  - ./gmail-intelligence-service/node_modules/proto3-json-serializer/LICENSE
  - ./gmail-intelligence-service/node_modules/teeny-request/LICENSE
  - ./gmail-intelligence-service/node_modules/googleapis-common/LICENSE
  - ./gmail-intelligence-service/node_modules/@grpc/grpc-js/LICENSE
  - ./gmail-intelligence-service/node_modules/@grpc/grpc-js/proto/protoc-gen-validate/LICENSE
  - ./gmail-intelligence-service/node_modules/@grpc/grpc-js/proto/xds/LICENSE
  - ./gmail-intelligence-service/node_modules/@grpc/grpc-js/node_modules/@grpc/proto-loader/LICENSE
  - ./gmail-intelligence-service/node_modules/@grpc/proto-loader/LICENSE
  - ./gmail-intelligence-service/node_modules/google-logging-utils/LICENSE
  - ./gmail-intelligence-service/node_modules/readable-stream/CONTRIBUTING.md
  - ./gmail-intelligence-service/node_modules/mime-db/db.json
  - ./gmail-intelligence-service/package-lock.json
  - ./gmail-intelligence-service/package.json
  - ./gmail-intelligence-service/src/middleware/auth.ts
  - ./gmail-intelligence-service/src/config/firebase.ts
  - ./gmail-intelligence-service/src/config/config.ts
  - ./gmail-intelligence-service/src/firebase.ts
  - ./gmail-intelligence-service/src/config.ts
  - ./gmail-intelligence-service/src/server.ts
  - ./gmail-intelligence-service/src/routes/health.ts
  - ./analytics-data-layer/requirements.txt
  - ./analytics-data-layer/main.py
  - ./.env.production
  - ./business-entity-service/package-lock.json
  - ./business-entity-service/package.json
  - ./business-entity-service/src/server.ts
  - ./business-entity-service/src/services/entityService.ts
  - ./business-entity-service/src/services/userService.ts
  - ./business-entity-service/src/services/continuumService.ts
  - ./setup_infrastructure.sh
  - ./performance-scaling/requirements.txt
  - ./performance-scaling/shared/tenant_utils.py
  - ./performance-scaling/main.py
  - ./content-hub/main.py
  - ./JWT_AUTH_COMPLETE.md
  - ./ARCHITECTURE.md
  - ./xynergyos-intelligence-gateway/dist/middleware/auth.js
  - ./xynergyos-intelligence-gateway/dist/config/firebase.d.ts.map
  - ./xynergyos-intelligence-gateway/dist/config/config.d.ts
  - ./xynergyos-intelligence-gateway/dist/config/config.js
  - ./xynergyos-intelligence-gateway/dist/config/firebase.js.map
  - ./xynergyos-intelligence-gateway/dist/config/firebase.d.ts
  - ./xynergyos-intelligence-gateway/dist/config/firebase.js
  - ./xynergyos-intelligence-gateway/dist/server.js
  - ./xynergyos-intelligence-gateway/dist/routes/health.js
  - ./xynergyos-intelligence-gateway/dist/services/cacheService.js
  - ./xynergyos-intelligence-gateway/dist/services/websocket.d.ts
  - ./xynergyos-intelligence-gateway/dist/services/websocket.js
  - ./xynergyos-intelligence-gateway/dist/services/cacheService.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/node-forge/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/node-forge/lib/jsbn.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/MREVRANGE_WITHLABELS.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/MREVRANGE.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/GET.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/INCRBY.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/DECRBY.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/MGET.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/RANGE.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/index.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/DEL.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/QUERYINDEX.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/REVRANGE.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/QUERYINDEX.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/MGET_WITHLABELS.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/MRANGE.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/dist/commands/MRANGE_WITHLABELS.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@redis/time-series/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@redis/graph/dist/graph.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/graph/dist/commands/QUERY.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/graph/dist/commands/RO_QUERY.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/graph/dist/commands/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/graph/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@redis/graph/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/top-k/QUERY.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/top-k/QUERY.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/top-k/ADD.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/top-k/COUNT.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/top-k/COUNT.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/top-k/ADD.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/BYRANK.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/MERGE.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/CDF.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/MIN.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/MAX.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/TRIMMED_MEAN.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/QUANTILE.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/BYREVRANK.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/CREATE.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/ADD.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/INFO.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/RANK.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/MERGE.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/RESET.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/t-digest/REVRANK.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/LOADCHUNK.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/MADD.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/MEXISTS.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/EXISTS.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/ADD.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/MEXISTS.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/ADD.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/MADD.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/INSERT.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/EXISTS.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/bloom/INSERT.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/ADDNX.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/INSERTNX.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/LOADCHUNK.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/DEL.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/INSERTNX.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/EXISTS.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/index.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/ADD.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/DEL.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/ADDNX.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/ADD.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/INSERT.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/EXISTS.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/cuckoo/INSERT.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/count-min-sketch/QUERY.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/dist/commands/count-min-sketch/QUERY.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@redis/bloom/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/DICTDEL.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/SYNUPDATE.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/DICTADD.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/SEARCH.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/AGGREGATE.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/DICTADD.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/index.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/CREATE.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/SUGDEL.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/DICTDEL.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/INFO.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/AGGREGATE.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/CURSOR_READ.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/CURSOR_DEL.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/PROFILE_SEARCH.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/INFO.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/SYNUPDATE.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/SEARCH_NOCONTENT.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/AGGREGATE_WITHCURSOR.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/dist/commands/SUGDEL.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@redis/search/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@redis/json/dist/commands/MSET.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/json/dist/commands/GET.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/json/dist/commands/GET.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/json/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@redis/json/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/cluster/cluster-slots.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/cluster/index.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/cluster/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/cluster/cluster-slots.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/commands/GEOSEARCHSTORE.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/commands/generic-transformers.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/commands/CLUSTER_NODES.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/commands/ZRANGESTORE.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/client/pub-sub.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/client/index.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/client/RESP2/decoder.js
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/dist/lib/client/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@redis/client/package.json
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/bin/nodejs/farmhash_modern.js
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/bin/bundler/farmhash_modern_bg.js
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/README.md
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/package.json
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/lib/index.d.mts
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/lib/index.d.cts
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/lib/index.js
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/lib/index.cjs
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/lib/index.mjs
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/lib/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/lib/browser.js
  - ./xynergyos-intelligence-gateway/node_modules/farmhash-modern/lib/browser.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/dotenv/README.md
  - ./xynergyos-intelligence-gateway/node_modules/resolve/lib/core.json
  - ./xynergyos-intelligence-gateway/node_modules/@opentelemetry/api/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/express/History.md
  - ./xynergyos-intelligence-gateway/node_modules/express/package.json
  - ./xynergyos-intelligence-gateway/node_modules/redis/dist/index.js
  - ./xynergyos-intelligence-gateway/node_modules/redis/dist/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/redis/README.md
  - ./xynergyos-intelligence-gateway/node_modules/redis/package.json
  - ./xynergyos-intelligence-gateway/node_modules/prettier/THIRD-PARTY-NOTICES.md
  - ./xynergyos-intelligence-gateway/node_modules/prettier/plugins/typescript.js
  - ./xynergyos-intelligence-gateway/node_modules/prettier/plugins/yaml.mjs
  - ./xynergyos-intelligence-gateway/node_modules/prettier/plugins/typescript.mjs
  - ./xynergyos-intelligence-gateway/node_modules/prettier/plugins/yaml.js
  - ./xynergyos-intelligence-gateway/node_modules/prettier/index.mjs
  - ./xynergyos-intelligence-gateway/node_modules/gaxios/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/socket.io-adapter/Readme.md
  - ./xynergyos-intelligence-gateway/node_modules/typescript/lib/typesMap.json
  - ./xynergyos-intelligence-gateway/node_modules/typescript/lib/typescript.js
  - ./xynergyos-intelligence-gateway/node_modules/typescript/lib/_tsc.js
  - ./xynergyos-intelligence-gateway/node_modules/typescript/LICENSE.txt
  - ./xynergyos-intelligence-gateway/node_modules/typescript/ThirdPartyNoticeText.txt
  - ./xynergyos-intelligence-gateway/node_modules/baseline-browser-mapping/LICENSE.txt
  - ./xynergyos-intelligence-gateway/node_modules/json-bigint/lib/stringify.js
  - ./xynergyos-intelligence-gateway/node_modules/json-bigint/lib/parse.js
  - ./xynergyos-intelligence-gateway/node_modules/@socket.io/redis-adapter/dist/sharded-adapter.js
  - ./xynergyos-intelligence-gateway/node_modules/@socket.io/redis-adapter/dist/util.js
  - ./xynergyos-intelligence-gateway/node_modules/@socket.io/redis-adapter/dist/index.js
  - ./xynergyos-intelligence-gateway/node_modules/@socket.io/redis-adapter/dist/sharded-adapter.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@socket.io/redis-adapter/dist/util.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@socket.io/redis-adapter/dist/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@socket.io/redis-adapter/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@socket.io/redis-adapter/package.json
  - ./xynergyos-intelligence-gateway/node_modules/keyv/README.md
  - ./xynergyos-intelligence-gateway/node_modules/keyv/package.json
  - ./xynergyos-intelligence-gateway/node_modules/keyv/src/index.js
  - ./xynergyos-intelligence-gateway/node_modules/keyv/src/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/eslint-visitor-keys/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@humanwhocodes/config-array/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@humanwhocodes/module-importer/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/mime-types/node_modules/mime-db/db.json
  - ./xynergyos-intelligence-gateway/node_modules/google-auth-library/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/types/firestore.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/build/src/transaction.js
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/build/src/backoff.js
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/build/src/rate-limiter.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/build/src/rate-limiter.js
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/build/src/index.js
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/build/src/bulk-writer.js
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/build/src/bulk-writer.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/firestore/build/src/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/promisify/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/projectify/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/storage/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@google-cloud/paginator/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/.package-lock.json
  - ./xynergyos-intelligence-gateway/node_modules/long/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/doctrine/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/doctrine/LICENSE.closure-compiler
  - ./xynergyos-intelligence-gateway/node_modules/ecdsa-sig-formatter/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/is-core-module/test/index.js
  - ./xynergyos-intelligence-gateway/node_modules/is-core-module/CHANGELOG.md
  - ./xynergyos-intelligence-gateway/node_modules/is-core-module/core.json
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/CHANGELOG.md
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/node_modules/@types/node/sqlite.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/node_modules/@types/node/process.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/node_modules/@types/node/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/node_modules/@types/node/ts5.6/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/README.md
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/package.json
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/database/database.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/database/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/database/database-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/database/database.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/database/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/database/database-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/credential/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/credential/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/default-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/credential-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/core.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/credential-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/lifecycle.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/credential.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/firebase-app.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/credential-factory.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/core.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/firebase-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/firebase-app.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/credential.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/credential-factory.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/firebase-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app/lifecycle.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/firestore/firestore-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/firestore/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/firestore/firestore-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/firestore/firestore-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/firestore/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/firestore/firestore-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/token-verifier.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/token-verifier.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/project-config.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/tenant-manager.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/auth-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/auth-config.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/tenant.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/project-config-manager.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/base-auth.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/auth.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/action-code-settings-builder.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/project-config-manager.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/token-generator.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/user-record.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/tenant.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/user-record.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/tenant-manager.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/identifier.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/auth-api-request.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/auth-config.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/auth-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/auth-api-request.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/project-config.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/auth.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/token-generator.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/action-code-settings-builder.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/base-auth.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/user-import-builder.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/identifier.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/auth/user-import-builder.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/app-metadata.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/project-management-api-request-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/project-management-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/android-app.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/project-management.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/ios-app.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/ios-app.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/project-management-api-request-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/project-management.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/app-metadata.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/android-app.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/project-management/project-management-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/jwt.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/error.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/crypto-signer.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/api-request.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/validator.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/crypto-signer.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/error.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/deep-copy.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/validator.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/jwt.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/deep-copy.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/utils/api-request.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/token-verifier.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/token-verifier.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/app-check-api-client-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/app-check-api.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/token-generator.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/app-check-api-client-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/app-check-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/app-check-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/app-check.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/app-check-api.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/token-generator.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/app-check/app-check.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/remote-config-api.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/remote-config-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/remote-config.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/condition-evaluator-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/internal/value-impl.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/internal/value-impl.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/remote-config-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/remote-config-api-client-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/condition-evaluator-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/remote-config.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/remote-config-api.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/remote-config/remote-config-api-client-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/firebase-namespace-api.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/storage/storage-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/storage/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/storage/utils.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/storage/storage-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/storage/utils.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/storage/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/storage/storage.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/storage/storage.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/extensions/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/extensions/extensions.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/extensions/extensions-api.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/extensions/extensions-api-client-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/extensions/extensions-api.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/extensions/extensions-api-client-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/extensions/extensions.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/extensions/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/installations/installations-request-handler.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/installations/installations-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/installations/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/installations/installations-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/installations/installations.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/installations/installations-request-handler.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/installations/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/installations/installations.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/default-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/instance-id/instance-id-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/instance-id/instance-id.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/instance-id/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/instance-id/instance-id.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/instance-id/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/instance-id/instance-id-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/firebase-namespace-api.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/eventarc/eventarc-utils.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/eventarc/cloudevent.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/eventarc/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/eventarc/eventarc.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/eventarc/eventarc-client-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/eventarc/eventarc.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/eventarc/eventarc-utils.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/eventarc/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/eventarc/eventarc-client-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/eventarc/cloudevent.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/functions/functions.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/functions/functions-api-client-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/functions/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/functions/functions-api.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/functions/functions-api.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/functions/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/functions/functions.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/functions/functions-api-client-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/data-connect/data-connect-api-client-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/data-connect/data-connect.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/data-connect/data-connect-api.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/data-connect/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/data-connect/data-connect-api.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/data-connect/data-connect.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/data-connect/data-connect-api-client-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/data-connect/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/machine-learning/machine-learning-utils.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/machine-learning/machine-learning.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/machine-learning/machine-learning-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/machine-learning/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/machine-learning/machine-learning-utils.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/machine-learning/machine-learning.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/machine-learning/machine-learning-api-client.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/machine-learning/machine-learning-api-client.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/machine-learning/machine-learning-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/machine-learning/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/batch-request-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/batch-request-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging-errors-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging-api-request-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging-api-request-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging-errors-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging-api.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/messaging/messaging-api.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/security-rules/security-rules-namespace.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/security-rules/security-rules.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/security-rules/security-rules-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/security-rules/security-rules-api-client-internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/security-rules/index.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/security-rules/security-rules-namespace.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/security-rules/security-rules.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/security-rules/security-rules-api-client-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/security-rules/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/firebase-admin/lib/security-rules/security-rules-internal.js
  - ./xynergyos-intelligence-gateway/node_modules/gcp-metadata/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/index.cjs.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/index.cjs.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/index.esm2017.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/index.esm5.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/index.node.esm.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/test/exp/integration.test.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/test/helpers/syncpoint-util.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/index.node.esm.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/core/AuthTokenProvider.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/core/util/validation.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/core/storage/DOMStorageWrapper.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/core/AppCheckTokenProvider.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/core/view/EventRegistration.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/internal/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/api/OnDisconnect.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/api/Reference.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/api/Database.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/api/Reference_impl.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/node-esm/src/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/index.standalone.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/test/exp/integration.test.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/test/helpers/syncpoint-util.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/index.node.cjs.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/private.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/index.esm5.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/index.standalone.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/index.esm2017.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/public.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/index.node.cjs.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/core/AuthTokenProvider.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/core/util/validation.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/core/storage/DOMStorageWrapper.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/core/AppCheckTokenProvider.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/core/view/EventRegistration.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/internal/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/api/OnDisconnect.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/api/Reference.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/api/Database.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/api/Reference_impl.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/dist/src/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/logger/dist/index.cjs.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/logger/dist/index.cjs.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/logger/dist/esm/index.esm2017.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/logger/dist/esm/index.esm5.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/logger/dist/esm/index.esm5.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/logger/dist/esm/index.esm2017.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/logger/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/logger/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/standalone/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/index.esm2017.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/index.esm5.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/node-esm/database-compat/test/helpers/util.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.node.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/onDisconnect.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/Reference.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/Database.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.standalone.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/node-esm/index.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/node-esm/index.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/index.standalone.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/database-compat/test/helpers/util.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/database-compat/src/index.node.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/database-compat/src/api/onDisconnect.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/database-compat/src/api/Reference.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/database-compat/src/api/Database.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/database-compat/src/api/internal.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/database-compat/src/index.standalone.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/database-compat/src/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/index.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/index.esm5.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/index.standalone.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/index.esm2017.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/dist/index.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-compat/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/index.cjs.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/index.cjs.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/index.esm2017.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/index.esm5.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/node-esm/index.node.esm.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/node-esm/index.node.esm.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/node-esm/src/emulator.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/util-public.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/index.node.cjs.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/index.esm5.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/index.esm2017.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/util.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/index.node.cjs.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/dist/src/emulator.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/util/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/app-check-interop-types/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/app-check-interop-types/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/app-check-interop-types/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/dist/index.cjs.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/dist/index.cjs.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/dist/test/util.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/dist/esm/index.esm2017.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/dist/esm/index.esm5.js
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/dist/esm/test/util.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/dist/esm/index.esm5.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/dist/esm/index.esm2017.js.map
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/dist/esm/src/types.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/dist/src/types.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/component/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/app-types/private.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/app-types/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/app-types/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/app-types/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/auth-interop-types/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/auth-interop-types/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/auth-interop-types/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-types/README.md
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-types/package.json
  - ./xynergyos-intelligence-gateway/node_modules/@firebase/database-types/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/proto3-json-serializer/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/teeny-request/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@grpc/grpc-js/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@grpc/grpc-js/proto/protoc-gen-validate/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@grpc/grpc-js/proto/xds/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@grpc/grpc-js/node_modules/@grpc/proto-loader/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/@grpc/proto-loader/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/cluster-key-slot/README.md
  - ./xynergyos-intelligence-gateway/node_modules/cluster-key-slot/package.json
  - ./xynergyos-intelligence-gateway/node_modules/cluster-key-slot/lib/index.js
  - ./xynergyos-intelligence-gateway/node_modules/cluster-key-slot/index.d.ts
  - ./xynergyos-intelligence-gateway/node_modules/google-logging-utils/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/readable-stream/CONTRIBUTING.md
  - ./xynergyos-intelligence-gateway/node_modules/human-signals/LICENSE
  - ./xynergyos-intelligence-gateway/node_modules/mime-db/db.json
  - ./xynergyos-intelligence-gateway/tests/websocket-test-client.ts
  - ./xynergyos-intelligence-gateway/IMPLEMENTATION_COMPLETE_SUMMARY.md
  - ./xynergyos-intelligence-gateway/README.md
  - ./xynergyos-intelligence-gateway/package-lock.json
  - ./xynergyos-intelligence-gateway/package.json
  - ./xynergyos-intelligence-gateway/src/middleware/tenantEnforcement.ts
  - ./xynergyos-intelligence-gateway/src/middleware/checkPermission.ts
  - ./xynergyos-intelligence-gateway/src/middleware/auth.ts
  - ./xynergyos-intelligence-gateway/src/config/firebase.ts
  - ./xynergyos-intelligence-gateway/src/config/config.ts
  - ./xynergyos-intelligence-gateway/src/server.ts
  - ./xynergyos-intelligence-gateway/src/routes/health.ts
  - ./xynergyos-intelligence-gateway/src/services/websocket.ts
  - ./xynergyos-intelligence-gateway/src/services/cacheService.ts
  - ./crm-engine/dist/middleware/auth.js
  - ./crm-engine/dist/config/firebase.d.ts.map
  - ./crm-engine/dist/config/config.d.ts
  - ./crm-engine/dist/config/config.js
  - ./crm-engine/dist/config/firebase.js.map
  - ./crm-engine/dist/config/firebase.d.ts
  - ./crm-engine/dist/config/firebase.js
  - ./crm-engine/dist/server.js
  - ./crm-engine/dist/routes/health.js
  - ./crm-engine/dist/services/crmService.js
  - ./crm-engine/node_modules/node-forge/LICENSE
  - ./crm-engine/node_modules/node-forge/lib/jsbn.js
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/MREVRANGE_WITHLABELS.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/MREVRANGE.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/GET.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/INCRBY.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/DECRBY.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/MGET.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/RANGE.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/index.js
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/DEL.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/QUERYINDEX.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/REVRANGE.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/QUERYINDEX.js
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/MGET_WITHLABELS.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/index.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/MRANGE.d.ts
  - ./crm-engine/node_modules/@redis/time-series/dist/commands/MRANGE_WITHLABELS.d.ts
  - ./crm-engine/node_modules/@redis/time-series/README.md
  - ./crm-engine/node_modules/@redis/time-series/package.json
  - ./crm-engine/node_modules/@redis/graph/dist/graph.d.ts
  - ./crm-engine/node_modules/@redis/graph/dist/commands/QUERY.d.ts
  - ./crm-engine/node_modules/@redis/graph/dist/commands/RO_QUERY.d.ts
  - ./crm-engine/node_modules/@redis/graph/dist/commands/index.d.ts
  - ./crm-engine/node_modules/@redis/graph/README.md
  - ./crm-engine/node_modules/@redis/graph/package.json
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/top-k/QUERY.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/top-k/QUERY.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/top-k/ADD.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/top-k/COUNT.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/top-k/COUNT.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/top-k/ADD.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/BYRANK.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/MERGE.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/CDF.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/MIN.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/MAX.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/TRIMMED_MEAN.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/QUANTILE.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/BYREVRANK.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/CREATE.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/ADD.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/INFO.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/RANK.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/index.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/MERGE.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/RESET.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/t-digest/REVRANK.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/LOADCHUNK.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/MADD.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/MEXISTS.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/EXISTS.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/ADD.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/MEXISTS.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/ADD.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/MADD.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/INSERT.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/EXISTS.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/bloom/INSERT.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/ADDNX.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/INSERTNX.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/LOADCHUNK.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/DEL.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/INSERTNX.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/EXISTS.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/index.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/ADD.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/DEL.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/ADDNX.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/ADD.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/index.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/INSERT.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/EXISTS.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/cuckoo/INSERT.js
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/count-min-sketch/QUERY.d.ts
  - ./crm-engine/node_modules/@redis/bloom/dist/commands/count-min-sketch/QUERY.js
  - ./crm-engine/node_modules/@redis/bloom/README.md
  - ./crm-engine/node_modules/@redis/bloom/package.json
  - ./crm-engine/node_modules/@redis/search/dist/commands/DICTDEL.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/SYNUPDATE.js
  - ./crm-engine/node_modules/@redis/search/dist/commands/DICTADD.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/SEARCH.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/AGGREGATE.js
  - ./crm-engine/node_modules/@redis/search/dist/commands/DICTADD.js
  - ./crm-engine/node_modules/@redis/search/dist/commands/index.js
  - ./crm-engine/node_modules/@redis/search/dist/commands/CREATE.js
  - ./crm-engine/node_modules/@redis/search/dist/commands/SUGDEL.js
  - ./crm-engine/node_modules/@redis/search/dist/commands/DICTDEL.js
  - ./crm-engine/node_modules/@redis/search/dist/commands/INFO.js
  - ./crm-engine/node_modules/@redis/search/dist/commands/AGGREGATE.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/CURSOR_READ.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/CURSOR_DEL.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/PROFILE_SEARCH.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/INFO.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/SYNUPDATE.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/SEARCH_NOCONTENT.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/index.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/AGGREGATE_WITHCURSOR.d.ts
  - ./crm-engine/node_modules/@redis/search/dist/commands/SUGDEL.d.ts
  - ./crm-engine/node_modules/@redis/search/README.md
  - ./crm-engine/node_modules/@redis/search/package.json
  - ./crm-engine/node_modules/@redis/json/dist/commands/MSET.d.ts
  - ./crm-engine/node_modules/@redis/json/dist/commands/GET.d.ts
  - ./crm-engine/node_modules/@redis/json/dist/commands/GET.js
  - ./crm-engine/node_modules/@redis/json/README.md
  - ./crm-engine/node_modules/@redis/json/package.json
  - ./crm-engine/node_modules/@redis/client/dist/package.json
  - ./crm-engine/node_modules/@redis/client/dist/lib/cluster/cluster-slots.d.ts
  - ./crm-engine/node_modules/@redis/client/dist/lib/cluster/index.js
  - ./crm-engine/node_modules/@redis/client/dist/lib/cluster/index.d.ts
  - ./crm-engine/node_modules/@redis/client/dist/lib/cluster/cluster-slots.js
  - ./crm-engine/node_modules/@redis/client/dist/lib/commands/GEOSEARCHSTORE.js
  - ./crm-engine/node_modules/@redis/client/dist/lib/commands/generic-transformers.js
  - ./crm-engine/node_modules/@redis/client/dist/lib/commands/CLUSTER_NODES.js
  - ./crm-engine/node_modules/@redis/client/dist/lib/commands/ZRANGESTORE.js
  - ./crm-engine/node_modules/@redis/client/dist/lib/client/pub-sub.js
  - ./crm-engine/node_modules/@redis/client/dist/lib/client/index.js
  - ./crm-engine/node_modules/@redis/client/dist/lib/client/RESP2/decoder.js
  - ./crm-engine/node_modules/@redis/client/dist/lib/client/index.d.ts
  - ./crm-engine/node_modules/@redis/client/README.md
  - ./crm-engine/node_modules/@redis/client/package.json
  - ./crm-engine/node_modules/farmhash-modern/bin/nodejs/farmhash_modern.js
  - ./crm-engine/node_modules/farmhash-modern/bin/bundler/farmhash_modern_bg.js
  - ./crm-engine/node_modules/farmhash-modern/README.md
  - ./crm-engine/node_modules/farmhash-modern/package.json
  - ./crm-engine/node_modules/farmhash-modern/lib/index.d.mts
  - ./crm-engine/node_modules/farmhash-modern/lib/index.d.cts
  - ./crm-engine/node_modules/farmhash-modern/lib/index.js
  - ./crm-engine/node_modules/farmhash-modern/lib/index.cjs
  - ./crm-engine/node_modules/farmhash-modern/lib/index.mjs
  - ./crm-engine/node_modules/farmhash-modern/lib/index.d.ts
  - ./crm-engine/node_modules/farmhash-modern/lib/browser.js
  - ./crm-engine/node_modules/farmhash-modern/lib/browser.d.ts
  - ./crm-engine/node_modules/dotenv/README.md
  - ./crm-engine/node_modules/resolve/lib/core.json
  - ./crm-engine/node_modules/@opentelemetry/api/LICENSE
  - ./crm-engine/node_modules/express/History.md
  - ./crm-engine/node_modules/express/package.json
  - ./crm-engine/node_modules/redis/dist/index.js
  - ./crm-engine/node_modules/redis/dist/index.d.ts
  - ./crm-engine/node_modules/redis/README.md
  - ./crm-engine/node_modules/redis/package.json
  - ./crm-engine/node_modules/gaxios/LICENSE
  - ./crm-engine/node_modules/typescript/lib/typesMap.json
  - ./crm-engine/node_modules/typescript/lib/typescript.js
  - ./crm-engine/node_modules/typescript/lib/_tsc.js
  - ./crm-engine/node_modules/typescript/LICENSE.txt
  - ./crm-engine/node_modules/typescript/ThirdPartyNoticeText.txt
  - ./crm-engine/node_modules/baseline-browser-mapping/LICENSE.txt
  - ./crm-engine/node_modules/json-bigint/lib/stringify.js
  - ./crm-engine/node_modules/json-bigint/lib/parse.js
  - ./crm-engine/node_modules/keyv/README.md
  - ./crm-engine/node_modules/keyv/package.json
  - ./crm-engine/node_modules/keyv/src/index.js
  - ./crm-engine/node_modules/keyv/src/index.d.ts
  - ./crm-engine/node_modules/eslint-visitor-keys/LICENSE
  - ./crm-engine/node_modules/@humanwhocodes/config-array/LICENSE
  - ./crm-engine/node_modules/@humanwhocodes/module-importer/LICENSE
  - ./crm-engine/node_modules/mime-types/node_modules/mime-db/db.json
  - ./crm-engine/node_modules/google-auth-library/LICENSE
  - ./crm-engine/node_modules/@google-cloud/firestore/types/firestore.d.ts
  - ./crm-engine/node_modules/@google-cloud/firestore/LICENSE
  - ./crm-engine/node_modules/@google-cloud/firestore/README.md
  - ./crm-engine/node_modules/@google-cloud/firestore/build/src/transaction.js
  - ./crm-engine/node_modules/@google-cloud/firestore/build/src/backoff.js
  - ./crm-engine/node_modules/@google-cloud/firestore/build/src/rate-limiter.d.ts
  - ./crm-engine/node_modules/@google-cloud/firestore/build/src/rate-limiter.js
  - ./crm-engine/node_modules/@google-cloud/firestore/build/src/index.js
  - ./crm-engine/node_modules/@google-cloud/firestore/build/src/bulk-writer.js
  - ./crm-engine/node_modules/@google-cloud/firestore/build/src/bulk-writer.d.ts
  - ./crm-engine/node_modules/@google-cloud/firestore/build/src/index.d.ts
  - ./crm-engine/node_modules/@google-cloud/promisify/LICENSE
  - ./crm-engine/node_modules/@google-cloud/projectify/LICENSE
  - ./crm-engine/node_modules/@google-cloud/storage/LICENSE
  - ./crm-engine/node_modules/@google-cloud/paginator/LICENSE
  - ./crm-engine/node_modules/.package-lock.json
  - ./crm-engine/node_modules/long/LICENSE
  - ./crm-engine/node_modules/doctrine/LICENSE
  - ./crm-engine/node_modules/doctrine/LICENSE.closure-compiler
  - ./crm-engine/node_modules/ecdsa-sig-formatter/LICENSE
  - ./crm-engine/node_modules/is-core-module/test/index.js
  - ./crm-engine/node_modules/is-core-module/CHANGELOG.md
  - ./crm-engine/node_modules/is-core-module/core.json
  - ./crm-engine/node_modules/firebase-admin/LICENSE
  - ./crm-engine/node_modules/firebase-admin/CHANGELOG.md
  - ./crm-engine/node_modules/firebase-admin/node_modules/@types/node/sqlite.d.ts
  - ./crm-engine/node_modules/firebase-admin/node_modules/@types/node/process.d.ts
  - ./crm-engine/node_modules/firebase-admin/node_modules/@types/node/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/node_modules/@types/node/ts5.6/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/README.md
  - ./crm-engine/node_modules/firebase-admin/package.json
  - ./crm-engine/node_modules/firebase-admin/lib/database/database.js
  - ./crm-engine/node_modules/firebase-admin/lib/database/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/database/database-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/database/database.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/database/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/database/database-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/credential/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/credential/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/default-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app/credential-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/app/core.js
  - ./crm-engine/node_modules/firebase-admin/lib/app/credential-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app/lifecycle.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app/credential.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app/firebase-app.js
  - ./crm-engine/node_modules/firebase-admin/lib/app/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/app/credential-factory.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app/core.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app/firebase-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app/firebase-app.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app/credential.js
  - ./crm-engine/node_modules/firebase-admin/lib/app/credential-factory.js
  - ./crm-engine/node_modules/firebase-admin/lib/app/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app/firebase-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/app/lifecycle.js
  - ./crm-engine/node_modules/firebase-admin/lib/firestore/firestore-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/firestore/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/firestore/firestore-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/firestore/firestore-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/firestore/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/firestore/firestore-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/token-verifier.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/token-verifier.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/project-config.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/tenant-manager.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/auth-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/auth-config.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/tenant.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/project-config-manager.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/base-auth.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/auth.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/action-code-settings-builder.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/project-config-manager.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/token-generator.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/user-record.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/tenant.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/user-record.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/tenant-manager.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/identifier.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/auth-api-request.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/auth-config.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/auth-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/auth-api-request.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/project-config.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/auth.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/token-generator.js
  - ./crm-engine/node_modules/firebase-admin/lib/auth/action-code-settings-builder.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/base-auth.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/user-import-builder.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/identifier.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/auth/user-import-builder.js
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/app-metadata.js
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/project-management-api-request-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/project-management-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/android-app.js
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/project-management.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/ios-app.js
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/ios-app.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/project-management-api-request-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/project-management.js
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/app-metadata.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/android-app.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/project-management/project-management-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/utils/jwt.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/utils/error.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/utils/crypto-signer.js
  - ./crm-engine/node_modules/firebase-admin/lib/utils/api-request.js
  - ./crm-engine/node_modules/firebase-admin/lib/utils/validator.js
  - ./crm-engine/node_modules/firebase-admin/lib/utils/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/utils/crypto-signer.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/utils/error.js
  - ./crm-engine/node_modules/firebase-admin/lib/utils/deep-copy.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/utils/validator.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/utils/jwt.js
  - ./crm-engine/node_modules/firebase-admin/lib/utils/deep-copy.js
  - ./crm-engine/node_modules/firebase-admin/lib/utils/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/utils/api-request.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/token-verifier.js
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/token-verifier.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/app-check-api-client-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/app-check-api.js
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/token-generator.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/app-check-api-client-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/app-check-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/app-check-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/app-check.js
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/app-check-api.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/token-generator.js
  - ./crm-engine/node_modules/firebase-admin/lib/app-check/app-check.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/remote-config-api.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/remote-config-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/remote-config.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/condition-evaluator-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/internal/value-impl.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/internal/value-impl.js
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/remote-config-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/remote-config-api-client-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/condition-evaluator-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/remote-config.js
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/remote-config-api.js
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/remote-config/remote-config-api-client-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/firebase-namespace-api.js
  - ./crm-engine/node_modules/firebase-admin/lib/storage/storage-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/storage/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/storage/utils.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/storage/storage-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/storage/utils.js
  - ./crm-engine/node_modules/firebase-admin/lib/storage/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/storage/storage.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/storage/storage.js
  - ./crm-engine/node_modules/firebase-admin/lib/extensions/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/extensions/extensions.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/extensions/extensions-api.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/extensions/extensions-api-client-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/extensions/extensions-api.js
  - ./crm-engine/node_modules/firebase-admin/lib/extensions/extensions-api-client-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/extensions/extensions.js
  - ./crm-engine/node_modules/firebase-admin/lib/extensions/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/installations/installations-request-handler.js
  - ./crm-engine/node_modules/firebase-admin/lib/installations/installations-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/installations/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/installations/installations-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/installations/installations.js
  - ./crm-engine/node_modules/firebase-admin/lib/installations/installations-request-handler.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/installations/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/installations/installations.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/default-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/instance-id/instance-id-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/instance-id/instance-id.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/instance-id/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/instance-id/instance-id.js
  - ./crm-engine/node_modules/firebase-admin/lib/instance-id/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/instance-id/instance-id-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/firebase-namespace-api.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/eventarc/eventarc-utils.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/eventarc/cloudevent.js
  - ./crm-engine/node_modules/firebase-admin/lib/eventarc/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/eventarc/eventarc.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/eventarc/eventarc-client-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/eventarc/eventarc.js
  - ./crm-engine/node_modules/firebase-admin/lib/eventarc/eventarc-utils.js
  - ./crm-engine/node_modules/firebase-admin/lib/eventarc/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/eventarc/eventarc-client-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/eventarc/cloudevent.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/functions/functions.js
  - ./crm-engine/node_modules/firebase-admin/lib/functions/functions-api-client-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/functions/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/functions/functions-api.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/functions/functions-api.js
  - ./crm-engine/node_modules/firebase-admin/lib/functions/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/functions/functions.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/functions/functions-api-client-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/data-connect/data-connect-api-client-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/data-connect/data-connect.js
  - ./crm-engine/node_modules/firebase-admin/lib/data-connect/data-connect-api.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/data-connect/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/data-connect/data-connect-api.js
  - ./crm-engine/node_modules/firebase-admin/lib/data-connect/data-connect.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/data-connect/data-connect-api-client-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/data-connect/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/machine-learning/machine-learning-utils.js
  - ./crm-engine/node_modules/firebase-admin/lib/machine-learning/machine-learning.js
  - ./crm-engine/node_modules/firebase-admin/lib/machine-learning/machine-learning-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/machine-learning/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/machine-learning/machine-learning-utils.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/machine-learning/machine-learning.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/machine-learning/machine-learning-api-client.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/machine-learning/machine-learning-api-client.js
  - ./crm-engine/node_modules/firebase-admin/lib/machine-learning/machine-learning-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/machine-learning/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/batch-request-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/batch-request-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging-errors-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging-api-request-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging-api-request-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging.js
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging-errors-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging-api.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/messaging/messaging-api.js
  - ./crm-engine/node_modules/firebase-admin/lib/security-rules/security-rules-namespace.js
  - ./crm-engine/node_modules/firebase-admin/lib/security-rules/security-rules.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/security-rules/security-rules-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/security-rules/security-rules-api-client-internal.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/security-rules/index.js
  - ./crm-engine/node_modules/firebase-admin/lib/security-rules/security-rules-namespace.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/security-rules/security-rules.js
  - ./crm-engine/node_modules/firebase-admin/lib/security-rules/security-rules-api-client-internal.js
  - ./crm-engine/node_modules/firebase-admin/lib/security-rules/index.d.ts
  - ./crm-engine/node_modules/firebase-admin/lib/security-rules/security-rules-internal.js
  - ./crm-engine/node_modules/gcp-metadata/LICENSE
  - ./crm-engine/node_modules/@firebase/database/dist/index.cjs.js.map
  - ./crm-engine/node_modules/@firebase/database/dist/index.cjs.js
  - ./crm-engine/node_modules/@firebase/database/dist/index.esm2017.js
  - ./crm-engine/node_modules/@firebase/database/dist/index.esm5.js
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/index.node.esm.js.map
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/test/exp/integration.test.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/test/helpers/syncpoint-util.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/index.node.esm.js
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/core/AuthTokenProvider.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/core/util/validation.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/core/storage/DOMStorageWrapper.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/core/AppCheckTokenProvider.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/core/view/EventRegistration.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/internal/index.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/api/OnDisconnect.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/api/Reference.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/api/Database.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/api/Reference_impl.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/node-esm/src/index.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/index.standalone.js.map
  - ./crm-engine/node_modules/@firebase/database/dist/test/exp/integration.test.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/test/helpers/syncpoint-util.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/index.node.cjs.js
  - ./crm-engine/node_modules/@firebase/database/dist/private.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/index.esm5.js.map
  - ./crm-engine/node_modules/@firebase/database/dist/index.standalone.js
  - ./crm-engine/node_modules/@firebase/database/dist/index.esm2017.js.map
  - ./crm-engine/node_modules/@firebase/database/dist/public.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/internal.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/index.node.cjs.js.map
  - ./crm-engine/node_modules/@firebase/database/dist/src/core/AuthTokenProvider.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/src/core/util/validation.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/src/core/storage/DOMStorageWrapper.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/src/core/AppCheckTokenProvider.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/src/core/view/EventRegistration.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/src/internal/index.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/src/api/OnDisconnect.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/src/api/Reference.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/src/api/Database.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/src/api/Reference_impl.d.ts
  - ./crm-engine/node_modules/@firebase/database/dist/src/index.d.ts
  - ./crm-engine/node_modules/@firebase/database/README.md
  - ./crm-engine/node_modules/@firebase/database/package.json
  - ./crm-engine/node_modules/@firebase/logger/dist/index.cjs.js.map
  - ./crm-engine/node_modules/@firebase/logger/dist/index.cjs.js
  - ./crm-engine/node_modules/@firebase/logger/dist/esm/index.esm2017.js
  - ./crm-engine/node_modules/@firebase/logger/dist/esm/index.esm5.js
  - ./crm-engine/node_modules/@firebase/logger/dist/esm/index.esm5.js.map
  - ./crm-engine/node_modules/@firebase/logger/dist/esm/index.esm2017.js.map
  - ./crm-engine/node_modules/@firebase/logger/README.md
  - ./crm-engine/node_modules/@firebase/logger/package.json
  - ./crm-engine/node_modules/@firebase/database-compat/standalone/package.json
  - ./crm-engine/node_modules/@firebase/database-compat/dist/index.esm2017.js
  - ./crm-engine/node_modules/@firebase/database-compat/dist/index.esm5.js
  - ./crm-engine/node_modules/@firebase/database-compat/dist/node-esm/database-compat/test/helpers/util.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.node.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/onDisconnect.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/Reference.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/Database.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/internal.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.standalone.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/node-esm/index.js
  - ./crm-engine/node_modules/@firebase/database-compat/dist/node-esm/index.js.map
  - ./crm-engine/node_modules/@firebase/database-compat/dist/index.standalone.js.map
  - ./crm-engine/node_modules/@firebase/database-compat/dist/database-compat/test/helpers/util.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/database-compat/src/index.node.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/database-compat/src/api/onDisconnect.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/database-compat/src/api/Reference.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/database-compat/src/api/Database.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/database-compat/src/api/internal.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/database-compat/src/index.standalone.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/database-compat/src/index.d.ts
  - ./crm-engine/node_modules/@firebase/database-compat/dist/index.js
  - ./crm-engine/node_modules/@firebase/database-compat/dist/index.esm5.js.map
  - ./crm-engine/node_modules/@firebase/database-compat/dist/index.standalone.js
  - ./crm-engine/node_modules/@firebase/database-compat/dist/index.esm2017.js.map
  - ./crm-engine/node_modules/@firebase/database-compat/dist/index.js.map
  - ./crm-engine/node_modules/@firebase/database-compat/README.md
  - ./crm-engine/node_modules/@firebase/database-compat/package.json
  - ./crm-engine/node_modules/@firebase/util/dist/index.cjs.js.map
  - ./crm-engine/node_modules/@firebase/util/dist/index.cjs.js
  - ./crm-engine/node_modules/@firebase/util/dist/index.esm2017.js
  - ./crm-engine/node_modules/@firebase/util/dist/index.esm5.js
  - ./crm-engine/node_modules/@firebase/util/dist/node-esm/index.node.esm.js.map
  - ./crm-engine/node_modules/@firebase/util/dist/node-esm/index.node.esm.js
  - ./crm-engine/node_modules/@firebase/util/dist/node-esm/src/emulator.d.ts
  - ./crm-engine/node_modules/@firebase/util/dist/util-public.d.ts
  - ./crm-engine/node_modules/@firebase/util/dist/index.node.cjs.js
  - ./crm-engine/node_modules/@firebase/util/dist/index.esm5.js.map
  - ./crm-engine/node_modules/@firebase/util/dist/index.esm2017.js.map
  - ./crm-engine/node_modules/@firebase/util/dist/util.d.ts
  - ./crm-engine/node_modules/@firebase/util/dist/index.node.cjs.js.map
  - ./crm-engine/node_modules/@firebase/util/dist/src/emulator.d.ts
  - ./crm-engine/node_modules/@firebase/util/README.md
  - ./crm-engine/node_modules/@firebase/util/package.json
  - ./crm-engine/node_modules/@firebase/app-check-interop-types/README.md
  - ./crm-engine/node_modules/@firebase/app-check-interop-types/package.json
  - ./crm-engine/node_modules/@firebase/app-check-interop-types/index.d.ts
  - ./crm-engine/node_modules/@firebase/component/dist/index.cjs.js.map
  - ./crm-engine/node_modules/@firebase/component/dist/index.cjs.js
  - ./crm-engine/node_modules/@firebase/component/dist/test/util.d.ts
  - ./crm-engine/node_modules/@firebase/component/dist/esm/index.esm2017.js
  - ./crm-engine/node_modules/@firebase/component/dist/esm/index.esm5.js
  - ./crm-engine/node_modules/@firebase/component/dist/esm/test/util.d.ts
  - ./crm-engine/node_modules/@firebase/component/dist/esm/index.esm5.js.map
  - ./crm-engine/node_modules/@firebase/component/dist/esm/index.esm2017.js.map
  - ./crm-engine/node_modules/@firebase/component/dist/esm/src/types.d.ts
  - ./crm-engine/node_modules/@firebase/component/dist/src/types.d.ts
  - ./crm-engine/node_modules/@firebase/component/README.md
  - ./crm-engine/node_modules/@firebase/component/package.json
  - ./crm-engine/node_modules/@firebase/app-types/private.d.ts
  - ./crm-engine/node_modules/@firebase/app-types/README.md
  - ./crm-engine/node_modules/@firebase/app-types/package.json
  - ./crm-engine/node_modules/@firebase/app-types/index.d.ts
  - ./crm-engine/node_modules/@firebase/auth-interop-types/README.md
  - ./crm-engine/node_modules/@firebase/auth-interop-types/package.json
  - ./crm-engine/node_modules/@firebase/auth-interop-types/index.d.ts
  - ./crm-engine/node_modules/@firebase/database-types/README.md
  - ./crm-engine/node_modules/@firebase/database-types/package.json
  - ./crm-engine/node_modules/@firebase/database-types/index.d.ts
  - ./crm-engine/node_modules/proto3-json-serializer/LICENSE
  - ./crm-engine/node_modules/teeny-request/LICENSE
  - ./crm-engine/node_modules/@grpc/grpc-js/LICENSE
  - ./crm-engine/node_modules/@grpc/grpc-js/proto/protoc-gen-validate/LICENSE
  - ./crm-engine/node_modules/@grpc/grpc-js/proto/xds/LICENSE
  - ./crm-engine/node_modules/@grpc/grpc-js/node_modules/@grpc/proto-loader/LICENSE
  - ./crm-engine/node_modules/@grpc/proto-loader/LICENSE
  - ./crm-engine/node_modules/cluster-key-slot/README.md
  - ./crm-engine/node_modules/cluster-key-slot/package.json
  - ./crm-engine/node_modules/cluster-key-slot/lib/index.js
  - ./crm-engine/node_modules/cluster-key-slot/index.d.ts
  - ./crm-engine/node_modules/google-logging-utils/LICENSE
  - ./crm-engine/node_modules/readable-stream/CONTRIBUTING.md
  - ./crm-engine/node_modules/human-signals/LICENSE
  - ./crm-engine/node_modules/mime-db/db.json
  - ./crm-engine/package-lock.json
  - ./crm-engine/package.json
  - ./crm-engine/src/middleware/auth.ts
  - ./crm-engine/src/config/firebase.ts
  - ./crm-engine/src/config/config.ts
  - ./crm-engine/src/server.ts
  - ./crm-engine/src/routes/health.ts
  - ./crm-engine/src/services/crmService.ts
  - ./permission-service/node_modules/node-forge/LICENSE
  - ./permission-service/node_modules/node-forge/lib/jsbn.js
  - ./permission-service/node_modules/@redis/time-series/dist/commands/MREVRANGE_WITHLABELS.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/MREVRANGE.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/GET.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/INCRBY.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/DECRBY.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/MGET.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/RANGE.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/index.js
  - ./permission-service/node_modules/@redis/time-series/dist/commands/DEL.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/QUERYINDEX.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/REVRANGE.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/QUERYINDEX.js
  - ./permission-service/node_modules/@redis/time-series/dist/commands/MGET_WITHLABELS.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/index.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/MRANGE.d.ts
  - ./permission-service/node_modules/@redis/time-series/dist/commands/MRANGE_WITHLABELS.d.ts
  - ./permission-service/node_modules/@redis/time-series/README.md
  - ./permission-service/node_modules/@redis/time-series/package.json
  - ./permission-service/node_modules/@redis/graph/dist/graph.d.ts
  - ./permission-service/node_modules/@redis/graph/dist/commands/QUERY.d.ts
  - ./permission-service/node_modules/@redis/graph/dist/commands/RO_QUERY.d.ts
  - ./permission-service/node_modules/@redis/graph/dist/commands/index.d.ts
  - ./permission-service/node_modules/@redis/graph/README.md
  - ./permission-service/node_modules/@redis/graph/package.json
  - ./permission-service/node_modules/@redis/bloom/dist/commands/top-k/QUERY.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/top-k/QUERY.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/top-k/ADD.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/top-k/COUNT.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/top-k/COUNT.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/top-k/ADD.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/BYRANK.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/MERGE.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/CDF.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/MIN.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/MAX.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/TRIMMED_MEAN.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/QUANTILE.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/BYREVRANK.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/CREATE.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/ADD.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/INFO.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/RANK.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/index.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/MERGE.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/RESET.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/t-digest/REVRANK.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/LOADCHUNK.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/MADD.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/MEXISTS.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/EXISTS.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/ADD.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/MEXISTS.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/ADD.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/MADD.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/INSERT.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/EXISTS.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/bloom/INSERT.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/ADDNX.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/INSERTNX.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/LOADCHUNK.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/DEL.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/INSERTNX.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/EXISTS.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/index.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/ADD.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/DEL.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/ADDNX.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/ADD.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/index.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/INSERT.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/EXISTS.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/cuckoo/INSERT.js
  - ./permission-service/node_modules/@redis/bloom/dist/commands/count-min-sketch/QUERY.d.ts
  - ./permission-service/node_modules/@redis/bloom/dist/commands/count-min-sketch/QUERY.js
  - ./permission-service/node_modules/@redis/bloom/README.md
  - ./permission-service/node_modules/@redis/bloom/package.json
  - ./permission-service/node_modules/@redis/search/dist/commands/DICTDEL.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/SYNUPDATE.js
  - ./permission-service/node_modules/@redis/search/dist/commands/DICTADD.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/SEARCH.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/AGGREGATE.js
  - ./permission-service/node_modules/@redis/search/dist/commands/DICTADD.js
  - ./permission-service/node_modules/@redis/search/dist/commands/index.js
  - ./permission-service/node_modules/@redis/search/dist/commands/CREATE.js
  - ./permission-service/node_modules/@redis/search/dist/commands/SUGDEL.js
  - ./permission-service/node_modules/@redis/search/dist/commands/DICTDEL.js
  - ./permission-service/node_modules/@redis/search/dist/commands/INFO.js
  - ./permission-service/node_modules/@redis/search/dist/commands/AGGREGATE.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/CURSOR_READ.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/CURSOR_DEL.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/PROFILE_SEARCH.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/INFO.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/SYNUPDATE.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/SEARCH_NOCONTENT.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/index.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/AGGREGATE_WITHCURSOR.d.ts
  - ./permission-service/node_modules/@redis/search/dist/commands/SUGDEL.d.ts
  - ./permission-service/node_modules/@redis/search/README.md
  - ./permission-service/node_modules/@redis/search/package.json
  - ./permission-service/node_modules/@redis/json/dist/commands/MSET.d.ts
  - ./permission-service/node_modules/@redis/json/dist/commands/GET.d.ts
  - ./permission-service/node_modules/@redis/json/dist/commands/GET.js
  - ./permission-service/node_modules/@redis/json/README.md
  - ./permission-service/node_modules/@redis/json/package.json
  - ./permission-service/node_modules/@redis/client/dist/package.json
  - ./permission-service/node_modules/@redis/client/dist/lib/cluster/cluster-slots.d.ts
  - ./permission-service/node_modules/@redis/client/dist/lib/cluster/index.js
  - ./permission-service/node_modules/@redis/client/dist/lib/cluster/index.d.ts
  - ./permission-service/node_modules/@redis/client/dist/lib/cluster/cluster-slots.js
  - ./permission-service/node_modules/@redis/client/dist/lib/commands/GEOSEARCHSTORE.js
  - ./permission-service/node_modules/@redis/client/dist/lib/commands/generic-transformers.js
  - ./permission-service/node_modules/@redis/client/dist/lib/commands/CLUSTER_NODES.js
  - ./permission-service/node_modules/@redis/client/dist/lib/commands/ZRANGESTORE.js
  - ./permission-service/node_modules/@redis/client/dist/lib/client/pub-sub.js
  - ./permission-service/node_modules/@redis/client/dist/lib/client/index.js
  - ./permission-service/node_modules/@redis/client/dist/lib/client/RESP2/decoder.js
  - ./permission-service/node_modules/@redis/client/dist/lib/client/index.d.ts
  - ./permission-service/node_modules/@redis/client/README.md
  - ./permission-service/node_modules/@redis/client/package.json
  - ./permission-service/node_modules/farmhash-modern/bin/nodejs/farmhash_modern.js
  - ./permission-service/node_modules/farmhash-modern/bin/bundler/farmhash_modern_bg.js
  - ./permission-service/node_modules/farmhash-modern/README.md
  - ./permission-service/node_modules/farmhash-modern/package.json
  - ./permission-service/node_modules/farmhash-modern/lib/index.d.mts
  - ./permission-service/node_modules/farmhash-modern/lib/index.d.cts
  - ./permission-service/node_modules/farmhash-modern/lib/index.js
  - ./permission-service/node_modules/farmhash-modern/lib/index.cjs
  - ./permission-service/node_modules/farmhash-modern/lib/index.mjs
  - ./permission-service/node_modules/farmhash-modern/lib/index.d.ts
  - ./permission-service/node_modules/farmhash-modern/lib/browser.js
  - ./permission-service/node_modules/farmhash-modern/lib/browser.d.ts
  - ./permission-service/node_modules/dotenv/README.md
  - ./permission-service/node_modules/resolve/lib/core.json
  - ./permission-service/node_modules/@opentelemetry/api/LICENSE
  - ./permission-service/node_modules/express/History.md
  - ./permission-service/node_modules/express/package.json
  - ./permission-service/node_modules/redis/dist/index.js
  - ./permission-service/node_modules/redis/dist/index.d.ts
  - ./permission-service/node_modules/redis/README.md
  - ./permission-service/node_modules/redis/package.json
  - ./permission-service/node_modules/gaxios/LICENSE
  - ./permission-service/node_modules/typescript/lib/typesMap.json
  - ./permission-service/node_modules/typescript/lib/typescript.js
  - ./permission-service/node_modules/typescript/lib/_tsc.js
  - ./permission-service/node_modules/typescript/LICENSE.txt
  - ./permission-service/node_modules/typescript/ThirdPartyNoticeText.txt
  - ./permission-service/node_modules/json-bigint/lib/stringify.js
  - ./permission-service/node_modules/json-bigint/lib/parse.js
  - ./permission-service/node_modules/keyv/README.md
  - ./permission-service/node_modules/keyv/package.json
  - ./permission-service/node_modules/keyv/src/index.js
  - ./permission-service/node_modules/keyv/src/index.d.ts
  - ./permission-service/node_modules/eslint-visitor-keys/LICENSE
  - ./permission-service/node_modules/@humanwhocodes/config-array/LICENSE
  - ./permission-service/node_modules/@humanwhocodes/module-importer/LICENSE
  - ./permission-service/node_modules/google-auth-library/LICENSE
  - ./permission-service/node_modules/@google-cloud/firestore/types/firestore.d.ts
  - ./permission-service/node_modules/@google-cloud/firestore/LICENSE
  - ./permission-service/node_modules/@google-cloud/firestore/README.md
  - ./permission-service/node_modules/@google-cloud/firestore/build/src/transaction.js
  - ./permission-service/node_modules/@google-cloud/firestore/build/src/backoff.js
  - ./permission-service/node_modules/@google-cloud/firestore/build/src/rate-limiter.d.ts
  - ./permission-service/node_modules/@google-cloud/firestore/build/src/rate-limiter.js
  - ./permission-service/node_modules/@google-cloud/firestore/build/src/index.js
  - ./permission-service/node_modules/@google-cloud/firestore/build/src/bulk-writer.js
  - ./permission-service/node_modules/@google-cloud/firestore/build/src/bulk-writer.d.ts
  - ./permission-service/node_modules/@google-cloud/firestore/build/src/index.d.ts
  - ./permission-service/node_modules/@google-cloud/promisify/LICENSE
  - ./permission-service/node_modules/@google-cloud/projectify/LICENSE
  - ./permission-service/node_modules/@google-cloud/storage/LICENSE
  - ./permission-service/node_modules/@google-cloud/paginator/LICENSE
  - ./permission-service/node_modules/.package-lock.json
  - ./permission-service/node_modules/long/LICENSE
  - ./permission-service/node_modules/doctrine/LICENSE
  - ./permission-service/node_modules/doctrine/LICENSE.closure-compiler
  - ./permission-service/node_modules/ecdsa-sig-formatter/LICENSE
  - ./permission-service/node_modules/is-core-module/test/index.js
  - ./permission-service/node_modules/is-core-module/CHANGELOG.md
  - ./permission-service/node_modules/is-core-module/core.json
  - ./permission-service/node_modules/firebase-admin/LICENSE
  - ./permission-service/node_modules/firebase-admin/CHANGELOG.md
  - ./permission-service/node_modules/firebase-admin/node_modules/@types/node/sqlite.d.ts
  - ./permission-service/node_modules/firebase-admin/node_modules/@types/node/process.d.ts
  - ./permission-service/node_modules/firebase-admin/node_modules/@types/node/index.d.ts
  - ./permission-service/node_modules/firebase-admin/node_modules/@types/node/ts5.6/index.d.ts
  - ./permission-service/node_modules/firebase-admin/README.md
  - ./permission-service/node_modules/firebase-admin/package.json
  - ./permission-service/node_modules/firebase-admin/lib/database/database.js
  - ./permission-service/node_modules/firebase-admin/lib/database/index.js
  - ./permission-service/node_modules/firebase-admin/lib/database/database-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/database/database.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/database/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/database/database-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/credential/index.js
  - ./permission-service/node_modules/firebase-admin/lib/credential/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/default-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app/credential-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/app/core.js
  - ./permission-service/node_modules/firebase-admin/lib/app/credential-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app/lifecycle.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app/credential.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app/firebase-app.js
  - ./permission-service/node_modules/firebase-admin/lib/app/index.js
  - ./permission-service/node_modules/firebase-admin/lib/app/credential-factory.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app/core.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app/firebase-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app/firebase-app.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app/credential.js
  - ./permission-service/node_modules/firebase-admin/lib/app/credential-factory.js
  - ./permission-service/node_modules/firebase-admin/lib/app/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app/firebase-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/app/lifecycle.js
  - ./permission-service/node_modules/firebase-admin/lib/firestore/firestore-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/firestore/index.js
  - ./permission-service/node_modules/firebase-admin/lib/firestore/firestore-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/firestore/firestore-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/firestore/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/firestore/firestore-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/token-verifier.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/token-verifier.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/project-config.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/tenant-manager.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/auth-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/auth-config.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/tenant.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/project-config-manager.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/base-auth.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/auth.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/action-code-settings-builder.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/project-config-manager.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/index.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/token-generator.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/user-record.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/tenant.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/user-record.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/tenant-manager.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/identifier.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/auth-api-request.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/auth-config.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/auth-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/auth-api-request.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/project-config.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/auth.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/token-generator.js
  - ./permission-service/node_modules/firebase-admin/lib/auth/action-code-settings-builder.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/base-auth.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/user-import-builder.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/identifier.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/auth/user-import-builder.js
  - ./permission-service/node_modules/firebase-admin/lib/project-management/app-metadata.js
  - ./permission-service/node_modules/firebase-admin/lib/project-management/project-management-api-request-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/project-management/project-management-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/project-management/android-app.js
  - ./permission-service/node_modules/firebase-admin/lib/project-management/project-management.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/project-management/ios-app.js
  - ./permission-service/node_modules/firebase-admin/lib/project-management/ios-app.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/project-management/index.js
  - ./permission-service/node_modules/firebase-admin/lib/project-management/project-management-api-request-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/project-management/project-management.js
  - ./permission-service/node_modules/firebase-admin/lib/project-management/app-metadata.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/project-management/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/project-management/android-app.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/project-management/project-management-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/index.js
  - ./permission-service/node_modules/firebase-admin/lib/utils/jwt.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/utils/error.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/utils/crypto-signer.js
  - ./permission-service/node_modules/firebase-admin/lib/utils/api-request.js
  - ./permission-service/node_modules/firebase-admin/lib/utils/validator.js
  - ./permission-service/node_modules/firebase-admin/lib/utils/index.js
  - ./permission-service/node_modules/firebase-admin/lib/utils/crypto-signer.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/utils/error.js
  - ./permission-service/node_modules/firebase-admin/lib/utils/deep-copy.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/utils/validator.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/utils/jwt.js
  - ./permission-service/node_modules/firebase-admin/lib/utils/deep-copy.js
  - ./permission-service/node_modules/firebase-admin/lib/utils/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/utils/api-request.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app-check/token-verifier.js
  - ./permission-service/node_modules/firebase-admin/lib/app-check/token-verifier.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app-check/app-check-api-client-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app-check/app-check-api.js
  - ./permission-service/node_modules/firebase-admin/lib/app-check/index.js
  - ./permission-service/node_modules/firebase-admin/lib/app-check/token-generator.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app-check/app-check-api-client-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/app-check/app-check-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app-check/app-check-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/app-check/app-check.js
  - ./permission-service/node_modules/firebase-admin/lib/app-check/app-check-api.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app-check/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/app-check/token-generator.js
  - ./permission-service/node_modules/firebase-admin/lib/app-check/app-check.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/remote-config-api.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/remote-config-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/remote-config.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/condition-evaluator-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/internal/value-impl.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/internal/value-impl.js
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/index.js
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/remote-config-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/remote-config-api-client-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/condition-evaluator-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/remote-config.js
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/remote-config-api.js
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/remote-config/remote-config-api-client-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/firebase-namespace-api.js
  - ./permission-service/node_modules/firebase-admin/lib/storage/storage-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/storage/index.js
  - ./permission-service/node_modules/firebase-admin/lib/storage/utils.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/storage/storage-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/storage/utils.js
  - ./permission-service/node_modules/firebase-admin/lib/storage/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/storage/storage.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/storage/storage.js
  - ./permission-service/node_modules/firebase-admin/lib/extensions/index.js
  - ./permission-service/node_modules/firebase-admin/lib/extensions/extensions.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/extensions/extensions-api.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/extensions/extensions-api-client-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/extensions/extensions-api.js
  - ./permission-service/node_modules/firebase-admin/lib/extensions/extensions-api-client-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/extensions/extensions.js
  - ./permission-service/node_modules/firebase-admin/lib/extensions/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/installations/installations-request-handler.js
  - ./permission-service/node_modules/firebase-admin/lib/installations/installations-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/installations/index.js
  - ./permission-service/node_modules/firebase-admin/lib/installations/installations-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/installations/installations.js
  - ./permission-service/node_modules/firebase-admin/lib/installations/installations-request-handler.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/installations/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/installations/installations.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/default-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/instance-id/instance-id-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/instance-id/instance-id.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/instance-id/index.js
  - ./permission-service/node_modules/firebase-admin/lib/instance-id/instance-id.js
  - ./permission-service/node_modules/firebase-admin/lib/instance-id/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/instance-id/instance-id-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/firebase-namespace-api.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/eventarc/eventarc-utils.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/eventarc/cloudevent.js
  - ./permission-service/node_modules/firebase-admin/lib/eventarc/index.js
  - ./permission-service/node_modules/firebase-admin/lib/eventarc/eventarc.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/eventarc/eventarc-client-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/eventarc/eventarc.js
  - ./permission-service/node_modules/firebase-admin/lib/eventarc/eventarc-utils.js
  - ./permission-service/node_modules/firebase-admin/lib/eventarc/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/eventarc/eventarc-client-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/eventarc/cloudevent.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/functions/functions.js
  - ./permission-service/node_modules/firebase-admin/lib/functions/functions-api-client-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/functions/index.js
  - ./permission-service/node_modules/firebase-admin/lib/functions/functions-api.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/functions/functions-api.js
  - ./permission-service/node_modules/firebase-admin/lib/functions/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/functions/functions.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/functions/functions-api-client-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/data-connect/data-connect-api-client-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/data-connect/data-connect.js
  - ./permission-service/node_modules/firebase-admin/lib/data-connect/data-connect-api.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/data-connect/index.js
  - ./permission-service/node_modules/firebase-admin/lib/data-connect/data-connect-api.js
  - ./permission-service/node_modules/firebase-admin/lib/data-connect/data-connect.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/data-connect/data-connect-api-client-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/data-connect/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-utils.js
  - ./permission-service/node_modules/firebase-admin/lib/machine-learning/machine-learning.js
  - ./permission-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/machine-learning/index.js
  - ./permission-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-utils.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/machine-learning/machine-learning.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-api-client.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-api-client.js
  - ./permission-service/node_modules/firebase-admin/lib/machine-learning/machine-learning-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/machine-learning/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/messaging/batch-request-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/messaging/batch-request-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging-errors-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging-api-request-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/messaging/index.js
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging-api-request-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging.js
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging-errors-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging-api.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/messaging/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/messaging/messaging-api.js
  - ./permission-service/node_modules/firebase-admin/lib/security-rules/security-rules-namespace.js
  - ./permission-service/node_modules/firebase-admin/lib/security-rules/security-rules.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/security-rules/security-rules-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/security-rules/security-rules-api-client-internal.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/security-rules/index.js
  - ./permission-service/node_modules/firebase-admin/lib/security-rules/security-rules-namespace.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/security-rules/security-rules.js
  - ./permission-service/node_modules/firebase-admin/lib/security-rules/security-rules-api-client-internal.js
  - ./permission-service/node_modules/firebase-admin/lib/security-rules/index.d.ts
  - ./permission-service/node_modules/firebase-admin/lib/security-rules/security-rules-internal.js
  - ./permission-service/node_modules/gcp-metadata/LICENSE
  - ./permission-service/node_modules/@firebase/database/dist/index.cjs.js.map
  - ./permission-service/node_modules/@firebase/database/dist/index.cjs.js
  - ./permission-service/node_modules/@firebase/database/dist/index.esm2017.js
  - ./permission-service/node_modules/@firebase/database/dist/index.esm5.js
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/index.node.esm.js.map
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/test/exp/integration.test.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/test/helpers/syncpoint-util.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/index.node.esm.js
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/core/AuthTokenProvider.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/core/util/validation.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/core/storage/DOMStorageWrapper.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/core/AppCheckTokenProvider.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/core/view/EventRegistration.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/internal/index.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/api/OnDisconnect.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/api/Reference.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/api/Database.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/api/Reference_impl.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/node-esm/src/index.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/index.standalone.js.map
  - ./permission-service/node_modules/@firebase/database/dist/test/exp/integration.test.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/test/helpers/syncpoint-util.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/index.node.cjs.js
  - ./permission-service/node_modules/@firebase/database/dist/private.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/index.esm5.js.map
  - ./permission-service/node_modules/@firebase/database/dist/index.standalone.js
  - ./permission-service/node_modules/@firebase/database/dist/index.esm2017.js.map
  - ./permission-service/node_modules/@firebase/database/dist/public.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/internal.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/index.node.cjs.js.map
  - ./permission-service/node_modules/@firebase/database/dist/src/core/AuthTokenProvider.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/src/core/util/validation.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/src/core/storage/DOMStorageWrapper.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/src/core/AppCheckTokenProvider.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/src/core/view/EventRegistration.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/src/internal/index.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/src/api/OnDisconnect.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/src/api/Reference.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/src/api/Database.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/src/api/Reference_impl.d.ts
  - ./permission-service/node_modules/@firebase/database/dist/src/index.d.ts
  - ./permission-service/node_modules/@firebase/database/README.md
  - ./permission-service/node_modules/@firebase/database/package.json
  - ./permission-service/node_modules/@firebase/logger/dist/index.cjs.js.map
  - ./permission-service/node_modules/@firebase/logger/dist/index.cjs.js
  - ./permission-service/node_modules/@firebase/logger/dist/esm/index.esm2017.js
  - ./permission-service/node_modules/@firebase/logger/dist/esm/index.esm5.js
  - ./permission-service/node_modules/@firebase/logger/dist/esm/index.esm5.js.map
  - ./permission-service/node_modules/@firebase/logger/dist/esm/index.esm2017.js.map
  - ./permission-service/node_modules/@firebase/logger/README.md
  - ./permission-service/node_modules/@firebase/logger/package.json
  - ./permission-service/node_modules/@firebase/database-compat/standalone/package.json
  - ./permission-service/node_modules/@firebase/database-compat/dist/index.esm2017.js
  - ./permission-service/node_modules/@firebase/database-compat/dist/index.esm5.js
  - ./permission-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/test/helpers/util.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.node.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/onDisconnect.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/Reference.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/Database.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/api/internal.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.standalone.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/node-esm/database-compat/src/index.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/node-esm/index.js
  - ./permission-service/node_modules/@firebase/database-compat/dist/node-esm/index.js.map
  - ./permission-service/node_modules/@firebase/database-compat/dist/index.standalone.js.map
  - ./permission-service/node_modules/@firebase/database-compat/dist/database-compat/test/helpers/util.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/database-compat/src/index.node.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/onDisconnect.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/Reference.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/Database.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/database-compat/src/api/internal.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/database-compat/src/index.standalone.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/database-compat/src/index.d.ts
  - ./permission-service/node_modules/@firebase/database-compat/dist/index.js
  - ./permission-service/node_modules/@firebase/database-compat/dist/index.esm5.js.map
  - ./permission-service/node_modules/@firebase/database-compat/dist/index.standalone.js
  - ./permission-service/node_modules/@firebase/database-compat/dist/index.esm2017.js.map
  - ./permission-service/node_modules/@firebase/database-compat/dist/index.js.map
  - ./permission-service/node_modules/@firebase/database-compat/README.md
  - ./permission-service/node_modules/@firebase/database-compat/package.json
  - ./permission-service/node_modules/@firebase/util/dist/index.cjs.js.map
  - ./permission-service/node_modules/@firebase/util/dist/index.cjs.js
  - ./permission-service/node_modules/@firebase/util/dist/index.esm2017.js
  - ./permission-service/node_modules/@firebase/util/dist/index.esm5.js
  - ./permission-service/node_modules/@firebase/util/dist/node-esm/index.node.esm.js.map
  - ./permission-service/node_modules/@firebase/util/dist/node-esm/index.node.esm.js
  - ./permission-service/node_modules/@firebase/util/dist/node-esm/src/emulator.d.ts
  - ./permission-service/node_modules/@firebase/util/dist/util-public.d.ts
  - ./permission-service/node_modules/@firebase/util/dist/index.node.cjs.js
  - ./permission-service/node_modules/@firebase/util/dist/index.esm5.js.map
  - ./permission-service/node_modules/@firebase/util/dist/index.esm2017.js.map
  - ./permission-service/node_modules/@firebase/util/dist/util.d.ts
  - ./permission-service/node_modules/@firebase/util/dist/index.node.cjs.js.map
  - ./permission-service/node_modules/@firebase/util/dist/src/emulator.d.ts
  - ./permission-service/node_modules/@firebase/util/README.md
  - ./permission-service/node_modules/@firebase/util/package.json
  - ./permission-service/node_modules/@firebase/app-check-interop-types/README.md
  - ./permission-service/node_modules/@firebase/app-check-interop-types/package.json
  - ./permission-service/node_modules/@firebase/app-check-interop-types/index.d.ts
  - ./permission-service/node_modules/@firebase/component/dist/index.cjs.js.map
  - ./permission-service/node_modules/@firebase/component/dist/index.cjs.js
  - ./permission-service/node_modules/@firebase/component/dist/test/util.d.ts
  - ./permission-service/node_modules/@firebase/component/dist/esm/index.esm2017.js
  - ./permission-service/node_modules/@firebase/component/dist/esm/index.esm5.js
  - ./permission-service/node_modules/@firebase/component/dist/esm/test/util.d.ts
  - ./permission-service/node_modules/@firebase/component/dist/esm/index.esm5.js.map
  - ./permission-service/node_modules/@firebase/component/dist/esm/index.esm2017.js.map
  - ./permission-service/node_modules/@firebase/component/dist/esm/src/types.d.ts
  - ./permission-service/node_modules/@firebase/component/dist/src/types.d.ts
  - ./permission-service/node_modules/@firebase/component/README.md
  - ./permission-service/node_modules/@firebase/component/package.json
  - ./permission-service/node_modules/@firebase/app-types/private.d.ts
  - ./permission-service/node_modules/@firebase/app-types/README.md
  - ./permission-service/node_modules/@firebase/app-types/package.json
  - ./permission-service/node_modules/@firebase/app-types/index.d.ts
  - ./permission-service/node_modules/@firebase/auth-interop-types/README.md
  - ./permission-service/node_modules/@firebase/auth-interop-types/package.json
  - ./permission-service/node_modules/@firebase/auth-interop-types/index.d.ts
  - ./permission-service/node_modules/@firebase/database-types/README.md
  - ./permission-service/node_modules/@firebase/database-types/package.json
  - ./permission-service/node_modules/@firebase/database-types/index.d.ts
  - ./permission-service/node_modules/proto3-json-serializer/LICENSE
  - ./permission-service/node_modules/teeny-request/LICENSE
  - ./permission-service/node_modules/@grpc/grpc-js/LICENSE
  - ./permission-service/node_modules/@grpc/grpc-js/proto/protoc-gen-validate/LICENSE
  - ./permission-service/node_modules/@grpc/grpc-js/proto/xds/LICENSE
  - ./permission-service/node_modules/@grpc/grpc-js/node_modules/@grpc/proto-loader/LICENSE
  - ./permission-service/node_modules/@grpc/proto-loader/LICENSE
  - ./permission-service/node_modules/cluster-key-slot/README.md
  - ./permission-service/node_modules/cluster-key-slot/package.json
  - ./permission-service/node_modules/cluster-key-slot/lib/index.js
  - ./permission-service/node_modules/cluster-key-slot/index.d.ts
  - ./permission-service/node_modules/google-logging-utils/LICENSE
  - ./permission-service/node_modules/readable-stream/CONTRIBUTING.md
  - ./permission-service/node_modules/mime-db/db.json
  - ./permission-service/README.md
  - ./permission-service/package-lock.json
  - ./permission-service/package.json
  - ./permission-service/src/server.ts
  - ./permission-service/src/routes/permissions.ts
  - ./permission-service/src/routes/templates.ts
  - ./permission-service/src/routes/roles.ts
  - ./permission-service/src/services/cache.ts
  - ./OPERATIONAL_LAYER_PHASE3_COMPLETE.md
  - ./plagiarism-detector/requirements.txt
  - ./plagiarism-detector/main.py
  - ./trending-engine-coordinator/requirements.txt
  - ./trending-engine-coordinator/main.py
  - ./archive/documentation/IMPLEMENTATION_ROADMAP.md
  - ./archive/documentation/DEPLOY_PHASE6_NOW.md
  - ./archive/documentation/ASO_IMPLEMENTATION_PLAN.md
  - ./archive/phase-reports/PHASE6_LIGHTWEIGHT_DEPLOYMENT_COMPLETE.md
  - ./archive/phase-reports/FINAL_STATUS_AND_NEXT_STEPS.md
  - ./archive/phase-reports/ASO_PHASE1_STATUS.md
  - ./archive/phase-reports/PHASE2_COMPLETE_FINAL.md
  - ./archive/phase-reports/ASO_PHASE1_DAY1_COMPLETE.md
  - ./archive/phase-reports/OPTIMIZATION_COMPLETE_SUMMARY.md
  - ./archive/phase-reports/PHASE6_ADVANCED_OPTIMIZATION_COMPLETE.md
  - ./archive/phase-reports/PHASE2_COST_OPTIMIZATION_COMPLETE.md
  - ./archive/phase-reports/PHASE4_DATABASE_OPTIMIZATION_COMPLETE.md
  - ./archive/phase-reports/ASO_PHASE1_COMPLETE.md
  - ./archive/phase8-optimization/PHASE8_OPTIMIZATION_COMPLETE.md
  - ./archive/phase8-optimization/PHASE8_CODE_REVIEW_FINDINGS.md
  - ./archive/README.md
  - ./archive/utilities/migrate_to_shared_db_clients.py
  - ./archive/templates/xynergy-update3.md
  - ./archive/templates/onboard.md
  - ./archive/templates/sdk_requirements.txt
  - ./archive/templates/feature.md
  - ./archive/templates/xynergy-seo-engines-requirements.md
  - ./fact-checking-layer/requirements.txt
  - ./fact-checking-layer/main.py
  - ./intelligence-gateway-trd.md
  - ./README_OPTIMIZATION.md
  - ./executive-dashboard/requirements.txt
  - ./executive-dashboard/main.py
  - ./qa-engine/main.py
  - ./market-intelligence-service/main.py
  - ./project-management/main.py
  - ./xynergy-competency-engine/requirements.txt
  - ./xynergy-competency-engine/collective_intelligence.py
  - ./xynergy-competency-engine/main.py
  - ./INTELLIGENCE_GATEWAY_OPTIMIZATION_PLAN.md
  - ./CODE_REVIEW_FIXES_COMPLETE.md
  - ./real-time-trend-monitor/requirements.txt
  - ./real-time-trend-monitor/main.py
  - ./INTELLIGENCE_GATEWAY_IMPLEMENTATION_PLAN.md
  - ./oauth-management-service/.gitignore
  - ./oauth-management-service/package-lock.json
  - ./oauth-management-service/package.json
  - ./oauth-management-service/src/utils/redis.ts
  - ./oauth-management-service/src/server.ts
  - ./oauth-management-service/src/routes/admin.ts
  - ./oauth-management-service/src/services/healthService.ts
  - ./oauth-management-service/src/services/tokenService.ts
  - ./oauth-management-service/src/services/oauthService.ts
  - ./COMPREHENSIVE_CODE_REVIEW_REPORT.md
  - ./validation-coordinator/requirements.txt
  - ./validation-coordinator/main.py
  - ./repo-review.md
  - ./intelligence-gateway.md
  - ./XYNERGY_CREDENTIALS_AUDIT_REPORT.md
  - ./automated-publisher/main.py
  - ./shared/tenant_utils.py
  - ./shared/tenant_data_utils.py
  - ./shared/bigquery_optimizer.py
  - ./shared/semantic_cache.py
  - ./shared/gcp_clients.py
  - ./shared/redis_cache.py
  - ./attribution-coordinator/requirements.txt
  - ./attribution-coordinator/main.py
  - ./internal-ai-service/main.py
  - ./docs/PERFORMANCE_OPTIMIZATION_GUIDE.md
  - ./docs/ADR/README.md
  - ./docs/SECURITY_ARCHITECTURE.md
  - ./docs/ALL_REMAINING_DOCUMENTATION.md
  - ./docs/TECHNICAL_DESIGN_DOCUMENT.md
  - ./docs/ARCHITECTURE_DECISION_RECORDS.md
  - ./docs/DATA_MODEL_SCHEMA.md
  - ./monetization-integration/tenant_utils.py
  - ./monetization-integration/tenant_data_utils.py
  - ./monetization-integration/main.py
  - ./PHASE4_COMPLETE.md
  - ./reports-export/main.py
  - ./PLATFORM_AS_BUILT.md
  - ./ai-ml-engine/requirements.txt
  - ./ai-ml-engine/shared/tenant_utils.py
  - ./ai-ml-engine/main.py
  - ./ai-routing-engine/requirements.txt
  - ./ai-routing-engine/main.py
  - ./ai-routing-engine/gcp_clients.py
  - ./ai-routing-engine/redis_cache.py
  - ./COMPREHENSIVE_CODE_REVIEW_REPORT_NOV_2025.md
  - ./PLATFORM_INTEGRATION_COMPLETE.md
  - ./audit-logging-service/requirements_optimized.txt
  - ./audit-logging-service/requirements.txt
  - ./audit-logging-service/main_optimized.py
  - ./audit-logging-service/main.py
  - ./system-runtime/main.py
  - ./rapid-content-generator/requirements.txt
  - ./rapid-content-generator/main.py
  - ./TECHNICAL_INTEGRATION_REPORT.md
  - ./PHASE3_COMPLETE.md
  - ./update-trd.md
  - ./beta-program-service/package-lock.json
  - ./beta-program-service/package.json
  - ./beta-program-service/src/server.ts
  - ./beta-program-service/src/services/phaseTransitionService.ts
  - ./beta-program-service/src/services/lifetimeAccessService.ts
  - ./beta-program-service/src/services/applicationService.ts
  - ./PHASE6_DEPLOYMENT_INSTRUCTIONS.md
  - ./scheduler-automation-engine/main.py
  - ./OPERATIONAL_LAYER_PHASE1_IMPLEMENTATION.md
  - ./PHASES_1-4_COMPLETE_SUMMARY.md
  - ./WEEK4_SLACK_INTELLIGENCE_COMPLETE.md
  - ./aso-engine/requirements.txt
  - ./aso-engine/main.py
  - ./SLACK_OAUTH_COMPLETE.md
  - ./DEPLOYMENT_GUIDE.md
  - ./BACKEND_PRODUCTION_AUDIT_REPORT.md
  - ./INTEGRATION_DEPLOYMENT_SUMMARY.md
  - ./analytics-aggregation-service/requirements_optimized.txt
  - ./analytics-aggregation-service/requirements.txt
  - ./analytics-aggregation-service/main_optimized.py
  - ./analytics-aggregation-service/main.py
  - ./LOCAL_INTEGRATION_ANALYSIS.md
  - ./scripts/init-operational-layer-database.ts
  - ./FIREBASE_CONFIG_COMPLETE.md
  - ./tenant-onboarding-service/app/models/onboarding.py
  - ./tenant-onboarding-service/app/services/cost_tracking.py
  - ./tenant-onboarding-service/requirements.txt
  - ./tenant-onboarding-service/IMPLEMENTATION_SUMMARY.md
  - ./tenant-onboarding-service/README.md
  - ./INFRASTRUCTURE_STATUS_REPORT.md
  - ./marketing-engine/requirements.txt
  - ./marketing-engine/main.py
  - ./WEEK1_INTELLIGENCE_GATEWAY_COMPLETE.md
  - ./ai-assistant/main.py
  - ./fact-checking-service/requirements.txt
  - ./fact-checking-service/main.py
  - ./ai-workflow-engine/tenant_utils.py
  - ./ai-workflow-engine/tenant_data_utils.py
  - ./ai-workflow-engine/requirements.txt
  - ./ai-workflow-engine/main.py
  - ./platform-integration-trd.md
  - ./WEEK5-6_CRM_ENGINE_COMPLETE.md
  - ./OPTIMIZATION_COMPLETE.md
  - ./advanced-analytics/tenant_utils.py
  - ./advanced-analytics/tenant_data_utils.py
  - ./advanced-analytics/requirements.txt
  - ./advanced-analytics/main.py
  - ./trust-safety-validator/requirements.txt
  - ./trust-safety-validator/main.py
  - ./GMAIL_OAUTH_COMPLETE.md
  - ./WEEK2_INTELLIGENCE_GATEWAY_COMPLETE.md
  - ./INTEGRATION_STATUS_SUMMARY.md
  - ./PHASE1_OPTIMIZATION_COMPLETE.md
  - ./OPTIMIZATION_COMPLETE_FINAL_STATUS.md
  - ./OPERATIONAL_LAYER_PHASE1_COMPLETE.md
  - ./XYNERGY_API_INTEGRATION_GUIDE.md
  - ./.env.development
  - ./OPERATIONAL_LAYER_DEPLOYMENT_STATUS.md
  - ./internal-ai-service-v2/requirements.txt
  - ./internal-ai-service-v2/main.py
  - ./tenant-management/tenant_utils.py
  - ./tenant-management/tenant_data_utils.py
  - ./tenant-management/requirements.txt
  - ./tenant-management/main.py
  - ./keyword-revenue-tracker/requirements.txt
  - ./keyword-revenue-tracker/main.py

## Security-Related Hints
  - None detected

## Linting/Formatting/Quality

## TODOs & FIXMEs
  - ./slack-intelligence-service/node_modules/jest-runtime/build/index.js:278:    // TODO: make mandatory in Jest 30
  - ./slack-intelligence-service/node_modules/jest-runtime/build/index.js:1187:          // TODO: will this work on windows? It might be better if `shouldInstrument` deals with it anyways
  - ./slack-intelligence-service/node_modules/jest-runtime/build/index.js:1861:      // TODO: consider warning somehow that this does nothing. We should support deletions, anyways
  - ./slack-intelligence-service/node_modules/jest-runtime/build/index.js:2031:          // TODO: remove this check in Jest 30
  - ./slack-intelligence-service/node_modules/jest-runtime/build/index.js:2049:          // TODO: remove this check in Jest 30
  - ./slack-intelligence-service/node_modules/jest-runtime/build/index.js:2085:        // TODO: remove this check in Jest 30
  - ./slack-intelligence-service/node_modules/jest-runtime/build/index.js:2123:          // TODO: remove this check in Jest 30
  - ./slack-intelligence-service/node_modules/jest-runtime/build/index.js:2140:          // TODO: remove this check in Jest 30
  - ./slack-intelligence-service/node_modules/jws/readme.md:220:# TODO
  - ./slack-intelligence-service/node_modules/callsites/index.js:12:// TODO: Remove this for the next major release
  - ./slack-intelligence-service/node_modules/callsites/index.d.ts:90:	// TODO: Remove this for the next major release, refactor the whole definition to:
  - ./slack-intelligence-service/node_modules/test-exclude/node_modules/minimatch/minimatch.js:491:        // TODO: It would probably be faster to determine this
  - ./slack-intelligence-service/node_modules/node-forge/README.md:593:// TODO
  - ./slack-intelligence-service/node_modules/node-forge/README.md:605:// TODO
  - ./slack-intelligence-service/node_modules/node-forge/README.md:1905:// TODO
  - ./slack-intelligence-service/node_modules/node-forge/README.md:1971:// TODO
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:534:  // FIXME: hex conversion inefficient, get BigInteger w/byte strings
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:542:  // FIXME: hex conversion inefficient, get BigInteger w/byte strings
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:585:  // FIXME: hex conversion inefficient, get BigInteger w/byte strings
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:599:  // FIXME: hex conversion inefficient, get BigInteger w/byte strings
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:633:  // TODO: migrate step-based prime generation code to forge.prime
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:698: *     // TODO: turn off progress indicator here
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:699: *     // TODO: use the generated key-pair in "state.keys"
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:702: * // TODO: turn on progress indicator here
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:717:  // TODO: migrate step-based prime generation code to forge.prime
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:718:  // TODO: abstract as PRIMEINC algorithm
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:1176:          // FIXME: add support to vaidator for strict value choices
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:1396:  // FIXME: inefficient, get a BigInteger that uses byte strings
  - ./slack-intelligence-service/node_modules/node-forge/lib/rsa.js:1490:  // FIXME: inefficient, get a BigInteger that uses byte strings
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1-validator.js:72:  // FIXME: this is capture group for rsaPublicKey, use it in this API or
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:156:// TODO: set ByteBuffer to best available backing
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:168:  // TODO: update to match DataBuffer API
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:182:      // FIXME: support native buffers internally instead
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:544:    // TODO: Use (rval * 0x100) if adding support for 33 to 53 bits.
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:724: * FIXME: Experimental. Do not use yet.
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:766:      // TODO: adjust read/write offset based on the type of view
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1207:    // TODO: Use (rval * 0x100) if adding support for 33 to 53 bits.
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1241:  // TODO: deprecate this method, it is poorly named and
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1269:  // TODO: deprecate this method, it is poorly named, add "getString()"
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1423:  // TODO: deprecate, use new ByteBuffer() instead
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1493:  // TODO: deprecate: "Deprecated. Use util.binary.hex.decode instead."
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1516:  // TODO: deprecate: "Deprecated. Use util.binary.hex.encode instead."
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1581:  // TODO: deprecate: "Deprecated. Use util.binary.base64.encode instead."
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1618:  // TODO: deprecate: "Deprecated. Use util.binary.base64.decode instead."
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1675:// FIXME: Experimental. Do not use yet.
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1853:// FIXME: Experimental. Do not use yet.
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:1972:  // TODO: add zlib header and trailer if necessary/possible
  - ./slack-intelligence-service/node_modules/node-forge/lib/util.js:2319:    // FIXME: do proper formating for numbers, etc
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs12.js:827:      // FIXME: consider using SHA-1 of public key (which can be generated
  - ./slack-intelligence-service/node_modules/node-forge/lib/random.js:67:  // FIXME: do we care about carry or signed issues?
  - ./slack-intelligence-service/node_modules/node-forge/lib/random.js:131:    // FIXME:
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs1.js:237:  // TODO: It must be possible to do this in a better/smarter way?
  - ./slack-intelligence-service/node_modules/node-forge/lib/prime.js:184:    // TODO: consider optimizing by starting workers outside getPrime() ...
  - ./slack-intelligence-service/node_modules/node-forge/lib/prime.js:191:      // FIXME: fix path or use blob URLs
  - ./slack-intelligence-service/node_modules/node-forge/lib/aesCipherSuites.js:260: * TODO: Expose elsewhere as a utility API.
  - ./slack-intelligence-service/node_modules/node-forge/lib/log.js:135:    // FIXME implement 'standardFull' logging
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:268:        // TODO: support arbitrary bit length ids
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:283:        // TODO: support arbitrary bit length ids
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:1058:      // TODO: support arbitrary bit length ids
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:1076:      // TODO: support arbitrary bit length ids
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:1129:    // TODO: get signature OID from private key
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:1793:    // TODO: get signature OID from private key
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:1880:      // FIXME: handle more encodings
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:2373:    // FIXME: handle more encodings
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:2465:          // TODO: support arbitrary bit length ids
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:2477:          // TODO: support arbitrary bit length ids
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:2675:      // TODO: resolve multiple matches by checking
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:2677:      // FIXME: or alternatively do authority key mapping
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:2982:    3. TODO: The certificate has not been revoked.
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:2984:    5. TODO: If the certificate is self-issued and not the final certificate
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:2990:    6. TODO: If the certificate is self-issued and not the final certificate
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:3052:          // TODO: we might want to reconsider renaming 'now' to
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:3071:        // FIXME: current CA store implementation might have multiple
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:3075:        // TODO: there's may be an extreme degenerate case currently uncovered
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:3113:    // TODO: 3. check revoked
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:3124:    // 5. TODO: check names with permitted names tree
  - ./slack-intelligence-service/node_modules/node-forge/lib/x509.js:3126:    // 6. TODO: check names against excluded names tree
  - ./slack-intelligence-service/node_modules/node-forge/lib/prng.js:413:      // TODO: do we need to remove the event listener when the worker dies?
  - ./slack-intelligence-service/node_modules/node-forge/lib/prime.worker.js:33:  // TODO: abstract based on data.algorithm (PRIMEINC vs. others)
  - ./slack-intelligence-service/node_modules/node-forge/lib/kem.js:100:// TODO: add forge.kem.kdf.create('KDF1', {md: ..., ...}) API?
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:220:    // TODO: copy byte buffer if it's a buffer not a string
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:222:    // TODO: add readonly flag to avoid this overhead
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:250:    // TODO: copy byte buffer if it's a buffer not a string
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:262:    // TODO: copy byte buffer if it's a buffer not a string
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:327:  // TODO: move this function and related DER/BER functions to a der.js
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:376:  // TODO: move this function and related DER/BER functions to a der.js
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:398:  // FIXME: this will only happen for 32 bit getInt with high bit set
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:559:    // FIXME: OCTET STRINGs not yet supported here
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:615:    // TODO: do DER to OID conversion and vice-versa in .toDer?
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:699:      // TODO: should all leading bytes be stripped vs just one?
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:1018:  // TODO: validate; currently assumes proper format
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:1054:  // TODO: validate; currently assumes proper format
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:1203:            // FIXME: support unused bits with data shifting
  - ./slack-intelligence-service/node_modules/node-forge/lib/asn1.js:1389:      // TODO: shift bits as needed to display without padding
  - ./slack-intelligence-service/node_modules/node-forge/lib/cipherModes.js:893:  // TODO: There are further optimizations that would use only the
  - ./slack-intelligence-service/node_modules/node-forge/lib/xhr.js:84:// TODO: provide optional clean up API for non-default clients
  - ./slack-intelligence-service/node_modules/node-forge/lib/xhr.js:207:    // FIXME: should a null domain cookie be added to all clients? should
  - ./slack-intelligence-service/node_modules/node-forge/lib/xhr.js:429:    // TODO: not implemented (not used yet)
  - ./slack-intelligence-service/node_modules/node-forge/lib/xhr.js:454:    // TODO: other validation steps in algorithm are not implemented
  - ./slack-intelligence-service/node_modules/node-forge/lib/xhr.js:498:    // TODO: other validation steps in spec aren't implemented
  - ./slack-intelligence-service/node_modules/node-forge/lib/xhr.js:560:      // TODO: update document.cookie with any cookies where the
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:361:   // FIXME: implement me for TLS 1.2
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:832:      // TODO: make extension support modular
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:877:      // FIXME: should be checking configured acceptable cipher suites
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:884:        // FIXME: should be checking configured acceptable suites
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:906:    // TODO: handle compression methods
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:930:  // TODO: handle other options from server when more supported
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:1444:    // TODO: support Diffie-Hellman
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:1492:  // TODO: TLS 1.2+ has different format including
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:1541:  // TODO: add support for DSA
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:1823:  // TODO: determine prf function and verify length for TLS 1.2
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:1898:  // TODO: consider using a table?
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:2361:  // TODO: TLS 1.2 implementation
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:2727:  // FIXME: deflate support disabled until issues with raw deflate data
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:2865:  // TODO: check certificate request to ensure types are supported
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:3200:  // TODO: support other certificate types
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:3216:  // TODO: TLS 1.2+ has a different format
  - ./slack-intelligence-service/node_modules/node-forge/lib/tls.js:3300:  // TODO: determine prf function and verify length for TLS 1.2
  - ./slack-intelligence-service/node_modules/node-forge/lib/http.js:32:  // TODO: include browser in ID to avoid sharing cookies between
  - ./slack-intelligence-service/node_modules/node-forge/lib/http.js:55:      // TODO: i assume we want this logged somewhere or
  - ./slack-intelligence-service/node_modules/node-forge/lib/http.js:75:      // TODO: i assume we want this logged somewhere or
  - ./slack-intelligence-service/node_modules/node-forge/lib/http.js:81:  // FIXME: remove me
  - ./slack-intelligence-service/node_modules/node-forge/lib/http.js:99:      // TODO: i assume we want this logged somewhere or
  - ./slack-intelligence-service/node_modules/node-forge/lib/ed25519.js:94:  // manually extract the private key bytes from nested octet string, see FIXME:
  - ./slack-intelligence-service/node_modules/node-forge/lib/ed25519.js:100:  // TODO: RFC8410 specifies a format for encoding the public key bytes along
  - ./slack-intelligence-service/node_modules/node-forge/lib/ed25519.js:233:      // TODO: more rigorous validation that `md` is a MessageDigest
  - ./slack-intelligence-service/node_modules/node-forge/lib/ed25519.js:287:// TODO: update forge buffer implementation to use `Buffer` or `Uint8Array`,
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs7.js:129:    // TODO: add json-formatted signer stuff here?
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs7.js:152:      // TODO: parse crls
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs7.js:167:      // TODO: implement CRLs
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs7.js:233:     * TODO: Support [subjectKeyIdentifier] as signer's ID.
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs7.js:423:        // TODO: optimize to just copy message digest state if that
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs7.js:523:          // TODO: optimize away duplication
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs7.js:939:  // TODO: convert attributes
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs7.js:1050:  // TODO: generalize to support more attributes
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs7.js:1065:    // TODO: make these module-level constants
  - ./slack-intelligence-service/node_modules/node-forge/lib/pkcs7.js:1094:  // TODO: expose as common API call
  - ./slack-intelligence-service/node_modules/pirates/README.md:45:  // TODO: Implement your logic here
  - ./slack-intelligence-service/node_modules/@types/lodash/common/object.d.ts:1901:    // TODO: Probably should just put all these methods on Object and forget about it.
  - ./slack-intelligence-service/node_modules/@types/express-serve-static-core/index.d.ts:101:    : Route extends `${string}(${string}` ? ParamsDictionary // TODO: handling for regex parameters
  - ./slack-intelligence-service/node_modules/@types/node/compatibility/iterators.d.ts:6:// TODO: remove once this package no longer supports TS 5.5, and replace NodeJS.BuiltinIteratorReturn with BuiltinIteratorReturn.
  - ./slack-intelligence-service/node_modules/@types/node/compatibility/disposable.d.ts:2:// TODO: remove once this package no longer supports TS 5.1, and replace with a
  - ./slack-intelligence-service/node_modules/@types/node/test.d.ts:177:             * Shorthand for marking a suite as `TODO`. This is the same as calling {@link suite} with `options.todo` set to `true`.
  - ./slack-intelligence-service/node_modules/@types/node/test.d.ts:202:         * Shorthand for marking a test as `TODO`. This is the same as calling {@link test} with `options.todo` set to `true`.
  - ./slack-intelligence-service/node_modules/@types/node/test.d.ts:906:             * This function adds a `TODO` directive to the test's output. If `message` is
  - ./slack-intelligence-service/node_modules/@types/node/test.d.ts:912:             *   // This test is marked as `TODO`
  - ./slack-intelligence-service/node_modules/@types/node/test.d.ts:917:             * @param message Optional `TODO` message.
  - ./slack-intelligence-service/node_modules/@types/node/test.d.ts:991:             * If truthy, the test marked as `TODO`. If a string is provided, that string is displayed in
  - ./slack-intelligence-service/node_modules/@types/node/test.d.ts:992:             * the test results as the reason why the test is `TODO`.
  - ./slack-intelligence-service/node_modules/@types/node/perf_hooks.d.ts:99:        readonly detail?: NodeGCPerformanceDetail | unknown | undefined; // TODO: Narrow this based on entry type.
  - ./slack-intelligence-service/node_modules/@types/node/util.d.ts:107:    export type CustomInspectFunction = (depth: number, options: InspectOptionsStylized) => any; // TODO: , inspect: inspect
  - ./slack-intelligence-service/node_modules/@types/node/wasi.d.ts:159:        start(instance: object): number; // TODO: avoid DOM dependency until WASM moved to own lib.
  - ./slack-intelligence-service/node_modules/@types/node/wasi.d.ts:169:        initialize(instance: object): void; // TODO: avoid DOM dependency until WASM moved to own lib.
  - ./slack-intelligence-service/node_modules/@types/node/wasi.d.ts:176:        readonly wasiImport: NodeJS.Dict<any>; // TODO: Narrow to DOM types
  - ./slack-intelligence-service/node_modules/@types/node/fs/promises.d.ts:94:    // TODO: Add `EventEmitter` close
  - ./slack-intelligence-service/node_modules/istanbul-lib-source-maps/node_modules/debug/src/browser.js:111: * TODO: add a `localStorage` variable to explicitly enable/disable colors
  - ./slack-intelligence-service/node_modules/jest-worker/build/workers/ChildProcessWorker.js:246:    // TODO: Add appropriate type check
  - ./slack-intelligence-service/node_modules/jest-worker/build/workers/ChildProcessWorker.js:296:      // TODO: At some point it would make sense to make use of
  - ./slack-intelligence-service/node_modules/jest-worker/build/workers/NodeThreadsWorker.js:282:      // TODO: At some point it would make sense to make use of
  - ./slack-intelligence-service/node_modules/ts-api-utils/lib/index.js:1237:    // TODO handle type-only imports
  - ./slack-intelligence-service/node_modules/ts-api-utils/lib/index.js:1354:    // TODO this actually references a parameter
  - ./slack-intelligence-service/node_modules/ts-api-utils/lib/index.cjs:1243:    // TODO handle type-only imports
  - ./slack-intelligence-service/node_modules/ts-api-utils/lib/index.cjs:1360:    // TODO this actually references a parameter
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/commands/CLUSTER_NODES.js:37:                    // TODO: importing & exporting (https://redis.io/commands/cluster-nodes#special-slot-entries)
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/client/index.js:172:        // TODO: consider breaking in v5
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/client/socket.js:208:        socket: net.connect(__classPrivateFieldGet(this, _RedisSocket_options, "f")) // TODO
  - ./slack-intelligence-service/node_modules/@redis/client/dist/lib/client/socket.js:213:        socket: tls.connect(__classPrivateFieldGet(this, _RedisSocket_options, "f")) // TODO
  - ./slack-intelligence-service/node_modules/mimic-fn/index.js:12:// TODO: Remove this for the next major release
  - ./slack-intelligence-service/node_modules/mimic-fn/index.d.ts:41:	// TODO: Remove this for the next major release, refactor the whole definition to:
  - ./slack-intelligence-service/node_modules/pkg-dir/node_modules/p-locate/index.js:51:// TODO: Remove this for the next major release
  - ./slack-intelligence-service/node_modules/pkg-dir/node_modules/p-locate/index.d.ts:54:	// TODO: Remove this for the next major release, refactor the whole definition to:
  - ./slack-intelligence-service/node_modules/pkg-dir/index.js:11:// TODO: Remove this for the next major release
  - ./slack-intelligence-service/node_modules/pkg-dir/index.d.ts:40:	// TODO: Remove this for the next major release
  - ./slack-intelligence-service/node_modules/@jest/fake-timers/build/legacyFakeTimers.js:452:      // TODO: Use performance.now() once it's mocked
  - ./slack-intelligence-service/node_modules/@jest/reporters/build/generateEmptyCoverage.js:138:    // TODO: consider passing AST
  - ./slack-intelligence-service/node_modules/@jest/transform/build/ScriptTransformer.js:824:// TODO: do we need to define the generics twice?
  - ./slack-intelligence-service/node_modules/eslint-scope/dist/eslint-scope.cjs:1002:        // TODO(Constellation)
  - ./slack-intelligence-service/node_modules/eslint-scope/dist/eslint-scope.cjs:1525:// FIXME: Now, we don't create module environment, because the context is
  - ./slack-intelligence-service/node_modules/eslint-scope/dist/eslint-scope.cjs:2084:    // TODO: ExportDeclaration doesn't exist. for bc?
  - ./slack-intelligence-service/node_modules/eslint-scope/dist/eslint-scope.cjs:2103:        // TODO: `node.id` doesn't exist. for bc?
  - ./slack-intelligence-service/node_modules/eslint-scope/lib/referencer.js:62:// FIXME: Now, we don't create module environment, because the context is
  - ./slack-intelligence-service/node_modules/eslint-scope/lib/referencer.js:621:    // TODO: ExportDeclaration doesn't exist. for bc?
  - ./slack-intelligence-service/node_modules/eslint-scope/lib/referencer.js:640:        // TODO: `node.id` doesn't exist. for bc?
  - ./slack-intelligence-service/node_modules/eslint-scope/lib/scope.js:668:        // TODO(Constellation)
  - ./slack-intelligence-service/node_modules/type-fest/source/require-exactly-one.d.ts:1:// TODO: Remove this when we target TypeScript >=3.5.
  - ./slack-intelligence-service/node_modules/type-fest/source/basic.d.ts:3:// TODO: This can just be `export type Primitive = not object` when the `not` keyword is out.
  - ./slack-intelligence-service/node_modules/type-fest/source/basic.d.ts:16:// TODO: Remove the `= unknown` sometime  in the future when most users are on TS 3.5 as it's now the default
  - ./slack-intelligence-service/node_modules/joi/lib/index.d.ts:10:// TODO express type of Schema in a type-parameter (.default, .valid, .example etc)
  - ./slack-intelligence-service/node_modules/joi/lib/index.d.ts:1610:        // TODO: support number and symbol index
  - ./slack-intelligence-service/node_modules/side-channel-list/index.js:111:	// @ts-expect-error TODO: figure out why this is erroring
  - ./slack-intelligence-service/node_modules/@eslint/eslintrc/node_modules/minimatch/minimatch.js:491:        // TODO: It would probably be faster to determine this
  - ./slack-intelligence-service/node_modules/@eslint/eslintrc/node_modules/debug/src/browser.js:111: * TODO: add a `localStorage` variable to explicitly enable/disable colors
  - ./slack-intelligence-service/node_modules/jest-cli/node_modules/yargs-parser/build/lib/index.js:37:    // TODO: figure  out a  way to combine ESM and CJS coverage, such  that
  - ./slack-intelligence-service/node_modules/jest-cli/node_modules/yargs-parser/build/lib/yargs-parser.js:167:        // TODO(bcoe): for the first pass at removing object prototype  we didn't
  - ./slack-intelligence-service/node_modules/jest-cli/node_modules/yargs-parser/build/lib/yargs-parser.js:753:                // TODO(bcoe): in the next major version of yargs, switch to
  - ./slack-intelligence-service/node_modules/jest-cli/node_modules/yargs-parser/build/lib/yargs-parser.js:774:            // TODO(bcoe): in the next major version of yargs, switch to
  - ./slack-intelligence-service/node_modules/jest-cli/node_modules/yargs-parser/build/lib/yargs-parser.js:1032:// TODO(bcoe): in the next major version of yargs, switch to
  - ./slack-intelligence-service/node_modules/jest-cli/node_modules/yargs-parser/browser.js:4:// TODO: figure out reasonable web equivalents for "resolve", "normalize", etc.
  - ./slack-intelligence-service/node_modules/jest-cli/node_modules/cliui/build/lib/string-utils.js:3:// TODO: look at porting https://www.npmjs.com/package/wrap-ansi to ESM.
  - ./slack-intelligence-service/node_modules/jest-cli/node_modules/yargs/yargs.mjs:1:// TODO: consolidate on using a helpers file at some point in the future, which
  - None found

## Large Files (top 20 by size)
  - 923M	.
  - 217M	./gmail-intelligence-service/node_modules
  - 217M	./gmail-intelligence-service
  - 182M	./slack-intelligence-service
  - 181M	./slack-intelligence-service/node_modules
  - 172M	./xynergyos-intelligence-gateway
  - 171M	./xynergyos-intelligence-gateway/node_modules
  - 167M	./crm-engine
  - 166M	./crm-engine/node_modules
  - 117M	./permission-service/node_modules
  - 117M	./permission-service
  - 101M	./gmail-intelligence-service/node_modules/googleapis
  - 100M	./gmail-intelligence-service/node_modules/googleapis/build/src/apis
  - 100M	./gmail-intelligence-service/node_modules/googleapis/build/src
  - 100M	./gmail-intelligence-service/node_modules/googleapis/build
  -  57M	./.git
  -  48M	./.git/objects/pack
  -  48M	./.git/objects
  -  47M	./.git/objects/pack/pack-4c26f364ba75cb5f2453a71aceb6175fcbed4789.pack
  -  23M	./xynergyos-intelligence-gateway/node_modules/typescript/lib

## Notes
- Static scan; runtime behavior and feature flags may not be fully captured.
