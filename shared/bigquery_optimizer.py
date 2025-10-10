"""
BigQuery Optimization Utilities for Xynergy Platform
Implements partitioning, clustering, and cost optimization strategies.
"""
import os
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BigQueryOptimizer:
    """Optimizes BigQuery performance and costs through partitioning and clustering."""

    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv("PROJECT_ID", "xynergy-dev-1757909467")
        self.client = bigquery.Client(project=self.project_id)

    def create_partitioned_table(self, dataset_id: str, table_id: str, schema: List[bigquery.SchemaField],
                                partition_field: str = "created_at", clustering_fields: List[str] = None) -> bool:
        """Create a partitioned table with optional clustering."""
        try:
            dataset_ref = self.client.dataset(dataset_id)
            table_ref = dataset_ref.table(table_id)

            # Configure time partitioning
            time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=partition_field,
                expiration_ms=7776000000  # 90 days in milliseconds
            )

            # Configure clustering if specified
            clustering = None
            if clustering_fields:
                clustering = bigquery.Clustering(fields=clustering_fields)

            table = bigquery.Table(table_ref, schema=schema)
            table.time_partitioning = time_partitioning
            if clustering:
                table.clustering = clustering

            # Set table description
            table.description = f"Partitioned table for {table_id} with optimized performance and cost management"

            # Create table
            table = self.client.create_table(table, exists_ok=True)
            logger.info(f"Created partitioned table {dataset_id}.{table_id} with partition field {partition_field}")

            return True

        except Exception as e:
            logger.error(f"Failed to create partitioned table {dataset_id}.{table_id}: {e}")
            return False

    def create_analytics_tables(self) -> Dict[str, bool]:
        """Create optimized analytics tables with partitioning."""
        results = {}

        # Marketing campaign analytics
        marketing_schema = [
            bigquery.SchemaField("campaign_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("client_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("campaign_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("keywords", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("performance_metrics", "JSON", mode="REQUIRED"),
            bigquery.SchemaField("cost_data", "JSON", mode="REQUIRED"),
            bigquery.SchemaField("engagement_stats", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("conversion_data", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED")
        ]

        results["marketing_campaigns"] = self.create_partitioned_table(
            "xynergy_analytics", "marketing_campaigns", marketing_schema,
            partition_field="created_at", clustering_fields=["client_id", "campaign_type"]
        )

        # Content performance analytics
        content_schema = [
            bigquery.SchemaField("content_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("client_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("published_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("content_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("topic", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("performance_metrics", "JSON", mode="REQUIRED"),
            bigquery.SchemaField("seo_metrics", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("engagement_data", "JSON", mode="NULLABLE"),
            bigquery.SchemaField("revenue_attribution", "FLOAT", mode="NULLABLE")
        ]

        results["content_performance"] = self.create_partitioned_table(
            "xynergy_analytics", "content_performance", content_schema,
            partition_field="published_at", clustering_fields=["client_id", "content_type"]
        )

        # AI processing metrics
        ai_metrics_schema = [
            bigquery.SchemaField("request_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("service_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("processed_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("ai_provider", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("model_used", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("tokens_used", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("processing_time_ms", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("cost_usd", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("success", "BOOLEAN", mode="REQUIRED"),
            bigquery.SchemaField("error_details", "STRING", mode="NULLABLE")
        ]

        results["ai_processing_metrics"] = self.create_partitioned_table(
            "xynergy_analytics", "ai_processing_metrics", ai_metrics_schema,
            partition_field="processed_at", clustering_fields=["service_name", "ai_provider"]
        )

        # System performance metrics
        system_metrics_schema = [
            bigquery.SchemaField("metric_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("service_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("recorded_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("cpu_usage", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("memory_usage", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("response_time_ms", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("throughput", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("error_rate", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("circuit_breaker_state", "STRING", mode="NULLABLE")
        ]

        results["system_performance"] = self.create_partitioned_table(
            "xynergy_analytics", "system_performance", system_metrics_schema,
            partition_field="recorded_at", clustering_fields=["service_name"]
        )

        return results

    def optimize_existing_tables(self, dataset_id: str = "xynergy_analytics") -> Dict[str, bool]:
        """Optimize existing tables by adding clustering and updating table settings."""
        results = {}

        try:
            dataset = self.client.get_dataset(dataset_id)
            tables = list(self.client.list_tables(dataset))

            for table in tables:
                try:
                    table_ref = self.client.get_table(table.reference)

                    # Skip if already optimized
                    if table_ref.time_partitioning and table_ref.clustering:
                        logger.info(f"Table {table_ref.table_id} already optimized")
                        continue

                    # Update table with clustering based on schema
                    updated = False

                    # Determine clustering fields based on table name and schema
                    clustering_fields = self._determine_clustering_fields(table_ref)

                    if clustering_fields and not table_ref.clustering:
                        clustering = bigquery.Clustering(fields=clustering_fields)
                        table_ref.clustering = clustering
                        updated = True

                    # Add expiration if not set
                    if table_ref.time_partitioning and not table_ref.time_partitioning.expiration_ms:
                        table_ref.time_partitioning = bigquery.TimePartitioning(
                            type_=table_ref.time_partitioning.type_,
                            field=table_ref.time_partitioning.field,
                            expiration_ms=7776000000  # 90 days
                        )
                        updated = True

                    if updated:
                        self.client.update_table(table_ref, ["clustering", "time_partitioning"])
                        logger.info(f"Optimized table {table_ref.table_id}")
                        results[table_ref.table_id] = True
                    else:
                        results[table_ref.table_id] = False

                except Exception as e:
                    logger.error(f"Failed to optimize table {table.table_id}: {e}")
                    results[table.table_id] = False

        except Exception as e:
            logger.error(f"Failed to optimize tables in dataset {dataset_id}: {e}")

        return results

    def _determine_clustering_fields(self, table: bigquery.Table) -> List[str]:
        """Determine optimal clustering fields based on table schema."""
        clustering_fields = []

        # Common clustering patterns based on field names
        field_names = [field.name for field in table.schema]

        # Priority clustering fields
        priority_fields = ["client_id", "tenant_id", "user_id", "service_name", "status"]
        for field in priority_fields:
            if field in field_names:
                clustering_fields.append(field)
                if len(clustering_fields) >= 4:  # BigQuery limit
                    break

        # Add type fields if space available
        type_fields = [f for f in field_names if f.endswith('_type') or f.endswith('_category')]
        for field in type_fields[:2]:  # Limit to 2 type fields
            if field not in clustering_fields and len(clustering_fields) < 4:
                clustering_fields.append(field)

        return clustering_fields[:4]  # BigQuery clustering limit

    def get_table_costs(self, dataset_id: str, days_back: int = 30) -> Dict[str, Dict[str, Any]]:
        """Analyze table costs and storage usage."""
        query = f"""
        SELECT
            table_id,
            ROUND(size_bytes / (1024 * 1024 * 1024), 2) as size_gb,
            row_count,
            ROUND(size_bytes / NULLIF(row_count, 0), 2) as bytes_per_row,
            type,
            creation_time,
            last_modified_time
        FROM `{self.project_id}.{dataset_id}.__TABLES__`
        ORDER BY size_bytes DESC
        """

        try:
            query_job = self.client.query(query)
            results = query_job.result()

            cost_analysis = {}
            for row in results:
                cost_analysis[row.table_id] = {
                    "size_gb": row.size_gb,
                    "row_count": row.row_count,
                    "bytes_per_row": row.bytes_per_row,
                    "type": row.type,
                    "created": row.creation_time,
                    "last_modified": row.last_modified_time
                }

            return cost_analysis

        except Exception as e:
            logger.error(f"Failed to analyze table costs: {e}")
            return {}

    def create_cost_optimization_views(self, dataset_id: str = "xynergy_analytics") -> Dict[str, bool]:
        """Create materialized views for cost optimization."""
        results = {}

        # Daily cost summary view
        daily_cost_view = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{dataset_id}.daily_cost_summary` AS
        SELECT
            DATE(processed_at) as cost_date,
            ai_provider,
            service_name,
            COUNT(*) as total_requests,
            SUM(tokens_used) as total_tokens,
            SUM(cost_usd) as total_cost_usd,
            AVG(processing_time_ms) as avg_processing_time,
            SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*) as success_rate
        FROM `{self.project_id}.{dataset_id}.ai_processing_metrics`
        WHERE DATE(processed_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
        GROUP BY cost_date, ai_provider, service_name
        ORDER BY cost_date DESC, total_cost_usd DESC
        """

        try:
            self.client.query(daily_cost_view).result()
            results["daily_cost_summary"] = True
            logger.info("Created daily cost summary view")
        except Exception as e:
            logger.error(f"Failed to create daily cost summary view: {e}")
            results["daily_cost_summary"] = False

        # Client performance dashboard view
        client_performance_view = f"""
        CREATE OR REPLACE VIEW `{self.project_id}.{dataset_id}.client_performance_dashboard` AS
        SELECT
            c.client_id,
            DATE(c.published_at) as report_date,
            COUNT(DISTINCT c.content_id) as content_published,
            COUNT(DISTINCT m.campaign_id) as campaigns_active,
            AVG(JSON_EXTRACT_SCALAR(c.performance_metrics, '$.engagement_score')) as avg_engagement,
            SUM(CAST(JSON_EXTRACT_SCALAR(c.performance_metrics, '$.views') AS INT64)) as total_views,
            SUM(c.revenue_attribution) as total_revenue_attributed
        FROM `{self.project_id}.{dataset_id}.content_performance` c
        LEFT JOIN `{self.project_id}.{dataset_id}.marketing_campaigns` m
            ON c.client_id = m.client_id AND DATE(c.published_at) = DATE(m.created_at)
        WHERE DATE(c.published_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
        GROUP BY c.client_id, report_date
        ORDER BY report_date DESC, total_revenue_attributed DESC
        """

        try:
            self.client.query(client_performance_view).result()
            results["client_performance_dashboard"] = True
            logger.info("Created client performance dashboard view")
        except Exception as e:
            logger.error(f"Failed to create client performance dashboard view: {e}")
            results["client_performance_dashboard"] = False

        return results

# Convenience functions for common operations
def optimize_platform_tables(project_id: str = None) -> Dict[str, Any]:
    """Run complete BigQuery optimization for the platform."""
    optimizer = BigQueryOptimizer(project_id)

    results = {
        "created_tables": optimizer.create_analytics_tables(),
        "optimized_tables": optimizer.optimize_existing_tables(),
        "created_views": optimizer.create_cost_optimization_views(),
        "cost_analysis": optimizer.get_table_costs("xynergy_analytics")
    }

    return results

def get_cost_analysis(project_id: str = None, dataset_id: str = "xynergy_analytics") -> Dict[str, Any]:
    """Get cost analysis for BigQuery tables."""
    optimizer = BigQueryOptimizer(project_id)
    return optimizer.get_table_costs(dataset_id)