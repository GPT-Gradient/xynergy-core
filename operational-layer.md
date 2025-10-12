# Xynergy Platform Backend - Operational Layer Support TRD

**Version:** 1.0  
**Date:** October 11, 2025  
**Purpose:** Define backend services and updates required to support XynergyOS operational layer  
**For:** Claude Code implementation based on existing platform codebase

---

## EXECUTIVE SUMMARY

This TRD defines backend platform updates required to support the XynergyOS operational layer, including:
- Business entity and multi-tenant data architecture
- Beta program lifecycle automation
- Permission enforcement and audit logging
- OAuth self-service infrastructure
- ASO content approval and AI confidence scoring
- Admin APIs for monitoring and management
- Living Memory backend with semantic search
- Conversational command processing

**Current State:** Core services operational (CRM, ASO, Marketing, AI Routing, Slack, Gmail), but no operational management layer.

**Target State:** Backend supports full multi-tenant operations, beta lifecycle management, and conversational interface.

---

## TABLE OF CONTENTS

1. [Architecture Overview](#1-architecture-overview)
2. [Database Schema Updates](#2-database-schema-updates)
3. [Multi-Tenant Enforcement](#3-multi-tenant-enforcement)
4. [Business Entity Service](#4-business-entity-service)
5. [Beta Program Service](#5-beta-program-service)
6. [Permission & RBAC Service](#6-permission--rbac-service)
7. [OAuth Management Service](#7-oauth-management-service)
8. [ASO Content Approval Updates](#8-aso-content-approval-updates)
9. [Admin API Gateway](#9-admin-api-gateway)
10. [Living Memory Service](#10-living-memory-service)
11. [Conversational Processing Service](#11-conversational-processing-service)
12. [Audit Logging Service](#12-audit-logging-service)
13. [Analytics & Monitoring Service](#13-analytics--monitoring-service)
14. [API Specifications](#14-api-specifications)
15. [Implementation Roadmap](#15-implementation-roadmap)

---

## 1. ARCHITECTURE OVERVIEW

### 1.1 New Services Required

**New Microservices:**
```
1. business-entity-service     - Manages entities, Continuum slots, lifecycle
2. beta-program-service        - Application processing, phase management
3. permission-service          - RBAC enforcement, role management
4. oauth-coordinator-service   - Self-service OAuth flows, token management
5. admin-api-gateway           - Aggregates admin operations, monitoring
6. living-memory-service       - Semantic search, conversation threading
7. conversational-service      - Natural language command parsing
8. audit-service               - Comprehensive logging, compliance
9. analytics-aggregator        - Cross-service metrics, reporting
```

**Updates to Existing Services:**
```
Intelligence Gateway           - Add permission middleware, tenant routing
ASO Engine                     - Add content approval, confidence scoring
CRM Engine                     - Add tenant scoping to all queries
Slack/Gmail Services           - Add tenant-scoped OAuth storage
```

### 1.2 Service Communication Patterns

**Synchronous (REST):**
- Admin operations (create tenant, approve beta user)
- Permission checks (validate user access)
- OAuth flows (generate URL, handle callback)
- Content approval (score content, approve/reject)

**Asynchronous (Pub/Sub):**
- Phase transitions (notify all services when project changes phase)
- Entity lifecycle events (project graduated, new project onboarded)
- Audit events (log to centralized audit service)
- Analytics events (usage tracking, metric aggregation)

**Event Topics:**
```
xynergy-entity-events          - Entity created, updated, graduated
xynergy-beta-events            - Application approved, phase transition
xynergy-permission-events      - Role assigned, permission changed
xynergy-oauth-events           - Connection established, token refreshed
xynergy-audit-events           - All admin actions, permission checks
xynergy-analytics-events       - Usage metrics, performance data
```

---

## 2. DATABASE SCHEMA UPDATES

### 2.1 New Firestore Collections

```
/business_entities/{entityId}
  - category: 'continuum' | 'internal_hosted' | 'client_hosted'
  - continuumGeneration?: number
  - continuumSlot?: number (1-6)
  - lifecycleState?: 'research' | 'pending' | 'active' | 'commercial' | 'archived'
  - tenantIds: string[]
  - metadata: object

/tenants/{tenantId}
  - type: 'master' | 'continuum_project' | 'internal_product' | 'client_deployment'
  - businessEntityId: string
  - parentTenantId?: string
  - status: 'active' | 'paused' | 'archived'
  - branding?: object
  - plan: string
  - features: string[]
  - featureFlags: object
  - isBetaTenant: boolean
  - betaPhase?: string
  - lifetimeAccess: string[]
  - limits: object

/users/{userId}
  - globalRole?: 'super_admin' | 'clearforge_admin'
  - tenantRoles: {
      [tenantId]: {
        role: string
        permissions: string[]
        grantedAt: Date
        grantedBy: string
      }
    }
  - activeTenantId: string
  - betaStatus?: object
  - affiliateCode?: string

/beta_applications/{applicationId}
  - projectId: string (which Continuum project)
  - email: string
  - name: string
  - company?: string
  - useCase: string
  - whyInterested: string
  - status: 'pending' | 'approved' | 'rejected' | 'waitlist'
  - phase: 'phase_1' | 'phase_2' | 'phase_3'
  - submittedAt: Date
  - reviewedAt?: Date
  - reviewedBy?: string
  - notes?: string

/permission_templates/{templateId}
  - name: string
  - description: string
  - permissions: string[]
  - targetRole: string
  - isSystemTemplate: boolean
  - createdBy: string

/oauth_connections/{connectionId}
  - userId: string
  - tenantId: string
  - provider: 'slack' | 'gmail' | 'calendar'
  - status: 'connected' | 'error' | 'expired'
  - connectedAt: Date
  - lastSyncAt?: Date
  - credentials: {
      accessToken: string (encrypted)
      refreshToken: string (encrypted)
      expiresAt: Date
      scopes: string[]
      accountInfo: object
    }
  - errorMessage?: string

/aso_content_approvals/{approvalId}
  - contentId: string
  - appId: string
  - tenantId: string
  - generatedContent: object
  - confidenceScores: {
      overall: number (0-100)
      quality: number
      brandSafety: number
      keywordRelevance: number
      competitive: number
    }
  - riskTolerance: 'conservative' | 'moderate' | 'aggressive'
  - autoApproved: boolean
  - status: 'pending' | 'approved' | 'rejected' | 'edited'
  - reviewedAt?: Date
  - reviewedBy?: string
  - rejectionReason?: string

/memory_entries/{memoryId}
  - userId: string
  - conversationId: string
  - content: string
  - extractedEntities: {
      people: string[]
      projects: string[]
      dates: Date[]
      decisions: string[]
      actionItems: string[]
    }
  - type: 'decision' | 'discussion' | 'idea' | 'action_item'
  - category: string[]
  - embedding: number[] (768-dim vector for semantic search)
  - relatedMemories: string[]
  - importance: number (1-10)
  - createdAt: Date

/audit_logs/{logId}
  - userId: string
  - tenantId?: string
  - action: string
  - resource: string
  - resourceId?: string
  - granted: boolean
  - reason?: string
  - metadata: object
  - ipAddress: string
  - userAgent: string
  - timestamp: Date
```

### 2.2 BigQuery Schema Updates

**New Tables:**

```sql
-- Analytics aggregation
CREATE TABLE xynergy_analytics.tenant_metrics (
  tenant_id STRING,
  date DATE,
  active_users INT64,
  api_calls INT64,
  storage_used_gb FLOAT64,
  costs_usd FLOAT64,
  revenue_usd FLOAT64
);

CREATE TABLE xynergy_analytics.beta_program_metrics (
  project_id STRING,
  date DATE,
  phase STRING,
  applications_submitted INT64,
  applications_approved INT64,
  active_users INT64,
  engagement_score FLOAT64,
  churn_count INT64
);

CREATE TABLE xynergy_analytics.entity_performance (
  entity_id STRING,
  entity_category STRING,
  date DATE,
  user_count INT64,
  active_user_count INT64,
  revenue_usd FLOAT64,
  costs_usd FLOAT64,
  profit_margin FLOAT64
);

CREATE TABLE xynergy_analytics.audit_events (
  log_id STRING,
  user_id STRING,
  tenant_id STRING,
  action STRING,
  resource STRING,
  granted BOOLEAN,
  timestamp TIMESTAMP
);
```

### 2.3 Tenant-Scoped Collection Updates

**All existing tenant-scoped collections need tenantId indexing:**

```
/tenants/{tenantId}/contacts/{contactId}       - Add composite index on tenantId + status
/tenants/{tenantId}/interactions/{interactionId} - Add composite index on tenantId + createdAt
/tenants/{tenantId}/projects/{projectId}       - Add composite index on tenantId + status
```

**Query Pattern:**
```typescript
// Before (hardcoded)
db.collection('contacts').where('status', '==', 'active')

// After (tenant-scoped)
db.collection(`tenants/${tenantId}/contacts`).where('status', '==', 'active')
```

---

## 3. MULTI-TENANT ENFORCEMENT

### 3.1 Tenant Isolation Middleware

**Requirements:**

1. **Create Middleware** (`middleware/tenantEnforcement.ts`)
   - Extract tenant ID from request (header `X-Tenant-Id` or user's `activeTenantId`)
   - Validate user has access to requested tenant
   - Bypass check if user is super admin
   - Attach validated `tenantId` to request object
   - Return 403 if no access

2. **Integration Points**
   - Apply to ALL endpoints that access tenant data
   - Apply after authentication middleware
   - Before route handlers execute

**Example Pattern:**
```typescript
// Middleware flow
authenticateRequest → enforceTenant → checkPermission → routeHandler
```

### 3.2 Permission Checking Middleware

**Requirements:**

1. **Create Middleware** (`middleware/checkPermission.ts`)
   - Accept required permission as parameter
   - Check user's permissions for active tenant
   - Support wildcard permissions (`crm.*`)
   - Allow super admin bypass
   - Return 403 if permission denied

2. **Permission Hierarchy**
   - Exact match: `crm.read` matches `crm.read`
   - Wildcard: `crm.*` matches any `crm.X`
   - Super wildcard: `*` matches everything

**Example Usage:**
```typescript
router.get('/contacts', 
  authenticateRequest,
  enforceTenant,
  checkPermission('crm.read'),
  async (req, res) => {
    // User verified to have access
  }
);
```

### 3.3 Super Admin Mode

**Requirements:**

1. **Detect Super Admin**
   - Check `user.globalRole === 'super_admin'`
   - Allow access to any tenant
   - Allow all permissions
   - Log all actions extensively

2. **Tenant Switching**
   - Super admin can set `X-Tenant-Id` header to any tenant
   - Normal users can only switch to tenants they have access to
   - Endpoint: `POST /api/v1/auth/switch-tenant`

3. **Impersonation**
   - Super admin can impersonate any user
   - Endpoint: `POST /api/v1/admin/users/:id/impersonate`
   - Returns temporary token with that user's permissions
   - Clear visual indicator needed (frontend)
   - All actions logged with "impersonated by X"

---

## 4. BUSINESS ENTITY SERVICE

### 4.1 Service Responsibilities

**Core Functions:**
- CRUD operations for business entities
- Continuum slot management (6 active slots)
- Graduation workflow
- Onboarding workflow
- Generation tracking
- Tenant creation/association

**Technology Stack:**
- Language: TypeScript (matches Intelligence Gateway)
- Framework: Express.js
- Database: Firestore
- Deployment: Cloud Run
- Pub/Sub: For lifecycle events

### 4.2 Continuum Slot Management

**Requirements:**

1. **Slot Tracking**
   - Maintain array of 6 active Continuum projects
   - Track which generation (Gen 1, Gen 2, etc.)
   - Prevent more than 6 active projects
   - Track pending projects waiting for slots

2. **Graduation Logic**
   - Mark project as graduating
   - Validate graduation criteria
   - Update lifecycle state to `commercial`
   - Free up slot (decrement active count)
   - Preserve beta user access
   - Publish event: `project.graduated`

3. **Onboarding Logic**
   - Check if slot available (< 6 active)
   - Move pending project to active
   - Assign to empty slot
   - Grant beta community access
   - Initialize required services
   - Publish event: `project.onboarded`

**API Endpoints:**
```
POST   /api/v1/entities/continuum                  - Create Continuum project
GET    /api/v1/entities/continuum/slots            - View 6 slots + pending
POST   /api/v1/entities/continuum/:id/graduate     - Graduate project
POST   /api/v1/entities/continuum/:id/onboard      - Onboard pending project
GET    /api/v1/entities/continuum/generations      - List all generations
```

### 4.3 Entity-Tenant Relationship

**Requirements:**

1. **Auto-Create Tenant**
   - When entity created, auto-create associated tenant
   - Link via `businessEntityId` field
   - Set appropriate tenant type based on entity category
   - Initialize feature flags

2. **Cascade Operations**
   - Archive entity → archive associated tenants
   - Update entity features → update tenant feature flags

---

## 5. BETA PROGRAM SERVICE

### 5.1 Service Responsibilities

**Core Functions:**
- Application processing and approval
- Phase transition automation
- Lifetime access management
- Beta user onboarding
- Community management
- Phase-specific feature gating

**Technology Stack:**
- Language: TypeScript
- Framework: Express.js
- Database: Firestore
- Email: SendGrid integration
- Pub/Sub: For phase events

### 5.2 Application Processing

**Requirements:**

1. **Application Submission**
   - Receive from website or API
   - Validate required fields
   - Store in `/beta_applications` collection
   - Set status to `pending`
   - Notify admin (email or Slack)

2. **Approval Workflow**
   - Admin reviews application
   - On approval:
     - Create user account if doesn't exist
     - Assign to appropriate tenant
     - Set `betaStatus` with phase and benefits
     - Grant lifetime access to ALL Continuum projects
     - Send welcome email
     - Update application status to `approved`
     - Publish event: `beta.user_approved`
   
   - On rejection:
     - Update status to `rejected`
     - Send rejection email (optional, with reason)
   
   - On waitlist:
     - Update status to `waitlist`
     - Send waitlist email

3. **Batch Approval**
   - Accept array of application IDs
   - Process all approvals in transaction
   - Generate summary report

**API Endpoints:**
```
POST   /api/v1/beta/applications                   - Submit application
GET    /api/v1/beta/applications                   - List applications (admin)
POST   /api/v1/beta/applications/:id/approve       - Approve application
POST   /api/v1/beta/applications/:id/reject        - Reject application
POST   /api/v1/beta/applications/:id/waitlist      - Move to waitlist
POST   /api/v1/beta/applications/batch-approve     - Approve multiple
```

### 5.3 Phase Transition Logic

**Requirements:**

1. **Transition Triggers**
   - Manual (admin initiates)
   - Automatic based on criteria:
     - User count threshold (P1: 100, P2: 600)
     - Time-based (3 months in phase)
     - Metric-based (validation goals met)

2. **Transition Process**
   - Check if criteria met
   - Update project's `betaPhase` field
   - Update all current beta users:
     - Mark as "graduated" from previous phase
     - Preserve all benefits
     - Add historical note
   - Open new application queue for next phase
   - Send announcement to community
   - Publish event: `beta.phase_transition`

3. **Rollback Capability**
   - If transition fails, rollback changes
   - Maintain audit trail

**API Endpoints:**
```
POST   /api/v1/beta/projects/:id/transition        - Transition to next phase
GET    /api/v1/beta/projects/:id/phase-status      - Check transition criteria
POST   /api/v1/beta/projects/:id/rollback          - Rollback transition
```

### 5.4 Lifetime Access Management

**Requirements:**

1. **Grant Access on Approval**
   - When beta user approved, grant access to ALL 6 active Continuum projects
   - Store in `user.betaStatus.lifetimeAccess` array
   - Mark which project they joined through

2. **Auto-Grant on New Project Onboard**
   - When new Continuum project onboarded:
     - Find all beta users across all phases
     - Add new project ID to their `lifetimeAccess` array
     - Publish event: `beta.access_granted`
     - Send notification email

3. **Preserve on Graduation**
   - When project graduates:
     - Do NOT remove from `lifetimeAccess`
     - Update project status but keep access
     - Beta users retain access to graduated commercial products

4. **Query Beta Benefits**
   - Endpoint to get user's full benefits
   - Shows: phase joined, all projects, perks

**API Endpoints:**
```
GET    /api/v1/beta/users/:id/benefits             - Get lifetime benefits
POST   /api/v1/beta/access/grant-all               - Grant access to all beta users
GET    /api/v1/beta/users/:id/projects             - List projects user has access to
```

---

## 6. PERMISSION & RBAC SERVICE

### 6.1 Service Responsibilities

**Core Functions:**
- Permission validation
- Role assignment/removal
- Permission template management
- Permission audit logging
- Cross-service permission checks

**Technology Stack:**
- Language: TypeScript
- Framework: Express.js
- Database: Firestore
- Cache: Redis (permission caching)

### 6.2 Permission Validation

**Requirements:**

1. **Validate Permission API**
   - Input: userId, tenantId, permission
   - Output: boolean (allowed or denied)
   - Check order:
     1. Super admin? → allow all
     2. User has tenant access? → check permissions
     3. Permission exact match or wildcard match? → allow
     4. Else → deny

2. **Caching Strategy**
   - Cache user permissions per tenant in Redis
   - TTL: 5 minutes
   - Invalidate on role/permission change

**API Endpoint:**
```
POST   /api/v1/permissions/validate                - Validate permission
  Body: { userId, tenantId, permission }
  Response: { allowed: boolean, reason?: string }
```

### 6.3 Role Management

**Requirements:**

1. **Assign Role**
   - Input: userId, tenantId, role, permissions array
   - Validate admin has permission to assign roles
   - Update user's `tenantRoles` map
   - Log assignment in audit
   - Invalidate permission cache
   - Publish event: `permission.role_assigned`

2. **Remove Role**
   - Remove tenant from user's `tenantRoles`
   - Log removal
   - Invalidate cache
   - Publish event: `permission.role_removed`

3. **Bulk Operations**
   - Assign role to multiple users
   - Remove role from multiple users

**API Endpoints:**
```
POST   /api/v1/permissions/roles/assign            - Assign role to user
DELETE /api/v1/permissions/roles/:userId/:tenantId - Remove role from user
POST   /api/v1/permissions/roles/bulk-assign       - Assign to multiple users
GET    /api/v1/permissions/roles/:userId           - Get user's roles
```

### 6.4 Permission Templates

**Requirements:**

1. **Template CRUD**
   - Create new template
   - List all templates
   - Get template details
   - Update template
   - Delete template

2. **System Templates**
   - Pre-defined templates (Beta User P1, Team Admin, etc.)
   - Marked as `isSystemTemplate: true`
   - Cannot be deleted (only modified by super admin)

3. **Apply Template**
   - One-click assign template to user
   - Copy permissions from template to user's tenant role
   - Log application

**API Endpoints:**
```
POST   /api/v1/permissions/templates               - Create template
GET    /api/v1/permissions/templates               - List templates
GET    /api/v1/permissions/templates/:id           - Get template
PATCH  /api/v1/permissions/templates/:id           - Update template
DELETE /api/v1/permissions/templates/:id           - Delete template
POST   /api/v1/permissions/templates/:id/apply     - Apply to user
```

---

## 7. OAUTH MANAGEMENT SERVICE

### 7.1 Service Responsibilities

**Core Functions:**
- OAuth URL generation (tenant-scoped)
- OAuth callback handling
- Token storage and encryption
- Token refresh automation
- Connection health monitoring
- Multi-workspace support

**Technology Stack:**
- Language: TypeScript
- Framework: Express.js
- Database: Firestore (encrypted credentials)
- Encryption: GCP KMS for token encryption
- OAuth Providers: Slack, Gmail, Google Calendar

### 7.2 Self-Service OAuth Flow

**Requirements:**

1. **Generate OAuth URL**
   - Input: userId, tenantId, provider (slack/gmail/calendar)
   - Generate state parameter (includes userId + tenantId + nonce)
   - Store state in Redis (15 min TTL) for validation
   - Build OAuth URL with proper scopes
   - Return URL to frontend

2. **Handle OAuth Callback**
   - Validate state parameter
   - Exchange authorization code for tokens
   - Encrypt access/refresh tokens using KMS
   - Store in `/oauth_connections` collection
   - Test connection (make API call to verify)
   - Return success/error to frontend

3. **Multi-Workspace (Slack)**
   - User can connect multiple Slack workspaces
   - Each workspace is separate OAuth connection
   - Each has own tokens and scopes
   - Frontend shows list of connected workspaces

**API Endpoints:**
```
GET    /api/v1/oauth/:provider/authorize-url       - Get OAuth URL
GET    /api/v1/oauth/:provider/callback            - Handle OAuth callback
DELETE /api/v1/oauth/:provider/disconnect          - Disconnect integration
GET    /api/v1/oauth/:provider/status              - Check connection status
POST   /api/v1/oauth/:provider/test                - Test connection
```

### 7.3 Token Management

**Requirements:**

1. **Token Storage**
   - Encrypt tokens before storing in Firestore
   - Use GCP KMS for encryption/decryption
   - Store: accessToken, refreshToken, expiresAt, scopes
   - Store account info (email, workspace name, etc.)

2. **Token Refresh**
   - Background job runs every 30 minutes
   - Finds tokens expiring within 1 hour
   - Refreshes tokens automatically
   - Updates stored credentials
   - Logs refresh status

3. **Token Retrieval**
   - Services request tokens via API
   - Decrypt and return fresh token
   - Auto-refresh if expired
   - Cache decrypted tokens in Redis (15 min TTL)

**Internal API:**
```
GET    /internal/v1/oauth/token                    - Get token for service
  Query: userId, tenantId, provider
  Response: { accessToken, expiresAt }
```

### 7.4 Connection Health Monitoring

**Requirements:**

1. **Health Check Job**
   - Runs hourly
   - Tests each connection with simple API call
   - Updates connection status (connected, error, expired)
   - Records error messages

2. **User Notifications**
   - Email user when connection breaks
   - In-app notification
   - Show status in integrations page

3. **Admin Dashboard**
   - View all connections across all tenants
   - See error rates per provider
   - Identify users needing reconnection
   - Alert if >10% connections failing

**API Endpoints:**
```
GET    /api/v1/admin/oauth/connections             - List all connections
GET    /api/v1/admin/oauth/health                  - Health dashboard
POST   /api/v1/admin/oauth/bulk-notify             - Notify users to reconnect
```

---

## 8. ASO CONTENT APPROVAL UPDATES

### 8.1 ASO Engine Updates Required

**Existing Service:** `/xynergy-platform/aso-engine/main.py`

**New Features Needed:**
- AI confidence scoring
- Risk tolerance settings
- Auto-approval logic
- Approval workflow APIs

### 8.2 AI Confidence Scoring

**Requirements:**

1. **Score Calculation**
   
   When content generated, calculate scores:
   
   **Quality Score (0-100):**
   - Grammar check (use grammar API or local model)
   - Readability (Flesch-Kincaid score)
   - Length appropriateness
   - Keyword density
   
   **Brand Safety Score (0-100):**
   - No prohibited words/phrases
   - No misleading claims
   - App Store guidelines compliance
   - Tone appropriateness
   
   **Keyword Relevance Score (0-100):**
   - Target keywords included
   - Keyword placement (title, subtitle, description)
   - Keyword stuffing check (penalty)
   - LSI keyword usage
   
   **Competitive Analysis Score (0-100):**
   - Compare to top-ranked apps
   - Unique value proposition clear
   - Competitive advantages highlighted
   
   **Overall Confidence:**
   - Weighted average of all scores
   - Formula: `(quality * 0.3) + (brandSafety * 0.4) + (keywordRelevance * 0.2) + (competitive * 0.1)`

2. **Store Scores**
   - Create record in `/aso_content_approvals`
   - Link to generated content
   - Include score breakdown

**API Updates:**
```python
# ASO Engine endpoint updates

POST /api/content/generate
  - Add confidence scoring after generation
  - Return scores in response
  - Auto-approve if score >= threshold

GET /api/content/:id/scores
  - Get detailed score breakdown
```

### 8.3 Risk Tolerance & Auto-Approval

**Requirements:**

1. **App Risk Settings**
   - Store per app in `/aso_apps/{appId}`
   - Fields:
     - `riskTolerance`: 'conservative' | 'moderate' | 'aggressive'
     - `autoApproveThreshold`: number (0-100)
     - `manualReviewCategories`: string[]
     - `blacklistedWords`: string[]

2. **Auto-Approval Logic**
   ```python
   if confidence_score >= app.autoApproveThreshold:
       if content_type not in app.manualReviewCategories:
           if not contains_blacklisted_words(content):
               auto_approve()
   else:
       send_for_manual_review()
   ```

3. **Conservative Mode (0-50% auto-approve)**
   - Human reviews all content
   - Only very high confidence (95%+) auto-approved
   - All categories require review

4. **Moderate Mode (51-80% auto-approve)**
   - High confidence auto-approved (80%+)
   - Medium confidence requires review
   - Low confidence rejected automatically

5. **Aggressive Mode (81-100% auto-approve)**
   - Most content auto-approved (60%+ confidence)
   - Only flagged content reviewed
   - Fast iteration

**API Endpoints:**
```python
GET    /api/apps/:id/risk-settings          - Get risk settings
PATCH  /api/apps/:id/risk-settings          - Update risk settings
```

### 8.4 Approval Workflow APIs

**Requirements:**

1. **Pending Approval List**
   - List all content awaiting approval
   - Filter by app, content type, confidence score
   - Sort by date, priority

2. **Approve Content**
   - Mark as approved
   - Update status in BigQuery
   - Notify user
   - Optionally publish to store (if API integration exists)

3. **Reject Content**
   - Mark as rejected
   - Store rejection reason
   - Notify user
   - Optionally request regeneration

4. **Edit and Approve**
   - Allow inline editing
   - Recalculate scores after edit
   - Mark as approved with edits
   - Track what was changed

**API Endpoints:**
```python
GET    /api/content/pending-approval        - List pending content
POST   /api/content/:id/approve             - Approve content
POST   /api/content/:id/reject              - Reject content
PATCH  /api/content/:id                     - Edit content
POST   /api/content/:id/regenerate          - Request regeneration
GET    /api/content/:id/approval-history    - Get approval history
```

---

## 9. ADMIN API GATEWAY

### 9.1 Service Responsibilities

**Core Functions:**
- Aggregate admin operations across all services
- Dashboard metrics collection
- Health monitoring
- Cost tracking
- Analytics reporting
- Log aggregation

**Technology Stack:**
- Language: TypeScript
- Framework: Express.js
- Databases: Firestore, BigQuery
- Monitoring: GCP Cloud Monitoring APIs
- Aggregation: In-memory caching with Redis

### 9.2 Dashboard Metrics API

**Requirements:**

1. **Overview Endpoint**
   - Aggregate metrics from multiple services
   - Total tenants (Firestore count)
   - Total users (Firestore count)
   - Active users last 7/30 days (BigQuery)
   - Continuum project slots (Business Entity Service)
   - Beta user counts per phase (Beta Service)
   - Revenue/costs (BigQuery)
   - System health (Cloud Monitoring)

2. **Caching Strategy**
   - Cache metrics in Redis
   - TTL: 5 minutes for overview
   - Invalidate on significant changes

**API Endpoint:**
```
GET    /api/v1/admin/dashboard/overview
  Response: {
    tenants: { total, active, paused },
    users: { total, active_7d, active_30d },
    continuum: { activeProjects, pendingProjects, generation },
    beta: { phase1, phase2, phase3, totalBeta },
    revenue: { total, thisMonth, lastMonth },
    costs: { total, thisMonth, lastMonth },
    health: { overall, services: [...] }
  }
```

### 9.3 Activity Feed API

**Requirements:**

1. **Aggregate Recent Events**
   - Listen to Pub/Sub topics
   - Store recent events in Redis (rolling 24 hours)
   - Types: user_signup, beta_approved, integration_connected, error_occurred

2. **Feed Endpoint**
   - Return last 50 events
   - Filter by type, tenant, severity
   - Real-time updates via WebSocket

**API Endpoint:**
```
GET    /api/v1/admin/dashboard/activity
  Query: type, limit, after
  Response: { events: [...] }
```

### 9.4 Alerts API

**Requirements:**

1. **Alert Detection**
   - Service down/degraded
   - Error rate > 5%
   - Pending beta applications > 10
   - OAuth tokens expiring soon
   - Cost spike detected

2. **Alert Storage**
   - Store active alerts in Firestore
   - Status: active, acknowledged, resolved
   - Severity: critical, warning, info

3. **Alert Notification**
   - Email to admin
   - Slack notification
   - In-app alert badge

**API Endpoint:**
```
GET    /api/v1/admin/dashboard/alerts
  Response: { alerts: [...] }

POST   /api/v1/admin/alerts/:id/acknowledge
PATCH  /api/v1/admin/alerts/:id/resolve
```

---

## 10. LIVING MEMORY SERVICE

### 10.1 Service Responsibilities

**Core Functions:**
- Conversation storage and indexing
- Entity extraction (people, projects, dates, decisions)
- Semantic search via vector embeddings
- Conversation threading
- Decision tracking
- Artifact generation from conversations

**Technology Stack:**
- Language: Python (for NLP libraries)
- Framework: FastAPI
- Database: Firestore (conversation data)
- Vector DB: Vertex AI Vector Search or Pinecone
- NLP: OpenAI Embeddings API or local models
- Deployment: Cloud Run

### 10.2 Conversation Processing

**Requirements:**

1. **Ingest Conversation**
   - Receive conversation message from frontend
   - Store in `/memory_entries` collection
   - Extract entities using NLP
   - Generate embedding vector
   - Link to related memories

2. **Entity Extraction**
   - Use NER (Named Entity Recognition) to extract:
     - People: "Shawn", "John from Acme Corp"
     - Projects: "NEXUS", "Data Democracy"
     - Dates: "next Monday", "Q3 2025"
     - Decisions: "we decided to use X"
     - Action items: "TODO: send email to..."
   
   - Store entities in `extractedEntities` field

3. **Embedding Generation**
   - Generate 768-dim vector from content
   - Use OpenAI `text-embedding-ada-002` or local model
   - Store in `embedding` field
   - Index in vector search service

**API Endpoints:**
```
POST   /api/v1/memory/ingest                     - Ingest conversation
  Body: { conversationId, userId, content }
  Response: { memoryId, extractedEntities }
```

### 10.3 Semantic Search

**Requirements:**

1. **Search Flow**
   - User query: "Find where we discussed pricing for NEXUS"
   - Generate embedding for query
   - Vector similarity search in vector DB
   - Retrieve top K results (K=10)
   - Re-rank by relevance and recency
   - Return matched memories with snippets

2. **Filters**
   - By user (my conversations only)
   - By tenant (tenant-scoped conversations)
   - By date range
   - By entity mentioned (all convos mentioning "NEXUS")
   - By type (decisions only, action items only)

**API Endpoint:**
```
POST   /api/v1/memory/search
  Body: { query, filters: {...}, limit }
  Response: { results: [{memoryId, content, relevance, extractedEntities}] }
```

### 10.4 Conversation Threading

**Requirements:**

1. **Link Related Conversations**
   - When memory ingested, find related memories
   - Link via `relatedMemories` array
   - Use semantic similarity + entity overlap

2. **Thread View**
   - Given a memory, show all related memories
   - Visualize as thread/timeline
   - Show how idea evolved over time

**API Endpoint:**
```
GET    /api/v1/memory/:id/thread                - Get conversation thread
  Response: { memories: [...], relationships: [...] }
```

### 10.5 Decision Tracking

**Requirements:**

1. **Classify as Decision**
   - Use NLP to detect decision language
   - Patterns: "we decided", "let's go with", "final decision"
   - Mark memory type as 'decision'

2. **Decision Log**
   - List all decisions across conversations
   - Show: what was decided, when, by whom, rationale
   - Link to conversation where decided

**API Endpoint:**
```
GET    /api/v1/memory/decisions                 - List all decisions
  Query: userId, tenantId, projectId, dateRange
  Response: { decisions: [...] }
```

### 10.6 Artifact Generation

**Requirements:**

1. **Generate from Conversation**
   - Input: conversationId or memoryIds array
   - Extract key points from conversation
   - Use LLM to structure into document
   - Return formatted artifact (markdown, PDF, etc.)

2. **Artifact Types**
   - Project brief
   - Requirements document
   - Email template
   - Checklist
   - Summary report

**API Endpoint:**
```
POST   /api/v1/memory/artifact/generate
  Body: { conversationId, artifactType, template? }
  Response: { artifact: { type, content, formatted } }
```

---

## 11. CONVERSATIONAL PROCESSING SERVICE

### 11.1 Service Responsibilities

**Core Functions:**
- Natural language command parsing
- Intent classification
- Entity extraction from commands
- Action execution routing
- Context management
- Multi-turn conversation handling

**Technology Stack:**
- Language: Python
- Framework: FastAPI
- NLP: OpenAI API or local LLM
- Database: Firestore (conversation state)
- Deployment: Cloud Run

### 11.2 Command Parsing

**Requirements:**

1. **Intent Classification**
   
   Classify user input into intents:
   - `query` - Asking for information ("How many users?")
   - `command` - Requesting action ("Approve top 10 applications")
   - `navigation` - Switching context ("Switch to NEXUS")
   - `creation` - Creating something ("Create new Continuum project")
   - `update` - Modifying something ("Mark NEXUS as graduating")
   
   Use LLM with prompt engineering or fine-tuned classifier

2. **Entity Extraction**
   - Extract entities from command
   - Example: "Approve the top 10 beta applications for NEXUS"
     - Intent: `command`
     - Action: `approve_beta_applications`
     - Entities: {count: 10, project: "NEXUS"}

3. **Slot Filling**
   - If missing required parameters, ask clarifying questions
   - Example: "Which project?" if user says "Show me beta users" without context

**API Endpoint:**
```
POST   /api/v1/conversation/parse
  Body: { message, userId, context }
  Response: { 
    intent, 
    action, 
    entities: {...}, 
    confidence,
    needsClarification,
    clarificationQuestion
  }
```

### 11.3 Action Execution

**Requirements:**

1. **Route to Service**
   - Based on parsed intent/action, call appropriate service
   - Examples:
     - `approve_beta_applications` → Beta Program Service
     - `switch_context` → Update user's active tenant
     - `query_metrics` → Admin API Gateway

2. **Confirmation for Destructive Actions**
   - Before executing delete, archive, or bulk operations
   - Return confirmation message to user
   - Wait for explicit "yes" before proceeding

3. **Response Generation**
   - Convert service response into natural language
   - Use LLM to generate friendly response
   - Example: "✅ Approved 10 beta applications. Welcome emails sent."

**API Endpoint:**
```
POST   /api/v1/conversation/execute
  Body: { intent, action, entities, confirmed }
  Response: { 
    success,
    message,
    data,
    needsConfirmation,
    confirmationPrompt
  }
```

### 11.4 Context Management

**Requirements:**

1. **Maintain Conversation State**
   - Store active entity (which project/tenant user is focused on)
   - Store conversation history (last 10 messages)
   - Track pending confirmations

2. **Context Switching**
   - User says "Switch to NEXUS"
   - Update user's `activeTenantId`
   - Clear previous context
   - Load new context

3. **Context Awareness**
   - User says "show me users" → use active tenant context
   - User says "that project" → reference last mentioned project

**API Endpoint:**
```
GET    /api/v1/conversation/context             - Get current context
POST   /api/v1/conversation/context/switch      - Switch context
```

---

## 12. AUDIT LOGGING SERVICE

### 12.1 Service Responsibilities

**Core Functions:**
- Log all admin actions
- Log permission checks
- Log cross-tenant access
- Log OAuth events
- Compliance reporting
- Security alerts

**Technology Stack:**
- Language: Python
- Framework: FastAPI
- Database: BigQuery (audit_events table)
- Real-time: Pub/Sub for event streaming
- Alerting: Cloud Monitoring

### 12.2 Event Logging

**Requirements:**

1. **What to Log**
   - All admin operations (create, update, delete)
   - Permission checks (allowed or denied)
   - Super admin actions
   - Impersonation events
   - Tenant switches
   - OAuth connections/disconnections
   - Beta approvals/rejections
   - Phase transitions
   - Cross-tenant queries

2. **Log Format**
   ```json
   {
     "logId": "log_abc123",
     "userId": "user_xyz",
     "tenantId": "nexus",
     "action": "beta.application.approve",
     "resource": "beta_application",
     "resourceId": "app_123",
     "granted": true,
     "reason": null,
     "metadata": {
       "applicantEmail": "user@example.com",
       "phase": "phase_1"
     },
     "ipAddress": "1.2.3.4",
     "userAgent": "Mozilla/5.0...",
     "timestamp": "2025-10-11T12:00:00Z"
   }
   ```

3. **Storage**
   - Write to BigQuery `xynergy_analytics.audit_events`
   - Also publish to Pub/Sub `xynergy-audit-events` for real-time processing
   - Retention: 7 years (compliance)

**API Endpoint:**
```
POST   /api/v1/audit/log
  Body: { userId, tenantId, action, resource, ... }
  Response: { logId, timestamp }
```

### 12.3 Security Alerting

**Requirements:**

1. **Alert Triggers**
   - Multiple permission denials (>5 in 5 minutes)
   - Super admin actions outside office hours
   - Cross-tenant access by non-admin
   - Mass deletion operations
   - Failed login attempts (>10)

2. **Alert Actions**
   - Email to security team
   - Slack notification
   - Log to Cloud Monitoring
   - Lock account if suspected breach

**Internal Service:**
- Background job monitors audit stream
- Detects patterns
- Triggers alerts

### 12.4 Compliance Reporting

**Requirements:**

1. **Generate Reports**
   - All actions by user X in date range
   - All access to tenant Y
   - All permission changes
   - All OAuth connections

2. **Export Formats**
   - CSV for auditors
   - PDF for reports
   - JSON for programmatic access

**API Endpoint:**
```
GET    /api/v1/audit/report
  Query: userId, tenantId, action, startDate, endDate, format
  Response: File download or JSON
```

---

## 13. ANALYTICS & MONITORING SERVICE

### 13.1 Service Responsibilities

**Core Functions:**
- Aggregate metrics from all services
- Tenant-level analytics
- Beta program analytics
- Cost tracking per tenant
- Performance monitoring
- Custom dashboard queries

**Technology Stack:**
- Language: Python
- Framework: FastAPI
- Database: BigQuery (analytics tables)
- Caching: Redis
- Deployment: Cloud Run

### 13.2 Tenant Metrics

**Requirements:**

1. **Collect Metrics**
   - Background job runs every 15 minutes
   - Queries each service for tenant data
   - Aggregates:
     - Active users (last 7/30 days)
     - API calls
     - Storage used
     - Features used
     - Costs incurred

2. **Store in BigQuery**
   - Table: `xynergy_analytics.tenant_metrics`
   - Partitioned by date
   - Enables time-series analysis

**API Endpoint:**
```
GET    /api/v1/analytics/tenants/:id
  Query: startDate, endDate, metrics[]
  Response: { tenant, metrics: {...}, timeSeries: [...] }
```

### 13.3 Beta Program Analytics

**Requirements:**

1. **Track Beta Metrics**
   - Applications submitted per day
   - Approval rate
   - Active beta users per phase
   - Engagement scores (logins, feature usage)
   - Churn (beta users who stopped using)
   - Referrals per user

2. **Store in BigQuery**
   - Table: `xynergy_analytics.beta_program_metrics`

**API Endpoint:**
```
GET    /api/v1/analytics/beta/:projectId
  Query: startDate, endDate
  Response: { 
    applications: { submitted, approved, rejected },
    users: { phase1, phase2, phase3, active },
    engagement: {...},
    churn: {...}
  }
```

### 13.4 Cost Tracking

**Requirements:**

1. **Aggregate Costs**
   - Query GCP Billing API
   - Break down by service
   - Allocate costs to tenants (if trackable via labels)

2. **Cost per Tenant**
   - Estimate based on resource usage
   - Store in `xynergy_analytics.tenant_metrics`
   - Calculate profit margin

**API Endpoint:**
```
GET    /api/v1/analytics/costs
  Query: startDate, endDate, groupBy (service/tenant)
  Response: { totalCosts, breakdown: [...] }
```

### 13.5 Performance Monitoring

**Requirements:**

1. **Service Health**
   - Query Cloud Monitoring API
   - Get metrics for each Cloud Run service:
     - Request count
     - Error rate
     - Response time (P50, P95, P99)
     - Instance count

2. **Store Historical Data**
   - Keep 90 days of performance data
   - Use for trend analysis

**API Endpoint:**
```
GET    /api/v1/analytics/performance
  Query: service, metric, startDate, endDate
  Response: { service, metric, timeSeries: [...] }
```

---

## 14. API SPECIFICATIONS

### 14.1 Authentication

**All admin APIs require:**
- Header: `Authorization: Bearer <token>`
- Token must have appropriate permissions
- Super admin bypasses most permission checks

### 14.2 Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {...},
  "timestamp": "2025-10-11T12:00:00Z"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "User does not have permission: beta.approve",
    "details": {...}
  },
  "timestamp": "2025-10-11T12:00:00Z"
}
```

### 14.3 Pagination

**List Endpoints:**
```
GET /api/v1/admin/users?limit=50&offset=0

Response:
{
  "success": true,
  "data": {
    "items": [...],
    "total": 234,
    "limit": 50,
    "offset": 0,
    "hasMore": true
  }
}
```

### 14.4 Filtering & Sorting

**Query Parameters:**
```
?filter[status]=active
?filter[tenantId]=nexus
?sort=createdAt:desc
?fields=id,name,email
```

---

## 15. IMPLEMENTATION ROADMAP

### 15.1 Phase 1: Foundation (Week 1-2)

**Goals:** Multi-tenant enforcement, basic admin APIs

**Tasks:**
1. Create tenant isolation middleware
2. Create permission checking middleware
3. Update Intelligence Gateway with middleware
4. Create Business Entity Service
5. Create Permission & RBAC Service
6. Add Firestore schemas (business_entities, tenants, users updates)
7. Create admin API for entity CRUD
8. Create admin API for user CRUD

**Deliverables:**
- Multi-tenant system enforced
- Super admin can manage entities and users
- Permission system operational

**Testing:**
- Unit tests for permission logic
- Integration test: Create tenant → assign user → verify isolation

---

### 15.2 Phase 2: Beta Program (Week 3-4)

**Goals:** Beta application workflow, phase management

**Tasks:**
1. Create Beta Program Service
2. Application submission API
3. Approval workflow (manual + batch)
4. Lifetime access tracking
5. Phase transition logic
6. Pub/Sub events for beta lifecycle
7. Email integration (SendGrid)
8. Beta user dashboard APIs

**Deliverables:**
- Beta applications can be submitted and approved
- Phase transitions work
- Lifetime access granted automatically

**Testing:**
- End-to-end: Submit app → approve → user created → access granted
- Phase transition: Verify all users updated

---

### 15.3 Phase 3: OAuth & Integrations (Week 5-6)

**Goals:** Self-service OAuth, connection management

**Tasks:**
1. Create OAuth Management Service
2. OAuth URL generation (tenant-scoped)
3. OAuth callback handling
4. Token encryption (GCP KMS)
5. Token refresh automation
6. Connection health monitoring
7. Multi-workspace support (Slack)
8. Admin dashboard for OAuth health

**Deliverables:**
- Users can connect Slack/Gmail themselves
- Tokens auto-refresh
- Admin can see connection health

**Testing:**
- Manual: Complete OAuth flow for Slack and Gmail
- Auto-refresh: Verify tokens refresh before expiry

---

### 15.4 Phase 4: ASO Updates (Week 7-8)

**Goals:** Content approval, AI scoring

**Tasks:**
1. Update ASO Engine with confidence scoring
2. Risk tolerance settings per app
3. Auto-approval logic
4. Approval workflow APIs
5. Pending approval queue
6. Bulk approval operations
7. Frontend integration

**Deliverables:**
- Content generated with confidence scores
- Auto-approval based on risk tolerance
- Manual approval queue functional

**Testing:**
- Generate content → verify scores calculated
- Test auto-approval at different thresholds
- Manual approval flow

---

### 15.5 Phase 5: Admin Dashboard Backend (Week 9-10)

**Goals:** Aggregated metrics, monitoring

**Tasks:**
1. Create Admin API Gateway
2. Dashboard overview endpoint (aggregate metrics)
3. Activity feed (recent events)
4. Alerts API
5. Tenant management endpoints
6. Beta program management endpoints
7. Infrastructure monitoring endpoints
8. Cost tracking

**Deliverables:**
- Admin dashboard backend complete
- Metrics aggregated from all services
- Real-time activity feed

**Testing:**
- Load dashboard → verify metrics accurate
- Create entity → verify appears in activity feed

---

### 15.6 Phase 6: Living Memory (Week 11-12)

**Goals:** Semantic search, conversation threading

**Tasks:**
1. Create Living Memory Service
2. Conversation ingestion
3. Entity extraction (NLP)
4. Embedding generation
5. Vector search setup (Vertex AI or Pinecone)
6. Semantic search API
7. Conversation threading
8. Decision tracking
9. Artifact generation

**Deliverables:**
- Conversations stored and indexed
- Semantic search functional
- Artifacts can be generated

**Testing:**
- Ingest conversations → search → verify relevant results
- Generate artifact from conversation

---

### 15.7 Phase 7: Conversational Interface (Week 13-14)

**Goals:** Natural language commands

**Tasks:**
1. Create Conversational Processing Service
2. Intent classification
3. Entity extraction from commands
4. Action routing
5. Context management
6. Multi-turn conversation handling
7. Confirmation workflows
8. Response generation

**Deliverables:**
- Natural language commands work
- Context switching via conversation
- Confirmation for destructive actions

**Testing:**
- Manual: Send commands → verify actions executed
- Context: Switch tenants via command

---

### 15.8 Phase 8: Audit & Analytics (Week 15-16)

**Goals:** Comprehensive logging, reporting

**Tasks:**
1. Create Audit Logging Service
2. Audit event schema
3. BigQuery audit table
4. Security alerting
5. Compliance reporting
6. Create Analytics & Monitoring Service
7. Tenant metrics aggregation
8. Beta analytics
9. Cost tracking
10. Performance monitoring

**Deliverables:**
- All actions logged
- Security alerts functional
- Analytics dashboards populated

**Testing:**
- Perform admin action → verify logged
- Generate compliance report

---

## 16. DEPLOYMENT STRATEGY

### 16.1 Service Deployment Order

1. **Permission Service** (blocking - needed by all)
2. **Business Entity Service**
3. **Beta Program Service**
4. **OAuth Management Service**
5. **Admin API Gateway**
6. **Living Memory Service**
7. **Conversational Service**
8. **Audit Service**
9. **Analytics Service**

### 16.2 Rollout Strategy

**Week 1-2: Internal Testing**
- Deploy to dev environment
- Shawn tests all admin features
- Fix bugs

**Week 3-4: Staging**
- Deploy to staging environment
- Onboard first 10 NEXUS beta users
- Monitor errors

**Week 5-6: Production**
- Deploy to production
- Gradual rollout (10% → 50% → 100% traffic)
- Monitor closely

### 16.3 Rollback Plan

**For Each Service:**
- Tag previous working version
- Keep previous version deployed (0 traffic)
- If issues, route traffic to previous version
- Fix issues, redeploy

---

## 17. MONITORING & ALERTS

### 17.1 Service Health Monitoring

**Metrics to Track:**
- Request count per service
- Error rate (target: <1%)
- Response time P95 (target: <500ms)
- Instance count
- Memory usage
- CPU usage

**Alerts:**
- Error rate >5% for 5 minutes → Email + Slack
- Response time P95 >1s for 5 minutes → Email
- Service down → Immediate page

### 17.2 Business Metrics Monitoring

**Metrics to Track:**
- Beta applications per day
- Approval rate
- Active users per tenant
- OAuth connection failures
- Cost per tenant

**Alerts:**
- >10 pending beta applications → Email
- OAuth failure rate >10% → Email
- Cost spike >20% vs previous week → Email

---

## 18. SECURITY CONSIDERATIONS

### 18.1 Data Encryption

**At Rest:**
- Firestore: Encrypted by default (GCP)
- BigQuery: Encrypted by default
- OAuth tokens: Encrypted with GCP KMS before storing

**In Transit:**
- All APIs use HTTPS
- Service-to-service: Use GCP VPC (private network)

### 18.2 Secret Management

**All secrets in GCP Secret Manager:**
- JWT signing keys
- OAuth client secrets
- Encryption keys
- API keys for external services

**Access Control:**
- Only service accounts can access secrets
- Principle of least privilege

### 18.3 Input Validation

**All APIs:**
- Validate all inputs (type, length, format)
- Sanitize user input (prevent injection)
- Use Pydantic (Python) or TypeScript interfaces

### 18.4 Rate Limiting

**Per User:**
- 100 requests per minute per API
- 1000 requests per hour

**Per Tenant:**
- Based on plan (beta unlimited, paid tiers have limits)

---

## 19. TESTING REQUIREMENTS

### 19.1 Unit Tests

**All Services:**
- Test business logic in isolation
- Mock external dependencies
- Target: >80% code coverage

### 19.2 Integration Tests

**Critical Flows:**
- Beta application approval → user creation
- OAuth connection → token storage → API usage
- Permission check → access granted/denied
- Content generation → scoring → approval

### 19.3 End-to-End Tests

**User Journeys:**
1. Admin creates Continuum project → beta users apply → approved → access all projects
2. User connects Slack → messages sync → appear in UI
3. ASO user generates content → approves → published

### 19.4 Load Tests

**Scenarios:**
- 100 concurrent users
- 1000 requests per minute
- Verify no degradation

---

## 20. SUCCESS CRITERIA

### 20.1 Technical Success

- ✅ All 9 new services deployed to production
- ✅ All existing services updated with multi-tenant enforcement
- ✅ All integration tests passing
- ✅ Load tests passing (100 concurrent users)
- ✅ Zero data breaches or permission bypass issues
- ✅ Error rate <1%
- ✅ P95 response time <500ms

### 20.2 Functional Success

- ✅ Shawn can manage 6 Continuum projects
- ✅ 100 NEXUS beta users onboarded successfully
- ✅ Users can connect Slack/Gmail via OAuth
- ✅ ASO content approval workflow functional
- ✅ Admin dashboard shows accurate metrics
- ✅ Natural language commands work for common operations
- ✅ Living Memory enables semantic search

### 20.3 Operational Success

- ✅ No manual Firestore edits required for operations
- ✅ Beta approval takes <5 minutes per user
- ✅ OAuth connection works first try >95% of time
- ✅ All admin actions audited
- ✅ Security alerts functional

---

**Document Version:** 1.0  
**Last Updated:** October 11, 2025  
**For Implementation By:** Claude Code  
**Maintained By:** Platform Engineering Team