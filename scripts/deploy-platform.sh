#!/bin/bash
set -e

# XynergyOS Platform-Wide Deployment Orchestration
# Deploys all platform services to dev or prod environments

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MANIFEST_FILE="${PROJECT_ROOT}/platform-services.yaml"
PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"

# Parse command line arguments
ENVIRONMENT=""
SERVICE_GROUP=""
SPECIFIC_SERVICE=""
DRY_RUN=false
PARALLEL=false
SKIP_BUILD=false

usage() {
  echo "Usage: $0 -e <environment> [-g <group>] [-s <service>] [options]"
  echo ""
  echo "Required:"
  echo "  -e, --environment ENV    Target environment: dev or prod"
  echo ""
  echo "Optional:"
  echo "  -g, --group GROUP        Deploy specific service group"
  echo "  -s, --service SERVICE    Deploy specific service"
  echo "  -d, --dry-run            Show what would be deployed without deploying"
  echo "  -p, --parallel           Deploy services in parallel (experimental)"
  echo "  --skip-build             Skip Docker image building"
  echo "  -h, --help               Show this help message"
  echo ""
  echo "Service Groups:"
  echo "  core_infrastructure      - Core platform services"
  echo "  intelligence_gateway     - Communication services"
  echo "  ai_services              - AI and ML services"
  echo "  data_analytics           - Analytics and data processing"
  echo "  business_operations      - Business and operational services"
  echo "  user_services            - User-facing services"
  echo ""
  echo "Examples:"
  echo "  # Deploy all services to dev"
  echo "  $0 -e dev"
  echo ""
  echo "  # Deploy intelligence gateway group to prod"
  echo "  $0 -e prod -g intelligence_gateway"
  echo ""
  echo "  # Deploy specific service to dev"
  echo "  $0 -e dev -s xynergyos-intelligence-gateway"
  echo ""
  echo "  # Dry run for prod deployment"
  echo "  $0 -e prod --dry-run"
  exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -e|--environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    -g|--group)
      SERVICE_GROUP="$2"
      shift 2
      ;;
    -s|--service)
      SPECIFIC_SERVICE="$2"
      shift 2
      ;;
    -d|--dry-run)
      DRY_RUN=true
      shift
      ;;
    -p|--parallel)
      PARALLEL=true
      shift
      ;;
    --skip-build)
      SKIP_BUILD=true
      shift
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

# Validate environment
if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
  echo -e "${RED}Error: Environment must be 'dev' or 'prod'${NC}"
  usage
fi

# Production safety check
if [[ "$ENVIRONMENT" == "prod" && "$DRY_RUN" == false ]]; then
  echo -e "${RED}======================================${NC}"
  echo -e "${RED}⚠️  PRODUCTION DEPLOYMENT${NC}"
  echo -e "${RED}======================================${NC}"
  echo ""
  echo -e "${YELLOW}This will deploy services to PRODUCTION!${NC}"
  echo ""
  if [[ -n "$SPECIFIC_SERVICE" ]]; then
    echo -e "Service: ${CYAN}${SPECIFIC_SERVICE}${NC}"
  elif [[ -n "$SERVICE_GROUP" ]]; then
    echo -e "Service Group: ${CYAN}${SERVICE_GROUP}${NC}"
  else
    echo -e "Deploying: ${CYAN}ALL PLATFORM SERVICES${NC}"
  fi
  echo ""
  read -p "Are you absolutely sure? (type 'yes' to continue): " confirm
  if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Deployment cancelled.${NC}"
    exit 1
  fi
fi

