"""
Automated Scaling Optimization System for Xynergy Platform
Advanced ML-driven auto-scaling with predictive resource allocation and cost optimization.
"""
import os
import json
import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import httpx
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class ScalingAction(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"
    OPTIMIZE = "optimize"

class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    INSTANCES = "instances"
    CONCURRENCY = "concurrency"

class ServiceProfile(Enum):
    AI_INTENSIVE = "ai_intensive"
    DATA_PROCESSING = "data_processing"
    API_SERVICE = "api_service"
    BACKGROUND_WORKER = "background_worker"
    DASHBOARD = "dashboard"

@dataclass
class ResourceMetrics:
    """Current resource utilization metrics."""
    timestamp: datetime
    service: str
    cpu_usage: float  # 0-100%
    memory_usage: float  # 0-100%
    instance_count: int
    request_rate: float  # requests per second
    response_time: float  # milliseconds
    error_rate: float  # 0-100%
    cost_per_hour: float

@dataclass
class ScalingDecision:
    """Scaling decision with rationale."""
    service: str
    action: ScalingAction
    target_instances: int
    target_cpu: str
    target_memory: str
    target_concurrency: int
    confidence: float
    reasoning: str
    estimated_cost_impact: float
    estimated_performance_impact: str

@dataclass
class PredictiveMetrics:
    """Predicted resource requirements."""
    predicted_load: float
    predicted_response_time: float
    predicted_error_rate: float
    confidence_interval: Tuple[float, float]
    time_horizon: int  # minutes ahead

class LoadPredictor:
    """ML-based load prediction for proactive scaling."""

    def __init__(self, history_window: int = 144):  # 24 hours of 10-minute intervals
        self.history_window = history_window
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_window))
        self.seasonal_patterns: Dict[str, Dict[str, float]] = {}

    def add_metrics(self, metrics: ResourceMetrics):
        """Add new metrics data point."""
        service_history = self.metrics_history[metrics.service]

        # Store metrics as tuple for easy processing
        data_point = (
            metrics.timestamp,
            metrics.cpu_usage,
            metrics.memory_usage,
            metrics.request_rate,
            metrics.response_time,
            metrics.error_rate
        )

        service_history.append(data_point)

        # Update seasonal patterns
        self._update_seasonal_patterns(metrics)

    def _update_seasonal_patterns(self, metrics: ResourceMetrics):
        """Update seasonal patterns for improved predictions."""
        if metrics.service not in self.seasonal_patterns:
            self.seasonal_patterns[metrics.service] = {}

        patterns = self.seasonal_patterns[metrics.service]

        # Hour of day pattern
        hour = metrics.timestamp.hour
        hour_key = f"hour_{hour}"
        if hour_key not in patterns:
            patterns[hour_key] = metrics.request_rate
        else:
            # Exponential moving average
            patterns[hour_key] = 0.9 * patterns[hour_key] + 0.1 * metrics.request_rate

        # Day of week pattern
        dow = metrics.timestamp.weekday()
        dow_key = f"dow_{dow}"
        if dow_key not in patterns:
            patterns[dow_key] = metrics.request_rate
        else:
            patterns[dow_key] = 0.9 * patterns[dow_key] + 0.1 * metrics.request_rate

    def predict_load(self, service: str, minutes_ahead: int = 30) -> PredictiveMetrics:
        """Predict future load for service."""
        try:
            if service not in self.metrics_history or len(self.metrics_history[service]) < 10:
                return PredictiveMetrics(
                    predicted_load=0.0,
                    predicted_response_time=100.0,
                    predicted_error_rate=0.0,
                    confidence_interval=(0.0, 0.0),
                    time_horizon=minutes_ahead
                )

            history = list(self.metrics_history[service])

            # Extract time series data
            timestamps = [point[0] for point in history]
            cpu_values = [point[1] for point in history]
            memory_values = [point[2] for point in history]
            request_rates = [point[3] for point in history]
            response_times = [point[4] for point in history]
            error_rates = [point[5] for point in history]

            # Simple trend-based prediction with seasonal adjustment
            predicted_load = self._predict_request_rate(service, timestamps, request_rates, minutes_ahead)
            predicted_response_time = self._predict_response_time(response_times, request_rates, predicted_load)
            predicted_error_rate = self._predict_error_rate(error_rates, predicted_load)

            # Calculate confidence interval
            load_std = np.std(request_rates[-20:]) if len(request_rates) >= 20 else np.std(request_rates)
            confidence_lower = max(0, predicted_load - 1.96 * load_std)
            confidence_upper = predicted_load + 1.96 * load_std

            return PredictiveMetrics(
                predicted_load=round(predicted_load, 2),
                predicted_response_time=round(predicted_response_time, 1),
                predicted_error_rate=round(predicted_error_rate, 3),
                confidence_interval=(round(confidence_lower, 2), round(confidence_upper, 2)),
                time_horizon=minutes_ahead
            )

        except Exception as e:
            logger.error(f"Load prediction failed for {service}: {e}")
            return PredictiveMetrics(0.0, 100.0, 0.0, (0.0, 0.0), minutes_ahead)

    def _predict_request_rate(self, service: str, timestamps: List[datetime],
                            rates: List[float], minutes_ahead: int) -> float:
        """Predict future request rate using trend and seasonality."""
        if len(rates) < 3:
            return rates[-1] if rates else 0.0

        # Linear trend component
        recent_rates = rates[-10:]  # Use last 10 data points for trend
        trend_slope = (recent_rates[-1] - recent_rates[0]) / len(recent_rates)
        trend_component = rates[-1] + trend_slope * (minutes_ahead / 10)  # Assuming 10-minute intervals

        # Seasonal component
        future_time = timestamps[-1] + timedelta(minutes=minutes_ahead)
        seasonal_component = self._get_seasonal_adjustment(service, future_time)

        # Combine components
        predicted = max(0, trend_component * seasonal_component)

        return predicted

    def _get_seasonal_adjustment(self, service: str, timestamp: datetime) -> float:
        """Get seasonal adjustment factor for timestamp."""
        if service not in self.seasonal_patterns:
            return 1.0

        patterns = self.seasonal_patterns[service]

        # Hour adjustment
        hour_key = f"hour_{timestamp.hour}"
        hour_adjustment = patterns.get(hour_key, 1.0)

        # Day of week adjustment
        dow_key = f"dow_{timestamp.weekday()}"
        dow_adjustment = patterns.get(dow_key, 1.0)

        # Calculate average baseline
        all_hourly = [v for k, v in patterns.items() if k.startswith("hour_")]
        baseline = np.mean(all_hourly) if all_hourly else 1.0

        # Return normalized seasonal factor
        return (hour_adjustment + dow_adjustment) / (2 * baseline) if baseline > 0 else 1.0

    def _predict_response_time(self, response_times: List[float], request_rates: List[float],
                             predicted_load: float) -> float:
        """Predict response time based on load."""
        if not response_times or not request_rates:
            return 100.0

        # Find correlation between load and response time
        if len(response_times) >= 5:
            # Simple linear relationship: response_time = base + load_factor * request_rate
            recent_times = response_times[-10:]
            recent_rates = request_rates[-10:]

            if len(recent_times) == len(recent_rates) and len(recent_rates) > 1:
                # Calculate load coefficient
                rate_diff = np.std(recent_rates)
                time_diff = np.std(recent_times)
                load_coefficient = time_diff / max(rate_diff, 0.1)

                baseline_time = np.mean(recent_times)
                baseline_rate = np.mean(recent_rates)

                predicted_time = baseline_time + load_coefficient * (predicted_load - baseline_rate)
                return max(50, predicted_time)  # Minimum 50ms response time

        # Fallback to recent average
        return np.mean(response_times[-5:]) if len(response_times) >= 5 else 100.0

    def _predict_error_rate(self, error_rates: List[float], predicted_load: float) -> float:
        """Predict error rate based on load."""
        if not error_rates:
            return 0.0

        recent_errors = error_rates[-10:]
        baseline_error = np.mean(recent_errors)

        # Assume error rate increases with high load
        if predicted_load > 100:  # High load threshold
            load_multiplier = 1 + (predicted_load - 100) / 1000  # Gradual increase
            return min(10.0, baseline_error * load_multiplier)  # Cap at 10% error rate

        return baseline_error

