from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from google.cloud import firestore, pubsub_v1, storage

# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

import os
import json
import asyncio
import uuid
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uvicorn
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile


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
storage_client = storage.Client()

app = FastAPI(title="Xynergy Reports & Export", version="1.0.0")

# Phase 2 initialization
service_monitor = PerformanceMonitor("reports-export")
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

# Report templates
REPORT_TEMPLATES = {
    "executive_summary": {
        "name": "Executive Summary",
        "description": "High-level platform performance overview",
        "sections": ["overview", "cost_savings", "key_metrics", "recommendations"],
        "frequency": ["daily", "weekly", "monthly"],
        "stakeholders": ["executives", "managers"]
    },
    "ai_optimization_report": {
        "name": "AI Cost Optimization Report", 
        "description": "Detailed analysis of AI routing and cost savings",
        "sections": ["routing_analysis", "cost_breakdown", "model_performance", "optimization_opportunities"],
        "frequency": ["daily", "weekly"],
        "stakeholders": ["technical", "finance"]
    },
    "platform_performance": {
        "name": "Platform Performance Report",
        "description": "Comprehensive system performance analysis",
        "sections": ["service_metrics", "uptime_analysis", "performance_trends", "capacity_planning"],
        "frequency": ["weekly", "monthly"],
        "stakeholders": ["technical", "operations"]
    },
    "business_analytics": {
        "name": "Business Analytics Report",
        "description": "Business intelligence and growth metrics",
        "sections": ["usage_analytics", "growth_trends", "user_engagement", "revenue_impact"],
        "frequency": ["weekly", "monthly", "quarterly"],
        "stakeholders": ["executives", "marketing", "sales"]
    }
}

