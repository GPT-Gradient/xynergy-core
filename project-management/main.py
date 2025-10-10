from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from google.cloud import firestore, pubsub_v1

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


# Phase 2 enhancements
from phase2_utils import CircuitBreaker, CircuitBreakerConfig, call_service_with_circuit_breaker, PerformanceMonitor
import time

# Import centralized authentication
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from auth import verify_api_key, verify_api_key_optional



PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")

# Initialize GCP clients
db = get_firestore_client()  # Phase 4: Shared connection pooling
publisher = get_publisher_client()  # Phase 4: Shared connection pooling

app = FastAPI(title="Xynergy Project Management", version="1.0.0")

# Phase 2 initialization
service_monitor = PerformanceMonitor("project-management")
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

class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Project templates for autonomous execution
PROJECT_TEMPLATES = {
    "marketing_campaign": {
        "name": "Marketing Campaign Project",
        "description": "Complete marketing campaign from concept to execution",
        "estimated_duration_days": 14,
        "phases": [
            {
                "name": "Research & Planning",
                "duration_days": 3,
                "tasks": [
                    {"name": "Market Research", "service": "ai-assistant", "estimated_hours": 4},
                    {"name": "Keyword Analysis", "service": "marketing-engine", "estimated_hours": 6},
                    {"name": "Strategy Development", "service": "ai-assistant", "estimated_hours": 8}
                ]
            },
            {
                "name": "Content Creation",
                "duration_days": 7,
                "tasks": [
                    {"name": "Content Generation", "service": "marketing-engine", "estimated_hours": 12},
                    {"name": "Asset Creation", "service": "content-hub", "estimated_hours": 8},
                    {"name": "Quality Review", "service": "qa-engine", "estimated_hours": 4}
                ]
            },
            {
                "name": "Execution & Monitoring",
                "duration_days": 4,
                "tasks": [
                    {"name": "Campaign Launch", "service": "scheduler-automation-engine", "estimated_hours": 2},
                    {"name": "Performance Monitoring", "service": "analytics-data-layer", "estimated_hours": 6},
                    {"name": "Optimization", "service": "ai-routing-engine", "estimated_hours": 4}
                ]
            }
        ]
    },
    "platform_enhancement": {
        "name": "Platform Enhancement Project",
        "description": "Systematic platform improvements and new feature deployment",
        "estimated_duration_days": 21,
        "phases": [
            {
                "name": "Analysis & Design",
                "duration_days": 5,
                "tasks": [
                    {"name": "Requirements Analysis", "service": "ai-assistant", "estimated_hours": 8},
                    {"name": "Technical Design", "service": "system-runtime", "estimated_hours": 12},
                    {"name": "Security Review", "service": "security-governance", "estimated_hours": 6}
                ]
            },
            {
                "name": "Development & Testing",
                "duration_days": 12,
                "tasks": [
                    {"name": "Feature Development", "service": "system-runtime", "estimated_hours": 24},
                    {"name": "Quality Assurance", "service": "qa-engine", "estimated_hours": 16},
                    {"name": "Security Testing", "service": "security-governance", "estimated_hours": 8}
                ]
            },
            {
                "name": "Deployment & Monitoring",
                "duration_days": 4,
                "tasks": [
                    {"name": "Production Deployment", "service": "scheduler-automation-engine", "estimated_hours": 4},
                    {"name": "Performance Monitoring", "service": "analytics-data-layer", "estimated_hours": 8},
                    {"name": "Documentation", "service": "reports-export", "estimated_hours": 6}
                ]
            }
        ]
    }
}

