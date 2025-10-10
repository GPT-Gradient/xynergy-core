#!/usr/bin/env python3
"""
Validation Coordinator Service
Orchestrates comprehensive content validation workflows with fact-checking,
plagiarism detection, and trust & safety verification.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from google.cloud import pubsub_v1, firestore, bigquery
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Validation Coordinator", version="1.0.0")

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

PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")

publisher = pubsub_v1.PublisherClient()
db = firestore.Client(project=PROJECT_ID)
bq_client = bigquery.Client(project=PROJECT_ID)

try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_client.ping()
    logger.info("Connected to Redis cache")
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    redis_client = None

class ValidationPriority(str, Enum):
    CRITICAL = "critical"      # Real-time trending content - validate within 5 min
    HIGH = "high"             # Time-sensitive content - validate within 15 min
    MEDIUM = "medium"         # Standard content - validate within 30 min
    LOW = "low"              # Archived/reference content - validate within 2 hours

class ValidationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"

class ContentType(str, Enum):
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    NEWS = "news"
    RESEARCH = "research"
    MARKETING = "marketing"
    SOCIAL_MEDIA = "social_media"

@dataclass
class ValidationCheck:
    check_type: str
    status: ValidationStatus
    score: float
    details: Dict[str, Any]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ContentValidationRequest(BaseModel):
    content_id: str
    content_type: ContentType
    title: str
    body: str
    metadata: Dict[str, Any] = {}
    priority: ValidationPriority = ValidationPriority.MEDIUM
    required_checks: List[str] = ["fact_check", "plagiarism", "trust_safety"]
    deadline: Optional[datetime] = None
    source: str = "trending-engine"

class ValidationReport(BaseModel):
    validation_id: str
    content_id: str
    status: ValidationStatus
    overall_score: float
    checks: Dict[str, Dict[str, Any]]
    validation_start: datetime
    validation_end: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    passed_checks: List[str] = []
    failed_checks: List[str] = []
    recommendations: List[str] = []

class ValidationCoordinator:
    def __init__(self):
        self.active_validations: Dict[str, ValidationReport] = {}
        self.check_services = {
            "fact_check": "fact-check-requests",
            "plagiarism": "plagiarism-checks",
            "trust_safety": "trust-safety-checks"
        }

    async def create_validation_task(self, request: ContentValidationRequest) -> ValidationReport:
        """Create and initiate comprehensive validation task"""
        validation_id = f"val_{uuid.uuid4().hex[:12]}"

        # Create validation report
        report = ValidationReport(
            validation_id=validation_id,
            content_id=request.content_id,
            status=ValidationStatus.PENDING,
            overall_score=0.0,
            checks={},
            validation_start=datetime.now()
        )

        # Cache validation task
        self.active_validations[validation_id] = report

        # Store in Firestore
        doc_ref = db.collection("validations").document(validation_id)
        doc_ref.set({
            "validation_id": validation_id,
            "content_id": request.content_id,
            "content_type": request.content_type.value,
            "title": request.title,
            "priority": request.priority.value,
            "required_checks": request.required_checks,
            "status": report.status.value,
            "created_at": firestore.SERVER_TIMESTAMP,
            "deadline": request.deadline
        })

        # Publish to validation tasks topic
        task_data = {
            "validation_id": validation_id,
            "content_id": request.content_id,
            "content_type": request.content_type.value,
            "title": request.title,
            "body": request.body,
            "priority": request.priority.value,
            "required_checks": request.required_checks,
            "metadata": request.metadata,
            "timestamp": datetime.now().isoformat()
        }

        topic_path = publisher.topic_path(PROJECT_ID, "validation-tasks")
        message_data = json.dumps(task_data).encode("utf-8")
        future = publisher.publish(topic_path, message_data)
        logger.info(f"Published validation task {validation_id} to Pub/Sub")

        return report

    async def initiate_validation_checks(self, validation_id: str, request: ContentValidationRequest):
        """Initiate individual validation checks based on priority"""

        priority_timeouts = {
            ValidationPriority.CRITICAL: 300,   # 5 minutes
            ValidationPriority.HIGH: 900,      # 15 minutes
            ValidationPriority.MEDIUM: 1800,   # 30 minutes
            ValidationPriority.LOW: 7200       # 2 hours
        }

        timeout = priority_timeouts.get(request.priority, 1800)

        for check_type in request.required_checks:
            if check_type in self.check_services:
                await self._publish_check_request(
                    validation_id,
                    check_type,
                    request,
                    timeout
                )

    async def _publish_check_request(self, validation_id: str, check_type: str,
                                   request: ContentValidationRequest, timeout: int):
        """Publish individual validation check request"""

        topic_name = self.check_services[check_type]
        topic_path = publisher.topic_path(PROJECT_ID, topic_name)

        check_data = {
            "validation_id": validation_id,
            "check_type": check_type,
            "content_id": request.content_id,
            "content_type": request.content_type.value,
            "title": request.title,
            "body": request.body,
            "priority": request.priority.value,
            "timeout": timeout,
            "metadata": request.metadata,
            "timestamp": datetime.now().isoformat()
        }

        message_data = json.dumps(check_data).encode("utf-8")
        future = publisher.publish(topic_path, message_data)
        logger.info(f"Published {check_type} check for validation {validation_id}")

    async def process_check_result(self, validation_id: str, check_type: str,
                                 result: Dict[str, Any]):
        """Process individual validation check result"""

        if validation_id not in self.active_validations:
            logger.error(f"Unknown validation ID: {validation_id}")
            return

        report = self.active_validations[validation_id]
        report.checks[check_type] = result

        # Update validation status
        if result.get("status") == "completed":
            if result.get("score", 0) >= 0.7:  # 70% threshold
                report.passed_checks.append(check_type)
            else:
                report.failed_checks.append(check_type)

        # Check if all required checks are complete
        required_checks = len(report.checks)
        completed_checks = sum(1 for check in report.checks.values()
                             if check.get("status") == "completed")

        if completed_checks == required_checks:
            await self._finalize_validation(validation_id)

    async def _finalize_validation(self, validation_id: str):
        """Finalize validation report and publish results"""

        report = self.active_validations[validation_id]
        report.validation_end = datetime.now()

        if report.validation_start:
            processing_time = (report.validation_end - report.validation_start).total_seconds()
            report.processing_time_seconds = processing_time

        # Calculate overall score
        if report.checks:
            scores = [check.get("score", 0) for check in report.checks.values()]
            report.overall_score = sum(scores) / len(scores)

        # Determine final status
        if len(report.failed_checks) == 0:
            report.status = ValidationStatus.COMPLETED
        elif len(report.failed_checks) > len(report.passed_checks):
            report.status = ValidationStatus.REJECTED
        else:
            report.status = ValidationStatus.COMPLETED  # Partial pass

        # Generate recommendations
        if report.failed_checks:
            report.recommendations.extend([
                f"Improve {check} validation score" for check in report.failed_checks
            ])

        # Update Firestore
        doc_ref = db.collection("validations").document(validation_id)
        doc_ref.update({
            "status": report.status.value,
            "overall_score": report.overall_score,
            "checks": {k: v for k, v in report.checks.items()},
            "passed_checks": report.passed_checks,
            "failed_checks": report.failed_checks,
            "processing_time_seconds": report.processing_time_seconds,
            "completed_at": firestore.SERVER_TIMESTAMP
        })

        # Log to BigQuery
        await self._log_validation_metrics(report)

        # Publish completion event
        completion_data = {
            "validation_id": validation_id,
            "content_id": report.content_id,
            "status": report.status.value,
            "overall_score": report.overall_score,
            "processing_time_seconds": report.processing_time_seconds,
            "passed_checks": report.passed_checks,
            "failed_checks": report.failed_checks,
            "timestamp": datetime.now().isoformat()
        }

        topic_path = publisher.topic_path(PROJECT_ID, "validation-complete")
        message_data = json.dumps(completion_data).encode("utf-8")
        future = publisher.publish(topic_path, message_data)

        logger.info(f"Validation {validation_id} completed with status {report.status.value}")

    async def _log_validation_metrics(self, report: ValidationReport):
        """Log validation metrics to BigQuery"""
        try:
            table_id = f"{PROJECT_ID}.validation_analytics.content_validations"

            rows_to_insert = [{
                "validation_id": report.validation_id,
                "content_id": report.content_id,
                "validation_timestamp": report.validation_start.isoformat(),
                "accuracy_score": report.overall_score,
                "fact_check_results": report.checks.get("fact_check"),
                "plagiarism_score": report.checks.get("plagiarism", {}).get("score"),
                "trust_safety_score": report.checks.get("trust_safety", {}).get("score"),
                "validation_status": report.status.value,
                "failed_checks": report.failed_checks
            }]

            errors = bq_client.insert_rows_json(table_id, rows_to_insert)
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
            else:
                logger.info(f"Logged validation metrics for {report.validation_id}")

        except Exception as e:
            logger.error(f"Failed to log validation metrics: {e}")

    async def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics and performance metrics"""

        # Query recent validations from Firestore
        validations_ref = db.collection("validations")
        recent_validations = validations_ref.where(
            "created_at", ">=", datetime.now() - timedelta(days=1)
        ).limit(100).get()

        stats = {
            "total_validations_24h": len(recent_validations),
            "status_breakdown": {"pending": 0, "completed": 0, "failed": 0, "rejected": 0},
            "average_processing_time": 0,
            "average_accuracy_score": 0,
            "validation_success_rate": 0
        }

        processing_times = []
        accuracy_scores = []

        for doc in recent_validations:
            data = doc.to_dict()
            status = data.get("status", "pending")
            stats["status_breakdown"][status] += 1

            if data.get("processing_time_seconds"):
                processing_times.append(data["processing_time_seconds"])

            if data.get("overall_score"):
                accuracy_scores.append(data["overall_score"])

        if processing_times:
            stats["average_processing_time"] = sum(processing_times) / len(processing_times)

        if accuracy_scores:
            stats["average_accuracy_score"] = sum(accuracy_scores) / len(accuracy_scores)

        completed = stats["status_breakdown"]["completed"]
        total = stats["total_validations_24h"]
        if total > 0:
            stats["validation_success_rate"] = completed / total

        return stats

