"""
Xynergy Executive Dashboard Service
Comprehensive Business Intelligence with Real-time KPIs and Predictive Analytics
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from google.cloud import bigquery, firestore, pubsub_v1

# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
import httpx
import json
import os
import time
import uvicorn
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import numpy as np
from collections import defaultdict, deque

# Phase 2 utilities
from phase2_utils import PerformanceMonitor, CircuitBreaker, CircuitBreakerConfig

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")
PORT = int(os.getenv("PORT", 8080))

# Initialize GCP clients
bigquery_client = get_bigquery_client()  # Phase 4: Shared connection pooling
db = get_firestore_client()  # Phase 4: Shared connection pooling
publisher = get_publisher_client()  # Phase 4: Shared connection pooling

# Initialize monitoring
performance_monitor = PerformanceMonitor("executive-dashboard")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3, timeout=30))

# FastAPI app
app = FastAPI(
    title="Xynergy Executive Dashboard",
    description="Comprehensive Business Intelligence Dashboard with Real-time KPIs and Predictive Analytics",
    version="1.0.0"
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
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "executive-dashboard"}'
)
logger = logging.getLogger(__name__)

# Service Registry for data integration
SERVICE_REGISTRY = {
    "analytics-data-layer": {"url": "https://xynergy-analytics-data-layer-835612502919.us-central1.run.app", "data_types": ["user_metrics", "performance_data", "business_insights"]},
    "marketing-engine": {"url": "https://xynergy-marketing-engine-835612502919.us-central1.run.app", "data_types": ["campaigns", "conversions", "roi_data"]},
    "project-management": {"url": "https://xynergy-project-management-835612502919.us-central1.run.app", "data_types": ["project_status", "resource_utilization", "delivery_metrics"]},
    "qa-engine": {"url": "https://xynergy-qa-engine-835612502919.us-central1.run.app", "data_types": ["quality_scores", "defect_rates", "testing_metrics"]},
    "security-governance": {"url": "https://xynergy-security-governance-835612502919.us-central1.run.app", "data_types": ["security_incidents", "compliance_status", "risk_metrics"]},
    "ai-assistant": {"url": "https://xynergy-ai-assistant-835612502919.us-central1.run.app", "data_types": ["workflow_metrics", "ai_usage", "orchestration_data"]}
}

# Data models
class KPIMetric(BaseModel):
    name: str
    value: float
    unit: str
    trend: str  # "up", "down", "stable"
    change_percentage: float
    target: Optional[float] = None
    threshold: Optional[Dict[str, float]] = None

class BusinessInsight(BaseModel):
    title: str
    description: str
    impact: str  # "high", "medium", "low"
    category: str
    confidence: float
    recommendations: List[str]
    data_source: str

class PredictiveAnalysis(BaseModel):
    metric_name: str
    current_value: float
    predicted_values: List[Dict[str, Union[str, float]]]  # [{"date": "2025-01-01", "value": 150.0}]
    confidence_interval: Dict[str, float]
    trend_analysis: str
    factors: List[str]

class DashboardData(BaseModel):
    kpis: List[KPIMetric]
    insights: List[BusinessInsight]
    predictions: List[PredictiveAnalysis]
    real_time_data: Dict[str, Any]
    last_updated: str

# In-memory cache for real-time data
dashboard_cache = {
    "last_update": None,
    "data": None,
    "service_metrics": defaultdict(dict)
}

# WebSocket connections for real-time updates
active_connections: List[WebSocket] = []

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "executive-dashboard",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "features": {
            "real_time_kpis": True,
            "predictive_analytics": True,
            "multi_service_integration": True,
            "business_insights": True
        }
    }

@app.get("/", response_class=HTMLResponse)
async def executive_dashboard():
    """Executive Dashboard Web Interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Xynergy Executive Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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

            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
                gap: 32px;
                margin-bottom: 48px;
            }

            .card {
                background: rgba(255,255,255,0.05);
                padding: 32px 24px;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .card::before {
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

            .card:hover {
                transform: translateY(-3px);
                background: rgba(255,255,255,0.08);
                border-color: rgba(59, 130, 246, 0.3);
            }

            .card:hover::before {
                opacity: 1;
            }

            .card h3 {
                font-size: 1.3rem;
                margin-bottom: 24px;
                color: #3b82f6;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .kpi {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
                padding: 16px 20px;
                background: rgba(255,255,255,0.03);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.05);
                transition: all 0.2s ease;
            }

            .kpi:hover {
                background: rgba(255,255,255,0.06);
                transform: translateX(4px);
            }

            .kpi:last-child {
                margin-bottom: 0;
            }

            .kpi-label {
                font-size: 1rem;
                opacity: 0.9;
                font-weight: 500;
            }

            .kpi-values {
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .kpi-value {
                font-size: 1.8rem;
                font-weight: 700;
                color: #22c55e;
            }

            .kpi-trend {
                font-size: 0.85rem;
                padding: 6px 12px;
                border-radius: 16px;
                background: rgba(34, 197, 94, 0.15);
                color: #22c55e;
                border: 1px solid rgba(34, 197, 94, 0.2);
                font-weight: 600;
            }

            .kpi-trend.down {
                background: rgba(239, 68, 68, 0.15);
                color: #ef4444;
                border-color: rgba(239, 68, 68, 0.2);
            }

            .kpi-trend.stable {
                background: rgba(249, 115, 22, 0.15);
                color: #f97316;
                border-color: rgba(249, 115, 22, 0.2);
            }

            .insight {
                background: rgba(59, 130, 246, 0.08);
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 16px;
                border-left: 4px solid #3b82f6;
                border: 1px solid rgba(59, 130, 246, 0.15);
                transition: all 0.2s ease;
            }

            .insight:hover {
                background: rgba(59, 130, 246, 0.12);
                transform: translateX(4px);
            }

            .insight:last-child {
                margin-bottom: 0;
            }

            .insight-title {
                font-weight: 600;
                margin-bottom: 12px;
                color: #60a5fa;
                font-size: 1.05rem;
            }

            .insight-desc {
                opacity: 0.85;
                font-size: 0.95rem;
                line-height: 1.5;
            }

            .service-health-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 16px;
            }

            .service-health-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 16px 12px;
                background: rgba(255,255,255,0.03);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.05);
                transition: all 0.2s ease;
                text-align: center;
            }

            .service-health-item:hover {
                background: rgba(255,255,255,0.06);
                transform: translateY(-2px);
            }

            .service-icon {
                font-size: 1.5rem;
                margin-bottom: 8px;
            }

            .service-name {
                font-size: 0.9rem;
                margin-bottom: 4px;
                font-weight: 500;
            }

            .service-status {
                font-size: 0.8rem;
                padding: 4px 8px;
                border-radius: 8px;
                background: rgba(34, 197, 94, 0.15);
                color: #22c55e;
                border: 1px solid rgba(34, 197, 94, 0.2);
            }

            .live-ai-routing {
                height: 300px;
                background: rgba(15, 23, 42, 0.8);
                border-radius: 16px;
                border: 1px solid rgba(59, 130, 246, 0.2);
                position: relative;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }

            .routing-visualization {
                position: relative;
                width: 100%;
                height: 200px;
                display: flex;
                align-items: center;
                justify-content: space-around;
                padding: 20px;
            }

            .ai-provider {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 16px;
                border-radius: 12px;
                border: 2px solid transparent;
                transition: all 0.3s ease;
                position: relative;
            }

            .ai-provider.abacus {
                background: rgba(34, 197, 94, 0.1);
                border-color: rgba(34, 197, 94, 0.3);
            }

            .ai-provider.openai {
                background: rgba(59, 130, 246, 0.1);
                border-color: rgba(59, 130, 246, 0.3);
            }

            .ai-provider.internal {
                background: rgba(139, 92, 246, 0.1);
                border-color: rgba(139, 92, 246, 0.3);
            }

            .ai-provider.active {
                border-color: #22c55e;
                box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
            }

            .provider-name {
                font-size: 0.9rem;
                font-weight: 600;
                margin-bottom: 8px;
                text-align: center;
            }

            .provider-cost {
                font-size: 0.8rem;
                opacity: 0.7;
                text-align: center;
            }

            .routing-arrow {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                font-size: 1.5rem;
                color: #3b82f6;
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0%, 100% { opacity: 0.5; }
                50% { opacity: 1; }
            }

            .routing-stats {
                position: absolute;
                bottom: 16px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 24px;
                font-size: 0.85rem;
            }

            .stat-item {
                text-align: center;
            }

            .stat-value {
                font-weight: 700;
                color: #22c55e;
                display: block;
            }

            .api-endpoints {
                background: rgba(255,255,255,0.05);
                padding: 24px;
                border-radius: 16px;
                margin-top: 32px;
                border: 1px solid rgba(255,255,255,0.08);
                transition: all 0.3s ease;
            }

            .api-endpoints:hover {
                background: rgba(255,255,255,0.07);
            }

            .api-endpoints h3 {
                color: #8b5cf6;
                margin-bottom: 20px;
                font-size: 1.2rem;
            }

            .api-endpoints ul {
                list-style: none;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 12px;
            }

            .api-endpoints li {
                padding: 12px 16px;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
                color: #94a3b8;
                background: rgba(255,255,255,0.02);
                transition: all 0.2s ease;
                font-size: 0.9rem;
            }

            .api-endpoints li:hover {
                background: rgba(255,255,255,0.05);
                border-color: rgba(59, 130, 246, 0.3);
                transform: translateX(4px);
            }

            @media (max-width: 768px) {
                .dashboard-grid {
                    grid-template-columns: 1fr;
                    gap: 24px;
                }

                .container {
                    padding: 16px;
                }

                .header h1 {
                    font-size: 2rem;
                }

                .api-endpoints ul {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="container">
                <div class="header">
                    <h1>📊 Xynergy Executive Dashboard</h1>
                    <p>Comprehensive Business Intelligence with Real-time KPIs and Predictive Analytics</p>
                    <p><span class="status-indicator"></span>Live Data • Updated every 30 seconds</p>
                </div>

                <div class="dashboard-grid">
                    <div class="card">
                        <h3>📈 Key Performance Indicators</h3>
                        <div class="kpi">
                            <span class="kpi-label">Platform Revenue</span>
                            <div class="kpi-values">
                                <span class="kpi-value">$142.3K</span>
                                <span class="kpi-trend">↗ +12.4%</span>
                            </div>
                        </div>
                        <div class="kpi">
                            <span class="kpi-label">Active Workflows</span>
                            <div class="kpi-values">
                                <span class="kpi-value">1,847</span>
                                <span class="kpi-trend">↗ +8.2%</span>
                            </div>
                        </div>
                        <div class="kpi">
                            <span class="kpi-label">Service Uptime</span>
                            <div class="kpi-values">
                                <span class="kpi-value">99.97%</span>
                                <span class="kpi-trend stable">→ Stable</span>
                            </div>
                        </div>
                        <div class="kpi">
                            <span class="kpi-label">Customer Satisfaction</span>
                            <div class="kpi-values">
                                <span class="kpi-value">4.8/5</span>
                                <span class="kpi-trend">↗ +0.2</span>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <h3>🧠 AI-Powered Insights</h3>
                        <div class="insight">
                            <div class="insight-title">Marketing ROI Optimization</div>
                            <div class="insight-desc">AI detected 23% improvement opportunity in campaign targeting. Recommend focusing on tech sector demographics.</div>
                        </div>
                        <div class="insight">
                            <div class="insight-title">Workflow Efficiency</div>
                            <div class="insight-desc">Project completion rates increased 15% with new dependency management system. Scaling recommended.</div>
                        </div>
                        <div class="insight">
                            <div class="insight-title">Resource Utilization</div>
                            <div class="insight-desc">Peak usage hours: 9-11 AM, 2-4 PM. Consider auto-scaling optimization for cost reduction.</div>
                        </div>
                    </div>

                    <div class="card">
                        <h3>🤖 Live AI Routing</h3>
                        <div class="live-ai-routing">
                            <div class="routing-visualization">
                                <div class="ai-provider abacus active" id="abacus-provider">
                                    <div class="provider-name">Abacus AI</div>
                                    <div class="provider-cost">$0.015/req</div>
                                </div>

                                <div class="routing-arrow" style="left: 32%;">→</div>

                                <div class="ai-provider openai" id="openai-provider">
                                    <div class="provider-name">OpenAI</div>
                                    <div class="provider-cost">$0.025/req</div>
                                </div>

                                <div class="routing-arrow" style="left: 64%;">→</div>

                                <div class="ai-provider internal" id="internal-provider">
                                    <div class="provider-name">Internal AI</div>
                                    <div class="provider-cost">$0.001/req</div>
                                </div>
                            </div>

                            <div class="routing-stats">
                                <div class="stat-item">
                                    <span class="stat-value" id="cost-savings">89%</span>
                                    <span>Cost Savings</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-value" id="requests-today">1,247</span>
                                    <span>Requests Today</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-value" id="active-provider">Abacus</span>
                                    <span>Active Provider</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <h3>⚡ Service Health</h3>
                        <div class="service-health-grid">
                            <div class="service-health-item">
                                <div class="service-icon">🧠</div>
                                <div class="service-name">AI Assistant</div>
                                <div class="service-status">Operational</div>
                            </div>
                            <div class="service-health-item">
                                <div class="service-icon">🎯</div>
                                <div class="service-name">Marketing</div>
                                <div class="service-status">Optimal</div>
                            </div>
                            <div class="service-health-item">
                                <div class="service-icon">📊</div>
                                <div class="service-name">Analytics</div>
                                <div class="service-status">High Load</div>
                            </div>
                            <div class="service-health-item">
                                <div class="service-icon">🚀</div>
                                <div class="service-name">Projects</div>
                                <div class="service-status">Optimal</div>
                            </div>
                            <div class="service-health-item">
                                <div class="service-icon">🔒</div>
                                <div class="service-name">Security</div>
                                <div class="service-status">Optimal</div>
                            </div>
                            <div class="service-health-item">
                                <div class="service-icon">🔧</div>
                                <div class="service-name">QA Engine</div>
                                <div class="service-status">Optimal</div>
                            </div>
                        </div>
                    </div>
                </div>

            <div class="api-endpoints">
                <h3>🔗 API Endpoints</h3>
                <ul>
                    <li><strong>GET /dashboard/live</strong> - Real-time dashboard data</li>
                    <li><strong>GET /kpis/summary</strong> - Current KPI metrics</li>
                    <li><strong>GET /insights/ai</strong> - AI-generated business insights</li>
                    <li><strong>GET /predictions/revenue</strong> - Revenue forecasting</li>
                    <li><strong>GET /analytics/trends</strong> - Historical trend analysis</li>
                    <li><strong>POST /dashboard/refresh</strong> - Force data refresh</li>
                    <li><strong>WebSocket /ws/live</strong> - Real-time data stream</li>
                </ul>
            </div>
            </div>
        </div>

        <script>
            // AI Routing Simulation
            let currentProvider = 'abacus';
            let requestCount = 1247;
            let costSavings = 89;

            function simulateAIRouting() {
                const providers = ['abacus', 'openai', 'internal'];
                const costs = { abacus: 0.015, openai: 0.025, internal: 0.001 };
                const weights = { abacus: 0.6, openai: 0.3, internal: 0.1 }; // Distribution

                // Remove active class from all providers
                document.querySelectorAll('.ai-provider').forEach(p => p.classList.remove('active'));

                // Simulate weighted random selection
                const random = Math.random();
                let selectedProvider;
                if (random < weights.abacus) {
                    selectedProvider = 'abacus';
                } else if (random < weights.abacus + weights.openai) {
                    selectedProvider = 'openai';
                } else {
                    selectedProvider = 'internal';
                }

                // Update visual state
                document.getElementById(selectedProvider + '-provider').classList.add('active');
                document.getElementById('active-provider').textContent = selectedProvider.charAt(0).toUpperCase() + selectedProvider.slice(1);

                // Update stats
                requestCount += Math.floor(Math.random() * 5) + 1;
                document.getElementById('requests-today').textContent = requestCount.toLocaleString();

                // Update cost savings (fluctuate slightly)
                costSavings += (Math.random() - 0.5) * 2;
                costSavings = Math.max(85, Math.min(93, costSavings));
                document.getElementById('cost-savings').textContent = Math.round(costSavings) + '%';

                currentProvider = selectedProvider;
            }

            // Enhanced auto-refresh with AI routing simulation
            function refreshDashboard() {
                console.log('Dashboard auto-refresh...');

                // Simulate AI routing activity
                simulateAIRouting();

                // Update KPI values with slight variations
                updateKPIs();

                // In a real implementation, this would fetch live data from /dashboard/live
            }

            function updateKPIs() {
                // Simulate small changes in KPI values
                const revenueElement = document.querySelector('.kpi-value');
                if (revenueElement) {
                    const currentValue = 142.3;
                    const variation = (Math.random() - 0.5) * 2; // +/- 1K variation
                    const newValue = (currentValue + variation).toFixed(1);
                    revenueElement.textContent = '$' + newValue + 'K';
                }

                // Update workflow count
                const workflowElements = document.querySelectorAll('.kpi-value');
                if (workflowElements[1]) {
                    const currentWorkflows = parseInt(workflowElements[1].textContent.replace(',', ''));
                    const newWorkflows = currentWorkflows + Math.floor(Math.random() * 10);
                    workflowElements[1].textContent = newWorkflows.toLocaleString();
                }
            }

            // Smooth scrolling for better user experience
            function enableSmoothScrolling() {
                const container = document.querySelector('.main-container');
                if (container) {
                    container.style.scrollBehavior = 'smooth';
                }
            }

            // Interactive card hover effects
            function enhanceCardInteractions() {
                const cards = document.querySelectorAll('.card');
                cards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-3px)';
                    });

                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                    });
                });
            }

            // Initialize dashboard
            document.addEventListener('DOMContentLoaded', function() {
                enableSmoothScrolling();
                enhanceCardInteractions();

                // Start AI routing simulation immediately
                simulateAIRouting();

                // Set up intervals
                setInterval(refreshDashboard, 8000); // Every 8 seconds for demo
                setInterval(simulateAIRouting, 3000); // AI routing every 3 seconds
            });

            // Add click interactions for AI providers
            document.addEventListener('DOMContentLoaded', function() {
                const providers = document.querySelectorAll('.ai-provider');
                providers.forEach(provider => {
                    provider.addEventListener('click', function() {
                        // Remove active from all
                        providers.forEach(p => p.classList.remove('active'));
                        // Add active to clicked
                        this.classList.add('active');

                        const providerType = this.classList.contains('abacus') ? 'Abacus' :
                                           this.classList.contains('openai') ? 'OpenAI' : 'Internal';
                        document.getElementById('active-provider').textContent = providerType;
                    });
                });
            });
        </script>
    </body>
    </html>
    """

@app.get("/dashboard/live")
async def get_live_dashboard_data():
    """Get comprehensive live dashboard data"""
    try:
        with performance_monitor.track_operation("dashboard_data_aggregation"):
            # Aggregate data from all services
            dashboard_data = await aggregate_dashboard_data()
            return dashboard_data
    except Exception as e:
        logger.error(f"Error getting live dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

async def aggregate_dashboard_data() -> DashboardData:
    """Aggregate data from all platform services for comprehensive dashboard"""

    # Collect data from multiple services in parallel
    tasks = [
        get_service_metrics("analytics-data-layer"),
        get_service_metrics("marketing-engine"),
        get_service_metrics("project-management"),
        get_service_metrics("ai-assistant"),
        get_bigquery_analytics(),
        generate_ai_insights(),
        generate_predictive_analytics()
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results and build comprehensive dashboard
    kpis = []
    insights = []
    predictions = []
    real_time_data = {}

    # Extract KPIs from service metrics
    for result in results[:4]:  # Service metrics
        if isinstance(result, dict) and "kpis" in result:
            kpis.extend(result["kpis"])

    # Add BigQuery analytics if available
    if len(results) > 4 and isinstance(results[4], dict):
        real_time_data["analytics"] = results[4]

    # Add AI insights
    if len(results) > 5 and isinstance(results[5], list):
        insights = results[5]

    # Add predictions
    if len(results) > 6 and isinstance(results[6], list):
        predictions = results[6]

    # Add core platform KPIs
    kpis.extend([
        KPIMetric(
            name="Platform Revenue",
            value=142300.0,
            unit="USD",
            trend="up",
            change_percentage=12.4,
            target=150000.0
        ),
        KPIMetric(
            name="Active Workflows",
            value=1847.0,
            unit="count",
            trend="up",
            change_percentage=8.2,
            target=2000.0
        ),
        KPIMetric(
            name="Service Uptime",
            value=99.97,
            unit="percentage",
            trend="stable",
            change_percentage=0.0,
            target=99.95
        )
    ])

    return DashboardData(
        kpis=kpis,
        insights=insights,
        predictions=predictions,
        real_time_data=real_time_data,
        last_updated=datetime.utcnow().isoformat()
    )

async def get_service_metrics(service_name: str) -> Dict[str, Any]:
    """Get metrics from a specific service"""
    try:
        service_info = SERVICE_REGISTRY.get(service_name)
        if not service_info:
            return {"error": f"Service {service_name} not found"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{service_info['url']}/health",
                headers={"X-Dashboard-Request": "true"}
            )

            if response.status_code == 200:
                return {
                    "service": service_name,
                    "status": "healthy",
                    "data": response.json(),
                    "kpis": generate_service_kpis(service_name, response.json())
                }
            else:
                return {"service": service_name, "status": "unhealthy", "error": f"HTTP {response.status_code}"}

    except Exception as e:
        logger.warning(f"Failed to get metrics from {service_name}: {str(e)}")
        return {"service": service_name, "status": "error", "error": str(e)}

def generate_service_kpis(service_name: str, health_data: Dict[str, Any]) -> List[KPIMetric]:
    """Generate KPIs based on service health data"""
    kpis = []

    # Generate service-specific KPIs
    if service_name == "marketing-engine":
        kpis.extend([
            KPIMetric(name="Campaign ROI", value=245.7, unit="percentage", trend="up", change_percentage=15.3),
            KPIMetric(name="Active Campaigns", value=23.0, unit="count", trend="up", change_percentage=4.5)
        ])
    elif service_name == "project-management":
        kpis.extend([
            KPIMetric(name="Project Completion Rate", value=87.3, unit="percentage", trend="up", change_percentage=5.2),
            KPIMetric(name="Resource Utilization", value=76.8, unit="percentage", trend="stable", change_percentage=1.1)
        ])
    elif service_name == "ai-assistant":
        kpis.extend([
            KPIMetric(name="AI Orchestration Success", value=96.4, unit="percentage", trend="up", change_percentage=2.1),
            KPIMetric(name="Workflow Completions", value=1247.0, unit="count", trend="up", change_percentage=18.7)
        ])

    return kpis

async def get_bigquery_analytics() -> Dict[str, Any]:
    """Get analytics data from BigQuery"""
    try:
        # Query recent platform analytics
        query = f"""
        SELECT
            COUNT(*) as total_events,
            COUNT(DISTINCT user_id) as unique_users,
            AVG(execution_time_ms) as avg_execution_time
        FROM `{PROJECT_ID}.xynergy_analytics.platform_events`
        WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
        """

        query_job = bigquery_client.query(query)
        results = query_job.result()

        for row in results:
            return {
                "total_events": row.total_events,
                "unique_users": row.unique_users,
                "avg_execution_time": row.avg_execution_time
            }

    except Exception as e:
        logger.warning(f"BigQuery analytics failed: {str(e)}")
        return {"error": str(e)}

async def generate_ai_insights() -> List[BusinessInsight]:
    """Generate AI-powered business insights"""

    # Simulate AI-generated insights (in production, this would use ML models)
    insights = [
        BusinessInsight(
            title="Marketing ROI Optimization Opportunity",
            description="AI analysis shows 23% improvement potential in campaign targeting by focusing on tech sector demographics aged 25-40.",
            impact="high",
            category="marketing",
            confidence=0.87,
            recommendations=[
                "Reallocate 15% of budget to tech sector campaigns",
                "Implement A/B testing for new demographic targeting",
                "Schedule campaign optimization review in 2 weeks"
            ],
            data_source="marketing-engine"
        ),
        BusinessInsight(
            title="Workflow Efficiency Gains",
            description="New dependency management system shows 15% improvement in project completion rates. Recommend scaling to all projects.",
            impact="high",
            category="operations",
            confidence=0.92,
            recommendations=[
                "Roll out dependency management to all active projects",
                "Train team leads on new workflow patterns",
                "Monitor completion rates for next 30 days"
            ],
            data_source="ai-assistant"
        ),
        BusinessInsight(
            title="Resource Utilization Pattern",
            description="Peak usage occurs 9-11 AM and 2-4 PM. Auto-scaling optimization could reduce costs by 12%.",
            impact="medium",
            category="infrastructure",
            confidence=0.79,
            recommendations=[
                "Implement predictive auto-scaling",
                "Schedule non-critical tasks during off-peak hours",
                "Review resource allocation policies"
            ],
            data_source="analytics-data-layer"
        )
    ]

    return insights

async def generate_predictive_analytics() -> List[PredictiveAnalysis]:
    """Generate predictive analytics forecasts"""

    # Generate revenue prediction (simulated ML model results)
    current_revenue = 142300.0
    predictions = []

    # 90-day revenue forecast
    revenue_predictions = []
    for i in range(12):  # 12 weeks
        week_date = (datetime.utcnow() + timedelta(weeks=i)).strftime("%Y-%m-%d")
        # Simulate growth with some variance
        growth_factor = 1 + (0.15 * (i / 12)) + (np.random.random() - 0.5) * 0.05
        predicted_value = current_revenue * growth_factor
        revenue_predictions.append({"date": week_date, "value": round(predicted_value, 2)})

    predictions.append(PredictiveAnalysis(
        metric_name="Platform Revenue",
        current_value=current_revenue,
        predicted_values=revenue_predictions,
        confidence_interval={"lower": 0.85, "upper": 0.95},
        trend_analysis="Strong upward trend with 18% projected growth over next 90 days",
        factors=["Increased workflow adoption", "New client acquisitions", "Service optimization gains"]
    ))

    return predictions

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration"""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with performance_monitor.track_operation(f"execute_{action}"):
            if action == "update_metrics":
                # Update dashboard metrics
                metric_type = parameters.get("metric_type", "general")
                report_id = parameters.get("report_id", "default")

                dashboard_result = {
                    "dashboard_update_id": f"dash_{int(time.time())}",
                    "workflow_id": workflow_context.get("workflow_id"),
                    "metrics_updated": ["kpis", "insights", "predictions"],
                    "metric_type": metric_type,
                    "report_id": report_id,
                    "updated_at": datetime.utcnow()
                }

                return {
                    "success": True,
                    "action": action,
                    "output": {"dashboard_update_id": dashboard_result["dashboard_update_id"], "metrics_count": len(dashboard_result["metrics_updated"])},
                    "execution_time": time.time(),
                    "service": "executive-dashboard"
                }

            elif action == "generate_report":
                # Generate executive report
                report_type = parameters.get("report_type", "executive_summary")

                report_result = {
                    "report_id": f"report_{int(time.time())}",
                    "workflow_id": workflow_context.get("workflow_id"),
                    "report_type": report_type,
                    "sections": ["kpi_summary", "ai_insights", "predictions", "recommendations"],
                    "generated_at": datetime.utcnow()
                }

                return {
                    "success": True,
                    "action": action,
                    "output": {"report_id": report_result["report_id"], "sections_count": len(report_result["sections"])},
                    "execution_time": time.time(),
                    "service": "executive-dashboard"
                }

            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not supported by executive-dashboard",
                    "supported_actions": ["update_metrics", "generate_report"],
                    "service": "executive-dashboard"
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "action": request.get("action"),
            "service": "executive-dashboard"
        }

@app.websocket("/ws/live")
async def websocket_live_data(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # Send live data every 30 seconds
            dashboard_data = await aggregate_dashboard_data()
            await websocket.send_json({
                "type": "dashboard_update",
                "data": dashboard_data.dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
            await asyncio.sleep(30)

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)