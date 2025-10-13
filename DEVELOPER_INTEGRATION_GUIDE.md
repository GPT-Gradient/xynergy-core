# XynergyOS Developer Integration Guide

**How to Build Apps That Integrate with XynergyOS**

**Last Updated:** October 13, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Environment Setup](#environment-setup)
3. [SDK & Client Libraries](#sdk--client-libraries)
4. [Authentication](#authentication)
5. [Making API Calls](#making-api-calls)
6. [Frontend-Backend Integration](#frontend-backend-integration)
7. [Testing Against Dev Environment](#testing-against-dev-environment)
8. [Example Applications](#example-applications)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

XynergyOS provides multiple ways to integrate your application:

1. **REST API** - Direct HTTP calls to the Intelligence Gateway
2. **Python SDK** - Pre-built Python client library
3. **JavaScript/TypeScript** - Fetch API or Axios with provided types
4. **WebSocket** - Real-time event streaming

**All integrations should go through the Intelligence Gateway** for authentication, caching, and fault tolerance.

---

## Environment Setup

### Dev Environment URLs

**Intelligence Gateway (Dev):**
```
https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
```

**Key Characteristics:**
- Mock mode enabled (no real OAuth required)
- Firestore uses `dev_*` collections
- Redis uses `dev:*` key prefix
- Returns mock data for Slack, Gmail, etc.
- Safe for testing and development

### Production Environment URLs

**Intelligence Gateway (Prod) - When Deployed:**
```
https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app
```

**Key Characteristics:**
- Mock mode disabled (requires real OAuth)
- Firestore uses `prod_*` collections
- Redis uses `prod:*` key prefix
- Returns real data from integrations
- Production-grade performance

### Environment Detection

Your app should support environment switching:

```javascript
// JavaScript/TypeScript
const XYNERGY_API_BASE = process.env.XYNERGY_ENV === 'production'
  ? 'https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app'
  : 'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app';
```

```python
# Python
import os

XYNERGY_ENV = os.getenv('XYNERGY_ENV', 'dev')
XYNERGY_API_BASE = (
    'https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app'
    if XYNERGY_ENV == 'prod'
    else 'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app'
)
```

---

## SDK & Client Libraries

### Python SDK

**Location:** `/xynergy_platform_sdk/` (in this repository)

**Installation:**
```bash
pip install -r sdk_requirements.txt
```

**Quick Start:**
```python
import asyncio
from xynergy_platform_sdk import XynergyPlatformSDK

async def main():
    # Point to dev environment
    async with XynergyPlatformSDK(
        api_key="your_jwt_token",
        base_url="https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app"
    ) as sdk:
        # Get platform health
        health = await sdk.get_platform_health()
        print(f"Status: {health.overall_status}")

        # Access Slack
        channels = await sdk.slack.get_channels()
        print(f"Found {len(channels)} Slack channels")

        # Access CRM
        contacts = await sdk.crm.get_contacts()
        print(f"Found {len(contacts)} CRM contacts")

asyncio.run(main())
```

**SDK Documentation:** See `XYNERGY_SDK_README.md`

### JavaScript/TypeScript Client

**Create a client wrapper:**

```typescript
// xynergy-client.ts
interface XynergyConfig {
  baseUrl: string;
  token: string;
  environment?: 'dev' | 'prod';
}

class XynergyClient {
  private baseUrl: string;
  private token: string;
  private environment: string;

  constructor(config: XynergyConfig) {
    this.baseUrl = config.baseUrl;
    this.token = config.token;
    this.environment = config.environment || 'dev';
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Health check
  async getHealth() {
    return this.request<{ status: string; environment: string }>('/health');
  }

  // Slack methods
  async getSlackChannels() {
    return this.request<any>('/api/v2/slack/channels');
  }

  async getSlackMessages(channelId: string) {
    return this.request<any>(`/api/v2/slack/channels/${channelId}/messages`);
  }

  // CRM methods
  async getContacts() {
    return this.request<any>('/api/v2/crm/contacts');
  }

  async createContact(contact: any) {
    return this.request<any>('/api/v2/crm/contacts', {
      method: 'POST',
      body: JSON.stringify(contact),
    });
  }

  // Gmail methods
  async getEmails() {
    return this.request<any>('/api/v2/email/messages');
  }

  // Projects
  async getProjects() {
    return this.request<any>('/api/v1/projects');
  }

  async createProject(project: any) {
    return this.request<any>('/api/v1/projects', {
      method: 'POST',
      body: JSON.stringify(project),
    });
  }
}

// Export configured client
export const createXynergyClient = (token: string) => {
  return new XynergyClient({
    baseUrl: process.env.NEXT_PUBLIC_XYNERGY_API_BASE ||
             'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app',
    token,
    environment: process.env.NEXT_PUBLIC_XYNERGY_ENV as 'dev' | 'prod' || 'dev',
  });
};
```

**Usage in React:**

```typescript
// pages/dashboard.tsx
import { createXynergyClient } from '../lib/xynergy-client';
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [channels, setChannels] = useState([]);
  const [contacts, setContacts] = useState([]);

  useEffect(() => {
    const loadData = async () => {
      // Get token from your auth system
      const token = await getAuthToken();

      // Create client pointing to dev
      const client = createXynergyClient(token);

      // Load data
      const [channelsData, contactsData] = await Promise.all([
        client.getSlackChannels(),
        client.getContacts(),
      ]);

      setChannels(channelsData.data || []);
      setContacts(contactsData.data || []);
    };

    loadData();
  }, []);

  return (
    <div>
      <h1>XynergyOS Dashboard</h1>

      <section>
        <h2>Slack Channels</h2>
        <ul>
          {channels.map(ch => (
            <li key={ch.id}>{ch.name}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2>CRM Contacts</h2>
        <ul>
          {contacts.map(contact => (
            <li key={contact.id}>{contact.name} - {contact.email}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
```

---

## Authentication

### Getting a JWT Token

**Option 1: Test Token (Dev Only)**

For quick testing in dev, you can use the existing dev JWT secret:

```bash
# Generate a test token using the dev secret
# (jwt-secret-dev from Secret Manager)

# Python
import jwt
import datetime

payload = {
  'user_id': 'test-user-123',
  'tenant_id': 'your-tenant',
  'email': 'test@example.com',
  'username': 'testuser',
  'roles': ['user'],
  'iat': datetime.datetime.utcnow(),
  'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
  'iss': 'xynergyos-intelligence-gateway',
  'sub': 'test-user-123'
}

token = jwt.encode(payload, 'your-dev-jwt-secret', algorithm='HS256')
print(token)
```

```javascript
// Node.js
const jwt = require('jsonwebtoken');

const payload = {
  user_id: 'test-user-123',
  tenant_id: 'your-tenant',
  email: 'test@example.com',
  username: 'testuser',
  roles: ['user'],
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours
  iss: 'xynergyos-intelligence-gateway',
  sub: 'test-user-123'
};

const token = jwt.sign(payload, 'your-dev-jwt-secret', { algorithm: 'HS256' });
console.log(token);
```

**Option 2: Firebase Auth (Production)**

For production, use Firebase Authentication:

```javascript
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';

const auth = getAuth();
const userCredential = await signInWithEmailAndPassword(
  auth,
  'user@example.com',
  'password'
);

// Get Firebase ID token
const idToken = await userCredential.user.getIdToken();

// Use this token with XynergyOS API
const client = createXynergyClient(idToken);
```

### Using the Token

**HTTP Header:**
```
Authorization: Bearer <your-jwt-token>
```

**Example:**
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/channels
```

---

## Making API Calls

### Available API Endpoints

**Intelligence Gateway Routes:**

```
# Health Check
GET /health
GET /api/v1/health

# Slack
GET    /api/v2/slack/channels
GET    /api/v2/slack/channels/:channelId/messages
POST   /api/v2/slack/channels/:channelId/messages
GET    /api/v2/slack/users
GET    /api/v2/slack/search

# Gmail/Email
GET    /api/v2/email/messages
POST   /api/v2/email/send
GET    /api/v2/email/threads
GET    /api/v2/email/search

# CRM
GET    /api/v2/crm/contacts
POST   /api/v2/crm/contacts
GET    /api/v2/crm/contacts/:id
PATCH  /api/v2/crm/contacts/:id
DELETE /api/v2/crm/contacts/:id
GET    /api/v2/crm/interactions
POST   /api/v2/crm/interactions

# Projects
GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/:id
PATCH  /api/v1/projects/:id
DELETE /api/v1/projects/:id
GET    /api/v1/projects/:id/tasks
POST   /api/v1/projects/:id/tasks

# Admin (requires admin role)
GET    /api/v1/admin/monitoring/cost
GET    /api/v1/admin/monitoring/circuit-breakers
GET    /api/v1/admin/monitoring/health
```

**Complete API Documentation:** See `XYNERGY_API_INTEGRATION_GUIDE.md`

### Example API Calls

**Fetch Slack Channels:**
```javascript
const response = await fetch(
  'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/slack/channels',
  {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  }
);

const { success, data } = await response.json();
console.log('Channels:', data);
```

**Create CRM Contact:**
```javascript
const response = await fetch(
  'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/crm/contacts',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: 'John Doe',
      email: 'john@example.com',
      company: 'Acme Corp',
      phone: '555-1234',
      tags: ['lead', 'enterprise'],
    }),
  }
);

const { success, data } = await response.json();
console.log('Created contact:', data);
```

**Create Project:**
```javascript
const response = await fetch(
  'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v1/projects',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: 'Q4 Marketing Campaign',
      description: 'Launch new product line',
      type: 'marketing',
      status: 'planning',
      priority: 'high',
    }),
  }
);

const { success, data } = await response.json();
console.log('Created project:', data);
```

---

## Frontend-Backend Integration

### Architecture Pattern

```
┌─────────────────┐
│  Your Frontend  │
│   (React/Vue)   │
└────────┬────────┘
         │ HTTPS + JWT
         │
┌────────▼────────────────────────────┐
│  XynergyOS Intelligence Gateway     │
│  (Dev or Prod Environment)          │
└────────┬────────────────────────────┘
         │
    ┌────┴────┬────────┬───────────┐
    │         │        │           │
┌───▼───┐ ┌──▼──┐ ┌───▼────┐ ┌───▼───┐
│ Slack │ │ CRM │ │Projects│ │ Gmail │
│Service│ │     │ │        │ │Service│
└───────┘ └─────┘ └────────┘ └───────┘
```

### Environment Configuration

**Frontend .env file:**

```bash
# .env.development (for local dev)
NEXT_PUBLIC_XYNERGY_ENV=dev
NEXT_PUBLIC_XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
NEXT_PUBLIC_XYNERGY_WS_BASE=wss://xynergyos-intelligence-gateway-835612502919.us-central1.run.app

# .env.production (for production build)
NEXT_PUBLIC_XYNERGY_ENV=prod
NEXT_PUBLIC_XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app
NEXT_PUBLIC_XYNERGY_WS_BASE=wss://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app
```

**Backend .env file (if you have your own backend):**

```bash
# .env.development
XYNERGY_ENV=dev
XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
XYNERGY_JWT_SECRET=your-dev-jwt-secret

# .env.production
XYNERGY_ENV=prod
XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app
XYNERGY_JWT_SECRET=your-prod-jwt-secret
```

---

## Testing Against Dev Environment

### Ensure Dev Environment Testing

**1. Use Dev Base URL:**

Always point to the dev gateway during development:

```javascript
// ✅ Correct - Points to dev
const API_BASE = 'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app';

// ❌ Wrong - Would point to prod (when deployed)
const API_BASE = 'https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app';
```

**2. Check Response for Environment:**

The dev environment returns environment info:

```javascript
const health = await fetch(`${API_BASE}/health`);
const data = await health.json();

console.log('Environment:', data.environment); // Should be 'dev'
console.log('Mock Mode:', data.mockMode);      // Should be true

if (data.environment !== 'dev') {
  console.warn('⚠️  Not connected to dev environment!');
}
```

**3. Verify Mock Data:**

Dev environment returns mock data with specific indicators:

```javascript
const channels = await fetch(`${API_BASE}/api/v2/slack/channels`, {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Dev mock data has mock: true flag
if (channels.data?.[0]?.name?.includes('mock-') || channels.mock) {
  console.log('✅ Receiving mock data from dev environment');
} else {
  console.warn('⚠️  Receiving real data - you may be hitting prod!');
}
```

**4. Use Environment Variable Checks:**

```javascript
// Runtime environment check
const isDev = process.env.NEXT_PUBLIC_XYNERGY_ENV === 'dev';
const API_BASE = isDev
  ? 'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app'
  : 'https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app';

// Add visual indicator in UI
{isDev && (
  <div className="dev-banner">
    🔧 Development Mode - Using Mock Data
  </div>
)}
```

**5. Network Tab Verification:**

Open browser DevTools → Network tab:
- Check request URLs start with the dev gateway URL
- Look for `x-environment: dev` response header
- Verify `x-mock-mode: true` response header

### Testing Checklist

Before deploying your integration:

- [ ] Confirm API base URL points to dev gateway
- [ ] Verify `/health` endpoint returns `environment: 'dev'`
- [ ] Check that mock data is being returned
- [ ] Test authentication with dev JWT tokens
- [ ] Verify CORS allows your dev origin (localhost:3000, etc.)
- [ ] Test all API endpoints you're using
- [ ] Check error handling works correctly
- [ ] Verify rate limiting doesn't block dev testing

---

## Example Applications

### Example 1: Simple Dashboard (React)

```typescript
// app/page.tsx
'use client';

import { useEffect, useState } from 'react';

const API_BASE = 'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app';

export default function Dashboard() {
  const [health, setHealth] = useState<any>(null);
  const [channels, setChannels] = useState<any[]>([]);
  const [contacts, setContacts] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        // Get JWT token (from your auth system)
        const token = 'your-jwt-token';

        // Check health
        const healthRes = await fetch(`${API_BASE}/health`);
        const healthData = await healthRes.json();
        setHealth(healthData);

        // Verify dev environment
        if (healthData.environment !== 'dev') {
          console.warn('Not connected to dev environment!');
        }

        // Load data from gateway
        const headers = { 'Authorization': `Bearer ${token}` };

        const [channelsRes, contactsRes, projectsRes] = await Promise.all([
          fetch(`${API_BASE}/api/v2/slack/channels`, { headers }),
          fetch(`${API_BASE}/api/v2/crm/contacts`, { headers }),
          fetch(`${API_BASE}/api/v1/projects`, { headers }),
        ]);

        const channelsData = await channelsRes.json();
        const contactsData = await contactsRes.json();
        const projectsData = await projectsRes.json();

        setChannels(channelsData.data || []);
        setContacts(contactsData.data || []);
        setProjects(projectsData.data || []);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-8">
      {/* Environment indicator */}
      {health?.environment === 'dev' && (
        <div className="bg-yellow-100 border border-yellow-400 p-2 mb-4">
          🔧 Development Mode - Mock Data
        </div>
      )}

      <h1 className="text-3xl font-bold mb-6">XynergyOS Dashboard</h1>

      {/* Slack Channels */}
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">
          Slack Channels ({channels.length})
        </h2>
        <div className="grid grid-cols-3 gap-4">
          {channels.map(channel => (
            <div key={channel.id} className="border p-4 rounded">
              <h3 className="font-bold">#{channel.name}</h3>
              <p className="text-sm text-gray-600">{channel.topic}</p>
              <p className="text-xs text-gray-500">
                {channel.memberCount} members
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CRM Contacts */}
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">
          CRM Contacts ({contacts.length})
        </h2>
        <div className="border rounded">
          {contacts.map(contact => (
            <div key={contact.id} className="border-b p-4 last:border-b-0">
              <h3 className="font-bold">{contact.name}</h3>
              <p className="text-sm">{contact.email}</p>
              <p className="text-sm text-gray-600">{contact.company}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Projects */}
      <section>
        <h2 className="text-2xl font-semibold mb-4">
          Projects ({projects.length})
        </h2>
        <div className="grid grid-cols-2 gap-4">
          {projects.map(project => (
            <div key={project.id} className="border p-4 rounded">
              <h3 className="font-bold">{project.name}</h3>
              <p className="text-sm">{project.description}</p>
              <div className="flex gap-2 mt-2">
                <span className="text-xs px-2 py-1 bg-blue-100 rounded">
                  {project.status}
                </span>
                <span className="text-xs px-2 py-1 bg-gray-100 rounded">
                  {project.type}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
```

### Example 2: Python CLI Tool

```python
# xynergy_cli.py
import asyncio
import os
from xynergy_platform_sdk import XynergyPlatformSDK

API_BASE = os.getenv(
    'XYNERGY_API_BASE',
    'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app'
)

async def main():
    token = os.getenv('XYNERGY_TOKEN')
    if not token:
        print("Error: XYNERGY_TOKEN environment variable not set")
        return

    async with XynergyPlatformSDK(
        api_key=token,
        base_url=API_BASE
    ) as sdk:
        # Check health
        health = await sdk.get_health()
        print(f"Environment: {health.get('environment')}")
        print(f"Mock Mode: {health.get('mockMode')}")
        print()

        # Get Slack channels
        print("Slack Channels:")
        channels = await sdk.slack.get_channels()
        for channel in channels:
            print(f"  #{channel['name']} - {channel.get('memberCount', 0)} members")
        print()

        # Get CRM contacts
        print("CRM Contacts:")
        contacts = await sdk.crm.get_contacts()
        for contact in contacts:
            print(f"  {contact['name']} <{contact['email']}>")
        print()

        # Get Projects
        print("Projects:")
        projects = await sdk.projects.get_all()
        for project in projects:
            print(f"  {project['name']} ({project['status']})")

if __name__ == '__main__':
    asyncio.run(main())
```

**Usage:**
```bash
export XYNERGY_TOKEN="your-jwt-token"
python xynergy_cli.py
```

---

## Best Practices

### 1. Always Use Environment Variables

```javascript
// ✅ Good
const API_BASE = process.env.NEXT_PUBLIC_XYNERGY_API_BASE;

// ❌ Bad - Hardcoded URL
const API_BASE = 'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app';
```

### 2. Implement Environment Indicators

Show users which environment they're using:

```jsx
{process.env.NEXT_PUBLIC_XYNERGY_ENV === 'dev' && (
  <div className="dev-indicator">
    🔧 Development Environment - Mock Data
  </div>
)}
```

### 3. Handle Errors Gracefully

```javascript
try {
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.json();
    console.error('API Error:', error);
    // Show user-friendly error message
    return;
  }

  const data = await response.json();
  // Handle success
} catch (error) {
  console.error('Network error:', error);
  // Show connectivity error
}
```

### 4. Cache Responses Client-Side

The gateway caches on the server, but you can also cache on the client:

```javascript
// React Query example
const { data, isLoading } = useQuery(
  ['slack-channels'],
  () => client.getSlackChannels(),
  {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  }
);
```

### 5. Use TypeScript Types

```typescript
// Define types for API responses
interface SlackChannel {
  id: string;
  name: string;
  topic?: string;
  memberCount: number;
  isPrivate: boolean;
}

interface CRMContact {
  id: string;
  name: string;
  email: string;
  company?: string;
  phone?: string;
  tags: string[];
}

// Use in your code
const channels: SlackChannel[] = await client.getSlackChannels();
```

### 6. Implement Retry Logic

```javascript
async function fetchWithRetry(url, options, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.ok) return response;

      // Don't retry on 4xx errors
      if (response.status >= 400 && response.status < 500) {
        throw new Error(`Client error: ${response.status}`);
      }
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

---

## Troubleshooting

### Issue: CORS Error

**Problem:** Browser blocks request with CORS error

**Solution:**
1. Verify your frontend origin is in the gateway's CORS whitelist
2. Dev gateway allows: `http://localhost:3000`, `http://localhost:5173`, etc.
3. For custom origins, update gateway CORS configuration
4. Never use `Access-Control-Allow-Origin: *` in production

### Issue: 401 Unauthorized

**Problem:** API returns 401 error

**Solutions:**
1. Check JWT token is valid and not expired
2. Verify token is sent in `Authorization: Bearer <token>` header
3. Ensure token includes required fields (user_id, tenant_id, etc.)
4. Check token is signed with correct secret

### Issue: Receiving Real Data Instead of Mock Data

**Problem:** Dev environment returning real data

**Solutions:**
1. Verify URL is pointing to dev gateway (not prod)
2. Check `/health` endpoint shows `environment: 'dev'`
3. Verify `MOCK_MODE=true` in gateway environment variables
4. Check logs: `gcloud run services logs read xynergyos-intelligence-gateway`

### Issue: Empty or No Data

**Problem:** API returns empty arrays

**Solutions:**
1. Check authentication token is valid
2. Verify tenant_id in token matches your data
3. For dev, mock data should always be returned
4. Check network tab for actual API response

### Issue: Rate Limiting

**Problem:** API returns 429 Too Many Requests

**Solutions:**
1. Dev rate limit: 1000 req/min (should be plenty)
2. Prod rate limit: 100 req/min
3. Implement client-side caching
4. Use batch endpoints where available
5. Contact admin to increase limits if needed

---

## Additional Resources

### Documentation

- **API Reference:** `XYNERGY_API_INTEGRATION_GUIDE.md`
- **SDK Documentation:** `XYNERGY_SDK_README.md`
- **Platform Setup:** `DEV_PROD_SETUP_COMPLETE.md`
- **Deployment Guide:** `PLATFORM_DEPLOYMENT_GUIDE.md`

### SDK Location

- **Python SDK:** `/xynergy_platform_sdk/`
- **Requirements:** `sdk_requirements.txt`

### Gateway URLs

- **Dev:** `https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app`
- **Prod:** `https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app`

### Support

For integration support:
1. Check API documentation
2. Review example applications above
3. Test with `/health` endpoint
4. Check gateway logs for errors
5. Verify environment configuration

---

## Summary

**To integrate with XynergyOS:**

1. **Use the Intelligence Gateway** as your API entry point
2. **Point to dev environment** during development
3. **Use environment variables** to switch between dev/prod
4. **Implement authentication** with JWT tokens
5. **Verify mock data** is being returned in dev
6. **Use the Python SDK** or create your own client wrapper
7. **Check the `/health` endpoint** to confirm environment
8. **Handle errors gracefully** and implement retries
9. **Cache responses** to improve performance
10. **Test thoroughly** in dev before deploying to prod

The dev environment is safe for testing - it uses mock data and won't affect production systems!
