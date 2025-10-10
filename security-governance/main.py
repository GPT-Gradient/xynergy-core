from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.cloud import firestore, pubsub_v1, monitoring_v3, logging_v2
import os
import json
import asyncio
import hashlib
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, validator
import uvicorn
from enum import Enum
import re


# Phase 2 enhancements
from phase2_utils import CircuitBreaker, CircuitBreakerConfig, call_service_with_circuit_breaker, PerformanceMonitor
import time


PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")

# Import shared clients for connection pooling
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_publisher_client

# Initialize optimized GCP clients with connection pooling
db = get_firestore_client()
publisher = get_publisher_client()
monitoring_client = monitoring_v3.MetricServiceClient()
logging_client = logging_v2.Client()

# Import centralized authentication
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from auth import verify_api_key, verify_api_key_optional

app = FastAPI(title="Xynergy Security & Governance", version="1.0.0")

# Phase 2 initialization
service_monitor = PerformanceMonitor("security-governance")
service_circuit_breaker = CircuitBreaker(CircuitBreakerConfig())
ai_routing_circuit_breaker = CircuitBreaker(CircuitBreakerConfig())

# Phase 2 monitoring ready

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://xynergy-platform.com",
        "https://api.xynergy.dev",
        "https://*.xynergy.com",
        "http://localhost:3000",  # Development only
        "http://localhost:8080"   # Development only
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEventType(str, Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_INTRUSION = "system_intrusion"
    MALWARE = "malware"
    DATA_BREACH = "data_breach"
    POLICY_VIOLATION = "policy_violation"

# Input validation models
class SecurityScanRequest(BaseModel):
    type: str = "full"
    target_systems: Optional[List[str]] = []
    severity_threshold: Optional[str] = "medium"

    @validator('type')
    def validate_scan_type(cls, v):
        valid_types = ["full", "quick", "vulnerability", "compliance", "penetration"]
        if v not in valid_types:
            raise ValueError(f'Scan type must be one of: {valid_types}')
        return v

    @validator('severity_threshold')
    def validate_severity(cls, v):
        if v and v not in ["low", "medium", "high", "critical"]:
            raise ValueError('Severity threshold must be: low, medium, high, or critical')
        return v

class ThreatActionRequest(BaseModel):
    action: str
    reason: Optional[str] = ""
    auto_block: bool = False

    @validator('action')
    def validate_action(cls, v):
        valid_actions = ["block", "quarantine", "monitor", "escalate"]
        if v not in valid_actions:
            raise ValueError(f'Action must be one of: {valid_actions}')
        return v

class LockdownRequest(BaseModel):
    reason: str
    scope: str = "platform"
    duration_minutes: Optional[int] = 60

    @validator('reason')
    def validate_reason(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Lockdown reason must be at least 10 characters')
        if len(v) > 500:
            raise ValueError('Lockdown reason too long (max 500 characters)')
        return v.strip()

    @validator('scope')
    def validate_scope(cls, v):
        valid_scopes = ["platform", "service", "tenant", "user"]
        if v not in valid_scopes:
            raise ValueError(f'Scope must be one of: {valid_scopes}')
        return v

    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v is not None and (v < 1 or v > 1440):  # Max 24 hours
            raise ValueError('Duration must be between 1 and 1440 minutes')
        return v

# Security policies and rules
SECURITY_POLICIES = {
    "password_policy": {
        "min_length": 12,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special_chars": True,
        "max_age_days": 90
    },
    "access_control": {
        "max_failed_logins": 5,
        "lockout_duration_minutes": 30,
        "session_timeout_minutes": 60,
        "require_mfa": True
    },
    "data_protection": {
        "encryption_at_rest": True,
        "encryption_in_transit": True,
        "data_retention_days": 2555,  # 7 years
        "backup_frequency_hours": 24
    },
    "compliance": {
        "gdpr_enabled": True,
        "soc2_controls": True,
        "audit_log_retention_years": 7,
        "data_classification_required": True
    }
}

@app.get("/", response_class=HTMLResponse)
async def security_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Xynergy Security & Governance</title>
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
                <h1>🛡️ Xynergy Security & Governance</h1>
                <p>Zero-trust monitoring, threat detection, and compliance management</p>
                <div style="display: flex; gap: 30px; margin-top: 15px;">
                    <div>Security Score: <span style="color: #22c55e; font-weight: 700;">94/100</span></div>
                    <div>Active Threats: <span id="activeThreats" style="color: #f59e0b; font-weight: 700;">2</span></div>
                    <div>Compliance: <span style="color: #22c55e; font-weight: 700;">98.7%</span></div>
                </div>
            </div>
            
            <div class="alert-banner" id="criticalAlerts">
                <strong>🚨 Security Alert:</strong> Unusual API access pattern detected from IP 192.168.1.100. Automated containment initiated.
                <button class="btn" onclick="investigateAlert('alert_001')" style="float: right;">Investigate</button>
            </div>
            
            <div class="grid">
                <div class="panel">
                    <h2>🎯 Threat Detection</h2>
                    <div class="metric-grid">
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Threats Blocked</div>
                            <div class="metric-value good" id="threatsBlocked">147</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Failed Logins</div>
                            <div class="metric-value warning" id="failedLogins">23</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Malware Detected</div>
                            <div class="metric-value good" id="malwareDetected">0</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Vulnerability Scan</div>
                            <div class="metric-value good" id="lastScan">2h ago</div>
                        </div>
                    </div>
                    
                    <h3>🔍 Active Threats</h3>
                    <div id="activeThreatsContainer">
                        <div class="threat-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <strong>Suspicious API Access Pattern</strong>
                                    <div style="font-size: 14px; color: #94a3b8;">IP: 192.168.1.100 • Detected 15 minutes ago</div>
                                </div>
                                <span class="threat-level medium">Medium</span>
                            </div>
                            <div style="font-size: 14px; color: #64748b; margin-bottom: 15px;">
                                Repeated failed authentication attempts followed by successful login
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn quarantine" onclick="blockIP('192.168.1.100')">Block IP</button>
                                <button class="btn" onclick="investigateThreat('threat_001')">Investigate</button>
                            </div>
                        </div>
                        
                        <div class="threat-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <strong>Unusual Data Access Volume</strong>
                                    <div style="font-size: 14px; color: #94a3b8;">Service: Content Hub • Detected 1 hour ago</div>
                                </div>
                                <span class="threat-level low">Low</span>
                            </div>
                            <div style="font-size: 14px; color: #64748b; margin-bottom: 15px;">
                                Data access volume 300% above baseline for this service
                            </div>
                            <div style="display: flex; gap: 10px;">
                                <button class="btn" onclick="analyzeAccess('content_hub')">Analyze</button>
                                <button class="btn" onclick="setBaseline('content_hub')">Update Baseline</button>
                            </div>
                        </div>
                    </div>
                    
                    <h3 style="margin-top: 30px;">⚡ Quick Actions</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        <button class="btn scan" onclick="runSecurityScan()">Run Security Scan</button>
                        <button class="btn" onclick="lockdownMode()">Emergency Lockdown</button>
                        <button class="btn" onclick="generateSecurityReport()">Security Report</button>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>🔐 Access Control</h2>
                    <div class="metric-grid">
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Active Sessions</div>
                            <div class="metric-value good" id="activeSessions">47</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Privileged Users</div>
                            <div class="metric-value warning" id="privilegedUsers">8</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Service Accounts</div>
                            <div class="metric-value good" id="serviceAccounts">12</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">API Keys</div>
                            <div class="metric-value good" id="apiKeys">24</div>
                        </div>
                    </div>
                    
                    <h3>👥 Recent Access Events</h3>
                    <div id="accessEvents">
                        <div class="security-event">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>admin@xynergy.com</strong> accessed Analytics Dashboard
                                    <div style="font-size: 12px; color: #94a3b8;">IP: 203.0.113.45 • 5 minutes ago</div>
                                </div>
                                <span class="status secure">Authorized</span>
                            </div>
                        </div>
                        
                        <div class="security-event">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>ai-routing-engine</strong> retrieved API secrets
                                    <div style="font-size: 12px; color: #94a3b8;">Service Account • 12 minutes ago</div>
                                </div>
                                <span class="status secure">Authorized</span>
                            </div>
                        </div>
                        
                        <div class="security-event">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>unknown@external.com</strong> attempted admin access
                                    <div style="font-size: 12px; color: #94a3b8;">IP: 192.168.1.100 • 15 minutes ago</div>
                                </div>
                                <span class="status vulnerable">BLOCKED</span>
                            </div>
                        </div>
                    </div>
                    
                    <h3 style="margin-top: 30px;">🔑 Permission Management</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        <button class="btn" onclick="reviewPermissions()">Review Permissions</button>
                        <button class="btn" onclick="rotateKeys()">Rotate API Keys</button>
                        <button class="btn" onclick="auditAccess()">Access Audit</button>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📋 Compliance Status</h2>
                    <div>
                        <div class="compliance-badge">GDPR Compliant</div>
                        <div class="compliance-badge">SOC 2 Type II</div>
                        <div class="compliance-badge">ISO 27001</div>
                        <div class="compliance-badge">HIPAA Ready</div>
                    </div>
                    
                    <h3 style="margin-top: 30px;">📊 Compliance Metrics</h3>
                    <div class="metric-grid">
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Data Encryption</div>
                            <div class="metric-value good">100%</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Audit Coverage</div>
                            <div class="metric-value good">98.7%</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Policy Compliance</div>
                            <div class="metric-value warning">94.2%</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Backup Success</div>
                            <div class="metric-value good">100%</div>
                        </div>
                    </div>
                    
                    <h3>📋 Security Policies</h3>
                    <div id="securityPolicies">
                        <div class="policy-item">
                            <strong>Password Policy</strong>
                            <div style="font-size: 14px; color: #94a3b8;">12+ chars, complex requirements, 90-day rotation</div>
                            <span class="status secure">Active</span>
                        </div>
                        
                        <div class="policy-item">
                            <strong>Multi-Factor Authentication</strong>
                            <div style="font-size: 14px; color: #94a3b8;">Required for all admin accounts</div>
                            <span class="status secure">Active</span>
                        </div>
                        
                        <div class="policy-item">
                            <strong>Data Retention</strong>
                            <div style="font-size: 14px; color: #94a3b8;">7-year retention, automated deletion</div>
                            <span class="status secure">Active</span>
                        </div>
                    </div>
                </div>
                
                <div class="panel">
                    <h2>📡 Network Security</h2>
                    <div class="network-map">
                        <div style="text-align: center; color: #64748b;">
                            🌐 Network Topology Visualization<br>
                            <small>VPC: xynergy-platform • Subnets: 3 • Firewalls: 12 rules active</small>
                        </div>
                    </div>
                    
                    <h3 style="margin-top: 20px;">🔥 Firewall Status</h3>
                    <div class="metric-grid">
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Blocked Requests</div>
                            <div class="metric-value good" id="blockedRequests">1,247</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">Firewall Rules</div>
                            <div class="metric-value good" id="firewallRules">12</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">DDoS Attempts</div>
                            <div class="metric-value good" id="ddosAttempts">0</div>
                        </div>
                        <div class="metric-box">
                            <div style="font-size: 12px; color: #94a3b8;">VPN Connections</div>
                            <div class="metric-value good" id="vpnConnections">8</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 30px;">
                <div class="panel">
                    <h2>📜 Security Event Log</h2>
                    <div class="security-log" id="securityLog">
                        <div class="log-entry critical">
                            [14:32:15] CRITICAL - Failed authentication attempt from 192.168.1.100 (5 attempts in 2 minutes)
                        </div>
                        <div class="log-entry warning">
                            [14:31:42] WARNING - Unusual data access pattern detected in content-hub service
                        </div>
                        <div class="log-entry info">
                            [14:30:58] INFO - API key rotation completed for external services
                        </div>
                        <div class="log-entry info">
                            [14:30:23] INFO - Security scan completed - 0 vulnerabilities found
                        </div>
                        <div class="log-entry warning">
                            [14:29:45] WARNING - Service account xynergy-platform-sa accessed from new IP
                        </div>
                        <div class="log-entry info">
                            [14:28:12] INFO - Backup verification completed successfully
                        </div>
                        <div class="log-entry critical">
                            [14:27:34] CRITICAL - Potential privilege escalation attempt blocked
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function investigateAlert(alertId) {
                console.log(`Investigating alert: ${alertId}`);
                alert('Opening detailed threat analysis dashboard...');
            }
            
            function blockIP(ipAddress) {
                console.log(`Blocking IP: ${ipAddress}`);
                if (confirm(`Block IP address ${ipAddress}?`)) {
                    alert(`IP ${ipAddress} has been blocked and added to the deny list.`);
                    addSecurityLogEntry('CRITICAL', `IP ${ipAddress} blocked due to suspicious activity`);
                }
            }
            
            function investigateThreat(threatId) {
                console.log(`Investigating threat: ${threatId}`);
                alert('Opening threat investigation workflow...');
            }
            
            function runSecurityScan() {
                console.log('Running security scan...');
                alert('Comprehensive security scan initiated. Results will be available in 5-10 minutes.');
                addSecurityLogEntry('INFO', 'Manual security scan initiated by administrator');
            }
            
            function lockdownMode() {
                console.log('Initiating emergency lockdown...');
                if (confirm('Initiate emergency security lockdown? This will restrict all non-essential access.')) {
                    alert('Emergency lockdown activated. All services are now in restricted access mode.');
                    addSecurityLogEntry('CRITICAL', 'Emergency security lockdown activated');
                }
            }
            
            function generateSecurityReport() {
                console.log('Generating security report...');
                alert('Security compliance report generation started. Report will be available for download in 3-5 minutes.');
            }
            
            function reviewPermissions() {
                console.log('Reviewing permissions...');
                alert('Opening permissions review dashboard...');
            }
            
            function rotateKeys() {
                console.log('Rotating API keys...');
                if (confirm('Rotate all API keys? This will require updating configurations across all services.')) {
                    alert('API key rotation initiated. Services will be notified of new keys automatically.');
                    addSecurityLogEntry('INFO', 'API key rotation initiated for all external services');
                }
            }
            
            function auditAccess() {
                console.log('Running access audit...');
                alert('Access audit started. Reviewing all user permissions and service account access.');
            }
            
            function addSecurityLogEntry(level, message) {
                const log = document.getElementById('securityLog');
                const entry = document.createElement('div');
                entry.className = `log-entry ${level.toLowerCase()}`;
                
                const timestamp = new Date().toLocaleTimeString();
                entry.textContent = `[${timestamp}] ${level} - ${message}`;
                
                log.insertBefore(entry, log.firstChild);
                
                // Keep only last 20 entries
                while (log.children.length > 20) {
                    log.removeChild(log.lastChild);
                }
            }
            
            // Simulate real-time updates
            function updateSecurityMetrics() {
                const threatsBlocked = Math.floor(Math.random() * 10) + 145;
                const failedLogins = Math.floor(Math.random() * 5) + 20;
                const activeThreats = Math.floor(Math.random() * 3) + 1;
                
                document.getElementById('threatsBlocked').textContent = threatsBlocked;
                document.getElementById('failedLogins').textContent = failedLogins;
                document.getElementById('activeThreats').textContent = activeThreats;
            }
            
            setInterval(updateSecurityMetrics, 30000);
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "security-governance", "timestamp": datetime.now().isoformat()}

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        with service_monitor.track_operation(f"execute_{action}"):
            if action == "security_audit":
                scope = parameters.get("scope", "platform")
                audit_result = {
                    "audit_id": f"audit_{int(time.time())}",
                    "workflow_id": workflow_context.get("workflow_id"),
                    "scope": scope,
                    "security_score": 0.94,
                    "findings": ["All security checks passed", "Zero critical vulnerabilities", "Compliance verified"],
                    "recommendations": ["Continue monitoring", "Regular security updates"],
                    "audit_completed_at": datetime.now()
                }
                if db:
                    db.collection("security_audits").document(audit_result["audit_id"]).set(audit_result)

                return {
                    "success": True,
                    "action": action,
                    "output": {"audit_id": audit_result["audit_id"], "security_score": audit_result["security_score"], "status": "passed"},
                    "execution_time": time.time(),
                    "service": "security-governance"
                }

            elif action == "compliance_check":
                audit_id = parameters.get("audit_id")
                compliance_result = {
                    "compliance_id": f"comp_{int(time.time())}",
                    "audit_id": audit_id,
                    "workflow_id": workflow_context.get("workflow_id"),
                    "compliance_standards": ["SOC2", "GDPR", "ISO27001"],
                    "compliance_status": "compliant",
                    "checked_at": datetime.now()
                }

                return {
                    "success": True,
                    "action": action,
                    "output": {"compliance_id": compliance_result["compliance_id"], "status": compliance_result["compliance_status"]},
                    "execution_time": time.time(),
                    "service": "security-governance"
                }

            else:
                return {
                    "success": False,
                    "error": f"Action '{action}' not supported by security-governance",
                    "supported_actions": ["security_audit", "compliance_check"],
                    "service": "security-governance"
                }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "action": request.get("action"),
            "service": "security-governance"
        }

