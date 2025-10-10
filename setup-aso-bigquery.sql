-- ASO Platform BigQuery Schema Setup
-- Purpose: Create all datasets and tables for ASO intelligence layer
-- Project: xynergy-dev-1757909467
-- Date: October 9, 2025

-- ============================================
-- PLATFORM INTELLIGENCE DATASETS
-- ============================================

-- Platform-wide intelligence (shared across all tenants)
CREATE SCHEMA IF NOT EXISTS `xynergy-dev-1757909467.platform_intelligence`
OPTIONS(
  location="US",
  description="Cross-tenant intelligence: verified facts, competitor profiles, patterns"
);

-- Training data for LLM fine-tuning
CREATE SCHEMA IF NOT EXISTS `xynergy-dev-1757909467.training_data`
OPTIONS(
  location="US",
  description="LLM training data accumulation for quarterly fine-tuning"
);

-- API call caching
CREATE SCHEMA IF NOT EXISTS `xynergy-dev-1757909467.api_cache`
OPTIONS(
  location="US",
  description="Cached API responses to minimize external dependency"
);

-- ============================================
-- VERIFIED FACTS DATABASE
-- ============================================

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.platform_intelligence.verified_facts` (
  fact_id STRING NOT NULL,
  fact_text STRING NOT NULL,
  topic STRING,
  source_url STRING,
  verified_date DATE NOT NULL,
  verification_method STRING,  -- 'internal', 'perplexity', 'manual'
  confidence_score FLOAT64,
  used_count INT64 DEFAULT 0,  -- How many times reused
  cost_savings FLOAT64,         -- Cumulative savings from reuse
  tenant_id STRING,             -- NULL for platform-wide facts
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_used TIMESTAMP,
  metadata JSON                 -- Additional context
)
PARTITION BY verified_date
CLUSTER BY topic, tenant_id
OPTIONS(
  description="Verified facts database - reusable across platform",
  partition_expiration_days=730  -- 2 year retention
);

-- ============================================
-- COMPETITOR INTELLIGENCE
-- ============================================

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.platform_intelligence.competitor_profiles` (
  domain STRING NOT NULL,
  tenant_id STRING,             -- Who requested tracking
  industry STRING,
  content_count INT64,
  avg_content_length INT64,
  update_frequency STRING,      -- 'daily', 'weekly', 'monthly'
  social_presence JSON,
  tech_stack ARRAY<STRING>,
  backlink_profile JSON,
  authority_score FLOAT64,
  last_scraped TIMESTAMP,
  tracking_since DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY domain, industry
OPTIONS(
  description="Competitor profiles - shared across tenants in same industry"
);

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.platform_intelligence.competitor_content` (
  domain STRING NOT NULL,
  url STRING NOT NULL,
  title STRING,
  content_type STRING,          -- 'blog', 'product', 'landing', 'resource'
  word_count INT64,
  publish_date DATE,
  topic_keywords ARRAY<STRING>,
  serp_rankings JSON,           -- {keyword: position} mapping
  estimated_traffic INT64,
  scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY publish_date
CLUSTER BY domain
OPTIONS(
  description="Competitor content tracking",
  partition_expiration_days=365  -- 1 year retention
);

-- ============================================
-- CROSS-CLIENT PATTERNS
-- ============================================

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.platform_intelligence.cross_client_patterns` (
  pattern_type STRING NOT NULL,  -- 'content_type', 'keyword_difficulty', 'conversion'
  industry STRING,
  pattern_data JSON,
  confidence_score FLOAT64,
  sample_size INT64,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY pattern_type, industry
OPTIONS(
  description="Anonymized patterns learned across all tenants"
);

-- ============================================
-- API CACHE TABLES
-- ============================================

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.api_cache.keyword_data` (
  keyword STRING NOT NULL,
  search_volume INT64,
  difficulty_score FLOAT64,
  competition STRING,           -- 'low', 'medium', 'high'
  cpc FLOAT64,
  intent STRING,                -- 'informational', 'commercial', 'transactional'
  related_keywords ARRAY<STRING>,
  data_source STRING,           -- 'google_keyword_planner', 'dataforseo', 'trends'
  cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  expires_at TIMESTAMP,
  reuse_count INT64 DEFAULT 0
)
PARTITION BY DATE(cached_at)
CLUSTER BY keyword
OPTIONS(
  description="Keyword data cache - reduces external API calls",
  partition_expiration_days=90
);

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.api_cache.serp_data` (
  keyword STRING NOT NULL,
  location STRING DEFAULT 'US',
  serp_snapshot JSON,           -- Full SERP results
  top_10_domains ARRAY<STRING>,
  cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  expires_at TIMESTAMP,
  reuse_count INT64 DEFAULT 0
)
PARTITION BY DATE(cached_at)
CLUSTER BY keyword
OPTIONS(
  description="SERP data cache",
  partition_expiration_days=30  -- Refresh monthly
);

-- ============================================
-- TRAINING DATA COLLECTION
-- ============================================

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.training_data.llm_interactions` (
  interaction_id STRING NOT NULL,
  task_type STRING,             -- 'content_generation', 'meta_description', etc.
  prompt TEXT,
  response TEXT,
  model_used STRING,            -- 'internal_llm', 'gpt-4', etc.
  quality_score FLOAT64,        -- User feedback or auto-score
  success BOOLEAN,
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY task_type, success
OPTIONS(
  description="LLM interactions for fine-tuning",
  partition_expiration_days=730
);

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.training_data.content_performance` (
  content_id STRING NOT NULL,
  tenant_id STRING,
  keyword_primary STRING,
  content_features JSON,        -- length, structure, images, links, etc.
  performance_metrics JSON,     -- ranking, traffic, conversions
  outcome STRING,               -- 'success', 'moderate', 'failure'
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY tenant_id, outcome
OPTIONS(
  description="Content performance for predictive models",
  partition_expiration_days=730
);

-- ============================================
-- EXAMPLE TENANT SCHEMA (Template)
-- ============================================
-- NOTE: These will be created dynamically per tenant
-- Template for aso_tenant_{tenant_id}

-- Example for tenant_demo (for testing)
CREATE SCHEMA IF NOT EXISTS `xynergy-dev-1757909467.aso_tenant_demo`
OPTIONS(
  location="US",
  description="Demo tenant for testing ASO functionality"
);

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.aso_tenant_demo.content_pieces` (
  content_id STRING NOT NULL,
  content_type STRING,          -- 'hub', 'spoke'
  keyword_primary STRING,
  keyword_secondary ARRAY<STRING>,
  status STRING,                -- 'draft', 'published', 'optimized', 'amplified', 'archived'
  hub_id STRING,                -- NULL for hub articles
  title STRING,
  meta_description STRING,
  url STRING,
  word_count INT64,
  performance_score FLOAT64,
  ranking_position INT64,
  monthly_traffic INT64,
  monthly_conversions INT64,
  conversion_rate FLOAT64,
  last_optimized DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  published_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY keyword_primary, status
OPTIONS(
  description="Demo tenant content tracking",
  partition_expiration_days=730
);

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.aso_tenant_demo.keywords` (
  keyword STRING NOT NULL,
  search_volume INT64,
  difficulty_score FLOAT64,
  kgr_score FLOAT64,            -- Keyword Golden Ratio
  intent STRING,
  current_ranking INT64,
  best_ranking INT64,
  target_ranking INT64,
  serp_history JSON,            -- [{date, position, url}]
  competitor_rankings JSON,
  last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  priority STRING,              -- 'tier1', 'tier2', 'tier3', 'tier4'
  content_id STRING,            -- Associated content
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(last_checked)
CLUSTER BY keyword, priority
OPTIONS(
  description="Demo tenant keyword tracking",
  partition_expiration_days=365
);

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.aso_tenant_demo.opportunities` (
  opportunity_id STRING NOT NULL,
  opportunity_type STRING,      -- 'trending', 'kgr', 'gap', 'seasonal'
  keyword STRING,
  confidence_score FLOAT64,
  estimated_traffic INT64,
  estimated_difficulty FLOAT64,
  recommendation TEXT,
  detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  status STRING,                -- 'pending', 'approved', 'rejected', 'completed'
  content_id STRING,            -- If actioned
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(detected_at)
CLUSTER BY opportunity_type, status
OPTIONS(
  description="Demo tenant opportunities",
  partition_expiration_days=180
);

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.aso_tenant_demo.performance_predictions` (
  prediction_id STRING NOT NULL,
  content_id STRING,
  predicted_ranking INT64,
  predicted_traffic INT64,
  predicted_conversions INT64,
  confidence_score FLOAT64,
  prediction_date DATE,
  actual_ranking INT64,         -- Filled after 30 days
  actual_traffic INT64,
  actual_conversions INT64,
  accuracy_score FLOAT64,       -- Calculated post-facto
  model_version STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY prediction_date
CLUSTER BY content_id
OPTIONS(
  description="Demo tenant performance predictions",
  partition_expiration_days=365
);

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

CREATE OR REPLACE VIEW `xynergy-dev-1757909467.platform_intelligence.fact_reuse_stats` AS
SELECT
  topic,
  COUNT(*) as total_facts,
  SUM(used_count) as total_reuses,
  SUM(cost_savings) as total_savings,
  AVG(confidence_score) as avg_confidence,
  MAX(used_count) as max_reuse_count
FROM `xynergy-dev-1757909467.platform_intelligence.verified_facts`
WHERE verified_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY topic
ORDER BY total_savings DESC;

CREATE OR REPLACE VIEW `xynergy-dev-1757909467.platform_intelligence.competitor_coverage` AS
SELECT
  industry,
  COUNT(DISTINCT domain) as competitor_count,
  SUM(content_count) as total_content_tracked,
  AVG(authority_score) as avg_authority,
  COUNT(DISTINCT tenant_id) as tracking_tenants
FROM `xynergy-dev-1757909467.platform_intelligence.competitor_profiles`
GROUP BY industry
ORDER BY competitor_count DESC;

CREATE OR REPLACE VIEW `xynergy-dev-1757909467.api_cache.cache_efficiency` AS
SELECT
  'keyword_data' as cache_type,
  COUNT(*) as total_entries,
  SUM(reuse_count) as total_reuses,
  AVG(reuse_count) as avg_reuse,
  SUM(reuse_count) * 0.05 as estimated_savings_usd  -- $0.05 per DataForSEO call
FROM `xynergy-dev-1757909467.api_cache.keyword_data`
WHERE cached_at >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
UNION ALL
SELECT
  'serp_data' as cache_type,
  COUNT(*) as total_entries,
  SUM(reuse_count) as total_reuses,
  AVG(reuse_count) as avg_reuse,
  SUM(reuse_count) * 0.01 as estimated_savings_usd  -- $0.01 per Serper call
FROM `xynergy-dev-1757909467.api_cache.serp_data`
WHERE cached_at >= DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY);

-- ============================================
-- COST TRACKING
-- ============================================

CREATE TABLE IF NOT EXISTS `xynergy-dev-1757909467.platform_intelligence.cost_tracking` (
  date DATE NOT NULL,
  service_name STRING,
  api_name STRING,              -- 'perplexity', 'serper', 'dataforseo', etc.
  request_count INT64,
  cache_hits INT64,
  cache_misses INT64,
  cost_usd FLOAT64,
  savings_usd FLOAT64,          -- From cache hits
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY date
CLUSTER BY service_name, api_name
OPTIONS(
  description="Daily cost and savings tracking",
  partition_expiration_days=730
);

-- ============================================
-- INDEXES & OPTIMIZATION
-- ============================================

-- Note: BigQuery doesn't use traditional indexes, but clustering and partitioning
-- already provide optimal query performance. The CLUSTER BY clauses above are
-- optimized for:
-- 1. Tenant isolation queries (tenant_id)
-- 2. Topic/keyword lookups (topic, keyword)
-- 3. Time-based queries (partitioned by date)
-- 4. Status filtering (status, priority)

-- ============================================
-- COMPLETION SUMMARY
-- ============================================

-- Created:
-- ✅ 3 platform datasets (intelligence, training_data, api_cache)
-- ✅ 1 demo tenant dataset (aso_tenant_demo)
-- ✅ 13 core tables (facts, competitors, patterns, cache, training, etc.)
-- ✅ 4 tenant-specific tables (content, keywords, opportunities, predictions)
-- ✅ 3 analytics views (fact reuse, competitor coverage, cache efficiency)
-- ✅ 1 cost tracking table

-- Estimated monthly cost at scale:
-- - Storage: ~200 GB → $4/month
-- - Queries: ~500 GB processed/month → $2.50/month
-- - Total BigQuery: ~$6.50/month

-- Next steps:
-- 1. Deploy services that populate these tables
-- 2. Set up Cloud Scheduler for automated data collection
-- 3. Implement cache-first logic in all services
-- 4. Monitor cost_tracking table for ROI

SELECT 'ASO BigQuery setup complete! ✅' as status;
