# Xynergy Intelligence Gateway

Public-facing API gateway that provides read-only access to Xynergy platform insights and handles lead capture for ClearForge.ai.

## Overview

The Intelligence Gateway is a lightweight aggregation service that sits between the ClearForge.ai public website and the internal Xynergy microservices platform. It provides:

- **ASO Intelligence**: Public read-only access to trending keywords, rankings, and content performance
- **Lead Capture**: Beta application and contact form submission with email notifications
- **Dashboard Metrics**: Real-time platform health and activity metrics
- **Rate Limiting**: IP-based throttling to prevent abuse
- **Caching**: In-memory cache with TTL for performance optimization
- **Circuit Breaker**: Fault tolerance for downstream service calls

## Architecture

```
┌─────────────────┐
│ ClearForge.ai   │
│ Website         │
└────────┬────────┘
         │
         │ HTTPS
         ▼
┌─────────────────┐
│ Intelligence    │
│ Gateway         │
│ (This Service)  │
└────┬────────┬───┘
     │        │
     │        └──────────────┐
     │                       │
     ▼                       ▼
┌─────────────┐    ┌─────────────────┐
│ ASO Engine  │    │ Firestore       │
│ (Internal)  │    │ - Beta Apps     │
└─────────────┘    │ - Contact Forms │
                   └─────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ SendGrid/SMTP   │
                   │ Email Service   │
                   └─────────────────┘
```

## Features

### 1. ASO Intelligence Endpoints

Aggregates and exposes App Store Optimization data from the internal ASO Engine:

- **Trending Keywords**: Top performing keywords with search volume and velocity
- **Keyword Rankings**: Current rankings with trend analysis
- **Content Performance**: Title, description, and keyword performance metrics

All ASO endpoints support tenant isolation (defaults to `clearforge`).

### 2. Lead Capture System

- **Beta Applications**: Structured intake for beta program applicants
  - Business information validation
  - Industry and use case capture
  - Automatic confirmation emails
  - Internal team notifications
  - Firestore persistence with timestamps

- **Contact Forms**: General inquiry handling
  - Contact type categorization (support, sales, partnership, feedback)
  - Subject and message validation
  - Ticket ID generation
  - Email confirmations and notifications

### 3. Dashboard Integration

Provides real-time metrics for public dashboard display:
- ASO performance indicators
- Lead capture statistics
- System health status

### 4. Built-in Protection

- **Rate Limiting**: IP-based throttling (slowapi)
  - 60/min for ASO endpoints
  - 5/min for beta applications
  - 10/min for contact forms
  - 30/min for dashboard metrics

- **Circuit Breaker**: Protects against ASO Engine failures
  - 5 failure threshold
  - 60 second timeout
  - Graceful degradation with cached data

- **Caching**: In-memory cache with 5-minute TTL
  - Reduces ASO Engine load
  - Improves response times
  - Cache statistics endpoint

- **CORS**: Configured for clearforge.ai domain
  - Supports credentials
  - Allows standard headers
  - GET, POST, OPTIONS methods

## API Endpoints

### Health & Status

#### `GET /health`
Health check endpoint with dependency status.

**Response:**
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

### ASO Intelligence

#### `GET /v1/aso/trending-keywords`
Get trending keywords with performance metrics.

**Parameters:**
- `limit` (optional): Number of keywords to return (default: 20, max: 100)
- `tenant_id` (optional): Tenant identifier (default: "clearforge")

**Response:**
```json
{
  "keywords": [
    {
      "keyword": "ai automation",
      "search_volume": 45000,
      "trend": "rising",
      "velocity": 23.5,
      "rank": 1,
      "last_updated": "2025-10-09T10:30:00Z"
    }
  ],
  "total": 20,
  "cached": false
}
```

**Rate Limit:** 60 requests/minute per IP

#### `GET /v1/aso/keyword-rankings`
Get keyword ranking data with trend analysis.

**Parameters:**
- `limit` (optional): Number of rankings to return (default: 50, max: 200)
- `tenant_id` (optional): Tenant identifier (default: "clearforge")

