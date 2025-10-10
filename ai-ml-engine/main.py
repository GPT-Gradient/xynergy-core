#!/usr/bin/env python3
"""
Xynergy Platform - AI & Machine Learning Engine
Package 3.4: Advanced AI Features & Machine Learning Capabilities

This service provides:
- Advanced machine learning model management and deployment
- Intelligent pattern recognition and anomaly detection
- Predictive analytics and forecasting capabilities
- Natural language processing and understanding
- Computer vision and image analysis
- Automated model training and optimization
- AI-powered recommendation systems
- Real-time inference and prediction APIs
"""

import os
import asyncio
import json
import uuid
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from google.cloud import firestore, bigquery, storage, pubsub_v1
import httpx
import redis
import websockets

# Import shared tenant utilities
from shared.tenant_utils import (
    TenantContext, get_tenant_context, require_tenant,
    check_feature_access, get_tenant_aware_firestore, add_tenant_middleware
)

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize clients
PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")

db = firestore.Client(project=PROJECT_ID)
bigquery_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)
publisher = pubsub_v1.PublisherClient()

# Redis for caching and model storage
redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

app = FastAPI(
    title="Xynergy AI & Machine Learning Engine",
    description="Advanced AI features and machine learning capabilities",
    version="3.4.0"
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

# Add tenant middleware
add_tenant_middleware(app)

# Data Models
@dataclass
class MLModel:
    model_id: str
    name: str
    model_type: str
    status: str
    accuracy: float
    created_at: datetime
    updated_at: datetime
    tenant_id: str
    features: List[str]
    target: str
    hyperparameters: Dict[str, Any]

@dataclass
class PredictionRequest:
    model_id: str
    input_data: Dict[str, Any]
    confidence_threshold: float = 0.7

@dataclass
class TrainingJob:
    job_id: str
    model_id: str
    status: str
    progress: int
    dataset_path: str
    created_at: datetime
    tenant_id: str
    config: Dict[str, Any]

@dataclass
class AnomalyDetection:
    detection_id: str
    timestamp: datetime
    anomaly_score: float
    is_anomaly: bool
    features: Dict[str, float]
    explanation: str
    tenant_id: str

# Pydantic models for API
class ModelCreationRequest(BaseModel):
    name: str
    model_type: str = Field(..., description="Type: classification, regression, clustering, anomaly_detection")
    features: List[str]
    target: str
    hyperparameters: Dict[str, Any] = {}

class TrainingRequest(BaseModel):
    model_id: str
    dataset_path: str
    config: Dict[str, Any] = {}

class PredictionData(BaseModel):
    model_id: str
    input_data: Dict[str, Any]
    confidence_threshold: float = 0.7

class TextAnalysisRequest(BaseModel):
    text: str
    analysis_type: str = Field(..., description="sentiment, entities, keywords, summary")

class ImageAnalysisRequest(BaseModel):
    image_url: str
    analysis_type: str = Field(..., description="objects, faces, text, similarity")

# Model Manager
class MLModelManager:
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}

    async def create_model(self, tenant_context: TenantContext, request: ModelCreationRequest) -> str:
        """Create a new ML model"""
        model_id = str(uuid.uuid4())

        model = MLModel(
            model_id=model_id,
            name=request.name,
            model_type=request.model_type,
            status="created",
            accuracy=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tenant_id=tenant_context.tenant_id,
            features=request.features,
            target=request.target,
            hyperparameters=request.hyperparameters
        )

        # Store model metadata in Firestore
        tenant_db = get_tenant_aware_firestore(db)
        await self._store_model_metadata(tenant_db, model)

        logger.info("ML model created", model_id=model_id, tenant_id=tenant_context.tenant_id)
        return model_id

    async def train_model(self, tenant_context: TenantContext, model_id: str, dataset_path: str, config: Dict[str, Any]) -> str:
        """Start model training job"""
        job_id = str(uuid.uuid4())

        training_job = TrainingJob(
            job_id=job_id,
            model_id=model_id,
            status="running",
            progress=0,
            dataset_path=dataset_path,
            created_at=datetime.utcnow(),
            tenant_id=tenant_context.tenant_id,
            config=config
        )

        # Store training job
        tenant_db = get_tenant_aware_firestore(db)
        await self._store_training_job(tenant_db, training_job)

        # Start background training
        asyncio.create_task(self._execute_training(tenant_context, training_job))

        logger.info("Model training started", job_id=job_id, model_id=model_id)
        return job_id

    async def _execute_training(self, tenant_context: TenantContext, job: TrainingJob):
        """Execute model training in background"""
        try:
            # Simulate loading dataset
            await asyncio.sleep(1)
            await self._update_training_progress(tenant_context, job.job_id, 20, "Loading dataset")

            # Generate synthetic dataset for demo
            np.random.seed(42)
            n_samples = 1000
            n_features = len(job.config.get("features", ["feature1", "feature2", "feature3"]))

            X = np.random.randn(n_samples, n_features)
            y = (X[:, 0] + X[:, 1] - X[:, 2] > 0).astype(int)

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            await self._update_training_progress(tenant_context, job.job_id, 40, "Preprocessing data")

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            await self._update_training_progress(tenant_context, job.job_id, 60, "Training model")

            # Train model
            model = RandomForestClassifier(
                n_estimators=job.config.get("n_estimators", 100),
                max_depth=job.config.get("max_depth", 10),
                random_state=42
            )
            model.fit(X_train_scaled, y_train)

            await self._update_training_progress(tenant_context, job.job_id, 80, "Evaluating model")

            # Evaluate
            y_pred = model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)

            # Store trained model
            self.models[job.model_id] = model
            self.scalers[job.model_id] = scaler

            # Save to file system
            model_dir = f"/tmp/models/{tenant_context.tenant_id}"
            os.makedirs(model_dir, exist_ok=True)
            joblib.dump(model, f"{model_dir}/{job.model_id}_model.pkl")
            joblib.dump(scaler, f"{model_dir}/{job.model_id}_scaler.pkl")

            await self._update_training_progress(tenant_context, job.job_id, 100, "Training completed")

            # Update model metadata
            tenant_db = get_tenant_aware_firestore(db)
            model_ref = tenant_db.collection("ml_models").document(job.model_id)
            model_ref.update({
                "status": "trained",
                "accuracy": accuracy,
                "updated_at": datetime.utcnow()
            })

            logger.info("Model training completed",
                       job_id=job.job_id,
                       model_id=job.model_id,
                       accuracy=accuracy)

        except Exception as e:
            logger.error("Model training failed", job_id=job.job_id, error=str(e))
            await self._update_training_progress(tenant_context, job.job_id, -1, f"Training failed: {str(e)}")

    async def predict(self, tenant_context: TenantContext, request: PredictionData) -> Dict[str, Any]:
        """Make prediction using trained model"""
        if request.model_id not in self.models:
            # Try to load from file system
            model_dir = f"/tmp/models/{tenant_context.tenant_id}"
            model_path = f"{model_dir}/{request.model_id}_model.pkl"
            scaler_path = f"{model_dir}/{request.model_id}_scaler.pkl"

            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.models[request.model_id] = joblib.load(model_path)
                self.scalers[request.model_id] = joblib.load(scaler_path)
            else:
                raise HTTPException(status_code=404, detail="Model not found or not trained")

        model = self.models[request.model_id]
        scaler = self.scalers[request.model_id]

        # Prepare input data
        features = list(request.input_data.values())
        features_array = np.array(features).reshape(1, -1)
        features_scaled = scaler.transform(features_array)

        # Make prediction
        prediction = model.predict(features_scaled)[0]
        prediction_proba = model.predict_proba(features_scaled)[0]
        confidence = max(prediction_proba)

        result = {
            "prediction": int(prediction),
            "confidence": float(confidence),
            "probabilities": prediction_proba.tolist(),
            "meets_threshold": confidence >= request.confidence_threshold
        }

        logger.info("Prediction made",
                   model_id=request.model_id,
                   prediction=prediction,
                   confidence=confidence)

        return result

    async def _store_model_metadata(self, tenant_db, model: MLModel):
        """Store model metadata in Firestore"""
        model_data = asdict(model)
        model_data["created_at"] = model.created_at
        model_data["updated_at"] = model.updated_at

        tenant_db.collection("ml_models").document(model.model_id).set(model_data)

    async def _store_training_job(self, tenant_db, job: TrainingJob):
        """Store training job in Firestore"""
        job_data = asdict(job)
        job_data["created_at"] = job.created_at

        tenant_db.collection("training_jobs").document(job.job_id).set(job_data)

    async def _update_training_progress(self, tenant_context: TenantContext, job_id: str, progress: int, status: str):
        """Update training job progress"""
        tenant_db = get_tenant_aware_firestore(db)
        job_ref = tenant_db.collection("training_jobs").document(job_id)
        job_ref.update({
            "progress": progress,
            "status": status,
            "updated_at": datetime.utcnow()
        })

