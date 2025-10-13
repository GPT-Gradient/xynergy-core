import { config } from 'dotenv';
config();

interface Config {
  port: number;
  nodeEnv: string;
  environment: 'dev' | 'prod' | 'local'; // NEW: Environment identifier
  mockMode: boolean; // NEW: Mock mode for external APIs
  gcpProjectId: string;
  gcpRegion: string;

  // Service URLs
  services: {
    aiRouting: string;
    aiAssistant: string;
    slackIntelligence: string;
    gmailIntelligence: string;
    calendarIntelligence: string;
    crmEngine: string;
    marketingEngine: string;
    asoEngine: string;
    researchCoordinator: string;
    memoryService: string;
  };

  // Redis
  redis: {
    host: string;
    port: number;
    password?: string;
    keyPrefix: string; // NEW: Environment-specific key prefix
  };

  // Firebase
  firebase: {
    projectId: string;
    serviceAccountPath?: string;
  };

  // Firestore
  firestore: {
    collectionPrefix: string; // NEW: Environment-specific collection prefix
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

// Detect environment from XYNERGY_ENV or default to 'dev'
const environment = (process.env.XYNERGY_ENV as 'dev' | 'prod' | 'local') ||
  (process.env.NODE_ENV === 'production' ? 'prod' : 'dev');

// Mock mode: enabled in dev/local, disabled in production
const mockMode = process.env.MOCK_MODE === 'true' ||
  (environment !== 'prod' && process.env.MOCK_MODE !== 'false');

export const appConfig: Config = {
  port: parseInt(process.env.PORT || '8080', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  environment,
  mockMode,
  gcpProjectId: process.env.GCP_PROJECT_ID || 'xynergy-dev-1757909467',
  gcpRegion: process.env.GCP_REGION || 'us-central1',

  services: {
    aiRouting: process.env.AI_ROUTING_URL ||
      'https://xynergy-ai-routing-engine-835612502919.us-central1.run.app',
    aiAssistant: process.env.AI_ASSISTANT_URL ||
      'https://xynergy-ai-assistant-vgjxy554mq-uc.a.run.app',
    slackIntelligence: process.env.SLACK_INTELLIGENCE_URL ||
      (environment === 'prod'
        ? 'https://slack-intelligence-service-prod-835612502919.us-central1.run.app'
        : 'https://slack-intelligence-service-835612502919.us-central1.run.app'),
    gmailIntelligence: process.env.GMAIL_INTELLIGENCE_URL ||
      (environment === 'prod'
        ? 'https://gmail-intelligence-service-prod-835612502919.us-central1.run.app'
        : 'https://gmail-intelligence-service-835612502919.us-central1.run.app'),
    calendarIntelligence: process.env.CALENDAR_INTELLIGENCE_URL ||
      (environment === 'prod'
        ? 'https://calendar-intelligence-service-prod-835612502919.us-central1.run.app'
        : 'https://calendar-intelligence-service-835612502919.us-central1.run.app'),
    crmEngine: process.env.CRM_ENGINE_URL ||
      (environment === 'prod'
        ? 'https://crm-engine-prod-vgjxy554mq-uc.a.run.app'
        : 'https://crm-engine-vgjxy554mq-uc.a.run.app'),
    marketingEngine: process.env.MARKETING_ENGINE_URL ||
      'https://marketing-engine-vgjxy554mq-uc.a.run.app',
    asoEngine: process.env.ASO_ENGINE_URL ||
      'https://aso-engine-vgjxy554mq-uc.a.run.app',
    researchCoordinator: process.env.RESEARCH_COORDINATOR_URL ||
      'https://research-coordinator-835612502919.us-central1.run.app',
    memoryService: process.env.MEMORY_SERVICE_URL ||
      'https://living-memory-service-vgjxy554mq-uc.a.run.app',
  },

  redis: {
    host: process.env.REDIS_HOST || '10.229.184.219',
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD,
    keyPrefix: environment === 'prod' ? 'prod:' : 'dev:', // Environment-specific cache keys
  },

  firebase: {
    projectId: process.env.FIREBASE_PROJECT_ID || 'xynergy-dev-1757909467',
    serviceAccountPath: process.env.GOOGLE_APPLICATION_CREDENTIALS,
  },

  firestore: {
    // Use collection prefixes to separate dev/prod data
    collectionPrefix: environment === 'prod' ? 'prod_' : 'dev_',
  },

  rateLimit: {
    windowMs: 60 * 1000, // 1 minute
    maxRequests: environment === 'prod' ? 100 : 1000, // Higher limits in dev for testing
  },

  cors: {
    origins: process.env.CORS_ORIGINS?.split(',') ||
      (environment === 'prod'
        ? [
            'https://app.xynergyos.com',
            'https://xynergyos.com',
            'https://*.xynergyos.com',
            'https://xynergy-platform.com',
            'https://*.xynergy.com',
          ]
        : [
            'http://localhost:3000',
            'http://localhost:5173',
            'http://localhost:8080',
            'https://dev.xynergyos.com',
            'https://xynergyos-frontend-vgjxy554mq-uc.a.run.app',
            'https://xynergyos.clearforgetech.com',
          ]
      ),
  },
};

// Log environment on startup
console.log(`🚀 XynergyOS Intelligence Gateway`);
console.log(`📍 Environment: ${environment.toUpperCase()}`);
console.log(`🎭 Mock Mode: ${mockMode ? 'ENABLED' : 'DISABLED'}`);
console.log(`🗄️  Firestore Prefix: ${appConfig.firestore.collectionPrefix}`);
console.log(`🔑 Redis Key Prefix: ${appConfig.redis.keyPrefix}`);