@app.get("/", response_class=HTMLResponse)
async def project_management_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Xynergy Project Management</title>
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
                <h1>🎯 Xynergy Project Management</h1>
                <p>Autonomous project execution and workflow orchestration</p>
                <div style="display: flex; gap: 30px; margin-top: 15px;">
                    <div>Active Projects: <span id="activeProjects">3</span></div>
                    <div>Tasks Completed: <span id="tasksCompleted">247</span></div>
                    <div>Success Rate: <span style="color: #22c55e; font-weight: 700;">96.4%</span></div>
                </div>
            </div>
            
            <div class="grid">
                <div class="panel">
                    <h2>📊 Project Dashboard</h2>
                    <div class="metric-grid">
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Total Projects</div>
                            <div class="metric-value info" id="totalProjects">12</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">In Progress</div>
                            <div class="metric-value good" id="inProgressProjects">3</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Completed</div>
                            <div class="metric-value good" id="completedProjects">8</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">On Time</div>
                            <div class="metric-value good" id="onTimeRate">94%</div>
                        </div>
                    </div>
                    
                    <h3>🚀 Active Projects</h3>
                    <div id="activeProjectsList">
                        <div class="project-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <strong>Q4 Marketing Campaign</strong>
                                    <div style="font-size: 14px; color: #94a3b8;">Marketing Campaign Project</div>
                                </div>
                                <span class="status active">Active</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                <span style="font-size: 14px; color: #64748b;">Progress: 67%</span>
                                <span style="font-size: 14px; color: #64748b;">Due: Oct 15</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: 67%;"></div>
                            </div>
                            <div style="display: flex; gap: 10px; margin-top: 15px;">
                                <button class="btn" onclick="viewProject('q4_marketing')">View Details</button>
                                <button class="btn pause" onclick="pauseProject('q4_marketing')">Pause</button>
                            </div>
                        </div>
                        
                        <div class="project-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <strong>Platform Security Enhancement</strong>
                                    <div style="font-size: 14px; color: #94a3b8;">Platform Enhancement Project</div>
                                </div>
                                <span class="status active">Active</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                <span style="font-size: 14px; color: #64748b;">Progress: 23%</span>
                                <span style="font-size: 14px; color: #64748b;">Due: Nov 2</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: 23%;"></div>
                            </div>
                            <div style="display: flex; gap: 10px; margin-top: 15px;">
                                <button class="btn" onclick="viewProject('security_enhancement')">View Details</button>
                                <button class="btn pause" onclick="pauseProject('security_enhancement')">Pause</button>
                            </div>
                        </div>
                    </div>
                    
                    <h3 style="margin-top: 30px;">⚙️ Quick Actions</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        <button class="btn create" onclick="createProject()">New Project</button>
                        <button class="btn" onclick="generateProjectReport()">Project Report</button>
                        <button class="btn" onclick="scheduleReview()">Schedule Review</button>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📋 Task Management</h2>
                    <div class="kanban-board">
                        <div class="kanban-column">
                            <div class="kanban-header">📝 To Do (4)</div>
                            <div class="task-card" onclick="viewTask('task_001')">
                                <strong>Market Analysis</strong>
                                <div style="font-size: 12px; color: #94a3b8; margin-top: 5px;">Q4 Marketing Campaign</div>
                                <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                    <span class="priority medium">Medium</span>
                                    <span style="font-size: 12px; color: #64748b;">2 days</span>
                                </div>
                            </div>
                            <div class="task-card" onclick="viewTask('task_002')">
                                <strong>Security Audit</strong>
                                <div style="font-size: 12px; color: #94a3b8; margin-top: 5px;">Security Enhancement</div>
                                <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                    <span class="priority high">High</span>
                                    <span style="font-size: 12px; color: #64748b;">1 day</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="kanban-column">
                            <div class="kanban-header">🔄 In Progress (3)</div>
                            <div class="task-card" onclick="viewTask('task_003')">
                                <strong>Content Creation</strong>
                                <div style="font-size: 12px; color: #94a3b8; margin-top: 5px;">Q4 Marketing Campaign</div>
                                <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                    <span class="priority high">High</span>
                                    <span style="font-size: 12px; color: #64748b;">AI Service</span>
                                </div>
                            </div>
                            <div class="task-card" onclick="viewTask('task_004')">
                                <strong>Performance Testing</strong>
                                <div style="font-size: 12px; color: #94a3b8; margin-top: 5px;">Platform Enhancement</div>
                                <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                    <span class="priority medium">Medium</span>
                                    <span style="font-size: 12px; color: #64748b;">QA Engine</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="kanban-column">
                            <div class="kanban-header">👁️ Review (2)</div>
                            <div class="task-card" onclick="viewTask('task_005')">
                                <strong>Campaign Strategy</strong>
                                <div style="font-size: 12px; color: #94a3b8; margin-top: 5px;">Q4 Marketing Campaign</div>
                                <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                    <span class="priority medium">Medium</span>
                                    <span style="font-size: 12px; color: #64748b;">Review</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="kanban-column">
                            <div class="kanban-header">✅ Done (8)</div>
                            <div class="task-card" onclick="viewTask('task_006')">
                                <strong>Requirements Analysis</strong>
                                <div style="font-size: 12px; color: #94a3b8; margin-top: 5px;">Security Enhancement</div>
                                <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                    <span class="priority low">Low</span>
                                    <span style="font-size: 12px; color: #22c55e;">Completed</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📈 Project Templates</h2>
                    <div id="projectTemplates">
                        <div class="project-card">
                            <div style="margin-bottom: 15px;">
                                <strong>Marketing Campaign Project</strong>
                                <div style="font-size: 14px; color: #94a3b8;">Complete marketing campaign from concept to execution</div>
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-bottom: 15px;">
                                3 phases • 14 days • 12 tasks • Fully automated
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn create" onclick="createFromTemplate('marketing_campaign')">Create Project</button>
                                <button class="btn" onclick="viewTemplate('marketing_campaign')">View Template</button>
                            </div>
                        </div>
                        
                        <div class="project-card">
                            <div style="margin-bottom: 15px;">
                                <strong>Platform Enhancement Project</strong>
                                <div style="font-size: 14px; color: #94a3b8;">Systematic platform improvements and feature deployment</div>
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-bottom: 15px;">
                                3 phases • 21 days • 18 tasks • AI-assisted
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn create" onclick="createFromTemplate('platform_enhancement')">Create Project</button>
                                <button class="btn" onclick="viewTemplate('platform_enhancement')">View Template</button>
                            </div>
                        </div>
                    </div>
                    
                    <h3 style="margin-top: 30px;">🤖 Autonomous Features</h3>
                    <div style="background: #0f172a; padding: 20px; border-radius: 8px; border: 1px solid #334155;">
                        <ul style="margin: 0; padding-left: 20px; color: #94a3b8;">
                            <li>Automatic task assignment based on service capabilities</li>
                            <li>Intelligent deadline prediction using historical data</li>
                            <li>Real-time progress tracking across all platform services</li>
                            <li>Automated quality gates and approval workflows</li>
                            <li>Dynamic resource allocation and load balancing</li>
                            <li>Predictive risk assessment and mitigation</li>
                        </ul>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📅 Project Timeline</h2>
                    <div class="timeline" id="projectTimeline">
                        <div class="timeline-item completed">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>Requirements Analysis Completed</strong>
                                <span style="font-size: 12px; color: #64748b;">3 days ago</span>
                            </div>
                            <div style="font-size: 14px; color: #94a3b8;">Security Enhancement Project</div>
                        </div>
                        
                        <div class="timeline-item completed">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>Content Creation Phase Started</strong>
                                <span style="font-size: 12px; color: #64748b;">2 days ago</span>
                            </div>
                            <div style="font-size: 14px; color: #94a3b8;">Q4 Marketing Campaign</div>
                        </div>
                        
                        <div class="timeline-item active">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>Performance Testing In Progress</strong>
                                <span style="font-size: 12px; color: #64748b;">Today</span>
                            </div>
                            <div style="font-size: 14px; color: #94a3b8;">Platform Enhancement Project</div>
                        </div>
                        
                        <div class="timeline-item">
                            <div style="display: flex; justify-content: space-between;">
                                <strong>Campaign Launch Scheduled</strong>
                                <span style="font-size: 12px; color: #64748b;">In 3 days</span>
                            </div>
                            <div style="font-size: 14px; color: #94a3b8;">Q4 Marketing Campaign</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function createProject() {
                console.log('Creating new project...');
                alert('Opening project creation wizard...');
            }
            
            function createFromTemplate(templateName) {
                console.log(`Creating project from template: ${templateName}`);
                const projectName = prompt(`Enter project name for ${templateName}:`);
                if (projectName) {
                    alert(`Creating "${projectName}" project from ${templateName} template. All tasks will be automatically assigned to appropriate services.`);
                }
            }
            
            function viewProject(projectId) {
                console.log(`Viewing project: ${projectId}`);
                alert('Opening detailed project view...');
            }
            
            function viewTemplate(templateName) {
                console.log(`Viewing template: ${templateName}`);
                alert(`Opening ${templateName} template details...`);
            }
            
            function pauseProject(projectId) {
                console.log(`Pausing project: ${projectId}`);
                if (confirm('Pause this project? All active tasks will be paused.')) {
                    alert('Project paused. All automated tasks have been suspended.');
                }
            }
            
            function viewTask(taskId) {
                console.log(`Viewing task: ${taskId}`);
                alert('Opening task details...');
            }
            
            function generateProjectReport() {
                console.log('Generating project report...');
                alert('Generating comprehensive project report. Report will be available for download in 2-3 minutes.');
            }
            
            function scheduleReview() {
                console.log('Scheduling project review...');
                alert('Scheduling project review meeting with all stakeholders...');
            }
            
            // Simulate real-time updates
            function updateMetrics() {
                const totalProjects = Math.floor(Math.random() * 3) + 11;
                const activeProjects = Math.floor(Math.random() * 2) + 3;
                const completedProjects = totalProjects - activeProjects - 1;
                
                document.getElementById('totalProjects').textContent = totalProjects;
                document.getElementById('activeProjects').textContent = activeProjects;
                document.getElementById('inProgressProjects').textContent = activeProjects;
                document.getElementById('completedProjects').textContent = completedProjects;
            }
            
            setInterval(updateMetrics, 45000);
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "project-management", "timestamp": datetime.now().isoformat()}

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with service_monitor.track_operation(f"execute_{action}"):
            if action == "create_project":
                # Create new project from workflow
                intent = parameters.get("intent", "")
                workflow_id = workflow_context.get("workflow_id")

                project_data = {
                    "project_id": f"proj_{int(time.time())}",
                    "workflow_id": workflow_id,
                    "name": f"Project: {intent[:50]}...",
                    "description": f"Auto-generated project for: {intent}",
                    "status": "planning",
                    "priority": "medium",
                    "created_at": datetime.now(),
                    "tasks": [
                        {"task_id": f"task_{int(time.time())}_1", "name": "Initial Planning", "status": "pending"},
                        {"task_id": f"task_{int(time.time())}_2", "name": "Resource Allocation", "status": "pending"},
                        {"task_id": f"task_{int(time.time())}_3", "name": "Execution Phase", "status": "pending"}
                    ]
                }

                db.collection("projects").document(project_data["project_id"]).set(project_data)

                return {
                    "success": True,
                    "action": action,
                    "output": {
                        "project_id": project_data["project_id"],
                        "project_created": True,
                        "tasks_created": len(project_data["tasks"])
                    },
                    "execution_time": time.time(),
                    "service": "project-management"
                }

            elif action == "setup_automation":
                # Setup project automation
                project_id = parameters.get("project_id")
                automation_config = {
                    "automation_id": f"auto_{int(time.time())}",
                    "project_id": project_id,
                    "workflow_id": workflow_context.get("workflow_id"),
                    "automations": ["task_scheduling", "status_updates", "resource_optimization"],
                    "setup_at": datetime.now()
                }

                db.collection("project_automations").document(automation_config["automation_id"]).set(automation_config)

                return {
                    "success": True,
                    "action": action,
                    "output": {
                        "automation_id": automation_config["automation_id"],
                        "automations_enabled": len(automation_config["automations"])
                    },
                    "execution_time": time.time(),
                    "service": "project-management"
                }

            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not supported by project-management",
                    "supported_actions": ["create_project", "setup_automation"],
                    "service": "project-management"
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "action": request.get("action"),
            "service": "project-management"
        }

