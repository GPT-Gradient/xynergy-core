#!/bin/bash
#
# Deploy ASO BigQuery Infrastructure
# Creates datasets, tables, and views for ASO platform
#

set -e

PROJECT_ID="xynergy-dev-1757909467"
LOCATION="US"

echo "=================================================="
echo "ASO Platform BigQuery Setup"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo "Location: $LOCATION"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Creating Datasets${NC}"
echo "------------------------------------------------------"

# Create platform intelligence dataset
echo -n "Creating platform_intelligence dataset... "
bq mk --dataset \
  --location=$LOCATION \
  --description="Cross-tenant intelligence: facts, competitors, patterns" \
  ${PROJECT_ID}:platform_intelligence 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Create training data dataset
echo -n "Creating training_data dataset... "
bq mk --dataset \
  --location=$LOCATION \
  --description="LLM training data for fine-tuning" \
  ${PROJECT_ID}:training_data 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Create API cache dataset
echo -n "Creating api_cache dataset... "
bq mk --dataset \
  --location=$LOCATION \
  --description="Cached API responses" \
  ${PROJECT_ID}:api_cache 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Create demo tenant dataset
echo -n "Creating aso_tenant_demo dataset... "
bq mk --dataset \
  --location=$LOCATION \
  --description="Demo tenant for testing" \
  ${PROJECT_ID}:aso_tenant_demo 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

echo ""
echo -e "${BLUE}Step 2: Creating Platform Intelligence Tables${NC}"
echo "------------------------------------------------------"

# Verified facts table
echo -n "Creating verified_facts table... "
bq mk --table \
  --time_partitioning_field=verified_date \
  --clustering_fields=topic,tenant_id \
  --schema='[
    {"name":"fact_id","type":"STRING","mode":"REQUIRED"},
    {"name":"fact_text","type":"STRING","mode":"REQUIRED"},
    {"name":"topic","type":"STRING"},
    {"name":"source_url","type":"STRING"},
    {"name":"verified_date","type":"DATE","mode":"REQUIRED"},
    {"name":"verification_method","type":"STRING"},
    {"name":"confidence_score","type":"FLOAT64"},
    {"name":"used_count","type":"INT64"},
    {"name":"cost_savings","type":"FLOAT64"},
    {"name":"tenant_id","type":"STRING"},
    {"name":"created_at","type":"TIMESTAMP"},
    {"name":"last_used","type":"TIMESTAMP"},
    {"name":"metadata","type":"JSON"}
  ]' \
  ${PROJECT_ID}:platform_intelligence.verified_facts 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Competitor profiles table
echo -n "Creating competitor_profiles table... "
bq mk --table \
  --clustering_fields=domain,industry \
  --schema='[
    {"name":"domain","type":"STRING","mode":"REQUIRED"},
    {"name":"tenant_id","type":"STRING"},
    {"name":"industry","type":"STRING"},
    {"name":"content_count","type":"INT64"},
    {"name":"avg_content_length","type":"INT64"},
    {"name":"update_frequency","type":"STRING"},
    {"name":"social_presence","type":"JSON"},
    {"name":"tech_stack","type":"STRING","mode":"REPEATED"},
    {"name":"backlink_profile","type":"JSON"},
    {"name":"authority_score","type":"FLOAT64"},
    {"name":"last_scraped","type":"TIMESTAMP"},
    {"name":"tracking_since","type":"DATE"},
    {"name":"created_at","type":"TIMESTAMP"},
    {"name":"updated_at","type":"TIMESTAMP"}
  ]' \
  ${PROJECT_ID}:platform_intelligence.competitor_profiles 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Competitor content table
echo -n "Creating competitor_content table... "
bq mk --table \
  --time_partitioning_field=publish_date \
  --clustering_fields=domain \
  --schema='[
    {"name":"domain","type":"STRING","mode":"REQUIRED"},
    {"name":"url","type":"STRING","mode":"REQUIRED"},
    {"name":"title","type":"STRING"},
    {"name":"content_type","type":"STRING"},
    {"name":"word_count","type":"INT64"},
    {"name":"publish_date","type":"DATE"},
    {"name":"topic_keywords","type":"STRING","mode":"REPEATED"},
    {"name":"serp_rankings","type":"JSON"},
    {"name":"estimated_traffic","type":"INT64"},
    {"name":"scraped_at","type":"TIMESTAMP"}
  ]' \
  ${PROJECT_ID}:platform_intelligence.competitor_content 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Cross-client patterns table
echo -n "Creating cross_client_patterns table... "
bq mk --table \
  --clustering_fields=pattern_type,industry \
  --schema='[
    {"name":"pattern_type","type":"STRING","mode":"REQUIRED"},
    {"name":"industry","type":"STRING"},
    {"name":"pattern_data","type":"JSON"},
    {"name":"confidence_score","type":"FLOAT64"},
    {"name":"sample_size","type":"INT64"},
    {"name":"last_updated","type":"TIMESTAMP"},
    {"name":"created_at","type":"TIMESTAMP"}
  ]' \
  ${PROJECT_ID}:platform_intelligence.cross_client_patterns 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Cost tracking table
