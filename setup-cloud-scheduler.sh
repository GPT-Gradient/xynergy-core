#!/bin/bash
#
# Setup Cloud Scheduler Jobs for ASO Platform
# Automates periodic data collection and processing
#

set -e

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"

echo "=================================================="
echo "Setting Up Cloud Scheduler for ASO Platform"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get service URLs
ASO_ENGINE_URL=$(gcloud run services describe aso-engine \
  --project=${PROJECT_ID} \
  --region=${REGION} \
  --format='value(status.url)')

FACT_CHECKING_URL=$(gcloud run services describe fact-checking-layer \
  --project=${PROJECT_ID} \
  --region=${REGION} \
  --format='value(status.url)')

echo "Service URLs:"
echo "  ASO Engine: $ASO_ENGINE_URL"
echo "  Fact Checking: $FACT_CHECKING_URL"
echo ""

# Create service account for Cloud Scheduler if it doesn't exist
echo -e "${BLUE}Step 1: Setting up service account${NC}"
echo "------------------------------------------------------"

SA_NAME="cloud-scheduler-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if service account exists
if gcloud iam service-accounts describe ${SA_EMAIL} --project=${PROJECT_ID} >/dev/null 2>&1; then
  echo "Service account ${SA_EMAIL} already exists"
else
  echo "Creating service account ${SA_EMAIL}"
  gcloud iam service-accounts create ${SA_NAME} \
    --project=${PROJECT_ID} \
    --display-name="Cloud Scheduler Service Account"
fi

# Grant necessary permissions
echo "Granting Cloud Run Invoker role..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.invoker" \
  --condition=None

echo ""
echo -e "${BLUE}Step 2: Creating Cloud Scheduler jobs${NC}"
echo "------------------------------------------------------"

# Job 1: Hourly keyword ranking checks (for top priority keywords)
echo "Creating hourly keyword ranking job..."
gcloud scheduler jobs create http keyword-ranking-hourly \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 * * * *" \
  --uri="${ASO_ENGINE_URL}/api/internal/collect-rankings" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"priority":"tier1","frequency":"hourly"}' \
  --oidc-service-account-email=${SA_EMAIL} \
  --oidc-token-audience=${ASO_ENGINE_URL} \
  --time-zone="America/New_York" \
  --description="Hourly ranking checks for tier-1 keywords" \
  --attempt-deadline=300s \
  --max-retry-attempts=3 || echo "Job already exists, updating..."

# If job exists, update it
gcloud scheduler jobs update http keyword-ranking-hourly \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 * * * *" \
  --uri="${ASO_ENGINE_URL}/api/internal/collect-rankings" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"priority":"tier1","frequency":"hourly"}' \
  --time-zone="America/New_York" \
  --attempt-deadline=300s \
  --max-retry-attempts=3 >/dev/null 2>&1 || true

echo -e "${GREEN}✓ Hourly keyword ranking job configured${NC}"

# Job 2: Daily SERP data collection (all monitored keywords)
echo "Creating daily SERP collection job..."
gcloud scheduler jobs create http serp-collection-daily \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 6 * * *" \
  --uri="${ASO_ENGINE_URL}/api/internal/collect-serp" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"scope":"all_keywords","include_features":true}' \
  --oidc-service-account-email=${SA_EMAIL} \
  --oidc-token-audience=${ASO_ENGINE_URL} \
  --time-zone="America/New_York" \
  --description="Daily SERP data collection for all keywords" \
  --attempt-deadline=600s \
  --max-retry-attempts=2 || echo "Job already exists, updating..."

gcloud scheduler jobs update http serp-collection-daily \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 6 * * *" \
  --uri="${ASO_ENGINE_URL}/api/internal/collect-serp" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"scope":"all_keywords","include_features":true}' \
  --time-zone="America/New_York" \
  --attempt-deadline=600s \
  --max-retry-attempts=2 >/dev/null 2>&1 || true

echo -e "${GREEN}✓ Daily SERP collection job configured${NC}"

# Job 3: Daily opportunity detection
echo "Creating daily opportunity detection job..."
gcloud scheduler jobs create http opportunity-detection-daily \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 7 * * *" \
  --uri="${ASO_ENGINE_URL}/api/opportunities/detect" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"tenant_id":"platform","auto_create_tasks":true}' \
  --oidc-service-account-email=${SA_EMAIL} \
  --oidc-token-audience=${ASO_ENGINE_URL} \
  --time-zone="America/New_York" \
  --description="Daily automated opportunity detection" \
  --attempt-deadline=300s \
  --max-retry-attempts=3 || echo "Job already exists, updating..."

gcloud scheduler jobs update http opportunity-detection-daily \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 7 * * *" \
  --uri="${ASO_ENGINE_URL}/api/opportunities/detect" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"tenant_id":"platform","auto_create_tasks":true}' \
  --time-zone="America/New_York" \
  --attempt-deadline=300s \
  --max-retry-attempts=3 >/dev/null 2>&1 || true

