# Xynergy Platform - Pre-Production Accelerated Plan

**Date:** October 13, 2025
**Timeline:** 3 Phases (3-4 Weeks Total)
**Status:** Ready for Implementation

---

## Executive Summary

This accelerated plan compresses the 8-week pre-production roadmap into **3 major phases over 3-4 weeks** by parallelizing work, eliminating sequential dependencies, and focusing on high-impact deliverables.

**Key Strategy:** Run infrastructure, tooling, and service improvements in parallel teams.

---

## Compressed Timeline

### Phase 1: Foundation (Week 1)
**Focus:** Observability, Secrets, CI/CD Templates

### Phase 2: Automation & Consolidation (Week 2-3)
**Focus:** Auth Service, Service Merges, CLI, Docs

### Phase 3: Testing & Polish (Week 3-4)
**Focus:** Load Testing, Security, Final Validation

---

## Phase 1: Foundation (Week 1) - Days 1-7

**Goal:** Establish observability, migrate secrets, create CI/CD templates

### Parallel Track A: Observability (Days 1-5)
**Owner:** DevOps Team

**Day 1-2: Setup**
```bash
# Create monitoring workspace
gcloud monitoring workspaces create --display-name="xynergy-observability"

# Enable APIs
gcloud services enable \
  monitoring.googleapis.com \
  logging.googleapis.com \
  cloudtrace.googleapis.com \
  cloudprofiler.googleapis.com
```

**Day 3-4: Instrumentation**
- Deploy Prometheus exporters to all services (automated script)
- Configure custom metrics collection
- Set up log aggregation

**Day 5: Dashboards & Alerts**
- Import pre-built Grafana dashboards (4 dashboards)
- Configure alert policies (latency, errors, health)
- Test alert notifications

**Deliverables:**
- ✅ Monitoring workspace operational
- ✅ All 41 services instrumented
- ✅ 4 Grafana dashboards live
- ✅ Alert policies active

---

### Parallel Track B: Secrets Migration (Days 1-4)
**Owner:** Security Team

**Day 1: Audit & Plan**
```bash
# Scan all services for .env files and hardcoded secrets
find . -name ".env*" -o -name "*.env"

# Generate secret inventory
# Result: ~100 secrets identified
```

**Day 2-3: Bulk Migration**
```bash
# Automated migration script
./scripts/migrate-secrets-to-gcp.sh

# Creates all secrets with naming convention: XYN_[SERVICE]_[NAME]_[ENV]
# Updates all 41 Cloud Run services with --set-secrets
```

**Day 4: Cleanup & Verification**
- Remove all .env files from repositories
- Update .gitignore
- Verify all services using Secret Manager
- Document secret rotation procedures

**Deliverables:**
- ✅ ~100 secrets in Secret Manager
- ✅ All 41 services using secrets
- ✅ .env files removed
- ✅ Secret rotation docs

---

### Parallel Track C: CI/CD Templates (Days 1-5)
**Owner:** DevOps Team

**Day 1-2: Create Templates**
Create two base templates:

**cloudbuild-python.yaml:**
```yaml
steps:
  # Lint & Test
  - name: python:3.11-slim
    entrypoint: bash
    args:
      - '-c'
      - |
        pip install -r requirements.txt black flake8 pytest pytest-cov
        black --check .
        flake8 .
        pytest tests/ --cov --cov-report=term

  # Build & Push
  - name: gcr.io/cloud-builders/docker
    args: ['build', '-t', '${_IMAGE_URL}:${SHORT_SHA}', '-t', '${_IMAGE_URL}:latest', '.']
  - name: gcr.io/cloud-builders/docker
    args: ['push', '--all-tags', '${_IMAGE_URL}']

  # Deploy
  - name: gcr.io/google.com/cloudsdktool/cloud-sdk
    entrypoint: gcloud
    args:
      - run
      - deploy
      - ${_SERVICE_NAME}
      - --image=${_IMAGE_URL}:${SHORT_SHA}
      - --region=us-central1
      - --set-env-vars=XYNERGY_ENV=${_ENV},MOCK_MODE=${_MOCK_MODE},NODE_ENV=production
      - --service-account=xynergy-platform-sa@${PROJECT_ID}.iam.gserviceaccount.com
      - --quiet

  # Verify
  - name: gcr.io/cloud-builders/curl
    entrypoint: bash
    args:
      - '-c'
      - |
        sleep 10
        SERVICE_URL=$(gcloud run services describe ${_SERVICE_NAME} --region=us-central1 --format='value(status.url)')
        curl -f $SERVICE_URL/health || exit 1

substitutions:
  _SERVICE_NAME: service-name
  _IMAGE_URL: us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-platform/${_SERVICE_NAME}
  _ENV: dev
  _MOCK_MODE: 'true'

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: E2_HIGHCPU_8
```

