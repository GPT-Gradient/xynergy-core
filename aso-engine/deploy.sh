#!/bin/bash
#
# Deploy ASO Engine
#

set -e

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
SERVICE_NAME="aso-engine"
IMAGE_URI="us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-platform/${SERVICE_NAME}:latest"

echo "=================================================="
echo "Deploying ASO Engine"
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
  --set-env-vars="PROJECT_ID=${PROJECT_ID},REGION=${REGION}" \
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
echo -e "${GREEN}✓ ASO Engine deployed successfully!${NC}"
echo ""
echo "Service Details:"
echo "  • URL: $SERVICE_URL"
echo "  • Memory: 2Gi"
echo "  • CPU: 2"
echo ""
echo "API Endpoints:"
echo "  • Create Content: ${SERVICE_URL}/api/content"
echo "  • List Content: ${SERVICE_URL}/api/content?tenant_id=demo"
echo "  • Add Keyword: ${SERVICE_URL}/api/keywords"
echo "  • List Keywords: ${SERVICE_URL}/api/keywords?tenant_id=demo"
echo "  • Detect Opportunities: ${SERVICE_URL}/api/opportunities/detect"
echo "  • Stats: ${SERVICE_URL}/api/stats?tenant_id=demo"
echo "  • Health: ${SERVICE_URL}/health"
echo ""
