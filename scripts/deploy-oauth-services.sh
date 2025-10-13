#!/bin/bash

###############################################################################
# XynergyOS OAuth Services Deployment Script
#
# This script builds and deploys all OAuth-enabled services with their
# credentials from Secret Manager.
#
# Prerequisites:
# 1. OAuth credentials stored in Secret Manager
# 2. Services updated with OAuth support
# 3. gcloud authenticated and project set
#
# Usage: ./scripts/deploy-oauth-services.sh [service-name]
#        If no service name provided, deploys all OAuth services
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
ARTIFACT_REGISTRY="us-central1-docker.pkg.dev/$PROJECT_ID/xynergy-services"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

###############################################################################
# Slack Intelligence Service
###############################################################################

deploy_slack() {
    print_header "Deploying Slack Intelligence Service"

    cd slack-intelligence-service

    print_info "Installing dependencies..."
    npm install

    print_info "Building TypeScript..."
    npm run build

    print_info "Building Docker image..."
    gcloud builds submit \
        --tag $ARTIFACT_REGISTRY/slack-intelligence-service:latest \
        --project $PROJECT_ID

    print_info "Deploying to Cloud Run..."
    gcloud run deploy slack-intelligence-service \
        --image $ARTIFACT_REGISTRY/slack-intelligence-service:latest \
        --region $REGION \
        --project $PROJECT_ID \
        --platform managed \
        --allow-unauthenticated \
        --memory 256Mi \
        --cpu 1 \
        --timeout 30s \
        --max-instances 10 \
        --set-secrets="SLACK_BOT_TOKEN=SLACK_BOT_TOKEN:latest,SLACK_CLIENT_ID=SLACK_CLIENT_ID:latest,SLACK_CLIENT_SECRET=SLACK_CLIENT_SECRET:latest,SLACK_SIGNING_SECRET=SLACK_SIGNING_SECRET:latest"

    print_success "Slack service deployed"
    cd ..
}

###############################################################################
# Gmail Intelligence Service
###############################################################################

deploy_gmail() {
    print_header "Deploying Gmail Intelligence Service"

    cd gmail-intelligence-service

    print_info "Installing dependencies..."
    npm install

    print_info "Building TypeScript..."
    npm run build

    print_info "Building Docker image..."
    gcloud builds submit \
        --tag $ARTIFACT_REGISTRY/gmail-intelligence-service:latest \
        --project $PROJECT_ID

    print_info "Deploying to Cloud Run..."
    gcloud run deploy gmail-intelligence-service \
        --image $ARTIFACT_REGISTRY/gmail-intelligence-service:latest \
        --region $REGION \
        --project $PROJECT_ID \
        --platform managed \
        --allow-unauthenticated \
        --memory 256Mi \
        --cpu 1 \
        --timeout 30s \
        --max-instances 10 \
        --set-secrets="GMAIL_CLIENT_ID=GMAIL_CLIENT_ID:latest,GMAIL_CLIENT_SECRET=GMAIL_CLIENT_SECRET:latest"

    print_success "Gmail service deployed"
    cd ..
}

###############################################################################
# Calendar Intelligence Service
###############################################################################

deploy_calendar() {
    print_header "Deploying Calendar Intelligence Service"

    cd calendar-intelligence-service

    print_info "Installing dependencies..."
    npm install

    print_info "Building TypeScript..."
    npm run build

    print_info "Building Docker image..."
    gcloud builds submit \
        --tag $ARTIFACT_REGISTRY/calendar-intelligence-service:latest \
        --project $PROJECT_ID

    print_info "Deploying to Cloud Run..."
    gcloud run deploy calendar-intelligence-service \
        --image $ARTIFACT_REGISTRY/calendar-intelligence-service:latest \
        --region $REGION \
        --project $PROJECT_ID \
        --platform managed \
        --allow-unauthenticated \
        --memory 256Mi \
        --cpu 1 \
        --timeout 30s \
        --max-instances 10 \
        --set-secrets="GMAIL_CLIENT_ID=GMAIL_CLIENT_ID:latest,GMAIL_CLIENT_SECRET=GMAIL_CLIENT_SECRET:latest"

    print_success "Calendar service deployed"
    cd ..
}

