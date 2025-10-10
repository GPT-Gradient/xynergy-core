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
import re
import hashlib

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

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
    title="Rapid Content Generator",
    description="Lightning-fast content generation for trending topics",
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
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "rapid-content-generator"}'
)
logger = logging.getLogger(__name__)

# Data Models
class ContentType(str, Enum):
    BLOG_POST = "blog_post"
    ANALYSIS_ARTICLE = "analysis_article"
    BREAKING_NEWS = "breaking_news"
    HOW_TO_GUIDE = "how_to_guide"
    OPINION_PIECE = "opinion_piece"
    CASE_STUDY = "case_study"

class ContentPriority(str, Enum):
    CRITICAL = "critical"    # 15 minutes
    HIGH = "high"           # 30 minutes
    MEDIUM = "medium"       # 60 minutes
    LOW = "low"            # 120 minutes

class ContentBrief(BaseModel):
    brief_id: str
    trend_id: str
    trend_topic: str
    content_type: ContentType
    priority: ContentPriority
    target_keywords: List[str]
    content_angle: str
    unique_perspective: str
    seo_requirements: Dict[str, Any]
    target_word_count: int
    deadline: datetime
    client_id: Optional[str] = None
    business_context: str = ""

class GeneratedContent(BaseModel):
    content_id: str
    brief_id: str
    trend_id: str
    title: str
    content: str
    meta_description: str
    target_keywords: List[str]
    schema_markup: Dict[str, Any]
    readability_score: float
    seo_score: float
    word_count: int
    generated_at: datetime
    generation_time_seconds: float

# Content Templates
class ContentTemplate:
    def __init__(self, template_type: ContentType):
        self.template_type = template_type
        self.templates = self.load_templates()

    def load_templates(self) -> Dict[str, str]:
        """Load content templates for different content types."""
        return {
            ContentType.BLOG_POST: """
# {title}

{meta_description}

## Introduction

{trend_topic} has been making waves in the industry, and it's crucial for businesses to understand its implications. In this analysis, we'll explore {content_angle} and what it means for your organization.

## The Trend: {trend_topic}

{trend_analysis}

### Key Insights:
{key_insights}

## Business Impact

{business_impact}

### Opportunities:
{opportunities}

### Challenges:
{challenges}

## Strategic Recommendations

{strategic_recommendations}

## What This Means for Your Business

{business_implications}

## Conclusion

{conclusion}

---

*This analysis was generated in response to emerging trends in {business_context}. Stay ahead of the curve with our AI-powered trend analysis.*
""",

            ContentType.BREAKING_NEWS: """
# BREAKING: {title}

**{meta_description}**

## What's Happening

{trend_topic} is rapidly gaining attention across the industry. Here's what you need to know:

{breaking_news_summary}

## Key Details

{key_details}

## Industry Impact

{industry_impact}

## What Experts Are Saying

{expert_opinions}

## What Happens Next

{future_implications}

## Bottom Line

{bottom_line}

---

*Breaking news coverage powered by real-time trend monitoring. Get the latest insights delivered to your inbox.*
""",

            ContentType.ANALYSIS_ARTICLE: """
# {title}: A Deep Dive Analysis

{meta_description}

## Executive Summary

{executive_summary}

## Background: Understanding {trend_topic}

{background_analysis}

## Data & Trends

{data_analysis}

### Key Metrics:
{key_metrics}

## Competitive Landscape

{competitive_analysis}

## Market Implications

{market_implications}

### Short-term Impact (0-6 months):
{short_term_impact}

### Long-term Impact (6+ months):
{long_term_impact}

## Strategic Recommendations

{strategic_recommendations}

### For SMBs:
{smb_recommendations}

### For Enterprises:
{enterprise_recommendations}

## Conclusion

{conclusion}

---

*Comprehensive analysis powered by AI-driven market intelligence. Subscribe for weekly trend reports.*
""",

            ContentType.HOW_TO_GUIDE: """
# How to Leverage {trend_topic} for Your Business

{meta_description}

## Why {trend_topic} Matters Right Now

{trend_importance}

## Getting Started: 5 Simple Steps

### Step 1: Assess Your Current Position
{step_1_details}

### Step 2: Identify Opportunities
{step_2_details}

### Step 3: Develop Your Strategy
{step_3_details}

### Step 4: Implement Solutions
{step_4_details}

### Step 5: Monitor and Optimize
{step_5_details}

## Tools and Resources

{tools_and_resources}

## Common Mistakes to Avoid

{common_mistakes}

## Measuring Success

{success_metrics}

## Next Steps

{next_steps}

---

*Practical guides for navigating emerging trends. Get actionable insights delivered weekly.*
"""
        }

