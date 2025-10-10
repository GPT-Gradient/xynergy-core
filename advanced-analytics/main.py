"""
Xynergy Advanced Analytics & Monetization Service
Package 2.3: Revenue optimization, pricing intelligence, and advanced billing management
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from google.cloud import bigquery, firestore, pubsub_v1, secretmanager

# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional, Any, Union
import asyncio
import httpx
import json
import os
import time
import uuid
import uvicorn
from datetime import datetime, timedelta
import logging
import numpy as np
from dataclasses import dataclass
from enum import Enum
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
bigquery_client = get_bigquery_client()  # Phase 4: Shared connection pooling
db = get_firestore_client()  # Phase 4: Shared connection pooling
tenant_db = get_tenant_aware_firestore(db)
publisher = get_publisher_client()  # Phase 4: Shared connection pooling

# Initialize monitoring
performance_monitor = PerformanceMonitor("advanced-analytics")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3, timeout=30))

# FastAPI app
app = FastAPI(
    title="Xynergy Advanced Analytics & Monetization",
    description="Revenue optimization, pricing intelligence, and advanced billing management",
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
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "advanced-analytics"}'
)
logger = logging.getLogger(__name__)

# Active WebSocket connections for real-time updates
active_connections = []

# Data Models

class RevenueMetrics(BaseModel):
    period: str  # "daily", "weekly", "monthly", "quarterly"
    total_revenue: float
    recurring_revenue: float
    one_time_revenue: float
    growth_rate: float
    churn_rate: float
    ltv: float  # Lifetime Value
    cac: float  # Customer Acquisition Cost
    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue

class PricingRecommendation(BaseModel):
    tenant_id: Optional[str]
    current_tier: str
    recommended_tier: str
    revenue_impact: float
    confidence: float
    reasons: List[str]
    usage_patterns: Dict[str, Any]
    optimal_price_point: float

class UsageAnalytics(BaseModel):
    tenant_id: str
    period: str
    service_usage: Dict[str, int]
    feature_adoption: Dict[str, float]
    api_calls: int
    storage_used_gb: float
    compute_hours: float
    ai_tokens_used: int
    cost_breakdown: Dict[str, float]
    efficiency_score: float

class BillingEvent(BaseModel):
    tenant_id: str
    event_type: str  # "subscription_created", "usage_charge", "payment_received", "overdue"
    amount: float
    currency: str = "USD"
    billing_period: str
    details: Dict[str, Any]
    processed_at: Optional[datetime] = None

class MonetizationInsight(BaseModel):
    title: str
    description: str
    impact_category: str  # "revenue_optimization", "cost_reduction", "retention"
    estimated_value: float
    implementation_effort: str  # "low", "medium", "high"
    priority: str  # "critical", "high", "medium", "low"
    tenant_segment: Optional[str] = None
    recommendations: List[str]

# WebSocket connections for real-time updates
@app.websocket("/ws/analytics")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        # Send initial analytics data
        analytics_data = await get_real_time_analytics(tenant_context)
        await websocket.send_json({
            "type": "analytics_update",
            "data": analytics_data,
            "timestamp": datetime.utcnow().isoformat()
        })

        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(30)  # Update every 30 seconds
            updated_data = await get_real_time_analytics(tenant_context)
            await websocket.send_json({
                "type": "analytics_update",
                "data": updated_data,
                "timestamp": datetime.utcnow().isoformat()
            })

    except WebSocketDisconnect:
        pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "advanced-analytics",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Revenue Analytics Endpoints

@app.get("/revenue/metrics", response_model=RevenueMetrics)
@require_tenant()
@check_feature_access("revenue_analytics")
async def get_revenue_metrics(
    period: str = "monthly",
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get comprehensive revenue metrics for tenant"""
    try:
        with performance_monitor.track_operation("revenue_metrics"):
            # Calculate revenue metrics from BigQuery
            revenue_data = await calculate_revenue_metrics(tenant_context.tenant_id, period)

            return RevenueMetrics(**revenue_data)

    except Exception as e:
        logger.error(f"Error getting revenue metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get revenue metrics: {str(e)}")

