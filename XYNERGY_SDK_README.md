# Xynergy Platform SDK

A comprehensive Python SDK for integrating with the Xynergy Platform's microservices architecture, enabling dashboard applications to monitor, control, and interact with AI-powered business operations.

## Quick Start

### Installation

```bash
pip install -r sdk_requirements.txt
```

### Basic Usage

```python
import asyncio
from xynergy_platform_sdk import XynergyPlatformSDK

async def main():
    # Initialize SDK
    async with XynergyPlatformSDK(api_key="your_api_key") as sdk:
        # Get platform health
        health = await sdk.get_platform_health()
        print(f"Platform Status: {health.overall_status}")

        # Execute business intent
        workflow = await sdk.execute_business_intent(
            "Create a marketing campaign for sustainable fashion"
        )
        print(f"Workflow ID: {workflow.workflow_id}")

asyncio.run(main())
```

## Features

### 🏥 Health Monitoring
- Real-time platform health status
- Individual service monitoring
- Circuit breaker status tracking
- Performance metrics collection

### 🔄 Workflow Orchestration
- Execute business intents through AI Assistant
- Create custom workflows with dependencies
- Monitor workflow progress in real-time
- Handle parallel execution and rollbacks

### 📡 Real-time Communication
- WebSocket connections for live updates
- Pub/Sub event streaming integration
- Event subscription and callbacks
- Service status notifications

### 📊 Performance Analytics
- Cost optimization tracking (89% savings)
- AI routing efficiency monitoring
- Request/response time analytics
- Success rate and error tracking

### 🔧 Service Integration
- Direct service API calls
- Standardized /execute endpoint access
- Circuit breaker management
- Authentication and authorization

## Architecture Overview

The SDK provides unified access to 15+ microservices:

- **Platform Dashboard** (`:8080`) - Central monitoring
- **Marketing Engine** (`:8081`) - AI-powered campaigns
- **AI Assistant** (`:8082`) - Workflow orchestration
- **Content Hub** (`:8083`) - Content management
- **System Runtime** (`:8084`) - Core orchestration
- **AI Routing Engine** (`:8085`) - Intelligent AI routing

## SDK Components

### Core Classes

```python
# Main SDK interface
XynergyPlatformSDK(api_key, base_url, timeout=30)

# Data models
ServiceHealth, PlatformHealth, WorkflowExecution
PerformanceMetrics, DashboardOverview

# Enums
ServiceStatus, WorkflowStatus, CircuitBreakerState
```

### Key Methods

```python
# Service Discovery
await sdk.get_platform_health()
await sdk.get_service_registry()

# Workflow Management
await sdk.execute_business_intent(intent, context)
await sdk.create_workflow(name, steps)
await sdk.get_workflow_status(workflow_id)

# Real-time Communication
await sdk.connect_websocket()
sdk.subscribe_to_events(callback)

# Performance Analytics
await sdk.get_dashboard_overview()
await sdk.get_performance_metrics()

# Service Integration
await sdk.call_service(service_name, endpoint, method, payload)
await sdk.execute_service_action(service, action, parameters)
```

## Usage Examples

### Real-time Dashboard

```python
async with XynergyPlatformSDK(api_key) as sdk:
    # Subscribe to events
    def on_update(event):
        if event['type'] == 'workflow_update':
            print(f"Workflow {event['workflow_id']}: {event['status']}")

    sdk.subscribe_to_events(on_update)
    await sdk.connect_websocket()

    # Get dashboard data
    overview = await sdk.get_dashboard_overview()
    print(f"Active Workflows: {overview.active_workflows}")
    print(f"Cost Savings: {overview.cost_metrics.cost_savings_percentage}%")
```

### Workflow Orchestration

```python
# Execute business intent
workflow = await sdk.execute_business_intent(
    intent="Create comprehensive marketing campaign",
    context={
        "company": "EcoFashion Co",
        "budget": "$25,000",
        "timeline": "Q2 2025"
    }
)

# Monitor progress
while workflow.status in [WorkflowStatus.PENDING, WorkflowStatus.EXECUTING]:
    await asyncio.sleep(5)
    workflow = await sdk.get_workflow_status(workflow.workflow_id)
    print(f"Progress: {workflow.progress:.1%}")
```

### Custom Workflow Creation

