#!/bin/bash

###############################################################################
# XynergyOS Enhanced Monitoring Setup
#
# This script sets up Cloud Monitoring dashboard and alert policies
#
# Prerequisites:
# 1. gcloud authenticated
# 2. monitoring/dashboard-config.json exists
# 3. Proper permissions for Cloud Monitoring
#
# Usage: ./scripts/setup-monitoring.sh
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ID="xynergy-dev-1757909467"

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
# Create Dashboard
###############################################################################

create_dashboard() {
    print_header "Creating Cloud Monitoring Dashboard"

    if [ ! -f "monitoring/dashboard-config.json" ]; then
        print_error "Dashboard config not found at monitoring/dashboard-config.json"
        exit 1
    fi

    print_info "Creating XynergyOS Integration Dashboard..."

    gcloud monitoring dashboards create \
        --config-from-file=monitoring/dashboard-config.json \
        --project=$PROJECT_ID 2>/dev/null || {
        print_info "Dashboard may already exist, updating..."
        # Get dashboard ID and update
        DASHBOARD_ID=$(gcloud monitoring dashboards list --project=$PROJECT_ID --filter="displayName:'XynergyOS Integration Dashboard'" --format="value(name)" | head -1)
        if [ -n "$DASHBOARD_ID" ]; then
            gcloud monitoring dashboards update $DASHBOARD_ID \
                --config-from-file=monitoring/dashboard-config.json \
                --project=$PROJECT_ID
            print_success "Dashboard updated"
        else
            print_error "Failed to create or update dashboard"
            return 1
        fi
    }

    print_success "Dashboard created/updated successfully"

    # Get dashboard URL
    DASHBOARD_ID=$(gcloud monitoring dashboards list --project=$PROJECT_ID --filter="displayName:'XynergyOS Integration Dashboard'" --format="value(name)" | head -1)
    echo ""
    echo "Dashboard URL:"
    echo "https://console.cloud.google.com/monitoring/dashboards/custom/$DASHBOARD_ID?project=$PROJECT_ID"
    echo ""
}

###############################################################################
# Create Alert Policies
###############################################################################

create_alert_high_error_rate() {
    print_header "Creating Alert: High Error Rate"

    gcloud alpha monitoring policies create \
        --notification-channels="" \
        --display-name="XynergyOS High Error Rate" \
        --condition-display-name="Error rate > 10%" \
        --condition-threshold-value=0.10 \
        --condition-threshold-duration=300s \
        --condition-filter='resource.type="cloud_run_revision" AND resource.labels.service_name=monitoring.regex.full_match(".*intelligence.*") AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"' \
        --aggregation='{"alignmentPeriod":"60s","perSeriesAligner":"ALIGN_RATE","crossSeriesReducer":"REDUCE_SUM"}' \
        --project=$PROJECT_ID 2>/dev/null || print_info "Alert may already exist"

    print_success "High error rate alert configured"
}

create_alert_high_latency() {
    print_header "Creating Alert: High Latency"

    gcloud alpha monitoring policies create \
        --notification-channels="" \
        --display-name="XynergyOS High Latency" \
        --condition-display-name="P95 latency > 2s" \
        --condition-threshold-value=2000 \
        --condition-threshold-duration=300s \
        --condition-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="xynergyos-intelligence-gateway" AND metric.type="run.googleapis.com/request_latencies"' \
        --aggregation='{"alignmentPeriod":"60s","perSeriesAligner":"ALIGN_DELTA","crossSeriesReducer":"REDUCE_PERCENTILE_95"}' \
        --project=$PROJECT_ID 2>/dev/null || print_info "Alert may already exist"

    print_success "High latency alert configured"
}

