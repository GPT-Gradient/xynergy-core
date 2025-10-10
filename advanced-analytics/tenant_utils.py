"""
Shared tenant isolation utilities for Xynergy Platform services.
This module provides consistent tenant context handling across all services.
"""

import os
import structlog
from fastapi import Header, HTTPException, Request
from typing import Optional, Dict, Any
from functools import wraps
from google.cloud import firestore
import httpx

logger = structlog.get_logger()

class TenantContext:
    def __init__(self, tenant_id: str, subscription_tier: str = "starter", features: Dict[str, bool] = None):
        self.tenant_id = tenant_id
        self.subscription_tier = subscription_tier
        self.features = features or {}

    def get_collection_name(self, base_collection: str) -> str:
        """Get tenant-specific collection name for Firestore"""
        return f"tenant_{self.tenant_id}_{base_collection}"

    def get_bigquery_dataset(self, base_dataset: str) -> str:
        """Get tenant-specific BigQuery dataset name"""
        return f"tenant_{self.tenant_id}_{base_dataset}"

    def has_feature(self, feature_name: str) -> bool:
        """Check if tenant has access to a specific feature"""
        return self.features.get(feature_name, False)

    def get_resource_limits(self) -> Dict[str, int]:
        """Get resource limits based on subscription tier"""
        limits = {
            "starter": {
                "max_campaigns": 5,
                "max_projects": 10,
                "max_workflows_per_day": 50,
                "max_storage_gb": 1,
                "max_ai_requests_per_day": 100
            },
            "professional": {
                "max_campaigns": 25,
                "max_projects": 50,
                "max_workflows_per_day": 500,
                "max_storage_gb": 10,
                "max_ai_requests_per_day": 1000
            },
            "enterprise": {
                "max_campaigns": 100,
                "max_projects": 200,
                "max_workflows_per_day": 5000,
                "max_storage_gb": 100,
                "max_ai_requests_per_day": 10000
            },
            "custom": {
                "max_campaigns": 999999,
                "max_projects": 999999,
                "max_workflows_per_day": 999999,
                "max_storage_gb": 999999,
                "max_ai_requests_per_day": 999999
            }
        }
        return limits.get(self.subscription_tier, limits["starter"])

# Global tenant context for request lifecycle
_current_tenant_context: Optional[TenantContext] = None

def get_current_tenant() -> Optional[TenantContext]:
    """Get the current tenant context for this request"""
    return _current_tenant_context

def set_current_tenant(tenant_context: TenantContext):
    """Set the current tenant context for this request"""
    global _current_tenant_context
    _current_tenant_context = tenant_context

async def validate_tenant_api_key(api_key: str) -> Optional[TenantContext]:
    """Validate tenant API key and return tenant context"""
    if not api_key:
        return None

    try:
        # Call tenant management service to validate API key
        tenant_mgmt_url = os.getenv("TENANT_MGMT_URL", "https://xynergy-tenant-management-835612502919.us-central1.run.app")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{tenant_mgmt_url}/validate-api-key",
                headers={"X-API-Key": api_key}
            )

            if response.status_code == 200:
                tenant_data = response.json()
                return TenantContext(
                    tenant_id=tenant_data["tenant_id"],
                    subscription_tier=tenant_data["subscription_tier"],
                    features=tenant_data["features"]
                )
            else:
                logger.warning("Invalid API key provided", api_key_prefix=api_key[:8])
                return None

    except Exception as e:
        logger.error("Failed to validate tenant API key", error=str(e))
        return None

async def get_tenant_context(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")
) -> Optional[TenantContext]:
    """
    FastAPI dependency to extract and validate tenant context from request headers.
    Supports both API key and direct tenant ID approaches.
    """

    # Primary method: API key validation
    if x_api_key:
        tenant_context = await validate_tenant_api_key(x_api_key)
        if tenant_context:
            set_current_tenant(tenant_context)
            return tenant_context

    # Fallback method: Direct tenant ID (for internal service communication)
    if x_tenant_id:
        # For internal services, create basic tenant context
        # In production, this should also validate against tenant management service
        tenant_context = TenantContext(
            tenant_id=x_tenant_id,
            subscription_tier="enterprise",  # Default for internal calls
            features={"all": True}
        )
        set_current_tenant(tenant_context)
        return tenant_context

    # No tenant context found
    return None

def require_tenant(allow_system: bool = False):
    """
    Decorator to require tenant context for endpoints.

    Args:
        allow_system: If True, allows requests without tenant context (for system endpoints)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tenant_context = get_current_tenant()

            if not tenant_context and not allow_system:
                raise HTTPException(
                    status_code=401,
                    detail="Missing or invalid tenant authentication. Please provide X-API-Key header."
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

def check_feature_access(feature_name: str):
    """
    Decorator to check if current tenant has access to a specific feature.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            tenant_context = get_current_tenant()

            if not tenant_context:
                raise HTTPException(
                    status_code=401,
                    detail="Missing tenant context"
                )

            if not tenant_context.has_feature(feature_name):
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied. Feature '{feature_name}' not available in {tenant_context.subscription_tier} plan."
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

def check_resource_limits(resource_type: str, current_usage: int):
    """
    Check if current tenant is within resource limits.

    Args:
        resource_type: Type of resource (e.g., 'max_campaigns', 'max_projects')
        current_usage: Current usage count

    Raises:
        HTTPException: If limit is exceeded
    """
    tenant_context = get_current_tenant()
    if not tenant_context:
        return

    limits = tenant_context.get_resource_limits()
    limit = limits.get(resource_type, 0)

    if current_usage >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Resource limit exceeded. {resource_type}: {current_usage}/{limit}. Upgrade your plan for higher limits."
        )

class TenantFirestoreClient:
    """
    Wrapper around Firestore client that automatically handles tenant isolation.
    """

    def __init__(self, db: firestore.Client):
        self.db = db

    def collection(self, collection_name: str):
        """Get tenant-specific collection"""
        tenant_context = get_current_tenant()
        if tenant_context:
            tenant_collection_name = tenant_context.get_collection_name(collection_name)
        else:
            # Fallback to system collection for non-tenant requests
            tenant_collection_name = f"system_{collection_name}"

        return self.db.collection(tenant_collection_name)

    def get_tenant_document(self, collection_name: str, document_id: str):
        """Get document from tenant-specific collection"""
        return self.collection(collection_name).document(document_id)

def get_tenant_aware_firestore(db: firestore.Client) -> TenantFirestoreClient:
    """Get a tenant-aware Firestore client"""
    return TenantFirestoreClient(db)

def add_tenant_middleware(app):
    """
    Add tenant context middleware to FastAPI app.
    This middleware extracts tenant context from headers and makes it available throughout the request.
    """

    @app.middleware("http")
    async def tenant_context_middleware(request: Request, call_next):
        # Extract tenant context from headers
        api_key = request.headers.get("X-API-Key")
        tenant_id = request.headers.get("X-Tenant-ID")

        tenant_context = None

        if api_key:
            tenant_context = await validate_tenant_api_key(api_key)
        elif tenant_id:
            tenant_context = TenantContext(
                tenant_id=tenant_id,
                subscription_tier="enterprise",
                features={"all": True}
            )

        # Set tenant context for this request
        if tenant_context:
            set_current_tenant(tenant_context)
            logger.info("Tenant context set", tenant_id=tenant_context.tenant_id, tier=tenant_context.subscription_tier)

        try:
            response = await call_next(request)
            return response
        finally:
            # Clear tenant context after request
            set_current_tenant(None)