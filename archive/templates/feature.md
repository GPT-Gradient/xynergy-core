# TECHNICAL REQUIREMENTS DOCUMENT (TRD)
## Xynergy Platform - Website Integration Layer

**Project**: ClearForge Website Public API Integration  
**Version**: 1.0  
**Date**: October 9, 2025  
**Status**: Ready for Implementation  
**Priority**: HIGH - Beta Launch Blocker  

---

## 1. EXECUTIVE SUMMARY

### 1.1 Purpose
Create a lightweight Intelligence Gateway service that aggregates ClearForge's internal Xynergy Platform data and exposes it to the public-facing ClearForge website. This service acts as a bridge between 22 deployed Xynergy microservices and the website's need for simplified, read-only access to live business intelligence data.

### 1.2 Scope
**In Scope:**
- Intelligence Gateway service (new FastAPI microservice)
- Beta application capture and storage
- Contact form submission handling
- Live ASO data aggregation from Xynergy ASO Engine
- Dashboard metrics aggregation
- Email notifications for leads

**Out of Scope:**
- XynergyOS deployment (remains local/internal)
- Multi-tenant architecture (single tenant: ClearForge)
- User authentication for website (public read-only access)
- Social media OAuth integrations
- Payment processing

### 1.3 Success Criteria
- ✅ Website displays live ASO keyword data from Xynergy Platform
- ✅ Beta applications successfully stored in Firestore
- ✅ Contact form submissions successfully stored in Firestore
- ✅ Email notifications sent for new applications/contacts
- ✅ Gateway responds in <500ms for all endpoints
- ✅ Zero downtime deployment capability
- ✅ Complete deployment in 1-2 days

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────┐
│  Public Website (Next.js)                       │
│  https://trisynq-website-[hash].run.app         │
│  - 51 static pages                              │
│  - Beta application form                        │
│  - Contact form                                 │
│  - ASO data display                             │
└────────────┬────────────────────────────────────┘
             │
             │ HTTPS (public)
             │ GET /v1/aso/trending-keywords
             │ POST /v1/beta/apply
             │ POST /v1/contact
             ▼
┌─────────────────────────────────────────────────┐
│  Intelligence Gateway (NEW)                     │
│  xynergy-intelligence-gateway                   │
│  https://xynergy-intelligence-gateway-[hash]... │
│  - Aggregation layer                            │
│  - Lead capture                                 │
│  - Email notifications                          │
└────────┬────────────────┬───────────────────────┘
         │                │
         │                │ Read/Write
         │                ▼
         │    ┌─────────────────────────┐
         │    │  Firestore              │
         │    │  - beta_applications    │
         │    │  - contact_submissions  │
         │    └─────────────────────────┘
         │
         │ Service-to-service calls (read-only)
         ▼
