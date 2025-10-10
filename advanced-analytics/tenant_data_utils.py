"""
Tenant-specific data segregation utilities for Firestore and BigQuery.
This module provides utilities for managing tenant data isolation.
"""

import os
import structlog
from typing import Dict, List, Optional, Any
from google.cloud import firestore, bigquery
from google.cloud.exceptions import NotFound

logger = structlog.get_logger()

class TenantDataManager:
    """Manages tenant data segregation across Firestore and BigQuery"""

    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
        self.firestore_client = firestore.Client(project=self.project_id)
        self.bigquery_client = bigquery.Client(project=self.project_id)

    async def provision_tenant_data_resources(self, tenant_id: str) -> Dict[str, bool]:
        """
        Provision all necessary data resources for a new tenant.

        Args:
            tenant_id: Unique tenant identifier

        Returns:
            Dict with success status for each resource type
        """
        results = {
            "firestore_collections": False,
            "bigquery_datasets": False,
            "bigquery_tables": False
        }

        try:
            # Create Firestore collections
            await self.create_tenant_firestore_collections(tenant_id)
            results["firestore_collections"] = True

            # Create BigQuery datasets
            await self.create_tenant_bigquery_datasets(tenant_id)
            results["bigquery_datasets"] = True

            # Create BigQuery tables
            await self.create_tenant_bigquery_tables(tenant_id)
            results["bigquery_tables"] = True

            logger.info("Tenant data resources provisioned successfully", tenant_id=tenant_id, results=results)

        except Exception as e:
            logger.error("Error provisioning tenant data resources", tenant_id=tenant_id, error=str(e))
            raise

        return results

    async def create_tenant_firestore_collections(self, tenant_id: str):
        """Create initial Firestore collections for a tenant with proper indexes"""

        collections_to_create = [
            "marketing_campaigns",
            "keyword_research",
            "content_assets",
            "projects",
            "workflows",
            "analytics_events",
            "reports",
            "qa_results",
            "security_policies",
            "ai_interactions",
            "competency_assessments"
        ]

        for collection_name in collections_to_create:
            tenant_collection_name = f"tenant_{tenant_id}_{collection_name}"

            # Create a dummy document to ensure collection exists
            dummy_doc = {
                "tenant_id": tenant_id,
                "collection_type": collection_name,
                "created_at": firestore.SERVER_TIMESTAMP,
                "_metadata": {
                    "is_dummy": True,
                    "created_by": "tenant_provisioning"
                }
            }

            collection_ref = self.firestore_client.collection(tenant_collection_name)
            await collection_ref.document("_init").set(dummy_doc)

            logger.info("Created Firestore collection", tenant_id=tenant_id, collection=tenant_collection_name)

    async def create_tenant_bigquery_datasets(self, tenant_id: str):
        """Create BigQuery datasets for tenant data"""

        datasets_to_create = [
            f"tenant_{tenant_id}_analytics",
            f"tenant_{tenant_id}_marketing",
            f"tenant_{tenant_id}_operations",
            f"tenant_{tenant_id}_security"
        ]

        for dataset_name in datasets_to_create:
            dataset_id = f"{self.project_id}.{dataset_name}"

            try:
                # Check if dataset already exists
                self.bigquery_client.get_dataset(dataset_id)
                logger.info("BigQuery dataset already exists", tenant_id=tenant_id, dataset=dataset_name)
                continue

            except NotFound:
                # Create the dataset
                dataset = bigquery.Dataset(dataset_id)
                dataset.location = "US"
                dataset.description = f"Data for tenant {tenant_id}"

                # Set access controls - tenant-specific
                access_entries = [
                    bigquery.AccessEntry(
                        role="OWNER",
                        entity_type="userByEmail",
                        entity_id=f"tenant-{tenant_id}@{self.project_id}.iam.gserviceaccount.com"
                    ),
                    bigquery.AccessEntry(
                        role="READER",
                        entity_type="serviceAccount",
                        entity_id=f"xynergy-platform-sa@{self.project_id}.iam.gserviceaccount.com"
                    )
                ]
                dataset.access_entries = access_entries

                # Add labels for tenant identification
                dataset.labels = {
                    "tenant_id": tenant_id.replace("-", "_").lower(),
                    "environment": "production",
                    "managed_by": "xynergy_platform"
                }

                dataset = self.bigquery_client.create_dataset(dataset, timeout=30)
                logger.info("Created BigQuery dataset", tenant_id=tenant_id, dataset=dataset_name)

    async def create_tenant_bigquery_tables(self, tenant_id: str):
        """Create standard BigQuery tables for tenant analytics"""

        # Define table schemas
        table_schemas = {
            "user_interactions": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("tenant_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("session_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("action", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("service", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("metadata", "JSON", mode="NULLABLE")
            ],
            "campaign_metrics": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("tenant_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("campaign_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("impressions", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("clicks", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("conversions", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("cost", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("revenue", "FLOAT", mode="NULLABLE")
            ],
            "workflow_executions": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("tenant_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("workflow_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("duration_seconds", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("services_used", "STRING", mode="REPEATED"),
                bigquery.SchemaField("error_message", "STRING", mode="NULLABLE")
            ],
            "ai_usage_metrics": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("tenant_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("service", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("ai_provider", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("tokens_used", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("cost", "FLOAT", mode="NULLABLE"),
                bigquery.SchemaField("response_time_ms", "INTEGER", mode="NULLABLE")
            ]
        }

        analytics_dataset = f"tenant_{tenant_id}_analytics"

        for table_name, schema in table_schemas.items():
            table_id = f"{self.project_id}.{analytics_dataset}.{table_name}"

            try:
                # Check if table already exists
                self.bigquery_client.get_table(table_id)
                logger.info("BigQuery table already exists", tenant_id=tenant_id, table=table_name)
                continue

            except NotFound:
                # Create the table
                table = bigquery.Table(table_id, schema=schema)
                table.description = f"{table_name} data for tenant {tenant_id}"

                # Set partitioning on timestamp field for performance
                table.time_partitioning = bigquery.TimePartitioning(
                    type_=bigquery.TimePartitioningType.DAY,
                    field="timestamp"
                )

                # Add clustering for better query performance
                if table_name in ["user_interactions", "workflow_executions"]:
                    table.clustering_fields = ["tenant_id", "timestamp"]

                table = self.bigquery_client.create_table(table, timeout=30)
                logger.info("Created BigQuery table", tenant_id=tenant_id, table=table_name)

    async def delete_tenant_data_resources(self, tenant_id: str) -> Dict[str, bool]:
        """
        Delete all data resources for a tenant (use with caution!).

        Args:
            tenant_id: Unique tenant identifier

        Returns:
            Dict with success status for each deletion operation
        """
        results = {
            "firestore_collections": False,
            "bigquery_datasets": False
        }

        try:
            # Delete Firestore collections
            await self.delete_tenant_firestore_collections(tenant_id)
            results["firestore_collections"] = True

            # Delete BigQuery datasets
            await self.delete_tenant_bigquery_datasets(tenant_id)
            results["bigquery_datasets"] = True

            logger.info("Tenant data resources deleted", tenant_id=tenant_id, results=results)

        except Exception as e:
            logger.error("Error deleting tenant data resources", tenant_id=tenant_id, error=str(e))
            raise

        return results

    async def delete_tenant_firestore_collections(self, tenant_id: str):
        """Delete all Firestore collections for a tenant"""

        # Get all collections that belong to this tenant
        collections = self.firestore_client.collections()

        for collection in collections:
            if collection.id.startswith(f"tenant_{tenant_id}_"):
                # Delete all documents in the collection
                docs = collection.stream()
                for doc in docs:
                    doc.reference.delete()

                logger.info("Deleted Firestore collection", tenant_id=tenant_id, collection=collection.id)

    async def delete_tenant_bigquery_datasets(self, tenant_id: str):
        """Delete all BigQuery datasets for a tenant"""

        datasets = self.bigquery_client.list_datasets()

        for dataset in datasets:
            if dataset.dataset_id.startswith(f"tenant_{tenant_id}_"):
                # Delete dataset and all tables
                self.bigquery_client.delete_dataset(
                    dataset.dataset_id,
                    delete_contents=True,
                    not_found_ok=True
                )

                logger.info("Deleted BigQuery dataset", tenant_id=tenant_id, dataset=dataset.dataset_id)

    def get_tenant_collections(self, tenant_id: str) -> List[str]:
        """Get list of all Firestore collections for a tenant"""

        collections = self.firestore_client.collections()
        tenant_collections = []

        for collection in collections:
            if collection.id.startswith(f"tenant_{tenant_id}_"):
                tenant_collections.append(collection.id)

        return tenant_collections

    def get_tenant_datasets(self, tenant_id: str) -> List[str]:
        """Get list of all BigQuery datasets for a tenant"""

        datasets = self.bigquery_client.list_datasets()
        tenant_datasets = []

        for dataset in datasets:
            if dataset.dataset_id.startswith(f"tenant_{tenant_id}_"):
                tenant_datasets.append(dataset.dataset_id)

        return tenant_datasets

    async def export_tenant_data(self, tenant_id: str, export_path: str) -> Dict[str, str]:
        """
        Export all tenant data for backup or migration.

        Args:
            tenant_id: Unique tenant identifier
            export_path: GCS path for data export

        Returns:
            Dict with export job IDs and status
        """
        results = {}

        try:
            # Export BigQuery datasets
            datasets = self.get_tenant_datasets(tenant_id)

            for dataset_id in datasets:
                # Create export job for each dataset
                job_config = bigquery.ExtractJobConfig()
                job_config.destination_format = bigquery.DestinationFormat.NEWLINE_DELIMITED_JSON

                destination_uri = f"{export_path}/bigquery/{dataset_id}/*.json"

                extract_job = self.bigquery_client.extract_table(
                    f"{self.project_id}.{dataset_id}",
                    destination_uri,
                    job_config=job_config
                )

                results[f"bigquery_{dataset_id}"] = extract_job.job_id

                logger.info("Started BigQuery export", tenant_id=tenant_id, dataset=dataset_id, job_id=extract_job.job_id)

            return results

        except Exception as e:
            logger.error("Error exporting tenant data", tenant_id=tenant_id, error=str(e))
            raise

# Factory function for easy usage
def get_tenant_data_manager(project_id: str = None) -> TenantDataManager:
    """Get a TenantDataManager instance"""
    return TenantDataManager(project_id)