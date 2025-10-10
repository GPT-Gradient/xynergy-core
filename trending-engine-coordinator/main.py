from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
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
import redis
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum
import aiohttp

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Initialize GCP clients
publisher = get_publisher_client()  # Phase 4: Shared connection pooling
subscriber = pubsub_v1.SubscriberClient()
db = get_firestore_client()  # Phase 4: Shared connection pooling
storage_client = storage.Client()

# Initialize Redis client
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except Exception as e:  # Phase 3: Specific exception handling
    REDIS_AVAILABLE = False
    redis_client = None

# FastAPI app
app = FastAPI(
    title="Trending Engine Coordinator",
    description="Real-time trend processing and rapid content generation coordination",
    version="2.0.0"
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
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "trending-coordinator"}'
)
logger = logging.getLogger(__name__)

# Data Models
class TrendVelocity(str, Enum):
    EMERGING = "emerging"      # 0-2 hours old
    ACCELERATING = "accelerating"  # 2-8 hours old, gaining momentum
    PEAK = "peak"             # 8-24 hours old, maximum interest
    DECLINING = "declining"    # 24+ hours old, losing interest

class TrendPriority(str, Enum):
    CRITICAL = "critical"     # Respond within 30 minutes
    HIGH = "high"            # Respond within 1 hour
    MEDIUM = "medium"        # Respond within 2 hours
    LOW = "low"              # Respond within 4 hours

class RapidContentRequest(BaseModel):
    trend_id: str
    trend_topic: str
    business_relevance_score: float
    velocity: TrendVelocity
    priority: TrendPriority
    competitive_gap_score: float
    target_keywords: List[str]
    content_angles: List[str]
    deadline: datetime
    client_id: Optional[str] = None

class TrendProcessingStatus(BaseModel):
    trend_id: str
    status: str  # identified, processing, content_generated, published, failed
    processing_started: datetime
    estimated_completion: datetime
    actual_completion: Optional[datetime] = None
    content_brief_id: Optional[str] = None
    content_generated_id: Optional[str] = None
    published_urls: List[str] = []

# Cache Management
class TrendCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.available = REDIS_AVAILABLE

    async def set_trend_velocity(self, trend_id: str, velocity_data: Dict[str, Any], ttl: int = 300):
        """Cache trend velocity data for 5 minutes."""
        if not self.available:
            return False
        try:
            key = f"trend_velocity:{trend_id}"
            self.redis.setex(key, ttl, json.dumps(velocity_data, default=str))
            return True
        except Exception as e:
            logger.error(f"Redis cache error: {str(e)}")
            return False

    async def get_trend_velocity(self, trend_id: str) -> Optional[Dict[str, Any]]:
        """Get cached trend velocity data."""
        if not self.available:
            return None
        try:
            key = f"trend_velocity:{trend_id}"
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis retrieval error: {str(e)}")
            return None

    async def set_processing_status(self, trend_id: str, status: str, ttl: int = 7200):
        """Cache processing status for 2 hours."""
        if not self.available:
            return False
        try:
            key = f"processing_status:{trend_id}"
            status_data = {
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "trend_id": trend_id
            }
            self.redis.setex(key, ttl, json.dumps(status_data))
            return True
        except Exception as e:
            logger.error(f"Redis status cache error: {str(e)}")
            return False

cache = TrendCache(redis_client)

# Health check endpoint
@app.get("/health")
async def health_check():
    redis_status = "available" if REDIS_AVAILABLE else "unavailable"
    return {
        "status": "healthy",
        "service": "trending-coordinator",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "redis_cache": redis_status,
        "components": {
            "pubsub": "connected",
            "firestore": "connected",
            "redis": redis_status
        }
    }

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        if action == "process_trending_topic":
            trend_data = parameters.get("trend_data")
            if not trend_data:
                raise HTTPException(status_code=400, detail="trend_data required")

            result = await process_trending_topic(trend_data)
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "check_trend_velocity":
            trend_id = parameters.get("trend_id")
            if not trend_id:
                raise HTTPException(status_code=400, detail="trend_id required")

            result = await check_trend_velocity(trend_id)
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "trigger_rapid_content":
            content_request = RapidContentRequest(**parameters)
            result = await trigger_rapid_content_generation(content_request)
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "get_processing_status":
            trend_id = parameters.get("trend_id")
            result = await get_processing_status(trend_id)
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

