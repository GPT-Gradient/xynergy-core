#!/bin/bash
set -e

# XynergyOS Traffic Rollout Script
# Gradually roll out traffic to new service revisions

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
TRAFFIC_PERCENTAGE=""
REVISION=""

usage() {
  echo "Usage: $0 -e <environment> -s <service> -t <percentage> [-r <revision>]"
  echo ""
  echo "Required:"
  echo "  -e, --environment ENV    Environment: dev or prod"
  echo "  -s, --service SERVICE    Service name"
  echo "  -t, --traffic PERCENT    Traffic percentage (0-100)"
  echo ""
  echo "Optional:"
  echo "  -r, --revision REV       Specific revision (default: latest)"
  echo "  -h, --help               Show this help"
  echo ""
  echo "Examples:"
  echo "  # Roll out 10% traffic to latest revision"
  echo "  $0 -e prod -s xynergyos-intelligence-gateway -t 10"
  echo ""
  echo "  # Roll out 100% traffic (full cutover)"
  echo "  $0 -e prod -s xynergyos-intelligence-gateway -t 100"
  echo ""
  echo "  # Roll out to specific revision"
  echo "  $0 -e prod -s my-service -t 50 -r my-service-00042-abc"
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
    -t|--traffic)
      TRAFFIC_PERCENTAGE="$2"
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
if [[ -z "$ENVIRONMENT" || -z "$SERVICE" || -z "$TRAFFIC_PERCENTAGE" ]]; then
  echo -e "${RED}Error: Missing required arguments${NC}"
  usage
fi

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
  echo -e "${RED}Error: Environment must be 'dev' or 'prod'${NC}"
  exit 1
fi

if [[ ! "$TRAFFIC_PERCENTAGE" =~ ^[0-9]+$ ]] || [[ "$TRAFFIC_PERCENTAGE" -lt 0 ]] || [[ "$TRAFFIC_PERCENTAGE" -gt 100 ]]; then
  echo -e "${RED}Error: Traffic percentage must be 0-100${NC}"
  exit 1
fi

# Determine service name
if [[ "$ENVIRONMENT" == "prod" && ! "$SERVICE" =~ -prod$ ]]; then
  SERVICE_NAME="${SERVICE}-prod"
else
  SERVICE_NAME="$SERVICE"
fi

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Traffic Rollout${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "Service: ${CYAN}${SERVICE_NAME}${NC}"
echo -e "Environment: ${CYAN}${ENVIRONMENT^^}${NC}"
echo -e "Traffic: ${CYAN}${TRAFFIC_PERCENTAGE}%${NC}"
echo ""

# Get current traffic allocation
echo -e "${YELLOW}Current traffic allocation:${NC}"
gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="table(status.traffic.revisionName,status.traffic.percent)" 2>/dev/null || {
  echo -e "${RED}Error: Service not found: ${SERVICE_NAME}${NC}"
  exit 1
}
echo ""

# Get latest revision if not specified
if [[ -z "$REVISION" ]]; then
  REVISION=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.latestCreatedRevisionName)")
  echo -e "Latest revision: ${CYAN}${REVISION}${NC}"
fi

# Confirmation
if [[ "$TRAFFIC_PERCENTAGE" -eq 100 ]]; then
  echo -e "${YELLOW}⚠️  This will send ALL traffic to revision: ${REVISION}${NC}"
else
  echo -e "${YELLOW}This will send ${TRAFFIC_PERCENTAGE}% traffic to: ${REVISION}${NC}"
fi
echo ""
read -p "Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
  echo -e "${YELLOW}Cancelled.${NC}"
  exit 0
fi

# Update traffic
echo ""
echo -e "${BLUE}Updating traffic allocation...${NC}"

if [[ "$TRAFFIC_PERCENTAGE" -eq 100 ]]; then
  # Send all traffic to latest
  gcloud run services update-traffic "$SERVICE_NAME" \
    --to-latest \
    --region="$REGION" \
    --project="$PROJECT_ID"
else
  # Split traffic
  gcloud run services update-traffic "$SERVICE_NAME" \
    --to-revisions="${REVISION}=${TRAFFIC_PERCENTAGE}" \
    --region="$REGION" \
    --project="$PROJECT_ID"
fi

if [ $? -eq 0 ]; then
  echo ""
  echo -e "${GREEN}✅ Traffic updated successfully${NC}"
  echo ""
  echo -e "${YELLOW}New traffic allocation:${NC}"
  gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="table(status.traffic.revisionName,status.traffic.percent)"
  echo ""
  echo -e "${BLUE}Next steps:${NC}"
  echo "1. Monitor logs:"
  echo "   gcloud run services logs read ${SERVICE_NAME} --region=${REGION} --limit=50"
  echo ""
  echo "2. Check error rates and latency"
  echo ""
  echo "3. Roll out more traffic or rollback:"
  echo "   ${0} -e ${ENVIRONMENT} -s ${SERVICE} -t <new-percentage>"
else
  echo -e "${RED}❌ Failed to update traffic${NC}"
  exit 1
fi
