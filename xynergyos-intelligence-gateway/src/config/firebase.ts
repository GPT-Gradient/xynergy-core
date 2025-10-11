import admin from 'firebase-admin';
import { appConfig } from './config';

let firebaseApp: admin.app.App;

export const initializeFirebase = (): admin.app.App => {
  if (firebaseApp) {
    return firebaseApp;
  }

  // In Cloud Run, Application Default Credentials are used
  if (appConfig.nodeEnv === 'production') {
    firebaseApp = admin.initializeApp({
      projectId: appConfig.firebase.projectId,
    });
  } else {
    // Local development
    const serviceAccount = appConfig.firebase.serviceAccountPath
      ? require(appConfig.firebase.serviceAccountPath)
      : undefined;

    firebaseApp = admin.initializeApp({
      credential: serviceAccount
        ? admin.credential.cert(serviceAccount)
        : admin.credential.applicationDefault(),
      projectId: appConfig.firebase.projectId,
    });
  }

  return firebaseApp;
};

export const getFirebaseAuth = (): admin.auth.Auth => {
  if (!firebaseApp) {
    initializeFirebase();
  }
  return admin.auth();
};

export const getFirestore = (): admin.firestore.Firestore => {
  if (!firebaseApp) {
    initializeFirebase();
  }
  return admin.firestore();
};
