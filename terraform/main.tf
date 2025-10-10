# Xynergy Platform - Foundation Infrastructure Only
# This creates the foundation without Cloud Run services

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "xynergy-dev-1757909467"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# Local Values
locals {
  common_labels = {
    environment = var.environment
    platform    = "xynergy"
    managed_by  = "terraform"
  }
  
  service_names = {
    marketing_engine    = "xynergy-marketing-engine"
    content_hub        = "xynergy-content-hub"
    ai_assistant       = "xynergy-ai-assistant"
    system_runtime     = "xynergy-system-runtime"
    analytics          = "xynergy-analytics"
    secrets_config     = "xynergy-secrets-config"
    scheduler          = "xynergy-scheduler"
    reports_export     = "xynergy-reports-export"
    security_governance = "xynergy-security-governance"
    qa_engine          = "xynergy-qa-engine"
    project_management = "xynergy-project-management"
    # Research Engine Services
    research_coordinator = "xynergy-research-coordinator"
    market_intelligence = "xynergy-market-intelligence"
    competitive_analysis = "xynergy-competitive-analysis"
    content_research   = "xynergy-content-research"
    # Trending Engine Services
    trending_coordinator = "xynergy-trending-coordinator"
    real_time_monitor   = "xynergy-real-time-monitor"
    rapid_generator     = "xynergy-rapid-generator"
    trend_publisher     = "xynergy-trend-publisher"
  }
}

#############################################################################
# FOUNDATION RESOURCES ONLY
#############################################################################

# Artifact Registry for Container Images
resource "google_artifact_registry_repository" "xynergy_registry" {
  location      = var.region
  repository_id = "xynergy-platform"
  description   = "Container registry for Xynergy platform services"
  format        = "DOCKER"
  
  labels = local.common_labels
}

# Pub/Sub Topics for Inter-Service Communication
resource "google_pubsub_topic" "service_events" {
  for_each = local.service_names
  
  name = "${each.value}-events"
  
  labels = merge(local.common_labels, {
    service = each.key
  })
}

# Pub/Sub Subscriptions
resource "google_pubsub_subscription" "service_subscriptions" {
  for_each = local.service_names

  name  = "${each.value}-subscription"
  topic = google_pubsub_topic.service_events[each.key].name

  labels = merge(local.common_labels, {
    service = each.key
  })

  # Message retention for 7 days
  message_retention_duration = "604800s"

  # Acknowledge deadline
  ack_deadline_seconds = 20
}

# Research Engine Specific Topics
resource "google_pubsub_topic" "research_engine_topics" {
  for_each = toset([
    "trend-identified",
    "competitor-alert",
    "research-complete",
    "content-opportunity"
  ])

  name = each.key

  labels = merge(local.common_labels, {
    engine = "research"
  })
}

# Trending Engine Specific Topics
resource "google_pubsub_topic" "trending_engine_topics" {
  for_each = toset([
    "trend-velocity-alert",
    "rapid-content-request",
    "content-generated",
    "publishing-triggered",
    "trend-peak-detected",
    "competitive-gap-alert"
  ])

  name = each.key

  labels = merge(local.common_labels, {
    engine = "trending"
  })
}

resource "google_pubsub_subscription" "research_engine_subscriptions" {
  for_each = google_pubsub_topic.research_engine_topics

  name  = "${each.key}-subscription"
  topic = each.value.name

  labels = merge(local.common_labels, {
    engine = "research"
  })

  message_retention_duration = "604800s"
  ack_deadline_seconds = 20
}

resource "google_pubsub_subscription" "trending_engine_subscriptions" {
  for_each = google_pubsub_topic.trending_engine_topics

  name  = "${each.key}-subscription"
  topic = each.value.name

  labels = merge(local.common_labels, {
    engine = "trending"
  })

  message_retention_duration = "604800s"
  ack_deadline_seconds = 10  # Faster ack for real-time processing
}

# BigQuery Dataset for Analytics
resource "google_bigquery_dataset" "xynergy_analytics" {
  dataset_id  = "xynergy_analytics"
  description = "Xynergy platform analytics and data processing"
  location    = "US"
  
  labels = local.common_labels
  
  # Data retention policies
  default_table_expiration_ms = 7776000000  # 90 days
}