**cloudbuild-typescript.yaml:**
```yaml
steps:
  # Install & Test
  - name: node:20
    entrypoint: npm
    args: ['ci']
  - name: node:20
    entrypoint: npm
    args: ['run', 'lint']
  - name: node:20
    entrypoint: npm
    args: ['test']

  # Build
  - name: node:20
    entrypoint: npm
    args: ['run', 'build']

  # Docker Build & Push
  - name: gcr.io/cloud-builders/docker
    args: ['build', '-t', '${_IMAGE_URL}:${SHORT_SHA}', '-t', '${_IMAGE_URL}:latest', '.']
  - name: gcr.io/cloud-builders/docker
    args: ['push', '--all-tags', '${_IMAGE_URL}']

  # Deploy
  - name: gcr.io/google.com/cloudsdktool/cloud-sdk
    entrypoint: gcloud
    args:
      - run
      - deploy
      - ${_SERVICE_NAME}
      - --image=${_IMAGE_URL}:${SHORT_SHA}
      - --region=us-central1
      - --set-env-vars=XYNERGY_ENV=${_ENV},MOCK_MODE=${_MOCK_MODE},NODE_ENV=production
      - --service-account=xynergy-platform-sa@${PROJECT_ID}.iam.gserviceaccount.com
      - --quiet

  # Verify
  - name: gcr.io/cloud-builders/curl
    entrypoint: bash
    args:
      - '-c'
      - |
        sleep 10
        SERVICE_URL=$(gcloud run services describe ${_SERVICE_NAME} --region=us-central1 --format='value(status.url)')
        curl -f $SERVICE_URL/health || exit 1

substitutions:
  _SERVICE_NAME: service-name
  _IMAGE_URL: us-central1-docker.pkg.dev/${PROJECT_ID}/xynergy-platform/${_SERVICE_NAME}
  _ENV: dev
  _MOCK_MODE: 'true'

options:
  logging: CLOUD_LOGGING_ONLY
  machineType: E2_HIGHCPU_8
```

**Day 3-4: GitHub Integration**
```bash
# Connect GitHub repository
gcloud alpha builds connections create github xynergy-github \
  --region=us-central1

# Create build triggers for all services (automated)
./scripts/create-build-triggers.sh
```

**Trigger Configuration (per service):**
- Branch: `main` → Deploy to dev
- Branch: `staging` → Deploy to staging
- Tag: `v*` → Deploy to prod (no traffic)

**Day 5: Test & Validate**
- Trigger test builds for 5 sample services
- Verify end-to-end pipeline
- Fix any issues

**Deliverables:**
- ✅ 2 reusable CI/CD templates
- ✅ GitHub repository connected
- ✅ 41 build triggers configured
- ✅ Pipeline tested and working

---

### End of Phase 1 Checklist
- [ ] Monitoring workspace with 4 dashboards
- [ ] All 41 services instrumented
- [ ] Alert policies configured
- [ ] ~100 secrets in Secret Manager
- [ ] All services using secrets
- [ ] CI/CD templates created
- [ ] 41 build triggers configured
- [ ] Pipeline tested

**Status:** Platform now has observability, secure secrets, and automated deployments

---

## Phase 2: Automation & Consolidation (Week 2-3) - Days 8-21

**Goal:** Unify auth, consolidate services, build CLI, create docs

### Parallel Track A: Auth Service (Days 8-14)
**Owner:** Platform Team

