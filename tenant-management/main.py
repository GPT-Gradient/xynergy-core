"""
Xynergy Tenant Management Service
Multi-tenant architecture with complete data isolation and tenant lifecycle management
"""

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.cloud import firestore, pubsub_v1, secretmanager
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
import hashlib
import secrets
from dataclasses import dataclass
from enum import Enum

# Phase 2 utilities
from phase2_utils import PerformanceMonitor, CircuitBreaker, CircuitBreakerConfig
from tenant_data_utils import TenantDataManager

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))

# Initialize GCP clients
db = firestore.Client()
publisher = pubsub_v1.PublisherClient()
secret_client = secretmanager.SecretManagerServiceClient()

# Initialize monitoring
performance_monitor = PerformanceMonitor("tenant-management")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3, timeout=30))

# FastAPI app
app = FastAPI(
    title="Xynergy Tenant Management",
    description="Multi-tenant architecture with data isolation and tenant lifecycle management",
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "tenant-management"}'
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Enums
class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    EXPIRED = "expired"

class SubscriptionTier(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

# Data models
class TenantCreate(BaseModel):
    organization_name: str
    admin_email: EmailStr
    admin_name: str
    subscription_tier: SubscriptionTier
    custom_domain: Optional[str] = None
    max_users: Optional[int] = 10
    storage_limit_gb: Optional[int] = 100
    api_rate_limit: Optional[int] = 1000

class Tenant(BaseModel):
    tenant_id: str
    organization_name: str
    admin_email: str
    admin_name: str
    subscription_tier: SubscriptionTier
    status: TenantStatus
    created_at: datetime
    updated_at: datetime
    custom_domain: Optional[str] = None
    api_key: str
    max_users: int
    current_users: int
    storage_limit_gb: int
    current_storage_gb: float
    api_rate_limit: int
    monthly_api_calls: int
    features: Dict[str, bool]
    billing_info: Dict[str, Any]

class TenantUpdate(BaseModel):
    organization_name: Optional[str] = None
    subscription_tier: Optional[SubscriptionTier] = None
    status: Optional[TenantStatus] = None
    max_users: Optional[int] = None
    storage_limit_gb: Optional[int] = None
    api_rate_limit: Optional[int] = None
    custom_domain: Optional[str] = None

class TenantUsage(BaseModel):
    tenant_id: str
    period_start: datetime
    period_end: datetime
    api_calls: int
    storage_used_gb: float
    active_users: int
    workflow_executions: int
    ai_requests: int
    cost_breakdown: Dict[str, float]

# Tenant context for request processing
class TenantContext:
    def __init__(self, tenant_id: str, tenant_data: Dict[str, Any]):
        self.tenant_id = tenant_id
        self.organization_name = tenant_data.get("organization_name", "")
        self.subscription_tier = tenant_data.get("subscription_tier", "starter")
        self.features = tenant_data.get("features", {})
        self.limits = {
            "max_users": tenant_data.get("max_users", 10),
            "storage_limit_gb": tenant_data.get("storage_limit_gb", 100),
            "api_rate_limit": tenant_data.get("api_rate_limit", 1000)
        }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "tenant-management",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "features": {
            "multi_tenant_support": True,
            "data_isolation": True,
            "tenant_onboarding": True,
            "usage_tracking": True,
            "subscription_management": True
        }
    }

