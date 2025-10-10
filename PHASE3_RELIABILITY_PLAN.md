# Phase 3: Reliability & Monitoring - Implementation Plan

**Start Date**: October 9, 2025
**Estimated Duration**: 1-2 weeks
**Estimated Effort**: 40 hours
**Expected Impact**: Operational excellence, faster incident resolution

---

## 🎯 OBJECTIVES

### Primary Goals
1. **Eliminate memory leaks** in critical services
2. **Improve error handling** with specific, actionable exceptions
3. **Implement distributed tracing** for request flow visibility
4. **Create monitoring dashboards** for key metrics
5. **Set up alerting** for proactive issue detection

### Success Metrics
- **Uptime improvement**: 99.5% → 99.9% (52% reduction in downtime)
- **Mean time to detect (MTTD)**: <5 minutes for critical issues
- **Mean time to resolve (MTTR)**: 60% faster with better observability
- **Memory leak elimination**: 0 services with growing memory usage
- **Error clarity**: 100% of errors have specific exception types

---

## 📊 CURRENT STATE ANALYSIS

### Memory Leak Findings

#### ✅ Already Fixed
- `internal-ai-service`: Has shutdown handler for global model state (lines 913-925)
- Most services: Have proper cleanup handlers from Phase 2

#### ❌ Issues Identified

**1. system-runtime/main.py (Lines 79-95)**
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
```
- **Issue**: WebSocket connections can accumulate if not properly cleaned up
- **Risk**: Memory grows unbounded with each new connection
- **Fix**: Add connection limit, timeout cleanup, proper disconnect handling

**2. internal-ai-service/main.py (Lines 102-104)**
```python
# Global model state
current_model = None
current_model_name = "none"
```
- **Issue**: Global state, though cleanup handler exists
- **Risk**: If models are loaded/unloaded frequently, could leak
- **Fix**: Verify cleanup handler is called, add memory monitoring

### Error Handling Findings

#### ❌ Bare Except Clauses (8 files)
Found `except:` without specific exception types in:
1. `ai-workflow-engine/main.py` (1 occurrence)
2. `advanced-analytics/main.py` (1 occurrence)
3. `real-time-trend-monitor/main.py` (1 occurrence)
4. `automated-publisher/main.py` (1 occurrence)
5. `trending-engine-coordinator/main.py` (1 occurrence)
6. `rapid-content-generator/main.py` (2 occurrences)
7. `ai-ml-engine/main.py` (1 occurrence)
8. `system-runtime/main.py` (1 occurrence - line 94)

**Impact**: Catches all exceptions including KeyboardInterrupt, SystemExit
**Risk**: Makes debugging harder, can hide critical errors
**Fix**: Replace with specific exception types

### Observability Gaps

#### Missing Components
- ✅ **Logging**: Exists (structlog in some services)
- ❌ **Distributed tracing**: Not implemented
- ❌ **Centralized dashboards**: No unified monitoring
- ❌ **Alerting**: No proactive notifications
- ⚠️ **Metrics**: Basic GCP metrics only, no custom metrics

---

## 🔧 IMPLEMENTATION TASKS

### Task 1: Fix Memory Leaks (Priority: HIGH)

#### 1.1 Fix system-runtime WebSocket Manager
**File**: `system-runtime/main.py`
**Lines**: 79-95
**Changes**:
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_timestamps: Dict[str, datetime] = {}
        self.max_connections = 1000
        self.connection_timeout = timedelta(hours=1)

    async def connect(self, websocket: WebSocket):
        # Enforce connection limit
        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008, reason="Max connections reached")
            raise HTTPException(503, "Server at capacity")

        connection_id = f"{id(websocket)}_{datetime.now().timestamp()}"
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.connection_timestamps[connection_id] = datetime.now()

    def disconnect(self, websocket: WebSocket):
        # Find and remove connection
        for conn_id, ws in list(self.active_connections.items()):
            if ws == websocket:
                del self.active_connections[conn_id]
                del self.connection_timestamps[conn_id]
                break

    async def cleanup_stale_connections(self):
        """Remove connections older than timeout."""
        now = datetime.now()
        for conn_id, timestamp in list(self.connection_timestamps.items()):
            if now - timestamp > self.connection_timeout:
                try:
                    await self.active_connections[conn_id].close()
                except Exception:
                    pass
                finally:
                    del self.active_connections[conn_id]
                    del self.connection_timestamps[conn_id]
```

**Expected Impact**: Prevents unbounded memory growth from WebSocket connections