**Day 8-9: Service Creation**
```typescript
// xynergy-auth/src/index.ts
import express from 'express';
import { initializeApp } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';
import jwt from 'jsonwebtoken';

const app = express();
const db = getFirestore();
initializeApp();

// Unified token validation
app.post('/api/v1/auth/validate', async (req, res) => {
  const { token, token_type } = req.body;

  try {
    let user;

    if (token_type === 'firebase') {
      const decodedToken = await getAuth().verifyIdToken(token);
      user = await getUserWithRoles(decodedToken.uid);
    } else if (token_type === 'jwt') {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      user = await getUserWithRoles(decoded.user_id);
    } else {
      return res.status(400).json({ valid: false, error: 'Unknown token type' });
    }

    return res.json({ valid: true, user });
  } catch (error) {
    return res.status(401).json({ valid: false, error: error.message });
  }
});

// RBAC permission check
app.post('/api/v1/auth/check-permission', async (req, res) => {
  const { user_id, tenant_id, permission } = req.body;

  const userDoc = await db
    .collection('tenants').doc(tenant_id)
    .collection('users').doc(user_id)
    .get();

  if (!userDoc.exists) {
    return res.status(404).json({ allowed: false, error: 'User not found' });
  }

  const roles = userDoc.data()?.roles || [];
  const hasPermission = await checkRolePermissions(roles, permission);

  res.json({ allowed: hasPermission, roles });
});

async function getUserWithRoles(userId: string) {
  // Query Firestore for user and their roles
  const userQuery = await db.collectionGroup('users')
    .where('user_id', '==', userId)
    .limit(1)
    .get();

  if (userQuery.empty) {
    throw new Error('User not found');
  }

  const userData = userQuery.docs[0].data();
  const roles = userData.roles || [];

  // Fetch role permissions
  const permissions = [];
  for (const roleName of roles) {
    const roleDoc = await db.collection('roles').doc(roleName).get();
    if (roleDoc.exists) {
      permissions.push(...(roleDoc.data()?.permissions || []));
    }
  }

  return {
    user_id: userId,
    email: userData.email,
    roles,
    permissions: [...new Set(permissions)], // Deduplicate
  };
}

async function checkRolePermissions(roles: string[], permission: string): Promise<boolean> {
  for (const roleName of roles) {
    const roleDoc = await db.collection('roles').doc(roleName).get();
    if (roleDoc.exists) {
      const permissions = roleDoc.data()?.permissions || [];
      if (permissions.includes(permission)) {
        return true;
      }
    }
  }
  return false;
}

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`xynergy-auth listening on port ${PORT}`);
});
```

**Day 10-11: Middleware Packages**

**Python Middleware:**
```python
# xynergy-auth-middleware/setup.py
from setuptools import setup, find_packages

setup(
    name='xynergy-auth-middleware',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['httpx', 'fastapi'],
)

# xynergy-auth-middleware/xynergy_auth/middleware.py
from fastapi import Request, HTTPException, Depends
import httpx
import os

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'https://xynergy-auth.run.app')

async def verify_token(request: Request):
    """Extract and validate token from request"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/api/v1/auth/validate",
            json={"token": token, "token_type": "jwt"},
            timeout=5.0
        )

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

        return response.json()["user"]

async def require_permission(permission: str):
    """Dependency to check if user has required permission"""
    async def permission_checker(user = Depends(verify_token)):
        if permission not in user.get('permissions', []):
            raise HTTPException(status_code=403, detail=f"Missing permission: {permission}")
        return user
    return permission_checker

# Usage in FastAPI services:
# from xynergy_auth.middleware import verify_token, require_permission
# from fastapi import Depends
#
# @app.get("/api/v1/resource")
# async def get_resource(user = Depends(verify_token)):
#     return {"user": user['email']}
#
# @app.post("/api/v1/admin/action")
# async def admin_action(user = Depends(require_permission("admin:write"))):
#     return {"success": True}
```

**TypeScript Middleware:**
```typescript
// @xynergy/auth-middleware/package.json
{
  "name": "@xynergy/auth-middleware",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts"
}

// @xynergy/auth-middleware/src/index.ts
import { Request, Response, NextFunction } from 'express';
import axios from 'axios';

const AUTH_SERVICE_URL = process.env.AUTH_SERVICE_URL || 'https://xynergy-auth.run.app';

export interface AuthUser {
  user_id: string;
  email: string;
  roles: string[];
  permissions: string[];
}

export async function verifyToken(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization || '';
  if (!authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }

  const token = authHeader.replace('Bearer ', '');

  try {
    const response = await axios.post(`${AUTH_SERVICE_URL}/api/v1/auth/validate`, {
      token,
      token_type: 'jwt',
    }, { timeout: 5000 });

    req.user = response.data.user as AuthUser;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}

export function requirePermission(permission: string) {
  return async (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const user = req.user as AuthUser;
    if (!user.permissions.includes(permission)) {
      return res.status(403).json({ error: `Missing permission: ${permission}` });
    }

    next();
  };
}

// Usage in Express services:
// import { verifyToken, requirePermission } from '@xynergy/auth-middleware';
//
// app.get('/api/v1/resource', verifyToken, (req, res) => {
//   res.json({ user: req.user.email });
// });
//
// app.post('/api/v1/admin/action', verifyToken, requirePermission('admin:write'), (req, res) => {
//   res.json({ success: true });
// });
```

**Day 12-14: Integration**
- Deploy xynergy-auth service
- Publish middleware packages (PyPI + npm)
- Update 41 services to use new middleware
- Test authentication flow

**Deliverables:**
- ✅ xynergy-auth service deployed
- ✅ Python middleware on PyPI
- ✅ TypeScript middleware on npm
- ✅ All services integrated

---

### Parallel Track B: Service Consolidation (Days 8-14)
**Owner:** Platform Team

**Day 8-10: Merge Services**

**Consolidations:**
1. `ai-routing-engine` → `xynergy-ai-routing-engine` (keep xynergy prefix)
2. `marketing-engine` → `xynergy-marketing-engine`
3. Deprecate `xynergy-intelligence-gateway` (Python) → Keep `xynergyos-intelligence-gateway` (TypeScript)
4. `xynergy-internal-ai-service` → `internal-ai-service-v2`

**Process per merge:**
```bash
# 1. Copy unique features from old service to new service
# 2. Update environment variables and secrets
# 3. Deploy new service version
# 4. Test thoroughly
# 5. Deprecate old service (redirect traffic)
# 6. Delete old service after 7 days
```

**Day 11-14: Create xynergy-common Package**

**Python Package Structure:**
```python
# xynergy-common/setup.py
from setuptools import setup, find_packages

setup(
    name='xynergy-common',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'redis>=4.5.0',
        'google-cloud-firestore>=2.13.0',
        'google-cloud-pubsub>=2.18.0',
        'httpx>=0.25.0',
        'structlog>=23.1.0',
    ],
)

# xynergy-common/xynergy_common/redis/client.py
from redis import Redis
from typing import Optional
import os

class RedisClient:
    _instance: Optional[Redis] = None

    @classmethod
    def get_instance(cls) -> Redis:
        if cls._instance is None:
            cls._instance = Redis(
                host=os.getenv('REDIS_HOST', '10.229.184.219'),
                port=int(os.getenv('REDIS_PORT', '6379')),
                password=os.getenv('REDIS_PASSWORD'),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                max_connections=50,
            )
        return cls._instance

# xynergy-common/xynergy_common/logging/logger.py
import structlog
import logging

def setup_logger(service_name: str, level: str = 'INFO'):
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger = structlog.get_logger(service=service_name)
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper()),
    )

    return logger

# xynergy-common/xynergy_common/http/client.py
import httpx
from typing import Optional, Dict, Any
import asyncio

class HTTPClient:
    def __init__(self, base_url: Optional[str] = None, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )

    async def get(self, path: str, **kwargs) -> Dict[Any, Any]:
        response = await self.client.get(path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def post(self, path: str, **kwargs) -> Dict[Any, Any]:
        response = await self.client.post(path, **kwargs)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()

# xynergy-common/xynergy_common/pubsub/publisher.py
from google.cloud import pubsub_v1
from typing import Dict, Any
import json
import os

class PubSubPublisher:
    def __init__(self):
        self.project_id = os.getenv('PROJECT_ID', 'xynergy-dev-1757909467')
        self.publisher = pubsub_v1.PublisherClient()

    def publish(self, topic_name: str, message: Dict[Any, Any]) -> str:
        topic_path = self.publisher.topic_path(self.project_id, topic_name)
        message_bytes = json.dumps(message).encode('utf-8')
        future = self.publisher.publish(topic_path, message_bytes)
        return future.result()
```

**TypeScript Package:**
```typescript
// @xynergy/common/src/redis/client.ts
import Redis from 'ioredis';

export class RedisClient {
  private static instance: Redis;

  static getInstance(): Redis {
    if (!this.instance) {
      this.instance = new Redis({
        host: process.env.REDIS_HOST || '10.229.184.219',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD,
        maxRetriesPerRequest: 3,
        retryStrategy: (times) => Math.min(times * 50, 2000),
      });
    }
    return this.instance;
  }
}

// @xynergy/common/src/logging/logger.ts
import winston from 'winston';

export function setupLogger(serviceName: string, level: string = 'info') {
  return winston.createLogger({
    level,
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.json()
    ),
    defaultMeta: { service: serviceName },
    transports: [
      new winston.transports.Console()
    ],
  });
}

// @xynergy/common/src/http/client.ts
import axios, { AxiosInstance } from 'axios';

export class HTTPClient {
  private client: AxiosInstance;

  constructor(baseURL?: string, timeout: number = 30000) {
    this.client = axios.create({
      baseURL,
      timeout,
      maxRedirects: 3,
    });
  }

  async get(path: string, config?: any) {
    const response = await this.client.get(path, config);
    return response.data;
  }

  async post(path: string, data?: any, config?: any) {
    const response = await this.client.post(path, data, config);
    return response.data;
  }
}
```

**Deliverables:**
- ✅ 4 services consolidated (41 → 37)
- ✅ xynergy-common Python package
- ✅ @xynergy/common TypeScript package
- ✅ Services migrated to use common packages

---

### Parallel Track C: CLI & Documentation (Days 8-21)
**Owner:** DevEx Team

**Days 8-14: Build xynergy-devtools CLI**

```python
# xynergy-devtools/setup.py
from setuptools import setup, find_packages

setup(
    name='xynergy-devtools',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'pyyaml>=6.0',
        'requests>=2.28.0',
        'rich>=13.0.0',
    ],
    entry_points={
        'console_scripts': [
            'xynergy=xynergy_devtools.cli:main',
        ],
    },
)

# xynergy-devtools/xynergy_devtools/cli.py
import click
import yaml
import subprocess
import requests
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def main():
    """Xynergy Developer Tools CLI"""
    pass

@main.command()
@click.option('--project', required=True, help='GCP project ID')
@click.option('--env', type=click.Choice(['dev', 'staging', 'prod']), default='dev')
def setup(project, env):
    """Configure local development environment"""
    console.print(f"[bold blue]Setting up Xynergy environment...[/bold blue]")

    # Authenticate with gcloud
    console.print("Authenticating with GCP...")
    subprocess.run(['gcloud', 'auth', 'login'], check=True)
    subprocess.run(['gcloud', 'config', 'set', 'project', project], check=True)

    # Create config file
    config = {
        'project_id': project,
        'environment': env,
        'region': 'us-central1',
    }

    config_dir = Path.home() / '.xynergy'
    config_dir.mkdir(exist_ok=True)

    with open(config_dir / 'config.yaml', 'w') as f:
        yaml.dump(config, f)

    console.print(f"[green]✓[/green] Configuration saved to {config_dir / 'config.yaml'}")
    console.print("[bold green]Setup complete![/bold green]")

@main.command()
@click.argument('service_name')
@click.option('--port', default=8080, help='Port to run on')
@click.option('--mock/--no-mock', default=True, help='Enable mock mode')
def run(service_name, port, mock):
    """Run a service locally"""
    console.print(f"[bold blue]Starting {service_name}...[/bold blue]")

    # Set environment variables
    env = {
        'PORT': str(port),
        'XYNERGY_ENV': 'local',
        'MOCK_MODE': 'true' if mock else 'false',
    }

    # Detect service type and run
    service_path = Path(service_name)
    if (service_path / 'package.json').exists():
        # TypeScript service
        subprocess.run(['npm', 'run', 'dev'], cwd=service_path, env=env)
    elif (service_path / 'main.py').exists():
        # Python service
        subprocess.run(['python', 'main.py'], cwd=service_path, env=env)
    else:
        console.print(f"[red]Error: Service not found at {service_path}[/red]")

@main.command()
@click.option('--service', help='Check specific service')
@click.option('--all', 'check_all', is_flag=True, help='Check all services')
def status(service, check_all):
    """Check service health"""
    config = load_config()

    if check_all:
        # Get all services
        result = subprocess.run(
            ['gcloud', 'run', 'services', 'list', '--region', config['region'],
             '--format', 'value(metadata.name)'],
            capture_output=True, text=True
        )
        services = result.stdout.strip().split('\n')
    else:
        services = [service]

    table = Table(title="Service Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("URL")

    for svc in services:
        # Get service status
        result = subprocess.run(
            ['gcloud', 'run', 'services', 'describe', svc, '--region', config['region'],
             '--format', 'value(status.conditions[0].status,status.url)'],
            capture_output=True, text=True
        )
        status_text, url = result.stdout.strip().split('\n')

        status_emoji = "✓" if status_text == "True" else "✗"
        table.add_row(svc, f"{status_emoji} {status_text}", url)

    console.print(table)

@main.command()
@click.argument('service_name')
@click.option('--follow', '-f', is_flag=True, help='Stream logs')
@click.option('--lines', '-n', default=50, help='Number of lines')
def logs(service_name, follow, lines):
    """Tail service logs"""
    config = load_config()

    cmd = [
        'gcloud', 'logging', 'read',
        f'resource.type=cloud_run_revision AND resource.labels.service_name={service_name}',
        '--project', config['project_id'],
        '--limit', str(lines),
        '--format', 'table(timestamp,severity,textPayload)'
    ]

    if follow:
        cmd.append('--freshness=1m')

    subprocess.run(cmd)

@main.command()
@click.argument('service_name')
@click.option('--target', type=click.Choice(['dev', 'staging', 'prod']), default='dev')
@click.option('--wait/--no-wait', default=True)
def deploy(service_name, target, wait):
    """Deploy a service"""
    config = load_config()

    console.print(f"[bold blue]Deploying {service_name} to {target}...[/bold blue]")

    # Trigger Cloud Build
    cmd = [
        'gcloud', 'builds', 'submit',
        '--config', 'cloudbuild.yaml',
        '--substitutions', f'_SERVICE_NAME={service_name},_ENV={target}',
        '--project', config['project_id']
    ]

    if wait:
        subprocess.run(cmd, check=True)
        console.print("[bold green]✓ Deployment complete![/bold green]")
    else:
        subprocess.Popen(cmd)
        console.print("[yellow]Deployment triggered (running in background)[/yellow]")

def load_config():
    config_path = Path.home() / '.xynergy' / 'config.yaml'
    if not config_path.exists():
        console.print("[red]Error: Configuration not found. Run 'xynergy setup' first.[/red]")
        exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)

if __name__ == '__main__':
    main()
```