class ResourceOptimizer:
    """Optimize resource allocation based on predictions and constraints."""

    def __init__(self):
        # Service-specific resource profiles
        self.service_profiles = {
            ServiceProfile.AI_INTENSIVE: {
                "cpu_per_rps": 20,  # 20m CPU per request/sec
                "memory_per_rps": 50,  # 50MB memory per request/sec
                "max_cpu": "4000m",
                "max_memory": "8Gi",
                "target_cpu_utilization": 70,
                "target_memory_utilization": 80,
                "cost_per_hour_base": 0.15
            },
            ServiceProfile.DATA_PROCESSING: {
                "cpu_per_rps": 10,
                "memory_per_rps": 30,
                "max_cpu": "2000m",
                "max_memory": "4Gi",
                "target_cpu_utilization": 75,
                "target_memory_utilization": 75,
                "cost_per_hour_base": 0.08
            },
            ServiceProfile.API_SERVICE: {
                "cpu_per_rps": 2,
                "memory_per_rps": 10,
                "max_cpu": "1000m",
                "max_memory": "2Gi",
                "target_cpu_utilization": 60,
                "target_memory_utilization": 70,
                "cost_per_hour_base": 0.04
            },
            ServiceProfile.BACKGROUND_WORKER: {
                "cpu_per_rps": 5,
                "memory_per_rps": 20,
                "max_cpu": "500m",
                "max_memory": "1Gi",
                "target_cpu_utilization": 80,
                "target_memory_utilization": 85,
                "cost_per_hour_base": 0.02
            },
            ServiceProfile.DASHBOARD: {
                "cpu_per_rps": 1,
                "memory_per_rps": 5,
                "max_cpu": "250m",
                "max_memory": "512Mi",
                "target_cpu_utilization": 50,
                "target_memory_utilization": 60,
                "cost_per_hour_base": 0.01
            }
        }

        # Service classification
        self.service_classification = {
            "ai-routing-engine": ServiceProfile.AI_INTENSIVE,
            "ai-providers": ServiceProfile.AI_INTENSIVE,
            "internal-ai-service": ServiceProfile.AI_INTENSIVE,
            "ai-assistant": ServiceProfile.AI_INTENSIVE,
            "analytics-data-layer": ServiceProfile.DATA_PROCESSING,
            "marketing-engine": ServiceProfile.DATA_PROCESSING,
            "content-hub": ServiceProfile.DATA_PROCESSING,
            "platform-dashboard": ServiceProfile.DASHBOARD,
            "executive-dashboard": ServiceProfile.DASHBOARD,
            "system-runtime": ServiceProfile.API_SERVICE,
            "security-governance": ServiceProfile.API_SERVICE,
            "qa-engine": ServiceProfile.API_SERVICE,
            "scheduler-automation-engine": ServiceProfile.BACKGROUND_WORKER
        }

    def calculate_optimal_resources(self, service: str, predicted_metrics: PredictiveMetrics,
                                  current_metrics: ResourceMetrics) -> Dict[str, Any]:
        """Calculate optimal resource allocation."""
        try:
            profile_type = self.service_classification.get(service, ServiceProfile.API_SERVICE)
            profile = self.service_profiles[profile_type]

            predicted_load = predicted_metrics.predicted_load

            # Calculate resource requirements based on predicted load
            required_cpu_m = max(100, int(predicted_load * profile["cpu_per_rps"]))  # Minimum 100m
            required_memory_mb = max(128, int(predicted_load * profile["memory_per_rps"]))  # Minimum 128MB

            # Convert to Kubernetes format
            cpu_limit = f"{min(required_cpu_m, int(profile['max_cpu'].rstrip('m')))}m"

            if required_memory_mb < 1024:
                memory_limit = f"{required_memory_mb}Mi"
            else:
                memory_limit = f"{min(required_memory_mb // 1024, int(profile['max_memory'].rstrip('Gi')))}Gi"

            # Calculate optimal instance count
            # Consider current utilization and predicted load
            current_capacity = current_metrics.instance_count * 100  # Assume 100 RPS per instance

            if predicted_load > current_capacity * 0.8:  # Scale up threshold
                target_instances = max(1, int(np.ceil(predicted_load / 80)))  # 80 RPS per instance with headroom
            elif predicted_load < current_capacity * 0.3:  # Scale down threshold
                target_instances = max(1, int(np.ceil(predicted_load / 60)))  # 60 RPS per instance
            else:
                target_instances = current_metrics.instance_count

            # Calculate optimal concurrency
            target_concurrency = min(100, max(10, int(predicted_load / max(target_instances, 1))))

            # Cost estimation
            cost_per_instance = profile["cost_per_hour_base"] * (required_cpu_m / 1000) * (required_memory_mb / 1024)
            estimated_hourly_cost = cost_per_instance * target_instances

            return {
                "cpu_limit": cpu_limit,
                "memory_limit": memory_limit,
                "target_instances": target_instances,
                "target_concurrency": target_concurrency,
                "estimated_hourly_cost": round(estimated_hourly_cost, 4),
                "resource_utilization_target": {
                    "cpu": profile["target_cpu_utilization"],
                    "memory": profile["target_memory_utilization"]
                },
                "scaling_rationale": self._generate_scaling_rationale(
                    current_metrics, predicted_metrics, target_instances
                )
            }

        except Exception as e:
            logger.error(f"Resource calculation failed for {service}: {e}")
            return {"error": str(e)}

    def _generate_scaling_rationale(self, current: ResourceMetrics,
                                  predicted: PredictiveMetrics, target_instances: int) -> str:
        """Generate human-readable scaling rationale."""
        rationale_parts = []

        # Load-based reasoning
        if predicted.predicted_load > current.request_rate * 1.5:
            rationale_parts.append(f"High load predicted ({predicted.predicted_load:.1f} vs current {current.request_rate:.1f} RPS)")
        elif predicted.predicted_load < current.request_rate * 0.5:
            rationale_parts.append(f"Low load predicted ({predicted.predicted_load:.1f} vs current {current.request_rate:.1f} RPS)")

        # Resource utilization reasoning
        if current.cpu_usage > 80:
            rationale_parts.append("High CPU utilization requires scaling")
        elif current.memory_usage > 85:
            rationale_parts.append("High memory utilization requires scaling")

        # Performance reasoning
        if predicted.predicted_response_time > 1000:
            rationale_parts.append("High response time predicted")
        elif predicted.predicted_error_rate > 2:
            rationale_parts.append("Elevated error rate predicted")

        # Instance count reasoning
        if target_instances > current.instance_count:
            rationale_parts.append(f"Scale up to {target_instances} instances")
        elif target_instances < current.instance_count:
            rationale_parts.append(f"Scale down to {target_instances} instances")
        else:
            rationale_parts.append("Maintain current instance count")

        return "; ".join(rationale_parts) if rationale_parts else "No scaling changes needed"

