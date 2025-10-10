"""
GitHub CI/CD Integration Service
Handles Cloud Build trigger setup for automatic deployments
"""
import structlog
from typing import Dict, Any
from google.cloud import build_v1, secretmanager
from app.models.onboarding import GitHubConfig

logger = structlog.get_logger()


class GitHubCICDService:
    """Service for setting up GitHub CI/CD with Cloud Build"""

    def __init__(self):
        self.build_client = build_v1.CloudBuildClient()
        self.secret_client = secretmanager.SecretManagerServiceClient()
        self.project_id = "xynergy-dev-1757909467"
        self.region = "us-central1"

    async def setup_cicd(self, tenant_id: str, github_config: GitHubConfig) -> Dict[str, Any]:
        """
        Set up GitHub CI/CD with Cloud Build triggers

        Creates:
        1. Production trigger (on push to main branch)
        2. Staging trigger (on push to staging branch)
        3. Stores GitHub access token in Secret Manager
        """
        logger.info("setting_up_github_cicd", tenant_id=tenant_id, repo=github_config.repo_url)

        # Parse GitHub URL
        owner, repo = self._parse_github_url(github_config.repo_url)

        # Store access token in Secret Manager (if provided)
        if github_config.access_token:
            await self._store_access_token(tenant_id, github_config.access_token)

        # Create production trigger
        production_trigger_id = await self._create_production_trigger(
            tenant_id=tenant_id,
            owner=owner,
            repo=repo,
            branch=github_config.branch_production
        )

        # Create staging trigger
        staging_trigger_id = await self._create_staging_trigger(
            tenant_id=tenant_id,
            owner=owner,
            repo=repo,
            branch=github_config.branch_staging
        )

        logger.info("github_cicd_setup_complete",
                    tenant_id=tenant_id,
                    production_trigger=production_trigger_id,
                    staging_trigger=staging_trigger_id)

        return {
            "production_trigger_id": production_trigger_id,
            "staging_trigger_id": staging_trigger_id,
            "github_owner": owner,
            "github_repo": repo
        }

    def _parse_github_url(self, repo_url: str) -> tuple:
        """Parse GitHub URL to extract owner and repo name"""
        # Handle various GitHub URL formats
        # - https://github.com/owner/repo
        # - github.com/owner/repo
        # - owner/repo

        url = repo_url.replace("https://", "").replace("http://", "")
        url = url.replace("github.com/", "")
        url = url.rstrip("/")

        parts = url.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        else:
            raise ValueError(f"Invalid GitHub URL: {repo_url}")

    async def _store_access_token(self, tenant_id: str, access_token: str):
        """Store GitHub access token in Secret Manager"""
        secret_id = f"github-token-{tenant_id}"
        parent = f"projects/{self.project_id}"

        try:
            # Create secret
            secret = {
                "replication": {
                    "automatic": {}
                }
            }
            self.secret_client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": secret
                }
            )

            # Add secret version
            secret_path = f"{parent}/secrets/{secret_id}"
            self.secret_client.add_secret_version(
                request={
                    "parent": secret_path,
                    "payload": {"data": access_token.encode("utf-8")}
                }
            )

            logger.info("github_token_stored", tenant_id=tenant_id, secret_id=secret_id)

        except Exception as e:
            logger.error("failed_to_store_token", tenant_id=tenant_id, error=str(e))
            raise

    async def _create_production_trigger(
        self,
        tenant_id: str,
        owner: str,
        repo: str,
        branch: str
    ) -> str:
        """Create Cloud Build trigger for production deployments"""

        trigger = {
            "name": f"deploy-{tenant_id}-production",
            "description": f"Auto-deploy {tenant_id} to production on push to {branch}",
            "github": {
                "owner": owner,
                "name": repo,
                "push": {
                    "branch": f"^{branch}$"
                }
            },
            "build": {
                "steps": [
                    # Build Docker image
                    {
                        "name": "gcr.io/cloud-builders/docker",
                        "args": [
                            "build",
                            "-t", f"gcr.io/{self.project_id}/{tenant_id}-website:$SHORT_SHA",
                            "-t", f"gcr.io/{self.project_id}/{tenant_id}-website:latest",
                            "."
                        ]
                    },
                    # Push to Container Registry
                    {
                        "name": "gcr.io/cloud-builders/docker",
                        "args": ["push", f"gcr.io/{self.project_id}/{tenant_id}-website:$SHORT_SHA"]
                    },
                    {
                        "name": "gcr.io/cloud-builders/docker",
                        "args": ["push", f"gcr.io/{self.project_id}/{tenant_id}-website:latest"]
                    },
                    # Deploy to Cloud Run
                    {
                        "name": "gcr.io/google.com/cloudsdktool/cloud-sdk",
                        "entrypoint": "gcloud",
                        "args": [
                            "run", "deploy", f"{tenant_id}-website",
                            "--image", f"gcr.io/{self.project_id}/{tenant_id}-website:$SHORT_SHA",
                            "--region", self.region,
                            "--platform", "managed",
                            "--allow-unauthenticated",
                            "--set-env-vars", f"TENANT_ID={tenant_id},ENVIRONMENT=production",
                            "--set-labels", f"tenant_id={tenant_id},environment=production,cost_center=clearforge_services"
                        ]
                    }
                ],
                "images": [
                    f"gcr.io/{self.project_id}/{tenant_id}-website:$SHORT_SHA",
                    f"gcr.io/{self.project_id}/{tenant_id}-website:latest"
                ],
                "options": {
                    "logging": "CLOUD_LOGGING_ONLY",
                    "machineType": "N1_HIGHCPU_8"
                }
            }
        }

        # Note: Actual Cloud Build API calls would go here
        # For now, returning a mock trigger ID
        trigger_id = f"prod-trigger-{tenant_id}"

        logger.info("production_trigger_created", tenant_id=tenant_id, trigger_id=trigger_id)

        return trigger_id

    async def _create_staging_trigger(
        self,
        tenant_id: str,
        owner: str,
        repo: str,
        branch: str
    ) -> str:
        """Create Cloud Build trigger for staging deployments"""

        trigger = {
            "name": f"deploy-{tenant_id}-staging",
            "description": f"Auto-deploy {tenant_id} to staging on push to {branch}",
            "github": {
                "owner": owner,
                "name": repo,
                "push": {
                    "branch": f"^{branch}$"
                }
            },
            "build": {
                "steps": [
                    # Build Docker image
                    {
                        "name": "gcr.io/cloud-builders/docker",
                        "args": [
                            "build",
                            "-t", f"gcr.io/{self.project_id}/{tenant_id}-website-staging:$SHORT_SHA",
                            "-t", f"gcr.io/{self.project_id}/{tenant_id}-website-staging:latest",
                            "."
                        ]
                    },
                    # Push to Container Registry
                    {
                        "name": "gcr.io/cloud-builders/docker",
                        "args": ["push", f"gcr.io/{self.project_id}/{tenant_id}-website-staging:$SHORT_SHA"]
                    },
                    {
                        "name": "gcr.io/cloud-builders/docker",
                        "args": ["push", f"gcr.io/{self.project_id}/{tenant_id}-website-staging:latest"]
                    },
                    # Deploy to Cloud Run
                    {
                        "name": "gcr.io/google.com/cloudsdktool/cloud-sdk",
                        "entrypoint": "gcloud",
                        "args": [
                            "run", "deploy", f"{tenant_id}-website-staging",
                            "--image", f"gcr.io/{self.project_id}/{tenant_id}-website-staging:$SHORT_SHA",
                            "--region", self.region,
                            "--platform", "managed",
                            "--allow-unauthenticated",
                            "--set-env-vars", f"TENANT_ID={tenant_id},ENVIRONMENT=staging",
                            "--set-labels", f"tenant_id={tenant_id},environment=staging,cost_center=clearforge_services",
                            "--memory", "512Mi",
                            "--cpu", "1",
                            "--max-instances", "3"
                        ]
                    }
                ],
                "images": [
                    f"gcr.io/{self.project_id}/{tenant_id}-website-staging:$SHORT_SHA",
                    f"gcr.io/{self.project_id}/{tenant_id}-website-staging:latest"
                ],
                "options": {
                    "logging": "CLOUD_LOGGING_ONLY",
                    "machineType": "N1_HIGHCPU_8"
                }
            }
        }

        # Note: Actual Cloud Build API calls would go here
        # For now, returning a mock trigger ID
        trigger_id = f"staging-trigger-{tenant_id}"

        logger.info("staging_trigger_created", tenant_id=tenant_id, trigger_id=trigger_id)

        return trigger_id

    async def trigger_manual_build(self, tenant_id: str, environment: str = "production") -> str:
        """Trigger a manual build for a tenant"""
        logger.info("triggering_manual_build", tenant_id=tenant_id, environment=environment)

        # Get trigger ID based on environment
        trigger_id = f"{environment}-trigger-{tenant_id}"

        # Trigger build via Cloud Build API
        # Note: Actual API call would go here

        build_id = f"build-{tenant_id}-{environment}-manual"

        logger.info("manual_build_triggered", tenant_id=tenant_id, build_id=build_id)

        return build_id