@app.post("/api/projects")
async def create_project(project_data: Dict[str, Any]):
    """Create a new project"""
    try:
        project_id = f"proj_{uuid.uuid4().hex[:8]}"
        project_name = project_data.get("name", "")
        template_name = project_data.get("template", "")
        description = project_data.get("description", "")
        priority = project_data.get("priority", Priority.MEDIUM)
        
        if not project_name:
            raise HTTPException(status_code=400, detail="Project name is required")
        
        # Use template if provided
        if template_name and template_name in PROJECT_TEMPLATES:
            template = PROJECT_TEMPLATES[template_name]
            phases = template["phases"]
            estimated_duration = template["estimated_duration_days"]
        else:
            phases = project_data.get("phases", [])
            estimated_duration = project_data.get("estimated_duration_days", 7)
        
        # Calculate project timeline
        start_date = datetime.now()
        end_date = start_date + timedelta(days=estimated_duration)
        
        # Create project document
        project_doc = {
            "id": project_id,
            "name": project_name,
            "description": description,
            "template": template_name,
            "status": ProjectStatus.PLANNING,
            "priority": priority,
            "created_at": start_date,
            "start_date": start_date,
            "end_date": end_date,
            "estimated_duration_days": estimated_duration,
            "phases": phases,
            "current_phase": 0,
            "progress_percentage": 0,
            "tasks_total": sum(len(phase.get("tasks", [])) for phase in phases),
            "tasks_completed": 0,
            "created_by": "system",
            "assigned_services": []
        }
        
        # Store project
        db.collection("projects").document(project_id).set(project_doc)
        
        # Create tasks from phases
        await create_project_tasks(project_id, phases)
        
        # Start project execution if using template
        if template_name:
            asyncio.create_task(start_autonomous_execution(project_id))
        
        # Publish project creation event
        topic_path = publisher.topic_path(PROJECT_ID, "xynergy-project-events")
        message_data = json.dumps({
            "event_type": "project_created",
            "project_id": project_id,
            "project_name": project_name,
            "template": template_name,
            "timestamp": datetime.now().isoformat()
        }).encode("utf-8")
        
        publisher.publish(topic_path, message_data)
        
        return {
            "project_id": project_id,
            "status": "created",
            "name": project_name,
            "estimated_completion": end_date.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project creation error: {str(e)}")

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    try:
        doc_ref = db.collection("projects").document(project_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = doc.to_dict()
        
        # Convert timestamps
        for field in ["created_at", "start_date", "end_date", "completed_at"]:
            if project_data.get(field):
                project_data[field] = project_data[field].isoformat()
        
        # Get project tasks
        tasks = await get_project_tasks(project_id)
        project_data["tasks"] = tasks
        
        return project_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project retrieval error: {str(e)}")

@app.get("/api/projects")
async def get_projects(status: Optional[str] = None, limit: int = 20):
    """Get projects list"""
    try:
        projects_ref = db.collection("projects").order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        
        if status:
            projects_ref = projects_ref.where("status", "==", status)
        
        projects = []
        for doc in projects_ref.stream():
            project_data = doc.to_dict()
            
            # Convert timestamps
            for field in ["created_at", "start_date", "end_date", "completed_at"]:
                if project_data.get(field):
                    project_data[field] = project_data[field].isoformat()
            
            projects.append(project_data)
        
        return projects
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Projects retrieval error: {str(e)}")

@app.put("/api/projects/{project_id}/status", dependencies=[Depends(verify_api_key)])
async def update_project_status(project_id: str, status_data: Dict[str, Any]):
    """Update project status"""
    try:
        new_status = status_data.get("status", "")
        
        if new_status not in [status.value for status in ProjectStatus]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        doc_ref = db.collection("projects").document(project_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Project not found")
        
        update_data = {"status": new_status}
        
        if new_status == ProjectStatus.ACTIVE:
            update_data["start_date"] = datetime.now()
        elif new_status == ProjectStatus.COMPLETED:
            update_data["completed_at"] = datetime.now()
            update_data["progress_percentage"] = 100
        
        doc_ref.update(update_data)
        
        # Publish status change event
        topic_path = publisher.topic_path(PROJECT_ID, "xynergy-project-events")
        message_data = json.dumps({
            "event_type": "project_status_changed",
            "project_id": project_id,
            "new_status": new_status,
            "timestamp": datetime.now().isoformat()
        }).encode("utf-8")
        
        publisher.publish(topic_path, message_data)
        
        return {
            "project_id": project_id,
            "status": new_status,
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project status update error: {str(e)}")

@app.get("/api/tasks")
async def get_tasks(project_id: Optional[str] = None, status: Optional[str] = None, assigned_service: Optional[str] = None):
    """Get tasks with optional filters"""
    try:
        tasks_ref = db.collection("tasks")
        
        if project_id:
            tasks_ref = tasks_ref.where("project_id", "==", project_id)
        
        if status:
            tasks_ref = tasks_ref.where("status", "==", status)
        
        if assigned_service:
            tasks_ref = tasks_ref.where("assigned_service", "==", assigned_service)
        
        tasks = []
        for doc in tasks_ref.order_by("created_at").stream():
            task_data = doc.to_dict()
            
            # Convert timestamps
            for field in ["created_at", "start_date", "due_date", "completed_at"]:
                if task_data.get(field):
                    task_data[field] = task_data[field].isoformat()
            
            tasks.append(task_data)
        
        return tasks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tasks retrieval error: {str(e)}")

@app.get("/api/templates")
async def get_project_templates():
    """Get available project templates"""
    return PROJECT_TEMPLATES

@app.get("/api/dashboard")
async def get_project_dashboard():
    """Get project management dashboard data"""
    try:
        # Get project statistics
        projects_ref = db.collection("projects")
        
        total_projects = 0
        active_projects = 0
        completed_projects = 0
        on_time_projects = 0
        
        for doc in projects_ref.stream():
            project_data = doc.to_dict()
            total_projects += 1
            
            status = project_data.get("status")
            if status == ProjectStatus.ACTIVE:
                active_projects += 1
            elif status == ProjectStatus.COMPLETED:
                completed_projects += 1
                
                # Check if completed on time
                end_date = project_data.get("end_date")
                completed_at = project_data.get("completed_at")
                if end_date and completed_at and completed_at <= end_date:
                    on_time_projects += 1
        
        # Calculate success rate
        success_rate = (on_time_projects / completed_projects * 100) if completed_projects > 0 else 0
        
        # Get task statistics
        tasks_ref = db.collection("tasks")
        
        total_tasks = 0
        completed_tasks = 0
        
        for doc in tasks_ref.stream():
            task_data = doc.to_dict()
            total_tasks += 1
            
            if task_data.get("status") == TaskStatus.COMPLETED:
                completed_tasks += 1
        
        dashboard_data = {
            "projects": {
                "total": total_projects,
                "active": active_projects,
                "completed": completed_projects,
                "success_rate": round(success_rate, 1),
                "on_time_rate": round((on_time_projects / completed_projects * 100) if completed_projects > 0 else 0, 1)
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data error: {str(e)}")

async def create_project_tasks(project_id: str, phases: List[Dict[str, Any]]):
    """Create tasks from project phases"""
    try:
        task_number = 1
        
        for phase_index, phase in enumerate(phases):
            phase_tasks = phase.get("tasks", [])
            
            for task_data in phase_tasks:
                task_id = f"task_{project_id}_{task_number:03d}"
                
                task_doc = {
                    "id": task_id,
                    "project_id": project_id,
                    "phase_index": phase_index,
                    "name": task_data["name"],
                    "assigned_service": task_data.get("service", ""),
                    "estimated_hours": task_data.get("estimated_hours", 4),
                    "status": TaskStatus.TODO,
                    "priority": Priority.MEDIUM,
                    "created_at": datetime.now(),
                    "start_date": None,
                    "due_date": None,
                    "completed_at": None,
                    "progress_percentage": 0,
                    "dependencies": []
                }
                
                db.collection("tasks").document(task_id).set(task_doc)
                task_number += 1
        
    except Exception as e:
        print(f"Task creation error: {e}")

async def get_project_tasks(project_id: str) -> List[Dict[str, Any]]:
    """Get all tasks for a project"""
    try:
        tasks_ref = db.collection("tasks").where("project_id", "==", project_id)
        
        tasks = []
        for doc in tasks_ref.stream():
            task_data = doc.to_dict()
            
            # Convert timestamps
            for field in ["created_at", "start_date", "due_date", "completed_at"]:
                if task_data.get(field):
                    task_data[field] = task_data[field].isoformat()
            
            tasks.append(task_data)
        
        return sorted(tasks, key=lambda x: x.get("created_at", ""))
        
    except Exception as e:
        print(f"Get project tasks error: {e}")
        return []

async def start_autonomous_execution(project_id: str):
    """Start autonomous project execution"""
    try:
        # Update project status to active
        project_ref = db.collection("projects").document(project_id)
        project_ref.update({
            "status": ProjectStatus.ACTIVE,
            "start_date": datetime.now()
        })
        
        # Begin task execution coordination
        await coordinate_project_execution(project_id)
        
    except Exception as e:
        print(f"Autonomous execution error: {e}")

async def coordinate_project_execution(project_id: str):
    """Coordinate autonomous project execution"""
    try:
        # This would implement the autonomous execution logic:
        # 1. Monitor task dependencies
        # 2. Assign tasks to appropriate services
        # 3. Track progress and update timelines
        # 4. Handle task failures and retries
        # 5. Coordinate between services
        
        # For demo, just log the coordination
        print(f"Coordinating autonomous execution for project {project_id}")
        
        # Publish execution start event
        topic_path = publisher.topic_path(PROJECT_ID, "xynergy-project-events")
        message_data = json.dumps({
            "event_type": "autonomous_execution_started",
            "project_id": project_id,
            "timestamp": datetime.now().isoformat()
        }).encode("utf-8")
        
        publisher.publish(topic_path, message_data)
        
    except Exception as e:
        print(f"Project coordination error: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
