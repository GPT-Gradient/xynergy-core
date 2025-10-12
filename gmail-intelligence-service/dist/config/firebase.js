"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.getFirestore = exports.getFirebaseAuth = exports.initializeFirebase = void 0;
const admin = __importStar(require("firebase-admin"));
const config_1 = require("./config");
const logger_1 = require("../utils/logger");
let firebaseApp = null;
/**
 * Initialize Firebase Admin SDK
 */
const initializeFirebase = () => {
    if (firebaseApp) {
        return firebaseApp;
    }
    try {
        if (config_1.appConfig.nodeEnv === 'production') {
            // In production, use Application Default Credentials
            firebaseApp = admin.initializeApp({
                projectId: config_1.appConfig.firebase.projectId,
            });
            logger_1.logger.info('Firebase initialized with Application Default Credentials');
        }
        else {
            // In development, use service account key if provided
            const serviceAccount = config_1.appConfig.firebase.serviceAccountPath
                ? require(config_1.appConfig.firebase.serviceAccountPath)
                : undefined;
            firebaseApp = admin.initializeApp({
                credential: serviceAccount
                    ? admin.credential.cert(serviceAccount)
                    : admin.credential.applicationDefault(),
                projectId: config_1.appConfig.firebase.projectId,
            });
            logger_1.logger.info('Firebase initialized for development');
        }
        return firebaseApp;
    }
    catch (error) {
        logger_1.logger.error('Failed to initialize Firebase', { error });
        throw error;
    }
};
exports.initializeFirebase = initializeFirebase;
/**
 * Get Firebase Auth instance
 */
const getFirebaseAuth = () => {
    if (!firebaseApp) {
        throw new Error('Firebase not initialized. Call initializeFirebase() first.');
    }
    return firebaseApp.auth();
};
exports.getFirebaseAuth = getFirebaseAuth;
/**
 * Get Firestore instance
 */
const getFirestore = () => {
    if (!firebaseApp) {
        throw new Error('Firebase not initialized. Call initializeFirebase() first.');
    }
    return firebaseApp.firestore();
};
exports.getFirestore = getFirestore;
//# sourceMappingURL=firebase.js.map