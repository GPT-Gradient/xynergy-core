# Xynergy Platform - Complete API Keys & Credentials Audit

**Purpose:** A comprehensive set of questions to ask Claude (in the Xynergy project) to identify ALL API keys, credentials, and configuration details needed for the platform.

**How to Use:** Copy each question and paste it to Claude in the Xynergy project. Claude will analyze the codebase and provide detailed answers about what credentials are needed.

---

## 1. Core Platform Infrastructure

### Question 1: Database Configuration
```
Please analyze all database connection requirements across the Xynergy platform.

For each service that needs database access, tell me:
- Which database system is used (PostgreSQL, MySQL, MongoDB, etc.)
- What connection details are needed (host, port, database name, username, password, SSL settings)
- Which environment variables are expected (e.g., DATABASE_URL, DB_HOST, etc.)
- Are there separate databases for different services or one shared database?
- Any special connection pool settings required
- Migration or schema management requirements
```

### Question 2: Redis/Cache Configuration
```
Analyze all caching layer requirements in the Xynergy platform.

Tell me:
- Which services use Redis or other caching?
- What connection details are needed (host, port, password, TLS settings)
- What are the environment variable names expected?
- Cache sizing or memory requirements
- Any special Redis configurations (clusters, sentinels, etc.)
- TTL policies or cache key patterns used
```

### Question 3: Message Queue/Event Bus
```
Review the codebase for any message queue or event bus usage.

Identify:
- Is RabbitMQ, Redis Pub/Sub, Google Pub/Sub, or another system used?
- Which services publish messages and which subscribe?
- Connection credentials needed
- Queue names and topic patterns
- Any dead letter queue configurations
- Message retention policies
```

### Question 4: File Storage
```
Analyze file storage and object storage requirements.

Tell me:
- Is Google Cloud Storage, AWS S3, or another storage system used?
- What credentials are needed (service account keys, access keys, etc.)
- Bucket names or storage locations
- Public vs private access requirements
- CDN configuration needed
- File upload size limits and restrictions
```

---

## 2. Intelligence Gateway & AI Services

### Question 5: AI Provider Configuration
```
Examine all AI service integrations in the Intelligence Gateway and AI Routing Engine.

For each AI provider, tell me:
- Provider name (OpenAI, Anthropic, Abacus.AI, etc.)
- API keys or credentials needed
- Model names being used
- Rate limits or quotas to configure
- Fallback providers and priority order
- Cost tracking or budget limits
- Any webhook configurations for async processing
```

### Question 6: AI Routing Logic
```
Analyze the AI Routing Engine configuration.

Explain:
- What determines which AI provider is used for which request?
- Are there tenant-specific AI configurations?
- Environment variables for routing rules
- Model performance monitoring settings
- Failover and retry logic credentials
```

### Question 7: Embeddings and Vector Search
```
Review vector database and embeddings usage.

Identify:
- Vector database system used (Pinecone, Weaviate, pgvector, etc.)
- API keys and connection details needed
- Embedding model provider and credentials
- Index names and namespaces
- Vector dimensions and similarity metrics
- Backup and sync requirements
```

---

## 3. Marketing Engine

### Question 8: Search Engine and SEO APIs
```
Analyze all search engine and SEO tool integrations in the Marketing Engine.

List every API needed:
- Google Search Console API - credentials and setup
- Google Analytics API - credentials and property IDs
- Bing Webmaster Tools API
- SEMrush, Ahrefs, Moz - which ones and their API keys
- Keyword research tools
- Rank tracking APIs
- Backlink analysis APIs
- SERP scraping tools (if any)
```

### Question 9: Social Media APIs
```
Review all social media platform integrations.

For each platform, tell me:
- Twitter/X - API credentials, access levels, webhook setup
- LinkedIn - OAuth credentials, API permissions
- Facebook/Meta - App ID, App Secret, access tokens
- Instagram - Business API credentials
- Pinterest, TikTok, YouTube - if integrated
- Social listening tools
- Scheduling/publishing APIs
- Analytics APIs for each platform
```

---

## 4. Content Hub

