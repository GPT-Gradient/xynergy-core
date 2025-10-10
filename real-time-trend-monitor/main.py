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
import redis
from datetime import datetime, timedelta
import json
import uuid
import aiohttp
import hashlib
from dataclasses import dataclass

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
GOOGLE_TRENDS_API_KEY = os.getenv("GOOGLE_TRENDS_API_KEY", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# Initialize GCP clients
publisher = get_publisher_client()  # Phase 4: Shared connection pooling
subscriber = pubsub_v1.SubscriberClient()
db = get_firestore_client()  # Phase 4: Shared connection pooling
storage_client = storage.Client()

# Initialize Redis client
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:  # Phase 3: Specific exception handling
    REDIS_AVAILABLE = False
    redis_client = None

# FastAPI app
app = FastAPI(
    title="Real-Time Trend Monitor",
    description="Multi-source trend monitoring for rapid trend identification",
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
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "trend-monitor"}'
)
logger = logging.getLogger(__name__)

# Data Models
@dataclass
class TrendSource:
    name: str
    url: str
    weight: float  # 0.0 to 1.0, how much to trust this source
    update_frequency: int  # minutes
    last_check: datetime
    status: str  # active, error, disabled

class TrendSignal(BaseModel):
    source: str
    topic: str
    signal_strength: float  # 0.0 to 1.0
    velocity: float  # rate of change
    volume: int  # absolute mentions/searches
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class MonitoringConfig(BaseModel):
    sources_enabled: List[str] = ["google_trends", "reddit_trends", "news_monitoring"]
    monitoring_interval: int = 5  # minutes
    trend_threshold: float = 0.6  # minimum signal strength to report
    velocity_threshold: float = 0.3  # minimum velocity to report
    categories: List[str] = ["seo_tools", "ai_platforms", "digital_marketing", "content_creation"]

# Trend Source Configuration
TREND_SOURCES = {
    "google_trends": TrendSource(
        name="Google Trends",
        url="https://trends.google.com/trends/api",
        weight=0.9,
        update_frequency=5,
        last_check=datetime.utcnow() - timedelta(hours=1),
        status="active"
    ),
    "reddit_trends": TrendSource(
        name="Reddit Hot Topics",
        url="https://www.reddit.com/r/seo+digital_marketing+ai+technology/hot.json",
        weight=0.7,
        update_frequency=3,
        last_check=datetime.utcnow() - timedelta(hours=1),
        status="active"
    ),
    "news_monitoring": TrendSource(
        name="Tech News Monitoring",
        url="https://newsapi.org/v2/everything",
        weight=0.8,
        update_frequency=10,
        last_check=datetime.utcnow() - timedelta(hours=1),
        status="active"
    ),
    "social_listening": TrendSource(
        name="Social Media Listening",
        url="https://api.twitter.com/2/tweets/search/recent",
        weight=0.6,
        update_frequency=2,
        last_check=datetime.utcnow() - timedelta(hours=1),
        status="active"
    )
}

