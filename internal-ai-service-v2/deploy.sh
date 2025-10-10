#!/bin/bash
#
# Deploy Internal AI Service v2
# Can deploy with or without GPU support
#

set -e

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
SERVICE_NAME="internal-ai-service-v2"

# Deployment mode: "cpu" or "gpu"
MODE="${1:-cpu}"

echo "=================================================="
echo "Deploying Internal AI Service v2"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Mode: $MODE"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Building container image${NC}"
echo "------------------------------------------------------"

# Use Artifact Registry instead of GCR
IMAGE_URI="us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-platform/${SERVICE_NAME}:latest"

gcloud builds submit \
  --project=${PROJECT_ID} \
  --tag=${IMAGE_URI} \
  .

echo ""
echo -e "${BLUE}Step 2: Deploying to Cloud Run${NC}"
echo "------------------------------------------------------"

if [ "$MODE" == "gpu" ]; then
  echo "Deploying with GPU support (NVIDIA L4)..."

  gcloud run deploy ${SERVICE_NAME} \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --image=${IMAGE_URI} \
    --platform=managed \
    --memory=16Gi \
    --cpu=4 \
    --gpu=1 \
    --gpu-type=nvidia-l4 \
    --min-instances=0 \
    --max-instances=10 \
    --set-env-vars="PROJECT_ID=${PROJECT_ID},REGION=${REGION},MODEL_NAME=meta-llama/Meta-Llama-3.1-8B-Instruct" \
    --allow-unauthenticated \
    --timeout=300 \
    --concurrency=10

else
  echo "Deploying with CPU only (development mode)..."

  gcloud run deploy ${SERVICE_NAME} \
    --project=${PROJECT_ID} \
    --region=${REGION} \
    --image=${IMAGE_URI} \
    --platform=managed \
    --memory=4Gi \
    --cpu=2 \
    --min-instances=0 \
    --max-instances=10 \
    --set-env-vars="PROJECT_ID=${PROJECT_ID},REGION=${REGION}" \
    --allow-unauthenticated \
    --timeout=300 \
    --concurrency=80
fi

echo ""
echo -e "${BLUE}Step 3: Getting service URL${NC}"
echo "------------------------------------------------------"

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --project=${PROJECT_ID} \
  --region=${REGION} \
  --format='value(status.url)')

echo "Service URL: $SERVICE_URL"

echo ""
echo -e "${BLUE}Step 4: Testing service${NC}"
echo "------------------------------------------------------"

echo -n "Health check... "
HEALTH_STATUS=$(curl -s "${SERVICE_URL}/health" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null || echo "failed")
if [ "$HEALTH_STATUS" == "healthy" ] || [ "$HEALTH_STATUS" == "degraded" ]; then
  echo -e "${GREEN}✓${NC}"
else
  echo -e "${YELLOW}⚠ Service may be starting up${NC}"
fi

echo ""
echo "=================================================="
echo "Deployment Summary"
echo "=================================================="
echo ""
echo -e "${GREEN}✓ Internal AI Service v2 deployed successfully!${NC}"
echo ""
echo "Service Details:"
echo "  • URL: $SERVICE_URL"
echo "  • Mode: $MODE"
if [ "$MODE" == "gpu" ]; then
  echo "  • GPU: NVIDIA L4 (1x)"
  echo "  • Memory: 16Gi"
  echo "  • Cost: ~\$0.70/hour when running (scales to zero)"
  echo "  • Inference: ~\$0.0002 per 1K tokens"
else
  echo "  • CPU: 2 vCPUs"
  echo "  • Memory: 4Gi"
  echo "  • Cost: ~\$0.10/hour when running (scales to zero)"
  echo "  • Note: CPU mode is for development only"
fi

echo ""
echo "API Endpoints:"
echo "  • Generate: ${SERVICE_URL}/api/generate"
echo "  • Stats: ${SERVICE_URL}/api/stats"
echo "  • Health: ${SERVICE_URL}/health"

echo ""
echo "Example usage:"
echo "  curl -X POST \"${SERVICE_URL}/api/generate\" \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"prompt\": \"What is SEO?\", \"max_tokens\": 256}'"

echo ""
echo "Next steps:"
echo "  1. Update AI Routing Engine to route to this service"
echo "  2. Monitor performance and cost in /api/stats"
if [ "$MODE" == "cpu" ]; then
  echo "  3. Redeploy with GPU for production: ./deploy.sh gpu"
fi
echo ""