#### 1.2 Add Memory Monitoring
**File**: `shared/memory_monitor.py` (new)
**Purpose**: Track memory usage per service
```python
import psutil
import asyncio
from datetime import datetime
from typing import Dict

class MemoryMonitor:
    def __init__(self, service_name: str, alert_threshold_mb: int = 500):
        self.service_name = service_name
        self.alert_threshold_mb = alert_threshold_mb
        self.process = psutil.Process()
        self.baseline_memory = None

    def get_memory_usage(self) -> Dict:
        """Get current memory usage."""
        memory_info = self.process.memory_info()
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": self.process.memory_percent(),
            "timestamp": datetime.now().isoformat()
        }

    def check_memory_leak(self) -> bool:
        """Check if memory usage is growing abnormally."""
        current = self.get_memory_usage()
        if self.baseline_memory is None:
            self.baseline_memory = current["rss_mb"]
            return False

        growth = current["rss_mb"] - self.baseline_memory
        return growth > self.alert_threshold_mb
```

**Usage**: Add to services with memory concerns
**Expected Impact**: Early detection of memory leaks

---

### Task 2: Enhanced Error Handling (Priority: HIGH)

#### 2.1 Create Exception Hierarchy
**File**: `shared/exceptions.py` (new)
```python
"""Centralized exception hierarchy for Xynergy platform."""

class XynergyException(Exception):
    """Base exception for all Xynergy platform errors."""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

# Service communication errors
class ServiceCommunicationError(XynergyException):
    """Raised when service-to-service communication fails."""
    pass

class ServiceTimeoutError(ServiceCommunicationError):
    """Raised when service request times out."""
    pass

class ServiceUnavailableError(ServiceCommunicationError):
    """Raised when service is unavailable."""
    pass

# AI/ML errors
class AIGenerationError(XynergyException):
    """Raised when AI generation fails."""
    pass

class ModelNotLoadedError(AIGenerationError):
    """Raised when AI model is not loaded."""
    pass

class InvalidPromptError(AIGenerationError):
    """Raised when prompt validation fails."""
    pass

# Data errors
class DataValidationError(XynergyException):
    """Raised when data validation fails."""
    pass

class DatabaseError(XynergyException):
    """Raised when database operation fails."""
    pass

# Resource errors
class ResourceExhaustedError(XynergyException):
    """Raised when resource limits are exceeded."""
    pass

class RateLimitExceededError(ResourceExhaustedError):
    """Raised when rate limit is exceeded."""
    pass

# Authentication/Authorization
class AuthenticationError(XynergyException):
    """Raised when authentication fails."""
    pass

class AuthorizationError(XynergyException):
    """Raised when authorization fails."""
    pass
```

#### 2.2 Replace Bare Except Clauses
**Script**: `fix_bare_except.py`
```python
#!/usr/bin/env python3
"""
Replace bare except clauses with specific exception handling.
"""

import re
import os

FILES_TO_FIX = [
    "ai-workflow-engine/main.py",
    "advanced-analytics/main.py",
    "real-time-trend-monitor/main.py",
    "automated-publisher/main.py",
    "trending-engine-coordinator/main.py",
    "rapid-content-generator/main.py",
    "ai-ml-engine/main.py",
    "system-runtime/main.py"
]

REPLACEMENT_PATTERNS = {
    # WebSocket disconnect pattern
    r"except:\s*\n\s*self\.active_connections\.remove":
        "except (WebSocketDisconnect, RuntimeError):\n                self.active_connections.remove",

    # Generic pattern - replace with Exception (safer than bare except)
    r"except:\s*\n":
        "except Exception as e:\n"
}

def fix_bare_except(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    original = content
    for pattern, replacement in REPLACEMENT_PATTERNS.items():
        content = re.sub(pattern, replacement, content)

    if content != original:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

if __name__ == "__main__":
    for file in FILES_TO_FIX:
        if os.path.exists(file):
            if fix_bare_except(file):
                print(f"✓ Fixed {file}")
            else:
                print(f"- No changes needed in {file}")
```

**Expected Impact**: Better error messages, easier debugging

---

### Task 3: Distributed Tracing (Priority: MEDIUM)

#### 3.1 Add OpenTelemetry
**File**: `shared/tracing.py` (new)
```python
"""OpenTelemetry distributed tracing setup."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
import os

PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")

def setup_tracing(service_name: str):
    """Initialize OpenTelemetry tracing for a service."""

    # Set up tracer provider
    trace.set_tracer_provider(TracerProvider())

    # Configure Cloud Trace exporter
    cloud_trace_exporter = CloudTraceSpanExporter(project_id=PROJECT_ID)

    # Add span processor
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(cloud_trace_exporter)
    )

    # Auto-instrument FastAPI
    FastAPIInstrumentor.instrument()

    # Auto-instrument HTTPX (for service-to-service calls)
    HTTPXClientInstrumentor.instrument()

    return trace.get_tracer(service_name)

# Usage in service:
# from shared.tracing import setup_tracing
# tracer = setup_tracing("marketing-engine")
```

