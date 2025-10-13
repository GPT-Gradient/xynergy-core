#!/bin/bash

# XynergyOS Platform Health Check
# Monitors all platform services and reports status

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m'

# Configuration
PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"

# Parse arguments
ENVIRONMENT="dev"
VERBOSE=false
CHECK_ENDPOINTS=false

usage() {
  echo "Usage: $0 [-e <environment>] [options]"
  echo ""
  echo "Options:"
  echo "  -e, --environment ENV    Environment: dev or prod (default: dev)"
  echo "  -v, --verbose            Show detailed information"
  echo "  -c, --check-endpoints    Check /health endpoints"
  echo "  -h, --help               Show this help"
  echo ""
  echo "Examples:"
  echo "  # Check dev environment"
  echo "  $0"
  echo ""
  echo "  # Check prod with health endpoints"
  echo "  $0 -e prod -c"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case $1 in
    -e|--environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    -c|--check-endpoints)
      CHECK_ENDPOINTS=true
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

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
  echo -e "${RED}Error: Environment must be 'dev' or 'prod'${NC}"
  exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   XynergyOS Platform Health Check     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "Environment: ${CYAN}${ENVIRONMENT^^}${NC}"
echo -e "Project: ${GRAY}${PROJECT_ID}${NC}"
echo -e "Region: ${GRAY}${REGION}${NC}"
echo ""

# Get all services
echo -e "${YELLOW}Fetching services...${NC}"

if [[ "$ENVIRONMENT" == "prod" ]]; then
  SERVICES=$(gcloud run services list \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --format="value(metadata.name)" \
    --filter="metadata.name~-prod$" 2>/dev/null)
else
  SERVICES=$(gcloud run services list \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --format="value(metadata.name)" \
    --filter="NOT metadata.name~-prod$" 2>/dev/null)
fi

if [[ -z "$SERVICES" ]]; then
  echo -e "${RED}No services found${NC}"
  exit 1
fi

SERVICE_COUNT=$(echo "$SERVICES" | wc -l | tr -d ' ')
echo -e "Found ${CYAN}${SERVICE_COUNT}${NC} services"
echo ""

# Service groups
declare -A SERVICE_GROUPS
SERVICE_GROUPS["Core Infrastructure"]="system-runtime security-governance tenant-management secrets-config permission-service"
SERVICE_GROUPS["Intelligence Gateway"]="xynergyos-intelligence-gateway slack-intelligence-service gmail-intelligence-service calendar-intelligence-service crm-engine"
SERVICE_GROUPS["AI Services"]="ai-routing-engine internal-ai-service ai-assistant competency-engine"
SERVICE_GROUPS["Data & Analytics"]="analytics-data-layer analytics-aggregation-service fact-checking-layer audit-logging-service"
SERVICE_GROUPS["Business Operations"]="marketing-engine content-hub project-management qa-engine scheduler-automation-engine aso-engine research-coordinator"
SERVICE_GROUPS["User Services"]="platform-dashboard executive-dashboard conversational-interface oauth-management beta-program business-entity"

# Statistics
TOTAL=0
HEALTHY=0
UNHEALTHY=0
UNKNOWN=0

