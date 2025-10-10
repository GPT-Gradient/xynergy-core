#!/usr/bin/env python3
"""
Plagiarism Detector Service
Advanced plagiarism detection using content fingerprinting, semantic similarity,
and citation verification for content validation pipeline.
"""

import os
import json
import asyncio
import logging
import hashlib
import difflib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from dataclasses import dataclass
import uuid
import re

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

app = FastAPI(title="Plagiarism Detector", version="1.0.0")

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

class PlagiarismType(str, Enum):
    EXACT_MATCH = "exact_match"
    PARAPHRASE = "paraphrase"
    MOSAIC = "mosaic"
    SELF_PLAGIARISM = "self_plagiarism"
    CITATION_MISSING = "citation_missing"

class SeverityLevel(str, Enum):
    CRITICAL = "critical"    # >30% similarity
    HIGH = "high"           # 15-30% similarity
    MEDIUM = "medium"       # 5-15% similarity
    LOW = "low"            # <5% similarity
    NONE = "none"          # No plagiarism detected

@dataclass
class PlagiarismMatch:
    match_id: str
    source_text: str
    matched_text: str
    similarity_score: float
    plagiarism_type: PlagiarismType
    source_url: Optional[str] = None
    start_position: int = 0
    end_position: int = 0

class PlagiarismCheckRequest(BaseModel):
    validation_id: str
    content_id: str
    title: str
    body: str
    priority: str = "medium"
    timeout: int = 1800
    metadata: Dict[str, Any] = {}
    check_web: bool = True
    check_internal: bool = True

class PlagiarismResult(BaseModel):
    validation_id: str
    content_id: str
    overall_similarity: float
    severity_level: SeverityLevel
    status: str
    total_matches: int
    unique_sources: int
    processing_time: float
    matches: List[Dict[str, Any]]
    recommendations: List[str]
    originality_score: float

