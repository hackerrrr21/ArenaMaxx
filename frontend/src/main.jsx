import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './App.css'
import { logFirestoreEvent, logAnalyticsEvent } from './services/firebase.js'

// ── Google Firebase: Log app initialization event ─────────────────────────
logFirestoreEvent('app_init', { version: '3.0.0', platform: 'web' });
logAnalyticsEvent('app_open', { platform: 'ArenaMaxx-Web' });

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