**Response:**
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
  "total": 50,
  "cached": false
}
```

**Rate Limit:** 60 requests/minute per IP

#### `GET /v1/aso/content-performance`
Get content performance metrics for titles, descriptions, and keywords.

**Parameters:**
- `period_days` (optional): Analysis period in days (default: 30, max: 90)
- `tenant_id` (optional): Tenant identifier (default: "clearforge")

**Response:**
```json
{
  "period_days": 30,
  "performance": {
    "titles": [
      {
        "title": "AI-Powered Business Automation",
        "impressions": 125000,
        "clicks": 8500,
        "ctr": 6.8,
        "conversions": 450
      }
    ],
    "descriptions": [...],
    "keywords": [...]
  },
  "cached": false
}
```

**Rate Limit:** 60 requests/minute per IP

### Lead Capture

#### `POST /v1/beta/apply`
Submit beta program application.

**Request Body:**
```json
{
  "businessName": "Acme Corp",
  "industry": "E-commerce",
  "size": "11-50",
  "name": "John Doe",
  "email": "john@acme.com",
  "phone": "+1-555-0123",
  "challenges": "We need to automate our marketing workflows...",
  "whyRightFit": "Our team is tech-savvy and eager to adopt AI...",
  "timeframe": "1-3 months"
}
```

**Response:**
```json
{
  "application_id": "beta_1696857600_abc123",
  "status": "submitted",
  "submitted_at": "2025-10-09T10:30:00Z",
  "confirmation_sent": true,
  "message": "Application submitted successfully"
}
```

**Rate Limit:** 5 requests/minute per IP

**Emails Sent:**
1. Confirmation to applicant
2. Notification to Xynergy team

#### `POST /v1/contact`
Submit contact form inquiry.

**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "contactType": "sales",
  "subject": "Pricing inquiry",
  "message": "I'd like to discuss pricing for 100 users..."
}
```

**Response:**
```json
{
  "ticket_id": "contact_1696857600_xyz789",
  "status": "submitted",
  "submitted_at": "2025-10-09T10:30:00Z",
  "confirmation_sent": true,
  "estimated_response": "We'll respond within 24 hours"
}
```

**Rate Limit:** 10 requests/minute per IP

**Contact Types:**
- `support`: Technical support requests
- `sales`: Sales and pricing inquiries
- `partnership`: Partnership opportunities
- `feedback`: Product feedback

**Emails Sent:**
1. Confirmation to submitter
2. Notification to appropriate team

### Dashboard

#### `GET /v1/dashboard/metrics`
Get real-time platform metrics for public dashboard.

**Response:**
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

**Rate Limit:** 30 requests/minute per IP

### Internal Monitoring

#### `GET /internal/cache-stats`
Get cache performance statistics.

**Response:**
```json
{
  "hits": 1523,
  "misses": 287,
  "hit_rate": 84.1,
  "evictions": 45,
  "current_size": 127
}
```

**Note:** This endpoint should be restricted to internal traffic only in production.

## Configuration

### Environment Variables

Required:
- `GOOGLE_CLOUD_PROJECT`: GCP project ID (default: xynergy-dev-1757909467)
- `ASO_ENGINE_URL`: ASO Engine service URL
- `SENDGRID_API_KEY`: SendGrid API key for email notifications
- `NOTIFICATION_EMAIL`: Email address for receiving notifications (e.g., team@clearforge.ai)

Optional:
- `ENVIRONMENT`: Environment name (default: production)
- `SMTP_HOST`: SMTP server hostname (fallback if SendGrid fails)
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USERNAME`: SMTP authentication username
- `SMTP_PASSWORD`: SMTP authentication password
- `SMTP_FROM_EMAIL`: Email address for SMTP sender

### Resource Limits

Default Cloud Run configuration:
- **Memory**: 1Gi
- **CPU**: 1 vCPU
- **Min Instances**: 0 (scales to zero)
- **Max Instances**: 10
- **Timeout**: 60 seconds
- **Concurrency**: 80 requests per instance

## Setup & Deployment

### Local Development

1. **Install Dependencies**
```bash
cd xynergy-intelligence-gateway
pip install -r requirements.txt
```

2. **Set Environment Variables**
```bash
export GOOGLE_CLOUD_PROJECT=xynergy-dev-1757909467
export ASO_ENGINE_URL=https://aso-engine-vgjxy554mq-uc.a.run.app
export SENDGRID_API_KEY=your_sendgrid_api_key
export NOTIFICATION_EMAIL=team@clearforge.ai
```

3. **Run Locally**
```bash
uvicorn app.main:app --reload --port 8080
```

4. **Test Health Endpoint**
```bash
curl http://localhost:8080/health
```

### Docker Development

1. **Build Image**
```bash
docker build -t xynergy-intelligence-gateway .
```

2. **Run Container**
```bash
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=xynergy-dev-1757909467 \
  -e ASO_ENGINE_URL=https://aso-engine-vgjxy554mq-uc.a.run.app \
  -e SENDGRID_API_KEY=your_key \
  -e NOTIFICATION_EMAIL=team@clearforge.ai \
  xynergy-intelligence-gateway
