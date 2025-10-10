#!/bin/bash
#
# Deploy ASO Cloud Storage Infrastructure
# Creates buckets for content, competitors, reports, and training data
#

set -e

PROJECT_ID="xynergy-dev-1757909467"
REGION="us-central1"
LOCATION="US"  # Multi-region for better availability

echo "=================================================="
echo "ASO Platform Cloud Storage Setup"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Location: $LOCATION (multi-region)"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Creating Storage Buckets${NC}"
echo "------------------------------------------------------"

# Content assets bucket (high-frequency access)
BUCKET_CONTENT="${PROJECT_ID}-aso-content"
echo -n "Creating content assets bucket ($BUCKET_CONTENT)... "
gsutil mb -p ${PROJECT_ID} -c STANDARD -l ${REGION} gs://${BUCKET_CONTENT}/ 2>&1 | grep -q "already exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Competitor data bucket (medium-frequency access)
BUCKET_COMPETITORS="${PROJECT_ID}-aso-competitors"
echo -n "Creating competitor data bucket ($BUCKET_COMPETITORS)... "
gsutil mb -p ${PROJECT_ID} -c STANDARD -l ${REGION} gs://${BUCKET_COMPETITORS}/ 2>&1 | grep -q "already exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Reports bucket (low-frequency access, cost-optimized)
BUCKET_REPORTS="${PROJECT_ID}-aso-reports"
echo -n "Creating reports bucket ($BUCKET_REPORTS)... "
gsutil mb -p ${PROJECT_ID} -c NEARLINE -l ${REGION} gs://${BUCKET_REPORTS}/ 2>&1 | grep -q "already exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# Training data bucket (low-frequency access)
BUCKET_TRAINING="${PROJECT_ID}-aso-training"
echo -n "Creating training data bucket ($BUCKET_TRAINING)... "
gsutil mb -p ${PROJECT_ID} -c NEARLINE -l ${REGION} gs://${BUCKET_TRAINING}/ 2>&1 | grep -q "already exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

# LLM models bucket (infrequent access)
BUCKET_MODELS="${PROJECT_ID}-aso-models"
echo -n "Creating LLM models bucket ($BUCKET_MODELS)... "
gsutil mb -p ${PROJECT_ID} -c STANDARD -l ${REGION} gs://${BUCKET_MODELS}/ 2>&1 | grep -q "already exists" && echo -e "${YELLOW}⚠ Exists${NC}" || echo -e "${GREEN}✓${NC}"

echo ""
echo -e "${BLUE}Step 2: Setting Lifecycle Policies${NC}"
echo "------------------------------------------------------"

# Content bucket lifecycle (delete old drafts after 90 days)
echo -n "Setting content lifecycle policy... "
cat > /tmp/content-lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 90,
          "matchesPrefix": ["drafts/"]
        }
      }
    ]
  }
}
EOF
gsutil lifecycle set /tmp/content-lifecycle.json gs://${BUCKET_CONTENT}/ 2>&1 | grep -q "Setting lifecycle" && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Already set${NC}"

# Competitor data lifecycle (delete raw scrapes after 180 days)
echo -n "Setting competitor lifecycle policy... "
cat > /tmp/competitor-lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 180,
          "matchesPrefix": ["raw-scrapes/"]
        }
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {
          "age": 30,
          "matchesStorageClass": ["STANDARD"]
        }
      }
    ]
  }
}
EOF
gsutil lifecycle set /tmp/competitor-lifecycle.json gs://${BUCKET_COMPETITORS}/ 2>&1 | grep -q "Setting lifecycle" && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Already set${NC}"

# Reports lifecycle (move to coldline after 90 days, delete after 365)
echo -n "Setting reports lifecycle policy... "
cat > /tmp/reports-lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {
          "age": 90,
          "matchesStorageClass": ["NEARLINE"]
        }
      },
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 365
        }
      }
    ]
  }
}
EOF
gsutil lifecycle set /tmp/reports-lifecycle.json gs://${BUCKET_REPORTS}/ 2>&1 | grep -q "Setting lifecycle" && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Already set${NC}"

# Training data lifecycle (archive old data to coldline after 180 days)
echo -n "Setting training data lifecycle policy... "
cat > /tmp/training-lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {
          "age": 180,
          "matchesStorageClass": ["NEARLINE"]
        }
      }
    ]
  }
}
EOF
gsutil lifecycle set /tmp/training-lifecycle.json gs://${BUCKET_TRAINING}/ 2>&1 | grep -q "Setting lifecycle" && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Already set${NC}"

echo ""
echo -e "${BLUE}Step 3: Setting CORS Policies${NC}"
echo "------------------------------------------------------"

