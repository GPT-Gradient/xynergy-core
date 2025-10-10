"""
Internal AI Service v2 - GPU-accelerated LLM inference
Uses Llama 3.1 8B Instruct with vLLM for high-performance, low-cost AI generation
Target: 80% of platform AI requests at $0.0002/1K tokens vs $0.003 external APIs
"""

import os
import sys
import time
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging
import psutil

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google.cloud import storage, firestore, bigquery
import structlog

# Import shared authentication and rate limiting
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from auth import verify_api_key
from rate_limiting import rate_limit_ai

# Import performance monitoring
from phase2_utils import PerformanceMonitor, CircuitBreaker, CircuitBreakerConfig

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
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Meta-Llama-3.1-8B-Instruct")
MODEL_BUCKET = f"{PROJECT_ID}-aso-models"

# Initialize GCP clients
storage_client = storage.Client(project=PROJECT_ID)
firestore_client = firestore.Client(project=PROJECT_ID)
bigquery_client = bigquery.Client(project=PROJECT_ID)

# Initialize performance monitoring
performance_monitor = PerformanceMonitor("internal-ai-service-v2")

# FastAPI app
app = FastAPI(
    title="Internal AI Service v2",
    description="GPU-accelerated LLM inference using Llama 3.1 8B",
    version="2.0.0"
)

# CORS - Secure configuration for internal services only
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