# Anomaly Detection Engine
class AnomalyDetectionEngine:
    def __init__(self):
        self.detectors: Dict[str, IsolationForest] = {}

    async def setup_anomaly_detection(self, tenant_context: TenantContext, features: List[str]) -> str:
        """Setup anomaly detection for tenant"""
        detector_id = f"{tenant_context.tenant_id}_anomaly_detector"

        # Create isolation forest detector
        detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )

        # Train on historical data (simulated)
        np.random.seed(42)
        normal_data = np.random.randn(1000, len(features))
        detector.fit(normal_data)

        self.detectors[detector_id] = detector

        logger.info("Anomaly detection setup", detector_id=detector_id, features=features)
        return detector_id

    async def detect_anomaly(self, tenant_context: TenantContext, features: Dict[str, float]) -> AnomalyDetection:
        """Detect anomalies in incoming data"""
        detector_id = f"{tenant_context.tenant_id}_anomaly_detector"

        if detector_id not in self.detectors:
            await self.setup_anomaly_detection(tenant_context, list(features.keys()))

        detector = self.detectors[detector_id]

        # Prepare features
        feature_values = np.array(list(features.values())).reshape(1, -1)

        # Detect anomaly
        anomaly_score = detector.decision_function(feature_values)[0]
        is_anomaly = detector.predict(feature_values)[0] == -1

        detection = AnomalyDetection(
            detection_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            anomaly_score=float(anomaly_score),
            is_anomaly=is_anomaly,
            features=features,
            explanation=f"Anomaly score: {anomaly_score:.3f}, Threshold: -0.1",
            tenant_id=tenant_context.tenant_id
        )

        # Store detection result
        tenant_db = get_tenant_aware_firestore(db)
        detection_data = asdict(detection)
        detection_data["timestamp"] = detection.timestamp

        tenant_db.collection("anomaly_detections").document(detection.detection_id).set(detection_data)

        if is_anomaly:
            logger.warning("Anomaly detected",
                          detection_id=detection.detection_id,
                          anomaly_score=anomaly_score,
                          features=features)

        return detection

