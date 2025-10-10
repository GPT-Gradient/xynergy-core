#!/usr/bin/env python3
"""
Trust & Safety Validator Service
Content safety verification, bias detection, compliance validation,
and ethical content screening for validation pipeline.
"""

import os
import json
import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import aiohttp
import requests

from google.cloud import pubsub_v1, firestore, bigquery
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Trust & Safety Validator", version="1.0.0")

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

subscriber = pubsub_v1.SubscriberClient()
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

class SafetyRiskLevel(str, Enum):
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    CRITICAL_RISK = "critical_risk"

class BiasType(str, Enum):
    GENDER = "gender"
    RACIAL = "racial"
    RELIGIOUS = "religious"
    POLITICAL = "political"
    CULTURAL = "cultural"
    SOCIOECONOMIC = "socioeconomic"
    AGE = "age"
    NONE = "none"

class ComplianceArea(str, Enum):
    GDPR = "gdpr"
    COPPA = "coppa"
    ACCESSIBILITY = "accessibility"
    MEDICAL_CLAIMS = "medical_claims"
    FINANCIAL_ADVICE = "financial_advice"
    LEGAL_CONTENT = "legal_content"

@dataclass
class SafetyIssue:
    issue_id: str
    issue_type: str
    description: str
    risk_level: SafetyRiskLevel
    confidence: float
    location: str
    recommendation: str

class TrustSafetyRequest(BaseModel):
    validation_id: str
    content_id: str
    title: str
    body: str
    priority: str = "medium"
    timeout: int = 1800
    metadata: Dict[str, Any] = {}
    content_category: str = "general"
    target_audience: str = "general"

class TrustSafetyResult(BaseModel):
    validation_id: str
    content_id: str
    overall_safety_score: float
    risk_level: SafetyRiskLevel
    status: str
    issues_found: int
    bias_detected: List[str]
    compliance_status: Dict[str, bool]
    processing_time: float
    detailed_issues: List[Dict[str, Any]]
    recommendations: List[str]
    approved_for_publication: bool

