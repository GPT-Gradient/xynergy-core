#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}======================================${NC}"
echo -e "${RED}⚠️  PRODUCTION DEPLOYMENT${NC}"
echo -e "${RED}======================================${NC}"
echo ""
echo -e "${YELLOW}This will deploy to the PRODUCTION environment!${NC}"
echo -e "${YELLOW}This affects real users and real data.${NC}"
echo ""
read -p "Are you absolutely sure you want to deploy to PRODUCTION? (type 'yes' to continue): " confirm

if [ "$confirm" != "yes" ]; then
  echo -e "${RED}Deployment cancelled.${NC}"
  exit 1
fi

# Configuration
PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
SERVICE_NAME="xynergyos-intelligence-gateway-prod"
IMAGE_NAME="us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-services/xynergyos-intelligence-gateway"

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Verify we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo -e "${RED}❌ Error: You must be on the 'main' branch to deploy to production.${NC}"
  echo -e "${RED}Current branch: ${CURRENT_BRANCH}${NC}"
  exit 1
fi

# Verify clean working directory
if [ -n "$(git status --porcelain)" ]; then
  echo -e "${RED}❌ Error: Working directory is not clean. Commit all changes before deploying.${NC}"
  git status --short
  exit 1
fi

# Get git tag or commit
GIT_TAG=$(git describe --exact-match --tags 2>/dev/null || echo "")
if [ -n "$GIT_TAG" ]; then
  VERSION="$GIT_TAG"
  echo -e "${GREEN}📌 Deploying version: ${VERSION}${NC}"
else
  VERSION="commit-$(git rev-parse --short HEAD)"
  echo -e "${YELLOW}⚠️  No git tag found. Deploying commit: ${VERSION}${NC}"
  read -p "Continue without a version tag? (type 'yes' to continue): " confirm_no_tag
  if [ "$confirm_no_tag" != "yes" ]; then
    echo -e "${RED}Deployment cancelled. Create a version tag first:${NC}"
    echo -e "  git tag -a v1.0.0 -m 'Release v1.0.0'"
    echo -e "  git push origin v1.0.0"
    exit 1
  fi
fi

echo ""
echo -e "${YELLOW}📦 Building application...${NC}"
npm run build

echo -e "${YELLOW}🐳 Building Docker image...${NC}"
gcloud builds submit \
  --tag "${IMAGE_NAME}:prod" \
  --tag "${IMAGE_NAME}:${VERSION}" \
  --project "${PROJECT_ID}" \
  --timeout=10m

echo -e "${YELLOW}🚀 Deploying to Cloud Run (PROD)...${NC}"
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE_NAME}:${VERSION}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="NODE_ENV=production,XYNERGY_ENV=prod,MOCK_MODE=false" \
  --set-secrets="JWT_SECRET=jwt-secret-prod:latest,SLACK_CLIENT_SECRET=slack-secret-prod:latest,GMAIL_CLIENT_SECRET=gmail-secret-prod:latest" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 50 \
  --timeout 300 \
  --concurrency 80 \
  --vpc-connector redis-connector \
  --vpc-egress private-ranges-only \
  --no-traffic

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --format="value(status.url)")

LATEST_REVISION=$(gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" \
  --project="${PROJECT_ID}" \
  --format="value(status.latestCreatedRevisionName)")

echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}📍 Environment: PRODUCTION${NC}"
echo -e "${GREEN}🎭 Mock Mode: DISABLED${NC}"
echo -e "${GREEN}📦 Version: ${VERSION}${NC}"
echo -e "${GREEN}🔄 Revision: ${LATEST_REVISION}${NC}"
echo ""
echo -e "${YELLOW}⚠️  New revision deployed with NO TRAFFIC${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Test the canary URL (no traffic):"
echo -e "   curl ${SERVICE_URL}${NC}"
echo ""
echo -e "2. Gradually roll out traffic:"
echo -e "   ${BLUE}# 10% traffic${NC}"
echo -e "   gcloud run services update-traffic ${SERVICE_NAME} --to-revisions=${LATEST_REVISION}=10 --region=${REGION} --project=${PROJECT_ID}"
echo ""
echo -e "   ${BLUE}# 50% traffic${NC}"
echo -e "   gcloud run services update-traffic ${SERVICE_NAME} --to-revisions=${LATEST_REVISION}=50 --region=${REGION} --project=${PROJECT_ID}"
echo ""
echo -e "   ${BLUE}# 100% traffic${NC}"
echo -e "   gcloud run services update-traffic ${SERVICE_NAME} --to-latest --region=${REGION} --project=${PROJECT_ID}"
echo ""
echo -e "3. Or rollback if there are issues:"
echo -e "   gcloud run services update-traffic ${SERVICE_NAME} --to-revisions=PREVIOUS_REVISION=100 --region=${REGION} --project=${PROJECT_ID}"
echo ""
