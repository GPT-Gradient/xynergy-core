"""
Advanced ML-based Anomaly Detection System for Xynergy Platform
Real-time anomaly detection with intelligent alerting and automated response capabilities.
"""
import os
import json
import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, deque
import warnings
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    COST = "cost"
    ERROR_RATE = "error_rate"
    SECURITY = "security"
    AVAILABILITY = "availability"

class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class DetectionMethod(Enum):
    STATISTICAL = "statistical"
    ML_ISOLATION_FOREST = "isolation_forest"
    THRESHOLD = "threshold"
    TREND_ANALYSIS = "trend_analysis"
    SEASONAL = "seasonal"

@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: datetime
    service: str
    metric_name: str
    value: float
    metadata: Dict[str, Any] = None

@dataclass
class Anomaly:
    """Detected anomaly with context."""
    anomaly_id: str
    timestamp: datetime
    service: str
    metric_name: str
    anomaly_type: AnomalyType
    severity: SeverityLevel
    detection_method: DetectionMethod
    score: float  # Anomaly score (0-1)
    expected_value: float
    actual_value: float
    context: Dict[str, Any]
    description: str
    suggested_actions: List[str]
    is_resolved: bool = False

@dataclass
class DetectionModel:
    """ML model for anomaly detection."""
    model_id: str
    service: str
    metric_name: str
    model_type: DetectionMethod
    parameters: Dict[str, Any]
    training_data_size: int
    last_updated: datetime
    accuracy_score: float

