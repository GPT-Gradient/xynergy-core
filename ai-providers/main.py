from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import json
import time
import asyncio
import httpx

# Import shared HTTP client
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from http_client import get_http_client
from datetime import datetime
from typing import Dict, Any, Optional
import uvicorn
import logging

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")

# API Keys - Environment variables
ABACUS_API_KEY = os.getenv("ABACUS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# API Endpoints
ABACUS_BASE_URL = "https://api.abacus.ai/v1"  # Replace with actual Abacus endpoint
OPENAI_BASE_URL = "https://api.openai.com/v1"

app = FastAPI(title="Xynergy AI Providers", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://xynergy.com",
        "https://*.xynergy.com",
        "http://localhost:*"  # Development pattern
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "ai-providers"}'
)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    return {
        "service": "ai-providers",
        "providers": ["abacus", "openai"],
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-providers",
        "timestamp": datetime.now().isoformat(),
        "providers_configured": {
            "abacus": bool(ABACUS_API_KEY),
            "openai": bool(OPENAI_API_KEY)
        }
    }

@app.post("/api/generate/abacus")
async def generate_with_abacus(request: Dict[str, Any]):
    """Generate response using Abacus AI"""
    if not ABACUS_API_KEY:
        raise HTTPException(status_code=503, detail="Abacus API key not configured")

    try:
        prompt = request.get("prompt", "")
        max_tokens = request.get("max_tokens", 512)
        temperature = request.get("temperature", 0.7)

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {ABACUS_API_KEY}",
            "Content-Type": "application/json"
        }

        # Abacus API request structure (adjust based on actual Abacus API)
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "model": "abacus-default"  # Replace with actual Abacus model name
        }

        client = await get_http_client()
            try:
                response = await client.post(
                    f"{ABACUS_BASE_URL}/completions",  # Adjust endpoint
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    processing_time = time.time() - start_time

                    return {
                        "success": True,
                        "provider": "abacus",
                        "text": result.get("text", result.get("choices", [{}])[0].get("text", "")),
                        "model": "abacus-ai-model",
                        "tokens_generated": result.get("usage", {}).get("completion_tokens", max_tokens),
                        "processing_time": processing_time,
                        "cost": 0.015
                    }
                else:
                    raise HTTPException(status_code=response.status_code, detail=f"Abacus API error: {response.text}")

            except httpx.TimeoutException:
                raise HTTPException(status_code=408, detail="Abacus API timeout")
            except httpx.RequestError as e:
                raise HTTPException(status_code=502, detail=f"Abacus API connection error: {str(e)}")

    except Exception as e:
        logger.error(f"Abacus generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Abacus generation failed: {str(e)}")

@app.post("/api/generate/openai")
async def generate_with_openai(request: Dict[str, Any]):
    """Generate response using OpenAI"""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")

    try:
        prompt = request.get("prompt", "")
        max_tokens = request.get("max_tokens", 512)
        temperature = request.get("temperature", 0.7)
        model = request.get("model", "gpt-4o-mini")

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        # OpenAI API request structure
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        client = await get_http_client()
            try:
                response = await client.post(
                    f"{OPENAI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    processing_time = time.time() - start_time

                    return {
                        "success": True,
                        "provider": "openai",
                        "text": result["choices"][0]["message"]["content"],
                        "model": model,
                        "tokens_generated": result["usage"]["completion_tokens"],
                        "processing_time": processing_time,
                        "cost": 0.025
                    }
                else:
                    raise HTTPException(status_code=response.status_code, detail=f"OpenAI API error: {response.text}")

            except httpx.TimeoutException:
                raise HTTPException(status_code=408, detail="OpenAI API timeout")
            except httpx.RequestError as e:
                raise HTTPException(status_code=502, detail=f"OpenAI API connection error: {str(e)}")

    except Exception as e:
        logger.error(f"OpenAI generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI generation failed: {str(e)}")

@app.post("/api/generate/intelligent")
async def generate_with_intelligent_routing(request: Dict[str, Any]):
    """Generate response with intelligent routing: Abacus first, OpenAI fallback"""
    prompt = request.get("prompt", "")

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    # Try Abacus first
    if ABACUS_API_KEY:
        try:
            logger.info("Attempting generation with Abacus")
            abacus_result = await generate_with_abacus(request)
            logger.info("Abacus generation successful")
            return abacus_result
        except HTTPException as e:
            if e.status_code in [503, 502, 408]:  # Service unavailable, bad gateway, timeout
                logger.warning(f"Abacus unavailable ({e.status_code}), falling back to OpenAI")
            else:
                logger.error(f"Abacus error ({e.status_code}), falling back to OpenAI")
        except Exception as e:
            logger.error(f"Abacus unexpected error: {str(e)}, falling back to OpenAI")

    # Fallback to OpenAI
    if OPENAI_API_KEY:
        try:
            logger.info("Attempting generation with OpenAI")
            openai_result = await generate_with_openai(request)
            openai_result["fallback_used"] = True
            logger.info("OpenAI generation successful")
            return openai_result
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise HTTPException(status_code=503, detail="All AI providers unavailable")
    else:
        raise HTTPException(status_code=503, detail="No AI providers configured")

@app.get("/api/providers/status")
async def check_providers_status():
    """Check availability of all AI providers"""
    providers_status = {}

    # Check Abacus
    if ABACUS_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {ABACUS_API_KEY}"}
            client = await get_http_client()
                response = await client.get(
                    f"{ABACUS_BASE_URL}/models",  # Adjust endpoint for health check
                    headers=headers,
                    timeout=5.0
                )
                providers_status["abacus"] = {
                    "available": response.status_code == 200,
                    "status_code": response.status_code,
                    "configured": True
                }
        except Exception as e:
            providers_status["abacus"] = {
                "available": False,
                "error": str(e),
                "configured": True
            }
    else:
        providers_status["abacus"] = {
            "available": False,
            "configured": False,
            "error": "API key not configured"
        }

    # Check OpenAI
    if OPENAI_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
            client = await get_http_client()
                response = await client.get(
                    f"{OPENAI_BASE_URL}/models",
                    headers=headers,
                    timeout=5.0
                )
                providers_status["openai"] = {
                    "available": response.status_code == 200,
                    "status_code": response.status_code,
                    "configured": True
                }
        except Exception as e:
            providers_status["openai"] = {
                "available": False,
                "error": str(e),
                "configured": True
            }
    else:
        providers_status["openai"] = {
            "available": False,
            "configured": False,
            "error": "API key not configured"
        }

    return {
        "timestamp": datetime.now().isoformat(),
        "providers": providers_status,
        "total_available": sum(1 for p in providers_status.values() if p.get("available", False))
    }

if __name__ == "__main__":
    print("Starting AI Providers service...")
    uvicorn.run(app, host="0.0.0.0", port=8080)