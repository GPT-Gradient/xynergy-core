"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.appConfig = void 0;
const dotenv_1 = require("dotenv");
(0, dotenv_1.config)();
exports.appConfig = {
    port: parseInt(process.env.PORT || '8080', 10),
    nodeEnv: process.env.NODE_ENV || 'development',
    gcpProjectId: process.env.GCP_PROJECT_ID || 'xynergy-dev-1757909467',
    gcpRegion: process.env.GCP_REGION || 'us-central1',
    services: {
        aiRouting: process.env.AI_ROUTING_URL ||
            'https://xynergy-ai-routing-engine-835612502919.us-central1.run.app',
        aiAssistant: process.env.AI_ASSISTANT_URL ||
            'https://xynergy-ai-assistant-vgjxy554mq-uc.a.run.app',
        slackIntelligence: process.env.SLACK_INTELLIGENCE_URL ||
            'https://slack-intelligence-service-835612502919.us-central1.run.app',
        gmailIntelligence: process.env.GMAIL_INTELLIGENCE_URL ||
            'https://gmail-intelligence-service-835612502919.us-central1.run.app',
        calendarIntelligence: process.env.CALENDAR_INTELLIGENCE_URL || '',
        crmEngine: process.env.CRM_ENGINE_URL ||
            'https://crm-engine-vgjxy554mq-uc.a.run.app',
        marketingEngine: process.env.MARKETING_ENGINE_URL ||
            'https://marketing-engine-vgjxy554mq-uc.a.run.app',
        asoEngine: process.env.ASO_ENGINE_URL ||
            'https://aso-engine-vgjxy554mq-uc.a.run.app',
        researchCoordinator: process.env.RESEARCH_COORDINATOR_URL || '',
    },
    redis: {
        host: process.env.REDIS_HOST || '10.229.184.219',
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
        origins: process.env.CORS_ORIGINS?.split(',') || (process.env.NODE_ENV === 'production'
            ? [
                'https://xynergyos-frontend-vgjxy554mq-uc.a.run.app',
                'https://xynergyos.clearforgetech.com',
                'https://xynergy-platform.com',
                'https://*.xynergy.com',
                'https://*.xynergyos.com',
            ]
            : [
                'http://localhost:3000',
                'http://localhost:5173',
                'http://localhost:8080',
                'https://xynergyos-frontend-vgjxy554mq-uc.a.run.app',
                'https://xynergyos.clearforgetech.com',
            ]),
    },
};
//# sourceMappingURL=config.js.map