import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './App.css'
import { logFirestoreEvent, logAnalyticsEvent, initializeAnonymousSession } from './services/firebase.js'

// ── Google Firebase: Start Secure Session & Log initialization ──────────
initializeAnonymousSession();
logFirestoreEvent('app_init', { version: '3.0.0', platform: 'web' });
logAnalyticsEvent('app_open', { platform: 'ArenaMaxx-Web' });

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