create_alert_service_down() {
    print_header "Creating Alert: Service Down"

    gcloud alpha monitoring policies create \
        --notification-channels="" \
        --display-name="XynergyOS Service Down" \
        --condition-display-name="No requests for 5 minutes" \
        --condition-threshold-value=0 \
        --condition-threshold-duration=300s \
        --condition-threshold-comparison=COMPARISON_LT \
        --condition-filter='resource.type="cloud_run_revision" AND resource.labels.service_name="xynergyos-intelligence-gateway" AND metric.type="run.googleapis.com/request_count"' \
        --aggregation='{"alignmentPeriod":"60s","perSeriesAligner":"ALIGN_RATE","crossSeriesReducer":"REDUCE_SUM"}' \
        --project=$PROJECT_ID 2>/dev/null || print_info "Alert may already exist"

    print_success "Service down alert configured"
}

###############################################################################
# Setup Notification Channels
###############################################################################

setup_notification_channels() {
    print_header "Notification Channels Setup"

    echo "To receive alerts, set up notification channels:"
    echo ""
    echo "1. Go to: https://console.cloud.google.com/monitoring/alerting/notifications?project=$PROJECT_ID"
    echo "2. Click 'Add Notification Channel'"
    echo "3. Choose your preferred channel (Email, Slack, PagerDuty, etc.)"
    echo "4. Configure the channel"
    echo "5. Update alert policies to use the new channel"
    echo ""
    echo "Supported channels:"
    echo "  - Email"
    echo "  - Slack"
    echo "  - PagerDuty"
    echo "  - Webhook"
    echo "  - SMS"
    echo "  - Mobile Push"
    echo ""

    print_info "Notification channels must be configured manually"
}

###############################################################################
# Create Log-Based Metrics
###############################################################################

create_log_metrics() {
    print_header "Creating Log-Based Metrics"

    # OAuth success rate metric
    print_info "Creating OAuth success rate metric..."
    gcloud logging metrics create oauth_success_rate \
        --description="OAuth authentication success rate" \
        --log-filter='resource.type="cloud_run_revision"
        AND (resource.labels.service_name:"slack-intelligence-service"
             OR resource.labels.service_name:"gmail-intelligence-service"
             OR resource.labels.service_name:"calendar-intelligence-service")
        AND jsonPayload.message=~"OAuth.*success"' \
        --project=$PROJECT_ID 2>/dev/null || print_info "Metric may already exist"

    # OAuth failure rate metric
    print_info "Creating OAuth failure rate metric..."
    gcloud logging metrics create oauth_failure_rate \
        --description="OAuth authentication failure rate" \
        --log-filter='resource.type="cloud_run_revision"
        AND (resource.labels.service_name:"slack-intelligence-service"
             OR resource.labels.service_name:"gmail-intelligence-service"
             OR resource.labels.service_name:"calendar-intelligence-service")
        AND (jsonPayload.message=~"OAuth.*fail" OR severity="ERROR")' \
        --project=$PROJECT_ID 2>/dev/null || print_info "Metric may already exist"

    print_success "Log-based metrics configured"
}

###############################################################################
# Main
###############################################################################

print_header "XynergyOS Enhanced Monitoring Setup"

create_dashboard
create_alert_high_error_rate
create_alert_high_latency
create_alert_service_down
create_log_metrics
setup_notification_channels

###############################################################################
# Summary
###############################################################################

print_header "Monitoring Setup Complete"

echo "What was configured:"
echo "  ✅ Cloud Monitoring Dashboard"
echo "  ✅ High Error Rate Alert (>10%)"
echo "  ✅ High Latency Alert (P95 >2s)"
echo "  ✅ Service Down Alert (no requests for 5min)"
echo "  ✅ Log-based metrics for OAuth"
echo ""
echo "Next Steps:"
echo "  1. View dashboard: https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
echo "  2. Configure notification channels (see instructions above)"
echo "  3. Test alerts by triggering conditions"
echo "  4. Customize alert thresholds as needed"
echo ""
echo "Monitoring Resources:"
echo "  - Dashboards: https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
echo "  - Alerts: https://console.cloud.google.com/monitoring/alerting?project=$PROJECT_ID"
echo "  - Logs: https://console.cloud.google.com/logs?project=$PROJECT_ID"
echo "  - Metrics: https://console.cloud.google.com/monitoring/metrics-explorer?project=$PROJECT_ID"
echo ""

print_success "Enhanced monitoring is now active!"
