from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from google.cloud import pubsub_v1, firestore, storage
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
from urllib.parse import urlparse, urljoin
import re
from dataclasses import dataclass
from bs4 import BeautifulSoup
import aiohttp

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))
DATAFORSEO_LOGIN = os.getenv("DATAFORSEO_LOGIN", "")
DATAFORSEO_PASSWORD = os.getenv("DATAFORSEO_PASSWORD", "")

# Initialize GCP clients
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
db = firestore.Client()
storage_client = storage.Client()

# FastAPI app
app = FastAPI(
    title="Competitive Analysis Service",
    description="Automated competitor monitoring and analysis",
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
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "competitive-analysis"}'
)
logger = logging.getLogger(__name__)

# Data Models
@dataclass
class CompetitorIntelligence:
    competitor_id: str
    competitor_name: str
    website_url: str
    recent_developments: List[Dict[str, Any]]
    content_strategy_changes: Dict[str, Any]
    positioning_shifts: List[str]
    performance_benchmarks: Dict[str, Any]
    partnership_activity: List[Dict[str, Any]]
    threat_level: float
    opportunities_created: List[str]
    last_analyzed: datetime

class CompetitorAnalysisRequest(BaseModel):
    competitor_urls: List[str]
    analysis_depth: str = "standard"  # standard, deep
    focus_areas: List[str] = ["content_strategy", "seo", "positioning"]
    monitoring_frequency: str = "daily"  # daily, weekly, monthly

class CompetitorProfileRequest(BaseModel):
    competitor_url: str
    initial_analysis: bool = True
    include_technical_seo: bool = True
    include_content_analysis: bool = True

class CompetitorBenchmark(BaseModel):
    competitor_id: str
    metrics: Dict[str, float]
    analysis_date: datetime
    comparison_baseline: Dict[str, float]

# DataForSEO API Integration
class DataForSEOClient:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self.base_url = "https://api.dataforseo.com/v3"

    async def get_competitor_keywords(self, domain: str, limit: int = 100) -> Dict[str, Any]:
        """Get competitor's ranking keywords."""
        try:
            endpoint = f"{self.base_url}/dataforseo_labs/google/competitors_domain/live"
            payload = [{
                "target": domain,
                "location_code": 2840,  # USA
                "language_code": "en",
                "limit": limit,
                "include_serp_info": True,
                "include_clickstream_data": True
            }]

            auth = aiohttp.BasicAuth(self.login, self.password)
            timeout = aiohttp.ClientTimeout(total=60)

            async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
                async with session.post(endpoint, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"DataForSEO error: {response.status}")
                        return {"error": f"API call failed: {response.status}"}

        except Exception as e:
            logger.error(f"DataForSEO exception: {str(e)}")
            return {"error": str(e)}

    async def get_domain_metrics(self, domain: str) -> Dict[str, Any]:
        """Get domain authority and other SEO metrics."""
        try:
            endpoint = f"{self.base_url}/dataforseo_labs/google/domain_metrics/live"
            payload = [{
                "targets": [domain],
                "location_code": 2840,
                "language_code": "en"
            }]

            auth = aiohttp.BasicAuth(self.login, self.password)
            timeout = aiohttp.ClientTimeout(total=60)

            async with aiohttp.ClientSession(auth=auth, timeout=timeout) as session:
                async with session.post(endpoint, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"DataForSEO metrics error: {response.status}")
                        return {"error": f"Metrics call failed: {response.status}"}

        except Exception as e:
            logger.error(f"Domain metrics exception: {str(e)}")
            return {"error": str(e)}

# Initialize DataForSEO client
dataforseo_client = DataForSEOClient(DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD) if DATAFORSEO_LOGIN else None

