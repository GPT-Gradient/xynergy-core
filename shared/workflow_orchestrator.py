"""
AI Workflow Orchestration System for Xynergy Platform
Implements intelligent workflow management with ML-based optimization and cost prediction.
"""
import os
import json
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import httpx
from concurrent.futures import ThreadPoolExecutor
import numpy as np

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

class ServicePriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class WorkflowStep:
    """Individual workflow step configuration."""
    step_id: str
    service: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    timeout_seconds: int = 300
    retries: int = 3
    priority: ServicePriority = ServicePriority.MEDIUM
    cost_estimate: float = 0.0

@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    max_execution_time: int = 3600
    auto_retry: bool = True
    cost_budget: float = 50.0

@dataclass
class WorkflowExecution:
    """Workflow execution state and results."""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = None
    errors: List[str] = None
    step_results: Dict[str, Any] = None
    total_cost: float = 0.0
    execution_time: float = 0.0

class CostPredictor:
    """ML-based cost prediction for workflow optimization."""

    def __init__(self):
        # Historical cost data for different service types
        self.service_cost_profiles = {
            "ai-intensive": {
                "base_cost": 0.015,
                "per_token": 0.0001,
                "complexity_multiplier": 2.0
            },
            "data-processing": {
                "base_cost": 0.008,
                "per_operation": 0.00005,
                "volume_multiplier": 1.5
            },
            "api-service": {
                "base_cost": 0.002,
                "per_request": 0.00001,
                "latency_factor": 0.1
            }
        }

        # ML model for cost prediction (simplified)
        self.cost_model_weights = np.array([0.3, 0.4, 0.2, 0.1])  # [complexity, volume, latency, service_type]

    def predict_step_cost(self, step: WorkflowStep, context: Dict[str, Any] = None) -> float:
        """Predict cost for a single workflow step."""
        try:
            service_type = self._classify_service_type(step.service)
            profile = self.service_cost_profiles.get(service_type, self.service_cost_profiles["api-service"])

            # Extract features for ML prediction
            complexity = self._calculate_complexity(step.action, step.parameters)
            volume = len(json.dumps(step.parameters))
            latency = step.timeout_seconds / 100
            service_factor = {"ai-intensive": 3, "data-processing": 2, "api-service": 1}[service_type]

            features = np.array([complexity, volume, latency, service_factor])
            ml_multiplier = np.dot(self.cost_model_weights, features) / 10

            base_cost = profile["base_cost"] * ml_multiplier
            return round(base_cost, 6)

        except Exception as e:
            logger.warning(f"Cost prediction failed for {step.step_id}: {e}")
            return 0.01  # Default fallback cost

    def predict_workflow_cost(self, workflow: WorkflowDefinition) -> Dict[str, float]:
        """Predict total cost and breakdown for entire workflow."""
        step_costs = {}
        total_cost = 0.0

        for step in workflow.steps:
            step_cost = self.predict_step_cost(step)
            step_costs[step.step_id] = step_cost
            total_cost += step_cost

        # Add orchestration overhead (5%)
        orchestration_overhead = total_cost * 0.05

        return {
            "step_costs": step_costs,
            "orchestration_overhead": orchestration_overhead,
            "total_predicted_cost": round(total_cost + orchestration_overhead, 4),
            "budget_utilization": round((total_cost / workflow.cost_budget) * 100, 1)
        }

    def _classify_service_type(self, service_name: str) -> str:
        """Classify service by type for cost modeling."""
        if any(keyword in service_name for keyword in ["ai", "ml", "routing", "assistant"]):
            return "ai-intensive"
        elif any(keyword in service_name for keyword in ["analytics", "data", "processing"]):
            return "data-processing"
        else:
            return "api-service"

    def _calculate_complexity(self, action: str, parameters: Dict[str, Any]) -> float:
        """Calculate action complexity score (0-10)."""
        complexity_indicators = {
            "generate": 8, "analyze": 7, "process": 6, "validate": 4,
            "create": 5, "update": 3, "read": 2, "delete": 1
        }

        base_complexity = complexity_indicators.get(action.split("_")[0], 5)
        param_complexity = len(parameters) * 0.5

        return min(base_complexity + param_complexity, 10)