echo -n "Creating cost_tracking table... "
bq mk --table \
  --time_partitioning_field=date \
  --clustering_fields=service_name,api_name \
  --schema='[
    {"name":"date","type":"DATE","mode":"REQUIRED"},
    {"name":"service_name","type":"STRING"},
    {"name":"api_name","type":"STRING"},
    {"name":"request_count","type":"INT64"},
    {"name":"cache_hits","type":"INT64"},
    {"name":"cache_misses","type":"INT64"},
    {"name":"cost_usd","type":"FLOAT64"},
    {"name":"savings_usd","type":"FLOAT64"},
    {"name":"created_at","type":"TIMESTAMP"}
  ]' \
  ${PROJECT_ID}:platform_intelligence.cost_tracking 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

echo ""
echo -e "${BLUE}Step 3: Creating API Cache Tables${NC}"
echo "------------------------------------------------------"

# Keyword data cache
echo -n "Creating keyword_data cache table... "
bq mk --table \
  --time_partitioning_field=cached_at \
  --time_partitioning_expiration=7776000 \
  --clustering_fields=keyword \
  --schema='[
    {"name":"keyword","type":"STRING","mode":"REQUIRED"},
    {"name":"search_volume","type":"INT64"},
    {"name":"difficulty_score","type":"FLOAT64"},
    {"name":"competition","type":"STRING"},
    {"name":"cpc","type":"FLOAT64"},
    {"name":"intent","type":"STRING"},
    {"name":"related_keywords","type":"STRING","mode":"REPEATED"},
    {"name":"data_source","type":"STRING"},
    {"name":"cached_at","type":"TIMESTAMP"},
    {"name":"expires_at","type":"TIMESTAMP"},
    {"name":"reuse_count","type":"INT64"}
  ]' \
  ${PROJECT_ID}:api_cache.keyword_data 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# SERP data cache
echo -n "Creating serp_data cache table... "
bq mk --table \
  --time_partitioning_field=cached_at \
  --time_partitioning_expiration=2592000 \
  --clustering_fields=keyword \
  --schema='[
    {"name":"keyword","type":"STRING","mode":"REQUIRED"},
    {"name":"location","type":"STRING"},
    {"name":"serp_snapshot","type":"JSON"},
    {"name":"top_10_domains","type":"STRING","mode":"REPEATED"},
    {"name":"cached_at","type":"TIMESTAMP"},
    {"name":"expires_at","type":"TIMESTAMP"},
    {"name":"reuse_count","type":"INT64"}
  ]' \
  ${PROJECT_ID}:api_cache.serp_data 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

echo ""
echo -e "${BLUE}Step 4: Creating Training Data Tables${NC}"
echo "------------------------------------------------------"

# LLM interactions
echo -n "Creating llm_interactions table... "
bq mk --table \
  --time_partitioning_field=created_at \
  --clustering_fields=task_type,success \
  --schema='[
    {"name":"interaction_id","type":"STRING","mode":"REQUIRED"},
    {"name":"task_type","type":"STRING"},
    {"name":"prompt","type":"STRING"},
    {"name":"response","type":"STRING"},
    {"name":"model_used","type":"STRING"},
    {"name":"quality_score","type":"FLOAT64"},
    {"name":"success","type":"BOOLEAN"},
    {"name":"metadata","type":"JSON"},
    {"name":"created_at","type":"TIMESTAMP"}
  ]' \
  ${PROJECT_ID}:training_data.llm_interactions 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Content performance
echo -n "Creating content_performance table... "
bq mk --table \
  --time_partitioning_field=created_at \
  --clustering_fields=tenant_id,outcome \
  --schema='[
    {"name":"content_id","type":"STRING","mode":"REQUIRED"},
    {"name":"tenant_id","type":"STRING"},
    {"name":"keyword_primary","type":"STRING"},
    {"name":"content_features","type":"JSON"},
    {"name":"performance_metrics","type":"JSON"},
    {"name":"outcome","type":"STRING"},
    {"name":"created_at","type":"TIMESTAMP"}
  ]' \
  ${PROJECT_ID}:training_data.content_performance 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

echo ""
echo -e "${BLUE}Step 5: Creating Demo Tenant Tables${NC}"
echo "------------------------------------------------------"

