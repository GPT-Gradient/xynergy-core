"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const errorHandler_1 = require("../middleware/errorHandler");
const firebase_1 = require("../config/firebase");
const gmailService_1 = require("../services/gmailService");
const router = (0, express_1.Router)();
router.get('/', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    res.json({
        status: 'healthy',
        service: 'gmail-intelligence-service',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        mode: gmailService_1.gmailService.isInMockMode() ? 'mock' : 'production',
    });
}));
router.get('/deep', (0, errorHandler_1.asyncHandler)(async (req, res) => {
    const checks = {
        service: { status: 'healthy', name: 'gmail-intelligence-service' },
    };
    try {
        const firestore = (0, firebase_1.getFirestore)();
        await firestore.collection('_health_check').doc('test').get();
        checks.firebase = { status: 'healthy', firestoreConnected: true };
    }
    catch (error) {
        checks.firebase = { status: 'degraded', firestoreConnected: false };
    }
    try {
        const gmailStatus = await gmailService_1.gmailService.testConnection();
        checks.gmail = {
            status: gmailStatus.ok ? 'healthy' : 'degraded',
            connected: gmailStatus.ok,
            email: gmailStatus.email,
            mockMode: gmailService_1.gmailService.isInMockMode(),
        };
    }
    catch (error) {
        checks.gmail = { status: 'degraded', connected: false, mockMode: true };
    }
    const allHealthy = Object.values(checks).every((check) => check.status === 'healthy');
    res.json({
        status: allHealthy ? 'healthy' : 'degraded',
        service: 'gmail-intelligence-service',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        checks,
    });
}));
exports.default = router;
//# sourceMappingURL=health.js.map