# Trend Detection Engine
class TrendDetectionEngine:
    def __init__(self):
        self.monitored_topics = set()
        self.trending_history = {}
        self.signal_cache = {}

    async def monitor_all_sources(self, config: MonitoringConfig):
        """Monitor all configured trend sources."""
        tasks = []

        for source_name in config.sources_enabled:
            if source_name in TREND_SOURCES:
                source = TREND_SOURCES[source_name]
                if source.status == "active":
                    tasks.append(self.monitor_source(source_name, source, config))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return self.process_monitoring_results(results)

        return []

    async def monitor_source(self, source_name: str, source: TrendSource, config: MonitoringConfig) -> List[TrendSignal]:
        """Monitor a specific trend source."""
        try:
            logger.info(f"Monitoring {source_name}...")

            signals = []

            if source_name == "google_trends":
                signals = await self.monitor_google_trends(config.categories)
            elif source_name == "reddit_trends":
                signals = await self.monitor_reddit(config.categories)
            elif source_name == "news_monitoring":
                signals = await self.monitor_news(config.categories)
            elif source_name == "social_listening":
                signals = await self.monitor_social_media(config.categories)

            # Update last check time
            TREND_SOURCES[source_name].last_check = datetime.utcnow()

            logger.info(f"Found {len(signals)} signals from {source_name}")
            return signals

        except Exception as e:
            logger.error(f"Error monitoring {source_name}: {str(e)}")
            TREND_SOURCES[source_name].status = "error"
            return []

    async def monitor_google_trends(self, categories: List[str]) -> List[TrendSignal]:
        """Monitor Google Trends for trending topics."""
        try:
            # This would integrate with Google Trends API
            # For now, simulate trending topics based on common SEO/AI topics

            simulated_trends = [
                {"topic": "AI content generation tools 2025", "volume": 12500, "growth": 0.45},
                {"topic": "Google algorithm update March", "volume": 8900, "growth": 0.72},
                {"topic": "SEO automation platforms", "volume": 6700, "growth": 0.38},
                {"topic": "Content strategy AI tools", "volume": 4200, "growth": 0.55},
                {"topic": "Voice search optimization", "volume": 3800, "growth": 0.29}
            ]

            signals = []
            for trend in simulated_trends:
                signal = TrendSignal(
                    source="google_trends",
                    topic=trend["topic"],
                    signal_strength=min(trend["growth"] + 0.2, 1.0),
                    velocity=trend["growth"],
                    volume=trend["volume"],
                    timestamp=datetime.utcnow(),
                    metadata={
                        "category": "seo_tools",
                        "region": "global",
                        "time_range": "24h"
                    }
                )
                signals.append(signal)

            return signals

        except Exception as e:
            logger.error(f"Error monitoring Google Trends: {str(e)}")
            return []

    async def monitor_reddit(self, categories: List[str]) -> List[TrendSignal]:
        """Monitor Reddit for trending discussions."""
        try:
            # This would use Reddit API to fetch hot posts
            # Simulating reddit trends

            reddit_trends = [
                {"topic": "New AI SEO tool disrupting industry", "score": 850, "comments": 123},
                {"topic": "Google Core Update breaking websites", "score": 720, "comments": 89},
                {"topic": "Content automation breakthrough", "score": 640, "comments": 67},
                {"topic": "SEO vs AI content debate", "score": 430, "comments": 156}
            ]

            signals = []
            for trend in reddit_trends:
                # Calculate signal strength based on score and engagement
                engagement_ratio = trend["comments"] / max(trend["score"] / 10, 1)
                signal_strength = min((trend["score"] / 1000) + (engagement_ratio * 0.3), 1.0)
                velocity = min(engagement_ratio * 0.5, 1.0)

                signal = TrendSignal(
                    source="reddit_trends",
                    topic=trend["topic"],
                    signal_strength=signal_strength,
                    velocity=velocity,
                    volume=trend["score"],
                    timestamp=datetime.utcnow(),
                    metadata={
                        "comments": trend["comments"],
                        "subreddit": "seo",
                        "engagement_ratio": engagement_ratio
                    }
                )
                signals.append(signal)

            return signals

        except Exception as e:
            logger.error(f"Error monitoring Reddit: {str(e)}")
            return []

    async def monitor_news(self, categories: List[str]) -> List[TrendSignal]:
        """Monitor tech news for trending topics."""
        try:
            # This would integrate with NewsAPI or similar
            # Simulating news trends

            news_trends = [
                {"title": "Major search engine announces AI integration", "mentions": 45, "sentiment": 0.8},
                {"title": "Content marketing landscape shifts with automation", "mentions": 32, "sentiment": 0.6},
                {"title": "SEO industry adapts to AI content detection", "mentions": 28, "sentiment": 0.4},
                {"title": "New regulations for AI-generated content", "mentions": 24, "sentiment": 0.3}
            ]

            signals = []
            for news in news_trends:
                signal_strength = min((news["mentions"] / 50) + (news["sentiment"] * 0.4), 1.0)
                velocity = news["sentiment"] * 0.6  # Positive sentiment drives velocity

                signal = TrendSignal(
                    source="news_monitoring",
                    topic=news["title"],
                    signal_strength=signal_strength,
                    velocity=velocity,
                    volume=news["mentions"],
                    timestamp=datetime.utcnow(),
                    metadata={
                        "sentiment": news["sentiment"],
                        "news_source": "tech_aggregator"
                    }
                )
                signals.append(signal)

            return signals

        except Exception as e:
            logger.error(f"Error monitoring news: {str(e)}")
            return []

    async def monitor_social_media(self, categories: List[str]) -> List[TrendSignal]:
        """Monitor social media for trending topics."""
        try:
            # This would integrate with Twitter API v2, LinkedIn, etc.
            # Simulating social media trends

            social_trends = [
                {"topic": "#AIContentCreation trending", "mentions": 1250, "growth_rate": 0.65},
                {"topic": "SEO automation discussion surge", "mentions": 890, "growth_rate": 0.48},
                {"topic": "Content strategy AI debate", "mentions": 670, "growth_rate": 0.72},
                {"topic": "Google update impact analysis", "mentions": 540, "growth_rate": 0.39}
            ]

            signals = []
            for trend in social_trends:
                signal_strength = min((trend["mentions"] / 1500) + trend["growth_rate"] * 0.5, 1.0)
                velocity = trend["growth_rate"]

                signal = TrendSignal(
                    source="social_listening",
                    topic=trend["topic"],
                    signal_strength=signal_strength,
                    velocity=velocity,
                    volume=trend["mentions"],
                    timestamp=datetime.utcnow(),
                    metadata={
                        "growth_rate": trend["growth_rate"],
                        "platform": "multi_platform"
                    }
                )
                signals.append(signal)

            return signals

        except Exception as e:
            logger.error(f"Error monitoring social media: {str(e)}")
            return []

    def process_monitoring_results(self, results: List) -> List[TrendSignal]:
        """Process and combine signals from all sources."""
        all_signals = []

        for result in results:
            if isinstance(result, list):
                all_signals.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Monitoring error: {result}")

        # Deduplicate and rank signals
        return self.deduplicate_and_rank(all_signals)

    def deduplicate_and_rank(self, signals: List[TrendSignal]) -> List[TrendSignal]:
        """Remove duplicates and rank signals by strength."""
        # Group similar topics
        topic_groups = {}

        for signal in signals:
            # Simple topic similarity - in production would use better matching
            topic_key = self.normalize_topic(signal.topic)

            if topic_key not in topic_groups:
                topic_groups[topic_key] = []
            topic_groups[topic_key].append(signal)

        # Combine signals for similar topics
        combined_signals = []
        for topic_key, topic_signals in topic_groups.items():
            if len(topic_signals) == 1:
                combined_signals.append(topic_signals[0])
            else:
                combined_signal = self.combine_signals(topic_signals)
                combined_signals.append(combined_signal)

        # Sort by signal strength
        combined_signals.sort(key=lambda x: x.signal_strength, reverse=True)

        return combined_signals

    def normalize_topic(self, topic: str) -> str:
        """Normalize topic for similarity matching."""
        # Simple normalization - remove common words, lowercase
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = topic.lower().split()
        filtered_words = [w for w in words if w not in stop_words]
        return " ".join(sorted(filtered_words[:3]))  # Use first 3 significant words

    def combine_signals(self, signals: List[TrendSignal]) -> TrendSignal:
        """Combine multiple signals for the same topic."""
        if not signals:
            return None

        # Weight signals by source reliability
        total_weight = 0
        weighted_strength = 0
        weighted_velocity = 0
        total_volume = 0

        for signal in signals:
            source_weight = TREND_SOURCES.get(signal.source, TrendSource("", "", 0.5, 0, datetime.utcnow(), "")).weight
            total_weight += source_weight
            weighted_strength += signal.signal_strength * source_weight
            weighted_velocity += signal.velocity * source_weight
            total_volume += signal.volume

        # Use the best topic name and most recent timestamp
        best_signal = max(signals, key=lambda x: x.signal_strength)
        latest_timestamp = max(signals, key=lambda x: x.timestamp).timestamp

        return TrendSignal(
            source="aggregated",
            topic=best_signal.topic,
            signal_strength=weighted_strength / total_weight if total_weight > 0 else 0,
            velocity=weighted_velocity / total_weight if total_weight > 0 else 0,
            volume=total_volume,
            timestamp=latest_timestamp,
            metadata={
                "combined_sources": [s.source for s in signals],
                "source_count": len(signals)
            }
        )

