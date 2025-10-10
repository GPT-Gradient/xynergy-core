"""
Fact Checking Layer - Two-Tier Verification System
1. Check internal verified_facts database (free)
2. Fallback to Perplexity API ($0.004/request) for new facts
Accumulates verified facts for reuse across all tenants
"""

import os
import hashlib
import time
from datetime import datetime, date
from typing import Dict, List, Optional
import httpx

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google.cloud import bigquery
import structlog

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
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")  # Set via env var

# Initialize GCP clients
bigquery_client = bigquery.Client(project=PROJECT_ID)

app = FastAPI(
    title="Fact Checking Layer",
    description="Two-tier fact verification: internal DB → Perplexity API",
    version="1.0.0"
)

# Secure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"https://*.{PROJECT_ID}.run.app",
        "https://*.xynergy.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Request/Response Models
class FactCheckRequest(BaseModel):
    statement: str = Field(..., min_length=1, max_length=2000)
    topic: Optional[str] = Field(default=None, description="Topic category for the fact")
    tenant_id: str = Field(default="platform", description="Tenant requesting verification")

class FactCheckResponse(BaseModel):
    fact_verified: bool
    fact_text: str
    source: str  # "internal_db" or "perplexity_api"
    confidence_score: float
    source_url: Optional[str] = None
    cost_usd: float
    cached: bool
    fact_id: Optional[str] = None

class FactStats(BaseModel):
    total_facts: int
    total_verifications: int
    cache_hit_rate: float
    cost_savings_usd: float
    most_reused_facts: List[Dict]

def generate_fact_id(statement: str) -> str:
    """Generate unique fact ID from statement"""
    return f"fact_{hashlib.sha256(statement.encode()).hexdigest()[:12]}"

async def check_internal_facts(statement: str, topic: Optional[str] = None) -> Optional[Dict]:
    """Check if fact exists in internal verified_facts database"""
    try:
        # Query for exact or similar facts
        query = f"""
        SELECT
            fact_id,
            fact_text,
            topic,
            source_url,
            confidence_score,
            used_count,
            cost_savings,
            verified_date
        FROM `{PROJECT_ID}.platform_intelligence.verified_facts`
        WHERE LOWER(fact_text) LIKE LOWER(@statement)
        """

        if topic:
            query += " AND topic = @topic"

        query += " ORDER BY verified_date DESC, used_count DESC LIMIT 1"

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("statement", "STRING", f"%{statement}%"),
            ]
        )

        if topic:
            job_config.query_parameters.append(
                bigquery.ScalarQueryParameter("topic", "STRING", topic)
            )

        query_job = bigquery_client.query(query, job_config=job_config)
        results = list(query_job.result())

        if results:
            row = results[0]
            return {
                "fact_id": row.fact_id,
                "fact_text": row.fact_text,
                "source_url": row.source_url,
                "confidence_score": row.confidence_score,
                "used_count": row.used_count,
                "cost_savings": row.cost_savings
            }

        return None

    except Exception as e:
        logger.error("internal_fact_check_failed", error=str(e))
        return None

async def verify_with_perplexity(statement: str, topic: Optional[str] = None) -> Dict:
    """Verify fact using Perplexity API (fallback)"""
    try:
        # Perplexity API endpoint
        url = "https://api.perplexity.ai/chat/completions"

        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"Verify this statement and provide a factual response: {statement}"
        if topic:
            prompt += f" (Topic: {topic})"

        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a fact-checking assistant. Verify statements and provide accurate, concise answers with sources."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                result = response.json()
                fact_text = result["choices"][0]["message"]["content"]

                # Extract citations if available
                citations = result.get("citations", [])
                source_url = citations[0] if citations else None

                return {
                    "verified": True,
                    "fact_text": fact_text,
                    "source_url": source_url,
                    "confidence_score": 0.85,  # Perplexity generally high confidence
                    "cost_usd": 0.004  # Estimated cost per request
                }
            else:
                logger.error("perplexity_api_failed",
                           status_code=response.status_code,
                           error=response.text)
                return {
                    "verified": False,
                    "fact_text": "Unable to verify fact at this time",
                    "source_url": None,
                    "confidence_score": 0.0,
                    "cost_usd": 0.004
                }

    except Exception as e:
        logger.error("perplexity_verification_failed", error=str(e))
        return {
            "verified": False,
            "fact_text": "Verification service temporarily unavailable",
            "source_url": None,
            "confidence_score": 0.0,
            "cost_usd": 0.0
        }

async def store_verified_fact(fact_id: str, statement: str, fact_text: str,
                              topic: Optional[str], source_url: Optional[str],
                              confidence_score: float, tenant_id: str, cost_usd: float):
    """Store newly verified fact in database for reuse"""
    try:
        table_id = f"{PROJECT_ID}.platform_intelligence.verified_facts"

        rows_to_insert = [{
            "fact_id": fact_id,
            "fact_text": fact_text,
            "topic": topic,
            "source_url": source_url,
            "verified_date": date.today().isoformat(),
            "verification_method": "perplexity",
            "confidence_score": confidence_score,
            "used_count": 1,
            "cost_savings": 0.0,  # First use, no savings yet
            "tenant_id": tenant_id,
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "metadata": {
                "original_statement": statement,
                "verification_cost": cost_usd
            }
        }]

        errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)

        if errors:
            logger.error("fact_storage_failed", errors=errors, fact_id=fact_id)
        else:
            logger.info("fact_stored", fact_id=fact_id, topic=topic)

    except Exception as e:
        logger.error("fact_storage_exception", error=str(e))

