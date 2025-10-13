#!/bin/bash

###############################################################################
# XynergyOS Phase 2 OAuth Setup Script
#
# This script automates the backend portion of OAuth configuration for
# Slack, Gmail, and Calendar services.
#
# Prerequisites:
# 1. Slack App created at https://api.slack.com/apps
# 2. Google OAuth Client created in Cloud Console
# 3. OAuth credentials ready to store
#
# Usage: ./scripts/phase2-oauth-setup.sh
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
SERVICE_ACCOUNT="835612502919-compute@developer.gserviceaccount.com"

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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

prompt_user() {
    local prompt="$1"
    local var_name="$2"
    echo -e "${YELLOW}${prompt}${NC}"
    read -r value
    eval "$var_name='$value'"
}

###############################################################################
# Check Prerequisites
###############################################################################

print_header "Phase 2 OAuth Setup - Prerequisites Check"

# Check gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed"
    exit 1
fi
print_success "gcloud CLI found"

# Check authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    print_error "Not authenticated with gcloud"
    echo "Run: gcloud auth login"
    exit 1
fi
print_success "Authenticated with gcloud"

# Check project access
if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
    print_error "Cannot access project $PROJECT_ID"
    exit 1
fi
print_success "Project access confirmed"

###############################################################################
# Enable Required APIs
###############################################################################

print_header "Step 1: Enable Required APIs"

print_info "Enabling Gmail API..."
gcloud services enable gmail.googleapis.com --project=$PROJECT_ID
print_success "Gmail API enabled"

print_info "Enabling Calendar API..."
gcloud services enable calendar-json.googleapis.com --project=$PROJECT_ID
print_success "Calendar API enabled"

print_info "Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID
print_success "Secret Manager API enabled"

###############################################################################
# Slack OAuth Setup
###############################################################################

print_header "Step 2: Slack OAuth Configuration"

echo ""
echo "Before continuing, please:"
echo "1. Go to https://api.slack.com/apps"
echo "2. Click 'Create New App' → 'From scratch'"
echo "3. App Name: 'XynergyOS Intelligence'"
echo "4. Select your workspace"
echo "5. In 'OAuth & Permissions', add redirect URL:"
echo "   https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/oauth/callback"
echo "6. Add Bot Token Scopes:"
echo "   - channels:read"
echo "   - channels:history"
echo "   - chat:write"
echo "   - users:read"
echo "   - search:read"
echo "7. Install app to workspace and copy Bot User OAuth Token"
echo "8. Go to 'Basic Information' and copy Client ID, Client Secret, Signing Secret"
echo ""

read -p "Have you completed the Slack App setup? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Skipping Slack OAuth setup"
    SKIP_SLACK=true
else
    SKIP_SLACK=false

    prompt_user "Enter Slack Bot Token (xoxb-...): " SLACK_BOT_TOKEN
    prompt_user "Enter Slack Client ID: " SLACK_CLIENT_ID
    prompt_user "Enter Slack Client Secret: " SLACK_CLIENT_SECRET
    prompt_user "Enter Slack Signing Secret: " SLACK_SIGNING_SECRET

    print_info "Storing Slack credentials in Secret Manager..."

    # Store Slack Bot Token
    echo -n "$SLACK_BOT_TOKEN" | gcloud secrets create SLACK_BOT_TOKEN \
        --data-file=- \
        --project=$PROJECT_ID 2>/dev/null || \
    echo -n "$SLACK_BOT_TOKEN" | gcloud secrets versions add SLACK_BOT_TOKEN \
        --data-file=- \
        --project=$PROJECT_ID

    # Store Client ID
    echo -n "$SLACK_CLIENT_ID" | gcloud secrets create SLACK_CLIENT_ID \
        --data-file=- \
        --project=$PROJECT_ID 2>/dev/null || \
    echo -n "$SLACK_CLIENT_ID" | gcloud secrets versions add SLACK_CLIENT_ID \
        --data-file=- \
        --project=$PROJECT_ID

    # Store Client Secret
    echo -n "$SLACK_CLIENT_SECRET" | gcloud secrets create SLACK_CLIENT_SECRET \
        --data-file=- \
        --project=$PROJECT_ID 2>/dev/null || \
    echo -n "$SLACK_CLIENT_SECRET" | gcloud secrets versions add SLACK_CLIENT_SECRET \
        --data-file=- \
        --project=$PROJECT_ID

    # Store Signing Secret
    echo -n "$SLACK_SIGNING_SECRET" | gcloud secrets create SLACK_SIGNING_SECRET \
        --data-file=- \
        --project=$PROJECT_ID 2>/dev/null || \
    echo -n "$SLACK_SIGNING_SECRET" | gcloud secrets versions add SLACK_SIGNING_SECRET \
        --data-file=- \
        --project=$PROJECT_ID

    print_success "Slack credentials stored in Secret Manager"

    # Grant service account access
    print_info "Granting service account access to secrets..."

    for secret in SLACK_BOT_TOKEN SLACK_CLIENT_ID SLACK_CLIENT_SECRET SLACK_SIGNING_SECRET; do
        gcloud secrets add-iam-policy-binding $secret \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="roles/secretmanager.secretAccessor" \
            --project=$PROJECT_ID &> /dev/null || true
    done

    print_success "Service account access granted"
