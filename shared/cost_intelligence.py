"""
Intelligent Cost Prediction and Optimization Engine for Xynergy Platform
Advanced ML-based cost forecasting, anomaly detection, and optimization recommendations.
"""
import os
import json
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

logger = logging.getLogger(__name__)

class CostCategory(Enum):
    COMPUTE = "compute"
    AI_PROCESSING = "ai_processing"
    DATA_STORAGE = "data_storage"
    NETWORK = "network"
    EXTERNAL_APIS = "external_apis"

class AnomalyLevel(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    SEVERE = "severe"

@dataclass
class CostDataPoint:
    """Individual cost measurement point."""
    timestamp: datetime
    service: str
    category: CostCategory
    amount: float
    usage_metrics: Dict[str, float]
    metadata: Dict[str, Any] = None

@dataclass
class CostPrediction:
    """Cost prediction result."""
    predicted_cost: float
    confidence_interval: Tuple[float, float]
    trend: str  # "increasing", "decreasing", "stable"
    factors: Dict[str, float]  # Contributing factors
    recommendation: str

@dataclass
class CostAnomaly:
    """Cost anomaly detection result."""
    timestamp: datetime
    service: str
    category: CostCategory
    expected_cost: float
    actual_cost: float
    anomaly_score: float
    level: AnomalyLevel
    description: str
    suggested_actions: List[str]

class TimeSeriesPredictor:
    """Advanced time series predictor for cost forecasting."""

    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.models = {}  # Store models per service/category
        self.feature_importance = {}

    def train_cost_model(self, historical_data: List[CostDataPoint]) -> Dict[str, Any]:
        """Train predictive model on historical cost data."""
        try:
            # Convert to pandas DataFrame for easier manipulation
            df = self._prepare_dataframe(historical_data)

            if len(df) < self.window_size:
                return {"error": "Insufficient historical data", "min_required": self.window_size}

            results = {}

            # Train models per service-category combination
            for (service, category), group in df.groupby(['service', 'category']):
                if len(group) >= 10:  # Minimum data points for training
                    model_results = self._train_single_model(group, f"{service}_{category}")
                    results[f"{service}_{category}"] = model_results

            return {
                "models_trained": len(results),
                "training_results": results,
                "feature_importance": self.feature_importance,
                "training_completed": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {"error": str(e)}

    def _prepare_dataframe(self, data_points: List[CostDataPoint]) -> pd.DataFrame:
        """Convert cost data points to structured DataFrame."""
        records = []

        for point in data_points:
            record = {
                'timestamp': point.timestamp,
                'service': point.service,
                'category': point.category.value,
                'amount': point.amount,
                'hour': point.timestamp.hour,
                'day_of_week': point.timestamp.weekday(),
                'day_of_month': point.timestamp.day
            }

            # Add usage metrics as features
            if point.usage_metrics:
                record.update(point.usage_metrics)

            records.append(record)

        df = pd.DataFrame(records)
        df = df.sort_values('timestamp')

        # Create lag features
        for service in df['service'].unique():
            service_mask = df['service'] == service
            df.loc[service_mask, 'cost_lag_1'] = df.loc[service_mask, 'amount'].shift(1)
            df.loc[service_mask, 'cost_lag_7'] = df.loc[service_mask, 'amount'].shift(7)
            df.loc[service_mask, 'cost_ma_7'] = df.loc[service_mask, 'amount'].rolling(7).mean()

        return df.fillna(0)

    def _train_single_model(self, data: pd.DataFrame, model_key: str) -> Dict[str, Any]:
        """Train model for specific service-category combination."""
        try:
            # Prepare features and target
            feature_cols = ['hour', 'day_of_week', 'day_of_month', 'cost_lag_1', 'cost_lag_7', 'cost_ma_7']

            # Add usage metrics as features
            usage_cols = [col for col in data.columns if col not in ['timestamp', 'service', 'category', 'amount']]
            feature_cols.extend([col for col in usage_cols if col not in feature_cols])

            X = data[feature_cols].values
            y = data['amount'].values

            # Simple linear regression with regularization (avoiding sklearn dependency)
            X_norm = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

            # Ridge regression implementation
            alpha = 0.1
            weights = np.linalg.inv(X_norm.T @ X_norm + alpha * np.eye(X_norm.shape[1])) @ X_norm.T @ y

            # Calculate predictions and metrics
            y_pred = X_norm @ weights
            mse = np.mean((y - y_pred) ** 2)
            r2 = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - y.mean()) ** 2))

            # Store model
            self.models[model_key] = {
                'weights': weights,
                'feature_names': feature_cols,
                'mean': X.mean(axis=0),
                'std': X.std(axis=0),
                'target_mean': y.mean(),
                'target_std': y.std()
            }

            # Feature importance (absolute weights normalized)
            importance = np.abs(weights) / np.sum(np.abs(weights))
            self.feature_importance[model_key] = {
                feature_cols[i]: float(importance[i])
                for i in range(len(feature_cols))
            }

            return {
                'mse': float(mse),
                'r2_score': float(r2),
                'training_samples': len(data),
                'feature_count': len(feature_cols)
            }

        except Exception as e:
            logger.error(f"Single model training failed for {model_key}: {e}")
            return {'error': str(e)}

    def predict_costs(self, service: str, category: CostCategory,
                     horizon_hours: int = 24, current_context: Dict[str, Any] = None) -> CostPrediction:
        """Predict future costs for service and category."""
        try:
            model_key = f"{service}_{category.value}"

            if model_key not in self.models:
                return CostPrediction(
                    predicted_cost=0.0,
                    confidence_interval=(0.0, 0.0),
                    trend="unknown",
                    factors={},
                    recommendation="Insufficient training data for predictions"
                )

            model = self.models[model_key]

            # Prepare prediction features
            now = datetime.now()
            future_times = [now + timedelta(hours=h) for h in range(horizon_hours)]

            predictions = []
            for future_time in future_times:
                features = self._create_prediction_features(future_time, current_context)

                # Normalize features
                features_norm = (features - model['mean']) / (model['std'] + 1e-8)

                # Make prediction
                pred = float(features_norm @ model['weights'])
                predictions.append(max(0, pred))  # Ensure non-negative costs

            # Calculate statistics
            total_predicted = sum(predictions)
            trend = self._determine_trend(predictions)

            # Confidence interval (simple approach)
            std_dev = model['target_std']
            confidence_lower = max(0, total_predicted - 1.96 * std_dev)
            confidence_upper = total_predicted + 1.96 * std_dev

            # Generate recommendation
            recommendation = self._generate_cost_recommendation(
                service, category, total_predicted, trend, model
            )

            return CostPrediction(
                predicted_cost=round(total_predicted, 4),
                confidence_interval=(round(confidence_lower, 4), round(confidence_upper, 4)),
                trend=trend,
                factors=self.feature_importance.get(model_key, {}),
                recommendation=recommendation
            )

        except Exception as e:
            logger.error(f"Cost prediction failed: {e}")
            return CostPrediction(
                predicted_cost=0.0,
                confidence_interval=(0.0, 0.0),
                trend="error",
                factors={},
                recommendation=f"Prediction failed: {str(e)}"
            )

    def _create_prediction_features(self, timestamp: datetime, context: Dict[str, Any] = None) -> np.ndarray:
        """Create feature vector for prediction."""
        features = [
            timestamp.hour,
            timestamp.weekday(),
            timestamp.day,
            0,  # cost_lag_1 (would need recent data)
            0,  # cost_lag_7 (would need recent data)
            0   # cost_ma_7 (would need recent data)
        ]

        # Add context features if available
        if context:
            for key in ['cpu_usage', 'memory_usage', 'request_count']:
                features.append(context.get(key, 0))

        return np.array(features)

    def _determine_trend(self, predictions: List[float]) -> str:
        """Determine cost trend from predictions."""
        if len(predictions) < 2:
            return "stable"

        # Calculate trend using first and last quarters
        first_quarter = np.mean(predictions[:len(predictions)//4])
        last_quarter = np.mean(predictions[-len(predictions)//4:])

        change_percent = (last_quarter - first_quarter) / (first_quarter + 1e-8) * 100

        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"

    def _generate_cost_recommendation(self, service: str, category: CostCategory,
                                    predicted_cost: float, trend: str, model: Dict[str, Any]) -> str:
        """Generate cost optimization recommendation."""
        recommendations = []

        if trend == "increasing":
            if category == CostCategory.AI_PROCESSING:
                recommendations.append("Consider implementing more aggressive caching for AI responses")
            elif category == CostCategory.COMPUTE:
                recommendations.append("Review auto-scaling policies and consider lower resource limits")
            elif category == CostCategory.EXTERNAL_APIS:
                recommendations.append("Optimize external API usage with batching and rate limiting")

        if predicted_cost > 100:  # High cost threshold
            recommendations.append("High cost predicted - implement cost monitoring alerts")

        # Feature-based recommendations
        if hasattr(model, 'feature_importance'):
            top_feature = max(self.feature_importance.get(f"{service}_{category.value}", {}).items(),
                            key=lambda x: x[1], default=("unknown", 0))[0]

            if "hour" in top_feature:
                recommendations.append("Cost varies by time of day - consider time-based scaling")
            elif "lag" in top_feature:
                recommendations.append("Cost shows strong temporal patterns - optimize based on history")

        return "; ".join(recommendations) if recommendations else "No specific recommendations at this time"

class AnomalyDetector:
    """ML-based anomaly detection for cost monitoring."""

    def __init__(self, sensitivity: float = 2.0):
        self.sensitivity = sensitivity  # Standard deviations for anomaly threshold
        self.baseline_models = {}  # Service-category baseline costs

    def build_baselines(self, historical_data: List[CostDataPoint]) -> Dict[str, Any]:
        """Build baseline cost models for anomaly detection."""
        try:
            # Group data by service and category
            grouped_data = defaultdict(list)

            for point in historical_data:
                key = f"{point.service}_{point.category.value}"
                grouped_data[key].append(point.amount)

            # Calculate baseline statistics
            baselines_built = 0
            for key, costs in grouped_data.items():
                if len(costs) >= 10:  # Minimum data points
                    costs_array = np.array(costs)

                    # Remove outliers for baseline calculation
                    q1, q3 = np.percentile(costs_array, [25, 75])
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr

                    clean_costs = costs_array[(costs_array >= lower_bound) & (costs_array <= upper_bound)]

                    self.baseline_models[key] = {
                        'mean': float(np.mean(clean_costs)),
                        'std': float(np.std(clean_costs)),
                        'median': float(np.median(clean_costs)),
                        'q25': float(np.percentile(clean_costs, 25)),
                        'q75': float(np.percentile(clean_costs, 75)),
                        'sample_count': len(clean_costs)
                    }
                    baselines_built += 1

            return {
                'baselines_built': baselines_built,
                'total_services': len(grouped_data),
                'baseline_stats': self.baseline_models,
                'sensitivity': self.sensitivity
            }

        except Exception as e:
            logger.error(f"Baseline building failed: {e}")
            return {'error': str(e)}

    def detect_anomalies(self, recent_data: List[CostDataPoint]) -> List[CostAnomaly]:
        """Detect cost anomalies in recent data."""
        anomalies = []

        try:
            for point in recent_data:
                key = f"{point.service}_{point.category.value}"

                if key not in self.baseline_models:
                    continue  # Skip if no baseline available

                baseline = self.baseline_models[key]

                # Calculate anomaly score using multiple methods
                z_score = abs(point.amount - baseline['mean']) / (baseline['std'] + 1e-8)

                # Interquartile range method
                iqr_score = 0
                if point.amount < baseline['q25'] or point.amount > baseline['q75']:
                    iqr = baseline['q75'] - baseline['q25']
                    if point.amount < baseline['q25']:
                        iqr_score = (baseline['q25'] - point.amount) / (iqr + 1e-8)
                    else:
                        iqr_score = (point.amount - baseline['q75']) / (iqr + 1e-8)

                # Combined anomaly score
                anomaly_score = max(z_score, iqr_score)

                # Determine anomaly level
                level = AnomalyLevel.NORMAL
                if anomaly_score > self.sensitivity * 2:
                    level = AnomalyLevel.SEVERE
                elif anomaly_score > self.sensitivity * 1.5:
                    level = AnomalyLevel.CRITICAL
                elif anomaly_score > self.sensitivity:
                    level = AnomalyLevel.WARNING

                if level != AnomalyLevel.NORMAL:
                    anomaly = CostAnomaly(
                        timestamp=point.timestamp,
                        service=point.service,
                        category=point.category,
                        expected_cost=baseline['mean'],
                        actual_cost=point.amount,
                        anomaly_score=round(anomaly_score, 2),
                        level=level,
                        description=self._generate_anomaly_description(point, baseline, anomaly_score),
                        suggested_actions=self._generate_anomaly_actions(point, level, anomaly_score)
                    )
                    anomalies.append(anomaly)

            return sorted(anomalies, key=lambda x: x.anomaly_score, reverse=True)

        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []

    def _generate_anomaly_description(self, point: CostDataPoint, baseline: Dict[str, float],
                                    score: float) -> str:
        """Generate human-readable anomaly description."""
        expected = baseline['mean']
        actual = point.amount

        if actual > expected:
            percent_increase = ((actual - expected) / expected) * 100
            return f"Cost spike detected: ${actual:.4f} vs expected ${expected:.4f} ({percent_increase:.1f}% increase)"
        else:
            percent_decrease = ((expected - actual) / expected) * 100
            return f"Unusual cost drop: ${actual:.4f} vs expected ${expected:.4f} ({percent_decrease:.1f}% decrease)"

    def _generate_anomaly_actions(self, point: CostDataPoint, level: AnomalyLevel,
                                score: float) -> List[str]:
        """Generate suggested actions for anomaly."""
        actions = []

        if level in [AnomalyLevel.CRITICAL, AnomalyLevel.SEVERE]:
            actions.append("Immediate investigation required")

            if point.category == CostCategory.AI_PROCESSING:
                actions.append("Check AI provider costs and usage patterns")
                actions.append("Review request volume and complexity")
            elif point.category == CostCategory.COMPUTE:
                actions.append("Check for resource scaling issues")
                actions.append("Verify auto-scaling policies")
            elif point.category == CostCategory.EXTERNAL_APIS:
                actions.append("Review API usage rates and quotas")

        if level == AnomalyLevel.WARNING:
            actions.append("Monitor closely for trend continuation")
            actions.append("Review recent changes in service configuration")

        actions.append(f"Anomaly score: {score:.2f} - Set up enhanced monitoring")

        return actions

class CostIntelligenceEngine:
    """Main cost intelligence and optimization engine."""

    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
        self.predictor = TimeSeriesPredictor()
        self.anomaly_detector = AnomalyDetector()

        # Cost optimization thresholds
        self.optimization_thresholds = {
            CostCategory.AI_PROCESSING: 50.0,  # $50/day
            CostCategory.COMPUTE: 30.0,        # $30/day
            CostCategory.DATA_STORAGE: 20.0,   # $20/day
            CostCategory.NETWORK: 10.0,        # $10/day
            CostCategory.EXTERNAL_APIS: 40.0   # $40/day
        }

        # Historical cost data storage
        self.cost_history: List[CostDataPoint] = []

    def add_cost_data(self, service: str, category: CostCategory, amount: float,
                     usage_metrics: Dict[str, float] = None, metadata: Dict[str, Any] = None):
        """Add new cost data point."""
        data_point = CostDataPoint(
            timestamp=datetime.now(),
            service=service,
            category=category,
            amount=amount,
            usage_metrics=usage_metrics or {},
            metadata=metadata or {}
        )

        self.cost_history.append(data_point)

        # Keep only last 1000 data points per service
        if len(self.cost_history) > 10000:
            self.cost_history = self.cost_history[-10000:]

    def initialize_intelligence_models(self) -> Dict[str, Any]:
        """Initialize ML models with historical data."""
        if len(self.cost_history) < 50:
            return {
                "error": "Insufficient historical data",
                "required_minimum": 50,
                "current_data_points": len(self.cost_history)
            }

        # Train prediction models
        prediction_results = self.predictor.train_cost_model(self.cost_history)

        # Build anomaly baselines
        anomaly_results = self.anomaly_detector.build_baselines(self.cost_history)

        return {
            "prediction_models": prediction_results,
            "anomaly_baselines": anomaly_results,
            "total_data_points": len(self.cost_history),
            "initialization_time": datetime.now().isoformat()
        }

    def get_cost_forecast(self, service: str = "all", hours_ahead: int = 24) -> Dict[str, Any]:
        """Get comprehensive cost forecast."""
        forecasts = {}
        total_predicted = 0.0

        if service == "all":
            services = set(point.service for point in self.cost_history)
        else:
            services = {service}

        for svc in services:
            service_forecast = {}
            service_total = 0.0

            for category in CostCategory:
                prediction = self.predictor.predict_costs(svc, category, hours_ahead)
                service_forecast[category.value] = asdict(prediction)
                service_total += prediction.predicted_cost

            service_forecast["total_predicted"] = round(service_total, 4)
            forecasts[svc] = service_forecast
            total_predicted += service_total

        return {
            "forecast_horizon_hours": hours_ahead,
            "total_predicted_cost": round(total_predicted, 4),
            "service_forecasts": forecasts,
            "generated_at": datetime.now().isoformat(),
            "optimization_opportunities": self._identify_optimization_opportunities(forecasts)
        }

    def detect_cost_anomalies(self, hours_back: int = 24) -> Dict[str, Any]:
        """Detect cost anomalies in recent data."""
        # Get recent data
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_data = [point for point in self.cost_history if point.timestamp > cutoff_time]

        if not recent_data:
            return {
                "anomalies": [],
                "summary": "No recent data available for anomaly detection"
            }

        # Detect anomalies
        anomalies = self.anomaly_detector.detect_anomalies(recent_data)

        # Categorize anomalies by severity
        anomaly_summary = {
            "total_anomalies": len(anomalies),
            "severe": len([a for a in anomalies if a.level == AnomalyLevel.SEVERE]),
            "critical": len([a for a in anomalies if a.level == AnomalyLevel.CRITICAL]),
            "warning": len([a for a in anomalies if a.level == AnomalyLevel.WARNING]),
            "analyzed_data_points": len(recent_data),
            "analysis_period_hours": hours_back
        }

        return {
            "anomalies": [asdict(anomaly) for anomaly in anomalies],
            "summary": anomaly_summary,
            "detected_at": datetime.now().isoformat()
        }

    def _identify_optimization_opportunities(self, forecasts: Dict[str, Any]) -> List[str]:
        """Identify cost optimization opportunities from forecasts."""
        opportunities = []

        for service, forecast in forecasts.items():
            total_predicted = forecast.get("total_predicted", 0)

            # High cost services
            if total_predicted > 100:
                opportunities.append(f"High cost predicted for {service} (${total_predicted:.2f}) - review resource allocation")

            # Check category-specific thresholds
            for category, threshold in self.optimization_thresholds.items():
                category_forecast = forecast.get(category.value, {})
                if isinstance(category_forecast, dict):
                    predicted = category_forecast.get("predicted_cost", 0)
                    if predicted > threshold:
                        opportunities.append(
                            f"{service} {category.value} costs (${predicted:.2f}) exceed threshold - optimize {category.value}"
                        )

        return opportunities

    def get_intelligence_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive cost intelligence dashboard."""
        # Current period costs
        last_24h = datetime.now() - timedelta(hours=24)
        recent_costs = [point for point in self.cost_history if point.timestamp > last_24h]

        current_cost = sum(point.amount for point in recent_costs)

        # Service breakdown
        service_costs = defaultdict(float)
        category_costs = defaultdict(float)

        for point in recent_costs:
            service_costs[point.service] += point.amount
            category_costs[point.category.value] += point.amount

        # Get forecast
        forecast = self.get_cost_forecast(hours_ahead=24)

        # Get anomalies
        anomalies = self.detect_cost_anomalies(hours_back=24)

        return {
            "current_period": {
                "total_cost_24h": round(current_cost, 4),
                "service_breakdown": dict(service_costs),
                "category_breakdown": dict(category_costs),
                "data_points_analyzed": len(recent_costs)
            },
            "predictions": {
                "next_24h_forecast": forecast["total_predicted_cost"],
                "optimization_opportunities": forecast["optimization_opportunities"]
            },
            "anomalies": {
                "active_anomalies": len(anomalies["anomalies"]),
                "severity_distribution": anomalies["summary"]
            },
            "intelligence_status": {
                "models_trained": len(self.predictor.models),
                "baselines_established": len(self.anomaly_detector.baseline_models),
                "historical_data_points": len(self.cost_history)
            },
            "cost_trends": self._calculate_cost_trends(),
            "recommendations": self._generate_strategic_recommendations()
        }

    def _calculate_cost_trends(self) -> Dict[str, Any]:
        """Calculate cost trends over different periods."""
        now = datetime.now()

        # Daily trend (today vs yesterday)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)

        today_costs = [p.amount for p in self.cost_history if p.timestamp >= today_start]
        yesterday_costs = [p.amount for p in self.cost_history
                          if yesterday_start <= p.timestamp < today_start]

        today_total = sum(today_costs)
        yesterday_total = sum(yesterday_costs)

        daily_change = ((today_total - yesterday_total) / max(yesterday_total, 0.01)) * 100

        # Weekly trend
        week_ago = now - timedelta(days=7)
        week_costs = [p.amount for p in self.cost_history if p.timestamp >= week_ago]
        weekly_average = sum(week_costs) / max(len(week_costs), 1)

        return {
            "daily_change_percent": round(daily_change, 1),
            "today_total": round(today_total, 4),
            "yesterday_total": round(yesterday_total, 4),
            "weekly_average": round(weekly_average, 4),
            "trend_direction": "increasing" if daily_change > 5 else "decreasing" if daily_change < -5 else "stable"
        }

    def _generate_strategic_recommendations(self) -> List[str]:
        """Generate strategic cost optimization recommendations."""
        recommendations = []

        # Analyze recent cost patterns
        recent_costs = self.cost_history[-100:] if len(self.cost_history) > 100 else self.cost_history

        if not recent_costs:
            return ["Insufficient data for recommendations"]

        # Service cost analysis
        service_totals = defaultdict(float)
        category_totals = defaultdict(float)

        for point in recent_costs:
            service_totals[point.service] += point.amount
            category_totals[point.category.value] += point.amount

        # High-cost service recommendations
        top_cost_service = max(service_totals.items(), key=lambda x: x[1], default=("none", 0))
        if top_cost_service[1] > 50:
            recommendations.append(f"Focus optimization efforts on {top_cost_service[0]} (${top_cost_service[1]:.2f})")

        # Category-specific recommendations
        if category_totals.get("ai_processing", 0) > 100:
            recommendations.append("Implement aggressive AI response caching to reduce processing costs")

        if category_totals.get("compute", 0) > 80:
            recommendations.append("Review container resource allocation and auto-scaling policies")

        # Model-specific recommendations
        if len(self.predictor.models) < 5:
            recommendations.append("Collect more data to improve cost prediction accuracy")

        return recommendations

# Global intelligence engine instance
cost_intelligence = CostIntelligenceEngine()

# Convenience functions
def track_service_cost(service: str, category: str, amount: float, metrics: Dict[str, float] = None):
    """Track cost for a service."""
    cost_category = CostCategory(category)
    cost_intelligence.add_cost_data(service, cost_category, amount, metrics)

def get_cost_insights() -> Dict[str, Any]:
    """Get comprehensive cost insights dashboard."""
    return cost_intelligence.get_intelligence_dashboard()