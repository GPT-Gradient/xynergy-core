"""
Xynergy Platform SDK for Management Dashboard Integration

This SDK provides a comprehensive interface for integrating with the Xynergy Platform
microservices architecture, enabling dashboard applications to monitor, control,
and interact with the platform's AI-powered business operations.

Features:
- Service discovery and health monitoring
- Workflow orchestration and execution
- Real-time event streaming via WebSocket and Pub/Sub
- Circuit breaker management and error handling
- Performance analytics and cost optimization tracking
- AI routing and provider management

Usage:
    from xynergy_platform_sdk import XynergyPlatformSDK

    sdk = XynergyPlatformSDK(
        api_key="your_api_key",
        base_url="https://xynergy-platform-dashboard.us-central1.run.app"
    )

    # Get platform health
    health = await sdk.get_platform_health()

    # Execute business intent
    result = await sdk.execute_business_intent("Create marketing campaign")
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import httpx
import websockets
from google.cloud import pubsub_v1
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Data Models
class ServiceStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"

class WorkflowStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

@dataclass
class ServiceHealth:
    service_name: str
    status: ServiceStatus
    url: str
    capabilities: List[str]
    last_health_check: datetime
    response_time: Optional[float] = None
    error_message: Optional[str] = None

@dataclass
class PlatformHealth:
    overall_status: ServiceStatus
    healthy_services: int
    total_services: int
    unhealthy_services: List[str]
    services: Dict[str, ServiceHealth]
    timestamp: datetime

@dataclass
class WorkflowStep:
    step_id: str
    service: str
    action: str
    parameters: Dict[str, Any]
    depends_on: Optional[List[str]] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

@dataclass
class WorkflowExecution:
    workflow_id: str
    workflow_name: str
    status: WorkflowStatus
    steps: List[WorkflowStep]
    progress: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None

@dataclass
class PerformanceMetrics:
    average_response_time: float
    requests_per_minute: int
    success_rate: float
    ai_routing_efficiency: int
    cost_savings_percentage: int
    total_cost_today: float
    projected_monthly_cost: float

@dataclass
class DashboardOverview:
    platform_health: PlatformHealth
    active_workflows: int
    completed_today: int
    cost_metrics: PerformanceMetrics
    ai_routing_distribution: Dict[str, int]
    timestamp: datetime

class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

class ServiceUnavailableError(Exception):
    """Raised when a service is unavailable"""
    pass

class XynergyPlatformSDK:
    """
    Main SDK class for interacting with the Xynergy Platform.

    Provides comprehensive access to all platform services including:
    - Service discovery and health monitoring
    - Workflow orchestration
    - Real-time event streaming
    - Performance analytics
    - AI routing management
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://xynergy-platform-dashboard.us-central1.run.app",
        project_id: str = "xynergy-dev-1757909467",
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.project_id = project_id
        self.timeout = timeout
        self.max_retries = max_retries

        # HTTP client configuration
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }

        # Service registry cache
        self._service_registry: Dict[str, ServiceHealth] = {}
        self._registry_last_updated: Optional[datetime] = None
        self._registry_ttl = timedelta(minutes=5)

        # WebSocket connection
        self._ws_connection: Optional[websockets.WebSocketServerProtocol] = None
        self._event_callbacks: List[Callable] = []

        # Circuit breaker tracking
        self._circuit_breakers: Dict[str, Dict] = {}

        # Performance tracking
        self._request_times: List[float] = []

        self.logger = logger.bind(sdk_version="1.0.0", base_url=base_url)

    async def __aenter__(self):
        """Async context manager entry"""
        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers=self.headers,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if hasattr(self, '_http_client'):
            await self._http_client.aclose()

        if self._ws_connection:
            await self._ws_connection.close()

    # Authentication and Service Discovery

    async def verify_authentication(self) -> bool:
        """Verify API key authentication with the platform"""
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception as e:
            self.logger.error("Authentication verification failed", error=str(e))
            return False

    async def get_service_registry(self, force_refresh: bool = False) -> Dict[str, ServiceHealth]:
        """Get current service registry with caching"""
        now = datetime.now()

        if (not force_refresh and
            self._registry_last_updated and
            now - self._registry_last_updated < self._registry_ttl and
            self._service_registry):
            return self._service_registry

        try:
            start_time = time.time()
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/platform-status")
                response.raise_for_status()

                data = response.json()
                self._track_request_time(time.time() - start_time)

                # Parse services into ServiceHealth objects
                services = {}
                for service_name, service_data in data.get("services", {}).items():
                    services[service_name] = ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus(service_data.get("status", "unknown")),
                        url=service_data.get("url", ""),
                        capabilities=service_data.get("capabilities", []),
                        last_health_check=datetime.fromisoformat(
                            service_data.get("last_health_check", now.isoformat()).replace("Z", "+00:00")
                        ),
                        response_time=service_data.get("response_time")
                    )

                self._service_registry = services
                self._registry_last_updated = now

                self.logger.info("Service registry updated",
                               services_count=len(services),
                               healthy_count=len([s for s in services.values() if s.status == ServiceStatus.HEALTHY]))

                return services

        except Exception as e:
            self.logger.error("Failed to fetch service registry", error=str(e))
            raise ServiceUnavailableError(f"Could not fetch service registry: {e}")

    async def get_platform_health(self) -> PlatformHealth:
        """Get comprehensive platform health status"""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/platform-status")
                response.raise_for_status()

                data = response.json()
                self._track_request_time(time.time() - start_time)

                # Parse platform metrics
                metrics = data.get("platform_metrics", {})
                services_data = data.get("services", {})

                # Build service health objects
                services = {}
                unhealthy_services = []

                for service_name, service_info in services_data.items():
                    status = ServiceStatus(service_info.get("status", "unknown"))
                    if status != ServiceStatus.HEALTHY:
                        unhealthy_services.append(service_name)

                    services[service_name] = ServiceHealth(
                        service_name=service_name,
                        status=status,
                        url=service_info.get("url", ""),
                        capabilities=service_info.get("capabilities", []),
                        last_health_check=datetime.fromisoformat(
                            service_info.get("last_health_check", datetime.now().isoformat()).replace("Z", "+00:00")
                        ),
                        response_time=service_info.get("response_time"),
                        error_message=service_info.get("error_message")
                    )

                # Determine overall status
                healthy_count = metrics.get("healthy_services", 0)
                total_count = metrics.get("total_services", 0)

                if healthy_count == total_count:
                    overall_status = ServiceStatus.HEALTHY
                elif healthy_count > total_count * 0.8:
                    overall_status = ServiceStatus.WARNING
                else:
                    overall_status = ServiceStatus.ERROR

                return PlatformHealth(
                    overall_status=overall_status,
                    healthy_services=healthy_count,
                    total_services=total_count,
                    unhealthy_services=unhealthy_services,
                    services=services,
                    timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()).replace("Z", "+00:00"))
                )

        except Exception as e:
            self.logger.error("Failed to get platform health", error=str(e))
            raise ServiceUnavailableError(f"Could not get platform health: {e}")

    # Workflow Orchestration

    async def execute_business_intent(
        self,
        intent: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> WorkflowExecution:
        """Execute a business intent through the AI Assistant workflow orchestration"""
        try:
            payload = {
                "intent": intent,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }

            start_time = time.time()
            async with httpx.AsyncClient(headers=self.headers, timeout=timeout or self.timeout) as client:
                # Route through AI Assistant service
                ai_assistant_url = await self._get_service_url("ai-assistant")
                response = await client.post(f"{ai_assistant_url}/api/execute-intent", json=payload)
                response.raise_for_status()

                result = response.json()
                self._track_request_time(time.time() - start_time)

                # Parse workflow execution response
                return WorkflowExecution(
                    workflow_id=result["workflow_id"],
                    workflow_name=f"Business Intent: {intent[:50]}...",
                    status=WorkflowStatus(result["status"]),
                    steps=[
                        WorkflowStep(
                            step_id=step["step_id"],
                            service=step["service"],
                            action=step["action"],
                            parameters=step.get("parameters", {}),
                            status=WorkflowStatus(step["status"])
                        ) for step in result.get("steps", [])
                    ],
                    progress=result.get("progress", 0.0),
                    created_at=datetime.now(),
                    estimated_completion=datetime.fromisoformat(
                        result["estimated_completion"].replace("Z", "+00:00")
                    ) if result.get("estimated_completion") else None
                )

        except Exception as e:
            self.logger.error("Failed to execute business intent", intent=intent, error=str(e))
            raise ServiceUnavailableError(f"Could not execute business intent: {e}")

    async def create_workflow(
        self,
        workflow_name: str,
        steps: List[Dict[str, Any]]
    ) -> WorkflowExecution:
        """Create a custom workflow with specified steps"""
        try:
            payload = {
                "workflow_name": workflow_name,
                "steps": steps
            }

            start_time = time.time()
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/create-workflow", json=payload)
                response.raise_for_status()

                result = response.json()
                self._track_request_time(time.time() - start_time)

                # Convert to WorkflowExecution object
                workflow_steps = [
                    WorkflowStep(
                        step_id=step["step_id"],
                        service=step["service"],
                        action=step["action"],
                        parameters=step.get("parameters", {}),
                        depends_on=step.get("depends_on"),
                        status=WorkflowStatus.PENDING
                    ) for step in steps
                ]

                return WorkflowExecution(
                    workflow_id=result["workflow_id"],
                    workflow_name=workflow_name,
                    status=WorkflowStatus.PENDING,
                    steps=workflow_steps,
                    progress=0.0,
                    created_at=datetime.now()
                )

        except Exception as e:
            self.logger.error("Failed to create workflow", workflow_name=workflow_name, error=str(e))
            raise ServiceUnavailableError(f"Could not create workflow: {e}")

    async def get_workflow_status(self, workflow_id: str) -> WorkflowExecution:
        """Get current status of a workflow"""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/workflow/{workflow_id}/status")
                response.raise_for_status()

                data = response.json()
                self._track_request_time(time.time() - start_time)

                # Parse workflow status
                steps = []
                for step_data in data.get("steps", []):
                    step = WorkflowStep(
                        step_id=step_data["step_id"],
                        service=step_data["service"],
                        action=step_data["action"],
                        parameters=step_data.get("parameters", {}),
                        depends_on=step_data.get("depends_on"),
                        status=WorkflowStatus(step_data["status"]),
                        result=step_data.get("result"),
                        error=step_data.get("error"),
                        execution_time=step_data.get("execution_time")
                    )
                    steps.append(step)

                return WorkflowExecution(
                    workflow_id=workflow_id,
                    workflow_name=data.get("workflow_name", "Unknown"),
                    status=WorkflowStatus(data["status"]),
                    steps=steps,
                    progress=data.get("progress", 0.0),
                    created_at=datetime.fromisoformat(
                        data["created_at"].replace("Z", "+00:00")
                    ) if data.get("created_at") else datetime.now(),
                    started_at=datetime.fromisoformat(
                        data["started_at"].replace("Z", "+00:00")
                    ) if data.get("started_at") else None,
                    completed_at=datetime.fromisoformat(
                        data["completed_at"].replace("Z", "+00:00")
                    ) if data.get("completed_at") else None,
                    results=data.get("results")
                )

        except Exception as e:
            self.logger.error("Failed to get workflow status", workflow_id=workflow_id, error=str(e))
            raise ServiceUnavailableError(f"Could not get workflow status: {e}")

    # Real-time Communication

    async def connect_websocket(self, auto_reconnect: bool = True) -> None:
        """Connect to platform WebSocket for real-time updates"""
        ws_url = self.base_url.replace("https://", "wss://").replace("http://", "ws://")

        try:
            self._ws_connection = await websockets.connect(
                f"{ws_url}/ws/platform",
                extra_headers={"Authorization": f"Bearer {self.api_key}"}
            )

            # Authenticate WebSocket connection
            await self._ws_connection.send(json.dumps({
                "type": "auth",
                "token": self.api_key
            }))

            self.logger.info("WebSocket connected successfully")

            # Start listening for messages
            asyncio.create_task(self._websocket_listener(auto_reconnect))

        except Exception as e:
            self.logger.error("Failed to connect WebSocket", error=str(e))
            raise ServiceUnavailableError(f"Could not connect to WebSocket: {e}")

    async def _websocket_listener(self, auto_reconnect: bool) -> None:
        """Listen for WebSocket messages and dispatch to callbacks"""
        while True:
            try:
                if not self._ws_connection:
                    break

                message = await self._ws_connection.recv()
                data = json.loads(message)

                # Dispatch to registered callbacks
                for callback in self._event_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(data)
                        else:
                            callback(data)
                    except Exception as e:
                        self.logger.error("Event callback failed", error=str(e))

            except websockets.exceptions.ConnectionClosed:
                self.logger.warning("WebSocket connection closed")
                if auto_reconnect:
                    await asyncio.sleep(5)
                    try:
                        await self.connect_websocket(auto_reconnect)
                    except Exception as e:
                        self.logger.error("Failed to reconnect WebSocket", error=str(e))
                break
            except Exception as e:
                self.logger.error("WebSocket listener error", error=str(e))
                break

    def subscribe_to_events(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe to real-time platform events"""
        self._event_callbacks.append(callback)
        self.logger.info("Event callback registered", callback_count=len(self._event_callbacks))

    async def send_websocket_message(self, message: Dict[str, Any]) -> None:
        """Send a message through the WebSocket connection"""
        if not self._ws_connection:
            raise ServiceUnavailableError("WebSocket not connected")

        try:
            await self._ws_connection.send(json.dumps(message))
        except Exception as e:
            self.logger.error("Failed to send WebSocket message", error=str(e))
            raise ServiceUnavailableError(f"Could not send WebSocket message: {e}")

    # Performance Analytics and Dashboard Data

    async def get_dashboard_overview(self) -> DashboardOverview:
        """Get comprehensive dashboard overview data"""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/dashboard-overview")
                response.raise_for_status()

                data = response.json()
                self._track_request_time(time.time() - start_time)

                # Parse platform health
                health_data = data["platform_health"]
                platform_health = PlatformHealth(
                    overall_status=ServiceStatus(health_data["overall_status"]),
                    healthy_services=health_data["healthy_services"],
                    total_services=health_data["total_services"],
                    unhealthy_services=health_data["unhealthy_services"],
                    services={},  # Populated separately if needed
                    timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                )

                # Parse performance metrics
                perf_data = data["performance"]
                cost_data = data["cost_metrics"]
                performance_metrics = PerformanceMetrics(
                    average_response_time=perf_data["average_response_time"],
                    requests_per_minute=perf_data["requests_per_minute"],
                    success_rate=perf_data["success_rate"],
                    ai_routing_efficiency=data["ai_routing"]["abacus_percentage"],
                    cost_savings_percentage=cost_data["savings_percentage"],
                    total_cost_today=float(cost_data["total_cost_today"].replace("$", "")),
                    projected_monthly_cost=float(cost_data["projected_monthly"].replace("$", ""))
                )

                return DashboardOverview(
                    platform_health=platform_health,
                    active_workflows=data["active_workflows"],
                    completed_today=data["completed_today"],
                    cost_metrics=performance_metrics,
                    ai_routing_distribution=data["ai_routing"],
                    timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                )

        except Exception as e:
            self.logger.error("Failed to get dashboard overview", error=str(e))
            raise ServiceUnavailableError(f"Could not get dashboard overview: {e}")

    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Get detailed performance metrics"""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/performance-metrics")
                response.raise_for_status()

                data = response.json()
                self._track_request_time(time.time() - start_time)

                return PerformanceMetrics(
                    average_response_time=data["average_response_time"],
                    requests_per_minute=data["requests_per_minute"],
                    success_rate=data["success_rate"],
                    ai_routing_efficiency=data["ai_routing_efficiency"],
                    cost_savings_percentage=data["cost_savings_percentage"],
                    total_cost_today=data["total_cost_today"],
                    projected_monthly_cost=data["projected_monthly_cost"]
                )

        except Exception as e:
            self.logger.error("Failed to get performance metrics", error=str(e))
            raise ServiceUnavailableError(f"Could not get performance metrics: {e}")

    # Circuit Breaker Management

    async def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current circuit breaker status across all services"""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/circuit-breaker-status")
                response.raise_for_status()

                data = response.json()
                self._track_request_time(time.time() - start_time)

                self._circuit_breakers = data["circuit_breakers"]
                return self._circuit_breakers

        except Exception as e:
            self.logger.error("Failed to get circuit breaker status", error=str(e))
            raise ServiceUnavailableError(f"Could not get circuit breaker status: {e}")

    async def reset_circuit_breaker(self, service_name: str, breaker_name: str) -> bool:
        """Reset a specific circuit breaker"""
        try:
            payload = {
                "service": service_name,
                "circuit_breaker": breaker_name,
                "action": "reset"
            }

            start_time = time.time()
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/circuit-breaker-control", json=payload)
                response.raise_for_status()

                self._track_request_time(time.time() - start_time)
                return response.json()["success"]

        except Exception as e:
            self.logger.error("Failed to reset circuit breaker",
                            service=service_name, breaker=breaker_name, error=str(e))
            return False

    # Service Communication Helpers

    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        payload: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make a direct call to a specific service"""
        try:
            service_url = await self._get_service_url(service_name)
            url = f"{service_url}/{endpoint.lstrip('/')}"

            start_time = time.time()
            async with httpx.AsyncClient(headers=self.headers, timeout=timeout or self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=payload)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=payload)
                elif method.upper() == "DELETE":
                    response = await client.delete(url)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                self._track_request_time(time.time() - start_time)

                return response.json()

        except Exception as e:
            self.logger.error("Service call failed",
                            service=service_name, endpoint=endpoint, error=str(e))
            raise ServiceUnavailableError(f"Could not call {service_name}: {e}")

    async def execute_service_action(
        self,
        service_name: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        workflow_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a standardized action on a service via the /execute endpoint"""
        payload = {
            "action": action,
            "parameters": parameters or {},
            "workflow_context": workflow_context or {}
        }

        return await self.call_service(service_name, "/execute", "POST", payload)

    # Utility Methods

    async def _get_service_url(self, service_name: str) -> str:
        """Get the URL for a specific service"""
        services = await self.get_service_registry()

        if service_name in services:
            return services[service_name].url

        # Fallback to default URL pattern
        return f"https://xynergy-{service_name}.us-central1.run.app"

    def _track_request_time(self, duration: float) -> None:
        """Track request timing for performance monitoring"""
        self._request_times.append(duration)

        # Keep only recent measurements (last 100)
        if len(self._request_times) > 100:
            self._request_times = self._request_times[-100:]

    def get_sdk_performance_stats(self) -> Dict[str, float]:
        """Get SDK performance statistics"""
        if not self._request_times:
            return {
                "average_request_time": 0.0,
                "min_request_time": 0.0,
                "max_request_time": 0.0,
                "total_requests": 0
            }

        return {
            "average_request_time": sum(self._request_times) / len(self._request_times),
            "min_request_time": min(self._request_times),
            "max_request_time": max(self._request_times),
            "total_requests": len(self._request_times)
        }

# Convenience factory function
async def create_xynergy_sdk(api_key: str, base_url: str = None) -> XynergyPlatformSDK:
    """
    Factory function to create and initialize the Xynergy Platform SDK

    Args:
        api_key: Your Xynergy Platform API key
        base_url: Optional base URL override

    Returns:
        Initialized XynergyPlatformSDK instance
    """
    sdk = XynergyPlatformSDK(
        api_key=api_key,
        base_url=base_url or "https://xynergy-platform-dashboard.us-central1.run.app"
    )

    # Verify authentication
    if not await sdk.verify_authentication():
        raise AuthenticationError("Invalid API key or authentication failed")

    return sdk

# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Example usage
        api_key = "your_api_key_here"

        async with XynergyPlatformSDK(api_key) as sdk:
            # Get platform health
            health = await sdk.get_platform_health()
            print(f"Platform Status: {health.overall_status}")
            print(f"Healthy Services: {health.healthy_services}/{health.total_services}")

            # Execute business intent
            workflow = await sdk.execute_business_intent(
                "Create a marketing campaign for sustainable fashion",
                context={"budget": "$25000", "timeline": "Q2 2025"}
            )
            print(f"Workflow ID: {workflow.workflow_id}")

            # Monitor workflow progress
            status = await sdk.get_workflow_status(workflow.workflow_id)
            print(f"Workflow Progress: {status.progress}%")

            # Get dashboard overview
            overview = await sdk.get_dashboard_overview()
            print(f"Active Workflows: {overview.active_workflows}")
            print(f"Cost Savings: {overview.cost_metrics.cost_savings_percentage}%")

    # Run example
    # asyncio.run(main())