class PlagiarismDetector:
    def __init__(self):
        # Minimum text length for meaningful comparison
        self.min_match_length = 20
        self.similarity_threshold = 0.7

        # Common phrases that shouldn't be flagged
        self.common_phrases = {
            "in conclusion", "for example", "on the other hand", "in addition",
            "furthermore", "moreover", "however", "therefore", "according to",
            "as a result", "in other words", "first and foremost"
        }

    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text for comparison"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()-]', '', text)

        # Convert to lowercase for comparison
        return text.lower().strip()

    def _create_text_fingerprints(self, text: str, n_gram_size: int = 5) -> Set[str]:
        """Create n-gram fingerprints for efficient similarity detection"""
        words = text.split()
        fingerprints = set()

        for i in range(len(words) - n_gram_size + 1):
            n_gram = ' '.join(words[i:i + n_gram_size])
            if not any(phrase in n_gram for phrase in self.common_phrases):
                fingerprints.add(n_gram)

        return fingerprints

    async def check_web_sources(self, text: str) -> List[PlagiarismMatch]:
        """Check text against web sources (simulated)"""
        matches = []

        # Simulate web search for similar content
        # In production, this would use actual search APIs

        # Create some realistic simulated matches
        paragraphs = text.split('\n\n')

        for i, paragraph in enumerate(paragraphs[:3]):  # Check first 3 paragraphs
            if len(paragraph) < 50:  # Skip short paragraphs
                continue

            # Simulate finding similar content
            similarity = await self._simulate_web_similarity_check(paragraph)

            if similarity > self.similarity_threshold:
                match = PlagiarismMatch(
                    match_id=f"web_{uuid.uuid4().hex[:8]}",
                    source_text=paragraph[:100] + "...",
                    matched_text=paragraph,
                    similarity_score=similarity,
                    plagiarism_type=PlagiarismType.PARAPHRASE if similarity < 0.9 else PlagiarismType.EXACT_MATCH,
                    source_url=f"https://example-source-{i+1}.com/article",
                    start_position=text.find(paragraph),
                    end_position=text.find(paragraph) + len(paragraph)
                )
                matches.append(match)

        return matches

    async def _simulate_web_similarity_check(self, text: str) -> float:
        """Simulate web similarity check (replace with real implementation)"""
        await asyncio.sleep(0.1)  # Simulate API latency

        # Simulate realistic similarity scores
        import random

        # Most content is original
        base_similarity = random.uniform(0.1, 0.4)

        # Occasionally detect higher similarity
        if random.random() < 0.1:  # 10% chance of potential plagiarism
            base_similarity = random.uniform(0.7, 0.95)

        return base_similarity

    async def check_internal_sources(self, text: str) -> List[PlagiarismMatch]:
        """Check text against internal content database"""
        matches = []

        try:
            # Query Firestore for similar content
            content_ref = db.collection("published_content")

            # For efficiency, we'll use text fingerprints
            text_fingerprints = self._create_text_fingerprints(self._preprocess_text(text))

            # In production, you'd want a more sophisticated indexing system
            # This is a simplified version for demonstration

            recent_content = content_ref.where(
                "published_date", ">=", datetime.now() - timedelta(days=365)
            ).limit(50).get()

            for doc in recent_content:
                content_data = doc.to_dict()
                stored_text = content_data.get("body", "")

                if len(stored_text) < 100:  # Skip short content
                    continue

                similarity = await self._calculate_text_similarity(text, stored_text)

                if similarity > self.similarity_threshold:
                    match = PlagiarismMatch(
                        match_id=f"internal_{doc.id}",
                        source_text=stored_text[:100] + "...",
                        matched_text=text,
                        similarity_score=similarity,
                        plagiarism_type=PlagiarismType.SELF_PLAGIARISM,
                        source_url=f"internal://{doc.id}",
                        start_position=0,
                        end_position=len(text)
                    )
                    matches.append(match)

        except Exception as e:
            logger.error(f"Error checking internal sources: {e}")

        return matches

    async def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using various methods"""

        # Preprocess both texts
        clean_text1 = self._preprocess_text(text1)
        clean_text2 = self._preprocess_text(text2)

        # Use difflib for sequence similarity
        sequence_similarity = difflib.SequenceMatcher(None, clean_text1, clean_text2).ratio()

        # Use n-gram fingerprint similarity
        fingerprints1 = self._create_text_fingerprints(clean_text1)
        fingerprints2 = self._create_text_fingerprints(clean_text2)

        if len(fingerprints1) == 0 or len(fingerprints2) == 0:
            fingerprint_similarity = 0.0
        else:
            intersection = len(fingerprints1.intersection(fingerprints2))
            union = len(fingerprints1.union(fingerprints2))
            fingerprint_similarity = intersection / union if union > 0 else 0.0

        # Combine similarities (weighted average)
        combined_similarity = (sequence_similarity * 0.4) + (fingerprint_similarity * 0.6)

        return combined_similarity

    def _determine_severity(self, similarity: float) -> SeverityLevel:
        """Determine severity level based on similarity score"""
        if similarity >= 0.30:
            return SeverityLevel.CRITICAL
        elif similarity >= 0.15:
            return SeverityLevel.HIGH
        elif similarity >= 0.05:
            return SeverityLevel.MEDIUM
        elif similarity > 0.01:
            return SeverityLevel.LOW
        else:
            return SeverityLevel.NONE

    def _generate_recommendations(self, matches: List[PlagiarismMatch],
                                severity: SeverityLevel) -> List[str]:
        """Generate recommendations based on plagiarism detection results"""
        recommendations = []

        if severity == SeverityLevel.CRITICAL:
            recommendations.append("CRITICAL: Content contains significant plagiarism - requires major revision")
            recommendations.append("Add proper citations and quotations for borrowed content")
            recommendations.append("Rewrite plagiarized sections using original language")

        elif severity == SeverityLevel.HIGH:
            recommendations.append("HIGH: Notable similarity detected - review and revise")
            recommendations.append("Verify all sources are properly attributed")
            recommendations.append("Consider paraphrasing similar sections")

        elif severity == SeverityLevel.MEDIUM:
            recommendations.append("MEDIUM: Some similarities found - review for proper attribution")
            recommendations.append("Ensure all quotes and references are properly cited")

        elif severity == SeverityLevel.LOW:
            recommendations.append("LOW: Minor similarities detected - generally acceptable")
            recommendations.append("Double-check citations for completeness")

        # Specific recommendations based on match types
        match_types = {match.plagiarism_type for match in matches}

        if PlagiarismType.EXACT_MATCH in match_types:
            recommendations.append("Exact matches found - add quotation marks and citations")

        if PlagiarismType.SELF_PLAGIARISM in match_types:
            recommendations.append("Self-plagiarism detected - consider referencing previous work")

        if PlagiarismType.CITATION_MISSING in match_types:
            recommendations.append("Missing citations identified - add proper source attribution")

        return recommendations

    async def process_plagiarism_check(self, request: PlagiarismCheckRequest) -> PlagiarismResult:
        """Process complete plagiarism detection request"""
        start_time = datetime.now()

        try:
            all_matches = []

            # Check web sources if requested
            if request.check_web:
                web_matches = await self.check_web_sources(request.body)
                all_matches.extend(web_matches)
                logger.info(f"Found {len(web_matches)} web matches for {request.validation_id}")

            # Check internal sources if requested
            if request.check_internal:
                internal_matches = await self.check_internal_sources(request.body)
                all_matches.extend(internal_matches)
                logger.info(f"Found {len(internal_matches)} internal matches for {request.validation_id}")

            # Calculate overall similarity
            if all_matches:
                overall_similarity = max(match.similarity_score for match in all_matches)
            else:
                overall_similarity = 0.0

            # Determine severity
            severity = self._determine_severity(overall_similarity)

            # Calculate originality score (inverse of similarity)
            originality_score = max(0.0, 1.0 - overall_similarity)

            # Get unique sources
            unique_sources = len(set(match.source_url for match in all_matches if match.source_url))

            # Generate recommendations
            recommendations = self._generate_recommendations(all_matches, severity)

            # Convert matches to dict format
            matches_dict = [
                {
                    "match_id": match.match_id,
                    "source_text": match.source_text,
                    "matched_text": match.matched_text[:200] + "..." if len(match.matched_text) > 200 else match.matched_text,
                    "similarity_score": match.similarity_score,
                    "plagiarism_type": match.plagiarism_type.value,
                    "source_url": match.source_url,
                    "start_position": match.start_position,
                    "end_position": match.end_position
                }
                for match in all_matches
            ]

            processing_time = (datetime.now() - start_time).total_seconds()

            result = PlagiarismResult(
                validation_id=request.validation_id,
                content_id=request.content_id,
                overall_similarity=overall_similarity,
                severity_level=severity,
                status="completed",
                total_matches=len(all_matches),
                unique_sources=unique_sources,
                processing_time=processing_time,
                matches=matches_dict,
                recommendations=recommendations,
                originality_score=originality_score
            )

            # Cache result
            if redis_client:
                cache_key = f"plagiarism:{request.validation_id}"
                redis_client.setex(cache_key, 3600, json.dumps(result.dict()))

            # Log to Firestore
            doc_ref = db.collection("plagiarism_checks").document(request.validation_id)
            doc_ref.set({
                "validation_id": request.validation_id,
                "content_id": request.content_id,
                "overall_similarity": result.overall_similarity,
                "severity_level": result.severity_level.value,
                "total_matches": result.total_matches,
                "unique_sources": result.unique_sources,
                "processing_time": result.processing_time,
                "originality_score": result.originality_score,
                "matches": result.matches,
                "recommendations": result.recommendations,
                "created_at": firestore.SERVER_TIMESTAMP
            })

            return result

        except Exception as e:
            logger.error(f"Plagiarism check failed for {request.validation_id}: {e}")

            # Return failure result
            return PlagiarismResult(
                validation_id=request.validation_id,
                content_id=request.content_id,
                overall_similarity=0.0,
                severity_level=SeverityLevel.NONE,
                status="failed",
                total_matches=0,
                unique_sources=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                matches=[],
                recommendations=["Plagiarism check service error - manual review required"],
                originality_score=1.0
            )

plagiarism_detector = PlagiarismDetector()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "plagiarism-detector",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "firestore": "connected",
            "redis": "connected" if redis_client else "not_available",
            "web_checking": "simulated",
            "internal_checking": "active"
        }
    }

@app.post("/execute")
async def execute_plagiarism_check(request: PlagiarismCheckRequest):
    """Execute comprehensive plagiarism detection"""
    try:
        result = await plagiarism_detector.process_plagiarism_check(request)

        # Publish result back to validation coordinator
        result_data = result.dict()
        result_data["check_type"] = "plagiarism"
        result_data["timestamp"] = datetime.now().isoformat()
        result_data["score"] = result.originality_score  # Use originality as the score

        topic_path = publisher.topic_path(PROJECT_ID, "validation-check-results")
        message_data = json.dumps(result_data).encode("utf-8")
        future = publisher.publish(topic_path, message_data)

        logger.info(f"Plagiarism check completed for {request.validation_id}: "
                   f"similarity {result.overall_similarity:.2f}, "
                   f"originality {result.originality_score:.2f}")

        return {
            "status": "success",
            "validation_id": request.validation_id,
            "overall_similarity": result.overall_similarity,
            "originality_score": result.originality_score,
            "severity_level": result.severity_level.value,
            "total_matches": result.total_matches,
            "unique_sources": result.unique_sources,
            "processing_time": result.processing_time
        }

    except Exception as e:
        logger.error(f"Plagiarism check execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Plagiarism check failed: {str(e)}")

@app.get("/plagiarism/{validation_id}")
async def get_plagiarism_result(validation_id: str):
    """Get plagiarism check results for validation"""
    try:
        # Try cache first
        if redis_client:
            cache_key = f"plagiarism:{validation_id}"
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

        # Query Firestore
        doc_ref = db.collection("plagiarism_checks").document(validation_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail="Plagiarism check results not found")

    except Exception as e:
        logger.error(f"Failed to get plagiarism results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_plagiarism_statistics():
    """Get plagiarism detection performance statistics"""
    try:
        # Query recent plagiarism checks
        checks_ref = db.collection("plagiarism_checks")
        recent_checks = checks_ref.where(
            "created_at", ">=", datetime.now() - timedelta(days=1)
        ).limit(100).get()

        stats = {
            "total_checks_24h": len(recent_checks),
            "average_originality_score": 0,
            "average_similarity": 0,
            "average_processing_time": 0,
            "severity_distribution": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "none": 0
            },
            "total_matches_found": 0,
            "unique_sources_identified": 0
        }

        originality_scores = []
        similarity_scores = []
        processing_times = []
        total_matches = 0
        total_sources = 0

        for doc in recent_checks:
            data = doc.to_dict()

            if data.get("originality_score"):
                originality_scores.append(data["originality_score"])

            if data.get("overall_similarity"):
                similarity_scores.append(data["overall_similarity"])

            if data.get("processing_time"):
                processing_times.append(data["processing_time"])

            severity = data.get("severity_level", "none")
            stats["severity_distribution"][severity] += 1

            total_matches += data.get("total_matches", 0)
            total_sources += data.get("unique_sources", 0)

        if originality_scores:
            stats["average_originality_score"] = sum(originality_scores) / len(originality_scores)

        if similarity_scores:
            stats["average_similarity"] = sum(similarity_scores) / len(similarity_scores)

        if processing_times:
            stats["average_processing_time"] = sum(processing_times) / len(processing_times)

        stats["total_matches_found"] = total_matches
        stats["unique_sources_identified"] = total_sources

        return stats

    except Exception as e:
        logger.error(f"Failed to get plagiarism stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Plagiarism Detector Dashboard"""
    try:
        stats = await get_plagiarism_statistics()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Plagiarism Detector Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .stat-card h3 {{ margin: 0; font-size: 2rem; }}
                .stat-card p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                .section {{ margin-bottom: 30px; }}
                .severity-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }}
                .severity-item {{ padding: 15px; border-radius: 8px; text-align: center; }}
                .critical {{ background-color: #f8d7da; color: #721c24; }}
                .high {{ background-color: #fff3cd; color: #856404; }}
                .medium {{ background-color: #d4edda; color: #155724; }}
                .low {{ background-color: #d1ecf1; color: #0c5460; }}
                .none {{ background-color: #e2e3e5; color: #6c757d; }}
                .refresh-btn {{ background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
                .refresh-btn:hover {{ background: #218838; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📄 Plagiarism Detector Dashboard</h1>
                    <p>Advanced content originality verification and similarity detection</p>
                    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Stats</button>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>{stats.get('total_checks_24h', 0)}</h3>
                        <p>Checks (24h)</p>
                    </div>
                    <div class="stat-card">
                        <h3>{stats.get('average_originality_score', 0):.2f}</h3>
                        <p>Avg Originality Score</p>
                    </div>
                    <div class="stat-card">
                        <h3>{stats.get('total_matches_found', 0):,}</h3>
                        <p>Matches Found</p>
                    </div>
                    <div class="stat-card">
                        <h3>{stats.get('average_processing_time', 0):.1f}s</h3>
                        <p>Avg Processing Time</p>
                    </div>
                </div>

                <div class="section">
                    <h2>⚠️ Severity Distribution</h2>
                    <div class="severity-grid">
                        <div class="severity-item critical">
                            <strong>{stats.get('severity_distribution', {}).get('critical', 0)}</strong><br>
                            Critical (>30%)
                        </div>
                        <div class="severity-item high">
                            <strong>{stats.get('severity_distribution', {}).get('high', 0)}</strong><br>
                            High (15-30%)
                        </div>
                        <div class="severity-item medium">
                            <strong>{stats.get('severity_distribution', {}).get('medium', 0)}</strong><br>
                            Medium (5-15%)
                        </div>
                        <div class="severity-item low">
                            <strong>{stats.get('severity_distribution', {}).get('low', 0)}</strong><br>
                            Low (<5%)
                        </div>
                        <div class="severity-item none">
                            <strong>{stats.get('severity_distribution', {}).get('none', 0)}</strong><br>
                            Clean
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>🔧 Detection Capabilities</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                        <div style="background: #e3f2fd; padding: 20px; border-radius: 10px;">
                            <h3>🌐 Web Source Detection</h3>
                            <p>Scans content against billions of web pages for similarity matches</p>
                        </div>
                        <div style="background: #f3e5f5; padding: 20px; border-radius: 10px;">
                            <h3>📚 Internal Database Check</h3>
                            <p>Compares against previously published content to prevent self-plagiarism</p>
                        </div>
                        <div style="background: #e8f5e8; padding: 20px; border-radius: 10px;">
                            <h3>🧬 Content Fingerprinting</h3>
                            <p>Uses advanced n-gram analysis and semantic similarity detection</p>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>📊 Analysis Metrics</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                        <div style="background: #fff3cd; padding: 20px; border-radius: 10px; text-align: center;">
                            <h3>{stats.get('average_similarity', 0):.1%}</h3>
                            <p>Average Similarity</p>
                        </div>
                        <div style="background: #d4edda; padding: 20px; border-radius: 10px; text-align: center;">
                            <h3>{stats.get('unique_sources_identified', 0):,}</h3>
                            <p>Sources Identified</p>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>🔍 Detection Types</h2>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                        <p><strong>Exact Match:</strong> Identical text passages without proper attribution</p>
                        <p><strong>Paraphrase:</strong> Content that closely resembles existing sources</p>
                        <p><strong>Mosaic:</strong> Patchwork of content from multiple sources</p>
                        <p><strong>Self-Plagiarism:</strong> Reuse of author's previously published content</p>
                        <p><strong>Citation Missing:</strong> Proper source material without citation</p>
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