┌─────────────────────────────────────────────────┐
│  Xynergy Platform (22 Services - DEPLOYED)      │
│  GCP Project: xynergy-dev-1757909467            │
│                                                 │
│  Key Services for Integration:                  │
│  • ASO Engine (aso-engine-vgjxy554mq-uc...)    │
│  • Analytics Data Layer (xynergy-analytics...) │
│  • Platform Dashboard (xynergy-platform...)     │
└─────────────────────────────────────────────────┘
```

### 2.2 Data Flow

#### Flow 1: Website Displays Live ASO Data
```
1. User visits /forge/topics or /dashboard on website
2. Website makes GET request to Intelligence Gateway
3. Gateway calls Xynergy ASO Engine
4. Gateway transforms data for website consumption
5. Website displays trending keywords and rankings
```

#### Flow 2: Beta Application Submission
```
1. User fills out beta application form
2. Website makes POST to /v1/beta/apply
3. Gateway validates required fields
4. Gateway stores in Firestore beta_applications collection
5. Gateway sends email notification to hello@clearforge.ai
6. Gateway returns success to user
```

#### Flow 3: Contact Form Submission
```
1. User fills out contact form
2. Website makes POST to /v1/contact
3. Gateway validates and categorizes (beta/partnership/consulting/general/media)
4. Gateway stores in Firestore contact_submissions collection
5. Gateway sends email notification to appropriate team
6. Gateway returns success to user
```

---

## 3. INTELLIGENCE GATEWAY SERVICE SPECIFICATION

### 3.1 Service Details

**Service Name**: `xynergy-intelligence-gateway`  
**Technology**: FastAPI (Python 3.11)  
**Deployment**: Google Cloud Run  
**GCP Project**: xynergy-dev-1757909467  
**Region**: us-central1  

**Resource Configuration**:
```yaml
cpu: 500m (0.5 vCPU)
memory: 1Gi
min_instances: 0 (scale to zero)
max_instances: 10
timeout: 60s
concurrency: 80
```

### 3.2 API Endpoints

#### 3.2.1 Health & Info

**GET /**
```
Purpose: Service information
Request: None
Response:
{
  "service": "xynergy-intelligence-gateway",
  "version": "1.0.0",
  "status": "healthy",
  "endpoints": {
    "aso": ["/v1/aso/trending-keywords", "/v1/aso/keyword-rankings"],
    "leads": ["/v1/beta/apply", "/v1/contact"],
    "metrics": ["/v1/dashboard/metrics"]
  }
}
Auth: None
Status Code: 200
```

**GET /health**
```
Purpose: Health check for monitoring
Request: None
Response:
{
  "status": "healthy",
  "timestamp": "2025-10-09T10:30:00Z",
  "checks": {
    "firestore": "healthy",
    "xynergy_aso": "healthy"
  }
}
Auth: None
Status Code: 200
```

#### 3.2.2 ASO Intelligence

**GET /v1/aso/trending-keywords**
```
Purpose: Get trending keywords from Xynergy ASO Engine
Request Query Parameters:
  - limit: integer (default: 20, max: 50)
  - tenant_id: string (default: "clearforge")

Response:
{
  "status": "success",
  "keywords": [
    {
      "keyword": "AI business automation",
      "search_volume": 8100,
      "trend_score": 92.5,
      "growth_rate": 156.3,
      "difficulty_score": 55.3,
      "opportunity_score": 78.2
    }
  ],
  "total": 20,
  "tenant_id": "clearforge",
  "generated_at": "2025-10-09T10:30:00Z"
}

Error Response (if ASO Engine unavailable):
{
  "status": "error",
  "error": "Unable to fetch trending keywords",
  "fallback_data": []
}

Auth: None
Status Code: 200 (success), 503 (service unavailable)
Cache: 15 minutes (client-side)
```

**GET /v1/aso/keyword-rankings**
```
Purpose: Get current keyword rankings for ClearForge content
Request Query Parameters:
  - tenant_id: string (default: "clearforge")
  - limit: integer (default: 50, max: 100)

Response:
{
  "status": "success",
  "rankings": [
    {
      "keyword": "AI transparency tools",
      "content_id": "content_abc123",
      "content_title": "AI Transparency Guide",
      "current_position": 3,
      "previous_position": 5,
      "change": 2,
      "url": "https://clearforge.ai/forge/topics/ai-transparency"
    }
  ],
  "summary": {
    "total_keywords_tracked": 145,
    "avg_position": 8.2,
    "trending_up": 42,
    "trending_down": 15
  },
  "generated_at": "2025-10-09T10:30:00Z"
}

Auth: None
Status Code: 200
Cache: 1 hour (client-side)
```

**GET /v1/aso/content-performance**
```
Purpose: Get aggregated content performance metrics
Request Query Parameters:
  - tenant_id: string (default: "clearforge")
  - period_days: integer (default: 30)