# Function to check service health
check_service() {
  local service=$1
  local status_symbol=""
  local status_color=""
  local details=""

  # Get service info
  local service_info=$(gcloud run services describe "$service" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="json" 2>/dev/null)

  if [[ -z "$service_info" ]]; then
    status_symbol="❓"
    status_color="$GRAY"
    details="Not found"
    ((UNKNOWN++))
    return
  fi

  # Extract info
  local ready=$(echo "$service_info" | jq -r '.status.conditions[] | select(.type=="Ready") | .status')
  local url=$(echo "$service_info" | jq -r '.status.url // "N/A"')
  local latest_revision=$(echo "$service_info" | jq -r '.status.latestReadyRevisionName')
  local traffic=$(echo "$service_info" | jq -r '.status.traffic[] | select(.latestRevision==true) | .percent // 0')

  # Determine health status
  if [[ "$ready" == "True" ]]; then
    status_symbol="✅"
    status_color="$GREEN"
    details="Ready"
    ((HEALTHY++))

    # Check endpoint if requested
    if [[ "$CHECK_ENDPOINTS" == true && "$url" != "N/A" ]]; then
      local health_url="${url}/health"
      local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$health_url" --max-time 5 2>/dev/null || echo "000")
      if [[ "$http_code" == "200" ]]; then
        details="Ready • /health OK"
      else
        details="Ready • /health ${http_code}"
      fi
    fi
  elif [[ "$ready" == "False" ]]; then
    status_symbol="❌"
    status_color="$RED"
    details="Not ready"
    ((UNHEALTHY++))
  else
    status_symbol="⚠️"
    status_color="$YELLOW"
    details="Unknown status"
    ((UNKNOWN++))
  fi

  # Print service status
  printf "${status_color}${status_symbol}${NC} %-45s ${GRAY}%s${NC}\n" "$service" "$details"

  # Verbose details
  if [[ "$VERBOSE" == true ]]; then
    echo -e "${GRAY}   URL: $url${NC}"
    echo -e "${GRAY}   Latest Revision: $latest_revision${NC}"
    echo -e "${GRAY}   Traffic: ${traffic}%${NC}"
    echo ""
  fi

  ((TOTAL++))
}

# Check services by group
for group in "${!SERVICE_GROUPS[@]}"; do
  local group_services="${SERVICE_GROUPS[$group]}"
  local found_any=false

  # Check if any services in this group are deployed
  for base_service in $group_services; do
    local service_name="$base_service"
    if [[ "$ENVIRONMENT" == "prod" ]]; then
      # Try with -prod suffix for services that don't already have it
      if [[ ! "$base_service" =~ -prod$ ]]; then
        service_name="${base_service}-prod"
      fi
    fi

    if echo "$SERVICES" | grep -q "^${service_name}$\|${base_service}"; then
      if [[ "$found_any" == false ]]; then
        echo -e "${CYAN}━━━ ${group} ━━━${NC}"
        found_any=true
      fi

      # Find exact service name
      local exact_service=$(echo "$SERVICES" | grep "^${service_name}$\|${base_service}" | head -1)
      check_service "$exact_service"
    fi
  done

  if [[ "$found_any" == true ]]; then
    echo ""
  fi
done

# Check for ungrouped services
echo -e "${CYAN}━━━ Other Services ━━━${NC}"
for service in $SERVICES; do
  # Check if service is already in a group
  local is_grouped=false
  for group_services in "${SERVICE_GROUPS[@]}"; do
    for base_service in $group_services; do
      if [[ "$service" == *"$base_service"* ]]; then
        is_grouped=true
        break 2
      fi
    done
  done

  if [[ "$is_grouped" == false ]]; then
    check_service "$service"
  fi
done

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Health Check Summary           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
printf "Total Services:    ${CYAN}%3d${NC}\n" $TOTAL
printf "Healthy:           ${GREEN}%3d${NC}\n" $HEALTHY
printf "Unhealthy:         ${RED}%3d${NC}\n" $UNHEALTHY
printf "Unknown:           ${GRAY}%3d${NC}\n" $UNKNOWN
echo ""

# Health percentage
if [[ $TOTAL -gt 0 ]]; then
  HEALTH_PERCENT=$((HEALTHY * 100 / TOTAL))
  if [[ $HEALTH_PERCENT -ge 90 ]]; then
    echo -e "Platform Health: ${GREEN}${HEALTH_PERCENT}%${NC} ✅"
  elif [[ $HEALTH_PERCENT -ge 70 ]]; then
    echo -e "Platform Health: ${YELLOW}${HEALTH_PERCENT}%${NC} ⚠️"
  else
    echo -e "Platform Health: ${RED}${HEALTH_PERCENT}%${NC} ❌"
  fi
else
  echo -e "Platform Health: ${GRAY}N/A${NC}"
fi

echo ""

# Exit code based on health
if [[ $UNHEALTHY -gt 0 ]]; then
  exit 1
else
  exit 0
fi
