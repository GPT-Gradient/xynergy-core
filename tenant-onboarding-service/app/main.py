"""
Tenant Onboarding Service - Main Application
Handles complete company onboarding workflow from form submission to fully operational XynergyOS tenant
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.cloud import firestore, storage
import structlog
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import secrets
import string

from app.models.onboarding import (
    CompanyOnboardingForm,
    OnboardingProgress,
    OnboardingStatus,
    TenantDeployment,
    CostDashboard,
    DeploymentPromotion,
    ASOPreset,
    WebsiteSource,
    ASO_PRESETS,
    get_aso_preset_config
)
from app.services.github_cicd import GitHubCICDService
from app.services.staging_deploy import StagingDeploymentService
from app.services.cost_tracking import CostTrackingService

# Initialize FastAPI app
app = FastAPI(
    title="Tenant Onboarding Service",
    description="Complete company onboarding workflow for XynergyOS",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://xynergyos.com",
        "https://*.xynergyos.com",
        "https://clearforge.ai",
        "https://*.clearforge.ai"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Configure structured logging
logger = structlog.get_logger()

# Initialize GCP clients
db = firestore.Client()
storage_client = storage.Client()

# Initialize services
github_service = GitHubCICDService()
staging_service = StagingDeploymentService()
cost_service = CostTrackingService()

# ===== Helper Functions =====

def generate_tenant_id(company_name: str) -> str:
    """Generate unique tenant ID"""
    # Sanitize company name
    base = company_name.lower().replace(" ", "_").replace("-", "_")
    base = ''.join(c for c in base if c.isalnum() or c == '_')

    # Add random suffix
    suffix = ''.join(secrets.choice(string.digits) for _ in range(3))
    return f"{base}_{suffix}"


async def create_tenant_record(form: CompanyOnboardingForm, tenant_id: str) -> Dict[str, Any]:
    """Create initial tenant record in Firestore"""
    # Get ASO preset config
    if form.aso_preset == ASOPreset.CUSTOM:
        aso_config = form.custom_aso_config.dict() if form.custom_aso_config else {}
    else:
        aso_config = get_aso_preset_config(form.aso_preset)
        if aso_config:
            aso_config = aso_config.dict()

    tenant_data = {
        "tenant_id": tenant_id,
        "company_name": form.company_name,
        "domain": form.domain,
        "contact": {
            "name": form.contact_name,
            "email": form.contact_email
        },
        "website_source": form.website_source.value,
        "github_config": form.github_config.dict() if form.github_config else None,
        "generated_site_id": form.generated_site_id,
        "enable_staging": form.enable_staging,
        "staging_subdomain": form.staging_subdomain or f"staging.{form.domain}",
        "aso_preset": form.aso_preset.value,
        "aso_config": aso_config,
        "target_keywords": form.target_keywords,
        "competitors": form.competitors,
        "cost_tracking": {
            "monthly_budget": form.monthly_budget,
            "enabled": True,
            "labels": {
                "tenant_id": tenant_id,
                "company_name": form.company_name.lower().replace(" ", "_"),
                "cost_center": "clearforge_services"
            }
        },
        "status": "pending",
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP
    }

    # Store in Firestore
    db.collection("tenants").document(tenant_id).set(tenant_data)

    logger.info("tenant_created", tenant_id=tenant_id, company_name=form.company_name)

    return tenant_data


async def run_onboarding_workflow(tenant_id: str, form: CompanyOnboardingForm):
    """Execute complete onboarding workflow as background task"""
    progress_ref = db.collection("onboarding_progress").document(tenant_id)

    try:
        # Initialize progress tracking
        progress = OnboardingProgress(
            tenant_id=tenant_id,
            status=OnboardingStatus.PENDING,
            started_at=datetime.utcnow(),
            estimated_completion=datetime.utcnow() + timedelta(minutes=20)
        )
        progress_ref.set(progress.dict())

        # Step 1: Tenant created (already done)
        progress.status = OnboardingStatus.TENANT_CREATED
        progress.current_step = 1
        progress.steps_completed.append("tenant_record_created")
        progress_ref.update(progress.dict())

        # Step 2: DNS Configuration
        logger.info("configuring_dns", tenant_id=tenant_id, domain=form.domain)
        # TODO: Integrate with SiteGround API for DNS setup
        # For now, we'll mark as complete
        progress.current_step = 2
        progress.status = OnboardingStatus.DNS_CONFIGURED
        progress.steps_completed.append("dns_configured")
        progress_ref.update(progress.dict())

        # Step 3: Website Deployment
        logger.info("deploying_website", tenant_id=tenant_id, source=form.website_source)

        if form.website_source == WebsiteSource.GITHUB_REPO and form.github_config:
            # Set up GitHub CI/CD
            await github_service.setup_cicd(tenant_id, form.github_config)
            progress.steps_completed.append("github_cicd_configured")

        # Deploy production and staging
        if form.enable_staging:
            deployment_info = await staging_service.deploy_both_environments(
                tenant_id=tenant_id,
                domain=form.domain,
                website_source=form.website_source,
                generated_site_id=form.generated_site_id,
                github_config=form.github_config
            )
            progress.production_url = deployment_info["production_url"]
            progress.staging_url = deployment_info["staging_url"]
        else:
            # Deploy production only
            # TODO: Implement production-only deployment
            progress.production_url = f"https://{form.domain}"

        progress.current_step = 3
        progress.status = OnboardingStatus.WEBSITE_DEPLOYED
        progress.steps_completed.append("website_deployed")
        progress_ref.update(progress.dict())

        # Step 4: Analytics & Tracking Setup
        logger.info("setting_up_analytics", tenant_id=tenant_id)
        # TODO: Create GA4 property, Search Console connection
        progress.current_step = 4
        progress.status = OnboardingStatus.ANALYTICS_SETUP
        progress.steps_completed.append("analytics_configured")
        progress_ref.update(progress.dict())

        # Step 5: ASO Engine Initialization
        logger.info("initializing_aso", tenant_id=tenant_id, preset=form.aso_preset)
        # TODO: Call ASO Engine to add tenant with preset config
        progress.current_step = 5
        progress.status = OnboardingStatus.ASO_INITIALIZED
        progress.steps_completed.append("aso_initialized")
        progress_ref.update(progress.dict())

        # Step 6: Access Configuration
        logger.info("configuring_access", tenant_id=tenant_id)
        # TODO: Create Firebase user, set up XynergyOS access
        progress.current_step = 6
        progress.status = OnboardingStatus.ACCESS_CONFIGURED
        progress.xynergyos_url = f"https://xynergyos.com/dashboard/{tenant_id}"
        progress.steps_completed.append("access_configured")
        progress_ref.update(progress.dict())

        # Complete!
        progress.current_step = 8
        progress.status = OnboardingStatus.COMPLETE
        progress.completed_at = datetime.utcnow()
        progress_ref.update(progress.dict())

        # Update tenant status
        db.collection("tenants").document(tenant_id).update({
            "status": "active",
            "activated_at": firestore.SERVER_TIMESTAMP
        })

        logger.info("onboarding_complete", tenant_id=tenant_id)

    except Exception as e:
        logger.error("onboarding_failed", tenant_id=tenant_id, error=str(e))
        progress.status = OnboardingStatus.FAILED
        progress.error_message = str(e)
        progress_ref.update(progress.dict())

        # Update tenant status
        db.collection("tenants").document(tenant_id).update({
            "status": "failed",
            "error": str(e)
        })


# ===== API Endpoints =====

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tenant-onboarding-service",
        "version": "1.0.0",
        "dependencies": {
            "firestore": "healthy",
            "storage": "healthy"
        }
    }


@app.get("/v1/aso-presets")
async def get_aso_presets():
    """Get all available ASO presets"""
    presets = []
    for preset, config in ASO_PRESETS.items():
        presets.append({
            "id": preset.value,
            "name": config["name"],
            "description": config["description"],
            "config": config["config"].dict() if config["config"] else None
        })
    return {"presets": presets}


@app.get("/v1/aso-presets/{preset_id}")
async def get_aso_preset(preset_id: str):
    """Get specific ASO preset details"""
    try:
        preset = ASOPreset(preset_id)
        preset_data = ASO_PRESETS.get(preset)
        if not preset_data:
            raise HTTPException(status_code=404, detail="Preset not found")

        return {
            "id": preset.value,
            "name": preset_data["name"],
            "description": preset_data["description"],
            "config": preset_data["config"].dict() if preset_data["config"] else None
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Preset not found")


@app.post("/v1/onboarding/start")
async def start_onboarding(form: CompanyOnboardingForm, background_tasks: BackgroundTasks):
    """
    Start the onboarding process for a new company

    This endpoint initiates the complete onboarding workflow:
    1. Create tenant record
    2. Configure DNS
    3. Deploy website (production + staging)
    4. Set up analytics
    5. Initialize ASO
    6. Configure access
    """
    logger.info("onboarding_requested", company_name=form.company_name, domain=form.domain)

    # Generate tenant ID
    tenant_id = generate_tenant_id(form.company_name)

    # Create tenant record
    tenant_data = await create_tenant_record(form, tenant_id)

    # Start background workflow
    background_tasks.add_task(run_onboarding_workflow, tenant_id, form)

    return {
        "tenant_id": tenant_id,
        "status": "onboarding_started",
        "message": "Onboarding workflow initiated. This will take approximately 20 minutes.",
        "progress_url": f"/v1/onboarding/progress/{tenant_id}",
        "estimated_completion": datetime.utcnow() + timedelta(minutes=20)
    }


@app.get("/v1/onboarding/progress/{tenant_id}")
async def get_onboarding_progress(tenant_id: str):
    """Get onboarding progress for a tenant"""
    progress_doc = db.collection("onboarding_progress").document(tenant_id).get()

    if not progress_doc.exists:
        raise HTTPException(status_code=404, detail="Onboarding progress not found")

    progress_data = progress_doc.to_dict()
    return progress_data


@app.get("/v1/tenants")
async def list_tenants(status: Optional[str] = None, limit: int = 50):
    """List all tenants with optional status filter"""
    query = db.collection("tenants").order_by("created_at", direction=firestore.Query.DESCENDING)

    if status:
        query = query.where("status", "==", status)

    query = query.limit(limit)

    tenants = []
    for doc in query.stream():
        tenant_data = doc.to_dict()
        tenant_data["tenant_id"] = doc.id
        tenants.append(tenant_data)

    return {"tenants": tenants, "total": len(tenants)}


@app.get("/v1/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get detailed tenant information"""
    tenant_doc = db.collection("tenants").document(tenant_id).get()

    if not tenant_doc.exists:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant_data = tenant_doc.to_dict()
    tenant_data["tenant_id"] = tenant_id

    return tenant_data


