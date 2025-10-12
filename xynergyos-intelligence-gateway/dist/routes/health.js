"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const firebase_1 = require("../config/firebase");
const logger_1 = require("../utils/logger");
const config_1 = require("../config/config");
const router = (0, express_1.Router)();
// Basic health check
router.get('/', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'xynergyos-intelligence-gateway',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
    });
});
// Deep health check
router.get('/deep', async (req, res) => {
    const checks = {
        timestamp: new Date().toISOString(),
        service: 'xynergyos-intelligence-gateway',
        status: 'healthy',
        checks: {},
    };
    // Check Firestore
    try {
        const db = (0, firebase_1.getFirestore)();
        await db.collection('_health_check').doc('test').set({
            timestamp: new Date(),
        });
        checks.checks.firestore = 'healthy';
    }
    catch (error) {
        checks.checks.firestore = 'unhealthy';
        checks.status = 'degraded';
        logger_1.logger.error('Firestore health check failed', { error });
    }
    // Check service configuration
    checks.checks.services = {
        aiRouting: config_1.appConfig.services.aiRouting ? 'configured' : 'not_configured',
        slackIntelligence: config_1.appConfig.services.slackIntelligence ? 'configured' : 'not_configured',
        gmailIntelligence: config_1.appConfig.services.gmailIntelligence ? 'configured' : 'not_configured',
        calendarIntelligence: config_1.appConfig.services.calendarIntelligence ? 'configured' : 'not_configured',
        crmEngine: config_1.appConfig.services.crmEngine ? 'configured' : 'not_configured',
    };
    const statusCode = checks.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(checks);
});
exports.default = router;
//# sourceMappingURL=health.js.map