**Day 15-21: Documentation Portal**

**Documentation Structure:**
```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Create docs structure
mkdir -p docs/{getting-started,developer-guide,api-reference,operations,architecture}

# Generate docs from existing files
./scripts/consolidate-docs.sh

# Build and serve
mkdocs serve
```

**mkdocs.yml:**
```yaml
site_name: Xynergy Platform Documentation
theme:
  name: material
  palette:
    primary: blue
    accent: indigo
  features:
    - navigation.tabs
    - navigation.sections
    - search.highlight

nav:
  - Home: index.md
  - Getting Started:
    - Overview: getting-started/overview.md
    - Quick Start: getting-started/quick-start.md
    - Architecture: getting-started/architecture.md
  - Developer Guide:
    - Local Setup: developer-guide/local-setup.md
    - Creating Services: developer-guide/creating-services.md
    - Testing: developer-guide/testing-guide.md
    - Best Practices: developer-guide/best-practices.md
  - API Reference:
    - Authentication: api-reference/authentication.md
    - Intelligence Gateway: api-reference/intelligence-gateway.md
    - AI Services: api-reference/ai-services.md
  - Operations:
    - Deployment: operations/deployment.md
    - Monitoring: operations/monitoring.md
    - Troubleshooting: operations/troubleshooting.md

plugins:
  - search
  - swagger-ui-tag

markdown_extensions:
  - admonition
  - codehilite
  - toc:
      permalink: true
```

**Deliverables:**
- ✅ xynergy-devtools CLI on PyPI
- ✅ 10 commands implemented
- ✅ Documentation portal with MkDocs
- ✅ All docs consolidated
- ✅ API docs generated

---

### End of Phase 2 Checklist
- [ ] xynergy-auth service deployed and integrated
- [ ] Auth middleware packages published
- [ ] 4 services consolidated (37 total)
- [ ] xynergy-common packages published
- [ ] xynergy-devtools CLI published
- [ ] Documentation portal live

**Status:** Platform has unified auth, consolidated services, CLI tools, and complete documentation

---

## Phase 3: Testing & Polish (Week 3-4) - Days 15-28

**Goal:** Validate performance, security, and prepare for handoff

### Parallel Track A: Load Testing (Days 15-21)
**Owner:** QA Team

**Day 15-17: Create k6 Scripts**