coordinator = ValidationCoordinator()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "validation-coordinator",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "firestore": "connected",
            "pubsub": "connected",
            "bigquery": "connected",
            "redis": "connected" if redis_client else "not_available"
        }
    }

@app.post("/execute")
async def execute_validation(request: ContentValidationRequest, background_tasks: BackgroundTasks):
    """Execute comprehensive content validation workflow"""
    try:
        # Create validation task
        report = await coordinator.create_validation_task(request)

        # Initiate validation checks in background
        background_tasks.add_task(
            coordinator.initiate_validation_checks,
            report.validation_id,
            request
        )

        return {
            "status": "success",
            "validation_id": report.validation_id,
            "message": "Content validation initiated",
            "estimated_completion": f"{15 if request.priority == ValidationPriority.HIGH else 30} minutes",
            "checks_requested": request.required_checks,
            "priority": request.priority.value
        }

    except Exception as e:
        logger.error(f"Failed to execute validation: {e}")
        raise HTTPException(status_code=500, detail=f"Validation execution failed: {str(e)}")

@app.get("/validation/{validation_id}")
async def get_validation_status(validation_id: str):
    """Get validation status and results"""
    try:
        # Try active validations first
        if validation_id in coordinator.active_validations:
            report = coordinator.active_validations[validation_id]
            return report.dict()

        # Query Firestore for completed validations
        doc_ref = db.collection("validations").document(validation_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail="Validation not found")

    except Exception as e:
        logger.error(f"Failed to get validation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_validation_statistics():
    """Get validation performance statistics"""
    try:
        stats = await coordinator.get_validation_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get validation stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Validation Coordinator Dashboard"""
    try:
        stats = await coordinator.get_validation_stats()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Validation Coordinator Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .stat-card h3 {{ margin: 0; font-size: 2rem; }}
                .stat-card p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                .section {{ margin-bottom: 30px; }}
                .status-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .status-item {{ padding: 15px; border-radius: 8px; text-align: center; }}
                .pending {{ background-color: #fff3cd; color: #856404; }}
                .completed {{ background-color: #d4edda; color: #155724; }}
                .failed {{ background-color: #f8d7da; color: #721c24; }}
                .rejected {{ background-color: #f1c6c7; color: #721c24; }}
                .refresh-btn {{ background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
                .refresh-btn:hover {{ background: #218838; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 Validation Coordinator Dashboard</h1>
                    <p>Comprehensive content validation orchestration</p>
                    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Stats</button>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>{stats.get('total_validations_24h', 0)}</h3>
                        <p>Validations (24h)</p>
                    </div>
                    <div class="stat-card">
                        <h3>{stats.get('average_processing_time', 0):.1f}s</h3>
                        <p>Avg Processing Time</p>
                    </div>
                    <div class="stat-card">
                        <h3>{stats.get('average_accuracy_score', 0):.2f}</h3>
                        <p>Avg Accuracy Score</p>
                    </div>
                    <div class="stat-card">
                        <h3>{stats.get('validation_success_rate', 0):.1%}</h3>
                        <p>Success Rate</p>
                    </div>
                </div>

                <div class="section">
                    <h2>📊 Validation Status Breakdown</h2>
                    <div class="status-list">
                        <div class="status-item pending">
                            <strong>{stats.get('status_breakdown', {}).get('pending', 0)}</strong><br>
                            Pending Validations
                        </div>
                        <div class="status-item completed">
                            <strong>{stats.get('status_breakdown', {}).get('completed', 0)}</strong><br>
                            Completed Validations
                        </div>
                        <div class="status-item failed">
                            <strong>{stats.get('status_breakdown', {}).get('failed', 0)}</strong><br>
                            Failed Validations
                        </div>
                        <div class="status-item rejected">
                            <strong>{stats.get('status_breakdown', {}).get('rejected', 0)}</strong><br>
                            Rejected Content
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>🔧 Validation Checks Available</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 10px;">
                            <h3>🔍 Fact Checking</h3>
                            <p>Verifies claims, statistics, and factual accuracy using multiple sources and AI-powered validation</p>
                        </div>
                        <div style="background: #f3e5f5; padding: 20px; border-radius: 10px;">
                            <h3>📄 Plagiarism Detection</h3>
                            <p>Scans for duplicate content, citation verification, and originality assessment</p>
                        </div>
                        <div style="background: #e8f5e8; padding: 20px; border-radius: 10px;">
                            <h3>🛡️ Trust & Safety</h3>
                            <p>Content safety verification, bias detection, and compliance validation</p>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>⚡ Priority Processing</h2>
                    <div style="background: #fff8e1; padding: 20px; border-radius: 10px;">
                        <p><strong>Critical (5 min):</strong> Real-time trending content</p>
                        <p><strong>High (15 min):</strong> Time-sensitive content</p>
                        <p><strong>Medium (30 min):</strong> Standard content validation</p>
                        <p><strong>Low (2 hours):</strong> Archived/reference content</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content

    except Exception as e:
        return f"<html><body><h1>Dashboard Error</h1><p>{str(e)}</p></body></html>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)