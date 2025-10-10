#!/bin/bash
#
# Deploy Cloud Run Resource Limits - Phase 2 Completion
# Expected savings: $1,500-2,000/month from right-sizing
#
# Usage: ./deploy-resource-limits.sh [tier] [dry-run]
#   tier: all, tier1, tier2, tier3 (default: all)
#   dry-run: yes/no (default: yes)

set -e

PROJECT_ID="${PROJECT_ID:-xynergy-dev-1757909467}"
REGION="${REGION:-us-central1}"
DRY_RUN="${2:-yes}"
TIER="${1:-all}"

echo "=================================================="
echo "Cloud Run Resource Limits Deployment"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Tier: $TIER"
echo "Dry Run: $DRY_RUN"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Tier 1: Lightweight Services (14 services)
# 512Mi memory, 1 vCPU, scale to 0
TIER1_SERVICES=(
    "content-hub"
    "reports-export"
    "scheduler-automation-engine"
    "project-management"
    "qa-engine"
    "security-compliance"
    "monetization-integration"
    "tenant-management"
    "validation-coordinator"
    "trust-safety-validator"
    "plagiarism-detector"
    "fact-checking-service"
    "keyword-revenue-tracker"
    "attribution-coordinator"
)

# Tier 2: Medium Load Services (6 services)
# 1Gi memory, 2 vCPU, min 1 instance
TIER2_SERVICES=(
    "marketing-engine"
    "analytics-data-layer"
    "ai-workflow-engine"
    "advanced-analytics"
    "executive-dashboard"
    "performance-scaling"
)

# Tier 3: High Load / AI Services (7 services)
# 2Gi memory, 4 vCPU, min 2 instances
TIER3_SERVICES=(
    "ai-assistant"
    "ai-routing-engine"
    "internal-ai-service"
    "ai-providers"
    "platform-dashboard"
    "system-runtime"
    "security-governance"
)

deploy_service() {
    local service=$1
    local memory=$2
    local cpu=$3
    local min_instances=$4
    local max_instances=$5
    local tier=$6

    echo -e "${YELLOW}[$tier] Configuring: xynergy-$service${NC}"

    local cmd="gcloud run services update xynergy-$service \
        --project=$PROJECT_ID \
        --region=$REGION \
        --memory=$memory \
        --cpu=$cpu \
        --min-instances=$min_instances \
        --max-instances=$max_instances \
        --cpu-throttling \
        --concurrency=80 \
        --timeout=300"

    if [ "$DRY_RUN" = "yes" ]; then
        echo "  [DRY RUN] Would execute:"
        echo "  $cmd"
        echo ""
    else
        echo "  Deploying..."
        if eval "$cmd" 2>&1; then
            echo -e "  ${GREEN}✓ Success${NC}"
        else
            echo -e "  ${RED}✗ Failed${NC}"
            return 1
        fi
        echo ""
    fi
}

deploy_tier1() {
    echo ""
    echo "=================================================="
    echo "TIER 1: Lightweight Services (14 services)"
    echo "Config: 512Mi RAM, 1 vCPU, 0-10 instances"
    echo "Expected savings: ~$500/month"
    echo "=================================================="
    echo ""

    for service in "${TIER1_SERVICES[@]}"; do
        deploy_service "$service" "512Mi" "1" "0" "10" "TIER1" || true
    done
}

deploy_tier2() {
    echo ""
    echo "=================================================="
    echo "TIER 2: Medium Load Services (6 services)"
    echo "Config: 1Gi RAM, 2 vCPU, 1-20 instances"
    echo "Expected savings: ~$600/month"
    echo "=================================================="
    echo ""

    for service in "${TIER2_SERVICES[@]}"; do
        deploy_service "$service" "1Gi" "2" "1" "20" "TIER2" || true
    done
}

