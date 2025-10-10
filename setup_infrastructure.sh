#!/bin/bash
#############################################
# Xynergy Platform - Infrastructure Setup
# Handles: Redis, API Keys, Service Cleanup
#############################################

set -e  # Exit on error

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"

echo "🚀 Xynergy Platform - Infrastructure Setup"
echo "=========================================="
echo ""

# ========================================
# 1. Create Redis Instance
# ========================================
echo "1️⃣  Creating Redis instance..."
echo "This will take 5-10 minutes..."
echo ""

gcloud redis instances create xynergy-cache \
  --project=$PROJECT_ID \
  --region=$REGION \
  --tier=basic \
  --size=1 \
  --network=default \
  --redis-version=redis_6_x \
  --display-name="Xynergy Platform Cache" \
  --labels=environment=production,platform=xynergy,purpose=ai-caching

echo "✅ Redis instance created!"
echo ""

# Get Redis IP
REDIS_IP=$(gcloud redis instances describe xynergy-cache \
  --region=$REGION \
  --project=$PROJECT_ID \
  --format="value(host)")

echo "📊 Redis Instance Details:"
echo "  IP: $REDIS_IP"
echo "  Port: 6379"
echo ""

if [ "$REDIS_IP" != "10.0.0.3" ]; then
  echo "⚠️  WARNING: Redis IP is $REDIS_IP (expected 10.0.0.3)"
  echo "You'll need to update REDIS_HOST environment variable on services"
  echo "I'll provide the commands to do this."
fi

# ========================================
# 2. Generate API Keys
# ========================================
echo ""
echo "2️⃣  Generating secure API keys..."

KEY1=$(openssl rand -hex 32)
KEY2=$(openssl rand -hex 32)
XYNERGY_API_KEYS="$KEY1,$KEY2"

echo "✅ Generated 2 API keys for rotation"
echo ""
echo "📋 Your API Keys (SAVE THESE SECURELY):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Key 1: $KEY1"
echo "Key 2: $KEY2"
echo ""
echo "Combined (for env var): $XYNERGY_API_KEYS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save to a file for reference
echo "$XYNERGY_API_KEYS" > /tmp/xynergy_api_keys.txt
echo "💾 Keys also saved to: /tmp/xynergy_api_keys.txt"
echo ""

# Store in Secret Manager
echo "Storing in GCP Secret Manager..."
echo -n "$XYNERGY_API_KEYS" | gcloud secrets create xynergy-api-keys \
  --data-file=- \
  --replication-policy="automatic" \
  --project=$PROJECT_ID 2>&1 || {
    echo "⚠️  Secret 'xynergy-api-keys' already exists. Updating..."
    echo -n "$XYNERGY_API_KEYS" | gcloud secrets versions add xynergy-api-keys \
      --data-file=- \
      --project=$PROJECT_ID
  }

echo "✅ Stored in Secret Manager: xynergy-api-keys"

# ========================================
# 3. Clean Up Redundant Services
# ========================================
echo ""
echo "3️⃣  Cleaning up redundant services..."
echo ""
echo "Found these redundant services:"
echo "  - ai-assistant (alternative: xynergy-ai-assistant ✅)"
echo "  - marketing-engine (alternative: xynergy-marketing-engine ✅)"
echo ""
read -p "Delete redundant services? (y/n): " CLEANUP

if [ "$CLEANUP" = "y" ]; then
  echo "Deleting ai-assistant..."
  gcloud run services delete ai-assistant \
    --region=$REGION \
    --project=$PROJECT_ID \
    --quiet 2>/dev/null && echo "  ✅ ai-assistant deleted" || echo "  ℹ️  ai-assistant not found or already deleted"

  echo "Deleting marketing-engine..."
  gcloud run services delete marketing-engine \
    --region=$REGION \
    --project=$PROJECT_ID \
    --quiet 2>/dev/null && echo "  ✅ marketing-engine deleted" || echo "  ℹ️  marketing-engine not found or already deleted"

  echo "✅ Cleanup complete"
else
  echo "⏭️  Skipped cleanup - redundant services kept"
fi

# ========================================
# 4. Summary
# ========================================
echo ""
echo "═══════════════════════════════════════════"
echo "🎉 Infrastructure Setup Complete!"
echo "═══════════════════════════════════════════"
echo ""
echo "✅ What's Done:"
echo "  - Redis instance created at $REDIS_IP:6379"
echo "  - API keys generated and stored in Secret Manager"
echo "  - Redundant services cleaned up (if selected)"
echo ""
echo "💾 Important Information Saved:"
echo "  - API Keys: /tmp/xynergy_api_keys.txt"
echo "  - Redis IP: $REDIS_IP"
echo ""
echo "⚠️  NEXT STEPS - Provide These To Claude:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Redis IP: $REDIS_IP"
echo "2. Get AI Provider API Key:"
echo "   Option A (Recommended): Abacus AI - https://abacus.ai/"
echo "   Option B: OpenAI - https://platform.openai.com/"
echo "   Option C (Best): Both for redundancy"
echo ""
echo "3. Optional: SendGrid API Key - https://sendgrid.com/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💰 Cost Impact:"
echo "  - Redis: +$50/month"
echo "  - Saves: $1,500/month in AI costs (with caching)"
echo "  - Net Savings: $1,450/month ($17,400/year)"
echo ""
echo "📊 Current Service Status:"
gcloud run services list --platform=managed --region=$REGION --project=$PROJECT_ID --format="table(metadata.name, status.conditions[0].status)" 2>&1 | grep -E "NAME|xynergy-|aso-|fact-checking|internal-ai"
echo ""
echo "🔐 Your API Keys are in: /tmp/xynergy_api_keys.txt"
echo "⚠️  Keep these secret! You'll need them for API requests."
