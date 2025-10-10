from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from google.cloud import pubsub_v1, firestore

# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import os
import uvicorn
import logging
import asyncio
import json
import httpx
from datetime import datetime
import uuid
import sys

# Import Phase 2 utilities
from phase2_utils import PerformanceMonitor, CircuitBreaker, CircuitBreakerConfig

# Import centralized authentication
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from auth import verify_api_key, verify_api_key_optional
from http_client import get_http_client

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))

# Initialize GCP clients
publisher = get_publisher_client()  # Phase 4: Shared connection pooling
db = get_firestore_client()  # Phase 4: Shared connection pooling

# Initialize monitoring and tracing
performance_monitor = PerformanceMonitor("ai-assistant")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3, timeout=30))

# FastAPI app
app = FastAPI(
    title="Xynergy AI Assistant - Platform Brain",
    description="Central coordinator for all Xynergy platform services and business operations",
    version="2.0.0"
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
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "X-Workflow-ID"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "ai-assistant"}'
)
logger = logging.getLogger(__name__)

# Service Registry - All platform services
SERVICE_REGISTRY = {
    "platform-dashboard": {"url": "https://xynergy-platform-dashboard-835612502919.us-central1.run.app", "capabilities": ["monitoring", "metrics", "status"]},
    "marketing-engine": {"url": "https://xynergy-marketing-engine-835612502919.us-central1.run.app", "capabilities": ["campaigns", "keywords", "marketing"]},
    "analytics-data-layer": {"url": "https://xynergy-analytics-data-layer-835612502919.us-central1.run.app", "capabilities": ["analytics", "data", "insights"]},
    "content-hub": {"url": "https://xynergy-content-hub-835612502919.us-central1.run.app", "capabilities": ["content", "assets", "media"]},
    "project-management": {"url": "https://xynergy-project-management-835612502919.us-central1.run.app", "capabilities": ["projects", "tasks", "planning"]},
    "qa-engine": {"url": "https://xynergy-qa-engine-835612502919.us-central1.run.app", "capabilities": ["quality", "testing", "validation"]},
    "reports-export": {"url": "https://xynergy-reports-export-835612502919.us-central1.run.app", "capabilities": ["reports", "export", "visualization"]},
    "scheduler-automation-engine": {"url": "https://xynergy-scheduler-automation-engine-835612502919.us-central1.run.app", "capabilities": ["scheduling", "automation", "workflows"]},
    "secrets-config": {"url": "https://xynergy-secrets-config-835612502919.us-central1.run.app", "capabilities": ["configuration", "secrets", "settings"]},
    "security-governance": {"url": "https://xynergy-security-governance-835612502919.us-central1.run.app", "capabilities": ["security", "governance", "compliance"]},
    "system-runtime": {"url": "https://xynergy-system-runtime-835612502919.us-central1.run.app", "capabilities": ["system", "runtime", "coordination"]},
    "xynergy-competency-engine": {"url": "https://xynergy-competency-engine-835612502919.us-central1.run.app", "capabilities": ["competency", "assessment", "development"]},
    "ai-routing-engine": {"url": "https://xynergy-ai-routing-engine-835612502919.us-central1.run.app", "capabilities": ["routing", "classification", "ai"]},
    "internal-ai-service": {"url": "https://xynergy-internal-ai-service-835612502919.us-central1.run.app", "capabilities": ["ai", "processing", "intelligence"]}
}

# Data models
class BusinessRequest(BaseModel):
    intent: str
    context: Optional[Dict[str, Any]] = {}
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = []
    follow_up: Optional[bool] = False

class WorkflowStep(BaseModel):
    step_id: str
    service: str
    action: str
    parameters: Dict[str, Any]
    depends_on: Optional[List[str]] = []
    retry_count: Optional[int] = 0
    max_retries: Optional[int] = 3
    timeout: Optional[int] = 30
    rollback_action: Optional[str] = None
    rollback_parameters: Optional[Dict[str, Any]] = {}

class WorkflowPlan(BaseModel):
    workflow_id: str
    business_intent: str
    steps: List[WorkflowStep]
    estimated_duration: int
    priority: str = "normal"
    enable_rollback: bool = True
    max_parallel_steps: int = 3

class WorkflowExecutionState:
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.completed_steps: Dict[str, Dict[str, Any]] = {}
        self.failed_steps: Dict[str, Dict[str, Any]] = {}
        self.executing_steps: Dict[str, asyncio.Task] = {}
        self.rollback_stack: List[Dict[str, Any]] = []
        self.execution_context: Dict[str, Any] = {"workflow_id": workflow_id}

class PlatformResponse(BaseModel):
    success: bool
    workflow_id: Optional[str] = None
    results: Dict[str, Any]
    execution_time: float
    services_used: List[str]

# Active WebSocket connections for real-time updates
active_connections: List[WebSocket] = []

# Conversation context management with TTL to prevent memory leaks
from cachetools import TTLCache