detector = TrendDetectionEngine()

# Health check endpoint
@app.get("/health")
async def health_check():
    source_status = {name: source.status for name, source in TREND_SOURCES.items()}
    redis_status = "available" if REDIS_AVAILABLE else "unavailable"

    return {
        "status": "healthy",
        "service": "real-time-trend-monitor",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "sources": source_status,
        "redis_cache": redis_status
    }

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        if action == "start_monitoring":
            config = MonitoringConfig(**parameters)
            result = await start_trend_monitoring(config)
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "check_trends":
            result = await get_current_trends()
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "configure_sources":
            source_config = parameters.get("source_config", {})
            result = await configure_monitoring_sources(source_config)
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

# Trend Monitoring Endpoints
@app.post("/start-monitoring")
async def start_trend_monitoring(config: MonitoringConfig, background_tasks: BackgroundTasks):
    """Start real-time trend monitoring with specified configuration."""
    try:
        logger.info(f"Starting trend monitoring with config: {config.dict()}")

        # Start background monitoring task
        background_tasks.add_task(continuous_monitoring_loop, config)

        return {
            "status": "monitoring_started",
            "config": config.dict(),
            "sources_enabled": config.sources_enabled,
            "monitoring_interval": config.monitoring_interval,
            "trend_threshold": config.trend_threshold
        }

    except Exception as e:
        logger.error(f"Error starting monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/current-trends")