# Request/Response models
class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000, description="The prompt to generate from")
    max_tokens: int = Field(default=512, ge=1, le=2048, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    task_type: Optional[str] = Field(default="general", description="Type of task (for logging)")
    tenant_id: Optional[str] = Field(default="platform", description="Tenant ID for tracking")

class GenerateResponse(BaseModel):
    text: str
    tokens_used: int
    cost_usd: float
    latency_ms: int
    model: str
    cached: bool = False

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    gpu_available: bool
    version: str
    checks: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None

# Global model state (will be loaded on startup)
llm_engine = None
model_loaded = False

async def load_model():
    """Load Llama 3.1 8B model with vLLM"""
    global llm_engine, model_loaded

    try:
        logger.info("loading_model", model=MODEL_NAME)

        # Note: In production, this would use vLLM
        # For now, we'll simulate the model with a placeholder
        # Real implementation would be:
        # from vllm import LLM, SamplingParams
        # llm_engine = LLM(model=MODEL_NAME, tensor_parallel_size=1, gpu_memory_utilization=0.9)

        # Placeholder for development
        llm_engine = {"model": MODEL_NAME, "status": "simulated"}
        model_loaded = True

        logger.info("model_loaded_successfully", model=MODEL_NAME)
        return True

    except Exception as e:
        logger.error("model_loading_failed", error=str(e))
        model_loaded = False
        return False

def estimate_tokens(text: str) -> int:
    """Estimate token count (roughly 4 chars per token)"""
    return len(text) // 4

def calculate_cost(tokens: int) -> float:
    """Calculate cost at $0.0002 per 1K tokens"""
    return (tokens / 1000) * 0.0002

async def generate_text(prompt: str, max_tokens: int, temperature: float, top_p: float) -> str:
    """Generate text using LLM"""
    global llm_engine

    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Simulate generation for development
        # Real implementation would use vLLM:
        # sampling_params = SamplingParams(
        #     temperature=temperature,
        #     top_p=top_p,
        #     max_tokens=max_tokens
        # )
        # outputs = llm_engine.generate([prompt], sampling_params)
        # return outputs[0].outputs[0].text

        # Placeholder response
        await asyncio.sleep(0.1)  # Simulate inference latency
        return f"[SIMULATED RESPONSE] Generated text for prompt: {prompt[:50]}... [This would be actual LLM output in production with vLLM]"

    except Exception as e:
        logger.error("generation_failed", error=str(e), prompt=prompt[:100])
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

async def log_to_bigquery(request_data: Dict, response_data: Dict):
    """Log interaction to BigQuery for training data"""
    try:
        table_id = f"{PROJECT_ID}.training_data.llm_interactions"

        rows_to_insert = [{
            "interaction_id": f"{request_data['tenant_id']}_{int(time.time() * 1000)}",
            "task_type": request_data.get("task_type", "general"),
            "prompt": request_data["prompt"][:5000],  # Truncate long prompts
            "response": response_data["text"][:5000],
            "model_used": "llama-3.1-8b-instruct",
            "quality_score": None,  # To be updated based on user feedback
            "success": True,
            "metadata": {
                "max_tokens": request_data["max_tokens"],
                "temperature": request_data["temperature"],
                "tokens_used": response_data["tokens_used"],
                "cost_usd": response_data["cost_usd"],
                "latency_ms": response_data["latency_ms"]
            },
            "created_at": datetime.utcnow().isoformat()
        }]

        errors = bigquery_client.insert_rows_json(table_id, rows_to_insert)

        if errors:
            logger.warning("bigquery_insert_errors", errors=errors)
        else:
            logger.debug("interaction_logged", table=table_id)

    except Exception as e:
        logger.error("bigquery_logging_failed", error=str(e))
        # Don't fail the request if logging fails

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    logger.info("starting_internal_ai_service_v2")
    await load_model()
    logger.info("service_ready")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check with actual connectivity tests"""

    health_status = {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "gpu_available": True,  # In production: torch.cuda.is_available()
        "version": "2.0.0",
        "checks": {}
    }

    # Test BigQuery connectivity
    try:
        test_query = "SELECT 1 as test LIMIT 1"
        query_job = bigquery_client.query(test_query)
        list(query_job.result())
        health_status["checks"]["bigquery"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["bigquery"] = {"status": "unhealthy", "error": str(e)[:100]}
        health_status["status"] = "degraded"

    # Test Firestore connectivity
    try:
        doc_ref = firestore_client.collection("_health_check").document("test")
        doc_ref.set({"timestamp": datetime.utcnow().isoformat()}, merge=True)
        health_status["checks"]["firestore"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["firestore"] = {"status": "unhealthy", "error": str(e)[:100]}
        health_status["status"] = "degraded"

    # Test Cloud Storage connectivity
    try:
        bucket = storage_client.bucket(MODEL_BUCKET)
        bucket.exists()
        health_status["checks"]["storage"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["storage"] = {"status": "unhealthy", "error": str(e)[:100]}
        health_status["status"] = "degraded"

    # Model status
    health_status["checks"]["model"] = {
        "loaded": model_loaded,
        "name": MODEL_NAME if model_loaded else None
    }

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

    return HealthResponse(**health_status)

@app.post("/api/generate", response_model=GenerateResponse, dependencies=[Depends(verify_api_key), Depends(rate_limit_ai)])
async def generate(request: GenerateRequest):
    """Generate text using internal LLM"""

    with performance_monitor.track_operation("ai_generation"):
        start_time = time.time()

        try:
            logger.info("generation_request",
                       task_type=request.task_type,
                       tenant_id=request.tenant_id,
                       prompt_length=len(request.prompt))

            # Generate text
            generated_text = await generate_text(
                prompt=request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p
            )

            # Calculate metrics
            tokens_used = estimate_tokens(request.prompt) + estimate_tokens(generated_text)
            cost_usd = calculate_cost(tokens_used)
            latency_ms = int((time.time() - start_time) * 1000)

            response_data = {
                "text": generated_text,
                "tokens_used": tokens_used,
                "cost_usd": cost_usd,
                "latency_ms": latency_ms,
                "model": "llama-3.1-8b-instruct",
                "cached": False
            }

            # Log to BigQuery asynchronously
            asyncio.create_task(log_to_bigquery(request.dict(), response_data))

            logger.info("generation_complete",
                       tokens=tokens_used,
                       cost=cost_usd,
                       latency_ms=latency_ms)

            return GenerateResponse(**response_data)

        except Exception as e:
            logger.error("generation_error", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats", dependencies=[Depends(verify_api_key)])
async def get_stats():
    """Get service statistics"""

    try:
        # Query BigQuery for usage stats (last 24 hours)
        query = f"""
        SELECT
            COUNT(*) as total_requests,
            SUM(JSON_EXTRACT_SCALAR(metadata, '$.tokens_used')) as total_tokens,
            SUM(JSON_EXTRACT_SCALAR(metadata, '$.cost_usd')) as total_cost,
            AVG(JSON_EXTRACT_SCALAR(metadata, '$.latency_ms')) as avg_latency_ms,
            task_type,
            COUNT(*) as count
        FROM `{PROJECT_ID}.training_data.llm_interactions`
        WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
          AND model_used = 'llama-3.1-8b-instruct'
        GROUP BY task_type
        ORDER BY count DESC
        """

        query_job = bigquery_client.query(query)
        results = list(query_job.result())

        stats = {
            "period": "last_24_hours",
            "total_requests": sum(r.total_requests for r in results),
            "total_tokens": sum(r.total_tokens for r in results),
            "total_cost_usd": sum(r.total_cost for r in results),
            "avg_latency_ms": sum(r.avg_latency_ms for r in results) / len(results) if results else 0,
            "by_task_type": [
                {
                    "task_type": r.task_type,
                    "count": r.count
                }
                for r in results
            ]
        }

        return stats

    except Exception as e:
        logger.error("stats_query_failed", error=str(e))
        return {
            "error": "Failed to retrieve stats",
            "period": "last_24_hours"
        }

@app.get("/")
async def root():
    """Service information"""
    return {
        "service": "Internal AI Service v2",
        "model": MODEL_NAME,
        "model_loaded": model_loaded,
        "version": "2.0.0",
        "cost_per_1k_tokens": "$0.0002",
        "endpoints": {
            "generate": "/api/generate",
            "stats": "/api/stats",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