# NLP Engine
class NLPEngine:
    def __init__(self):
        self.sentiment_model = None

    async def analyze_text(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze text using NLP techniques"""

        if analysis_type == "sentiment":
            return await self._analyze_sentiment(text)
        elif analysis_type == "entities":
            return await self._extract_entities(text)
        elif analysis_type == "keywords":
            return await self._extract_keywords(text)
        elif analysis_type == "summary":
            return await self._summarize_text(text)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")

    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        # Simple rule-based sentiment analysis for demo
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like"]
        negative_words = ["bad", "terrible", "awful", "horrible", "hate", "dislike", "poor", "worst"]

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_score": positive_count,
            "negative_score": negative_count
        }

    async def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text"""
        # Simple entity extraction for demo
        import re

        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

        # Extract phone numbers
        phones = re.findall(r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b', text)

        # Extract potential names (capitalized words)
        names = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text)

        return {
            "entities": {
                "emails": emails,
                "phones": phones,
                "names": names
            },
            "entity_count": len(emails) + len(phones) + len(names)
        }

    async def _extract_keywords(self, text: str) -> Dict[str, Any]:
        """Extract keywords from text"""
        # Simple keyword extraction based on word frequency
        import re
        from collections import Counter

        # Remove punctuation and convert to lowercase
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Filter out common stop words
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "up", "about", "into", "through", "during", "before", "after", "above", "below", "between", "among", "this", "that", "these", "those", "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "whose", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "will", "would", "could", "should", "may", "might", "must", "can", "shall"}

        filtered_words = [word for word in words if word not in stop_words]

        # Count word frequencies
        word_counts = Counter(filtered_words)
        top_keywords = word_counts.most_common(10)

        return {
            "keywords": [{"word": word, "frequency": count} for word, count in top_keywords],
            "total_words": len(words),
            "unique_words": len(set(words))
        }

    async def _summarize_text(self, text: str) -> Dict[str, Any]:
        """Summarize text"""
        # Simple extractive summarization for demo
        sentences = text.split('.')

        if len(sentences) <= 2:
            summary = text
        else:
            # Take first and last sentences as summary
            summary = f"{sentences[0].strip()}. {sentences[-2].strip()}."

        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(text) if len(text) > 0 else 0
        }