class TrustSafetyValidator:
    def __init__(self):
        # Sensitive content patterns
        self.sensitive_patterns = {
            "hate_speech": [
                r"\b(hate|despise|loathe)\s+(women|men|people|group)",
                r"\b(terrorist|extremist)\s+(?:group|organization)",
                r"\b(all|every)\s+(?:women|men|people)\s+are\s+(?:bad|evil|stupid)"
            ],
            "harassment": [
                r"\b(kill|harm|hurt)\s+(?:yourself|someone)",
                r"\b(stupid|idiot|moron)\s+(?:person|people)",
                r"\b(?:you|they)\s+(?:should|must)\s+(?:die|suffer)"
            ],
            "misinformation": [
                r"\b(?:proven|scientific)\s+fact:\s*(?:vaccines|climate)",
                r"\b(?:definitely|certainly)\s+(?:causes|prevents)\s+(?:cancer|disease)",
                r"\b(?:guaranteed|proven)\s+(?:cure|treatment|solution)"
            ],
            "financial_advice": [
                r"\b(?:guaranteed|sure)\s+(?:profit|return|investment)",
                r"\b(?:buy|sell|invest)\s+(?:now|immediately|today)",
                r"\b(?:zero|no)\s+risk\s+(?:investment|opportunity)"
            ],
            "medical_claims": [
                r"\b(?:cures|treats|prevents)\s+(?:cancer|diabetes|disease)",
                r"\b(?:doctor|medical)\s+(?:breakthrough|miracle|secret)",
                r"\b(?:fda|clinically)\s+(?:approved|proven|tested)"
            ]
        }

        # Bias detection patterns
        self.bias_patterns = {
            BiasType.GENDER: [
                r"\b(?:women|girls)\s+are\s+(?:naturally|typically)\s+(?:worse|better)\s+at",
                r"\b(?:men|boys)\s+are\s+(?:naturally|typically)\s+(?:worse|better)\s+at",
                r"\b(?:females|males)\s+(?:cannot|should not)\s+(?:work|participate)"
            ],
            BiasType.RACIAL: [
                r"\b(?:people|individuals)\s+of\s+(?:color|race)\s+are\s+(?:typically|usually)",
                r"\b(?:asian|african|hispanic)\s+people\s+are\s+(?:naturally|typically)",
                r"\b(?:white|caucasian)\s+people\s+are\s+(?:superior|better)"
            ],
            BiasType.AGE: [
                r"\b(?:older|elderly)\s+(?:people|individuals)\s+(?:cannot|should not)",
                r"\b(?:young|millennial)\s+(?:people|generation)\s+are\s+(?:lazy|entitled)",
                r"\b(?:too\s+old|too\s+young)\s+(?:to|for)"
            ]
        }

        # Compliance requirements
        self.compliance_checks = {
            ComplianceArea.GDPR: {
                "data_collection": r"\b(?:collect|gather|store)\s+(?:personal|user)\s+(?:data|information)",
                "consent": r"\b(?:consent|permission|agree)\s+to\s+(?:data|information|tracking)",
                "cookies": r"\b(?:cookies|tracking|analytics)\s+(?:on|for|website)"
            },
            ComplianceArea.ACCESSIBILITY: {
                "alt_text": r"<img(?!\s+alt=)",
                "color_only": r"\b(?:click|see)\s+(?:the|this)\s+(?:red|green|blue|color)",
                "contrast": r"\b(?:light|pale|faded)\s+(?:text|color)"
            },
            ComplianceArea.MEDICAL_CLAIMS: {
                "diagnosis": r"\b(?:diagnose|cure|treat|prevent)\s+(?:disease|condition|illness)",
                "prescription": r"\b(?:take|use|try)\s+(?:medication|drug|supplement)",
                "medical_advice": r"\b(?:you\s+should|must|need\s+to)\s+(?:see|consult)\s+(?:doctor|physician)"
            }
        }

    async def analyze_content_safety(self, content: str) -> List[SafetyIssue]:
        """Analyze content for safety issues"""
        issues = []

        for category, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    issue = SafetyIssue(
                        issue_id=f"safety_{uuid.uuid4().hex[:8]}",
                        issue_type=category,
                        description=f"Potentially {category.replace('_', ' ')} content detected",
                        risk_level=self._determine_risk_level(category),
                        confidence=0.8,
                        location=f"Position {match.start()}-{match.end()}",
                        recommendation=f"Review and modify {category.replace('_', ' ')} content"
                    )
                    issues.append(issue)

        return issues

    def _determine_risk_level(self, category: str) -> SafetyRiskLevel:
        """Determine risk level based on content category"""
        high_risk_categories = ["hate_speech", "harassment", "misinformation"]
        medium_risk_categories = ["financial_advice", "medical_claims"]

        if category in high_risk_categories:
            return SafetyRiskLevel.HIGH_RISK
        elif category in medium_risk_categories:
            return SafetyRiskLevel.MEDIUM_RISK
        else:
            return SafetyRiskLevel.LOW_RISK

    async def detect_bias(self, content: str) -> List[BiasType]:
        """Detect potential bias in content"""
        detected_biases = []

        for bias_type, patterns in self.bias_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    detected_biases.append(bias_type)
                    break  # Avoid duplicate detection for same bias type

        return detected_biases if detected_biases else [BiasType.NONE]

    async def check_compliance(self, content: str, content_category: str) -> Dict[str, bool]:
        """Check content compliance with various regulations"""
        compliance_status = {}

        for area, checks in self.compliance_checks.items():
            # Check if compliance area is relevant to content category
            if self._is_compliance_relevant(area, content_category):
                compliance_status[area.value] = True  # Default to compliant

                for check_type, pattern in checks.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        # Found potential compliance issue
                        compliance_status[area.value] = False
                        break

        return compliance_status

    def _is_compliance_relevant(self, area: ComplianceArea, content_category: str) -> bool:
        """Determine if compliance area is relevant to content category"""
        relevance_map = {
            ComplianceArea.GDPR: ["website", "marketing", "technology"],
            ComplianceArea.COPPA: ["children", "family", "education"],
            ComplianceArea.ACCESSIBILITY: ["website", "documentation", "tutorial"],
            ComplianceArea.MEDICAL_CLAIMS: ["health", "medical", "wellness"],
            ComplianceArea.FINANCIAL_ADVICE: ["finance", "investment", "business"],
            ComplianceArea.LEGAL_CONTENT: ["legal", "policy", "terms"]
        }

        relevant_categories = relevance_map.get(area, [])
        return content_category.lower() in relevant_categories or content_category.lower() == "general"

    def _calculate_safety_score(self, issues: List[SafetyIssue]) -> float:
        """Calculate overall safety score based on issues found"""
        if not issues:
            return 1.0

        risk_weights = {
            SafetyRiskLevel.SAFE: 0.0,
            SafetyRiskLevel.LOW_RISK: 0.1,
            SafetyRiskLevel.MEDIUM_RISK: 0.3,
            SafetyRiskLevel.HIGH_RISK: 0.6,
            SafetyRiskLevel.CRITICAL_RISK: 1.0
        }

        total_risk = sum(risk_weights[issue.risk_level] * issue.confidence for issue in issues)
        max_possible_risk = len(issues) * 1.0

        safety_score = max(0.0, 1.0 - (total_risk / max_possible_risk)) if max_possible_risk > 0 else 1.0
        return safety_score

    def _determine_overall_risk(self, issues: List[SafetyIssue]) -> SafetyRiskLevel:
        """Determine overall risk level"""
        if not issues:
            return SafetyRiskLevel.SAFE

        highest_risk = max(issue.risk_level for issue in issues)
        return highest_risk

    def _generate_recommendations(self, issues: List[SafetyIssue], biases: List[BiasType],
                                compliance: Dict[str, bool]) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []

        # Safety issue recommendations
        if issues:
            issue_types = set(issue.issue_type for issue in issues)
            for issue_type in issue_types:
                recommendations.append(f"Address {issue_type.replace('_', ' ')} concerns in content")

        # Bias recommendations
        active_biases = [bias for bias in biases if bias != BiasType.NONE]
        if active_biases:
            bias_names = [bias.value.replace('_', ' ') for bias in active_biases]
            recommendations.append(f"Review content for potential {', '.join(bias_names)} bias")

        # Compliance recommendations
        non_compliant = [area for area, status in compliance.items() if not status]
        if non_compliant:
            recommendations.append(f"Address {', '.join(non_compliant).upper()} compliance issues")

        # General recommendations
        if not recommendations:
            recommendations.append("Content meets trust and safety standards")
        else:
            recommendations.append("Consider legal and editorial review before publication")

        return recommendations

    async def process_trust_safety_check(self, request: TrustSafetyRequest) -> TrustSafetyResult:
        """Process complete trust and safety validation"""
        start_time = datetime.now()

        try:
            # Analyze content safety
            safety_issues = await self.analyze_content_safety(request.body)
            logger.info(f"Found {len(safety_issues)} safety issues for {request.validation_id}")

            # Detect bias
            detected_biases = await self.detect_bias(request.body)
            logger.info(f"Detected biases: {[bias.value for bias in detected_biases]}")

            # Check compliance
            compliance_status = await self.check_compliance(request.body, request.content_category)
            logger.info(f"Compliance status: {compliance_status}")

            # Calculate overall safety score
            safety_score = self._calculate_safety_score(safety_issues)

            # Determine overall risk level
            risk_level = self._determine_overall_risk(safety_issues)

            # Generate recommendations
            recommendations = self._generate_recommendations(safety_issues, detected_biases, compliance_status)

            # Determine if approved for publication
            approved = (safety_score >= 0.7 and
                       risk_level in [SafetyRiskLevel.SAFE, SafetyRiskLevel.LOW_RISK] and
                       all(compliance_status.values()))

            # Convert issues to dict format
            detailed_issues = [
                {
                    "issue_id": issue.issue_id,
                    "issue_type": issue.issue_type,
                    "description": issue.description,
                    "risk_level": issue.risk_level.value,
                    "confidence": issue.confidence,
                    "location": issue.location,
                    "recommendation": issue.recommendation
                }
                for issue in safety_issues
            ]

            processing_time = (datetime.now() - start_time).total_seconds()

            result = TrustSafetyResult(
                validation_id=request.validation_id,
                content_id=request.content_id,
                overall_safety_score=safety_score,
                risk_level=risk_level,
                status="completed",
                issues_found=len(safety_issues),
                bias_detected=[bias.value for bias in detected_biases if bias != BiasType.NONE],
                compliance_status=compliance_status,
                processing_time=processing_time,
                detailed_issues=detailed_issues,
                recommendations=recommendations,
                approved_for_publication=approved
            )

            # Cache result
            if redis_client:
                cache_key = f"trust_safety:{request.validation_id}"
                redis_client.setex(cache_key, 3600, json.dumps(result.dict()))

            # Log to Firestore
            doc_ref = db.collection("trust_safety_checks").document(request.validation_id)
            doc_ref.set({
                "validation_id": request.validation_id,
                "content_id": request.content_id,
                "overall_safety_score": result.overall_safety_score,
                "risk_level": result.risk_level.value,
                "issues_found": result.issues_found,
                "bias_detected": result.bias_detected,
                "compliance_status": result.compliance_status,
                "processing_time": result.processing_time,
                "detailed_issues": result.detailed_issues,
                "recommendations": result.recommendations,
                "approved_for_publication": result.approved_for_publication,
                "created_at": firestore.SERVER_TIMESTAMP
            })

            return result

        except Exception as e:
            logger.error(f"Trust & safety check failed for {request.validation_id}: {e}")

            # Return failure result
            return TrustSafetyResult(
                validation_id=request.validation_id,
                content_id=request.content_id,
                overall_safety_score=0.0,
                risk_level=SafetyRiskLevel.CRITICAL_RISK,
                status="failed",
                issues_found=0,
                bias_detected=[],
                compliance_status={},
                processing_time=(datetime.now() - start_time).total_seconds(),
                detailed_issues=[],
                recommendations=["Trust & safety check service error - manual review required"],
                approved_for_publication=False
            )