```

### Production Deployment

1. **Configure GCP Authentication**
```bash
gcloud auth login
gcloud config set project xynergy-dev-1757909467
```

2. **Set SendGrid API Key (One-time)**
```bash
# Store in Secret Manager or set via Cloud Run console
gcloud secrets create sendgrid-api-key --data-file=- <<< "your_sendgrid_api_key"
```

3. **Deploy to Cloud Run**
```bash
chmod +x deploy.sh
./deploy.sh
```

4. **Verify Deployment**
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe xynergy-intelligence-gateway \
  --region=us-central1 \
  --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health
```

5. **Configure Custom Domain (Optional)**
```bash
gcloud run domain-mappings create \
  --service=xynergy-intelligence-gateway \
  --domain=api.clearforge.ai \
  --region=us-central1
```

## Firestore Setup

The service requires two Firestore collections with indexes:

### Collections

1. **beta_applications**
   - Document ID: Auto-generated
   - Fields: businessName, industry, size, name, email, phone, challenges, whyRightFit, timeframe, submitted_at, status

2. **contact_submissions**
   - Document ID: Auto-generated
   - Fields: name, email, contactType, subject, message, submitted_at, status, ticket_id

### Indexes

Create composite indexes for queries:

```bash
# Beta applications by submission date
gcloud firestore indexes composite create \
  --collection-group=beta_applications \
  --field-config field-path=submitted_at,order=descending \
  --field-config field-path=status,order=ascending

# Contact submissions by type and date
gcloud firestore indexes composite create \
  --collection-group=contact_submissions \
  --field-config field-path=contactType,order=ascending \
  --field-config field-path=submitted_at,order=descending
```

## Email Configuration

### SendGrid Setup (Recommended)

1. Create SendGrid account and verify sender domain
2. Generate API key with Mail Send permissions
3. Set `SENDGRID_API_KEY` environment variable
4. Configure `NOTIFICATION_EMAIL` for receiving notifications

### SMTP Fallback

If SendGrid is unavailable, the service falls back to SMTP:

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=your_email@gmail.com
export SMTP_PASSWORD=your_app_password
export SMTP_FROM_EMAIL=your_email@gmail.com
```

## Monitoring & Observability

### Structured Logging

All logs use structured JSON format via structlog:

```json
{
  "event": "aso_data_fetched",
  "tenant_id": "clearforge",
  "endpoint": "trending-keywords",
  "duration_ms": 234,
  "cached": false,
  "timestamp": "2025-10-09T10:30:00Z"
}
```

### Cloud Logging Queries

View logs in Google Cloud Console:

```
resource.type="cloud_run_revision"
resource.labels.service_name="xynergy-intelligence-gateway"
severity="ERROR"
```

### Metrics

Monitor via Cloud Run metrics:
- Request count
- Request latency (p50, p95, p99)
- Error rate
- Instance count
- CPU and memory utilization

### Alerts

Recommended alerting rules:
1. Error rate > 5% for 5 minutes
2. p95 latency > 2 seconds for 5 minutes
3. Instance count = max instances for 10 minutes

## Security Considerations

### Authentication
- Public read endpoints (ASO): No authentication required
- Lead capture endpoints: Rate limited by IP
- Internal endpoints: Should be restricted to VPC or require API key in production

### CORS Configuration
- Configured for `https://clearforge.ai` and `https://*.clearforge.ai`
- Does not allow all origins (security best practice)
- Update CORS origins in `app/main.py` for additional domains

### Rate Limiting
- IP-based throttling prevents abuse
- Configurable limits per endpoint type
- Returns 429 status code when exceeded

### Data Privacy
- Email addresses validated before storage
- No sensitive data logged
- PII stored in Firestore with appropriate security rules

