# Xynergy Platform API Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Service Discovery](#service-discovery)
4. [Core API Patterns](#core-api-patterns)
5. [Service-Specific APIs](#service-specific-apis)
6. [Workflow Orchestration](#workflow-orchestration)
7. [Real-time Communication](#real-time-communication)
8. [Error Handling & Circuit Breakers](#error-handling--circuit-breakers)
9. [Dashboard Integration Patterns](#dashboard-integration-patterns)
10. [SDK Usage Examples](#sdk-usage-examples)

## Overview

The Xynergy Platform is a microservices-based AI platform built on Google Cloud Platform, consisting of 15+ specialized services that handle autonomous business operations. This guide provides comprehensive documentation for integrating with the platform APIs to build management dashboards and external applications.

### Platform Architecture
- **Microservices**: 15+ independent services with REST APIs
- **Communication**: HTTP APIs + Pub/Sub messaging + WebSocket real-time
- **Authentication**: API key-based authentication with HTTPBearer
- **Security**: Hardened CORS, rate limiting, circuit breakers
- **Optimization**: AI routing for 89% cost savings, connection pooling, caching

### Base URLs
All services follow the pattern: `https://xynergy-{service-name}-*.us-central1.run.app`

**Core Services:**
- Platform Dashboard: `:8080`
- Marketing Engine: `:8081`
- AI Assistant: `:8082`
- Content Hub: `:8083`
- System Runtime: `:8084`
- AI Routing Engine: `:8085`

## Authentication

### API Key Authentication

All protected endpoints require API key authentication via HTTPBearer tokens.

**Request Headers:**
```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
X-API-Key: YOUR_API_KEY (optional backup)
```

**Authentication Flow:**
```python
import httpx

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

async with httpx.AsyncClient() as client:
    response = await client.get(
        "https://xynergy-platform-dashboard.us-central1.run.app/api/platform-status",
        headers=headers
    )
```

### CORS Configuration

The platform uses strict CORS policies. Allowed origins:
- `https://xynergy.com`
- `https://*.xynergy.com`
- `http://localhost:*` (development only)

### Rate Limiting

Most endpoints implement rate limiting:
- **Public endpoints**: 10-30 requests/minute
- **Authenticated endpoints**: 100-500 requests/minute
- **WebSocket connections**: 1 per client

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Service Discovery

### Health Check Pattern

Every service implements standardized health checks at `GET /health`:

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "platform-dashboard-v2",
  "timestamp": "2025-01-19T10:30:00.000Z",
  "version": "2.0.0",
  "features": ["circuit_breakers", "ml_routing", "performance_monitoring"]
}
```

### Service Registry

Query the platform dashboard for service discovery:

**Request:**
```http
GET /api/platform-status
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "platform_metrics": {
    "total_services": 15,
    "healthy_services": 14,
    "ai_routing_efficiency": 78,
    "cost_savings": 89,
    "phase_1_optimizations": true
  },
  "services": {
    "marketing-engine": {
      "status": "healthy",
      "url": "https://xynergy-marketing-engine-*.us-central1.run.app",
      "capabilities": ["campaign_generation", "market_analysis"],
      "last_health_check": "2025-01-19T10:29:30.000Z"
    }
  },
  "timestamp": "2025-01-19T10:30:00.000Z"
}
```

## Core API Patterns

### Universal Execute Endpoint

Every service implements `POST /execute` for workflow orchestration:

**Request:**
```http
POST /execute
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "action": "analyze_market",
  "parameters": {
    "business_type": "SaaS",
    "target_market": "enterprise",
    "budget": "50000"
  },
  "workflow_context": {
    "workflow_id": "wf_123456789",
    "step_id": "market_analysis_1",
    "user_id": "user_123"
  }
}
```

**Response:**
```json
{
  "success": true,
  "action": "analyze_market",
  "output": {
    "market_size": "$2.5B",
    "competition_level": "moderate",
    "recommended_channels": ["google_ads", "linkedin", "content_marketing"]
  },
  "execution_time": 2.45,
  "service": "marketing-engine",
  "workflow_id": "wf_123456789"
}
```

### Error Response Format

Standardized error responses across all services:

```json
{
  "success": false,
  "error": "Invalid business type provided",
  "error_code": "VALIDATION_ERROR",
  "action": "analyze_market",
  "service": "marketing-engine",
  "timestamp": "2025-01-19T10:30:00.000Z"
}
```

## Service-Specific APIs

### Platform Dashboard API

**Get Platform Status:**
```http
GET /api/platform-status
Authorization: Bearer YOUR_API_KEY
```

**Execute Workflow Step:**
```http
POST /execute
Authorization: Bearer YOUR_API_KEY

{
  "action": "update_metrics",
  "parameters": {
    "report_id": "report_123",
    "metrics": {
      "total_campaigns": 45,
      "active_workflows": 12
    }
  }
}
```

### Marketing Engine API

**Generate Campaign:**
```http
POST /api/generate-campaign
Authorization: Bearer YOUR_API_KEY

{
  "business_type": "E-commerce",
  "target_audience": "millennials",
  "budget_range": "$10,000-$50,000",
  "campaign_goals": ["brand_awareness", "lead_generation"],
  "preferred_channels": ["social_media", "google_ads"]
}
```

**Response:**
```json
{
  "campaign_id": "camp_123456",
  "campaign_name": "Millennial Engagement Drive",
  "strategy": {
    "primary_message": "Sustainable fashion for conscious consumers",
    "creative_themes": ["sustainability", "authenticity"]
  },
  "recommended_channels": ["instagram", "tiktok", "google_ads"],
  "estimated_reach": 250000,
  "budget_allocation": {
    "instagram": 0.4,
    "tiktok": 0.3,
    "google_ads": 0.3
  }
}
```

### AI Routing Engine API

**Route AI Request:**
```http
POST /api/route-request
Authorization: Bearer YOUR_API_KEY

{
  "query": "Generate a marketing campaign for sustainable fashion",
  "context": {
    "user_id": "user_123",
    "session_id": "session_456"
  },
  "preferred_provider": "abacus"
}
```

**Response:**
```json
{
  "routing_id": "route_789",
  "selected_provider": "abacus_ai",
  "confidence": 0.95,
  "cost_estimate": 0.012,
  "fallback_providers": ["openai", "internal_ai"],
  "ai_response": {
    "content": "Here's your sustainable fashion campaign...",
    "tokens_used": 150
  }
}
```

### AI Assistant API

**Execute Business Intent:**
```http
POST /api/execute-intent
Authorization: Bearer YOUR_API_KEY

{
  "intent": "Create a comprehensive marketing campaign for our new sustainable clothing line",
  "context": {
    "company": "EcoFashion Co",
    "budget": "$25,000",
    "timeline": "Q2 2025"
  }
}
```

**Response:**
```json
{
  "workflow_id": "wf_marketing_123",
  "status": "executing",
  "estimated_completion": "2025-01-19T10:45:00.000Z",
  "steps": [
    {
      "service": "marketing-engine",
      "action": "analyze_market",
      "status": "completed"
    },
    {
      "service": "content-hub",
      "action": "generate_assets",
      "status": "in_progress"
    }
  ]
}
```

## Workflow Orchestration

### Create Workflow

**Request:**
```http
POST /api/create-workflow
Authorization: Bearer YOUR_API_KEY

{
  "workflow_name": "Complete Marketing Campaign",
  "steps": [
    {
      "step_id": "market_analysis",
      "service": "marketing-engine",
      "action": "analyze_market",
      "parameters": {
        "business_type": "SaaS",
        "target_market": "enterprise"
      }
    },
    {
      "step_id": "content_generation",
      "service": "content-hub",
      "action": "generate_campaign_assets",
      "depends_on": ["market_analysis"],
      "parameters": {
        "asset_types": ["blog_posts", "social_media", "email_templates"]
      }
    }
  ]
}
```

### Monitor Workflow Status

**Request:**
```http
GET /api/workflow/{workflow_id}/status
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "workflow_id": "wf_123456",
  "status": "executing",
  "progress": 0.6,
  "completed_steps": 3,
  "total_steps": 5,
  "current_step": "content_generation",
  "estimated_completion": "2025-01-19T10:45:00.000Z",
  "results": {
    "market_analysis": {
      "market_size": "$2.5B",
      "competition_level": "moderate"
    }
  }
}
```

## Real-time Communication

### WebSocket Connections

Connect to real-time updates via WebSocket:

**Connection:**
```javascript
const ws = new WebSocket('wss://xynergy-platform-dashboard.us-central1.run.app/ws/platform');

ws.onopen = function(event) {
    console.log('Connected to platform updates');

    // Authenticate
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'YOUR_API_KEY'
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Platform update:', data);
};
```

**Message Types:**
```json
{
  "type": "workflow_update",
  "workflow_id": "wf_123456",
  "status": "completed",
  "step": "content_generation",
  "timestamp": "2025-01-19T10:30:00.000Z"
}

{
  "type": "service_status",
  "service": "marketing-engine",
  "status": "healthy",
  "metrics": {
    "requests_per_minute": 45,
    "average_response_time": 250
  }
}
```

### Pub/Sub Event Streaming

Subscribe to platform events via Pub/Sub:

**Topic:** `xynergy-platform-events`

**Event Structure:**
```json
{
  "event_type": "business_intent_executed",
  "event_id": "evt_123456",
  "workflow_id": "wf_789012",
  "service": "ai-assistant",
  "timestamp": "2025-01-19T10:30:00.000Z",
  "data": {
    "intent": "Create marketing campaign",
    "execution_time": 45.2,
    "services_used": ["marketing-engine", "content-hub", "ai-routing-engine"]
  }
}
```

## Error Handling & Circuit Breakers

### Circuit Breaker Status

Check circuit breaker status across services:

**Request:**
```http
GET /api/circuit-breaker-status
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "circuit_breakers": {
    "bigquery_service": {
      "state": "CLOSED",
      "failure_count": 0,
      "last_failure": null
    },
    "external_ai_service": {
      "state": "HALF_OPEN",
      "failure_count": 3,
      "last_failure": "2025-01-19T10:25:00.000Z",
      "next_attempt": "2025-01-19T10:35:00.000Z"
    }
  }
}
```

### Error Recovery

Handle circuit breaker failures:

```python
async def call_with_fallback(primary_service, fallback_service, payload):
    try:
        return await primary_service.call(payload)
    except CircuitBreakerOpen:
        return await fallback_service.call(payload)
    except Exception as e:
        # Log error and return graceful degradation
        return {"error": "Service temporarily unavailable"}
```

## Dashboard Integration Patterns

### Real-time Dashboard Updates

**1. Service Health Monitoring:**
```javascript
// Poll service health every 30 seconds
setInterval(async () => {
    const response = await fetch('/api/platform-status', {
        headers: { 'Authorization': `Bearer ${apiKey}` }
    });
    const status = await response.json();
    updateServiceCards(status.services);
}, 30000);
```

**2. Workflow Progress Tracking:**
```javascript
// WebSocket for real-time workflow updates
ws.onmessage = function(event) {
    const update = JSON.parse(event.data);
    if (update.type === 'workflow_update') {
        updateWorkflowProgress(update.workflow_id, update);
    }
};
```

**3. Performance Metrics:**
```javascript
// Fetch and display performance metrics
async function loadMetrics() {
    const metrics = await fetch('/api/performance-metrics', {
        headers: { 'Authorization': `Bearer ${apiKey}` }
    }).then(r => r.json());

    updateCharts({
        aiRoutingEfficiency: metrics.ai_routing_efficiency,
        costSavings: metrics.cost_savings,
        requestVolume: metrics.request_volume
    });
}
```

### Aggregated Status API

Single endpoint for dashboard overview:

**Request:**
```http
GET /api/dashboard-overview
Authorization: Bearer YOUR_API_KEY
```

**Response:**
```json
{
  "platform_health": {
    "overall_status": "healthy",
    "healthy_services": 14,
    "total_services": 15,
    "unhealthy_services": ["external-integration-temp-down"]
  },
  "active_workflows": 23,
  "completed_today": 145,
  "cost_metrics": {
    "savings_percentage": 89,
    "total_cost_today": "$45.23",
    "projected_monthly": "$1,356.90"
  },
  "ai_routing": {
    "abacus_percentage": 78,
    "openai_percentage": 15,
    "internal_percentage": 7
  },
  "performance": {
    "average_response_time": 245,
    "requests_per_minute": 342,
    "success_rate": 99.7
  }
}
```

## SDK Usage Examples

### Basic SDK Initialization

```python
from xynergy_sdk import XynergyPlatformSDK

# Initialize SDK
sdk = XynergyPlatformSDK(
    api_key="your_api_key",
    base_url="https://xynergy-platform-dashboard.us-central1.run.app"
)

# Health check
health = await sdk.get_platform_health()
print(f"Platform status: {health.overall_status}")
```

### Execute Business Intent

```python
# Execute a business intent through the platform
result = await sdk.execute_business_intent(
    intent="Create a marketing campaign for sustainable fashion",
    context={
        "company": "EcoFashion Co",
        "budget": "$25,000",
        "timeline": "Q2 2025"
    }
)

print(f"Workflow ID: {result.workflow_id}")
print(f"Status: {result.status}")
```

### Real-time Monitoring

```python
# Subscribe to platform events
def on_workflow_update(event):
    print(f"Workflow {event.workflow_id} status: {event.status}")

await sdk.subscribe_to_events(on_workflow_update)

# Monitor specific workflow
workflow_status = await sdk.get_workflow_status("wf_123456")
print(f"Progress: {workflow_status.progress}%")
```

### Dashboard Data Aggregation

```python
# Get comprehensive dashboard data
dashboard_data = await sdk.get_dashboard_overview()

# Service health
for service, health in dashboard_data.services.items():
    print(f"{service}: {health.status}")

# Performance metrics
metrics = dashboard_data.performance
print(f"Response time: {metrics.average_response_time}ms")
print(f"Success rate: {metrics.success_rate}%")

# Cost optimization
cost = dashboard_data.cost_metrics
print(f"Cost savings: {cost.savings_percentage}%")
```

---

## Best Practices

1. **Always use circuit breakers** for external service calls
2. **Implement exponential backoff** for retry logic
3. **Cache responses** appropriately (1-hour for AI, 15-min for analytics)
4. **Use WebSocket** for real-time updates instead of polling
5. **Monitor rate limits** and implement client-side throttling
6. **Handle graceful degradation** when services are unavailable
7. **Use connection pooling** for HTTP clients
8. **Implement proper error logging** with structured data

## Rate Limits & Quotas

- **Health checks**: 30 requests/minute
- **Execute endpoints**: 100 requests/minute
- **Workflow creation**: 10 requests/minute
- **Dashboard API**: 500 requests/minute
- **WebSocket connections**: 1 per client
- **Pub/Sub messages**: 1000 messages/minute

## Security Considerations

- **Never expose API keys** in client-side code
- **Use HTTPS only** for all communications
- **Implement request signing** for sensitive operations
- **Validate all inputs** before sending to APIs
- **Monitor for unusual patterns** in API usage
- **Rotate API keys** regularly
- **Use environment-specific keys** (dev/staging/prod)

---

*For additional support or questions, refer to the platform documentation or contact the Xynergy development team.*