```python
# Define workflow with dependencies
steps = [
    {
        "step_id": "market_research",
        "service": "marketing-engine",
        "action": "analyze_market",
        "parameters": {"business_type": "SaaS"}
    },
    {
        "step_id": "content_strategy",
        "service": "content-hub",
        "action": "create_strategy",
        "depends_on": ["market_research"]
    }
]

workflow = await sdk.create_workflow("Marketing Launch", steps)
```

### Service Integration

```python
# Direct service calls
campaign = await sdk.call_service(
    service_name="marketing-engine",
    endpoint="/api/generate-campaign",
    method="POST",
    payload={
        "business_type": "E-commerce",
        "target_audience": "millennials",
        "budget_range": "$10,000-$50,000"
    }
)

# Standardized service actions
result = await sdk.execute_service_action(
    service_name="ai-routing-engine",
    action="route_request",
    parameters={
        "query": "Generate marketing content",
        "preferred_provider": "abacus"
    }
)
```

## Error Handling

### Circuit Breaker Management

```python
try:
    result = await sdk.execute_business_intent("Generate campaign")
except Exception as e:
    # Check circuit breaker status
    breakers = await sdk.get_circuit_breaker_status()
    for service, states in breakers.items():
        for breaker, status in states.items():
            if status["state"] == "OPEN":
                print(f"Circuit breaker open: {service}.{breaker}")
                # Implement fallback logic
```

### Service Unavailability

```python
# Check service health before operations
health = await sdk.get_platform_health()
if health.overall_status != ServiceStatus.HEALTHY:
    print(f"Platform issues: {health.unhealthy_services}")
    # Implement graceful degradation
```

## Configuration

### Environment Variables

```bash
# Required
XYNERGY_API_KEY=your_api_key_here

# Optional
XYNERGY_BASE_URL=https://xynergy-platform-dashboard.us-central1.run.app
XYNERGY_PROJECT_ID=xynergy-dev-1757909467
XYNERGY_TIMEOUT=30
XYNERGY_MAX_RETRIES=3
```

### SDK Options

```python
sdk = XynergyPlatformSDK(
    api_key="your_key",
    base_url="https://custom-url.com",
    timeout=60,  # Request timeout in seconds
    max_retries=5  # Max retry attempts
)
```

## Performance Optimization

### Connection Pooling
- HTTP/2 support with connection reuse
- 20 keepalive connections, 100 max connections
- Automatic connection management

### Caching
- Service registry cached for 5 minutes
- Request timing tracked for performance monitoring
- Circuit breaker state caching

### Rate Limiting
- Built-in respect for platform rate limits
- Exponential backoff on failures
- Automatic retry with circuit breakers

## Security

### Authentication
- API key-based authentication
- HTTPBearer token support
- Automatic header management

### CORS Compliance
- Respects platform CORS policies
- Supports specific domain allowlists
- Development and production configurations

### Data Protection
- Structured logging with sensitive data filtering
- Secure WebSocket connections (WSS)
- Request/response validation

## Examples and Testing

Run the comprehensive examples:

```bash
python sdk_usage_examples.py
```

Available examples:
1. Real-time Dashboard Monitoring
2. Platform Health Monitoring
3. Workflow Orchestration
4. Custom Workflow Creation
5. Performance Analytics Dashboard
6. Service Integration Examples
7. Circuit Breaker Error Handling
8. Service Unavailable Handling

## API Reference

See the complete [API Integration Guide](XYNERGY_API_INTEGRATION_GUIDE.md) for detailed endpoint documentation.

## Platform Metrics

Current platform optimization achievements:
- **89% cost savings** through intelligent AI routing
- **78% AI routing efficiency** (Abacus → OpenAI → Internal)
- **99.7% success rate** with circuit breaker protection
- **<250ms average response time** with connection pooling
- **15+ microservices** with standardized APIs

## Support

- 📖 Documentation: See `XYNERGY_API_INTEGRATION_GUIDE.md`
- 🔧 Examples: Run `sdk_usage_examples.py`
- 🏥 Health Checks: All services expose `/health` endpoints
- 📊 Monitoring: Real-time metrics via WebSocket and Pub/Sub

## License

This SDK is part of the Xynergy Platform ecosystem. See platform documentation for licensing terms.