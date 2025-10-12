# Firebase Configuration - COMPLETE ✅

**Date:** October 11, 2025
**Status:** CONFIGURED AND READY

---

## Firebase Setup Complete

### ✅ Firebase Secrets Created

**Secrets stored in Secret Manager:**
```bash
gcloud secrets list --filter="name:FIREBASE" --project=xynergy-dev-1757909467
```

| Secret | Value | Status |
|--------|-------|--------|
| `FIREBASE_API_KEY` | AIzaSyDV3dfxDiqBpNi3IWpKH8nZ3jr4kSpXxDw | ✅ Created |
| `FIREBASE_APP_ID` | 1:835612502919:web:700fd8d6f2e5843c3b4122 | ✅ Created |

---

## Frontend Configuration Files Created

### Production Environment (`.env.production`)
```env
# Intelligence Gateway URLs
REACT_APP_API_URL=https://xynergy-intelligence-gateway-835612502919.us-central1.run.app
REACT_APP_WS_URL=wss://xynergy-intelligence-gateway-835612502919.us-central1.run.app

# Firebase Configuration
REACT_APP_FIREBASE_API_KEY=AIzaSyDV3dfxDiqBpNi3IWpKH8nZ3jr4kSpXxDw
REACT_APP_FIREBASE_AUTH_DOMAIN=xynergy-dev-1757909467.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=xynergy-dev-1757909467
REACT_APP_FIREBASE_STORAGE_BUCKET=xynergy-dev-1757909467.firebasestorage.app
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=835612502919
REACT_APP_FIREBASE_APP_ID=1:835612502919:web:700fd8d6f2e5843c3b4122
REACT_APP_FIREBASE_MEASUREMENT_ID=G-YTWVDK6Q42
```

### Development Environment (`.env.development`)
Same Firebase config, but can use localhost for API:
```env
REACT_APP_API_URL=http://localhost:8080
REACT_APP_WS_URL=ws://localhost:8080
```

---

## Firebase Web App Details

**App Name:** XynergyOS Frontend
**Project ID:** xynergy-dev-1757909467
**Project Number:** 835612502919

**Firebase Console:** https://console.firebase.google.com/project/xynergy-dev-1757909467

---

## Using Firebase in Your Frontend

### Option 1: Initialize Firebase (React/Next.js)

Create `src/config/firebase.ts`:
```typescript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getAnalytics } from 'firebase/analytics';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
  measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const analytics = getAnalytics(app);
```

### Option 2: Authentication Flow

```typescript
import { auth } from './config/firebase';
import { signInWithEmailAndPassword, onAuthStateChanged } from 'firebase/auth';

// Login
async function login(email: string, password: string) {
  const userCredential = await signInWithEmailAndPassword(auth, email, password);
  const idToken = await userCredential.user.getIdToken();

  // Use this token for Intelligence Gateway API calls
  return idToken;
}

// Listen for auth state
onAuthStateChanged(auth, async (user) => {
  if (user) {
    const idToken = await user.getIdToken();
    // Store token for API calls
    localStorage.setItem('firebase_token', idToken);
  } else {
    // User is signed out
    localStorage.removeItem('firebase_token');
  }
});
```

### Option 3: API Calls with Firebase Token

```typescript
async function callIntelligenceGateway(endpoint: string, options = {}) {
  const token = localStorage.getItem('firebase_token');

  const response = await fetch(
    `${process.env.REACT_APP_API_URL}${endpoint}`,
    {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    }
  );

  return response.json();
}

// Example: Get CRM contacts
const contacts = await callIntelligenceGateway('/api/v2/crm/contacts');
```

---

## WebSocket Connection with Firebase Auth

```typescript
import { io } from 'socket.io-client';
import { auth } from './config/firebase';

async function connectWebSocket() {
  const user = auth.currentUser;
  if (!user) throw new Error('User not authenticated');

  const idToken = await user.getIdToken();

  const socket = io(process.env.REACT_APP_WS_URL, {
    path: '/api/xynergyos/v2/stream',
    auth: {
      token: idToken
    },
    transports: ['websocket', 'polling']
  });

  socket.on('connect', () => {
    console.log('Connected to Intelligence Gateway');

    // Subscribe to events
    socket.emit('subscribe', ['slack-messages', 'email-updates', 'crm-changes']);
  });

  socket.on('slack-message', (data) => {
    console.log('New Slack message:', data);
  });

  socket.on('email-update', (data) => {
    console.log('Email update:', data);
  });

  return socket;
}
```

---

## Intelligence Gateway API Endpoints

All endpoints require Firebase ID token in `Authorization: Bearer <token>` header.

### CRM Endpoints
```bash
GET    /api/v2/crm/contacts           # List contacts
GET    /api/v2/crm/contacts/:id       # Get contact
POST   /api/v2/crm/contacts           # Create contact
PUT    /api/v2/crm/contacts/:id       # Update contact
DELETE /api/v2/crm/contacts/:id       # Delete contact
GET    /api/v2/crm/statistics         # Get statistics
POST   /api/v2/crm/contacts/:id/interactions  # Log interaction
```