async def get_current_trends(limit: int = 20):
    """Get current trending topics from all monitored sources."""
    try:
        config = MonitoringConfig()  # Use default config
        signals = await detector.monitor_all_sources(config)

        # Filter by thresholds
        filtered_signals = [
            s for s in signals
            if s.signal_strength >= config.trend_threshold and s.velocity >= config.velocity_threshold
        ]

        # Limit results
        trending_topics = []
        for signal in filtered_signals[:limit]:
            trending_topics.append({
                "topic": signal.topic,
                "signal_strength": signal.signal_strength,
                "velocity": signal.velocity,
                "volume": signal.volume,
                "source": signal.source,
                "timestamp": signal.timestamp.isoformat(),
                "metadata": signal.metadata
            })

        return {
            "trending_topics": trending_topics,
            "total_signals": len(signals),
            "filtered_signals": len(filtered_signals),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting current trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/source-status")
async def get_source_status():
    """Get the status of all monitoring sources."""
    try:
        source_status = {}
        for name, source in TREND_SOURCES.items():
            source_status[name] = {
                "name": source.name,
                "status": source.status,
                "weight": source.weight,
                "update_frequency": source.update_frequency,
                "last_check": source.last_check.isoformat(),
                "minutes_since_last_check": (datetime.utcnow() - source.last_check).total_seconds() / 60
            }

        return {
            "sources": source_status,
            "total_sources": len(TREND_SOURCES),
            "active_sources": sum(1 for s in TREND_SOURCES.values() if s.status == "active"),
            "redis_available": REDIS_AVAILABLE
        }

    except Exception as e:
        logger.error(f"Error getting source status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/configure-sources")
async def configure_monitoring_sources(source_config: Dict[str, Any]):
    """Configure monitoring sources settings."""
    try:
        updated_sources = []

        for source_name, settings in source_config.items():
            if source_name in TREND_SOURCES:
                source = TREND_SOURCES[source_name]

                if "status" in settings:
                    source.status = settings["status"]
                if "weight" in settings:
                    source.weight = float(settings["weight"])
                if "update_frequency" in settings:
                    source.update_frequency = int(settings["update_frequency"])

                updated_sources.append(source_name)

        return {
            "status": "configured",
            "updated_sources": updated_sources,
            "current_config": {name: {"status": s.status, "weight": s.weight, "frequency": s.update_frequency}
                             for name, s in TREND_SOURCES.items()}
        }

    except Exception as e:
        logger.error(f"Error configuring sources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background Monitoring Loop
async def continuous_monitoring_loop(config: MonitoringConfig):
    """Continuously monitor trends and publish significant changes."""
    try:
        logger.info("Starting continuous monitoring loop")

        while True:
            try:
                # Get current trends
                signals = await detector.monitor_all_sources(config)

                # Filter significant trends
                significant_trends = [
                    s for s in signals
                    if s.signal_strength >= config.trend_threshold and s.velocity >= config.velocity_threshold
                ]

                # Publish trend alerts for significant trends
                for trend in significant_trends:
                    await publish_trend_alert(trend, config)

                # Cache current trends
                if REDIS_AVAILABLE:
                    await cache_current_trends(significant_trends)

                logger.info(f"Monitoring cycle completed: {len(significant_trends)} significant trends found")

            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")

            # Wait for next monitoring cycle
            await asyncio.sleep(config.monitoring_interval * 60)

    except asyncio.CancelledError:
        logger.info("Monitoring loop cancelled")
    except Exception as e:
        logger.error(f"Fatal error in monitoring loop: {str(e)}")

async def publish_trend_alert(signal: TrendSignal, config: MonitoringConfig):
    """Publish trend alert to trending engine coordinator."""
    try:
        # Calculate business relevance score based on categories
        business_relevance = calculate_business_relevance(signal, config.categories)

        # Only publish if business relevance is high enough
        if business_relevance < 0.5:
            return

        topic_path = publisher.topic_path(PROJECT_ID, "trend-identified")
        trend_data = {
            "trend_id": str(uuid.uuid4()),
            "topic": signal.topic,
            "relevance_score": business_relevance,
            "signal_strength": signal.signal_strength,
            "velocity": signal.velocity,
            "volume": signal.volume,
            "source": signal.source,
            "discovered_at": signal.timestamp.isoformat(),
            "related_keywords": extract_keywords(signal.topic),
            "content_angles": generate_content_angles(signal.topic),
            "metadata": signal.metadata
        }

        future = publisher.publish(topic_path, json.dumps(trend_data, default=str).encode())
        logger.info(f"Published trend alert: {signal.topic} (relevance: {business_relevance:.2f})")

    except Exception as e:
        logger.error(f"Error publishing trend alert: {str(e)}")

def calculate_business_relevance(signal: TrendSignal, categories: List[str]) -> float:
    """Calculate business relevance score for a trend signal."""
    try:
        topic_lower = signal.topic.lower()
        relevance_score = 0.3  # Base relevance

        # Check for category keywords
        category_keywords = {
            "seo_tools": ["seo", "search", "optimization", "ranking", "google", "keywords"],
            "ai_platforms": ["ai", "artificial intelligence", "machine learning", "automation", "chatgpt"],
            "digital_marketing": ["marketing", "content", "social media", "advertising", "campaign"],
            "content_creation": ["content", "writing", "blogging", "copywriting", "generation"]
        }

        for category in categories:
            if category in category_keywords:
                for keyword in category_keywords[category]:
                    if keyword in topic_lower:
                        relevance_score += 0.15

        # Boost for high-signal topics
        if signal.signal_strength > 0.7:
            relevance_score += 0.2

        # Boost for high-velocity topics
        if signal.velocity > 0.6:
            relevance_score += 0.15

        return min(relevance_score, 1.0)

    except Exception as e:
        logger.error(f"Error calculating business relevance: {str(e)}")
        return 0.5

def extract_keywords(topic: str) -> List[str]:
    """Extract relevant keywords from a topic."""
    try:
        # Simple keyword extraction - in production would use NLP
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = topic.lower().replace("#", "").split()
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        return keywords[:5]  # Return top 5 keywords

    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return [topic]

def generate_content_angles(topic: str) -> List[str]:
    """Generate content angles for a trending topic."""
    try:
        angles = [
            f"Breaking: {topic}",
            f"Analysis: {topic}",
            f"Impact of {topic} on Business",
            f"How {topic} Changes the Industry",
            f"Expert Opinion: {topic}"
        ]
        return angles

    except Exception as e:
        logger.error(f"Error generating content angles: {str(e)}")
        return [f"Analysis: {topic}"]

async def cache_current_trends(trends: List[TrendSignal]):
    """Cache current trends in Redis for fast access."""
    try:
        if not REDIS_AVAILABLE:
            return

        trends_data = []
        for trend in trends:
            trends_data.append({
                "topic": trend.topic,
                "signal_strength": trend.signal_strength,
                "velocity": trend.velocity,
                "volume": trend.volume,
                "source": trend.source,
                "timestamp": trend.timestamp.isoformat()
            })

        redis_client.setex("current_trends", 300, json.dumps(trends_data, default=str))  # 5 minute cache
        logger.info(f"Cached {len(trends_data)} trends")

    except Exception as e:
        logger.error(f"Error caching trends: {str(e)}")

# Dashboard endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Real-Time Trend Monitor dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-Time Trend Monitor Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
            .header { background: linear-gradient(135deg, #17a2b8 0%, #138496 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
            .stat { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stat h3 { margin: 0; font-size: 2em; color: #17a2b8; }
            .sources { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }
            .source { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .trends { margin-top: 20px; }
            .trend { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .button { background: #17a2b8; color: white; padding: 12px 24px; border: none; border-radius: 8px; margin: 8px; cursor: pointer; font-weight: bold; }
            .button:hover { background: #138496; }
            .signal-strength { padding: 4px 12px; border-radius: 20px; font-size: 12px; color: white; font-weight: bold; }
            .signal-strength.high { background: #28a745; }
            .signal-strength.medium { background: #ffc107; color: #000; }
            .signal-strength.low { background: #dc3545; }
            .source-status { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .source-status.active { background: #d4edda; color: #155724; }
            .source-status.error { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📡 Real-Time Trend Monitor</h1>
            <p>Multi-source trend monitoring for rapid trend identification</p>
        </div>

        <div class="stats">
            <div class="stat">
                <h3 id="active-signals">0</h3>
                <p>Active Signals</p>
            </div>
            <div class="stat">
                <h3 id="sources-online">0/4</h3>
                <p>Sources Online</p>
            </div>
            <div class="stat">
                <h3 id="trends-identified">0</h3>
                <p>Trends Identified</p>
            </div>
            <div class="stat">
                <h3 id="avg-velocity">0.0</h3>
                <p>Avg Velocity</p>
            </div>
        </div>

        <div>
            <h2>🔍 Quick Actions</h2>
            <button class="button" onclick="startMonitoring()">Start Monitoring</button>
            <button class="button" onclick="getCurrentTrends()">Get Current Trends</button>
            <button class="button" onclick="checkSources()">Check Source Status</button>
            <button class="button" onclick="refreshDashboard()">Refresh Dashboard</button>
        </div>

        <div class="sources">
            <div class="source">
                <h3>📊 Google Trends</h3>
                <p>Status: <span class="source-status active" id="google-status">ACTIVE</span></p>
                <p>Weight: 0.9 | Frequency: 5min</p>
                <p>Last Check: <span id="google-last-check">2 minutes ago</span></p>
            </div>
            <div class="source">
                <h3>🔥 Reddit Trends</h3>
                <p>Status: <span class="source-status active" id="reddit-status">ACTIVE</span></p>
                <p>Weight: 0.7 | Frequency: 3min</p>
                <p>Last Check: <span id="reddit-last-check">1 minute ago</span></p>
            </div>
            <div class="source">
                <h3>📰 News Monitor</h3>
                <p>Status: <span class="source-status active" id="news-status">ACTIVE</span></p>
                <p>Weight: 0.8 | Frequency: 10min</p>
                <p>Last Check: <span id="news-last-check">5 minutes ago</span></p>
            </div>
            <div class="source">
                <h3>🐦 Social Listening</h3>
                <p>Status: <span class="source-status active" id="social-status">ACTIVE</span></p>
                <p>Weight: 0.6 | Frequency: 2min</p>
                <p>Last Check: <span id="social-last-check">30 seconds ago</span></p>
            </div>
        </div>

        <div class="trends">
            <h2>🚀 Current Trending Topics</h2>
            <div id="trends-list">Loading trending topics...</div>
        </div>

        <script>
            async function startMonitoring() {
                try {
                    const config = {
                        sources_enabled: ["google_trends", "reddit_trends", "news_monitoring", "social_listening"],
                        monitoring_interval: 5,
                        trend_threshold: 0.6,
                        velocity_threshold: 0.3,
                        categories: ["seo_tools", "ai_platforms", "digital_marketing", "content_creation"]
                    };

                    const response = await fetch('/start-monitoring', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(config)
                    });
                    const result = await response.json();
                    alert('Monitoring started successfully!\\nSources: ' + result.sources_enabled.join(', ') + '\\nInterval: ' + result.monitoring_interval + ' minutes');
                } catch (error) {
                    alert('Error starting monitoring: ' + error.message);
                }
            }

            async function getCurrentTrends() {
                try {
                    const response = await fetch('/current-trends?limit=10');
                    const result = await response.json();

                    let trendsList = 'Current Trending Topics:\\n\\n';
                    result.trending_topics.forEach((trend, index) => {
                        trendsList += `${index + 1}. ${trend.topic}\\n`;
                        trendsList += `   Signal: ${(trend.signal_strength * 100).toFixed(0)}% | Velocity: ${(trend.velocity * 100).toFixed(0)}%\\n`;
                        trendsList += `   Source: ${trend.source} | Volume: ${trend.volume}\\n\\n`;
                    });

                    alert(trendsList || 'No significant trends detected at this time.');
                } catch (error) {
                    alert('Error getting trends: ' + error.message);
                }
            }

            async function checkSources() {
                try {
                    const response = await fetch('/source-status');
                    const result = await response.json();

                    let statusReport = `Source Status Report:\\n\\n`;
                    statusReport += `Active Sources: ${result.active_sources}/${result.total_sources}\\n`;
                    statusReport += `Redis Cache: ${result.redis_available ? 'Available' : 'Unavailable'}\\n\\n`;

                    Object.entries(result.sources).forEach(([name, source]) => {
                        statusReport += `${source.name}: ${source.status.toUpperCase()}\\n`;
                        statusReport += `  Last check: ${source.minutes_since_last_check.toFixed(1)} min ago\\n\\n`;
                    });

                    alert(statusReport);
                } catch (error) {
                    alert('Error checking sources: ' + error.message);
                }
            }

            async function refreshDashboard() {
                try {
                    // Update stats
                    const trendsResponse = await fetch('/current-trends');
                    const trendsData = await trendsResponse.json();

                    document.getElementById('active-signals').textContent = trendsData.total_signals || 0;
                    document.getElementById('trends-identified').textContent = trendsData.filtered_signals || 0;

                    if (trendsData.trending_topics.length > 0) {
                        const avgVelocity = trendsData.trending_topics.reduce((sum, t) => sum + t.velocity, 0) / trendsData.trending_topics.length;
                        document.getElementById('avg-velocity').textContent = avgVelocity.toFixed(2);
                    }

                    // Update source status
                    const statusResponse = await fetch('/source-status');
                    const statusData = await statusResponse.json();
                    document.getElementById('sources-online').textContent = `${statusData.active_sources}/${statusData.total_sources}`;

                    // Update trends list
                    const trendsList = document.getElementById('trends-list');
                    trendsList.innerHTML = '';

                    trendsData.trending_topics.slice(0, 10).forEach(trend => {
                        const trendDiv = document.createElement('div');
                        trendDiv.className = 'trend';

                        const strengthClass = trend.signal_strength > 0.7 ? 'high' : (trend.signal_strength > 0.5 ? 'medium' : 'low');

                        trendDiv.innerHTML = `
                            <div>
                                <strong>${trend.topic}</strong><br>
                                <small>Source: ${trend.source} | Volume: ${trend.volume} | ${new Date(trend.timestamp).toLocaleTimeString()}</small>
                            </div>
                            <div>
                                <span class="signal-strength ${strengthClass}">${(trend.signal_strength * 100).toFixed(0)}%</span>
                                <small style="margin-left: 10px;">Velocity: ${(trend.velocity * 100).toFixed(0)}%</small>
                            </div>
                        `;
                        trendsList.appendChild(trendDiv);
                    });

                    if (trendsData.trending_topics.length === 0) {
                        trendsList.innerHTML = '<div class="trend">No significant trends detected at this time.</div>';
                    }

                } catch (error) {
                    console.error('Error refreshing dashboard:', error);
                    document.getElementById('trends-list').innerHTML = '<div class="trend">Error loading trend data</div>';
                }
            }

            // Auto-refresh dashboard every 30 seconds
            refreshDashboard();
            setInterval(refreshDashboard, 30000);
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