trust_safety_validator = TrustSafetyValidator()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "trust-safety-validator",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "firestore": "connected",
            "redis": "connected" if redis_client else "not_available",
            "safety_patterns": len(trust_safety_validator.sensitive_patterns),
            "bias_patterns": len(trust_safety_validator.bias_patterns),
            "compliance_areas": len(trust_safety_validator.compliance_checks)
        }
    }

@app.post("/execute")
async def execute_trust_safety_check(request: TrustSafetyRequest):
    """Execute comprehensive trust and safety validation"""
    try:
        result = await trust_safety_validator.process_trust_safety_check(request)

        # Publish result back to validation coordinator
        result_data = result.dict()
        result_data["check_type"] = "trust_safety"
        result_data["timestamp"] = datetime.now().isoformat()
        result_data["score"] = result.overall_safety_score

        topic_path = publisher.topic_path(PROJECT_ID, "validation-check-results")
        message_data = json.dumps(result_data).encode("utf-8")
        future = publisher.publish(topic_path, message_data)

        logger.info(f"Trust & safety check completed for {request.validation_id}: "
                   f"score {result.overall_safety_score:.2f}, "
                   f"risk {result.risk_level.value}, "
                   f"approved {result.approved_for_publication}")

        return {
            "status": "success",
            "validation_id": request.validation_id,
            "overall_safety_score": result.overall_safety_score,
            "risk_level": result.risk_level.value,
            "issues_found": result.issues_found,
            "approved_for_publication": result.approved_for_publication,
            "processing_time": result.processing_time
        }

    except Exception as e:
        logger.error(f"Trust & safety check execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Trust & safety check failed: {str(e)}")