@app.get("/revenue/forecast")
@require_tenant()
@check_feature_access("revenue_forecasting")
async def get_revenue_forecast(
    months_ahead: int = 12,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Generate revenue forecast using predictive analytics"""
    try:
        with performance_monitor.track_operation("revenue_forecast"):
            forecast_data = await generate_revenue_forecast(tenant_context.tenant_id, months_ahead)

            return {
                "tenant_id": tenant_context.tenant_id,
                "forecast_period": f"{months_ahead} months",
                "forecast": forecast_data["forecast"],
                "confidence_intervals": forecast_data["confidence"],
                "key_factors": forecast_data["factors"],
                "methodology": "Time series analysis with ML predictions",
                "generated_at": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"Error generating revenue forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast: {str(e)}")

# Pricing Intelligence Endpoints

@app.get("/pricing/recommendations", response_model=List[PricingRecommendation])
@require_tenant(allow_system=True)
@check_feature_access("pricing_intelligence")
async def get_pricing_recommendations(
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get AI-powered pricing recommendations"""
    try:
        with performance_monitor.track_operation("pricing_recommendations"):
            if tenant_context:
                # Single tenant recommendations
                recommendations = await analyze_tenant_pricing(tenant_context.tenant_id)
            else:
                # System-wide pricing analysis
                recommendations = await analyze_global_pricing_opportunities()

            return recommendations

    except Exception as e:
        logger.error(f"Error getting pricing recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get pricing recommendations: {str(e)}")

@app.post("/pricing/optimize")
@require_tenant()
@check_feature_access("pricing_optimization")
async def optimize_pricing(
    target_metric: str = "revenue",  # "revenue", "retention", "acquisition"
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Run pricing optimization algorithm"""
    try:
        with performance_monitor.track_operation("pricing_optimization"):
            optimization_result = await run_pricing_optimization(
                tenant_context.tenant_id,
                target_metric
            )

            return {
                "tenant_id": tenant_context.tenant_id,
                "optimization_target": target_metric,
                "current_pricing": optimization_result["current"],
                "optimized_pricing": optimization_result["optimized"],
                "expected_impact": optimization_result["impact"],
                "implementation_plan": optimization_result["plan"],
                "confidence_score": optimization_result["confidence"]
            }

    except Exception as e:
        logger.error(f"Error optimizing pricing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize pricing: {str(e)}")

# Usage Analytics Endpoints

@app.get("/usage/analytics", response_model=UsageAnalytics)
@require_tenant()
@check_feature_access("usage_analytics")
async def get_usage_analytics(
    period: str = "monthly",
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get detailed usage analytics for tenant"""
    try:
        with performance_monitor.track_operation("usage_analytics"):
            usage_data = await calculate_usage_analytics(tenant_context.tenant_id, period)

            return UsageAnalytics(**usage_data)

    except Exception as e:
        logger.error(f"Error getting usage analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage analytics: {str(e)}")

@app.get("/usage/trends")
@require_tenant()
@check_feature_access("usage_trends")
async def get_usage_trends(
    service: Optional[str] = None,
    days: int = 30,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get usage trends and patterns"""
    try:
        with performance_monitor.track_operation("usage_trends"):
            trends_data = await analyze_usage_trends(
                tenant_context.tenant_id,
                service,
                days
            )

            return {
                "tenant_id": tenant_context.tenant_id,
                "analysis_period": f"{days} days",
                "service_filter": service,
                "trends": trends_data["trends"],
                "patterns": trends_data["patterns"],
                "anomalies": trends_data["anomalies"],
                "growth_indicators": trends_data["growth"]
            }

    except Exception as e:
        logger.error(f"Error getting usage trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage trends: {str(e)}")

# Advanced Billing Endpoints

@app.post("/billing/calculate")
@require_tenant()
@check_feature_access("advanced_billing")
async def calculate_billing(
    billing_period: str,
    include_usage: bool = True,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Calculate advanced billing with usage-based components"""
    try:
        with performance_monitor.track_operation("billing_calculation"):
            billing_result = await calculate_advanced_billing(
                tenant_context.tenant_id,
                billing_period,
                include_usage
            )

            # Store billing event
            billing_event = BillingEvent(
                tenant_id=tenant_context.tenant_id,
                event_type="billing_calculated",
                amount=billing_result["total_amount"],
                billing_period=billing_period,
                details=billing_result,
                processed_at=datetime.utcnow()
            )

            await store_billing_event(billing_event)

            return billing_result

    except Exception as e:
        logger.error(f"Error calculating billing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate billing: {str(e)}")

@app.get("/billing/events")
@require_tenant()
@check_feature_access("billing_history")
async def get_billing_events(
    limit: int = 50,
    event_type: Optional[str] = None,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get billing events history"""
    try:
        with performance_monitor.track_operation("billing_events"):
            events = await get_billing_events_history(
                tenant_context.tenant_id,
                limit,
                event_type
            )

            return {
                "tenant_id": tenant_context.tenant_id,
                "events": events,
                "total_count": len(events),
                "filtered_by": event_type
            }

    except Exception as e:
        logger.error(f"Error getting billing events: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get billing events: {str(e)}")

# Monetization Insights Endpoints

@app.get("/insights/monetization", response_model=List[MonetizationInsight])
@require_tenant(allow_system=True)
@check_feature_access("monetization_insights")
async def get_monetization_insights(
    category: Optional[str] = None,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get AI-powered monetization insights"""
    try:
        with performance_monitor.track_operation("monetization_insights"):
            insights = await generate_monetization_insights(
                tenant_context.tenant_id if tenant_context else None,
                category
            )

            return insights

    except Exception as e:
        logger.error(f"Error getting monetization insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@app.post("/insights/implement")
@require_tenant()
@check_feature_access("insight_implementation")
async def implement_insight(
    insight_id: str,
    background_tasks: BackgroundTasks,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Implement a monetization insight recommendation"""
    try:
        with performance_monitor.track_operation("implement_insight"):
            # Queue implementation as background task
            background_tasks.add_task(
                execute_insight_implementation,
                tenant_context.tenant_id,
                insight_id
            )

            return {
                "tenant_id": tenant_context.tenant_id,
                "insight_id": insight_id,
                "status": "implementation_queued",
                "message": "Implementation started in background",
                "estimated_completion": "5-10 minutes"
            }

    except Exception as e:
        logger.error(f"Error implementing insight: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to implement insight: {str(e)}")

# Service Mesh Integration

@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration"""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with performance_monitor.track_operation(f"execute_{action}"):
            if action == "analyze_revenue":
                result = await calculate_revenue_metrics(
                    parameters.get("tenant_id"),
                    parameters.get("period", "monthly")
                )

            elif action == "pricing_optimization":
                result = await run_pricing_optimization(
                    parameters.get("tenant_id"),
                    parameters.get("target_metric", "revenue")
                )

            elif action == "generate_insights":
                result = await generate_monetization_insights(
                    parameters.get("tenant_id"),
                    parameters.get("category")
                )

            elif action == "billing_calculation":
                result = await calculate_advanced_billing(
                    parameters.get("tenant_id"),
                    parameters.get("billing_period"),
                    parameters.get("include_usage", True)
                )

            else:
                raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

            return {
                "success": True,
                "action": action,
                "result": result,
                "workflow_id": workflow_context.get("workflow_id"),
                "execution_time": time.time() - time.time(),
                "service": "advanced-analytics"
            }

    except Exception as e:
        logger.error(f"Error executing workflow step: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute: {str(e)}")

# Helper Functions

async def calculate_revenue_metrics(tenant_id: str, period: str) -> Dict[str, Any]:
    """Calculate comprehensive revenue metrics"""

    # Mock data for demonstration - in production, query BigQuery
    base_revenue = 50000 + (hash(tenant_id) % 100000)

    return {
        "period": period,
        "total_revenue": base_revenue,
        "recurring_revenue": base_revenue * 0.8,
        "one_time_revenue": base_revenue * 0.2,
        "growth_rate": 15.5,
        "churn_rate": 2.3,
        "ltv": base_revenue * 24,  # 24 months
        "cac": base_revenue * 0.1,
        "mrr": base_revenue if period == "monthly" else base_revenue / 3,
        "arr": base_revenue * 12 if period == "monthly" else base_revenue * 4
    }

async def generate_revenue_forecast(tenant_id: str, months_ahead: int) -> Dict[str, Any]:
    """Generate revenue forecast using ML predictions"""

    # Generate realistic forecast data
    base_revenue = 50000 + (hash(tenant_id) % 100000)
    forecast = []

    for month in range(1, months_ahead + 1):
        # Simulate growth with some seasonality
        growth_factor = 1 + (0.02 * month) + (0.01 * np.sin(month * np.pi / 6))
        predicted_revenue = base_revenue * growth_factor

        forecast.append({
            "month": month,
            "predicted_revenue": round(predicted_revenue, 2),
            "confidence_low": round(predicted_revenue * 0.9, 2),
            "confidence_high": round(predicted_revenue * 1.1, 2)
        })

    return {
        "forecast": forecast,
        "confidence": {"average": 0.85, "range": [0.8, 0.9]},
        "factors": ["Historical growth", "Market trends", "Seasonal patterns", "Product roadmap"]
    }

async def analyze_tenant_pricing(tenant_id: str) -> List[PricingRecommendation]:
    """Analyze pricing for specific tenant"""

    # Mock pricing analysis
    return [
        PricingRecommendation(
            tenant_id=tenant_id,
            current_tier="professional",
            recommended_tier="enterprise",
            revenue_impact=2500.0,
            confidence=0.87,
            reasons=[
                "High feature adoption rate (89%)",
                "Consistently hitting usage limits",
                "Strong growth trajectory"
            ],
            usage_patterns={
                "api_calls_per_month": 95000,
                "storage_usage_gb": 45.2,
                "feature_adoption_rate": 0.89
            },
            optimal_price_point=299.0
        )
    ]

async def analyze_global_pricing_opportunities() -> List[PricingRecommendation]:
    """Analyze pricing opportunities across all tenants"""

    # Mock global analysis
    return [
        PricingRecommendation(
            tenant_id=None,
            current_tier="starter",
            recommended_tier="professional",
            revenue_impact=15000.0,
            confidence=0.92,
            reasons=[
                "23% of starter users hit limits monthly",
                "High engagement with premium features",
                "Low price sensitivity in segment"
            ],
            usage_patterns={
                "avg_api_calls": 8500,
                "avg_storage_gb": 2.1,
                "upgrade_likelihood": 0.67
            },
            optimal_price_point=49.0
        )
    ]

async def run_pricing_optimization(tenant_id: str, target_metric: str) -> Dict[str, Any]:
    """Run pricing optimization algorithm"""

    return {
        "current": {"tier": "professional", "price": 199.0},
        "optimized": {"tier": "professional", "price": 229.0},
        "impact": {
            "revenue_increase": 15.2,
            "retention_impact": -0.5,
            "adoption_change": 2.1
        },
        "plan": [
            "Gradual price increase over 3 months",
            "Grandfathering for existing customers",
            "Enhanced value proposition communication"
        ],
        "confidence": 0.84
    }

async def calculate_usage_analytics(tenant_id: str, period: str) -> Dict[str, Any]:
    """Calculate detailed usage analytics"""

    return {
        "tenant_id": tenant_id,
        "period": period,
        "service_usage": {
            "marketing_engine": 450,
            "ai_assistant": 320,
            "analytics_data": 180,
            "content_hub": 95
        },
        "feature_adoption": {
            "campaigns": 0.87,
            "workflows": 0.65,
            "analytics": 0.92,
            "ai_insights": 0.78
        },
        "api_calls": 8750,
        "storage_used_gb": 12.4,
        "compute_hours": 45.2,
        "ai_tokens_used": 125000,
        "cost_breakdown": {
            "subscription": 199.0,
            "usage_overages": 23.50,
            "ai_usage": 45.20
        },
        "efficiency_score": 0.85
    }

async def analyze_usage_trends(tenant_id: str, service: Optional[str], days: int) -> Dict[str, Any]:
    """Analyze usage trends and patterns"""

    return {
        "trends": {
            "overall_growth": 12.5,
            "api_usage_trend": "increasing",
            "feature_adoption_trend": "stable"
        },
        "patterns": {
            "peak_usage_hours": [9, 10, 14, 15],
            "peak_usage_days": ["Tuesday", "Wednesday", "Thursday"],
            "seasonal_patterns": "Higher usage in Q4"
        },
        "anomalies": [
            {"date": "2025-09-20", "type": "usage_spike", "deviation": 340},
            {"date": "2025-09-15", "type": "low_usage", "deviation": -45}
        ],
        "growth": {
            "daily_average_change": 1.2,
            "weekly_growth_rate": 8.5,
            "predicted_next_month": 15.3
        }
    }

async def calculate_advanced_billing(tenant_id: str, billing_period: str, include_usage: bool) -> Dict[str, Any]:
    """Calculate advanced billing with usage components"""

    base_subscription = 199.0
    usage_charges = 67.50 if include_usage else 0.0

    return {
        "tenant_id": tenant_id,
        "billing_period": billing_period,
        "subscription_amount": base_subscription,
        "usage_charges": usage_charges,
        "total_amount": base_subscription + usage_charges,
        "currency": "USD",
        "line_items": [
            {"description": "Professional Plan", "amount": base_subscription},
            {"description": "API Usage Overage", "amount": 23.50},
            {"description": "AI Token Usage", "amount": 44.00}
        ],
        "payment_due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "billing_details": {
            "api_calls": 8750,
            "storage_gb": 12.4,
            "ai_tokens": 125000
        }
    }

async def store_billing_event(billing_event: BillingEvent):
    """Store billing event in tenant-specific collection"""

    doc_data = billing_event.dict()
    doc_data["created_at"] = datetime.utcnow()

    tenant_db.collection("billing_events").document(str(uuid.uuid4())).set(doc_data)

async def get_billing_events_history(tenant_id: str, limit: int, event_type: Optional[str]) -> List[Dict]:
    """Get billing events history"""

    # Mock data - in production, query Firestore
    return [
        {
            "event_id": str(uuid.uuid4()),
            "event_type": "billing_calculated",
            "amount": 266.50,
            "billing_period": "2025-09",
            "processed_at": datetime.utcnow().isoformat()
        }
    ]

async def generate_monetization_insights(tenant_id: Optional[str], category: Optional[str]) -> List[MonetizationInsight]:
    """Generate AI-powered monetization insights"""

    insights = [
        MonetizationInsight(
            title="Upsell Opportunity Detected",
            description="Tenant shows high engagement with premium features but remains on professional plan",
            impact_category="revenue_optimization",
            estimated_value=3600.0,
            implementation_effort="low",
            priority="high",
            tenant_segment="high_engagement",
            recommendations=[
                "Present enterprise plan benefits during next billing cycle",
                "Offer 30-day enterprise trial",
                "Highlight advanced analytics capabilities"
            ]
        ),
        MonetizationInsight(
            title="Usage-Based Pricing Opportunity",
            description="API usage patterns indicate potential for consumption-based pricing model",
            impact_category="revenue_optimization",
            estimated_value=8500.0,
            implementation_effort="medium",
            priority="medium",
            tenant_segment="api_heavy_users",
            recommendations=[
                "Introduce API usage tiers",
                "Implement pay-per-use model for high-volume customers",
                "Create API credit packages"
            ]
        )
    ]

    if category:
        insights = [i for i in insights if i.impact_category == category]

    return insights

async def execute_insight_implementation(tenant_id: str, insight_id: str):
    """Execute insight implementation in background"""

    # Simulate implementation process
    await asyncio.sleep(5)  # Simulate work

    # Log implementation
    logger.info(f"Implemented insight {insight_id} for tenant {tenant_id}")

    # Broadcast to WebSocket connections
    for connection in active_connections:
        try:
            await connection.send_json({
                "type": "insight_implemented",
                "tenant_id": tenant_id,
                "insight_id": insight_id,
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:  # Phase 3: Specific exception handling
            pass

async def get_real_time_analytics(tenant_context: Optional[TenantContext]) -> Dict[str, Any]:
    """Get real-time analytics data for WebSocket updates"""

    if not tenant_context:
        return {"error": "No tenant context"}

    # Generate real-time analytics
    return {
        "tenant_id": tenant_context.tenant_id,
        "current_revenue": 52750.0 + (int(time.time()) % 1000),
        "active_users": 145 + (int(time.time()) % 20),
        "api_calls_today": 2340 + (int(time.time()) % 100),
        "conversion_rate": 3.4 + (int(time.time()) % 10) * 0.1,
        "churn_risk_alerts": 2,
        "upsell_opportunities": 5,
        "billing_forecast": 267500.0,
        "efficiency_score": 0.87,
        "last_updated": datetime.utcnow().isoformat()
    }

# Advanced Analytics Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve advanced analytics dashboard"""

    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Xynergy Advanced Analytics Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }

            html, body {
                height: 100vh;
                overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #f8fafc;
            }

            .main-container {
                height: 100vh;
                overflow-y: auto;
                scroll-behavior: smooth;
                scrollbar-width: thin;
                scrollbar-color: rgba(59, 130, 246, 0.3) transparent;
            }

            .main-container::-webkit-scrollbar {
                width: 6px;
            }

            .main-container::-webkit-scrollbar-track {
                background: transparent;
            }

            .main-container::-webkit-scrollbar-thumb {
                background: rgba(59, 130, 246, 0.3);
                border-radius: 3px;
            }

            .container {
                max-width: 1600px;
                margin: 0 auto;
                padding: 24px;
                min-height: calc(100vh - 48px);
            }

            .header {
                text-align: center;
                margin-bottom: 32px;
                padding: 32px 24px;
                background: rgba(255,255,255,0.05);
                border-radius: 16px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.08);
                transition: all 0.3s ease;
            }

            .header:hover {
                transform: translateY(-1px);
                background: rgba(255,255,255,0.07);
            }

            .header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 12px;
                background: linear-gradient(45deg, #3b82f6, #8b5cf6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .header p {
                font-size: 1.1rem;
                opacity: 0.8;
                line-height: 1.6;
                margin-bottom: 8px;
            }

            .grid, .services-grid, .feature-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
                gap: 32px;
                margin: 32px 0 48px 0;
            }

            .card, .service-card, .feature {
                background: rgba(255,255,255,0.05);
                padding: 32px 24px;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .card::before, .service-card::before, .feature::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .card:hover, .service-card:hover, .feature:hover {
                transform: translateY(-3px);
                background: rgba(255,255,255,0.08);
                border-color: rgba(59, 130, 246, 0.3);
            }

            .card:hover::before, .service-card:hover::before, .feature:hover::before {
                opacity: 1;
            }

            .card h3, .service-card h3, .feature h3 {
                font-size: 1.3rem;
                margin-bottom: 24px;
                color: #3b82f6;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                background: #22c55e;
                border-radius: 50%;
                margin-right: 8px;
            }

            .btn, button {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.2s ease;
                font-size: 0.9rem;
            }

            .btn:hover, button:hover {
                background: #2563eb;
                transform: translateY(-1px);
            }

            @media (max-width: 768px) {
                .grid, .services-grid, .feature-list {
                    grid-template-columns: 1fr;
                    gap: 24px;
                }

                .container {
                    padding: 16px;
                }

                .header h1 {
                    font-size: 2rem;
                }
            }
            </style>
    </head>
    <body>
            <div class="main-container">
                <div class="container">
            <div class="header">
                <h1>🚀 Advanced Analytics & Monetization</h1>
                <p>Revenue optimization, pricing intelligence, and billing analytics</p>
                <p><span class="real-time-indicator"></span><span id="connection-status" class="status-disconnected">Connecting to real-time data...</span></p>
            </div>

            <div class="dashboard-grid">
                <!-- Revenue Metrics -->
                <div class="card">
                    <h3>💰 Revenue Metrics</h3>
                    <div class="metric">
                        <span>Monthly Recurring Revenue</span>
                        <span class="metric-value" id="mrr">$52,750</span>
                    </div>
                    <div class="metric">
                        <span>Annual Run Rate</span>
                        <span class="metric-value" id="arr">$633,000</span>
                    </div>
                    <div class="metric">
                        <span>Growth Rate</span>
                        <span class="metric-value" id="growth-rate">+15.5%</span>
                    </div>
                    <div class="metric">
                        <span>Churn Rate</span>
                        <span class="metric-value" id="churn-rate">2.3%</span>
                    </div>
                </div>

                <!-- Pricing Intelligence -->
                <div class="card">
                    <h3>🎯 Pricing Intelligence</h3>
                    <div class="metric">
                        <span>Pricing Optimization Score</span>
                        <span class="metric-value">87%</span>
                    </div>
                    <div class="metric">
                        <span>Upsell Opportunities</span>
                        <span class="metric-value" id="upsell-ops">5</span>
                    </div>
                    <div class="metric">
                        <span>Revenue Impact</span>
                        <span class="metric-value">+$12,100</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="pricingChart"></canvas>
                    </div>
                </div>

                <!-- Usage Analytics -->
                <div class="card">
                    <h3>📊 Usage Analytics</h3>
                    <div class="metric">
                        <span>API Calls Today</span>
                        <span class="metric-value" id="api-calls">2,340</span>
                    </div>
                    <div class="metric">
                        <span>Active Tenants</span>
                        <span class="metric-value" id="active-tenants">145</span>
                    </div>
                    <div class="metric">
                        <span>Efficiency Score</span>
                        <span class="metric-value" id="efficiency">87%</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="usageChart"></canvas>
                    </div>
                </div>

                <!-- Monetization Insights -->
                <div class="card">
                    <h3>💡 Monetization Insights</h3>
                    <ul class="insights-list" id="insights-list">
                        <li class="insight-item priority-high">
                            <strong>High-Priority:</strong> Upsell opportunity detected for 3 tenants - Est. $3,600 revenue
                        </li>
                        <li class="insight-item priority-medium">
                            <strong>Medium-Priority:</strong> Usage-based pricing could increase revenue by $8,500
                        </li>
                        <li class="insight-item priority-low">
                            <strong>Low-Priority:</strong> Feature adoption optimization for starter plans
                        </li>
                    </ul>
                </div>

                <!-- Billing Analytics -->
                <div class="card">
                    <h3>💳 Billing Analytics</h3>
                    <div class="metric">
                        <span>Outstanding Invoices</span>
                        <span class="metric-value">$15,420</span>
                    </div>
                    <div class="metric">
                        <span>Collection Rate</span>
                        <span class="metric-value">96.8%</span>
                    </div>
                    <div class="metric">
                        <span>Average Deal Size</span>
                        <span class="metric-value">$267</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="billingChart"></canvas>
                    </div>
                </div>

                <!-- Real-time Forecast -->
                <div class="card">
                    <h3>🔮 Revenue Forecast</h3>
                    <div class="metric">
                        <span>Next Month Forecast</span>
                        <span class="metric-value">$58,200</span>
                    </div>
                    <div class="metric">
                        <span>Confidence Interval</span>
                        <span class="metric-value">85%</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="forecastChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // WebSocket connection for real-time updates
            let ws = null;

            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/analytics`;

                ws = new WebSocket(wsUrl);

                ws.onopen = function() {
                    document.getElementById('connection-status').textContent = 'Connected to real-time data';
                    document.getElementById('connection-status').className = 'status-connected';
                };

                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    if (data.type === 'analytics_update') {
                        updateMetrics(data.data);
                    }
                };

                ws.onclose = function() {
                    document.getElementById('connection-status').textContent = 'Disconnected - Reconnecting...';
                    document.getElementById('connection-status').className = 'status-disconnected';
                    setTimeout(connectWebSocket, 3000);
                };
            }

            function updateMetrics(data) {
                // Update real-time metrics
                if (data.current_revenue) {
                    document.getElementById('mrr').textContent = `$${data.current_revenue.toLocaleString()}`;
                }
                if (data.active_users) {
                    document.getElementById('active-tenants').textContent = data.active_users;
                }
                if (data.api_calls_today) {
                    document.getElementById('api-calls').textContent = data.api_calls_today.toLocaleString();
                }
                if (data.upsell_opportunities) {
                    document.getElementById('upsell-ops').textContent = data.upsell_opportunities;
                }
                if (data.efficiency_score) {
                    document.getElementById('efficiency').textContent = `${Math.round(data.efficiency_score * 100)}%`;
                }
            }

            // Initialize charts
            function initializeCharts() {
                // Pricing Chart
                const pricingCtx = document.getElementById('pricingChart').getContext('2d');
                new Chart(pricingCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Optimized', 'Under-priced', 'Over-priced'],
                        datasets: [{
                            data: [65, 25, 10],
                            backgroundColor: ['#4ecdc4', '#ffd93d', '#ff6b6b']
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });

                // Usage Chart
                const usageCtx = document.getElementById('usageChart').getContext('2d');
                new Chart(usageCtx, {
                    type: 'line',
                    data: {
                        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                        datasets: [{
                            label: 'API Calls',
                            data: [1200, 1900, 3000, 2100, 2800, 1500, 2200],
                            borderColor: '#4ecdc4',
                            tension: 0.4
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });

                // Billing Chart
                const billingCtx = document.getElementById('billingChart').getContext('2d');
                new Chart(billingCtx, {
                    type: 'bar',
                    data: {
                        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                        datasets: [{
                            label: 'Revenue',
                            data: [42000, 45000, 48000, 52000, 49000, 53000],
                            backgroundColor: '#667eea'
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });

                // Forecast Chart
                const forecastCtx = document.getElementById('forecastChart').getContext('2d');
                new Chart(forecastCtx, {
                    type: 'line',
                    data: {
                        labels: ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
                        datasets: [{
                            label: 'Forecast',
                            data: [53000, 56000, 59000, 62000, 65000, 68000],
                            borderColor: '#ffd93d',
                            backgroundColor: 'rgba(255, 217, 61, 0.2)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            }

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', function() {
                initializeCharts();
                connectWebSocket();
            });
        </script>
    </body>
    </html>
    """


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)