# Xynergy Platform - Autonomous Business Operations

AI-powered microservices platform for automated marketing, content generation, analytics, and business operations on Google Cloud Platform.

## Overview

The Xynergy Platform is a comprehensive suite of 20+ specialized microservices that handle autonomous business operations including marketing campaign generation, content creation, analytics processing, and AI-powered decision making.

## Architecture

### Core Services

**Platform Management**
- `platform-dashboard` - Central monitoring and control interface
- `system-runtime` - Core platform orchestration
- `security-governance` - Security policies and compliance
- `tenant-management` - Multi-tenant account management

**AI & Intelligence**
- `ai-routing-engine` - Intelligent AI request routing (Abacus → OpenAI → Internal)
- `ai-providers` - External AI API integration (Abacus AI and OpenAI)
- `internal-ai-service` - Internal AI model hosting
- `ai-assistant` - Conversational AI interface
- `aso-engine` - Adaptive Search Optimization engine

**Marketing & Content**
- `marketing-engine` - AI-powered marketing campaign generation
- `content-hub` - Content management and storage
- `rapid-content-generator` - Fast content creation
- `automated-publisher` - Content distribution automation
- `competitive-analysis-service` - Market intelligence

**Analytics & Reporting**
- `analytics-data-layer` - Data processing and analytics
- `reports-export` - Report generation and export
- `advanced-analytics` - Advanced metrics and insights
- `keyword-revenue-tracker` - SEO performance tracking

**Operations**
- `project-management` - Project tracking and coordination
- `scheduler-automation-engine` - Task scheduling and automation
- `qa-engine` - Quality assurance and testing

### Supporting Services

- `xynergy-intelligence-gateway` - Public-facing API for ClearForge.ai
- `tenant-onboarding-service` - Automated tenant onboarding
- `research-coordinator` - Research task orchestration
- `validation-coordinator` - Data validation pipeline
- `trending-engine-coordinator` - Trending content analysis
- `attribution-coordinator` - Attribution tracking

## Technology Stack

- **Backend**: Python 3.11, FastAPI
- **Cloud Platform**: Google Cloud Platform (GCP)
- **Infrastructure**: Terraform, Docker
- **Data Storage**: Firestore, BigQuery, Cloud Storage
- **Messaging**: Cloud Pub/Sub
- **Caching**: Redis
- **Deployment**: Cloud Run, Cloud Build

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Google Cloud SDK
- Terraform 1.5+
- GCP Project with billing enabled

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd xynergy-platform
```

2. **Set up environment variables**
```bash
export PROJECT_ID=xynergy-dev-1757909467
export REGION=us-central1
export GCP_PROJECT=$PROJECT_ID
```

3. **Run a service locally**
```bash
cd <service-directory>
pip install -r requirements.txt
python main.py
```

4. **Build and run with Docker**
```bash
cd <service-directory>
docker build -t xynergy-<service-name> .
docker run -p 8080:8080 xynergy-<service-name>
```

### Infrastructure Setup

```bash
cd terraform/
terraform init
terraform plan
terraform apply
```

## Service Communication

- **Pub/Sub**: Asynchronous messaging via `<service>-events` topics
- **HTTP APIs**: Direct service-to-service REST communication
- **Health Checks**: All services expose `/health` endpoint

## Key Features

- **AI Cost Optimization**: 89% cost reduction through intelligent routing
- **Multi-Tenancy**: Full tenant isolation with per-tenant cost tracking
- **Auto-Scaling**: Cloud Run auto-scaling based on demand
- **Circuit Breakers**: Fault-tolerant external API calls
- **Caching**: Redis-based caching for performance
- **Monitoring**: Structured logging and performance tracking

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - AI assistant guidance for this codebase
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture documentation
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Deployment procedures
- **[API_INTEGRATION_GUIDE.md](API_INTEGRATION_GUIDE.md)** - API integration guide
- **[COST_OPTIMIZATION_TRACKING.md](COST_OPTIMIZATION_TRACKING.md)** - Cost monitoring
- **[SECURITY_FIXES.md](SECURITY_FIXES.md)** - Security best practices
- **[LOCAL_INTEGRATION_ANALYSIS.md](LOCAL_INTEGRATION_ANALYSIS.md)** - Local integration guide

### Service-Specific Documentation

- **[xynergy-intelligence-gateway/README.md](xynergy-intelligence-gateway/README.md)** - Intelligence Gateway API
- **[tenant-onboarding-service/IMPLEMENTATION_SUMMARY.md](tenant-onboarding-service/IMPLEMENTATION_SUMMARY.md)** - Onboarding automation

## Configuration

All services use consistent environment variables:

- `PROJECT_ID` - GCP project ID (default: xynergy-dev-1757909467)
- `REGION` - GCP region (default: us-central1)
- `PORT` - Service port (default: 8080)
- `ENVIRONMENT` - Environment name (development/staging/production)

## Testing

Each service includes health check endpoints:

```bash
curl http://localhost:8080/health
```

For specific service testing, see individual service README files.

## Archive

Historical documentation, deployment scripts, and phase reports have been moved to the [archive/](archive/) folder for reference. See [archive/README.md](archive/README.md) for details.

## Security

- **CORS**: Configured per-service with explicit allowed origins
- **Authentication**: API key validation for all sensitive endpoints
- **Input Validation**: Pydantic models for all user inputs
- **Circuit Breakers**: Protection against cascading failures
- **Rate Limiting**: Per-endpoint throttling

## Support

For issues, questions, or contributions:

1. Check service-specific documentation
2. Review [CLAUDE.md](CLAUDE.md) for development guidance
3. See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common tasks

## License

Copyright © 2024 Xynergy Platform. All rights reserved.
