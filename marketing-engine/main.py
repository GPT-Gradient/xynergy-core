from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from google.cloud import pubsub_v1, firestore

# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uvicorn
import logging
import asyncio
import time
from datetime import datetime
import json
import sys

# Import Phase 2 utilities
from phase2_utils import PerformanceMonitor, CircuitBreaker, CircuitBreakerConfig

# Import centralized authentication and caching
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from auth import verify_api_key, verify_api_key_optional
from redis_cache import redis_cache


# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))

# Initialize GCP clients
publisher = get_publisher_client()  # Phase 4: Shared connection pooling
db = get_firestore_client()  # Phase 4: Shared connection pooling

# Initialize monitoring and tracing
performance_monitor = PerformanceMonitor("marketing-engine")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=5, timeout=60))

# FastAPI app with correct title
app = FastAPI(
    title="Marketing Engine",
    description="AI-powered marketing campaign creation and management",
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
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "marketing-engine"}'
)
logger = logging.getLogger(__name__)

# Data models
class CampaignRequest(BaseModel):
    business_type: str
    target_audience: str
    budget_range: str
    campaign_goals: List[str]
    preferred_channels: List[str]

class CampaignResponse(BaseModel):
    campaign_id: str
    campaign_name: str
    strategy: Dict[str, Any]
    recommended_channels: List[str]
    estimated_reach: int
    budget_allocation: Dict[str, float]

class KeywordResearchRequest(BaseModel):
    business_type: str
    target_market: str
    competitor_urls: Optional[List[str]] = []

# Health check endpoint
@app.on_event("startup")
async def startup_event():
    """Initialize Redis cache connection on startup."""
    try:
        await redis_cache.connect()
        logger.info("Redis cache connected successfully")
    except Exception as e:
        logger.warning(f"Redis cache connection failed (will operate without cache): {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    try:
        await redis_cache.disconnect()
        logger.info("Redis cache disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting Redis: {e}")

@app.get("/health")
async def health_check():
    cache_status = "connected" if redis_cache._connected else "disconnected"
    return {
        "status": "healthy",
        "service": "marketing-engine",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "cache_status": cache_status
    }

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with performance_monitor.track_operation(f"execute_{action}"):
            if action == "analyze_market":
                intent = parameters.get("intent", "")
                context = parameters.get("context", {})
                market_analysis = {
                    "analysis_id": f"market_{int(time.time())}",
                    "workflow_id": workflow_context.get("workflow_id"),
                    "intent": intent,
                    "market_insights": ["High demand identified", "Competitive landscape analyzed", "Target segments defined"],
                    "recommendations": ["Focus on digital channels", "Emphasize unique value proposition"],
                    "confidence": 0.91,
                    "analyzed_at": datetime.utcnow()
                }

                return {
                    "success": True,
                    "action": action,
                    "output": {"analysis_id": market_analysis["analysis_id"], "insights": market_analysis["market_insights"]},
                    "execution_time": time.time(),
                    "service": "marketing-engine"
                }

            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not supported by marketing-engine",
                    "supported_actions": ["analyze_market"],
                    "service": "marketing-engine"
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "action": request.get("action"),
            "service": "marketing-engine"
        }

