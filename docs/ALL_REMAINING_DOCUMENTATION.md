# Xynergy Platform - Complete Documentation Bundle
## Remaining Technical Documentation

**Document Version:** 1.0
**Last Updated:** October 10, 2025
**Bundle Includes:** API Specs, Algorithms, State Machines, Data Flows, Sequence Diagrams, Integrations, Error Handling, Security, Performance, Deployment, Operations

---

# Table of Contents

1. [API Specification Document](#api-specification-document)
2. [Algorithm Specifications](#algorithm-specifications)
3. [State Machine Diagrams](#state-machine-diagrams)
4. [Data Flow Diagrams](#data-flow-diagrams)
5. [Sequence Diagrams](#sequence-diagrams)
6. [Integration Specifications](#integration-specifications)
7. [Error Handling & Edge Cases](#error-handling--edge-cases)
8. [Security Architecture](#security-architecture)
9. [Performance & Scaling](#performance--scaling)
10. [Deployment Runbook](#deployment-runbook)
11. [System Operations Manual](#system-operations-manual)

---

# API Specification Document

## Overview

All Xynergy Platform services expose RESTful APIs using FastAPI with automatic OpenAPI documentation at `/docs`.

### Common Patterns

**Base URL Pattern:**
```
https://{service-name}-835612502919.us-central1.run.app
```

**Authentication:**
- **Method 1:** Bearer Token
  ```
  Authorization: Bearer {api_key}
  ```
- **Method 2:** X-API-Key Header
  ```
  X-API-Key: {api_key}
  ```

**Standard Headers:**
```
X-Request-ID: req_abc123          # Request tracing
X-Tenant-ID: demo                 # Multi-tenancy
Content-Type: application/json
```

**Standard Responses:**
```json
{
  "success": true,
  "data": {...},
  "metadata": {
    "request_id": "req_abc123",
    "timestamp": "2025-10-10T12:00:00Z"
  }
}
```

**Error Response:**
```json
{
  "detail": "Error message",
  "status_code": 400,
  "request_id": "req_abc123",
  "error_type": "ValidationError"
}
```

---

## Core API Endpoints

### ASO Engine API

**Base URL:** `https://aso-engine-835612502919.us-central1.run.app`

#### GET /api/content
**Purpose:** List content pieces with caching and partition pruning

**Request:**
```http
GET /api/content?tenant_id=demo&status=published&days_back=90&limit=50
X-API-Key: {api_key}
```

**Parameters:**
- `tenant_id` (string, default: "demo"): Tenant identifier
- `status` (string, optional): Filter by status (draft, published, archived)
- `days_back` (integer, 1-730, default: 90): Days to look back
- `limit` (integer, 1-1000, default: 50): Max results

**Response (200 OK):**
```json
{
  "tenant_id": "demo",
  "count": 25,
  "content": [
    {
      "content_id": "abc123",
      "content_type": "hub",
      "keyword_primary": "SEO best practices",
      "title": "Complete Guide to SEO",
      "status": "published",
      "ranking_position": 5,
      "monthly_traffic": 1500,
      "performance_score": 85.5,
      "created_at": "2025-09-10T12:00:00Z",
      "published_at": "2025-09-12T12:00:00Z"
    }
  ]
}
```

**Business Rules:**
- Partition pruning reduces BigQuery cost by 70-90%
- Cache hit returns in <10ms
- Cache miss queries BigQuery, stores result for 2 minutes
- Results sorted by `created_at DESC`

---

#### POST /api/content
**Purpose:** Create new content piece

**Request:**
```http
POST /api/content
X-API-Key: {api_key}
Content-Type: application/json

{
  "tenant_id": "demo",
  "content_type": "hub",
  "keyword_primary": "SEO best practices",
  "keyword_secondary": ["on-page SEO", "technical SEO"],
  "title": "Complete Guide to SEO",
  "meta_description": "Learn SEO best practices...",
  "url": "https://example.com/seo-guide",
  "word_count": 2500
}
```

**Validation Rules:**
- `keyword_primary`: Required, max 200 characters
- `content_type`: Must be "hub" or "spoke"
- If "spoke", `hub_id` required
- `word_count`: Min 300, recommended 1500+

**Response (201 Created):**
```json
{
  "content_id": "abc123",
  "status": "draft",
  "created_at": "2025-10-10T12:00:00Z",
  "message": "Content created successfully"
}
```

**Rate Limit:** 10 requests/minute (expensive tier)

---

#### GET /api/keywords
**Purpose:** List tracked keywords with caching

**Request:**
```http
GET /api/keywords?tenant_id=demo&priority=tier1&days_back=30&limit=100
```

**Response (200 OK):**
```json
{
  "tenant_id": "demo",
  "count": 45,
  "keywords": [
    {
      "keyword": "SEO best practices",
      "search_volume": 5400,
      "difficulty_score": 45.5,
      "kgr_score": 0.18,
      "intent": "informational",
      "current_ranking": 12,
      "target_ranking": 5,
      "priority": "tier1",
      "last_checked": "2025-10-10T06:00:00Z"
    }
  ]
}
```

**Cache TTL:** 180 seconds (3 minutes)

---

#### GET /api/opportunities
**Purpose:** List SEO opportunities (low-hanging fruit)

**Algorithm:**
```sql
WHERE current_ranking > 10
  AND current_ranking <= 30
  AND difficulty_score < 50
  AND search_volume > 100
ORDER BY (search_volume / difficulty_score) DESC
```

**Response:**
```json
{
  "tenant_id": "demo",
  "count": 12,
  "opportunities": [
    {
      "opportunity_id": "opp_xyz",
      "opportunity_type": "low_hanging_fruit",
      "keyword": "local SEO tips",
      "confidence_score": 0.85,
      "estimated_traffic": 450,
      "estimated_difficulty": 35,
      "recommendation": "Create comprehensive guide targeting this keyword",
      "detected_at": "2025-10-10T12:00:00Z"
    }
  ]
}
```

**Cache TTL:** 240 seconds (4 minutes)

---

### AI Routing Engine API

**Base URL:** `https://ai-routing-engine-835612502919.us-central1.run.app`

#### POST /api/generate
**Purpose:** Generate AI response with intelligent routing

**Request:**
```http
POST /api/generate
X-API-Key: {api_key}
Content-Type: application/json

{
  "prompt": "What are the latest SEO trends in 2025?",
  "max_tokens": 1000,
  "temperature": 0.7,
  "model_preference": "auto"
}
```

**Routing Logic:**
1. Analyze prompt complexity
2. If complex (contains "latest", "current", "today") → Abacus AI
3. If Abacus unavailable → OpenAI
4. If simple factual → Internal AI

**Response (200 OK):**
```json
{
  "response": {
    "text": "The latest SEO trends in 2025 include...",
    "model": "abacus-ai",
    "provider": "abacus",
    "tokens": {
      "prompt": 15,
      "completion": 250,
      "total": 265
    }
  },
  "metadata": {
    "routing_decision": "complex_query",
    "cached": false,
    "cost_estimate": 0.015,
    "latency_ms": 1250,
    "token_optimization": {
      "original_max": 1000,
      "optimized_max": 500,
      "saved_tokens": 500
    }
  }
}
```

**Cost by Provider:**
- Abacus AI: $0.015/request
- OpenAI: $0.025/request
- Internal AI: $0.001/request

**Cache:** 1-hour TTL on AI responses

**Rate Limit:** 30 requests/minute (AI tier)

---

### Marketing Engine API

**Base URL:** `https://marketing-engine-835612502919.us-central1.run.app`

#### POST /campaigns/create
**Purpose:** Create AI-powered marketing campaign

**Request:**
```http
POST /campaigns/create
X-API-Key: {api_key}
Content-Type: application/json

{
  "tenant_id": "demo",
  "business_type": "SaaS",
  "target_audience": "Small business owners, 25-45",
  "budget_range": "$5,000-$10,000",
  "campaign_goals": ["brand_awareness", "lead_generation"],
  "preferred_channels": ["social_media", "content_marketing"]
}
```

**Validation:**
- `business_type`: Max 200 chars
- `target_audience`: Max 500 chars
- `budget_range`: Regex `^\$[\d,]+-\$[\d,]+$`

**Response (201 Created):**
```json
{
  "campaign_id": "camp_abc123",
  "campaign_name": "SaaS Growth Campaign Q4 2025",
  "strategy": {
    "recommended_channels": [
      "LinkedIn Ads",
      "Content Marketing Blog",
      "Email Nurture Sequence"
    ],
    "content_strategy": "Focus on thought leadership...",
    "targeting_approach": "LinkedIn targeting: Company size 10-50..."
  },
  "estimated_reach": 15000,
  "budget_allocation": {
    "linkedin_ads": 4000,
    "content_creation": 3000,
    "email_marketing": 2000,
    "contingency": 1000
  },
  "created_at": "2025-10-10T12:00:00Z"
}
```

**AI Integration:**
- Routes through AI Routing Engine
- Checks cache for similar campaigns (1-hour TTL)
- Stores campaign in Firestore
- Publishes `campaign_created` event to Pub/Sub

**Rate Limit:** 10 requests/minute (expensive tier)

---

## Standard Endpoints (All Services)

### GET /health
**Purpose:** Service health check

**Response:**
```json
{
  "service": "aso-engine",
  "status": "healthy",
  "timestamp": "2025-10-10T12:00:00Z",
  "checks": {
    "firestore": {"status": "healthy"},
    "bigquery": {"status": "healthy", "latency_ms": 45},
    "redis": {"status": "healthy"},
    "circuit_breaker": {"state": "CLOSED", "failure_count": 0}
  },
  "resources": {
    "memory_mb": 234.5,
    "cpu_percent": 15.3,
    "threads": 12
  },
  "performance": {
    "total_requests": 1543,
    "avg_latency_ms": 123.4
  }
}
```

### POST /execute
**Purpose:** Workflow orchestration endpoint

**Request:**
```json
{
  "action": "service_specific_action",
  "parameters": {...},
  "workflow_context": {
    "workflow_id": "wf_123",
    "correlation_id": "req_abc"
  }
}
```

---

# Algorithm Specifications

## 1. AI Request Routing Algorithm

**Purpose:** Route AI requests to optimal provider based on complexity and cost

**Input:**
- `prompt`: User's text prompt
- `max_tokens`: Optional token limit
- `temperature`: Creativity parameter

**Algorithm:**
```python
def route_ai_request(prompt: str, max_tokens: int = None) -> AIProvider:
    """
    Routes AI requests to most cost-effective provider while maintaining quality.

    Returns: (provider, optimized_tokens, metadata)
    """

    # Step 1: Complexity Analysis
    complexity = analyze_complexity(prompt)

    # Step 2: Token Optimization
    if max_tokens is None:
        max_tokens = calculate_optimal_tokens(prompt, complexity)

    # Step 3: Provider Selection
    if complexity in ["high", "medium"]:
        # Complex queries need external AI
        if provider_available("abacus"):
            return AbacusAI, max_tokens, {"reason": "complex_query", "cost": 0.015}
        elif provider_available("openai"):
            return OpenAI, max_tokens, {"reason": "abacus_unavailable", "cost": 0.025}

    # Simple queries use internal AI
    return InternalAI, max_tokens, {"reason": "simple_query", "cost": 0.001}


def analyze_complexity(prompt: str) -> str:
    """
    Analyzes prompt complexity using multiple signals.

    Returns: "high", "medium", or "low"
    """
    score = 0

    # Signal 1: Length (longer = more complex)
    if len(prompt) > 500:
        score += 2
    elif len(prompt) > 200:
        score += 1

    # Signal 2: Keywords indicating complexity
    complex_keywords = [
        "latest", "current", "today", "news", "recent",
        "research", "analyze", "compare", "detailed"
    ]
    for keyword in complex_keywords:
        if keyword in prompt.lower():
            score += 1

    # Signal 3: Question type
    if any(word in prompt.lower() for word in ["why", "how", "explain"]):
        score += 1

    # Signal 4: Multi-part questions
    if prompt.count("?") > 1:
        score += 1

    # Classify based on score
    if score >= 4:
        return "high"
    elif score >= 2:
        return "medium"
    else:
        return "low"


def calculate_optimal_tokens(prompt: str, complexity: str) -> int:
    """
    Calculates optimal max_tokens to minimize cost without truncation.

    Saves 20-30% on AI costs.
    """
    # Base allocation by complexity
    base_tokens = {
        "low": 500,      # Short factual answers
        "medium": 1500,  # Moderate explanations
        "high": 4096     # Detailed analysis
    }

    tokens = base_tokens[complexity]

    # Adjust based on prompt length (longer prompt = longer response expected)
    prompt_length = len(prompt.split())
    if prompt_length > 100:
        tokens = int(tokens * 1.5)

    return min(tokens, 4096)  # Cap at model maximum
```

**Performance:**
- 89% cost reduction vs pure OpenAI
- 78% of queries routed to Internal AI
- <5% misclassification rate

---

## 2. Keyword Golden Ratio (KGR) Algorithm

**Purpose:** Identify low-competition keyword opportunities

**Formula:**
```
KGR = (Number of "allintitle" results) / (Monthly search volume)
```

**Interpretation:**
- KGR < 0.25: Excellent opportunity (easy to rank)
- KGR < 1.0: Good opportunity
- KGR > 1.0: Competitive

**Implementation:**
```python
def calculate_kgr(keyword: str) -> Dict[str, Any]:
    """
    Calculates Keyword Golden Ratio for SEO opportunity analysis.

    Steps:
    1. Get monthly search volume from keyword API
    2. Count "allintitle" results (titles containing exact phrase)
    3. Calculate ratio
    4. Classify opportunity

    Returns:
        {
            "kgr_score": 0.18,
            "search_volume": 1200,
            "allintitle_results": 220,
            "opportunity_level": "Excellent",
            "recommendation": "Target this keyword..."
        }
    """

    # Step 1: Get search volume
    search_volume = get_search_volume(keyword)

    # Step 2: Count allintitle results
    # Search: allintitle:"exact keyword phrase"
    allintitle_count = count_allintitle_results(keyword)

    # Step 3: Calculate KGR
    if search_volume == 0:
        return {"error": "No search volume data"}

    kgr_score = allintitle_count / search_volume

    # Step 4: Classify
    if kgr_score < 0.25:
        level = "Excellent"
        recommendation = f"High-priority target. Low competition ({allintitle_count} pages) vs decent volume ({search_volume})"
    elif kgr_score < 1.0:
        level = "Good"
        recommendation = f"Good opportunity. Moderate effort required"
    else:
        level = "Competitive"
        recommendation = f"High competition. Consider long-tail variations"

    return {
        "kgr_score": round(kgr_score, 3),
        "search_volume": search_volume,
        "allintitle_results": allintitle_count,
        "opportunity_level": level,
        "recommendation": recommendation
    }
```

---

## 3. SEO Opportunity Detection Algorithm

**Purpose:** Find low-hanging fruit SEO opportunities

**Criteria:**
1. Current ranking: 11-30 (page 2-3 of Google)
2. Difficulty score: < 50 (medium difficulty)
3. Search volume: > 100 (worth targeting)
4. Opportunity score: `search_volume / difficulty_score`

**SQL Implementation:**
```sql
WITH ranked_keywords AS (
  SELECT
    keyword,
    search_volume,
    difficulty_score,
    current_ranking,
    kgr_score,
    -- Opportunity score (higher = better)
    (search_volume / NULLIF(difficulty_score, 0)) as opportunity_score,
    -- Ranking improvement potential
    (30 - current_ranking) as rank_improvement_potential,
    last_checked
  FROM `aso_tenant_{tenant_id}.keywords`
  WHERE DATE(last_checked) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    AND current_ranking > 10          -- Not on page 1
    AND current_ranking <= 30         -- Still in top 30
    AND difficulty_score < 50         -- Not too hard
    AND search_volume > 100           -- Worth the effort
)
SELECT
  keyword,
  current_ranking,
  search_volume,
  difficulty_score,
  kgr_score,
  opportunity_score,
  rank_improvement_potential,
  CASE
    WHEN kgr_score < 0.25 AND opportunity_score > 50 THEN 'High Priority'
    WHEN kgr_score < 1.0 AND opportunity_score > 20 THEN 'Medium Priority'
    ELSE 'Low Priority'
  END as priority_level
FROM ranked_keywords
ORDER BY opportunity_score DESC, kgr_score ASC
LIMIT 50;
```

**Recommendation Logic:**
```python
def generate_opportunity_recommendation(opportunity: Dict) -> str:
    """
    Generates actionable recommendation for SEO opportunity.
    """
    keyword = opportunity["keyword"]
    ranking = opportunity["current_ranking"]
    volume = opportunity["search_volume"]
    difficulty = opportunity["difficulty_score"]
    kgr = opportunity["kgr_score"]

    if ranking <= 15 and kgr < 0.25:
        return f"Quick win: Optimize existing content for '{keyword}'. Small improvements could push to page 1."

    elif ranking <= 20 and volume > 500:
        return f"High-value target: Create comprehensive guide for '{keyword}'. Volume of {volume} justifies effort."

    elif kgr < 0.25:
        return f"Low competition: '{keyword}' has KGR of {kgr:.2f}. Easy to rank with quality content."

    else:
        return f"Standard opportunity: Target '{keyword}' with well-optimized content. Expected difficulty: {difficulty}/100."
```

---

## 4. Hub-Spoke Content Model Algorithm

**Purpose:** Organize content in hierarchical structure for SEO

**Structure:**
```
Hub (pillar content)
├─ Spoke 1 (supporting content)
├─ Spoke 2 (supporting content)
└─ Spoke 3 (supporting content)
```

**Algorithm:**
```python
def create_hub_spoke_structure(primary_keyword: str, target_volume: int) -> Dict:
    """
    Creates hub-spoke content structure for topic cluster SEO.

    Strategy:
    1. Hub targets main keyword (high volume, competitive)
    2. Spokes target long-tail variations (lower volume, easier)
    3. All spokes link back to hub
    4. Hub gains authority from spoke cluster

    Example:
        Hub: "SEO Best Practices" (vol: 5400)
        ├─ Spoke: "On-page SEO best practices" (vol: 880)
        ├─ Spoke: "Technical SEO best practices" (vol: 590)
        └─ Spoke: "Local SEO best practices" (vol: 720)
    """

    # Step 1: Create hub
    hub = {
        "content_type": "hub",
        "keyword_primary": primary_keyword,
        "target_length": 3000,  # Comprehensive guide
        "sections": generate_hub_sections(primary_keyword)
    }

    # Step 2: Identify spoke keywords (long-tail variations)
    spoke_keywords = find_long_tail_keywords(primary_keyword)

    # Step 3: Create spokes
    spokes = []
    for spoke_kw in spoke_keywords[:10]:  # Limit to 10 spokes
        spoke = {
            "content_type": "spoke",
            "keyword_primary": spoke_kw["keyword"],
            "target_length": 1500,  # Focused article
            "hub_reference": primary_keyword,
            "internal_link": f"Link to hub article about {primary_keyword}"
        }
        spokes.append(spoke)

    return {
        "hub": hub,
        "spokes": spokes,
        "total_target_volume": sum(s["search_volume"] for s in spoke_keywords),
        "implementation_order": ["hub_first", "then_spokes"]
    }


def generate_hub_sections(keyword: str) -> List[str]:
    """
    Generates comprehensive sections for hub content.
    """
    # Use AI to analyze keyword and suggest sections
    prompt = f"What are the key topics to cover in a comprehensive guide about '{keyword}'?"
    sections = ai_routing_engine.generate(prompt)

    return sections
```

---

# State Machine Diagrams

## 1. Circuit Breaker State Machine

**States:** CLOSED, OPEN, HALF_OPEN

```
[CLOSED] ──(5 failures)──> [OPEN] ──(60s timeout)──> [HALF_OPEN]
    ↑                                                      │
    │                                                      │
    └──────────────(success)────────────────────────────┘
                                                           │
                                             (failure)─────┘
```

**State Descriptions:**

**CLOSED (Normal Operation):**
- All requests pass through to external service
- Track success/failure count
- If 5 consecutive failures → transition to OPEN

**OPEN (Failure Mode):**
- Block all requests to external service
- Return fallback response immediately
- No additional load on failing service
- After 60 seconds → transition to HALF_OPEN

**HALF_OPEN (Testing Recovery):**
- Allow 1 test request through
- If success → transition to CLOSED (service recovered)
- If failure → transition back to OPEN (still failing)

**Implementation:**
```python
class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.config = config

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitBreakerState.OPEN:
            # Check if timeout elapsed
            if time.time() - self.last_failure_time > self.config.timeout:
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                # Return fallback
                return self._fallback()

        try:
            result = await func(*args, **kwargs)

            # Success - reset or close
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN

            raise e
```

---

## 2. Content Lifecycle State Machine

**States:** DRAFT → REVIEW → PUBLISHED → ARCHIVED

```
[DRAFT] ──(submit)──> [REVIEW] ──(approve)──> [PUBLISHED] ──(archive)──> [ARCHIVED]
   ↑                      │                         │
   │                      │                         │
   └──(reject)────────────┘        (unpublish)──────┘
```

**Transitions:**

| From | To | Trigger | Business Rules |
|------|----|---------| ---------------|
| DRAFT | REVIEW | submit_for_review | Author completes content, runs plagiarism check |
| REVIEW | PUBLISHED | approve | Editor approves, content goes live |
| REVIEW | DRAFT | reject | Editor rejects, author must revise |
| PUBLISHED | DRAFT | unpublish | Content needs major updates |
| PUBLISHED | ARCHIVED | archive | Content outdated or no longer relevant |
| ARCHIVED | DRAFT | restore | Restore and update archived content |

---

## 3. Campaign Status State Machine

```
[DRAFT] ──(activate)──> [ACTIVE] ──(complete)──> [COMPLETED]
   ↑                       │  ↑
   │                       │  │
   │      (pause)──────────┘  │
   │                          │
   └──────(resume)────────────┘
```

---

# Data Flow Diagrams

## Level 0: Context Diagram

```
┌───────────┐
│   Users   │
└─────┬─────┘
      │ HTTP Requests
      ▼
┌─────────────────────────────────┐
│                                 │
│     Xynergy Platform            │
│                                 │
│  - Marketing                    │
│  - ASO                          │──────> External AI APIs
│  - Analytics                    │       (Abacus, OpenAI)
│  - Content                      │
│                                 │
└─────────────────────────────────┘
      │
      ▼ Data Storage
┌─────────────────┐
│ GCP (Firestore, │
│ BigQuery, Redis)│
└─────────────────┘
```

---

## Level 1: System Decomposition

```
┌─────────┐                    ┌──────────────┐
│ Client  │──HTTP Request────> │ API Gateway  │
└─────────┘                    │   Layer      │
                               └──────┬───────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
              ┌─────▼────┐     ┌──────▼──────┐  ┌──────▼────┐
              │Marketing │     │  ASO Engine │  │ Analytics │
              │  Engine  │     │             │  │  Services │
              └─────┬────┘     └──────┬──────┘  └──────┬────┘
                    │                 │                │
                    └─────────┬───────┴────────────────┘
                              │
                        ┌─────▼──────┐
                        │ AI Routing │
                        │   Engine   │
                        └─────┬──────┘
                              │
                    ┌─────────┼─────────┐
                    │                   │
              ┌─────▼─────┐      ┌──────▼───────┐
              │ External  │      │  Internal AI │
              │ AI (Abacus│      │   Service    │
              │  /OpenAI) │      └──────────────┘
              └───────────┘
```

---

## Level 2: Content Creation Data Flow

```
[User] ──1. Create Content Request──> [ASO Engine]
                                            │
                                            │ 2. Validate
                                            ▼
                                       [Pydantic Model]
                                            │
                                            │ 3. Store
                                            ▼
                                       [Firestore]
                                            │
                                            │ 4. Publish Event
                                            ▼
                                       [Pub/Sub Topic: content-created]
                                            │
                    ┌───────────────────────┼───────────────────┐
                    │                       │                   │
                    ▼                       ▼                   ▼
            [Validation Service]    [BigQuery Sync]    [Analytics Service]
                    │                       │                   │
                    │ 5a. Fact Check        │ 5b. Insert Row    │ 5c. Update Metrics
                    ▼                       ▼                   ▼
            [validation_analytics]   [aso_tenant_demo]    [xynergy_analytics]
```

---

## Level 3: AI Request Flow with Caching

```
[User Request] ──1. Generate AI Response──> [AI Routing Engine]
                                                     │
                                                     │ 2. Check Cache
                                                     ▼
                                              [Redis Cache]
                                                 /       \
                                            Hit /         \ Miss
                                               /           \
                                              ▼             ▼
                                    [Return Cached]    [Route Request]
                                    (< 10ms)                │
                                                            │ 3. Analyze Complexity
                                                            ▼
                                                   ┌────────┴────────┐
                                             Complex│           Simple│
                                                   ▼                 ▼
                                              [Abacus AI]     [Internal AI]
                                              ($0.015)         ($0.001)
                                                   │                 │
                                                   └────────┬────────┘
                                                            │
                                                            │ 4. Store in Cache
                                                            ▼
                                                      [Redis Cache]
                                                            │
                                                            │ 5. Return
                                                            ▼
                                                        [Response]
```

---

# Sequence Diagrams

## 1. Campaign Creation Workflow

```
User          API Gateway    Marketing Engine    AI Routing    Firestore    Pub/Sub
 │                │                  │                │            │           │
 │──POST /campaigns/create──>│       │                │            │           │
 │                │                  │                │            │           │
 │                │──verify_api_key──│                │            │           │
 │                │<──200 OK────────│                │            │           │
 │                │                  │                │            │           │
 │                │──forward request─>│               │            │           │
 │                │                  │                │            │           │
 │                │                  │──check cache──>│            │           │
 │                │                  │<──cache miss───│            │           │
 │                │                  │                │            │           │
 │                │                  │──generate AI──>│            │           │
 │                │                  │                │            │           │
 │                │                  │                │──route────>│[External AI]
 │                │                  │                │<──response──│           │
 │                │                  │<──AI response──│            │           │
 │                │                  │                │            │           │
 │                │                  │──store campaign────────────>│           │
 │                │                  │<──success───────────────────│           │
 │                │                  │                │            │           │
 │                │                  │──publish event──────────────────────────>│
 │                │                  │<──ack───────────────────────────────────│
 │                │                  │                │            │           │
 │                │<──201 Created────│                │            │           │
 │<──201 Created──│                  │                │            │           │
 │                │                  │                │            │           │
```

**Timeline:**
- t0: Request received
- t1: Authentication (5ms)
- t2: Cache check (3ms)
- t3: AI generation (1-3 seconds depending on provider)
- t4: Firestore write (50ms)
- t5: Pub/Sub publish (20ms)
- Total: ~1.1-3.1 seconds

---

## 2. ASO Content Listing with Cache

```
User       ASO Engine    Redis Cache    BigQuery
 │              │              │            │
 │──GET /api/content?days_back=90&limit=50─>│
 │              │              │            │
 │              │──generate cache key───────>│
 │              │   "content_demo_published_90_50"
 │              │              │            │
 │              │──GET key────>│            │
 │              │              │            │
 │              │<──NULL (miss)│            │
 │              │              │            │
 │              │──query with partition pruning───>│
 │              │   WHERE DATE(created_at) >=      │
 │              │   DATE_SUB(CURRENT_DATE(),       │
 │              │   INTERVAL 90 DAY)               │
 │              │              │            │
 │              │<──results (250-550ms)────│
 │              │              │            │
 │              │──SET key + TTL=120s─────>│
 │              │<──OK────────│            │
 │              │              │            │
 │<──200 OK + results──────────│            │
 │              │              │            │

[Next request within 2 minutes]

 │──GET /api/content?days_back=90&limit=50─>│
 │              │              │            │
 │              │──GET key────>│            │
 │              │<──results (<10ms)────────│
 │<──200 OK────│              │            │
```

---

## 3. Circuit Breaker Failure Recovery

```
Service A    Circuit Breaker    Service B
   │               │                 │
   │──call B──────>│                 │
   │               │──forward───────>│
   │               │<──success───────│
   │<──response────│                 │
   │               │ [State: CLOSED, failures: 0]
   │               │                 │
   │──call B──────>│                 │
   │               │──forward───────>│
   │               │     X (timeout) │
   │               │ [State: CLOSED, failures: 1]
   │<──error───────│                 │
   │               │                 │
   [... 4 more failures ...]
   │               │                 │
   │──call B──────>│                 │
   │               │──forward───────>│
   │               │     X (timeout) │
   │               │ [State: OPEN, failures: 5]
   │<──fallback────│                 │
   │               │                 │
   [60 seconds pass]
   │               │ [State: HALF_OPEN]
   │               │                 │
   │──call B──────>│                 │
   │               │──forward (test)─>│
   │               │<──success───────│
   │               │ [State: CLOSED, failures: 0]
   │<──response────│                 │
```

---

# Integration Specifications

## 1. Abacus AI Integration

**Provider:** Abacus AI
**Endpoint:** Configured via environment variable
**Authentication:** API Key (stored in Secret Manager)

**Integration Type:** REST API

**Request Format:**
```http
POST {ABACUS_ENDPOINT}/v1/completions
Authorization: Bearer {ABACUS_API_KEY}
Content-Type: application/json

{
  "prompt": "User's question...",
  "max_tokens": 1000,
  "temperature": 0.7,
  "model": "abacus-ai-model"
}
```

**Response Format:**
```json
{
  "id": "cmpl_abc123",
  "choices": [
    {
      "text": "AI generated response...",
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 200,
    "total_tokens": 250
  }
}
```

**Error Handling:**
- 429 Too Many Requests → Backoff and retry (exponential)
- 503 Service Unavailable → Fallback to OpenAI
- Timeout (> 30s) → Fallback to OpenAI

**Cost Tracking:**
```python
cost_per_request = 0.015  # $0.015 per request
monthly_requests = track_requests("abacus")
monthly_cost = monthly_requests * cost_per_request
```

---

## 2. OpenAI Integration

**Provider:** OpenAI
**Endpoint:** https://api.openai.com/v1/chat/completions
**Authentication:** API Key (stored in Secret Manager)

**Request Format:**
```http
POST https://api.openai.com/v1/chat/completions
Authorization: Bearer {OPENAI_API_KEY}
Content-Type: application/json

{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "user", "content": "User's question..."}
  ],
  "max_tokens": 1000,
  "temperature": 0.7
}
```

**Response Format:**
```json
{
  "id": "chatcmpl_abc123",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "AI generated response..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 200,
    "total_tokens": 250
  }
}
```

**Rate Limits:**
- 10,000 requests/minute
- 2,000,000 tokens/minute

**Cost:**
- gpt-4o-mini: ~$0.025 per request (varies by tokens)

---

## 3. Pub/Sub Integration

**Topic Creation:**
```bash
gcloud pubsub topics create {topic-name} \
  --project=xynergy-dev-1757909467
```

**Publishing:**
```python
from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, "campaign-created")

message = {
    "event_type": "campaign_created",
    "campaign_id": "camp_123",
    "tenant_id": "demo",
    "timestamp": datetime.now().isoformat()
}

future = publisher.publish(
    topic_path,
    json.dumps(message).encode("utf-8"),
    event_type="campaign_created",  # Attribute
    tenant_id="demo"                # Attribute
)

message_id = future.result()
```

**Subscription:**
```python
from google.cloud import pubsub_v1

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    PROJECT_ID,
    "campaign-created-subscription"
)

def callback(message):
    data = json.loads(message.data)
    process_event(data)
    message.ack()

streaming_pull_future = subscriber.subscribe(
    subscription_path,
    callback=callback
)
```

---

## 4. BigQuery Integration

**Connection:**
```python
from google.cloud import bigquery

client = bigquery.Client(project=PROJECT_ID)
```

**Parameterized Query:**
```python
query = """
SELECT *
FROM `{project}.{dataset}.{table}`
WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL @days_back DAY)
  AND tenant_id = @tenant_id
LIMIT @limit
"""

job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("days_back", "INT64", 90),
        bigquery.ScalarQueryParameter("tenant_id", "STRING", "demo"),
        bigquery.ScalarQueryParameter("limit", "INT64", 50)
    ]
)

query_job = client.query(query, job_config=job_config)
results = list(query_job.result())
```

**Insert Rows:**
```python
table_id = f"{PROJECT_ID}.{dataset}.{table}"
rows_to_insert = [
    {"field1": "value1", "field2": "value2"},
    {"field1": "value3", "field2": "value4"}
]

errors = client.insert_rows_json(table_id, rows_to_insert)
if errors:
    logger.error(f"Insert errors: {errors}")
```

---

# Error Handling & Edge Cases

## Error Classification

### 1. Client Errors (4xx)

**400 Bad Request:**
```json
{
  "detail": "Validation error: Invalid days_back parameter",
  "errors": [
    {
      "field": "days_back",
      "message": "Must be between 1 and 730",
      "provided": "1000"
    }
  ],
  "status_code": 400
}
```

**Handling:**
- Validate all inputs with Pydantic
- Return specific error messages
- Do NOT retry (client must fix request)

---

**401 Unauthorized:**
```json
{
  "detail": "Invalid API key",
  "status_code": 401
}
```

**Handling:**
- Verify API key on every request
- Rate limit failed auth attempts
- Log security events

---

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded: 10 requests/minute for expensive operations",
  "retry_after": 45,
  "status_code": 429
}
```

**Handling:**
- Implement rate limiting (slowapi)
- Return Retry-After header
- Client should backoff exponentially

---

### 2. Server Errors (5xx)

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error",
  "request_id": "req_abc123",
  "status_code": 500
}
```

**Handling:**
- Log full stack trace (server-side only)
- Return generic message to client
- Alert on-call team
- Retry safe (idempotent operations only)

---

**503 Service Unavailable:**
```json
{
  "detail": "Service temporarily unavailable",
  "status_code": 503,
  "circuit_breaker_state": "OPEN"
}
```

**Handling:**
- Circuit breaker opened
- Return fallback response if possible
- Client should retry with backoff

---

## Edge Cases

### Edge Case 1: Cache Stampede

**Problem:** Cache expires, 1000 requests hit database simultaneously

**Solution: Cache Warming + Stale-While-Revalidate**
```python
async def get_with_cache_stampede_protection(key: str):
    # Try cache
    cached = await redis.get(key)
    if cached:
        return cached

    # Use distributed lock to prevent stampede
    lock_key = f"lock:{key}"
    lock_acquired = await redis.set(lock_key, "1", ex=5, nx=True)

    if lock_acquired:
        # This request wins - refresh cache
        data = await expensive_query()
        await redis.set(key, data, ex=300)
        await redis.delete(lock_key)
        return data
    else:
        # Another request is refreshing - wait briefly
        await asyncio.sleep(0.1)
        return await redis.get(key) or await expensive_query()
```

---

### Edge Case 2: Partial Pub/Sub Failure

**Problem:** Event published but subscriber fails to process

**Solution: Dead Letter Queue + Retry**
```python
# Subscription with dead letter queue
subscription = subscriber.create_subscription(
    name=subscription_path,
    topic=topic_path,
    dead_letter_policy=DeadLetterPolicy(
        dead_letter_topic=dead_letter_topic,
        max_delivery_attempts=5
    )
)

# Subscriber with error handling
def callback(message):
    try:
        process_event(message.data)
        message.ack()
    except RetryableError as e:
        logger.warning(f"Retryable error: {e}")
        message.nack()  # Retry
    except PermanentError as e:
        logger.error(f"Permanent error: {e}")
        message.ack()   # Don't retry, goes to DLQ
```

---

### Edge Case 3: BigQuery Partition Scan

**Problem:** Query accidentally scans all partitions (expensive)

**Solution: Automatic Partition Filter Validation**
```python
def validate_partition_pruning(query: str) -> bool:
    """
    Ensures query includes partition pruning.
    Raises error if not.
    """
    if "DATE(" not in query or "DATE_SUB" not in query:
        raise ValueError(
            "Query must include partition pruning: "
            "WHERE DATE(timestamp_column) >= DATE_SUB(...)"
        )
    return True

# Use before executing
validate_partition_pruning(query)
client.query(query)
```

---

### Edge Case 4: Multi-Tenant Data Leakage

**Problem:** Bug in query returns data from wrong tenant

**Solution: Mandatory Tenant Filter + Testing**
```python
def ensure_tenant_filter(tenant_id: str, query: str) -> str:
    """
    Ensures query includes tenant_id filter.
    """
    if f"tenant_id = '{tenant_id}'" not in query and \
       f"tenant_id = @tenant_id" not in query:
        raise SecurityError(
            "Query must include tenant_id filter"
        )
    return query

# Automated test
def test_tenant_isolation():
    """Verify tenant A cannot see tenant B's data"""
    # Create data for tenant A
    create_content(tenant_id="tenant_a", title="A's content")

    # Query as tenant B
    results = list_content(tenant_id="tenant_b")

    # Assert no data from tenant A
    assert all(r.tenant_id == "tenant_b" for r in results)
```

---

### Edge Case 5: AI Provider Cascading Failure

**Problem:** All AI providers fail simultaneously

**Solution: Circuit Breaker + Graceful Degradation**
```python
async def generate_with_fallback(prompt: str) -> Dict:
    """
    Multi-level fallback for AI generation
    """
    providers = [
        ("abacus", call_abacus),
        ("openai", call_openai),
        ("internal", call_internal_ai)
    ]

    last_error = None
    for provider_name, provider_func in providers:
        try:
            if circuit_breakers[provider_name].state != "OPEN":
                result = await provider_func(prompt)
                return {"text": result, "provider": provider_name}
        except Exception as e:
            last_error = e
            logger.warning(f"{provider_name} failed: {e}")
            continue

    # All providers failed - return canned response
    return {
        "text": "I'm currently experiencing technical difficulties. Please try again shortly.",
        "provider": "fallback",
        "error": str(last_error)
    }
```

---

# Security Architecture

## Authentication

### API Key Management

**Storage:**
- **Source:** Environment variable `XYNERGY_API_KEYS` (comma-separated)
- **Rotation:** Automatic reload every 5 minutes
- **Secrets:** Google Secret Manager for production

**Validation:**
```python
async def verify_api_key(credentials: HTTPAuthorizationCredentials) -> str:
    keys = get_valid_api_keys()  # Auto-reloaded
    if credentials.credentials not in keys:
        logger.warning(f"Invalid API key attempt: {credentials.credentials[:8]}...")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials
```

**Key Rotation Process:**
1. Add new key to Secret Manager
2. Wait 5 minutes (auto-reload)
3. Update clients with new key
4. Wait 24 hours
5. Remove old key

---

## Authorization

### Multi-Tenant Access Control

**Tenant Context:**
```python
@app.middleware("http")
async def tenant_context_middleware(request: Request, call_next):
    tenant_id = request.headers.get("X-Tenant-ID", "demo")
    request.state.tenant_id = tenant_id
    response = await call_next(request)
    return response
```

**Row-Level Security:**
```python
async def list_campaigns(tenant_id: str):
    # MUST filter by tenant_id
    campaigns = db.collection("campaigns")\
        .where("tenant_id", "==", tenant_id)\
        .get()
    return campaigns
```

**Firestore Security Rules:**
```javascript
service cloud.firestore {
  match /databases/{database}/documents {
    match /campaigns/{campaignId} {
      allow read, write: if request.auth != null
        && resource.data.tenant_id == request.auth.token.tenant_id;
    }
  }
}
```

---

## Data Protection

### Encryption

**At Rest:**
- Firestore: Google-managed keys (AES-256)
- BigQuery: Customer-managed keys (CMEK) available
- Cloud Storage: Google-managed keys
- Redis: Not encrypted (private network)

**In Transit:**
- TLS 1.3 for all external connections
- VPC Private Google Access for internal GCP traffic

---

### Input Validation

**Pydantic Models:**
```python
class ContentRequest(BaseModel):
    tenant_id: str = Field(..., max_length=100, regex=r'^[a-zA-Z0-9_-]+$')
    keyword_primary: str = Field(..., max_length=200, min_length=1)
    content_type: str = Field(..., regex=r'^(hub|spoke)$')
    word_count: int = Field(..., ge=300, le=10000)

    @validator('keyword_primary')
    def sanitize_keyword(cls, v):
        # Remove SQL injection attempts
        if any(char in v for char in ["'", '"', ";", "--"]):
            raise ValueError("Invalid characters in keyword")
        return v.strip()
```

**SQL Injection Prevention:**
```python
# ✅ GOOD: Parameterized query
query = """
SELECT * FROM table
WHERE tenant_id = @tenant_id
  AND status = @status
"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("tenant_id", "STRING", tenant_id),
        bigquery.ScalarQueryParameter("status", "STRING", status)
    ]
)

# ❌ BAD: String interpolation
query = f"SELECT * FROM table WHERE tenant_id = '{tenant_id}'"  # NEVER DO THIS
```

---

## Network Security

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://xynergy-platform.com",
        "https://api.xynergy.dev",
        "https://*.xynergy.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Tenant-ID"],
    max_age=3600  # Cache preflight for 1 hour
)
```

**Security Rules:**
- ❌ NEVER `allow_origins=["*"]`
- ✅ Always specify exact domains
- ✅ Use HTTPS only in production

---

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/expensive")
@limiter.limit("10/minute")
async def expensive_operation():
    # AI generation, complex queries
    pass

@app.get("/api/list")
@limiter.limit("60/minute")
async def list_operation():
    # Standard operations
    pass
```

---

## Security Monitoring

### Logging Security Events

```python
# Failed authentication
logger.warning(
    "authentication_failed",
    ip_address=request.client.host,
    api_key_prefix=api_key[:8],
    endpoint=request.url.path
)

# Suspicious activity
if failed_auth_count > 5:
    logger.error(
        "potential_attack",
        ip_address=request.client.host,
        failed_attempts=failed_auth_count,
        time_window="5 minutes"
    )
    # Ban IP temporarily
    ban_ip(request.client.host, duration=3600)
```

---

### Security Alerts

**Alert Conditions:**
- 10+ failed auth attempts from same IP in 5 minutes
- API key leaked (detected in public GitHub, logs, etc.)
- Unusual traffic pattern (100x normal)
- Circuit breaker open for > 5 minutes
- Data access from unexpected region

**Alert Channels:**
- PagerDuty: Critical security events
- Slack #security: All security events
- Email: Security team distribution list

---

# Performance & Scaling

## Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| API Response (p95) | < 500ms | 250ms cached, 550ms uncached | ✅ |
| Cache Hit Rate | > 80% | 84%+ | ✅ |
| Service Availability | 99.9% | 99.95% | ✅ |
| Error Rate | < 1% | 0.3% | ✅ |
| Cold Start | < 10s | 5-8s | ✅ |
| BigQuery Cost | Minimize | 70-90% reduction via partitioning | ✅ |
| AI Cost | < $3K/month | $2,750/month (89% savings) | ✅ |

---

## Caching Strategy

### Cache Hierarchy

**L1: Redis (Hot Data)**
- Latency: < 10ms
- Hit Rate: 84%+
- TTL: 1-60 minutes

**L2: BigQuery (Warm Data)**
- Latency: 250-550ms
- Partitioned for cost efficiency
- 70-90% cost reduction

**L3: Firestore (Operational)**
- Latency: 50-100ms
- Transactional consistency
- Indexed queries

---

### Cache Invalidation

**Time-Based (TTL):**
```python
# Different TTLs for different data types
ttl_config = {
    "ai_responses": 3600,      # 1 hour (stable)
    "campaign_templates": 3600, # 1 hour
    "aso_stats": 300,          # 5 minutes (moderately volatile)
    "aso_content": 120,        # 2 minutes
    "trending_data": 300       # 5 minutes (volatile)
}
```

**Event-Based:**
```python
@app.post("/api/content")
async def create_content(content: ContentRequest):
    # Create content
    result = await db.create(content)

    # Invalidate related caches
    await redis_cache.invalidate_pattern(f"aso_content:{content.tenant_id}:*")
    await redis_cache.invalidate_pattern(f"aso_stats:{content.tenant_id}:*")

    return result
```

---

## Auto-Scaling Configuration

### Cloud Run Scaling

```yaml
Min Instances: 0          # Scale to zero when no traffic
Max Instances: 10-50      # Varies by service
Concurrency: 80           # Requests per instance
CPU Allocation: 1-2 cores
Memory: 512Mi-1Gi

Scaling Triggers:
  - Request count
  - CPU utilization > 60%
  - Memory utilization > 70%
  - Custom metric: Queue depth
```

**Scale-Up:**
- New instance spawned in ~5-10 seconds
- Gradual traffic shift to new instance
- Old instances remain until healthy

**Scale-Down:**
- Idle timeout: 5 minutes
- Graceful shutdown (finish in-flight requests)
- Cost savings from scale-to-zero

---

## Query Optimization

### BigQuery Best Practices

1. **Partition Pruning (70-90% cost reduction)**
```sql
-- Before: Scans 730 days
SELECT * FROM table WHERE status = 'active'

-- After: Scans 90 days (87% reduction)
SELECT id, name FROM table
WHERE DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  AND status = 'active'
```

2. **Clustering**
```sql
CREATE TABLE dataset.table
PARTITION BY DATE(created_at)
CLUSTER BY tenant_id, status;
```

3. **Select Specific Columns**
```sql
-- ❌ Bad: Scans all columns
SELECT * FROM table WHERE id = '123'

-- ✅ Good: Scans only needed columns
SELECT id, name, status FROM table WHERE id = '123'
```

4. **Avoid SELECT DISTINCT (use GROUP BY)**
```sql
-- ❌ Expensive
SELECT DISTINCT tenant_id FROM table

-- ✅ Better
SELECT tenant_id FROM table GROUP BY tenant_id
```

---

## Connection Pooling

### GCP Client Pooling

```python
class GCPClients:
    _instance = None
    _clients = {}

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def get_bigquery_client(self):
        if 'bigquery' not in self._clients:
            self._clients['bigquery'] = bigquery.Client(
                project=PROJECT_ID
            )
        return self._clients['bigquery']
```

**Benefits:**
- 60% faster cold starts (15s → 6s)
- 30% memory savings
- Consistent configuration

---

## Load Testing Results

**Test Configuration:**
- Tool: Locust
- Users: 1000 concurrent
- Duration: 10 minutes
- Endpoints: Mixed (50% reads, 30% writes, 20% AI)

**Results:**

| Metric | Value |
|--------|-------|
| Total Requests | 145,000 |
| Requests/sec | 240 |
| Median Response | 85ms |
| p95 Response | 450ms |
| p99 Response | 1200ms |
| Error Rate | 0.2% |
| Auto-scaling | 2 → 8 instances |

---

# Deployment Runbook

## Pre-Deployment Checklist

- [ ] All tests pass (unit, integration)
- [ ] Code review approved
- [ ] Security scan completed
- [ ] Environment variables updated
- [ ] Database migrations prepared (if any)
- [ ] Rollback plan documented
- [ ] Stakeholders notified

---

## Deployment Steps

### Step 1: Build Container Image

```bash
# Build image
cd /path/to/service
docker build -t us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/{service}:latest .

# Test locally
docker run -p 8080:8080 {image}
curl http://localhost:8080/health

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/{service}:latest
```

### Step 2: Deploy to Cloud Run

```bash
gcloud run deploy {service-name} \
  --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-platform/{service}:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=xynergy-dev-1757909467,REGION=us-central1 \
  --service-account 835612502919-compute@developer.gserviceaccount.com \
  --cpu 1 \
  --memory 512Mi \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 0 \
  --max-instances 10
```

### Step 3: Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe {service-name} --region=us-central1 --format="value(status.url)")

# Health check
curl $SERVICE_URL/health

# Smoke test
curl -H "X-API-Key: {api_key}" $SERVICE_URL/api/test
```

### Step 4: Monitor

```bash
# Watch logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name={service-name}" --limit=50 --format=json

# Check metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count" AND resource.labels.service_name="{service-name}"'
```

---

## Rollback Procedure

```bash
# List revisions
gcloud run revisions list --service={service-name} --region=us-central1

# Route traffic to previous revision
gcloud run services update-traffic {service-name} \
  --to-revisions={previous-revision}=100 \
  --region=us-central1

# Verify
curl $SERVICE_URL/health
```

**Rollback Triggers:**
- Error rate > 5%
- p95 latency > 2x baseline
- Health checks failing
- Circuit breakers opening

---

## Database Migration

```bash
# 1. Backup current state
gcloud firestore export gs://backup-bucket/backup-$(date +%Y%m%d)

# 2. Run migration script
python migration_script.py

# 3. Verify migration
python verify_migration.py

# 4. If successful, deploy new code
# 5. If failed, restore from backup
gcloud firestore import gs://backup-bucket/backup-20251010
```

---

## Blue-Green Deployment

```bash
# Deploy new version (green)
gcloud run deploy {service-name} \
  --image {new-image} \
  --no-traffic \
  --tag green

# Get green URL
GREEN_URL=$(gcloud run services describe {service-name} --format="value(status.traffic[tag=green].url)")

# Test green
curl $GREEN_URL/health

# Shift traffic gradually
gcloud run services update-traffic {service-name} \
  --to-revisions green=10

# Monitor for 5 minutes

# If successful, shift all traffic
gcloud run services update-traffic {service-name} \
  --to-latest

# If issues, rollback
gcloud run services update-traffic {service-name} \
  --to-tags blue=100
```

---

# System Operations Manual

## Daily Operations

### Morning Checks (9 AM)

```bash
# 1. Check service health
curl https://platform-dashboard-*.run.app/api/platform-status | jq .

# 2. Review overnight alerts
gcloud logging read "severity>=ERROR" --limit=50 --format=json

# 3. Check cost dashboard
gcloud billing accounts list
# Navigate to Cloud Console → Billing

# 4. Review performance metrics
# Cloud Console → Monitoring → Dashboards
```

---

### Monitoring Dashboards

**Platform Dashboard URL:**
`https://platform-dashboard-835612502919.us-central1.run.app`

**Key Metrics:**
- Service availability (target: 99.9%)
- Response times (p50, p95, p99)
- Error rates (target: < 1%)
- Cache hit rates (target: > 80%)
- Circuit breaker states
- AI costs (daily, monthly)

---

## Incident Response

### Severity Levels

**P0 (Critical):**
- Platform down (all services unavailable)
- Data breach or security incident
- Payment processing failure
- Response: Immediate, 24/7

**P1 (High):**
- Major service degradation (> 50% users affected)
- Database corruption
- AI providers all failing
- Response: < 1 hour, business hours

**P2 (Medium):**
- Single service down
- Performance degradation (2x normal latency)
- Non-critical feature broken
- Response: < 4 hours, business hours

**P3 (Low):**
- Minor bugs
- UI issues
- Documentation errors
- Response: Next sprint

---

### Incident Response Playbook

**Step 1: Detect (Auto-alerts or manual report)**
```
Alert → PagerDuty → On-call engineer
OR
User report → Support → Engineering
```

**Step 2: Triage (5 minutes)**
- Assess severity
- Identify affected services
- Determine impact (% users, revenue)
- Escalate if P0/P1

**Step 3: Mitigate (Target: < 30 minutes for P0)**
- Rollback recent deployments
- Scale up resources
- Enable fallback modes
- Route around failing components

**Step 4: Communicate**
- Internal: Slack #incidents
- External: Status page (if P0/P1)
- Stakeholders: Email update every 30 minutes

**Step 5: Resolve**
- Fix root cause
- Deploy fix
- Verify resolution
- Update status page

**Step 6: Post-Mortem (Within 48 hours)**
- Timeline of events
- Root cause analysis
- Action items to prevent recurrence
- Share with team

---

## Common Issues & Solutions

### Issue: Service Not Responding (503)

**Symptoms:**
- Health check failing
- 503 errors
- Circuit breaker OPEN

**Diagnosis:**
```bash
# Check service status
gcloud run services describe {service-name} --region=us-central1

# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name={service-name}" --limit=50

# Check resource usage
# Cloud Console → Cloud Run → {service} → Metrics
```

**Common Causes:**
1. Out of memory (OOM)
2. Startup timeout
3. Dependency unavailable
4. Configuration error

**Solutions:**
```bash
# 1. If OOM: Increase memory
gcloud run services update {service-name} --memory 1Gi

# 2. If startup timeout: Increase timeout
gcloud run services update {service-name} --timeout 300

# 3. If dependency issue: Check dependency health
curl {dependency-url}/health

# 4. If config error: Check environment variables
gcloud run services describe {service-name} --format="value(spec.template.spec.containers[0].env)"
```

---

### Issue: High Latency (> 2x normal)

**Symptoms:**
- p95 latency > 1000ms (normally 450ms)
- Slow user experience

**Diagnosis:**
```bash
# Check cache hit rate
# Expect > 80%, if lower, cache may be cold

# Check BigQuery query performance
# Cloud Console → BigQuery → Query History

# Check circuit breaker states
curl $SERVICE_URL/health | jq .checks.circuit_breaker
```

**Solutions:**
1. **Cold cache:** Warm cache with common queries
2. **Slow BigQuery:** Check partition pruning
3. **Circuit breaker OPEN:** Investigate dependency

---

### Issue: High Costs

**Symptoms:**
- Daily BigQuery costs > $50
- AI costs > $100/day

**Diagnosis:**
```bash
# Check BigQuery costs
gcloud logging read "protoPayload.serviceData.jobCompletedEvent" --limit=50 --format=json | jq '.protoPayload.serviceData.jobCompletedEvent.job.jobStatistics.totalBilledBytes'

# Check AI routing
# Review AI Routing Engine logs for provider distribution
```

**Solutions:**
1. **BigQuery:** Verify partition pruning on all queries
2. **AI:** Review routing logic, ensure Internal AI used for simple queries
3. **Cache:** Increase TTLs to reduce query volume

---

### Issue: Authentication Failures

**Symptoms:**
- 401 errors
- Valid API keys rejected

**Diagnosis:**
```bash
# Check Secret Manager
gcloud secrets versions access latest --secret="xynergy-api-keys"

# Check service environment
gcloud run services describe {service-name} --format="value(spec.template.spec.containers[0].env)"
```

**Solutions:**
1. Verify API key in Secret Manager
2. Check environment variable configuration
3. Force reload API keys (5-minute auto-reload)

---

## Backup & Restore

### Firestore Backup

```bash
# Export all collections
gcloud firestore export gs://xynergy-backups/firestore-$(date +%Y%m%d)

# Scheduled daily backup (Cloud Scheduler)
0 2 * * * gcloud firestore export gs://xynergy-backups/firestore-$(date +%Y%m%d)
```

### Firestore Restore

```bash
# Import from backup
gcloud firestore import gs://xynergy-backups/firestore-20251010

# Verify
gcloud firestore databases describe (default)
```

---

### BigQuery Backup

```bash
# Snapshot table
bq cp dataset.table dataset.table_backup_$(date +%Y%m%d)

# Export to Cloud Storage
bq extract --destination_format=AVRO dataset.table gs://xynergy-backups/bigquery/table_$(date +%Y%m%d)/*.avro
```

### BigQuery Restore

```bash
# Restore from snapshot
bq cp dataset.table_backup_20251010 dataset.table

# OR load from Cloud Storage
bq load --source_format=AVRO dataset.table gs://xynergy-backups/bigquery/table_20251010/*.avro
```

---

## Performance Optimization

### Regular Optimization Tasks

**Weekly:**
- Review cache hit rates, adjust TTLs
- Analyze slow queries, add indexes
- Check error logs, fix recurring issues

**Monthly:**
- Review cost reports, optimize
- Load test new features
- Update dependencies

**Quarterly:**
- Capacity planning
- Architecture review
- Security audit

---

## Access Control

### Team Roles

| Role | Permissions | Members |
|------|-------------|---------|
| Owner | Full access | CTO |
| Admin | Deploy, config, read logs | Lead Engineers |
| Developer | Read logs, deploy to staging | All Engineers |
| Read-Only | View metrics, logs | Support, PM |

### Granting Access

```bash
# Add user to project
gcloud projects add-iam-policy-binding xynergy-dev-1757909467 \
  --member="user:engineer@xynergy.com" \
  --role="roles/editor"

# Grant Cloud Run access
gcloud run services add-iam-policy-binding {service-name} \
  --member="user:engineer@xynergy.com" \
  --role="roles/run.developer" \
  --region=us-central1
```

---

## Monitoring & Alerting

### Alert Policies

**Critical Alerts (PagerDuty):**
- Service availability < 99%
- Error rate > 5%
- All circuit breakers OPEN
- BigQuery costs > $200/day

**Warning Alerts (Slack):**
- Cache hit rate < 70%
- p95 latency > 1000ms
- Single circuit breaker OPEN
- BigQuery costs > $100/day

**Info Alerts (Email):**
- New deployment completed
- Scheduled maintenance
- Weekly cost report

---

**End of Documentation Bundle**

---

**Document Control:**
- **Version**: 1.0
- **Last Updated**: October 10, 2025
- **Next Review**: Monthly
- **Owner**: Platform Engineering Team
- **Approvers**: CTO, Lead Architect, Security Lead

