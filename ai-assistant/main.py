from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from google.cloud import pubsub_v1, firestore
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
performance_monitor = PerformanceMonitor("ai-assistant")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3, timeout=30))

# FastAPI app
app = FastAPI(
    title="Xynergy AI Assistant - Platform Brain",
    description="Central coordinator for all Xynergy platform services and business operations",
    version="2.0.0"
)

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

class WorkflowStep(BaseModel):
    service: str
    action: str
    parameters: Dict[str, Any]
    depends_on: Optional[List[str]] = []

class WorkflowPlan(BaseModel):
    workflow_id: str
    business_intent: str
    steps: List[WorkflowStep]
    estimated_duration: int
    priority: str = "normal"

class PlatformResponse(BaseModel):
    success: bool
    workflow_id: Optional[str] = None
    results: Dict[str, Any]
    execution_time: float
    services_used: List[str]

# Active WebSocket connections for real-time updates
active_connections: List[WebSocket] = []

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-assistant-brain",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "services_available": len(SERVICE_REGISTRY),
        "platform_status": "unified"
    }

# Root endpoint with comprehensive platform interface
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Xynergy AI Assistant - Platform Brain</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; }
                .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
                .service-card { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; }
                .feature-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
                .feature { background: #e3f2fd; padding: 15px; border-radius: 8px; }
                .chat-interface { background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .status-indicator { display: inline-block; width: 12px; height: 12px; background: #28a745; border-radius: 50%; margin-right: 8px; }
            </style>
        </head>
        <body>
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
        </body>
    </html>
    """

# Main business execution endpoint - natural language interface
@app.post("/business/execute", response_model=PlatformResponse)
async def execute_business_intent(request: BusinessRequest):
    start_time = datetime.utcnow()
    workflow_id = str(uuid.uuid4())

    try:
        with performance_monitor.track_operation("business_execution"):
            # Analyze business intent and create workflow plan
            workflow_plan = await analyze_and_plan_workflow(request.intent, request.context, workflow_id)

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

            logger.info(f"Business intent executed successfully: {workflow_id} in {execution_time:.2f}s")

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
        async with httpx.AsyncClient(timeout=10.0) as client:
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
    """Analyze business intent and create intelligent workflow plan"""
    
    # AI-powered intent analysis and service selection
    intent_lower = intent.lower()
    steps = []
    
    # Marketing related intents
    if any(word in intent_lower for word in ["marketing", "campaign", "advertise", "promote", "seo", "keywords"]):
        steps.extend([
            WorkflowStep(service="marketing-engine", action="analyze_market", parameters={"intent": intent, "context": context}),
            WorkflowStep(service="content-hub", action="prepare_assets", parameters={"campaign_type": "marketing"}),
            WorkflowStep(service="analytics-data-layer", action="setup_tracking", parameters={"campaign_id": workflow_id})
        ])
    
    # Project management intents
    if any(word in intent_lower for word in ["project", "plan", "manage", "execute", "delivery", "timeline"]):
        steps.extend([
            WorkflowStep(service="project-management", action="create_project", parameters={"intent": intent, "workflow_id": workflow_id}),
            WorkflowStep(service="scheduler-automation-engine", action="setup_automation", parameters={"project_id": workflow_id}),
            WorkflowStep(service="qa-engine", action="setup_quality_gates", parameters={"project_id": workflow_id})
        ])
    
    # Analytics and reporting intents
    if any(word in intent_lower for word in ["analyze", "report", "metrics", "data", "insights", "performance"]):
        steps.extend([
            WorkflowStep(service="analytics-data-layer", action="analyze_data", parameters={"intent": intent, "context": context}),
            WorkflowStep(service="reports-export", action="generate_report", parameters={"analysis_id": workflow_id}),
            WorkflowStep(service="platform-dashboard", action="update_metrics", parameters={"report_id": workflow_id})
        ])
    
    # Security and compliance intents
    if any(word in intent_lower for word in ["security", "audit", "compliance", "governance", "risk"]):
        steps.extend([
            WorkflowStep(service="security-governance", action="security_audit", parameters={"scope": intent, "context": context}),
            WorkflowStep(service="qa-engine", action="compliance_check", parameters={"audit_id": workflow_id})
        ])
    
    # Content creation intents
    if any(word in intent_lower for word in ["content", "create", "media", "assets", "design"]):
        steps.extend([
            WorkflowStep(service="content-hub", action="create_content", parameters={"intent": intent, "context": context}),
            WorkflowStep(service="qa-engine", action="quality_review", parameters={"content_id": workflow_id})
        ])
    
    # Default workflow if no specific intent detected
    if not steps:
        steps = [
            WorkflowStep(service="internal-ai-service", action="analyze_intent", parameters={"intent": intent, "context": context}),
            WorkflowStep(service="ai-routing-engine", action="route_request", parameters={"intent": intent})
        ]
    
    # Always add monitoring and coordination
    steps.append(WorkflowStep(service="system-runtime", action="coordinate_execution", parameters={"workflow_id": workflow_id}))
    
    return WorkflowPlan(
        workflow_id=workflow_id,
        business_intent=intent,
        steps=steps,
        estimated_duration=len(steps) * 30,
        priority="normal"
    )

async def execute_workflow(workflow_plan: WorkflowPlan) -> Dict[str, Any]:
    """Execute workflow steps across multiple services"""
    
    results = {}
    execution_context = {"workflow_id": workflow_plan.workflow_id}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for step in workflow_plan.steps:
            try:
                service_info = SERVICE_REGISTRY.get(step.service)
                if not service_info:
                    results[step.service] = {"error": f"Service {step.service} not found in registry"}
                    continue
                
                # Prepare step parameters
                step_params = {**step.parameters, **execution_context}

                # Execute step with circuit breaker protection
                async def execute_step():
                    return await client.post(
                        f"{service_info['url']}/execute",
                        json={
                            "action": step.action,
                            "parameters": step_params,
                            "workflow_context": execution_context
                        },
                        headers={"X-Workflow-ID": workflow_plan.workflow_id}
                    )

                response = await circuit_breaker.call(execute_step)

                if response.status_code == 200:
                    step_result = response.json()
                    results[step.service] = step_result

                    # Update execution context with results
                    if "output" in step_result:
                        execution_context.update(step_result["output"])
                else:
                    results[step.service] = {
                        "error": f"HTTP {response.status_code}",
                        "details": response.text
                    }
                
            except Exception as e:
                results[step.service] = {"error": str(e)}
                logger.error(f"Error executing step {step.service}.{step.action}: {str(e)}")
    
    return results

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
