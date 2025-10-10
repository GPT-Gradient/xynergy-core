# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Xynergy Platform - AI-Powered Business Operations

This is a microservices-based AI platform built on Google Cloud Platform, consisting of 20+ specialized services that handle autonomous business operations including marketing, content generation, analytics, and project management.

## Architecture Overview

### Service Structure
The platform follows a consistent microservice pattern where each service is:
- **Python-based**: All services use FastAPI with Python 3.11
- **Containerized**: Each service has its own Dockerfile and requirements.txt
- **Self-contained**: Complete service implementation in a single main.py file
- **GCP-native**: Integrates with Pub/Sub, BigQuery, Cloud Storage, and Firestore

### Core Services

**Platform Management**
- `platform-dashboard`: Central monitoring and control interface
- `system-runtime`: Core platform orchestration
- `security-governance`: Security policies and compliance
- `tenant-management`: Multi-tenant account management

**AI & Intelligence**
- `ai-routing-engine`: Intelligent AI request routing (Abacus → OpenAI → Internal)
- `ai-providers`: External AI API integration (Abacus AI and OpenAI)
- `internal-ai-service`: Internal AI model hosting
- `ai-assistant`: Conversational AI interface
- `aso-engine`: Adaptive Search Optimization engine

**Marketing & Content**
- `marketing-engine`: AI-powered marketing campaign generation
- `content-hub`: Content management and storage
- `rapid-content-generator`: Fast content creation
- `automated-publisher`: Content distribution automation
- `competitive-analysis-service`: Market intelligence

**Analytics & Reporting**
- `analytics-data-layer`: Data processing and analytics
- `reports-export`: Report generation and export
- `advanced-analytics`: Advanced metrics and insights
- `keyword-revenue-tracker`: SEO performance tracking

**Operations**
- `project-management`: Project tracking and coordination
- `scheduler-automation-engine`: Task scheduling and automation
- `qa-engine`: Quality assurance and testing

### Supporting Services
- `xynergy-intelligence-gateway`: Public-facing API for ClearForge.ai
- `tenant-onboarding-service`: Automated tenant onboarding with CI/CD
- `research-coordinator`: Research task orchestration
- `validation-coordinator`: Data validation pipeline
- `trending-engine-coordinator`: Trending content analysis
- `attribution-coordinator`: Attribution tracking

### Infrastructure Pattern
- **Terraform**: Infrastructure as code in `/terraform/main.tf`
- **GCP Resources**: Pub/Sub topics, BigQuery datasets, Cloud Storage buckets
- **Service Account**: `xynergy-platform-sa` with appropriate permissions
- **Artifact Registry**: Container image storage

## Development Commands

### Building and Running Services
Each service can be run locally:
```bash
cd <service-directory>
pip install -r requirements.txt
python main.py
```

### Docker Development
Build and run individual services:
```bash
cd <service-directory>
docker build -t xynergy-<service-name> .
docker run -p 8080:8080 xynergy-<service-name>
```

### Infrastructure Management
```bash
cd terraform/
terraform init
terraform plan
terraform apply
```

## Key Patterns and Conventions

### Service Communication
- **Pub/Sub**: Asynchronous messaging between services via topics named `<service>-events`
- **HTTP APIs**: Direct service-to-service communication via REST endpoints
- **Health Checks**: All services expose `/health` endpoint

### Configuration
- **Environment Variables**: `PROJECT_ID` (default: xynergy-dev-1757909467), `REGION` (default: us-central1)
- **GCP Integration**: Services automatically use GCP client libraries with service account authentication

### Code Structure
- **Single File Services**: Each service implements its complete functionality in `main.py`
- **FastAPI Framework**: Consistent API structure across all services
- **CORS Enabled**: All services allow cross-origin requests
- **Embedded UIs**: Many services include embedded HTML/JavaScript interfaces

### AI Integration
- **Intelligent Routing**: The `ai-routing-engine` routes requests through: Abacus AI (primary) → OpenAI (fallback) → Internal AI (final fallback)
- **Multi-Provider Support**: `ai-providers` service integrates with Abacus AI and OpenAI APIs
- **Cost Optimization**: Platform tracks and optimizes AI usage costs (targeting ~89% cost reduction vs external APIs)
- **Hybrid Architecture**: Combines external AI services with internal model hosting for optimal cost/performance
- **Content Generation**: Multiple services leverage AI for automated content creation

### Data Storage
- **Firestore**: Primary database for service data and configurations
- **BigQuery**: Analytics and data warehouse (`xynergy_analytics` dataset)
- **Cloud Storage**: Content and report storage with lifecycle management