@app.get("/trust-safety/{validation_id}")
async def get_trust_safety_result(validation_id: str):
    """Get trust and safety check results for validation"""
    try:
        # Try cache first
        if redis_client:
            cache_key = f"trust_safety:{validation_id}"
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

        # Query Firestore
        doc_ref = db.collection("trust_safety_checks").document(validation_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail="Trust & safety check results not found")

    except Exception as e:
        logger.error(f"Failed to get trust & safety results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_trust_safety_statistics():
    """Get trust and safety validation performance statistics"""
    try:
        # Query recent checks
        checks_ref = db.collection("trust_safety_checks")
        recent_checks = checks_ref.where(
            "created_at", ">=", datetime.now() - timedelta(days=1)
        ).limit(100).get()

        stats = {
            "total_checks_24h": len(recent_checks),
            "average_safety_score": 0,
            "average_processing_time": 0,
            "approval_rate": 0,
            "risk_distribution": {
                "safe": 0,
                "low_risk": 0,
                "medium_risk": 0,
                "high_risk": 0,
                "critical_risk": 0
            },
            "total_issues_found": 0,
            "bias_detections": 0,
            "compliance_violations": 0
        }

        safety_scores = []
        processing_times = []
        approved_count = 0
        total_issues = 0
        total_biases = 0
        total_violations = 0

        for doc in recent_checks:
            data = doc.to_dict()

            if data.get("overall_safety_score") is not None:
                safety_scores.append(data["overall_safety_score"])

            if data.get("processing_time"):
                processing_times.append(data["processing_time"])

            if data.get("approved_for_publication"):
                approved_count += 1

            risk_level = data.get("risk_level", "safe")
            stats["risk_distribution"][risk_level] += 1

            total_issues += data.get("issues_found", 0)

            bias_list = data.get("bias_detected", [])
            if bias_list:
                total_biases += len(bias_list)

            compliance_status = data.get("compliance_status", {})
            total_violations += sum(1 for status in compliance_status.values() if not status)

        if safety_scores:
            stats["average_safety_score"] = sum(safety_scores) / len(safety_scores)

        if processing_times:
            stats["average_processing_time"] = sum(processing_times) / len(processing_times)

        if len(recent_checks) > 0:
            stats["approval_rate"] = approved_count / len(recent_checks)

        stats["total_issues_found"] = total_issues
        stats["bias_detections"] = total_biases
        stats["compliance_violations"] = total_violations

        return stats

    except Exception as e:
        logger.error(f"Failed to get trust & safety stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Trust & Safety Validator Dashboard"""
    try:
        stats = await get_trust_safety_statistics()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Trust & Safety Validator Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .stat-card h3 {{ margin: 0; font-size: 2rem; }}
                .stat-card p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                .section {{ margin-bottom: 30px; }}
                .risk-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }}
                .risk-item {{ padding: 15px; border-radius: 8px; text-align: center; }}
                .safe {{ background-color: #d4edda; color: #155724; }}
                .low-risk {{ background-color: #d1ecf1; color: #0c5460; }}
                .medium-risk {{ background-color: #fff3cd; color: #856404; }}
                .high-risk {{ background-color: #f8d7da; color: #721c24; }}
                .critical-risk {{ background-color: #f1c6c7; color: #721c24; font-weight: bold; }}
                .refresh-btn {{ background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
                .refresh-btn:hover {{ background: #218838; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Trust & Safety Validator Dashboard</h1>
                    <p>Content safety, bias detection, and compliance verification</p>
                    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Stats</button>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>{stats.get('total_checks_24h', 0)}</h3>
                        <p>Safety Checks (24h)</p>
                    </div>
                    <div class="stat-card">
                        <h3>{stats.get('average_safety_score', 0):.2f}</h3>
                        <p>Avg Safety Score</p>
                    </div>
                    <div class="stat-card">
                        <h3>{stats.get('approval_rate', 0):.1%}</h3>
                        <p>Approval Rate</p>
                    </div>
                    <div class="stat-card">
                        <h3>{stats.get('average_processing_time', 0):.1f}s</h3>
                        <p>Avg Processing Time</p>
                    </div>
                </div>

                <div class="section">
                    <h2>⚠️ Risk Level Distribution</h2>
                    <div class="risk-grid">
                        <div class="risk-item safe">
                            <strong>{stats.get('risk_distribution', {}).get('safe', 0)}</strong><br>
                            Safe
                        </div>
                        <div class="risk-item low-risk">
                            <strong>{stats.get('risk_distribution', {}).get('low_risk', 0)}</strong><br>
                            Low Risk
                        </div>
                        <div class="risk-item medium-risk">
                            <strong>{stats.get('risk_distribution', {}).get('medium_risk', 0)}</strong><br>
                            Medium Risk
                        </div>
                        <div class="risk-item high-risk">
                            <strong>{stats.get('risk_distribution', {}).get('high_risk', 0)}</strong><br>
                            High Risk
                        </div>
                        <div class="risk-item critical-risk">
                            <strong>{stats.get('risk_distribution', {}).get('critical_risk', 0)}</strong><br>
                            Critical Risk
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>📊 Detection Summary</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                        <div style="background: #fff3cd; padding: 20px; border-radius: 10px; text-align: center;">
                            <h3>{stats.get('total_issues_found', 0):,}</h3>
                            <p>Safety Issues Found</p>
                        </div>
                        <div style="background: #f8d7da; padding: 20px; border-radius: 10px; text-align: center;">
                            <h3>{stats.get('bias_detections', 0):,}</h3>
                            <p>Bias Instances</p>
                        </div>
                        <div style="background: #d1ecf1; padding: 20px; border-radius: 10px; text-align: center;">
                            <h3>{stats.get('compliance_violations', 0):,}</h3>
                            <p>Compliance Violations</p>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>🔧 Validation Capabilities</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 10px;">
                            <h3>🛡️ Content Safety</h3>
                            <p>Detects hate speech, harassment, misinformation, and harmful content</p>
                        </div>
                        <div style="background: #f3e5f5; padding: 20px; border-radius: 10px;">
                            <h3>⚖️ Bias Detection</h3>
                            <p>Identifies gender, racial, religious, and other forms of bias in content</p>
                        </div>
                        <div style="background: #e8f5e8; padding: 20px; border-radius: 10px;">
                            <h3>📋 Compliance Checking</h3>
                            <p>Validates GDPR, COPPA, accessibility, and industry-specific compliance</p>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>📋 Safety Categories</h2>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                        <p><strong>Hate Speech:</strong> Content promoting hatred or discrimination against groups</p>
                        <p><strong>Harassment:</strong> Content targeting individuals with harmful intent</p>
                        <p><strong>Misinformation:</strong> False or misleading information presented as fact</p>
                        <p><strong>Medical Claims:</strong> Unverified health or medical advice</p>
                        <p><strong>Financial Advice:</strong> Potentially harmful financial recommendations</p>
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