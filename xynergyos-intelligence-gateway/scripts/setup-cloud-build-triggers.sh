#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Cloud Build Triggers Setup${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

PROJECT_ID="xynergy-dev-1757909467"
REPO_OWNER="GPT-Gradient"
REPO_NAME="xynergy-core"

echo -e "${YELLOW}This script will set up Cloud Build triggers for automated deployments.${NC}"
echo ""
echo -e "${YELLOW}Prerequisites:${NC}"
echo "1. GitHub repository must be connected to Cloud Build"
echo "2. You must have completed GitHub OAuth authorization"
echo ""
echo -e "${BLUE}If you haven't connected GitHub yet:${NC}"
echo "Visit: https://console.cloud.google.com/cloud-build/triggers?project=${PROJECT_ID}"
echo "Click 'Connect Repository' and follow the GitHub authorization flow"
echo ""
read -p "Have you connected the GitHub repository? (yes/no): " github_connected

if [ "$github_connected" != "yes" ]; then
  echo -e "${RED}Please connect the GitHub repository first.${NC}"
  echo "Visit: https://console.cloud.google.com/cloud-build/triggers?project=${PROJECT_ID}"
  exit 1
fi

echo ""
echo -e "${YELLOW}Checking for existing triggers...${NC}"
EXISTING_TRIGGERS=$(gcloud builds triggers list --project="${PROJECT_ID}" --format="value(name)" 2>/dev/null || echo "")

if echo "$EXISTING_TRIGGERS" | grep -q "gateway-dev-deploy"; then
  echo -e "${YELLOW}⚠️  DEV trigger 'gateway-dev-deploy' already exists${NC}"
  read -p "Do you want to recreate it? (yes/no): " recreate_dev
  if [ "$recreate_dev" == "yes" ]; then
    echo "Deleting existing DEV trigger..."
    gcloud builds triggers delete gateway-dev-deploy --project="${PROJECT_ID}" --quiet
  fi
fi

if echo "$EXISTING_TRIGGERS" | grep -q "gateway-prod-deploy"; then
  echo -e "${YELLOW}⚠️  PROD trigger 'gateway-prod-deploy' already exists${NC}"
  read -p "Do you want to recreate it? (yes/no): " recreate_prod
  if [ "$recreate_prod" == "yes" ]; then
    echo "Deleting existing PROD trigger..."
    gcloud builds triggers delete gateway-prod-deploy --project="${PROJECT_ID}" --quiet
  fi
fi

echo ""
echo -e "${YELLOW}Creating DEV trigger (auto-deploy on push to main)...${NC}"

# Create DEV trigger
if ! echo "$EXISTING_TRIGGERS" | grep -q "gateway-dev-deploy" || [ "$recreate_dev" == "yes" ]; then
  gcloud builds triggers create github \
    --name="gateway-dev-deploy" \
    --description="Auto-deploy Intelligence Gateway to DEV on push to main" \
    --repo-name="${REPO_NAME}" \
    --repo-owner="${REPO_OWNER}" \
    --branch-pattern="^main$" \
    --build-config="xynergyos-intelligence-gateway/cloudbuild-dev.yaml" \
    --included-files="xynergyos-intelligence-gateway/**" \
    --project="${PROJECT_ID}"

  echo -e "${GREEN}✅ DEV trigger created successfully${NC}"
else
  echo -e "${BLUE}ℹ️  DEV trigger already exists, skipping${NC}"
fi

echo ""
echo -e "${YELLOW}Creating PROD trigger (deploy on version tags)...${NC}"

# Create PROD trigger
if ! echo "$EXISTING_TRIGGERS" | grep -q "gateway-prod-deploy" || [ "$recreate_prod" == "yes" ]; then
  gcloud builds triggers create github \
    --name="gateway-prod-deploy" \
    --description="Deploy Intelligence Gateway to PROD on version tags" \
    --repo-name="${REPO_NAME}" \
    --repo-owner="${REPO_OWNER}" \
    --tag-pattern="^v[0-9]+\\.[0-9]+\\.[0-9]+$" \
    --build-config="xynergyos-intelligence-gateway/cloudbuild-prod.yaml" \
    --included-files="xynergyos-intelligence-gateway/**" \
    --project="${PROJECT_ID}"

  echo -e "${GREEN}✅ PROD trigger created successfully${NC}"
else
  echo -e "${BLUE}ℹ️  PROD trigger already exists, skipping${NC}"
fi

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}✅ Triggers Setup Complete${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

echo -e "${BLUE}Listing all triggers:${NC}"
gcloud builds triggers list --project="${PROJECT_ID}" --format="table(name,triggerTemplate.branchName,triggerTemplate.tagName,filename)"

echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo -e "${YELLOW}Test DEV Trigger:${NC}"
echo "1. Make a change to the gateway code"
echo "2. Push to main branch:"
echo "   git add ."
echo "   git commit -m 'feat: test auto-deploy'"
echo "   git push origin main"
echo "3. Monitor build:"
echo "   https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}"
echo ""
echo -e "${YELLOW}Test PROD Trigger:${NC}"
echo "1. Create a version tag:"
echo "   git tag -a v1.0.0 -m 'Release v1.0.0'"
echo "   git push origin v1.0.0"
echo "2. Monitor build:"
echo "   https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}"
echo "3. Gradually roll out traffic (see deploy-prod.sh output)"
echo ""
echo -e "${GREEN}For detailed documentation, see:${NC}"
echo "  xynergyos-intelligence-gateway/docs/CLOUD_BUILD_TRIGGERS_SETUP.md"
echo ""
