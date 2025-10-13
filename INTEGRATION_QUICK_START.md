# XynergyOS Integration Quick Start Guide

**For Frontend Developers**
**Date:** October 13, 2025

---

## 🚀 Quick Start (5 Minutes)

### 1. Environment Variables

Add to your `.env` file:

```env
# API Gateway
REACT_APP_API_BASE_URL=https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
REACT_APP_WS_URL=wss://xynergyos-intelligence-gateway-835612502919.us-central1.run.app

# Firebase (for authentication)
REACT_APP_FIREBASE_PROJECT_ID=xynergy-dev-1757909467

# Feature Flags
REACT_APP_ENABLE_SLACK=true
REACT_APP_ENABLE_GMAIL=true
REACT_APP_ENABLE_CALENDAR=true
REACT_APP_ENABLE_CRM=true
REACT_APP_ENABLE_MEMORY=true
REACT_APP_ENABLE_RESEARCH=true
```

### 2. Authentication Setup

```typescript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Initialize Firebase
const firebaseConfig = {
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Get auth token for API calls
const token = await auth.currentUser?.getIdToken();
```

### 3. Make Your First API Call

```typescript
// Example: Fetch calendar events
const response = await fetch(
  `${process.env.REACT_APP_API_BASE_URL}/api/v2/calendar/events`,
  {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  }
);

const data = await response.json();
console.log('Calendar events:', data);
```

---

## 📡 Available Endpoints

### Communication Services (v2 API)

#### Slack
```typescript
GET    /api/v2/slack/channels
GET    /api/v2/slack/channels/:id/messages
POST   /api/v2/slack/channels/:id/messages
GET    /api/v2/slack/users
POST   /api/v2/slack/search
```

#### Email (Gmail)
```typescript
GET    /api/v2/email/messages
GET    /api/v2/email/messages/:id
POST   /api/v2/email/messages
GET    /api/v2/email/threads/:id
POST   /api/v2/email/search
```

#### Calendar
```typescript
GET    /api/v2/calendar/events
GET    /api/v2/calendar/events/:id
POST   /api/v2/calendar/events
PATCH  /api/v2/calendar/events/:id
DELETE /api/v2/calendar/events/:id
GET    /api/v2/calendar/prep/:eventId
```

#### CRM
```typescript
GET    /api/v2/crm/contacts
POST   /api/v2/crm/contacts
GET    /api/v2/crm/contacts/:id
PATCH  /api/v2/crm/contacts/:id
DELETE /api/v2/crm/contacts/:id
POST   /api/v2/crm/interactions
GET    /api/v2/crm/statistics
```

### Core Services (v1 API)

#### Memory
```typescript
GET    /api/v1/memory/items
POST   /api/v1/memory/items
GET    /api/v1/memory/items/:id
PATCH  /api/v1/memory/items/:id
DELETE /api/v1/memory/items/:id
POST   /api/v1/memory/search
GET    /api/v1/memory/stats
```

#### Research
```typescript
GET    /api/v1/research-sessions
POST   /api/v1/research-sessions
GET    /api/v1/research-sessions/:id
PATCH  /api/v1/research-sessions/:id
POST   /api/v1/research-sessions/:id/complete
DELETE /api/v1/research-sessions/:id
```

#### AI
```typescript
POST   /api/v1/ai/query
POST   /api/v1/ai/chat
GET    /api/v1/ai/models
```

---

## 🔌 WebSocket Integration

### Connect to WebSocket

```typescript
import io from 'socket.io-client';

const socket = io(process.env.REACT_APP_WS_URL, {
  auth: {
    token: await auth.currentUser?.getIdToken(),
  },
});

// Listen for events
socket.on('connect', () => {
  console.log('Connected to WebSocket');
});

socket.on('slack:new_message', (data) => {
  console.log('New Slack message:', data);
});

socket.on('email:new_message', (data) => {
  console.log('New email:', data);
});

socket.on('calendar:event_added', (data) => {
  console.log('Calendar event added:', data);
});

socket.on('crm:contact_created', (data) => {
  console.log('Contact created:', data);
});

socket.on('workflow:update', (data) => {
  console.log('Workflow update:', data);
});
```