Response:
{
  "status": "success",
  "content_performance": [
    {
      "content_id": "content_abc123",
      "title": "Complete Guide to AI Transparency",
      "content_type": "hub",
      "total_views": 5420,
      "total_conversions": 87,
      "conversion_rate": 0.016,
      "avg_position": 3.2,
      "performance_score": 85,
      "trend": "rising"
    }
  ],
  "period_days": 30,
  "generated_at": "2025-10-09T10:30:00Z"
}

Auth: None
Status Code: 200
Cache: 1 hour
```

#### 3.2.3 Lead Capture

**POST /v1/beta/apply**
```
Purpose: Submit beta program application
Request Body:
{
  "businessName": "Acme Corp",
  "industry": "SaaS",
  "name": "John Doe",
  "email": "john@acme.com",
  "challenges": "Need to improve content ROI and automate SEO",
  "whyRightFit": "We have 3 content creators and need better tools",
  "company": "Acme Corp",            // Optional
  "role": "VP of Marketing",          // Optional
  "website": "https://acme.com",      // Optional
  "teamSize": "10-50",                // Optional
  "goals": ["improve_seo", "automate_content"]  // Optional
}

Validation Rules:
- businessName: required, 2-200 characters
- industry: required, 2-100 characters
- name: required, 2-100 characters
- email: required, valid email format
- challenges: required, 10-2000 characters
- whyRightFit: required, 10-2000 characters

Success Response:
{
  "success": true,
  "message": "Application submitted successfully. We'll review and respond within 48 hours.",
  "applicationId": "beta_a1b2c3d4e5f6"
}

Error Response:
{
  "success": false,
  "error": "Missing required field: email"
}

Auth: None (public endpoint)
Status Code: 200 (success), 400 (validation error), 500 (server error)
Rate Limit: 5 requests per minute per IP
Side Effects:
  1. Store in Firestore: beta_applications/{applicationId}
  2. Send email to hello@clearforge.ai
  3. Send confirmation email to applicant
```

**POST /v1/contact**
```
Purpose: Submit contact form
Request Body:
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "type": "partnership",  // beta|partnership|consulting|general|media
  "message": "I'd like to discuss a partnership opportunity",
  "company": "Example Inc",  // Optional
  "phone": "+1-555-0123"     // Optional
}

Validation Rules:
- name: required, 2-100 characters
- email: required, valid email format
- type: required, one of: beta, partnership, consulting, general, media
- message: required, 10-5000 characters

Success Response:
{
  "success": true,
  "message": "Message received! We'll respond within 48 hours.",
  "ticketId": "ticket_x1y2z3a4b5"
}

Error Response:
{
  "success": false,
  "error": "Invalid contact type. Must be one of: beta, partnership, consulting, general, media"
}

Auth: None
Status Code: 200 (success), 400 (validation error), 500 (server error)
Rate Limit: 10 requests per minute per IP
Side Effects:
  1. Store in Firestore: contact_submissions/{ticketId}
  2. Send email notification to appropriate team
  3. Send confirmation email to submitter
```

#### 3.2.4 Dashboard Metrics

**GET /v1/dashboard/metrics**
```
Purpose: Get aggregated metrics for public transparency dashboard
Request Query Parameters: None

Response:
{
  "status": "success",
  "data": {
    "betaParticipants": 47,
    "projectProgress": {
      "nexus": 85,
      "data-democracy": 40,
      "no-cheating": 25,
      "ctos-heart": 15,
      "safe-spaces": 10,
      "re-connect": 5
    },
    "communityMembers": 124,
    "successStories": 3,
    "keywordRankings": {
      "total_tracked": 145,
      "top_10_positions": 42,
      "avg_position": 8.2
    }
  },
  "generated_at": "2025-10-09T10:30:00Z"
}

Auth: None
Status Code: 200
Cache: 5 minutes (server-side)
Data Sources:
  - betaParticipants: Count from Firestore beta_applications
  - communityMembers: Count from Firestore contact_submissions
  - keywordRankings: From Xynergy ASO Engine
  - projectProgress: Manual updates or from Xynergy Project Management
