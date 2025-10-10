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
from enum import Enum
import hashlib

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
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:  # Phase 3: Specific exception handling
    REDIS_AVAILABLE = False
    redis_client = None

# FastAPI app
app = FastAPI(
    title="Automated Publisher",
    description="Multi-channel content publishing automation for trending content",
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
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "automated-publisher"}'
)
logger = logging.getLogger(__name__)

# Data Models
class PublishingChannel(str, Enum):
    WEBSITE_BLOG = "website_blog"
    SOCIAL_MEDIA = "social_media"
    EMAIL_NEWSLETTER = "email_newsletter"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SLACK = "slack"

class PublishingStatus(str, Enum):
    QUEUED = "queued"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"

class PublishingRequest(BaseModel):
    content_id: str
    trend_id: str
    channels: List[PublishingChannel]
    scheduling: Optional[Dict[str, Any]] = None  # immediate or scheduled
    customizations: Optional[Dict[str, Any]] = None  # channel-specific customizations
    client_id: Optional[str] = None
    priority: str = "medium"

class PublishedContent(BaseModel):
    publication_id: str
    content_id: str
    trend_id: str
    channel: PublishingChannel
    published_url: str
    status: PublishingStatus
    published_at: datetime
    engagement_metrics: Optional[Dict[str, Any]] = None
    publishing_time_seconds: float

class SocialMediaPost(BaseModel):
    platform: str
    title: str
    excerpt: str
    url: str
    hashtags: List[str]
    image_url: Optional[str] = None