### Question 10: Content Services
```
Examine all content-related APIs in the Content Hub.

Identify:
- Media/image APIs (Pexels, Unsplash, Pixabay) - API keys
- Stock photo services - credentials
- Video hosting (YouTube API, Vimeo) - if used
- Font services - API keys if needed
- Giphy or other GIF services
- Content delivery network (CDN) credentials
- Image optimization services
- Plagiarism checking APIs (Copyscape, etc.)
- Grammar/writing tools (Grammarly API, etc.)
```

---

## 5. Business Operations

### Question 11: Business APIs
```
Analyze business operations integrations.

List all APIs for:
- Payment processing (Stripe, PayPal) - API keys and webhook secrets
- Invoicing systems - credentials
- CRM systems (HubSpot, Salesforce) - OAuth and API keys
- Accounting software (QuickBooks, Xero) - if integrated
- Project management tools (Asana, Jira, Linear) - if integrated
- Customer support (Zendesk, Intercom) - if integrated
- Calendar systems (Google Calendar, Outlook) - OAuth setup
```

---

## 6. Analytics & Monitoring

### Question 12: Application Monitoring
```
Review all monitoring and observability integrations.

Identify:
- Error tracking (Sentry, Bugsnag) - DSN and project keys
- Logging service (Logtail, Datadog) - API keys
- APM tools (New Relic, Datadog APM) - credentials
- Uptime monitoring (Pingdom, UptimeRobot) - API keys
- Real user monitoring (LogRocket, FullStory)
- Performance monitoring configurations
- Alert notification webhooks
```

### Question 13: Custom Analytics
```
Examine the Analytics Data Layer implementation.

Tell me:
- Internal analytics database credentials
- Data warehouse connections (BigQuery, Snowflake, etc.)
- BI tool integrations (Tableau, Looker, Metabase)
- ETL/pipeline credentials
- Reporting service APIs
- Data export configurations
```

---

## 7. XynergyOS Orchestration

### Question 14: Orchestration Configuration
```
Analyze XynergyOS orchestration layer requirements.

Identify:
- Service discovery configuration
- Service mesh credentials (if used)
- Load balancer settings
- API gateway authentication
- Inter-service communication secrets
- Workflow engine credentials (Temporal, Airflow, etc. if used)
- Job scheduler configuration
```

---

## 8. Multi-Tenancy & Security

### Question 15: Authentication System
```
Review all authentication and authorization requirements.

Tell me:
- JWT secret keys and configuration
- OAuth providers and their credentials
- Session management (Redis, etc.)
- Password hashing configuration
- MFA/2FA service (Twilio, Authy) - if implemented
- SSO configurations
- API key generation and management
- Service-to-service authentication
```

### Question 16: Encryption and Secrets
```
Examine encryption and secrets management.

Identify:
- Data encryption keys
- Field-level encryption settings
- At-rest encryption configuration
- In-transit encryption (TLS certificates)
- Key rotation policies
- Secrets management system in use
- Tenant isolation security settings
```

---

## 9. Cross-Service Integration

### Question 17: Service Communication
```
Analyze how services communicate with each other.

Tell me:
- API authentication between services (API keys, JWT, mutual TLS)
- Shared secrets for internal APIs
- Service account credentials
- Network security requirements
- API versioning and compatibility settings
- Health check endpoints and credentials
```

---

## 10. Deployment & Configuration

### Question 18: Cloud Provider Settings
```
Review GCP-specific configurations.

List:
- Project ID and number
- Service account emails and their roles
- Cloud Run configuration (CPU, memory, concurrency)
- VPC and networking setup
- Cloud SQL or other managed service credentials
- Secret Manager usage - which secrets are stored where
- IAM roles and permissions needed
- Resource quotas and limits
```

### Question 19: Environment-Specific Settings
```
Analyze environment variable requirements.

For DEV, STAGING, and PROD, tell me:
- All environment variables needed per service
- Which ones are environment-specific vs shared
- Default values and acceptable value ranges
- Required vs optional environment variables
- Feature flags and their configuration
- Debug settings
- CORS and security header configurations
```

---

## 11. Email & Communications

