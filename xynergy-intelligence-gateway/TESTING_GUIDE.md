# Intelligence Gateway Testing Guide

Comprehensive testing guide for the Xynergy Intelligence Gateway service.

## Table of Contents
1. [Local Testing Setup](#local-testing-setup)
2. [API Endpoint Testing](#api-endpoint-testing)
3. [Integration Testing](#integration-testing)
4. [Load Testing](#load-testing)
5. [Deployment Verification](#deployment-verification)
6. [Troubleshooting](#troubleshooting)

## Local Testing Setup

### Prerequisites
- Python 3.11+
- Docker (optional)
- curl or Postman
- gcloud CLI (for cloud testing)

### Environment Setup

1. **Install Dependencies**
```bash
cd xynergy-intelligence-gateway
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment Variables**

Create `.env.local` file:
```bash
GOOGLE_CLOUD_PROJECT=xynergy-dev-1757909467
ASO_ENGINE_URL=https://aso-engine-vgjxy554mq-uc.a.run.app
SENDGRID_API_KEY=your_test_sendgrid_api_key
NOTIFICATION_EMAIL=test@clearforge.ai
ENVIRONMENT=development

# Optional SMTP fallback
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=test@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=test@gmail.com
```

3. **Load Environment Variables**
```bash
export $(cat .env.local | xargs)
```

4. **Start Local Server**
```bash
uvicorn app.main:app --reload --port 8080
```

Server should start at `http://localhost:8080`

### Docker Testing

1. **Build Image**
```bash
docker build -t xynergy-intelligence-gateway:test .
```

2. **Run Container**
```bash
docker run -p 8080:8080 \
  --env-file .env.local \
  xynergy-intelligence-gateway:test
```

3. **Test Health Check**
```bash
curl http://localhost:8080/health
```

## API Endpoint Testing

### 1. Health Check Endpoint

**Test Basic Health**
```bash
curl -X GET "http://localhost:8080/health" | jq
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "xynergy-intelligence-gateway",
  "version": "1.0.0",
  "dependencies": {
    "aso_engine": "healthy",
    "firestore": "healthy",
    "email_service": "healthy"
  }
}
```

**Validation Checklist:**
- [ ] Status is "healthy"
- [ ] Service name is correct
- [ ] All dependencies show "healthy"
- [ ] Response time < 1 second

### 2. ASO Intelligence Endpoints

#### Trending Keywords

**Test Default Request**
```bash
curl -X GET "http://localhost:8080/v1/aso/trending-keywords" | jq
```

**Test with Parameters**
```bash
curl -X GET "http://localhost:8080/v1/aso/trending-keywords?limit=10&tenant_id=clearforge" | jq
```

**Test Cache Behavior**
```bash
# First request (cache miss)
curl -X GET "http://localhost:8080/v1/aso/trending-keywords" \
  -w "\nTime: %{time_total}s\n" | jq '.cached'

# Second request within 5 minutes (cache hit)
curl -X GET "http://localhost:8080/v1/aso/trending-keywords" \
  -w "\nTime: %{time_total}s\n" | jq '.cached'
```

**Expected Behavior:**
- First request: `"cached": false`, ~500-1000ms
- Second request: `"cached": true`, ~50-100ms

**Validation Checklist:**
- [ ] Returns array of keywords
- [ ] Each keyword has: keyword, search_volume, trend, velocity, rank
- [ ] Limit parameter works correctly
- [ ] Cache flag indicates caching status
- [ ] Response time improved on cached requests

#### Keyword Rankings

**Test Request**
```bash
curl -X GET "http://localhost:8080/v1/aso/keyword-rankings?limit=20" | jq
```

**Expected Response Structure:**
```json
{
  "rankings": [
    {
      "keyword": "business automation",
      "current_rank": 3,
      "previous_rank": 5,
      "trend": "improving",
      "rank_change": 2,
      "last_updated": "2025-10-09T10:30:00Z"
    }
  ],
  "total": 20,
  "cached": false
}
```

**Validation Checklist:**
- [ ] Returns rankings array
- [ ] Trend calculation is correct (current vs previous)
- [ ] rank_change matches the difference
- [ ] last_updated is recent timestamp

#### Content Performance

**Test Request**
```bash
curl -X GET "http://localhost:8080/v1/aso/content-performance?period_days=30" | jq
```

**Expected Response Structure:**
```json
{
  "period_days": 30,
  "performance": {
    "titles": [...],
    "descriptions": [...],
    "keywords": [...]
  },
  "cached": false
}
```

**Validation Checklist:**
- [ ] Period parameter reflects in response
- [ ] Performance includes titles, descriptions, keywords
- [ ] Metrics include impressions, clicks, ctr, conversions
- [ ] CTR calculation is correct (clicks/impressions * 100)

### 3. Lead Capture Endpoints

#### Beta Application Submission

**Test Valid Submission**
```bash
curl -X POST "http://localhost:8080/v1/beta/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "Acme Test Corp",
    "industry": "E-commerce",
    "size": "11-50",
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+1-555-0123",
    "challenges": "We need to automate our marketing workflows and reduce manual tasks across our team.",
    "whyRightFit": "Our team is tech-savvy and eager to adopt AI tools to improve efficiency.",
    "timeframe": "1-3 months"
  }' | jq
```

**Expected Response:**
```json
{
  "application_id": "beta_1696857600_abc123",
  "status": "submitted",
  "submitted_at": "2025-10-09T10:30:00Z",
  "confirmation_sent": true,
  "message": "Application submitted successfully"
}
```

**Test Invalid Email**
```bash
curl -X POST "http://localhost:8080/v1/beta/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "Acme Corp",
    "industry": "E-commerce",
    "size": "11-50",
    "name": "Test User",
    "email": "invalid-email",
    "challenges": "Test challenge text that is long enough.",
    "whyRightFit": "Test fit text that is long enough."
  }'
```

**Expected Response:** 422 Validation Error

**Test Missing Required Fields**
```bash
curl -X POST "http://localhost:8080/v1/beta/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "Acme Corp"
  }'
```

**Expected Response:** 422 Validation Error with field details

**Test String Length Validation**
```bash
# Too short businessName (min 2 chars)
curl -X POST "http://localhost:8080/v1/beta/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "A",
    "industry": "Tech",
    "name": "Test",
    "email": "test@example.com",
    "challenges": "Short text",
    "whyRightFit": "Also short"
  }'
```

**Validation Checklist:**
- [ ] Valid submission returns 200 with application_id
- [ ] Application ID follows format: `beta_{timestamp}_{random}`
- [ ] confirmation_sent is true when email succeeds
- [ ] Invalid email returns 422 error
- [ ] Missing required fields return 422 with details
- [ ] String length validation works (min/max)
- [ ] Firestore document created successfully
- [ ] Emails sent (check inbox and logs)

**Verify Firestore Storage**
```bash
# List recent beta applications
gcloud firestore query \
  --collection=beta_applications \
  --order-by=submitted_at:desc \
  --limit=5
```

#### Contact Form Submission

**Test Valid Contact Submission**
```bash
curl -X POST "http://localhost:8080/v1/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "contactType": "sales",
    "subject": "Pricing inquiry for 100 users",
    "message": "I would like to discuss pricing options for our team of 100 users. Please provide details."
  }' | jq
```

**Expected Response:**
```json
{
  "ticket_id": "contact_1696857600_xyz789",
  "status": "submitted",
  "submitted_at": "2025-10-09T10:30:00Z",
  "confirmation_sent": true,
  "estimated_response": "We'll respond within 24 hours"
}
```

**Test All Contact Types**
```bash
for type in support sales partnership feedback; do
  echo "Testing contact type: $type"
  curl -X POST "http://localhost:8080/v1/contact" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"Test User\",
      \"email\": \"test@example.com\",
      \"contactType\": \"$type\",
      \"subject\": \"Test subject for $type\",
      \"message\": \"This is a test message for contact type $type.\"
    }" | jq '.ticket_id'
  sleep 1
done
```

**Test Invalid Contact Type**
```bash
curl -X POST "http://localhost:8080/v1/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "contactType": "invalid_type",
    "subject": "Test",
    "message": "Test message"
  }'
```

**Expected Response:** 422 Validation Error

**Validation Checklist:**
- [ ] Valid submission returns 200 with ticket_id
- [ ] Ticket ID follows format: `contact_{timestamp}_{random}`
- [ ] All contact types (support, sales, partnership, feedback) work
- [ ] Invalid contact type returns 422
- [ ] confirmation_sent is true when email succeeds
- [ ] Firestore document created
- [ ] Appropriate emails sent based on contact type

### 4. Dashboard Metrics

**Test Metrics Endpoint**
```bash
curl -X GET "http://localhost:8080/v1/dashboard/metrics" | jq
```

**Expected Response Structure:**
```json
{
  "aso": {
    "total_keywords": 450,
    "trending_keywords": 45,
    "avg_rank": 12.3,
    "rank_improvements": 23
  },
  "leads": {
    "beta_applications_total": 127,
    "beta_applications_30d": 15,
    "contact_submissions_total": 342,
    "contact_submissions_30d": 28
  },
  "system": {
    "uptime_percentage": 99.9,
    "avg_response_time_ms": 145,
    "cache_hit_rate": 78.5
  },
  "as_of": "2025-10-09T10:30:00Z"
}
```

**Validation Checklist:**
- [ ] All sections present (aso, leads, system)
- [ ] Numeric values are reasonable
- [ ] as_of timestamp is current
- [ ] Response time < 1 second

### 5. Rate Limiting Testing

**Test ASO Endpoint Rate Limit (60/minute)**
```bash
# Send 65 requests rapidly
for i in {1..65}; do
  echo "Request $i"
  curl -X GET "http://localhost:8080/v1/aso/trending-keywords" \
    -w "\nHTTP Status: %{http_code}\n" \
    -s -o /dev/null
  sleep 0.5
done
```

**Expected Behavior:**
- First 60 requests: HTTP 200
- Requests 61-65: HTTP 429 (Rate limit exceeded)

**Test Beta Application Rate Limit (5/minute)**
```bash
# Send 7 requests rapidly
for i in {1..7}; do
  echo "Request $i"
  curl -X POST "http://localhost:8080/v1/beta/apply" \
    -H "Content-Type: application/json" \
    -d '{
      "businessName": "Test Corp '$i'",
      "industry": "Tech",
      "name": "Test",
      "email": "test'$i'@example.com",
      "challenges": "Testing rate limits with request number '$i'.",
      "whyRightFit": "Rate limit testing request number '$i'."
    }' \
    -w "\nHTTP Status: %{http_code}\n" \
    -s -o /dev/null
  sleep 1
done
```

**Expected Behavior:**
- First 5 requests: HTTP 200
- Requests 6-7: HTTP 429

**Test Contact Form Rate Limit (10/minute)**
```bash
# Send 12 requests rapidly
for i in {1..12}; do
  echo "Request $i"
  curl -X POST "http://localhost:8080/v1/contact" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Test User",
      "email": "test@example.com",
      "contactType": "support",
      "subject": "Test '$i'",
      "message": "Rate limit test message number '$i'."
    }' \
    -w "\nHTTP Status: %{http_code}\n" \
    -s -o /dev/null
  sleep 0.5
done
```

**Expected Behavior:**
- First 10 requests: HTTP 200
- Requests 11-12: HTTP 429

**Validation Checklist:**
- [ ] ASO endpoints enforce 60/minute limit
- [ ] Beta application enforces 5/minute limit
- [ ] Contact form enforces 10/minute limit
- [ ] Rate limit resets after 1 minute
- [ ] 429 response includes Retry-After header

### 6. Cache Statistics

**Test Cache Stats Endpoint**
```bash
# Make some cached requests first
curl "http://localhost:8080/v1/aso/trending-keywords" > /dev/null
curl "http://localhost:8080/v1/aso/trending-keywords" > /dev/null
curl "http://localhost:8080/v1/aso/keyword-rankings" > /dev/null
curl "http://localhost:8080/v1/aso/keyword-rankings" > /dev/null

# Check cache statistics
curl "http://localhost:8080/internal/cache-stats" | jq
```

**Expected Response:**
```json
{
  "hits": 2,
  "misses": 2,
  "hit_rate": 50.0,
  "evictions": 0,
  "current_size": 2
}
```

**Validation Checklist:**
- [ ] Hit rate calculation is correct: (hits / (hits + misses)) * 100
- [ ] Current size reflects number of cached items
- [ ] Stats update in real-time

### 7. Circuit Breaker Testing

**Simulate ASO Engine Failure**

1. **Stop ASO Engine (or set invalid URL)**
```bash
export ASO_ENGINE_URL=https://invalid-url-that-does-not-exist.run.app
# Restart server
```

2. **Make Requests to Trigger Circuit Breaker**
```bash
# First 5 requests will fail and increment failure counter
for i in {1..5}; do
  echo "Request $i"
  curl "http://localhost:8080/v1/aso/trending-keywords" | jq '.error'
  sleep 1
done
```

3. **Circuit Should Open**
```bash
# 6th request should fail immediately (circuit open)
curl "http://localhost:8080/v1/aso/trending-keywords" | jq
```

**Expected Response:**
```json
{
  "error": "aso_engine_circuit_open",
  "message": "ASO Engine is currently unavailable. Using cached data.",
  "cached_data": [...]
}
```

4. **Wait for Circuit Reset (60 seconds)**
```bash
sleep 60
curl "http://localhost:8080/v1/aso/trending-keywords" | jq
```

**Validation Checklist:**
- [ ] Circuit opens after 5 consecutive failures
- [ ] Cached data returned when circuit is open
- [ ] Circuit resets after 60 second timeout
- [ ] Graceful degradation (no 500 errors)

## Integration Testing

### End-to-End Beta Application Flow

**Test Complete Application Workflow**

```bash
#!/bin/bash
# Save as test_beta_flow.sh

echo "=== Beta Application E2E Test ==="

# 1. Submit application
echo "1. Submitting beta application..."
RESPONSE=$(curl -s -X POST "http://localhost:8080/v1/beta/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "E2E Test Corp",
    "industry": "SaaS",
    "size": "51-200",
    "name": "Integration Test",
    "email": "e2e-test@example.com",
    "phone": "+1-555-9999",
    "challenges": "We need comprehensive automation for our growing team.",
    "whyRightFit": "We have technical expertise and clear use cases.",
    "timeframe": "Immediately"
  }')

APPLICATION_ID=$(echo $RESPONSE | jq -r '.application_id')
echo "Application ID: $APPLICATION_ID"

# 2. Verify Firestore storage
echo "2. Verifying Firestore storage..."
gcloud firestore query \
  --collection=beta_applications \
  --filter="application_id=$APPLICATION_ID" \
  --limit=1

# 3. Check email logs
echo "3. Checking email logs..."
gcloud logging read "resource.type=cloud_run_revision \
  AND jsonPayload.application_id=$APPLICATION_ID \
  AND jsonPayload.event=email_sent" \
  --limit=10 \
  --format=json

# 4. Verify dashboard metrics updated
echo "4. Verifying dashboard metrics..."
curl -s "http://localhost:8080/v1/dashboard/metrics" | jq '.leads'

echo "=== E2E Test Complete ==="
```

**Run Test:**
```bash
chmod +x test_beta_flow.sh
./test_beta_flow.sh
```

### ASO Data Integration Test

**Test ASO Engine Connection**

```bash
#!/bin/bash
# Save as test_aso_integration.sh

echo "=== ASO Integration Test ==="

# 1. Test trending keywords
echo "1. Fetching trending keywords..."
curl -s "http://localhost:8080/v1/aso/trending-keywords?limit=5" | jq

# 2. Test keyword rankings
echo "2. Fetching keyword rankings..."
curl -s "http://localhost:8080/v1/aso/keyword-rankings?limit=5" | jq

# 3. Test content performance
echo "3. Fetching content performance..."
curl -s "http://localhost:8080/v1/aso/content-performance?period_days=7" | jq

# 4. Test cache behavior
echo "4. Testing cache (second request should be cached)..."
curl -s "http://localhost:8080/v1/aso/trending-keywords" | jq '.cached'
sleep 1
curl -s "http://localhost:8080/v1/aso/trending-keywords" | jq '.cached'

# 5. Check cache stats
echo "5. Cache statistics..."
curl -s "http://localhost:8080/internal/cache-stats" | jq

echo "=== Integration Test Complete ==="
```

**Run Test:**
```bash
chmod +x test_aso_integration.sh
./test_aso_integration.sh
```

## Load Testing

### Using Apache Bench (ab)

**Install Apache Bench**
```bash
# macOS
brew install httpd

# Ubuntu/Debian
sudo apt-get install apache2-utils
```

**Test Health Endpoint**
```bash
ab -n 1000 -c 10 http://localhost:8080/health
```

**Test ASO Endpoint**
```bash
ab -n 500 -c 5 "http://localhost:8080/v1/aso/trending-keywords"
```

**Expected Results:**
- Requests per second: > 50
- Mean response time: < 200ms
- Failed requests: 0 (excluding rate limited)

### Using hey

**Install hey**
```bash
go install github.com/rakyll/hey@latest
```

**Load Test Health Endpoint**
```bash
hey -n 1000 -c 10 http://localhost:8080/health
```

**Load Test with POST Requests**
```bash
echo '{
  "name": "Load Test",
  "email": "loadtest@example.com",
  "contactType": "support",
  "subject": "Load test",
  "message": "This is a load test message."
}' > contact_payload.json

hey -n 100 -c 5 -m POST \
  -H "Content-Type: application/json" \
  -D contact_payload.json \
  http://localhost:8080/v1/contact
```

**Validation Checklist:**
- [ ] No failed requests (except rate limits)
- [ ] Response times remain consistent under load
- [ ] Memory usage stays within limits
- [ ] No connection errors

## Deployment Verification

### Pre-Deployment Checklist

**Code Quality**
- [ ] All unit tests pass (if implemented)
- [ ] No syntax errors
- [ ] Dependencies listed in requirements.txt
- [ ] Dockerfile builds successfully
- [ ] Environment variables documented

**Configuration**
- [ ] ASO_ENGINE_URL is correct
- [ ] SENDGRID_API_KEY is set
- [ ] NOTIFICATION_EMAIL is configured
- [ ] CORS origins are correct
- [ ] Rate limits are appropriate

**Security**
- [ ] No hardcoded secrets
- [ ] CORS not set to allow_origins=["*"]
- [ ] Input validation on all endpoints
- [ ] Rate limiting enabled
- [ ] HTTPS enforced in production

### Post-Deployment Verification

**1. Deploy to Cloud Run**
```bash
./deploy.sh
```

**2. Get Service URL**
```bash
SERVICE_URL=$(gcloud run services describe xynergy-intelligence-gateway \
  --region=us-central1 \
  --project=xynergy-dev-1757909467 \
  --format='value(status.url)')

echo "Service URL: $SERVICE_URL"
```

**3. Test Health Endpoint**
```bash
curl "$SERVICE_URL/health" | jq
```

**4. Test ASO Endpoints**
```bash
# Trending keywords
curl "$SERVICE_URL/v1/aso/trending-keywords?limit=5" | jq

# Keyword rankings
curl "$SERVICE_URL/v1/aso/keyword-rankings?limit=5" | jq

# Content performance
curl "$SERVICE_URL/v1/aso/content-performance" | jq
```

**5. Test Lead Capture**
```bash
# Beta application
curl -X POST "$SERVICE_URL/v1/beta/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "Production Test Corp",
    "industry": "Technology",
    "size": "11-50",
    "name": "Prod Test",
    "email": "prodtest@example.com",
    "challenges": "Testing production deployment of beta application endpoint.",
    "whyRightFit": "Verifying that all integrations work correctly in production."
  }' | jq

# Contact form
curl -X POST "$SERVICE_URL/v1/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prod Test",
    "email": "prodtest@example.com",
    "contactType": "support",
    "subject": "Production deployment test",
    "message": "Testing contact form submission in production environment."
  }' | jq
```

**6. Verify Logs**
```bash
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=xynergy-intelligence-gateway" \
  --limit=50 \
  --format=json
```

**7. Check Metrics**
```bash
# Request count
gcloud monitoring time-series list \
  --filter="resource.type=cloud_run_revision \
    AND resource.labels.service_name=xynergy-intelligence-gateway" \
  --format=json

# Or view in console
echo "View metrics: https://console.cloud.google.com/run/detail/us-central1/xynergy-intelligence-gateway/metrics"
```

**8. Test Rate Limiting**
```bash
# Should get rate limited after 5 requests
for i in {1..7}; do
  curl -X POST "$SERVICE_URL/v1/beta/apply" \
    -H "Content-Type: application/json" \
    -d "{
      \"businessName\": \"Rate Test $i\",
      \"industry\": \"Tech\",
      \"name\": \"Test\",
      \"email\": \"test$i@example.com\",
      \"challenges\": \"Testing rate limiting in production environment.\",
      \"whyRightFit\": \"Verifying security controls work correctly.\"
    }" \
    -w "\nHTTP Status: %{http_code}\n"
  sleep 2
done
```

**9. Test Circuit Breaker (if ASO Engine is down)**
```bash
curl "$SERVICE_URL/v1/aso/trending-keywords" | jq
```

**10. Verify Email Delivery**
- [ ] Check inbox for beta application confirmation
- [ ] Check team inbox for notification
- [ ] Verify email formatting and content

### Performance Benchmarks

**Expected Performance (Production):**
- Health endpoint: < 100ms (p95)
- ASO endpoints (cached): < 150ms (p95)
- ASO endpoints (uncached): < 1000ms (p95)
- Lead capture: < 500ms (p95)
- Dashboard metrics: < 300ms (p95)

**Monitor Over Time:**
```bash
# Run load test against production
hey -n 1000 -c 10 "$SERVICE_URL/v1/aso/trending-keywords"
```

## Troubleshooting

### Common Issues

**Issue: Health check fails**
```bash
# Check service logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=xynergy-intelligence-gateway \
  AND severity=ERROR" \
  --limit=20

# Check service status
gcloud run services describe xynergy-intelligence-gateway \
  --region=us-central1 \
  --format=yaml
```

**Issue: ASO endpoints return errors**
```bash
# Test ASO Engine directly
curl "https://aso-engine-vgjxy554mq-uc.a.run.app/health"

# Check circuit breaker status
curl "$SERVICE_URL/internal/cache-stats"
```

**Issue: Emails not sending**
```bash
# Check email service logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=xynergy-intelligence-gateway \
  AND jsonPayload.event=email_send_failed" \
  --limit=20

# Verify SendGrid API key
echo $SENDGRID_API_KEY | cut -c1-10  # Should show first 10 chars
```

**Issue: Rate limiting not working**
```bash
# Check slowapi configuration in logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=xynergy-intelligence-gateway \
  AND jsonPayload.message:'rate_limit'" \
  --limit=20
```

**Issue: Firestore permission denied**
```bash
# Check service account permissions
gcloud projects get-iam-policy xynergy-dev-1757909467 \
  --flatten="bindings[].members" \
  --filter="bindings.members:*compute@developer.gserviceaccount.com"

# Grant Firestore access if needed
gcloud projects add-iam-policy-binding xynergy-dev-1757909467 \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### Debug Mode

**Enable Verbose Logging**

Modify `app/main.py` temporarily:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Redeploy and check logs:
```bash
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=xynergy-intelligence-gateway" \
  --limit=100
```

## Test Coverage Summary

### Functional Tests
- [x] Health check endpoint
- [x] ASO trending keywords
- [x] ASO keyword rankings
- [x] ASO content performance
- [x] Beta application submission (valid)
- [x] Beta application submission (invalid)
- [x] Contact form submission (all types)
- [x] Dashboard metrics
- [x] Cache statistics

### Non-Functional Tests
- [x] Rate limiting (all endpoints)
- [x] Circuit breaker behavior
- [x] Cache hit/miss behavior
- [x] Input validation
- [x] Email delivery
- [x] Firestore storage
- [x] Error handling
- [x] Load testing
- [x] Deployment verification

### Integration Tests
- [x] ASO Engine integration
- [x] Firestore integration
- [x] SendGrid integration
- [x] SMTP fallback
- [x] End-to-end workflows

## Automated Testing Script

**Complete Test Suite**

Save as `run_all_tests.sh`:
```bash
#!/bin/bash
set -e

BASE_URL=${1:-"http://localhost:8080"}
echo "Testing against: $BASE_URL"

echo "=== 1. Health Check ==="
curl -f "$BASE_URL/health" | jq

echo -e "\n=== 2. ASO Endpoints ==="
curl -f "$BASE_URL/v1/aso/trending-keywords?limit=5" | jq '.total'
curl -f "$BASE_URL/v1/aso/keyword-rankings?limit=5" | jq '.total'
curl -f "$BASE_URL/v1/aso/content-performance" | jq '.period_days'

echo -e "\n=== 3. Lead Capture ==="
curl -f -X POST "$BASE_URL/v1/beta/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "Automated Test Corp",
    "industry": "Technology",
    "name": "Test Bot",
    "email": "test@example.com",
    "challenges": "Automated testing of beta application endpoint functionality.",
    "whyRightFit": "Ensuring all validation and processing works correctly."
  }' | jq '.application_id'

curl -f -X POST "$BASE_URL/v1/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Bot",
    "email": "test@example.com",
    "contactType": "support",
    "subject": "Automated test",
    "message": "Testing contact form submission endpoint."
  }' | jq '.ticket_id'

echo -e "\n=== 4. Dashboard Metrics ==="
curl -f "$BASE_URL/v1/dashboard/metrics" | jq '.aso.total_keywords'

echo -e "\n=== 5. Cache Statistics ==="
curl -f "$BASE_URL/internal/cache-stats" | jq '.hit_rate'

echo -e "\n=== All Tests Passed ==="
```

**Run Test Suite:**
```bash
chmod +x run_all_tests.sh

# Test locally
./run_all_tests.sh http://localhost:8080

# Test production
./run_all_tests.sh https://xynergy-intelligence-gateway-xxx.run.app
```

## Continuous Monitoring

**Set Up Monitoring Dashboard**

Create monitoring queries for:
1. Request latency (p50, p95, p99)
2. Error rate
3. Request count by endpoint
4. Cache hit rate
5. Circuit breaker events
6. Rate limit violations

**Example Cloud Monitoring Query:**
```
resource.type="cloud_run_revision"
resource.labels.service_name="xynergy-intelligence-gateway"
metric.type="run.googleapis.com/request_latencies"
```

**Alert Policies:**
1. Error rate > 5% for 5 minutes
2. p95 latency > 2 seconds for 5 minutes
3. Circuit breaker open for > 5 minutes
4. Email delivery failures > 10% for 10 minutes

---

For additional support, see README.md or contact the team.
