from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from google.cloud import firestore, pubsub_v1, scheduler

# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

import os
import json
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uvicorn
from enum import Enum
import cron_descriptor

# Phase 2 enhancements
from phase2_utils import CircuitBreaker, CircuitBreakerConfig, call_service_with_circuit_breaker, PerformanceMonitor

# Import centralized authentication
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from auth import verify_api_key, verify_api_key_optional

PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")

# Initialize GCP clients
db = get_firestore_client()  # Phase 4: Shared connection pooling
publisher = get_publisher_client()  # Phase 4: Shared connection pooling
scheduler_client = scheduler.CloudSchedulerClient()

app = FastAPI(title="Xynergy Scheduler & Automation Engine", version="1.0.0")

# Phase 2 initialization
service_monitor = PerformanceMonitor("scheduler-automation-engine")
service_circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
ai_routing_circuit_breaker = CircuitBreaker(CircuitBreakerConfig())

# Phase 2 monitoring ready

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

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TriggerType(str, Enum):
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    MANUAL = "manual"
    DEPENDENCY = "dependency"

# Predefined workflow templates
WORKFLOW_TEMPLATES = {
    "marketing_campaign": {
        "name": "Marketing Campaign Automation",
        "description": "Complete marketing campaign creation and deployment",
        "steps": [
            {"service": "ai-assistant", "action": "analyze_brief", "timeout": 300},
            {"service": "marketing-engine", "action": "generate_content", "timeout": 600},
            {"service": "content-hub", "action": "store_assets", "timeout": 180},
            {"service": "qa-engine", "action": "review_content", "timeout": 300},
            {"service": "marketing-engine", "action": "schedule_posts", "timeout": 120}
        ]
    },
    "ai_cost_optimization": {
        "name": "AI Cost Optimization Check",
        "description": "Analyze and optimize AI routing for cost efficiency",
        "steps": [
            {"service": "analytics-data-layer", "action": "analyze_usage", "timeout": 180},
            {"service": "ai-routing-engine", "action": "optimize_routing", "timeout": 120},
            {"service": "internal-ai-service", "action": "adjust_models", "timeout": 240}
        ]
    },
    "platform_health_check": {
        "name": "Platform Health Monitoring",
        "description": "Comprehensive platform health and performance check",
        "steps": [
            {"service": "system-runtime", "action": "check_services", "timeout": 120},
            {"service": "analytics-data-layer", "action": "generate_metrics", "timeout": 180},
            {"service": "security-governance", "action": "security_scan", "timeout": 300}
        ]
    }
}

