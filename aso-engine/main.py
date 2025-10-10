"""
ASO Engine - Adaptive Search Optimization Engine
Core service for content management, keyword tracking, and optimization recommendations
"""

import os
import sys
import time
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional
import logging
import psutil
import asyncio

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google.cloud import bigquery, storage, firestore
import structlog
from contextvars import ContextVar

# Import authentication, rate limiting, caching, and shared GCP clients
from auth import verify_api_key_header
from rate_limiting import rate_limit_standard, rate_limit_expensive
from gcp_clients import get_bigquery_client, get_storage_client, get_firestore_client
from redis_cache import RedisCache

# Import performance monitoring
from phase2_utils import PerformanceMonitor, CircuitBreaker, CircuitBreakerConfig

# Configure structured logging with context vars
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,  # Merge context vars (request_id, etc.)
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
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
CONTENT_BUCKET = f"{PROJECT_ID}-aso-content"

# Initialize GCP clients with connection pooling
bigquery_client = get_bigquery_client()
storage_client = get_storage_client()
firestore_client = get_firestore_client()

# Initialize performance monitoring
performance_monitor = PerformanceMonitor("aso-engine")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig())

# Initialize Redis cache
redis_cache = RedisCache()

# Request ID context for structured logging
request_id_context: ContextVar[str] = ContextVar("request_id", default="no-request-id")

app = FastAPI(
    title="ASO Engine",
    description="Adaptive Search Optimization Engine for content management and optimization",
    version="1.0.0"
)

# Request ID middleware for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracing"""
    request_id = request.headers.get("X-Request-ID", f"req_{uuid.uuid4().hex[:12]}")
    request_id_context.set(request_id)

    # Bind request_id to structlog context
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    # Clear context
    structlog.contextvars.clear_contextvars()

    return response

# Secure CORS (least-trust model)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://clearforge.ai",
        "https://xynergy.com",
        "https://dashboard.xynergy.com",
        f"https://platform-dashboard-{PROJECT_ID.split('-')[-1]}.us-central1.run.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-API-Key",
        "X-Request-ID"
    ],
    max_age=3600
)

# Request/Response Models
class ContentPiece(BaseModel):
    content_type: str = Field(..., max_length=50, description="Type: 'hub' or 'spoke'")
    keyword_primary: str = Field(..., min_length=1, max_length=200)
    keyword_secondary: List[str] = Field(default=[], max_items=50)
    title: str = Field(..., min_length=1, max_length=500)
    meta_description: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, max_length=2000)
    word_count: Optional[int] = Field(None, ge=0, le=50000)
    hub_id: Optional[str] = Field(None, max_length=100)
    tenant_id: str = Field(default="demo", max_length=100)

class ContentResponse(BaseModel):
    content_id: str
    status: str
    message: str
    created_at: str

class KeywordData(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=200)
    tenant_id: str = Field(default="demo", max_length=100)
    search_volume: Optional[int] = Field(None, ge=0, le=10000000)
    difficulty_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    intent: Optional[str] = Field(None, max_length=100)
    priority: str = Field(default="tier3", max_length=50)

class OpportunityResponse(BaseModel):
    opportunity_id: str
    opportunity_type: str
    keyword: str
    confidence_score: float
    estimated_traffic: int
    recommendation: str