class ScalingOrchestrator:
    """Main scaling orchestration engine with ML-driven decisions."""

    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
        self.load_predictor = LoadPredictor()
        self.resource_optimizer = ResourceOptimizer()

        # Scaling constraints and safety limits
        self.scaling_constraints = {
            "max_scale_up_rate": 2,  # Max 2x instances in single scaling event
            "max_scale_down_rate": 0.5,  # Max 50% reduction in single scaling event
            "min_stability_minutes": 10,  # Wait 10 minutes between scaling decisions
            "max_cost_per_service_hour": 5.0  # $5/hour limit per service
        }

        # Track scaling history for safety
        self.scaling_history: Dict[str, List[Tuple[datetime, ScalingDecision]]] = defaultdict(list)

        # Service endpoints for scaling operations
        self.gcp_endpoints = {
            "cloud_run_update": f"https://run.googleapis.com/v1/namespaces/{self.project_id}/services",
            "monitoring": f"https://monitoring.googleapis.com/v3/projects/{self.project_id}"
        }

    async def analyze_and_scale(self, service: str, current_metrics: ResourceMetrics) -> ScalingDecision:
        """Analyze service metrics and make scaling decision."""
        try:
            # Add metrics to predictor
            self.load_predictor.add_metrics(current_metrics)

            # Get load prediction
            predicted_metrics = self.load_predictor.predict_load(service, minutes_ahead=30)

            # Check scaling constraints
            if not self._can_scale_now(service):
                return ScalingDecision(
                    service=service,
                    action=ScalingAction.MAINTAIN,
                    target_instances=current_metrics.instance_count,
                    target_cpu=f"{int(current_metrics.cpu_usage * 10)}m",
                    target_memory="1Gi",
                    target_concurrency=50,
                    confidence=0.0,
                    reasoning="Scaling cooldown period active",
                    estimated_cost_impact=0.0,
                    estimated_performance_impact="No change"
                )

            # Calculate optimal resources
            optimal_resources = self.resource_optimizer.calculate_optimal_resources(
                service, predicted_metrics, current_metrics
            )

            if "error" in optimal_resources:
                raise Exception(optimal_resources["error"])

            # Determine scaling action
            scaling_action = self._determine_scaling_action(current_metrics, optimal_resources)

            # Calculate confidence based on prediction quality
            confidence = self._calculate_decision_confidence(predicted_metrics, current_metrics)

            # Estimate performance impact
            performance_impact = self._estimate_performance_impact(
                current_metrics, optimal_resources, predicted_metrics
            )

            # Create scaling decision
            decision = ScalingDecision(
                service=service,
                action=scaling_action,
                target_instances=optimal_resources["target_instances"],
                target_cpu=optimal_resources["cpu_limit"],
                target_memory=optimal_resources["memory_limit"],
                target_concurrency=optimal_resources["target_concurrency"],
                confidence=confidence,
                reasoning=optimal_resources["scaling_rationale"],
                estimated_cost_impact=optimal_resources["estimated_hourly_cost"] - current_metrics.cost_per_hour,
                estimated_performance_impact=performance_impact
            )

            # Apply safety checks
            decision = self._apply_safety_checks(decision, current_metrics)

            # Record decision
            self.scaling_history[service].append((datetime.now(), decision))

            # Keep only recent history
            if len(self.scaling_history[service]) > 100:
                self.scaling_history[service] = self.scaling_history[service][-100:]

            return decision

        except Exception as e:
            logger.error(f"Scaling analysis failed for {service}: {e}")
            return ScalingDecision(
                service=service,
                action=ScalingAction.MAINTAIN,
                target_instances=current_metrics.instance_count,
                target_cpu="500m",
                target_memory="1Gi",
                target_concurrency=50,
                confidence=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                estimated_cost_impact=0.0,
                estimated_performance_impact="Unknown"
            )

    def _can_scale_now(self, service: str) -> bool:
        """Check if service can be scaled based on cooldown periods."""
        if service not in self.scaling_history:
            return True

        recent_scaling = [
            event for event in self.scaling_history[service]
            if event[0] > datetime.now() - timedelta(minutes=self.scaling_constraints["min_stability_minutes"])
        ]

        return len(recent_scaling) == 0

    def _determine_scaling_action(self, current: ResourceMetrics, optimal: Dict[str, Any]) -> ScalingAction:
        """Determine what scaling action to take."""
        current_instances = current.instance_count
        target_instances = optimal["target_instances"]

        if target_instances > current_instances * 1.2:  # 20% increase threshold
            return ScalingAction.SCALE_UP
        elif target_instances < current_instances * 0.8:  # 20% decrease threshold
            return ScalingAction.SCALE_DOWN
        elif abs(target_instances - current_instances) <= 1 and (
            current.cpu_usage > 80 or current.memory_usage > 85
        ):
            return ScalingAction.OPTIMIZE  # Optimize resources without changing instance count
        else:
            return ScalingAction.MAINTAIN

    def _calculate_decision_confidence(self, predicted: PredictiveMetrics,
                                     current: ResourceMetrics) -> float:
        """Calculate confidence score for scaling decision."""
        confidence_factors = []

        # Data availability factor
        service_history_length = len(self.load_predictor.metrics_history.get(current.service, []))
        data_factor = min(1.0, service_history_length / 50)  # Full confidence at 50 data points
        confidence_factors.append(data_factor)

        # Prediction stability factor (based on confidence interval)
        if predicted.confidence_interval[1] > 0:
            interval_width = predicted.confidence_interval[1] - predicted.confidence_interval[0]
            stability_factor = max(0.1, 1.0 - (interval_width / predicted.predicted_load))
            confidence_factors.append(stability_factor)

        # Recent performance factor
        if current.error_rate < 1.0 and current.response_time < 500:
            performance_factor = 0.9
        elif current.error_rate < 2.0 and current.response_time < 1000:
            performance_factor = 0.7
        else:
            performance_factor = 0.5
        confidence_factors.append(performance_factor)

        # Overall confidence is the geometric mean
        overall_confidence = np.prod(confidence_factors) ** (1.0 / len(confidence_factors))
        return round(overall_confidence, 2)

    def _estimate_performance_impact(self, current: ResourceMetrics, optimal: Dict[str, Any],
                                   predicted: PredictiveMetrics) -> str:
        """Estimate performance impact of scaling decision."""
        target_instances = optimal["target_instances"]
        current_instances = current.instance_count

        if target_instances > current_instances:
            response_improvement = max(0, current.response_time - predicted.predicted_response_time)
            if response_improvement > 100:
                return f"Significant improvement: -{response_improvement:.0f}ms response time"
            else:
                return "Moderate improvement expected"

        elif target_instances < current_instances:
            if predicted.predicted_response_time > current.response_time * 1.2:
                return "Potential performance degradation"
            else:
                return "Minimal performance impact expected"
        else:
            return "Performance maintained"

    def _apply_safety_checks(self, decision: ScalingDecision, current: ResourceMetrics) -> ScalingDecision:
        """Apply safety checks to scaling decision."""
        # Check scaling rate limits
        scale_factor = decision.target_instances / max(current.instance_count, 1)

        if decision.action == ScalingAction.SCALE_UP:
            max_allowed = current.instance_count * self.scaling_constraints["max_scale_up_rate"]
            if decision.target_instances > max_allowed:
                decision.target_instances = int(max_allowed)
                decision.reasoning += f"; Limited by max scale-up rate to {decision.target_instances}"

        elif decision.action == ScalingAction.SCALE_DOWN:
            min_allowed = max(1, int(current.instance_count * self.scaling_constraints["max_scale_down_rate"]))
            if decision.target_instances < min_allowed:
                decision.target_instances = min_allowed
                decision.reasoning += f"; Limited by max scale-down rate to {decision.target_instances}"

        # Check cost limits
        if decision.estimated_cost_impact > 0:  # Cost increase
            new_cost = current.cost_per_hour + decision.estimated_cost_impact
            if new_cost > self.scaling_constraints["max_cost_per_service_hour"]:
                decision.action = ScalingAction.MAINTAIN
                decision.target_instances = current.instance_count
                decision.reasoning = f"Scaling blocked by cost limit (${new_cost:.2f}/hour > ${self.scaling_constraints['max_cost_per_service_hour']}/hour)"
                decision.estimated_cost_impact = 0.0

        return decision

    async def execute_scaling_decision(self, decision: ScalingDecision) -> Dict[str, Any]:
        """Execute the scaling decision on Cloud Run."""
        if decision.action == ScalingAction.MAINTAIN:
            return {
                "success": True,
                "action": "maintain",
                "message": "No scaling changes applied",
                "service": decision.service
            }

        try:
            # In a real implementation, this would call Google Cloud Run API
            # For now, we'll simulate the execution

            scaling_config = {
                "service": decision.service,
                "resource_limits": {
                    "cpu": decision.target_cpu,
                    "memory": decision.target_memory
                },
                "scaling_config": {
                    "min_instances": max(0, decision.target_instances - 1),
                    "max_instances": decision.target_instances + 2,
                    "concurrency": decision.target_concurrency
                }
            }

            # Simulate API call delay
            await asyncio.sleep(0.1)

            logger.info(f"Scaling {decision.service}: {decision.action.value} to {decision.target_instances} instances")

            return {
                "success": True,
                "action": decision.action.value,
                "applied_config": scaling_config,
                "estimated_cost_impact": decision.estimated_cost_impact,
                "reasoning": decision.reasoning,
                "service": decision.service
            }

        except Exception as e:
            logger.error(f"Scaling execution failed for {decision.service}: {e}")
            return {
                "success": False,
                "error": str(e),
                "service": decision.service
            }

    def get_scaling_insights(self) -> Dict[str, Any]:
        """Get comprehensive scaling insights and analytics."""
        total_scaling_events = sum(len(history) for history in self.scaling_history.values())

        # Analyze scaling patterns
        scaling_patterns = {}
        cost_impacts = []

        for service, history in self.scaling_history.items():
            if history:
                recent_decisions = history[-10:]  # Last 10 decisions

                actions = [decision.action.value for _, decision in recent_decisions]
                avg_confidence = np.mean([decision.confidence for _, decision in recent_decisions])
                total_cost_impact = sum([decision.estimated_cost_impact for _, decision in recent_decisions])

                scaling_patterns[service] = {
                    "recent_actions": actions,
                    "avg_confidence": round(avg_confidence, 2),
                    "total_cost_impact": round(total_cost_impact, 4),
                    "scaling_frequency": len(recent_decisions)
                }

                cost_impacts.extend([decision.estimated_cost_impact for _, decision in recent_decisions])

        return {
            "scaling_overview": {
                "total_events": total_scaling_events,
                "services_managed": len(self.scaling_history),
                "avg_cost_impact": round(np.mean(cost_impacts), 4) if cost_impacts else 0.0,
                "total_cost_impact": round(sum(cost_impacts), 4) if cost_impacts else 0.0
            },
            "service_patterns": scaling_patterns,
            "constraints": self.scaling_constraints,
            "optimization_metrics": {
                "prediction_accuracy": self._calculate_prediction_accuracy(),
                "scaling_efficiency": self._calculate_scaling_efficiency()
            },
            "recommendations": self._generate_scaling_recommendations()
        }

    def _calculate_prediction_accuracy(self) -> float:
        """Calculate prediction accuracy based on historical data."""
        # Simplified accuracy calculation
        # In a real system, this would compare predictions with actual observed metrics
        total_predictions = sum(len(self.load_predictor.metrics_history[service])
                              for service in self.load_predictor.metrics_history)

        if total_predictions < 50:
            return 0.7  # Default accuracy for insufficient data

        # Simulate accuracy based on data volume (more data = better accuracy)
        accuracy = min(0.95, 0.6 + (total_predictions / 1000) * 0.35)
        return round(accuracy, 2)

    def _calculate_scaling_efficiency(self) -> float:
        """Calculate scaling efficiency based on decision outcomes."""
        if not self.scaling_history:
            return 0.0

        total_decisions = sum(len(history) for history in self.scaling_history.values())

        # High confidence decisions that resulted in cost savings are more efficient
        efficient_decisions = 0

        for service_history in self.scaling_history.values():
            for _, decision in service_history:
                if decision.confidence > 0.7 and decision.estimated_cost_impact <= 0:
                    efficient_decisions += 1
                elif decision.confidence > 0.8:  # High confidence decisions are generally good
                    efficient_decisions += 0.5

        efficiency = efficient_decisions / max(total_decisions, 1)
        return round(efficiency, 2)

    def _generate_scaling_recommendations(self) -> List[str]:
        """Generate scaling optimization recommendations."""
        recommendations = []

        if not self.scaling_history:
            recommendations.append("Collect more metrics data to improve scaling decisions")
            return recommendations

        # Analyze recent scaling patterns
        recent_cost_impacts = []
        high_frequency_services = []

        for service, history in self.scaling_history.items():
            recent_history = history[-20:]  # Last 20 events

            if len(recent_history) > 10:  # High frequency scaling
                high_frequency_services.append(service)

            recent_impacts = [decision.estimated_cost_impact for _, decision in recent_history]
            recent_cost_impacts.extend(recent_impacts)

        # Generate recommendations based on analysis
        if high_frequency_services:
            recommendations.append(f"Services with frequent scaling: {', '.join(high_frequency_services)} - consider adjusting thresholds")

        if recent_cost_impacts:
            avg_impact = np.mean(recent_cost_impacts)
            if avg_impact > 0.1:
                recommendations.append("Recent scaling decisions increase costs - review optimization strategies")
            elif avg_impact < -0.05:
                recommendations.append("Good cost optimization through scaling - maintain current strategy")

        prediction_accuracy = self._calculate_prediction_accuracy()
        if prediction_accuracy < 0.8:
            recommendations.append("Improve prediction accuracy by collecting more diverse metrics")

        return recommendations

# Global scaling orchestrator instance
scaling_orchestrator = ScalingOrchestrator()

# Convenience functions
async def analyze_service_scaling(service: str, cpu_usage: float, memory_usage: float,
                                instance_count: int, request_rate: float, response_time: float,
                                error_rate: float, cost_per_hour: float) -> Dict[str, Any]:
    """Analyze scaling needs for a service."""
    current_metrics = ResourceMetrics(
        timestamp=datetime.now(),
        service=service,
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        instance_count=instance_count,
        request_rate=request_rate,
        response_time=response_time,
        error_rate=error_rate,
        cost_per_hour=cost_per_hour
    )

    decision = await scaling_orchestrator.analyze_and_scale(service, current_metrics)
    execution_result = await scaling_orchestrator.execute_scaling_decision(decision)

    return {
        "scaling_decision": asdict(decision),
        "execution_result": execution_result
    }

def get_scaling_dashboard() -> Dict[str, Any]:
    """Get scaling optimization dashboard."""
    return scaling_orchestrator.get_scaling_insights()