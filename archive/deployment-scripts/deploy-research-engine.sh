#!/bin/bash

# Research Engine Deployment Script
# Deploys Research Engine services to Google Cloud Run

set -e

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
ARTIFACT_REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/xynergy-platform"

echo "🚀 Deploying Research Engine Services"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Registry: $ARTIFACT_REGISTRY"

# Authenticate Docker with Artifact Registry
echo "🔐 Authenticating with Artifact Registry..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Function to build and deploy a service
deploy_service() {
    local service_dir=$1
    local service_name=$2

    echo "📦 Building and deploying $service_name..."

    # Build image
    cd $service_dir
    docker build -t ${ARTIFACT_REGISTRY}/${service_name}:latest .

    # Push image
    docker push ${ARTIFACT_REGISTRY}/${service_name}:latest

    # Deploy to Cloud Run
    gcloud run deploy $service_name \
        --image=${ARTIFACT_REGISTRY}/${service_name}:latest \
        --platform=managed \
        --region=$REGION \
        --allow-unauthenticated \
        --memory=2Gi \
        --cpu=2 \
        --min-instances=0 \
        --max-instances=10 \
        --set-env-vars="PROJECT_ID=${PROJECT_ID},REGION=${REGION}" \
        --service-account=xynergy-platform-sa@${PROJECT_ID}.iam.gserviceaccount.com

    echo "✅ $service_name deployed successfully"
    cd ..
}

# Deploy services
deploy_service "research-coordinator" "xynergy-research-coordinator"
deploy_service "market-intelligence-service" "xynergy-market-intelligence"
deploy_service "competitive-analysis-service" "xynergy-competitive-analysis"

echo ""
echo "🎉 Research Engine deployment complete!"
echo ""
echo "Service URLs:"
gcloud run services list --platform=managed --region=$REGION --filter="metadata.name:xynergy-research*" --format="table(metadata.name,status.url)"

echo ""
echo "🔍 Testing services..."

# Test health endpoints
for service in "xynergy-research-coordinator" "xynergy-market-intelligence" "xynergy-competitive-analysis"; do
    echo "Testing $service..."
    url=$(gcloud run services describe $service --platform=managed --region=$REGION --format="value(status.url)")
    curl -s "${url}/health" | jq '.' || echo "❌ Health check failed for $service"
done

echo ""
echo "✨ Research Engine is ready for operation!"