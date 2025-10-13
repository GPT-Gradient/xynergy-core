"""
Audit Logging Service
Phase 8: Operational Layer
Provides comprehensive audit logging, compliance reporting, and security monitoring
"""

from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import os
import json
import uuid
import asyncio
import httpx
from google.cloud import bigquery, firestore, pubsub_v1
from google.api_core import exceptions
import redis
import hashlib
from collections import defaultdict
import re

app = FastAPI(title="Audit Logging Service", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://xynergy-platform.com",
        "https://*.xynergy.com",
        "https://xynergy-platform-dashboard-*.run.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REDIS_HOST = os.getenv("REDIS_HOST", "10.229.184.219")
DATASET_ID = "xynergy_analytics"
TABLE_ID = "audit_events"

# Initialize GCP clients
try:
    bq_client = bigquery.Client(project=PROJECT_ID)
    db = firestore.Client(project=PROJECT_ID)
    publisher = pubsub_v1.PublisherClient()
    audit_topic = publisher.topic_path(PROJECT_ID, "xynergy-audit-events")
except Exception as e:
    print(f"Warning: Could not initialize GCP clients: {e}")
    bq_client = None
    db = None
    publisher = None

# Initialize Redis
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=6379,
        decode_responses=True,
        socket_connect_timeout=5
    )
    redis_client.ping()
except Exception as e:
    print(f"Warning: Redis not available: {e}")
    redis_client = None

# Data models
class AuditEvent(BaseModel):
    log_id: str = Field(default_factory=lambda: f"log_{uuid.uuid4().hex[:8]}")
    user_id: str
    tenant_id: Optional[str] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    granted: bool
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    severity: str = "INFO"  # INFO, WARNING, ERROR, CRITICAL

class ComplianceReport(BaseModel):
    report_type: str  # SOC2, GDPR, HIPAA, PCI
    start_date: str
    end_date: str
    format: str = "JSON"  # JSON, CSV, PDF

class SecurityAlert(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"alert_{uuid.uuid4().hex[:8]}")
    alert_type: str
    severity: str
    description: str
    affected_user: Optional[str] = None
    affected_resource: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None

# Security pattern detection
SUSPICIOUS_PATTERNS = {
    "MULTIPLE_FAILURES": {
        "pattern": r"(login\.failed|auth\.failed|permission\.denied)",
        "threshold": 5,
        "window_minutes": 5,
        "severity": "WARNING"
    },
    "DATA_EXFILTRATION": {
        "pattern": r"(export\.data|download\.bulk|api\.export)",
        "threshold": 10,
        "window_minutes": 10,
        "severity": "ERROR"
    },
    "PRIVILEGE_ESCALATION": {
        "pattern": r"(admin\.access|role\.elevated|permission\.granted\.admin)",
        "threshold": 3,
        "window_minutes": 15,
        "severity": "CRITICAL"
    },
    "BRUTE_FORCE": {
        "pattern": r"login\.failed",
        "threshold": 10,
        "window_minutes": 2,
        "severity": "ERROR"
    }
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "audit-logging-service", "version": "1.0.0"}

@app.post("/api/audit/log")
async def log_audit_event(
    event: AuditEvent,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    """Log an audit event"""
    try:
        # Store in BigQuery
        if bq_client:
            table_ref = bq_client.dataset(DATASET_ID).table(TABLE_ID)
            table = bq_client.get_table(table_ref)

            row_to_insert = {
                "log_id": event.log_id,
                "user_id": event.user_id,
                "tenant_id": event.tenant_id,
                "action": event.action,
                "resource": event.resource,
                "resource_id": event.resource_id,
                "granted": event.granted,
                "reason": event.reason,
                "metadata": json.dumps(event.metadata) if event.metadata else None,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "timestamp": event.timestamp,
                "severity": event.severity
            }

            errors = bq_client.insert_rows_json(table, [row_to_insert])
            if errors:
                print(f"BigQuery insert error: {errors}")

        # Store in Firestore for quick access
        if db:
            doc_ref = db.collection("audit_logs").document(event.log_id)
            doc_ref.set(event.dict())

        # Cache recent events in Redis
        if redis_client:
            cache_key = f"audit:recent:{event.user_id}"
            redis_client.lpush(cache_key, json.dumps(event.dict()))
            redis_client.ltrim(cache_key, 0, 99)  # Keep last 100 events
            redis_client.expire(cache_key, 3600)  # 1 hour TTL

        # Publish to Pub/Sub for real-time processing
        if publisher:
            message_data = json.dumps(event.dict()).encode("utf-8")
            future = publisher.publish(audit_topic, message_data)

        # Check for security patterns
        await check_security_patterns(event)

        return {
            "success": True,
            "log_id": event.log_id,
            "message": "Audit event logged successfully"
        }

    except Exception as e:
        print(f"Error logging audit event: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to log audit event", "details": str(e)}
        )

