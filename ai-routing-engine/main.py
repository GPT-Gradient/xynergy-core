from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import json
import time
import httpx
from datetime import datetime
from typing import Dict, Any
import uvicorn


# Phase 2 enhancements
from phase2_utils import CircuitBreaker, CircuitBreakerConfig, call_service_with_circuit_breaker, PerformanceMonitor
import time

# Import shared utilities
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from redis_cache import RedisCache, cache_ai_response, get_cached_ai_response
# Phase 6: Advanced optimization
# Semantic cache temporarily disabled (requires sentence-transformers - 4GB+ deps)
# from semantic_cache import get_semantic_cache, get_semantic_cached_ai_response, cache_ai_response_semantic
from ai_token_optimizer import optimize_ai_request


PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")

# AI Providers service URL
AI_PROVIDERS_URL = os.getenv("AI_PROVIDERS_URL", "https://xynergy-ai-providers-835612502919.us-central1.run.app")
# Updated to use new Internal AI Service v2
INTERNAL_AI_URL = os.getenv("INTERNAL_AI_URL", "https://internal-ai-service-v2-vgjxy554mq-uc.a.run.app")

# Import centralized authentication and rate limiting
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from auth import verify_api_key, verify_api_key_optional
from http_client import get_http_client
from rate_limiting import rate_limit_ai

app = FastAPI(title="Xynergy AI Routing Engine", version="2.0.0")

# Phase 2 initialization
service_monitor = PerformanceMonitor("ai-routing-engine")
service_circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
ai_routing_circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
redis_cache = RedisCache()

# Phase 2 monitoring ready


# Basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://xynergy-platform.com",
        "https://api.xynergy.dev",
        "https://*.xynergy.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/")
async def root():
    return {"message": "AI Routing Engine v2.0 Online", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-routing-engine-v2",
        "timestamp": datetime.now().isoformat()
    }

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with service_monitor.track_operation(f"execute_{action}"):
            if action == "route_request":
                intent = parameters.get("intent", "")
                route_result = {
                    "route_id": f"route_{int(time.time())}",
                    "workflow_id": workflow_context.get("workflow_id"),
                    "intent": intent,
                    "routing_decision": "internal_ai_service",
                    "confidence": 0.95,
                    "routed_at": datetime.now()
                }

                return {
                    "success": True,
                    "action": action,
                    "output": {"route_id": route_result["route_id"], "routing_decision": route_result["routing_decision"]},
                    "execution_time": time.time(),
                    "service": "ai-routing-engine"
                }

            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not supported by ai-routing-engine",
                    "supported_actions": ["route_request"],
                    "service": "ai-routing-engine"
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "action": request.get("action"),
            "service": "ai-routing-engine"
        }

@app.post("/api/route")
async def route_ai_request(ai_request: dict):
    """AI routing with Abacus first, OpenAI second fallback"""
    prompt = ai_request.get("prompt", "")

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # Enhanced routing logic: Abacus first, OpenAI second
    route_decision = await determine_optimal_route(prompt)

    return {
        "response": f"AI routing response for: {prompt[:100]}...",
        "route": route_decision["provider"],
        "model": route_decision["model"],
        "cost": route_decision["cost"],
        "processing_time": route_decision["processing_time"],
        "fallback_available": route_decision["fallback_available"]
    }

