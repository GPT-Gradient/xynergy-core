from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
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
from enum import Enum

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))

# Initialize GCP clients
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
db = firestore.Client()
storage_client = storage.Client()

# FastAPI app
app = FastAPI(
    title="Research Coordinator",
    description="Orchestrates market intelligence, competitive analysis, and content research",
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
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "research-coordinator"}'
)
logger = logging.getLogger(__name__)

# Data Models
class ResearchTaskType(str, Enum):
    MARKET_INTELLIGENCE = "market_intelligence"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    CONTENT_RESEARCH = "content_research"
    TREND_ANALYSIS = "trend_analysis"

class ResearchTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ResearchTaskRequest(BaseModel):
    task_type: ResearchTaskType
    parameters: Dict[str, Any]
    priority: int = 1  # 1=high, 2=medium, 3=low
    client_id: Optional[str] = None
    deadline: Optional[datetime] = None

class ResearchTaskResponse(BaseModel):
    task_id: str
    task_type: ResearchTaskType
    status: ResearchTaskStatus
    created_at: datetime
    estimated_completion: Optional[datetime] = None

class MarketIntelligenceRequest(BaseModel):
    monitoring_categories: List[str]
    update_frequency: int = 30  # minutes
    business_context: str

class CompetitorAnalysisRequest(BaseModel):
    competitor_urls: List[str]
    analysis_depth: str = "standard"  # standard, deep
    focus_areas: List[str] = ["content_strategy", "seo", "positioning"]

