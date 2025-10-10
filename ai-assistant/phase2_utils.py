import asyncio
import httpx
import time
import structlog
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = structlog.get_logger()

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    timeout: int = 60
    half_open_max_calls: int = 3

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.half_open_calls = 0
    
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.config.timeout:
                self.state = "HALF_OPEN"
                self.half_open_calls = 0
            else:
                raise Exception(f"Circuit breaker OPEN for {func.__name__}")
        
        if self.state == "HALF_OPEN" and self.half_open_calls >= self.config.half_open_max_calls:
            raise Exception(f"Circuit breaker HALF_OPEN limit reached for {func.__name__}")
        
        try:
            if self.state == "HALF_OPEN":
                self.half_open_calls += 1
            
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                self.half_open_calls = 0
            
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.config.failure_threshold:
                self.state = "OPEN"
            
            logger.error("Circuit breaker failure", function=func.__name__, error=str(e), state=self.state)
            raise e

async def call_service_with_circuit_breaker(url: str, data: Dict = None, circuit_breaker: CircuitBreaker = None) -> Dict[str, Any]:
    """Make HTTP calls with circuit breaker protection"""
    async def make_request():
        async with httpx.AsyncClient(timeout=30.0) as client:
            if data:
                response = await client.post(url, json=data)
                return response.json()
            else:
                response = await client.get(url)
                return response.json()

    if circuit_breaker:
        return await circuit_breaker.call(make_request)
    else:
        return await make_request()

def get_opentelemetry_tracer(service_name: str):
    """Initialize OpenTelemetry tracing"""
    # Placeholder for OpenTelemetry integration
    logger.info("OpenTelemetry tracer initialized", service=service_name)
    return None

class PerformanceMonitor:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.metrics = {
            "request_count": 0,
            "error_count": 0,
            "total_response_time": 0.0,
            "circuit_breaker_trips": 0
        }

    def record_request(self, response_time: float, success: bool = True):
        self.metrics["request_count"] += 1
        self.metrics["total_response_time"] += response_time
        if not success:
            self.metrics["error_count"] += 1

    def track_operation(self, operation_name: str):
        """Context manager for tracking operation performance"""
        return OperationTracker(self, operation_name)

    def get_metrics(self) -> Dict[str, Any]:
        if self.metrics["request_count"] > 0:
            avg_response_time = self.metrics["total_response_time"] / self.metrics["request_count"]
            error_rate = self.metrics["error_count"] / self.metrics["request_count"]
        else:
            avg_response_time = 0.0
            error_rate = 0.0

        return {
            **self.metrics,
            "average_response_time": round(avg_response_time, 3),
            "error_rate": round(error_rate * 100, 2)
        }

class OperationTracker:
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            success = exc_type is None
            self.monitor.record_request(duration, success)
            if exc_type:
                logger.error(f"Operation {self.operation_name} failed", error=str(exc_val))
