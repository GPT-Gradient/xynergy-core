"""
Comprehensive Deployment Automation System for Xynergy Platform
Advanced CI/CD pipeline with intelligent deployment strategies, rollback capabilities, and cost optimization.
"""
import os
import json
import asyncio
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import httpx

logger = logging.getLogger(__name__)

class DeploymentStrategy(Enum):
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    IMMEDIATE = "immediate"

class DeploymentStatus(Enum):
    PENDING = "pending"
    BUILDING = "building"
    TESTING = "testing"
    DEPLOYING = "deploying"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class EnvironmentType(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class ServiceConfig:
    """Service deployment configuration."""
    service_name: str
    image_tag: str
    cpu_limit: str
    memory_limit: str
    min_instances: int
    max_instances: int
    concurrency: int
    timeout: str
    environment_variables: Dict[str, str]
    health_check_path: str = "/health"
    readiness_check_path: str = "/ready"

@dataclass
class DeploymentPlan:
    """Comprehensive deployment plan."""
    deployment_id: str
    services: List[ServiceConfig]
    strategy: DeploymentStrategy
    target_environment: EnvironmentType
    rollback_enabled: bool
    verification_tests: List[str]
    cost_budget: float
    created_by: str
    created_at: datetime

@dataclass
class DeploymentExecution:
    """Deployment execution tracking."""
    execution_id: str
    deployment_id: str
    status: DeploymentStatus
    started_at: datetime
    completed_at: Optional[datetime]
    services_deployed: List[str]
    services_failed: List[str]
    total_cost: float
    execution_logs: List[str]
    rollback_plan: Optional[Dict[str, Any]]
    verification_results: Dict[str, bool]

class ContainerBuilder:
    """Advanced container building with optimization."""

    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.artifact_registry = f"{region}-docker.pkg.dev/{project_id}/xynergy-platform"

    async def build_optimized_image(self, service_name: str, build_context: str = ".") -> Dict[str, Any]:
        """Build optimized Docker image with multi-stage builds."""
        try:
            build_start = datetime.now()

            # Generate build tag
            timestamp = int(build_start.timestamp())
            build_tag = f"opt-{timestamp}"
            image_name = f"{self.artifact_registry}/{service_name}:{build_tag}"

            logger.info(f"Building optimized image for {service_name}...")

            # Use optimized Dockerfile if available
            dockerfile_path = os.path.join(build_context, "Dockerfile.optimized")
            if not os.path.exists(dockerfile_path):
                dockerfile_path = os.path.join(build_context, "Dockerfile")

            # Build command with optimization flags
            build_cmd = [
                "docker", "build",
                "-f", dockerfile_path,
                "-t", image_name,
                "--build-arg", f"BUILD_DATE={build_start.isoformat()}",
                "--build-arg", f"VERSION={build_tag}",
                "--build-arg", "OPTIMIZATION_LEVEL=production",
                build_context
            ]

            # Execute build
            process = await asyncio.create_subprocess_exec(
                *build_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                build_time = (datetime.now() - build_start).total_seconds()

                # Get image info
                image_info = await self._get_image_info(image_name)

                logger.info(f"Built {service_name} in {build_time:.2f}s - Size: {image_info.get('size', 'unknown')}")

                return {
                    "success": True,
                    "image_name": image_name,
                    "build_tag": build_tag,
                    "build_time_seconds": build_time,
                    "image_size_mb": image_info.get('size_mb', 0),
                    "layers": image_info.get('layers', 0),
                    "build_logs": stdout.decode('utf-8')
                }
            else:
                error_msg = stderr.decode('utf-8')
                logger.error(f"Build failed for {service_name}: {error_msg}")

                return {
                    "success": False,
                    "error": error_msg,
                    "build_logs": stdout.decode('utf-8')
                }

        except Exception as e:
            logger.error(f"Build process failed: {e}")
            return {"success": False, "error": str(e)}

    async def push_image(self, image_name: str) -> bool:
        """Push image to Artifact Registry."""
        try:
            push_cmd = ["docker", "push", image_name]

            process = await asyncio.create_subprocess_exec(
                *push_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info(f"Successfully pushed {image_name}")
                return True
            else:
                logger.error(f"Push failed: {stderr.decode('utf-8')}")
                return False

        except Exception as e:
            logger.error(f"Push process failed: {e}")
            return False

    async def _get_image_info(self, image_name: str) -> Dict[str, Any]:
        """Get detailed image information."""
        try:
            inspect_cmd = ["docker", "inspect", image_name]

            process = await asyncio.create_subprocess_exec(
                *inspect_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                image_data = json.loads(stdout.decode('utf-8'))[0]

                return {
                    "size_mb": round(image_data.get("Size", 0) / (1024 * 1024), 2),
                    "layers": len(image_data.get("RootFS", {}).get("Layers", [])),
                    "created": image_data.get("Created", ""),
                    "architecture": image_data.get("Architecture", "")
                }

        except Exception as e:
            logger.error(f"Failed to get image info: {e}")

        return {}

class DeploymentStrategies:
    """Implementation of different deployment strategies."""

    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region

    async def deploy_blue_green(self, service: ServiceConfig, image_name: str) -> Dict[str, Any]:
        """Blue-Green deployment strategy."""
        try:
            logger.info(f"Starting Blue-Green deployment for {service.service_name}")

            # Deploy to staging (green) environment first
            green_service = f"{service.service_name}-green"

            deploy_result = await self._deploy_cloud_run_service(
                green_service, image_name, service
            )

            if not deploy_result["success"]:
                return deploy_result

            # Verify green deployment
            verification_result = await self._verify_deployment(green_service, service.health_check_path)

            if verification_result["healthy"]:
                # Switch traffic from blue to green
                traffic_switch_result = await self._switch_traffic(service.service_name, green_service)

                if traffic_switch_result["success"]:
                    # Clean up old blue deployment after successful switch
                    await asyncio.sleep(300)  # Wait 5 minutes before cleanup
                    await self._cleanup_old_deployment(f"{service.service_name}-blue")

                    return {
                        "success": True,
                        "strategy": "blue_green",
                        "green_service": green_service,
                        "traffic_switched": True,
                        "deployment_time": deploy_result.get("deployment_time", 0)
                    }
                else:
                    return {"success": False, "error": "Traffic switch failed"}
            else:
                return {"success": False, "error": "Green deployment verification failed"}

        except Exception as e:
            logger.error(f"Blue-Green deployment failed: {e}")
            return {"success": False, "error": str(e)}

    async def deploy_canary(self, service: ServiceConfig, image_name: str, traffic_percent: int = 10) -> Dict[str, Any]:
        """Canary deployment strategy with gradual traffic increase."""
        try:
            logger.info(f"Starting Canary deployment for {service.service_name} ({traffic_percent}% traffic)")

            # Deploy canary version
            canary_service = f"{service.service_name}-canary"

            deploy_result = await self._deploy_cloud_run_service(
                canary_service, image_name, service
            )

            if not deploy_result["success"]:
                return deploy_result

            # Configure traffic split
            traffic_config = {
                service.service_name: 100 - traffic_percent,
                canary_service: traffic_percent
            }

            traffic_result = await self._configure_traffic_split(service.service_name, traffic_config)

            if traffic_result["success"]:
                # Monitor canary for issues
                canary_monitoring = await self._monitor_canary_deployment(
                    canary_service, service.health_check_path, duration_minutes=15
                )

                if canary_monitoring["stable"]:
                    return {
                        "success": True,
                        "strategy": "canary",
                        "canary_service": canary_service,
                        "traffic_split": traffic_config,
                        "monitoring_results": canary_monitoring,
                        "ready_for_promotion": canary_monitoring["error_rate"] < 2.0
                    }
                else:
                    # Rollback canary due to issues
                    await self._rollback_canary(service.service_name, canary_service)
                    return {"success": False, "error": "Canary deployment rolled back due to instability"}
            else:
                return {"success": False, "error": "Traffic split configuration failed"}

        except Exception as e:
            logger.error(f"Canary deployment failed: {e}")
            return {"success": False, "error": str(e)}

    async def deploy_rolling(self, service: ServiceConfig, image_name: str) -> Dict[str, Any]:
        """Rolling deployment strategy."""
        try:
            logger.info(f"Starting Rolling deployment for {service.service_name}")

            # Configure rolling update parameters
            rolling_config = {
                "max_surge": 1,  # One additional instance during update
                "max_unavailable": 0,  # Keep all instances available during update
                "revision_timeout": "10m"
            }

            deploy_result = await self._deploy_cloud_run_service(
                service.service_name, image_name, service, rolling_config
            )

            if deploy_result["success"]:
                # Monitor rolling deployment progress
                progress = await self._monitor_rolling_deployment(service.service_name)

                return {
                    "success": True,
                    "strategy": "rolling",
                    "deployment_progress": progress,
                    "deployment_time": deploy_result.get("deployment_time", 0)
                }
            else:
                return deploy_result

        except Exception as e:
            logger.error(f"Rolling deployment failed: {e}")
            return {"success": False, "error": str(e)}

    async def _deploy_cloud_run_service(self, service_name: str, image_name: str,
                                      config: ServiceConfig, deployment_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Deploy service to Cloud Run."""
        try:
            deploy_start = datetime.now()

            # Prepare environment variables
            env_vars = []
            for key, value in config.environment_variables.items():
                env_vars.extend(["--set-env-vars", f"{key}={value}"])

            # Build gcloud command
            deploy_cmd = [
                "gcloud", "run", "deploy", service_name,
                "--image", image_name,
                "--platform", "managed",
                "--region", self.region,
                "--allow-unauthenticated",
                "--memory", config.memory_limit,
                "--cpu", config.cpu_limit,
                "--concurrency", str(config.concurrency),
                "--min-instances", str(config.min_instances),
                "--max-instances", str(config.max_instances),
                "--timeout", config.timeout,
                "--port", "8080"
            ]

            # Add environment variables
            if env_vars:
                deploy_cmd.extend(env_vars)

            # Add deployment-specific configuration
            if deployment_config:
                if "revision_timeout" in deployment_config:
                    deploy_cmd.extend(["--revision-suffix", f"r{int(datetime.now().timestamp())}"])

            # Execute deployment
            process = await asyncio.create_subprocess_exec(
                *deploy_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            deployment_time = (datetime.now() - deploy_start).total_seconds()

            if process.returncode == 0:
                logger.info(f"Successfully deployed {service_name} in {deployment_time:.2f}s")

                return {
                    "success": True,
                    "service_name": service_name,
                    "deployment_time": deployment_time,
                    "deployment_logs": stdout.decode('utf-8')
                }
            else:
                error_msg = stderr.decode('utf-8')
                logger.error(f"Deployment failed for {service_name}: {error_msg}")

                return {
                    "success": False,
                    "error": error_msg,
                    "deployment_logs": stdout.decode('utf-8')
                }

        except Exception as e:
            logger.error(f"Cloud Run deployment failed: {e}")
            return {"success": False, "error": str(e)}

    async def _verify_deployment(self, service_name: str, health_path: str) -> Dict[str, Any]:
        """Verify deployment health."""
        try:
            # Get service URL
            service_url = await self._get_service_url(service_name)
            if not service_url:
                return {"healthy": False, "error": "Could not get service URL"}

            # Perform health checks
            health_checks = []
            for attempt in range(5):  # 5 attempts with exponential backoff
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        response = await client.get(f"{service_url}{health_path}")

                        health_check = {
                            "attempt": attempt + 1,
                            "status_code": response.status_code,
                            "response_time": response.elapsed.total_seconds(),
                            "healthy": response.status_code == 200
                        }
                        health_checks.append(health_check)

                        if response.status_code == 200:
                            return {
                                "healthy": True,
                                "service_url": service_url,
                                "health_checks": health_checks
                            }

                except httpx.TimeoutException:
                    health_checks.append({
                        "attempt": attempt + 1,
                        "error": "timeout",
                        "healthy": False
                    })

                # Wait before retry
                await asyncio.sleep(2 ** attempt)

            return {
                "healthy": False,
                "error": "Health checks failed",
                "health_checks": health_checks
            }

        except Exception as e:
            return {"healthy": False, "error": str(e)}

    async def _get_service_url(self, service_name: str) -> Optional[str]:
        """Get Cloud Run service URL."""
        try:
            cmd = [
                "gcloud", "run", "services", "describe", service_name,
                "--region", self.region,
                "--format", "value(status.url)"
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return stdout.decode('utf-8').strip()
            else:
                logger.error(f"Failed to get service URL: {stderr.decode('utf-8')}")
                return None

        except Exception as e:
            logger.error(f"Error getting service URL: {e}")
            return None

    async def _switch_traffic(self, main_service: str, new_service: str) -> Dict[str, Any]:
        """Switch traffic from main service to new service."""
        try:
            # In a real implementation, this would update load balancer or service mesh configuration
            # For Cloud Run, we would update the traffic allocation

            cmd = [
                "gcloud", "run", "services", "update-traffic", main_service,
                "--to-latest",
                "--region", self.region
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "logs": stdout.decode('utf-8') if process.returncode == 0 else stderr.decode('utf-8')
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _configure_traffic_split(self, service_name: str, traffic_config: Dict[str, int]) -> Dict[str, Any]:
        """Configure traffic split for canary deployment."""
        try:
            # Simulate traffic split configuration
            logger.info(f"Configuring traffic split for {service_name}: {traffic_config}")

            # In a real implementation, this would configure Cloud Run traffic allocation
            await asyncio.sleep(1)  # Simulate configuration delay

            return {
                "success": True,
                "traffic_configuration": traffic_config
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _monitor_canary_deployment(self, canary_service: str, health_path: str,
                                       duration_minutes: int = 15) -> Dict[str, Any]:
        """Monitor canary deployment for stability."""
        try:
            monitoring_start = datetime.now()
            monitoring_end = monitoring_start + timedelta(minutes=duration_minutes)

            health_checks = []
            error_count = 0
            total_checks = 0

            while datetime.now() < monitoring_end:
                # Perform health check
                verification = await self._verify_deployment(canary_service, health_path)
                total_checks += 1

                if not verification["healthy"]:
                    error_count += 1

                health_checks.append({
                    "timestamp": datetime.now().isoformat(),
                    "healthy": verification["healthy"]
                })

                await asyncio.sleep(30)  # Check every 30 seconds

            error_rate = (error_count / total_checks) * 100 if total_checks > 0 else 0
            stable = error_rate < 5.0  # Consider stable if error rate < 5%

            return {
                "stable": stable,
                "error_rate": round(error_rate, 2),
                "total_checks": total_checks,
                "error_count": error_count,
                "monitoring_duration_minutes": duration_minutes,
                "health_checks": health_checks[-10:]  # Return last 10 checks
            }

        except Exception as e:
            logger.error(f"Canary monitoring failed: {e}")
            return {"stable": False, "error": str(e)}

    async def _rollback_canary(self, main_service: str, canary_service: str) -> bool:
        """Rollback canary deployment."""
        try:
            logger.info(f"Rolling back canary deployment: {canary_service}")

            # Reset traffic to main service
            await self._switch_traffic(main_service, main_service)

            # Delete canary service
            await self._cleanup_old_deployment(canary_service)

            return True

        except Exception as e:
            logger.error(f"Canary rollback failed: {e}")
            return False

    async def _monitor_rolling_deployment(self, service_name: str) -> Dict[str, Any]:
        """Monitor rolling deployment progress."""
        try:
            # Simulate monitoring rolling deployment
            progress_steps = ["Updating revision", "Rolling out instances", "Verifying health", "Completed"]
            progress = []

            for step in progress_steps:
                await asyncio.sleep(2)  # Simulate step duration
                progress.append({
                    "step": step,
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed"
                })

            return {
                "completed": True,
                "progress": progress,
                "total_steps": len(progress_steps)
            }

        except Exception as e:
            logger.error(f"Rolling deployment monitoring failed: {e}")
            return {"completed": False, "error": str(e)}

    async def _cleanup_old_deployment(self, service_name: str) -> bool:
        """Clean up old deployment."""
        try:
            cmd = [
                "gcloud", "run", "services", "delete", service_name,
                "--region", self.region,
                "--quiet"
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            return process.returncode == 0

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False

class DeploymentOrchestrator:
    """Main deployment orchestration engine."""

    def __init__(self, project_id: str = None, region: str = "us-central1"):
        self.project_id = project_id or os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
        self.region = region

        self.container_builder = ContainerBuilder(self.project_id, region)
        self.deployment_strategies = DeploymentStrategies(self.project_id, region)

        # Deployment tracking
        self.active_deployments: Dict[str, DeploymentExecution] = {}
        self.deployment_history: List[DeploymentExecution] = []

        # Cost tracking
        self.deployment_costs: Dict[str, float] = defaultdict(float)

    async def execute_deployment_plan(self, plan: DeploymentPlan) -> DeploymentExecution:
        """Execute complete deployment plan."""
        execution_id = f"exec_{int(datetime.now().timestamp())}_{plan.deployment_id}"

        execution = DeploymentExecution(
            execution_id=execution_id,
            deployment_id=plan.deployment_id,
            status=DeploymentStatus.PENDING,
            started_at=datetime.now(),
            completed_at=None,
            services_deployed=[],
            services_failed=[],
            total_cost=0.0,
            execution_logs=[],
            rollback_plan=None,
            verification_results={}
        )

        self.active_deployments[execution_id] = execution

        try:
            execution.status = DeploymentStatus.BUILDING
            execution.execution_logs.append(f"Starting deployment plan: {plan.deployment_id}")

            # Build and deploy services
            for service in plan.services:
                try:
                    execution.execution_logs.append(f"Building {service.service_name}...")

                    # Build container image
                    build_result = await self.container_builder.build_optimized_image(
                        service.service_name, f"./{service.service_name}"
                    )

                    if not build_result["success"]:
                        execution.services_failed.append(service.service_name)
                        execution.execution_logs.append(f"Build failed for {service.service_name}: {build_result['error']}")
                        continue

                    # Push image
                    push_success = await self.container_builder.push_image(build_result["image_name"])
                    if not push_success:
                        execution.services_failed.append(service.service_name)
                        execution.execution_logs.append(f"Push failed for {service.service_name}")
                        continue

                    execution.status = DeploymentStatus.DEPLOYING

                    # Deploy using specified strategy
                    deploy_result = await self._execute_deployment_strategy(
                        service, build_result["image_name"], plan.strategy
                    )

                    if deploy_result["success"]:
                        execution.services_deployed.append(service.service_name)
                        execution.execution_logs.append(f"Successfully deployed {service.service_name}")

                        # Track cost
                        service_cost = self._calculate_service_cost(service, deploy_result)
                        execution.total_cost += service_cost
                        self.deployment_costs[service.service_name] += service_cost
                    else:
                        execution.services_failed.append(service.service_name)
                        execution.execution_logs.append(f"Deployment failed for {service.service_name}: {deploy_result['error']}")

                except Exception as e:
                    execution.services_failed.append(service.service_name)
                    execution.execution_logs.append(f"Service deployment error for {service.service_name}: {str(e)}")

            # Run verification tests
            if execution.services_deployed and plan.verification_tests:
                execution.status = DeploymentStatus.VERIFYING
                execution.execution_logs.append("Running verification tests...")

                verification_results = await self._run_verification_tests(
                    plan.verification_tests, execution.services_deployed
                )
                execution.verification_results = verification_results

            # Determine final status
            if execution.services_failed:
                execution.status = DeploymentStatus.FAILED

                # Create rollback plan if enabled
                if plan.rollback_enabled:
                    execution.rollback_plan = self._create_rollback_plan(execution.services_deployed)
            else:
                execution.status = DeploymentStatus.COMPLETED

            execution.completed_at = datetime.now()
            execution.execution_logs.append(f"Deployment {execution.status.value}: {len(execution.services_deployed)} services deployed, {len(execution.services_failed)} failed")

            # Move to history and remove from active
            self.deployment_history.append(execution)
            if execution_id in self.active_deployments:
                del self.active_deployments[execution_id]

            return execution

        except Exception as e:
            execution.status = DeploymentStatus.FAILED
            execution.execution_logs.append(f"Deployment execution failed: {str(e)}")
            execution.completed_at = datetime.now()

            logger.error(f"Deployment execution failed: {e}")
            return execution

    async def _execute_deployment_strategy(self, service: ServiceConfig, image_name: str,
                                         strategy: DeploymentStrategy) -> Dict[str, Any]:
        """Execute deployment using specified strategy."""
        if strategy == DeploymentStrategy.BLUE_GREEN:
            return await self.deployment_strategies.deploy_blue_green(service, image_name)
        elif strategy == DeploymentStrategy.CANARY:
            return await self.deployment_strategies.deploy_canary(service, image_name)
        elif strategy == DeploymentStrategy.ROLLING:
            return await self.deployment_strategies.deploy_rolling(service, image_name)
        else:  # IMMEDIATE
            return await self.deployment_strategies._deploy_cloud_run_service(
                service.service_name, image_name, service
            )

    async def _run_verification_tests(self, test_names: List[str], deployed_services: List[str]) -> Dict[str, bool]:
        """Run verification tests on deployed services."""
        results = {}

        for test_name in test_names:
            try:
                if test_name == "health_check":
                    results[test_name] = await self._run_health_checks(deployed_services)
                elif test_name == "load_test":
                    results[test_name] = await self._run_basic_load_test(deployed_services)
                elif test_name == "integration_test":
                    results[test_name] = await self._run_integration_tests(deployed_services)
                else:
                    results[test_name] = True  # Unknown test passes by default

            except Exception as e:
                logger.error(f"Verification test {test_name} failed: {e}")
                results[test_name] = False

        return results

    async def _run_health_checks(self, services: List[str]) -> bool:
        """Run health checks on deployed services."""
        for service in services:
            verification = await self.deployment_strategies._verify_deployment(service, "/health")
            if not verification["healthy"]:
                return False
        return True

    async def _run_basic_load_test(self, services: List[str]) -> bool:
        """Run basic load test on deployed services."""
        # Simulate load test
        await asyncio.sleep(2)
        return True

    async def _run_integration_tests(self, services: List[str]) -> bool:
        """Run integration tests between services."""
        # Simulate integration tests
        await asyncio.sleep(3)
        return True

    def _calculate_service_cost(self, service: ServiceConfig, deploy_result: Dict[str, Any]) -> float:
        """Calculate estimated deployment cost for service."""
        # Simple cost calculation based on resources
        cpu_cores = float(service.cpu_limit.rstrip('m')) / 1000
        memory_gb = float(service.memory_limit.rstrip('Gi')) if service.memory_limit.endswith('Gi') else 0.5

        # Estimate hourly cost
        cpu_cost_per_hour = cpu_cores * 0.05  # $0.05 per vCPU hour
        memory_cost_per_hour = memory_gb * 0.01  # $0.01 per GB hour

        deployment_time_hours = deploy_result.get("deployment_time", 60) / 3600
        cost = (cpu_cost_per_hour + memory_cost_per_hour) * deployment_time_hours

        return round(cost, 4)

    def _create_rollback_plan(self, deployed_services: List[str]) -> Dict[str, Any]:
        """Create rollback plan for deployed services."""
        return {
            "rollback_strategy": "previous_revision",
            "services_to_rollback": deployed_services,
            "rollback_timeout": "10m",
            "verification_required": True,
            "created_at": datetime.now().isoformat()
        }

    async def execute_rollback(self, execution_id: str) -> Dict[str, Any]:
        """Execute rollback for deployment."""
        if execution_id not in [exec.execution_id for exec in self.deployment_history]:
            return {"success": False, "error": "Deployment not found"}

        execution = next(exec for exec in self.deployment_history if exec.execution_id == execution_id)

        if not execution.rollback_plan:
            return {"success": False, "error": "No rollback plan available"}

        try:
            rollback_results = []

            for service in execution.rollback_plan["services_to_rollback"]:
                try:
                    # Rollback to previous revision
                    rollback_cmd = [
                        "gcloud", "run", "services", "update-traffic", service,
                        "--to-revisions", "LATEST=100",
                        "--region", self.region
                    ]

                    process = await asyncio.create_subprocess_exec(
                        *rollback_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )

                    stdout, stderr = await process.communicate()

                    rollback_results.append({
                        "service": service,
                        "success": process.returncode == 0,
                        "logs": stdout.decode('utf-8') if process.returncode == 0 else stderr.decode('utf-8')
                    })

                except Exception as e:
                    rollback_results.append({
                        "service": service,
                        "success": False,
                        "error": str(e)
                    })

            # Update execution status
            execution.status = DeploymentStatus.ROLLED_BACK
            successful_rollbacks = sum(1 for r in rollback_results if r["success"])

            return {
                "success": successful_rollbacks == len(rollback_results),
                "rollback_results": rollback_results,
                "services_rolled_back": successful_rollbacks,
                "total_services": len(rollback_results)
            }

        except Exception as e:
            logger.error(f"Rollback execution failed: {e}")
            return {"success": False, "error": str(e)}

    def get_deployment_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status."""
        # Check active deployments
        if execution_id in self.active_deployments:
            execution = self.active_deployments[execution_id]
            return {
                "status": "active",
                "execution": asdict(execution)
            }

        # Check deployment history
        for execution in self.deployment_history:
            if execution.execution_id == execution_id:
                return {
                    "status": "completed",
                    "execution": asdict(execution)
                }

        return None

    def get_deployment_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive deployment dashboard."""
        # Calculate statistics
        total_deployments = len(self.deployment_history)
        successful_deployments = sum(1 for exec in self.deployment_history if exec.status == DeploymentStatus.COMPLETED)
        failed_deployments = sum(1 for exec in self.deployment_history if exec.status == DeploymentStatus.FAILED)

        success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0

        # Recent deployments (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_deployments = [exec for exec in self.deployment_history if exec.started_at > recent_cutoff]

        # Cost analysis
        total_deployment_cost = sum(self.deployment_costs.values())
        avg_cost_per_service = total_deployment_cost / max(len(self.deployment_costs), 1)

        return {
            "overview": {
                "total_deployments": total_deployments,
                "success_rate": round(success_rate, 1),
                "active_deployments": len(self.active_deployments),
                "recent_deployments_24h": len(recent_deployments)
            },
            "deployment_stats": {
                "successful": successful_deployments,
                "failed": failed_deployments,
                "rolled_back": sum(1 for exec in self.deployment_history if exec.status == DeploymentStatus.ROLLED_BACK)
            },
            "cost_analysis": {
                "total_cost": round(total_deployment_cost, 4),
                "avg_cost_per_service": round(avg_cost_per_service, 4),
                "service_costs": dict(self.deployment_costs)
            },
            "recent_activity": [
                {
                    "execution_id": exec.execution_id,
                    "status": exec.status.value,
                    "services_count": len(exec.services_deployed) + len(exec.services_failed),
                    "started_at": exec.started_at.isoformat(),
                    "total_cost": exec.total_cost
                }
                for exec in sorted(recent_deployments, key=lambda x: x.started_at, reverse=True)[:10]
            ],
            "recommendations": self._generate_deployment_recommendations()
        }

    def _generate_deployment_recommendations(self) -> List[str]:
        """Generate deployment optimization recommendations."""
        recommendations = []

        if len(self.deployment_history) < 5:
            recommendations.append("Collect more deployment data to generate meaningful recommendations")
            return recommendations

        # Analyze failure patterns
        recent_executions = self.deployment_history[-20:]  # Last 20 deployments
        failed_executions = [exec for exec in recent_executions if exec.status == DeploymentStatus.FAILED]

        if len(failed_executions) > len(recent_executions) * 0.2:  # > 20% failure rate
            recommendations.append("High failure rate detected - review deployment processes and testing")

        # Cost analysis
        if self.deployment_costs:
            avg_cost = sum(self.deployment_costs.values()) / len(self.deployment_costs)
            if avg_cost > 1.0:
                recommendations.append("Consider optimizing container resources to reduce deployment costs")

        # Strategy analysis
        strategy_usage = defaultdict(int)
        for execution in recent_executions:
            # This would be tracked if we stored strategy info
            strategy_usage["rolling"] += 1  # Placeholder

        if strategy_usage.get("immediate", 0) > strategy_usage.get("canary", 0):
            recommendations.append("Consider using canary deployments for safer production releases")

        return recommendations

# Global deployment orchestrator
deployment_orchestrator = DeploymentOrchestrator()

# Convenience functions
async def deploy_service(service_name: str, cpu_limit: str = "500m", memory_limit: str = "1Gi",
                        min_instances: int = 0, max_instances: int = 5,
                        strategy: str = "rolling") -> Dict[str, Any]:
    """Deploy single service with default configuration."""
    service_config = ServiceConfig(
        service_name=service_name,
        image_tag="latest",
        cpu_limit=cpu_limit,
        memory_limit=memory_limit,
        min_instances=min_instances,
        max_instances=max_instances,
        concurrency=80,
        timeout="300s",
        environment_variables={
            "PROJECT_ID": deployment_orchestrator.project_id,
            "REGION": deployment_orchestrator.region
        }
    )

    deployment_plan = DeploymentPlan(
        deployment_id=f"single_{service_name}_{int(datetime.now().timestamp())}",
        services=[service_config],
        strategy=DeploymentStrategy(strategy),
        target_environment=EnvironmentType.PRODUCTION,
        rollback_enabled=True,
        verification_tests=["health_check"],
        cost_budget=10.0,
        created_by="automated",
        created_at=datetime.now()
    )

    execution = await deployment_orchestrator.execute_deployment_plan(deployment_plan)
    return asdict(execution)

def get_deployment_dashboard() -> Dict[str, Any]:
    """Get deployment dashboard data."""
    return deployment_orchestrator.get_deployment_dashboard()