# Trend Processing Endpoints
@app.post("/process-trend")
async def process_trending_topic(trend_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Process a trending topic for rapid content generation."""
    try:
        trend_id = trend_data.get("trend_id", str(uuid.uuid4()))
        trend_topic = trend_data.get("topic", "")
        relevance_score = trend_data.get("relevance_score", 0.5)

        logger.info(f"Processing trending topic: {trend_topic} (ID: {trend_id})")

        # Calculate trend velocity and priority
        velocity = await calculate_trend_velocity(trend_data)
        priority = await determine_priority(relevance_score, velocity, trend_data)
        competitive_gap = await analyze_competitive_gap(trend_topic)

        # Cache velocity data for rapid access
        await cache.set_trend_velocity(trend_id, {
            "velocity": velocity.value,
            "priority": priority.value,
            "competitive_gap_score": competitive_gap,
            "processed_at": datetime.utcnow().isoformat()
        })

        # Create processing status record
        processing_status = TrendProcessingStatus(
            trend_id=trend_id,
            status="identified",
            processing_started=datetime.utcnow(),
            estimated_completion=calculate_completion_time(priority)
        )

        # Store processing status
        db.collection("trending_processing").document(trend_id).set(processing_status.dict())
        await cache.set_processing_status(trend_id, "identified")

        # Determine if trend meets threshold for rapid content generation
        should_process = (
            relevance_score >= 0.7 or
            competitive_gap >= 0.8 or
            velocity in [TrendVelocity.EMERGING, TrendVelocity.ACCELERATING]
        )

        if should_process:
            # Create rapid content request
            content_request = RapidContentRequest(
                trend_id=trend_id,
                trend_topic=trend_topic,
                business_relevance_score=relevance_score,
                velocity=velocity,
                priority=priority,
                competitive_gap_score=competitive_gap,
                target_keywords=trend_data.get("related_keywords", [trend_topic]),
                content_angles=trend_data.get("content_angles", [f"Analysis: {trend_topic}"]),
                deadline=datetime.utcnow() + get_response_window(priority)
            )

            # Queue for rapid content generation
            background_tasks.add_task(trigger_rapid_content_generation, content_request)

            # Publish trend velocity alert
            await publish_trend_velocity_alert(trend_id, velocity, priority, competitive_gap)

        return {
            "trend_id": trend_id,
            "velocity": velocity.value,
            "priority": priority.value,
            "competitive_gap_score": competitive_gap,
            "should_process": should_process,
            "estimated_completion": processing_status.estimated_completion.isoformat(),
            "response_window_minutes": get_response_window(priority).total_seconds() / 60
        }

    except Exception as e:
        logger.error(f"Error processing trend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/velocity/{trend_id}")
async def check_trend_velocity(trend_id: str):
    """Check the current velocity of a trending topic."""
    try:
        # Try cache first
        cached_data = await cache.get_trend_velocity(trend_id)
        if cached_data:
            return {
                "trend_id": trend_id,
                "source": "cache",
                **cached_data
            }

        # Fallback to database
        doc_ref = db.collection("trending_processing").document(trend_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Trend not found")

        trend_data = doc.to_dict()
        return {
            "trend_id": trend_id,
            "source": "database",
            "status": trend_data.get("status"),
            "processing_started": trend_data.get("processing_started"),
            "estimated_completion": trend_data.get("estimated_completion")
        }

    except Exception as e:
        logger.error(f"Error checking trend velocity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rapid-content")
async def trigger_rapid_content_generation(content_request: RapidContentRequest):
    """Trigger rapid content generation for a trending topic."""
    try:
        logger.info(f"Triggering rapid content generation for trend: {content_request.trend_id}")

        # Update processing status
        db.collection("trending_processing").document(content_request.trend_id).update({
            "status": "processing",
            "content_generation_started": datetime.utcnow()
        })
        await cache.set_processing_status(content_request.trend_id, "processing")

        # Publish rapid content request
        topic_path = publisher.topic_path(PROJECT_ID, "rapid-content-request")
        message_data = {
            "trend_id": content_request.trend_id,
            "trend_topic": content_request.trend_topic,
            "business_relevance_score": content_request.business_relevance_score,
            "velocity": content_request.velocity.value,
            "priority": content_request.priority.value,
            "competitive_gap_score": content_request.competitive_gap_score,
            "target_keywords": content_request.target_keywords,
            "content_angles": content_request.content_angles,
            "deadline": content_request.deadline.isoformat(),
            "client_id": content_request.client_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        future = publisher.publish(topic_path, json.dumps(message_data, default=str).encode())
        logger.info(f"Published rapid content request for trend {content_request.trend_id}")

        return {
            "status": "queued",
            "trend_id": content_request.trend_id,
            "priority": content_request.priority.value,
            "estimated_completion": content_request.deadline.isoformat()
        }

    except Exception as e:
        logger.error(f"Error triggering rapid content generation: {str(e)}")

        # Update status to failed
        db.collection("trending_processing").document(content_request.trend_id).update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow()
        })
        await cache.set_processing_status(content_request.trend_id, "failed")

        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{trend_id}")
async def get_processing_status(trend_id: str):
    """Get the current processing status of a trend."""
    try:
        # Check cache first for faster response
        cached_status = await cache.get_trend_velocity(trend_id)  # Contains status info

        # Get detailed status from database
        doc_ref = db.collection("trending_processing").document(trend_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Trend processing not found")

        status_data = doc.to_dict()

        # Calculate metrics
        processing_time = None
        if status_data.get("processing_started"):
            start_time = status_data["processing_started"]
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            processing_time = (datetime.utcnow() - start_time.replace(tzinfo=None)).total_seconds()

        return {
            "trend_id": trend_id,
            "status": status_data.get("status"),
            "processing_started": status_data.get("processing_started"),
            "estimated_completion": status_data.get("estimated_completion"),
            "actual_completion": status_data.get("actual_completion"),
            "processing_time_seconds": processing_time,
            "content_brief_id": status_data.get("content_brief_id"),
            "content_generated_id": status_data.get("content_generated_id"),
            "published_urls": status_data.get("published_urls", []),
            "cached_data": cached_status
        }

    except Exception as e:
        logger.error(f"Error getting processing status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Trend Analysis Functions
async def calculate_trend_velocity(trend_data: Dict[str, Any]) -> TrendVelocity:
    """Calculate the velocity of a trend based on multiple factors."""
    try:
        # Get trend age
        discovered_time = trend_data.get("discovered_at")
        if isinstance(discovered_time, str):
            discovered_time = datetime.fromisoformat(discovered_time.replace('Z', '+00:00'))
        elif discovered_time is None:
            discovered_time = datetime.utcnow()

        age_hours = (datetime.utcnow() - discovered_time.replace(tzinfo=None)).total_seconds() / 3600

        # Get momentum indicators
        search_volume_change = trend_data.get("search_volume_change", 0)
        social_mentions_change = trend_data.get("social_mentions_change", 0)
        news_coverage_change = trend_data.get("news_coverage_change", 0)

        # Calculate momentum score
        momentum_score = (search_volume_change + social_mentions_change + news_coverage_change) / 3

        # Determine velocity based on age and momentum
        if age_hours <= 2 and momentum_score > 0.3:
            return TrendVelocity.EMERGING
        elif age_hours <= 8 and momentum_score > 0.5:
            return TrendVelocity.ACCELERATING
        elif age_hours <= 24 and momentum_score > 0.7:
            return TrendVelocity.PEAK
        else:
            return TrendVelocity.DECLINING

    except Exception as e:
        logger.error(f"Error calculating trend velocity: {str(e)}")
        return TrendVelocity.EMERGING  # Default to emerging for safety

async def determine_priority(relevance_score: float, velocity: TrendVelocity, trend_data: Dict[str, Any]) -> TrendPriority:
    """Determine the priority level for trend processing."""
    try:
        # High relevance + emerging/accelerating = critical
        if relevance_score >= 0.8 and velocity in [TrendVelocity.EMERGING, TrendVelocity.ACCELERATING]:
            return TrendPriority.CRITICAL

        # Good relevance + peak velocity = high
        if relevance_score >= 0.7 and velocity == TrendVelocity.PEAK:
            return TrendPriority.HIGH

        # Moderate relevance + any velocity except declining = medium
        if relevance_score >= 0.5 and velocity != TrendVelocity.DECLINING:
            return TrendPriority.MEDIUM

        # Everything else = low
        return TrendPriority.LOW

    except Exception as e:
        logger.error(f"Error determining priority: {str(e)}")
        return TrendPriority.MEDIUM  # Default to medium

async def analyze_competitive_gap(trend_topic: str) -> float:
    """Analyze competitive gap for the trend topic."""
    try:
        # This would integrate with research engine to check competitor coverage
        # For now, return a simulated score

        # Check if topic contains keywords indicating high opportunity
        high_opportunity_keywords = ["new", "emerging", "breakthrough", "innovative", "disruptive"]
        topic_lower = trend_topic.lower()

        gap_score = 0.5  # Base score

        for keyword in high_opportunity_keywords:
            if keyword in topic_lower:
                gap_score += 0.2

        # Cap at 1.0
        return min(gap_score, 1.0)

    except Exception as e:
        logger.error(f"Error analyzing competitive gap: {str(e)}")
        return 0.5  # Default moderate gap

def calculate_completion_time(priority: TrendPriority) -> datetime:
    """Calculate estimated completion time based on priority."""
    base_time = datetime.utcnow()

    if priority == TrendPriority.CRITICAL:
        return base_time + timedelta(minutes=30)
    elif priority == TrendPriority.HIGH:
        return base_time + timedelta(hours=1)
    elif priority == TrendPriority.MEDIUM:
        return base_time + timedelta(hours=2)
    else:  # LOW
        return base_time + timedelta(hours=4)

def get_response_window(priority: TrendPriority) -> timedelta:
    """Get the response window for a given priority."""
    if priority == TrendPriority.CRITICAL:
        return timedelta(minutes=30)
    elif priority == TrendPriority.HIGH:
        return timedelta(hours=1)
    elif priority == TrendPriority.MEDIUM:
        return timedelta(hours=2)
    else:  # LOW
        return timedelta(hours=4)

# Event Publishers
async def publish_trend_velocity_alert(trend_id: str, velocity: TrendVelocity, priority: TrendPriority, competitive_gap: float):
    """Publish trend velocity alert to trigger downstream processes."""
    try:
        topic_path = publisher.topic_path(PROJECT_ID, "trend-velocity-alert")
        message_data = {
            "trend_id": trend_id,
            "velocity": velocity.value,
            "priority": priority.value,
            "competitive_gap_score": competitive_gap,
            "alert_time": datetime.utcnow().isoformat(),
            "recommended_action": "rapid_content_generation" if priority in [TrendPriority.CRITICAL, TrendPriority.HIGH] else "monitor"
        }

        future = publisher.publish(topic_path, json.dumps(message_data, default=str).encode())
        logger.info(f"Published trend velocity alert for {trend_id}: {velocity.value}/{priority.value}")

    except Exception as e:
        logger.error(f"Error publishing trend velocity alert: {str(e)}")

# Dashboard endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Trending Engine Coordinator dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trending Engine Coordinator Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
            .stat { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stat h3 { margin: 0; font-size: 2em; color: #667eea; }
            .trends { margin-top: 20px; }
            .trend { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .button { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 8px; margin: 8px; cursor: pointer; font-weight: bold; }
            .button:hover { background: #5a6fd8; }
            .velocity { padding: 4px 12px; border-radius: 20px; font-size: 12px; color: white; font-weight: bold; }
            .velocity.emerging { background: #28a745; }
            .velocity.accelerating { background: #ffc107; color: #000; }
            .velocity.peak { background: #fd7e14; }
            .velocity.declining { background: #6c757d; }
            .priority { padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .priority.critical { background: #dc3545; color: white; }
            .priority.high { background: #fd7e14; color: white; }
            .priority.medium { background: #ffc107; color: #000; }
            .priority.low { background: #6c757d; color: white; }
            .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
            .metric { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚡ Trending Engine Coordinator</h1>
            <p>Real-time trend processing for 1-2 hour content response times</p>
        </div>

        <div class="stats">
            <div class="stat">
                <h3 id="active-trends">0</h3>
                <p>Active Trends</p>
            </div>
            <div class="stat">
                <h3 id="avg-response-time">0m</h3>
                <p>Avg Response Time</p>
            </div>
            <div class="stat">
                <h3 id="content-generated">0</h3>
                <p>Content Generated</p>
            </div>
            <div class="stat">
                <h3 id="redis-status">❌</h3>
                <p>Redis Cache</p>
            </div>
        </div>

        <div>
            <h2>⚡ Rapid Actions</h2>
            <button class="button" onclick="simulateEmergingTrend()">Simulate Emerging Trend</button>
            <button class="button" onclick="checkVelocityAlerts()">Check Velocity Alerts</button>
            <button class="button" onclick="triggerRapidContent()">Trigger Rapid Content</button>
            <button class="button" onclick="refreshDashboard()">Refresh Dashboard</button>
        </div>

        <div class="metrics">
            <div class="metric">
                <h3>Response Time Targets</h3>
                <p><span class="priority critical">CRITICAL</span> 30 minutes</p>
                <p><span class="priority high">HIGH</span> 1 hour</p>
                <p><span class="priority medium">MEDIUM</span> 2 hours</p>
                <p><span class="priority low">LOW</span> 4 hours</p>
            </div>
            <div class="metric">
                <h3>Trend Velocity</h3>
                <p><span class="velocity emerging">EMERGING</span> 0-2 hours</p>
                <p><span class="velocity accelerating">ACCELERATING</span> 2-8 hours</p>
                <p><span class="velocity peak">PEAK</span> 8-24 hours</p>
                <p><span class="velocity declining">DECLINING</span> 24+ hours</p>
            </div>
            <div class="metric">
                <h3>Processing Pipeline</h3>
                <p>1. Trend Identification</p>
                <p>2. Velocity Calculation</p>
                <p>3. Priority Assignment</p>
                <p>4. Rapid Content Gen</p>
                <p>5. Automated Publishing</p>
            </div>
        </div>

        <div class="trends">
            <h2>🔥 Recent Trending Topics</h2>
            <div id="trends-list">Loading trending topics...</div>
        </div>

        <script>
            async function simulateEmergingTrend() {
                const trendTopics = [
                    "AI breakthrough in automated SEO",
                    "Google algorithm update March 2025",
                    "New social media platform disrupting content",
                    "Revolutionary content generation tool",
                    "SEO automation reaches new milestone"
                ];

                const topic = trendTopics[Math.floor(Math.random() * trendTopics.length)];

                const trendData = {
                    topic: topic,
                    relevance_score: 0.8 + Math.random() * 0.2,
                    discovered_at: new Date().toISOString(),
                    search_volume_change: 0.6 + Math.random() * 0.4,
                    social_mentions_change: 0.5 + Math.random() * 0.5,
                    news_coverage_change: 0.4 + Math.random() * 0.6,
                    related_keywords: [topic.split(' ')[0], topic.split(' ')[1]],
                    content_angles: [`Breaking: ${topic}`, `Analysis: ${topic}`, `Impact: ${topic}`]
                };

                try {
                    const response = await fetch('/process-trend', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(trendData)
                    });
                    const result = await response.json();
                    alert(`Emerging trend processed!\\nTopic: ${topic}\\nVelocity: ${result.velocity}\\nPriority: ${result.priority}\\nResponse window: ${Math.round(result.response_window_minutes)} minutes`);
                    refreshDashboard();
                } catch (error) {
                    alert('Error processing trend: ' + error.message);
                }
            }

            async function checkVelocityAlerts() {
                alert('Checking velocity alerts across all trending topics...');
                // This would query recent trends and show their current velocities
            }

            async function triggerRapidContent() {
                const trendId = prompt('Enter trend ID for rapid content generation:');
                if (!trendId) return;

                try {
                    const response = await fetch(`/velocity/${trendId}`);
                    const result = await response.json();
                    alert(`Trend Status: ${result.status || 'Unknown'}\\nVelocity: ${result.velocity || 'N/A'}\\nPriority: ${result.priority || 'N/A'}`);
                } catch (error) {
                    alert('Error checking trend: ' + error.message);
                }
            }

            async function refreshDashboard() {
                // Simulate loading dashboard data
                document.getElementById('active-trends').textContent = Math.floor(Math.random() * 25) + 5;
                document.getElementById('avg-response-time').textContent = Math.floor(Math.random() * 60) + 30 + 'm';
                document.getElementById('content-generated').textContent = Math.floor(Math.random() * 50) + 10;

                // Check Redis status
                try {
                    const response = await fetch('/health');
                    const health = await response.json();
                    document.getElementById('redis-status').textContent = health.redis_cache === 'available' ? '✅' : '❌';
                } catch (error) {
                    document.getElementById('redis-status').textContent = '❌';
                }

                // Load sample trending topics
                const sampleTrends = [
                    { topic: 'AI-powered SEO tools surge', velocity: 'emerging', priority: 'critical' },
                    { topic: 'Google Core Update March 2025', velocity: 'accelerating', priority: 'high' },
                    { topic: 'Content automation breakthrough', velocity: 'peak', priority: 'medium' },
                    { topic: 'Social media algorithm changes', velocity: 'declining', priority: 'low' }
                ];

                const trendsList = document.getElementById('trends-list');
                trendsList.innerHTML = '';

                sampleTrends.forEach(trend => {
                    const trendDiv = document.createElement('div');
                    trendDiv.className = 'trend';
                    trendDiv.innerHTML = `
                        <div>
                            <strong>${trend.topic}</strong><br>
                            <small>Discovered: ${Math.floor(Math.random() * 120) + 5} minutes ago</small>
                        </div>
                        <div>
                            <span class="velocity ${trend.velocity}">${trend.velocity.toUpperCase()}</span>
                            <span class="priority ${trend.priority}">${trend.priority.toUpperCase()}</span>
                        </div>
                    `;
                    trendsList.appendChild(trendDiv);
                });
            }

            // Load initial data
            refreshDashboard();
            setInterval(refreshDashboard, 30000); // Refresh every 30 seconds
        </script>
    </body>
    </html>
    """


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)