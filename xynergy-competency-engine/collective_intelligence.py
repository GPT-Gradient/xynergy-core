"""
collective_intelligence.py
Cross-client learning and shared intelligence system
"""
import json
import hashlib
from typing import Dict, List, Any, Optional
from google.cloud import firestore, bigquery
from datetime import datetime, timedelta
import asyncio

class CollectiveIntelligenceEngine:
    def __init__(self):
        self.db = firestore.Client()
        self.bq_client = bigquery.Client()
        self.dataset_id = 'xynergy_collective_intelligence'
        self.patterns_table = 'learning_patterns'
        self.insights_table = 'collective_insights'
        self.MAX_PATTERNS_PER_TYPE = 100
    
    async def process_interaction(self, client_id: str, user_id: str, interaction: dict) -> Dict[str, Any]:
        """Process user interaction and extract patterns for collective learning"""
        try:
            patterns = await self.extract_anonymized_patterns(interaction, client_id)
            await self.store_interaction_patterns(patterns)
            insights = await self.get_relevant_insights(user_id, interaction)
            await self.update_global_intelligence(patterns)
            
            return {
                'patterns_extracted': len(patterns),
                'relevant_insights': insights,
                'contribution_to_collective': True
            }
        except Exception as e:
            print(f"Error processing interaction: {e}")
            return {
                'patterns_extracted': 0,
                'relevant_insights': [],
                'contribution_to_collective': False,
                'error': str(e)
            }
    
    async def extract_anonymized_patterns(self, interaction: dict, client_id: str) -> List[Dict[str, Any]]:
        """Extract patterns from interaction while preserving privacy"""
        patterns = []
        
        if 'task_complexity' in interaction:
            patterns.append({
                'pattern_type': 'task_complexity',
                'complexity_level': interaction['task_complexity'].get('complexity_level'),
                'domains_involved': interaction['task_complexity'].get('domains_involved', []),
                'success_outcome': interaction.get('success', False),
                'client_category': self._categorize_client(client_id),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        if 'competency_assessment' in interaction:
            assessment = interaction['competency_assessment']
            if assessment.get('gaps'):
                patterns.append({
                    'pattern_type': 'competency_gaps',
                    'gap_domains': assessment['gaps'],
                    'assessment_duration': assessment.get('duration_minutes', 0),
                    'completion_rate': assessment.get('completion_rate', 0),
                    'client_category': self._categorize_client(client_id),
                    'timestamp': datetime.utcnow().isoformat()
                })
        
        if 'workflow_execution' in interaction:
            workflow = interaction['workflow_execution']
            patterns.append({
                'pattern_type': 'workflow_effectiveness',
                'workflow_type': workflow.get('type'),
                'guidance_level': workflow.get('guidance_level'),
                'completion_rate': workflow.get('completion_rate', 0),
                'user_satisfaction': workflow.get('satisfaction_score', 0),
                'time_to_completion': workflow.get('duration_minutes', 0),
                'client_category': self._categorize_client(client_id),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return patterns
    
    def _categorize_client(self, client_id: str) -> str:
        """Categorize client for pattern analysis while maintaining privacy"""
        client_hash = hashlib.sha256(f"{client_id}_salt".encode()).hexdigest()
        categories = ['startup', 'enterprise', 'consulting', 'education', 'government']
        category_index = int(client_hash[:2], 16) % len(categories)
        return categories[category_index]
    
    async def store_interaction_patterns(self, patterns: List[Dict[str, Any]]):
        """Store patterns in BigQuery for collective analysis"""
        if not patterns:
            return
        
        try:
            table_ref = self.bq_client.dataset(self.dataset_id).table(self.patterns_table)
            
            rows_to_insert = []
            for pattern in patterns:
                row = {
                    'pattern_id': hashlib.sha256(json.dumps(pattern, sort_keys=True).encode()).hexdigest(),
                    'pattern_type': pattern['pattern_type'],
                    'pattern_data': json.dumps(pattern),
                    'client_category': pattern.get('client_category', 'unknown'),
                    'created_at': pattern['timestamp']
                }
                rows_to_insert.append(row)
            
            errors = self.bq_client.insert_rows_json(table_ref, rows_to_insert)
            if errors:
                print(f"Error inserting patterns: {errors}")
        except Exception as e:
            print(f"Error storing patterns: {e}")
    
    async def get_relevant_insights(self, user_id: str, interaction: dict) -> List[Dict[str, Any]]:
        """Get collective insights relevant to current user interaction"""
        insights = []
        
        try:
            profile_ref = self.db.collection('user_competency_profiles').document(user_id)
            profile_doc = await profile_ref.get()
            
            if not profile_doc.exists:
                return insights
            
            profile = profile_doc.to_dict()
            user_domains = list(profile.get('domains', {}).keys())
            
            query = f"""
            SELECT 
                insight_type,
                insight_data,
                effectiveness_score,
                sample_size
            FROM `{self.dataset_id}.{self.insights_table}`
            WHERE domains_applicable && @user_domains
            AND effectiveness_score > 0.7
            AND sample_size > 10
            ORDER BY effectiveness_score DESC
            LIMIT 100
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ArrayQueryParameter("user_domains", "STRING", user_domains)
                ]
            )
            
            query_job = self.bq_client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                insights.append({
                    'type': row.insight_type,
                    'data': json.loads(row.insight_data),
                    'effectiveness': row.effectiveness_score,
                    'confidence': min(row.sample_size / 100, 1.0)
                })
        except Exception as e:
            print(f"Error querying insights: {e}")
        
        return insights
    
    async def update_global_intelligence(self, patterns: List[Dict[str, Any]]):
        """Update global intelligence based on new patterns with memory optimization"""
        if not patterns:
            return
        
        pattern_aggregations = {}
        
        for pattern in patterns:
            pattern_type = pattern['pattern_type']
            if pattern_type not in pattern_aggregations:
                pattern_aggregations[pattern_type] = []
            pattern_aggregations[pattern_type].append(pattern)
        
        for pattern_type, pattern_list in pattern_aggregations.items():
            if len(pattern_list) > self.MAX_PATTERNS_PER_TYPE:
                pattern_list = pattern_list[-self.MAX_PATTERNS_PER_TYPE:]
            
            await self._process_pattern_type_for_insights(pattern_type, pattern_list)
    
    async def _process_pattern_type_for_insights(self, pattern_type: str, patterns: List[Dict[str, Any]]):
        """Process specific pattern type to generate collective insights"""
        try:
            if pattern_type == 'workflow_effectiveness':
                await self._analyze_workflow_patterns(patterns)
            elif pattern_type == 'competency_gaps':
                await self._analyze_competency_patterns(patterns)
            elif pattern_type == 'task_complexity':
                await self._analyze_complexity_patterns(patterns)
        except Exception as e:
            print(f"Error processing pattern type {pattern_type}: {e}")
    
    async def _analyze_workflow_patterns(self, patterns: List[Dict[str, Any]]):
        """Analyze workflow patterns with memory optimization"""
        effectiveness_by_guidance = {}
        
        for pattern in patterns:
            guidance_level = pattern.get('guidance_level', 'unknown')
            workflow_type = pattern.get('workflow_type', 'unknown')
            completion_rate = pattern.get('completion_rate', 0)
            satisfaction = pattern.get('user_satisfaction', 0)
            
            key = f"{guidance_level}_{workflow_type}"
            if key not in effectiveness_by_guidance:
                effectiveness_by_guidance[key] = {
                    'completion_rates': [],
                    'satisfaction_scores': [],
                    'sample_count': 0
                }
            
            effectiveness_by_guidance[key]['completion_rates'].append(completion_rate)
            effectiveness_by_guidance[key]['satisfaction_scores'].append(satisfaction)
            effectiveness_by_guidance[key]['sample_count'] += 1
            
            if len(effectiveness_by_guidance[key]['completion_rates']) > 50:
                effectiveness_by_guidance[key]['completion_rates'] = effectiveness_by_guidance[key]['completion_rates'][-50:]
            if len(effectiveness_by_guidance[key]['satisfaction_scores']) > 50:
                effectiveness_by_guidance[key]['satisfaction_scores'] = effectiveness_by_guidance[key]['satisfaction_scores'][-50:]
        
        insights = []
        for key, data in effectiveness_by_guidance.items():
            if data['sample_count'] >= 5:
                avg_completion = sum(data['completion_rates']) / len(data['completion_rates'])
                avg_satisfaction = sum(data['satisfaction_scores']) / len(data['satisfaction_scores'])
                
                if avg_completion > 0.8 and avg_satisfaction > 0.7:
                    guidance_level, workflow_type = key.split('_', 1)
                    insights.append({
                        'insight_type': 'effective_workflow_pattern',
                        'guidance_level': guidance_level,
                        'workflow_type': workflow_type,
                        'effectiveness_score': (avg_completion + avg_satisfaction) / 2,
                        'sample_size': data['sample_count'],
                        'recommendation': f"Use {guidance_level} guidance for {workflow_type} workflows"
                    })
        
        await self._store_collective_insights(insights)
    
    async def _analyze_competency_patterns(self, patterns: List[Dict[str, Any]]):
        """Analyze competency gap patterns with memory optimization"""
        gap_combinations = {}
        
        for pattern in patterns:
            gaps = sorted(pattern.get('gap_domains', []))
            completion_rate = pattern.get('completion_rate', 0)
            
            gap_key = '_'.join(gaps)
            if gap_key not in gap_combinations:
                gap_combinations[gap_key] = {
                    'completion_rates': [],
                    'durations': [],
                    'sample_count': 0
                }
            
            gap_combinations[gap_key]['completion_rates'].append(completion_rate)
            gap_combinations[gap_key]['durations'].append(pattern.get('assessment_duration', 0))
            gap_combinations[gap_key]['sample_count'] += 1
            
            if len(gap_combinations[gap_key]['completion_rates']) > 30:
                gap_combinations[gap_key]['completion_rates'] = gap_combinations[gap_key]['completion_rates'][-30:]
            if len(gap_combinations[gap_key]['durations']) > 30:
                gap_combinations[gap_key]['durations'] = gap_combinations[gap_key]['durations'][-30:]
        
        insights = []
        for gap_combo, data in gap_combinations.items():
            if data['sample_count'] >= 3:
                avg_completion = sum(data['completion_rates']) / len(data['completion_rates'])
                avg_duration = sum(data['durations']) / len(data['durations'])
                
                if avg_completion > 0.7:
                    insights.append({
                        'insight_type': 'effective_gap_remediation',
                        'gap_combination': gap_combo.split('_'),
                        'effectiveness_score': avg_completion,
                        'optimal_duration': avg_duration,
                        'sample_size': data['sample_count'],
                        'recommendation': f"Address {gap_combo.replace('_', ' and ')} gaps together for optimal results"
                    })
        
        await self._store_collective_insights(insights)
    
    async def _analyze_complexity_patterns(self, patterns: List[Dict[str, Any]]):
        """Analyze task complexity patterns with memory optimization"""
        complexity_success = {}
        
        for pattern in patterns:
            complexity_level = pattern.get('complexity_level')
            domains = tuple(sorted(pattern.get('domains_involved', [])))
            success = pattern.get('success_outcome', False)
            
            key = f"{complexity_level}_{len(domains)}domains"
            if key not in complexity_success:
                complexity_success[key] = {
                    'success_count': 0,
                    'total_count': 0,
                    'domain_combinations': []
                }
            
            complexity_success[key]['total_count'] += 1
            if success:
                complexity_success[key]['success_count'] += 1
            complexity_success[key]['domain_combinations'].append(domains)
            
            if len(complexity_success[key]['domain_combinations']) > 25:
                complexity_success[key]['domain_combinations'] = complexity_success[key]['domain_combinations'][-25:]
        
        insights = []
        for key, data in complexity_success.items():
            if data['total_count'] >= 5:
                success_rate = data['success_count'] / data['total_count']
                
                if success_rate > 0.8 or success_rate < 0.5:
                    complexity_level, domain_info = key.split('_')
                    insights.append({
                        'insight_type': 'complexity_assessment_accuracy',
                        'complexity_level': complexity_level,
                        'domain_count': domain_info,
                        'success_rate': success_rate,
                        'sample_size': data['total_count'],
                        'recommendation': f"{'Continue' if success_rate > 0.8 else 'Adjust'} complexity assessment for {complexity_level} tasks"
                    })
        
        await self._store_collective_insights(insights)
    
    async def _store_collective_insights(self, insights: List[Dict[str, Any]]):
        """Store generated insights in BigQuery for future use"""
        if not insights:
            return
        
        try:
            table_ref = self.bq_client.dataset(self.dataset_id).table(self.insights_table)
            
            rows_to_insert = []
            for insight in insights:
                row = {
                    'insight_id': hashlib.sha256(json.dumps(insight, sort_keys=True).encode()).hexdigest(),
                    'insight_type': insight['insight_type'],
                    'insight_data': json.dumps(insight),
                    'effectiveness_score': insight.get('effectiveness_score', 0),
                    'sample_size': insight.get('sample_size', 0),
                    'domains_applicable': self._extract_domains_from_insight(insight),
                    'created_at': datetime.utcnow().isoformat(),
                    'last_updated': datetime.utcnow().isoformat()
                }
                rows_to_insert.append(row)
            
            errors = self.bq_client.insert_rows_json(table_ref, rows_to_insert)
            if errors:
                print(f"Error inserting insights: {errors}")
        except Exception as e:
            print(f"Error storing insights: {e}")
    
    def _extract_domains_from_insight(self, insight: Dict[str, Any]) -> List[str]:
        """Extract applicable domains from insight for querying"""
        domains = []
        
        if 'from_domain' in insight:
            domains.append(insight['from_domain'])
        if 'to_domain' in insight:
            domains.append(insight['to_domain'])
        if 'gap_combination' in insight:
            domains.extend(insight['gap_combination'])
        
        return list(set(domains))
    
    async def get_platform_intelligence_summary(self) -> Dict[str, Any]:
        """Get summary of collective intelligence for platform monitoring"""
        try:
            query = f"""
            SELECT 
                insight_type,
                COUNT(*) as insight_count,
                AVG(effectiveness_score) as avg_effectiveness,
                SUM(sample_size) as total_samples
            FROM `{self.dataset_id}.{self.insights_table}`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            GROUP BY insight_type
            ORDER BY insight_count DESC
            LIMIT 50
            """
            
            insights_summary = []
            query_job = self.bq_client.query(query)
            results = query_job.result()
            
            for row in results:
                insights_summary.append({
                    'type': row.insight_type,
                    'count': row.insight_count,
                    'avg_effectiveness': float(row.avg_effectiveness) if row.avg_effectiveness else 0,
                    'total_samples': row.total_samples
                })
            
            return {
                'recent_insights': insights_summary,
                'total_insight_types': len(insights_summary),
                'platform_learning_active': len(insights_summary) > 0,
                'generated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error querying insights summary: {e}")
            return {
                'recent_insights': [],
                'total_insight_types': 0,
                'platform_learning_active': False,
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }
