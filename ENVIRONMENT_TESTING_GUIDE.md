# Environment Testing Guide

**How to Ensure You're Testing Against Dev (Not Prod)**

---

## Quick Checklist ✅

Use this checklist to verify you're testing against the dev environment:

- [ ] **URL Check:** Using `xynergyos-intelligence-gateway` (NOT `xynergyos-intelligence-gateway-prod`)
- [ ] **Health Check:** `/health` returns `environment: "dev"`
- [ ] **Mock Mode:** `/health` returns `mockMode: true`
- [ ] **Mock Data:** API responses include mock indicators
- [ ] **Environment Variable:** `XYNERGY_ENV=dev` set
- [ ] **Visual Indicator:** Dev banner shown in UI

---

## Environment URLs

### ✅ Development Environment (Use This for Testing)

```
https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
```

**Characteristics:**
- Mock mode enabled
- Returns mock data for Slack, Gmail, etc.
- Firestore uses `dev_*` collections
- Redis uses `dev:*` key prefix
- Safe for testing and development

### ⚠️ Production Environment (Avoid During Development)

```
https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app
```

**Characteristics:**
- Mock mode disabled
- Returns real data
- Firestore uses `prod_*` collections
- Redis uses `prod:*` key prefix
- Requires real OAuth credentials

---

## Verification Methods

### Method 1: Check Health Endpoint

```bash
# Test your API base URL
curl https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/health
```

**Expected Response (Dev):**
```json
{
  "status": "healthy",
  "environment": "dev",
  "mockMode": true,
  "timestamp": "2025-10-13T10:30:00.000Z",
  "version": "1.0.0"
}
```

