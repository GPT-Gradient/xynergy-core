from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from google.cloud import pubsub_v1, firestore, storage

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
from datetime import datetime, timedelta
import json
import uuid
import requests
import concurrent.futures
from dataclasses import dataclass

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

# Initialize GCP clients
publisher = get_publisher_client()  # Phase 4: Shared connection pooling
subscriber = pubsub_v1.SubscriberClient()
db = get_firestore_client()  # Phase 4: Shared connection pooling
storage_client = storage.Client()

# FastAPI app
app = FastAPI(
    title="Market Intelligence Service",
    description="Perplexity integration and market trend analysis",
    version="1.0.0"
)

# CORS configuration
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
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "market-intelligence"}'
)
logger = logging.getLogger(__name__)

# Data Models
@dataclass
class MarketTrend:
    trend_id: str
    discovery_source: str
    trend_topic: str
    business_relevance_score: float
    opportunity_window: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    content_angles: List[str]
    related_keywords: List[str]
    business_implications: str
    created_at: datetime
    updated_at: datetime

class TrendDiscoveryRequest(BaseModel):
    categories: List[str]
    business_context: str
    relevance_threshold: float = 0.7
    max_results: int = 10

class TrendAnalysisResponse(BaseModel):
    trend_id: str
    topic: str
    relevance_score: float
    business_implications: str
    recommended_actions: List[str]
    content_opportunities: List[str]

# Perplexity API Integration
class PerplexityClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def discover_trends(self, query: str, context: str = "") -> Dict[str, Any]:
        """Discover trends using Perplexity's discovery capabilities."""
        try:
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a market intelligence analyst. Analyze current trends and provide business insights."
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\nContext: {context}\n\nProvide current trends, business implications, and opportunities in JSON format."
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 2000
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return {"error": f"API call failed: {response.status_code}"}

        except Exception as e:
            logger.error(f"Perplexity API exception: {str(e)}")
            return {"error": str(e)}

    async def analyze_trend(self, trend_topic: str, business_context: str) -> Dict[str, Any]:
        """Analyze a specific trend for business relevance."""
        try:
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a business analyst specializing in SEO and digital marketing trends."
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze this trend for business opportunities:

Trend: {trend_topic}
Business Context: {business_context}