### Input Validation
- All inputs validated via Pydantic models
- String length limits enforced
- Email format validation
- No SQL injection risk (Firestore)

## Troubleshooting

### Circuit Breaker Triggered

**Symptom**: `aso_engine_circuit_open` errors in logs

**Cause**: ASO Engine is experiencing failures

**Resolution**:
1. Check ASO Engine health: `curl $ASO_ENGINE_URL/health`
2. Review ASO Engine logs for errors
3. Circuit will auto-reset after 60 seconds
4. Cached data will be served during outage

### Email Delivery Failures

**Symptom**: `email_send_failed` errors in logs

**Cause**: SendGrid API key invalid or SMTP configuration incorrect

**Resolution**:
1. Verify SendGrid API key: Test via SendGrid dashboard
2. Check SMTP credentials if using fallback
3. Verify sender email is verified in SendGrid
4. Check email service logs: `logger.error("email_send_failed")`

### Rate Limit Exceeded

**Symptom**: 429 status code returned

**Cause**: Too many requests from single IP

**Resolution**:
1. Client should implement exponential backoff
2. Distribute requests across time
3. For legitimate high-volume use, contact team about API key authentication

### Firestore Permission Denied

**Symptom**: `firestore_error` with permission denied

**Cause**: Service account lacks Firestore permissions

**Resolution**:
```bash
# Grant Firestore permissions to Cloud Run service account
gcloud projects add-iam-policy-binding xynergy-dev-1757909467 \
  --member="serviceAccount:835612502919-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"
```

## Performance Optimization

### Caching Strategy

Current implementation uses in-memory cache:
- TTL: 5 minutes (300 seconds)
- Automatic eviction on expiry
- Cache statistics tracking

**Future Enhancement**: Migrate to Redis for:
- Shared cache across instances
- Persistent cache across deployments
- Better memory management

### ASO Engine Optimization

- Circuit breaker prevents cascade failures
- Cached responses reduce downstream load
- Configurable timeout (30 seconds)
- Connection pooling via httpx

### Database Optimization

- Firestore indexes for common queries
- Batch writes where applicable
- Connection pooling via shared client

## Future Enhancements

### Phase 2 Enhancements
- [ ] API key authentication for high-volume clients
- [ ] Redis cache for multi-instance deployments
- [ ] GraphQL interface for flexible querying
- [ ] WebSocket support for real-time updates
- [ ] Expanded ASO metrics (competitor analysis, predictions)

### Phase 3 Enhancements
- [ ] Multi-tenant support with API keys
- [ ] Custom webhook notifications
- [ ] Advanced analytics dashboard
- [ ] A/B testing framework
- [ ] Export endpoints (CSV, PDF reports)

## Integration Examples

### JavaScript/TypeScript

```typescript
// Fetch trending keywords
async function getTrendingKeywords() {
  const response = await fetch(
    'https://xynergy-intelligence-gateway-xxx.run.app/v1/aso/trending-keywords?limit=20'
  );
  const data = await response.json();
  return data.keywords;
}

// Submit beta application
async function submitBetaApplication(formData) {
  const response = await fetch(
    'https://xynergy-intelligence-gateway-xxx.run.app/v1/beta/apply',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    }
  );
  return await response.json();
}
```

### Python

```python
import httpx

async def get_trending_keywords(limit: int = 20):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://xynergy-intelligence-gateway-xxx.run.app/v1/aso/trending-keywords",
            params={"limit": limit}
        )
        return response.json()

async def submit_contact_form(contact_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://xynergy-intelligence-gateway-xxx.run.app/v1/contact",
            json=contact_data
        )
        return response.json()
```

### cURL

```bash
# Get trending keywords
curl "https://xynergy-intelligence-gateway-xxx.run.app/v1/aso/trending-keywords?limit=10"

# Submit beta application
curl -X POST "https://xynergy-intelligence-gateway-xxx.run.app/v1/beta/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "Acme Corp",
    "industry": "Technology",
    "size": "11-50",
    "name": "John Doe",
    "email": "john@acme.com",
    "challenges": "Need automation",
    "whyRightFit": "Tech-savvy team"
  }'
```

## Support

For issues, questions, or feature requests:
- Technical issues: Submit via contact form (contactType: "support")
- Integration questions: team@clearforge.ai
- Documentation: See `/docs` directory

## License

Internal Xynergy Platform service - Proprietary
