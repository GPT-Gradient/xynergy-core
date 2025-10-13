import { config } from 'dotenv';
config();

export interface Config {
  port: number;
  nodeEnv: string;
  serviceName: string;
  gcpProjectId: string;
  gcpRegion: string;

  // Calendar OAuth credentials (reuses Gmail OAuth)
  calendar: {
    clientId?: string;
    clientSecret?: string;
    redirectUri: string;
  };

  // Firebase
  firebase: {
    projectId: string;
    serviceAccountPath?: string;
  };

  // Redis
  redis: {
    host: string;
    port: number;
    password?: string;
  };

  // Rate limiting
  rateLimit: {
    windowMs: number;
    maxRequests: number;
  };

  // CORS
  cors: {
    origins: string[];
  };

  // Pub/Sub
  pubsub: {
    calendarEventsTopic: string;
  };
}

export const appConfig: Config = {
  port: parseInt(process.env.PORT || '8080', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  serviceName: 'calendar-intelligence-service',
  gcpProjectId: process.env.GCP_PROJECT_ID || 'xynergy-dev-1757909467',
  gcpRegion: process.env.GCP_REGION || 'us-central1',

  calendar: {
    // Calendar uses the same OAuth credentials as Gmail
    clientId: process.env.GMAIL_CLIENT_ID,
    clientSecret: process.env.GMAIL_CLIENT_SECRET,
    redirectUri: process.env.CALENDAR_REDIRECT_URI ||
      'https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app/api/v2/calendar/oauth/callback',
  },

  firebase: {
    projectId: process.env.FIREBASE_PROJECT_ID || 'xynergy-dev-1757909467',
    serviceAccountPath: process.env.GOOGLE_APPLICATION_CREDENTIALS,
  },

  redis: {
    host: process.env.REDIS_HOST || '10.0.0.3',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD,
  },

  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10),
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '200', 10),
  },

  cors: {
    origins: (process.env.CORS_ORIGINS || 'http://localhost:3000,https://xynergyos.com').split(','),
  },

  pubsub: {
    calendarEventsTopic: process.env.CALENDAR_EVENTS_TOPIC || 'calendar-events',
  },
};