### Slack Endpoints (Mock data until OAuth configured)
```bash
GET    /api/v2/slack/channels         # List channels
GET    /api/v2/slack/messages/:ch     # Get messages
POST   /api/v2/slack/messages/:ch     # Send message
GET    /api/v2/slack/users            # List users
GET    /api/v2/slack/search           # Search messages
```

### Gmail Endpoints (Mock data until OAuth configured)
```bash
GET    /api/v2/email/emails           # List emails (alias: /api/v2/gmail/emails)
GET    /api/v2/email/email/:id        # Get email
POST   /api/v2/email/send             # Send email
GET    /api/v2/email/search           # Search emails
```

### AI Endpoints
```bash
POST   /api/v1/ai/query               # AI query
POST   /api/v1/ai/chat                # AI chat
```

### Marketing Endpoints
```bash
POST   /api/v1/marketing/campaigns    # Create campaign
GET    /api/v1/marketing/campaigns    # List campaigns
POST   /api/v1/marketing/content      # Generate content
```

### ASO Endpoints
```bash
POST   /api/v1/aso/optimize           # Run optimization
GET    /api/v1/aso/keywords           # Get recommendations
POST   /api/v1/aso/analyze            # Analyze listing
```

---

## Testing Firebase Authentication

### Test 1: Create a Test User

```bash
# Via Firebase Console
# 1. Go to Authentication > Users
# 2. Click "Add user"
# 3. Email: test@xynergy.com, Password: TestPassword123!
```

### Test 2: Get ID Token Programmatically

```javascript
// In browser console after login
import { getAuth } from 'firebase/auth';
const auth = getAuth();
const token = await auth.currentUser.getIdToken();
console.log('Firebase ID Token:', token);
```

### Test 3: Test API Call

```bash
# Get token from step 2
export FIREBASE_TOKEN="<your-firebase-id-token>"

# Test CRM endpoint
curl -H "Authorization: Bearer $FIREBASE_TOKEN" \
  https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/api/v2/crm/statistics
```

---

## Dual Authentication Support

The Intelligence Gateway supports **BOTH** Firebase ID tokens AND JWT tokens:

**Option 1: Firebase ID Token** (Recommended for new frontend)
- Get from Firebase Authentication
- Gateway validates with Firebase Admin SDK
- Full user profile available

**Option 2: JWT Token** (For existing xynergyos-backend integration)
- Get from xynergyos-backend login endpoint
- Gateway validates with JWT_SECRET
- Maintains backward compatibility

---

## Security Notes

### ✅ Safe to Commit
These values are safe to include in frontend code:
- `FIREBASE_API_KEY` - Public API key for Firebase SDK
- `FIREBASE_APP_ID` - Public app identifier
- All other Firebase config values

### 🔒 Keep Secret
These should NEVER be in frontend code:
- `JWT_SECRET` - Server-side only
- Firebase Admin SDK service account JSON
- OAuth client secrets

### Rate Limiting
- 100 requests per 15 minutes per IP
- Exceeding limit returns HTTP 429

---

## Next Steps

### For Frontend Team

1. **Copy environment files to your frontend repo:**
   ```bash
   cp .env.production <your-frontend-repo>/
   cp .env.development <your-frontend-repo>/
   ```

2. **Install Firebase SDK:**
   ```bash
   npm install firebase
   # or
   yarn add firebase
   ```

3. **Initialize Firebase** using the code examples above

4. **Test authentication flow:**
   - Create test user in Firebase Console
   - Implement login in your app
   - Test API calls with Firebase token

### For Backend/DevOps

1. **OAuth Credentials (Still Pending):**
   - Slack OAuth (for real Slack data)
   - Gmail OAuth (for real email access)

2. **Optional Services:**
   - Calendar Intelligence Service
   - Research Coordinator integration

---

## Support

**Documentation:**
- Intelligence Gateway: `xynergyos-intelligence-gateway/README.md`
- API Integration: `XYNERGY_API_INTEGRATION_GUIDE.md`
- Quick Reference: `QUICK_REFERENCE.md`

**Production URLs:**
- Gateway: https://xynergy-intelligence-gateway-835612502919.us-central1.run.app
- Health Check: https://xynergy-intelligence-gateway-835612502919.us-central1.run.app/health
- Firebase Console: https://console.firebase.google.com/project/xynergy-dev-1757909467

---

## Summary

✅ **Firebase API Key** - Stored in Secret Manager
✅ **Firebase App ID** - Stored in Secret Manager
✅ **Frontend Config Files** - Created (.env.production, .env.development)
✅ **Intelligence Gateway** - Accepts Firebase ID tokens
✅ **Dual Authentication** - Firebase + JWT both supported
✅ **All Endpoints** - Documented and ready

**Status:** Your frontend team can now integrate with the Intelligence Gateway using Firebase Authentication! 🎉
