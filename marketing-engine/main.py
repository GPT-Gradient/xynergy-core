from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from google.cloud import pubsub_v1, firestore
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import uvicorn
import logging
import asyncio
from datetime import datetime
import json

# Import Phase 2 utilities
from phase2_utils import PerformanceMonitor, CircuitBreaker, CircuitBreakerConfig

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))

# Initialize GCP clients
publisher = pubsub_v1.PublisherClient()
db = firestore.Client()

# Initialize monitoring and tracing
performance_monitor = PerformanceMonitor("marketing-engine")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=5, timeout=60))

# FastAPI app with correct title
app = FastAPI(
    title="Marketing Engine",
    description="AI-powered marketing campaign creation and management",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "marketing-engine",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Root endpoint with service info
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>Xynergy Marketing Engine</title></head>
        <body>
            <h1>🎯 Xynergy Marketing Engine</h1>
            <p>AI-powered marketing campaign creation and management</p>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><strong>POST /campaigns/create</strong> - Create AI-generated marketing campaigns</li>
                <li><strong>POST /keywords/research</strong> - AI keyword research and analysis</li>
                <li><strong>GET /campaigns/{campaign_id}</strong> - Retrieve campaign details</li>
                <li><strong>GET /analytics/performance</strong> - Campaign performance metrics</li>
                <li><strong>GET /health</strong> - Health check</li>
            </ul>
            <p><em>Service Status: Active | Version: 1.0.0</em></p>
        </body>
    </html>
    """

# Create marketing campaign
@app.post("/campaigns/create", response_model=CampaignResponse)
async def create_campaign(request: CampaignRequest):
    try:
        # Performance monitoring
        with performance_monitor.track_operation("campaign_creation"):
            # Generate campaign strategy using AI
            campaign_strategy = await generate_campaign_strategy(request)

            # Create campaign ID
            campaign_id = f"camp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            # Store campaign in Firestore
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

            # Store research in Firestore
            research_id = f"kw_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
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
