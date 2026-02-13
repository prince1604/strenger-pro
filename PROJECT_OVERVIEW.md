# Strenger Pro - Advanced Proximity P2P Chat

## 1. Project Vision
**Strenger Pro** is a high-performance, security-focused anonymous chat platform. Unlike traditional chat apps, it emphasizes **proximity discovery** (finding people nearby) and **P2P Privacy** (direct browser-to-browser communication).

## 2. Core Technologies
*   **Backend**: FastAPI (Python 3.10+) - Orchestrates authentication and signaling.
*   **Real-time Protocol**: WebSockets - Maintains a live connection for location updates and signaling.
*   **Chat Protocol**: WebRTC (P2P DataChannel) - Messages are sent directly between users, bypassing the server for near-zero latency and ultimate privacy.
*   **Database**: MySQL with **Spatial Indexing** - Uses `ST_Distance_Sphere` for high-speed neighbor discovery.
*   **Security**: JWT (HS256) for session management and `bcrypt` (12 rounds) for identity protection.
*   **UI/UX**: HTML5/CSS3 with **Glassmorphism** design and **Leaflet.js** for real-time map visualization.

## 3. High-Speed Features
### ⚡ Proximity Matching Engine
The system uses MySQL's built-in spatial geometry. When a user clicks "Search", the backend scans the `active_sessions` table using a spatial index to find the physically closest user in milliseconds.

### 🔒 P2P Tunneling (WebRTC)
The backend acts only as a "Signaling Server". Once two users are matched, their browsers exchange "Offers" and "Answers" via WebSockets. They then establish a **direct peer-to-peer connection**.
*   **Result**: Message delivery is as fast as your internet allows (usually < 10ms).
*   **Privacy**: Even if the server is compromised, your actual P2P chat messages are never stored in any database.

### 🛰️ Live Map Discovery
The sidebar features a real-time dark-themed map. Every active user on the platform appears as a live node. The map updates dynamically via WebSocket broadcasts whenever someone enters or leaves discovery mode.

## 4. Operational Activity Log (`strenger_activity.log`)
A centralized project log keeps track of every vital metric:
*   **REG-SUCCESS**: New Identities created.
*   **AUTH-SUCCESS**: Secure sessions initiated.
*   **P2P-MATCH**: Neighbor pairings.
*   **CHAT-LOG**: Centralized message auditing (optional/configurable).

## 5. Deployment Guidelines
*   **SSL Required**: To use browser Geolocation (GPS) and WebRTC, the project **must** be hosted on an `https://` domain.
*   **Database**: Ensure XAMPP/MySQL is running with the `ST_GeomFromText` extension enabled.

---
**Current Status**: STABLE (v2.0.0). All protocols (Socket, WebRTC, Proximity) are fully synchronized and optimized for speed.