```

### 3.3 Error Handling

**Standard Error Response Format**:
```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {}  // Optional additional context
}
```

**HTTP Status Codes**:
- 200: Success
- 400: Bad Request (validation error)
- 404: Not Found
- 429: Too Many Requests (rate limit)
- 500: Internal Server Error
- 503: Service Unavailable (Xynergy services down)

**Circuit Breaker Pattern**:
- If Xynergy ASO Engine fails 3 times in 1 minute, return cached data
- Reset circuit after 60 seconds
- Log failures for monitoring

### 3.4 Rate Limiting

```python
Rate Limits (per IP address):
- /v1/beta/apply: 5 requests/minute, 20 requests/hour
- /v1/contact: 10 requests/minute, 50 requests/hour
- /v1/aso/*: 60 requests/minute
- /v1/dashboard/*: 30 requests/minute

Implementation: slowapi library with Redis backend (optional)
Fallback: In-memory rate limiting if Redis unavailable
```

### 3.5 Caching Strategy

```python
Server-Side Cache (Redis or In-Memory):
- /v1/aso/trending-keywords: 15 minutes
- /v1/aso/keyword-rankings: 1 hour
- /v1/aso/content-performance: 1 hour
- /v1/dashboard/metrics: 5 minutes

Client-Side Cache Headers:
Cache-Control: public, max-age=300, stale-while-revalidate=60

No Caching:
- POST endpoints (leads)
- /health (monitoring)
```

---

## 4. DATA MODELS

### 4.1 Firestore Collections

#### beta_applications
```javascript
{
  id: "beta_a1b2c3d4e5f6",  // Auto-generated
  businessName: "Acme Corp",
  industry: "SaaS",
  name: "John Doe",
  email: "john@acme.com",
  challenges: "Need to improve content ROI...",
  whyRightFit: "We have 3 content creators...",
  company: "Acme Corp",      // Optional
  role: "VP of Marketing",   // Optional
  website: "https://acme.com", // Optional
  teamSize: "10-50",         // Optional
  goals: ["improve_seo", "automate_content"], // Optional
  status: "submitted",       // submitted|under_review|accepted|rejected
  qualificationScore: null,  // 0-100, calculated later
  source: "website",
  submittedAt: Timestamp,
  reviewedAt: null,
  reviewedBy: null,
  notes: null
}

Indexes:
- status (ascending)
- submittedAt (descending)
- email (ascending) - for duplicate detection
```

#### contact_submissions
```javascript
{
  id: "ticket_x1y2z3a4b5",  // Auto-generated
  name: "Jane Smith",
  email: "jane@example.com",
  type: "partnership",  // beta|partnership|consulting|general|media
  message: "I'd like to discuss...",
  company: "Example Inc",  // Optional
  phone: "+1-555-0123",    // Optional
  status: "new",  // new|in_progress|resolved|closed
  assignedTo: null,
  source: "website",
  submittedAt: Timestamp,
  respondedAt: null,
  notes: []
}

Indexes:
- status (ascending)
- type (ascending)
- submittedAt (descending)
```

### 4.2 Xynergy ASO Engine Data Model (Read-Only)

Gateway reads from these BigQuery tables via ASO Engine API:

**aso_tenant_clearforge.content_pieces**
```sql
content_id STRING
content_type STRING  -- 'hub' or 'spoke'
keyword_primary STRING
title STRING
url STRING
status STRING
performance_score FLOAT64
ranking_position INT64
monthly_traffic INT64
created_at TIMESTAMP
```

**aso_tenant_clearforge.keyword_tracking**
```sql
keyword_id STRING
keyword STRING
search_volume INT64
difficulty_score FLOAT64
current_rank INT64
trend STRING  -- 'rising', 'falling', 'stable'
last_checked TIMESTAMP
```

---

## 5. INTEGRATION WITH XYNERGY SERVICES

### 5.1 ASO Engine Integration

**Service**: ASO Engine  
**URL**: `https://aso-engine-vgjxy554mq-uc.a.run.app`  
**Auth**: None (currently - TODO: add API key)  

**Endpoints Used by Gateway**:

```python
# Get trending keywords
GET https://aso-engine-vgjxy554mq-uc.a.run.app/api/keywords/trending
Query Params: tenant_id=clearforge, limit=20
Response: Array of keyword objects

# Get content list with performance
GET https://aso-engine-vgjxy554mq-uc.a.run.app/api/content
Query Params: tenant_id=clearforge, status=published
Response: Array of content objects with rankings

# Get opportunities
GET https://aso-engine-vgjxy554mq-uc.a.run.app/api/opportunities
Query Params: tenant_id=clearforge, limit=10
Response: Array of opportunity objects
```

**Error Handling**:
```python
try:
    response = await httpx_client.get(ASO_ENGINE_URL, timeout=5.0)
    response.raise_for_status()
    return response.json()
except httpx.TimeoutException:
    logger.error("ASO Engine timeout")
    return get_cached_data() or []
except httpx.HTTPStatusError as e:
    logger.error(f"ASO Engine error: {e.response.status_code}")
    return []
```

### 5.2 Analytics Data Layer Integration (Future)

**Service**: Analytics Data Layer  
**URL**: `https://xynergy-analytics-data-layer-vgjxy554mq-uc.a.run.app`  

**Potential Endpoints** (for Phase 2):
- GET /api/v1/dashboard/overview - Comprehensive metrics
- GET /api/v1/performance/summary - Performance data

### 5.3 Connection Pooling

```python
# Use httpx.AsyncClient with connection pooling
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(10.0, connect=5.0),
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
    http2=True
)

# Reuse client across requests
# Close on shutdown
```

---

## 6. EMAIL NOTIFICATIONS

### 6.1 Email Service Configuration

**Options** (Choose one):
- **Option A**: SendGrid (Recommended)
  - API-based, no SMTP needed
  - Requires: SENDGRID_API_KEY
  - Cost: Free tier (100 emails/day)
  
- **Option B**: Gmail SMTP (Quick MVP)
  - Use Gmail account with App Password
  - Requires: SMTP_USER, SMTP_PASSWORD
  - Cost: Free
  
- **Option C**: Google Cloud Email API
  - Requires more setup
  - Better for production

**Recommendation**: Start with SendGrid for reliability

### 6.2 Email Templates

#### Beta Application Received (to ClearForge)
```
To: hello@clearforge.ai
Subject: New Beta Application: {businessName}

New Beta Application Received
=============================

Business: {businessName}
Industry: {industry}
Contact: {name} ({email})
Website: {website}

Challenges:
{challenges}

Why Right Fit:
{whyRightFit}

Application ID: {applicationId}
Submitted: {submittedAt}

View in Dashboard: https://console.firebase.google.com/...
```

#### Beta Application Confirmation (to Applicant)
```
To: {applicant_email}
Subject: Beta Application Received - ClearForge

Hi {name},

Thanks for applying to the ClearForge Beta Program!

We've received your application for {businessName} and will review it within 48 hours. 

We're looking for businesses that:
- Create content regularly
- Want to improve SEO/content ROI
- Are ready to provide feedback

We'll reach out soon with next steps.

Questions? Reply to this email.

Best,
The ClearForge Team

---
Application ID: {applicationId}
```

#### Contact Form Received (to ClearForge)
```
To: hello@clearforge.ai (or type-specific email)
Subject: New Contact: {type} - {name}

New Contact Form Submission
==========================

Type: {type}
Name: {name}
Email: {email}
Company: {company}
Phone: {phone}

Message:
{message}

Ticket ID: {ticketId}
Submitted: {submittedAt}
```

#### Contact Form Confirmation (to Submitter)
```
To: {submitter_email}
Subject: Message Received - ClearForge

Hi {name},

We've received your message regarding {type}.

Expected Response Time:
- Beta inquiries: 48 hours
- Partnership: 48-72 hours
- Consulting: 48-72 hours
- General: 24-48 hours

We'll get back to you soon.

Best,
The ClearForge Team

---
Ticket ID: {ticketId}
```

### 6.3 Email Sending Implementation

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

async def send_email(to_email: str, subject: str, html_content: str):
    """Send email via SendGrid"""
    message = Mail(
        from_email='noreply@clearforge.ai',
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        logger.info(f"Email sent: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Email failed: {str(e)}")
        return False
```

---

## 7. MONITORING & OBSERVABILITY

### 7.1 Logging

**Structured Logging with structlog**:
```python
import structlog

logger = structlog.get_logger()

# Log example
logger.info(
    "beta_application_received",
    application_id=application_id,
    business_name=data.businessName,
    industry=data.industry
)
```

**Log Levels**:
- INFO: Normal operations (application received, email sent)
- WARNING: Degraded performance (ASO Engine slow response)
- ERROR: Failures (email send failed, validation error)
- CRITICAL: Service unavailable

**Log Retention**: 30 days in Cloud Logging

### 7.2 Metrics

**Key Metrics to Track**:
```python
# Request metrics
http_requests_total{method, endpoint, status}
http_request_duration_seconds{endpoint}

# Application metrics
beta_applications_total
contact_submissions_total{type}

# Integration metrics
aso_engine_requests_total{status}
aso_engine_response_time_seconds
email_send_total{status}

# Cache metrics
cache_hit_rate
cache_hits_total
cache_misses_total
```

### 7.3 Health Checks

**Endpoint**: GET /health

**Checks**:
```python
{
  "status": "healthy" | "degraded" | "unhealthy",
  "timestamp": "2025-10-09T10:30:00Z",
  "checks": {
    "firestore": {
      "status": "healthy",
      "response_time_ms": 45
    },
    "aso_engine": {
      "status": "healthy",
      "response_time_ms": 234
    },
    "email_service": {
      "status": "healthy",
      "last_test": "2025-10-09T10:00:00Z"
    }
  },
  "uptime_seconds": 86400
}
```

### 7.4 Alerts

**Critical Alerts** (PagerDuty/Slack):
- Service down (health check fails)
- Error rate >5% for 5 minutes
- ASO Engine unavailable for >2 minutes

**Warning Alerts** (Slack):
- Response time >1s for 5 minutes
- Email send failures >10% for 10 minutes
- Cache hit rate <70%

---

## 8. SECURITY

### 8.1 Current Security Model

**Phase 1 (Beta PoC)**:
- No authentication required (public read-only data)
- Rate limiting by IP address
- Input validation on all POST endpoints
- CORS restricted to clearforge.ai domain

### 8.2 Input Validation

```python
from pydantic import BaseModel, EmailStr, Field, validator

class BetaApplication(BaseModel):
    businessName: str = Field(..., min_length=2, max_length=200)
    industry: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    challenges: str = Field(..., min_length=10, max_length=2000)
    whyRightFit: str = Field(..., min_length=10, max_length=2000)
    company: Optional[str] = Field(None, max_length=200)
    role: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    teamSize: Optional[str] = None
    goals: Optional[List[str]] = None
    
    @validator('website')
    def validate_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Invalid URL')
        return v
```

### 8.3 CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://trisynq-website-vgjxy554mq-uc.a.run.app",
        "https://clearforge.ai",
        "http://localhost:3000"  # Development only
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=False,
    max_age=3600
)
```

### 8.4 Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/beta/apply")
@limiter.limit("5/minute")
async def submit_beta_application(request: Request, data: BetaApplication):
    # Implementation
```

### 8.5 Future Security Enhancements

**Phase 2** (When adding authenticated features):
- API key authentication for programmatic access
- JWT tokens for user sessions
- Field-level encryption for sensitive data
- WAF (Web Application Firewall) via Cloud Armor

---

## 9. DEPLOYMENT

### 9.1 Prerequisites

**Required**:
- ✅ GCP Project: xynergy-dev-1757909467
- ✅ gcloud CLI installed and authenticated
- ✅ Cloud Run API enabled
- ✅ Firestore database created
- ⏳ SendGrid API key (or Gmail SMTP credentials)

**Optional**:
- Redis instance (for caching - can use in-memory fallback)
- Custom domain (clearforge.ai)

### 9.2 Environment Variables

```bash
# Application
ENVIRONMENT=production
PORT=8080

# GCP
GOOGLE_CLOUD_PROJECT=xynergy-dev-1757909467

# Xynergy Services
ASO_ENGINE_URL=https://aso-engine-vgjxy554mq-uc.a.run.app
ANALYTICS_DATA_LAYER_URL=https://xynergy-analytics-data-layer-vgjxy554mq-uc.a.run.app

# Email Service (Choose one)
# Option A: SendGrid
SENDGRID_API_KEY=SG.xxxxx

# Option B: SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@clearforge.ai
SMTP_PASSWORD=xxxx

# CORS
CORS_ORIGINS=https://trisynq-website-vgjxy554mq-uc.a.run.app,https://clearforge.ai

# Optional: Redis
REDIS_HOST=10.x.x.x
REDIS_PORT=6379
REDIS_PASSWORD=xxxxx
```

### 9.3 Deployment Commands

```bash
# Navigate to gateway directory
cd xynergy-intelligence-gateway

# Deploy to Cloud Run
gcloud run deploy xynergy-intelligence-gateway \
  --source=. \
  --platform=managed \
  --region=us-central1 \
  --project=xynergy-dev-1757909467 \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=60 \
  --concurrency=80 \
  --set-env-vars=ENVIRONMENT=production,ASO_ENGINE_URL=https://aso-engine-vgjxy554mq-uc.a.run.app \
  --set-secrets=SENDGRID_API_KEY=sendgrid-api-key:latest

# Get service URL
gcloud run services describe xynergy-intelligence-gateway \
  --region=us-central1 \
  --format='value(status.url)'
```

### 9.4 Docker Configuration

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**requirements.txt**:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic[email]
google-cloud-firestore==2.13.1
google-cloud-logging==3.8.0
httpx==0.25.2
structlog==23.1.0
slowapi==0.1.9
sendgrid==6.10.0
python-multipart==0.0.6
```

---

## 10. TESTING STRATEGY

### 10.1 Unit Tests

```python
# tests/test_validation.py
def test_beta_application_validation():
    """Test beta application validation"""
    # Valid application
    valid_data = {
        "businessName": "Test Corp",
        "industry": "SaaS",
        "name": "John Doe",
        "email": "john@test.com",
        "challenges": "Need to improve content ROI",
        "whyRightFit": "We have a team ready to provide feedback"
    }
    app = BetaApplication(**valid_data)
    assert app.businessName == "Test Corp"
    
    # Invalid email
    invalid_data = valid_data.copy()
    invalid_data["email"] = "not-an-email"
    with pytest.raises(ValidationError):
        BetaApplication(**invalid_data)

# tests/test_aso_integration.py
async def test_aso_trending_keywords():
    """Test ASO Engine integration"""
    client = TestClient(app)
    response = client.get("/v1/aso/trending-keywords?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["keywords"]) <= 5
```

### 10.2 Integration Tests

```python
# tests/test_firestore.py
async def test_beta_application_storage():
    """Test Firestore storage"""
    application_data = {...}
    application_id = await store_beta_application(application_data)
    
    # Verify stored
    doc = db.collection("beta_applications").document(application_id).get()
    assert doc.exists
    assert doc.get("email") == application_data["email"]
    
    # Cleanup
    doc.reference.delete()
```

### 10.3 End-to-End Tests

```bash
# Smoke test after deployment
curl -X POST https://xynergy-intelligence-gateway-[hash].run.app/v1/beta/apply \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "Test Corp",
    "industry": "SaaS",
    "name": "Test User",
    "email": "test@example.com",
    "challenges": "Testing the integration",
    "whyRightFit": "This is a test application"
  }'

# Expected: 200 OK with applicationId
```

---

## 11. ROLLBACK PLAN

### 11.1 Rollback Triggers

Rollback if:
- Error rate >10% for 5 minutes
- Health check fails for 3 consecutive checks
- Critical bug discovered
- Performance degradation (p95 latency >2s)

### 11.2 Rollback Procedure

```bash
# List revisions
gcloud run revisions list \
  --service=xynergy-intelligence-gateway \
  --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic xynergy-intelligence-gateway \
  --region=us-central1 \
  --to-revisions=xynergy-intelligence-gateway-00001-abc=100

# Verify rollback
curl https://xynergy-intelligence-gateway-[hash].run.app/health
```

---

## 12. SUCCESS METRICS

### 12.1 Technical Metrics

**Target SLOs**:
- Availability: 99.5% uptime
- Latency: p95 <500ms, p99 <1s
- Error Rate: <1%
- ASO Engine integration success rate: >95%

### 12.2 Business Metrics

**Week 1 Goals**:
- ✅ Service deployed and healthy
- ✅ Website displaying live ASO data
- ✅ First beta application captured
- ✅ Email notifications working

**Month 1 Goals**:
- 10+ beta applications received
- 50+ contact form submissions
- 1000+ ASO data requests served
- Zero critical incidents

---

## 13. TIMELINE

### Day 1: Development (6-8 hours)
- Hour 0-2: Set up project structure, dependencies
- Hour 2-4: Implement core endpoints (ASO, leads)
- Hour 4-6: Implement Firestore storage
- Hour 6-7: Implement email notifications
- Hour 7-8: Unit tests, local testing

### Day 2: Deployment & Testing (4-6 hours)
- Hour 0-1: Configure GCP secrets
- Hour 1-2: Deploy to Cloud Run
- Hour 2-3: Integration testing
- Hour 3-4: Update website configuration
- Hour 4-5: End-to-end testing
- Hour 5-6: Monitoring setup, documentation

**Total Effort**: 10-14 hours (1-2 business days)

---

## 14. RISKS & MITIGATIONS

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| ASO Engine downtime | Website shows no data | Low | Implement caching, fallback data |
| Email delivery failures | Leads not notified | Medium | Queue emails, retry logic, monitor delivery |
| Rate limit abuse | Service overload | Medium | IP-based rate limiting, CAPTCHA if needed |
| Firestore quota exceeded | Cannot store leads | Low | Monitor quotas, alerts at 80% |
| Validation bypass | Bad data stored | Low | Pydantic validation, server-side checks |

---

## 15. NEXT STEPS

### Immediate (Day 1)
1. Review and approve this TRD
2. Set up SendGrid account and get API key
3. Create Firestore collections (beta_applications, contact_submissions)
4. Begin Intelligence Gateway development

### Short-term (Week 1)
1. Deploy Intelligence Gateway to Cloud Run
2. Update website with Gateway URL
3. Deploy website to Cloud Run
4. End-to-end testing
5. Soft launch to internal team

### Medium-term (Month 1)
1. Monitor performance and errors
2. Iterate based on feedback
3. Add advanced features (content performance, etc.)
4. Prepare for beta user onboarding

---

**Document Status**: Ready for Implementation  
**Approval Required**: CTO/Tech Lead  
**Next Document**: Website Integration TRD (separate artifact)