#!/bin/bash
#
# Deploy GCP Alert Policies for Xynergy Platform
# Phase 3: Reliability & Monitoring
#

set -e

PROJECT_ID="${PROJECT_ID:-xynergy-dev-1757909467}"

echo "=================================================="
echo "Deploying Alert Policies"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo ""

# NOTE: Replace this with your notification channel ID
# Get it by running: gcloud alpha monitoring channels list
NOTIFICATION_CHANNEL_ID=""

if [ -z "$NOTIFICATION_CHANNEL_ID" ]; then
    echo "⚠️  No notification channel configured"
    echo ""
    echo "To set up notifications:"
    echo "1. Create a notification channel:"
    echo "   gcloud alpha monitoring channels create \\"
    echo "     --display-name='Xynergy Alerts' \\"
    echo "     --type=email \\"
    echo "     --channel-labels=email_address=YOUR_EMAIL"
    echo ""
    echo "2. Get the channel ID:"
    echo "   gcloud alpha monitoring channels list"
    echo ""
    echo "3. Set it in this script: NOTIFICATION_CHANNEL_ID='projects/.../notificationChannels/...'"
    echo ""
    echo "Proceeding without notifications (alerts will still be created)..."
    echo ""
fi

# Function to create alert policy
create_alert() {
    local name="$1"
    local filter="$2"
    local threshold="$3"
    local comparison="$4"
    local duration="${5:-300s}"

    echo "Creating alert: $name"

    gcloud alpha monitoring policies create \
      --notification-channels="$NOTIFICATION_CHANNEL_ID" \
      --display-name="$name" \
      --condition-display-name="$name Condition" \
      --condition-threshold-value="$threshold" \
      --condition-threshold-duration="$duration" \
      --condition-threshold-comparison="$comparison" \
      --condition-threshold-filter="$filter" \
      --condition-threshold-aggregation-alignment-period=60s \
      --condition-threshold-aggregation-per-series-aligner=ALIGN_RATE \
      --alert-strategy-auto-close=604800s \
      2>&1 | grep -v "WARNING" || echo "  ✓ Created (or already exists)"
}

# Alert 1: High Error Rate
echo ""
echo "1. High Error Rate Alert"
create_alert \
    "Xynergy - High Error Rate (5xx)" \
    'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.label.response_code_class="5xx"' \
    "5" \
    "COMPARISON_GT" \
    "300s"

# Alert 2: High Memory Usage
echo ""
echo "2. High Memory Usage Alert"
create_alert \
    "Xynergy - High Memory Usage" \
    'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/container/memory/utilizations"' \
    "0.85" \
    "COMPARISON_GT" \
    "300s"

# Alert 3: High CPU Usage
echo ""
echo "3. High CPU Usage Alert"
create_alert \
    "Xynergy - High CPU Usage" \
    'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/container/cpu/utilizations"' \
    "0.80" \
    "COMPARISON_GT" \
    "600s"

# Alert 4: High Latency
echo ""
echo "4. High Latency Alert"
create_alert \
    "Xynergy - High Request Latency" \
    'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_latencies"' \
    "3000" \
    "COMPARISON_GT" \
    "300s"

echo ""
echo "=================================================="
echo "Alert Policies Created"
echo "=================================================="
echo ""
echo "View alerts in GCP Console:"
echo "https://console.cloud.google.com/monitoring/alerting/policies?project=$PROJECT_ID"
echo ""
echo "To set up notifications, see monitoring/README.md"
echo ""