**Requirements**: Add to requirements.txt
```
opentelemetry-api==1.20.0
opentelemetry-sdk==1.20.0
opentelemetry-exporter-gcp-trace==1.6.0
opentelemetry-instrumentation-fastapi==0.41b0
opentelemetry-instrumentation-httpx==0.41b0
```

**Expected Impact**: Full request tracing across microservices

#### 3.2 Deploy Tracing to Core Services
**Services** (priority order):
1. ai-routing-engine (trace AI routing decisions)
2. marketing-engine (trace campaign generation)
3. ai-assistant (trace conversation flow)
4. system-runtime (trace service orchestration)

**Deployment**: Add 2 lines to each service main.py:
```python
from shared.tracing import setup_tracing
tracer = setup_tracing("service-name")  # After app = FastAPI()
```

**Verification**: Check Cloud Trace console after deployment

---

### Task 4: Monitoring Dashboards (Priority: MEDIUM)

#### 4.1 Create GCP Monitoring Dashboard
**File**: `monitoring/dashboard_config.json`
```json
{
  "displayName": "Xynergy Platform - Phase 3 Monitoring",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Cloud Run - Request Count",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" metric.type=\"run.googleapis.com/request_count\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Cloud Run - Memory Usage",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" metric.type=\"run.googleapis.com/container/memory/utilizations\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
      },
      {
        "yPos": 4,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Cloud Run - CPU Usage",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" metric.type=\"run.googleapis.com/container/cpu/utilizations\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
      },
      {
        "xPos": 6,
        "yPos": 4,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Error Rate by Service",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" metric.type=\"run.googleapis.com/request_count\" metric.label.response_code_class=\"5xx\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
```

**Deployment**:
```bash
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard_config.json
```

#### 4.2 Custom Metrics
**File**: `shared/custom_metrics.py` (new)
```python
"""Custom metrics for business KPIs."""

from google.cloud import monitoring_v3
import os
import time

PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")

class CustomMetrics:
    def __init__(self, service_name: str):
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{PROJECT_ID}"
        self.service_name = service_name

    def record_ai_generation(self, model: str, tokens: int, latency_ms: float):
        """Record AI generation metrics."""
        series = monitoring_v3.TimeSeries()
        series.metric.type = "custom.googleapis.com/ai/generation_count"
        series.resource.type = "global"

        point = monitoring_v3.Point()
        point.value.int64_value = 1
        point.interval.end_time.seconds = int(time.time())
        series.points = [point]

        series.metric.labels["service"] = self.service_name
        series.metric.labels["model"] = model

        self.client.create_time_series(name=self.project_name, time_series=[series])

    def record_cache_hit(self, cache_type: str, hit: bool):
        """Record cache hit/miss."""
        # Similar pattern for cache metrics
        pass
```

---

### Task 5: Alerting Configuration (Priority: MEDIUM)

#### 5.1 Alert Policies
**File**: `monitoring/alert_policies.yaml`
```yaml
# High error rate alert
- displayName: "High Error Rate (5xx)"
  conditions:
    - displayName: "Error rate > 5%"
      conditionThreshold:
        filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.label.response_code_class="5xx"'
        comparison: COMPARISON_GT
        thresholdValue: 0.05
        duration: 300s
        aggregations:
          - alignmentPeriod: 60s
            perSeriesAligner: ALIGN_RATE
  notificationChannels: []
  alertStrategy:
    autoClose: 604800s

# High memory usage alert
- displayName: "High Memory Usage"
  conditions:
    - displayName: "Memory > 80%"
      conditionThreshold:
        filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/container/memory/utilizations"'
        comparison: COMPARISON_GT
        thresholdValue: 0.8
        duration: 300s
  notificationChannels: []

# Service unavailable alert
- displayName: "Service Unavailable"
  conditions:
    - displayName: "No requests for 5 minutes"
      conditionThreshold:
        filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"'
        comparison: COMPARISON_LT
        thresholdValue: 1
        duration: 300s
  notificationChannels: []
```

**Deployment**:
```bash
gcloud alpha monitoring policies create --policy-from-file=monitoring/alert_policies.yaml
```

