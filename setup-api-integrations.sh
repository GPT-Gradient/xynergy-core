#!/bin/bash
#
# Quick Setup Script for API Integrations
# Run this script to enable all required APIs and create placeholders
#

set -e

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "ASO Platform - API Integration Setup"
echo "=================================================="
echo ""

echo -e "${BLUE}Step 1: Enabling Required Google APIs${NC}"
echo "------------------------------------------------------"
echo "Enabling Search Console API..."
gcloud services enable searchconsole.googleapis.com --project=${PROJECT_ID}

echo "Enabling Analytics Data API..."
gcloud services enable analyticsdata.googleapis.com --project=${PROJECT_ID}

echo "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=${PROJECT_ID}

echo -e "${GREEN}✓ All Google APIs enabled${NC}"
echo ""

echo -e "${BLUE}Step 2: API Integration Status${NC}"
echo "------------------------------------------------------"
echo ""
echo "📊 REQUIRED MANUAL SETUP:"
echo ""
echo "1. ${YELLOW}Google Search Console (GSC)${NC}"
echo "   • Go to: https://console.cloud.google.com/apis/credentials?project=${PROJECT_ID}"
echo "   • Create OAuth 2.0 Client ID (Web application)"
echo "   • Add redirect URI: https://aso-engine-vgjxy554mq-uc.a.run.app/api/oauth/gsc/callback"
echo "   • Download JSON and store in Secret Manager"
echo "   • Status: Manual setup required"
echo ""

echo "2. ${YELLOW}Google Trends${NC}"
echo "   • No API key required!"
echo "   • Uses public pytrends library"
echo "   • Status: ✅ Ready to use"
echo ""

echo "3. ${YELLOW}Google Analytics 4 (GA4)${NC}"
echo "   • Create service account: ga4-reader@${PROJECT_ID}.iam.gserviceaccount.com"
echo "   • Grant Viewer access in GA4 property"
echo "   • Store service account key in Secret Manager"
echo "   • Status: Manual setup required"
echo ""

echo "4. ${YELLOW}Reddit API${NC}"
echo "   • Go to: https://www.reddit.com/prefs/apps"
echo "   • Create app (type: script)"
echo "   • Note client ID and secret"
echo "   • Status: Manual setup required"
echo ""

echo "5. ${YELLOW}Twitter API (X)${NC}"
echo "   • Go to: https://developer.twitter.com/"
echo "   • Apply for Essential access (FREE)"
echo "   • Create app and get Bearer token"
echo "   • Status: Manual setup required (24hr approval)"
echo ""

echo "=================================================="
echo "AUTOMATED SETUP AVAILABLE"
echo "=================================================="
echo ""

read -p "Would you like to create placeholder secrets for testing? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo ""
  echo -e "${BLUE}Creating placeholder secrets...${NC}"

  # Create placeholder secrets (to be replaced with real credentials)
  echo -n "placeholder-gsc-oauth" | gcloud secrets create gsc-oauth-credentials \
    --data-file=- --project=${PROJECT_ID} 2>/dev/null || \
    echo "Secret gsc-oauth-credentials already exists"

  echo -n "placeholder-ga4-sa" | gcloud secrets create ga4-service-account \
    --data-file=- --project=${PROJECT_ID} 2>/dev/null || \
    echo "Secret ga4-service-account already exists"

  echo -n "placeholder-reddit-id" | gcloud secrets create reddit-client-id \
    --data-file=- --project=${PROJECT_ID} 2>/dev/null || \
    echo "Secret reddit-client-id already exists"

  echo -n "placeholder-reddit-secret" | gcloud secrets create reddit-client-secret \
    --data-file=- --project=${PROJECT_ID} 2>/dev/null || \
    echo "Secret reddit-client-secret already exists"

  echo -n "placeholder-twitter-token" | gcloud secrets create twitter-bearer-token \
    --data-file=- --project=${PROJECT_ID} 2>/dev/null || \
    echo "Secret twitter-bearer-token already exists"

  echo ""
  echo -e "${GREEN}✓ Placeholder secrets created${NC}"
  echo ""
  echo "To replace with real credentials:"
  echo "  gcloud secrets versions add SECRET_NAME --data-file=real-credentials.json"
  echo ""
fi

echo "=================================================="
echo "NEXT STEPS"
echo "=================================================="
echo ""
echo "1. Follow the manual setup instructions in API_INTEGRATION_GUIDE.md"
echo ""
echo "2. For Google Search Console:"
echo "   • Create OAuth credentials in GCP Console"
echo "   • Download JSON file"
echo "   • gcloud secrets versions add gsc-oauth-credentials --data-file=client_secret.json"
echo ""
echo "3. For Google Analytics 4:"
echo "   • Create service account with this command:"
echo "   gcloud iam service-accounts create ga4-reader \\"
echo "     --display-name='GA4 Data Reader' \\"
echo "     --project=${PROJECT_ID}"
echo ""
echo "4. For Reddit:"
echo "   • Create app at https://www.reddit.com/prefs/apps"
echo "   • Store credentials:"
echo "   echo -n 'your-client-id' | gcloud secrets versions add reddit-client-id --data-file=-"
echo ""
echo "5. For Twitter:"
echo "   • Apply at https://developer.twitter.com/"
echo "   • After approval, store bearer token:"
echo "   echo -n 'your-bearer-token' | gcloud secrets versions add twitter-bearer-token --data-file=-"
echo ""
echo "6. Grant Secret Manager access to Cloud Run:"
for secret in gsc-oauth-credentials ga4-service-account reddit-client-id reddit-client-secret twitter-bearer-token; do
  echo "   gcloud secrets add-iam-policy-binding $secret \\"
  echo "     --member='serviceAccount:835612502919-compute@developer.gserviceaccount.com' \\"
  echo "     --role='roles/secretmanager.secretAccessor'"
done
echo ""
echo "=================================================="
echo "DOCUMENTATION"
echo "=================================================="
echo ""
echo "📄 Complete guide: API_INTEGRATION_GUIDE.md"
echo "📊 Estimated setup time: 2 hours"
echo "💰 Monthly cost: \$0 (all free APIs)"
echo ""
echo -e "${GREEN}✓ API Infrastructure Ready${NC}"
echo ""