# Web Scraping Utilities
class CompetitorScraper:
    def __init__(self):
        self.session = None

    async def analyze_competitor_website(self, url: str) -> Dict[str, Any]:
        """Scrape and analyze competitor website."""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self.parse_website_content(html, url)
                    else:
                        return {"error": f"Failed to fetch {url}: {response.status}"}

        except Exception as e:
            logger.error(f"Website analysis error for {url}: {str(e)}")
            return {"error": str(e)}

    def parse_website_content(self, html: str, url: str) -> Dict[str, Any]:
        """Parse website HTML for competitive intelligence."""
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Extract basic information
            title = soup.find('title').text if soup.find('title') else ""
            meta_description = ""
            meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_desc_tag:
                meta_description = meta_desc_tag.get('content', '')

            # Analyze content structure
            headings = {
                'h1': [h.text.strip() for h in soup.find_all('h1')],
                'h2': [h.text.strip() for h in soup.find_all('h2')],
                'h3': [h.text.strip() for h in soup.find_all('h3')]
            }

            # Extract navigation structure
            nav_links = []
            nav = soup.find('nav') or soup.find('div', class_=re.compile(r'nav|menu', re.I))
            if nav:
                links = nav.find_all('a', href=True)
                nav_links = [{'text': link.text.strip(), 'href': link['href']} for link in links if link.text.strip()]

            # Analyze content themes
            content_text = soup.get_text()
            word_count = len(content_text.split())

            # Look for pricing information
            pricing_indicators = soup.find_all(text=re.compile(r'\$[\d,]+|\d+\s*(?:per month|/month|monthly)', re.I))

            # Check for specific business indicators
            contact_info = {
                'phone': bool(soup.find(text=re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'))),
                'email': bool(soup.find(text=re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'))),
                'address': bool(soup.find(text=re.compile(r'\d+.*(?:street|st|avenue|ave|road|rd|drive|dr)', re.I)))
            }

            return {
                "url": url,
                "title": title,
                "meta_description": meta_description,
                "headings": headings,
                "navigation": nav_links[:10],  # Limit to first 10
                "word_count": word_count,
                "pricing_mentions": len(pricing_indicators),
                "contact_info": contact_info,
                "analyzed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"HTML parsing error: {str(e)}")
            return {"error": f"Parsing failed: {str(e)}"}

scraper = CompetitorScraper()

# Health check endpoint
@app.get("/health")
async def health_check():
    status = "healthy"
    if not DATAFORSEO_LOGIN:
        status = "degraded"

    return {
        "status": status,
        "service": "competitive-analysis",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "dataforseo_configured": bool(DATAFORSEO_LOGIN)
    }

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        if action == "analyze_competitor":
            competitor_url = parameters.get("competitor_url")
            if not competitor_url:
                raise HTTPException(status_code=400, detail="competitor_url required")

            result = await analyze_single_competitor(competitor_url, parameters.get("analysis_depth", "standard"))
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "batch_competitor_analysis":
            urls = parameters.get("competitor_urls", [])
            if not urls:
                raise HTTPException(status_code=400, detail="competitor_urls required")

            result = await batch_analyze_competitors(urls)
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "get_competitor_insights":
            competitor_id = parameters.get("competitor_id")
            result = await get_competitor_insights(competitor_id)
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

# Competitive Analysis Endpoints
@app.post("/analyze-competitor")
async def analyze_single_competitor(
    competitor_url: str,
    analysis_depth: str = "standard",
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """Analyze a single competitor."""
    try:
        competitor_id = str(uuid.uuid4())
        domain = urlparse(competitor_url).netloc

        # Basic website analysis
        website_analysis = await scraper.analyze_competitor_website(competitor_url)

        analysis_data = {
            "competitor_id": competitor_id,
            "competitor_url": competitor_url,
            "domain": domain,
            "analysis_depth": analysis_depth,
            "website_analysis": website_analysis,
            "analyzed_at": datetime.utcnow(),
            "status": "in_progress"
        }

        # Store initial analysis
        db.collection("competitor_intelligence").document(competitor_id).set(analysis_data)

        # Enhanced analysis if DataForSEO is available
        if dataforseo_client and analysis_depth == "deep":
            if background_tasks:
                background_tasks.add_task(perform_deep_analysis, competitor_id, domain)
            else:
                await perform_deep_analysis(competitor_id, domain)

        # Publish competitor alert
        await publish_competitor_alert(competitor_id, domain, "new_analysis")

        logger.info(f"Started competitor analysis for {domain}")

        return {
            "competitor_id": competitor_id,
            "domain": domain,
            "status": "analysis_started",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        }

    except Exception as e:
        logger.error(f"Competitor analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-analysis")
async def batch_analyze_competitors(
    competitor_urls: List[str],
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Analyze multiple competitors in batch."""
    try:
        analysis_batch_id = str(uuid.uuid4())
        competitor_analyses = []

        for url in competitor_urls:
            analysis = await analyze_single_competitor(url, "standard", background_tasks)
            competitor_analyses.append(analysis)

        # Store batch information
        batch_data = {
            "batch_id": analysis_batch_id,
            "competitor_count": len(competitor_urls),
            "analyses": competitor_analyses,
            "started_at": datetime.utcnow(),
            "status": "in_progress"
        }

        db.collection("competitor_batches").document(analysis_batch_id).set(batch_data)

        return {
            "batch_id": analysis_batch_id,
            "competitor_count": len(competitor_urls),
            "analyses": competitor_analyses,
            "status": "batch_started"
        }

    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/competitor/{competitor_id}")
async def get_competitor_insights(competitor_id: str) -> Dict[str, Any]:
    """Get detailed competitor insights."""
    try:
        doc_ref = db.collection("competitor_intelligence").document(competitor_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Competitor analysis not found")

        competitor_data = doc.to_dict()

        # Add recent changes if available
        changes_query = db.collection("competitor_changes").where("competitor_id", "==", competitor_id).order_by("detected_at", direction=firestore.Query.DESCENDING).limit(5)

        recent_changes = []
        for change_doc in changes_query.stream():
            recent_changes.append(change_doc.to_dict())

        competitor_data["recent_changes"] = recent_changes

        return competitor_data

    except Exception as e:
        logger.error(f"Error getting competitor insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/competitors")
async def list_monitored_competitors() -> List[Dict[str, Any]]:
    """List all monitored competitors."""
    try:
        competitors_ref = db.collection("competitor_intelligence")
        query = competitors_ref.order_by("analyzed_at", direction=firestore.Query.DESCENDING).limit(50)

        competitors = []
        for doc in query.stream():
            competitor_data = doc.to_dict()
            competitors.append({
                "competitor_id": competitor_data.get("competitor_id"),
                "domain": competitor_data.get("domain"),
                "analyzed_at": competitor_data.get("analyzed_at").isoformat() if competitor_data.get("analyzed_at") else None,
                "status": competitor_data.get("status", "unknown")
            })

        return competitors

    except Exception as e:
        logger.error(f"Error listing competitors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background Processing
async def perform_deep_analysis(competitor_id: str, domain: str):
    """Perform deep competitive analysis using DataForSEO."""
    try:
        logger.info(f"Starting deep analysis for {domain}")

        # Get competitor keywords
        keyword_data = await dataforseo_client.get_competitor_keywords(domain)

        # Get domain metrics
        metrics_data = await dataforseo_client.get_domain_metrics(domain)

        # Process and store enhanced data
        enhanced_analysis = {
            "keyword_analysis": keyword_data,
            "domain_metrics": metrics_data,
            "deep_analysis_completed_at": datetime.utcnow(),
            "analysis_type": "deep"
        }

        # Update competitor record
        db.collection("competitor_intelligence").document(competitor_id).update({
            "enhanced_analysis": enhanced_analysis,
            "status": "completed",
            "completed_at": datetime.utcnow()
        })

        # Publish completion event
        await publish_competitor_alert(competitor_id, domain, "analysis_complete")

        logger.info(f"Deep analysis completed for {domain}")

    except Exception as e:
        logger.error(f"Deep analysis error for {domain}: {str(e)}")
        db.collection("competitor_intelligence").document(competitor_id).update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow()
        })

async def publish_competitor_alert(competitor_id: str, domain: str, alert_type: str):
    """Publish competitor alert event."""
    try:
        topic_path = publisher.topic_path(PROJECT_ID, "competitor-alert")
        message_data = {
            "competitor_id": competitor_id,
            "domain": domain,
            "alert_type": alert_type,
            "timestamp": datetime.utcnow().isoformat()
        }

        future = publisher.publish(topic_path, json.dumps(message_data, default=str).encode())
        logger.info(f"Published competitor alert for {domain}: {alert_type}")

    except Exception as e:
        logger.error(f"Error publishing competitor alert: {str(e)}")

# Pub/Sub message handler
def handle_pubsub_message(message):
    """Handle incoming Pub/Sub messages."""
    try:
        data = json.loads(message.data.decode())
        task_id = data.get("task_id")
        task_type = data.get("task_type")
        parameters = data.get("parameters", {})

        logger.info(f"Processing task {task_id} of type {task_type}")

        if task_type == "competitive_analysis":
            asyncio.run(process_competitive_analysis_task(task_id, parameters))

        message.ack()

    except Exception as e:
        logger.error(f"Error handling Pub/Sub message: {str(e)}")
        message.nack()

async def process_competitive_analysis_task(task_id: str, parameters: Dict[str, Any]):
    """Process competitive analysis task from Pub/Sub."""
    try:
        competitor_urls = parameters.get("competitor_urls", [])
        analysis_depth = parameters.get("analysis_depth", "standard")

        if not competitor_urls:
            raise ValueError("No competitor URLs provided")

        # Perform batch analysis
        result = await batch_analyze_competitors(competitor_urls, BackgroundTasks())

        # Update task status
        db.collection("research_tasks").document(task_id).update({
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "results": {
                "batch_id": result["batch_id"],
                "competitors_analyzed": result["competitor_count"]
            }
        })

    except Exception as e:
        logger.error(f"Error processing competitive analysis task {task_id}: {str(e)}")
        db.collection("research_tasks").document(task_id).update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow()
        })

# Dashboard endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Competitive Analysis dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Competitive Analysis Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
            .stat { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
            .competitors { margin-top: 20px; }
            .competitor { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 3px; display: flex; justify-content: space-between; align-items: center; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer; }
            .status { padding: 2px 8px; border-radius: 3px; font-size: 12px; color: white; }
            .status.completed { background: #28a745; }
            .status.in-progress { background: #ffc107; color: #000; }
            .status.failed { background: #dc3545; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 Competitive Analysis Dashboard</h1>
            <p>Automated competitor monitoring and strategic intelligence</p>
        </div>

        <div class="stats">
            <div class="stat">
                <h3 id="competitors-monitored">0</h3>
                <p>Competitors Monitored</p>
            </div>
            <div class="stat">
                <h3 id="analyses-today">0</h3>
                <p>Analyses Today</p>
            </div>
            <div class="stat">
                <h3 id="alerts-generated">0</h3>
                <p>Alerts Generated</p>
            </div>
            <div class="stat">
                <h3 id="success-rate">0%</h3>
                <p>Analysis Success Rate</p>
            </div>
        </div>

        <div>
            <h2>Quick Actions</h2>
            <button class="button" onclick="analyzeCompetitor()">Analyze Competitor</button>
            <button class="button" onclick="batchAnalysis()">Batch Analysis</button>
            <button class="button" onclick="refreshData()">Refresh Data</button>
        </div>

        <div class="competitors">
            <h2>Recent Competitor Analyses</h2>
            <div id="competitors-list">Loading...</div>
        </div>

        <script>
            async function analyzeCompetitor() {
                const url = prompt('Enter competitor URL:');
                if (!url) return;

                const response = await fetch('/analyze-competitor', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        competitor_url: url,
                        analysis_depth: 'standard'
                    })
                });
                const result = await response.json();
                alert('Competitor analysis started: ' + result.competitor_id);
                loadCompetitors();
            }

            async function batchAnalysis() {
                const urls = prompt('Enter competitor URLs (comma-separated):');
                if (!urls) return;

                const urlList = urls.split(',').map(u => u.trim()).filter(u => u);

                const response = await fetch('/batch-analysis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        competitor_urls: urlList
                    })
                });
                const result = await response.json();
                alert('Batch analysis started: ' + result.batch_id);
                loadCompetitors();
            }

            async function loadCompetitors() {
                try {
                    const response = await fetch('/competitors');
                    const competitors = await response.json();

                    const competitorsList = document.getElementById('competitors-list');
                    competitorsList.innerHTML = '';

                    competitors.forEach(competitor => {
                        const competitorDiv = document.createElement('div');
                        competitorDiv.className = 'competitor';
                        competitorDiv.innerHTML = `
                            <div>
                                <strong>${competitor.domain}</strong><br>
                                <small>${competitor.analyzed_at || 'Never'}</small>
                            </div>
                            <div class="status ${competitor.status}">${competitor.status}</div>
                        `;
                        competitorsList.appendChild(competitorDiv);
                    });

                    document.getElementById('competitors-monitored').textContent = competitors.length;
                    document.getElementById('analyses-today').textContent = competitors.filter(c =>
                        c.analyzed_at && new Date(c.analyzed_at).toDateString() === new Date().toDateString()
                    ).length;

                } catch (error) {
                    console.error('Error loading competitors:', error);
                    document.getElementById('competitors-list').innerHTML = '<div class="competitor">Error loading competitor data</div>';
                }
            }

            function refreshData() {
                loadCompetitors();
            }

            // Load initial data
            loadCompetitors();
            setInterval(loadCompetitors, 60000); // Refresh every minute
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    # Set up Pub/Sub subscriber
    if os.getenv("PUBSUB_ENABLED", "true").lower() == "true":
        subscription_path = subscriber.subscription_path(PROJECT_ID, "xynergy-competitive-analysis-events-subscription")
        try:
            subscriber.subscribe(subscription_path, callback=handle_pubsub_message)
            logger.info("Pub/Sub subscriber started")
        except Exception as e:
            logger.error(f"Failed to start Pub/Sub subscriber: {str(e)}")

    uvicorn.run(app, host="0.0.0.0", port=PORT)