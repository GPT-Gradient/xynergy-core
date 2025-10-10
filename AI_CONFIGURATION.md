# AI Configuration Guide

## Overview

The Xynergy platform now uses an intelligent AI routing system that prioritizes Abacus AI first, then falls back to OpenAI, and finally to internal AI models. This document outlines the required API keys and configuration.

## AI Routing Strategy

```
Request → ai-routing-engine → ai-providers → Abacus AI (primary)
                                         ↓ (if unavailable)
                                         → OpenAI (fallback)
                                         ↓ (if unavailable)
                                         → internal-ai-service (final fallback)
```

## Required API Keys

### 1. Abacus AI (Primary Provider)

**Environment Variable:** `ABACUS_API_KEY`

**How to obtain:**
1. Sign up at [Abacus AI](https://abacus.ai)
2. Navigate to API settings in your dashboard
3. Generate a new API key
4. Copy the key (format: `abacus_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

**Configuration:**
```bash
export ABACUS_API_KEY="your_abacus_api_key_here"
```

**Cost:** ~$0.015 per request (lower than OpenAI)

### 2. OpenAI (Fallback Provider)

**Environment Variable:** `OPENAI_API_KEY`

**How to obtain:**
1. Sign up at [OpenAI Platform](https://platform.openai.com)
2. Navigate to API Keys section
3. Create a new secret key
4. Copy the key (format: `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

**Configuration:**
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

**Cost:** ~$0.025 per request (higher than Abacus)

## Service Configuration

### ai-providers Service

The `ai-providers` service requires both API keys to function optimally:

```bash
# Docker run example
docker run -d \
  -e ABACUS_API_KEY="your_abacus_key" \
  -e OPENAI_API_KEY="your_openai_key" \
  -p 8080:8080 \
  xynergy-ai-providers

# Kubernetes deployment
apiVersion: v1
kind: Secret
metadata:
  name: ai-provider-secrets
data:
  abacus-api-key: <base64-encoded-key>
  openai-api-key: <base64-encoded-key>
```

### GCP Cloud Run Deployment

When deploying to Cloud Run, set environment variables:

```bash
gcloud run deploy xynergy-ai-providers \
  --image gcr.io/xynergy-dev-1757909467/ai-providers \
  --set-env-vars ABACUS_API_KEY="your_abacus_key",OPENAI_API_KEY="your_openai_key" \
  --region us-central1
```

## Configuration Validation

### Health Check Endpoints

**Check provider status:**
```bash
curl https://xynergy-ai-providers-*.run.app/api/providers/status
```

**Expected response:**
```json
{
  "timestamp": "2025-01-XX...",
  "providers": {
    "abacus": {
      "available": true,
      "configured": true,
      "status_code": 200
    },
    "openai": {
      "available": true,
      "configured": true,
      "status_code": 200
    }
  },
  "total_available": 2
}
```

### Test AI Generation

**Test routing:**
```bash
curl -X POST https://xynergy-ai-routing-engine-*.run.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a brief introduction to AI routing",
    "max_tokens": 256
  }'
```

**Expected response:**
```json
{
  "success": true,
  "provider": "abacus",
  "text": "AI routing is a technique...",
  "model": "abacus-ai-model",
  "cost": 0.015,
  "routed_via": "ai-routing-engine"
}
```

## Fallback Behavior

### Scenario 1: Both APIs Configured
- Primary: Abacus AI
- Fallback: OpenAI
- Final: Internal AI models

### Scenario 2: Only OpenAI Configured
- Primary: OpenAI
- Fallback: Internal AI models

### Scenario 3: No APIs Configured
- All requests route to internal AI models
- Cost: $0.001 per request
- Models: Llama 3.1, Code Llama, Mistral

## Cost Optimization

### Current Routing Costs
- **Abacus AI**: $0.015 per request (40% savings vs OpenAI)
- **OpenAI**: $0.025 per request
- **Internal**: $0.001 per request (96% savings vs OpenAI)

### Monthly Cost Estimates (10,000 requests)
- **All Abacus**: $150/month
- **All OpenAI**: $250/month
- **Mixed (60% Abacus, 30% OpenAI, 10% Internal)**: ~$166/month
- **All Internal**: $10/month

## Security Best Practices

### API Key Management
1. **Never commit API keys to version control**
2. **Use environment variables or secret management systems**
3. **Rotate keys regularly (quarterly)**
4. **Monitor usage for unexpected spikes**

### GCP Secret Manager Integration
```bash
# Store secrets
gcloud secrets create abacus-api-key --data-file=abacus_key.txt
gcloud secrets create openai-api-key --data-file=openai_key.txt

# Grant access to service account
gcloud secrets add-iam-policy-binding abacus-api-key \
  --member="serviceAccount:xynergy-platform-sa@xynergy-dev-1757909467.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Troubleshooting

### Common Issues

1. **"Abacus API key not configured" error**
   - Verify `ABACUS_API_KEY` environment variable is set
   - Check key format and validity

2. **"OpenAI API key not configured" error**
   - Verify `OPENAI_API_KEY` environment variable is set
   - Ensure key starts with `sk-`

3. **"All AI providers unavailable" error**
   - Check network connectivity
   - Verify API keys are valid and have sufficient credits
   - Check provider status endpoints

4. **High costs**
   - Review routing logic in `ai-routing-engine`
   - Consider adjusting complex_indicators in routing code
   - Monitor usage patterns in GCP billing

### Monitoring and Alerts

Set up alerts for:
- API key expiration
- Unusual usage spikes
- Provider availability issues
- Cost thresholds

## Support

For configuration issues:
1. Check service logs in GCP Cloud Run
2. Verify environment variables are properly set
3. Test individual provider endpoints
4. Review routing logic in `ai-routing-engine/main.py`

## Next Steps

After configuring API keys:
1. Deploy updated services to GCP
2. Test routing functionality
3. Monitor costs and performance
4. Adjust routing logic as needed
5. Set up monitoring and alerts