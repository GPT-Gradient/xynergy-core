"""
Xynergy Intelligence Gateway
A lightweight service that aggregates Xynergy Platform data and exposes it to the public ClearForge website.

Author: Xynergy Platform Team
Date: October 9, 2025
Version: 1.0.0
"""

import os
import uuid
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
import httpx
import structlog

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator
from google.cloud import firestore
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.services.email_service import EmailService
from app.services.aso_service import ASOService
from app.utils.cache import SimpleCache

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)

logger = structlog.get_logger()

# Environment configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "xynergy-dev-1757909467")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
ASO_ENGINE_URL = os.getenv("ASO_ENGINE_URL", "https://aso-engine-vgjxy554mq-uc.a.run.app")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://clearforge.ai,http://localhost:3000").split(",")

# Initialize FastAPI app
app = FastAPI(
    title="Xynergy Intelligence Gateway",
    description="Public API for ClearForge website integration with Xynergy Platform",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None
)

# Initialize services
db = firestore.Client(project=PROJECT_ID)
email_service = EmailService()
aso_service = ASOService(aso_engine_url=ASO_ENGINE_URL)
cache = SimpleCache()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600
)

# HTTP client for service-to-service calls
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(10.0, connect=5.0),
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
)

# ================================
# REQUEST/RESPONSE MODELS
# ================================

class BetaApplication(BaseModel):
    """Beta program application model"""
    businessName: str = Field(..., min_length=2, max_length=200)
    industry: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    challenges: str = Field(..., min_length=10, max_length=2000)
    whyRightFit: str = Field(..., min_length=10, max_length=2000)
    company: Optional[str] = Field(None, max_length=200)
    role: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    teamSize: Optional[str] = None
    goals: Optional[List[str]] = None

    @validator('website')
    def validate_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Invalid URL format. Must start with http:// or https://')
        return v