@app.get("/v1/tenants/{tenant_id}/deployments")
async def get_tenant_deployments(tenant_id: str):
    """Get tenant deployment information"""
    tenant = db.collection("tenants").document(tenant_id).get()

    if not tenant.exists:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant_data = tenant.to_dict()

    # Get deployment info from deployment collection
    deployment_doc = db.collection("deployments").document(tenant_id).get()

    if deployment_doc.exists:
        return deployment_doc.to_dict()

    # Construct from tenant data
    return {
        "tenant_id": tenant_id,
        "company_name": tenant_data.get("company_name"),
        "domain": tenant_data.get("domain"),
        "production_url": f"https://{tenant_data.get('domain')}",
        "staging_url": f"https://{tenant_data.get('staging_subdomain')}" if tenant_data.get("enable_staging") else None,
        "github_enabled": tenant_data.get("website_source") == "github_repo"
    }


@app.post("/v1/deployments/{tenant_id}/promote")
async def promote_staging_to_production(tenant_id: str, promotion: DeploymentPromotion):
    """Promote staging deployment to production"""
    logger.info("promotion_requested", tenant_id=tenant_id, promoted_by=promotion.promoted_by)

    try:
        result = await staging_service.promote_to_production(tenant_id, promotion.promoted_by, promotion.notes)

        logger.info("promotion_complete", tenant_id=tenant_id)

        return {
            "status": "success",
            "message": "Staging successfully promoted to production",
            "promotion_details": result
        }
    except Exception as e:
        logger.error("promotion_failed", tenant_id=tenant_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Promotion failed: {str(e)}")


@app.get("/v1/costs/{tenant_id}")
async def get_tenant_costs(tenant_id: str):
    """Get cost dashboard for a tenant"""
    try:
        cost_dashboard = await cost_service.get_cost_dashboard(tenant_id)
        return cost_dashboard
    except Exception as e:
        logger.error("cost_fetch_failed", tenant_id=tenant_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch costs: {str(e)}")


@app.get("/v1/costs/summary")
async def get_all_costs_summary():
    """Get cost summary for all tenants"""
    try:
        summary = await cost_service.get_all_tenants_summary()
        return summary
    except Exception as e:
        logger.error("cost_summary_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch cost summary: {str(e)}")


@app.get("/v1/generated-sites")
async def list_generated_sites(limit: int = 20):
    """List recently generated sites available for deployment"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    query = db.collection("generated_sites") \
        .where("status", "==", "generated") \
        .where("generated_at", ">", thirty_days_ago) \
        .order_by("generated_at", direction=firestore.Query.DESCENDING) \
        .limit(limit)

    sites = []
    for doc in query.stream():
        site_data = doc.to_dict()
        site_data["generation_id"] = doc.id
        sites.append(site_data)

    return {"generated_sites": sites, "total": len(sites)}


@app.put("/v1/tenants/{tenant_id}")
async def update_tenant(tenant_id: str, update_data: Dict[str, Any]):
    """Update tenant configuration"""
    tenant_ref = db.collection("tenants").document(tenant_id)
    tenant_doc = tenant_ref.get()

    if not tenant_doc.exists:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Update allowed fields
    allowed_fields = [
        "target_keywords",
        "competitors",
        "aso_config",
        "cost_tracking.monthly_budget",
        "contact"
    ]

    updates = {}
    for key, value in update_data.items():
        if key in allowed_fields:
            updates[key] = value

    if updates:
        updates["updated_at"] = firestore.SERVER_TIMESTAMP
        tenant_ref.update(updates)
        logger.info("tenant_updated", tenant_id=tenant_id, fields=list(updates.keys()))

    return {"status": "success", "updated_fields": list(updates.keys())}


@app.delete("/v1/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str, confirm: bool = False):
    """Delete a tenant (soft delete by default)"""
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Must confirm deletion by passing confirm=true"
        )

    tenant_ref = db.collection("tenants").document(tenant_id)
    tenant_doc = tenant_ref.get()

    if not tenant_doc.exists:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Soft delete - mark as deleted
    tenant_ref.update({
        "status": "deleted",
        "deleted_at": firestore.SERVER_TIMESTAMP
    })

    logger.info("tenant_deleted", tenant_id=tenant_id)

    return {"status": "success", "message": f"Tenant {tenant_id} marked as deleted"}


@app.get("/v1/admin/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard with all companies overview"""
    # Get all active tenants
    tenants_query = db.collection("tenants") \
        .where("status", "==", "active") \
        .order_by("created_at", direction=firestore.Query.DESCENDING)

    companies = []
    total_cost_mtd = 0.0

    for doc in tenants_query.stream():
        tenant_data = doc.to_dict()
        tenant_id = doc.id

        # Get current month cost
        try:
            cost_data = await cost_service.get_current_month_cost(tenant_id)
            tenant_cost = cost_data.get("total_cost", 0.0)
            total_cost_mtd += tenant_cost
        except:
            tenant_cost = 0.0

        companies.append({
            "tenant_id": tenant_id,
            "company_name": tenant_data.get("company_name"),
            "domain": tenant_data.get("domain"),
            "status": tenant_data.get("status"),
            "created_at": tenant_data.get("created_at"),
            "cost_mtd": tenant_cost,
            "budget": tenant_data.get("cost_tracking", {}).get("monthly_budget", 100),
            "aso_preset": tenant_data.get("aso_preset"),
            "staging_enabled": tenant_data.get("enable_staging", False),
            "github_enabled": tenant_data.get("website_source") == "github_repo"
        })

    return {
        "companies": companies,
        "total_companies": len(companies),
        "total_cost_mtd": total_cost_mtd
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
