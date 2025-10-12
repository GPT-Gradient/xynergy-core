# Business Entity Service

Business Entity & Continuum Management Service for Xynergy Platform

## Overview

This microservice manages:
- Business entities (Continuum, NEXUS, Venture, Enterprise)
- Continuum slot management (6 active slots)
- Graduation and onboarding workflows
- User administration and tenant assignments

## Technology Stack

- **Language:** TypeScript 5.3
- **Runtime:** Node.js 20
- **Framework:** Express.js 4.18
- **Database:** Firestore
- **Events:** Google Cloud Pub/Sub
- **Deployment:** Cloud Run (GCP)

## API Endpoints

### Entities
- `POST /api/v1/entities` - Create new business entity
- `GET /api/v1/entities` - List all entities (with filters)
- `GET /api/v1/entities/:id` - Get entity by ID
- `PATCH /api/v1/entities/:id` - Update entity
- `DELETE /api/v1/entities/:id` - Archive entity (soft delete)

### Continuum
- `GET /api/v1/continuum/slots` - Get current state of 6 slots
- `POST /api/v1/continuum` - Create new Continuum project
- `POST /api/v1/continuum/:id/graduate` - Graduate project (free up slot)
- `POST /api/v1/continuum/:id/onboard` - Onboard pending project to active slot
- `GET /api/v1/continuum/generations` - Get all generations summary
- `GET /api/v1/continuum/generations/:generation` - Get projects by generation

### Users (Admin)
- `POST /api/v1/users` - Create new user
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/:id` - Get user by ID
- `POST /api/v1/users/:id/tenants` - Assign user to tenant
- `DELETE /api/v1/users/:id/tenants/:tenantId` - Remove user from tenant
- `PATCH /api/v1/users/:id/global-role` - Update user's global role

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build TypeScript
npm run build

# Run production build
npm start
```

## Deployment

```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-services/business-entity-service

gcloud run deploy business-entity-service \
  --image us-central1-docker.pkg.dev/xynergy-dev-1757909467/xynergy-services/business-entity-service:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=xynergy-dev-1757909467
```

## Features

### Continuum Slot Management
- Maintains exactly 6 active Continuum project slots
- Automatic slot assignment during onboarding
- Slot liberation on graduation
- Pending queue for projects waiting for slots

### Entity Lifecycle
- **Concept** → **Development** → **Beta** → **Commercial** → **Graduated**
- Automatic tenant creation on onboarding
- Pub/Sub events for all lifecycle changes
- Beta user access preservation on graduation

### User Management
- Firebase Auth + Firestore integration
- Global roles (super_admin, admin, user)
- Multi-tenant role assignments
- Tenant-scoped permissions

## Pub/Sub Events

Topic: `xynergy-entity-events`

Event Types:
- `entity.created` - New entity created
- `entity.updated` - Entity updated
- `entity.graduated` - Continuum project graduated
- `entity.onboarded` - Pending project onboarded to active slot
- `entity.archived` - Entity archived

## Environment Variables

- `PORT` - Server port (default: 8080)
- `PROJECT_ID` - GCP project ID (default: xynergy-dev-1757909467)
- `NODE_ENV` - Environment (development | production)
- `LOG_LEVEL` - Logging level (debug | info | warn | error)

## License

MIT