### Question 20: Email Service Configuration
```
Review email sending capabilities.

Identify:
- Email provider (SendGrid, Postmark, AWS SES, etc.)
- API keys and webhook signing secrets
- From addresses and domain verification
- Email template IDs
- SMTP credentials (if used)
- Bounce and complaint handling
- Email tracking and analytics
```

---

## 12. ASO Engine Specific

### Question 21: ASO Data Sources
```
Analyze the ASO Engine's data requirements.

Tell me:
- Competitive intelligence APIs
- Market research data sources
- SEO data aggregation APIs
- Trend analysis APIs (Google Trends, etc.)
- Patent or research databases (if used)
- News APIs for opportunity detection
- Industry-specific data sources
```

---

## 13. Webhooks & External Integrations

### Question 22: Webhook Management
```
Review all webhook implementations.

Identify:
- Outgoing webhooks we send (URLs, authentication)
- Incoming webhooks we receive (signing secrets, validation)
- Webhook retry logic and credentials
- Event payload encryption
- Rate limiting for webhooks
```

---

## 14. Development & Testing

### Question 23: Testing Infrastructure
```
Examine testing environment needs.

Tell me:
- Test database credentials
- Mock API services and their configuration
- CI/CD pipeline secrets (if in codebase)
- Test data generation requirements
- Load testing tool credentials
- E2E testing service credentials
```

---

## 15. Compliance & Legal

### Question 24: Compliance Requirements
```
Review compliance-related configurations.

Identify:
- Data privacy settings (GDPR, CCPA)
- Cookie consent management
- Terms of service version tracking
- Audit logging requirements
- Data retention policy settings
- Right to deletion workflow credentials
```

---

## 16. Backup & Disaster Recovery

### Question 25: Backup Configuration
```
Analyze backup and DR requirements.

Tell me:
- Automated backup service credentials
- Backup storage locations and keys
- Disaster recovery region configuration
- Failover DNS credentials
- Database replication settings
- Point-in-time recovery requirements
```

---

## How to Use This Document

### Step 1: Prepare
- Have access to the Xynergy project in Claude
- Have a document ready to paste responses
- Allocate time to work through all 25 questions

### Step 2: Ask Each Question
- Copy each question block (including the context)
- Paste into Claude in the Xynergy project
- Wait for comprehensive analysis
- Save the response

### Step 3: Consolidate
- Create a master spreadsheet with all identified credentials
- Mark each as: CONFIGURED ✅ | PLACEHOLDER ⚠️ | MISSING ❌
- Prioritize by: CRITICAL | HIGH | MEDIUM | LOW

### Step 4: Action Plan
- Obtain missing CRITICAL credentials first
- Replace placeholders in priority order
- Configure secrets in GCP Secret Manager
- Update Cloud Run services
- Test and verify

---

## Expected Output Format

For each question, Claude should provide:

1. **List of specific credentials needed**
   - Exact environment variable names
   - Expected format (API key, URL, JSON, etc.)
   - Which services need each credential

2. **Current status**
   - Is it configured with real values?
   - Is it a placeholder?
   - Is it completely missing?

3. **Priority level**
   - CRITICAL - Platform won't work without it
   - HIGH - Major features broken
   - MEDIUM - Some features impacted
   - LOW - Optional or future features

4. **Setup instructions**
   - Where to get the credential
   - How to configure it
   - Any special setup required

---

## Quick Reference: Priority Levels

### CRITICAL (Get These First)
- Database credentials
- JWT secrets
- Primary AI API (OpenAI or Abacus)
- Email service
- GCP service accounts

### HIGH (Get These Next)
- Redis/caching
- Social media APIs for core features
- Google Search Console
- Monitoring/error tracking

### MEDIUM (Important But Not Blocking)
- Additional AI providers
- Media APIs
- Advanced analytics
- Business integrations

### LOW (Future/Optional)
- Payment processing (if not launched yet)
- Optional third-party tools
- Beta features
- Nice-to-have integrations

---

**Next Step:** Start with Question 1 and systematically work through all 25 questions with Claude in the Xynergy project. Each question is designed to extract comprehensive information about specific aspects of the platform's credential requirements.