echo -e "${GREEN}✓ Daily opportunity detection job configured${NC}"

# Job 4: Weekly competitor analysis
echo "Creating weekly competitor analysis job..."
gcloud scheduler jobs create http competitor-analysis-weekly \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 8 * * 1" \
  --uri="${ASO_ENGINE_URL}/api/internal/analyze-competitors" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"depth":"full","include_content":true}' \
  --oidc-service-account-email=${SA_EMAIL} \
  --oidc-token-audience=${ASO_ENGINE_URL} \
  --time-zone="America/New_York" \
  --description="Weekly competitor content and ranking analysis" \
  --attempt-deadline=900s \
  --max-retry-attempts=2 || echo "Job already exists, updating..."

gcloud scheduler jobs update http competitor-analysis-weekly \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 8 * * 1" \
  --uri="${ASO_ENGINE_URL}/api/internal/analyze-competitors" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"depth":"full","include_content":true}' \
  --time-zone="America/New_York" \
  --attempt-deadline=900s \
  --max-retry-attempts=2 >/dev/null 2>&1 || true

echo -e "${GREEN}✓ Weekly competitor analysis job configured${NC}"

# Job 5: Daily fact verification cleanup (remove old facts)
echo "Creating daily fact cleanup job..."
gcloud scheduler jobs create http fact-cleanup-daily \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 2 * * *" \
  --uri="${FACT_CHECKING_URL}/api/internal/cleanup" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"max_age_days":180,"min_used_count":2}' \
  --oidc-service-account-email=${SA_EMAIL} \
  --oidc-token-audience=${FACT_CHECKING_URL} \
  --time-zone="America/New_York" \
  --description="Daily cleanup of unused verified facts" \
  --attempt-deadline=300s \
  --max-retry-attempts=2 || echo "Job already exists, updating..."

gcloud scheduler jobs update http fact-cleanup-daily \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 2 * * *" \
  --uri="${FACT_CHECKING_URL}/api/internal/cleanup" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"max_age_days":180,"min_used_count":2}' \
  --time-zone="America/New_York" \
  --attempt-deadline=300s \
  --max-retry-attempts=2 >/dev/null 2>&1 || true

echo -e "${GREEN}✓ Daily fact cleanup job configured${NC}"

# Job 6: Monthly performance reporting
echo "Creating monthly reporting job..."
gcloud scheduler jobs create http performance-report-monthly \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 9 1 * *" \
  --uri="${ASO_ENGINE_URL}/api/internal/generate-report" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"report_type":"monthly","include_predictions":true}' \
  --oidc-service-account-email=${SA_EMAIL} \
  --oidc-token-audience=${ASO_ENGINE_URL} \
  --time-zone="America/New_York" \
  --description="Monthly performance and prediction reporting" \
  --attempt-deadline=600s \
  --max-retry-attempts=2 || echo "Job already exists, updating..."

gcloud scheduler jobs update http performance-report-monthly \
  --project=${PROJECT_ID} \
  --location=${REGION} \
  --schedule="0 9 1 * *" \
  --uri="${ASO_ENGINE_URL}/api/internal/generate-report" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"report_type":"monthly","include_predictions":true}' \
  --time-zone="America/New_York" \
  --attempt-deadline=600s \
  --max-retry-attempts=2 >/dev/null 2>&1 || true

echo -e "${GREEN}✓ Monthly performance reporting job configured${NC}"

echo ""
echo -e "${BLUE}Step 3: Listing all scheduled jobs${NC}"
echo "------------------------------------------------------"

gcloud scheduler jobs list \
  --project=${PROJECT_ID} \
  --location=${REGION}

echo ""
echo "=================================================="
echo "Cloud Scheduler Setup Complete!"
echo "=================================================="
echo ""
echo -e "${GREEN}✓ 6 scheduled jobs configured:${NC}"
echo ""
echo "📊 Data Collection:"
echo "  • Hourly: Tier-1 keyword ranking checks"
echo "  • Daily (6am): Full SERP data collection"
echo "  • Weekly (Mon 8am): Competitor analysis"
echo ""
echo "🔍 Intelligence:"
echo "  • Daily (7am): Opportunity detection"
echo "  • Daily (2am): Fact database cleanup"
echo "  • Monthly (1st, 9am): Performance reports"
echo ""
echo "💡 Next Steps:"
echo "  1. Test jobs: gcloud scheduler jobs run JOB_NAME --location=${REGION}"
echo "  2. View logs: gcloud logging read 'resource.type=cloud_scheduler_job'"
echo "  3. Monitor: Cloud Console → Cloud Scheduler"
echo ""
echo "⚠️  NOTE: Services need internal endpoints implemented"
echo "    The jobs are configured but will fail until endpoints exist"
echo ""