**Production Response (What You DON'T Want):**
```json
{
  "status": "healthy",
  "environment": "prod",
  "mockMode": false,
  "timestamp": "2025-10-13T10:30:00.000Z"
}
```

### Method 2: Check Response Headers

Open browser DevTools → Network tab → Select any API request:

**Dev Environment Headers:**
```
x-environment: dev
x-mock-mode: true
x-powered-by: XynergyOS Intelligence Gateway
```

**Production Headers:**
```
x-environment: prod
x-mock-mode: false
```

### Method 3: Check Mock Data Indicators

Dev environment returns mock data with specific patterns:

**Slack Channels (Dev Mock):**
```json
{
  "success": true,
  "data": [
    {
      "id": "C001",
      "name": "mock-general",
      "topic": "Mock channel for testing",
      "memberCount": 10
    }
  ],
  "mock": true
}
```

**Real Slack Channels (Prod):**
```json
{
  "success": true,
  "data": [
    {
      "id": "C123ABC",
      "name": "general",
      "topic": "Company-wide announcements",
      "memberCount": 247
    }
  ]
}
```

### Method 4: Check Browser Console Logs

The gateway logs environment information:

```javascript
// In your app
const health = await fetch(`${API_BASE}/health`).then(r => r.json());
console.log('Environment:', health.environment);
console.log('Mock Mode:', health.mockMode);

// Add assertion
if (health.environment !== 'dev') {
  console.error('⚠️  WARNING: Not connected to dev environment!');
  alert('You are not connected to the dev environment!');
}
```

---

## Configuration Examples

### React/Next.js

**.env.local (for development):**
```bash
NEXT_PUBLIC_XYNERGY_ENV=dev
NEXT_PUBLIC_XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
```

**.env.production (for production builds):**
```bash
NEXT_PUBLIC_XYNERGY_ENV=prod
NEXT_PUBLIC_XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app
```

**Usage in code:**
```typescript
const API_BASE = process.env.NEXT_PUBLIC_XYNERGY_API_BASE;
const IS_DEV = process.env.NEXT_PUBLIC_XYNERGY_ENV === 'dev';

// Verify on app load
useEffect(() => {
  fetch(`${API_BASE}/health`)
    .then(r => r.json())
    .then(health => {
      if (health.environment !== 'dev') {
        console.error('Not in dev environment!');
      }
    });
}, []);

// Show dev indicator
{IS_DEV && (
  <div className="bg-yellow-100 p-2">
    🔧 Development Mode - Mock Data
  </div>
)}
```

### Vue.js

**.env.development:**
```bash
VUE_APP_XYNERGY_ENV=dev
VUE_APP_XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
```

**Usage:**
```javascript
const API_BASE = process.env.VUE_APP_XYNERGY_API_BASE;

export default {
  data() {
    return {
      isDev: process.env.VUE_APP_XYNERGY_ENV === 'dev',
    };
  },
  mounted() {
    // Verify environment
    fetch(`${API_BASE}/health`)
      .then(r => r.json())
      .then(health => {
        if (health.environment !== 'dev') {
          console.error('Not in dev environment!');
        }
      });
  },
};
```

### Python Backend

```python
import os
import requests

XYNERGY_ENV = os.getenv('XYNERGY_ENV', 'dev')
API_BASE = os.getenv(
    'XYNERGY_API_BASE',
    'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app'
    if XYNERGY_ENV == 'dev'
    else 'https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app'
)

# Verify environment on startup
def verify_environment():
    response = requests.get(f'{API_BASE}/health')
    health = response.json()

    if health.get('environment') != XYNERGY_ENV:
        raise Exception(
            f"Environment mismatch! Expected {XYNERGY_ENV}, "
            f"got {health.get('environment')}"
        )

    print(f"✅ Connected to {XYNERGY_ENV} environment")
    print(f"   Mock Mode: {health.get('mockMode')}")

# Run on startup
verify_environment()
```

---

## Visual Indicators

### Add Dev Environment Banner

**React Component:**
```tsx
export function EnvironmentBanner() {
  const isDev = process.env.NEXT_PUBLIC_XYNERGY_ENV === 'dev';

  if (!isDev) return null;

  return (
    <div className="bg-yellow-100 border-b-2 border-yellow-400 px-4 py-2">
      <div className="container mx-auto flex items-center gap-2">
        <span className="text-2xl">🔧</span>
        <div>
          <strong>Development Mode</strong>
          <p className="text-sm text-gray-700">
            Using mock data from dev environment
          </p>
        </div>
      </div>
    </div>
  );
}
```

**Usage:**
```tsx
export default function Layout({ children }) {
  return (
    <>
      <EnvironmentBanner />
      {children}
    </>
  );
}
```

### Add Environment Badge

```tsx
export function EnvironmentBadge() {
  const env = process.env.NEXT_PUBLIC_XYNERGY_ENV || 'dev';

  return (
    <div
      className={`
        fixed bottom-4 right-4 px-3 py-1 rounded-full text-sm font-bold
        ${env === 'dev' ? 'bg-yellow-400 text-black' : 'bg-red-500 text-white'}
      `}
    >
      {env === 'dev' ? '🔧 DEV' : '⚠️ PROD'}
    </div>
  );
}
```

---

## Common Mistakes

### ❌ Mistake 1: Hardcoded Production URL

```javascript
// DON'T DO THIS
const API_BASE = 'https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app';
```

**Fix:**
```javascript
// Use environment variable
const API_BASE = process.env.NEXT_PUBLIC_XYNERGY_API_BASE;
```

### ❌ Mistake 2: No Environment Verification

```javascript
// DON'T DO THIS
function App() {
  // Just assumes it's in dev...
  return <Dashboard />;
}
```

**Fix:**
```javascript
// Verify and show indicator
function App() {
  const [env, setEnv] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(r => r.json())
      .then(health => setEnv(health.environment));
  }, []);

  return (
    <>
      {env === 'dev' && <DevBanner />}
      {env === 'prod' && <ProdWarning />}
      <Dashboard />
    </>
  );
}
```

### ❌ Mistake 3: Same .env for Dev and Prod

```bash
# DON'T DO THIS - Same file for both
XYNERGY_API_BASE=https://...
```

**Fix:**
```bash
# .env.development
XYNERGY_ENV=dev
XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app

# .env.production
XYNERGY_ENV=prod
XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app
```

### ❌ Mistake 4: No Mock Data Check

```javascript
// DON'T DO THIS
const channels = await getSlackChannels();
// Just assumes it's mock data...
```

**Fix:**
```javascript
const response = await getSlackChannels();

// Check for mock data
if (response.mock || response.data?.[0]?.name?.startsWith('mock-')) {
  console.log('✅ Using mock data');
} else {
  console.warn('⚠️  Using real data - check environment!');
}
```

---

## Testing Workflow

### 1. Start Development

```bash
# Set environment variables
export XYNERGY_ENV=dev
export XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app

# Start your app
npm run dev
```

### 2. Verify Environment

```bash
# Check health endpoint
curl $XYNERGY_API_BASE/health

# Should return: environment: "dev", mockMode: true
```

### 3. Test API Calls

```bash
# Get JWT token (use dev secret)
export TOKEN="your-dev-jwt-token"

# Test Slack endpoint
curl -H "Authorization: Bearer $TOKEN" \
  $XYNERGY_API_BASE/api/v2/slack/channels

# Should return mock channels
```

### 4. Check Browser

- Open DevTools → Network tab
- Verify all requests go to dev URL
- Check response headers show `x-environment: dev`
- Verify dev banner is shown in UI

### 5. Validate Mock Data

- Check API responses for mock indicators
- Verify data has mock prefixes (mock-general, etc.)
- Confirm no real user data is returned

---

## Production Deployment Checklist

Before deploying to production:

- [ ] Update `.env.production` with prod URLs
- [ ] Remove dev banners/indicators from prod build
- [ ] Test build locally: `npm run build && npm start`
- [ ] Verify prod environment URL is correct
- [ ] Confirm mock mode is disabled in prod
- [ ] Test authentication with prod tokens
- [ ] Verify CORS allows prod origins
- [ ] Check rate limits are appropriate
- [ ] Monitor logs after deployment

---

## Quick Commands

### Check Current Environment

```bash
# Using curl
curl https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/health | jq '.environment'

# Should return: "dev"
```

### Test API Access

```bash
# Set variables
export API_BASE="https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app"
export TOKEN="your-jwt-token"

# Test health
curl $API_BASE/health

# Test authenticated endpoint
curl -H "Authorization: Bearer $TOKEN" $API_BASE/api/v2/slack/channels
```

### Switch Environments

```bash
# Development
export XYNERGY_ENV=dev
export XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app

# Production
export XYNERGY_ENV=prod
export XYNERGY_API_BASE=https://xynergyos-intelligence-gateway-prod-835612502919.us-central1.run.app
```

---

## Summary

**To ensure you're testing against dev:**

1. ✅ **Use dev URL** in your `.env.development`
2. ✅ **Check `/health`** returns `environment: "dev"`
3. ✅ **Verify mock mode** is enabled
4. ✅ **Add visual indicator** in your UI
5. ✅ **Check response headers** in browser
6. ✅ **Validate mock data** patterns
7. ✅ **Never hardcode** production URLs
8. ✅ **Use environment variables** for all configs

**The dev environment is completely safe for testing - it uses mock data and won't affect production!**
