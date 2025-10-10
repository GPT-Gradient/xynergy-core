#!/bin/bash
#
# Deploy ASO BigQuery Infrastructure v2
# Uses external schema files for cleaner deployment
#

set -e

PROJECT_ID="xynergy-dev-1757909467"
LOCATION="US"
SCHEMA_DIR="/Users/sesloan/Dev/xynergy-platform/schemas"

echo "=================================================="
echo "ASO Platform BigQuery Setup v2"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo "Location: $LOCATION"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Verifying Datasets${NC}"
echo "------------------------------------------------------"
echo "Datasets already created in previous run:"
bq ls --project_id=${PROJECT_ID} | grep -E "(platform_intelligence|training_data|api_cache|aso_tenant_demo)" || echo "No datasets found"
echo ""

echo -e "${BLUE}Step 2: Creating Platform Intelligence Tables${NC}"
echo "------------------------------------------------------"

# Verified facts table
echo -n "Creating verified_facts table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=verified_date \
  --clustering_fields=topic,tenant_id \
  ${PROJECT_ID}:platform_intelligence.verified_facts \
  ${SCHEMA_DIR}/verified_facts.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Competitor profiles table
echo -n "Creating competitor_profiles table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --clustering_fields=domain,industry \
  ${PROJECT_ID}:platform_intelligence.competitor_profiles \
  ${SCHEMA_DIR}/competitor_profiles.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Competitor content table
echo -n "Creating competitor_content table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=publish_date \
  --clustering_fields=domain \
  ${PROJECT_ID}:platform_intelligence.competitor_content \
  ${SCHEMA_DIR}/competitor_content.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Cross-client patterns table
echo -n "Creating cross_client_patterns table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --clustering_fields=pattern_type,industry \
  ${PROJECT_ID}:platform_intelligence.cross_client_patterns \
  ${SCHEMA_DIR}/cross_client_patterns.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Cost tracking table
echo -n "Creating cost_tracking table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=date \
  --clustering_fields=service_name,api_name \
  ${PROJECT_ID}:platform_intelligence.cost_tracking \
  ${SCHEMA_DIR}/cost_tracking.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

echo ""
echo -e "${BLUE}Step 3: Creating API Cache Tables${NC}"
echo "------------------------------------------------------"

# Keyword data cache
echo -n "Creating keyword_data cache table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=cached_at \
  --time_partitioning_expiration=7776000 \
  --clustering_fields=keyword \
  ${PROJECT_ID}:api_cache.keyword_data \
  ${SCHEMA_DIR}/keyword_data.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# SERP data cache
echo -n "Creating serp_data cache table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=cached_at \
  --time_partitioning_expiration=2592000 \
  --clustering_fields=keyword \
  ${PROJECT_ID}:api_cache.serp_data \
  ${SCHEMA_DIR}/serp_data.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

echo ""
echo -e "${BLUE}Step 4: Creating Training Data Tables${NC}"
echo "------------------------------------------------------"

# LLM interactions
echo -n "Creating llm_interactions table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=created_at \
  --clustering_fields=task_type,success \
  ${PROJECT_ID}:training_data.llm_interactions \
  ${SCHEMA_DIR}/llm_interactions.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Content performance
echo -n "Creating content_performance table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=created_at \
  --clustering_fields=tenant_id,outcome \
  ${PROJECT_ID}:training_data.content_performance \
  ${SCHEMA_DIR}/content_performance.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

echo ""
echo -e "${BLUE}Step 5: Creating Demo Tenant Tables${NC}"
echo "------------------------------------------------------"

# Demo tenant content
echo -n "Creating demo content_pieces table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=created_at \
  --clustering_fields=keyword_primary,status \
  ${PROJECT_ID}:aso_tenant_demo.content_pieces \
  ${SCHEMA_DIR}/content_pieces.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Demo tenant keywords
echo -n "Creating demo keywords table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=last_checked \
  --clustering_fields=keyword,priority \
  ${PROJECT_ID}:aso_tenant_demo.keywords \
  ${SCHEMA_DIR}/keywords.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Demo tenant opportunities
echo -n "Creating demo opportunities table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=detected_at \
  --clustering_fields=opportunity_type,status \
  ${PROJECT_ID}:aso_tenant_demo.opportunities \
  ${SCHEMA_DIR}/opportunities.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Demo tenant predictions
echo -n "Creating demo predictions table... "
bq mk --table \
  --project_id=${PROJECT_ID} \
  --time_partitioning_field=prediction_date \
  --clustering_fields=content_id \
  ${PROJECT_ID}:aso_tenant_demo.performance_predictions \
  ${SCHEMA_DIR}/performance_predictions.json 2>&1 | grep -q "Already Exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

echo ""
echo "=================================================="
echo "Deployment Summary"
echo "=================================================="
echo ""

# Count datasets
DATASET_COUNT=$(bq ls --project_id=${PROJECT_ID} | grep -E "(platform_intelligence|training_data|api_cache|aso_tenant_demo)" | wc -l | xargs)
echo "Datasets verified: $DATASET_COUNT / 4"

# List tables
echo ""
echo "Tables created:"
PI_COUNT=$(bq ls ${PROJECT_ID}:platform_intelligence 2>/dev/null | tail -n +3 | wc -l | xargs)
echo "  platform_intelligence: $PI_COUNT"

AC_COUNT=$(bq ls ${PROJECT_ID}:api_cache 2>/dev/null | tail -n +3 | wc -l | xargs)
echo "  api_cache: $AC_COUNT"

TD_COUNT=$(bq ls ${PROJECT_ID}:training_data 2>/dev/null | tail -n +3 | wc -l | xargs)
echo "  training_data: $TD_COUNT"

DT_COUNT=$(bq ls ${PROJECT_ID}:aso_tenant_demo 2>/dev/null | tail -n +3 | wc -l | xargs)
echo "  aso_tenant_demo: $DT_COUNT"

TOTAL_TABLES=$((PI_COUNT + AC_COUNT + TD_COUNT + DT_COUNT))
echo ""
echo "Total tables: $TOTAL_TABLES / 13"

if [ $TOTAL_TABLES -eq 13 ]; then
  echo ""
  echo -e "${GREEN}✓ ASO BigQuery infrastructure fully deployed!${NC}"
else
  echo ""
  echo -e "${YELLOW}⚠ Some tables may have failed to create. Check logs above.${NC}"
fi

echo ""
echo "Next steps:"
echo "  1. Deploy ASO services to populate data"
echo "  2. Set up Cloud Scheduler for automated collection"
echo "  3. Configure API integrations"
echo ""