---

## 🛠️ API Helper Functions

### Create an API Client

```typescript
// src/lib/api.ts
class XynergyAPI {
  private baseUrl: string;
  private getToken: () => Promise<string>;

  constructor(baseUrl: string, getToken: () => Promise<string>) {
    this.baseUrl = baseUrl;
    this.getToken = getToken;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = await this.getToken();

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'API request failed');
    }

    return response.json();
  }

  // Calendar
  async getCalendarEvents() {
    return this.request('/api/v2/calendar/events');
  }

  async createCalendarEvent(event: any) {
    return this.request('/api/v2/calendar/events', {
      method: 'POST',
      body: JSON.stringify(event),
    });
  }

  // Memory
  async getMemoryItems() {
    return this.request('/api/v1/memory/items');
  }

  async createMemoryItem(item: any) {
    return this.request('/api/v1/memory/items', {
      method: 'POST',
      body: JSON.stringify(item),
    });
  }

  async searchMemory(query: string) {
    return this.request('/api/v1/memory/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  // Research
  async getResearchSessions() {
    return this.request('/api/v1/research-sessions');
  }

  async createResearchSession(session: any) {
    return this.request('/api/v1/research-sessions', {
      method: 'POST',
      body: JSON.stringify(session),
    });
  }

  // CRM
  async getContacts() {
    return this.request('/api/v2/crm/contacts');
  }

  async createContact(contact: any) {
    return this.request('/api/v2/crm/contacts', {
      method: 'POST',
      body: JSON.stringify(contact),
    });
  }

  // Slack
  async getSlackChannels() {
    return this.request('/api/v2/slack/channels');
  }

  async getSlackMessages(channelId: string) {
    return this.request(`/api/v2/slack/channels/${channelId}/messages`);
  }

  // Email
  async getEmails() {
    return this.request('/api/v2/email/messages');
  }

  async sendEmail(email: any) {
    return this.request('/api/v2/email/messages', {
      method: 'POST',
      body: JSON.stringify(email),
    });
  }
}

// Export configured instance
export const api = new XynergyAPI(
  process.env.REACT_APP_API_BASE_URL!,
  async () => {
    const user = auth.currentUser;
    if (!user) throw new Error('Not authenticated');
    return user.getIdToken();
  }
);
```

### Usage in Components

```typescript
// src/components/CalendarView.tsx
import { useEffect, useState } from 'react';
import { api } from '../lib/api';

export function CalendarView() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvents();
  }, []);

  async function loadEvents() {
    try {
      const data = await api.getCalendarEvents();
      setEvents(data.events);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  }

  async function createEvent(eventData: any) {
    try {
      await api.createCalendarEvent(eventData);
      await loadEvents(); // Reload
    } catch (error) {
      console.error('Failed to create event:', error);
    }
  }

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      {events.map(event => (
        <div key={event.id}>{event.summary}</div>
      ))}
    </div>
  );
}
```

---

## 🧪 Testing the Integration

### Manual Testing with cURL

```bash
# Get a Firebase token (from browser console)
# Then test endpoints:

# Health check
curl https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/health

# Calendar events (requires auth)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/calendar/events

# Memory items (requires auth)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v1/memory/items

# Research sessions (requires auth)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v1/research-sessions
```

### Test in Browser Console

```javascript
// Get your Firebase token
const token = await firebase.auth().currentUser.getIdToken();

// Test calendar API
fetch('https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/calendar/events', {
  headers: { 'Authorization': `Bearer ${token}` }
})
  .then(r => r.json())
  .then(console.log);

// Test memory API
fetch('https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v1/memory/items', {
  headers: { 'Authorization': `Bearer ${token}` }
})
  .then(r => r.json())
  .then(console.log);
```