Provide analysis in JSON format with:
1. business_relevance_score (0-1)
2. opportunity_window (timing analysis)
3. content_angles (list of content ideas)
4. related_keywords (SEO keywords)
5. business_implications (detailed analysis)
6. competitive_landscape (market analysis)"""
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Perplexity analysis error: {response.status_code}")
                return {"error": f"Analysis failed: {response.status_code}"}

        except Exception as e:
            logger.error(f"Trend analysis exception: {str(e)}")
            return {"error": str(e)}

# Initialize Perplexity client
perplexity_client = PerplexityClient(PERPLEXITY_API_KEY) if PERPLEXITY_API_KEY else None

# Health check endpoint
@app.get("/health")
async def health_check():
    status = "healthy" if PERPLEXITY_API_KEY else "degraded"
    return {
        "status": status,
        "service": "market-intelligence",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "perplexity_configured": bool(PERPLEXITY_API_KEY)
    }

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        if action == "discover_market_trends":
            categories = parameters.get("categories", ["seo_tools", "ai_platforms"])
            context = parameters.get("business_context", "SEO and AI industry analysis")
            result = await discover_market_trends(categories, context)
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "analyze_trend":
            trend_topic = parameters.get("trend_topic")
            context = parameters.get("business_context", "")
            if not trend_topic:
                raise HTTPException(status_code=400, detail="trend_topic required")

            result = await analyze_specific_trend(trend_topic, context)
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "get_trending_topics":
            result = await get_current_trending_topics()
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

    except Exception as e:
        logger.error(f"Execute workflow error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "workflow_context": workflow_context
        }

# Market Intelligence Endpoints
@app.post("/discover-trends")
async def discover_market_trends(
    categories: List[str],
    business_context: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Discover current market trends."""
    if not perplexity_client:
        raise HTTPException(status_code=503, detail="Perplexity API not configured")

    try:
        # Construct discovery query
        query = f"Current trends and developments in: {', '.join(categories)}"

        # Call Perplexity API
        trend_data = await perplexity_client.discover_trends(query, business_context)

        if "error" in trend_data:
            raise HTTPException(status_code=500, detail=trend_data["error"])

        # Process and store trends
        background_tasks.add_task(process_discovered_trends, trend_data, categories, business_context)

        return {
            "status": "success",
            "message": "Trend discovery initiated",
            "categories": categories,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Trend discovery error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-trend")
async def analyze_specific_trend(trend_topic: str, business_context: str) -> TrendAnalysisResponse:
    """Analyze a specific trend for business relevance."""
    if not perplexity_client:
        raise HTTPException(status_code=503, detail="Perplexity API not configured")

    try:
        # Analyze trend with Perplexity
        analysis = await perplexity_client.analyze_trend(trend_topic, business_context)

        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])

        # Extract analysis from response
        content = analysis.get("choices", [{}])[0].get("message", {}).get("content", "{}")

        # Parse JSON response (with fallback)
        try:
            parsed_analysis = json.loads(content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            parsed_analysis = {
                "business_relevance_score": 0.5,
                "business_implications": content,
                "content_angles": ["General trend analysis"],
                "related_keywords": [trend_topic.lower().replace(" ", "_")]
            }

        # Create trend record
        trend_id = str(uuid.uuid4())
        trend_data = {
            "trend_id": trend_id,
            "topic": trend_topic,
            "business_context": business_context,
            "analysis": parsed_analysis,
            "created_at": datetime.utcnow(),
            "source": "perplexity_analysis"
        }

        # Store in Firestore
        db.collection("market_intelligence").document(trend_id).set(trend_data)

        # Publish trend identified event
        await publish_trend_identified(trend_id, trend_topic, parsed_analysis.get("business_relevance_score", 0.5))

        return TrendAnalysisResponse(
            trend_id=trend_id,
            topic=trend_topic,
            relevance_score=parsed_analysis.get("business_relevance_score", 0.5),
            business_implications=parsed_analysis.get("business_implications", "Analysis in progress"),
            recommended_actions=parsed_analysis.get("recommended_actions", []),
            content_opportunities=parsed_analysis.get("content_angles", [])
        )

    except Exception as e:
        logger.error(f"Trend analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trending-topics")
async def get_current_trending_topics() -> List[Dict[str, Any]]:
    """Get current trending topics from Firestore."""
    try:
        # Query recent trends from Firestore
        trends_ref = db.collection("market_intelligence")
        query = trends_ref.where("created_at", ">=", datetime.utcnow() - timedelta(days=7)).order_by("created_at", direction=firestore.Query.DESCENDING).limit(20)

        trends = []
        for doc in query.stream():
            trend_data = doc.to_dict()
            trends.append({
                "trend_id": trend_data.get("trend_id"),
                "topic": trend_data.get("topic"),
                "relevance_score": trend_data.get("analysis", {}).get("business_relevance_score", 0),
                "created_at": trend_data.get("created_at").isoformat() if trend_data.get("created_at") else None
            })

        return trends

    except Exception as e:
        logger.error(f"Error getting trending topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background Processing
async def process_discovered_trends(trend_data: Dict[str, Any], categories: List[str], business_context: str):
    """Process discovered trends and store them."""
    try:
        # Extract trends from Perplexity response
        content = trend_data.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Store raw discovery data
        discovery_id = str(uuid.uuid4())
        discovery_record = {
            "discovery_id": discovery_id,
            "categories": categories,
            "business_context": business_context,
            "raw_response": content,
            "discovered_at": datetime.utcnow(),
            "source": "perplexity_discovery"
        }

        db.collection("market_discoveries").document(discovery_id).set(discovery_record)

        # Publish discovery complete event
        topic_path = publisher.topic_path(PROJECT_ID, "research-complete")
        message_data = {
            "discovery_id": discovery_id,
            "categories": categories,
            "trend_count": len(content.split("\n")) if content else 0,
            "timestamp": datetime.utcnow().isoformat()
        }

        future = publisher.publish(topic_path, json.dumps(message_data, default=str).encode())
        logger.info(f"Published discovery complete event for {discovery_id}")

    except Exception as e:
        logger.error(f"Error processing discovered trends: {str(e)}")

async def publish_trend_identified(trend_id: str, topic: str, relevance_score: float):
    """Publish trend identified event."""
    try:
        topic_path = publisher.topic_path(PROJECT_ID, "trend-identified")
        message_data = {
            "trend_id": trend_id,
            "topic": topic,
            "relevance_score": relevance_score,
            "source": "market_intelligence",
            "timestamp": datetime.utcnow().isoformat()
        }

        future = publisher.publish(topic_path, json.dumps(message_data, default=str).encode())
        logger.info(f"Published trend identified event for {trend_id}")

    except Exception as e:
        logger.error(f"Error publishing trend identified event: {str(e)}")

# Pub/Sub message handler
def handle_pubsub_message(message):
    """Handle incoming Pub/Sub messages."""
    try:
        data = json.loads(message.data.decode())
        task_id = data.get("task_id")
        task_type = data.get("task_type")
        parameters = data.get("parameters", {})

        logger.info(f"Processing task {task_id} of type {task_type}")

        if task_type == "market_intelligence":
            asyncio.run(process_market_intelligence_task(task_id, parameters))

        message.ack()

    except Exception as e:
        logger.error(f"Error handling Pub/Sub message: {str(e)}")
        message.nack()

async def process_market_intelligence_task(task_id: str, parameters: Dict[str, Any]):
    """Process market intelligence task from Pub/Sub."""
    try:
        categories = parameters.get("monitoring_categories", ["seo_tools", "ai_platforms"])
        context = parameters.get("business_context", "Market intelligence monitoring")

        # Discover trends
        await discover_market_trends(categories, context, BackgroundTasks())

        # Update task status
        db.collection("research_tasks").document(task_id).update({
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "results": {
                "categories_monitored": categories,
                "discovery_completed": True
            }
        })

    except Exception as e:
        logger.error(f"Error processing market intelligence task {task_id}: {str(e)}")
        db.collection("research_tasks").document(task_id).update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow()
        })