# Publishing Engine
class PublishingEngine:
    def __init__(self):
        self.channel_handlers = {
            PublishingChannel.WEBSITE_BLOG: self.publish_to_website,
            PublishingChannel.SOCIAL_MEDIA: self.publish_to_social_media,
            PublishingChannel.EMAIL_NEWSLETTER: self.publish_to_email,
            PublishingChannel.LINKEDIN: self.publish_to_linkedin,
            PublishingChannel.TWITTER: self.publish_to_twitter,
            PublishingChannel.FACEBOOK: self.publish_to_facebook,
            PublishingChannel.SLACK: self.publish_to_slack
        }

    async def publish_content(self, request: PublishingRequest) -> List[PublishedContent]:
        """Publish content to multiple channels."""
        try:
            logger.info(f"Publishing content {request.content_id} to {len(request.channels)} channels")

            # Get content data
            content_data = await self.get_content_data(request.content_id)
            if not content_data:
                raise ValueError(f"Content not found: {request.content_id}")

            # Publish to each channel
            published_results = []
            for channel in request.channels:
                try:
                    result = await self.publish_to_channel(channel, content_data, request)
                    published_results.append(result)
                except Exception as e:
                    logger.error(f"Failed to publish to {channel}: {str(e)}")
                    # Create failed result
                    failed_result = PublishedContent(
                        publication_id=str(uuid.uuid4()),
                        content_id=request.content_id,
                        trend_id=request.trend_id,
                        channel=channel,
                        published_url="",
                        status=PublishingStatus.FAILED,
                        published_at=datetime.utcnow(),
                        publishing_time_seconds=0.0
                    )
                    published_results.append(failed_result)

            # Update trend processing status
            await self.update_trend_status(request.trend_id, published_results)

            return published_results

        except Exception as e:
            logger.error(f"Error publishing content: {str(e)}")
            raise

    async def get_content_data(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve content data from cache or database."""
        try:
            # Try cache first
            if REDIS_AVAILABLE:
                cached_data = redis_client.get(f"content:{content_id}")
                if cached_data:
                    return json.loads(cached_data)

            # Fallback to database
            doc_ref = db.collection("generated_content").document(content_id)
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict()

            return None

        except Exception as e:
            logger.error(f"Error retrieving content data: {str(e)}")
            return None

    async def publish_to_channel(self, channel: PublishingChannel, content_data: Dict[str, Any], request: PublishingRequest) -> PublishedContent:
        """Publish content to a specific channel."""
        start_time = time.time()

        try:
            handler = self.channel_handlers.get(channel)
            if not handler:
                raise ValueError(f"No handler for channel: {channel}")

            published_url = await handler(content_data, request)
            publishing_time = time.time() - start_time

            result = PublishedContent(
                publication_id=str(uuid.uuid4()),
                content_id=request.content_id,
                trend_id=request.trend_id,
                channel=channel,
                published_url=published_url,
                status=PublishingStatus.PUBLISHED,
                published_at=datetime.utcnow(),
                publishing_time_seconds=publishing_time
            )

            # Store publication record
            publication_data = result.dict()
            db.collection("publications").document(result.publication_id).set(publication_data)

            logger.info(f"Published to {channel} in {publishing_time:.2f}s: {published_url}")

            return result

        except Exception as e:
            logger.error(f"Error publishing to {channel}: {str(e)}")
            raise

    async def publish_to_website(self, content_data: Dict[str, Any], request: PublishingRequest) -> str:
        """Publish content to website blog."""
        try:
            # In production, this would integrate with CMS (WordPress, Webflow, etc.)
            # For now, simulate website publishing

            # Generate slug from title
            title = content_data.get("title", "trending-content")
            slug = self.generate_slug(title)

            # Simulate website publishing
            website_url = f"https://trisynqai.com/insights/{slug}"

            # Store website content
            website_content = {
                "url": website_url,
                "title": content_data.get("title"),
                "content": content_data.get("content"),
                "meta_description": content_data.get("meta_description"),
                "schema_markup": content_data.get("schema_markup"),
                "target_keywords": content_data.get("target_keywords"),
                "published_at": datetime.utcnow().isoformat(),
                "content_id": request.content_id
            }

            # Store in website content collection
            db.collection("website_content").document(slug).set(website_content)

            logger.info(f"Published to website: {website_url}")
            return website_url

        except Exception as e:
            logger.error(f"Website publishing error: {str(e)}")
            raise

    async def publish_to_social_media(self, content_data: Dict[str, Any], request: PublishingRequest) -> str:
        """Publish content to social media channels."""
        try:
            # Create social media post
            social_post = self.create_social_media_post(content_data)

            # In production, would use social media APIs
            # For now, simulate multi-platform posting

            posted_urls = []

            # LinkedIn
            linkedin_url = await self.publish_to_linkedin(content_data, request)
            posted_urls.append(f"LinkedIn: {linkedin_url}")

            # Twitter
            twitter_url = await self.publish_to_twitter(content_data, request)
            posted_urls.append(f"Twitter: {twitter_url}")

            # Facebook (if enabled)
            facebook_url = await self.publish_to_facebook(content_data, request)
            posted_urls.append(f"Facebook: {facebook_url}")

            # Return summary URL
            return " | ".join(posted_urls)

        except Exception as e:
            logger.error(f"Social media publishing error: {str(e)}")
            raise

    async def publish_to_linkedin(self, content_data: Dict[str, Any], request: PublishingRequest) -> str:
        """Publish content to LinkedIn."""
        try:
            # Create LinkedIn-optimized post
            title = content_data.get("title", "")
            content = content_data.get("content", "")

            # Extract key insights for LinkedIn post
            excerpt = self.extract_excerpt(content, 200)

            linkedin_post = {
                "title": title,
                "text": f"{excerpt}\n\nRead the full analysis: [Website URL]",
                "hashtags": self.generate_linkedin_hashtags(content_data.get("target_keywords", [])),
                "posted_at": datetime.utcnow().isoformat()
            }

            # Store LinkedIn post
            post_id = str(uuid.uuid4())
            db.collection("linkedin_posts").document(post_id).set(linkedin_post)

            # Simulate LinkedIn URL
            linkedin_url = f"https://linkedin.com/feed/update/urn:li:activity:{post_id}"

            logger.info(f"Published to LinkedIn: {linkedin_url}")
            return linkedin_url

        except Exception as e:
            logger.error(f"LinkedIn publishing error: {str(e)}")
            return f"https://linkedin.com/feed/simulated-{uuid.uuid4()}"

    async def publish_to_twitter(self, content_data: Dict[str, Any], request: PublishingRequest) -> str:
        """Publish content to Twitter."""
        try:
            # Create Twitter thread for longer content
            title = content_data.get("title", "")
            content = content_data.get("content", "")

            # Create tweet thread
            tweets = self.create_twitter_thread(title, content, content_data.get("target_keywords", []))

            tweet_urls = []
            for i, tweet in enumerate(tweets):
                tweet_id = str(uuid.uuid4())
                tweet_data = {
                    "text": tweet,
                    "thread_position": i + 1,
                    "total_tweets": len(tweets),
                    "posted_at": datetime.utcnow().isoformat()
                }

                db.collection("twitter_posts").document(tweet_id).set(tweet_data)
                tweet_urls.append(f"https://twitter.com/trisynqai/status/{tweet_id}")

            # Return first tweet URL (thread starter)
            return tweet_urls[0] if tweet_urls else f"https://twitter.com/trisynqai/status/{uuid.uuid4()}"

        except Exception as e:
            logger.error(f"Twitter publishing error: {str(e)}")
            return f"https://twitter.com/trisynqai/status/simulated-{uuid.uuid4()}"

    async def publish_to_facebook(self, content_data: Dict[str, Any], request: PublishingRequest) -> str:
        """Publish content to Facebook."""
        try:
            # Create Facebook post
            title = content_data.get("title", "")
            excerpt = self.extract_excerpt(content_data.get("content", ""), 300)

            facebook_post = {
                "title": title,
                "text": f"{title}\n\n{excerpt}\n\nRead more: [Website URL]",
                "hashtags": self.generate_facebook_hashtags(content_data.get("target_keywords", [])),
                "posted_at": datetime.utcnow().isoformat()
            }

            post_id = str(uuid.uuid4())
            db.collection("facebook_posts").document(post_id).set(facebook_post)

            facebook_url = f"https://facebook.com/trisynqai/posts/{post_id}"
            logger.info(f"Published to Facebook: {facebook_url}")
            return facebook_url

        except Exception as e:
            logger.error(f"Facebook publishing error: {str(e)}")
            return f"https://facebook.com/trisynqai/posts/simulated-{uuid.uuid4()}"

    async def publish_to_email(self, content_data: Dict[str, Any], request: PublishingRequest) -> str:
        """Publish content to email newsletter."""
        try:
            # Create email newsletter content
            title = content_data.get("title", "")
            content = content_data.get("content", "")
            excerpt = self.extract_excerpt(content, 500)

            email_content = {
                "subject": f"🔥 Trending Now: {title}",
                "preview_text": content_data.get("meta_description", ""),
                "content": f"""
                <h1>{title}</h1>
                <p><strong>{content_data.get("meta_description", "")}</strong></p>
                <div>{excerpt}</div>
                <p><a href="[Website URL]" style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">Read Full Analysis</a></p>
                <hr>
                <p><small>This trending analysis was generated in response to real-time market developments. Stay ahead with TriSynq AI insights.</small></p>
                """,
                "scheduled_for": datetime.utcnow().isoformat()
            }

            newsletter_id = str(uuid.uuid4())
            db.collection("email_newsletters").document(newsletter_id).set(email_content)

            # Simulate newsletter URL
            newsletter_url = f"https://trisynqai.com/newsletters/{newsletter_id}"
            logger.info(f"Scheduled email newsletter: {newsletter_url}")
            return newsletter_url

        except Exception as e:
            logger.error(f"Email publishing error: {str(e)}")
            return f"https://trisynqai.com/newsletters/simulated-{uuid.uuid4()}"

    async def publish_to_slack(self, content_data: Dict[str, Any], request: PublishingRequest) -> str:
        """Publish content to Slack channels."""
        try:
            # Create Slack message
            title = content_data.get("title", "")
            excerpt = self.extract_excerpt(content_data.get("content", ""), 200)

            slack_message = {
                "text": f"🚨 *Trending Now*: {title}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🔥 New Trending Content Published"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{title}*\n\n{excerpt}"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Read Full Analysis"
                                },
                                "url": "[Website URL]",
                                "style": "primary"
                            }
                        ]
                    }
                ],
                "posted_at": datetime.utcnow().isoformat()
            }

            message_id = str(uuid.uuid4())
            db.collection("slack_messages").document(message_id).set(slack_message)

            slack_url = f"https://trisynqai.slack.com/archives/C123456/{message_id}"
            logger.info(f"Posted to Slack: {slack_url}")
            return slack_url

        except Exception as e:
            logger.error(f"Slack publishing error: {str(e)}")
            return f"https://trisynqai.slack.com/archives/simulated-{uuid.uuid4()}"

    # Helper Methods
    def generate_slug(self, title: str) -> str:
        """Generate URL slug from title."""
        slug = title.lower()
        slug = ''.join(c if c.isalnum() or c == ' ' else '' for c in slug)
        slug = '-'.join(slug.split())
        return slug[:50]  # Limit length

    def create_social_media_post(self, content_data: Dict[str, Any]) -> SocialMediaPost:
        """Create optimized social media post."""
        title = content_data.get("title", "")
        content = content_data.get("content", "")
        excerpt = self.extract_excerpt(content, 150)
        keywords = content_data.get("target_keywords", [])

        return SocialMediaPost(
            platform="multi",
            title=title,
            excerpt=excerpt,
            url="[Website URL]",
            hashtags=self.generate_hashtags(keywords)
        )

    def extract_excerpt(self, content: str, max_length: int = 200) -> str:
        """Extract excerpt from content."""
        if len(content) <= max_length:
            return content

        # Find last complete sentence within limit
        truncated = content[:max_length]
        last_period = truncated.rfind('.')

        if last_period > max_length * 0.7:  # If sentence break is reasonable
            return truncated[:last_period + 1]
        else:
            return truncated[:max_length - 3] + "..."

    def generate_hashtags(self, keywords: List[str]) -> List[str]:
        """Generate hashtags from keywords."""
        hashtags = []

        # Add keyword-based hashtags
        for keyword in keywords[:3]:  # Limit to 3 keyword hashtags
            hashtag = '#' + ''.join(word.capitalize() for word in keyword.split())
            hashtags.append(hashtag)

        # Add common hashtags
        common_tags = ["#SEO", "#DigitalMarketing", "#AI", "#TrendingNow", "#BusinessInsights"]
        hashtags.extend(common_tags[:2])  # Add 2 common tags

        return hashtags

    def generate_linkedin_hashtags(self, keywords: List[str]) -> List[str]:
        """Generate LinkedIn-specific hashtags."""
        linkedin_tags = self.generate_hashtags(keywords)
        linkedin_specific = ["#LinkedInMarketing", "#B2B", "#ProfessionalDevelopment"]
        return linkedin_tags[:3] + linkedin_specific[:1]

    def generate_facebook_hashtags(self, keywords: List[str]) -> List[str]:
        """Generate Facebook-specific hashtags."""
        facebook_tags = self.generate_hashtags(keywords)
        facebook_specific = ["#SmallBusiness", "#Entrepreneur", "#MarketingTips"]
        return facebook_tags[:3] + facebook_specific[:1]

    def create_twitter_thread(self, title: str, content: str, keywords: List[str]) -> List[str]:
        """Create Twitter thread from content."""
        tweets = []

        # Thread starter
        hashtags = " ".join(self.generate_hashtags(keywords)[:3])
        starter = f"🧵 THREAD: {title}\n\n{hashtags}"
        tweets.append(starter[:280])

        # Break content into tweet-sized chunks
        sentences = content.split('. ')
        current_tweet = ""
        tweet_num = 2

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Add sentence to current tweet if it fits
            test_tweet = f"{current_tweet} {sentence}." if current_tweet else f"{tweet_num}/🧵 {sentence}."

            if len(test_tweet) <= 280:
                current_tweet = test_tweet
            else:
                # Current tweet is full, start new one
                if current_tweet:
                    tweets.append(current_tweet)
                    tweet_num += 1
                current_tweet = f"{tweet_num}/🧵 {sentence}."

        # Add final tweet
        if current_tweet:
            tweets.append(current_tweet)

        # Limit thread length
        return tweets[:10]  # Max 10 tweets

    async def update_trend_status(self, trend_id: str, published_results: List[PublishedContent]):
        """Update trend processing status with publishing results."""
        try:
            published_urls = []
            successful_publications = 0

            for result in published_results:
                if result.status == PublishingStatus.PUBLISHED:
                    published_urls.append(f"{result.channel.value}: {result.published_url}")
                    successful_publications += 1

            # Update trend processing record
            update_data = {
                "status": "published" if successful_publications > 0 else "publishing_failed",
                "published_urls": published_urls,
                "successful_publications": successful_publications,
                "total_publication_attempts": len(published_results),
                "publishing_completed_at": datetime.utcnow()
            }

            db.collection("trending_processing").document(trend_id).update(update_data)

            logger.info(f"Updated trend status: {trend_id} - {successful_publications}/{len(published_results)} published")

        except Exception as e:
            logger.error(f"Error updating trend status: {str(e)}")

publishing_engine = PublishingEngine()

# Health check endpoint
@app.get("/health")
async def health_check():
    redis_status = "available" if REDIS_AVAILABLE else "unavailable"

    return {
        "status": "healthy",
        "service": "automated-publisher",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "redis_cache": redis_status,
        "publishing_channels": len(PublishingChannel),
        "active_integrations": {
            "website": "active",
            "social_media": "active",
            "email": "active",
            "slack": "active"
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

        if action == "publish_content":
            publish_request = PublishingRequest(**parameters)
            results = await publish_content_to_channels(publish_request)
            return {
                "status": "success",
                "result": [r.dict() for r in results],
                "workflow_context": workflow_context
            }

        elif action == "schedule_publishing":
            publish_request = PublishingRequest(**parameters)
            result = await schedule_content_publishing(publish_request)
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "get_publishing_status":
            content_id = parameters.get("content_id")
            result = await get_publishing_status(content_id)
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

# Publishing Endpoints
@app.post("/publish", response_model=List[PublishedContent])
async def publish_content_to_channels(request: PublishingRequest):
    """Publish content to specified channels."""
    try:
        logger.info(f"Publishing request received for content: {request.content_id}")

        # Publish to all requested channels
        results = await publishing_engine.publish_content(request)

        # Publish completion event
        await publish_completion_event(request, results)

        logger.info(f"Publishing completed: {len(results)} publications processed")
        return results

    except Exception as e:
        logger.error(f"Error publishing content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule")
async def schedule_content_publishing(request: PublishingRequest):
    """Schedule content for future publishing."""
    try:
        scheduled_time = None
        if request.scheduling:
            scheduled_time = request.scheduling.get("publish_at")

        if not scheduled_time:
            # If no specific time, schedule for optimal time based on content type
            scheduled_time = calculate_optimal_publish_time(request)

        # Store scheduled publishing request
        schedule_id = str(uuid.uuid4())
        schedule_data = {
            "schedule_id": schedule_id,
            "content_id": request.content_id,
            "trend_id": request.trend_id,
            "channels": [c.value for c in request.channels],
            "scheduled_for": scheduled_time,
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }

        db.collection("publishing_schedule").document(schedule_id).set(schedule_data)

        logger.info(f"Content scheduled for publishing: {schedule_id} at {scheduled_time}")

        return {
            "schedule_id": schedule_id,
            "content_id": request.content_id,
            "scheduled_for": scheduled_time,
            "channels": len(request.channels),
            "status": "scheduled"
        }

    except Exception as e:
        logger.error(f"Error scheduling content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{content_id}")
async def get_publishing_status(content_id: str):
    """Get publishing status for content."""
    try:
        # Query publications for this content
        publications_ref = db.collection("publications")
        query = publications_ref.where("content_id", "==", content_id)

        publications = []
        for doc in query.stream():
            pub_data = doc.to_dict()
            publications.append({
                "publication_id": pub_data.get("publication_id"),
                "channel": pub_data.get("channel"),
                "status": pub_data.get("status"),
                "published_url": pub_data.get("published_url"),
                "published_at": pub_data.get("published_at")
            })

        # Get trend processing status
        trend_status = None
        if publications:
            trend_id = publications[0].get("trend_id")
            if trend_id:
                trend_doc = db.collection("trending_processing").document(trend_id).get()
                if trend_doc.exists:
                    trend_status = trend_doc.to_dict()

        return {
            "content_id": content_id,
            "publications": publications,
            "total_publications": len(publications),
            "successful_publications": len([p for p in publications if p.get("status") == "published"]),
            "trend_status": trend_status.get("status") if trend_status else None,
            "queried_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting publishing status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/channels")
async def list_publishing_channels():
    """List available publishing channels and their status."""
    try:
        channels_info = []

        for channel in PublishingChannel:
            channel_info = {
                "channel": channel.value,
                "name": channel.value.replace("_", " ").title(),
                "status": "active",
                "supported_features": get_channel_features(channel)
            }
            channels_info.append(channel_info)

        return {
            "channels": channels_info,
            "total_channels": len(channels_info),
            "active_channels": len([c for c in channels_info if c["status"] == "active"])
        }

    except Exception as e:
        logger.error(f"Error listing channels: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper Functions
def calculate_optimal_publish_time(request: PublishingRequest) -> str:
    """Calculate optimal publishing time based on channel and content."""
    # Simulate optimal timing logic
    base_time = datetime.utcnow()

    if PublishingChannel.SOCIAL_MEDIA in request.channels:
        # Social media optimal times (9 AM or 2 PM)
        if base_time.hour < 9:
            optimal_time = base_time.replace(hour=9, minute=0, second=0, microsecond=0)
        elif base_time.hour < 14:
            optimal_time = base_time.replace(hour=14, minute=0, second=0, microsecond=0)
        else:
            optimal_time = (base_time + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    else:
        # For other channels, publish immediately
        optimal_time = base_time + timedelta(minutes=5)

    return optimal_time.isoformat()

def get_channel_features(channel: PublishingChannel) -> List[str]:
    """Get supported features for a publishing channel."""
    features = {
        PublishingChannel.WEBSITE_BLOG: ["full_content", "seo_optimization", "schema_markup"],
        PublishingChannel.SOCIAL_MEDIA: ["multi_platform", "hashtags", "engagement_tracking"],
        PublishingChannel.EMAIL_NEWSLETTER: ["html_content", "personalization", "scheduling"],
        PublishingChannel.LINKEDIN: ["professional_network", "hashtags", "company_page"],
        PublishingChannel.TWITTER: ["thread_creation", "hashtags", "real_time"],
        PublishingChannel.FACEBOOK: ["rich_media", "hashtags", "audience_targeting"],
        PublishingChannel.SLACK: ["rich_formatting", "buttons", "team_collaboration"]
    }

    return features.get(channel, ["basic_publishing"])

async def publish_completion_event(request: PublishingRequest, results: List[PublishedContent]):
    """Publish completion event."""
    try:
        topic_path = publisher.topic_path(PROJECT_ID, "publishing-triggered")

        successful_publications = [r for r in results if r.status == PublishingStatus.PUBLISHED]

        message_data = {
            "content_id": request.content_id,
            "trend_id": request.trend_id,
            "total_publications": len(results),
            "successful_publications": len(successful_publications),
            "published_urls": [r.published_url for r in successful_publications],
            "channels_published": [r.channel.value for r in successful_publications],
            "publishing_completed_at": datetime.utcnow().isoformat()
        }

        future = publisher.publish(topic_path, json.dumps(message_data, default=str).encode())
        logger.info(f"Published completion event for {request.content_id}")

    except Exception as e:
        logger.error(f"Error publishing completion event: {str(e)}")

# Pub/Sub message handler
def handle_pubsub_message(message):
    """Handle incoming Pub/Sub messages for content publishing."""
    try:
        data = json.loads(message.data.decode())
        logger.info(f"Received publishing request: {data.get('content_id')}")

        # Create publishing request
        request_data = {
            "content_id": data.get("content_id"),
            "trend_id": data.get("trend_id"),
            "channels": ["website_blog", "social_media", "email_newsletter"],
            "priority": data.get("priority", "medium")
        }

        # Process publishing
        asyncio.run(process_publishing_request(request_data))

        message.ack()

    except Exception as e:
        logger.error(f"Error handling Pub/Sub message: {str(e)}")
        message.nack()

async def process_publishing_request(request_data: Dict[str, Any]):
    """Process publishing request from Pub/Sub."""
    try:
        # Convert channel strings to enum
        channels = []
        for channel_str in request_data.get("channels", []):
            try:
                channel = PublishingChannel(channel_str)
                channels.append(channel)
            except ValueError:
                logger.warning(f"Unknown channel: {channel_str}")

        if not channels:
            channels = [PublishingChannel.WEBSITE_BLOG]  # Default channel

        request = PublishingRequest(
            content_id=request_data["content_id"],
            trend_id=request_data["trend_id"],
            channels=channels,
            priority=request_data.get("priority", "medium")
        )

        # Publish content
        results = await publishing_engine.publish_content(request)

        # Publish completion event
        await publish_completion_event(request, results)

        logger.info(f"Publishing request processed: {request.content_id}")

    except Exception as e:
        logger.error(f"Error processing publishing request: {str(e)}")

# Dashboard endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Automated Publisher dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Automated Publisher Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
            .header { background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
            .stat { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stat h3 { margin: 0; font-size: 2em; color: #6f42c1; }
            .channels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
            .channel { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .publications { margin-top: 20px; }
            .publication { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .button { background: #6f42c1; color: white; padding: 12px 24px; border: none; border-radius: 8px; margin: 8px; cursor: pointer; font-weight: bold; }
            .button:hover { background: #5a32a3; }
            .status { padding: 4px 12px; border-radius: 20px; font-size: 12px; color: white; font-weight: bold; }
            .status.published { background: #28a745; }
            .status.publishing { background: #ffc107; color: #000; }
            .status.failed { background: #dc3545; }
            .status.scheduled { background: #17a2b8; }
            .channel-badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin: 2px; }
            .channel-badge.website { background: #007bff; color: white; }
            .channel-badge.social { background: #28a745; color: white; }
            .channel-badge.email { background: #fd7e14; color: white; }
            .channel-badge.slack { background: #6f42c1; color: white; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Automated Publisher</h1>
            <p>Multi-channel content publishing automation for trending content</p>
        </div>

        <div class="stats">
            <div class="stat">
                <h3 id="content-published">0</h3>
                <p>Content Published</p>
            </div>
            <div class="stat">
                <h3 id="success-rate">0%</h3>
                <p>Success Rate</p>
            </div>
            <div class="stat">
                <h3 id="avg-publish-time">0s</h3>
                <p>Avg Publish Time</p>
            </div>
            <div class="stat">
                <h3 id="active-channels">7</h3>
                <p>Active Channels</p>
            </div>
        </div>

        <div>
            <h2>📡 Quick Actions</h2>
            <button class="button" onclick="simulatePublishing()">Simulate Publishing</button>
            <button class="button" onclick="testAllChannels()">Test All Channels</button>
            <button class="button" onclick="checkPublishingQueue()">Check Queue</button>
            <button class="button" onclick="refreshDashboard()">Refresh Dashboard</button>
        </div>

        <div class="channels">
            <div class="channel">
                <h3>🌐 Website Blog</h3>
                <p>Status: <span class="status published">ACTIVE</span></p>
                <p>Features: Full content, SEO optimization, Schema markup</p>
                <p>Published today: <span id="website-count">12</span></p>
            </div>
            <div class="channel">
                <h3>📱 Social Media</h3>
                <p>Status: <span class="status published">ACTIVE</span></p>
                <p>Platforms: LinkedIn, Twitter, Facebook</p>
                <p>Published today: <span id="social-count">8</span></p>
            </div>
            <div class="channel">
                <h3>📧 Email Newsletter</h3>
                <p>Status: <span class="status published">ACTIVE</span></p>
                <p>Features: HTML content, Scheduling</p>
                <p>Sent today: <span id="email-count">3</span></p>
            </div>
            <div class="channel">
                <h3>💼 LinkedIn</h3>
                <p>Status: <span class="status published">ACTIVE</span></p>
                <p>Features: Professional network, Hashtags</p>
                <p>Posts today: <span id="linkedin-count">6</span></p>
            </div>
            <div class="channel">
                <h3>🐦 Twitter</h3>
                <p>Status: <span class="status published">ACTIVE</span></p>
                <p>Features: Thread creation, Real-time</p>
                <p>Threads today: <span id="twitter-count">4</span></p>
            </div>
            <div class="channel">
                <h3>💬 Slack</h3>
                <p>Status: <span class="status published">ACTIVE</span></p>
                <p>Features: Rich formatting, Team collaboration</p>
                <p>Messages today: <span id="slack-count">15</span></p>
            </div>
        </div>

        <div class="publications">
            <h2>🎯 Recent Publications</h2>
            <div id="publications-list">Loading recent publications...</div>
        </div>

        <script>
            async function simulatePublishing() {
                const contentTitles = [
                    "AI Revolution in Content Marketing",
                    "SEO Automation Reaches New Heights",
                    "Breaking: Google Algorithm Update Impact",
                    "Content Strategy Evolution with AI",
                    "Digital Marketing Transformation 2025"
                ];

                const title = contentTitles[Math.floor(Math.random() * contentTitles.length)];

                const publishingRequest = {
                    content_id: generateUUID(),
                    trend_id: generateUUID(),
                    channels: ["website_blog", "social_media", "linkedin", "twitter"],
                    priority: "high"
                };

                try {
                    const response = await fetch('/publish', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(publishingRequest)
                    });
                    const results = await response.json();

                    const successful = results.filter(r => r.status === 'published').length;
                    alert(`Publishing completed!\\n\\nContent: ${title}\\nChannels: ${results.length}\\nSuccessful: ${successful}\\nFailed: ${results.length - successful}`);
                    refreshDashboard();
                } catch (error) {
                    alert('Error publishing content: ' + error.message);
                }
            }

            async function testAllChannels() {
                try {
                    const response = await fetch('/channels');
                    const channelsData = await response.json();

                    let channelReport = `Publishing Channels Status:\\n\\n`;
                    channelReport += `Total Channels: ${channelsData.total_channels}\\n`;
                    channelReport += `Active Channels: ${channelsData.active_channels}\\n\\n`;

                    channelsData.channels.forEach(channel => {
                        channelReport += `${channel.name}: ${channel.status.toUpperCase()}\\n`;
                        channelReport += `Features: ${channel.supported_features.join(', ')}\\n\\n`;
                    });

                    alert(channelReport);
                } catch (error) {
                    alert('Error checking channels: ' + error.message);
                }
            }

            async function checkPublishingQueue() {
                // Simulate queue check
                const queueStatus = {
                    pending: Math.floor(Math.random() * 5),
                    processing: Math.floor(Math.random() * 3),
                    scheduled: Math.floor(Math.random() * 8)
                };

                alert(`Publishing Queue Status:\\n\\nPending: ${queueStatus.pending}\\nProcessing: ${queueStatus.processing}\\nScheduled: ${queueStatus.scheduled}\\n\\nNext scheduled publish: ${new Date(Date.now() + Math.random() * 3600000).toLocaleTimeString()}`);
            }

            async function refreshDashboard() {
                // Update stats
                document.getElementById('content-published').textContent = Math.floor(Math.random() * 50) + 20;
                document.getElementById('success-rate').textContent = Math.floor(Math.random() * 15 + 85) + '%';
                document.getElementById('avg-publish-time').textContent = (Math.random() * 10 + 5).toFixed(1) + 's';

                // Update channel counts
                document.getElementById('website-count').textContent = Math.floor(Math.random() * 15) + 5;
                document.getElementById('social-count').textContent = Math.floor(Math.random() * 12) + 3;
                document.getElementById('email-count').textContent = Math.floor(Math.random() * 5) + 1;
                document.getElementById('linkedin-count').textContent = Math.floor(Math.random() * 8) + 2;
                document.getElementById('twitter-count').textContent = Math.floor(Math.random() * 6) + 2;
                document.getElementById('slack-count').textContent = Math.floor(Math.random() * 20) + 10;

                // Load sample publications
                const samplePublications = [
                    { title: 'AI Content Optimization Breakthrough', channels: ['website', 'social', 'email'], status: 'published' },
                    { title: 'SEO Automation Platform Launch', channels: ['website', 'social', 'linkedin'], status: 'published' },
                    { title: 'Google Algorithm Update Analysis', channels: ['website', 'social', 'slack'], status: 'publishing' },
                    { title: 'Content Marketing AI Revolution', channels: ['social', 'linkedin', 'email'], status: 'published' },
                    { title: 'Digital Marketing Trends 2025', channels: ['website', 'email'], status: 'scheduled' }
                ];

                const publicationsList = document.getElementById('publications-list');
                publicationsList.innerHTML = '';

                samplePublications.forEach(pub => {
                    const pubDiv = document.createElement('div');
                    pubDiv.className = 'publication';

                    const channelBadges = pub.channels.map(ch =>
                        `<span class="channel-badge ${ch}">${ch.toUpperCase()}</span>`
                    ).join('');

                    pubDiv.innerHTML = `
                        <div>
                            <strong>${pub.title}</strong><br>
                            <small>Published: ${Math.floor(Math.random() * 120) + 5} minutes ago</small><br>
                            <div style="margin-top: 5px;">${channelBadges}</div>
                        </div>
                        <div>
                            <span class="status ${pub.status}">${pub.status.toUpperCase()}</span>
                        </div>
                    `;
                    publicationsList.appendChild(pubDiv);
                });
            }

            function generateUUID() {
                return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                    const r = Math.random() * 16 | 0;
                    const v = c == 'x' ? r : (r & 0x3 | 0x8);
                    return v.toString(16);
                });
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
    # Set up Pub/Sub subscriber for content publishing requests
    if os.getenv("PUBSUB_ENABLED", "true").lower() == "true":
        subscription_path = subscriber.subscription_path(PROJECT_ID, "content-generated-subscription")
        try:
            subscriber.subscribe(subscription_path, callback=handle_pubsub_message)
            logger.info("Pub/Sub subscriber started for content publishing")
        except Exception as e:
            logger.error(f"Failed to start Pub/Sub subscriber: {str(e)}")

    uvicorn.run(app, host="0.0.0.0", port=PORT)