"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getFirestore = exports.getFirebaseAuth = exports.initializeFirebase = void 0;
const firebase_admin_1 = __importDefault(require("firebase-admin"));
const config_1 = require("./config");
let firebaseApp;
const initializeFirebase = () => {
    if (firebaseApp) {
        return firebaseApp;
    }
    // In Cloud Run, Application Default Credentials are used
    if (config_1.appConfig.nodeEnv === 'production') {
        firebaseApp = firebase_admin_1.default.initializeApp({
            projectId: config_1.appConfig.firebase.projectId,
        });
    }
    else {
        // Local development
        const serviceAccount = config_1.appConfig.firebase.serviceAccountPath
            ? require(config_1.appConfig.firebase.serviceAccountPath)
            : undefined;
        firebaseApp = firebase_admin_1.default.initializeApp({
            credential: serviceAccount
                ? firebase_admin_1.default.credential.cert(serviceAccount)
                : firebase_admin_1.default.credential.applicationDefault(),
            projectId: config_1.appConfig.firebase.projectId,
        });
    }
    return firebaseApp;
};
exports.initializeFirebase = initializeFirebase;
const getFirebaseAuth = () => {
    if (!firebaseApp) {
        (0, exports.initializeFirebase)();
    }
    return firebase_admin_1.default.auth();
};
exports.getFirebaseAuth = getFirebaseAuth;
const getFirestore = () => {
    if (!firebaseApp) {
        (0, exports.initializeFirebase)();
    }
    return firebase_admin_1.default.firestore();
};
exports.getFirestore = getFirestore;
//# sourceMappingURL=firebase.js.map