@app.get("/", response_class=HTMLResponse)
async def scheduler_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Xynergy Scheduler & Automation Engine</title>
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

            .grid, .services-grid, .feature-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
                gap: 32px;
                margin: 32px 0 48px 0;
            }

            .card, .service-card, .feature {
                background: rgba(255,255,255,0.05);
                padding: 32px 24px;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .card::before, .service-card::before, .feature::before {
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

            .card:hover, .service-card:hover, .feature:hover {
                transform: translateY(-3px);
                background: rgba(255,255,255,0.08);
                border-color: rgba(59, 130, 246, 0.3);
            }

            .card:hover::before, .service-card:hover::before, .feature:hover::before {
                opacity: 1;
            }

            .card h3, .service-card h3, .feature h3 {
                font-size: 1.3rem;
                margin-bottom: 24px;
                color: #3b82f6;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                background: #22c55e;
                border-radius: 50%;
                margin-right: 8px;
            }

            .btn, button {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.2s ease;
                font-size: 0.9rem;
            }

            .btn:hover, button:hover {
                background: #2563eb;
                transform: translateY(-1px);
            }

            @media (max-width: 768px) {
                .grid, .services-grid, .feature-list {
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
                <h1>⚡ Xynergy Scheduler & Automation Engine</h1>
                <p>Workflow orchestration and automated process management</p>
                <div style="display: flex; gap: 30px; margin-top: 15px;">
                    <div>Active Jobs: <span id="activeJobs">12</span></div>
                    <div>Completed Today: <span id="completedToday">47</span></div>
                    <div>Success Rate: <span style="color: #22c55e; font-weight: 700;">98.3%</span></div>
                </div>
            </div>
            
            <div class="grid">
                <div class="panel">
                    <h2>🔄 Active Workflows</h2>
                    <div id="activeWorkflows">
                        <div class="workflow-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <strong>Marketing Campaign Automation</strong>
                                    <div style="font-size: 14px; color: #94a3b8;">Started 2 minutes ago</div>
                                </div>
                                <span class="status running">Running</span>
                            </div>
                            
                            <div class="workflow-steps">
                                <div class="step">
                                    <div class="step-number">1</div>
                                    <div>
                                        <strong>AI Assistant</strong> - Analyze campaign brief
                                        <div style="font-size: 12px; color: #22c55e;">✓ Completed (45s)</div>
                                    </div>
                                </div>
                                <div class="step">
                                    <div class="step-number" style="background: #f59e0b;">2</div>
                                    <div>
                                        <strong>Marketing Engine</strong> - Generate content
                                        <div style="font-size: 12px; color: #f59e0b;">⟳ Running (1m 30s)</div>
                                    </div>
                                </div>
                                <div class="step">
                                    <div class="step-number" style="background: #64748b;">3</div>
                                    <div>
                                        <strong>Content Hub</strong> - Store assets
                                        <div style="font-size: 12px; color: #64748b;">⏳ Pending</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div style="display: flex; gap: 10px;">
                                <button class="btn stop" onclick="stopWorkflow('wf_123')">Stop</button>
                                <button class="btn" onclick="viewWorkflow('wf_123')">View Details</button>
                            </div>
                        </div>
                        
                        <div class="workflow-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <strong>AI Cost Optimization Check</strong>
                                    <div style="font-size: 14px; color: #94a3b8;">Scheduled for 15:00</div>
                                </div>
                                <span class="status scheduled">Scheduled</span>
                            </div>
                            <div style="font-size: 14px; color: #64748b; margin-bottom: 15px;">
                                Hourly optimization check to maintain cost efficiency
                            </div>
                            <button class="btn" onclick="runWorkflowNow('ai_cost_optimization')">Run Now</button>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📋 Workflow Templates</h2>
                    <div id="workflowTemplates">
                        <div class="workflow-card">
                            <div style="margin-bottom: 15px;">
                                <strong>Marketing Campaign Automation</strong>
                                <div style="font-size: 14px; color: #94a3b8;">Complete campaign creation and deployment</div>
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-bottom: 15px;">
                                5 steps • ~15 minutes • High priority
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn create" onclick="createWorkflow('marketing_campaign')">Create Workflow</button>
                                <button class="btn" onclick="scheduleWorkflow('marketing_campaign')">Schedule</button>
                            </div>
                        </div>
                        
                        <div class="workflow-card">
                            <div style="margin-bottom: 15px;">
                                <strong>Platform Health Check</strong>
                                <div style="font-size: 14px; color: #94a3b8;">Comprehensive system monitoring</div>
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-bottom: 15px;">
                                3 steps • ~8 minutes • Medium priority
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn create" onclick="createWorkflow('platform_health_check')">Create Workflow</button>
                                <button class="btn" onclick="scheduleWorkflow('platform_health_check')">Schedule</button>
                            </div>
                        </div>
                        
                        <div class="workflow-card">
                            <div style="margin-bottom: 15px;">
                                <strong>AI Cost Optimization</strong>
                                <div style="font-size: 14px; color: #94a3b8;">Analyze and optimize AI routing</div>
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-bottom: 15px;">
                                3 steps • ~6 minutes • Auto-scheduled
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn create" onclick="createWorkflow('ai_cost_optimization')">Create Workflow</button>
                                <button class="btn" onclick="scheduleWorkflow('ai_cost_optimization')">Schedule</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📅 Scheduled Jobs</h2>
                    <div id="scheduledJobs">
                        <div class="job-item">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>Daily Platform Health Check</strong>
                                    <div style="font-size: 12px; color: #94a3b8;">0 8 * * * (Daily at 8:00 AM)</div>
                                </div>
                                <span class="status scheduled">Active</span>
                            </div>
                            <div style="margin: 10px 0; font-size: 14px; color: #64748b;">
                                Next run: Tomorrow 8:00 AM
                            </div>
                        </div>
                        
                        <div class="job-item">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>Hourly AI Cost Optimization</strong>
                                    <div style="font-size: 12px; color: #94a3b8;">0 * * * * (Every hour)</div>
                                </div>
                                <span class="status scheduled">Active</span>
                            </div>
                            <div style="margin: 10px 0; font-size: 14px; color: #64748b;">
                                Next run: In 23 minutes
                            </div>
                        </div>
                        
                        <div class="job-item">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>Weekly Analytics Report</strong>
                                    <div style="font-size: 12px; color: #94a3b8;">0 9 * * 1 (Mondays at 9:00 AM)</div>
                                </div>
                                <span class="status scheduled">Active</span>
                            </div>
                            <div style="margin: 10px 0; font-size: 14px; color: #64748b;">
                                Next run: Monday 9:00 AM
                            </div>
                        </div>
                    </div>
                    
                    <h3 style="margin-top: 30px;">⚙️ Create Schedule</h3>
                    <div>
                        <input type="text" placeholder="Job name" class="schedule-input" id="jobName">
                        <input type="text" placeholder="Cron expression (e.g., 0 9 * * 1)" class="schedule-input" id="cronExpression">
                        <div class="cron-helper">
                            Examples: "0 9 * * *" (daily at 9 AM), "0 */2 * * *" (every 2 hours)
                        </div>
                        <select class="schedule-input" id="workflowTemplate">
                            <option value="marketing_campaign">Marketing Campaign</option>
                            <option value="platform_health_check">Platform Health Check</option>
                            <option value="ai_cost_optimization">AI Cost Optimization</option>
                        </select>
                        <button class="btn create" onclick="createSchedule()">Create Schedule</button>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📊 Execution History</h2>
                    <div class="timeline" id="executionHistory">
                        <div class="timeline-item completed">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>Marketing Campaign Automation</strong>
                                <span style="font-size: 12px; color: #64748b;">14:32</span>
                            </div>
                            <div style="font-size: 14px; color: #22c55e;">✓ Completed successfully (8m 45s)</div>
                        </div>
                        
                        <div class="timeline-item completed">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>AI Cost Optimization Check</strong>
                                <span style="font-size: 12px; color: #64748b;">14:00</span>
                            </div>
                            <div style="font-size: 14px; color: #22c55e;">✓ Completed successfully (3m 12s)</div>
                        </div>
                        
                        <div class="timeline-item failed">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>Platform Health Check</strong>
                                <span style="font-size: 12px; color: #64748b;">13:45</span>
                            </div>
                            <div style="font-size: 14px; color: #ef4444;">✗ Failed at step 2 (timeout)</div>
                        </div>
                        
                        <div class="timeline-item completed">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>Marketing Campaign Automation</strong>
                                <span style="font-size: 12px; color: #64748b;">13:15</span>
                            </div>
                            <div style="font-size: 14px; color: #22c55e;">✓ Completed successfully (12m 3s)</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function createWorkflow(templateName) {
                console.log(`Creating workflow from template: ${templateName}`);
                alert(`Workflow created from ${templateName} template and started immediately.`);
            }
            
            function scheduleWorkflow(templateName) {
                console.log(`Scheduling workflow: ${templateName}`);
                const schedule = prompt('Enter cron schedule (e.g., "0 9 * * *" for daily at 9 AM):');
                if (schedule) {
                    alert(`Workflow ${templateName} scheduled with pattern: ${schedule}`);
                }
            }
            
            function stopWorkflow(workflowId) {
                console.log(`Stopping workflow: ${workflowId}`);
                if (confirm('Are you sure you want to stop this workflow?')) {
                    alert('Workflow stopped successfully.');
                }
            }
            
            function viewWorkflow(workflowId) {
                console.log(`Viewing workflow details: ${workflowId}`);
                alert('Opening detailed workflow execution view...');
            }
            
            function runWorkflowNow(templateName) {
                console.log(`Running workflow immediately: ${templateName}`);
                alert(`Starting ${templateName} workflow now...`);
            }
            
            function createSchedule() {
                const jobName = document.getElementById('jobName').value;
                const cronExpression = document.getElementById('cronExpression').value;
                const template = document.getElementById('workflowTemplate').value;
                
                if (!jobName || !cronExpression) {
                    alert('Please fill in job name and cron expression.');
                    return;
                }
                
                console.log(`Creating schedule: ${jobName}, ${cronExpression}, ${template}`);
                alert(`Schedule created: ${jobName} will run on ${cronExpression}`);
                
                // Clear form
                document.getElementById('jobName').value = '';
                document.getElementById('cronExpression').value = '';
            }
            
            // Simulate real-time updates
            function updateMetrics() {
                const activeJobs = Math.floor(Math.random() * 5) + 10;
                const completedToday = Math.floor(Math.random() * 10) + 45;
                
                document.getElementById('activeJobs').textContent = activeJobs;
                document.getElementById('completedToday').textContent = completedToday;
            }
            
            setInterval(updateMetrics, 30000);
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "scheduler-automation-engine", "timestamp": datetime.now().isoformat()}

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with service_monitor.track_operation(f"execute_{action}"):
            if action == "setup_automation":
                project_id = parameters.get("project_id")
                automation_schedule = {
                    "schedule_id": f"sched_{int(time.time())}",
                    "project_id": project_id,
                    "workflow_id": workflow_context.get("workflow_id"),
                    "automation_type": "project_workflow",
                    "schedule": "0 9 * * 1-5",  # Weekdays at 9 AM
                    "status": "active",
                    "created_at": datetime.now()
                }
                if db:
                    db.collection("automation_schedules").document(automation_schedule["schedule_id"]).set(automation_schedule)

                return {
                    "success": True,
                    "action": action,
                    "output": {"schedule_id": automation_schedule["schedule_id"], "automation_active": True},
                    "execution_time": time.time(),
                    "service": "scheduler-automation-engine"
                }

            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not supported by scheduler-automation-engine",
                    "supported_actions": ["setup_automation"],
                    "service": "scheduler-automation-engine"
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "action": request.get("action"),
            "service": "scheduler-automation-engine"
        }

@app.post("/api/workflows")
async def create_workflow(workflow_data: Dict[str, Any]):
    """Create and start a new workflow"""
    try:
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        template_name = workflow_data.get("template", "")
        trigger_type = workflow_data.get("trigger_type", TriggerType.MANUAL)
        parameters = workflow_data.get("parameters", {})
        
        if template_name not in WORKFLOW_TEMPLATES:
            raise HTTPException(status_code=400, detail="Invalid workflow template")
        
        template = WORKFLOW_TEMPLATES[template_name]
        
        # Create workflow document
        workflow_doc = {
            "id": workflow_id,
            "name": template["name"],
            "description": template["description"],
            "template": template_name,
            "status": WorkflowStatus.PENDING,
            "trigger_type": trigger_type,
            "parameters": parameters,
            "steps": template["steps"],
            "current_step": 0,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "created_by": "system",
            "execution_log": [],
            "retry_count": 0,
            "max_retries": 3
        }
        
        # Store workflow
        db.collection("workflows").document(workflow_id).set(workflow_doc)
        
        # Start workflow execution
        await execute_workflow(workflow_id)
        
        # Publish workflow creation event
        topic_path = publisher.topic_path(PROJECT_ID, "xynergy-scheduler-events")
        message_data = json.dumps({
            "event_type": "workflow_created",
            "workflow_id": workflow_id,
            "template": template_name,
            "timestamp": datetime.now().isoformat()
        }).encode("utf-8")
        
        publisher.publish(topic_path, message_data)
        
        return {
            "workflow_id": workflow_id,
            "status": "created",
            "template": template_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow creation error: {str(e)}")

@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow details and status"""
    try:
        doc_ref = db.collection("workflows").document(workflow_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow_data = doc.to_dict()
        
        # Convert timestamps for JSON serialization
        for field in ["created_at", "started_at", "completed_at"]:
            if workflow_data.get(field):
                workflow_data[field] = workflow_data[field].isoformat()
        
        return workflow_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow retrieval error: {str(e)}")

@app.put("/api/workflows/{workflow_id}/stop", dependencies=[Depends(verify_api_key)])
async def stop_workflow(workflow_id: str):
    """Stop a running workflow"""
    try:
        doc_ref = db.collection("workflows").document(workflow_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow_data = doc.to_dict()
        
        if workflow_data["status"] not in [WorkflowStatus.RUNNING, WorkflowStatus.PENDING]:
            raise HTTPException(status_code=400, detail="Workflow cannot be stopped")
        
        # Update workflow status
        doc_ref.update({
            "status": WorkflowStatus.CANCELLED,
            "completed_at": datetime.now(),
            "execution_log": firestore.ArrayUnion([{
                "timestamp": datetime.now().isoformat(),
                "event": "workflow_cancelled",
                "message": "Workflow cancelled by user"
            }])
        })
        
        return {"status": "cancelled", "workflow_id": workflow_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow stop error: {str(e)}")

@app.post("/api/schedules")
async def create_schedule(schedule_data: Dict[str, Any]):
    """Create a new scheduled job"""
    try:
        schedule_id = f"sched_{uuid.uuid4().hex[:8]}"
        job_name = schedule_data.get("name", "")
        cron_expression = schedule_data.get("cron", "")
        workflow_template = schedule_data.get("workflow_template", "")
        enabled = schedule_data.get("enabled", True)
        
        if not all([job_name, cron_expression, workflow_template]):
            raise HTTPException(status_code=400, detail="Name, cron expression, and workflow template are required")
        
        if workflow_template not in WORKFLOW_TEMPLATES:
            raise HTTPException(status_code=400, detail="Invalid workflow template")
        
        # Create schedule document
        schedule_doc = {
            "id": schedule_id,
            "name": job_name,
            "cron_expression": cron_expression,
            "workflow_template": workflow_template,
            "enabled": enabled,
            "created_at": datetime.now(),
            "last_execution": None,
            "next_execution": None,  # Would calculate based on cron
            "execution_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "created_by": "system"
        }
        
        # Store schedule
        db.collection("schedules").document(schedule_id).set(schedule_doc)
        
        # In production, would create actual Cloud Scheduler job
        try:
            parent = f"projects/{PROJECT_ID}/locations/{REGION}"
            job = {
                "name": f"{parent}/jobs/{schedule_id}",
                "description": f"Scheduled workflow: {job_name}",
                "schedule": cron_expression,
                "time_zone": "UTC",
                "pub_sub_target": {
                    "topic_name": f"projects/{PROJECT_ID}/topics/xynergy-scheduler-triggers",
                    "data": json.dumps({
                        "schedule_id": schedule_id,
                        "workflow_template": workflow_template
                    }).encode()
                }
            }
            
            # Create Cloud Scheduler job (commented for demo)
            # scheduler_client.create_job(parent=parent, job=job)
            
        except Exception as scheduler_error:
            print(f"Cloud Scheduler error: {scheduler_error}")
            # Continue even if Cloud Scheduler fails
        
        return {
            "schedule_id": schedule_id,
            "status": "created",
            "name": job_name,
            "next_execution": "calculated_based_on_cron"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule creation error: {str(e)}")

@app.get("/api/schedules")
async def get_schedules():
    """Get all scheduled jobs"""
    try:
        schedules_ref = db.collection("schedules").where("enabled", "==", True)
        
        schedules = []
        for doc in schedules_ref.stream():
            schedule_data = doc.to_dict()
            
            # Convert timestamps
            for field in ["created_at", "last_execution", "next_execution"]:
                if schedule_data.get(field):
                    schedule_data[field] = schedule_data[field].isoformat()
            
            schedules.append(schedule_data)
        
        return sorted(schedules, key=lambda x: x.get("created_at", ""), reverse=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedules retrieval error: {str(e)}")

@app.get("/api/workflows")
async def get_workflows(status: Optional[str] = None, limit: int = 50):
    """Get workflows with optional status filter"""
    try:
        workflows_ref = db.collection("workflows").order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        
        if status:
            workflows_ref = workflows_ref.where("status", "==", status)
        
        workflows = []
        for doc in workflows_ref.stream():
            workflow_data = doc.to_dict()
            
            # Convert timestamps
            for field in ["created_at", "started_at", "completed_at"]:
                if workflow_data.get(field):
                    workflow_data[field] = workflow_data[field].isoformat()
            
            workflows.append(workflow_data)
        
        return workflows
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflows retrieval error: {str(e)}")

@app.get("/api/templates")
async def get_workflow_templates():
    """Get available workflow templates"""
    return WORKFLOW_TEMPLATES

@app.post("/api/workflows/{workflow_id}/retry")
async def retry_workflow(workflow_id: str):
    """Retry a failed workflow"""
    try:
        doc_ref = db.collection("workflows").document(workflow_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow_data = doc.to_dict()
        
        if workflow_data["status"] != WorkflowStatus.FAILED:
            raise HTTPException(status_code=400, detail="Only failed workflows can be retried")
        
        if workflow_data.get("retry_count", 0) >= workflow_data.get("max_retries", 3):
            raise HTTPException(status_code=400, detail="Maximum retry attempts reached")
        
        # Reset workflow for retry
        doc_ref.update({
            "status": WorkflowStatus.PENDING,
            "current_step": 0,
            "retry_count": firestore.Increment(1),
            "started_at": None,
            "completed_at": None,
            "execution_log": firestore.ArrayUnion([{
                "timestamp": datetime.now().isoformat(),
                "event": "workflow_retry",
                "message": f"Workflow retry attempt {workflow_data.get('retry_count', 0) + 1}"
            }])
        })
        
        # Restart workflow execution
        await execute_workflow(workflow_id)
        
        return {"status": "retrying", "workflow_id": workflow_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow retry error: {str(e)}")

async def execute_workflow(workflow_id: str):
    """Execute workflow steps sequentially"""
    try:
        doc_ref = db.collection("workflows").document(workflow_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return
        
        workflow_data = doc.to_dict()
        
        # Update status to running
        doc_ref.update({
            "status": WorkflowStatus.RUNNING,
            "started_at": datetime.now(),
            "execution_log": firestore.ArrayUnion([{
                "timestamp": datetime.now().isoformat(),
                "event": "workflow_started",
                "message": "Workflow execution started"
            }])
        })
        
        steps = workflow_data["steps"]
        current_step = workflow_data.get("current_step", 0)
        
        # Execute each step
        for i in range(current_step, len(steps)):
            step = steps[i]
            
            # Update current step
            doc_ref.update({"current_step": i})
            
            # Log step start
            doc_ref.update({
                "execution_log": firestore.ArrayUnion([{
                    "timestamp": datetime.now().isoformat(),
                    "event": "step_started",
                    "step": i + 1,
                    "service": step["service"],
                    "action": step["action"]
                }])
            })
            
            # Simulate step execution
            step_success = await execute_workflow_step(step, workflow_id)
            
            if step_success:
                # Log step completion
                doc_ref.update({
                    "execution_log": firestore.ArrayUnion([{
                        "timestamp": datetime.now().isoformat(),
                        "event": "step_completed",
                        "step": i + 1,
                        "service": step["service"],
                        "action": step["action"],
                        "duration": "simulated"
                    }])
                })
            else:
                # Step failed
                doc_ref.update({
                    "status": WorkflowStatus.FAILED,
                    "completed_at": datetime.now(),
                    "execution_log": firestore.ArrayUnion([{
                        "timestamp": datetime.now().isoformat(),
                        "event": "step_failed",
                        "step": i + 1,
                        "service": step["service"],
                        "action": step["action"],
                        "error": "Step execution failed"
                    }])
                })
                return
        
        # All steps completed successfully
        doc_ref.update({
            "status": WorkflowStatus.COMPLETED,
            "completed_at": datetime.now(),
            "execution_log": firestore.ArrayUnion([{
                "timestamp": datetime.now().isoformat(),
                "event": "workflow_completed",
                "message": "All workflow steps completed successfully"
            }])
        })
        
    except Exception as e:
        # Workflow execution error
        doc_ref.update({
            "status": WorkflowStatus.FAILED,
            "completed_at": datetime.now(),
            "execution_log": firestore.ArrayUnion([{
                "timestamp": datetime.now().isoformat(),
                "event": "workflow_error",
                "error": str(e)
            }])
        })

async def execute_workflow_step(step: Dict[str, Any], workflow_id: str) -> bool:
    """Execute a single workflow step"""
    try:
        service = step["service"]
        action = step["action"]
        timeout = step.get("timeout", 300)
        
        # Simulate step execution time
        await asyncio.sleep(2)

        # Simulate step success/failure (95% success rate)
        import random
        success = random.random() > 0.05
        
        if success:
            # Publish step completion event
            topic_path = publisher.topic_path(PROJECT_ID, f"xynergy-{service}-events")
            message_data = json.dumps({
                "action": action,
                "workflow_id": workflow_id,
                "triggered_by": "scheduler-automation-engine",
                "timestamp": datetime.now().isoformat()
            }).encode("utf-8")
            
            try:
                publisher.publish(topic_path, message_data)
            except Exception:
                pass  # Continue even if pub/sub fails
        
        return success
        
    except Exception as e:
        print(f"Step execution error: {e}")
        return False


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