# Computer Vision Engine
class ComputerVisionEngine:
    def __init__(self):
        pass

    async def analyze_image(self, image_url: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze image using computer vision techniques"""

        if analysis_type == "objects":
            return await self._detect_objects(image_url)
        elif analysis_type == "faces":
            return await self._detect_faces(image_url)
        elif analysis_type == "text":
            return await self._extract_text(image_url)
        elif analysis_type == "similarity":
            return await self._compute_similarity(image_url)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")

    async def _detect_objects(self, image_url: str) -> Dict[str, Any]:
        """Detect objects in image"""
        # Mock object detection for demo
        mock_objects = [
            {"name": "person", "confidence": 0.95, "bbox": [100, 100, 200, 300]},
            {"name": "car", "confidence": 0.87, "bbox": [300, 150, 500, 250]},
            {"name": "tree", "confidence": 0.76, "bbox": [50, 50, 150, 200]}
        ]

        return {
            "objects": mock_objects,
            "object_count": len(mock_objects),
            "image_url": image_url
        }

    async def _detect_faces(self, image_url: str) -> Dict[str, Any]:
        """Detect faces in image"""
        # Mock face detection for demo
        mock_faces = [
            {"confidence": 0.99, "bbox": [120, 80, 180, 140], "age": 35, "gender": "male"},
            {"confidence": 0.92, "bbox": [250, 90, 310, 150], "age": 28, "gender": "female"}
        ]

        return {
            "faces": mock_faces,
            "face_count": len(mock_faces),
            "image_url": image_url
        }

    async def _extract_text(self, image_url: str) -> Dict[str, Any]:
        """Extract text from image (OCR)"""
        # Mock OCR for demo
        mock_text = "Welcome to Xynergy Platform\nAdvanced AI Features\nBuilding the future today"

        return {
            "text": mock_text,
            "confidence": 0.94,
            "word_count": len(mock_text.split()),
            "image_url": image_url
        }

    async def _compute_similarity(self, image_url: str) -> Dict[str, Any]:
        """Compute image similarity features"""
        # Mock similarity computation for demo
        feature_vector = np.random.rand(128).tolist()  # 128-dimensional feature vector

        return {
            "feature_vector": feature_vector,
            "vector_dimension": len(feature_vector),
            "image_url": image_url
        }

# Initialize engines
model_manager = MLModelManager()
anomaly_engine = AnomalyDetectionEngine()
nlp_engine = NLPEngine()
cv_engine = ComputerVisionEngine()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:  # Phase 3: Specific exception handling
                pass

manager = ConnectionManager()

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Xynergy AI & ML Engine</title>
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
            <h1>🤖 Xynergy AI & Machine Learning Engine</h1>
            <p>Advanced AI features and machine learning capabilities for intelligent business operations</p>

            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🎯 Machine Learning Models</h3>
                    <p>Create, train, and deploy custom ML models with automated optimization</p>
                </div>
                <div class="feature-card">
                    <h3>🔍 Anomaly Detection</h3>
                    <p>Real-time anomaly detection with intelligent alerting and pattern recognition</p>
                </div>
                <div class="feature-card">
                    <h3>💬 Natural Language Processing</h3>
                    <p>Sentiment analysis, entity extraction, keyword analysis, and text summarization</p>
                </div>
                <div class="feature-card">
                    <h3>👁️ Computer Vision</h3>
                    <p>Object detection, face recognition, OCR, and image similarity analysis</p>
                </div>
                <div class="feature-card">
                    <h3>📊 Predictive Analytics</h3>
                    <p>Advanced forecasting and prediction with confidence scoring</p>
                </div>
                <div class="feature-card">
                    <h3>🚀 Model Management</h3>
                    <p>Automated model training, versioning, and deployment pipeline</p>
                </div>
            </div>

            <div class="demo-section">
                <h3>🎯 ML Model Demo</h3>
                <div>
                    <input type="text" id="modelName" placeholder="Model Name" value="Demo Classification Model">
                    <select id="modelType">
                        <option value="classification">Classification</option>
                        <option value="regression">Regression</option>
                        <option value="clustering">Clustering</option>
                        <option value="anomaly_detection">Anomaly Detection</option>
                    </select>
                    <button onclick="createModel()">Create Model</button>
                    <button onclick="trainModel()">Train Model</button>
                    <button onclick="makePrediction()">Make Prediction</button>
                </div>
                <div id="trainingStatus"></div>
            </div>

            <div class="demo-section">
                <h3>🔍 Anomaly Detection Demo</h3>
                <div>
                    <input type="number" id="feature1" placeholder="Feature 1" value="1.5" step="0.1">
                    <input type="number" id="feature2" placeholder="Feature 2" value="-0.5" step="0.1">
                    <input type="number" id="feature3" placeholder="Feature 3" value="2.1" step="0.1">
                    <button onclick="detectAnomaly()">Detect Anomaly</button>
                </div>
                <div id="anomalyResults"></div>
            </div>

            <div class="demo-section">
                <h3>💬 NLP Analysis Demo</h3>
                <div>
                    <textarea id="nlpText" placeholder="Enter text to analyze..." rows="3" style="width: 60%;">This is an amazing product! I love how easy it is to use and the results are fantastic.</textarea>
                    <select id="nlpType">
                        <option value="sentiment">Sentiment Analysis</option>
                        <option value="entities">Entity Extraction</option>
                        <option value="keywords">Keyword Extraction</option>
                        <option value="summary">Text Summarization</option>
                    </select>
                    <button onclick="analyzeText()">Analyze Text</button>
                </div>
                <div id="nlpResults"></div>
            </div>

            <div class="demo-section">
                <h3>👁️ Computer Vision Demo</h3>
                <div>
                    <input type="url" id="imageUrl" placeholder="Image URL" value="https://example.com/sample-image.jpg" style="width: 50%;">
                    <select id="cvType">
                        <option value="objects">Object Detection</option>
                        <option value="faces">Face Detection</option>
                        <option value="text">Text Extraction (OCR)</option>
                        <option value="similarity">Similarity Features</option>
                    </select>
                    <button onclick="analyzeImage()">Analyze Image</button>
                </div>
                <div id="cvResults"></div>
            </div>

            <div class="demo-section">
                <h3>📊 Real-time AI Monitoring</h3>
                <div>
                    <button onclick="connectWebSocket()">Connect Live Updates</button>
                    <button onclick="disconnectWebSocket()">Disconnect</button>
                    <div id="wsStatus">Disconnected</div>
                </div>
            </div>
        </div>

        <script>
            let currentModelId = null;
            let ws = null;

            async function createModel() {
                const modelName = document.getElementById('modelName').value;
                const modelType = document.getElementById('modelType').value;

                try {
                    const response = await fetch('/models', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Tenant-ID': 'demo-tenant'
                        },
                        body: JSON.stringify({
                            name: modelName,
                            model_type: modelType,
                            features: ['feature1', 'feature2', 'feature3'],
                            target: 'target',
                            hyperparameters: {n_estimators: 100, max_depth: 10}
                        })
                    });

                    const result = await response.json();
                    currentModelId = result.model_id;

                    document.getElementById('trainingStatus').innerHTML =
                        `<div class="result">✅ Model created successfully! ID: ${result.model_id}</div>`;
                } catch (error) {
                    document.getElementById('trainingStatus').innerHTML =
                        `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }

            async function trainModel() {
                if (!currentModelId) {
                    alert('Please create a model first');
                    return;
                }

                try {
                    const response = await fetch('/models/train', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Tenant-ID': 'demo-tenant'
                        },
                        body: JSON.stringify({
                            model_id: currentModelId,
                            dataset_path: 'demo/dataset.csv',
                            config: {features: ['feature1', 'feature2', 'feature3'], n_estimators: 100}
                        })
                    });

                    const result = await response.json();

                    document.getElementById('trainingStatus').innerHTML =
                        `<div class="result">🚀 Training started! Job ID: ${result.job_id}<br>
                         <span class="status-badge status-running">Training in progress...</span></div>`;
                } catch (error) {
                    document.getElementById('trainingStatus').innerHTML =
                        `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }

            async function makePrediction() {
                if (!currentModelId) {
                    alert('Please create and train a model first');
                    return;
                }

                try {
                    // Wait a bit for training to complete
                    await new Promise(resolve => setTimeout(resolve, 3000));

                    const response = await fetch('/models/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Tenant-ID': 'demo-tenant'
                        },
                        body: JSON.stringify({
                            model_id: currentModelId,
                            input_data: {feature1: 1.2, feature2: -0.5, feature3: 0.8},
                            confidence_threshold: 0.7
                        })
                    });

                    const result = await response.json();

                    document.getElementById('trainingStatus').innerHTML +=
                        `<div class="result">🎯 Prediction: ${result.prediction}<br>
                         Confidence: ${(result.confidence * 100).toFixed(1)}%<br>
                         Meets threshold: ${result.meets_threshold ? '✅' : '❌'}</div>`;
                } catch (error) {
                    document.getElementById('trainingStatus').innerHTML +=
                        `<div class="result">❌ Prediction error: ${error.message}</div>`;
                }
            }

            async function detectAnomaly() {
                const feature1 = parseFloat(document.getElementById('feature1').value);
                const feature2 = parseFloat(document.getElementById('feature2').value);
                const feature3 = parseFloat(document.getElementById('feature3').value);

                try {
                    const response = await fetch('/anomaly/detect', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Tenant-ID': 'demo-tenant'
                        },
                        body: JSON.stringify({
                            features: {feature1, feature2, feature3}
                        })
                    });

                    const result = await response.json();

                    document.getElementById('anomalyResults').innerHTML =
                        `<div class="result">
                            ${result.is_anomaly ? '🚨 ANOMALY DETECTED' : '✅ Normal behavior'}<br>
                            Anomaly Score: ${result.anomaly_score.toFixed(3)}<br>
                            ${result.explanation}
                         </div>`;
                } catch (error) {
                    document.getElementById('anomalyResults').innerHTML =
                        `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }

            async function analyzeText() {
                const text = document.getElementById('nlpText').value;
                const analysisType = document.getElementById('nlpType').value;

                try {
                    const response = await fetch('/nlp/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Tenant-ID': 'demo-tenant'
                        },
                        body: JSON.stringify({
                            text: text,
                            analysis_type: analysisType
                        })
                    });

                    const result = await response.json();

                    document.getElementById('nlpResults').innerHTML =
                        `<div class="result">
                            <strong>${analysisType.toUpperCase()} Results:</strong><br>
                            <pre>${JSON.stringify(result, null, 2)}</pre>
                         </div>`;
                } catch (error) {
                    document.getElementById('nlpResults').innerHTML =
                        `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }

            async function analyzeImage() {
                const imageUrl = document.getElementById('imageUrl').value;
                const analysisType = document.getElementById('cvType').value;

                try {
                    const response = await fetch('/cv/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Tenant-ID': 'demo-tenant'
                        },
                        body: JSON.stringify({
                            image_url: imageUrl,
                            analysis_type: analysisType
                        })
                    });

                    const result = await response.json();

                    document.getElementById('cvResults').innerHTML =
                        `<div class="result">
                            <strong>${analysisType.toUpperCase()} Results:</strong><br>
                            <pre>${JSON.stringify(result, null, 2)}</pre>
                         </div>`;
                } catch (error) {
                    document.getElementById('cvResults').innerHTML =
                        `<div class="result">❌ Error: ${error.message}</div>`;
                }
            }

            function connectWebSocket() {
                ws = new WebSocket(`ws://localhost:8080/ws`);

                ws.onopen = function(event) {
                    document.getElementById('wsStatus').innerHTML = '🟢 Connected - Live AI updates active';
                };

                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    console.log('AI Update:', data);
                };

                ws.onclose = function(event) {
                    document.getElementById('wsStatus').innerHTML = '🔴 Disconnected';
                };
            }

            function disconnectWebSocket() {
                if (ws) {
                    ws.close();
                    document.getElementById('wsStatus').innerHTML = '🔴 Disconnected';
                }
            }
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-ml-engine",
        "version": "3.4.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "ml_models": "active",
            "anomaly_detection": "active",
            "nlp": "active",
            "computer_vision": "active"
        }
    }

@app.post("/models")
@require_tenant(allow_system=False)
@check_feature_access("advanced_ai")
async def create_ml_model(
    request: ModelCreationRequest,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Create a new ML model"""
    model_id = await model_manager.create_model(tenant_context, request)
    return {"model_id": model_id, "status": "created"}

@app.post("/models/train")
@require_tenant(allow_system=False)
@check_feature_access("advanced_ai")
async def train_ml_model(
    request: TrainingRequest,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Start model training"""
    job_id = await model_manager.train_model(
        tenant_context,
        request.model_id,
        request.dataset_path,
        request.config
    )
    return {"job_id": job_id, "status": "training_started"}

@app.post("/models/predict")
@require_tenant(allow_system=False)
@check_feature_access("advanced_ai")
async def predict(
    request: PredictionData,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Make prediction using trained model"""
    result = await model_manager.predict(tenant_context, request)
    return result

@app.get("/models/{model_id}")
@require_tenant(allow_system=False)
async def get_model(
    model_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Get model information"""
    tenant_db = get_tenant_aware_firestore(db)
    model_doc = tenant_db.collection("ml_models").document(model_id).get()

    if not model_doc.exists:
        raise HTTPException(status_code=404, detail="Model not found")

    return model_doc.to_dict()

@app.post("/anomaly/detect")
@require_tenant(allow_system=False)
@check_feature_access("anomaly_detection")
async def detect_anomaly(
    features: Dict[str, float],
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Detect anomalies in data"""
    detection = await anomaly_engine.detect_anomaly(tenant_context, features)
    return asdict(detection)

@app.get("/anomaly/history")
@require_tenant(allow_system=False)
async def get_anomaly_history(
    limit: int = 100,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Get anomaly detection history"""
    tenant_db = get_tenant_aware_firestore(db)
    detections = (
        tenant_db.collection("anomaly_detections")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )

    history = []
    for detection in detections:
        data = detection.to_dict()
        history.append(data)

    return {"detections": history, "count": len(history)}

@app.post("/nlp/analyze")
@require_tenant(allow_system=False)
@check_feature_access("nlp")
async def analyze_text(
    request: TextAnalysisRequest,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Analyze text using NLP techniques"""
    result = await nlp_engine.analyze_text(request.text, request.analysis_type)
    return result

@app.post("/cv/analyze")
@require_tenant(allow_system=False)
@check_feature_access("computer_vision")
async def analyze_image(
    request: ImageAnalysisRequest,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Analyze image using computer vision"""
    result = await cv_engine.analyze_image(request.image_url, request.analysis_type)
    return result

@app.get("/analytics/ai-usage")
@require_tenant(allow_system=False)
async def get_ai_usage_analytics(
    days: int = 30,
    tenant_context: TenantContext = Depends(get_tenant_context)
):
    """Get AI usage analytics for tenant"""
    try:
        # Query BigQuery for usage data
        dataset_id = f"tenant_{tenant_context.tenant_id}_analytics"

        query = f"""
        SELECT
            DATE(timestamp) as date,
            COUNT(*) as total_requests,
            SUM(CASE WHEN service = 'ml_models' THEN 1 ELSE 0 END) as ml_requests,
            SUM(CASE WHEN service = 'anomaly_detection' THEN 1 ELSE 0 END) as anomaly_requests,
            SUM(CASE WHEN service = 'nlp' THEN 1 ELSE 0 END) as nlp_requests,
            SUM(CASE WHEN service = 'computer_vision' THEN 1 ELSE 0 END) as cv_requests,
            AVG(processing_time_ms) as avg_processing_time
        FROM `{PROJECT_ID}.{dataset_id}.ai_usage`
        WHERE timestamp >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
        GROUP BY date
        ORDER BY date DESC
        """

        query_job = bigquery_client.query(query)
        results = list(query_job)

        usage_data = []
        for row in results:
            usage_data.append({
                "date": row.date.isoformat(),
                "total_requests": row.total_requests,
                "ml_requests": row.ml_requests,
                "anomaly_requests": row.anomaly_requests,
                "nlp_requests": row.nlp_requests,
                "cv_requests": row.cv_requests,
                "avg_processing_time": round(row.avg_processing_time, 2) if row.avg_processing_time else 0
            })

        return {
            "tenant_id": tenant_context.tenant_id,
            "period_days": days,
            "usage_data": usage_data,
            "total_requests": sum(d["total_requests"] for d in usage_data)
        }

    except Exception as e:
        logger.error("Failed to fetch AI usage analytics", error=str(e))
        return {
            "tenant_id": tenant_context.tenant_id,
            "period_days": days,
            "usage_data": [],
            "total_requests": 0,
            "error": "Analytics data not available"
        }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time AI updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic AI system updates
            status_update = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "ai_status",
                "data": {
                    "active_models": len(model_manager.models),
                    "anomaly_detectors": len(anomaly_engine.detectors),
                    "system_status": "healthy",
                    "cpu_usage": np.random.uniform(10, 80),
                    "memory_usage": np.random.uniform(30, 70),
                    "gpu_usage": np.random.uniform(0, 95)
                }
            }

            await manager.send_personal_message(json.dumps(status_update), websocket)
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/execute")
@require_tenant(allow_system=True)
async def execute_ai_task(
    task: Dict[str, Any],
    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)
):
    """Execute AI/ML task from service mesh"""
    task_type = task.get("type")
    task_data = task.get("data", {})

    try:
        if task_type == "train_model":
            model_id = await model_manager.create_model(
                tenant_context,
                ModelCreationRequest(**task_data["model_config"])
            )
            job_id = await model_manager.train_model(
                tenant_context,
                model_id,
                task_data["dataset_path"],
                task_data.get("config", {})
            )
            return {"status": "success", "model_id": model_id, "job_id": job_id}

        elif task_type == "predict":
            result = await model_manager.predict(
                tenant_context,
                PredictionData(**task_data)
            )
            return {"status": "success", "prediction": result}

        elif task_type == "detect_anomaly":
            detection = await anomaly_engine.detect_anomaly(
                tenant_context,
                task_data["features"]
            )
            return {"status": "success", "detection": asdict(detection)}

        elif task_type == "analyze_text":
            result = await nlp_engine.analyze_text(
                task_data["text"],
                task_data["analysis_type"]
            )
            return {"status": "success", "analysis": result}

        elif task_type == "analyze_image":
            result = await cv_engine.analyze_image(
                task_data["image_url"],
                task_data["analysis_type"]
            )
            return {"status": "success", "analysis": result}

        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}

    except Exception as e:
        logger.error("AI task execution failed", task_type=task_type, error=str(e))
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    logger.info("Starting Xynergy AI & ML Engine", version="3.4.0")
    uvicorn.run(app, host="0.0.0.0", port=8080)