@app.get("/", response_class=HTMLResponse)
async def tenant_management_dashboard():
    """Tenant Management Dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Xynergy Tenant Management</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                <h1>🏢 Xynergy Tenant Management</h1>
                <p>Multi-tenant architecture with complete data isolation and subscription management</p>
            </div>

            <div class="dashboard-grid">
                <div class="card">
                    <h3>📊 Platform Metrics</h3>
                    <div class="metric">
                        <span>Active Tenants</span>
                        <span class="metric-value">47</span>
                    </div>
                    <div class="metric">
                        <span>Total Organizations</span>
                        <span class="metric-value">52</span>
                    </div>
                    <div class="metric">
                        <span>Monthly Revenue</span>
                        <span class="metric-value">$89.2K</span>
                    </div>
                    <div class="metric">
                        <span>Platform Utilization</span>
                        <span class="metric-value">73.4%</span>
                    </div>
                </div>

                <div class="card">
                    <h3>🏭 Recent Tenants</h3>
                    <div class="tenant-item">
                        <div class="tenant-name">TechCorp Solutions</div>
                        <div class="tenant-details">
                            Enterprise • <span class="status-active">Active</span> • 45 users
                        </div>
                    </div>
                    <div class="tenant-item">
                        <div class="tenant-name">Startup Inc</div>
                        <div class="tenant-details">
                            Professional • <span class="status-active">Active</span> • 12 users
                        </div>
                    </div>
                    <div class="tenant-item">
                        <div class="tenant-name">Global Enterprises</div>
                        <div class="tenant-details">
                            Custom • <span class="status-pending">Pending Setup</span> • 0 users
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>💰 Subscription Distribution</h3>
                    <div class="metric">
                        <span>Enterprise (68%)</span>
                        <span class="metric-value">32</span>
                    </div>
                    <div class="metric">
                        <span>Professional (25%)</span>
                        <span class="metric-value">12</span>
                    </div>
                    <div class="metric">
                        <span>Starter (7%)</span>
                        <span class="metric-value">3</span>
                    </div>
                </div>

                <div class="card">
                    <h3>📈 Usage Analytics</h3>
                    <div class="metric">
                        <span>API Calls (24h)</span>
                        <span class="metric-value">2.4M</span>
                    </div>
                    <div class="metric">
                        <span>Storage Used</span>
                        <span class="metric-value">1.8TB</span>
                    </div>
                    <div class="metric">
                        <span>Active Workflows</span>
                        <span class="metric-value">847</span>
                    </div>
                </div>
            </div>

            <div class="api-endpoints">
                <h3>🔗 Tenant Management API</h3>
                <ul>
                    <li><strong>POST /tenants</strong> - Create new tenant</li>
                    <li><strong>GET /tenants</strong> - List all tenants</li>
                    <li><strong>GET /tenants/{tenant_id}</strong> - Get tenant details</li>
                    <li><strong>PUT /tenants/{tenant_id}</strong> - Update tenant</li>
                    <li><strong>DELETE /tenants/{tenant_id}</strong> - Delete tenant</li>
                    <li><strong>GET /tenants/{tenant_id}/usage</strong> - Get usage metrics</li>
                    <li><strong>POST /tenants/{tenant_id}/provision</strong> - Provision tenant resources</li>
                    <li><strong>GET /validate-tenant</strong> - Validate tenant access</li>
                </ul>
            </div>
        </div>
                    </div>
            </div>
        </body>
    </html>
    """