fi

###############################################################################
# Gmail OAuth Setup
###############################################################################

print_header "Step 3: Gmail OAuth Configuration"

echo ""
echo "Before continuing, please:"
echo "1. Go to https://console.cloud.google.com"
echo "2. Select project: $PROJECT_ID"
echo "3. Navigate to 'APIs & Services' > 'Credentials'"
echo "4. Click 'Create Credentials' > 'OAuth 2.0 Client ID'"
echo "5. If needed, configure OAuth consent screen:"
echo "   - User Type: Internal (or External)"
echo "   - App name: XynergyOS Intelligence"
echo "6. Application type: Web application"
echo "7. Name: XynergyOS Gmail Integration"
echo "8. Authorized redirect URIs:"
echo "   https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/gmail/oauth/callback"
echo "9. Add scopes:"
echo "   - https://www.googleapis.com/auth/gmail.readonly"
echo "   - https://www.googleapis.com/auth/gmail.send"
echo "   - https://www.googleapis.com/auth/gmail.modify"
echo "   - https://www.googleapis.com/auth/calendar (for Calendar)"
echo "10. Copy Client ID and Client Secret"
echo ""

read -p "Have you completed the Google OAuth setup? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Skipping Gmail/Calendar OAuth setup"
    SKIP_GOOGLE=true
else
    SKIP_GOOGLE=false

    prompt_user "Enter Google OAuth Client ID: " GMAIL_CLIENT_ID
    prompt_user "Enter Google OAuth Client Secret: " GMAIL_CLIENT_SECRET

    print_info "Storing Google OAuth credentials in Secret Manager..."

    # Store Gmail Client ID
    echo -n "$GMAIL_CLIENT_ID" | gcloud secrets create GMAIL_CLIENT_ID \
        --data-file=- \
        --project=$PROJECT_ID 2>/dev/null || \
    echo -n "$GMAIL_CLIENT_ID" | gcloud secrets versions add GMAIL_CLIENT_ID \
        --data-file=- \
        --project=$PROJECT_ID

    # Store Gmail Client Secret
    echo -n "$GMAIL_CLIENT_SECRET" | gcloud secrets create GMAIL_CLIENT_SECRET \
        --data-file=- \
        --project=$PROJECT_ID 2>/dev/null || \
    echo -n "$GMAIL_CLIENT_SECRET" | gcloud secrets versions add GMAIL_CLIENT_SECRET \
        --data-file=- \
        --project=$PROJECT_ID

    print_success "Google OAuth credentials stored in Secret Manager"

    # Grant service account access
    print_info "Granting service account access to secrets..."

    for secret in GMAIL_CLIENT_ID GMAIL_CLIENT_SECRET; do
        gcloud secrets add-iam-policy-binding $secret \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="roles/secretmanager.secretAccessor" \
            --project=$PROJECT_ID &> /dev/null || true
    done

    print_success "Service account access granted"
fi

###############################################################################
# Summary
###############################################################################

print_header "OAuth Setup Complete"

echo "Credentials Status:"
if [ "$SKIP_SLACK" = false ]; then
    print_success "Slack OAuth credentials stored"
else
    print_warning "Slack OAuth skipped"
fi

if [ "$SKIP_GOOGLE" = false ]; then
    print_success "Google OAuth credentials stored (Gmail + Calendar)"
else
    print_warning "Google OAuth skipped"
fi

echo ""
echo "Next Steps:"
echo "1. Run: cd slack-intelligence-service && npm run build"
echo "2. Run: cd gmail-intelligence-service && npm run build"
echo "3. Run: cd calendar-intelligence-service && npm run build"
echo "4. Run: ./scripts/deploy-oauth-services.sh"
echo ""
echo "This will deploy the updated services with OAuth enabled."
echo ""

print_success "Phase 2 OAuth backend setup complete!"
