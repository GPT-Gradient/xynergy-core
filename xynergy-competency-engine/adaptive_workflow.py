"""
adaptive_workflow.py
Intelligent workflow orchestration based on user competency
"""
import json
from typing import Dict, List, Optional, Any
from google.cloud import firestore
from datetime import datetime

class AdaptiveWorkflowEngine:
    def __init__(self):
        self.db = firestore.Client()
        self.complexity_thresholds = {
            'simple': 1,
            'moderate': 3,
            'complex': 5,
            'expert': 8
        }
    
    async def process_request(self, user_id: str, request: str, context: dict = None):
        """Main entry point for processing user requests with adaptive workflows"""
        try:
            complexity_analysis = await self.analyze_task_complexity(request)
            
            if complexity_analysis['complexity_level'] == 'simple':
                return await self.standard_workflow(request, context)
            
            competency_check = await self.assess_user_readiness(user_id, request)
            
            if competency_check['needs_assessment']:
                return await self.initiate_competency_assessment(user_id, competency_check)
            
            return await self.generate_personalized_workflow(
                user_id, 
                request, 
                competency_check['profile'],
                complexity_analysis
            )
        except Exception as e:
            return {
                'workflow_type': 'error_fallback',
                'error': str(e),
                'fallback_to': 'standard_workflow'
            }
    
    async def analyze_task_complexity(self, request: str) -> Dict[str, Any]:
        """Analyze the complexity of a user request"""
        complexity_indicators = {
            'multi_domain': 0,
            'technical_depth': 0,
            'integration_points': 0,
            'decision_complexity': 0
        }
        
        domain_keywords = {
            'frontend': ['ui', 'interface', 'react', 'vue', 'angular', 'html', 'css'],
            'backend': ['api', 'server', 'database', 'endpoint', 'service'],
            'infrastructure': ['deploy', 'cloud', 'docker', 'kubernetes', 'terraform'],
            'security': ['auth', 'permission', 'secure', 'encrypt', 'ssl'],
            'data': ['database', 'sql', 'nosql', 'analytics', 'report']
        }
        
        domains_involved = []
        for domain, keywords in domain_keywords.items():
            if any(keyword in request.lower() for keyword in keywords):
                domains_involved.append(domain)
        
        complexity_indicators['multi_domain'] = len(domains_involved)
        
        technical_terms = ['architecture', 'design pattern', 'scalable', 'optimize', 'performance']
        complexity_indicators['technical_depth'] = sum(
            1 for term in technical_terms if term in request.lower()
        )
        
        integration_terms = ['integrate', 'connect', 'sync', 'webhook', 'api call']
        complexity_indicators['integration_points'] = sum(
            1 for term in integration_terms if term in request.lower()
        )
        
        decision_terms = ['choose', 'decide', 'compare', 'evaluate', 'recommend']
        complexity_indicators['decision_complexity'] = sum(
            1 for term in decision_terms if term in request.lower()
        )
        
        total_complexity = sum(complexity_indicators.values())
        
        if total_complexity <= self.complexity_thresholds['simple']:
            complexity_level = 'simple'
        elif total_complexity <= self.complexity_thresholds['moderate']:
            complexity_level = 'moderate'
        elif total_complexity <= self.complexity_thresholds['complex']:
            complexity_level = 'complex'
        else:
            complexity_level = 'expert'
        
        return {
            'complexity_level': complexity_level,
            'complexity_score': total_complexity,
            'indicators': complexity_indicators,
            'domains_involved': domains_involved,
            'requires_strategic_pause': total_complexity >= self.complexity_thresholds['complex']
        }
    
    async def assess_user_readiness(self, user_id: str, request: str) -> Dict[str, Any]:
        """Assess if user is ready for the requested task"""
        try:
            profile_ref = self.db.collection('user_competency_profiles').document(user_id)
            profile_doc = profile_ref.get()
            
            if not profile_doc.exists:
                return {
                    'needs_assessment': True,
                    'assessment_type': 'initial_profiling',
                    'reason': 'No competency profile found'
                }
            
            profile = profile_doc.to_dict()
            required_domains = self._extract_required_domains(request)
            
            competency_gaps = []
            weak_areas = []
            
            for domain in required_domains:
                user_competency = profile.get('domains', {}).get(domain, {})
                confidence = user_competency.get('confidence', 0)
                
                if confidence < 0.3:
                    competency_gaps.append(domain)
                elif confidence < 0.6:
                    weak_areas.append(domain)
            
            if competency_gaps:
                return {
                    'needs_assessment': True,
                    'assessment_type': 'targeted_gaps',
                    'gaps': competency_gaps,
                    'weak_areas': weak_areas,
                    'reason': f'Low competency in: {", ".join(competency_gaps)}'
                }
            
            return {
                'needs_assessment': False,
                'profile': profile,
                'weak_areas': weak_areas,
                'recommended_approach': 'adaptive_workflow'
            }
        except Exception as e:
            return {
                'needs_assessment': False,
                'error': str(e),
                'fallback_approach': 'standard_workflow'
            }
    
    def _extract_required_domains(self, request: str) -> List[str]:
        """Extract required competency domains from request"""
        domain_mapping = {
            'frontend_development': ['ui', 'interface', 'react', 'vue', 'html', 'css', 'javascript'],
            'backend_development': ['api', 'server', 'endpoint', 'service', 'backend'],
            'data_management': ['database', 'sql', 'data', 'analytics', 'query'],
            'cloud_architecture': ['deploy', 'cloud', 'aws', 'gcp', 'azure', 'infrastructure'],
            'security_practices': ['auth', 'secure', 'permission', 'encrypt', 'ssl'],
            'devops_practices': ['ci/cd', 'docker', 'kubernetes', 'terraform', 'deployment']
        }
        
        required_domains = []
        request_lower = request.lower()
        
        for domain, keywords in domain_mapping.items():
            if any(keyword in request_lower for keyword in keywords):
                required_domains.append(domain)
        
        return required_domains
    
    async def generate_personalized_workflow(self, user_id: str, request: str, profile: dict, complexity: dict) -> Dict[str, Any]:
        """Generate a workflow adapted to user's competency profile"""
        
        workflow = {
            'workflow_id': f"adaptive_{user_id}_{datetime.now().isoformat()}",
            'user_id': user_id,
            'request': request,
            'complexity_analysis': complexity,
            'adaptation_strategy': {},
            'phases': [],
            'guidance_level': self._determine_guidance_level(profile, complexity),
            'learning_opportunities': []
        }
        
        strong_domains = [
            domain for domain, data in profile.get('domains', {}).items()
            if data.get('confidence', 0) > 0.7
        ]
        
        weak_domains = [
            domain for domain, data in profile.get('domains', {}).items()
            if data.get('confidence', 0) < 0.5
        ]
        
        workflow['adaptation_strategy'] = {
            'leverage_strengths': strong_domains,
            'provide_support_for': weak_domains,
            'learning_bridges': self._identify_learning_bridges(strong_domains, weak_domains)
        }
        
        if complexity['complexity_level'] in ['complex', 'expert']:
            workflow['phases'] = await self._generate_strategic_phases(request, profile, complexity)
        else:
            workflow['phases'] = await self._generate_standard_phases(request, profile)
        
        workflow['learning_opportunities'] = self._identify_learning_opportunities(
            request, profile, complexity
        )
        
        return workflow
    
    def _determine_guidance_level(self, profile: dict, complexity: dict) -> str:
        """Determine appropriate level of guidance based on user profile and task complexity"""
        avg_confidence = sum(
            data.get('confidence', 0) 
            for data in profile.get('domains', {}).values()
        ) / max(len(profile.get('domains', {})), 1)
        
        if avg_confidence > 0.8 and complexity['complexity_level'] in ['simple', 'moderate']:
            return 'minimal'
        elif avg_confidence > 0.6:
            return 'structured'
        else:
            return 'comprehensive'
    
    def _identify_learning_bridges(self, strong_domains: List[str], weak_domains: List[str]) -> List[Dict[str, str]]:
        """Identify ways to bridge from strong domains to weak domains"""
        bridges = []
        
        bridge_mappings = {
            'cloud_architecture': {
                'data_management': 'Use your infrastructure knowledge to understand database deployment patterns',
                'security_practices': 'Apply your network security concepts to application security'
            },
            'backend_development': {
                'frontend_development': 'Your API design skills help you understand how frontends consume data',
                'data_management': 'Your server-side experience translates well to database operations'
            }
        }
        
        for strong in strong_domains:
            if strong in bridge_mappings:
                for weak in weak_domains:
                    if weak in bridge_mappings[strong]:
                        bridges.append({
                            'from_domain': strong,
                            'to_domain': weak,
                            'bridge_explanation': bridge_mappings[strong][weak]
                        })
        
        return bridges
    
    async def _generate_strategic_phases(self, request: str, profile: dict, complexity: dict) -> List[Dict[str, Any]]:
        """Generate strategic phases for complex requests"""
        return [
            {
                'phase': 'strategic_planning',
                'title': 'Strategic Planning and Architecture',
                'description': 'Define approach and key decisions before implementation',
                'tasks': [
                    'Analyze requirements and constraints',
                    'Design overall architecture',
                    'Identify integration points and dependencies',
                    'Plan implementation phases'
                ]
            },
            {
                'phase': 'foundation_setup',
                'title': 'Foundation and Infrastructure',
                'description': 'Establish core infrastructure and foundational components',
                'tasks': [
                    'Set up development environment',
                    'Configure base infrastructure',
                    'Implement core services',
                    'Establish security framework'
                ]
            },
            {
                'phase': 'core_implementation',
                'title': 'Core Feature Implementation',
                'description': 'Build main functionality and business logic',
                'tasks': [
                    'Implement core business logic',
                    'Build user interfaces',
                    'Integrate external services',
                    'Add comprehensive error handling'
                ]
            }
        ]
    
    async def _generate_standard_phases(self, request: str, profile: dict) -> List[Dict[str, Any]]:
        """Generate standard phases for moderate complexity requests"""
        return [
            {
                'phase': 'setup',
                'title': 'Project Setup',
                'description': 'Initialize project structure and dependencies',
                'tasks': ['Create project structure', 'Configure dependencies', 'Set up development environment']
            },
            {
                'phase': 'implementation',
                'title': 'Implementation',
                'description': 'Build the requested functionality',
                'tasks': ['Implement core features', 'Add error handling', 'Test functionality']
            }
        ]
    
    def _identify_learning_opportunities(self, request: str, profile: dict, complexity: dict) -> List[Dict[str, str]]:
        """Identify learning opportunities within the workflow"""
        opportunities = []
        
        weak_domains = [
            domain for domain, data in profile.get('domains', {}).items()
            if data.get('confidence', 0) < 0.6
        ]
        
        required_domains = self._extract_required_domains(request)
        learning_domains = set(weak_domains) & set(required_domains)
        
        for domain in learning_domains:
            opportunities.append({
                'domain': domain,
                'learning_type': 'hands_on_practice',
                'description': f'Practice {domain} skills through direct implementation in this project'
            })
        
        return opportunities
    
    async def standard_workflow(self, request: str, context: dict = None) -> Dict[str, Any]:
        """Standard workflow for simple requests"""
        return {
            'workflow_type': 'standard',
            'request': request,
            'approach': 'direct_implementation',
            'phases': [
                {
                    'phase': 'implementation',
                    'title': 'Direct Implementation',
                    'description': 'Implement the requested functionality',
                    'tasks': ['Analyze requirements', 'Implement solution', 'Test and validate']
                }
            ]
        }
    
    async def initiate_competency_assessment(self, user_id: str, competency_check: dict) -> Dict[str, Any]:
        """Initiate competency assessment before proceeding with workflow"""
        return {
            'workflow_type': 'competency_assessment',
            'assessment_required': True,
            'assessment_type': competency_check['assessment_type'],
            'gaps': competency_check.get('gaps', []),
            'estimated_time': f"{len(competency_check.get('gaps', []))} minutes",
            'next_step': 'complete_assessment_then_generate_workflow'
        }