# AI Content Generation Engine
class AIContentEngine:
    def __init__(self):
        self.openai_available = bool(OPENAI_API_KEY)
        self.perplexity_available = bool(PERPLEXITY_API_KEY)

    async def generate_content(self, brief: ContentBrief) -> GeneratedContent:
        """Generate content based on content brief."""
        start_time = time.time()

        try:
            logger.info(f"Generating content for trend: {brief.trend_topic}")

            # Get template
            template_engine = ContentTemplate(brief.content_type)
            base_template = template_engine.templates.get(brief.content_type, "")

            # Research the topic
            research_data = await self.research_topic(brief.trend_topic, brief.target_keywords)

            # Generate content sections
            content_sections = await self.generate_content_sections(brief, research_data)

            # Populate template
            populated_content = self.populate_template(base_template, content_sections, brief)

            # Generate SEO elements
            seo_elements = await self.generate_seo_elements(brief, populated_content)

            # Calculate metrics
            word_count = len(populated_content.split())
            readability_score = self.calculate_readability_score(populated_content)
            seo_score = self.calculate_seo_score(populated_content, brief.target_keywords)

            generation_time = time.time() - start_time

            generated_content = GeneratedContent(
                content_id=str(uuid.uuid4()),
                brief_id=brief.brief_id,
                trend_id=brief.trend_id,
                title=seo_elements["title"],
                content=populated_content,
                meta_description=seo_elements["meta_description"],
                target_keywords=brief.target_keywords,
                schema_markup=seo_elements["schema_markup"],
                readability_score=readability_score,
                seo_score=seo_score,
                word_count=word_count,
                generated_at=datetime.utcnow(),
                generation_time_seconds=generation_time
            )

            logger.info(f"Content generated successfully in {generation_time:.2f}s: {word_count} words")
            return generated_content

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise

    async def research_topic(self, topic: str, keywords: List[str]) -> Dict[str, Any]:
        """Research topic using available AI services."""
        try:
            research_data = {
                "topic_analysis": "",
                "key_insights": [],
                "business_context": "",
                "competitive_landscape": "",
                "expert_opinions": [],
                "data_points": []
            }

            # Use Perplexity for real-time research if available
            if self.perplexity_available:
                perplexity_research = await self.research_with_perplexity(topic, keywords)
                research_data.update(perplexity_research)
            else:
                # Fallback to simulated research
                research_data = await self.simulate_research(topic, keywords)

            return research_data

        except Exception as e:
            logger.error(f"Error researching topic: {str(e)}")
            return await self.simulate_research(topic, keywords)

    async def research_with_perplexity(self, topic: str, keywords: List[str]) -> Dict[str, Any]:
        """Research using Perplexity API for real-time insights."""
        try:
            headers = {
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }

            research_queries = [
                f"What are the latest developments in {topic}? Provide key insights and business implications.",
                f"How is {topic} impacting the industry? Include expert opinions and market analysis.",
                f"What are the competitive advantages of {topic}? Include data and case studies."
            ]

            research_results = []

            async with aiohttp.ClientSession() as session:
                for query in research_queries:
                    payload = {
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a business analyst providing detailed insights on emerging trends. Focus on actionable business intelligence."
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ],
                        "temperature": 0.2,
                        "max_tokens": 1000
                    }

                    async with session.post("https://api.perplexity.ai/chat/completions",
                                          headers=headers, json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                            research_results.append(content)

            return {
                "topic_analysis": research_results[0] if len(research_results) > 0 else "",
                "business_context": research_results[1] if len(research_results) > 1 else "",
                "competitive_landscape": research_results[2] if len(research_results) > 2 else "",
                "key_insights": [f"Insight {i+1}: {r[:100]}..." for i, r in enumerate(research_results[:3])],
                "expert_opinions": ["Industry experts highlight the growing importance of this trend"],
                "data_points": ["Trend gaining 40%+ search volume", "Industry adoption increasing rapidly"]
            }

        except Exception as e:
            logger.error(f"Perplexity research error: {str(e)}")
            return await self.simulate_research(topic, keywords)

    async def simulate_research(self, topic: str, keywords: List[str]) -> Dict[str, Any]:
        """Simulate research data for content generation."""
        return {
            "topic_analysis": f"{topic} represents a significant shift in the industry landscape, offering new opportunities for businesses to enhance their operations and competitive positioning.",
            "key_insights": [
                f"{topic} is experiencing rapid adoption across multiple industries",
                f"Early adopters are seeing significant competitive advantages",
                f"Integration challenges remain but solutions are emerging",
                f"ROI projections show positive outcomes within 6-12 months"
            ],
            "business_context": f"Organizations are increasingly recognizing {topic} as a strategic imperative for maintaining competitive advantage in today's rapidly evolving market.",
            "competitive_landscape": f"Market leaders are already implementing {topic} solutions, creating pressure for others to follow suit or risk falling behind.",
            "expert_opinions": [
                "Industry analysts predict continued growth and innovation in this space",
                "Early adopters report improved efficiency and customer satisfaction",
                "Technology providers are expanding their offerings to meet demand"
            ],
            "data_points": [
                "Search volume increased by 45% in the past month",
                "Industry mentions up 60% across social media platforms",
                "Investment in related solutions growing at 30% annually"
            ]
        }

    async def generate_content_sections(self, brief: ContentBrief, research_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate specific content sections based on research."""
        try:
            sections = {}

            if brief.content_type == ContentType.BLOG_POST:
                sections = {
                    "trend_analysis": research_data.get("topic_analysis", ""),
                    "key_insights": "\n".join([f"• {insight}" for insight in research_data.get("key_insights", [])]),
                    "business_impact": research_data.get("business_context", ""),
                    "opportunities": "• Enhanced operational efficiency\n• Competitive differentiation\n• Improved customer experience\n• New revenue streams",
                    "challenges": "• Implementation complexity\n• Resource requirements\n• Change management\n• Technical integration",
                    "strategic_recommendations": f"Organizations should evaluate {brief.trend_topic} for strategic fit and begin pilot implementations to gain early experience.",
                    "business_implications": f"The emergence of {brief.trend_topic} creates both opportunities and imperatives for businesses to adapt their strategies.",
                    "conclusion": f"As {brief.trend_topic} continues to evolve, proactive organizations will benefit from early engagement and strategic implementation."
                }

            elif brief.content_type == ContentType.BREAKING_NEWS:
                sections = {
                    "breaking_news_summary": research_data.get("topic_analysis", ""),
                    "key_details": "\n".join([f"• {point}" for point in research_data.get("data_points", [])]),
                    "industry_impact": research_data.get("business_context", ""),
                    "expert_opinions": "\n".join([f"• {opinion}" for opinion in research_data.get("expert_opinions", [])]),
                    "future_implications": f"This development in {brief.trend_topic} is expected to accelerate adoption across the industry.",
                    "bottom_line": f"Organizations should monitor {brief.trend_topic} developments closely and assess strategic implications."
                }

            elif brief.content_type == ContentType.ANALYSIS_ARTICLE:
                sections = {
                    "executive_summary": f"Analysis of {brief.trend_topic} reveals significant implications for industry stakeholders and strategic decision-making.",
                    "background_analysis": research_data.get("topic_analysis", ""),
                    "data_analysis": research_data.get("competitive_landscape", ""),
                    "key_metrics": "\n".join([f"• {metric}" for metric in research_data.get("data_points", [])]),
                    "competitive_analysis": research_data.get("competitive_landscape", ""),
                    "market_implications": research_data.get("business_context", ""),
                    "short_term_impact": f"Immediate effects of {brief.trend_topic} include increased market attention and early adopter advantages.",
                    "long_term_impact": f"Long-term implications suggest {brief.trend_topic} will become a standard industry practice.",
                    "strategic_recommendations": f"Organizations should develop {brief.trend_topic} capabilities to maintain competitive positioning.",
                    "smb_recommendations": "• Start with pilot implementations\n• Focus on high-impact use cases\n• Leverage cloud-based solutions",
                    "enterprise_recommendations": "• Develop comprehensive strategies\n• Invest in capability building\n• Create centers of excellence",
                    "conclusion": f"The strategic importance of {brief.trend_topic} will continue to grow, making early action advisable."
                }

            elif brief.content_type == ContentType.HOW_TO_GUIDE:
                sections = {
                    "trend_importance": f"{brief.trend_topic} offers significant opportunities for businesses to improve operations and competitiveness.",
                    "step_1_details": f"Evaluate your current capabilities and identify gaps related to {brief.trend_topic} implementation.",
                    "step_2_details": f"Assess potential applications of {brief.trend_topic} within your organization and prioritize by impact and feasibility.",
                    "step_3_details": f"Create a roadmap for {brief.trend_topic} adoption, including timeline, resources, and success metrics.",
                    "step_4_details": f"Begin with pilot projects to gain experience and demonstrate value of {brief.trend_topic} initiatives.",
                    "step_5_details": f"Monitor results, gather feedback, and scale successful {brief.trend_topic} implementations.",
                    "tools_and_resources": f"Essential tools for {brief.trend_topic} implementation include planning frameworks, assessment tools, and monitoring solutions.",
                    "common_mistakes": "• Lack of clear objectives\n• Insufficient stakeholder buy-in\n• Inadequate resource allocation\n• Poor change management",
                    "success_metrics": "• Implementation timeline adherence\n• Stakeholder satisfaction\n• Operational improvements\n• ROI achievement",
                    "next_steps": f"Continue monitoring {brief.trend_topic} developments and expand successful implementations."
                }

            return sections

        except Exception as e:
            logger.error(f"Error generating content sections: {str(e)}")
            return {}

    def populate_template(self, template: str, sections: Dict[str, str], brief: ContentBrief) -> str:
        """Populate content template with generated sections."""
        try:
            # Basic template variables
            template_vars = {
                "title": self.generate_title(brief),
                "meta_description": self.generate_meta_description(brief),
                "trend_topic": brief.trend_topic,
                "content_angle": brief.content_angle,
                "business_context": brief.business_context or "digital transformation and business optimization"
            }

            # Add generated sections
            template_vars.update(sections)

            # Replace template variables
            populated = template
            for var, value in template_vars.items():
                populated = populated.replace(f"{{{var}}}", str(value))

            # Clean up any remaining placeholders
            populated = re.sub(r'\{[^}]+\}', '[Content section pending]', populated)

            return populated.strip()

        except Exception as e:
            logger.error(f"Error populating template: {str(e)}")
            return f"# {brief.trend_topic}\n\nContent generation error. Please try again."

    def generate_title(self, brief: ContentBrief) -> str:
        """Generate SEO-optimized title."""
        titles = {
            ContentType.BLOG_POST: f"How {brief.trend_topic} is Transforming Business Operations",
            ContentType.BREAKING_NEWS: f"Breaking: {brief.trend_topic} Disrupts Industry Landscape",
            ContentType.ANALYSIS_ARTICLE: f"{brief.trend_topic}: Complete Market Analysis and Strategic Insights",
            ContentType.HOW_TO_GUIDE: f"Complete Guide to Leveraging {brief.trend_topic} for Business Growth",
            ContentType.OPINION_PIECE: f"Why {brief.trend_topic} is the Future of Business Innovation",
            ContentType.CASE_STUDY: f"{brief.trend_topic} Success Story: Lessons from Early Adopters"
        }

        base_title = titles.get(brief.content_type, f"{brief.trend_topic}: Industry Analysis")

        # Add primary keyword if not already included
        if brief.target_keywords and brief.target_keywords[0].lower() not in base_title.lower():
            base_title = f"{base_title} - {brief.target_keywords[0]}"

        return base_title

    def generate_meta_description(self, brief: ContentBrief) -> str:
        """Generate SEO meta description."""
        descriptions = {
            ContentType.BLOG_POST: f"Discover how {brief.trend_topic} is reshaping business strategies. Expert insights, practical applications, and strategic recommendations for competitive advantage.",
            ContentType.BREAKING_NEWS: f"Latest developments in {brief.trend_topic}: breaking news, industry impact, and expert analysis. Stay ahead of the curve.",
            ContentType.ANALYSIS_ARTICLE: f"Comprehensive analysis of {brief.trend_topic}: market trends, competitive landscape, and strategic implications for business leaders.",
            ContentType.HOW_TO_GUIDE: f"Step-by-step guide to implementing {brief.trend_topic} in your business. Practical strategies, tools, and best practices.",
            ContentType.OPINION_PIECE: f"Expert opinion on {brief.trend_topic}: why it matters for your business and how to capitalize on emerging opportunities.",
            ContentType.CASE_STUDY: f"Real-world {brief.trend_topic} implementation: case study analysis, results, and lessons learned from successful adoption."
        }

        base_description = descriptions.get(brief.content_type, f"Expert analysis of {brief.trend_topic} and its business implications.")

        # Ensure it's under 160 characters
        if len(base_description) > 157:
            base_description = base_description[:157] + "..."

        return base_description

    async def generate_seo_elements(self, brief: ContentBrief, content: str) -> Dict[str, Any]:
        """Generate SEO elements for content."""
        try:
            return {
                "title": self.generate_title(brief),
                "meta_description": self.generate_meta_description(brief),
                "schema_markup": {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    "headline": self.generate_title(brief),
                    "description": self.generate_meta_description(brief),
                    "author": {
                        "@type": "Organization",
                        "name": "TriSynq AI"
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "TriSynq AI",
                        "logo": {
                            "@type": "ImageObject",
                            "url": "https://trisynqai.com/logo.png"
                        }
                    },
                    "datePublished": datetime.utcnow().isoformat(),
                    "dateModified": datetime.utcnow().isoformat(),
                    "mainEntityOfPage": {
                        "@type": "WebPage",
                        "@id": f"https://trisynqai.com/insights/{brief.trend_id}"
                    },
                    "keywords": ", ".join(brief.target_keywords),
                    "articleSection": brief.content_type.value.replace("_", " ").title(),
                    "wordCount": len(content.split()),
                    "about": {
                        "@type": "Thing",
                        "name": brief.trend_topic
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error generating SEO elements: {str(e)}")
            return {
                "title": brief.trend_topic,
                "meta_description": f"Analysis of {brief.trend_topic}",
                "schema_markup": {}
            }

    def calculate_readability_score(self, content: str) -> float:
        """Calculate readability score (simplified Flesch-Kincaid)."""
        try:
            sentences = content.count('.') + content.count('!') + content.count('?')
            words = len(content.split())
            syllables = sum([self.count_syllables(word) for word in content.split()])

            if sentences == 0 or words == 0:
                return 0.0

            # Simplified Flesch Reading Ease
            score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
            return max(0.0, min(100.0, score)) / 100.0  # Normalize to 0-1

        except Exception as e:
            logger.error(f"Error calculating readability: {str(e)}")
            return 0.7  # Default moderate readability

    def count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        try:
            word = word.lower()
            vowels = "aeiouy"
            syllable_count = 0
            prev_was_vowel = False

            for char in word:
                if char in vowels:
                    if not prev_was_vowel:
                        syllable_count += 1
                    prev_was_vowel = True
                else:
                    prev_was_vowel = False

            # Handle silent e
            if word.endswith('e'):
                syllable_count -= 1

            return max(1, syllable_count)

        except Exception as e:  # Phase 3: Specific exception handling
            return 2  # Default syllable count

    def calculate_seo_score(self, content: str, keywords: List[str]) -> float:
        """Calculate SEO optimization score."""
        try:
            if not keywords:
                return 0.5

            content_lower = content.lower()
            total_score = 0.0

            for keyword in keywords:
                keyword_lower = keyword.lower()
                keyword_count = content_lower.count(keyword_lower)
                word_count = len(content.split())

                # Keyword density (optimal around 1-2%)
                density = (keyword_count / word_count) * 100 if word_count > 0 else 0

                if 0.5 <= density <= 3.0:
                    density_score = 1.0
                elif density < 0.5:
                    density_score = density / 0.5
                else:
                    density_score = max(0.0, 1.0 - (density - 3.0) / 3.0)

                total_score += density_score

            return total_score / len(keywords)

        except Exception as e:
            logger.error(f"Error calculating SEO score: {str(e)}")
            return 0.6  # Default moderate SEO score

ai_engine = AIContentEngine()

# Health check endpoint
@app.get("/health")
async def health_check():
    redis_status = "available" if REDIS_AVAILABLE else "unavailable"
    ai_services = {
        "openai": "available" if ai_engine.openai_available else "unavailable",
        "perplexity": "available" if ai_engine.perplexity_available else "unavailable"
    }

    return {
        "status": "healthy",
        "service": "rapid-content-generator",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "redis_cache": redis_status,
        "ai_services": ai_services
    }

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        if action == "generate_content":
            brief = ContentBrief(**parameters)
            result = await generate_rapid_content(brief)
            return {
                "status": "success",
                "result": result.dict(),
                "workflow_context": workflow_context
            }

        elif action == "generate_brief":
            trend_data = parameters.get("trend_data")
            result = await create_content_brief(trend_data)
            return {
                "status": "success",
                "result": result.dict(),
                "workflow_context": workflow_context
            }

        elif action == "optimize_content":
            content_id = parameters.get("content_id")
            optimization_type = parameters.get("optimization_type", "seo")
            result = await optimize_content(content_id, optimization_type)
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

# Rapid Content Generation Endpoints
@app.post("/generate-content", response_model=GeneratedContent)
async def generate_rapid_content(brief: ContentBrief, background_tasks: BackgroundTasks):
    """Generate content rapidly based on content brief."""
    try:
        logger.info(f"Generating rapid content for trend: {brief.trend_topic}")

        start_time = time.time()

        # Generate content
        generated_content = await ai_engine.generate_content(brief)

        # Store generated content
        content_data = generated_content.dict()
        db.collection("generated_content").document(generated_content.content_id).set(content_data)

        # Cache for quick access
        if REDIS_AVAILABLE:
            redis_client.setex(f"content:{generated_content.content_id}", 3600,
                             json.dumps(content_data, default=str))

        # Update trending processing status
        db.collection("trending_processing").document(brief.trend_id).update({
            "status": "content_generated",
            "content_generated_id": generated_content.content_id,
            "content_generation_completed": datetime.utcnow()
        })

        # Publish content generated event
        background_tasks.add_task(publish_content_generated_event, generated_content)

        generation_time = time.time() - start_time
        logger.info(f"Content generated in {generation_time:.2f}s - {generated_content.word_count} words")

        return generated_content

    except Exception as e:
        logger.error(f"Error generating rapid content: {str(e)}")
        # Update status to failed
        db.collection("trending_processing").document(brief.trend_id).update({
            "status": "content_generation_failed",
            "error": str(e),
            "failed_at": datetime.utcnow()
        })
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-brief", response_model=ContentBrief)
async def create_content_brief(trend_data: Dict[str, Any]):
    """Create content brief from trend data."""
    try:
        # Extract trend information
        trend_id = trend_data.get("trend_id", str(uuid.uuid4()))
        trend_topic = trend_data.get("topic", "")
        priority_map = {
            "critical": ContentPriority.CRITICAL,
            "high": ContentPriority.HIGH,
            "medium": ContentPriority.MEDIUM,
            "low": ContentPriority.LOW
        }

        priority = priority_map.get(trend_data.get("priority", "medium"), ContentPriority.MEDIUM)

        # Determine content type based on trend characteristics
        content_type = determine_content_type(trend_data)

        # Calculate deadline
        deadline_minutes = {
            ContentPriority.CRITICAL: 15,
            ContentPriority.HIGH: 30,
            ContentPriority.MEDIUM: 60,
            ContentPriority.LOW: 120
        }

        deadline = datetime.utcnow() + timedelta(minutes=deadline_minutes[priority])

        # Create content brief
        brief = ContentBrief(
            brief_id=str(uuid.uuid4()),
            trend_id=trend_id,
            trend_topic=trend_topic,
            content_type=content_type,
            priority=priority,
            target_keywords=trend_data.get("related_keywords", [trend_topic]),
            content_angle=trend_data.get("content_angles", [f"Analysis: {trend_topic}"])[0],
            unique_perspective=f"TriSynq AI's expert analysis of {trend_topic} and its business implications",
            seo_requirements={
                "target_word_count": get_target_word_count(content_type, priority),
                "keyword_density": "1-2%",
                "readability_target": "8th-10th grade",
                "schema_markup": True
            },
            target_word_count=get_target_word_count(content_type, priority),
            deadline=deadline,
            business_context=trend_data.get("business_context", "SEO and digital marketing optimization")
        )

        # Store brief
        brief_data = brief.dict()
        db.collection("content_briefs").document(brief.brief_id).set(brief_data)

        logger.info(f"Created content brief: {brief.brief_id} for trend {trend_topic}")

        return brief

    except Exception as e:
        logger.error(f"Error creating content brief: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/content/{content_id}")
async def get_generated_content(content_id: str):
    """Get generated content by ID."""
    try:
        # Try cache first
        if REDIS_AVAILABLE:
            cached_data = redis_client.get(f"content:{content_id}")
            if cached_data:
                return json.loads(cached_data)

        # Fallback to database
        doc_ref = db.collection("generated_content").document(content_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Content not found")

        return doc.to_dict()

    except Exception as e:
        logger.error(f"Error getting content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/brief/{brief_id}")
async def get_content_brief(brief_id: str):
    """Get content brief by ID."""
    try:
        doc_ref = db.collection("content_briefs").document(brief_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Brief not found")

        return doc.to_dict()

    except Exception as e:
        logger.error(f"Error getting brief: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize-content")
async def optimize_content(content_id: str, optimization_type: str = "seo"):
    """Optimize generated content for SEO or readability."""
    try:
        # Get existing content
        doc_ref = db.collection("generated_content").document(content_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Content not found")

        content_data = doc.to_dict()

        # Perform optimization based on type
        if optimization_type == "seo":
            # Re-calculate SEO score and suggest improvements
            current_seo_score = content_data.get("seo_score", 0)
            target_keywords = content_data.get("target_keywords", [])

            optimization_suggestions = []
            if current_seo_score < 0.7:
                optimization_suggestions.append("Increase keyword density in key sections")
                optimization_suggestions.append("Add more semantic keywords and phrases")
                optimization_suggestions.append("Optimize headings for target keywords")

            return {
                "content_id": content_id,
                "optimization_type": optimization_type,
                "current_seo_score": current_seo_score,
                "target_keywords": target_keywords,
                "suggestions": optimization_suggestions,
                "optimized_at": datetime.utcnow().isoformat()
            }

        elif optimization_type == "readability":
            current_readability = content_data.get("readability_score", 0)

            readability_suggestions = []
            if current_readability < 0.7:
                readability_suggestions.append("Use shorter sentences and paragraphs")
                readability_suggestions.append("Replace complex words with simpler alternatives")
                readability_suggestions.append("Add more transition words and phrases")

            return {
                "content_id": content_id,
                "optimization_type": optimization_type,
                "current_readability_score": current_readability,
                "suggestions": readability_suggestions,
                "optimized_at": datetime.utcnow().isoformat()
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid optimization type")

    except Exception as e:
        logger.error(f"Error optimizing content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper Functions
def determine_content_type(trend_data: Dict[str, Any]) -> ContentType:
    """Determine optimal content type based on trend characteristics."""
    velocity = trend_data.get("velocity", 0.5)
    relevance_score = trend_data.get("relevance_score", 0.5)
    competitive_gap_score = trend_data.get("competitive_gap_score", 0.5)

    # High velocity + high relevance = breaking news
    if velocity >= 0.7 and relevance_score >= 0.7:
        return ContentType.BREAKING_NEWS

    # High competitive gap = analysis article
    elif competitive_gap_score >= 0.7:
        return ContentType.ANALYSIS_ARTICLE

    # Medium-high relevance = how-to guide
    elif relevance_score >= 0.6:
        return ContentType.HOW_TO_GUIDE

    # Default to blog post
    else:
        return ContentType.BLOG_POST

def get_target_word_count(content_type: ContentType, priority: ContentPriority) -> int:
    """Get target word count based on content type and priority."""
    base_counts = {
        ContentType.BREAKING_NEWS: 800,
        ContentType.BLOG_POST: 1200,
        ContentType.HOW_TO_GUIDE: 1500,
        ContentType.ANALYSIS_ARTICLE: 2000,
        ContentType.OPINION_PIECE: 1000,
        ContentType.CASE_STUDY: 1800
    }

    base_count = base_counts.get(content_type, 1200)

    # Adjust for priority (faster = shorter)
    if priority == ContentPriority.CRITICAL:
        return int(base_count * 0.7)
    elif priority == ContentPriority.HIGH:
        return int(base_count * 0.85)
    else:
        return base_count

# Event Publishers
async def publish_content_generated_event(content: GeneratedContent):
    """Publish content generated event."""
    try:
        topic_path = publisher.topic_path(PROJECT_ID, "content-generated")
        message_data = {
            "content_id": content.content_id,
            "brief_id": content.brief_id,
            "trend_id": content.trend_id,
            "title": content.title,
            "word_count": content.word_count,
            "generation_time_seconds": content.generation_time_seconds,
            "seo_score": content.seo_score,
            "readability_score": content.readability_score,
            "generated_at": content.generated_at.isoformat()
        }

        future = publisher.publish(topic_path, json.dumps(message_data, default=str).encode())
        logger.info(f"Published content generated event for {content.content_id}")

    except Exception as e:
        logger.error(f"Error publishing content generated event: {str(e)}")

# Pub/Sub message handler for rapid content requests
def handle_pubsub_message(message):
    """Handle incoming Pub/Sub messages for rapid content generation."""
    try:
        data = json.loads(message.data.decode())
        logger.info(f"Received rapid content request: {data.get('trend_id')}")

        # Create content brief from trend data
        brief_data = {
            "brief_id": str(uuid.uuid4()),
            "trend_id": data.get("trend_id"),
            "trend_topic": data.get("trend_topic"),
            "content_type": determine_content_type(data),
            "priority": data.get("priority", "medium"),
            "target_keywords": data.get("target_keywords", []),
            "content_angle": data.get("content_angles", ["Analysis"])[0] if data.get("content_angles") else "Analysis",
            "unique_perspective": f"Expert analysis of {data.get('trend_topic')}",
            "seo_requirements": {"target_word_count": 1200},
            "target_word_count": 1200,
            "deadline": data.get("deadline"),
            "business_context": "SEO and digital marketing"
        }

        # Process content generation
        asyncio.run(process_rapid_content_request(brief_data))

        message.ack()

    except Exception as e:
        logger.error(f"Error handling Pub/Sub message: {str(e)}")
        message.nack()

async def process_rapid_content_request(brief_data: Dict[str, Any]):
    """Process rapid content generation request."""
    try:
        # Create brief object
        brief = ContentBrief(**brief_data)

        # Generate content
        generated_content = await ai_engine.generate_content(brief)

        # Store and cache
        content_data = generated_content.dict()
        db.collection("generated_content").document(generated_content.content_id).set(content_data)

        if REDIS_AVAILABLE:
            redis_client.setex(f"content:{generated_content.content_id}", 3600,
                             json.dumps(content_data, default=str))

        # Update processing status
        db.collection("trending_processing").document(brief.trend_id).update({
            "status": "content_generated",
            "content_generated_id": generated_content.content_id,
            "content_generation_completed": datetime.utcnow()
        })

        # Publish completion event
        await publish_content_generated_event(generated_content)

        logger.info(f"Rapid content generation completed: {generated_content.content_id}")

    except Exception as e:
        logger.error(f"Error processing rapid content request: {str(e)}")

# Dashboard endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Rapid Content Generator dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rapid Content Generator Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
            .header { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
            .stat { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stat h3 { margin: 0; font-size: 2em; color: #28a745; }
            .performance { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
            .metric { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .content-list { margin-top: 20px; }
            .content-item { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .button { background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 8px; margin: 8px; cursor: pointer; font-weight: bold; }
            .button:hover { background: #218838; }
            .score { padding: 4px 12px; border-radius: 20px; font-size: 12px; color: white; font-weight: bold; }
            .score.high { background: #28a745; }
            .score.medium { background: #ffc107; color: #000; }
            .score.low { background: #dc3545; }
            .priority { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .priority.critical { background: #dc3545; color: white; }
            .priority.high { background: #fd7e14; color: white; }
            .priority.medium { background: #ffc107; color: #000; }
            .priority.low { background: #6c757d; color: white; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚡ Rapid Content Generator</h1>
            <p>Lightning-fast content generation for trending topics</p>
        </div>

        <div class="stats">
            <div class="stat">
                <h3 id="content-generated">0</h3>
                <p>Content Generated</p>
            </div>
            <div class="stat">
                <h3 id="avg-generation-time">0s</h3>
                <p>Avg Generation Time</p>
            </div>
            <div class="stat">
                <h3 id="avg-seo-score">0%</h3>
                <p>Avg SEO Score</p>
            </div>
            <div class="stat">
                <h3 id="content-pending">0</h3>
                <p>Pending Generation</p>
            </div>
        </div>

        <div>
            <h2>⚡ Quick Actions</h2>
            <button class="button" onclick="simulateContentRequest()">Simulate Content Request</button>
            <button class="button" onclick="generateTestContent()">Generate Test Content</button>
            <button class="button" onclick="checkPerformanceMetrics()">Check Performance</button>
            <button class="button" onclick="refreshDashboard()">Refresh Dashboard</button>
        </div>

        <div class="performance">
            <div class="metric">
                <h3>Generation Speed Targets</h3>
                <p><span class="priority critical">CRITICAL</span> 15 minutes</p>
                <p><span class="priority high">HIGH</span> 30 minutes</p>
                <p><span class="priority medium">MEDIUM</span> 60 minutes</p>
                <p><span class="priority low">LOW</span> 120 minutes</p>
            </div>
            <div class="metric">
                <h3>Content Types</h3>
                <p>📰 Breaking News (800 words)</p>
                <p>📝 Blog Posts (1200 words)</p>
                <p>📊 Analysis (2000 words)</p>
                <p>📚 How-to Guides (1500 words)</p>
            </div>
            <div class="metric">
                <h3>Quality Metrics</h3>
                <p>SEO Score: 80%+ target</p>
                <p>Readability: 70%+ target</p>
                <p>Keyword Density: 1-2%</p>
                <p>Schema Markup: Included</p>
            </div>
        </div>

        <div class="content-list">
            <h2>🚀 Recent Content Generation</h2>
            <div id="content-list">Loading recent content...</div>
        </div>

        <script>
            async function simulateContentRequest() {
                const trendTopics = [
                    "AI-powered content optimization breakthrough",
                    "Google announces major algorithm update",
                    "Revolutionary SEO automation platform launches",
                    "Content strategy AI tools reach new milestone",
                    "Search engine optimization redefined by AI"
                ];

                const topic = trendTopics[Math.floor(Math.random() * trendTopics.length)];

                const briefData = {
                    brief_id: generateUUID(),
                    trend_id: generateUUID(),
                    trend_topic: topic,
                    content_type: "blog_post",
                    priority: "high",
                    target_keywords: [topic.split(' ')[0], topic.split(' ')[1]],
                    content_angle: `Expert analysis: ${topic}`,
                    unique_perspective: `TriSynq AI's expert analysis of ${topic}`,
                    seo_requirements: { target_word_count: 1200 },
                    target_word_count: 1200,
                    deadline: new Date(Date.now() + 30*60*1000).toISOString(),
                    business_context: "SEO and digital marketing optimization"
                };

                try {
                    const response = await fetch('/generate-content', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(briefData)
                    });
                    const result = await response.json();
                    alert(`Content generated successfully!\\n\\nTitle: ${result.title}\\nWords: ${result.word_count}\\nSEO Score: ${(result.seo_score * 100).toFixed(0)}%\\nGeneration Time: ${result.generation_time_seconds.toFixed(1)}s`);
                    refreshDashboard();
                } catch (error) {
                    alert('Error generating content: ' + error.message);
                }
            }

            async function generateTestContent() {
                const topic = prompt('Enter trend topic for content generation:');
                if (!topic) return;

                const briefData = {
                    brief_id: generateUUID(),
                    trend_id: generateUUID(),
                    trend_topic: topic,
                    content_type: "analysis_article",
                    priority: "medium",
                    target_keywords: [topic],
                    content_angle: `Comprehensive analysis: ${topic}`,
                    unique_perspective: `Expert insights on ${topic}`,
                    seo_requirements: { target_word_count: 1500 },
                    target_word_count: 1500,
                    deadline: new Date(Date.now() + 60*60*1000).toISOString(),
                    business_context: "Digital transformation and business optimization"
                };

                try {
                    const response = await fetch('/generate-content', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(briefData)
                    });
                    const result = await response.json();
                    alert(`Test content generated!\\n\\nContent ID: ${result.content_id}\\nWords: ${result.word_count}\\nGeneration Time: ${result.generation_time_seconds.toFixed(1)}s`);
                    refreshDashboard();
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }

            async function checkPerformanceMetrics() {
                try {
                    const response = await fetch('/health');
                    const health = await response.json();

                    let statusReport = `Rapid Content Generator Status:\\n\\n`;
                    statusReport += `Service: ${health.status}\\n`;
                    statusReport += `Redis Cache: ${health.redis_cache}\\n`;
                    statusReport += `OpenAI: ${health.ai_services.openai}\\n`;
                    statusReport += `Perplexity: ${health.ai_services.perplexity}\\n\\n`;
                    statusReport += `Generation targets:\\n`;
                    statusReport += `• Critical: 15 minutes\\n`;
                    statusReport += `• High: 30 minutes\\n`;
                    statusReport += `• Medium: 60 minutes\\n`;
                    statusReport += `• Low: 120 minutes`;

                    alert(statusReport);
                } catch (error) {
                    alert('Error checking performance: ' + error.message);
                }
            }

            async function refreshDashboard() {
                // Simulate dashboard metrics
                document.getElementById('content-generated').textContent = Math.floor(Math.random() * 150) + 50;
                document.getElementById('avg-generation-time').textContent = (Math.random() * 30 + 15).toFixed(1) + 's';
                document.getElementById('avg-seo-score').textContent = Math.floor(Math.random() * 20 + 75) + '%';
                document.getElementById('content-pending').textContent = Math.floor(Math.random() * 8);

                // Load sample content items
                const sampleContent = [
                    { title: 'AI Content Generation Revolution', words: 1245, seo_score: 0.87, type: 'blog_post', priority: 'high' },
                    { title: 'SEO Automation Platform Analysis', words: 1890, seo_score: 0.92, type: 'analysis_article', priority: 'medium' },
                    { title: 'Breaking: Google Algorithm Update', words: 832, seo_score: 0.79, type: 'breaking_news', priority: 'critical' },
                    { title: 'How to Implement AI SEO Tools', words: 1567, seo_score: 0.85, type: 'how_to_guide', priority: 'medium' }
                ];

                const contentList = document.getElementById('content-list');
                contentList.innerHTML = '';

                sampleContent.forEach(content => {
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'content-item';

                    const scoreClass = content.seo_score > 0.8 ? 'high' : (content.seo_score > 0.6 ? 'medium' : 'low');

                    contentDiv.innerHTML = `
                        <div>
                            <strong>${content.title}</strong><br>
                            <small>Type: ${content.type.replace('_', ' ')} | Words: ${content.words} | Generated: ${Math.floor(Math.random() * 120) + 5} min ago</small>
                        </div>
                        <div>
                            <span class="priority ${content.priority}">${content.priority.toUpperCase()}</span>
                            <span class="score ${scoreClass}">${(content.seo_score * 100).toFixed(0)}%</span>
                        </div>
                    `;
                    contentList.appendChild(contentDiv);
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
    # Set up Pub/Sub subscriber for rapid content requests
    if os.getenv("PUBSUB_ENABLED", "true").lower() == "true":
        subscription_path = subscriber.subscription_path(PROJECT_ID, "rapid-content-request-subscription")
        try:
            subscriber.subscribe(subscription_path, callback=handle_pubsub_message)
            logger.info("Pub/Sub subscriber started for rapid content requests")
        except Exception as e:
            logger.error(f"Failed to start Pub/Sub subscriber: {str(e)}")

    uvicorn.run(app, host="0.0.0.0", port=PORT)