# Root endpoint with service info
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Xynergy Marketing Engine</title>
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

            .card {
                background: rgba(255,255,255,0.05);
                padding: 32px 24px;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                margin-bottom: 32px;
            }

            .card::before {
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

            .card:hover {
                transform: translateY(-3px);
                background: rgba(255,255,255,0.08);
                border-color: rgba(59, 130, 246, 0.3);
            }

            .card:hover::before {
                opacity: 1;
            }

            .card h2 {
                font-size: 1.3rem;
                margin-bottom: 24px;
                color: #3b82f6;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .card ul {
                list-style: none;
                padding-left: 0;
            }

            .card li {
                margin-bottom: 12px;
                padding: 12px 16px;
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
                border-left: 3px solid #3b82f6;
                transition: all 0.2s ease;
            }

            .card li:hover {
                background: rgba(255,255,255,0.08);
                transform: translateX(4px);
            }

            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                background: #22c55e;
                border-radius: 50%;
                margin-right: 8px;
            }

            @media (max-width: 768px) {
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
                        <h1>🎯 Xynergy Marketing Engine</h1>
                        <p>AI-powered marketing campaign creation and management</p>
                        <p><span class="status-indicator"></span>Service Status: Active | Version: 1.0.0</p>
                    </div>

                    <div class="card">
                        <h2>📋 Available Endpoints</h2>
                        <ul>
                            <li><strong>POST /campaigns/create</strong> - Create AI-generated marketing campaigns</li>
                            <li><strong>POST /keywords/research</strong> - AI keyword research and analysis</li>
                            <li><strong>GET /campaigns/{campaign_id}</strong> - Retrieve campaign details</li>
                            <li><strong>GET /analytics/performance</strong> - Campaign performance metrics</li>
                            <li><strong>GET /health</strong> - Health check</li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

# Create marketing campaign
@app.post("/campaigns/create", response_model=CampaignResponse, dependencies=[Depends(verify_api_key)])
async def create_campaign(request: CampaignRequest):
    try:
        # Performance monitoring
        with performance_monitor.track_operation("campaign_creation"):
            # Check Redis cache for similar campaign templates
            cache_key = f"{request.business_type}_{request.target_audience}_{request.budget_range}"
            cached_strategy = await redis_cache.get("campaign", cache_key)

            if cached_strategy:
                logger.info(f"Cache hit for campaign template: {cache_key}")
                campaign_strategy = cached_strategy
            else:
                # Generate campaign strategy using AI (expensive operation)
                campaign_strategy = await generate_campaign_strategy(request)

                # Cache the strategy for 1 hour (campaigns in same category are similar)
                await redis_cache.set("campaign", cache_key, campaign_strategy, ttl=3600)
                logger.info(f"Cached new campaign template: {cache_key}")

            # Create campaign ID
            campaign_id = f"camp_system_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            # Store campaign in Firestore collection
            campaign_doc = {
                "campaign_id": campaign_id,
                "business_type": request.business_type,
                "target_audience": request.target_audience,
                "budget_range": request.budget_range,
                "campaign_goals": request.campaign_goals,
                "strategy": campaign_strategy,
                "created_at": datetime.utcnow(),
                "status": "draft"
            }

            db.collection("marketing_campaigns").document(campaign_id).set(campaign_doc)

            # Publish event
            event_data = {
                "event_type": "campaign_created",
                "campaign_id": campaign_id,
                "business_type": request.business_type,
                "timestamp": datetime.utcnow().isoformat()
            }

            topic_path = publisher.topic_path(PROJECT_ID, "xynergy-marketing-events")
            publisher.publish(topic_path, json.dumps(event_data).encode())

            logger.info(f"Campaign created successfully: {campaign_id}")

            return CampaignResponse(
                campaign_id=campaign_id,
                campaign_name=campaign_strategy["name"],
                strategy=campaign_strategy,
                recommended_channels=campaign_strategy["channels"],
                estimated_reach=campaign_strategy["estimated_reach"],
                budget_allocation=campaign_strategy["budget_allocation"]
            )

    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")

# AI keyword research
@app.post("/keywords/research")
async def keyword_research(request: KeywordResearchRequest):
    try:
        with performance_monitor.track_operation("keyword_research"):
            # Generate keyword suggestions using AI
            keyword_data = await generate_keyword_research(request)

            # Store research in Firestore collection
            research_id = f"kw_system_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            research_doc = {
                "research_id": research_id,
                "business_type": request.business_type,
                "target_market": request.target_market,
                "keyword_data": keyword_data,
                "created_at": datetime.utcnow()
            }

            db.collection("keyword_research").document(research_id).set(research_doc)

            logger.info(f"Keyword research completed: {research_id}")

            return {
                "research_id": research_id,
                "primary_keywords": keyword_data["primary_keywords"],
                "long_tail_keywords": keyword_data["long_tail_keywords"],
                "competitor_analysis": keyword_data["competitor_analysis"],
                "search_volume_estimates": keyword_data["search_volumes"],
                "difficulty_scores": keyword_data["difficulty_scores"]
            }

    except Exception as e:
        logger.error(f"Error in keyword research: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to perform keyword research: {str(e)}")