###############################################################################
# Main
###############################################################################

print_header "XynergyOS OAuth Services Deployment"

# Check if specific service requested
SERVICE="${1:-all}"

case $SERVICE in
    slack)
        deploy_slack
        ;;
    gmail)
        deploy_gmail
        ;;
    calendar)
        deploy_calendar
        ;;
    all)
        deploy_slack
        deploy_gmail
        deploy_calendar
        ;;
    *)
        print_error "Unknown service: $SERVICE"
        echo "Usage: $0 [slack|gmail|calendar|all]"
        exit 1
        ;;
esac

###############################################################################
# Verify Deployment
###############################################################################

print_header "Verifying Deployments"

# Wait for services to be ready
print_info "Waiting 10 seconds for services to initialize..."
sleep 10

# Test Slack
print_info "Testing Slack service..."
SLACK_RESPONSE=$(curl -s https://slack-intelligence-service-835612502919.us-central1.run.app/ 2>/dev/null || echo "ERROR")
if echo "$SLACK_RESPONSE" | grep -q "Slack Intelligence"; then
    print_success "Slack service is responding"
    if echo "$SLACK_RESPONSE" | grep -q '"mockMode":false'; then
        print_success "Slack OAuth IS CONFIGURED - Real data enabled!"
    else
        print_info "Slack still in mock mode (check credentials)"
    fi
else
    print_error "Slack service not responding correctly"
fi

# Test Gmail
print_info "Testing Gmail service..."
GMAIL_RESPONSE=$(curl -s https://gmail-intelligence-service-835612502919.us-central1.run.app/ 2>/dev/null || echo "ERROR")
if echo "$GMAIL_RESPONSE" | grep -q "Gmail Intelligence"; then
    print_success "Gmail service is responding"
    if echo "$GMAIL_RESPONSE" | grep -q '"mockMode":false'; then
        print_success "Gmail OAuth IS CONFIGURED - Real data enabled!"
    else
        print_info "Gmail still in mock mode (check credentials)"
    fi
else
    print_error "Gmail service not responding correctly"
fi

# Test Calendar
print_info "Testing Calendar service..."
CALENDAR_RESPONSE=$(curl -s https://calendar-intelligence-service-835612502919.us-central1.run.app/ 2>/dev/null || echo "ERROR")
if echo "$CALENDAR_RESPONSE" | grep -q "Calendar Intelligence"; then
    print_success "Calendar service is responding"
    if echo "$CALENDAR_RESPONSE" | grep -q '"mockMode":false'; then
        print_success "Calendar OAuth IS CONFIGURED - Real data enabled!"
    else
        print_info "Calendar still in mock mode (check credentials)"
    fi
else
    print_error "Calendar service not responding correctly"
fi

###############################################################################
# Summary
###############################################################################

print_header "Deployment Complete"

echo "Service URLs:"
echo "  Slack:    https://slack-intelligence-service-835612502919.us-central1.run.app"
echo "  Gmail:    https://gmail-intelligence-service-835612502919.us-central1.run.app"
echo "  Calendar: https://calendar-intelligence-service-835612502919.us-central1.run.app"
echo ""
echo "Next Steps:"
echo "1. Run comprehensive verification: ./scripts/verify-deployment.sh"
echo "2. Test with real OAuth credentials if configured"
echo "3. Check Cloud Run logs for any issues:"
echo "   gcloud run services logs read slack-intelligence-service"
echo "   gcloud run services logs read gmail-intelligence-service"
echo "   gcloud run services logs read calendar-intelligence-service"
echo ""

print_success "All OAuth services deployed successfully!"