# Use TTL cache: max 1000 conversations, 1 hour TTL
conversation_contexts = TTLCache(maxsize=1000, ttl=3600)

async def get_conversation_context(session_id: str, user_id: str) -> Dict[str, Any]:
    """Retrieve conversation context from memory and Firestore"""
    context_key = f"{user_id}_{session_id}"

    # Check in-memory cache first
    if context_key in conversation_contexts:
        return conversation_contexts[context_key]

    # Load from Firestore if not in memory
    try:
        doc_ref = db.collection("conversation_contexts").document(context_key)
        doc = doc_ref.get()
        if doc.exists:
        context = doc.to_dict()
        conversation_contexts[context_key] = context  # Cache in memory
        return context
    except Exception as e:
        logger.warning(f"Failed to load conversation context: {e}")

    # Return empty context if none found
    return {"conversation_history": [], "user_preferences": {}, "business_context": {}}

async def update_conversation_context(session_id: str, user_id: str, intent: str, workflow_result: Dict[str, Any]):
    """Update conversation context with new interaction"""
    context_key = f"{user_id}_{session_id}"

    # Get current context
    current_context = await get_conversation_context(session_id, user_id)

    # Add new interaction to history
    interaction = {
        "timestamp": datetime.utcnow().isoformat(),
        "intent": intent,
        "workflow_id": workflow_result.get("workflow_id"),
        "services_used": workflow_result.get("services_used", []),
        "success": workflow_result.get("success", False)
    }

    current_context["conversation_history"].append(interaction)

    # Limit history to last 10 interactions to prevent memory bloat
    current_context["conversation_history"] = current_context["conversation_history"][-10:]

    # Extract business preferences and context
    if "business_type" in workflow_result.get("context", {}):
        current_context["business_context"]["business_type"] = workflow_result["context"]["business_type"]

    # Cache in memory and persist to Firestore
    conversation_contexts[context_key] = current_context

    try:
        doc_ref = db.collection("conversation_contexts").document(context_key)
        doc_ref.set(current_context, merge=True)
    except Exception as e:
        logger.warning(f"Failed to persist conversation context: {e}")

