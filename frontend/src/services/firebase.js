/**
 * firebase.js — Google Firebase Client SDK for ArenaMaxx Frontend
 *
 * Integrates the following Google Firebase & Cloud services:
 *   - Firebase App (core initialization)
 *   - Firebase Firestore (real-time event streaming to frontend)
 *   - Firebase Analytics (Google Analytics for Firebase)
 *   - Firebase Performance Monitoring
 *
 * Firebase Project: arenamaxx (Google Cloud Project ID: arenamaxx)
 * Region: us-central1
 */

import { initializeApp } from 'firebase/app';
import { getFirestore, collection, addDoc, getDocs, query, orderBy, limit, serverTimestamp } from 'firebase/firestore';
import { getAnalytics, logEvent } from 'firebase/analytics';
import { getPerformance } from 'firebase/performance';
import { getAuth, signInAnonymously, onAuthStateChanged } from 'firebase/auth';

// ─── Firebase Configuration ────────────────────────────────────────────────
// Configuration for Firebase project: arenamaxx
// Credentials are non-sensitive public config (safe to include in frontend)
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "demo-api-key",
  authDomain: "arenamaxx.firebaseapp.com",
  projectId: "arenamaxx",
  storageBucket: "arenamaxx.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_SENDER_ID || "413044465338",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:413044465338:web:arenamaxx",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-ARENAMAXX01",
};

// ─── Initialize Firebase Services ─────────────────────────────────────────
const firebaseApp = initializeApp(firebaseConfig);
const db = getFirestore(firebaseApp);
const auth = getAuth(firebaseApp);

// Analytics — only in production to avoid polluting dev data
let analytics = null;
let perf = null;
try {
  if (import.meta.env.PROD) {
    analytics = getAnalytics(firebaseApp);
    perf = getPerformance(firebaseApp);
    console.log('[ArenaMaxx] Firebase Analytics & Performance Monitoring active.');
  }
} catch (e) {
  console.warn('[ArenaMaxx] Firebase Analytics unavailable in this environment.');
}

// ─── Firestore Event Logging ───────────────────────────────────────────────

/**
 * Log a user interaction event to Google Cloud Firestore.
 * Used for tracking page views, feature usage, and navigation patterns.
 *
 * @param {string} eventName - The name of the event (e.g., 'page_view', 'seat_selected').
 * @param {Object} eventData - Additional event metadata.
 * @returns {Promise<string|null>} The Firestore document ID, or null on failure.
 */
export async function logFirestoreEvent(eventName, eventData = {}) {
  try {
    const docRef = await addDoc(collection(db, 'stadium_events'), {
      event: eventName,
      ...eventData,
      source: 'ArenaMaxx-Frontend',
      platform: navigator.platform,
      timestamp: serverTimestamp(),
    });
    return docRef.id;
  } catch (e) {
    console.warn(`[Firebase] Event log failed for '${eventName}':`, e.message);
    return null;
  }
}

/**
 * Log an event to Google Analytics for Firebase.
 *
 * @param {string} eventName - Analytics event name.
 * @param {Object} params - Event parameters for GA4.
 */
export function logAnalyticsEvent(eventName, params = {}) {
  if (analytics) {
    logEvent(analytics, eventName, params);
  }
}

/**
 * Retrieve the most recent stadium events from Cloud Firestore.
 * Used by the Dashboard to stream live event updates.
 *
 * @param {string} collectionName - The Firestore collection to query.
 * @param {number} maxResults - Maximum number of events to return.
 * @returns {Promise<Array>} Array of event documents from Firestore.
 */
export async function getRecentFirestoreEvents(collectionName = 'stadium_events', maxResults = 10) {
  try {
    const q = query(
      collection(db, collectionName),
      orderBy('timestamp', 'desc'),
      limit(maxResults)
    );
    const snapshot = await getDocs(q);
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
  } catch (e) {
    console.warn(`[Firebase] Firestore read failed for '${collectionName}':`, e.message);
    return [];
  }
}

/**
 * Initialize an anonymous session with Firebase Identity Platform.
 * This secures the client-side interactions and provides a unique uid.
 * 
 * @returns {Promise<string|null>} The Firebase user UID or null.
 */
export async function initializeAnonymousSession() {
  try {
    const userCredential = await signInAnonymously(auth);
    console.log('[Firebase] Anonymous session started:', userCredential.user.uid);
    return userCredential.user.uid;
  } catch (e) {
    console.error('[Firebase] Auth failed:', e.message);
    return null;
  }
}

export { firebaseApp, db, auth, analytics };