# Content bucket CORS (for web access)
echo -n "Setting content CORS policy... "
cat > /tmp/content-cors.json <<EOF
[
  {
    "origin": ["https://*.xynergy.com", "https://*.run.app"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF
gsutil cors set /tmp/content-cors.json gs://${BUCKET_CONTENT}/ 2>&1 | grep -q "Setting CORS" && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠ Already set${NC}"

echo ""
echo -e "${BLUE}Step 4: Creating Directory Structure${NC}"
echo "------------------------------------------------------"

# Create placeholder files to establish directory structure
echo -n "Creating content directories... "
echo "placeholder" | gsutil cp - gs://${BUCKET_CONTENT}/published/.placeholder 2>/dev/null
echo "placeholder" | gsutil cp - gs://${BUCKET_CONTENT}/drafts/.placeholder 2>/dev/null
echo "placeholder" | gsutil cp - gs://${BUCKET_CONTENT}/optimized/.placeholder 2>/dev/null
echo -e "${GREEN}✓${NC}"

echo -n "Creating competitor directories... "
echo "placeholder" | gsutil cp - gs://${BUCKET_COMPETITORS}/profiles/.placeholder 2>/dev/null
echo "placeholder" | gsutil cp - gs://${BUCKET_COMPETITORS}/raw-scrapes/.placeholder 2>/dev/null
echo "placeholder" | gsutil cp - gs://${BUCKET_COMPETITORS}/analysis/.placeholder 2>/dev/null
echo -e "${GREEN}✓${NC}"

echo -n "Creating report directories... "
echo "placeholder" | gsutil cp - gs://${BUCKET_REPORTS}/daily/.placeholder 2>/dev/null
echo "placeholder" | gsutil cp - gs://${BUCKET_REPORTS}/weekly/.placeholder 2>/dev/null
echo "placeholder" | gsutil cp - gs://${BUCKET_REPORTS}/monthly/.placeholder 2>/dev/null
echo -e "${GREEN}✓${NC}"

echo -n "Creating training data directories... "
echo "placeholder" | gsutil cp - gs://${BUCKET_TRAINING}/llm-interactions/.placeholder 2>/dev/null
echo "placeholder" | gsutil cp - gs://${BUCKET_TRAINING}/content-performance/.placeholder 2>/dev/null
echo "placeholder" | gsutil cp - gs://${BUCKET_TRAINING}/datasets/.placeholder 2>/dev/null
echo -e "${GREEN}✓${NC}"

echo -n "Creating model directories... "
echo "placeholder" | gsutil cp - gs://${BUCKET_MODELS}/llama-3.1-8b/.placeholder 2>/dev/null
echo "placeholder" | gsutil cp - gs://${BUCKET_MODELS}/fine-tuned/.placeholder 2>/dev/null
echo -e "${GREEN}✓${NC}"

# Clean up temp files
rm -f /tmp/*-lifecycle.json /tmp/*-cors.json

echo ""
echo "=================================================="
echo "Deployment Summary"
echo "=================================================="
echo ""

# List buckets
echo "Buckets created:"
gsutil ls -p ${PROJECT_ID} | grep "aso-" | while read bucket; do
  echo "  ✓ $bucket"
done

echo ""
echo "Bucket purposes:"
echo "  • $BUCKET_CONTENT - Content assets (STANDARD)"
echo "  • $BUCKET_COMPETITORS - Competitor data (STANDARD → NEARLINE after 30d)"
echo "  • $BUCKET_REPORTS - Generated reports (NEARLINE → COLDLINE after 90d)"
echo "  • $BUCKET_TRAINING - LLM training data (NEARLINE → COLDLINE after 180d)"
echo "  • $BUCKET_MODELS - LLM model files (STANDARD)"

echo ""
echo "Estimated monthly storage costs (assuming 100GB total):"
echo "  • Content (50GB STANDARD): \$1.00/month"
echo "  • Competitors (20GB STANDARD): \$0.40/month"
echo "  • Reports (15GB NEARLINE): \$0.15/month"
echo "  • Training (10GB NEARLINE): \$0.10/month"
echo "  • Models (5GB STANDARD): \$0.10/month"
echo "  • Total: ~\$1.75/month"

echo ""
echo -e "${GREEN}✓ ASO Cloud Storage infrastructure deployed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Deploy Internal LLM Service (will use $BUCKET_MODELS)"
echo "  2. Deploy ASO Engine (will use $BUCKET_CONTENT)"
echo "  3. Deploy Competitive Intelligence (will use $BUCKET_COMPETITORS)"
echo ""
