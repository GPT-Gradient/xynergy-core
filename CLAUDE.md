# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Xynergy Platform - AI-Powered Business Operations

This is a microservices-based AI platform built on Google Cloud Platform, consisting of 11+ specialized services that handle autonomous business operations including marketing, content generation, analytics, and project management.

## Architecture Overview

### Service Structure
The platform follows a consistent microservice pattern where each service is:
- **Python-based**: All services use FastAPI with Python 3.11
- **Containerized**: Each service has its own Dockerfile and requirements.txt
- **Self-contained**: Complete service implementation in a single main.py file
- **GCP-native**: Integrates with Pub/Sub, BigQuery, Cloud Storage, and Firestore

### Core Services
- `platform-dashboard`: Central monitoring and control interface
- `marketing-engine`: AI-powered marketing campaign generation
- `ai-routing-engine`: Intelligent AI request routing (Abacus → OpenAI → internal)
- `ai-providers`: External AI API integration (Abacus AI and OpenAI)
- `ai-assistant`: Conversational AI interface
- `content-hub`: Content management and storage
- `analytics-data-layer`: Data processing and analytics
- `internal-ai-service`: Internal AI model hosting
- `system-runtime`: Core platform orchestration
- `scheduler-automation-engine`: Task scheduling and automation
- `reports-export`: Report generation and export
- `security-governance`: Security policies and compliance
- `qa-engine`: Quality assurance and testing
- `project-management`: Project tracking and management

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

## Optimization Documentation

Key optimization documents available:
- `OPTIMIZATION_PLAN.md` - Comprehensive optimization strategy
- `SECURITY_FIXES.md` - Critical security vulnerabilities and fixes
- `IMPLEMENTATION_ROADMAP.md` - 16-week implementation timeline
- `COST_OPTIMIZATION_TRACKING.md` - Cost monitoring and tracking dashboard

Target: 35-50% cost reduction while maintaining client experience priority.

## Important Notes

- **GCP Project**: Default project is `xynergy-dev-1757909467`
- **Region**: Services deployed to `us-central1`
- **Service Accounts**: Use `xynergy-platform-sa` for GCP resource access
- **Cost Optimization**: Platform emphasizes AI cost reduction through intelligent routing
- **Real-time Updates**: Many services include WebSocket support for live updates