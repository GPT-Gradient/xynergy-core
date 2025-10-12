"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.appConfig = void 0;
const dotenv_1 = require("dotenv");
(0, dotenv_1.config)();
exports.appConfig = {
    port: parseInt(process.env.PORT || '8080', 10),
    nodeEnv: process.env.NODE_ENV || 'development',
    serviceName: 'slack-intelligence-service',
    gcpProjectId: process.env.GCP_PROJECT_ID || 'xynergy-dev-1757909467',
    gcpRegion: process.env.GCP_REGION || 'us-central1',
    slack: {
        botToken: process.env.SLACK_BOT_TOKEN,
        signingSecret: process.env.SLACK_SIGNING_SECRET,
        appToken: process.env.SLACK_APP_TOKEN,
        clientId: process.env.SLACK_CLIENT_ID,
        clientSecret: process.env.SLACK_CLIENT_SECRET,
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
        maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10),
    },
    cors: {
        origins: (process.env.CORS_ORIGINS || 'http://localhost:3000,https://xynergyos.com').split(','),
    },
    pubsub: {
        slackEventsTopic: process.env.SLACK_EVENTS_TOPIC || 'slack-events',
    },
};
//# sourceMappingURL=config.js.map