#!/bin/bash

echo "🔧 Fixing Phase 2 Dockerfile issues for all services..."

SERVICES_WITH_PHASE2=(
    "ai-assistant"
    "ai-routing-engine" 
    "analytics-data-layer"
    "content-hub"
    "marketing-engine"
    "project-management"
    "qa-engine"
    "reports-export"
    "scheduler-automation-engine"
    "secrets-config"
    "security-governance"
    "system-runtime"
)

for service in "${SERVICES_WITH_PHASE2[@]}"; do
    echo "🔧 Rebuilding and deploying $service..."
    
    cd "$service"
    
    # Build for correct architecture
    docker build --platform linux/amd64 \
        -t "us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergy-$service:phase2-fixed" . || {
        echo "❌ Build failed for $service"
        cd ..
        continue
    }
    
    # Push image
    docker push "us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergy-$service:phase2-fixed" || {
        echo "❌ Push failed for $service"
        cd ..
        continue
    }
    
    # Deploy to Cloud Run
    gcloud run deploy "xynergy-$service" \
        --image "us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/xynergy-$service:phase2-fixed" \
        --region us-central1 \
        --platform managed || {
        echo "❌ Deploy failed for $service"
        cd ..
        continue
    }
    
    echo "✅ $service fixed and deployed successfully!"
    cd ..
done

echo "🎉 Phase 2 Dockerfile fixes complete!"