@app.get("/")
async def root():
    return {
        "service": "ASO Engine",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "content": "/api/content",
            "keywords": "/api/keywords",
            "opportunities": "/api/opportunities",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with actual connectivity tests"""
    health_status = {
        "service": "aso-engine",
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "checks": {}
    }

    # Test BigQuery connectivity
    try:
        test_query = f"SELECT 1 as test LIMIT 1"
        query_job = bigquery_client.query(test_query)
        list(query_job.result())
        health_status["checks"]["bigquery"] = {"status": "healthy", "latency_ms": 0}
    except Exception as e:
        health_status["checks"]["bigquery"] = {"status": "unhealthy", "error": str(e)[:100]}
        health_status["status"] = "degraded"

    # Test Cloud Storage connectivity
    try:
        bucket = storage_client.bucket(f"{PROJECT_ID}-aso-content")
        bucket.exists()
        health_status["checks"]["storage"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["storage"] = {"status": "unhealthy", "error": str(e)[:100]}
        health_status["status"] = "degraded"

    # Test Firestore connectivity
    try:
        doc_ref = firestore_client.collection("_health_check").document("test")
        doc_ref.set({"timestamp": datetime.now().isoformat()}, merge=True)
        health_status["checks"]["firestore"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["firestore"] = {"status": "unhealthy", "error": str(e)[:100]}
        health_status["status"] = "degraded"

    # Resource usage
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        health_status["resources"] = {
            "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent(interval=0.1),
            "threads": process.num_threads()
        }
    except Exception as e:
        logger.warning(f"Failed to get resource metrics: {e}")

    # Performance metrics
    health_status["performance"] = performance_monitor.get_metrics()

    return health_status

@app.post("/api/content", response_model=ContentResponse, dependencies=[Depends(verify_api_key_header), Depends(rate_limit_expensive)])
async def create_content(content: ContentPiece):
    """Create new content piece and track in BigQuery"""
    with performance_monitor.track_operation("content_creation"):
        try:
            content_id = f"content_{uuid.uuid4().hex[:12]}"
            created_at = datetime.now()

            # Prepare BigQuery row
            table_id = f"{PROJECT_ID}.aso_tenant_{content.tenant_id}.content_pieces"

            rows_to_insert = [{
                "content_id": content_id,
                "content_type": content.content_type,
                "keyword_primary": content.keyword_primary,
                "keyword_secondary": content.keyword_secondary,
                "status": "draft",
                "hub_id": content.hub_id,
                "title": content.title,
                "meta_description": content.meta_description,
                "url": content.url,
                "word_count": content.word_count,
                "performance_score": None,
                "ranking_position": None,
                "monthly_traffic": 0,
                "monthly_conversions": 0,
                "conversion_rate": 0.0,
                "last_optimized": None,
                "created_at": created_at.isoformat(),
                "published_at": None,
                "updated_at": created_at.isoformat()
            }]

            errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)

            if errors:
                logger.error("bigquery_insert_failed", errors=errors, content_id=content_id)
                raise HTTPException(status_code=500, detail=f"Failed to insert content: {errors}")

            logger.info("content_created",
                       content_id=content_id,
                       tenant_id=content.tenant_id,
                       keyword=content.keyword_primary)

            return ContentResponse(
                content_id=content_id,
                status="draft",
                message="Content piece created successfully",
                created_at=created_at.isoformat()
            )

        except Exception as e:
            logger.error("content_creation_failed", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/content", dependencies=[Depends(verify_api_key_header)])
async def list_content(
    tenant_id: str = "demo",
    status: Optional[str] = None,
    days_back: int = Field(default=90, ge=1, le=730, description="Days to look back"),
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum number of items to return")
):
    """List content pieces for a tenant with partition pruning and caching"""
    try:
        # Check cache first
        cache_key = f"content_{tenant_id}_{status or 'all'}_{days_back}_{limit}"
        cached_content = await redis_cache.get("aso_content", cache_key)
        if cached_content:
            logger.info("content_cache_hit", tenant_id=tenant_id, status=status)
            return cached_content

        # Use partition pruning to reduce scanned data
        query = f"""
        SELECT
            content_id,
            content_type,
            keyword_primary,
            title,
            status,
            ranking_position,
            monthly_traffic,
            performance_score,
            created_at,
            published_at
        FROM `{PROJECT_ID}.aso_tenant_{tenant_id}.content_pieces`
        WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days_back DAY)
        """

        query_parameters = [
            bigquery.ScalarQueryParameter("days_back", "INT64", days_back)
        ]

        if status:
            query += " AND status = @status"
            query_parameters.append(bigquery.ScalarQueryParameter("status", "STRING", status))

        query += f" ORDER BY created_at DESC LIMIT @limit"
        query_parameters.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))

        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
        query_job = bigquery_client.query(query, job_config=job_config)
        results = list(query_job.result())

        content_list = []
        for row in results:
            content_list.append({
                "content_id": row.content_id,
                "content_type": row.content_type,
                "keyword_primary": row.keyword_primary,
                "title": row.title,
                "status": row.status,
                "ranking_position": row.ranking_position,
                "monthly_traffic": row.monthly_traffic,
                "performance_score": row.performance_score,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "published_at": row.published_at.isoformat() if row.published_at else None
            })

        content_result = {
            "tenant_id": tenant_id,
            "count": len(content_list),
            "content": content_list
        }

        # Cache for 2 minutes (content lists change more frequently than stats)
        await redis_cache.set("aso_content", cache_key, content_result, ttl=120)
        logger.info("content_cache_set", tenant_id=tenant_id, count=len(content_list))

        return content_result

    except Exception as e:
        logger.error("content_list_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/keywords", dependencies=[Depends(verify_api_key_header), Depends(rate_limit_standard)])
async def add_keyword(keyword_data: KeywordData):
    """Add keyword to tracking"""
    with performance_monitor.track_operation("keyword_tracking"):
        try:
            table_id = f"{PROJECT_ID}.aso_tenant_{keyword_data.tenant_id}.keywords"
            created_at = datetime.now()

            rows_to_insert = [{
                "keyword": keyword_data.keyword,
                "search_volume": keyword_data.search_volume,
                "difficulty_score": keyword_data.difficulty_score,
                "kgr_score": None,
                "intent": keyword_data.intent,
                "current_ranking": None,
                "best_ranking": None,
                "target_ranking": 10,
                "serp_history": None,
                "competitor_rankings": None,
                "last_checked": created_at.isoformat(),
                "priority": keyword_data.priority,
                "content_id": None,
                "created_at": created_at.isoformat()
            }]

            errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)

            if errors:
                logger.error("keyword_insert_failed", errors=errors)
                raise HTTPException(status_code=500, detail=f"Failed to insert keyword: {errors}")

            logger.info("keyword_added", keyword=keyword_data.keyword, tenant_id=keyword_data.tenant_id)

            return {
                "success": True,
                "keyword": keyword_data.keyword,
                "tenant_id": keyword_data.tenant_id,
                "priority": keyword_data.priority,
                "created_at": created_at.isoformat()
            }

        except Exception as e:
            logger.error("keyword_add_failed", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/keywords", dependencies=[Depends(verify_api_key_header)])
async def list_keywords(
    tenant_id: str = "demo",
    priority: Optional[str] = None,
    days_back: int = Field(default=365, ge=1, le=730, description="Days to look back"),
    limit: int = 100
):
    """List tracked keywords for a tenant with partition pruning and caching"""
    try:
        # Check cache first
        cache_key = f"keywords_{tenant_id}_{priority or 'all'}_{days_back}_{limit}"
        cached_keywords = await redis_cache.get("aso_keywords", cache_key)
        if cached_keywords:
            logger.info("keywords_cache_hit", tenant_id=tenant_id, priority=priority)
            return cached_keywords

        # Use partition pruning on last_checked date
        query = f"""
        SELECT
            keyword,
            search_volume,
            difficulty_score,
            kgr_score,
            intent,
            current_ranking,
            target_ranking,
            priority,
            content_id,
            last_checked
        FROM `{PROJECT_ID}.aso_tenant_{tenant_id}.keywords`
        WHERE DATE(last_checked) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days_back DAY)
        """

        query_parameters = [
            bigquery.ScalarQueryParameter("days_back", "INT64", days_back)
        ]

        if priority:
            query += " AND priority = @priority"
            query_parameters.append(bigquery.ScalarQueryParameter("priority", "STRING", priority))

        query += f" ORDER BY last_checked DESC LIMIT @limit"
        query_parameters.append(bigquery.ScalarQueryParameter("limit", "INT64", limit))

        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
        query_job = bigquery_client.query(query, job_config=job_config)
        results = list(query_job.result())

        keywords_list = []
        for row in results:
            keywords_list.append({
                "keyword": row.keyword,
                "search_volume": row.search_volume,
                "difficulty_score": row.difficulty_score,
                "kgr_score": row.kgr_score,
                "intent": row.intent,
                "current_ranking": row.current_ranking,
                "target_ranking": row.target_ranking,
                "priority": row.priority,
                "content_id": row.content_id,
                "last_checked": row.last_checked.isoformat() if row.last_checked else None
            })

        keywords_result = {
            "tenant_id": tenant_id,
            "count": len(keywords_list),
            "keywords": keywords_list
        }

        # Cache for 3 minutes (keyword data changes periodically)
        await redis_cache.set("aso_keywords", cache_key, keywords_result, ttl=180)
        logger.info("keywords_cache_set", tenant_id=tenant_id, count=len(keywords_list))

        return keywords_result

    except Exception as e:
        logger.error("keywords_list_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/opportunities/detect", dependencies=[Depends(verify_api_key_header)])
async def detect_opportunities(tenant_id: str = "demo"):
    """Detect optimization opportunities for a tenant"""
    try:
        # Query for low-hanging fruit keywords
        query = f"""
        SELECT
            k.keyword,
            k.search_volume,
            k.difficulty_score,
            k.current_ranking,
            k.target_ranking
        FROM `{PROJECT_ID}.aso_tenant_{tenant_id}.keywords` k
        WHERE k.current_ranking IS NOT NULL
          AND k.current_ranking > 10
          AND k.current_ranking <= 30
          AND k.difficulty_score < 50
          AND k.search_volume > 100
        ORDER BY k.search_volume DESC
        LIMIT 20
        """

        query_job = bigquery_client.query(query)
        results = list(query_job.result())

        opportunities = []
        for row in results:
            opportunity_id = f"opp_{uuid.uuid4().hex[:12]}"

            # Calculate confidence based on ranking and difficulty
            confidence = min(0.95, (40 - row.current_ranking) / 30 * (60 - row.difficulty_score) / 60)

            # Estimate traffic increase
            estimated_traffic = int(row.search_volume * 0.3 * (row.current_ranking / 10))

            opportunity = {
                "opportunity_id": opportunity_id,
                "opportunity_type": "low_hanging_fruit",
                "keyword": row.keyword,
                "confidence_score": round(confidence, 2),
                "estimated_traffic": estimated_traffic,
                "estimated_difficulty": row.difficulty_score,
                "current_ranking": row.current_ranking,
                "target_ranking": row.target_ranking,
                "recommendation": f"Optimize existing content for '{row.keyword}' - currently ranking #{row.current_ranking}, can reach top 10"
            }

            opportunities.append(opportunity)

            # Store opportunity in BigQuery
            opp_table = f"{PROJECT_ID}.aso_tenant_{tenant_id}.opportunities"
            opp_rows = [{
                "opportunity_id": opportunity_id,
                "opportunity_type": "low_hanging_fruit",
                "keyword": row.keyword,
                "confidence_score": confidence,
                "estimated_traffic": estimated_traffic,
                "estimated_difficulty": row.difficulty_score,
                "recommendation": opportunity["recommendation"],
                "detected_at": datetime.now().isoformat(),
                "status": "pending",
                "content_id": None,
                "created_at": datetime.now().isoformat()
            }]

            bigquery_client.insert_rows_json(opp_table, opp_rows)

        logger.info("opportunities_detected", count=len(opportunities), tenant_id=tenant_id)

        return {
            "tenant_id": tenant_id,
            "opportunities_detected": len(opportunities),
            "opportunities": opportunities
        }

    except Exception as e:
        logger.error("opportunity_detection_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities", dependencies=[Depends(verify_api_key_header)])
async def list_opportunities(
    tenant_id: str = "demo",
    status: str = "pending",
    days_back: int = Field(default=180, ge=1, le=730, description="Days to look back"),
    limit: int = 50
):
    """List optimization opportunities with partition pruning and caching"""
    try:
        # Check cache first
        cache_key = f"opps_{tenant_id}_{status}_{days_back}_{limit}"
        cached_opps = await redis_cache.get("aso_opportunities", cache_key)
        if cached_opps:
            logger.info("opportunities_cache_hit", tenant_id=tenant_id, status=status)
            return cached_opps

        # Use partition pruning on detected_at date
        query = f"""
        SELECT
            opportunity_id,
            opportunity_type,
            keyword,
            confidence_score,
            estimated_traffic,
            estimated_difficulty,
            recommendation,
            detected_at,
            status
        FROM `{PROJECT_ID}.aso_tenant_{tenant_id}.opportunities`
        WHERE DATE(detected_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days_back DAY)
          AND status = @status
        ORDER BY confidence_score DESC, estimated_traffic DESC
        LIMIT @limit
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("days_back", "INT64", days_back),
                bigquery.ScalarQueryParameter("status", "STRING", status),
                bigquery.ScalarQueryParameter("limit", "INT64", limit)
            ]
        )

        query_job = bigquery_client.query(query, job_config=job_config)
        results = list(query_job.result())

        opportunities = []
        for row in results:
            opportunities.append({
                "opportunity_id": row.opportunity_id,
                "opportunity_type": row.opportunity_type,
                "keyword": row.keyword,
                "confidence_score": row.confidence_score,
                "estimated_traffic": row.estimated_traffic,
                "estimated_difficulty": row.estimated_difficulty,
                "recommendation": row.recommendation,
                "detected_at": row.detected_at.isoformat() if row.detected_at else None,
                "status": row.status
            })

        opps_result = {
            "tenant_id": tenant_id,
            "count": len(opportunities),
            "opportunities": opportunities
        }

        # Cache for 4 minutes (opportunities change but not constantly)
        await redis_cache.set("aso_opportunities", cache_key, opps_result, ttl=240)
        logger.info("opportunities_cache_set", tenant_id=tenant_id, count=len(opportunities))

        return opps_result

    except Exception as e:
        logger.error("opportunities_list_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats", dependencies=[Depends(verify_api_key_header)])