```javascript
// load-tests/platform-test.js
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 200 },   // Steady state at 200 users
    { duration: '5m', target: 200 },   // Continue at 200 users
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
    'errors': ['rate<0.01'],                           // Error rate < 1%
    'http_reqs': ['rate>100'],                         // > 100 RPS
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app';
const TOKEN = __ENV.TEST_TOKEN;

export default function () {
  const params = {
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json',
    },
  };

  // Test 1: Health Check
  group('health_check', () => {
    const res = http.get(`${BASE_URL}/health`, params);
    check(res, {
      'health check is 200': (r) => r.status === 200,
      'health check is fast': (r) => r.timings.duration < 200,
    }) || errorRate.add(1);
    responseTime.add(res.timings.duration);
  });

  // Test 2: API Endpoints
  group('api_calls', () => {
    // Slack channels
    let res = http.get(`${BASE_URL}/api/v2/slack/channels`, params);
    check(res, {
      'slack channels returns 200': (r) => r.status === 200,
      'slack channels has data': (r) => JSON.parse(r.body).channels !== undefined,
    }) || errorRate.add(1);
    responseTime.add(res.timings.duration);

    // Gmail messages
    res = http.get(`${BASE_URL}/api/v2/gmail/messages`, params);
    check(res, {
      'gmail messages returns 200': (r) => r.status === 200,
    }) || errorRate.add(1);
    responseTime.add(res.timings.duration);

    // CRM contacts
    res = http.get(`${BASE_URL}/api/v2/crm/contacts`, params);
    check(res, {
      'crm contacts returns 200': (r) => r.status === 200,
    }) || errorRate.add(1);
    responseTime.add(res.timings.duration);
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    'summary.json': JSON.stringify(data),
    'summary.html': htmlReport(data),
  };
}

function htmlReport(data) {
  // Generate HTML report
  return `
    <html>
      <head><title>Load Test Results</title></head>
      <body>
        <h1>Load Test Summary</h1>
        <h2>Thresholds</h2>
        <ul>
          <li>P95 Response Time: ${data.metrics.http_req_duration.values['p(95)']}ms</li>
          <li>P99 Response Time: ${data.metrics.http_req_duration.values['p(99)']}ms</li>
          <li>Error Rate: ${(data.metrics.errors.values.rate * 100).toFixed(2)}%</li>
          <li>Request Rate: ${data.metrics.http_reqs.values.rate.toFixed(2)} RPS</li>
        </ul>
      </body>
    </html>
  `;
}
```

**Day 18-19: Run Tests**
```bash
# Run load test
k6 run --env BASE_URL=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app \
       --env TEST_TOKEN=$TEST_TOKEN \
       --out json=results.json \
       load-tests/platform-test.js

# Generate report
k6 report results.json --out summary.html
```

**Day 20-21: Analyze & Optimize**
- Review test results
- Identify bottlenecks
- Optimize slow endpoints
- Re-test

**Deliverables:**
- ✅ k6 test scripts for all service groups
- ✅ Load test results meeting baselines
- ✅ Performance optimizations applied

---

### Parallel Track B: Security Testing (Days 15-21)
**Owner:** Security Team

**Day 15-18: OWASP ZAP Scans**

```bash
# Install OWASP ZAP
docker pull owasp/zap2docker-stable

# Run baseline scan
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable \
  zap-baseline.py \
  -t https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app \
  -r zap-scan-report.html

# Run full scan (with authentication)
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable \
  zap-full-scan.py \
  -t https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app \
  -z "-config replacer.full_list(0).description=auth1 \
      -config replacer.full_list(0).enabled=true \
      -config replacer.full_list(0).matchtype=REQ_HEADER \
      -config replacer.full_list(0).matchstr=Authorization \
      -config replacer.full_list(0).replacement='Bearer $TEST_TOKEN'"
```

**Day 19-21: Remediation**
- Review scan results
- Fix high/critical vulnerabilities
- Re-scan to verify fixes

**Deliverables:**
- ✅ Security scan reports
- ✅ No critical vulnerabilities
- ✅ Security best practices documented

---

### Parallel Track C: Automation & CI (Days 15-21)
**Owner:** DevOps

**Day 15-18: GitHub Actions for Monthly Tests**

```yaml
# .github/workflows/monthly-tests.yml
name: Monthly Platform Tests

on:
  schedule:
    - cron: '0 0 1 * *'  # 1st of every month at midnight
  workflow_dispatch:      # Manual trigger

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install k6
        run: |
          sudo gpg -k
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
            --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
            | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run load tests
        run: |
          k6 run --env BASE_URL=${{ secrets.GATEWAY_URL }} \
                 --env TEST_TOKEN=${{ secrets.TEST_TOKEN }} \
                 --out json=results.json \
                 load-tests/platform-test.js

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: |
            results.json
            summary.html

      - name: Check thresholds
        run: |
          # Fail if thresholds not met
          if grep -q '"failed": true' results.json; then
            echo "Load test thresholds not met!"
            exit 1
          fi

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: ZAP Scan
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: ${{ secrets.GATEWAY_URL }}
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'

      - name: Upload scan results
        uses: actions/upload-artifact@v3
        with:
          name: zap-scan-results
          path: report_html.html

  notify:
    runs-on: ubuntu-latest
    needs: [load-test, security-scan]
    if: always()
    steps:
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Monthly platform tests completed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Monthly Platform Tests*\nLoad Test: ${{ needs.load-test.result }}\nSecurity Scan: ${{ needs.security-scan.result }}"
                  }
                }
              ]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

**Day 19-21: Terraform Validation**

```yaml
# .github/workflows/terraform-validation.yml
name: Terraform Validation