class StatisticalDetector:
    """Statistical anomaly detection using Z-score and IQR methods."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metric_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.baseline_stats: Dict[str, Dict[str, float]] = {}

    def add_metric_point(self, point: MetricPoint):
        """Add new metric point to detection window."""
        key = f"{point.service}_{point.metric_name}"
        self.metric_windows[key].append((point.timestamp, point.value))

        # Update baseline statistics
        if len(self.metric_windows[key]) >= 30:  # Minimum for stable statistics
            self._update_baseline_stats(key)

    def _update_baseline_stats(self, key: str):
        """Update baseline statistics for a metric."""
        values = [point[1] for point in self.metric_windows[key]]

        # Remove outliers for baseline calculation
        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        clean_values = [v for v in values if lower_bound <= v <= upper_bound]

        if clean_values:
            self.baseline_stats[key] = {
                'mean': np.mean(clean_values),
                'std': np.std(clean_values),
                'median': np.median(clean_values),
                'q1': q1,
                'q3': q3,
                'iqr': iqr,
                'min': np.min(clean_values),
                'max': np.max(clean_values)
            }

    def detect_anomalies(self, point: MetricPoint, z_threshold: float = 3.0,
                        iqr_threshold: float = 2.0) -> Optional[Anomaly]:
        """Detect anomalies using statistical methods."""
        key = f"{point.service}_{point.metric_name}"

        if key not in self.baseline_stats:
            return None  # Not enough data for detection

        stats = self.baseline_stats[key]

        # Z-score detection
        z_score = abs(point.value - stats['mean']) / (stats['std'] + 1e-8)

        # IQR-based detection
        iqr_score = 0
        if point.value < stats['q1'] - iqr_threshold * stats['iqr']:
            iqr_score = (stats['q1'] - point.value) / stats['iqr']
        elif point.value > stats['q3'] + iqr_threshold * stats['iqr']:
            iqr_score = (point.value - stats['q3']) / stats['iqr']

        # Combined anomaly score
        anomaly_score = max(z_score / z_threshold, iqr_score / iqr_threshold)

        if anomaly_score > 1.0:  # Anomaly detected
            severity = self._calculate_severity(anomaly_score, point.metric_name)

            return Anomaly(
                anomaly_id=f"stat_{int(point.timestamp.timestamp())}_{point.service}_{point.metric_name}",
                timestamp=point.timestamp,
                service=point.service,
                metric_name=point.metric_name,
                anomaly_type=self._classify_anomaly_type(point.metric_name),
                severity=severity,
                detection_method=DetectionMethod.STATISTICAL,
                score=min(1.0, anomaly_score),
                expected_value=stats['mean'],
                actual_value=point.value,
                context={
                    'z_score': round(z_score, 2),
                    'iqr_score': round(iqr_score, 2),
                    'baseline_stats': stats
                },
                description=self._generate_description(point, stats, anomaly_score),
                suggested_actions=self._generate_actions(point, severity, anomaly_score)
            )

        return None

    def _calculate_severity(self, score: float, metric_name: str) -> SeverityLevel:
        """Calculate severity based on anomaly score and metric type."""
        critical_metrics = ['error_rate', 'response_time', 'cpu_usage', 'memory_usage']

        if score > 3.0:
            return SeverityLevel.EMERGENCY
        elif score > 2.0:
            return SeverityLevel.CRITICAL if metric_name in critical_metrics else SeverityLevel.WARNING
        elif score > 1.5:
            return SeverityLevel.WARNING
        else:
            return SeverityLevel.INFO

    def _classify_anomaly_type(self, metric_name: str) -> AnomalyType:
        """Classify anomaly type based on metric name."""
        if 'response_time' in metric_name or 'latency' in metric_name:
            return AnomalyType.PERFORMANCE
        elif 'cpu' in metric_name or 'memory' in metric_name or 'disk' in metric_name:
            return AnomalyType.RESOURCE
        elif 'cost' in metric_name or 'billing' in metric_name:
            return AnomalyType.COST
        elif 'error' in metric_name or 'failure' in metric_name:
            return AnomalyType.ERROR_RATE
        elif 'security' in metric_name or 'auth' in metric_name:
            return AnomalyType.SECURITY
        else:
            return AnomalyType.AVAILABILITY

    def _generate_description(self, point: MetricPoint, stats: Dict[str, float], score: float) -> str:
        """Generate human-readable anomaly description."""
        expected = stats['mean']
        actual = point.value
        metric = point.metric_name

        if actual > expected:
            change_percent = ((actual - expected) / expected) * 100
            return f"{metric} spike detected: {actual:.2f} (expected ~{expected:.2f}, +{change_percent:.1f}%)"
        else:
            change_percent = ((expected - actual) / expected) * 100
            return f"{metric} drop detected: {actual:.2f} (expected ~{expected:.2f}, -{change_percent:.1f}%)"

    def _generate_actions(self, point: MetricPoint, severity: SeverityLevel, score: float) -> List[str]:
        """Generate suggested actions for anomaly."""
        actions = []
        metric = point.metric_name

        if severity in [SeverityLevel.CRITICAL, SeverityLevel.EMERGENCY]:
            actions.append("Immediate investigation required")

            if 'response_time' in metric:
                actions.append("Check service load and scaling policies")
                actions.append("Review recent deployments")
            elif 'error_rate' in metric:
                actions.append("Check service logs for errors")
                actions.append("Verify service dependencies")
            elif 'cpu' in metric or 'memory' in metric:
                actions.append("Check resource allocation and limits")
                actions.append("Consider scaling up service")

        if severity == SeverityLevel.WARNING:
            actions.append("Monitor closely for trend continuation")

        actions.append(f"Anomaly score: {score:.2f}")
        return actions

class IsolationForestDetector:
    """Isolation Forest-based anomaly detection for multivariate data."""

    def __init__(self, contamination: float = 0.1, n_estimators: int = 100):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.models: Dict[str, Dict[str, Any]] = {}
        self.feature_data: Dict[str, List[List[float]]] = defaultdict(list)
        self.feature_names: Dict[str, List[str]] = {}

    def add_multivariate_data(self, service: str, features: Dict[str, float], timestamp: datetime):
        """Add multivariate data point for service."""
        if service not in self.feature_names:
            self.feature_names[service] = list(features.keys())

        # Ensure consistent feature ordering
        feature_vector = [features.get(name, 0.0) for name in self.feature_names[service]]
        self.feature_data[service].append(feature_vector)

        # Keep only recent data for training
        if len(self.feature_data[service]) > 1000:
            self.feature_data[service] = self.feature_data[service][-1000:]

    def train_model(self, service: str) -> bool:
        """Train isolation forest model for service."""
        if len(self.feature_data[service]) < 50:
            return False  # Insufficient data

        try:
            # Simple isolation forest implementation (avoiding sklearn dependency)
            data = np.array(self.feature_data[service])

            # Normalize features
            mean = np.mean(data, axis=0)
            std = np.std(data, axis=0) + 1e-8
            normalized_data = (data - mean) / std

            # Store model parameters (simplified)
            self.models[service] = {
                'mean': mean,
                'std': std,
                'training_data': normalized_data[-500:],  # Keep recent training data
                'contamination': self.contamination,
                'trained_at': datetime.now(),
                'feature_names': self.feature_names[service]
            }

            return True

        except Exception as e:
            logger.error(f"Model training failed for {service}: {e}")
            return False

    def detect_anomaly(self, service: str, features: Dict[str, float]) -> Optional[Anomaly]:
        """Detect anomaly using isolation forest."""
        if service not in self.models:
            return None

        try:
            model = self.models[service]

            # Prepare feature vector
            feature_vector = np.array([features.get(name, 0.0) for name in model['feature_names']])

            # Normalize
            normalized_features = (feature_vector - model['mean']) / model['std']

            # Calculate anomaly score (simplified isolation score)
            training_data = model['training_data']
            distances = np.linalg.norm(training_data - normalized_features, axis=1)
            isolation_score = np.percentile(distances, 95) / (np.mean(distances) + 1e-8)

            # Anomaly threshold
            threshold = 2.0  # Configurable threshold
            if isolation_score > threshold:
                severity = SeverityLevel.CRITICAL if isolation_score > 3.0 else SeverityLevel.WARNING

                return Anomaly(
                    anomaly_id=f"if_{int(datetime.now().timestamp())}_{service}",
                    timestamp=datetime.now(),
                    service=service,
                    metric_name="multivariate_pattern",
                    anomaly_type=AnomalyType.PERFORMANCE,
                    severity=severity,
                    detection_method=DetectionMethod.ML_ISOLATION_FOREST,
                    score=min(1.0, isolation_score / 4.0),  # Normalize to 0-1
                    expected_value=1.0,  # Baseline pattern
                    actual_value=isolation_score,
                    context={
                        'features': features,
                        'isolation_score': round(isolation_score, 2),
                        'feature_names': model['feature_names']
                    },
                    description=f"Anomalous behavior pattern detected (isolation score: {isolation_score:.2f})",
                    suggested_actions=[
                        "Investigate unusual system behavior pattern",
                        "Review multiple metrics simultaneously",
                        f"Isolation score: {isolation_score:.2f} > threshold: {threshold}"
                    ]
                )

            return None

        except Exception as e:
            logger.error(f"Anomaly detection failed for {service}: {e}")
            return None

class TrendAnalyzer:
    """Trend-based anomaly detection for identifying unusual patterns."""

    def __init__(self, trend_window: int = 50):
        self.trend_window = trend_window
        self.trend_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=trend_window))

    def add_data_point(self, point: MetricPoint):
        """Add data point for trend analysis."""
        key = f"{point.service}_{point.metric_name}"
        self.trend_data[key].append((point.timestamp, point.value))

    def detect_trend_anomalies(self, point: MetricPoint) -> Optional[Anomaly]:
        """Detect trend-based anomalies."""
        key = f"{point.service}_{point.metric_name}"

        if len(self.trend_data[key]) < 20:
            return None

        values = [p[1] for p in self.trend_data[key]]

        # Calculate trend metrics
        recent_trend = self._calculate_trend(values[-10:])  # Recent trend
        historical_trend = self._calculate_trend(values[:-10])  # Historical trend

        # Detect significant trend changes
        trend_change = abs(recent_trend - historical_trend)

        # Volatility check
        recent_volatility = np.std(values[-10:])
        historical_volatility = np.std(values[:-10])
        volatility_ratio = recent_volatility / (historical_volatility + 1e-8)

        # Anomaly conditions
        significant_trend_change = trend_change > np.std(values) * 2
        volatility_spike = volatility_ratio > 3.0

        if significant_trend_change or volatility_spike:
            # Calculate severity
            anomaly_score = max(trend_change / (np.std(values) + 1e-8), volatility_ratio / 3.0)
            severity = SeverityLevel.CRITICAL if anomaly_score > 2.0 else SeverityLevel.WARNING

            return Anomaly(
                anomaly_id=f"trend_{int(point.timestamp.timestamp())}_{point.service}_{point.metric_name}",
                timestamp=point.timestamp,
                service=point.service,
                metric_name=point.metric_name,
                anomaly_type=AnomalyType.PERFORMANCE,
                severity=severity,
                detection_method=DetectionMethod.TREND_ANALYSIS,
                score=min(1.0, anomaly_score / 3.0),
                expected_value=historical_trend,
                actual_value=recent_trend,
                context={
                    'recent_trend': round(recent_trend, 4),
                    'historical_trend': round(historical_trend, 4),
                    'trend_change': round(trend_change, 4),
                    'volatility_ratio': round(volatility_ratio, 2)
                },
                description=self._generate_trend_description(
                    point.metric_name, recent_trend, historical_trend, volatility_ratio
                ),
                suggested_actions=[
                    "Analyze recent system changes",
                    "Check for external factors affecting performance",
                    f"Trend change magnitude: {trend_change:.4f}"
                ]
            )

        return None

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate linear trend (slope) of values."""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        y = np.array(values)

        # Simple linear regression
        n = len(values)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x**2) - np.sum(x)**2 + 1e-8)

        return slope

    def _generate_trend_description(self, metric_name: str, recent_trend: float,
                                  historical_trend: float, volatility_ratio: float) -> str:
        """Generate trend anomaly description."""
        if abs(recent_trend) > abs(historical_trend) * 2:
            direction = "increasing" if recent_trend > 0 else "decreasing"
            return f"{metric_name} showing unusual {direction} trend (slope: {recent_trend:.4f})"
        elif volatility_ratio > 3:
            return f"{metric_name} showing increased volatility ({volatility_ratio:.1f}x normal)"
        else:
            return f"{metric_name} trend pattern change detected"

