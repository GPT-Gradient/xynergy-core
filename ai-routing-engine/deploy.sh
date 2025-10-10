#!/bin/bash
#
# Deploy AI Routing Engine with updated Internal AI Service v2 URL
#

set -e

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
SERVICE_NAME="ai-routing-engine"
IMAGE_URI="us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-platform/${SERVICE_NAME}:latest"

echo "=================================================="
echo "Deploying AI Routing Engine v2"
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
  --max-instances=20 \
  --set-env-vars="PROJECT_ID=${PROJECT_ID},REGION=${REGION},INTERNAL_AI_URL=https://internal-ai-service-v2-vgjxy554mq-uc.a.run.app" \
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
echo -e "${GREEN}✓ AI Routing Engine deployed successfully!${NC}"
echo ""
echo "Service Details:"
echo "  • URL: $SERVICE_URL"
echo "  • Memory: 2Gi"
echo "  • CPU: 2"
echo "  • Internal AI Service: https://internal-ai-service-v2-vgjxy554mq-uc.a.run.app"
echo ""
echo "API Endpoints:"
echo "  • Generate: ${SERVICE_URL}/api/generate"
echo "  • Route: ${SERVICE_URL}/api/route"
echo "  • Cache Stats: ${SERVICE_URL}/cache/stats"
echo "  • Health: ${SERVICE_URL}/health"
echo ""
