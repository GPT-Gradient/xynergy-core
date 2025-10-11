# Data Model & Schema Documentation
## Xynergy Platform

**Document Version:** 1.1
**Last Updated:** October 11, 2025 (Added CRM Engine data model)

---

## Table of Contents

1. [Overview](#overview)
2. [Firestore Collections](#firestore-collections)
3. [BigQuery Datasets & Tables](#bigquery-datasets--tables)
4. [Redis Cache Keys](#redis-cache-keys)
5. [Cloud Storage Buckets](#cloud-storage-buckets)
6. [Entity Relationships](#entity-relationships)
7. [Data Flow](#data-flow)

---

## Overview

### Storage Strategy

| Data Type | Storage | Reason |
|-----------|---------|--------|
| Transactional | Firestore | Real-time, ACID guarantees |
| Analytical | BigQuery | Massive scale, SQL queries |
| Cache | Redis | Sub-10ms latency |
| Blobs/Files | Cloud Storage | Cost-effective for large files |

### Multi-Tenant Strategy

**Firestore:** Shared collections with `tenant_id` field
**BigQuery:** Isolated datasets per tenant (`aso_tenant_{tenant_id}`)
**Redis:** Namespaced keys (`{tenant_id}:*`)
**Storage:** Bucket with tenant metadata

---

## Firestore Collections

### Collection: `marketing_campaigns`

**Purpose:** Store marketing campaign data

**Schema:**
```javascript
{
  campaign_id: string,          // PK, UUID
  tenant_id: string,            // Index
  campaign_name: string,
  business_type: string,
  target_audience: string,
  budget_range: string,
  campaign_goals: [string],
  strategy: {
    recommended_channels: [string],
    content_strategy: string,
    targeting_approach: string
  },
  estimated_reach: number,
  budget_allocation: {
    channel1: number,
    channel2: number
  },
  status: string,               // draft, active, paused, completed
  created_at: timestamp,        // Index
  updated_at: timestamp,
  created_by: string
}
```

**Indexes:**
- `tenant_id` + `created_at` (DESC)
- `tenant_id` + `status`

**Security Rules:**
```javascript
match /marketing_campaigns/{campaignId} {
  allow read, write: if request.auth != null
    && resource.data.tenant_id == request.auth.token.tenant_id;
}
```

---

### Collection: `service_status`

**Purpose:** Track service health for dashboard

**Schema:**
```javascript
{
  service_name: string,         // PK
  status: string,               // healthy, degraded, unhealthy
  last_check: timestamp,
  checks: {
    firestore: { status: string, latency_ms: number },
    bigquery: { status: string, latency_ms: number },
    redis: { status: string }
  },
  metrics: {
    request_count: number,
    error_count: number,
    avg_latency_ms: number
  },
  circuit_breaker: {
    state: string,              // CLOSED, OPEN, HALF_OPEN
    failure_count: number
  }
}
```

---

### Collection: `tenants/{tenantId}/contacts` (CRM Engine)

**Purpose:** Store customer/prospect contact information with tenant isolation

**Schema:**
```javascript
{
  id: string,                     // PK, UUID
  tenantId: string,               // Partition key
  type: string,                   // person, company
  name: string,                   // Index
  email: string,                  // Index, unique per tenant
  phone: string,
  company: string,
  title: string,
  relationshipType: string,       // customer, prospect, partner, vendor
  status: string,                 // active, inactive, archived
  tags: [string],
  customFields: {
    key: value
  },
  socialProfiles: {
    linkedin: string,
    twitter: string
  },
  source: string,                 // slack, gmail, manual, import
  assignedTo: string,             // user ID
  interactionCount: number,
  emailCount: number,
  slackMessageCount: number,
  lastInteractionDate: timestamp,
  createdAt: timestamp,           // Index
  updatedAt: timestamp,
  createdBy: string,
  createdByEmail: string
}
```

**Indexes:**
- `tenantId` + `email` (unique)
- `tenantId` + `createdAt` (DESC)
- `tenantId` + `status` + `relationshipType`

---

### Collection: `tenants/{tenantId}/interactions` (CRM Engine)

**Purpose:** Track all customer interactions across channels

**Schema:**
```javascript
{
  id: string,                     // PK, UUID
  tenantId: string,
  contactId: string,              // Index - FK to contacts
  type: string,                   // email, slack_message, meeting, call, note
  direction: string,              // inbound, outbound
  subject: string,
  content: string,
  timestamp: timestamp,           // Index
  metadata: {
    emailId: string,              // If from Gmail
    slackChannelId: string,       // If from Slack
    slackMessageTs: string,
    meetingDuration: number
  },
  participants: [string],         // Other contacts involved
  attachments: [string],          // File references
  createdAt: timestamp,
  createdBy: string,
  createdByEmail: string
}
```

**Indexes:**
- `tenantId` + `contactId` + `timestamp` (DESC)
- `tenantId` + `type` + `timestamp` (DESC)

---

### Collection: `tenants/{tenantId}/notes` (CRM Engine)

**Purpose:** User notes about contacts and interactions

**Schema:**
```javascript
{
  id: string,                     // PK, UUID
  tenantId: string,
  contactId: string,              // Index - FK to contacts
  content: string,
  tags: [string],
  isPrivate: boolean,
  createdAt: timestamp,
  updatedAt: timestamp,
  createdBy: string,
  createdByEmail: string
}
```

---

### Collection: `tenants/{tenantId}/tasks` (CRM Engine)

**Purpose:** Track follow-up tasks related to contacts

**Schema:**
```javascript
{
  id: string,                     // PK, UUID
  tenantId: string,
  contactId: string,              // Index - FK to contacts
  title: string,
  description: string,
  dueDate: timestamp,             // Index
  priority: string,               // low, medium, high
  status: string,                 // pending, completed, cancelled
  assignedTo: string,
  completedAt: timestamp,
  createdAt: timestamp,
  updatedAt: timestamp,
  createdBy: string,
  createdByEmail: string
}
```

**Indexes:**
- `tenantId` + `contactId` + `status`
- `tenantId` + `dueDate` + `status`
- `tenantId` + `assignedTo` + `status`

---

### Collection: `workflow_monitoring`

**Purpose:** Track multi-service workflows

**Schema:**
```javascript
{
  workflow_id: string,          // PK, UUID
  workflow_type: string,        // campaign_creation, content_validation
  tenant_id: string,
  status: string,               // pending, in_progress, completed, failed
  steps: [
    {
      step_name: string,
      service: string,
      status: string,
      started_at: timestamp,
      completed_at: timestamp,
      error: string
    }
  ],
  created_at: timestamp,
  completed_at: timestamp,
  correlation_id: string
}
```

---

## BigQuery Datasets & Tables

### Dataset: `xynergy_analytics`

**Purpose:** Platform-wide analytics

**Location:** US
**Default Expiration:** 90 days

#### Table: `service_metrics`

**Schema:**
```sql
CREATE TABLE `xynergy_analytics.service_metrics` (
  metric_id STRING NOT NULL,
  service_name STRING NOT NULL,
  metric_type STRING NOT NULL,    -- request_count, error_rate, latency
  metric_value FLOAT64 NOT NULL,
  timestamp TIMESTAMP NOT NULL,    -- PARTITIONED
  tenant_id STRING,
  metadata JSON
)
PARTITION BY DATE(timestamp)
CLUSTER BY service_name, tenant_id;
```

**Partition Pruning Example:**
```sql
SELECT service_name, AVG(metric_value) as avg_latency
FROM `xynergy_analytics.service_metrics`
WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND metric_type = 'latency'
GROUP BY service_name;
```

---

### Dataset: `aso_tenant_{tenant_id}`

**Purpose:** Per-tenant ASO data (complete isolation)

**Location:** us-central1
**Tables:** content_pieces, keywords, opportunities

#### Table: `content_pieces`

**Schema:**
```sql
CREATE TABLE `aso_tenant_demo.content_pieces` (
  content_id STRING NOT NULL,
  content_type STRING NOT NULL,      -- hub, spoke
  keyword_primary STRING NOT NULL,
  keyword_secondary ARRAY<STRING>,
  hub_id STRING,                     -- NULL for hub content
  title STRING NOT NULL,
  meta_description STRING,
  url STRING,
  word_count INT64,
  status STRING NOT NULL,            -- draft, published, archived
  performance_score FLOAT64,
  ranking_position INT64,
  monthly_traffic INT64,
  monthly_conversions INT64,
  conversion_rate FLOAT64,
  created_at TIMESTAMP NOT NULL,     -- PARTITIONED
  published_at TIMESTAMP,
  updated_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY status, content_type;
```

**Relationships:**
- Hub Content (content_type = 'hub', hub_id = NULL)
- Spoke Content (content_type = 'spoke', hub_id = parent_content_id)

**Query Example (Hub/Spoke):**
```sql
-- Get hub with all spokes
SELECT
  h.content_id as hub_id,
  h.title as hub_title,
  ARRAY_AGG(STRUCT(s.content_id, s.title, s.ranking_position)) as spokes
FROM `aso_tenant_demo.content_pieces` h
LEFT JOIN `aso_tenant_demo.content_pieces` s
  ON h.content_id = s.hub_id
WHERE DATE(h.created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  AND h.content_type = 'hub'
GROUP BY h.content_id, h.title;
```

#### Table: `keywords`

**Schema:**
```sql
CREATE TABLE `aso_tenant_demo.keywords` (
  keyword STRING NOT NULL,
  search_volume INT64,
  difficulty_score FLOAT64,        -- 0-100
  kgr_score FLOAT64,               -- Keyword Golden Ratio
  intent STRING,                   -- informational, commercial, transactional
  current_ranking INT64,
  best_ranking INT64,
  target_ranking INT64,
  serp_history JSON,               -- [{date, position, url}]
  competitor_rankings JSON,        -- [{competitor, position}]
  last_checked TIMESTAMP,          -- PARTITIONED
  priority STRING,                 -- tier1, tier2, tier3
  content_id STRING,               -- FK to content_pieces
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(last_checked)
CLUSTER BY priority, intent;
```

**KGR Calculation:**
```sql
-- Keyword Golden Ratio = (# of allintitle results) / (monthly search volume)
-- KGR < 0.25 = excellent opportunity
SELECT
  keyword,
  search_volume,
  kgr_score,
  CASE
    WHEN kgr_score < 0.25 THEN 'Excellent'
    WHEN kgr_score < 1.0 THEN 'Good'
    ELSE 'Competitive'
  END as opportunity_level
FROM `aso_tenant_demo.keywords`
WHERE DATE(last_checked) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
ORDER BY kgr_score ASC;
```

#### Table: `opportunities`

**Purpose:** Low-hanging fruit SEO opportunities

**Schema:**
```sql
CREATE TABLE `aso_tenant_demo.opportunities` (
  opportunity_id STRING NOT NULL,
  opportunity_type STRING NOT NULL, -- low_hanging_fruit, content_gap, rank_improvement
  keyword STRING NOT NULL,
  confidence_score FLOAT64,         -- 0-1
  estimated_traffic INT64,
  estimated_difficulty FLOAT64,
  recommendation STRING,            -- Action to take
  detected_at TIMESTAMP NOT NULL,   -- PARTITIONED
  status STRING NOT NULL,           -- new, in_progress, completed, dismissed
  content_id STRING,                -- FK to content_pieces
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(detected_at)
CLUSTER BY status, opportunity_type;
```

**Opportunity Detection Query:**
```sql
-- Find low-hanging fruit (ranking 11-30, low difficulty, high volume)
SELECT
  k.keyword,
  k.current_ranking,
  k.search_volume,
  k.difficulty_score,
  (k.search_volume / k.difficulty_score) as opportunity_score
FROM `aso_tenant_demo.keywords` k
WHERE DATE(k.last_checked) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND k.current_ranking > 10
  AND k.current_ranking <= 30
  AND k.difficulty_score < 50
  AND k.search_volume > 100
ORDER BY opportunity_score DESC
LIMIT 50;
```

---

### Dataset: `validation_analytics`

**Purpose:** Content validation metrics

#### Table: `content_validations`

**Schema:**
```sql
CREATE TABLE `validation_analytics.content_validations` (
  validation_id STRING NOT NULL,
  content_id STRING NOT NULL,
  validation_timestamp TIMESTAMP NOT NULL,  -- PARTITIONED
  accuracy_score FLOAT64 NOT NULL,          -- 0-100
  fact_check_results JSON,
  plagiarism_score FLOAT64,
  trust_safety_score FLOAT64,
  validation_status STRING NOT NULL,        -- passed, failed, needs_review
  failed_checks JSON
)
PARTITION BY DATE(validation_timestamp)
CLUSTER BY validation_status;
```

---

### Dataset: `attribution_analytics`

**Purpose:** Revenue attribution and customer journey tracking

#### Table: `customer_journeys`

**Schema:**
```sql
CREATE TABLE `attribution_analytics.customer_journeys` (
  journey_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  client_id STRING NOT NULL,
  journey_start TIMESTAMP NOT NULL,         -- PARTITIONED
  journey_end TIMESTAMP,
  touchpoints JSON NOT NULL,                -- [{type, timestamp, channel, content_id}]
  conversion_events JSON,                   -- [{type, timestamp, value}]
  revenue_attributed FLOAT64,
  attribution_model STRING NOT NULL,        -- first_touch, last_touch, linear, time_decay
  keyword_attribution JSON                  -- {keyword: contribution_percentage}
)
PARTITION BY DATE(journey_start)
CLUSTER BY client_id, attribution_model;
```

**Attribution Models:**

1. **First Touch:** 100% credit to first touchpoint
2. **Last Touch:** 100% credit to last touchpoint
3. **Linear:** Equal credit to all touchpoints
4. **Time Decay:** More credit to recent touchpoints

**Example Query:**
```sql
-- Revenue by keyword (last-touch attribution)
SELECT
  JSON_EXTRACT_SCALAR(touchpoint, '$.keyword') as keyword,
  SUM(revenue_attributed) as total_revenue,
  COUNT(DISTINCT journey_id) as journey_count
FROM `attribution_analytics.customer_journeys`,
UNNEST(JSON_EXTRACT_ARRAY(touchpoints)) as touchpoint
WHERE DATE(journey_start) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND attribution_model = 'last_touch'
GROUP BY keyword
ORDER BY total_revenue DESC;
```

---

## Redis Cache Keys

### Namespace Structure

**Pattern:** `{category}:{identifier}:{param_hash}`

### Cache Namespaces

#### 1. AI Responses
**Keys:** `ai:resp:{provider}:{model}:{prompt_hash}`
**TTL:** 3600 seconds (1 hour)
**Value:**
```json
{
  "value": {
    "text": "Response text...",
    "model": "gpt-4o-mini",
    "tokens": {
      "prompt": 50,
      "completion": 200
    }
  },
  "cached_at": "2025-10-10T12:00:00Z",
  "ttl": 3600
}
```

#### 2. ASO Stats
**Keys:** `aso_stats:{tenant_id}:{days_back}`
**TTL:** 300 seconds (5 minutes)
**Value:**
```json
{
  "tenant_id": "demo",
  "total_content": 150,
  "total_keywords": 500,
  "total_opportunities": 25,
  "avg_ranking": 15.3,
  "cached_at": "2025-10-10T12:00:00Z"
}
```

#### 3. ASO Content
**Keys:** `aso_content:{tenant_id}:{status}:{days}:{limit}`
**TTL:** 120 seconds (2 minutes)

#### 4. ASO Keywords
**Keys:** `aso_keywords:{tenant_id}:{priority}:{days}:{limit}`
**TTL:** 180 seconds (3 minutes)

#### 5. ASO Opportunities
**Keys:** `aso_opportunities:{tenant_id}:{status}:{days}:{limit}`
**TTL:** 240 seconds (4 minutes)

### Cache Invalidation

**Pattern Invalidation:**
```python
# Invalidate all ASO content for tenant
await redis_cache.invalidate_pattern("aso_content:demo:*")

# Invalidate all AI responses from OpenAI
await redis_cache.invalidate_pattern("ai:resp:openai:*")
```

---

## Cloud Storage Buckets

### Bucket: `xynergy-dev-1757909467-xynergy-content`

**Purpose:** Content assets (images, videos, documents)
**Lifecycle:** 30 days
**Versioning:** Enabled

**Object Structure:**
```
{tenant_id}/
  content/
    {content_id}/
      images/
        {filename}.jpg
      documents/
        {filename}.pdf
  assets/
    logos/
    templates/
```

**Metadata:**
```json
{
  "tenant_id": "demo",
  "content_id": "abc123",
  "content_type": "image/jpeg",
  "uploaded_at": "2025-10-10T12:00:00Z",
  "uploaded_by": "user@example.com"
}
```

### Bucket: `xynergy-dev-1757909467-xynergy-reports`

**Purpose:** Generated reports (PDF, CSV, Excel)
**Lifecycle:** 365 days
**Versioning:** Enabled

**Object Structure:**
```
{tenant_id}/
  reports/
    {report_type}/
      {year}/
        {month}/
          {report_id}.pdf
```

---

## Entity Relationships

### ASO Domain

```
Hub Content (1) ──┬── (N) Spoke Content
                  │
                  └── (N) Keywords
                           │
                           └── (N) Opportunities
```

**Relationship Details:**

1. **Hub → Spokes:**
   - One hub can have multiple spokes
   - Spoke references hub via `hub_id`
   - CASCADE delete (delete hub = delete all spokes)

2. **Content → Keywords:**
   - One content piece targets multiple keywords
   - Keywords can be shared across content
   - `content_id` FK in keywords table

3. **Keywords → Opportunities:**
   - One keyword can have multiple opportunities over time
   - Opportunities reference keywords
   - Historical tracking

### Attribution Domain

```
Customer (1) ──┐
               ├── (N) Journeys
               │         │
               │         └── (N) Touchpoints
               │                   │
               │                   └── (1) Content
Client (1) ────┘
```

---

## Data Flow

### Write Path (CQRS)

```
API Request (Write)
    ↓
Validate with Pydantic
    ↓
Write to Firestore (Source of Truth)
    ↓
Publish Event to Pub/Sub
    ↓
Event Handler syncs to BigQuery
    ↓
Invalidate Redis Cache
```

### Read Path (Cache-Aside)

```
API Request (Read)
    ↓
Check Redis Cache
    ├─ HIT → Return (< 10ms)
    │
    └─ MISS → Query BigQuery (with partition pruning)
                ↓
            Store in Redis Cache (with TTL)
                ↓
            Return to Client
```

### Example: Content Creation Flow

```sql
-- 1. Write to Firestore
db.collection('content_queue').add({
  content_id: uuid(),
  tenant_id: 'demo',
  data: {...}
})

-- 2. Event published
topic: content-created
payload: {content_id, tenant_id, ...}

-- 3. Event handler inserts to BigQuery
INSERT INTO `aso_tenant_demo.content_pieces` VALUES (...)

-- 4. Cache invalidation
DELETE FROM Redis WHERE key LIKE 'aso_content:demo:*'

-- 5. Next read will cache miss, then cache
```

---

## Data Retention Policies

| Data Type | Storage | Retention | Reason |
|-----------|---------|-----------|--------|
| Transactional | Firestore | 90 days | Operational data |
| Analytics | BigQuery | 90 days default | Configurable per table |
| Cache | Redis | 1-60 minutes | TTL-based expiration |
| Content Assets | Cloud Storage | 30 days | Cost optimization |
| Reports | Cloud Storage | 365 days | Compliance |
| Logs | Cloud Logging | 30 days | Debugging |
| Pub/Sub Messages | Pub/Sub | 7 days | Event replay |

---

## Data Migration Patterns

### Firestore → BigQuery Sync

**Trigger:** Pub/Sub event
**Frequency:** Real-time (event-driven)
**Consistency:** Eventual

```python
@app.post("/sync-event")
async def handle_sync_event(event: PubSubEvent):
    # 1. Parse event
    data = event.data

    # 2. Transform to BigQuery schema
    row = {
        "id": data["id"],
        "timestamp": datetime.now(),
        "data": json.dumps(data)
    }

    # 3. Insert to BigQuery
    bigquery_client.insert_rows(table, [row])

    # 4. Acknowledge event
    return {"status": "synced"}
```

### Backfill Process

```python
# Backfill historical data from Firestore to BigQuery
async def backfill(collection: str, start_date: date):
    docs = firestore_client.collection(collection)\
        .where('created_at', '>=', start_date)\
        .stream()

    batch = []
    for doc in docs:
        batch.append(transform_to_bq(doc))

        if len(batch) >= 1000:
            bigquery_client.insert_rows(table, batch)
            batch = []

    # Insert remaining
    if batch:
        bigquery_client.insert_rows(table, batch)
```

---

## Schema Version Control

**Strategy:** Event-sourced schema evolution

**Version Field:** All tables include `schema_version` field

**Migration Process:**
1. Add new field as NULLABLE
2. Backfill existing rows
3. Update application code
4. Make field REQUIRED (if needed)

**Example:**
```sql
-- Step 1: Add new field
ALTER TABLE `aso_tenant_demo.content_pieces`
ADD COLUMN new_field STRING;

-- Step 2: Backfill (if needed)
UPDATE `aso_tenant_demo.content_pieces`
SET new_field = 'default_value'
WHERE new_field IS NULL;

-- Step 3: Deploy code that uses new_field

-- Step 4: Make required (optional)
-- Note: BigQuery doesn't support ALTER to make NOT NULL
-- Create new table with schema, copy data, rename
```

---

**Document Control:**
- **Version**: 1.0
- **Last Updated**: October 10, 2025
- **Next Review**: Monthly
- **Owner**: Data Team

**End of Data Model & Schema Documentation**