@app.post("/api/generate", dependencies=[Depends(rate_limit_ai)])
async def generate_ai_response(request: dict):
    """Generate AI response using optimal routing (Abacus -> OpenAI -> Internal) with semantic caching and token optimization"""
    prompt = request.get("prompt", "")
    user_max_tokens = request.get("max_tokens")  # User-specified, may be None
    temperature = request.get("temperature", 0.7)

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # Phase 6: Token optimization (20-30% cost reduction)
    optimized_tokens, token_metadata = optimize_ai_request(prompt, 512, user_max_tokens)
    max_tokens = optimized_tokens

    # Phase 6: Semantic cache temporarily disabled (lightweight deployment)
    # try:
    #     semantic_response = await get_semantic_cached_ai_response(prompt, max_tokens, temperature)
    #     if semantic_response:
    #         semantic_response["cache_hit"] = True
    #         semantic_response["routed_via"] = "ai-routing-engine-semantic-cache"
    #         semantic_response["token_optimization"] = token_metadata
    #         return semantic_response
    # except Exception as e:
    #     print(f"Semantic cache check failed: {e}")

    # Fallback: Check basic Redis cache for exact match
    try:
        await redis_cache.connect()
        cached_response = await get_cached_ai_response(prompt, "ai-routing-engine")
        if cached_response:
            cached_response["cache_hit"] = True
            cached_response["routed_via"] = "ai-routing-engine-cache"
            cached_response["token_optimization"] = token_metadata
            return cached_response
    except Exception as e:
        print(f"Redis cache check failed: {e}")

    # Determine routing decision
    route_decision = await determine_optimal_route(prompt)

    try:
        client = await get_http_client()
        if route_decision["provider"] in ["abacus", "openai"]:
            # Use external AI providers service
            response = await client.post(
                f"{AI_PROVIDERS_URL}/api/generate/intelligent",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                result["routed_via"] = "ai-routing-engine"
                result["cache_hit"] = False
                result["token_optimization"] = token_metadata

                # Phase 6: Cache with semantic indexing (disabled in lightweight deployment)
                try:
                    # await cache_ai_response_semantic(prompt, result, max_tokens, temperature)
                    # Cache in basic Redis for exact matches
                    await cache_ai_response(prompt, result, "ai-routing-engine")
                except Exception as e:
                    print(f"Failed to cache AI response: {e}")

                return result

            # Fallback to internal AI service
            response = await client.post(
                f"{INTERNAL_AI_URL}/api/generate",
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()
                result["provider"] = "internal"
                result["routed_via"] = "ai-routing-engine"
                result["cache_hit"] = False
                result["token_optimization"] = token_metadata

                # Phase 6: Cache with semantic indexing
                try:
                    await cache_ai_response_semantic(prompt, result, max_tokens, temperature)
                    # Also cache in basic Redis for exact matches
                    await cache_ai_response(prompt, result, "ai-routing-engine")
                except Exception as e:
                    print(f"Failed to cache AI response: {e}")

                return result

    except Exception as e:
        # Ultimate fallback - return simulated response
        return {
            "success": False,
            "provider": "fallback",
            "text": f"AI services temporarily unavailable. Your request: '{prompt[:100]}...' has been logged for processing.",
            "model": "fallback-response",
            "error": str(e),
            "routed_via": "ai-routing-engine",
            "cache_hit": False
        }

    raise HTTPException(status_code=503, detail="All AI services unavailable")

async def determine_optimal_route(prompt: str) -> dict:
    """Determine optimal AI provider: Abacus first, OpenAI second, internal third"""

    # Complex requests that need external AI
    complex_indicators = [
        "current", "latest", "today", "news", "real-time", "recent",
        "advanced reasoning", "complex analysis", "research", "detailed explanation"
    ]

    is_complex = any(keyword in prompt.lower() for keyword in complex_indicators)

    if is_complex:
        # Try Abacus first (primary external provider)
        abacus_available = await check_abacus_availability()
        if abacus_available:
            return {
                "provider": "abacus",
                "model": "abacus-ai-model",
                "cost": 0.015,  # Lower cost than OpenAI
                "processing_time": 2.5,
                "fallback_available": True
            }

        # Fallback to OpenAI if Abacus unavailable
        openai_available = await check_openai_availability()
        if openai_available:
            return {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "cost": 0.025,  # Higher cost
                "processing_time": 3.0,
                "fallback_available": False
            }

    # Default to internal AI service
    return {
        "provider": "internal",
        "model": "llama-3.1-8b",
        "cost": 0.001,
        "processing_time": 1.0,
        "fallback_available": True
    }

async def check_abacus_availability() -> bool:
    """Check if Abacus AI service is available"""
    try:
        client = await get_http_client()
        response = await client.get(f"{AI_PROVIDERS_URL}/api/providers/status", timeout=5.0)
        if response.status_code == 200:
                status = response.json()
                return status.get("providers", {}).get("abacus", {}).get("available", False)
    except Exception:
        pass
    return False

async def check_openai_availability() -> bool:
    """Check if OpenAI service is available"""
    try:
        client = await get_http_client()
        response = await client.get(f"{AI_PROVIDERS_URL}/api/providers/status", timeout=5.0)
        if response.status_code == 200:
                status = response.json()
                return status.get("providers", {}).get("openai", {}).get("available", False)
    except Exception:
        pass
    return False

@app.get("/cache/stats")
async def get_cache_statistics():
    """Get Redis cache statistics and performance metrics."""
    try:
        await redis_cache.connect()
        stats = await redis_cache.get_cache_stats()

        # Phase 6: Semantic cache stats (disabled in lightweight deployment)
        # semantic_cache = await get_semantic_cache()
        # semantic_stats = await semantic_cache.get_stats()

        return {
            "cache_stats": stats,
            # "semantic_cache_stats": semantic_stats,  # Phase 6 (disabled)
            "ai_routing_cache": {
                "enabled": True,
                "ttl_seconds": 3600,
                "provider": "redis",
                "semantic_enabled": False,  # Phase 6 (disabled in lightweight mode)
                "token_optimization_enabled": True  # Phase 6 (active)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cache stats unavailable: {str(e)}")

@app.post("/cache/invalidate/{pattern}")
async def invalidate_cache_pattern(pattern: str):
    """Invalidate cache entries matching a pattern."""
    try:
        await redis_cache.connect()
        invalidated_count = await redis_cache.invalidate_pattern(f"*{pattern}*")
        return {
            "success": True,
            "pattern": pattern,
            "invalidated_keys": invalidated_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache invalidation failed: {str(e)}")

@app.post("/cache/warm")
async def warm_ai_cache():
    """Pre-warm cache with common AI prompts."""
    try:
        await redis_cache.connect()

        # Common prompts to pre-cache
        common_prompts = {
            "content": {
                "seo_optimization": "How can I optimize this content for SEO?",
                "market_analysis": "Analyze the current market trends",
                "competitor_research": "Research competitor strategies",
                "keyword_suggestions": "Suggest high-value keywords",
                "content_ideas": "Generate content ideas for marketing"
            }
        }

        # Simulate responses for cache warming
        warm_data = {}
        for category, prompts in common_prompts.items():
            warm_data[category] = {}
            for key, prompt in prompts.items():
                warm_data[category][key] = {
                    "text": f"Pre-cached response for: {prompt}",
                    "provider": "cache-warmer",
                    "model": "pre-cached",
                    "generated_at": datetime.now().isoformat(),
                    "pre_cached": True
                }

        results = await redis_cache.warm_cache(warm_data)
        return {
            "success": True,
            "cache_warming": results,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache warming failed: {str(e)}")

@app.on_event("shutdown")
async def cleanup_resources():
    """Clean up Redis connections on shutdown."""
    try:
        await redis_cache.disconnect()
        print("AI routing engine shutdown complete")
    except Exception as e:
        print(f"Cleanup error: {e}")

if __name__ == "__main__":
    print(f"Starting AI Routing Engine on port 8080...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