class WorkflowOptimizer:
    """Optimize workflow execution for performance and cost."""

    def __init__(self):
        self.optimization_strategies = {
            "cost": self._optimize_for_cost,
            "speed": self._optimize_for_speed,
            "balanced": self._optimize_balanced
        }

    def optimize_workflow(self, workflow: WorkflowDefinition, strategy: str = "balanced") -> WorkflowDefinition:
        """Optimize workflow based on strategy."""
        optimizer_func = self.optimization_strategies.get(strategy, self._optimize_balanced)
        return optimizer_func(workflow)

    def _optimize_for_cost(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize workflow to minimize cost."""
        # Sort steps by cost (ascending) and adjust priorities
        optimized_steps = []
        for step in sorted(workflow.steps, key=lambda s: s.cost_estimate):
            # Reduce timeouts for cost optimization
            step.timeout_seconds = min(step.timeout_seconds, 180)
            # Lower priority for non-critical steps
            if step.priority.value > 2:
                step.priority = ServicePriority.LOW
            optimized_steps.append(step)

        workflow.steps = optimized_steps
        return workflow

    def _optimize_for_speed(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize workflow for maximum speed."""
        # Identify parallel execution opportunities
        optimized_steps = []
        for step in workflow.steps:
            # Increase timeouts for speed optimization
            step.timeout_seconds = min(step.timeout_seconds * 1.5, 600)
            # Increase priority for faster execution
            if step.priority.value > 1:
                step.priority = ServicePriority.HIGH
            optimized_steps.append(step)

        workflow.steps = optimized_steps
        return workflow

    def _optimize_balanced(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Balance cost and speed optimization."""
        # Find optimal balance between cost and performance
        for step in workflow.steps:
            if step.cost_estimate > 0.05:  # High cost steps
                step.timeout_seconds = min(step.timeout_seconds, 240)
            elif step.priority == ServicePriority.CRITICAL:
                step.timeout_seconds = min(step.timeout_seconds * 1.2, 360)

        return workflow

class WorkflowOrchestrator:
    """Main workflow orchestration engine."""

    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
        self.cost_predictor = CostPredictor()
        self.optimizer = WorkflowOptimizer()

        # Execution tracking
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.completed_executions: List[WorkflowExecution] = []
        self.execution_history: Dict[str, List[float]] = {}  # For cost tracking

        # Service endpoints
        self.service_endpoints = {
            "ai-routing-engine": "https://xynergy-ai-routing-engine-835612502919.us-central1.run.app",
            "analytics-data-layer": "https://xynergy-analytics-data-layer-835612502919.us-central1.run.app",
            "marketing-engine": "https://xynergy-marketing-engine-835612502919.us-central1.run.app",
            "internal-ai-service": "https://xynergy-internal-ai-service-835612502919.us-central1.run.app",
            "system-runtime": "https://xynergy-system-runtime-835612502919.us-central1.run.app",
            "security-governance": "https://xynergy-security-governance-835612502919.us-central1.run.app"
        }

        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=10)

    async def execute_workflow(self, workflow: WorkflowDefinition,
                             optimization_strategy: str = "balanced") -> WorkflowExecution:
        """Execute a complete workflow with optimization."""
        execution_id = f"exec_{int(time.time())}_{workflow.workflow_id}"

        try:
            # Predict and validate costs
            cost_prediction = self.cost_predictor.predict_workflow_cost(workflow)
            if cost_prediction["total_predicted_cost"] > workflow.cost_budget:
                logger.warning(f"Workflow {workflow.workflow_id} exceeds budget: "
                             f"${cost_prediction['total_predicted_cost']:.4f} > ${workflow.cost_budget}")

            # Optimize workflow
            optimized_workflow = self.optimizer.optimize_workflow(workflow, optimization_strategy)

            # Create execution record
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow.workflow_id,
                status=WorkflowStatus.RUNNING,
                started_at=datetime.now(),
                results={},
                errors=[],
                step_results={},
                total_cost=0.0
            )

            self.active_executions[execution_id] = execution

            # Execute workflow steps
            await self._execute_workflow_steps(optimized_workflow, execution)

            # Update execution status
            execution.completed_at = datetime.now()
            execution.execution_time = (execution.completed_at - execution.started_at).total_seconds()
            execution.status = WorkflowStatus.COMPLETED if not execution.errors else WorkflowStatus.FAILED

            # Move to completed executions
            self.completed_executions.append(execution)
            del self.active_executions[execution_id]

            # Update cost tracking
            self._update_cost_history(workflow.workflow_id, execution.total_cost)

            logger.info(f"Workflow {workflow.workflow_id} completed: "
                       f"${execution.total_cost:.4f} in {execution.execution_time:.2f}s")

            return execution

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.errors.append(str(e))
            return execution

    async def _execute_workflow_steps(self, workflow: WorkflowDefinition,
                                    execution: WorkflowExecution):
        """Execute individual workflow steps with dependency resolution."""
        completed_steps = set()
        step_map = {step.step_id: step for step in workflow.steps}

        while len(completed_steps) < len(workflow.steps):
            # Find steps ready to execute (dependencies satisfied)
            ready_steps = []
            for step in workflow.steps:
                if (step.step_id not in completed_steps and
                    all(dep in completed_steps for dep in (step.dependencies or []))):
                    ready_steps.append(step)

            if not ready_steps:
                # Detect circular dependencies
                remaining_steps = [s.step_id for s in workflow.steps if s.step_id not in completed_steps]
                execution.errors.append(f"Circular dependency detected in steps: {remaining_steps}")
                break

            # Execute ready steps in parallel (by priority)
            ready_steps.sort(key=lambda s: s.priority.value)

            # Execute steps concurrently
            tasks = [self._execute_single_step(step, execution) for step in ready_steps[:3]]  # Max 3 concurrent
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for i, result in enumerate(results):
                step = ready_steps[i]
                if isinstance(result, Exception):
                    execution.errors.append(f"Step {step.step_id} failed: {str(result)}")
                    if step.priority == ServicePriority.CRITICAL:
                        break  # Stop execution for critical step failures
                else:
                    completed_steps.add(step.step_id)
                    execution.step_results[step.step_id] = result

    async def _execute_single_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a single workflow step."""
        step_start = time.time()

        try:
            service_url = self.service_endpoints.get(step.service)
            if not service_url:
                raise ValueError(f"Unknown service: {step.service}")

            # Prepare request
            request_data = {
                "action": step.action,
                "parameters": step.parameters,
                "workflow_context": {
                    "execution_id": execution.execution_id,
                    "workflow_id": execution.workflow_id,
                    "step_id": step.step_id
                }
            }

            # Execute with timeout and retries
            async with httpx.AsyncClient(timeout=step.timeout_seconds) as client:
                for attempt in range(step.retries + 1):
                    try:
                        response = await client.post(
                            f"{service_url}/execute",
                            json=request_data,
                            headers={"Authorization": f"Bearer {os.getenv('XYNERGY_API_KEY', '')}"}
                        )

                        if response.status_code == 200:
                            result = response.json()

                            # Track step cost
                            step_cost = self.cost_predictor.predict_step_cost(step)
                            execution.total_cost += step_cost

                            # Add execution metadata
                            result["step_metadata"] = {
                                "execution_time": time.time() - step_start,
                                "cost": step_cost,
                                "attempt": attempt + 1
                            }

                            return result

                        elif attempt < step.retries:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff

                    except httpx.TimeoutException:
                        if attempt < step.retries:
                            await asyncio.sleep(2 ** attempt)
                        else:
                            raise

            raise Exception(f"Step failed after {step.retries + 1} attempts")

        except Exception as e:
            execution.errors.append(f"Step {step.step_id}: {str(e)}")
            raise

    def create_standard_workflows(self) -> Dict[str, WorkflowDefinition]:
        """Create standard Xynergy platform workflows."""
        workflows = {}

        # Content Generation Workflow
        workflows["content_generation"] = WorkflowDefinition(
            workflow_id="content_generation",
            name="AI Content Generation",
            description="Complete content generation with SEO optimization",
            steps=[
                WorkflowStep(
                    step_id="analyze_topic",
                    service="marketing-engine",
                    action="analyze_topic",
                    parameters={"topic": "", "target_audience": ""},
                    priority=ServicePriority.HIGH,
                    timeout_seconds=180
                ),
                WorkflowStep(
                    step_id="generate_content",
                    service="ai-routing-engine",
                    action="generate_content",
                    parameters={"prompt": "", "content_type": "article"},
                    dependencies=["analyze_topic"],
                    priority=ServicePriority.HIGH,
                    timeout_seconds=300
                ),
                WorkflowStep(
                    step_id="validate_content",
                    service="system-runtime",
                    action="validate_content",
                    parameters={"content": "", "quality_threshold": 0.8},
                    dependencies=["generate_content"],
                    priority=ServicePriority.MEDIUM,
                    timeout_seconds=120
                )
            ],
            cost_budget=25.0
        )

        # Analytics Processing Workflow
        workflows["analytics_processing"] = WorkflowDefinition(
            workflow_id="analytics_processing",
            name="Analytics Data Processing",
            description="Process and analyze platform metrics",
            steps=[
                WorkflowStep(
                    step_id="collect_metrics",
                    service="analytics-data-layer",
                    action="collect_metrics",
                    parameters={"time_range": "24h", "services": "all"},
                    priority=ServicePriority.HIGH,
                    timeout_seconds=300
                ),
                WorkflowStep(
                    step_id="generate_insights",
                    service="ai-routing-engine",
                    action="generate_insights",
                    parameters={"data": "", "analysis_type": "performance"},
                    dependencies=["collect_metrics"],
                    priority=ServicePriority.MEDIUM,
                    timeout_seconds=240
                )
            ],
            cost_budget=15.0
        )

        return workflows

    def _update_cost_history(self, workflow_id: str, cost: float):
        """Update cost history for trend analysis."""
        if workflow_id not in self.execution_history:
            self.execution_history[workflow_id] = []

        self.execution_history[workflow_id].append(cost)

        # Keep only last 100 executions
        if len(self.execution_history[workflow_id]) > 100:
            self.execution_history[workflow_id] = self.execution_history[workflow_id][-100:]

    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get comprehensive orchestration statistics."""
        total_executions = len(self.completed_executions)
        successful_executions = sum(1 for ex in self.completed_executions if ex.status == WorkflowStatus.COMPLETED)

        total_cost = sum(ex.total_cost for ex in self.completed_executions)
        avg_execution_time = sum(ex.execution_time for ex in self.completed_executions) / max(total_executions, 1)

        return {
            "orchestration_metrics": {
                "total_executions": total_executions,
                "success_rate": round(successful_executions / max(total_executions, 1) * 100, 1),
                "active_executions": len(self.active_executions),
                "total_cost": round(total_cost, 4),
                "avg_execution_time": round(avg_execution_time, 2)
            },
            "cost_trends": {
                workflow_id: {
                    "avg_cost": round(sum(costs) / len(costs), 4),
                    "min_cost": round(min(costs), 4),
                    "max_cost": round(max(costs), 4),
                    "executions": len(costs)
                }
                for workflow_id, costs in self.execution_history.items()
            },
            "service_utilization": self._calculate_service_utilization(),
            "optimization_recommendations": self._generate_optimization_recommendations()
        }

    def _calculate_service_utilization(self) -> Dict[str, float]:
        """Calculate service utilization statistics."""
        service_usage = {}

        for execution in self.completed_executions:
            for step_id, result in execution.step_results.items():
                service = step_id.split("_")[0]  # Extract service from step_id
                if service not in service_usage:
                    service_usage[service] = 0
                service_usage[service] += 1

        total_steps = sum(service_usage.values())
        return {
            service: round(count / max(total_steps, 1) * 100, 1)
            for service, count in service_usage.items()
        }

    def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on execution history."""
        recommendations = []

        if len(self.completed_executions) < 10:
            recommendations.append("Insufficient data for optimization recommendations")
            return recommendations

        # Analyze cost trends
        total_cost = sum(ex.total_cost for ex in self.completed_executions[-20:])
        if total_cost > 200:
            recommendations.append("Consider implementing more aggressive caching for AI responses")

        # Analyze failure rates
        recent_failures = sum(1 for ex in self.completed_executions[-20:] if ex.status == WorkflowStatus.FAILED)
        if recent_failures > 3:
            recommendations.append("Increase retry limits or implement better circuit breaker policies")

        # Analyze execution times
        avg_time = sum(ex.execution_time for ex in self.completed_executions[-20:]) / 20
        if avg_time > 300:
            recommendations.append("Consider parallel execution optimization for workflow steps")

        return recommendations

# Global orchestrator instance
workflow_orchestrator = WorkflowOrchestrator()

# Convenience functions
async def execute_standard_workflow(workflow_name: str, parameters: Dict[str, Any] = None) -> WorkflowExecution:
    """Execute a standard workflow with custom parameters."""
    workflows = workflow_orchestrator.create_standard_workflows()
    workflow = workflows.get(workflow_name)

    if not workflow:
        raise ValueError(f"Unknown workflow: {workflow_name}")

    # Inject custom parameters
    if parameters:
        for step in workflow.steps:
            step.parameters.update(parameters.get(step.step_id, {}))

    return await workflow_orchestrator.execute_workflow(workflow)

def get_orchestration_dashboard() -> Dict[str, Any]:
    """Get orchestration dashboard data."""
    return workflow_orchestrator.get_orchestration_stats()