@app.get("/", response_class=HTMLResponse)
async def reports_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Xynergy Reports & Export</title>
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
                <h1>📊 Xynergy Reports & Export</h1>
                <p>Data visualization and comprehensive business reporting</p>
                <div style="display: flex; gap: 30px; margin-top: 15px;">
                    <div>Generated Today: <span id="reportsToday">8</span></div>
                    <div>Scheduled Reports: <span id="scheduledReports">12</span></div>
                    <div>Export Formats: <span style="color: #22c55e; font-weight: 700;">PDF, Excel, CSV</span></div>
                </div>
            </div>
            
            <div class="grid">
                <div class="panel">
                    <h2>📋 Report Templates</h2>
                    <div id="reportTemplates">
                        <div class="report-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <strong>Executive Summary</strong>
                                    <div style="font-size: 14px; color: #94a3b8;">High-level platform performance overview</div>
                                </div>
                                <span class="status ready">Ready</span>
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-bottom: 15px;">
                                Sections: Overview, Cost Savings, Key Metrics, Recommendations
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn generate" onclick="generateReport('executive_summary')">Generate Now</button>
                                <button class="btn" onclick="scheduleReport('executive_summary')">Schedule</button>
                                <button class="btn download" onclick="downloadSample('executive_summary')">Sample PDF</button>
                            </div>
                        </div>
                        
                        <div class="report-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <strong>AI Optimization Report</strong>
                                    <div style="font-size: 14px; color: #94a3b8;">Detailed AI routing and cost analysis</div>
                                </div>
                                <span class="status ready">Ready</span>
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-bottom: 15px;">
                                Sections: Routing Analysis, Cost Breakdown, Model Performance
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn generate" onclick="generateReport('ai_optimization_report')">Generate Now</button>
                                <button class="btn" onclick="scheduleReport('ai_optimization_report')">Schedule</button>
                                <button class="btn download" onclick="downloadSample('ai_optimization_report')">Sample PDF</button>
                            </div>
                        </div>
                        
                        <div class="report-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <strong>Platform Performance</strong>
                                    <div style="font-size: 14px; color: #94a3b8;">Comprehensive system performance analysis</div>
                                </div>
                                <span class="status generating">Generating</span>
                            </div>
                            <div style="font-size: 12px; color: #64748b; margin-bottom: 15px;">
                                Sections: Service Metrics, Uptime Analysis, Performance Trends
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn" disabled>Generating...</button>
                                <button class="btn" onclick="scheduleReport('platform_performance')">Schedule</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📈 Report Preview</h2>
                    <div class="report-preview">
                        <h3 style="margin-top: 0;">Executive Summary - September 2025</h3>
                        
                        <div class="metric-grid">
                            <div class="metric-box">
                                <div style="font-size: 12px; color: #94a3b8;">Platform Uptime</div>
                                <div class="metric-value">99.8%</div>
                            </div>
                            <div class="metric-box">
                                <div style="font-size: 12px; color: #94a3b8;">Cost Savings</div>
                                <div class="metric-value">$2,347</div>
                            </div>
                            <div class="metric-box">
                                <div style="font-size: 12px; color: #94a3b8;">AI Efficiency</div>
                                <div class="metric-value">67%</div>
                            </div>
                            <div class="metric-box">
                                <div style="font-size: 12px; color: #94a3b8;">Total Requests</div>
                                <div class="metric-value">45.2K</div>
                            </div>
                        </div>
                        
                        <div class="chart-preview">
                            📊 Cost Savings Trend Chart
                        </div>
                        
                        <div class="chart-preview">
                            📈 Platform Performance Over Time
                        </div>
                        
                        <div style="margin-top: 20px;">
                            <h4>Key Insights:</h4>
                            <ul style="font-size: 14px; color: #94a3b8;">
                                <li>AI routing optimization saved $2,347 this month</li>
                                <li>Platform uptime exceeded 99.8% target</li>
                                <li>Internal AI models handled 67% of requests</li>
                                <li>Response times improved by 23% over last month</li>
                            </ul>
                        </div>
                    </div>
                    
                    <h3 style="margin-top: 30px;">📤 Export Options</h3>
                    <div class="export-options">
                        <button class="export-btn selected" onclick="selectFormat('pdf')">PDF Report</button>
                        <button class="export-btn" onclick="selectFormat('excel')">Excel Workbook</button>
                        <button class="export-btn" onclick="selectFormat('csv')">CSV Data</button>
                        <button class="export-btn" onclick="selectFormat('json')">JSON Export</button>
                        <button class="export-btn" onclick="selectFormat('powerpoint')">PowerPoint</button>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>🕒 Recent Reports</h2>
                    <div id="recentReports">
                        <div class="report-preview">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>Executive Summary - Daily</strong>
                                    <div style="font-size: 12px; color: #94a3b8;">Generated 2 hours ago</div>
                                </div>
                                <button class="btn download" onclick="downloadReport('exec_daily_20250919')">Download</button>
                            </div>
                            <div style="margin: 10px 0; font-size: 14px; color: #64748b;">
                                15 pages • PDF • 2.3 MB
                            </div>
                        </div>
                        
                        <div class="report-preview">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>AI Optimization Report</strong>
                                    <div style="font-size: 12px; color: #94a3b8;">Generated 6 hours ago</div>
                                </div>
                                <button class="btn download" onclick="downloadReport('ai_opt_20250919')">Download</button>
                            </div>
                            <div style="margin: 10px 0; font-size: 14px; color: #64748b;">
                                22 pages • PDF • 4.1 MB
                            </div>
                        </div>
                        
                        <div class="report-preview">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>Platform Performance - Weekly</strong>
                                    <div style="font-size: 12px; color: #94a3b8;">Generated yesterday</div>
                                </div>
                                <button class="btn download" onclick="downloadReport('platform_weekly_20250918')">Download</button>
                            </div>
                            <div style="margin: 10px 0; font-size: 14px; color: #64748b;">
                                31 pages • PDF • 6.8 MB
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>⚙️ Custom Report Builder</h2>
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 5px;">Report Name:</label>
                        <input type="text" class="form-input" placeholder="Enter report name" id="customReportName">
                    </div>
                    
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 5px;">Time Period:</label>
                        <select class="form-input" id="timePeriod">
                            <option value="last_24h">Last 24 Hours</option>
                            <option value="last_7d">Last 7 Days</option>
                            <option value="last_30d" selected>Last 30 Days</option>
                            <option value="last_90d">Last 90 Days</option>
                            <option value="custom">Custom Range</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 5px;">Data Sources:</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px;">
                            <label style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox" checked> Platform Metrics
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox" checked> AI Analytics
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox"> Service Logs
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox"> Cost Data
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox"> User Analytics
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox"> Security Events
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 5px;">Output Format:</label>
                        <select class="form-input" id="outputFormat">
                            <option value="pdf">PDF Report</option>
                            <option value="excel">Excel Workbook</option>
                            <option value="dashboard">Interactive Dashboard</option>
                            <option value="csv">CSV Data Export</option>
                        </select>
                    </div>
                    
                    <button class="btn generate" onclick="buildCustomReport()" style="width: 100%; margin-top: 20px;">Build Custom Report</button>
                </div>
            </div>
        </div>
        
        <script>
            let selectedFormat = 'pdf';
            
            function generateReport(template) {
                console.log(`Generating report: ${template}`);
                alert(`Generating ${template} report. You'll receive a notification when it's ready.`);
            }
            
            function scheduleReport(template) {
                console.log(`Scheduling report: ${template}`);
                const frequency = prompt('Select frequency (daily, weekly, monthly):');
                if (frequency) {
                    alert(`${template} report scheduled for ${frequency} generation.`);
                }
            }
            
            function downloadSample(template) {
                console.log(`Downloading sample: ${template}`);
                alert(`Downloading sample ${template} report...`);
            }
            
            function downloadReport(reportId) {
                console.log(`Downloading report: ${reportId}`);
                alert(`Downloading report ${reportId}...`);
            }
            
            function selectFormat(format) {
                selectedFormat = format;
                
                // Update UI
                document.querySelectorAll('.export-btn').forEach(btn => {
                    btn.classList.remove('selected');
                });
                event.target.classList.add('selected');
                
                console.log(`Selected format: ${format}`);
            }
            
            function buildCustomReport() {
                const name = document.getElementById('customReportName').value;
                const timePeriod = document.getElementById('timePeriod').value;
                const outputFormat = document.getElementById('outputFormat').value;
                
                if (!name) {
                    alert('Please enter a report name.');
                    return;
                }
                
                console.log(`Building custom report: ${name}, ${timePeriod}, ${outputFormat}`);
                alert(`Custom report "${name}" is being generated. You'll receive it in ${outputFormat} format.`);
                
                // Clear form
                document.getElementById('customReportName').value = '';
            }
            
            // Simulate real-time updates
            function updateMetrics() {
                const reportsToday = Math.floor(Math.random() * 3) + 7;
                const scheduledReports = Math.floor(Math.random() * 4) + 10;
                
                document.getElementById('reportsToday').textContent = reportsToday;
                document.getElementById('scheduledReports').textContent = scheduledReports;
            }
            
            setInterval(updateMetrics, 45000);
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "reports-export", "timestamp": datetime.now().isoformat()}

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with service_monitor.track_operation(f"execute_{action}"):
            if action == "generate_report":
                analysis_id = parameters.get("analysis_id")
                report_data = {
                    "report_id": f"report_{int(time.time())}",
                    "workflow_id": workflow_context.get("workflow_id"),
                    "analysis_id": analysis_id,
                    "report_type": "workflow_summary",
                    "generated_at": datetime.now(),
                    "status": "completed"
                }
                if db:
                    db.collection("generated_reports").document(report_data["report_id"]).set(report_data)

                return {
                    "success": True,
                    "action": action,
                    "output": {"report_id": report_data["report_id"], "report_ready": True},
                    "execution_time": time.time(),
                    "service": "reports-export"
                }

            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not supported by reports-export",
                    "supported_actions": ["generate_report"],
                    "service": "reports-export"
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "action": request.get("action"),
            "service": "reports-export"
        }