## Service Dependencies

### High-Level Flow
1. `platform-dashboard` → Central monitoring of all services
2. `marketing-engine` → `ai-routing-engine` → `internal-ai-service` or external APIs
3. `marketing-engine` → `content-hub` for content storage
4. All services → Pub/Sub for event broadcasting
5. All services → BigQuery for analytics data

### Inter-Service URLs
Services communicate via Cloud Run URLs following pattern:
`https://xynergy-<service-name>-*.us-central1.run.app`

## Testing and Quality

- **Health Checks**: Built into Docker containers and service endpoints
- **No Formal Test Suite**: Services rely on integration testing via health endpoints
- **Quality Assurance**: Handled by dedicated `qa-engine` service

## Optimization Guidelines

### Security Requirements (CRITICAL)
- **CORS Configuration**: NEVER use `allow_origins=["*"]` - always specify exact domains
  - ✅ Good: `allow_origins=["https://xynergy-platform.com", "https://*.xynergy.com"]`
  - ❌ Bad: `allow_origins=["*"]` - CRITICAL security vulnerability
- **Authentication**: All sensitive endpoints must use API key validation
- **Input Validation**: Use Pydantic models for all user inputs

### Performance & Cost Optimization
- **Connection Pooling**: Always use shared GCP clients (see `shared/gcp_clients.py`)
- **Resource Management**: Implement proper cleanup in `@app.on_event("shutdown")`
- **Database Queries**: Use partitioned tables and specific columns (avoid `SELECT *`)
- **Caching**: Implement Redis caching for AI responses and frequent queries
- **Circuit Breakers**: Use `CircuitBreaker` from `phase2_utils` for external calls

### Development Standards
- **Error Handling**: Always use structured error handling with proper fallbacks
- **Memory Management**: Clean up global state and connections
- **Monitoring**: Include performance tracking with `PerformanceMonitor`
- **Resource Limits**: Set appropriate CPU/memory limits in container configs

### Cost Control Measures
- **AI Routing**: Maintain intelligent routing (Abacus → OpenAI → Internal) for 89% cost savings
- **Resource Right-sizing**: Use monitoring data to optimize container allocations
- **Storage Lifecycle**: Implement proper lifecycle policies for Cloud Storage
- **Query Optimization**: Use BigQuery partitioning and clustering for cost efficiency

## Documentation Structure

### Active Documentation
- `README.md` - Main project documentation and quick start guide
- `CLAUDE.md` - This file - AI assistant guidance
- `ARCHITECTURE.md` - Detailed architecture documentation
- `DEPLOYMENT_GUIDE.md` - Deployment procedures and best practices
- `API_INTEGRATION_GUIDE.md` - API integration guide
- `COST_OPTIMIZATION_TRACKING.md` - Cost monitoring dashboard
- `SECURITY_FIXES.md` - Security best practices and guidelines
- `LOCAL_INTEGRATION_ANALYSIS.md` - Local development integration guide
- `QUICK_REFERENCE.md` - Common tasks and commands
- `AI_CONFIGURATION.md` - AI service configuration
- `XYNERGY_API_INTEGRATION_GUIDE.md` - External API integration
- `XYNERGY_SDK_README.md` - SDK documentation
- `project-state.md` - Current project status

### Service-Specific Documentation
- `xynergy-intelligence-gateway/README.md` - Intelligence Gateway API
- `xynergy-intelligence-gateway/TESTING_GUIDE.md` - Testing procedures
- `tenant-onboarding-service/README.md` - Onboarding service documentation
- `tenant-onboarding-service/IMPLEMENTATION_SUMMARY.md` - Implementation details
- `tenant-onboarding-service/TESTING_GUIDE.md` - Testing procedures

### Historical Documentation (Archive)
Phase reports, planning documents, deployment scripts, and historical files have been moved to `archive/` for reference:
- `archive/phase-reports/` - Completed phase status reports
- `archive/documentation/` - Historical planning and implementation docs
- `archive/deployment-scripts/` - One-time deployment and setup scripts
- `archive/utilities/` - Migration and testing scripts
- `archive/templates/` - Deprecated templates and examples

See `archive/README.md` for complete archive index and context.

## Important Notes

- **GCP Project**: Default project is `xynergy-dev-1757909467`
- **Region**: Services deployed to `us-central1`
- **Service Accounts**: Use `xynergy-platform-sa` for GCP resource access
- **Cost Optimization**: Platform emphasizes AI cost reduction through intelligent routing
- **Real-time Updates**: Many services include WebSocket support for live updates