# Cloud Storage Buckets
resource "google_storage_bucket" "xynergy_content" {
  name     = "${var.project_id}-xynergy-content"
  location = var.region
  
  labels = local.common_labels
  
  # Uniform bucket-level access
  uniform_bucket_level_access = true
  
  # Lifecycle management
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  
  # Versioning
  versioning {
    enabled = true
  }
}

resource "google_storage_bucket" "xynergy_reports" {
  name     = "${var.project_id}-xynergy-reports"
  location = var.region

  labels = local.common_labels

  # Uniform bucket-level access
  uniform_bucket_level_access = true

  # Lifecycle management - keep reports longer
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}

# Research Engine Storage
resource "google_storage_bucket" "xynergy_research_data" {
  name     = "${var.project_id}-xynergy-research"
  location = var.region

  labels = merge(local.common_labels, {
    engine = "research"
  })

  # Uniform bucket-level access
  uniform_bucket_level_access = true

  # Lifecycle management - research data retention
  lifecycle_rule {
    condition {
      age = 90  # 90 days as per requirements
    }
    action {
      type = "Delete"
    }
  }

  # Versioning for research data
  versioning {
    enabled = true
  }
}

# Trending Engine Storage
resource "google_storage_bucket" "xynergy_trending_data" {
  name     = "${var.project_id}-xynergy-trending"
  location = var.region

  labels = merge(local.common_labels, {
    engine = "trending"
  })

  # Uniform bucket-level access
  uniform_bucket_level_access = true

  # Lifecycle management - trending data retention (shorter than research)
  lifecycle_rule {
    condition {
      age = 30  # 30 days for trending data
    }
    action {
      type = "Delete"
    }
  }

  # Versioning for trending data
  versioning {
    enabled = true
  }
}

# Redis Cache for Trending Engine
resource "google_redis_instance" "trending_cache" {
  name           = "xynergy-trending-cache"
  memory_size_gb = 1
  region         = var.region

  labels = merge(local.common_labels, {
    engine = "trending"
    purpose = "cache"
  })

  # Configuration for high performance
  redis_version     = "REDIS_6_X"
  tier             = "STANDARD_HA"
  replica_count    = 1
  read_replicas_mode = "READ_REPLICAS_ENABLED"

  # Network configuration
  authorized_network = "default"

  # High availability
  location_id             = "${var.region}-a"
  alternative_location_id = "${var.region}-b"
}

#############################################################################
# SERVICE ACCOUNTS
#############################################################################

# Service Account for Platform Services
resource "google_service_account" "xynergy_platform" {
  account_id   = "xynergy-platform-sa"
  display_name = "Xynergy Platform Service Account"
  description  = "Service account for Xynergy platform services"
}

# IAM Bindings for Platform Service Account
resource "google_project_iam_member" "xynergy_platform_permissions" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/datastore.user",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/storage.objectAdmin",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.xynergy_platform.email}"
}

#############################################################################
# OUTPUTS
#############################################################################

output "artifact_registry" {
  description = "Artifact Registry repository for container images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.xynergy_registry.repository_id}"
}

output "pubsub_topics" {
  description = "Pub/Sub topics for inter-service communication"
  value = {
    for k, v in google_pubsub_topic.service_events : k => v.name
  }
}

output "storage_buckets" {
  description = "Storage buckets for content and reports"
  value = {
    content = google_storage_bucket.xynergy_content.name
    reports = google_storage_bucket.xynergy_reports.name
  }
}

output "bigquery_dataset" {
  description = "BigQuery dataset for analytics"
  value       = google_bigquery_dataset.xynergy_analytics.dataset_id
}

output "service_account" {
  description = "Platform service account email"
  value       = google_service_account.xynergy_platform.email
}

# Validation & Fact-Check Engine Services (Phase 3)
resource "google_pubsub_topic" "validation_tasks" {
  name = "validation-tasks"

  labels = {
    engine = "validation"
    phase = "3"
  }
}

resource "google_pubsub_topic" "fact_check_requests" {
  name = "fact-check-requests"

  labels = {
    engine = "validation"
    phase = "3"
  }
}

resource "google_pubsub_topic" "plagiarism_checks" {
  name = "plagiarism-checks"

  labels = {
    engine = "validation"
    phase = "3"
  }
}