class AnomalyDetectionEngine:
    """Main anomaly detection engine coordinating multiple detection methods."""

    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("PROJECT_ID", "xynergy-dev-1757909467")

        # Detection components
        self.statistical_detector = StatisticalDetector()
        self.isolation_detector = IsolationForestDetector()
        self.trend_analyzer = TrendAnalyzer()

        # Anomaly storage and management
        self.active_anomalies: Dict[str, Anomaly] = {}
        self.anomaly_history: List[Anomaly] = []
        self.alert_callbacks: List[Callable[[Anomaly], None]] = []

        # Detection configuration
        self.detection_config = {
            'statistical_enabled': True,
            'ml_enabled': True,
            'trend_enabled': True,
            'auto_resolution': True,
            'alert_cooldown_minutes': 15
        }

        # Metric thresholds for threshold-based detection
        self.metric_thresholds = {
            'cpu_usage': {'warning': 80, 'critical': 95},
            'memory_usage': {'warning': 85, 'critical': 95},
            'error_rate': {'warning': 2, 'critical': 5},
            'response_time': {'warning': 1000, 'critical': 5000},
            'disk_usage': {'warning': 80, 'critical': 90}
        }

    def add_metric_data(self, service: str, metrics: Dict[str, float], timestamp: datetime = None):
        """Add new metric data for anomaly detection."""
        timestamp = timestamp or datetime.now()

        # Create metric points
        metric_points = []
        for metric_name, value in metrics.items():
            point = MetricPoint(
                timestamp=timestamp,
                service=service,
                metric_name=metric_name,
                value=value
            )
            metric_points.append(point)

        # Process with all detectors
        detected_anomalies = []

        for point in metric_points:
            # Statistical detection
            if self.detection_config['statistical_enabled']:
                self.statistical_detector.add_metric_point(point)
                stat_anomaly = self.statistical_detector.detect_anomalies(point)
                if stat_anomaly:
                    detected_anomalies.append(stat_anomaly)

            # Trend analysis
            if self.detection_config['trend_enabled']:
                self.trend_analyzer.add_data_point(point)
                trend_anomaly = self.trend_analyzer.detect_trend_anomalies(point)
                if trend_anomaly:
                    detected_anomalies.append(trend_anomaly)

            # Threshold-based detection
            threshold_anomaly = self._check_thresholds(point)
            if threshold_anomaly:
                detected_anomalies.append(threshold_anomaly)

        # ML-based multivariate detection
        if self.detection_config['ml_enabled']:
            self.isolation_detector.add_multivariate_data(service, metrics, timestamp)

            # Train model periodically
            if len(self.isolation_detector.feature_data[service]) % 100 == 0:
                self.isolation_detector.train_model(service)

            # Detect multivariate anomalies
            ml_anomaly = self.isolation_detector.detect_anomaly(service, metrics)
            if ml_anomaly:
                detected_anomalies.append(ml_anomaly)

        # Process detected anomalies
        for anomaly in detected_anomalies:
            self._process_anomaly(anomaly)

        return len(detected_anomalies)

    def _check_thresholds(self, point: MetricPoint) -> Optional[Anomaly]:
        """Check threshold-based anomalies."""
        if point.metric_name not in self.metric_thresholds:
            return None

        thresholds = self.metric_thresholds[point.metric_name]
        value = point.value

        severity = None
        if value >= thresholds['critical']:
            severity = SeverityLevel.CRITICAL
        elif value >= thresholds['warning']:
            severity = SeverityLevel.WARNING

        if severity:
            return Anomaly(
                anomaly_id=f"threshold_{int(point.timestamp.timestamp())}_{point.service}_{point.metric_name}",
                timestamp=point.timestamp,
                service=point.service,
                metric_name=point.metric_name,
                anomaly_type=self.statistical_detector._classify_anomaly_type(point.metric_name),
                severity=severity,
                detection_method=DetectionMethod.THRESHOLD,
                score=min(1.0, value / thresholds['critical']),
                expected_value=thresholds['warning'],
                actual_value=value,
                context={'thresholds': thresholds},
                description=f"{point.metric_name} threshold exceeded: {value} > {thresholds[severity.value]}",
                suggested_actions=[
                    f"Immediate attention required for {point.metric_name}",
                    f"Current value: {value}, {severity.value} threshold: {thresholds[severity.value]}"
                ]
            )

        return None

    def _process_anomaly(self, anomaly: Anomaly):
        """Process detected anomaly."""
        # Check for duplicate/similar anomalies
        if self._is_duplicate_anomaly(anomaly):
            return

        # Add to active anomalies
        self.active_anomalies[anomaly.anomaly_id] = anomaly
        self.anomaly_history.append(anomaly)

        # Trigger alerts
        for callback in self.alert_callbacks:
            try:
                callback(anomaly)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

        logger.info(f"Anomaly detected: {anomaly.service}.{anomaly.metric_name} - {anomaly.severity.value}")

    def _is_duplicate_anomaly(self, new_anomaly: Anomaly) -> bool:
        """Check if anomaly is duplicate of recent anomaly."""
        cutoff_time = datetime.now() - timedelta(minutes=self.detection_config['alert_cooldown_minutes'])

        for existing_anomaly in self.active_anomalies.values():
            if (existing_anomaly.service == new_anomaly.service and
                existing_anomaly.metric_name == new_anomaly.metric_name and
                existing_anomaly.anomaly_type == new_anomaly.anomaly_type and
                existing_anomaly.timestamp > cutoff_time):
                return True

        return False

    def resolve_anomaly(self, anomaly_id: str, resolution_note: str = "") -> bool:
        """Manually resolve an anomaly."""
        if anomaly_id in self.active_anomalies:
            anomaly = self.active_anomalies[anomaly_id]
            anomaly.is_resolved = True
            anomaly.context['resolution_note'] = resolution_note
            anomaly.context['resolved_at'] = datetime.now().isoformat()

            del self.active_anomalies[anomaly_id]
            logger.info(f"Anomaly resolved: {anomaly_id}")
            return True

        return False

    def get_active_anomalies(self, service: str = None, severity: SeverityLevel = None) -> List[Anomaly]:
        """Get currently active anomalies with optional filtering."""
        anomalies = list(self.active_anomalies.values())

        if service:
            anomalies = [a for a in anomalies if a.service == service]

        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]

        return sorted(anomalies, key=lambda x: x.timestamp, reverse=True)

    def get_anomaly_summary(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get comprehensive anomaly detection summary."""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_anomalies = [a for a in self.anomaly_history if a.timestamp > cutoff_time]

        # Categorize anomalies
        by_severity = defaultdict(int)
        by_service = defaultdict(int)
        by_type = defaultdict(int)
        by_method = defaultdict(int)

        for anomaly in recent_anomalies:
            by_severity[anomaly.severity.value] += 1
            by_service[anomaly.service] += 1
            by_type[anomaly.anomaly_type.value] += 1
            by_method[anomaly.detection_method.value] += 1

        # Calculate detection effectiveness
        total_detected = len(recent_anomalies)
        resolved_count = sum(1 for a in recent_anomalies if a.is_resolved)
        resolution_rate = (resolved_count / total_detected * 100) if total_detected > 0 else 0

        return {
            "summary": {
                "analysis_period_hours": hours_back,
                "total_anomalies": total_detected,
                "active_anomalies": len(self.active_anomalies),
                "resolution_rate": round(resolution_rate, 1)
            },
            "breakdown": {
                "by_severity": dict(by_severity),
                "by_service": dict(by_service),
                "by_type": dict(by_type),
                "by_detection_method": dict(by_method)
            },
            "detection_stats": {
                "statistical_detector": len(self.statistical_detector.baseline_stats),
                "ml_models_trained": len(self.isolation_detector.models),
                "trend_analyzers": len(self.trend_analyzer.trend_data)
            },
            "top_services": sorted(by_service.items(), key=lambda x: x[1], reverse=True)[:5],
            "recommendations": self._generate_recommendations(recent_anomalies)
        }

    def _generate_recommendations(self, recent_anomalies: List[Anomaly]) -> List[str]:
        """Generate recommendations based on anomaly patterns."""
        recommendations = []

        if not recent_anomalies:
            recommendations.append("No recent anomalies detected - system appears stable")
            return recommendations

        # Analyze patterns
        severity_counts = defaultdict(int)
        service_counts = defaultdict(int)

        for anomaly in recent_anomalies:
            severity_counts[anomaly.severity.value] += 1
            service_counts[anomaly.service] += 1

        # High severity recommendations
        if severity_counts.get('critical', 0) + severity_counts.get('emergency', 0) > 5:
            recommendations.append("High number of critical anomalies - review system stability")

        # Service-specific recommendations
        top_service = max(service_counts.items(), key=lambda x: x[1], default=("none", 0))
        if top_service[1] > 3:
            recommendations.append(f"Focus investigation on {top_service[0]} service ({top_service[1]} anomalies)")

        # Detection method recommendations
        active_detectors = len(self.statistical_detector.baseline_stats)
        ml_models = len(self.isolation_detector.models)

        if active_detectors < 5:
            recommendations.append("Increase metric collection to improve statistical detection")

        if ml_models < 3:
            recommendations.append("Train more ML models for better multivariate anomaly detection")

        return recommendations

    def add_alert_callback(self, callback: Callable[[Anomaly], None]):
        """Add callback function for anomaly alerts."""
        self.alert_callbacks.append(callback)

    def get_detection_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive detection dashboard."""
        summary = self.get_anomaly_summary(hours_back=24)

        # Add configuration and status
        summary["configuration"] = self.detection_config
        summary["thresholds"] = self.metric_thresholds
        summary["system_status"] = {
            "statistical_baselines": len(self.statistical_detector.baseline_stats),
            "ml_models": len(self.isolation_detector.models),
            "trend_analyzers": len(self.trend_analyzer.trend_data),
            "alert_callbacks": len(self.alert_callbacks)
        }

        return summary

# Global anomaly detection engine
anomaly_engine = AnomalyDetectionEngine()

# Convenience functions
def detect_service_anomalies(service: str, metrics: Dict[str, float]) -> int:
    """Detect anomalies for service metrics."""
    return anomaly_engine.add_metric_data(service, metrics)

def get_anomaly_dashboard() -> Dict[str, Any]:
    """Get anomaly detection dashboard."""
    return anomaly_engine.get_detection_dashboard()

def setup_anomaly_alerts(callback: Callable[[Anomaly], None]):
    """Setup anomaly alert callback."""
    anomaly_engine.add_alert_callback(callback)