class ContentResearchRequest(BaseModel):
    business_type: str
    target_keywords: List[str]
    competitor_analysis: bool = True
    trend_correlation: bool = True

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "research-coordinator",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        if action == "initiate_research":
            task_request = ResearchTaskRequest(**parameters)
            result = await initiate_research_task(task_request)
            return {
                "status": "success",
                "result": result,
                "workflow_context": workflow_context
            }

        elif action == "get_research_status":
            task_id = parameters.get("task_id")
            if not task_id:
                raise HTTPException(status_code=400, detail="task_id required")

            status = await get_task_status(task_id)
            return {
                "status": "success",
                "result": status,
                "workflow_context": workflow_context
            }

        elif action == "get_research_results":
            task_id = parameters.get("task_id")
            if not task_id:
                raise HTTPException(status_code=400, detail="task_id required")

            results = await get_research_results(task_id)
            return {
                "status": "success",
                "result": results,
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

# Research Task Management
@app.post("/tasks", response_model=ResearchTaskResponse)
async def create_research_task(
    task_request: ResearchTaskRequest,
    background_tasks: BackgroundTasks
):
    """Create a new research task."""
    try:
        task_id = str(uuid.uuid4())
        task_data = {
            "task_id": task_id,
            "task_type": task_request.task_type.value,
            "parameters": task_request.parameters,
            "priority": task_request.priority,
            "client_id": task_request.client_id,
            "status": ResearchTaskStatus.PENDING.value,
            "created_at": datetime.utcnow(),
            "deadline": task_request.deadline
        }

        # Store task in Firestore
        db.collection("research_tasks").document(task_id).set(task_data)

        # Queue task for processing
        background_tasks.add_task(queue_research_task, task_id, task_request)

        logger.info(f"Created research task {task_id} of type {task_request.task_type}")

        return ResearchTaskResponse(
            task_id=task_id,
            task_type=task_request.task_type,
            status=ResearchTaskStatus.PENDING,
            created_at=task_data["created_at"],
            estimated_completion=calculate_estimated_completion(task_request.task_type)
        )

    except Exception as e:
        logger.error(f"Error creating research task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a research task."""
    try:
        doc_ref = db.collection("research_tasks").document(task_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail="Task not found")

        task_data = doc.to_dict()
        return task_data

    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}/results")
async def get_research_results(task_id: str):
    """Get the results of a completed research task."""
    try:
        # Get task status
        task_doc = db.collection("research_tasks").document(task_id).get()
        if not task_doc.exists:
            raise HTTPException(status_code=404, detail="Task not found")

        task_data = task_doc.to_dict()
        if task_data["status"] != ResearchTaskStatus.COMPLETED.value:
            return {
                "status": task_data["status"],
                "message": "Task not yet completed",
                "results": None
            }

        # Get results from appropriate collection
        results_collection = f"research_results_{task_data['task_type']}"
        results_doc = db.collection(results_collection).document(task_id).get()

        if results_doc.exists:
            return {
                "status": "completed",
                "results": results_doc.to_dict()
            }
        else:
            return {
                "status": "completed",
                "message": "Results not found",
                "results": None
            }

    except Exception as e:
        logger.error(f"Error getting research results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Specialized Research Endpoints
@app.post("/market-intelligence")
async def initiate_market_intelligence(
    request: MarketIntelligenceRequest,
    background_tasks: BackgroundTasks
):
    """Initiate market intelligence research."""
    task_request = ResearchTaskRequest(
        task_type=ResearchTaskType.MARKET_INTELLIGENCE,
        parameters=request.dict(),
        priority=1
    )
    return await create_research_task(task_request, background_tasks)

@app.post("/competitive-analysis")
async def initiate_competitive_analysis(
    request: CompetitorAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Initiate competitive analysis research."""
    task_request = ResearchTaskRequest(
        task_type=ResearchTaskType.COMPETITIVE_ANALYSIS,
        parameters=request.dict(),
        priority=1
    )
    return await create_research_task(task_request, background_tasks)

@app.post("/content-research")
async def initiate_content_research(
    request: ContentResearchRequest,
    background_tasks: BackgroundTasks
):
    """Initiate content research."""
    task_request = ResearchTaskRequest(
        task_type=ResearchTaskType.CONTENT_RESEARCH,
        parameters=request.dict(),
        priority=1
    )
    return await create_research_task(task_request, background_tasks)

# Background Task Processing
async def queue_research_task(task_id: str, task_request: ResearchTaskRequest):
    """Queue research task to appropriate service via Pub/Sub."""
    try:
        # Update task status
        db.collection("research_tasks").document(task_id).update({
            "status": ResearchTaskStatus.IN_PROGRESS.value,
            "started_at": datetime.utcnow()
        })

        # Determine target service based on task type
        topic_name = get_topic_for_task_type(task_request.task_type)
        topic_path = publisher.topic_path(PROJECT_ID, topic_name)

        # Prepare message
        message_data = {
            "task_id": task_id,
            "task_type": task_request.task_type.value,
            "parameters": task_request.parameters,
            "priority": task_request.priority,
            "client_id": task_request.client_id
        }

        # Publish message
        message_json = json.dumps(message_data, default=str)
        future = publisher.publish(topic_path, message_json.encode())

        logger.info(f"Queued task {task_id} to topic {topic_name}")

    except Exception as e:
        logger.error(f"Error queuing research task: {str(e)}")
        # Update task status to failed
        db.collection("research_tasks").document(task_id).update({
            "status": ResearchTaskStatus.FAILED.value,
            "error": str(e),
            "failed_at": datetime.utcnow()
        })

def get_topic_for_task_type(task_type: ResearchTaskType) -> str:
    """Map task type to Pub/Sub topic."""
    topic_mapping = {
        ResearchTaskType.MARKET_INTELLIGENCE: "xynergy-market-intelligence-events",
        ResearchTaskType.COMPETITIVE_ANALYSIS: "xynergy-competitive-analysis-events",
        ResearchTaskType.CONTENT_RESEARCH: "xynergy-content-research-events",
        ResearchTaskType.TREND_ANALYSIS: "trend-identified"
    }
    return topic_mapping.get(task_type, "research-complete")

def calculate_estimated_completion(task_type: ResearchTaskType) -> datetime:
    """Calculate estimated completion time based on task type."""
    base_time = datetime.utcnow()

    if task_type == ResearchTaskType.MARKET_INTELLIGENCE:
        return base_time + timedelta(minutes=45)
    elif task_type == ResearchTaskType.COMPETITIVE_ANALYSIS:
        return base_time + timedelta(hours=2)
    elif task_type == ResearchTaskType.CONTENT_RESEARCH:
        return base_time + timedelta(hours=1)
    else:
        return base_time + timedelta(hours=1)

async def initiate_research_task(task_request: ResearchTaskRequest) -> Dict[str, Any]:
    """Helper function for workflow execution."""
    background_tasks = BackgroundTasks()
    response = await create_research_task(task_request, background_tasks)
    return response.dict()

# Dashboard endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Research Coordinator dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Research Coordinator Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
            .stat { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
            .tasks { margin-top: 20px; }
            .task { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 3px; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Research Coordinator Dashboard</h1>
            <p>Orchestrating market intelligence, competitive analysis, and content research</p>
        </div>

        <div class="stats">
            <div class="stat">
                <h3 id="active-tasks">0</h3>
                <p>Active Tasks</p>
            </div>
            <div class="stat">
                <h3 id="completed-today">0</h3>
                <p>Completed Today</p>
            </div>
            <div class="stat">
                <h3 id="avg-response-time">0m</h3>
                <p>Avg Response Time</p>
            </div>
            <div class="stat">
                <h3 id="success-rate">0%</h3>
                <p>Success Rate</p>
            </div>
        </div>

        <div>
            <h2>Quick Actions</h2>
            <button class="button" onclick="startMarketIntelligence()">Market Intelligence</button>
            <button class="button" onclick="startCompetitiveAnalysis()">Competitive Analysis</button>
            <button class="button" onclick="startContentResearch()">Content Research</button>
        </div>

        <div class="tasks">
            <h2>Recent Tasks</h2>
            <div id="task-list">Loading...</div>
        </div>

        <script>
            async function startMarketIntelligence() {
                const response = await fetch('/market-intelligence', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        monitoring_categories: ['seo_tools', 'ai_platforms'],
                        business_context: 'SEO and AI platform monitoring'
                    })
                });
                const result = await response.json();
                alert('Market intelligence task started: ' + result.task_id);
                loadTasks();
            }

            async function startCompetitiveAnalysis() {
                const urls = prompt('Enter competitor URLs (comma-separated):');
                if (!urls) return;

                const response = await fetch('/competitive-analysis', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        competitor_urls: urls.split(',').map(u => u.trim()),
                        analysis_depth: 'standard'
                    })
                });
                const result = await response.json();
                alert('Competitive analysis task started: ' + result.task_id);
                loadTasks();
            }

            async function startContentResearch() {
                const keywords = prompt('Enter target keywords (comma-separated):');
                if (!keywords) return;

                const response = await fetch('/content-research', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        business_type: 'SEO Services',
                        target_keywords: keywords.split(',').map(k => k.trim()),
                        competitor_analysis: true,
                        trend_correlation: true
                    })
                });
                const result = await response.json();
                alert('Content research task started: ' + result.task_id);
                loadTasks();
            }

            async function loadTasks() {
                // This would load recent tasks from the API
                document.getElementById('task-list').innerHTML = '<div class="task">Sample task - Market Intelligence - In Progress</div>';
            }

            // Load initial data
            loadTasks();
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)