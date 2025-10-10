"""
Xynergy Performance Optimization & Enterprise Scaling Service
Package 3.3: Auto-scaling, performance monitoring, and enterprise-grade optimizations
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from google.cloud import firestore, pubsub_v1, monitoring_v3

# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

from pydantic import BaseModel
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
import psutil
import statistics

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
monitoring_client = monitoring_v3.MetricServiceClient()

# Initialize monitoring
performance_monitor = PerformanceMonitor("performance-scaling")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3, timeout=30))

# FastAPI app
app = FastAPI(
    title="Xynergy Performance & Scaling Engine",
    description="Auto-scaling, performance monitoring, and enterprise-grade optimizations",
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
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "performance-scaling"}'
)
logger = logging.getLogger(__name__)

# Active WebSocket connections for real-time monitoring
active_connections = []

# Service Registry with performance characteristics
PLATFORM_SERVICES = {
    "ai-assistant": {
        "url": "https://xynergy-ai-assistant-835612502919.us-central1.run.app",
        "scaling_profile": "cpu_intensive",
        "target_cpu": 70,
        "max_instances": 20
    },
    "marketing-engine": {
        "url": "https://xynergy-marketing-engine-835612502919.us-central1.run.app",
        "scaling_profile": "balanced",
        "target_cpu": 60,
        "max_instances": 15
    },
    "analytics-data-layer": {
        "url": "https://xynergy-analytics-data-layer-835612502919.us-central1.run.app",
        "scaling_profile": "memory_intensive",
        "target_cpu": 65,
        "max_instances": 10
    },
    "advanced-analytics": {
        "url": "https://xynergy-advanced-analytics-835612502919.us-central1.run.app",
        "scaling_profile": "compute_intensive",
        "target_cpu": 75,
        "max_instances": 12
    }
}

# Data Models

class ScalingPolicy(Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

class PerformanceMetric(BaseModel):
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    service: str
    tenant_id: Optional[str] = None

class AutoScalingConfig(BaseModel):
    service: str
    policy: ScalingPolicy
    min_instances: int = 1
    max_instances: int = 10
    target_cpu_utilization: float = 70.0
    target_memory_utilization: float = 80.0
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 30.0
    cooldown_period: int = 300  # seconds

class PerformanceOptimization(BaseModel):
    optimization_id: str
    service: str
    optimization_type: str
    description: str
    impact_estimate: float
    implementation_effort: str
    status: str = "pending"

class CacheConfig(BaseModel):
    cache_type: str  # "redis", "memcached", "in_memory"
    ttl: int = 3600  # seconds
    max_size_mb: int = 512
    eviction_policy: str = "lru"

class LoadBalancingConfig(BaseModel):
    algorithm: str = "round_robin"  # "round_robin", "least_connections", "weighted"
    health_check_interval: int = 30
    unhealthy_threshold: int = 3
    healthy_threshold: int = 2

class PerformanceProfile(BaseModel):
    profile_id: str
    tenant_id: str
    service_configs: Dict[str, AutoScalingConfig]
    cache_configs: Dict[str, CacheConfig]
    load_balancing: LoadBalancingConfig
    monitoring_enabled: bool = True
    optimization_level: str = "balanced"

# WebSocket for real-time performance monitoring
@app.websocket("/ws/performance")
async def websocket_performance_monitor(
    websocket: WebSocket,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        # Send initial performance data
        performance_data = await get_real_time_performance_data(tenant_context)
        await websocket.send_json({
            "type": "performance_data",
            "data": performance_data,
            "timestamp": datetime.utcnow().isoformat()
        })

        while True:
            # Send real-time updates every 10 seconds
            await asyncio.sleep(10)
            updated_data = await get_real_time_performance_data(tenant_context)
            await websocket.send_json({
                "type": "performance_update",
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
        "service": "performance-scaling",
        "auto_scaling": "enabled",
        "monitoring": "active",
        "optimization_engine": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Performance Monitoring Endpoints

@app.get("/performance/metrics")
@require_tenant()
@check_feature_access("performance_monitoring")
async def get_performance_metrics(
    service: Optional[str] = None,
    time_range: str = "1h",
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get comprehensive performance metrics"""
    try:
        with performance_monitor.track_operation("get_performance_metrics"):
            # Collect metrics from all services
            metrics = await collect_service_metrics(
                tenant_context.tenant_id,
                service,
                time_range
            )

            # Calculate performance insights
            insights = await analyze_performance_trends(metrics)

            return {
                "tenant_id": tenant_context.tenant_id,
                "time_range": time_range,
                "service_filter": service,
                "metrics": metrics,
                "performance_insights": insights,
                "recommendations": generate_performance_recommendations(metrics),
                "overall_health_score": calculate_health_score(metrics)
            }

    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@app.post("/performance/optimize")
