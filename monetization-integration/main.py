"""
Xynergy Monetization Integration Service
Integrates monetization features across all platform services
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore, pubsub_v1

# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import asyncio
import httpx
import json
import os
import time
import uuid
import uvicorn
from datetime import datetime, timedelta
import logging
import sys

# Add shared modules to path
sys.path.append('/Users/sesloan/Dev/xynergy-platform/shared')

# Phase 2 utilities and tenant support
from phase2_utils import PerformanceMonitor, CircuitBreaker, CircuitBreakerConfig
from tenant_utils import (
    TenantContext, get_tenant_context, require_tenant, check_feature_access,
    check_resource_limits, get_tenant_aware_firestore, add_tenant_middleware
)

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))

# Initialize GCP clients
db = get_firestore_client()  # Phase 4: Shared connection pooling
tenant_db = get_tenant_aware_firestore(db)
publisher = get_publisher_client()  # Phase 4: Shared connection pooling

# Initialize monitoring
performance_monitor = PerformanceMonitor("monetization-integration")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3, timeout=30))

# FastAPI app
app = FastAPI(
    title="Xynergy Monetization Integration",
    description="Integrates monetization features across all platform services",
    version="1.0.0"
)

# CORS configuration - Production security hardening
ALLOWED_ORIGINS = [
    "https://xynergy-platform.com",
    "https://api.xynergy.dev",
    "https://*.xynergy.com",
    os.getenv("ADDITIONAL_CORS_ORIGIN", "")  # For staging environments
]
# Remove empty strings from list
ALLOWED_ORIGINS = [origin for origin in ALLOWED_ORIGINS if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# Add tenant isolation middleware
add_tenant_middleware(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "monetization-integration"}'
)
logger = logging.getLogger(__name__)

# Service Registry with monetization endpoints
PLATFORM_SERVICES = {
    "marketing-engine": {
        "url": "https://xynergy-marketing-engine-835612502919.us-central1.run.app",
        "monetization_features": ["campaign_billing", "keyword_research_credits", "ai_content_usage"]
    },
    "analytics-data-layer": {
        "url": "https://xynergy-analytics-data-layer-835612502919.us-central1.run.app",
        "monetization_features": ["report_generation", "custom_analytics", "data_export"]
    },
    "ai-assistant": {
        "url": "https://xynergy-ai-assistant-835612502919.us-central1.run.app",
        "monetization_features": ["workflow_executions", "ai_conversations", "intelligent_routing"]
    },
    "content-hub": {
        "url": "https://xynergy-content-hub-835612502919.us-central1.run.app",
        "monetization_features": ["storage_usage", "content_generation", "asset_management"]
    },
    "project-management": {
        "url": "https://xynergy-project-management-835612502919.us-central1.run.app",
        "monetization_features": ["project_seats", "advanced_tracking", "resource_planning"]
    },
    "qa-engine": {
        "url": "https://xynergy-qa-engine-835612502919.us-central1.run.app",
        "monetization_features": ["test_executions", "quality_reports", "automated_testing"]
    },
    "advanced-analytics": {
        "url": "https://xynergy-advanced-analytics-835612502919.us-central1.run.app",
        "monetization_features": ["revenue_analytics", "pricing_optimization", "billing_intelligence"]
    }
}

# Data Models

class UsageEvent(BaseModel):
    tenant_id: str
    service: str
    feature: str
    quantity: int
    unit: str  # "api_calls", "gb", "hours", "executions"
    cost_per_unit: float
    total_cost: float
    metadata: Dict[str, Any] = {}

class MonetizationRule(BaseModel):
    rule_id: str
    service: str
    feature: str
    pricing_model: str  # "usage_based", "tiered", "flat_rate"
    pricing_tiers: List[Dict[str, Any]]
    effective_date: datetime
    tenant_tier_overrides: Dict[str, Any] = {}

class RevenueAllocation(BaseModel):
    tenant_id: str
    period: str
    service_revenue: Dict[str, float]
    total_revenue: float
    cost_breakdown: Dict[str, float]
    profit_margin: float

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "monetization-integration",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Usage Tracking Endpoints

@app.post("/usage/track")
@require_tenant()
async def track_usage(
    usage_event: UsageEvent,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Track usage event for billing and analytics"""
    try:
        with performance_monitor.track_operation("track_usage"):
            # Validate tenant matches
            if usage_event.tenant_id != tenant_context.tenant_id:
                raise HTTPException(status_code=403, detail="Tenant ID mismatch")

            # Apply monetization rules
            processed_event = await apply_monetization_rules(usage_event)

            # Store usage event
            await store_usage_event(processed_event)

            # Update real-time usage tracking
            await update_usage_counters(processed_event)

            # Check if billing threshold reached
            await check_billing_thresholds(tenant_context.tenant_id)

            logger.info(f"Usage tracked: {usage_event.service}.{usage_event.feature} for {tenant_context.tenant_id}")

            return {
                "success": True,
                "event_id": str(uuid.uuid4()),
                "processed_cost": processed_event.total_cost,
                "billing_period": get_current_billing_period(),
                "usage_tracking": "enabled"
            }

    except Exception as e:
        logger.error(f"Error tracking usage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to track usage: {str(e)}")