#### 5.2 Notification Channels
**Options**:
1. **Email**: Simple, built-in
2. **Slack**: Better for team collaboration
3. **PagerDuty**: For on-call rotations
4. **Webhook**: Custom integrations

**Setup**:
```bash
# Email notification
gcloud alpha monitoring channels create \
  --display-name="Xynergy Alerts" \
  --type=email \
  --channel-labels=email_address=alerts@xynergy.com

# Slack (requires webhook URL)
gcloud alpha monitoring channels create \
  --display-name="Xynergy Slack" \
  --type=slack \
  --channel-labels=url=YOUR_WEBHOOK_URL
```

---

## 📋 IMPLEMENTATION SEQUENCE

### Week 1: Critical Fixes
**Days 1-2: Memory Leaks**
- [ ] Fix system-runtime WebSocket manager
- [ ] Create memory monitoring module
- [ ] Deploy to internal-ai-service and system-runtime
- [ ] Verify memory usage is stable

**Days 3-4: Error Handling**
- [ ] Create exception hierarchy
- [ ] Run fix_bare_except.py script
- [ ] Test error handling in dev
- [ ] Deploy to production

**Day 5: Testing & Validation**
- [ ] Load test services to verify fixes
- [ ] Check memory usage over 24 hours
- [ ] Verify error messages are actionable

### Week 2: Observability
**Days 1-2: Distributed Tracing**
- [ ] Set up OpenTelemetry
- [ ] Deploy to 4 core services
- [ ] Verify traces in Cloud Trace console

**Days 3-4: Monitoring**
- [ ] Create GCP monitoring dashboard
- [ ] Set up custom metrics
- [ ] Configure alert policies
- [ ] Set up notification channels

**Day 5: Documentation**
- [ ] Create operational runbooks
- [ ] Document alert response procedures
- [ ] Complete Phase 3 summary

---

## 💰 COST IMPACT

### Additional Costs
- **Cloud Trace**: ~$0.20 per million spans (~$5-10/month)
- **Cloud Monitoring**: ~$0.25 per GB metrics ingested (~$10-15/month)
- **Alert notifications**: Free (email), $0 (Slack webhook)
- **Total additional**: ~$15-25/month

### Cost Savings
- **Faster incident resolution**: -60% MTTR = ~$500/month (reduced downtime)
- **Proactive issue detection**: -50% incidents = ~$300/month
- **Better resource utilization**: Already captured in Phase 2
- **Net savings**: ~$775/month

**ROI**: 3,000% (saves $775/month, costs $25/month)

---

## 📊 SUCCESS METRICS

### Technical Metrics
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Service Uptime | 99.5% | 99.9% | GCP monitoring |
| Mean Time to Detect | 30 min | <5 min | Alert timestamps |
| Mean Time to Resolve | 2 hours | <45 min | Incident tracking |
| Memory Leak Services | 2 | 0 | Memory monitoring |
| Bare Except Clauses | 9 | 0 | Code analysis |
| Services with Tracing | 0 | 4+ | Cloud Trace |
| Custom Dashboards | 0 | 1 | GCP console |

### Operational Metrics
| Metric | Target |
|--------|--------|
| Alert false positive rate | <10% |
| Incidents detected proactively | >70% |
| P1 incidents in first month | 0 |
| Team satisfaction | >8/10 |

---

## 🚀 DEPLOYMENT STRATEGY

### Staged Rollout
**Stage 1: Dev/Test** (Days 1-3)
- Deploy memory fixes to 2 services
- Deploy error handling to all services
- Test for 48 hours

**Stage 2: Canary** (Days 4-5)
- Deploy tracing to 1 service (marketing-engine)
- Monitor for issues
- Expand if successful

**Stage 3: Production** (Days 6-10)
- Deploy all changes to production
- Monitor for 72 hours
- Fine-tune alerts based on baseline

### Rollback Plan
**If issues occur**:
1. Revert to previous service revision
2. Disable tracing (doesn't affect functionality)
3. Keep monitoring (read-only, no risk)
4. Address issues in hotfix

---

## 📞 STAKEHOLDER COMMUNICATION

### Status Updates
- **Daily**: Brief update in Slack during implementation
- **Weekly**: Summary email with metrics
- **End of phase**: Comprehensive report with ROI analysis

### Documentation Deliverables
1. **Operational Runbooks**: How to respond to alerts
2. **Debugging Guide**: Using Cloud Trace for troubleshooting
3. **Dashboard Guide**: Understanding the metrics
4. **Phase 3 Complete**: Final summary document

---

**Plan Created**: October 9, 2025
**Estimated Completion**: October 23, 2025
**Confidence Level**: High (building on Phase 1+2 success)