# Display deployment info
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}XynergyOS Platform Deployment${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "Environment: ${CYAN}${ENVIRONMENT^^}${NC}"
echo -e "Project: ${CYAN}${PROJECT_ID}${NC}"
echo -e "Region: ${CYAN}${REGION}${NC}"
if [[ -n "$SERVICE_GROUP" ]]; then
  echo -e "Service Group: ${CYAN}${SERVICE_GROUP}${NC}"
fi
if [[ -n "$SPECIFIC_SERVICE" ]]; then
  echo -e "Specific Service: ${CYAN}${SPECIFIC_SERVICE}${NC}"
fi
if [[ "$DRY_RUN" == true ]]; then
  echo -e "Mode: ${YELLOW}DRY RUN${NC}"
fi
if [[ "$PARALLEL" == true ]]; then
  echo -e "Parallel: ${YELLOW}ENABLED${NC}"
fi
echo ""

# Function to get services for a group
get_services_for_group() {
  local group=$1
  case $group in
    core_infrastructure)
      echo "system-runtime security-governance tenant-management secrets-config permission-service"
      ;;
    intelligence_gateway)
      echo "xynergyos-intelligence-gateway slack-intelligence-service gmail-intelligence-service calendar-intelligence-service crm-engine"
      ;;
    ai_services)
      echo "ai-routing-engine internal-ai-service-v2 ai-assistant xynergy-competency-engine"
      ;;
    data_analytics)
      echo "analytics-data-layer analytics-aggregation-service fact-checking-layer audit-logging-service"
      ;;
    business_operations)
      echo "marketing-engine content-hub project-management qa-engine scheduler-automation-engine aso-engine research-coordinator"
      ;;
    user_services)
      echo "platform-dashboard executive-dashboard conversational-interface-service oauth-management-service beta-program-service business-entity-service"
      ;;
    *)
      echo ""
      ;;
  esac
}

# Function to get all services in priority order
get_all_services() {
  echo "$(get_services_for_group core_infrastructure) $(get_services_for_group intelligence_gateway) $(get_services_for_group ai_services) $(get_services_for_group data_analytics) $(get_services_for_group business_operations) $(get_services_for_group user_services)"
}

# Function to deploy a single service
deploy_service() {
  local service=$1
  local service_path="${PROJECT_ROOT}/${service}"

  # Check if service directory exists
  if [ ! -d "$service_path" ]; then
    echo -e "${YELLOW}⚠️  Service directory not found: ${service}${NC}"
    return 1
  fi

  # Check if Dockerfile exists
  if [ ! -f "${service_path}/Dockerfile" ]; then
    echo -e "${YELLOW}⚠️  No Dockerfile found for: ${service}${NC}"
    return 1
  fi

  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${CYAN}📦 Deploying: ${service}${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

  if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}[DRY RUN] Would deploy ${service} to ${ENVIRONMENT}${NC}"
    return 0
  fi

  # Determine service name based on environment
  local service_name
  if [[ "$ENVIRONMENT" == "prod" ]]; then
    # Check if service follows xynergy-* naming convention
    if [[ "$service" == xynergy-* ]]; then
      service_name="${service}-prod"
    elif [[ "$service" == *-service ]]; then
      service_name="${service}-prod"
    else
      service_name="${service}-prod"
    fi
  else
    service_name="$service"
  fi

  # Build Docker image
  local image_name="us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-services/${service}:${ENVIRONMENT}"

  if [[ "$SKIP_BUILD" == false ]]; then
    echo -e "${YELLOW}🏗️  Building Docker image...${NC}"
    cd "$service_path"

    # Check for package.json (TypeScript service)
    if [ -f "package.json" ]; then
      echo "Installing dependencies..."
      npm ci > /dev/null 2>&1 || npm install > /dev/null 2>&1
      if [ -f "tsconfig.json" ]; then
        echo "Building TypeScript..."
        npm run build > /dev/null 2>&1
      fi
    fi

    # Build and push image
    gcloud builds submit \
      --tag "$image_name" \
      --project "$PROJECT_ID" \
      --timeout=10m \
      --quiet 2>&1 | grep -E "(SUCCESS|FAILURE|ERROR)" || echo "Building..."

    if [ ${PIPESTATUS[0]} -ne 0 ]; then
      echo -e "${RED}❌ Failed to build ${service}${NC}"
      return 1
    fi

    cd "$PROJECT_ROOT"
  else
    echo -e "${YELLOW}⏭️  Skipping build (using existing image)${NC}"
  fi

  # Deploy to Cloud Run
  echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"

  # Build deployment command
  local deploy_cmd="gcloud run deploy ${service_name} \
    --image=${image_name} \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --platform=managed \
    --allow-unauthenticated"

  # Add environment-specific configuration
  if [[ "$ENVIRONMENT" == "prod" ]]; then
    deploy_cmd+=" --set-env-vars=NODE_ENV=production,XYNERGY_ENV=prod,MOCK_MODE=false"
    deploy_cmd+=" --no-traffic"  # Safety: Deploy without traffic
  else
    deploy_cmd+=" --set-env-vars=NODE_ENV=production,XYNERGY_ENV=dev,MOCK_MODE=true"
  fi

  # Execute deployment
  eval "$deploy_cmd --quiet" 2>&1 | grep -E "(Service|Deploying|URL)" || echo "Deploying..."

  if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully deployed ${service}${NC}"
    return 0
  else
    echo -e "${RED}❌ Failed to deploy ${service}${NC}"
    return 1
  fi
}

