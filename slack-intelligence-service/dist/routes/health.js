"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const config_1 = require("../config/config");
const firebase_1 = require("../config/firebase");
const slackService_1 = require("../services/slackService");
const logger_1 = require("../utils/logger");
const router = (0, express_1.Router)();
/**
 * GET /health
 * Basic health check
 */
router.get('/', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    res.json({
        status: 'healthy',
        service: config_1.appConfig.serviceName,
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        mode: slackService_1.slackService.isInMockMode() ? 'mock' : 'production',
    });
}));
/**
 * GET /health/deep
 * Deep health check with dependency validation
 */
router.get('/deep', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const checks = {
        service: {
            status: 'healthy',
            name: config_1.appConfig.serviceName,
        },
    };
    // Check Firebase/Firestore
    try {
        const firestore = (0, firebase_1.getFirestore)();
        const testDoc = await firestore.collection('_health_check').doc('test').get();
        checks.firebase = {
            status: 'healthy',
            firestoreConnected: true,
        };
    }
    catch (error) {
        logger_1.logger.warn('Firestore health check failed', { error: error.message });
        checks.firebase = {
            status: 'degraded',
            firestoreConnected: false,
            error: error.message,
        };
    }
    // Check Slack API configuration (not per-user since health check is public)
    checks.slack = {
        status: slackService_1.slackService.isInMockMode() ? 'degraded' : 'healthy',
        configured: !slackService_1.slackService.isInMockMode(),
        mockMode: slackService_1.slackService.isInMockMode(),
        note: 'Health check does not test per-user OAuth tokens',
    };
    // Determine overall status
    const allHealthy = Object.values(checks).every((check) => check.status === 'healthy');
    res.json({
        status: allHealthy ? 'healthy' : 'degraded',
        service: config_1.appConfig.serviceName,
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        checks,
    });
}));
exports.default = router;
//# sourceMappingURL=health.js.map