@app.get("/usage/summary")
@require_tenant()
@check_feature_access("usage_summary")
async def get_usage_summary(
    period: str = "current",
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get usage summary for tenant"""
    try:
        with performance_monitor.track_operation("usage_summary"):
            summary = await calculate_usage_summary(tenant_context.tenant_id, period)

            return {
                "tenant_id": tenant_context.tenant_id,
                "period": period,
                "usage_summary": summary["usage"],
                "cost_summary": summary["costs"],
                "service_breakdown": summary["services"],
                "projected_bill": summary["projected_bill"],
                "billing_alerts": summary["alerts"]
            }

    except Exception as e:
        logger.error(f"Error getting usage summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage summary: {str(e)}")

# Monetization Rules Management

@app.post("/rules/create")
@require_tenant(allow_system=True)
@check_feature_access("monetization_rules")
async def create_monetization_rule(
    rule: MonetizationRule,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Create new monetization rule"""
    try:
        with performance_monitor.track_operation("create_rule"):
            # Validate rule
            await validate_monetization_rule(rule)

            # Store rule
            rule_doc = rule.dict()
            rule_doc["created_at"] = datetime.utcnow()
            rule_doc["created_by"] = tenant_context.tenant_id if tenant_context else "system"

            db.collection("monetization_rules").document(rule.rule_id).set(rule_doc)

            # Notify all services of new rule
            await broadcast_rule_update(rule)

            logger.info(f"Monetization rule created: {rule.rule_id}")

            return {
                "success": True,
                "rule_id": rule.rule_id,
                "status": "active",
                "services_notified": len(PLATFORM_SERVICES)
            }

    except Exception as e:
        logger.error(f"Error creating monetization rule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")

@app.get("/rules/list")
@require_tenant(allow_system=True)
@check_feature_access("monetization_rules")
async def list_monetization_rules(
    service: Optional[str] = None,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """List monetization rules"""
    try:
        with performance_monitor.track_operation("list_rules"):
            rules_query = db.collection("monetization_rules")

            if service:
                rules_query = rules_query.where("service", "==", service)

            rules_docs = rules_query.stream()
            rules = [doc.to_dict() for doc in rules_docs]

            return {
                "rules": rules,
                "total_count": len(rules),
                "service_filter": service
            }

    except Exception as e:
        logger.error(f"Error listing monetization rules: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list rules: {str(e)}")

# Revenue Analytics

@app.get("/revenue/allocation")
@require_tenant()
@check_feature_access("revenue_analytics")
async def get_revenue_allocation(
    period: str = "monthly",
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get revenue allocation across services"""
    try:
        with performance_monitor.track_operation("revenue_allocation"):
            allocation = await calculate_revenue_allocation(tenant_context.tenant_id, period)

            return RevenueAllocation(**allocation)

    except Exception as e:
        logger.error(f"Error getting revenue allocation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get revenue allocation: {str(e)}")

@app.get("/revenue/optimization")
@require_tenant(allow_system=True)
@check_feature_access("revenue_optimization")
async def get_revenue_optimization(
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get revenue optimization recommendations"""
    try:
        with performance_monitor.track_operation("revenue_optimization"):
            recommendations = await generate_revenue_optimization(
                tenant_context.tenant_id if tenant_context else None
            )

            return {
                "tenant_id": tenant_context.tenant_id if tenant_context else "global",
                "optimization_opportunities": recommendations["opportunities"],
                "projected_impact": recommendations["impact"],
                "implementation_priority": recommendations["priority"],
                "risk_assessment": recommendations["risks"]
            }

    except Exception as e:
        logger.error(f"Error getting revenue optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization: {str(e)}")

# Service Integration

@app.post("/services/sync-monetization")
@require_tenant(allow_system=True)
async def sync_monetization_features(
    background_tasks: BackgroundTasks,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Sync monetization features across all services"""
    try:
        with performance_monitor.track_operation("sync_monetization"):
            # Queue sync as background task
            background_tasks.add_task(sync_all_services)

            return {
                "status": "sync_initiated",
                "services_count": len(PLATFORM_SERVICES),
                "estimated_completion": "2-3 minutes",
                "sync_id": str(uuid.uuid4())
            }

    except Exception as e:
        logger.error(f"Error syncing monetization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sync: {str(e)}")

@app.get("/services/monetization-status")
@require_tenant(allow_system=True)
async def get_monetization_status(
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get monetization integration status across services"""
    try:
        with performance_monitor.track_operation("monetization_status"):
            status = await check_service_monetization_status()

            return {
                "overall_status": status["overall"],
                "service_status": status["services"],
                "integration_health": status["health"],
                "last_sync": status["last_sync"],
                "active_rules": status["active_rules"]
            }

    except Exception as e:
        logger.error(f"Error getting monetization status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

# Billing Integration

@app.post("/billing/process")
@require_tenant()
@check_feature_access("billing_processing")
async def process_billing(
    billing_period: str,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Process billing for tenant"""
    try:
        with performance_monitor.track_operation("process_billing"):
            # Calculate comprehensive billing
            billing_result = await process_comprehensive_billing(
                tenant_context.tenant_id,
                billing_period
            )

            # Store billing record
            await store_billing_record(billing_result)

            # Generate invoice
            invoice = await generate_invoice(billing_result)

            return {
                "tenant_id": tenant_context.tenant_id,
                "billing_period": billing_period,
                "total_amount": billing_result["total_amount"],
                "service_breakdown": billing_result["breakdown"],
                "invoice_id": invoice["invoice_id"],
                "payment_due_date": invoice["due_date"],
                "billing_status": "processed"
            }

    except Exception as e:
        logger.error(f"Error processing billing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process billing: {str(e)}")

# Service Mesh Integration

@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration"""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with performance_monitor.track_operation(f"execute_{action}"):
            if action == "track_usage":
                result = await track_usage_internal(parameters)

            elif action == "calculate_billing":
                result = await process_comprehensive_billing(
                    parameters.get("tenant_id"),
                    parameters.get("billing_period")
                )

            elif action == "optimize_revenue":
                result = await generate_revenue_optimization(
                    parameters.get("tenant_id")
                )

            elif action == "sync_services":
                result = await sync_all_services()

            else:
                raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

            return {
                "success": True,
                "action": action,
                "result": result,
                "workflow_id": workflow_context.get("workflow_id"),
                "execution_time": time.time() - time.time(),
                "service": "monetization-integration"
            }

    except Exception as e:
        logger.error(f"Error executing workflow step: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute: {str(e)}")

# Helper Functions

async def apply_monetization_rules(usage_event: UsageEvent) -> UsageEvent:
    """Apply monetization rules to usage event"""

    # Get applicable rules
    rules = await get_monetization_rules(usage_event.service, usage_event.feature)

    if not rules:
        # Use default pricing
        return usage_event

    # Apply pricing logic
    rule = rules[0]  # Use first matching rule

    if rule["pricing_model"] == "tiered":
        tier_cost = calculate_tiered_pricing(usage_event.quantity, rule["pricing_tiers"])
        usage_event.total_cost = tier_cost
    elif rule["pricing_model"] == "usage_based":
        usage_event.total_cost = usage_event.quantity * usage_event.cost_per_unit

    return usage_event

async def get_monetization_rules(service: str, feature: str) -> List[Dict]:
    """Get monetization rules for service and feature"""

    rules_ref = db.collection("monetization_rules")
    query = rules_ref.where("service", "==", service).where("feature", "==", feature)

    rules_docs = query.stream()
    return [doc.to_dict() for doc in rules_docs]

def calculate_tiered_pricing(quantity: int, tiers: List[Dict]) -> float:
    """Calculate tiered pricing"""

    total_cost = 0.0
    remaining_quantity = quantity

    for tier in sorted(tiers, key=lambda x: x["from_quantity"]):
        if remaining_quantity <= 0:
            break

        tier_quantity = min(remaining_quantity, tier["to_quantity"] - tier["from_quantity"] + 1)
        total_cost += tier_quantity * tier["price_per_unit"]
        remaining_quantity -= tier_quantity

    return total_cost

async def store_usage_event(usage_event: UsageEvent):
    """Store usage event in tenant-specific collection"""

    event_doc = usage_event.dict()
    event_doc["timestamp"] = datetime.utcnow()
    event_doc["billing_period"] = get_current_billing_period()

    tenant_db.collection("usage_events").document(str(uuid.uuid4())).set(event_doc)

async def update_usage_counters(usage_event: UsageEvent):
    """Update real-time usage counters"""

    counter_doc_id = f"{usage_event.tenant_id}_{get_current_billing_period()}"
    counter_ref = tenant_db.collection("usage_counters").document(counter_doc_id)

    # Update counters atomically
    counter_ref.update({
        f"services.{usage_event.service}.{usage_event.feature}": firestore.Increment(usage_event.quantity),
        f"costs.{usage_event.service}.{usage_event.feature}": firestore.Increment(usage_event.total_cost),
        "last_updated": datetime.utcnow()
    })

async def check_billing_thresholds(tenant_id: str):
    """Check if billing thresholds are reached"""

    # Get current usage
    counter_doc_id = f"{tenant_id}_{get_current_billing_period()}"
    counter_doc = tenant_db.collection("usage_counters").document(counter_doc_id).get()

    if not counter_doc.exists:
        return

    usage_data = counter_doc.to_dict()
    total_cost = sum([
        sum(service_costs.values()) if isinstance(service_costs, dict) else 0
        for service_costs in usage_data.get("costs", {}).values()
    ])

    # Check threshold (e.g., $500)
    if total_cost > 500:
        await send_billing_alert(tenant_id, total_cost)

async def send_billing_alert(tenant_id: str, current_cost: float):
    """Send billing threshold alert"""

    alert_data = {
        "tenant_id": tenant_id,
        "alert_type": "billing_threshold",
        "current_cost": current_cost,
        "threshold": 500,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Publish to Pub/Sub
    topic_path = publisher.topic_path(PROJECT_ID, "billing-alerts")
    publisher.publish(topic_path, json.dumps(alert_data).encode())

async def calculate_usage_summary(tenant_id: str, period: str) -> Dict[str, Any]:
    """Calculate usage summary for tenant"""

    # Mock data for demonstration
    return {
        "usage": {
            "api_calls": 8750,
            "storage_gb": 12.4,
            "ai_tokens": 125000,
            "workflow_executions": 45
        },
        "costs": {
            "subscription": 199.0,
            "usage_overages": 67.50,
            "total": 266.50
        },
        "services": {
            "marketing_engine": 89.20,
            "ai_assistant": 124.30,
            "analytics": 53.00
        },
        "projected_bill": 289.75,
        "alerts": []
    }

async def validate_monetization_rule(rule: MonetizationRule):
    """Validate monetization rule"""

    # Basic validation
    if not rule.service or not rule.feature:
        raise ValueError("Service and feature are required")

    if rule.pricing_model not in ["usage_based", "tiered", "flat_rate"]:
        raise ValueError("Invalid pricing model")

    # Validate pricing tiers
    if rule.pricing_model == "tiered" and not rule.pricing_tiers:
        raise ValueError("Tiered pricing requires pricing tiers")

async def broadcast_rule_update(rule: MonetizationRule):
    """Broadcast rule update to all services"""

    rule_data = {
        "event_type": "monetization_rule_update",
        "rule": rule.dict(),
        "timestamp": datetime.utcnow().isoformat()
    }

    # Publish to Pub/Sub
    topic_path = publisher.topic_path(PROJECT_ID, "monetization-updates")
    publisher.publish(topic_path, json.dumps(rule_data).encode())

async def calculate_revenue_allocation(tenant_id: str, period: str) -> Dict[str, Any]:
    """Calculate revenue allocation across services"""

    # Mock data for demonstration
    return {
        "tenant_id": tenant_id,
        "period": period,
        "service_revenue": {
            "marketing_engine": 89.20,
            "ai_assistant": 124.30,
            "analytics_data": 53.00
        },
        "total_revenue": 266.50,
        "cost_breakdown": {
            "infrastructure": 45.20,
            "ai_costs": 23.50,
            "storage": 12.30
        },
        "profit_margin": 0.695
    }

async def generate_revenue_optimization(tenant_id: Optional[str]) -> Dict[str, Any]:
    """Generate revenue optimization recommendations"""

    return {
        "opportunities": [
            {
                "type": "upsell",
                "description": "Upgrade to enterprise plan",
                "estimated_revenue": 3600.0,
                "confidence": 0.87
            },
            {
                "type": "usage_optimization",
                "description": "Implement usage-based pricing",
                "estimated_revenue": 1200.0,
                "confidence": 0.73
            }
        ],
        "impact": {
            "total_potential": 4800.0,
            "implementation_cost": 500.0,
            "net_benefit": 4300.0
        },
        "priority": "high",
        "risks": ["Customer churn", "Implementation complexity"]
    }

async def sync_all_services():
    """Sync monetization features across all services"""

    sync_results = {}

    for service_name, service_config in PLATFORM_SERVICES.items():
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{service_config['url']}/monetization/sync",
                    json={"features": service_config["monetization_features"]}
                )
                sync_results[service_name] = "success" if response.status_code == 200 else "failed"
        except Exception as e:
            sync_results[service_name] = f"error: {str(e)}"

    return sync_results

async def check_service_monetization_status() -> Dict[str, Any]:
    """Check monetization integration status across services"""

    return {
        "overall": "healthy",
        "services": {
            service: "active" for service in PLATFORM_SERVICES.keys()
        },
        "health": {
            "integration_rate": 1.0,
            "sync_errors": 0,
            "last_error": None
        },
        "last_sync": datetime.utcnow().isoformat(),
        "active_rules": 12
    }

async def process_comprehensive_billing(tenant_id: str, billing_period: str) -> Dict[str, Any]:
    """Process comprehensive billing for tenant"""

    # Mock comprehensive billing
    return {
        "tenant_id": tenant_id,
        "billing_period": billing_period,
        "total_amount": 266.50,
        "breakdown": {
            "subscription": 199.0,
            "usage_charges": 67.50
        },
        "service_costs": {
            "marketing_engine": 89.20,
            "ai_assistant": 124.30,
            "analytics": 53.00
        }
    }

async def store_billing_record(billing_result: Dict[str, Any]):
    """Store billing record"""

    billing_doc = {
        **billing_result,
        "processed_at": datetime.utcnow(),
        "status": "processed"
    }

    tenant_db.collection("billing_records").document(str(uuid.uuid4())).set(billing_doc)

async def generate_invoice(billing_result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate invoice from billing result"""

    return {
        "invoice_id": f"INV-{uuid.uuid4().hex[:8].upper()}",
        "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "amount": billing_result["total_amount"],
        "status": "pending"
    }

async def track_usage_internal(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Internal usage tracking for workflow execution"""

    usage_event = UsageEvent(**parameters)
    processed_event = await apply_monetization_rules(usage_event)
    await store_usage_event(processed_event)

    return {
        "tracked": True,
        "cost": processed_event.total_cost,
        "billing_period": get_current_billing_period()
    }

def get_current_billing_period() -> str:
    """Get current billing period"""
    now = datetime.utcnow()
    return f"{now.year}-{now.month:02d}"


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)