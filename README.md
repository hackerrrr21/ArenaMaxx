# ArenaMaxx — Smart Stadium Management Platform

> Built for **PromptWars Virtual** | Powered by **Google Cloud**, **Firebase**, and **Gemini AI**

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-19-61dafb?logo=react)](https://react.dev)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore%20%7C%20Analytics-orange?logo=firebase)](https://firebase.google.com)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-Deployed-4285F4?logo=googlecloud)](https://cloud.google.com/run)
[![Gemini AI](https://img.shields.io/badge/Gemini%20AI-gemini--1.5--flash-blueviolet?logo=google)](https://deepmind.google/technologies/gemini)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📖 Overview

**ArenaMaxx** transforms passive stadium infrastructure into an intelligent, living ecosystem. From the moment a fan enters the gates to the final whistle, ArenaMaxx acts as their digital concierge — handling seat selection, food ordering, washroom queueing, live crowd analytics, and AI-powered navigation in one unified platform.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Google Cloud Run                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Flask Backend (Gunicorn + Eventlet)               │ │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │ │
│  │  │ REST API │  │SocketIO  │  │  Gemini AI    │   │ │
│  │  │ (Flask)  │  │(WebSocket│  │gemini-1.5-    │   │ │
│  │  │          │  │  )       │  │flash          │   │ │
│  │  └────┬─────┘  └────┬─────┘  └───────────────┘   │ │
│  │       │              │                             │ │
│  │  ┌────▼──────────────▼─────┐  ┌────────────────┐  │ │
│  │  │   SQLite (Prototype)    │  │Firebase Admin  │  │ │
│  │  │   → Cloud SQL (Prod)    │  │Firestore Client│  │ │
│  │  └─────────────────────────┘  └────────────────┘  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ▲
              WebSocket + REST API
                           │
┌─────────────────────────────────────────────────────────┐
│                 React Frontend (Vite)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │Dashboard │  │SeatMap   │  │Washrooms │  │AR Map  │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Firebase JS SDK (Firestore + Analytics + Perf)  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description | Technology |
|---|---|---|
| 🏟️ **Live Dashboard** | Real-time crowd density, gate status, zone analytics | Flask-SocketIO, WebSocket |
| 🎫 **Smart Seating** | Interactive seat map with section selection | React, SQLAlchemy |
| 🍔 **Food Ordering** | Virtual queue ordering with wait time estimates | REST API, Firestore |
| 🚻 **Washroom Tracker** | Live occupancy + timed slot booking | WebSocket, Firestore |
| 🗺️ **AR Wayfinding** | Camera-overlay navigation with compass direction | Web APIs |
| 🤖 **Gemini AI Concierge** | Agentic navigation — AI books services and navigates | Google Gemini 1.5 Flash |
| 🚨 **Emergency Help** | Dispatches nearest MaxxKnight responder | Real-time |
| 📊 **Analytics** | Google Analytics for Firebase + Cloud Logging | Firebase Analytics |

---

## 🛠️ Tech Stack

### Backend
- **Flask 3.0** — Lightweight Python web framework
- **Flask-SocketIO** — WebSocket support with Eventlet async mode
- **Flask-SQLAlchemy** — ORM for SQLite (prototype) / Cloud SQL (production)
- **Flask-Limiter** — Rate limiting (60 req/hr default)
- **Flask-Caching** — In-memory response caching (30s TTL)
- **Firebase Admin SDK** — Firestore event persistence
- **Google Cloud Logging** — Structured log ingestion
- **Google Gemini AI** (`gemini-1.5-flash`) — AI concierge

### Frontend
- **React 19 + Vite** — Modern reactive UI framework
- **Firebase JS SDK v11** — Firestore client, Analytics, Performance
- **Socket.IO Client** — Real-time WebSocket events
- **Lucide React** — Icon system
- **Custom CSS** — Glassmorphism design system

### Infrastructure
- **Google Cloud Run** — Containerized auto-scaling deployment
- **Google Cloud Firestore** — Real-time NoSQL event database
- **Google Cloud Logging** — Centralized log management
- **Firebase Hosting** — (Optional CDN hosting for frontend)
- **Docker** — Multi-stage build (Node → Python)

---

## 📁 Project Structure

```
ArenaMaxx/
├── .firebaserc              # Firebase project binding
├── firebase.json            # Firebase Hosting + Firestore config
├── firestore.rules          # Firestore security rules
├── firestore.indexes.json   # Firestore composite indexes
├── Dockerfile               # Multi-stage production build
│
├── backend/
│   ├── app.py               # Main Flask application + API routes
│   ├── firebase_service.py  # Firebase Admin SDK / Firestore integration
│   ├── models.py            # SQLAlchemy ORM models
│   ├── simulation.py        # Real-time crowd simulation engine
│   ├── test_app.py          # Comprehensive test suite (45+ tests)
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── App.jsx           # Root app + routing
    │   ├── App.css           # Global design system
    │   ├── main.jsx          # Entry point + Firebase initialization
    │   ├── pages/
    │   │   ├── Dashboard.jsx  # Live stadium overview
    │   │   ├── SeatMap.jsx    # Interactive seat selection
    │   │   ├── Concessions.jsx# Food & beverage ordering
    │   │   ├── Washrooms.jsx  # Washroom status & booking
    │   │   ├── Wayfinding.jsx # AR navigation map
    │   │   └── Landing.jsx    # Home / entry page
    │   ├── components/
    │   │   ├── SplashScreen.jsx
    │   │   └── GeminiChat.jsx
    │   └── services/
    │       ├── firebase.js    # Firebase JS SDK (Firestore + Analytics)
    │       └── socket.js      # Socket.IO WebSocket client
    └── package.json
```

---

## 🚀 Local Setup

### Prerequisites
- Python 3.12+
- Node.js 20+
- Google API Key (for Gemini AI)

### 1. Clone the Repository
```bash
git clone https://github.com/hackerrrr21/ArenaMaxx.git
cd ArenaMaxx
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env and add your GOOGLE_API_KEY
python app.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173` (frontend) and `http://localhost:8080` (backend).

---

## 🌐 Production Deployment (Google Cloud Run)

```bash
# 1. Build and push Docker image
gcloud builds submit --tag gcr.io/arenamaxx/platform

# 2. Deploy to Cloud Run with session affinity (required for WebSockets)
gcloud run deploy arenamaxx \
  --image gcr.io/arenamaxx/platform \
  --region us-central1 \
  --allow-unauthenticated \
  --session-affinity \
  --set-env-vars="GOOGLE_API_KEY=your_key_here"
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | ✅ Yes | Google Gemini AI API key |
| `SECRET_KEY` | Optional | Flask session secret (auto-generated if absent) |
| `GOOGLE_CLOUD_PROJECT` | Optional | GCP project ID for Cloud Logging |
| `PORT` | Optional | Server port (default: `8080`) |
| `VITE_FIREBASE_API_KEY` | Optional | Firebase frontend API key |
| `VITE_FIREBASE_APP_ID` | Optional | Firebase App ID |
| `VITE_FIREBASE_SENDER_ID` | Optional | Firebase Cloud Messaging Sender ID |

---

## 🧪 Running Tests

```bash
cd backend
pytest test_app.py -v --tb=short
```

**Coverage Areas:** Health checks, Seats API, Concessions, Washrooms, Gemini Chat, Security headers, Injection blocking, Firebase mocks, Content-Type enforcement — **45+ test cases**.

---

## 🔐 Security

- ✅ Input validation & injection pattern blocking (XSS, SQLi)
- ✅ Rate limiting (Flask-Limiter)
- ✅ Security headers: `X-Frame-Options`, `X-XSS-Protection`, `X-Content-Type-Options`, `CSP`, `Referrer-Policy`, `Permissions-Policy`
- ✅ Content-Type enforcement on all POST endpoints
- ✅ Firestore security rules (collection-level access control)
- ✅ API key managed via environment variables (never in source code)

---

## 🔮 Future Scope

- **IoT Integration** — Replace simulated crowd data with real UWB sensor feeds
- **Firebase Authentication** — Attendee login and personalized experience  
- **Cloud SQL Migration** — Replace SQLite with production-grade Cloud SQL (PostgreSQL)
- **Google Maps API** — Real stadium coordinates for AR wayfinding
- **Firebase Cloud Messaging** — Push notifications for queue updates
- **Vertex AI** — Advanced crowd prediction models

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ for PromptWars Virtual 2026*
