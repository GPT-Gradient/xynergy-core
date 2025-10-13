#!/bin/bash
set -e

# XynergyOS Service Rollback Script
# Quickly rollback to previous revision

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"

# Parse arguments
ENVIRONMENT=""
SERVICE=""
REVISION=""

usage() {
  echo "Usage: $0 -e <environment> -s <service> [-r <revision>]"
  echo ""
  echo "Required:"
  echo "  -e, --environment ENV    Environment: dev or prod"
  echo "  -s, --service SERVICE    Service name"
  echo ""
  echo "Optional:"
  echo "  -r, --revision REV       Specific revision to rollback to"
  echo "                          (if not specified, will show menu)"
  echo "  -h, --help               Show this help"
  echo ""
  echo "Examples:"
  echo "  # Interactive rollback (shows menu)"
  echo "  $0 -e prod -s xynergyos-intelligence-gateway"
  echo ""
  echo "  # Rollback to specific revision"
  echo "  $0 -e prod -s my-service -r my-service-00042-abc"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case $1 in
    -e|--environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    -s|--service)
      SERVICE="$2"
      shift 2
      ;;
    -r|--revision)
      REVISION="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      usage
      ;;
  esac
done

# Validate inputs
if [[ -z "$ENVIRONMENT" || -z "$SERVICE" ]]; then
  echo -e "${RED}Error: Missing required arguments${NC}"
  usage
fi

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
  echo -e "${RED}Error: Environment must be 'dev' or 'prod'${NC}"
  exit 1
fi

# Determine service name
if [[ "$ENVIRONMENT" == "prod" && ! "$SERVICE" =~ -prod$ ]]; then
  SERVICE_NAME="${SERVICE}-prod"
else
  SERVICE_NAME="$SERVICE"
fi

echo -e "${RED}======================================${NC}"
echo -e "${RED}⚠️  SERVICE ROLLBACK${NC}"
echo -e "${RED}======================================${NC}"
echo -e "Service: ${CYAN}${SERVICE_NAME}${NC}"
echo -e "Environment: ${CYAN}${ENVIRONMENT^^}${NC}"
echo ""

# Get current revisions
echo -e "${YELLOW}Fetching service revisions...${NC}"
REVISIONS=$(gcloud run revisions list \
  --service="$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="table(metadata.name,status.conditions[0].lastTransitionTime,spec.containers[0].image)" 2>/dev/null)

if [ $? -ne 0 ]; then
  echo -e "${RED}Error: Service not found: ${SERVICE_NAME}${NC}"
  exit 1
fi

echo ""
echo -e "${CYAN}Available revisions:${NC}"
echo "$REVISIONS"
echo ""

# Get current traffic allocation
echo -e "${YELLOW}Current traffic allocation:${NC}"
CURRENT_TRAFFIC=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="table(status.traffic.revisionName,status.traffic.percent)")
echo "$CURRENT_TRAFFIC"
echo ""

# If revision not specified, prompt for selection
if [[ -z "$REVISION" ]]; then
  # Get list of revision names
  REVISION_LIST=$(gcloud run revisions list \
    --service="$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(metadata.name)" | head -10)

  echo -e "${YELLOW}Select a revision to rollback to:${NC}"
  select REVISION in $REVISION_LIST "Cancel"; do
    if [[ "$REVISION" == "Cancel" ]]; then
      echo -e "${YELLOW}Rollback cancelled.${NC}"
      exit 0
    elif [[ -n "$REVISION" ]]; then
      break
    else
      echo -e "${RED}Invalid selection${NC}"
    fi
  done
fi

# Get revision details
REVISION_IMAGE=$(gcloud run revisions describe "$REVISION" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(spec.containers[0].image)" 2>/dev/null)

if [ $? -ne 0 ]; then
  echo -e "${RED}Error: Revision not found: ${REVISION}${NC}"
  exit 1
fi

REVISION_DATE=$(gcloud run revisions describe "$REVISION" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(metadata.creationTimestamp)")

echo ""
echo -e "${YELLOW}Rolling back to:${NC}"
echo -e "  Revision: ${CYAN}${REVISION}${NC}"
echo -e "  Image: ${CYAN}${REVISION_IMAGE}${NC}"
echo -e "  Created: ${CYAN}${REVISION_DATE}${NC}"
echo ""

# Final confirmation
echo -e "${RED}⚠️  This will route 100% of traffic to the selected revision${NC}"
echo ""
read -p "Continue with rollback? (type 'yes' to confirm): " confirm
if [ "$confirm" != "yes" ]; then
  echo -e "${YELLOW}Rollback cancelled.${NC}"
  exit 0
fi

# Perform rollback
echo ""
echo -e "${BLUE}Performing rollback...${NC}"

gcloud run services update-traffic "$SERVICE_NAME" \
  --to-revisions="${REVISION}=100" \
  --region="$REGION" \
  --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
  echo ""
  echo -e "${GREEN}✅ Rollback successful${NC}"
  echo ""
  echo -e "${YELLOW}New traffic allocation:${NC}"
  gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="table(status.traffic.revisionName,status.traffic.percent)"
  echo ""
  echo -e "${BLUE}Next steps:${NC}"
  echo "1. Monitor the service for issues"
  echo "2. Check logs:"
  echo "   gcloud run services logs read ${SERVICE_NAME} --region=${REGION} --limit=50"
  echo "3. Investigate what caused the need for rollback"
  echo "4. Fix the issue before next deployment"
else
  echo ""
  echo -e "${RED}❌ Rollback failed${NC}"
  echo "Check the error message above and try again"
  exit 1
fi
