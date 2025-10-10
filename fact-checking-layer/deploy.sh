#!/bin/bash
#
# Deploy Fact Checking Layer
#

set -e

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
SERVICE_NAME="fact-checking-layer"
IMAGE_URI="us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-platform/${SERVICE_NAME}:latest"

echo "=================================================="
echo "Deploying Fact Checking Layer"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Building container image${NC}"
echo "------------------------------------------------------"

gcloud builds submit \
  --project=${PROJECT_ID} \
  --tag=${IMAGE_URI} \
  .

echo ""
echo -e "${BLUE}Step 2: Deploying to Cloud Run${NC}"
echo "------------------------------------------------------"

gcloud run deploy ${SERVICE_NAME} \
  --project=${PROJECT_ID} \
  --region=${REGION} \
  --image=${IMAGE_URI} \
  --platform=managed \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=0 \
  --max-instances=10 \
  --set-env-vars="PROJECT_ID=${PROJECT_ID},REGION=${REGION},PERPLEXITY_API_KEY=" \
  --timeout=300 \
  --concurrency=80

echo ""
echo -e "${BLUE}Step 3: Getting service URL${NC}"
echo "------------------------------------------------------"

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --project=${PROJECT_ID} \
  --region=${REGION} \
  --format='value(status.url)')

echo "Service URL: $SERVICE_URL"

echo ""
echo "=================================================="
echo "Deployment Summary"
echo "=================================================="
echo ""
echo -e "${GREEN}✓ Fact Checking Layer deployed successfully!${NC}"
echo ""
echo "Service Details:"
echo "  • URL: $SERVICE_URL"
echo "  • Memory: 2Gi"
echo "  • CPU: 2"
echo ""
echo "API Endpoints:"
echo "  • Check Fact: ${SERVICE_URL}/api/fact/check"
echo "  • Get Stats: ${SERVICE_URL}/api/facts/stats"
echo "  • Health: ${SERVICE_URL}/health"
echo ""
echo "Two-Tier Verification:"
echo "  • Tier 1: Internal verified_facts database (free)"
echo "  • Tier 2: Perplexity API (\$0.004/request)"
echo ""
echo "NOTE: PERPLEXITY_API_KEY is empty - set via Cloud Run console or gcloud"
echo ""