# Demo tenant content
echo -n "Creating demo content_pieces table... "
bq mk --table \
  --time_partitioning_field=created_at \
  --clustering_fields=keyword_primary,status \
  --schema='[
    {"name":"content_id","type":"STRING","mode":"REQUIRED"},
    {"name":"content_type","type":"STRING"},
    {"name":"keyword_primary","type":"STRING"},
    {"name":"keyword_secondary","type":"STRING","mode":"REPEATED"},
    {"name":"status","type":"STRING"},
    {"name":"hub_id","type":"STRING"},
    {"name":"title","type":"STRING"},
    {"name":"meta_description","type":"STRING"},
    {"name":"url","type":"STRING"},
    {"name":"word_count","type":"INT64"},
    {"name":"performance_score","type":"FLOAT64"},
    {"name":"ranking_position","type":"INT64"},
    {"name":"monthly_traffic","type":"INT64"},
    {"name":"monthly_conversions","type":"INT64"},
    {"name":"conversion_rate","type":"FLOAT64"},
    {"name":"last_optimized","type":"DATE"},
    {"name":"created_at","type":"TIMESTAMP"},
    {"name":"published_at","type":"TIMESTAMP"},
    {"name":"updated_at","type":"TIMESTAMP"}
  ]' \
  ${PROJECT_ID}:aso_tenant_demo.content_pieces 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Demo tenant keywords
echo -n "Creating demo keywords table... "
bq mk --table \
  --time_partitioning_field=last_checked \
  --clustering_fields=keyword,priority \
  --schema='[
    {"name":"keyword","type":"STRING","mode":"REQUIRED"},
    {"name":"search_volume","type":"INT64"},
    {"name":"difficulty_score","type":"FLOAT64"},
    {"name":"kgr_score","type":"FLOAT64"},
    {"name":"intent","type":"STRING"},
    {"name":"current_ranking","type":"INT64"},
    {"name":"best_ranking","type":"INT64"},
    {"name":"target_ranking","type":"INT64"},
    {"name":"serp_history","type":"JSON"},
    {"name":"competitor_rankings","type":"JSON"},
    {"name":"last_checked","type":"TIMESTAMP"},
    {"name":"priority","type":"STRING"},
    {"name":"content_id","type":"STRING"},
    {"name":"created_at","type":"TIMESTAMP"}
  ]' \
  ${PROJECT_ID}:aso_tenant_demo.keywords 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Demo tenant opportunities
echo -n "Creating demo opportunities table... "
bq mk --table \
  --time_partitioning_field=detected_at \
  --clustering_fields=opportunity_type,status \
  --schema='[
    {"name":"opportunity_id","type":"STRING","mode":"REQUIRED"},
    {"name":"opportunity_type","type":"STRING"},
    {"name":"keyword","type":"STRING"},
    {"name":"confidence_score","type":"FLOAT64"},
    {"name":"estimated_traffic","type":"INT64"},
    {"name":"estimated_difficulty","type":"FLOAT64"},
    {"name":"recommendation","type":"STRING"},
    {"name":"detected_at","type":"TIMESTAMP"},
    {"name":"status","type":"STRING"},
    {"name":"content_id","type":"STRING"},
    {"name":"created_at","type":"TIMESTAMP"}
  ]' \
  ${PROJECT_ID}:aso_tenant_demo.opportunities 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

# Demo tenant predictions
echo -n "Creating demo predictions table... "
bq mk --table \
  --time_partitioning_field=prediction_date \
  --clustering_fields=content_id \
  --schema='[
    {"name":"prediction_id","type":"STRING","mode":"REQUIRED"},
    {"name":"content_id","type":"STRING"},
    {"name":"predicted_ranking","type":"INT64"},
    {"name":"predicted_traffic","type":"INT64"},
    {"name":"predicted_conversions","type":"INT64"},
    {"name":"confidence_score","type":"FLOAT64"},
    {"name":"prediction_date","type":"DATE"},
    {"name":"actual_ranking","type":"INT64"},
    {"name":"actual_traffic","type":"INT64"},
    {"name":"actual_conversions","type":"INT64"},
    {"name":"accuracy_score","type":"FLOAT64"},
    {"name":"model_version","type":"STRING"},
    {"name":"created_at","type":"TIMESTAMP"}
  ]' \
  ${PROJECT_ID}:aso_tenant_demo.performance_predictions 2>/dev/null && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Exists${NC}"

echo ""
echo "=================================================="
echo "Deployment Summary"
echo "=================================================="
echo ""

# Count datasets
DATASET_COUNT=$(bq ls --project_id=${PROJECT_ID} | grep -E "(platform_intelligence|training_data|api_cache|aso_tenant_demo)" | wc -l)
echo "Datasets created: $DATASET_COUNT / 4"

# List tables
echo ""
echo "Tables created:"
bq ls ${PROJECT_ID}:platform_intelligence | tail -n +3 | wc -l | xargs echo "  platform_intelligence:"
bq ls ${PROJECT_ID}:api_cache | tail -n +3 | wc -l | xargs echo "  api_cache:"
bq ls ${PROJECT_ID}:training_data | tail -n +3 | wc -l | xargs echo "  training_data:"
bq ls ${PROJECT_ID}:aso_tenant_demo | tail -n +3 | wc -l | xargs echo "  aso_tenant_demo:"

echo ""
echo -e "${GREEN}✓ ASO BigQuery infrastructure deployed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Deploy ASO services to populate data"
echo "  2. Set up Cloud Scheduler for automated collection"
echo "  3. Configure API integrations"
echo ""