async def increment_fact_usage(fact_id: str):
    """Increment usage count and calculate savings for cached fact"""
    try:
        # Update used_count and cost_savings
        query = f"""
        UPDATE `{PROJECT_ID}.platform_intelligence.verified_facts`
        SET
            used_count = used_count + 1,
            cost_savings = cost_savings + 0.004,  -- Perplexity API cost per request
            last_used = CURRENT_TIMESTAMP()
        WHERE fact_id = @fact_id
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("fact_id", "STRING", fact_id)
            ]
        )

        bigquery_client.query(query, job_config=job_config)
        logger.info("fact_usage_incremented", fact_id=fact_id)

    except Exception as e:
        logger.error("fact_usage_increment_failed", error=str(e), fact_id=fact_id)

@app.get("/")
async def root():
    return {
        "service": "Fact Checking Layer",
        "version": "1.0.0",
        "status": "healthy",
        "tiers": {
            "tier1": "Internal verified_facts database (free)",
            "tier2": "Perplexity API ($0.004/request)"
        },
        "endpoints": {
            "check": "/api/fact/check",
            "stats": "/api/facts/stats",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "fact-checking-layer",
        "timestamp": datetime.now().isoformat(),
        "perplexity_configured": bool(PERPLEXITY_API_KEY)
    }

@app.post("/api/fact/check", response_model=FactCheckResponse)
async def check_fact(request: FactCheckRequest):
    """
    Two-tier fact checking:
    1. Check internal database (free, instant)
    2. Fallback to Perplexity API ($0.004, 2-3s)
    """
    start_time = time.time()

    try:
        logger.info("fact_check_requested",
                   statement=request.statement[:100],
                   topic=request.topic,
                   tenant_id=request.tenant_id)

        # Tier 1: Check internal database
        internal_fact = await check_internal_facts(request.statement, request.topic)

        if internal_fact:
            # Cache hit - increment usage and savings
            await increment_fact_usage(internal_fact["fact_id"])

            latency_ms = int((time.time() - start_time) * 1000)

            logger.info("fact_check_cache_hit",
                       fact_id=internal_fact["fact_id"],
                       used_count=internal_fact["used_count"] + 1,
                       latency_ms=latency_ms)

            return FactCheckResponse(
                fact_verified=True,
                fact_text=internal_fact["fact_text"],
                source="internal_db",
                confidence_score=internal_fact["confidence_score"],
                source_url=internal_fact["source_url"],
                cost_usd=0.0,  # Free from cache!
                cached=True,
                fact_id=internal_fact["fact_id"]
            )

        # Tier 2: Verify with Perplexity API
        logger.info("fact_check_cache_miss", using_perplexity=True)

        perplexity_result = await verify_with_perplexity(request.statement, request.topic)

        # Generate fact ID and store for future reuse
        fact_id = generate_fact_id(request.statement)

        if perplexity_result["verified"]:
            await store_verified_fact(
                fact_id=fact_id,
                statement=request.statement,
                fact_text=perplexity_result["fact_text"],
                topic=request.topic,
                source_url=perplexity_result["source_url"],
                confidence_score=perplexity_result["confidence_score"],
                tenant_id=request.tenant_id,
                cost_usd=perplexity_result["cost_usd"]
            )

        latency_ms = int((time.time() - start_time) * 1000)

        logger.info("fact_check_complete",
                   fact_id=fact_id,
                   source="perplexity",
                   cost_usd=perplexity_result["cost_usd"],
                   latency_ms=latency_ms)

        return FactCheckResponse(
            fact_verified=perplexity_result["verified"],
            fact_text=perplexity_result["fact_text"],
            source="perplexity_api",
            confidence_score=perplexity_result["confidence_score"],
            source_url=perplexity_result["source_url"],
            cost_usd=perplexity_result["cost_usd"],
            cached=False,
            fact_id=fact_id
        )

    except Exception as e:
        logger.error("fact_check_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/facts/stats", response_model=FactStats)
async def get_fact_stats():
    """Get fact checking statistics and ROI"""
    try:
        # Query for statistics
        query = f"""
        SELECT
            COUNT(*) as total_facts,
            SUM(used_count) as total_verifications,
            SUM(cost_savings) as total_savings,
            AVG(used_count) as avg_reuse_rate
        FROM `{PROJECT_ID}.platform_intelligence.verified_facts`
        """

        query_job = bigquery_client.query(query)
        results = list(query_job.result())

        if results:
            row = results[0]
            total_facts = row.total_facts or 0
            total_verifications = row.total_verifications or 0
            total_savings = row.total_savings or 0.0

            # Calculate cache hit rate
            if total_verifications > 0:
                cache_hit_rate = ((total_verifications - total_facts) / total_verifications) * 100
            else:
                cache_hit_rate = 0.0

        else:
            total_facts = 0
            total_verifications = 0
            total_savings = 0.0
            cache_hit_rate = 0.0

        # Get most reused facts
        top_facts_query = f"""
        SELECT
            fact_text,
            topic,
            used_count,
            cost_savings
        FROM `{PROJECT_ID}.platform_intelligence.verified_facts`
        ORDER BY used_count DESC
        LIMIT 10
        """

        top_facts_job = bigquery_client.query(top_facts_query)
        top_facts = []

        for fact in top_facts_job.result():
            top_facts.append({
                "fact_text": fact.fact_text[:100] + "..." if len(fact.fact_text) > 100 else fact.fact_text,
                "topic": fact.topic,
                "used_count": fact.used_count,
                "cost_savings": fact.cost_savings
            })

        return FactStats(
            total_facts=total_facts,
            total_verifications=total_verifications,
            cache_hit_rate=round(cache_hit_rate, 2),
            cost_savings_usd=round(total_savings, 2),
            most_reused_facts=top_facts
        )

    except Exception as e:
        logger.error("stats_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
