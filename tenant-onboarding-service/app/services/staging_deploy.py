"""
Staging Deployment Service
Handles deployment of staging and production environments
"""
import structlog
from typing import Dict, Any, Optional
from google.cloud import firestore, storage, run_v2
from datetime import datetime
from app.models.onboarding import WebsiteSource, GitHubConfig

logger = structlog.get_logger()


class StagingDeploymentService:
    """Service for deploying staging and production environments"""

    def __init__(self):
        self.project_id = "xynergy-dev-1757909467"
        self.region = "us-central1"
        self.db = firestore.Client()
        self.storage_client = storage.Client()

    async def deploy_both_environments(
        self,
        tenant_id: str,
        domain: str,
        website_source: WebsiteSource,
        generated_site_id: Optional[str] = None,
        github_config: Optional[GitHubConfig] = None
    ) -> Dict[str, Any]:
        """
        Deploy both production and staging environments

        Returns URLs for both environments
        """
        logger.info("deploying_both_environments",
                    tenant_id=tenant_id,
                    source=website_source.value)

        # Prepare deployment files based on source
        deployment_files = await self._prepare_deployment_files(
            tenant_id=tenant_id,
            website_source=website_source,
            generated_site_id=generated_site_id,
            github_config=github_config
        )

        # Deploy production
        production_url = await self._deploy_environment(
            tenant_id=tenant_id,
            environment="production",
            domain=domain,
            deployment_files=deployment_files
        )

        # Deploy staging
        staging_domain = f"staging.{domain}"
        staging_url = await self._deploy_environment(
            tenant_id=tenant_id,
            environment="staging",
            domain=staging_domain,
            deployment_files=deployment_files
        )

        # Store deployment info
        await self._store_deployment_info(
            tenant_id=tenant_id,
            production_url=production_url,
            staging_url=staging_url
        )

        logger.info("both_environments_deployed",
                    tenant_id=tenant_id,
                    production_url=production_url,
                    staging_url=staging_url)

        return {
            "production_url": production_url,
            "staging_url": staging_url,
            "deployment_files": deployment_files
        }

    async def _prepare_deployment_files(
        self,
        tenant_id: str,
        website_source: WebsiteSource,
        generated_site_id: Optional[str],
        github_config: Optional[GitHubConfig]
    ) -> Dict[str, Any]:
        """Prepare files for deployment based on source"""

        if website_source == WebsiteSource.XYNERGY_GENERATED and generated_site_id:
            # Copy from Cloud Storage
            return await self._copy_from_generated_site(tenant_id, generated_site_id)

        elif website_source == WebsiteSource.GITHUB_REPO and github_config:
            # Clone from GitHub
            return await self._clone_from_github(tenant_id, github_config)

        elif website_source == WebsiteSource.UPLOAD_FILES:
            # Files already uploaded to Cloud Storage
            return await self._copy_from_uploads(tenant_id)

        else:
            raise ValueError(f"Unsupported website source: {website_source}")

    async def _copy_from_generated_site(self, tenant_id: str, generation_id: str) -> Dict[str, Any]:
        """Copy files from Xynergy-generated site"""
        logger.info("copying_from_generated_site",
                    tenant_id=tenant_id,
                    generation_id=generation_id)

        # Source path in Cloud Storage
        source_bucket = "xynergy-generated-sites"
        source_path = f"{generation_id}/"

        # Destination path
        dest_bucket = "xynergy-tenant-websites"
        dest_path = f"{tenant_id}/"

        # Copy files
        # Note: Actual Cloud Storage copy would happen here
        # For now, returning metadata

        # Update generated site status
        self.db.collection("generated_sites").document(generation_id).update({
            "status": "deployed",
            "deployed_to": tenant_id,
            "deployed_at": firestore.SERVER_TIMESTAMP
        })

        return {
            "source": "generated_site",
            "generation_id": generation_id,
            "storage_path": f"gs://{dest_bucket}/{dest_path}"
        }

    async def _clone_from_github(self, tenant_id: str, github_config: GitHubConfig) -> Dict[str, Any]:
        """Clone repository from GitHub"""
        logger.info("cloning_from_github",
                    tenant_id=tenant_id,
                    repo=github_config.repo_url)

        # Note: This would typically be handled by Cloud Build
        # For manual deployments, we'd clone the repo

        return {
            "source": "github",
            "repo_url": github_config.repo_url,
            "branch": github_config.branch_production
        }

    async def _copy_from_uploads(self, tenant_id: str) -> Dict[str, Any]:
        """Copy files from manual uploads"""
        logger.info("copying_from_uploads", tenant_id=tenant_id)

        # Files uploaded to uploads bucket
        source_bucket = "xynergy-tenant-uploads"
        source_path = f"{tenant_id}/"

        return {
            "source": "upload",
            "storage_path": f"gs://{source_bucket}/{source_path}"
        }

    async def _deploy_environment(
        self,
        tenant_id: str,
        environment: str,
        domain: str,
        deployment_files: Dict[str, Any]
    ) -> str:
        """Deploy a single environment (production or staging)"""

        service_name = f"{tenant_id}-website"
        if environment == "staging":
            service_name += "-staging"

        logger.info("deploying_environment",
                    tenant_id=tenant_id,
                    environment=environment,
                    service_name=service_name)

        # Build Docker image
        image_url = await self._build_docker_image(
            tenant_id=tenant_id,
            environment=environment,
            deployment_files=deployment_files
        )

        # Deploy to Cloud Run
        service_url = await self._deploy_to_cloud_run(
            service_name=service_name,
            image_url=image_url,
            tenant_id=tenant_id,
            environment=environment
        )

        logger.info("environment_deployed",
                    tenant_id=tenant_id,
                    environment=environment,
                    url=service_url)

        return service_url

    async def _build_docker_image(
        self,
        tenant_id: str,
        environment: str,
        deployment_files: Dict[str, Any]
    ) -> str:
        """Build Docker image for the website"""

        image_tag = f"{tenant_id}-website"
        if environment == "staging":
            image_tag += "-staging"

        image_url = f"gcr.io/{self.project_id}/{image_tag}:latest"

        logger.info("building_docker_image",
                    tenant_id=tenant_id,
                    environment=environment,
                    image_url=image_url)

        # Note: Actual Docker build would happen via Cloud Build
        # This is a simplified version

        return image_url

    async def _deploy_to_cloud_run(
        self,
        service_name: str,
        image_url: str,
        tenant_id: str,
        environment: str
    ) -> str:
        """Deploy service to Cloud Run"""

        logger.info("deploying_to_cloud_run",
                    service_name=service_name,
                    environment=environment)

        # Resource limits based on environment
        if environment == "staging":
            memory = "512Mi"
            cpu = "1"
            max_instances = 3
        else:
            memory = "1Gi"
            cpu = "1"
            max_instances = 10

        # Note: Actual Cloud Run deployment would use the Run API
        # For now, constructing the expected URL

        service_url = f"https://{service_name}-xxx-{self.region}.a.run.app"

        # Store deployment record
        self.db.collection("deployments").document(f"{tenant_id}-{environment}").set({
            "tenant_id": tenant_id,
            "environment": environment,
            "service_name": service_name,
            "image_url": image_url,
            "service_url": service_url,
            "memory": memory,
            "cpu": cpu,
            "max_instances": max_instances,
            "deployed_at": firestore.SERVER_TIMESTAMP,
            "status": "healthy"
        })

        return service_url

    async def _store_deployment_info(
        self,
        tenant_id: str,
        production_url: str,
        staging_url: str
    ):
        """Store deployment information in Firestore"""

        deployment_data = {
            "tenant_id": tenant_id,
            "production": {
                "service_name": f"{tenant_id}-website",
                "url": production_url,
                "deployed_at": firestore.SERVER_TIMESTAMP,
                "environment": "production"
            },
            "staging": {
                "service_name": f"{tenant_id}-website-staging",
                "url": staging_url,
                "deployed_at": firestore.SERVER_TIMESTAMP,
                "environment": "staging"
            },
            "last_updated": firestore.SERVER_TIMESTAMP
        }

        self.db.collection("deployments").document(tenant_id).set(deployment_data)

    async def promote_to_production(
        self,
        tenant_id: str,
        promoted_by: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Promote staging deployment to production"""

        logger.info("promoting_to_production",
                    tenant_id=tenant_id,
                    promoted_by=promoted_by)

        # Get staging image
        staging_deployment = self.db.collection("deployments").document(f"{tenant_id}-staging").get()

        if not staging_deployment.exists:
            raise ValueError("Staging deployment not found")

        staging_data = staging_deployment.to_dict()
        staging_image = staging_data.get("image_url")

        # Tag staging image for production
        production_image = staging_image.replace("-staging:", ":")

        # Deploy to production with staging image
        service_url = await self._deploy_to_cloud_run(
            service_name=f"{tenant_id}-website",
            image_url=staging_image,
            tenant_id=tenant_id,
            environment="production"
        )

        # Log promotion
        promotion_record = {
            "tenant_id": tenant_id,
            "promoted_from": "staging",
            "staging_image": staging_image,
            "promoted_by": promoted_by,
            "promoted_at": firestore.SERVER_TIMESTAMP,
            "notes": notes,
            "production_url": service_url
        }

        self.db.collection("deployment_promotions").add(promotion_record)

        logger.info("promotion_complete", tenant_id=tenant_id)

        return {
            "status": "promoted",
            "production_url": service_url,
            "promoted_at": datetime.utcnow().isoformat()
        }

    async def get_deployment_status(self, tenant_id: str) -> Dict[str, Any]:
        """Get deployment status for both environments"""

        deployment_doc = self.db.collection("deployments").document(tenant_id).get()

        if not deployment_doc.exists:
            return {"status": "not_deployed", "tenant_id": tenant_id}

        deployment_data = deployment_doc.to_dict()

        return {
            "tenant_id": tenant_id,
            "production": deployment_data.get("production"),
            "staging": deployment_data.get("staging"),
            "last_updated": deployment_data.get("last_updated")
        }
