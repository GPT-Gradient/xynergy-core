# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records for the Xynergy Platform.

## What is an ADR?

An Architecture Decision Record (ADR) documents a significant architectural decision made along with its context and consequences.

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-001](./ADR-001-microservices-architecture.md) | Microservices Architecture | Accepted | 2024-Q1 |
| [ADR-002](./ADR-002-google-cloud-platform.md) | Google Cloud Platform as Cloud Provider | Accepted | 2024-Q1 |
| [ADR-003](./ADR-003-fastapi-framework.md) | FastAPI as Web Framework | Accepted | 2024-Q1 |
| [ADR-004](./ADR-004-firestore-and-bigquery.md) | Firestore + BigQuery Polyglot Persistence | Accepted | 2024-Q1 |
| [ADR-005](./ADR-005-pubsub-event-bus.md) | Pub/Sub as Event Bus | Accepted | 2024-Q2 |
| [ADR-006](./ADR-006-redis-caching.md) | Redis for Caching Layer | Accepted | 2024-Q2 |
| [ADR-007](./ADR-007-ai-routing-strategy.md) | AI Routing Strategy (Abacus → OpenAI → Internal) | Accepted | 2024-Q3 |
| [ADR-008](./ADR-008-multi-tenant-isolation.md) | Multi-Tenant Data Isolation Strategy | Accepted | 2024-Q3 |
| [ADR-009](./ADR-009-circuit-breaker-pattern.md) | Circuit Breaker for Fault Tolerance | Accepted | 2024-Q4 |
| [ADR-010](./ADR-010-partition-pruning.md) | BigQuery Partition Pruning | Accepted | 2025-Q4 |

## ADR Template

Each ADR follows this structure:

- **Title**: Short noun phrase
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Context**: What is the issue we're facing?
- **Decision**: What are we going to do about it?
- **Consequences**: What becomes easier or harder?
- **Alternatives Considered**: What other options did we evaluate?
- **Related Decisions**: Links to related ADRs

## Status Definitions

- **Proposed**: ADR is under consideration
- **Accepted**: ADR has been approved and is being implemented
- **Deprecated**: ADR is no longer in use but kept for historical reference
- **Superseded**: ADR has been replaced by another ADR (link provided)