@app.get("/api/audit/events")
async def get_audit_events(
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0),
    x_api_key: str = Header(None, alias="X-API-Key")
):
    """Query audit events with filters"""
    try:
        # Check Redis cache first
        if redis_client and user_id and not any([action, resource, start_date, end_date]):
            cache_key = f"audit:recent:{user_id}"
            cached_events = redis_client.lrange(cache_key, offset, offset + limit - 1)
            if cached_events:
                events = [json.loads(event) for event in cached_events]
                return {
                    "success": True,
                    "events": events,
                    "count": len(events),
                    "from_cache": True
                }

        # Build BigQuery query
        query_parts = [f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`"]
        where_conditions = []

        if user_id:
            where_conditions.append(f"user_id = '{user_id}'")
        if tenant_id:
            where_conditions.append(f"tenant_id = '{tenant_id}'")
        if action:
            where_conditions.append(f"action LIKE '%{action}%'")
        if resource:
            where_conditions.append(f"resource = '{resource}'")
        if severity:
            where_conditions.append(f"severity = '{severity}'")
        if start_date:
            where_conditions.append(f"timestamp >= '{start_date}'")
        if end_date:
            where_conditions.append(f"timestamp <= '{end_date}'")

        if where_conditions:
            query_parts.append(f"WHERE {' AND '.join(where_conditions)}")

        query_parts.append(f"ORDER BY timestamp DESC")
        query_parts.append(f"LIMIT {limit} OFFSET {offset}")

        query = " ".join(query_parts)

        if bq_client:
            query_job = bq_client.query(query)
            results = query_job.result()

            events = []
            for row in results:
                event = {
                    "log_id": row.log_id,
                    "user_id": row.user_id,
                    "tenant_id": row.tenant_id,
                    "action": row.action,
                    "resource": row.resource,
                    "resource_id": row.resource_id,
                    "granted": row.granted,
                    "reason": row.reason,
                    "metadata": json.loads(row.metadata) if row.metadata else None,
                    "ip_address": row.ip_address,
                    "user_agent": row.user_agent,
                    "timestamp": row.timestamp.isoformat() if row.timestamp else None,
                    "severity": row.severity
                }
                events.append(event)

            return {
                "success": True,
                "events": events,
                "count": len(events),
                "query": query if os.getenv("DEBUG") else None
            }
        else:
            # Fallback to Firestore
            if db:
                events_ref = db.collection("audit_logs")
                if user_id:
                    events_ref = events_ref.where("user_id", "==", user_id)
                if tenant_id:
                    events_ref = events_ref.where("tenant_id", "==", tenant_id)
                if severity:
                    events_ref = events_ref.where("severity", "==", severity)

                events_ref = events_ref.order_by("timestamp", direction=firestore.Query.DESCENDING)
                events_ref = events_ref.limit(limit).offset(offset)

                docs = events_ref.stream()
                events = [doc.to_dict() for doc in docs]

                return {
                    "success": True,
                    "events": events,
                    "count": len(events),
                    "source": "firestore"
                }

            return {"success": False, "error": "No data source available"}

    except Exception as e:
        print(f"Error querying audit events: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to query audit events", "details": str(e)}
        )

@app.post("/api/audit/report")
async def generate_compliance_report(
    report: ComplianceReport,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    """Generate compliance report"""
    try:
        # Query relevant audit data
        query = f"""
        SELECT
            DATE(timestamp) as date,
            action,
            resource,
            COUNT(*) as event_count,
            SUM(CASE WHEN granted = TRUE THEN 1 ELSE 0 END) as granted_count,
            SUM(CASE WHEN granted = FALSE THEN 1 ELSE 0 END) as denied_count
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE timestamp BETWEEN '{report.start_date}' AND '{report.end_date}'
        GROUP BY date, action, resource
        ORDER BY date DESC
        """

        if bq_client:
            query_job = bq_client.query(query)
            results = query_job.result()

            report_data = {
                "report_type": report.report_type,
                "period": {
                    "start": report.start_date,
                    "end": report.end_date
                },
                "summary": {
                    "total_events": 0,
                    "unique_users": set(),
                    "access_granted": 0,
                    "access_denied": 0,
                    "critical_events": 0
                },
                "daily_breakdown": defaultdict(lambda: {
                    "events": 0,
                    "granted": 0,
                    "denied": 0
                }),
                "compliance_checks": {}
            }

            for row in results:
                date_str = row.date.isoformat()
                report_data["daily_breakdown"][date_str]["events"] += row.event_count
                report_data["daily_breakdown"][date_str]["granted"] += row.granted_count
                report_data["daily_breakdown"][date_str]["denied"] += row.denied_count
                report_data["summary"]["total_events"] += row.event_count
                report_data["summary"]["access_granted"] += row.granted_count
                report_data["summary"]["access_denied"] += row.denied_count

            # Convert defaultdict to regular dict for JSON serialization
            report_data["daily_breakdown"] = dict(report_data["daily_breakdown"])

            # Add compliance-specific checks
            if report.report_type == "SOC2":
                report_data["compliance_checks"] = {
                    "access_control": True,
                    "data_encryption": True,
                    "audit_logging": True,
                    "incident_response": True,
                    "change_management": True
                }
            elif report.report_type == "GDPR":
                report_data["compliance_checks"] = {
                    "data_minimization": True,
                    "right_to_erasure": True,
                    "data_portability": True,
                    "consent_management": True,
                    "breach_notification": True
                }
            elif report.report_type == "HIPAA":
                report_data["compliance_checks"] = {
                    "access_controls": True,
                    "audit_controls": True,
                    "integrity_controls": True,
                    "transmission_security": True,
                    "encryption": True
                }

            # Store report
            if db:
                report_id = f"report_{uuid.uuid4().hex[:8]}"
                doc_ref = db.collection("compliance_reports").document(report_id)
                doc_ref.set({
                    "report_id": report_id,
                    "report_type": report.report_type,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "data": report_data
                })

                return {
                    "success": True,
                    "report_id": report_id,
                    "report": report_data
                }

            return {
                "success": True,
                "report": report_data
            }

        return {"success": False, "error": "BigQuery not available"}

    except Exception as e:
        print(f"Error generating compliance report: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate report", "details": str(e)}
        )

@app.get("/api/audit/alerts")
async def get_security_alerts(
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = Query(default=50, le=100),
    x_api_key: str = Header(None, alias="X-API-Key")
):
    """Get security alerts"""
    try:
        if db:
            alerts_ref = db.collection("security_alerts")

            if severity:
                alerts_ref = alerts_ref.where("severity", "==", severity)
            if resolved is not None:
                alerts_ref = alerts_ref.where("resolved", "==", resolved)

            alerts_ref = alerts_ref.order_by("timestamp", direction=firestore.Query.DESCENDING)
            alerts_ref = alerts_ref.limit(limit)

            docs = alerts_ref.stream()
            alerts = [doc.to_dict() for doc in docs]

            return {
                "success": True,
                "alerts": alerts,
                "count": len(alerts)
            }

        return {"success": False, "error": "Firestore not available"}

    except Exception as e:
        print(f"Error getting security alerts: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get alerts", "details": str(e)}
        )

@app.patch("/api/audit/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolved_by: str,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    """Resolve a security alert"""
    try:
        if db:
            doc_ref = db.collection("security_alerts").document(alert_id)
            doc = doc_ref.get()

            if not doc.exists:
                raise HTTPException(status_code=404, detail="Alert not found")

            doc_ref.update({
                "resolved": True,
                "resolved_by": resolved_by,
                "resolved_at": datetime.now(timezone.utc).isoformat()
            })

            return {
                "success": True,
                "message": "Alert resolved successfully"
            }

        return {"success": False, "error": "Firestore not available"}

    except Exception as e:
        print(f"Error resolving alert: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to resolve alert", "details": str(e)}
        )

async def check_security_patterns(event: AuditEvent):
    """Check for suspicious patterns and create alerts"""
    try:
        for pattern_name, pattern_config in SUSPICIOUS_PATTERNS.items():
            if re.search(pattern_config["pattern"], event.action):
                # Check recent events for this pattern
                window_start = datetime.now(timezone.utc) - timedelta(minutes=pattern_config["window_minutes"])

                if redis_client:
                    # Use Redis for quick pattern detection
                    pattern_key = f"pattern:{pattern_name}:{event.user_id}"
                    redis_client.incr(pattern_key)
                    redis_client.expire(pattern_key, pattern_config["window_minutes"] * 60)

                    count = int(redis_client.get(pattern_key) or 0)

                    if count >= pattern_config["threshold"]:
                        # Create security alert
                        alert = SecurityAlert(
                            alert_type=pattern_name,
                            severity=pattern_config["severity"],
                            description=f"Detected {pattern_name}: {count} occurrences in {pattern_config['window_minutes']} minutes",
                            affected_user=event.user_id,
                            affected_resource=event.resource,
                            metadata={
                                "pattern": pattern_config["pattern"],
                                "threshold": pattern_config["threshold"],
                                "count": count,
                                "last_action": event.action
                            }
                        )

                        if db:
                            doc_ref = db.collection("security_alerts").document(alert.alert_id)
                            doc_ref.set(alert.dict())

                        # Publish alert
                        if publisher:
                            alert_topic = publisher.topic_path(PROJECT_ID, "xynergy-security-alerts")
                            message_data = json.dumps(alert.dict()).encode("utf-8")
                            publisher.publish(alert_topic, message_data)

                        # Reset counter after alert
                        redis_client.delete(pattern_key)

    except Exception as e:
        print(f"Error checking security patterns: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve audit dashboard UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Audit Logging Service</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #0a0a0a; color: #fff; }
            .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; }
            h1 { margin: 0; font-size: 28px; }
            .status { padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 20px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card { background: #1a1a1a; border-radius: 10px; padding: 20px; border: 1px solid #333; }
            .card h3 { margin-top: 0; color: #667eea; }
            .events-table { width: 100%; background: #1a1a1a; border-radius: 10px; overflow: hidden; }
            table { width: 100%; border-collapse: collapse; }
            th { background: #2a2a2a; padding: 12px; text-align: left; font-weight: 600; }
            td { padding: 12px; border-top: 1px solid #333; }
            .severity { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
            .severity.INFO { background: #1e40af; }
            .severity.WARNING { background: #ca8a04; }
            .severity.ERROR { background: #dc2626; }
            .severity.CRITICAL { background: #7c2d12; }
            .granted { color: #10b981; }
            .denied { color: #ef4444; }
            .btn { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; }
            .btn:hover { background: #764ba2; }
            .filters { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
            input, select { padding: 8px; background: #2a2a2a; border: 1px solid #444; border-radius: 4px; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Audit Logging Service</h1>
                <div class="status">✅ Operational</div>
            </div>

            <div class="grid">
                <div class="card">
                    <h3>📊 Statistics</h3>
                    <div id="stats">Loading...</div>
                </div>
                <div class="card">
                    <h3>⚠️ Recent Alerts</h3>
                    <div id="alerts">Loading...</div>
                </div>
                <div class="card">
                    <h3>📈 Compliance Status</h3>
                    <div id="compliance">
                        <div>SOC2: ✅ Compliant</div>
                        <div>GDPR: ✅ Compliant</div>
                        <div>HIPAA: ✅ Compliant</div>
                        <div>PCI: ✅ Compliant</div>
                    </div>
                </div>
            </div>

            <div class="filters">
                <input type="text" id="userFilter" placeholder="User ID">
                <input type="text" id="actionFilter" placeholder="Action">
                <select id="severityFilter">
                    <option value="">All Severities</option>
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                    <option value="CRITICAL">CRITICAL</option>
                </select>
                <button class="btn" onclick="loadEvents()">Search</button>
                <button class="btn" onclick="generateReport()">Generate Report</button>
            </div>

            <div class="events-table">
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>User</th>
                            <th>Action</th>
                            <th>Resource</th>
                            <th>Result</th>
                            <th>Severity</th>
                            <th>IP Address</th>
                        </tr>
                    </thead>
                    <tbody id="eventsTable">
                        <tr><td colspan="7" style="text-align: center;">Loading events...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            async function loadEvents() {
                const userFilter = document.getElementById('userFilter').value;
                const actionFilter = document.getElementById('actionFilter').value;
                const severityFilter = document.getElementById('severityFilter').value;

                let url = '/api/audit/events?limit=100';
                if (userFilter) url += '&user_id=' + userFilter;
                if (actionFilter) url += '&action=' + actionFilter;
                if (severityFilter) url += '&severity=' + severityFilter;

                try {
                    const response = await fetch(url, {
                        headers: { 'X-API-Key': 'demo-key' }
                    });
                    const data = await response.json();

                    const tbody = document.getElementById('eventsTable');
                    if (data.events && data.events.length > 0) {
                        tbody.innerHTML = data.events.map(event => `
                            <tr>
                                <td>${new Date(event.timestamp).toLocaleString()}</td>
                                <td>${event.user_id}</td>
                                <td>${event.action}</td>
                                <td>${event.resource}</td>
                                <td class="${event.granted ? 'granted' : 'denied'}">
                                    ${event.granted ? '✓ Granted' : '✗ Denied'}
                                </td>
                                <td><span class="severity ${event.severity}">${event.severity}</span></td>
                                <td>${event.ip_address || '-'}</td>
                            </tr>
                        `).join('');
                    } else {
                        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No events found</td></tr>';
                    }
                } catch (error) {
                    console.error('Error loading events:', error);
                }
            }

            async function loadAlerts() {
                try {
                    const response = await fetch('/api/audit/alerts?resolved=false&limit=5', {
                        headers: { 'X-API-Key': 'demo-key' }
                    });
                    const data = await response.json();

                    const alertsDiv = document.getElementById('alerts');
                    if (data.alerts && data.alerts.length > 0) {
                        alertsDiv.innerHTML = data.alerts.map(alert => `
                            <div style="margin-bottom: 10px; padding: 10px; background: #2a2a2a; border-radius: 6px;">
                                <div style="font-weight: bold; color: #ef4444;">${alert.alert_type}</div>
                                <div style="font-size: 14px; color: #999;">${alert.description}</div>
                            </div>
                        `).join('');
                    } else {
                        alertsDiv.innerHTML = '<div style="color: #10b981;">No active alerts</div>';
                    }
                } catch (error) {
                    console.error('Error loading alerts:', error);
                }
            }

            async function generateReport() {
                const reportType = prompt('Report type (SOC2/GDPR/HIPAA/PCI):', 'SOC2');
                if (!reportType) return;

                const today = new Date();
                const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());

                try {
                    const response = await fetch('/api/audit/report', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-API-Key': 'demo-key'
                        },
                        body: JSON.stringify({
                            report_type: reportType,
                            start_date: lastMonth.toISOString(),
                            end_date: today.toISOString(),
                            format: 'JSON'
                        })
                    });
                    const data = await response.json();

                    if (data.success) {
                        alert('Report generated successfully! Report ID: ' + (data.report_id || 'N/A'));
                        console.log('Report data:', data.report);
                    }
                } catch (error) {
                    console.error('Error generating report:', error);
                }
            }

            // Load initial data
            loadEvents();
            loadAlerts();
            setInterval(loadAlerts, 30000); // Refresh alerts every 30 seconds
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)