on:
  pull_request:
    paths:
      - 'terraform/**'
      - '.github/workflows/terraform-validation.yml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.5.0

      - name: Terraform Format Check
        run: terraform fmt -check -recursive
        working-directory: terraform

      - name: Terraform Init
        run: terraform init
        working-directory: terraform
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}

      - name: Terraform Validate
        run: terraform validate
        working-directory: terraform

      - name: Terraform Plan
        run: terraform plan -out=tfplan
        working-directory: terraform
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}

      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: terraform-plan
          path: terraform/tfplan
```

**Deliverables:**
- ✅ Monthly testing automation
- ✅ Terraform validation pipeline
- ✅ Automated notifications

---

### Day 22-28: Final Validation & Handoff

**Day 22-24: End-to-End Validation**
- [ ] Run full platform health check
- [ ] Verify all 37 services operational
- [ ] Confirm observability working
- [ ] Test CI/CD pipelines
- [ ] Validate auth service
- [ ] Test CLI commands
- [ ] Review documentation

**Day 25-26: Knowledge Transfer**
- [ ] Record video tutorials
- [ ] Conduct team training sessions
- [ ] Q&A sessions
- [ ] Update runbooks

**Day 27-28: Final Polish**
- [ ] Fix any remaining issues
- [ ] Update all documentation
- [ ] Create handoff document
- [ ] Final sign-off

---

## Success Criteria

### Must Have (Phase 1)
- [x] Monitoring workspace with dashboards
- [x] All services instrumented and exporting metrics
- [x] Alert policies configured
- [x] All secrets in Secret Manager
- [x] CI/CD templates and triggers configured

### Must Have (Phase 2)
- [x] xynergy-auth service deployed
- [x] All services using unified auth
- [x] Services consolidated (41 → 37)
- [x] xynergy-common packages published
- [x] xynergy-devtools CLI functional
- [x] Documentation portal published

### Must Have (Phase 3)
- [x] Load tests passing (≤300ms avg, <1% errors, ≥100 RPS)
- [x] Security scans passing (no critical issues)
- [x] Monthly testing automation configured
- [x] Team trained on new tools
- [x] Handoff documentation complete

---

## Final Deliverables Summary

| Category | Deliverable | Status |
|----------|-------------|--------|
| Observability | GCP Monitoring Workspace | ⏳ Phase 1 |
| Observability | 4 Grafana Dashboards | ⏳ Phase 1 |
| Observability | Alert Policies | ⏳ Phase 1 |
| Security | 100 secrets in Secret Manager | ⏳ Phase 1 |
| CI/CD | Build templates (Python & TS) | ⏳ Phase 1 |
| CI/CD | 37 Cloud Build triggers | ⏳ Phase 1 |
| Auth | xynergy-auth service | ⏳ Phase 2 |
| Auth | Middleware packages | ⏳ Phase 2 |
| Services | 4 services consolidated | ⏳ Phase 2 |
| Packages | xynergy-common (Python & TS) | ⏳ Phase 2 |
| Tools | xynergy-devtools CLI | ⏳ Phase 2 |
| Docs | Documentation portal | ⏳ Phase 2 |
| Testing | k6 load test suite | ⏳ Phase 3 |
| Testing | OWASP ZAP security scans | ⏳ Phase 3 |
| Testing | GitHub Actions automation | ⏳ Phase 3 |

---

## Timeline Summary

**Phase 1: Foundation (7 days)**
- Observability + Secrets + CI/CD Templates
- Can run in parallel across 3 teams

**Phase 2: Automation & Consolidation (14 days)**
- Auth + Services + CLI + Docs
- Can run in parallel across 3 teams
- Overlaps with Phase 1 (Days 8-14)

**Phase 3: Testing & Polish (14 days)**
- Load Testing + Security + Automation
- Can run in parallel with Phase 2 (Days 15-21)
- Final validation (Days 22-28)

**Total Timeline: 3-4 weeks with proper parallelization**

---

## Risk Mitigation

### Compressed Timeline Risks
- **Risk:** Quality issues due to speed
- **Mitigation:** Thorough testing at each phase, clear acceptance criteria

### Parallel Work Conflicts
- **Risk:** Teams stepping on each other
- **Mitigation:** Clear ownership, daily standups, shared project board

### Integration Issues
- **Risk:** Components don't work together
- **Mitigation:** Integration testing throughout, not just at end

---

**Document Version:** 1.0
**Created:** October 13, 2025
**Timeline:** 3-4 weeks (can start immediately)
**Status:** Ready for Implementation
