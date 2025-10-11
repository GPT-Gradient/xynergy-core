import { config } from 'dotenv';
config();

interface Config {
  port: number;
  nodeEnv: string;
  gcpProjectId: string;
  gcpRegion: string;

  // Service URLs
  services: {
    aiRouting: string;
    slackIntelligence: string;
    gmailIntelligence: string;
    calendarIntelligence: string;
    crmEngine: string;
  };

  // Redis
  redis: {
    host: string;
    port: number;
    password?: string;
  };

  // Firebase
  firebase: {
    projectId: string;
    serviceAccountPath?: string;
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
}

export const appConfig: Config = {
  port: parseInt(process.env.PORT || '8080', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  gcpProjectId: process.env.GCP_PROJECT_ID || 'xynergy-dev-1757909467',
  gcpRegion: process.env.GCP_REGION || 'us-central1',

  services: {
    aiRouting: process.env.AI_ROUTING_URL ||
      'https://xynergy-ai-routing-engine-835612502919.us-central1.run.app',
    slackIntelligence: process.env.SLACK_INTELLIGENCE_URL ||
      'https://slack-intelligence-service-835612502919.us-central1.run.app',
    gmailIntelligence: process.env.GMAIL_INTELLIGENCE_URL ||
      'https://gmail-intelligence-service-835612502919.us-central1.run.app',
    calendarIntelligence: process.env.CALENDAR_INTELLIGENCE_URL || '',
    crmEngine: process.env.CRM_ENGINE_URL ||
      'https://crm-engine-vgjxy554mq-uc.a.run.app',
  },

  redis: {
    host: process.env.REDIS_HOST || '10.0.0.3',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD,
  },

  firebase: {
    projectId: process.env.FIREBASE_PROJECT_ID || 'xynergy-dev-1757909467',
    serviceAccountPath: process.env.GOOGLE_APPLICATION_CREDENTIALS,
  },

  rateLimit: {
    windowMs: 60 * 1000, // 1 minute
    maxRequests: 100,
  },

  cors: {
    origins: process.env.CORS_ORIGINS?.split(',') || [
      'http://localhost:3000',
      'https://xynergyos.com',
      'https://*.xynergyos.com',
    ],
  },
};
