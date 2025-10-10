#!/bin/bash
set -e

PROJECT_ID="xynergy-dev-1757909467"
SERVICE_NAME="xynergy-intelligence-gateway"
REGION="us-central1"

echo "🚀 Deploying $SERVICE_NAME to Cloud Run..."

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --source=. \
  --platform=managed \
  --region=$REGION \
  --project=$PROJECT_ID \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=60 \
  --concurrency=80 \
  --set-env-vars=ENVIRONMENT=production,ASO_ENGINE_URL=https://aso-engine-vgjxy554mq-uc.a.run.app,GOOGLE_CLOUD_PROJECT=$PROJECT_ID

echo "✅ Deployment complete!"
echo ""
echo "Service URL:"
gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format='value(status.url)'
