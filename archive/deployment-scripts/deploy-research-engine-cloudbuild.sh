#!/bin/bash

# Research Engine Deployment Script using Cloud Build
# Deploys Research Engine services to Google Cloud Run

set -e

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"

echo "🚀 Deploying Research Engine Services using Cloud Build"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Function to deploy a service using Cloud Build
deploy_service() {
    local service_dir=$1
    local service_name=$2

    echo "📦 Building and deploying $service_name using Cloud Build..."

    cd $service_dir

    # Deploy using Cloud Run with source build
    gcloud run deploy $service_name \
        --source . \
        --platform=managed \
        --region=$REGION \
        --allow-unauthenticated \
        --memory=2Gi \
        --cpu=2 \
        --min-instances=0 \
        --max-instances=10 \
        --set-env-vars="PROJECT_ID=${PROJECT_ID},REGION=${REGION}" \
        --service-account=xynergy-platform-sa@${PROJECT_ID}.iam.gserviceaccount.com \
        --quiet

    echo "✅ $service_name deployed successfully"
    cd ..
}

# Deploy services one by one
echo "🔧 Deploying Research Coordinator..."
deploy_service "research-coordinator" "xynergy-research-coordinator"

echo "🌍 Deploying Market Intelligence Service..."
deploy_service "market-intelligence-service" "xynergy-market-intelligence"

echo "🎯 Deploying Competitive Analysis Service..."
deploy_service "competitive-analysis-service" "xynergy-competitive-analysis"

echo ""
echo "🎉 Research Engine deployment complete!"
echo ""
echo "Service URLs:"
gcloud run services list --platform=managed --region=$REGION --filter="metadata.name:xynergy-research*" --format="table(metadata.name,status.url)"

echo ""
echo "✨ Research Engine is ready for operation!"