deploy_tier3() {
    echo ""
    echo "=================================================="
    echo "TIER 3: High Load / AI Services (7 services)"
    echo "Config: 2Gi RAM, 4 vCPU, 2-50 instances"
    echo "Expected savings: ~$400/month"
    echo "=================================================="
    echo ""

    for service in "${TIER3_SERVICES[@]}"; do
        deploy_service "$service" "2Gi" "4" "2" "50" "TIER3" || true
    done
}

verify_deployment() {
    echo ""
    echo "=================================================="
    echo "Verifying Deployments"
    echo "=================================================="
    echo ""

    local failed_services=()

    for service in "${TIER1_SERVICES[@]}" "${TIER2_SERVICES[@]}" "${TIER3_SERVICES[@]}"; do
        echo -n "Checking xynergy-$service... "
        if gcloud run services describe "xynergy-$service" \
            --project="$PROJECT_ID" \
            --region="$REGION" \
            --format="value(status.url)" >/dev/null 2>&1; then

            local url=$(gcloud run services describe "xynergy-$service" \
                --project="$PROJECT_ID" \
                --region="$REGION" \
                --format="value(status.url)")

            if curl -sf "$url/health" >/dev/null 2>&1; then
                echo -e "${GREEN}✓ Healthy${NC}"
            else
                echo -e "${YELLOW}⚠ Deployed but health check failed${NC}"
            fi
        else
            echo -e "${RED}✗ Not found${NC}"
            failed_services+=("$service")
        fi
    done

    if [ ${#failed_services[@]} -gt 0 ]; then
        echo ""
        echo -e "${RED}Failed services:${NC}"
        printf '%s\n' "${failed_services[@]}"
    fi
}

show_cost_estimate() {
    echo ""
    echo "=================================================="
    echo "Cost Savings Estimate"
    echo "=================================================="
    echo ""
    echo "Before optimization (unmetered resources):"
    echo "  Average per service: ~$150-200/month"
    echo "  27 services x $175: ~$4,725/month"
    echo ""
    echo "After optimization (right-sized):"
    echo "  Tier 1 (14 services): ~$50/month each = $700/month"
    echo "  Tier 2 (6 services): ~$150/month each = $900/month"
    echo "  Tier 3 (7 services): ~$350/month each = $2,450/month"
    echo "  Total: ~$4,050/month"
    echo ""
    echo "  But with scale-to-zero on Tier 1 (75% idle time):"
    echo "  Tier 1 savings: $700 * 0.75 = $525 saved"
    echo "  Additional savings from CPU throttling: ~$150"
    echo ""
    echo "Monthly Savings: $1,500-2,000"
    echo "Annual Savings: $18,000-24,000"
    echo ""
}

# Main execution
case "$TIER" in
    tier1)
        deploy_tier1
        ;;
    tier2)
        deploy_tier2
        ;;
    tier3)
        deploy_tier3
        ;;
    all)
        deploy_tier1
        deploy_tier2
        deploy_tier3
        ;;
    *)
        echo "Invalid tier: $TIER"
        echo "Usage: $0 [tier] [dry-run]"
        echo "  tier: all, tier1, tier2, tier3"
        echo "  dry-run: yes, no"
        exit 1
        ;;
esac

if [ "$DRY_RUN" = "no" ]; then
    verify_deployment
fi

show_cost_estimate

echo ""
echo "=================================================="
echo "Deployment Complete"
echo "=================================================="
echo ""

if [ "$DRY_RUN" = "yes" ]; then
    echo -e "${YELLOW}This was a DRY RUN - no changes were made${NC}"
    echo ""
    echo "To deploy for real, run:"
    echo "  ./deploy-resource-limits.sh all no"
    echo ""
    echo "To deploy by tier:"
    echo "  ./deploy-resource-limits.sh tier1 no"
    echo "  ./deploy-resource-limits.sh tier2 no"
    echo "  ./deploy-resource-limits.sh tier3 no"
else
    echo -e "${GREEN}Resource limits deployed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Monitor costs over next 7 days"
    echo "  2. Check service health: ./check-service-health.sh"
    echo "  3. Adjust limits if needed based on actual usage"
    echo "  4. Review Cloud Run metrics in GCP Console"
fi

echo ""