# Get campaign details
@app.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    try:
        doc = db.collection("marketing_campaigns").document(campaign_id).get()
        if doc.exists:
            return doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail="Campaign not found")
    except Exception as e:
        logger.error(f"Error retrieving campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve campaign: {str(e)}")

# Campaign performance analytics
@app.get("/analytics/performance")
async def get_performance_analytics():
    try:
        # Get recent campaigns
        campaigns = db.collection("marketing_campaigns").order_by("created_at", direction=firestore.Query.DESCENDING).limit(10).stream()
        
        analytics_data = []
        for campaign in campaigns:
            data = campaign.to_dict()
            analytics_data.append({
                "campaign_id": data["campaign_id"],
                "business_type": data["business_type"],
                "status": data["status"],
                "created_at": data["created_at"].isoformat() if data["created_at"] else None,
                "estimated_reach": data["strategy"].get("estimated_reach", 0) if "strategy" in data else 0
            })
        
        return {
            "total_campaigns": len(analytics_data),
            "recent_campaigns": analytics_data,
            "performance_summary": {
                "total_estimated_reach": sum(c["estimated_reach"] for c in analytics_data),
                "active_campaigns": len([c for c in analytics_data if c["status"] == "active"]),
                "draft_campaigns": len([c for c in analytics_data if c["status"] == "draft"])
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")

# Helper functions
async def generate_campaign_strategy(request: CampaignRequest) -> Dict[str, Any]:
    """Generate AI-powered campaign strategy"""
    
    # Simulate AI strategy generation
    await asyncio.sleep(0.1)  # Simulate processing time
    
    strategy = {
        "name": f"{request.business_type.title()} Growth Campaign",
        "description": f"Targeted marketing campaign for {request.business_type} focusing on {request.target_audience}",
        "channels": request.preferred_channels if request.preferred_channels else ["social_media", "search", "email"],
        "estimated_reach": 10000 + len(request.campaign_goals) * 2000,
        "budget_allocation": {
            "social_media": 0.4,
            "search": 0.35,
            "email": 0.15,
            "content": 0.1
        },
        "timeline": "30 days",
        "key_messages": [
            f"Discover premium {request.business_type} solutions",
            f"Perfect for {request.target_audience}",
            "Limited time offer - act now!"
        ],
        "success_metrics": [
            "click_through_rate",
            "conversion_rate",
            "cost_per_acquisition",
            "return_on_ad_spend"
        ]
    }
    
    return strategy

async def generate_keyword_research(request: KeywordResearchRequest) -> Dict[str, Any]:
    """Generate AI-powered keyword research"""
    
    # Simulate AI keyword research
    await asyncio.sleep(0.1)  # Simulate processing time
    
    business_keywords = [
        f"{request.business_type} services",
        f"best {request.business_type}",
        f"{request.business_type} {request.target_market}",
        f"professional {request.business_type}",
        f"{request.business_type} solutions"
    ]
    
    long_tail_keywords = [
        f"affordable {request.business_type} services in {request.target_market}",
        f"top rated {request.business_type} company",
        f"how to choose {request.business_type} provider",
        f"{request.business_type} cost comparison",
        f"local {request.business_type} expert"
    ]
    
    return {
        "primary_keywords": business_keywords,
        "long_tail_keywords": long_tail_keywords,
        "competitor_analysis": {
            "competitive_keywords": 25,
            "opportunity_keywords": 15,
            "branded_keywords": 8
        },
        "search_volumes": {kw: 1000 + hash(kw) % 5000 for kw in business_keywords},
        "difficulty_scores": {kw: 30 + hash(kw) % 40 for kw in business_keywords}
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