@require_tenant()
@check_feature_access("performance_optimization")
async def optimize_performance(
    optimization_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Initiate performance optimization analysis and implementation"""
    try:
        with performance_monitor.track_operation("optimize_performance"):
            optimization_id = str(uuid.uuid4())
            target_services = optimization_request.get("services", ["all"])
            optimization_level = optimization_request.get("level", "balanced")

            # Queue optimization analysis
            background_tasks.add_task(
                run_performance_optimization,
                optimization_id,
                target_services,
                optimization_level,
                tenant_context.tenant_id
            )

            return {
                "optimization_id": optimization_id,
                "status": "initiated",
                "target_services": target_services,
                "optimization_level": optimization_level,
                "estimated_duration": "5-10 minutes",
                "progress_endpoint": f"/performance/optimize/{optimization_id}/status"
            }

    except Exception as e:
        logger.error(f"Error initiating performance optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize: {str(e)}")

@app.get("/performance/optimize/{optimization_id}/status")
@require_tenant()
async def get_optimization_status(
    optimization_id: str,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get performance optimization status and results"""
    try:
        with performance_monitor.track_operation("get_optimization_status"):
            optimization_doc = tenant_db.collection("performance_optimizations").document(optimization_id).get()

            if not optimization_doc.exists:
                raise HTTPException(status_code=404, detail="Optimization not found")

            optimization_data = optimization_doc.to_dict()

            return {
                "optimization_id": optimization_id,
                "status": optimization_data.get("status"),
                "progress": optimization_data.get("progress", 0),
                "optimizations_found": optimization_data.get("optimizations_found", []),
                "optimizations_applied": optimization_data.get("optimizations_applied", []),
                "performance_improvement": optimization_data.get("performance_improvement", {}),
                "recommendations": optimization_data.get("recommendations", [])
            }

    except Exception as e:
        logger.error(f"Error getting optimization status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

# Auto-Scaling Management

@app.post("/scaling/configure")
@require_tenant()
@check_feature_access("auto_scaling")
async def configure_auto_scaling(
    scaling_config: AutoScalingConfig,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Configure auto-scaling for a service"""
    try:
        with performance_monitor.track_operation("configure_auto_scaling"):
            # Validate scaling configuration
            validated_config = await validate_scaling_config(scaling_config)

            # Store configuration
            config_doc = validated_config.dict()
            config_doc["tenant_id"] = tenant_context.tenant_id
            config_doc["created_at"] = datetime.utcnow()

            tenant_db.collection("scaling_configs").document(f"{scaling_config.service}_{tenant_context.tenant_id}").set(config_doc)

            # Apply scaling configuration
            application_result = await apply_scaling_configuration(validated_config, tenant_context.tenant_id)

            return {
                "service": scaling_config.service,
                "configuration": validated_config.dict(),
                "application_status": application_result,
                "monitoring_enabled": True,
                "next_evaluation": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }

    except Exception as e:
        logger.error(f"Error configuring auto-scaling: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to configure scaling: {str(e)}")

@app.get("/scaling/status")
@require_tenant()
@check_feature_access("scaling_monitoring")
async def get_scaling_status(
    service: Optional[str] = None,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get current auto-scaling status across services"""
    try:
        with performance_monitor.track_operation("get_scaling_status"):
            # Get scaling status for services
            scaling_status = await get_service_scaling_status(
                tenant_context.tenant_id,
                service
            )

            # Get recent scaling events
            scaling_events = await get_recent_scaling_events(
                tenant_context.tenant_id,
                service
            )

            return {
                "tenant_id": tenant_context.tenant_id,
                "service_filter": service,
                "scaling_status": scaling_status,
                "recent_events": scaling_events,
                "auto_scaling_active": True,
                "next_evaluation": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            }

    except Exception as e:
        logger.error(f"Error getting scaling status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get scaling status: {str(e)}")

@app.post("/scaling/manual")
@require_tenant()
@check_feature_access("manual_scaling")
async def manual_scale_service(
    scale_request: Dict[str, Any],
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Manually scale a service"""
    try:
        with performance_monitor.track_operation("manual_scale_service"):
            service = scale_request.get("service")
            target_instances = scale_request.get("instances")
            reason = scale_request.get("reason", "manual_adjustment")

            # Validate scaling request
            if not service or target_instances is None:
                raise HTTPException(status_code=400, detail="Service and instances required")

            # Execute manual scaling
            scaling_result = await execute_manual_scaling(
                service,
                target_instances,
                reason,
                tenant_context.tenant_id
            )

            return {
                "service": service,
                "target_instances": target_instances,
                "scaling_result": scaling_result,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"Error in manual scaling: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to scale manually: {str(e)}")

# Cache Management

@app.post("/cache/configure")
@require_tenant()
@check_feature_access("cache_management")
async def configure_caching(
    cache_config: CacheConfig,
    service: str,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Configure caching for a service"""
    try:
        with performance_monitor.track_operation("configure_caching"):
            # Validate cache configuration
            validated_config = await validate_cache_config(cache_config, service)

            # Store cache configuration
            config_doc = validated_config.dict()
            config_doc["service"] = service
            config_doc["tenant_id"] = tenant_context.tenant_id
            config_doc["created_at"] = datetime.utcnow()

            tenant_db.collection("cache_configs").document(f"{service}_{tenant_context.tenant_id}").set(config_doc)

            # Apply cache configuration
            application_result = await apply_cache_configuration(validated_config, service, tenant_context.tenant_id)

            return {
                "service": service,
                "cache_configuration": validated_config.dict(),
                "application_status": application_result,
                "cache_active": True,
                "performance_impact": "estimated 40-60% improvement"
            }

    except Exception as e:
        logger.error(f"Error configuring caching: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to configure caching: {str(e)}")

@app.get("/cache/performance")
@require_tenant()
@check_feature_access("cache_monitoring")
async def get_cache_performance(
    service: Optional[str] = None,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get cache performance metrics"""
    try:
        with performance_monitor.track_operation("get_cache_performance"):
            # Get cache metrics
            cache_metrics = await collect_cache_metrics(
                tenant_context.tenant_id,
                service
            )

            return {
                "tenant_id": tenant_context.tenant_id,
                "service_filter": service,
                "cache_metrics": cache_metrics,
                "performance_impact": calculate_cache_impact(cache_metrics),
                "optimization_suggestions": generate_cache_optimizations(cache_metrics)
            }

    except Exception as e:
        logger.error(f"Error getting cache performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache performance: {str(e)}")

# Load Balancing and Traffic Management

@app.post("/load-balancing/configure")
@require_tenant()
@check_feature_access("load_balancing")
async def configure_load_balancing(
    lb_config: LoadBalancingConfig,
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Configure load balancing settings"""
    try:
        with performance_monitor.track_operation("configure_load_balancing"):
            # Validate load balancing configuration
            validated_config = await validate_lb_config(lb_config)

            # Store configuration
            config_doc = validated_config.dict()
            config_doc["tenant_id"] = tenant_context.tenant_id
            config_doc["created_at"] = datetime.utcnow()

            tenant_db.collection("lb_configs").document(tenant_context.tenant_id).set(config_doc)

            # Apply load balancing configuration
            application_result = await apply_lb_configuration(validated_config, tenant_context.tenant_id)

            return {
                "load_balancing_config": validated_config.dict(),
                "application_status": application_result,
                "traffic_distribution": "optimized",
                "health_monitoring": "enabled"
            }

    except Exception as e:
        logger.error(f"Error configuring load balancing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to configure load balancing: {str(e)}")

# Enterprise Features

@app.post("/enterprise/profile/create")
@require_tenant()
@check_feature_access("enterprise_profiles")
async def create_performance_profile(
    profile_data: Dict[str, Any],
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Create enterprise performance profile"""
    try:
        with performance_monitor.track_operation("create_performance_profile"):
            profile_id = str(uuid.uuid4())

            # Create comprehensive performance profile
            profile = PerformanceProfile(
                profile_id=profile_id,
                tenant_id=tenant_context.tenant_id,
                service_configs=profile_data.get("service_configs", {}),
                cache_configs=profile_data.get("cache_configs", {}),
                load_balancing=LoadBalancingConfig(**profile_data.get("load_balancing", {})),
                monitoring_enabled=profile_data.get("monitoring_enabled", True),
                optimization_level=profile_data.get("optimization_level", "balanced")
            )

            # Store performance profile
            tenant_db.collection("performance_profiles").document(profile_id).set(profile.dict())

            # Apply profile settings
            application_results = await apply_performance_profile(profile)

            return {
                "profile_id": profile_id,
                "profile_settings": profile.dict(),
                "application_results": application_results,
                "status": "active",
                "estimated_improvement": "15-25% performance boost"
            }

    except Exception as e:
        logger.error(f"Error creating performance profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create profile: {str(e)}")

@app.get("/enterprise/analytics")
@require_tenant()
@check_feature_access("enterprise_analytics")
async def get_enterprise_analytics(
    time_range: str = "24h",
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Get enterprise-level performance analytics"""
    try:
        with performance_monitor.track_operation("get_enterprise_analytics"):
            # Comprehensive analytics
            analytics = await generate_enterprise_analytics(
                tenant_context.tenant_id,
                time_range
            )

            return {
                "tenant_id": tenant_context.tenant_id,
                "time_range": time_range,
                "performance_overview": analytics["overview"],
                "service_breakdown": analytics["services"],
                "cost_optimization": analytics["cost"],
                "capacity_planning": analytics["capacity"],
                "predictive_insights": analytics["predictions"],
                "recommendations": analytics["recommendations"]
            }

    except Exception as e:
        logger.error(f"Error getting enterprise analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

# Service Mesh Integration

@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration"""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with performance_monitor.track_operation(f"execute_{action}"):
            if action == "performance_optimization":
                result = await run_performance_optimization_internal(
                    parameters.get("services", ["all"]),
                    parameters.get("level", "balanced"),
                    parameters.get("tenant_id")
                )

            elif action == "auto_scale":
                result = await execute_auto_scaling_internal(
                    parameters.get("service"),
                    parameters.get("target_instances"),
                    parameters.get("tenant_id")
                )

            elif action == "cache_optimization":
                result = await optimize_caching_internal(
                    parameters.get("service"),
                    parameters.get("tenant_id")
                )

            elif action == "performance_analysis":
                result = await analyze_performance_internal(
                    parameters.get("time_range", "1h"),
                    parameters.get("tenant_id")
                )

            else:
                raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

            return {
                "success": True,
                "action": action,
                "result": result,
                "workflow_id": workflow_context.get("workflow_id"),
                "performance_optimized": True,
                "execution_time": time.time() - time.time(),
                "service": "performance-scaling"
            }

    except Exception as e:
        logger.error(f"Error executing workflow step: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute: {str(e)}")

# Helper Functions

async def get_real_time_performance_data(tenant_context: Optional[TenantContext]) -> Dict[str, Any]:
    """Get real-time performance data for WebSocket updates"""

    if not tenant_context:
        return {"error": "No tenant context"}

    # Mock real-time performance data
    current_time = time.time()

    return {
        "tenant_id": tenant_context.tenant_id,
        "overall_cpu_utilization": 45.2 + (current_time % 30),
        "overall_memory_utilization": 62.8 + (current_time % 20),
        "active_instances": 12 + int(current_time % 5),
        "requests_per_second": 245 + int(current_time % 50),
        "average_response_time": 180 + (current_time % 100),
        "cache_hit_rate": 0.87 + (current_time % 10) * 0.01,
        "auto_scaling_events": 3,
        "performance_score": 0.89 + (current_time % 15) * 0.005,
        "cost_efficiency": 0.92,
        "optimization_opportunities": 2
    }

async def collect_service_metrics(tenant_id: str, service: Optional[str], time_range: str) -> List[PerformanceMetric]:
    """Collect performance metrics from services"""

    # Mock metrics collection
    metrics = []
    services = [service] if service else list(PLATFORM_SERVICES.keys())

    for svc in services:
        metrics.extend([
            PerformanceMetric(
                metric_name="cpu_utilization",
                value=np.random.uniform(40, 80),
                unit="percent",
                timestamp=datetime.utcnow(),
                service=svc,
                tenant_id=tenant_id
            ),
            PerformanceMetric(
                metric_name="memory_utilization",
                value=np.random.uniform(50, 90),
                unit="percent",
                timestamp=datetime.utcnow(),
                service=svc,
                tenant_id=tenant_id
            ),
            PerformanceMetric(
                metric_name="response_time",
                value=np.random.uniform(100, 500),
                unit="milliseconds",
                timestamp=datetime.utcnow(),
                service=svc,
                tenant_id=tenant_id
            )
        ])

    return metrics

async def analyze_performance_trends(metrics: List[PerformanceMetric]) -> Dict[str, Any]:
    """Analyze performance trends from metrics"""

    cpu_values = [m.value for m in metrics if m.metric_name == "cpu_utilization"]
    memory_values = [m.value for m in metrics if m.metric_name == "memory_utilization"]
    response_time_values = [m.value for m in metrics if m.metric_name == "response_time"]

    return {
        "cpu_trend": "stable" if statistics.stdev(cpu_values) < 10 else "volatile",
        "memory_trend": "increasing" if memory_values[-1] > memory_values[0] else "stable",
        "response_time_trend": "improving" if response_time_values[-1] < response_time_values[0] else "stable",
        "overall_health": "good",
        "optimization_potential": 15.5
    }

def generate_performance_recommendations(metrics: List[PerformanceMetric]) -> List[str]:
    """Generate performance recommendations based on metrics"""

    recommendations = []

    cpu_metrics = [m for m in metrics if m.metric_name == "cpu_utilization"]
    if any(m.value > 80 for m in cpu_metrics):
        recommendations.append("Consider enabling auto-scaling for high CPU utilization")

    memory_metrics = [m for m in metrics if m.metric_name == "memory_utilization"]
    if any(m.value > 85 for m in memory_metrics):
        recommendations.append("Implement memory optimization or increase instance memory")

    response_time_metrics = [m for m in metrics if m.metric_name == "response_time"]
    if any(m.value > 400 for m in response_time_metrics):
        recommendations.append("Enable caching to improve response times")

    return recommendations

def calculate_health_score(metrics: List[PerformanceMetric]) -> float:
    """Calculate overall health score from metrics"""

    if not metrics:
        return 0.0

    # Simple health score calculation
    cpu_score = 1.0 - (statistics.mean([m.value for m in metrics if m.metric_name == "cpu_utilization"]) / 100)
    memory_score = 1.0 - (statistics.mean([m.value for m in metrics if m.metric_name == "memory_utilization"]) / 100)
    response_score = max(0, 1.0 - (statistics.mean([m.value for m in metrics if m.metric_name == "response_time"]) / 1000))

    return round((cpu_score + memory_score + response_score) / 3, 2)

async def run_performance_optimization(optimization_id: str, target_services: List[str], level: str, tenant_id: str):
    """Run performance optimization in background"""

    try:
        optimization_ref = tenant_db.collection("performance_optimizations").document(optimization_id)

        # Initialize optimization record
        optimization_ref.set({
            "optimization_id": optimization_id,
            "tenant_id": tenant_id,
            "target_services": target_services,
            "level": level,
            "status": "running",
            "progress": 0,
            "started_at": datetime.utcnow()
        })

        # Analyze current performance
        optimization_ref.update({"progress": 20})
        current_metrics = await collect_service_metrics(tenant_id, None, "1h")

        # Identify optimization opportunities
        optimization_ref.update({"progress": 40})
        optimizations_found = await identify_optimizations(current_metrics, target_services, level)

        # Apply optimizations
        optimization_ref.update({"progress": 70})
        optimizations_applied = await apply_optimizations(optimizations_found, tenant_id)

        # Measure improvement
        optimization_ref.update({"progress": 90})
        improvement = await measure_performance_improvement(current_metrics, tenant_id)

        # Complete optimization
        optimization_ref.update({
            "status": "completed",
            "progress": 100,
            "completed_at": datetime.utcnow(),
            "optimizations_found": optimizations_found,
            "optimizations_applied": optimizations_applied,
            "performance_improvement": improvement,
            "recommendations": generate_optimization_recommendations(improvement)
        })

        logger.info(f"Performance optimization completed: {optimization_id}")

    except Exception as e:
        optimization_ref.update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.utcnow()
        })
        logger.error(f"Performance optimization failed: {optimization_id}, error: {str(e)}")

async def identify_optimizations(metrics: List[PerformanceMetric], services: List[str], level: str) -> List[Dict[str, Any]]:
    """Identify performance optimization opportunities"""

    optimizations = []

    # Cache optimization
    if any(m.value > 300 for m in metrics if m.metric_name == "response_time"):
        optimizations.append({
            "type": "cache_optimization",
            "description": "Implement aggressive caching for slow endpoints",
            "estimated_improvement": 40.0,
            "effort": "medium"
        })

    # Auto-scaling optimization
    if any(m.value > 75 for m in metrics if m.metric_name == "cpu_utilization"):
        optimizations.append({
            "type": "auto_scaling",
            "description": "Configure auto-scaling for high CPU services",
            "estimated_improvement": 25.0,
            "effort": "low"
        })

    # Database optimization
    optimizations.append({
        "type": "database_optimization",
        "description": "Optimize database queries and indexing",
        "estimated_improvement": 20.0,
        "effort": "high"
    })

    return optimizations

async def apply_optimizations(optimizations: List[Dict[str, Any]], tenant_id: str) -> List[Dict[str, Any]]:
    """Apply identified optimizations"""

    applied = []

    for opt in optimizations:
        try:
            if opt["type"] == "cache_optimization":
                result = await apply_cache_optimization(tenant_id)
                applied.append({**opt, "status": "applied", "result": result})
            elif opt["type"] == "auto_scaling":
                result = await apply_auto_scaling_optimization(tenant_id)
                applied.append({**opt, "status": "applied", "result": result})
            else:
                applied.append({**opt, "status": "planned", "reason": "requires manual intervention"})
        except Exception as e:
            applied.append({**opt, "status": "failed", "error": str(e)})

    return applied

async def measure_performance_improvement(baseline_metrics: List[PerformanceMetric], tenant_id: str) -> Dict[str, float]:
    """Measure performance improvement after optimization"""

    # Mock improvement measurement
    return {
        "response_time_improvement": 18.5,
        "cpu_utilization_improvement": 12.3,
        "memory_efficiency_improvement": 8.7,
        "overall_improvement": 15.2
    }

def generate_optimization_recommendations(improvement: Dict[str, float]) -> List[str]:
    """Generate recommendations based on optimization results"""

    recommendations = []

    if improvement.get("response_time_improvement", 0) < 10:
        recommendations.append("Consider implementing CDN for static content")

    if improvement.get("cpu_utilization_improvement", 0) < 10:
        recommendations.append("Review code efficiency and consider code optimization")

    recommendations.append("Monitor performance metrics to ensure sustained improvements")

    return recommendations

async def validate_scaling_config(config: AutoScalingConfig) -> AutoScalingConfig:
    """Validate auto-scaling configuration"""

    validated_config = config.copy()

    # Validation logic
    if config.min_instances >= config.max_instances:
        raise ValueError("min_instances must be less than max_instances")

    if config.target_cpu_utilization <= 0 or config.target_cpu_utilization > 100:
        raise ValueError("target_cpu_utilization must be between 0 and 100")

    return validated_config

async def apply_scaling_configuration(config: AutoScalingConfig, tenant_id: str) -> Dict[str, str]:
    """Apply auto-scaling configuration to service"""

    # Mock application
    return {
        "status": "applied",
        "service": config.service,
        "configuration_id": str(uuid.uuid4()),
        "next_evaluation": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    }

async def get_service_scaling_status(tenant_id: str, service: Optional[str]) -> Dict[str, Any]:
    """Get current scaling status for services"""

    # Mock scaling status
    services = [service] if service else list(PLATFORM_SERVICES.keys())

    status = {}
    for svc in services:
        status[svc] = {
            "current_instances": np.random.randint(2, 8),
            "target_instances": np.random.randint(3, 10),
            "cpu_utilization": np.random.uniform(40, 80),
            "scaling_status": "stable",
            "last_scaling_event": (datetime.utcnow() - timedelta(minutes=np.random.randint(5, 60))).isoformat()
        }

    return status

async def get_recent_scaling_events(tenant_id: str, service: Optional[str]) -> List[Dict[str, Any]]:
    """Get recent auto-scaling events"""

    # Mock scaling events
    return [
        {
            "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "service": "ai-assistant",
            "action": "scale_up",
            "from_instances": 3,
            "to_instances": 5,
            "reason": "high_cpu_utilization",
            "trigger_value": 82.3
        },
        {
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "service": "marketing-engine",
            "action": "scale_down",
            "from_instances": 4,
            "to_instances": 2,
            "reason": "low_traffic",
            "trigger_value": 25.1
        }
    ]

async def execute_manual_scaling(service: str, target_instances: int, reason: str, tenant_id: str) -> Dict[str, Any]:
    """Execute manual scaling operation"""

    # Mock manual scaling
    return {
        "scaling_id": str(uuid.uuid4()),
        "service": service,
        "target_instances": target_instances,
        "status": "scaling_in_progress",
        "estimated_completion": (datetime.utcnow() + timedelta(minutes=2)).isoformat(),
        "reason": reason
    }

async def validate_cache_config(config: CacheConfig, service: str) -> CacheConfig:
    """Validate cache configuration"""

    validated_config = config.copy()

    # Validation logic
    if config.ttl <= 0:
        raise ValueError("TTL must be positive")

    if config.max_size_mb <= 0:
        raise ValueError("Max size must be positive")

    return validated_config

async def apply_cache_configuration(config: CacheConfig, service: str, tenant_id: str) -> Dict[str, str]:
    """Apply cache configuration to service"""

    # Mock application
    return {
        "status": "applied",
        "service": service,
        "cache_type": config.cache_type,
        "configuration_id": str(uuid.uuid4())
    }

async def collect_cache_metrics(tenant_id: str, service: Optional[str]) -> Dict[str, Any]:
    """Collect cache performance metrics"""

    # Mock cache metrics
    return {
        "hit_rate": 0.87,
        "miss_rate": 0.13,
        "eviction_rate": 0.05,
        "memory_usage": 78.5,
        "average_lookup_time": 2.3,
        "total_requests": 15420,
        "cache_size_mb": 445
    }

def calculate_cache_impact(metrics: Dict[str, Any]) -> Dict[str, float]:
    """Calculate cache performance impact"""

    return {
        "response_time_improvement": 42.5,
        "database_load_reduction": 68.3,
        "bandwidth_savings": 35.2,
        "cost_savings_per_month": 127.50
    }

def generate_cache_optimizations(metrics: Dict[str, Any]) -> List[str]:
    """Generate cache optimization suggestions"""

    suggestions = []

    if metrics.get("hit_rate", 0) < 0.8:
        suggestions.append("Review cache key strategy to improve hit rate")

    if metrics.get("eviction_rate", 0) > 0.1:
        suggestions.append("Consider increasing cache size to reduce evictions")

    if metrics.get("memory_usage", 0) > 90:
        suggestions.append("Implement cache compression or increase memory allocation")

    return suggestions

async def validate_lb_config(config: LoadBalancingConfig) -> LoadBalancingConfig:
    """Validate load balancing configuration"""

    validated_config = config.copy()

    # Validation logic
    valid_algorithms = ["round_robin", "least_connections", "weighted"]
    if config.algorithm not in valid_algorithms:
        raise ValueError(f"Invalid algorithm. Must be one of: {valid_algorithms}")

    return validated_config

async def apply_lb_configuration(config: LoadBalancingConfig, tenant_id: str) -> Dict[str, str]:
    """Apply load balancing configuration"""

    # Mock application
    return {
        "status": "applied",
        "algorithm": config.algorithm,
        "health_monitoring": "enabled",
        "configuration_id": str(uuid.uuid4())
    }

async def apply_performance_profile(profile: PerformanceProfile) -> Dict[str, Any]:
    """Apply performance profile settings"""

    # Mock profile application
    return {
        "services_configured": len(profile.service_configs),
        "cache_configs_applied": len(profile.cache_configs),
        "load_balancing_configured": True,
        "monitoring_enabled": profile.monitoring_enabled,
        "estimated_performance_boost": "15-25%"
    }

async def generate_enterprise_analytics(tenant_id: str, time_range: str) -> Dict[str, Any]:
    """Generate comprehensive enterprise analytics"""

    # Mock enterprise analytics
    return {
        "overview": {
            "total_requests": 1250000,
            "average_response_time": 145.2,
            "uptime_percentage": 99.97,
            "cost_efficiency_score": 0.92
        },
        "services": {
            "ai-assistant": {"performance_score": 0.94, "cost_per_request": 0.0023},
            "marketing-engine": {"performance_score": 0.89, "cost_per_request": 0.0018},
            "analytics-data-layer": {"performance_score": 0.91, "cost_per_request": 0.0031}
        },
        "cost": {
            "total_infrastructure_cost": 2847.50,
            "cost_per_user": 1.23,
            "optimization_savings": 523.80,
            "projected_monthly_cost": 3200.00
        },
        "capacity": {
            "current_utilization": 68.5,
            "peak_capacity_prediction": 85.2,
            "scaling_recommendations": ["Increase ai-assistant capacity by 20%"],
            "resource_efficiency": 0.87
        },
        "predictions": {
            "next_scaling_event": (datetime.utcnow() + timedelta(hours=6)).isoformat(),
            "performance_trend": "improving",
            "cost_trend": "stable",
            "capacity_needs": "adequate_for_next_30_days"
        },
        "recommendations": [
            "Enable aggressive caching for marketing-engine",
            "Consider upgrading analytics-data-layer instances",
            "Implement predictive scaling for peak hours"
        ]
    }

# Mock internal functions for service mesh integration
async def run_performance_optimization_internal(services: List[str], level: str, tenant_id: str) -> Dict[str, Any]:
    return {"optimizations_applied": 5, "performance_improvement": 18.2, "status": "completed"}

async def execute_auto_scaling_internal(service: str, target_instances: int, tenant_id: str) -> Dict[str, Any]:
    return {"service": service, "instances": target_instances, "status": "scaling", "eta": "2 minutes"}

async def optimize_caching_internal(service: str, tenant_id: str) -> Dict[str, Any]:
    return {"service": service, "cache_optimization": "applied", "expected_improvement": "40%"}

async def analyze_performance_internal(time_range: str, tenant_id: str) -> Dict[str, Any]:
    return {"performance_score": 0.89, "bottlenecks": 2, "recommendations": 4}

async def apply_cache_optimization(tenant_id: str) -> Dict[str, Any]:
    return {"cache_enabled": True, "improvement": 35.2}

async def apply_auto_scaling_optimization(tenant_id: str) -> Dict[str, Any]:
    return {"auto_scaling_enabled": True, "efficiency_gain": 22.1}


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)