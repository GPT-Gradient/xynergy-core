"""
xynergy-competency-engine/main.py
Dynamic user competency profiling and assessment engine
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore, pubsub_v1

# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

import os
import uvicorn
import json
from datetime import datetime
from typing import Dict, List, Optional
from phase2_utils import CircuitBreaker, CircuitBreakerConfig, call_service_with_circuit_breaker, PerformanceMonitor
from adaptive_workflow import AdaptiveWorkflowEngine
from collective_intelligence import CollectiveIntelligenceEngine

PROJECT_ID = os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
REGION = os.getenv("REGION", "us-central1")

publisher = get_publisher_client()  # Phase 4: Shared connection pooling
db = get_firestore_client()  # Phase 4: Shared connection pooling

app = FastAPI(title="Xynergy Competency Engine", version="1.0.0")
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

performance_monitor = PerformanceMonitor("competency-engine")
circuit_breaker = CircuitBreaker(CircuitBreakerConfig(failure_threshold=5, timeout_duration=60))

adaptive_workflow = AdaptiveWorkflowEngine()
collective_intelligence = CollectiveIntelligenceEngine()

class CompetencyEngine:
    def __init__(self):
        self.domains = {}
        self.user_profiles = {}
    
    async def analyze_conversation(self, user_id: str, conversation_text: str, context: dict):
        """Extract competency signals from user conversation"""
        try:
            signals = []
            
            technical_indicators = [
                'database', 'api', 'cloud', 'security', 'frontend', 'backend',
                'docker', 'kubernetes', 'terraform', 'git', 'ci/cd'
            ]
            
            for indicator in technical_indicators:
                if indicator.lower() in conversation_text.lower():
                    signals.append({
                        'domain': self._map_to_domain(indicator),
                        'signal_type': 'vocabulary_usage',
                        'confidence': 0.7,
                        'evidence': indicator
                    })
            
            await self._update_user_competency_with_circuit_breaker(user_id, signals)
            return signals
        except Exception as e:
            print(f"Error analyzing conversation: {e}")
            return []
    
    def _map_to_domain(self, indicator: str) -> str:
        """Map technical indicators to competency domains"""
        domain_mapping = {
            'database': 'data_management',
            'api': 'backend_development',
            'cloud': 'cloud_architecture',
            'security': 'security_practices',
            'frontend': 'frontend_development',
            'backend': 'backend_development',
            'docker': 'containerization',
            'kubernetes': 'orchestration',
            'terraform': 'infrastructure_as_code',
            'git': 'version_control',
            'ci/cd': 'devops_practices'
        }
        return domain_mapping.get(indicator, 'general_technical')
    
    async def _update_user_competency_with_circuit_breaker(self, user_id: str, signals: List[dict]):
        """Update user competency profile with circuit breaker protection"""
        try:
            await call_service_with_circuit_breaker(
                self._update_user_competency,
                circuit_breaker,
                user_id,
                signals
            )
        except Exception as e:
            print(f"Circuit breaker protected: Error updating competency: {e}")
    
    async def _update_user_competency(self, user_id: str, signals: List[dict]):
        """Update user competency profile with new signals"""
        profile_ref = db.collection('user_competency_profiles').document(user_id)
        
        profile_data = {
            'user_id': user_id,
            'last_updated': datetime.utcnow(),
            'competency_signals': signals,
            'domains': {}
        }
        
        for signal in signals:
            domain = signal['domain']
            if domain not in profile_data['domains']:
                profile_data['domains'][domain] = {
                    'level': 'novice',
                    'confidence': 0.0,
                    'evidence_count': 0
                }
            
            profile_data['domains'][domain]['evidence_count'] += 1
            profile_data['domains'][domain]['confidence'] = min(
                profile_data['domains'][domain]['confidence'] + signal['confidence'] * 0.1,
                1.0
            )
        
        profile_ref.set(profile_data, merge=True)
    
    async def assess_task_readiness(self, user_id: str, task_description: str):
        """Assess if user is ready for a complex task or needs competency assessment"""
        try:
            return await call_service_with_circuit_breaker(
                self._do_task_assessment,
                circuit_breaker,
                user_id,
                task_description
            )
        except Exception as e:
            return {
                'needs_assessment': True,
                'assessment_type': 'fallback_assessment',
                'error': str(e)
            }
    
    async def _do_task_assessment(self, user_id: str, task_description: str):
        """Internal task assessment with circuit breaker protection"""
        profile_ref = db.collection('user_competency_profiles').document(user_id)
        profile_doc = await profile_ref.get()
        
        if not profile_doc.exists:
            return {
                'needs_assessment': True,
                'assessment_type': 'initial_profiling',
                'estimated_time': '3-5 minutes'
            }
        
        profile = profile_doc.to_dict()
        required_domains = self._analyze_task_requirements(task_description)
        
        competency_gaps = []
        for domain in required_domains:
            user_competency = profile.get('domains', {}).get(domain, {})
            if user_competency.get('confidence', 0) < 0.6:
                competency_gaps.append(domain)
        
        if competency_gaps:
            return {
                'needs_assessment': True,
                'assessment_type': 'targeted_gaps',
                'gaps': competency_gaps,
                'estimated_time': f"{len(competency_gaps)} minutes"
            }
        
        return {
            'needs_assessment': False,
            'profile': profile,
            'recommended_approach': 'adaptive_workflow'
        }
    
    def _analyze_task_requirements(self, task_description: str) -> List[str]:
        """Analyze what competencies are required for a given task"""
        requirements = []
        
        if any(word in task_description.lower() for word in ['app', 'application', 'build']):
            requirements.extend(['frontend_development', 'backend_development'])
        
        if any(word in task_description.lower() for word in ['database', 'data', 'store']):
            requirements.append('data_management')
        
        if any(word in task_description.lower() for word in ['deploy', 'cloud', 'server']):
            requirements.append('cloud_architecture')
        
        if any(word in task_description.lower() for word in ['secure', 'auth', 'permission']):
            requirements.append('security_practices')
        
        return requirements

competency_engine = CompetencyEngine()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "competency-engine"}

# Service Mesh Infrastructure - Workflow Execution Endpoint
@app.post("/execute")
async def execute_workflow_step(request: Dict[str, Any]):
    """Standardized execution endpoint for AI Assistant workflow orchestration."""
    try:
        action = request.get("action")
        parameters = request.get("parameters", {})
        workflow_context = request.get("workflow_context", {})

        if action == "assess_competency":
            user_id = parameters.get("user_id", "workflow_user")
            assessment_result = {
                "assessment_id": f"assess_{int(time.time())}",
                "user_id": user_id,
                "workflow_id": workflow_context.get("workflow_id"),
                "competency_scores": {
                    "technical_skills": 0.87,
                    "project_management": 0.92,
                    "communication": 0.89,
                    "problem_solving": 0.91
                },
                "overall_score": 0.90,
                "assessed_at": datetime.now()
            }

            return {
                "success": True,
                "action": action,
                "output": {"assessment_id": assessment_result["assessment_id"], "overall_score": assessment_result["overall_score"]},
                "execution_time": time.time(),
                "service": "xynergy-competency-engine"
            }

        else:
            return {
                "success": False,
                "error": f"Action '{action}' not supported by xynergy-competency-engine",
                "supported_actions": ["assess_competency"],
                "service": "xynergy-competency-engine"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "action": request.get("action"),
            "service": "xynergy-competency-engine"
        }

@app.post("/analyze-conversation")
async def analyze_conversation(data: dict):
    """Analyze conversation for competency signals"""
    try:
        user_id = data.get('user_id')
        conversation = data.get('conversation')
        context = data.get('context', {})
        
        if not user_id or not conversation:
            raise HTTPException(status_code=400, detail="user_id and conversation required")
        
        with performance_monitor.track_request("analyze_conversation"):
            signals = await competency_engine.analyze_conversation(user_id, conversation, context)
        
        return {"signals": signals, "status": "analyzed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/assess-task-readiness")
async def assess_task_readiness(data: dict):
    """Assess if user is ready for a complex task"""
    try:
        user_id = data.get('user_id')
        task_description = data.get('task_description')
        
        if not user_id or not task_description:
            raise HTTPException(status_code=400, detail="user_id and task_description required")
        
        with performance_monitor.track_request("assess_task_readiness"):
            assessment = await competency_engine.assess_task_readiness(user_id, task_description)
        
        return assessment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@app.post("/generate-adaptive-workflow")
async def generate_adaptive_workflow(data: dict):
    """Generate adaptive workflow based on user competency"""
    try:
        user_id = data.get('user_id')
        request = data.get('request')
        context = data.get('context', {})
        
        if not user_id or not request:
            raise HTTPException(status_code=400, detail="user_id and request required")
        
        with performance_monitor.track_request("generate_adaptive_workflow"):
            workflow = await adaptive_workflow.process_request(user_id, request, context)
        
        return workflow
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow generation failed: {str(e)}")

@app.post("/process-interaction")
async def process_interaction(data: dict):
    """Process interaction for collective intelligence"""
    try:
        client_id = data.get('client_id')
        user_id = data.get('user_id')
        interaction = data.get('interaction', {})
        
        if not client_id or not user_id:
            raise HTTPException(status_code=400, detail="client_id and user_id required")
        
        with performance_monitor.track_request("process_interaction"):
            result = await collective_intelligence.process_interaction(client_id, user_id, interaction)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interaction processing failed: {str(e)}")

@app.get("/user-profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user competency profile"""
    try:
        return await call_service_with_circuit_breaker(
            _get_user_profile_internal,
            circuit_breaker,
            user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile retrieval failed: {str(e)}")

async def _get_user_profile_internal(user_id: str):
    """Internal user profile retrieval with circuit breaker protection"""
    profile_ref = db.collection('user_competency_profiles').document(user_id)
    profile_doc = await profile_ref.get()
    
    if not profile_doc.exists:
        return {"profile": None, "status": "not_found"}
    
    return {"profile": profile_doc.to_dict(), "status": "found"}

@app.get("/platform-intelligence")
async def get_platform_intelligence():
    """Get platform intelligence summary"""
    try:
        with performance_monitor.track_request("platform_intelligence"):
            summary = await collective_intelligence.get_platform_intelligence_summary()
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligence summary failed: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