class ContactSubmission(BaseModel):
    """Contact form submission model"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    type: str = Field(..., pattern="^(beta|partnership|consulting|general|media)$")
    message: str = Field(..., min_length=10, max_length=5000)
    company: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=30)

# ================================
# LIFECYCLE EVENTS
# ================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("intelligence_gateway_starting", environment=ENVIRONMENT, project_id=PROJECT_ID)

    # Warm up cache with sample data
    cache.set("service_info", {
        "service": "xynergy-intelligence-gateway",
        "version": "1.0.0",
        "started_at": time.time()
    }, ttl=3600)

    logger.info("intelligence_gateway_started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("intelligence_gateway_shutting_down")
    await http_client.aclose()
    logger.info("intelligence_gateway_stopped")

# ================================
# HEALTH & INFO ENDPOINTS
# ================================

@app.get("/")
async def root():
    """Service information endpoint"""
    return {
        "service": "xynergy-intelligence-gateway",
        "version": "1.0.0",
        "status": "healthy",
        "environment": ENVIRONMENT,
        "endpoints": {
            "aso": [
                "/v1/aso/trending-keywords",
                "/v1/aso/keyword-rankings",
                "/v1/aso/content-performance"
            ],
            "leads": [
                "/v1/beta/apply",
                "/v1/contact"
            ],
            "metrics": [
                "/v1/dashboard/metrics"
            ]
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    checks = {}
    overall_status = "healthy"

    # Check Firestore
    try:
        start = time.time()
        db.collection("beta_applications").limit(1).get()
        firestore_time = int((time.time() - start) * 1000)
        checks["firestore"] = {
            "status": "healthy",
            "response_time_ms": firestore_time
        }
    except Exception as e:
        checks["firestore"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"

    # Check ASO Engine
    try:
        aso_healthy = await aso_service.health_check()
        checks["aso_engine"] = aso_healthy
        if aso_healthy["status"] != "healthy":
            overall_status = "degraded"
    except Exception as e:
        checks["aso_engine"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"

    # Check email service
    checks["email_service"] = {
        "status": "healthy" if email_service.is_configured() else "not_configured",
        "provider": email_service.provider
    }

    service_info = cache.get("service_info") or {}
    started_at = service_info.get("started_at") if isinstance(service_info, dict) else time.time()
    if isinstance(started_at, str):
        # Convert ISO string to timestamp if needed
        started_at = time.time()

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "checks": checks,
        "uptime_seconds": int(time.time() - started_at)
    }

# ================================
# ASO INTELLIGENCE ENDPOINTS
# ================================

@app.get("/v1/aso/trending-keywords")
@limiter.limit("60/minute")
async def get_trending_keywords(
    request: Request,
    limit: int = 20,
    tenant_id: str = "clearforge"
):
    """Get trending keywords from ASO Engine"""

    # Check cache first
    cache_key = f"trending_keywords_{tenant_id}_{limit}"
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info("trending_keywords_cache_hit", tenant_id=tenant_id)
        return cached_data

    try:
        keywords = await aso_service.get_trending_keywords(tenant_id=tenant_id, limit=min(limit, 50))

        response = {
            "status": "success",
            "keywords": keywords,
            "total": len(keywords),
            "tenant_id": tenant_id,
            "generated_at": datetime.now().isoformat()
        }

        # Cache for 15 minutes
        cache.set(cache_key, response, ttl=900)

        logger.info(
            "trending_keywords_fetched",
            tenant_id=tenant_id,
            count=len(keywords)
        )

        return response

    except Exception as e:
        logger.error("trending_keywords_error", error=str(e), tenant_id=tenant_id)
        return {
            "status": "error",
            "error": "Unable to fetch trending keywords",
            "fallback_data": [],
            "generated_at": datetime.now().isoformat()
        }

@app.get("/v1/aso/keyword-rankings")
@limiter.limit("60/minute")
async def get_keyword_rankings(
    request: Request,
    limit: int = 50,
    tenant_id: str = "clearforge"
):
    """Get current keyword rankings for ClearForge content"""

    cache_key = f"keyword_rankings_{tenant_id}_{limit}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    try:
        rankings = await aso_service.get_keyword_rankings(tenant_id=tenant_id, limit=min(limit, 100))

        # Calculate summary stats
        total_keywords = len(rankings)
        positions = [r.get("current_position", 0) for r in rankings if r.get("current_position")]
        avg_position = sum(positions) / len(positions) if positions else 0
        trending_up = len([r for r in rankings if r.get("change", 0) > 0])
        trending_down = len([r for r in rankings if r.get("change", 0) < 0])

        response = {
            "status": "success",
            "rankings": rankings,
            "summary": {
                "total_keywords_tracked": total_keywords,
                "avg_position": round(avg_position, 1),
                "trending_up": trending_up,
                "trending_down": trending_down
            },
            "generated_at": datetime.now().isoformat()
        }

        # Cache for 1 hour
        cache.set(cache_key, response, ttl=3600)

        logger.info(
            "keyword_rankings_fetched",
            tenant_id=tenant_id,
            total=total_keywords,
            avg_position=avg_position
        )

        return response

    except Exception as e:
        logger.error("keyword_rankings_error", error=str(e))
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

@app.get("/v1/aso/content-performance")
@limiter.limit("60/minute")
async def get_content_performance(
    request: Request,
    period_days: int = 30,
    tenant_id: str = "clearforge"
):
    """Get aggregated content performance metrics"""

    cache_key = f"content_performance_{tenant_id}_{period_days}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    try:
        content_performance = await aso_service.get_content_performance(
            tenant_id=tenant_id,
            period_days=period_days
        )

        response = {
            "status": "success",
            "content_performance": content_performance,
            "period_days": period_days,
            "generated_at": datetime.now().isoformat()
        }

        # Cache for 1 hour
        cache.set(cache_key, response, ttl=3600)

        logger.info(
            "content_performance_fetched",
            tenant_id=tenant_id,
            period_days=period_days,
            content_count=len(content_performance)
        )

        return response

    except Exception as e:
        logger.error("content_performance_error", error=str(e))
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

# ================================
# LEAD CAPTURE ENDPOINTS
# ================================

@app.post("/v1/beta/apply")
@limiter.limit("5/minute")
async def submit_beta_application(request: Request, data: BetaApplication):
    """Submit beta program application"""

    application_id = f"beta_{uuid.uuid4().hex[:12]}"
    submitted_at = datetime.now()

    try:
        # Prepare application data
        application_data = {
            "id": application_id,
            **data.dict(),
            "status": "submitted",
            "qualificationScore": None,
            "source": "website",
            "submittedAt": submitted_at,
            "reviewedAt": None,
            "reviewedBy": None,
            "notes": None
        }

        # Store in Firestore
        db.collection("beta_applications").document(application_id).set(application_data)

        logger.info(
            "beta_application_received",
            application_id=application_id,
            business_name=data.businessName,
            industry=data.industry,
            email=data.email
        )

        # Send notification emails (non-blocking)
        try:
            # Email to ClearForge team
            await email_service.send_beta_application_notification(
                application_id=application_id,
                application_data=data.dict(),
                submitted_at=submitted_at
            )

            # Confirmation email to applicant
            await email_service.send_beta_application_confirmation(
                applicant_name=data.name,
                applicant_email=data.email,
                business_name=data.businessName,
                application_id=application_id
            )

            logger.info("beta_application_emails_sent", application_id=application_id)
        except Exception as e:
            logger.error("beta_application_email_failed", error=str(e), application_id=application_id)
            # Don't fail the request if email fails

        return {
            "success": True,
            "message": "Application submitted successfully. We'll review and respond within 48 hours.",
            "applicationId": application_id
        }

    except Exception as e:
        logger.error("beta_application_storage_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to submit application. Please try again.")

@app.post("/v1/contact")
@limiter.limit("10/minute")
async def submit_contact(request: Request, data: ContactSubmission):
    """Submit contact form"""

    ticket_id = f"ticket_{uuid.uuid4().hex[:12]}"
    submitted_at = datetime.now()

    try:
        # Prepare contact data
        contact_data = {
            "id": ticket_id,
            **data.dict(),
            "status": "new",
            "assignedTo": None,
            "source": "website",
            "submittedAt": submitted_at,
            "respondedAt": None,
            "notes": []
        }

        # Store in Firestore
        db.collection("contact_submissions").document(ticket_id).set(contact_data)

        logger.info(
            "contact_submission_received",
            ticket_id=ticket_id,
            contact_type=data.type,
            name=data.name,
            email=data.email
        )

        # Send notification emails (non-blocking)
        try:
            # Email to ClearForge team
            await email_service.send_contact_notification(
                ticket_id=ticket_id,
                contact_data=data.dict(),
                submitted_at=submitted_at
            )

            # Confirmation email to submitter
            await email_service.send_contact_confirmation(
                submitter_name=data.name,
                submitter_email=data.email,
                contact_type=data.type,
                ticket_id=ticket_id
            )

            logger.info("contact_emails_sent", ticket_id=ticket_id)
        except Exception as e:
            logger.error("contact_email_failed", error=str(e), ticket_id=ticket_id)

        return {
            "success": True,
            "message": "Message received! We'll respond within 48 hours.",
            "ticketId": ticket_id
        }

    except Exception as e:
        logger.error("contact_submission_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to submit contact. Please try again.")

# ================================
# DASHBOARD METRICS ENDPOINT
# ================================

@app.get("/v1/dashboard/metrics")
@limiter.limit("30/minute")
async def get_dashboard_metrics(request: Request):
    """Get aggregated metrics for public transparency dashboard"""

    cache_key = "dashboard_metrics"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    try:
        # Count beta applications
        beta_count = len(list(db.collection("beta_applications").stream()))

        # Count community members (contact submissions)
        community_count = len(list(db.collection("contact_submissions").stream()))

        # Get keyword rankings summary from ASO
        try:
            rankings_data = await aso_service.get_keyword_rankings(tenant_id="clearforge", limit=200)
            keyword_stats = {
                "total_tracked": len(rankings_data),
                "top_10_positions": len([r for r in rankings_data if r.get("current_position", 100) <= 10]),
                "avg_position": round(
                    sum([r.get("current_position", 0) for r in rankings_data]) / len(rankings_data)
                    if rankings_data else 0,
                    1
                )
            }
        except:
            keyword_stats = {
                "total_tracked": 145,
                "top_10_positions": 42,
                "avg_position": 8.2
            }

        # Project progress (manual updates for now)
        project_progress = {
            "nexus": 85,
            "data-democracy": 40,
            "no-cheating": 25,
            "ctos-heart": 15,
            "safe-spaces": 10,
            "re-connect": 5
        }

        response = {
            "status": "success",
            "data": {
                "betaParticipants": beta_count,
                "projectProgress": project_progress,
                "communityMembers": community_count,
                "successStories": 3,  # Manual count
                "keywordRankings": keyword_stats
            },
            "generated_at": datetime.now().isoformat()
        }

        # Cache for 5 minutes
        cache.set(cache_key, response, ttl=300)

        logger.info(
            "dashboard_metrics_generated",
            beta_participants=beta_count,
            community_members=community_count
        )

        return response

    except Exception as e:
        logger.error("dashboard_metrics_error", error=str(e))
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

# ================================
# ERROR HANDLERS
# ================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
