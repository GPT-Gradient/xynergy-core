"""
Container Resource Optimization for Xynergy Platform
Optimizes Docker containers and Cloud Run configurations for performance and cost efficiency.
"""
import os
import json
import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ResourceRequirements:
    """Container resource requirements based on service type."""
    cpu: str
    memory: str
    max_instances: int
    min_instances: int
    concurrency: int
    timeout: str

class ContainerOptimizer:
    """Optimizes container configurations for different service types."""

    def __init__(self):
        # Optimized resource allocations by service type
        self.resource_profiles = {
            "ai-intensive": ResourceRequirements(
                cpu="2000m", memory="4Gi", max_instances=10, min_instances=1,
                concurrency=10, timeout="900s"
            ),
            "data-processing": ResourceRequirements(
                cpu="1000m", memory="2Gi", max_instances=20, min_instances=0,
                concurrency=20, timeout="300s"
            ),
            "api-service": ResourceRequirements(
                cpu="500m", memory="1Gi", max_instances=50, min_instances=0,
                concurrency=80, timeout="60s"
            ),
            "background-worker": ResourceRequirements(
                cpu="250m", memory="512Mi", max_instances=5, min_instances=0,
                concurrency=1, timeout="3600s"
            ),
            "dashboard": ResourceRequirements(
                cpu="250m", memory="512Mi", max_instances=10, min_instances=0,
                concurrency=100, timeout="30s"
            )
        }

        # Service type mapping
        self.service_classifications = {
            "ai-routing-engine": "ai-intensive",
            "ai-providers": "ai-intensive",
            "internal-ai-service": "ai-intensive",
            "ai-assistant": "ai-intensive",
            "analytics-data-layer": "data-processing",
            "advanced-analytics": "data-processing",
            "marketing-engine": "data-processing",
            "content-hub": "data-processing",
            "platform-dashboard": "dashboard",
            "executive-dashboard": "dashboard",
            "system-runtime": "api-service",
            "security-governance": "api-service",
            "tenant-management": "api-service",
            "secrets-config": "api-service",
            "qa-engine": "api-service",
            "reports-export": "api-service",
            "project-management": "api-service",
            "scheduler-automation-engine": "background-worker",
            "validation-coordinator": "background-worker",
            "attribution-coordinator": "background-worker",
            "keyword-revenue-tracker": "background-worker"
        }

    def generate_optimized_dockerfile(self, service_name: str, service_type: str = None) -> str:
        """Generate an optimized Dockerfile for a service."""
        profile_type = service_type or self.service_classifications.get(service_name, "api-service")
        profile = self.resource_profiles[profile_type]

        # Multi-stage build for smaller images
        dockerfile_content = f'''# Multi-stage optimized Dockerfile for {service_name}
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies in one layer
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    ca-certificates \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean \\
    && useradd --create-home --shell /bin/bash --uid 1001 appuser

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY main.py phase2_utils.py ./
COPY shared/ ./shared/

# Set ownership and permissions
RUN chown -R appuser:appuser /app
USER appuser

# Update PATH for user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8080

# Optimized healthcheck based on service type'''

        # Add service-type specific healthcheck
        if profile_type == "ai-intensive":
            dockerfile_content += '''
HEALTHCHECK --interval=60s --timeout=30s --start-period=30s --retries=2 \\
    CMD curl -f http://localhost:8080/health || exit 1'''
        elif profile_type == "dashboard":
            dockerfile_content += '''
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1'''
        else:
            dockerfile_content += '''
HEALTHCHECK --interval=45s --timeout=15s --start-period=15s --retries=2 \\
    CMD curl -f http://localhost:8080/health || exit 1'''

        dockerfile_content += '''

# Production-optimized startup
CMD ["python", "-u", "main.py"]
'''

        return dockerfile_content

    def generate_cloud_run_config(self, service_name: str, image_url: str,
                                service_type: str = None) -> Dict[str, Any]:
        """Generate optimized Cloud Run service configuration."""
        profile_type = service_type or self.service_classifications.get(service_name, "api-service")
        profile = self.resource_profiles[profile_type]

        config = {
            "apiVersion": "serving.knative.dev/v1",
            "kind": "Service",
            "metadata": {
                "name": service_name,
                "labels": {
                    "app": service_name,
                    "platform": "xynergy",
                    "optimization": "phase2",
                    "service-type": profile_type
                },
                "annotations": {
                    "run.googleapis.com/ingress": "all",
                    "run.googleapis.com/execution-environment": "gen2"
                }
            },
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "autoscaling.knative.dev/maxScale": str(profile.max_instances),
                            "autoscaling.knative.dev/minScale": str(profile.min_instances),
                            "run.googleapis.com/cpu-throttling": "true" if profile_type != "ai-intensive" else "false",
                            "run.googleapis.com/execution-environment": "gen2"
                        }
                    },
                    "spec": {
                        "containerConcurrency": profile.concurrency,
                        "timeoutSeconds": int(profile.timeout.rstrip('s')),
                        "containers": [{
                            "image": image_url,
                            "ports": [{
                                "containerPort": 8080
                            }],
                            "resources": {
                                "limits": {
                                    "cpu": profile.cpu,
                                    "memory": profile.memory
                                }
                            },
                            "env": [
                                {
                                    "name": "PROJECT_ID",
                                    "value": os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
                                },
                                {
                                    "name": "REGION",
                                    "value": os.getenv("REGION", "us-central1")
                                },
                                {
                                    "name": "OPTIMIZATION_ENABLED",
                                    "value": "true"
                                },
                                {
                                    "name": "SERVICE_TYPE",
                                    "value": profile_type
                                }
                            ]
                        }]
                    }
                }
            }
        }

        # Add specific configurations for AI services
        if profile_type == "ai-intensive":
            config["spec"]["template"]["spec"]["containers"][0]["env"].extend([
                {"name": "REDIS_CACHE_ENABLED", "value": "true"},
                {"name": "CONNECTION_POOLING", "value": "true"}
            ])

        return config

    def calculate_cost_savings(self, current_config: Dict[str, Any],
                             optimized_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate estimated cost savings from optimization."""
        # Simplified cost calculation (actual costs vary by region and usage)
        cpu_cost_per_hour = 0.000024  # $0.000024 per vCPU per second
        memory_cost_per_hour = 0.0000025  # $0.0000025 per GiB per second
        request_cost = 0.0000004  # $0.0000004 per request

        def parse_resources(config):
            container = config["spec"]["template"]["spec"]["containers"][0]
            cpu = container["resources"]["limits"]["cpu"]
            memory = container["resources"]["limits"]["memory"]

            # Parse CPU (convert millicores to cores)
            cpu_cores = float(cpu.rstrip('m')) / 1000 if cpu.endswith('m') else float(cpu)

            # Parse memory (convert to GiB)
            if memory.endswith('Gi'):
                memory_gib = float(memory.rstrip('Gi'))
            elif memory.endswith('Mi'):
                memory_gib = float(memory.rstrip('Mi')) / 1024
            else:
                memory_gib = float(memory) / (1024**3)  # Assume bytes

            return cpu_cores, memory_gib

        try:
            current_cpu, current_memory = parse_resources(current_config)
            optimized_cpu, optimized_memory = parse_resources(optimized_config)

            # Calculate hourly costs
            current_hourly_cost = (current_cpu * cpu_cost_per_hour * 3600) + (current_memory * memory_cost_per_hour * 3600)
            optimized_hourly_cost = (optimized_cpu * cpu_cost_per_hour * 3600) + (optimized_memory * memory_cost_per_hour * 3600)

            hourly_savings = current_hourly_cost - optimized_hourly_cost
            daily_savings = hourly_savings * 24
            monthly_savings = daily_savings * 30

            return {
                "current_hourly_cost": round(current_hourly_cost, 6),
                "optimized_hourly_cost": round(optimized_hourly_cost, 6),
                "hourly_savings": round(hourly_savings, 6),
                "daily_savings": round(daily_savings, 4),
                "monthly_savings": round(monthly_savings, 2),
                "savings_percentage": round((hourly_savings / current_hourly_cost) * 100, 1) if current_hourly_cost > 0 else 0,
                "resource_reduction": {
                    "cpu_reduction": f"{current_cpu - optimized_cpu:.2f} cores",
                    "memory_reduction": f"{current_memory - optimized_memory:.2f} GiB"
                }
            }

        except Exception as e:
            logger.error(f"Cost calculation failed: {e}")
            return {"error": "Could not calculate cost savings", "details": str(e)}

    def generate_deployment_script(self, service_name: str, project_id: str = None, region: str = None) -> str:
        """Generate optimized deployment script for a service."""
        project_id = project_id or os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
        region = region or os.getenv("REGION", "us-central1")

        script = f'''#!/bin/bash
# Optimized deployment script for {service_name}

set -euo pipefail

PROJECT_ID="{project_id}"
REGION="{region}"
SERVICE_NAME="{service_name}"
IMAGE_TAG="${{1:-latest}}"

echo "🚀 Deploying $SERVICE_NAME with optimized configuration..."

# Build optimized container
docker build -t $SERVICE_NAME:$IMAGE_TAG -f Dockerfile.optimized .

# Tag for Artifact Registry
docker tag $SERVICE_NAME:$IMAGE_TAG \\
    $REGION-docker.pkg.dev/$PROJECT_ID/xynergy-platform/$SERVICE_NAME:$IMAGE_TAG

# Push to registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/xynergy-platform/$SERVICE_NAME:$IMAGE_TAG

# Deploy to Cloud Run with optimized settings
gcloud run deploy $SERVICE_NAME \\
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/xynergy-platform/$SERVICE_NAME:$IMAGE_TAG \\
    --platform=managed \\
    --region=$REGION \\
    --allow-unauthenticated \\
    --set-env-vars="PROJECT_ID=$PROJECT_ID,REGION=$REGION,OPTIMIZATION_ENABLED=true" \\
    --memory={self.resource_profiles[self.service_classifications.get(service_name, "api-service")].memory} \\
    --cpu={self.resource_profiles[self.service_classifications.get(service_name, "api-service")].cpu} \\
    --concurrency={self.resource_profiles[self.service_classifications.get(service_name, "api-service")].concurrency} \\
    --min-instances={self.resource_profiles[self.service_classifications.get(service_name, "api-service")].min_instances} \\
    --max-instances={self.resource_profiles[self.service_classifications.get(service_name, "api-service")].max_instances} \\
    --timeout={self.resource_profiles[self.service_classifications.get(service_name, "api-service")].timeout}

echo "✅ $SERVICE_NAME deployed successfully with optimized configuration"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "🌐 Service URL: $SERVICE_URL"

# Health check
echo "🏥 Running health check..."
if curl -f "$SERVICE_URL/health"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi
'''
        return script

    def get_platform_optimization_summary(self) -> Dict[str, Any]:
        """Get optimization summary for the entire platform."""
        service_counts = {}
        for service, profile_type in self.service_classifications.items():
            service_counts[profile_type] = service_counts.get(profile_type, 0) + 1

        total_services = len(self.service_classifications)

        # Estimate cost savings across all services
        estimated_monthly_savings = 0
        for profile_type, count in service_counts.items():
            profile = self.resource_profiles[profile_type]
            # Rough estimate: $50-200/month per service based on type
            base_cost = {"ai-intensive": 200, "data-processing": 150, "api-service": 100,
                        "background-worker": 75, "dashboard": 50}.get(profile_type, 100)
            savings_per_service = base_cost * 0.30  # 30% average savings
            estimated_monthly_savings += savings_per_service * count

        return {
            "total_services": total_services,
            "service_distribution": service_counts,
            "optimization_profiles": {
                profile_type: {
                    "cpu": profile.cpu,
                    "memory": profile.memory,
                    "max_instances": profile.max_instances,
                    "concurrency": profile.concurrency
                }
                for profile_type, profile in self.resource_profiles.items()
            },
            "estimated_monthly_savings": round(estimated_monthly_savings, 2),
            "optimization_benefits": [
                "Right-sized resource allocation",
                "Intelligent auto-scaling",
                "Optimized container images",
                "Reduced cold start times",
                "Lower compute costs"
            ]
        }

# Global optimizer instance
container_optimizer = ContainerOptimizer()

def optimize_service_container(service_name: str, output_dir: str = ".") -> Dict[str, str]:
    """Generate optimized container files for a service."""
    optimizer = ContainerOptimizer()

    # Generate optimized files
    dockerfile = optimizer.generate_optimized_dockerfile(service_name)
    deployment_script = optimizer.generate_deployment_script(service_name)

    # Write files
    dockerfile_path = os.path.join(output_dir, "Dockerfile.optimized")
    script_path = os.path.join(output_dir, f"deploy-{service_name}-optimized.sh")

    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile)

    with open(script_path, 'w') as f:
        f.write(deployment_script)

    # Make script executable
    os.chmod(script_path, 0o755)

    return {
        "dockerfile": dockerfile_path,
        "deployment_script": script_path,
        "service_type": optimizer.service_classifications.get(service_name, "api-service")
    }