@app.post("/api/reports/generate")
async def generate_report(report_data: Dict[str, Any]):
    """Generate a new report from template or custom specification"""
    try:
        report_id = f"rpt_{uuid.uuid4().hex[:8]}"
        template = report_data.get("template", "")
        format_type = report_data.get("format", "pdf")
        time_period = report_data.get("time_period", "last_7d")
        custom_sections = report_data.get("sections", [])
        
        if template and template not in REPORT_TEMPLATES:
            raise HTTPException(status_code=400, detail="Invalid report template")
        
        # Create report generation job
        report_job = {
            "id": report_id,
            "template": template,
            "format": format_type,
            "time_period": time_period,
            "sections": custom_sections if custom_sections else REPORT_TEMPLATES.get(template, {}).get("sections", []),
            "status": "generating",
            "created_at": datetime.now(),
            "created_by": "system",
            "progress": 0,
            "estimated_completion": datetime.now() + timedelta(minutes=5),
            "file_path": None,
            "file_size": None
        }
        
        # Store job
        db.collection("report_jobs").document(report_id).set(report_job)
        
        # Start report generation in background
        asyncio.create_task(generate_report_content(report_id))
        
        # Publish report generation event
        topic_path = publisher.topic_path(PROJECT_ID, "xynergy-reports-events")
        message_data = json.dumps({
            "event_type": "report_generation_started",
            "report_id": report_id,
            "template": template,
            "format": format_type,
            "timestamp": datetime.now().isoformat()
        }).encode("utf-8")
        
        publisher.publish(topic_path, message_data)
        
        return {
            "report_id": report_id,
            "status": "generating",
            "estimated_completion": report_job["estimated_completion"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

@app.get("/api/reports/{report_id}")
async def get_report_status(report_id: str):
    """Get report generation status"""
    try:
        doc_ref = db.collection("report_jobs").document(report_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_data = doc.to_dict()
        
        # Convert timestamps
        for field in ["created_at", "estimated_completion", "completed_at"]:
            if report_data.get(field):
                report_data[field] = report_data[field].isoformat()
        
        return report_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report status error: {str(e)}")

@app.get("/api/reports/{report_id}/download")
async def download_report(report_id: str):
    """Download a completed report"""
    try:
        doc_ref = db.collection("report_jobs").document(report_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_data = doc.to_dict()
        
        if report_data["status"] != "completed":
            raise HTTPException(status_code=400, detail="Report is not ready for download")
        
        # Generate sample report content for demo
        if report_data["format"] == "pdf":
            pdf_content = await generate_sample_pdf_report(report_data)
            
            return StreamingResponse(
                io.BytesIO(pdf_content),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"}
            )
        elif report_data["format"] == "excel":
            excel_content = await generate_sample_excel_report(report_data)
            
            return StreamingResponse(
                io.BytesIO(excel_content),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=report_{report_id}.xlsx"}
            )
        elif report_data["format"] == "csv":
            csv_content = await generate_sample_csv_report(report_data)
            
            return StreamingResponse(
                io.StringIO(csv_content),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=report_{report_id}.csv"}
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report download error: {str(e)}")

@app.get("/api/reports")
async def get_reports(status: Optional[str] = None, limit: int = 20):
    """Get list of reports with optional status filter"""
    try:
        reports_ref = db.collection("report_jobs").order_by("created_at", direction=firestore.Query.DESCENDING).limit(limit)
        
        if status:
            reports_ref = reports_ref.where("status", "==", status)
        
        reports = []
        for doc in reports_ref.stream():
            report_data = doc.to_dict()
            
            # Convert timestamps
            for field in ["created_at", "estimated_completion", "completed_at"]:
                if report_data.get(field):
                    report_data[field] = report_data[field].isoformat()
            
            reports.append(report_data)
        
        return reports
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reports retrieval error: {str(e)}")

@app.get("/api/templates")
async def get_report_templates():
    """Get available report templates"""
    return REPORT_TEMPLATES

@app.post("/api/reports/schedule")
async def schedule_report(schedule_data: Dict[str, Any]):
    """Schedule recurring report generation"""
    try:
        schedule_id = f"rpt_sched_{uuid.uuid4().hex[:8]}"
        template = schedule_data.get("template", "")
        frequency = schedule_data.get("frequency", "weekly")
        format_type = schedule_data.get("format", "pdf")
        recipients = schedule_data.get("recipients", [])
        
        if template not in REPORT_TEMPLATES:
            raise HTTPException(status_code=400, detail="Invalid report template")
        
        # Create schedule
        schedule_doc = {
            "id": schedule_id,
            "template": template,
            "frequency": frequency,
            "format": format_type,
            "recipients": recipients,
            "enabled": True,
            "created_at": datetime.now(),
            "last_generated": None,
            "next_generation": None,  # Would calculate based on frequency
            "generation_count": 0
        }
        
        db.collection("report_schedules").document(schedule_id).set(schedule_doc)
        
        return {
            "schedule_id": schedule_id,
            "status": "scheduled",
            "frequency": frequency,
            "template": template
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report scheduling error: {str(e)}")

async def generate_report_content(report_id: str):
    """Background task to generate report content"""
    try:
        doc_ref = db.collection("report_jobs").document(report_id)
        
        # Simulate report generation progress
        for progress in [20, 40, 60, 80, 100]:
            await asyncio.sleep(1)  # Simulate processing time
            
            doc_ref.update({
                "progress": progress,
                "status": "generating" if progress < 100 else "completed",
                "completed_at": datetime.now() if progress == 100 else None
            })
        
        # Mark as completed
        doc_ref.update({
            "status": "completed",
            "completed_at": datetime.now(),
            "file_path": f"reports/{report_id}",
            "file_size": "2.3 MB"
        })
        
        # Publish completion event
        topic_path = publisher.topic_path(PROJECT_ID, "xynergy-reports-events")
        message_data = json.dumps({
            "event_type": "report_generation_completed",
            "report_id": report_id,
            "timestamp": datetime.now().isoformat()
        }).encode("utf-8")
        
        publisher.publish(topic_path, message_data)
        
    except Exception as e:
        print(f"Report generation error: {e}")
        doc_ref.update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now()
        })

async def generate_sample_pdf_report(report_data: Dict[str, Any]) -> bytes:
    """Generate a sample PDF report"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            # Create PDF document
            doc = SimpleDocTemplate(tmp_file.name, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            
            story.append(Paragraph(f"Xynergy Platform Report", title_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Paragraph(
                "This report provides a comprehensive overview of the Xynergy platform performance, "
                "including AI cost optimization, service metrics, and business intelligence insights.",
                styles['Normal']
            ))
            story.append(Spacer(1, 20))
            
            # Key Metrics Table
            story.append(Paragraph("Key Performance Indicators", styles['Heading2']))
            
            metrics_data = [
                ['Metric', 'Value', 'Change'],
                ['Platform Uptime', '99.8%', '+0.2%'],
                ['AI Cost Savings', '$2,347', '+45%'],
                ['Total Requests', '45,213', '+23%'],
                ['Response Time', '1.2s', '-12%'],
                ['Success Rate', '99.7%', '+0.1%']
            ]
            
            metrics_table = Table(metrics_data)
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metrics_table)
            story.append(Spacer(1, 20))
            
            # Recommendations
            story.append(Paragraph("Recommendations", styles['Heading2']))
            recommendations = [
                "Continue optimizing AI routing to maintain cost savings",
                "Monitor service performance during peak usage hours", 
                "Implement additional automation workflows",
                "Expand analytics coverage for deeper insights"
            ]
            
            for rec in recommendations:
                story.append(Paragraph(f"• {rec}", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            # Read file content
            with open(tmp_file.name, 'rb') as f:
                pdf_content = f.read()
            
            return pdf_content
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return b""

async def generate_sample_excel_report(report_data: Dict[str, Any]) -> bytes:
    """Generate a sample Excel report"""
    try:
        # Create sample data
        data = {
            'Service': ['Marketing Engine', 'AI Routing', 'Content Hub', 'Analytics', 'Scheduler'],
            'Requests': [12847, 8934, 5623, 3421, 1876],
            'Response Time (ms)': [1200, 890, 1450, 2300, 670],
            'Success Rate (%)': [99.8, 99.7, 99.9, 99.5, 99.9],
            'Cost ($)': [234.56, 123.45, 167.89, 89.34, 45.67]
        }
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Platform Metrics', index=False)
            
            # Add more sheets with sample data
            cost_data = pd.DataFrame({
                'Date': pd.date_range('2025-09-01', '2025-09-19'),
                'Internal AI Cost': [12.34, 13.45, 11.23, 14.56, 12.89] * 4,
                'External API Cost': [123.45, 134.56, 112.34, 145.67, 128.90] * 4,
                'Total Savings': [111.11, 121.11, 101.11, 131.11, 116.01] * 4
            })
            cost_data.to_excel(writer, sheet_name='Cost Analysis', index=False)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        print(f"Excel generation error: {e}")
        return b""

async def generate_sample_csv_report(report_data: Dict[str, Any]) -> str:
    """Generate a sample CSV report"""
    try:
        csv_data = """Service,Requests,Response_Time_ms,Success_Rate_percent,Cost_USD
Marketing Engine,12847,1200,99.8,234.56
AI Routing,8934,890,99.7,123.45
Content Hub,5623,1450,99.9,167.89
Analytics,3421,2300,99.5,89.34
Scheduler,1876,670,99.9,45.67
Internal AI,7234,2100,99.6,12.34
System Runtime,4567,1100,99.8,78.90
Secrets Config,2345,980,99.9,34.56"""
        
        return csv_data
        
    except Exception as e:
        print(f"CSV generation error: {e}")
        return ""


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