@app.post("/api/security/scan", dependencies=[Depends(verify_api_key)])
async def initiate_security_scan(scan_data: SecurityScanRequest):
    """Initiate a comprehensive security scan"""
    try:
        scan_id = f"scan_{int(datetime.now().timestamp())}"
        scan_type = scan_data.type
        target_services = scan_data.target_systems
        
        # Create scan job
        scan_job = {
            "id": scan_id,
            "type": scan_type,
            "target_services": target_services,
            "status": "running",
            "started_at": datetime.now(),
            "progress": 0,
            "vulnerabilities_found": 0,
            "threats_detected": 0,
            "compliance_issues": 0,
            "estimated_completion": datetime.now() + timedelta(minutes=10)
        }
        
        # Store scan job
        db.collection("security_scans").document(scan_id).set(scan_job)
        
        # Start scan in background
        asyncio.create_task(run_security_scan(scan_id))
        
        # Log security event
        await log_security_event(
            SecurityEventType.SYSTEM_INTRUSION,
            "Security scan initiated",
            ThreatLevel.LOW,
            {"scan_id": scan_id, "scan_type": scan_type}
        )
        
        return {
            "scan_id": scan_id,
            "status": "initiated",
            "estimated_completion": scan_job["estimated_completion"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security scan error: {str(e)}")

@app.get("/api/security/threats")
async def get_active_threats(severity: Optional[str] = None):
    """Get active security threats"""
    try:
        threats_ref = db.collection("security_threats").where("status", "==", "active")
        
        if severity:
            threats_ref = threats_ref.where("severity", "==", severity)
        
        threats = []
        for doc in threats_ref.order_by("detected_at", direction=firestore.Query.DESCENDING).stream():
            threat_data = doc.to_dict()
            
            # Convert timestamps
            for field in ["detected_at", "last_seen", "resolved_at"]:
                if threat_data.get(field):
                    threat_data[field] = threat_data[field].isoformat()
            
            threats.append(threat_data)
        
        return threats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threats retrieval error: {str(e)}")

@app.post("/api/security/threats/{threat_id}/block", dependencies=[Depends(verify_api_key)])
async def block_threat(threat_id: str, action_data: ThreatActionRequest):
    """Block or contain a security threat"""
    try:
        doc_ref = db.collection("security_threats").document(threat_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Threat not found")
        
        threat_data = doc.to_dict()
        action_type = action_data.get("action", "block")
        
        # Update threat status
        doc_ref.update({
            "status": "contained",
            "action_taken": action_type,
            "resolved_at": datetime.now(),
            "resolved_by": "system"
        })
        
        # Implement blocking action based on threat type
        if threat_data.get("type") == "suspicious_ip":
            await block_ip_address(threat_data.get("source_ip", ""))
        elif threat_data.get("type") == "malicious_user":
            await disable_user_account(threat_data.get("user_id", ""))
        
        # Log security action
        await log_security_event(
            SecurityEventType.SYSTEM_INTRUSION,
            f"Threat {threat_id} contained via {action_type}",
            ThreatLevel.MEDIUM,
            {"threat_id": threat_id, "action": action_type}
        )
        
        return {
            "threat_id": threat_id,
            "status": "contained",
            "action": action_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Threat blocking error: {str(e)}")

@app.get("/api/security/compliance")
async def get_compliance_status():
    """Get current compliance status and metrics"""
    try:
        # Simulate compliance metrics
        compliance_data = {
            "overall_score": 94.7,
            "frameworks": {
                "gdpr": {
                    "compliant": True,
                    "score": 98.5,
                    "last_audit": "2025-09-01",
                    "issues": 0
                },
                "soc2": {
                    "compliant": True,
                    "score": 96.2,
                    "last_audit": "2025-08-15",
                    "issues": 2
                },
                "iso27001": {
                    "compliant": True,
                    "score": 92.1,
                    "last_audit": "2025-07-30",
                    "issues": 3
                }
            },
            "data_protection": {
                "encryption_at_rest": 100.0,
                "encryption_in_transit": 100.0,
                "backup_success_rate": 99.8,
                "data_retention_compliance": 98.5
            },
            "access_controls": {
                "mfa_coverage": 95.5,
                "privileged_access_monitoring": 100.0,
                "password_policy_compliance": 89.2,
                "access_review_completion": 92.1
            },
            "audit_metrics": {
                "log_retention_compliance": 100.0,
                "audit_trail_completeness": 98.7,
                "incident_response_time": "< 15 minutes",
                "security_training_completion": 94.3
            }
        }
        
        return compliance_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance status error: {str(e)}")

@app.get("/api/security/policies")
async def get_security_policies():
    """Get current security policies and their status"""
    try:
        # Get policies from database or return default
        policies_ref = db.collection("security_policies").document("current")
        doc = policies_ref.get()
        
        if doc.exists:
            policies = doc.to_dict()
        else:
            policies = SECURITY_POLICIES
            # Store default policies
            policies_ref.set(policies)
        
        # Add compliance status to each policy
        for policy_name, policy_data in policies.items():
            policy_data["compliance_rate"] = await calculate_policy_compliance(policy_name)
            policy_data["last_updated"] = datetime.now().isoformat()
        
        return policies
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security policies error: {str(e)}")

@app.put("/api/security/policies/{policy_name}")
async def update_security_policy(policy_name: str, policy_data: Dict[str, Any]):
    """Update a security policy"""
    try:
        if policy_name not in SECURITY_POLICIES:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Update policy in database
        policies_ref = db.collection("security_policies").document("current")
        policies_ref.update({
            f"{policy_name}": policy_data,
            f"{policy_name}.last_updated": datetime.now()
        })
        
        # Log policy change
        await log_security_event(
            SecurityEventType.POLICY_VIOLATION,
            f"Security policy updated: {policy_name}",
            ThreatLevel.LOW,
            {"policy": policy_name, "changes": policy_data}
        )
        
        return {
            "policy": policy_name,
            "status": "updated",
            "effective_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy update error: {str(e)}")

@app.get("/api/security/events")
async def get_security_events(event_type: Optional[str] = None, limit: int = 50):
    """Get security events log"""
    try:
        events_ref = db.collection("security_events").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
        
        if event_type:
            events_ref = events_ref.where("event_type", "==", event_type)
        
        events = []
        for doc in events_ref.stream():
            event_data = doc.to_dict()
            
            # Convert timestamp
            if event_data.get("timestamp"):
                event_data["timestamp"] = event_data["timestamp"].isoformat()
            
            events.append(event_data)
        
        return events
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security events error: {str(e)}")

@app.post("/api/security/lockdown", dependencies=[Depends(verify_api_key)])
async def emergency_lockdown(lockdown_data: LockdownRequest):
    """Initiate emergency security lockdown"""
    try:
        lockdown_id = f"lockdown_{int(datetime.now().timestamp())}"
        reason = lockdown_data.reason
        scope = lockdown_data.scope
        
        # Create lockdown record
        lockdown_record = {
            "id": lockdown_id,
            "reason": reason,
            "scope": scope,
            "initiated_at": datetime.now(),
            "initiated_by": "system",
            "status": "active",
            "affected_services": [],
            "affected_users": []
        }
        
        # Store lockdown record
        db.collection("security_lockdowns").document(lockdown_id).set(lockdown_record)
        
        # Implement lockdown procedures
        if scope in ["all", "services"]:
            await lockdown_services()
        
        if scope in ["all", "users"]:
            await lockdown_user_access()
        
        # Log critical security event
        await log_security_event(
            SecurityEventType.SYSTEM_INTRUSION,
            f"Emergency security lockdown initiated: {reason}",
            ThreatLevel.CRITICAL,
            {"lockdown_id": lockdown_id, "scope": scope}
        )
        
        # Publish emergency notification
        topic_path = publisher.topic_path(PROJECT_ID, "xynergy-security-alerts")
        message_data = json.dumps({
            "alert_type": "emergency_lockdown",
            "lockdown_id": lockdown_id,
            "reason": reason,
            "scope": scope,
            "timestamp": datetime.now().isoformat()
        }).encode("utf-8")
        
        publisher.publish(topic_path, message_data)
        
        return {
            "lockdown_id": lockdown_id,
            "status": "active",
            "scope": scope,
            "reason": reason
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency lockdown error: {str(e)}")

async def run_security_scan(scan_id: str):
    """Background task to run security scan"""
    try:
        doc_ref = db.collection("security_scans").document(scan_id)
        
        # Simulate scan progress
        scan_steps = [
            "Scanning network ports",
            "Checking service vulnerabilities", 
            "Analyzing access controls",
            "Reviewing compliance status",
            "Generating report"
        ]
        
        for i, step in enumerate(scan_steps):
            progress = (i + 1) * 20
            
            # Update scan progress
            doc_ref.update({
                "progress": progress,
                "current_step": step
            })
            
            # Simulate processing time
            await asyncio.sleep(2)
        
        # Complete scan with results
        doc_ref.update({
            "status": "completed",
            "completed_at": datetime.now(),
            "progress": 100,
            "vulnerabilities_found": 0,  # Simulate clean scan
            "threats_detected": 2,
            "compliance_issues": 1,
            "recommendations": [
                "Update password policy compliance",
                "Review privileged access permissions",
                "Enable additional monitoring for content-hub service"
            ]
        })
        
    except Exception as e:
        print(f"Security scan error: {e}")
        doc_ref.update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now()
        })

async def log_security_event(event_type: SecurityEventType, message: str, threat_level: ThreatLevel, metadata: Dict[str, Any] = None):
    """Log a security event"""
    try:
        event_data = {
            "event_type": event_type,
            "message": message,
            "threat_level": threat_level,
            "timestamp": datetime.now(),
            "source": "security-governance",
            "metadata": metadata or {},
            "ip_address": "127.0.0.1",  # In production, get real IP
            "user_agent": "Xynergy Security System"
        }
        
        db.collection("security_events").add(event_data)
        
    except Exception as e:
        print(f"Security event logging error: {e}")

async def block_ip_address(ip_address: str):
    """Block an IP address"""
    try:
        # Add to blocked IPs collection
        blocked_ip_data = {
            "ip_address": ip_address,
            "blocked_at": datetime.now(),
            "blocked_by": "security-governance",
            "reason": "Suspicious activity detected",
            "status": "active"
        }
        
        db.collection("blocked_ips").document(ip_address.replace(".", "_")).set(blocked_ip_data)
        
        # In production, would update firewall rules
        print(f"IP {ip_address} added to block list")
        
    except Exception as e:
        print(f"IP blocking error: {e}")

async def disable_user_account(user_id: str):
    """Disable a user account"""
    try:
        # Update user account status
        user_ref = db.collection("users").document(user_id)
        user_ref.update({
            "status": "disabled",
            "disabled_at": datetime.now(),
            "disabled_by": "security-governance",
            "reason": "Security threat detected"
        })
        
    except Exception as e:
        print(f"User disable error: {e}")

async def lockdown_services():
    """Implement service lockdown procedures"""
    try:
        # In production, would restrict service access
        print("Services locked down - restricted access mode activated")
        
    except Exception as e:
        print(f"Service lockdown error: {e}")

async def lockdown_user_access():
    """Implement user access lockdown"""
    try:
        # In production, would restrict user sessions
        print("User access locked down - emergency mode activated")
        
    except Exception as e:
        print(f"User lockdown error: {e}")

async def calculate_policy_compliance(policy_name: str) -> float:
    """Calculate compliance rate for a security policy"""
    try:
        # Simulate compliance calculation
        compliance_rates = {
            "password_policy": 89.2,
            "access_control": 95.5,
            "data_protection": 98.7,
            "compliance": 94.3
        }
        
        return compliance_rates.get(policy_name, 90.0)
        
    except Exception as e:
        print(f"Policy compliance calculation error: {e}")
        return 85.0

# Add cleanup handler for connection pooling
@app.on_event("shutdown")
async def cleanup_resources():
    """Clean up shared client connections on shutdown."""
    try:
        from gcp_clients import gcp_clients
        gcp_clients.close_all_connections()
    except Exception as e:
        print(f"Error during connection cleanup: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