# Dashboard endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Market Intelligence dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Market Intelligence Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
            .stat { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
            .trends { margin-top: 20px; }
            .trend { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 3px; display: flex; justify-content: space-between; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer; }
            .score { background: #28a745; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌍 Market Intelligence Dashboard</h1>
            <p>Perplexity-powered trend discovery and market analysis</p>
        </div>

        <div class="stats">
            <div class="stat">
                <h3 id="trends-discovered">0</h3>
                <p>Trends Discovered</p>
            </div>
            <div class="stat">
                <h3 id="high-relevance">0</h3>
                <p>High Relevance</p>
            </div>
            <div class="stat">
                <h3 id="content-opportunities">0</h3>
                <p>Content Opportunities</p>
            </div>
            <div class="stat">
                <h3 id="api-calls">0</h3>
                <p>API Calls Today</p>
            </div>
        </div>

        <div>
            <h2>Quick Actions</h2>
            <button class="button" onclick="discoverTrends()">Discover Trends</button>
            <button class="button" onclick="analyzeTrend()">Analyze Specific Trend</button>
            <button class="button" onclick="refreshTrends()">Refresh Data</button>
        </div>

        <div class="trends">
            <h2>Recent Trends</h2>
            <div id="trends-list">Loading...</div>
        </div>

        <script>
            async function discoverTrends() {
                const categories = prompt('Enter categories (comma-separated):', 'seo_tools,ai_platforms');
                if (!categories) return;

                const response = await fetch('/discover-trends', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        categories: categories.split(',').map(c => c.trim()),
                        business_context: 'SEO and AI industry trend discovery'
                    })
                });
                const result = await response.json();
                alert('Trend discovery started');
                loadTrends();
            }

            async function analyzeTrend() {
                const topic = prompt('Enter trend topic to analyze:');
                if (!topic) return;

                const response = await fetch('/analyze-trend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        trend_topic: topic,
                        business_context: 'SEO services business analysis'
                    })
                });
                const result = await response.json();
                alert('Trend analysis completed: ' + result.trend_id);
                loadTrends();
            }

            async function loadTrends() {
                try {
                    const response = await fetch('/trending-topics');
                    const trends = await response.json();

                    const trendsList = document.getElementById('trends-list');
                    trendsList.innerHTML = '';

                    trends.forEach(trend => {
                        const trendDiv = document.createElement('div');
                        trendDiv.className = 'trend';
                        trendDiv.innerHTML = `
                            <div>
                                <strong>${trend.topic}</strong><br>
                                <small>${trend.created_at}</small>
                            </div>
                            <div class="score">Score: ${(trend.relevance_score * 100).toFixed(0)}%</div>
                        `;
                        trendsList.appendChild(trendDiv);
                    });

                    document.getElementById('trends-discovered').textContent = trends.length;
                    document.getElementById('high-relevance').textContent = trends.filter(t => t.relevance_score > 0.7).length;
                } catch (error) {
                    console.error('Error loading trends:', error);
                    document.getElementById('trends-list').innerHTML = '<div class="trend">Error loading trends</div>';
                }
            }

            function refreshTrends() {
                loadTrends();
            }

            // Load initial data
            loadTrends();
            setInterval(loadTrends, 60000); // Refresh every minute
        </script>
    </body>
    </html>
    """


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    # Set up Pub/Sub subscriber
    if os.getenv("PUBSUB_ENABLED", "true").lower() == "true":
        subscription_path = subscriber.subscription_path(PROJECT_ID, "xynergy-market-intelligence-events-subscription")
        try:
            subscriber.subscribe(subscription_path, callback=handle_pubsub_message)
            logger.info("Pub/Sub subscriber started")
        except Exception as e:
            logger.error(f"Failed to start Pub/Sub subscriber: {str(e)}")

    uvicorn.run(app, host="0.0.0.0", port=PORT)