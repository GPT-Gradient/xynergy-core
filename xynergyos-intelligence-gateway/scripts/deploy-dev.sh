#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Deploying to DEVELOPMENT environment${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Configuration
PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
SERVICE_NAME="xynergyos-intelligence-gateway"
IMAGE_NAME="us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-services/${SERVICE_NAME}"

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo -e "${YELLOW}📦 Building application...${NC}"
npm run build

echo -e "${YELLOW}🐳 Building Docker image...${NC}"
gcloud builds submit \
  --tag "${IMAGE_NAME}:dev" \
  --tag "${IMAGE_NAME}:dev-$(git rev-parse --short HEAD)" \
  --project "${PROJECT_ID}" \
  --timeout=10m

echo -e "${YELLOW}🚀 Deploying to Cloud Run (DEV)...${NC}"
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_NAME}:dev" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="NODE_ENV=production,XYNERGY_ENV=dev,MOCK_MODE=true" \
  --set-secrets="JWT_SECRET=jwt-secret-dev:latest" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --concurrency 80 \
  --vpc-connector redis-connector \
  --vpc-egress private-ranges-only

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --format="value(status.url)")

echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}📍 Environment: DEV${NC}"
echo -e "${GREEN}🎭 Mock Mode: ENABLED${NC}"
echo ""
echo -e "${BLUE}Test the deployment:${NC}"
echo -e "curl ${SERVICE_URL}/health"
echo ""