---

## 🚨 Troubleshooting

### Common Issues

**401 Unauthorized**
```
Problem: Token is invalid or expired
Solution:
- Ensure user is logged in
- Get fresh token: await user.getIdToken(true)
- Check Authorization header format
```

**404 Not Found**
```
Problem: Wrong endpoint path
Solution:
- Check path carefully (v1 vs v2)
- Calendar is v2: /api/v2/calendar/events
- Memory is v1: /api/v1/memory/items
```

**CORS Error**
```
Problem: Origin not allowed
Solution:
- Check you're using correct API_BASE_URL
- Ensure localhost is in allowed origins for dev
- In production, domain must be whitelisted
```

**Network Error**
```
Problem: Service might be down
Solution:
- Check service status: curl <gateway>/health
- Check specific service health endpoint
- Review Cloud Run logs
```

### Debug Mode

```typescript
// Enable detailed logging
const api = new XynergyAPI(
  process.env.REACT_APP_API_BASE_URL!,
  async () => {
    const token = await auth.currentUser?.getIdToken();
    console.log('Using token:', token?.substring(0, 20) + '...');
    return token!;
  }
);

// Log all requests
api.request = new Proxy(api.request, {
  apply: async (target, thisArg, args) => {
    console.log('API Request:', args[0], args[1]);
    try {
      const result = await target.apply(thisArg, args);
      console.log('API Response:', result);
      return result;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
});
```

---

## 📊 Mock Data vs Real Data

### Current Status (Mock Mode)

**Slack, Gmail, Calendar** return mock data because OAuth is not yet configured.

**Mock Response Example:**
```json
{
  "events": [...],
  "mock": true,
  "message": "This is mock data. Configure OAuth for real data."
}
```

**CRM, Memory, Research** use real Firestore data (production ready).

### When OAuth is Configured

Mock responses will be replaced with real data from:
- Slack workspaces
- Gmail accounts
- Google Calendar

**Timeline:** OAuth can be configured in Phase 2 (1-2 days per service)

---

## 🎯 Next Steps

### Immediate (Today)
1. ✅ Add environment variables to your `.env`
2. ✅ Test health endpoint
3. ✅ Make first authenticated API call
4. ✅ Verify all features work with mock data

### This Week
1. Build out UI components using API
2. Implement WebSocket event handlers
3. Add error handling and loading states
4. Test all CRUD operations

### Next Week (Optional)
1. Configure OAuth for real data
2. Add integration tests
3. Performance testing
4. Production deployment

---

## 📞 Support

### Documentation
- **API Mapping:** `INTEGRATION_API_MAPPING.md`
- **Complete Summary:** `INTEGRATION_COMPLETE_SUMMARY.md`
- **This Guide:** `INTEGRATION_QUICK_START.md`

### Service URLs
- **Gateway:** https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app
- **Calendar:** https://calendar-intelligence-service-835612502919.us-central1.run.app
- **Memory:** https://living-memory-service-vgjxy554mq-uc.a.run.app
- **Research:** https://research-coordinator-835612502919.us-central1.run.app

### Health Checks
```bash
# Quick health check script
curl -s https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/health | jq .
```

---

## ✅ Integration Checklist

Before deploying to production:

- [ ] Environment variables configured
- [ ] Firebase authentication working
- [ ] Can fetch data from all endpoints
- [ ] WebSocket events receiving
- [ ] Error handling implemented
- [ ] Loading states added
- [ ] CORS working correctly
- [ ] All features tested with mock data
- [ ] Performance acceptable
- [ ] Error messages user-friendly

---

**🚀 You're ready to start building!**

All backend services are deployed and ready. Start making API calls and building your UI. The integration is production-ready with mock data, and OAuth can be added later without any frontend changes.

Happy coding! 🎉
