#!/bin/bash
#
# Service Health Check - Phase 2 Post-Deployment
# Verifies all optimized services are healthy and responding
#

set -e

PROJECT_ID="${PROJECT_ID:-xynergy-dev-1757909467}"
REGION="${REGION:-us-central1}"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=================================================="
echo "Xynergy Platform - Service Health Check"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Time: $(date)"
echo ""

# Services with resource limits applied
OPTIMIZED_SERVICES=(
    # Tier 1
    "xynergy-content-hub"
    "xynergy-reports-export"
    "xynergy-scheduler-automation-engine"
    "xynergy-project-management"
    "xynergy-qa-engine"

    # Tier 2
    "xynergy-marketing-engine"
    "xynergy-analytics-data-layer"
    "xynergy-executive-dashboard"

    # Tier 3
    "xynergy-ai-assistant"
    "xynergy-ai-routing-engine"
    "xynergy-internal-ai-service"
    "xynergy-platform-dashboard"
    "xynergy-system-runtime"
    "xynergy-security-governance"
)

total_services=${#OPTIMIZED_SERVICES[@]}
healthy_count=0
unhealthy_count=0
unreachable_count=0

echo "=================================================="
echo "Checking ${total_services} Optimized Services"
echo "=================================================="
echo ""

for service in "${OPTIMIZED_SERVICES[@]}"; do
    echo -n "Checking $service... "

    # Get service status from Cloud Run
    status=$(gcloud run services describe "$service" \
        --project="$PROJECT_ID" \
        --region="$REGION" \
        --format="value(status.conditions[0].status)" 2>/dev/null || echo "NOT_FOUND")

    if [ "$status" = "NOT_FOUND" ]; then
        echo -e "${RED}✗ Service not found${NC}"
        ((unhealthy_count++))
        continue
    fi

    if [ "$status" != "True" ]; then
        echo -e "${RED}✗ Unhealthy (status: $status)${NC}"
        ((unhealthy_count++))
        continue
    fi

    # Get service URL
    url=$(gcloud run services describe "$service" \
        --project="$PROJECT_ID" \
        --region="$REGION" \
        --format="value(status.url)" 2>/dev/null)

    if [ -z "$url" ]; then
        echo -e "${RED}✗ No URL found${NC}"
        ((unhealthy_count++))
        continue
    fi

    # Test health endpoint
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url/health" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Healthy${NC} (HTTP $http_code)"
        ((healthy_count++))
    elif [ "$http_code" = "000" ]; then
        echo -e "${YELLOW}⚠ Unreachable${NC} (timeout or connection failed)"
        ((unreachable_count++))
    else
        echo -e "${RED}✗ Unhealthy${NC} (HTTP $http_code)"
        ((unhealthy_count++))
    fi
done

echo ""
echo "=================================================="
echo "Summary"
echo "=================================================="
echo -e "${GREEN}Healthy:${NC}     $healthy_count / $total_services"
echo -e "${YELLOW}Unreachable:${NC} $unreachable_count / $total_services"
echo -e "${RED}Unhealthy:${NC}   $unhealthy_count / $total_services"
echo ""

# Calculate percentage
health_percentage=$((healthy_count * 100 / total_services))

if [ $health_percentage -eq 100 ]; then
    echo -e "${GREEN}✓ All services are healthy!${NC}"
    exit 0
elif [ $health_percentage -ge 90 ]; then
    echo -e "${YELLOW}⚠ Most services are healthy ($health_percentage%)${NC}"
    exit 0
elif [ $health_percentage -ge 75 ]; then
    echo -e "${YELLOW}⚠ Some services need attention ($health_percentage%)${NC}"
    exit 1
else
    echo -e "${RED}✗ Critical: Many services are unhealthy ($health_percentage%)${NC}"
    exit 1
fi