async def analyze_context_for_intent(intent: str, conversation_history: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze conversation history to enhance intent understanding"""
    enhanced_context = dict(context)

    if not conversation_history:
        return enhanced_context

    # Extract patterns from recent interactions
    recent_services = []
    recent_scenarios = []

    for interaction in conversation_history[-3:]:  # Look at last 3 interactions
        recent_services.extend(interaction.get("services_used", []))
        if "scenario" in interaction:
        recent_scenarios.append(interaction["scenario"])

    # Context enrichment based on history
    enhanced_context["recent_services"] = list(set(recent_services))
    enhanced_context["conversation_flow"] = len(conversation_history)

    # Detect follow-up intent patterns
    follow_up_indicators = ["also", "additionally", "then", "next", "after that", "now"]
    if any(indicator in intent.lower() for indicator in follow_up_indicators):
        enhanced_context["is_follow_up"] = True
        enhanced_context["previous_workflow"] = conversation_history[-1] if conversation_history else None

    # Business context inheritance
    for interaction in reversed(conversation_history):
        if "business_type" in interaction and "business_type" not in enhanced_context:
        enhanced_context["business_type"] = interaction["business_type"]
        break

    return enhanced_context

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-assistant-brain",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "services_available": len(SERVICE_REGISTRY),
        "platform_status": "unified",
        "features": {
        "dependency_management": True,
        "rollback_capabilities": True,
        "parallel_execution": True,
        "context_awareness": True,
        "enterprise_grade": True
        }
    }

@app.get("/workflow/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get detailed workflow execution status"""
    try:
        # Get workflow execution record from Firestore
        doc_ref = db.collection("workflow_executions").document(workflow_id)
        doc = doc_ref.get()

        if doc.exists:
        workflow_data = doc.to_dict()

        # Add real-time execution status
        execution_status = {
            "workflow_id": workflow_id,
            "status": workflow_data.get("status", "unknown"),
            "business_intent": workflow_data.get("business_intent", ""),
            "created_at": workflow_data.get("created_at"),
            "completed_at": workflow_data.get("completed_at"),
            "execution_results": workflow_data.get("execution_results", {}),
            "services_used": [step.get("service") for step in workflow_data.get("workflow_plan", {}).get("steps", [])],
            "circuit_breaker_status": {
                "state": circuit_breaker.state,
                "failure_count": circuit_breaker.failure_count
            }
        }

        return execution_status
        else:
        raise HTTPException(status_code=404, detail="Workflow not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving workflow status: {str(e)}")

@app.post("/workflow/retry/{workflow_id}")
async def retry_failed_workflow(workflow_id: str):
    """Retry a failed workflow with enhanced error handling"""
    try:
        # Get original workflow from Firestore
        doc_ref = db.collection("workflow_executions").document(workflow_id)
        doc = doc_ref.get()

        if not doc.exists:
        raise HTTPException(status_code=404, detail="Workflow not found")

        workflow_data = doc.to_dict()

        if workflow_data.get("status") != "failed":
        raise HTTPException(status_code=400, detail="Only failed workflows can be retried")

        # Create new workflow with enhanced error handling
        original_plan = workflow_data["workflow_plan"]
        enhanced_steps = []

        for step_data in original_plan["steps"]:
        enhanced_step = WorkflowStep(
            step_id=step_data.get("step_id", f"retry_{step_data['service']}"),
            service=step_data["service"],
            action=step_data["action"],
            parameters=step_data["parameters"],
            depends_on=step_data.get("depends_on", []),
            max_retries=5,  # Increased retry count for failed workflow
            timeout=60      # Extended timeout
        )
        enhanced_steps.append(enhanced_step)

        # Create enhanced workflow plan
        enhanced_plan = WorkflowPlan(
        workflow_id=f"{workflow_id}_retry_{int(datetime.utcnow().timestamp())}",
        business_intent=workflow_data["business_intent"],
        steps=enhanced_steps,
        estimated_duration=len(enhanced_steps) * 45,
        priority="high",
        enable_rollback=True,
        max_parallel_steps=2  # Reduced parallelism for stability
        )

        # Execute enhanced workflow
        execution_results = await execute_workflow(enhanced_plan)

        return {
        "success": True,
        "original_workflow_id": workflow_id,
        "retry_workflow_id": enhanced_plan.workflow_id,
        "results": execution_results
        }

    except Exception as e:
        logger.error(f"Error retrying workflow {workflow_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retry workflow: {str(e)}")

# Root endpoint with comprehensive platform interface
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
        <title>Xynergy AI Assistant - Platform Brain</title>
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

            .services-grid, .feature-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
                gap: 32px;
                margin: 32px 0 48px 0;
            }

            .service-card, .feature {
                background: rgba(255,255,255,0.05);
                padding: 32px 24px;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .service-card::before, .feature::before {
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

            .service-card:hover, .feature:hover {
                transform: translateY(-3px);
                background: rgba(255,255,255,0.08);
                border-color: rgba(59, 130, 246, 0.3);
            }

            .service-card:hover::before, .feature:hover::before {
                opacity: 1;
            }

            .service-card h3, .feature h3 {
                font-size: 1.3rem;
                margin-bottom: 24px;
                color: #3b82f6;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .chat-interface {
                background: rgba(59, 130, 246, 0.08);
                padding: 32px 24px;
                border-radius: 16px;
                margin: 32px 0;
                border: 1px solid rgba(59, 130, 246, 0.15);
                transition: all 0.3s ease;
            }

            .chat-interface:hover {
                background: rgba(59, 130, 246, 0.12);
            }

            .chat-interface h2 {
                color: #60a5fa;
                margin-bottom: 16px;
                font-size: 1.5rem;
            }

            .chat-interface p {
                margin-bottom: 16px;
                line-height: 1.6;
            }

            .chat-interface ul {
                list-style: none;
                padding-left: 0;
            }

            .chat-interface li {
                margin-bottom: 8px;
                padding: 12px 16px;
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
                border-left: 3px solid #3b82f6;
                transition: all 0.2s ease;
            }

            .chat-interface li:hover {
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
                .services-grid, .feature-list {
                    grid-template-columns: 1fr;
                    gap: 24px;
                }

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
                <h1>🧠 Xynergy AI Assistant - Platform Brain</h1>
                <p><span class="status-indicator"></span>Central coordinator for all Xynergy platform services</p>
                <p><strong>15 Services Online</strong> | <strong>Platform Status: Unified</strong> | <strong>Version: 2.0.0</strong></p>
            </div>
            
            <div class="chat-interface">
                <h2>🗣️ Conversational Business Interface</h2>
                <p><strong>Tell me what you want to accomplish, and I'll orchestrate the entire platform to make it happen:</strong></p>
                <ul>
                    <li>"Launch a marketing campaign for my tech startup targeting developers"</li>
                    <li>"Analyze our Q3 performance and create a comprehensive report"</li>
                    <li>"Set up automated content creation and social media scheduling"</li>
                    <li>"Conduct a security audit and implement governance policies"</li>
                    <li>"Plan and execute a complete product launch project"</li>
                </ul>
                <p><em>Use POST /business/execute with natural language intent</em></p>
            </div>

            <div class="feature-list">
                <div class="feature">
                    <h3>🎯 Autonomous Marketing</h3>
                    <p>Complete campaign creation, keyword research, content generation, and performance tracking</p>
                </div>
                <div class="feature">
                    <h3>📊 Business Intelligence</h3>
                    <p>Real-time analytics, data processing, comprehensive reporting, and insights generation</p>
                </div>
                <div class="feature">
                    <h3>🚀 Project Execution</h3>
                    <p>End-to-end project planning, task coordination, team management, and delivery tracking</p>
                </div>
                <div class="feature">
                    <h3>🔒 Security & Governance</h3>
                    <p>Zero-trust architecture, compliance monitoring, risk assessment, and governance automation</p>
                </div>
                <div class="feature">
                    <h3>🎨 Content Operations</h3>
                    <p>Asset management, content creation, media processing, and distribution coordination</p>
                </div>
                <div class="feature">
                    <h3>🔧 Quality Assurance</h3>
                    <p>Automated testing, validation workflows, quality control, and performance optimization</p>
                </div>
            </div>

            <h2>🏗️ Platform Services</h2>
            <div class="services-grid">
                <div class="service-card">
                    <h3>📊 Analytics & Data Layer</h3>
                    <p>Business intelligence and data processing</p>
                </div>
                <div class="service-card">
                    <h3>🎯 Marketing Engine</h3>
                    <p>Campaign creation and keyword research</p>
                </div>
                <div class="service-card">
                    <h3>🚀 Project Management</h3>
                    <p>Autonomous project execution</p>
                </div>
                <div class="service-card">
                    <h3>🎨 Content Hub</h3>
                    <p>Asset management and content operations</p>
                </div>
                <div class="service-card">
                    <h3>🔒 Security & Governance</h3>
                    <p>Zero-trust monitoring and compliance</p>
                </div>
                <div class="service-card">
                    <h3>📈 Reports & Export</h3>
                    <p>Data visualization and reporting</p>
                </div>
            </div>

            <h2>🛠️ API Endpoints</h2>
            <ul>
                <li><strong>POST /business/execute</strong> - Execute any business intent through natural language</li>
                <li><strong>GET /platform/status</strong> - Complete platform health and service status</li>
                <li><strong>POST /workflows/create</strong> - Create custom multi-service workflows</li>
                <li><strong>GET /services/discover</strong> - Service discovery and capability mapping</li>
                <li><strong>WebSocket /ws/platform</strong> - Real-time platform updates and notifications</li>
                <li><strong>GET /health</strong> - AI Assistant health check</li>
            </ul>
        </div>
            </div>
        </div>
        </body>
    </html>
    """

# Main business execution endpoint - natural language interface
# SECURITY: Requires authentication for business operations
@app.post("/business/execute", response_model=PlatformResponse, dependencies=[Depends(verify_api_key)])
async def execute_business_intent(request: BusinessRequest):
    start_time = datetime.utcnow()
    workflow_id = str(uuid.uuid4())

    try:
        with performance_monitor.track_operation("business_execution"):
        # Get conversation context for context-aware processing
        session_id = request.session_id or "default_session"
        user_id = request.user_id or "anonymous_user"

        conversation_context = await get_conversation_context(session_id, user_id)

        # Enhance context with conversation history analysis
        enhanced_context = await analyze_context_for_intent(
            request.intent,
            conversation_context.get("conversation_history", []),
            request.context
        )

        # Merge business context from conversation history
        if conversation_context.get("business_context"):
            enhanced_context.update(conversation_context["business_context"])

        # Analyze business intent and create context-aware workflow plan
        workflow_plan = await analyze_and_plan_workflow(request.intent, enhanced_context, workflow_id)

        # Execute the workflow across multiple services
        execution_results = await execute_workflow(workflow_plan)

        # Store workflow execution record
        workflow_record = {
            "workflow_id": workflow_id,
            "business_intent": request.intent,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "workflow_plan": workflow_plan.dict(),
            "execution_results": execution_results,
            "created_at": start_time,
            "completed_at": datetime.utcnow(),
            "status": "completed"
        }

        db.collection("workflow_executions").document(workflow_id).set(workflow_record)

        # Broadcast to connected WebSockets
        await broadcast_workflow_update(workflow_id, "completed", execution_results)

        # Publish platform event
        platform_event = {
            "event_type": "business_intent_executed",
            "workflow_id": workflow_id,
            "intent": request.intent,
            "services_used": workflow_plan.steps,
            "timestamp": datetime.utcnow().isoformat()
        }

        topic_path = publisher.topic_path(PROJECT_ID, "xynergy-platform-events")
        publisher.publish(topic_path, json.dumps(platform_event).encode())

        execution_time = (datetime.utcnow() - start_time).total_seconds()
        services_used = list(set([step.service for step in workflow_plan.steps]))

        # Update conversation context with this interaction
        workflow_result = {
            "success": True,
            "workflow_id": workflow_id,
            "services_used": services_used,
            "context": enhanced_context
        }
        await update_conversation_context(session_id, user_id, request.intent, workflow_result)

        logger.info(f"Business intent executed successfully: {workflow_id} in {execution_time:.2f}s using context-aware processing")

        return PlatformResponse(
            success=True,
            workflow_id=workflow_id,
            results=execution_results,
            execution_time=execution_time,
            services_used=services_used
        )

    except Exception as e:
        logger.error(f"Error executing business intent: {str(e)}")
        await broadcast_workflow_update(workflow_id, "failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Failed to execute business intent: {str(e)}")

# Platform status and service discovery
@app.get("/platform/status")
async def get_platform_status():
    try:
        service_health = {}
        
        # Check health of all services
        client = await get_http_client()
        for service_name, service_info in SERVICE_REGISTRY.items():
            try:
                response = await client.get(f"{service_info['url']}/health")
                service_health[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": service_info["url"],
                    "capabilities": service_info["capabilities"],
                    "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None
                }
            except Exception as e:
                service_health[service_name] = {
                    "status": "unreachable",
                    "url": service_info["url"],
                    "capabilities": service_info["capabilities"],
                    "error": str(e)
                }
        
        # Calculate platform metrics
        healthy_services = sum(1 for s in service_health.values() if s["status"] == "healthy")
        total_services = len(service_health)
        platform_health = "healthy" if healthy_services == total_services else "degraded" if healthy_services > total_services * 0.8 else "critical"
        
        return {
        "platform_health": platform_health,
        "healthy_services": healthy_services,
        "total_services": total_services,
        "service_health": service_health,
        "platform_capabilities": list(set([cap for service in SERVICE_REGISTRY.values() for cap in service["capabilities"]])),
        "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting platform status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get platform status: {str(e)}")

# Service discovery endpoint
@app.get("/services/discover")
async def discover_services():
    return {
        "total_services": len(SERVICE_REGISTRY),
        "services": SERVICE_REGISTRY,
        "capability_map": {
        cap: [service for service, info in SERVICE_REGISTRY.items() if cap in info["capabilities"]]
        for cap in set([cap for service in SERVICE_REGISTRY.values() for cap in service["capabilities"]])
        }
    }

# Create custom workflows
@app.post("/workflows/create", response_model=WorkflowPlan)
async def create_workflow(steps: List[WorkflowStep], business_intent: str):
    try:
        workflow_id = str(uuid.uuid4())
        
        # Validate steps and dependencies
        validated_steps = await validate_workflow_steps(steps)
        
        workflow_plan = WorkflowPlan(
        workflow_id=workflow_id,
        business_intent=business_intent,
        steps=validated_steps,
        estimated_duration=len(validated_steps) * 30,  # Estimate 30 seconds per step
        priority="normal"
        )
        
        # Store workflow template
        db.collection("workflow_templates").document(workflow_id).set(workflow_plan.dict())
        
        logger.info(f"Workflow template created: {workflow_id}")
        
        return workflow_plan
        
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")

# WebSocket endpoint for real-time platform updates
@app.websocket("/ws/platform")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial platform status
        status = await get_platform_status()
        await websocket.send_json({
        "type": "platform_status",
        "data": status,
        "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
        # Keep connection alive and listen for messages
        try:
            data = await websocket.receive_text()
            # Echo back any messages for testing
            await websocket.send_json({
                "type": "echo",
                "message": data,
                "timestamp": datetime.utcnow().isoformat()
            })
        except WebSocketDisconnect:
            break
            
    except WebSocketDisconnect:
        pass
    finally:
        active_connections.remove(websocket)

# Helper functions
async def analyze_and_plan_workflow(intent: str, context: Dict[str, Any], workflow_id: str) -> WorkflowPlan:
    """Enhanced AI-powered intent analysis and intelligent workflow planning for complex business scenarios"""

    intent_lower = intent.lower()
    steps = []
    priority = "normal"

    # Complex business scenario patterns
    complex_scenarios = {
        "product_launch": ["launch", "product", "rollout", "introduce", "debut"],
        "market_expansion": ["expand", "growth", "scale", "new market", "territory"],
        "customer_acquisition": ["acquire", "customers", "onboard", "convert", "leads"],
        "brand_campaign": ["brand", "awareness", "visibility", "recognition", "reputation"],
        "digital_transformation": ["digital", "transform", "modernize", "digitize", "automate"],
        "compliance_audit": ["comply", "audit", "regulation", "governance", "standards"],
        "crisis_management": ["crisis", "urgent", "emergency", "critical", "immediate"]
    }

    # Detect complex business scenarios
    detected_scenario = None
    for scenario, keywords in complex_scenarios.items():
        if any(keyword in intent_lower for keyword in keywords):
        detected_scenario = scenario
        break

    # Enhanced intent classification with context awareness and dependency management
    if detected_scenario == "product_launch":
        priority = "high"
        steps.extend([
        WorkflowStep(
            step_id="project_setup", service="project-management", action="create_project",
            parameters={"intent": intent, "workflow_id": workflow_id, "project_type": "product_launch"},
            rollback_action="delete_project", rollback_parameters={"project_id": workflow_id}
        ),
        WorkflowStep(
            step_id="market_analysis", service="marketing-engine", action="analyze_market",
            parameters={"intent": intent, "context": context, "campaign_type": "product_launch"},
            depends_on=["project_setup"]
        ),
        WorkflowStep(
            step_id="content_creation", service="content-hub", action="create_content",
            parameters={"content_type": "launch_materials", "campaign_id": workflow_id},
            depends_on=["market_analysis"],
            rollback_action="delete_content", rollback_parameters={"campaign_id": workflow_id}
        ),
        WorkflowStep(
            step_id="analytics_setup", service="analytics-data-layer", action="setup_tracking",
            parameters={"event_type": "product_launch", "campaign_id": workflow_id},
            depends_on=["project_setup"]
        ),
        WorkflowStep(
            step_id="quality_gates", service="qa-engine", action="setup_quality_gates",
            parameters={"project_id": workflow_id, "quality_type": "launch_readiness"},
            depends_on=["content_creation", "analytics_setup"]
        )
        ])

    elif detected_scenario == "market_expansion":
        priority = "high"
        steps.extend([
        WorkflowStep(
            step_id="market_opportunity", service="analytics-data-layer", action="analyze_data",
            parameters={"analysis_type": "market_opportunity", "target_market": context.get("target_market", "")}
        ),
        WorkflowStep(
            step_id="market_analysis", service="marketing-engine", action="analyze_market",
            parameters={"intent": intent, "context": context, "scope": "expansion"},
            depends_on=["market_opportunity"]
        ),
        WorkflowStep(
            step_id="expansion_project", service="project-management", action="create_project",
            parameters={"project_type": "market_expansion", "workflow_id": workflow_id},
            depends_on=["market_analysis"],
            rollback_action="delete_project", rollback_parameters={"project_id": workflow_id}
        ),
        WorkflowStep(
            step_id="compliance_check", service="security-governance", action="compliance_check",
            parameters={"scope": "market_regulations", "target_market": context.get("target_market", "")},
            depends_on=["market_opportunity"]
        )
        ])

    elif detected_scenario == "crisis_management":
        priority = "critical"
        steps.extend([
        WorkflowStep(service="platform-dashboard", action="monitor_workflow", parameters={
            "alert_level": "critical", "workflow_id": workflow_id
        }),
        WorkflowStep(service="security-governance", action="security_audit", parameters={
            "priority": "emergency", "scope": intent
        }),
        WorkflowStep(service="content-hub", action="create_content", parameters={
            "content_type": "crisis_communication", "urgency": "high"
        }),
        WorkflowStep(service="system-runtime", action="coordinate_execution", parameters={
            "priority": "critical", "workflow_id": workflow_id
        })
        ])

    # Standard intent patterns with enhanced context awareness
    elif any(word in intent_lower for word in ["marketing", "campaign", "advertise", "promote", "seo", "keywords"]):
        campaign_type = context.get("campaign_type", "general")
        target_audience = context.get("target_audience", "general")

        steps.extend([
        WorkflowStep(service="marketing-engine", action="analyze_market", parameters={
            "intent": intent, "context": context, "campaign_type": campaign_type
        }),
        WorkflowStep(service="content-hub", action="prepare_assets", parameters={
            "campaign_type": campaign_type, "target_audience": target_audience
        }),
        WorkflowStep(service="analytics-data-layer", action="setup_tracking", parameters={
            "campaign_id": workflow_id, "tracking_type": "marketing"
        })
        ])

    elif any(word in intent_lower for word in ["project", "plan", "manage", "execute", "delivery", "timeline"]):
        project_type = context.get("project_type", "general")

        steps.extend([
        WorkflowStep(service="project-management", action="create_project", parameters={
            "intent": intent, "workflow_id": workflow_id, "project_type": project_type
        }),
        WorkflowStep(service="scheduler-automation-engine", action="setup_automation", parameters={
            "project_id": workflow_id, "automation_type": project_type
        }),
        WorkflowStep(service="qa-engine", action="setup_quality_gates", parameters={
            "project_id": workflow_id, "project_type": project_type
        })
        ])

    elif any(word in intent_lower for word in ["analyze", "report", "metrics", "data", "insights", "performance"]):
        analysis_type = context.get("analysis_type", "general")

        steps.extend([
        WorkflowStep(service="analytics-data-layer", action="analyze_data", parameters={
            "intent": intent, "context": context, "analysis_type": analysis_type
        }),
        WorkflowStep(service="reports-export", action="generate_report", parameters={
            "analysis_id": workflow_id, "report_type": analysis_type
        }),
        WorkflowStep(service="platform-dashboard", action="update_metrics", parameters={
            "report_id": workflow_id, "metric_type": analysis_type
        })
        ])

    elif any(word in intent_lower for word in ["security", "audit", "compliance", "governance", "risk"]):
        audit_scope = context.get("audit_scope", intent)

        steps.extend([
        WorkflowStep(service="security-governance", action="security_audit", parameters={
            "scope": audit_scope, "context": context
        }),
        WorkflowStep(service="qa-engine", action="compliance_check", parameters={
            "audit_id": workflow_id, "compliance_type": audit_scope
        })
        ])

    elif any(word in intent_lower for word in ["content", "create", "media", "assets", "design"]):
        content_type = context.get("content_type", "general")

        steps.extend([
        WorkflowStep(service="content-hub", action="create_content", parameters={
            "intent": intent, "context": context, "content_type": content_type
        }),
        WorkflowStep(service="qa-engine", action="quality_review", parameters={
            "content_id": workflow_id, "review_type": content_type
        })
        ])

    # Competency assessment for complex tasks
    elif any(word in intent_lower for word in ["learn", "assess", "skill", "competency", "training"]):
        steps.extend([
        WorkflowStep(service="xynergy-competency-engine", action="assess_competency", parameters={
            "intent": intent, "context": context, "assessment_type": "comprehensive"
        }),
        WorkflowStep(service="project-management", action="create_project", parameters={
            "project_type": "learning_path", "workflow_id": workflow_id
        })
        ])

    # AI routing for complex or unclear intents
    else:
        steps.extend([
        WorkflowStep(service="internal-ai-service", action="analyze_intent", parameters={
            "intent": intent, "context": context, "analysis_depth": "deep"
        }),
        WorkflowStep(service="ai-routing-engine", action="route_request", parameters={
            "intent": intent, "routing_strategy": "intelligent"
        })
        ])

    # Always add system coordination for workflow management
    steps.append(WorkflowStep(
        step_id="system_coordination", service="system-runtime", action="coordinate_execution",
        parameters={"workflow_id": workflow_id, "priority": priority, "scenario": detected_scenario}
    ))

    return WorkflowPlan(
        workflow_id=workflow_id,
        business_intent=intent,
        steps=steps,
        estimated_duration=len(steps) * 30,
        priority=priority
    )

async def execute_workflow(workflow_plan: WorkflowPlan) -> Dict[str, Any]:
    """Enhanced workflow execution with dependency management, parallel execution, and rollback capabilities"""

    state = WorkflowExecutionState(workflow_plan.workflow_id)

    try:
        # Execute workflow with dependency-aware scheduling
        await execute_workflow_with_dependencies(workflow_plan, state)

        return {
        "completed_steps": state.completed_steps,
        "failed_steps": state.failed_steps,
        "execution_context": state.execution_context,
        "rollback_performed": False
        }

    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")

        # Perform rollback if enabled
        if workflow_plan.enable_rollback and state.rollback_stack:
        logger.info(f"Performing rollback for workflow {workflow_plan.workflow_id}")
        await perform_rollback(state)
        return {
            "completed_steps": state.completed_steps,
            "failed_steps": state.failed_steps,
            "execution_context": state.execution_context,
            "rollback_performed": True,
            "rollback_error": str(e)
        }

        raise e

async def execute_workflow_with_dependencies(workflow_plan: WorkflowPlan, state: WorkflowExecutionState):
    """Execute workflow steps respecting dependencies and enabling parallel execution"""

    # Build dependency graph
    dependency_graph = {step.step_id: step for step in workflow_plan.steps}

    client = await get_http_client()
        while len(state.completed_steps) + len(state.failed_steps) < len(workflow_plan.steps):
        # Find ready steps (dependencies satisfied)
        ready_steps = get_ready_steps(dependency_graph, state)

        if not ready_steps:
            # Check if we have executing steps
            if state.executing_steps:
                # Wait for at least one executing step to complete
                done, pending = await asyncio.wait(
                    state.executing_steps.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                # Process completed tasks
                for task in done:
                    await process_completed_task(task, state)
            else:
                # No ready steps and nothing executing - check for failure
                remaining_steps = set(dependency_graph.keys()) - set(state.completed_steps.keys()) - set(state.failed_steps.keys())
                if remaining_steps:
                    raise Exception(f"Workflow deadlock: Cannot execute remaining steps {remaining_steps}")
                break
            continue

        # Execute ready steps (up to max_parallel_steps)
        for step in ready_steps[:workflow_plan.max_parallel_steps - len(state.executing_steps)]:
            task = asyncio.create_task(execute_single_step(step, state, client))
            state.executing_steps[step.step_id] = task

        # Wait for at least one step to complete if we're at parallel limit
        if len(state.executing_steps) >= workflow_plan.max_parallel_steps:
            done, pending = await asyncio.wait(
                state.executing_steps.values(),
                return_when=asyncio.FIRST_COMPLETED
            )
            for task in done:
                await process_completed_task(task, state)

        # Wait for all remaining tasks to complete
        if state.executing_steps:
        await asyncio.gather(*state.executing_steps.values(), return_exceptions=True)

def get_ready_steps(dependency_graph: Dict[str, WorkflowStep], state: WorkflowExecutionState) -> List[WorkflowStep]:
    """Get steps that are ready to execute (dependencies satisfied)"""
    ready_steps = []

    for step_id, step in dependency_graph.items():
        if (step_id not in state.completed_steps and
        step_id not in state.failed_steps and
        step_id not in state.executing_steps):

        # Check if all dependencies are satisfied
        dependencies_satisfied = all(
            dep_id in state.completed_steps for dep_id in step.depends_on
        )

        if dependencies_satisfied:
            ready_steps.append(step)

    return ready_steps

async def execute_single_step(step: WorkflowStep, state: WorkflowExecutionState, client: httpx.AsyncClient) -> Dict[str, Any]:
    """Execute a single workflow step with retry logic"""

    step_id = step.step_id

    for attempt in range(step.max_retries + 1):
        try:
        service_info = SERVICE_REGISTRY.get(step.service)
        if not service_info:
            raise Exception(f"Service {step.service} not found in registry")

        # Prepare step parameters with current context
        step_params = {**step.parameters, **state.execution_context}

        # Execute step with timeout
        response = await asyncio.wait_for(
            client.post(
                f"{service_info['url']}/execute",
                json={
                    "action": step.action,
                    "parameters": step_params,
                    "workflow_context": state.execution_context
                },
                headers={"X-Workflow-ID": state.workflow_id}
            ),
            timeout=step.timeout
        )

        if response.status_code == 200:
            step_result = response.json()

            # Add to rollback stack if rollback action defined
            if step.rollback_action:
                state.rollback_stack.append({
                    "step_id": step_id,
                    "service": step.service,
                    "rollback_action": step.rollback_action,
                    "rollback_parameters": step.rollback_parameters
                })

            return {
                "step_id": step_id,
                "success": True,
                "result": step_result,
                "attempt": attempt + 1
            }
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
        if attempt < step.max_retries:
            logger.warning(f"Step {step_id} attempt {attempt + 1} failed: {str(e)}, retrying...")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            continue
        else:
            return {
                "step_id": step_id,
                "success": False,
                "error": str(e),
                "attempts": attempt + 1
            }

async def process_completed_task(task: asyncio.Task, state: WorkflowExecutionState):
    """Process a completed workflow step task"""

    try:
        result = await task
        step_id = result["step_id"]

        # Remove from executing steps
        if step_id in state.executing_steps:
        del state.executing_steps[step_id]

        if result["success"]:
        state.completed_steps[step_id] = result

        # Update execution context with step output
        if "result" in result and "output" in result["result"]:
            state.execution_context.update(result["result"]["output"])

        logger.info(f"Step {step_id} completed successfully")
        else:
        state.failed_steps[step_id] = result
        logger.error(f"Step {step_id} failed: {result.get('error', 'Unknown error')}")

        # Check if this failure should stop the workflow
        raise Exception(f"Critical step {step_id} failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Error processing completed task: {str(e)}")
        raise e

async def perform_rollback(state: WorkflowExecutionState):
    """Perform rollback of completed steps in reverse order"""

    logger.info(f"Starting rollback for workflow {state.workflow_id}")

    client = await get_http_client()
        # Execute rollback actions in reverse order
        for rollback_info in reversed(state.rollback_stack):
        try:
            step_id = rollback_info["step_id"]
            service = rollback_info["service"]
            action = rollback_info["rollback_action"]
            parameters = rollback_info["rollback_parameters"]

            service_info = SERVICE_REGISTRY.get(service)
            if not service_info:
                logger.warning(f"Service {service} not found for rollback of step {step_id}")
                continue

            response = await client.post(
                f"{service_info['url']}/execute",
                json={
                    "action": action,
                    "parameters": parameters,
                    "workflow_context": {"workflow_id": state.workflow_id, "rollback": True}
                },
                headers={"X-Workflow-ID": state.workflow_id}
            )

            if response.status_code == 200:
                logger.info(f"Rollback successful for step {step_id}")
            else:
                logger.warning(f"Rollback failed for step {step_id}: HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"Error during rollback of step {rollback_info['step_id']}: {str(e)}")

    logger.info(f"Rollback completed for workflow {state.workflow_id}")

async def validate_workflow_steps(steps: List[WorkflowStep]) -> List[WorkflowStep]:
    """Validate workflow steps and dependencies"""
    
    validated_steps = []
    
    for step in steps:
        # Validate service exists
        if step.service not in SERVICE_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Service {step.service} not found")
        
        # Validate dependencies
        for dep in step.depends_on:
        if not any(s.service == dep for s in validated_steps):
            raise HTTPException(status_code=400, detail=f"Dependency {dep} not found in previous steps")
        
        validated_steps.append(step)
    
    return validated_steps

async def broadcast_workflow_update(workflow_id: str, status: str, data: Dict[str, Any]):
    """Broadcast workflow updates to all connected WebSocket clients"""
    
    message = {
        "type": "workflow_update",
        "workflow_id": workflow_id,
        "status": status,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send to all active WebSocket connections
    for connection in active_connections[:]:  # Copy list to avoid modification during iteration
        try:
        await connection.send_json(message)
        except Exception as e:
        logger.error(f"Error broadcasting to WebSocket: {str(e)}")
        # Remove broken connections
        active_connections.remove(connection)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