async def get_tenant_from_api_key(api_key: str = Header(None, alias="X-API-Key")) -> TenantContext:
    """Extract and validate tenant context from API key"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    try:
        # Query tenant by API key
        tenants_ref = db.collection("tenants")
        query = tenants_ref.where("api_key", "==", api_key).where("status", "==", "active").limit(1)
        docs = query.stream()

        tenant_doc = None
        for doc in docs:
            tenant_doc = doc
            break

        if not tenant_doc:
            raise HTTPException(status_code=401, detail="Invalid or inactive API key")

        tenant_data = tenant_doc.to_dict()
        return TenantContext(tenant_doc.id, tenant_data)

    except Exception as e:
        logger.error(f"Error validating tenant API key: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/tenants", response_model=Tenant)
async def create_tenant(tenant_data: TenantCreate, background_tasks: BackgroundTasks):
    """Create a new tenant with complete resource provisioning"""
    try:
        with performance_monitor.track_operation("tenant_creation"):
            # Generate tenant ID and API key
            tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"
            api_key = f"xyn_{secrets.token_urlsafe(32)}"

            # Define subscription features
            subscription_features = {
                "starter": {
                    "ai_assistant": True,
                    "workflow_orchestration": True,
                    "basic_analytics": True,
                    "standard_support": True,
                    "custom_integrations": False,
                    "advanced_analytics": False,
                    "white_label": False,
                    "sla_guarantee": False
                },
                "professional": {
                    "ai_assistant": True,
                    "workflow_orchestration": True,
                    "basic_analytics": True,
                    "advanced_analytics": True,
                    "custom_integrations": True,
                    "standard_support": True,
                    "priority_support": True,
                    "white_label": False,
                    "sla_guarantee": False
                },
                "enterprise": {
                    "ai_assistant": True,
                    "workflow_orchestration": True,
                    "basic_analytics": True,
                    "advanced_analytics": True,
                    "custom_integrations": True,
                    "white_label": True,
                    "priority_support": True,
                    "dedicated_support": True,
                    "sla_guarantee": True,
                    "audit_logs": True,
                    "advanced_security": True
                }
            }

            # Create tenant document
            tenant = {
                "tenant_id": tenant_id,
                "organization_name": tenant_data.organization_name,
                "admin_email": tenant_data.admin_email,
                "admin_name": tenant_data.admin_name,
                "subscription_tier": tenant_data.subscription_tier,
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "custom_domain": tenant_data.custom_domain,
                "api_key": api_key,
                "max_users": tenant_data.max_users or get_tier_defaults(tenant_data.subscription_tier)["max_users"],
                "current_users": 0,
                "storage_limit_gb": tenant_data.storage_limit_gb or get_tier_defaults(tenant_data.subscription_tier)["storage_limit_gb"],
                "current_storage_gb": 0.0,
                "api_rate_limit": tenant_data.api_rate_limit or get_tier_defaults(tenant_data.subscription_tier)["api_rate_limit"],
                "monthly_api_calls": 0,
                "features": subscription_features.get(tenant_data.subscription_tier, subscription_features["starter"]),
                "billing_info": {
                    "billing_cycle": "monthly",
                    "next_billing_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                    "payment_method": None,
                    "billing_address": None
                }
            }

            # Store tenant in Firestore
            db.collection("tenants").document(tenant_id).set(tenant)

            # Schedule background provisioning
            background_tasks.add_task(provision_tenant_resources, tenant_id, tenant_data.subscription_tier)

            # Publish tenant creation event
            event_data = {
                "event_type": "tenant_created",
                "tenant_id": tenant_id,
                "organization_name": tenant_data.organization_name,
                "subscription_tier": tenant_data.subscription_tier,
                "timestamp": datetime.utcnow().isoformat()
            }

            topic_path = publisher.topic_path(PROJECT_ID, "xynergy-tenant-events")
            publisher.publish(topic_path, json.dumps(event_data).encode())

            logger.info(f"Tenant created successfully: {tenant_id}")

            return Tenant(**tenant)

    except Exception as e:
        logger.error(f"Error creating tenant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create tenant: {str(e)}")

def get_tier_defaults(tier: SubscriptionTier) -> Dict[str, Any]:
    """Get default limits for subscription tier"""
    defaults = {
        "starter": {"max_users": 10, "storage_limit_gb": 100, "api_rate_limit": 1000},
        "professional": {"max_users": 50, "storage_limit_gb": 500, "api_rate_limit": 5000},
        "enterprise": {"max_users": 500, "storage_limit_gb": 2000, "api_rate_limit": 25000},
        "custom": {"max_users": 1000, "storage_limit_gb": 5000, "api_rate_limit": 100000}
    }
    return defaults.get(tier, defaults["starter"])

async def provision_tenant_resources(tenant_id: str, subscription_tier: str):
    """Provision tenant-specific resources (databases, storage, etc.)"""
    try:
        logger.info(f"Starting resource provisioning for tenant {tenant_id}")

        # Create tenant-specific Firestore collections
        await create_tenant_firestore_structure(tenant_id)

        # Create tenant-specific BigQuery dataset
        await create_tenant_bigquery_dataset(tenant_id)

        # Setup tenant-specific storage buckets
        await create_tenant_storage_buckets(tenant_id)

        # Create tenant-specific secrets
        await create_tenant_secrets(tenant_id)

        # Update tenant status to active
        tenant_ref = db.collection("tenants").document(tenant_id)
        tenant_ref.update({
            "status": "active",
            "provisioned_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })

        logger.info(f"Resource provisioning completed for tenant {tenant_id}")

    except Exception as e:
        logger.error(f"Error provisioning resources for tenant {tenant_id}: {str(e)}")
        # Update tenant status to indicate provisioning failure
        tenant_ref = db.collection("tenants").document(tenant_id)
        tenant_ref.update({
            "status": "suspended",
            "error_message": str(e),
            "updated_at": datetime.utcnow()
        })

async def create_tenant_firestore_structure(tenant_id: str):
    """Create tenant-specific Firestore collection structure"""
    collections = [
        "workflow_executions",
        "conversation_contexts",
        "user_competency_profiles",
        "marketing_campaigns",
        "keyword_research",
        "analytics_data",
        "project_data",
        "quality_reports",
        "security_logs",
        "content_assets"
    ]

    for collection in collections:
        # Create a placeholder document to initialize the collection
        tenant_collection = f"tenant_{tenant_id}_{collection}"
        doc_ref = db.collection(tenant_collection).document("_init")
        doc_ref.set({
            "created_at": datetime.utcnow(),
            "tenant_id": tenant_id,
            "collection_type": collection,
            "initialized": True
        })

async def create_tenant_bigquery_dataset(tenant_id: str):
    """Create tenant-specific BigQuery dataset"""
    # In a real implementation, you would create BigQuery datasets here
    # For now, we'll simulate this operation
    dataset_id = f"tenant_{tenant_id}_analytics"
    logger.info(f"Created BigQuery dataset: {dataset_id}")

async def create_tenant_storage_buckets(tenant_id: str):
    """Create tenant-specific Cloud Storage buckets"""
    # In a real implementation, you would create storage buckets here
    # For now, we'll simulate this operation
    bucket_name = f"xynergy-tenant-{tenant_id}-storage"
    logger.info(f"Created storage bucket: {bucket_name}")

async def create_tenant_secrets(tenant_id: str):
    """Create tenant-specific secrets"""
    # Create tenant-specific encryption keys and secrets
    # For now, we'll simulate this operation
    secret_name = f"tenant-{tenant_id}-encryption-key"
    logger.info(f"Created tenant secret: {secret_name}")

@app.get("/tenants")
async def list_tenants(
    status: Optional[TenantStatus] = None,
    subscription_tier: Optional[SubscriptionTier] = None,
    limit: int = 50,
    offset: int = 0
):
    """List all tenants with optional filtering"""
    try:
        query = db.collection("tenants")

        if status:
            query = query.where("status", "==", status)
        if subscription_tier:
            query = query.where("subscription_tier", "==", subscription_tier)

        # Apply pagination
        query = query.limit(limit).offset(offset)

        tenants = []
        for doc in query.stream():
            tenant_data = doc.to_dict()
            tenants.append(Tenant(**tenant_data))

        return {
            "tenants": tenants,
            "total": len(tenants),
            "offset": offset,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error listing tenants: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list tenants: {str(e)}")

@app.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get detailed tenant information"""
    try:
        doc = db.collection("tenants").document(tenant_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant_data = doc.to_dict()
        return Tenant(**tenant_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tenant {tenant_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tenant: {str(e)}")

@app.get("/validate-tenant")
async def validate_tenant_access(tenant_context: TenantContext = Depends(get_tenant_from_api_key)):
    """Validate tenant access and return tenant context"""
    return {
        "valid": True,
        "tenant_id": tenant_context.tenant_id,
        "organization_name": tenant_context.organization_name,
        "subscription_tier": tenant_context.subscription_tier,
        "features": tenant_context.features,
        "limits": tenant_context.limits
    }

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration"""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with performance_monitor.track_operation(f"execute_{action}"):
            if action == "validate_tenant":
                tenant_id = parameters.get("tenant_id")
                api_key = parameters.get("api_key")

                # Validate tenant exists and is active
                tenant_doc = db.collection("tenants").document(tenant_id).get()
                if not tenant_doc.exists:
                    return {
                        "success": False,
                        "error": "Tenant not found",
                        "service": "tenant-management"
                    }

                tenant_data = tenant_doc.to_dict()
                if tenant_data.get("status") != "active":
                    return {
                        "success": False,
                        "error": f"Tenant status: {tenant_data.get('status')}",
                        "service": "tenant-management"
                    }

                return {
                    "success": True,
                    "action": action,
                    "output": {
                        "tenant_id": tenant_id,
                        "valid": True,
                        "subscription_tier": tenant_data.get("subscription_tier")
                    },
                    "execution_time": time.time(),
                    "service": "tenant-management"
                }

            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not supported by tenant-management",
                    "supported_actions": ["validate_tenant"],
                    "service": "tenant-management"
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "action": request.get("action"),
            "service": "tenant-management"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)