async def get_tenant_stats(
    tenant_id: str = "demo",
    days_back: int = Field(default=90, ge=1, le=730, description="Days to calculate stats for")
):
    """Get tenant statistics with partition pruning and caching"""
    try:
        # Check cache first
        cache_key = f"stats_{tenant_id}_{days_back}"
        cached_stats = await redis_cache.get("aso_stats", cache_key)
        if cached_stats:
            logger.info("stats_cache_hit", tenant_id=tenant_id, days_back=days_back)
            return cached_stats

        # Content stats with partition pruning
        content_query = f"""
        SELECT
            status,
            COUNT(*) as count,
            AVG(performance_score) as avg_performance,
            SUM(monthly_traffic) as total_traffic
        FROM `{PROJECT_ID}.aso_tenant_{tenant_id}.content_pieces`
        WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days_back DAY)
        GROUP BY status
        """

        content_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("days_back", "INT64", days_back)]
        )
        content_job = bigquery_client.query(content_query, job_config=content_config)
        content_results = list(content_job.result())

        content_stats = {}
        for row in content_results:
            content_stats[row.status] = {
                "count": row.count,
                "avg_performance": round(row.avg_performance, 2) if row.avg_performance else 0,
                "total_traffic": row.total_traffic or 0
            }

        # Keywords stats with partition pruning
        keywords_query = f"""
        SELECT
            priority,
            COUNT(*) as count,
            AVG(current_ranking) as avg_ranking
        FROM `{PROJECT_ID}.aso_tenant_{tenant_id}.keywords`
        WHERE DATE(last_checked) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days_back DAY)
        GROUP BY priority
        """

        keywords_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("days_back", "INT64", days_back)]
        )
        keywords_job = bigquery_client.query(keywords_query, job_config=keywords_config)
        keywords_results = list(keywords_job.result())

        keywords_stats = {}
        for row in keywords_results:
            keywords_stats[row.priority] = {
                "count": row.count,
                "avg_ranking": round(row.avg_ranking, 1) if row.avg_ranking else None
            }

        stats_result = {
            "tenant_id": tenant_id,
            "content": content_stats,
            "keywords": keywords_stats,
            "generated_at": datetime.now().isoformat()
        }

        # Cache the results for 5 minutes (stats don't change frequently)
        await redis_cache.set("aso_stats", cache_key, stats_result, ttl=300)
        logger.info("stats_cache_set", tenant_id=tenant_id, days_back=days_back)

        return stats_result

    except Exception as e:
        logger.error("stats_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def cleanup_resources():
    """Clean up GCP client connections and Redis on shutdown."""
    try:
        from gcp_clients import gcp_clients
        await gcp_clients.cleanup()
        await redis_cache.close()
        logger.info("ASO Engine shutdown complete")
    except Exception as e:
        logger.error("cleanup_error", error=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