resource "google_pubsub_topic" "validation_complete" {
  name = "validation-complete"

  labels = {
    engine = "validation"
    phase = "3"
  }
}

# BigQuery dataset for validation metrics
resource "google_bigquery_dataset" "validation_analytics" {
  dataset_id = "validation_analytics"
  location   = var.region

  labels = {
    engine = "validation"
    phase = "3"
  }
}

resource "google_bigquery_table" "content_validations" {
  dataset_id = google_bigquery_dataset.validation_analytics.dataset_id
  table_id   = "content_validations"

  schema = jsonencode([
    {
      name = "validation_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "content_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "validation_timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "accuracy_score"
      type = "FLOAT"
      mode = "REQUIRED"
    },
    {
      name = "fact_check_results"
      type = "JSON"
      mode = "NULLABLE"
    },
    {
      name = "plagiarism_score"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "trust_safety_score"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "validation_status"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "failed_checks"
      type = "JSON"
      mode = "NULLABLE"
    }
  ])
}

# Attribution & Analytics Engine Services (Phase 4)
resource "google_pubsub_topic" "attribution_events" {
  name = "attribution-events"

  labels = {
    engine = "attribution"
    phase = "4"
  }
}

resource "google_pubsub_topic" "revenue_tracking" {
  name = "revenue-tracking"

  labels = {
    engine = "attribution"
    phase = "4"
  }
}

resource "google_pubsub_topic" "performance_analytics" {
  name = "performance-analytics"

  labels = {
    engine = "attribution"
    phase = "4"
  }
}

resource "google_pubsub_topic" "client_reporting" {
  name = "client-reporting"

  labels = {
    engine = "attribution"
    phase = "4"
  }
}

# BigQuery dataset for attribution analytics
resource "google_bigquery_dataset" "attribution_analytics" {
  dataset_id = "attribution_analytics"
  location   = var.region

  labels = {
    engine = "attribution"
    phase = "4"
  }
}

resource "google_bigquery_table" "customer_journeys" {
  dataset_id = google_bigquery_dataset.attribution_analytics.dataset_id
  table_id   = "customer_journeys"

  schema = jsonencode([
    {
      name = "journey_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "customer_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "client_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "journey_start"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "journey_end"
      type = "TIMESTAMP"
      mode = "NULLABLE"
    },
    {
      name = "touchpoints"
      type = "JSON"
      mode = "REQUIRED"
    },
    {
      name = "conversion_events"
      type = "JSON"
      mode = "NULLABLE"
    },
    {
      name = "revenue_attributed"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "attribution_model"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "keyword_attribution"
      type = "JSON"
      mode = "NULLABLE"
    }
  ])
}

resource "google_bigquery_table" "performance_metrics" {
  dataset_id = google_bigquery_dataset.attribution_analytics.dataset_id
  table_id   = "performance_metrics"

  schema = jsonencode([
    {
      name = "metric_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "client_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "metric_timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "time_period"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "organic_traffic"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "keyword_rankings"
      type = "JSON"
      mode = "NULLABLE"
    },
    {
      name = "conversion_rate"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "engagement_metrics"
      type = "JSON"
      mode = "NULLABLE"
    },
    {
      name = "revenue_attributed"
      type = "FLOAT"
      mode = "NULLABLE"
    },
    {
      name = "roi_calculated"
      type = "FLOAT"
      mode = "NULLABLE"
    }
  ])
}

resource "google_bigquery_table" "client_dashboard_data" {
  dataset_id = google_bigquery_dataset.attribution_analytics.dataset_id
  table_id   = "client_dashboard_data"

  schema = jsonencode([
    {
      name = "dashboard_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "client_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "report_timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "reporting_period"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "traffic_growth"
      type = "JSON"
      mode = "REQUIRED"
    },
    {
      name = "ranking_improvements"
      type = "JSON"
      mode = "REQUIRED"
    },
    {
      name = "goal_achievement"
      type = "JSON"
      mode = "REQUIRED"
    },
    {
      name = "content_performance"
      type = "JSON"
      mode = "REQUIRED"
    },
    {
      name = "financial_metrics_background"
      type = "JSON"
      mode = "NULLABLE"
    }
  ])
}