# Determine which services to deploy
SERVICES_TO_DEPLOY=""
if [[ -n "$SPECIFIC_SERVICE" ]]; then
  SERVICES_TO_DEPLOY="$SPECIFIC_SERVICE"
elif [[ -n "$SERVICE_GROUP" ]]; then
  SERVICES_TO_DEPLOY=$(get_services_for_group "$SERVICE_GROUP")
  if [[ -z "$SERVICES_TO_DEPLOY" ]]; then
    echo -e "${RED}Error: Invalid service group: ${SERVICE_GROUP}${NC}"
    exit 1
  fi
else
  SERVICES_TO_DEPLOY=$(get_all_services)
fi

# Count services
SERVICE_COUNT=$(echo "$SERVICES_TO_DEPLOY" | wc -w | tr -d ' ')
echo -e "${CYAN}Services to deploy: ${SERVICE_COUNT}${NC}"
echo ""

# Confirmation for large deployments
if [[ $SERVICE_COUNT -gt 10 && "$DRY_RUN" == false ]]; then
  read -p "Deploy $SERVICE_COUNT services? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
  fi
fi

# Deploy services
echo -e "${BLUE}Starting deployment...${NC}"
echo ""

SUCCESSFUL=0
FAILED=0
SKIPPED=0

START_TIME=$(date +%s)

if [[ "$PARALLEL" == true ]]; then
  echo -e "${YELLOW}⚠️  Parallel deployment is experimental${NC}"
  for service in $SERVICES_TO_DEPLOY; do
    deploy_service "$service" &
  done
  wait
else
  for service in $SERVICES_TO_DEPLOY; do
    if deploy_service "$service"; then
      ((SUCCESSFUL++))
    else
      ((FAILED++))
    fi
    echo ""
  done
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Summary
echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Deployment Summary${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "Environment: ${CYAN}${ENVIRONMENT^^}${NC}"
echo -e "Total Services: ${CYAN}${SERVICE_COUNT}${NC}"
echo -e "Successful: ${GREEN}${SUCCESSFUL}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo -e "Duration: ${CYAN}${DURATION}s${NC}"
echo ""

if [[ "$ENVIRONMENT" == "prod" && "$DRY_RUN" == false ]]; then
  echo -e "${YELLOW}⚠️  Production services deployed with NO TRAFFIC${NC}"
  echo ""
  echo -e "${BLUE}Next steps:${NC}"
  echo "1. Test each service using its direct URL"
  echo "2. Gradually roll out traffic:"
  echo "   ./scripts/rollout-traffic.sh -e prod -s <service-name> -t <percentage>"
  echo "3. Monitor logs and metrics"
  echo "4. Rollback if needed:"
  echo "   ./scripts/rollback-service.sh -e prod -s <service-name>"
  echo ""
fi

if [[ $FAILED -gt 0 ]]; then
  echo -e "${RED}Some deployments failed. Check logs above for details.${NC}"
  exit 1
else
  echo -e "${GREEN}✅ All deployments successful!${NC}"
  exit 0
fi
