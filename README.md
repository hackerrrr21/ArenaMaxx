# ArenaMaxx - Smart Stadium Management Platform

**ArenaMaxx** is a high-fidelity stadium management and attendee experience platform designed to revolutionize how physical venues operate. By blending real-time sensor data (simulated UWB), AR wayfinding, and AI-driven hospitality, ArenaMaxx transforms a static stadium into a living, responsive ecosystem.

---

## 🏗️ Vertical: Smart Infrastructure & Event Technology
This project falls under **Smart Cities & Venues**. It addresses the complex logistical challenges of large-scale event management, focusing on crowd safety, facility optimization, and personalized attendee services.

---

## 🧠 Approach and Logic

### Core Philosophy
The platform operates on a **Dual-Flow Architecture**:
1.  **Operational Intelligence (Dashboard)**: Real-time parsing of physical coordinates into actionable sector density insights.
2.  **Attendee Empowerment (Services)**: Direct access to facility status (Washrooms), smart navigation (AR Map), and convenient logistics (Food Ordering).

### Technical Logic
-   **Sector Ranking Algorithm**: Rather than plotting abstract dots on a map, the system mathematically calculates node densities within coordinate bounds (VIP, Food, East/West Gates) to provide color-coded occupancy alerts (Green/Amber/Red).
-   **AR Vector Calculus**: The AR module uses device orientation and destination vectors to project real-time directional HUDs over the camera feed.
-   **AI Integration**: A persistent Google Gemini-powered concierge manages navigation requests and provides contextual help across the platform.

---

## 🚀 How the Solution Works

### 1. Live Operational Dashboard
Displays real-time attendee counts and sector-specific congestion. It replaces complex CAD maps with intuitive progress bars that update via **WebSockets** as simulated nodes move across the stadium.

### 2. AR Wayfinding (Google Services Integration)
Attendees specify a destination (Sections, Washrooms, Gates). The system activates the camera and overlays a dynamic 3D guide pointing toward the exact physical location based on current stadium geometry.

### 3. Smart Food & Facility Management
-   **Food Portal**: Includes quantity-limited (max 5) ordering to prevent hoarding and manage kitchen load.
-   **Washroom Queueing**: Displays real-time occupancy and allows users to book "Preferred Time Slots" for specific blocks (Men/Women).

### 4. Gemini AI Concierge
A persistent AI assistant that can take actions. A user can say *"I'm hungry"*, and the Gemini assistant will intelligently explain the food options and physically navigate the user to the Food page.

---

## 📝 Assumptions Made
-   **Data Simulation**: In a production environment, physical UWB (Ultra-Wideband) sensors or Wi-Fi triangulation would provide the `x/y` coordinates that the `CrowdSimulator` currently generates via a random-walk algorithm.
-   **Connectivity**: We assume stable stadium-wide Wi-Fi for WebSocket persistence.
-   **Local Persistence**: For this prototype, a local SQLite database handles ticketing and order states.

---

## ⭐ Evaluation Focus Areas

### 1. Code Quality
Built with a modular **React (Vite)** frontend and a **Flask-SocketIO** backend. State management is handled through hooks to ensure a high-performance, reactive UI.

### 2. Security
Implemented **Location Permission Gateways** for the AR module. Users must explicitly "Opt-In" to sharing location data before the AR engine or camera activates, ensuring privacy compliance.

### 3. Efficiency
Uses **Math-based filtering** for zone density. Instead of heavy SVG rendering of 1000+ points, the backend sends raw coordinates, and the frontend performs ultra-lightweight counting inside defined bounding boxes.

### 4. Testing
The system includes a built-in **Simulation Testbed (`simulation.py`)** that mimics chaotic match-day data, allowing developers to verify UI responses (like "Red Alert" congestion states) without physical hardware.

### 5. Accessibility
Features high-contrast icons (**Lucide-React**), large interactive targets for mobile use, and clear color-coded statuses (using semantic Green/Amber/Red) to communicate urgency and availability.

### 6. Google Services
Deeply integrated with **Google Gemini**. The assistant doesn't just chat; it interprets intent to drive platform navigation and provides a seamless "no-click" experience for complex requests.

---

## 🛠️ Local Setup

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. Create a `.env` file with `GOOGLE_API_KEY=your_key`
4. `python app.py`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`
