import * as admin from 'firebase-admin';
import { appConfig } from './config';
import { logger } from '../utils/logger';

let firebaseApp: admin.app.App | null = null;

/**
 * Initialize Firebase Admin SDK
 */
export const initializeFirebase = (): admin.app.App => {
  if (firebaseApp) {
    return firebaseApp;
  }

  try {
    if (appConfig.nodeEnv === 'production') {
      // In production, use Application Default Credentials
      firebaseApp = admin.initializeApp({
        projectId: appConfig.firebase.projectId,
      });
      logger.info('Firebase initialized with Application Default Credentials');
    } else {
      // In development, use service account key if provided
      const serviceAccount = appConfig.firebase.serviceAccountPath
        ? require(appConfig.firebase.serviceAccountPath)
        : undefined;

      firebaseApp = admin.initializeApp({
        credential: serviceAccount
          ? admin.credential.cert(serviceAccount)
          : admin.credential.applicationDefault(),
        projectId: appConfig.firebase.projectId,
      });
      logger.info('Firebase initialized for development');
    }

    return firebaseApp;
  } catch (error) {
    logger.error('Failed to initialize Firebase', { error });
    throw error;
  }
};

/**
 * Get Firebase Auth instance
 */
export const getFirebaseAuth = (): admin.auth.Auth => {
  if (!firebaseApp) {
    throw new Error('Firebase not initialized. Call initializeFirebase() first.');
  }
  return firebaseApp.auth();
};

/**
 * Get Firestore instance
 */
export const getFirestore = (): admin.firestore.Firestore => {
  if (!firebaseApp) {
    throw new Error('Firebase not initialized. Call initializeFirebase() first.');
  }
  return firebaseApp.firestore();
};
