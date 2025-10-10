"""
phase2_utils.py
Phase 2 utilities for circuit breakers and performance monitoring
"""
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import logging

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    timeout_duration: int = 60
    half_open_max_calls: int = 3

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
        self.half_open_calls = 0
    
    async def call(self, func: Callable, *args, **kwargs):
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                self.half_open_calls = 0
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        if not self.last_failure_time:
            return True
        return (datetime.now() - self.last_failure_time).seconds >= self.config.timeout_duration
    
    def _on_success(self):
        if self.state == "HALF_OPEN":
            self.half_open_calls += 1
            if self.half_open_calls >= self.config.half_open_max_calls:
                self.state = "CLOSED"
                self.failure_count = 0
        else:
            self.failure_count = 0
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = "OPEN"

class PerformanceMonitor:
    def __init__(self, service_name: str = "unknown"):
        self.service_name = service_name
        self.metrics = {}
        self.max_metrics = 1000
    
    def track_request(self, operation_name: str):
        return RequestTracker(operation_name, self.metrics, self.service_name, self.max_metrics)

class RequestTracker:
    def __init__(self, operation_name: str, metrics: Dict, service_name: str, max_metrics: int):
        self.operation_name = operation_name
        self.metrics = metrics
        self.service_name = service_name
        self.max_metrics = max_metrics
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if self.operation_name not in self.metrics:
            self.metrics[self.operation_name] = {
                'total_calls': 0,
                'total_duration': 0,
                'failures': 0,
                'service': self.service_name
            }
        
        self.metrics[self.operation_name]['total_calls'] += 1
        self.metrics[self.operation_name]['total_duration'] += duration
        
        if exc_type is not None:
            self.metrics[self.operation_name]['failures'] += 1
        
        if len(self.metrics) > self.max_metrics:
            oldest_keys = list(self.metrics.keys())[:100]
            for key in oldest_keys:
                del self.metrics[key]

async def call_service_with_circuit_breaker(service_func: Callable, circuit_breaker: CircuitBreaker, *args, **kwargs):
    """Call a service function with circuit breaker protection"""
    return await circuit_breaker.call(service_func, *args, **kwargs)
