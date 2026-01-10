/**
 * Google Firebase Client SDK Initialization
 * ==========================================
 * GOOGLE CLOUD IDENTITY PLATFORM:
 * - Firebase Authentication (Google's Enterprise Auth)
 * - Google Sign-In OAuth 2.0 (Primary Auth Method)
 * - Firebase Cloud Messaging (Push Notifications - Ready)
 * - Firebase Analytics (User Tracking - Ready)
 * 
 * This module initializes the Firebase SDK for client-side
 * Google authentication services.
 */

import { initializeApp, getApps, FirebaseApp } from 'firebase/app';
import { getAuth, Auth } from 'firebase/auth';

// Firebase config - should be in environment variables
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || '',
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || '',
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || '',
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || '',
};

// Initialize Firebase (singleton)
let app: FirebaseApp;
if (getApps().length === 0) {
  app = initializeApp(firebaseConfig);
} else {
  app = getApps()[0];
}

// Initialize Auth
export const auth: Auth = getAuth(app);

export default app;

