# Global Flight Intelligence Dashboard

## Overview

Global Flight Intelligence Dashboard is a production-style aviation intelligence platform that combines real-time flight tracking, route intelligence, anomaly detection, airport analytics, and historical replay capabilities within a modern intelligence dashboard.

The platform integrates live aviation data from OpenSky Network and automatically falls back to a synthetic intelligence engine when live data is unavailable. This ensures uninterrupted operation while maintaining a realistic monitoring and analysis environment.

The dashboard follows the Real Rails intelligence-layer architecture, featuring a 70/30 layout with a primary visualization stage and a dedicated intelligence sidebar.

---

## Core Features

### Live Flight Intelligence

* Real-time aircraft tracking using OpenSky Network.
* Up to 80 live aircraft state vectors.
* Country, altitude, heading, speed, and callsign information.
* Automatic refresh every 15 seconds.

### Synthetic Intelligence Engine

* Generates realistic flight movements.
* Generates route density data.
* Generates intelligence alerts.
* Generates historical replay snapshots.
* Activates automatically when live sources are unavailable.

### Intelligence Layer

* Active alerts panel.
* Route density analysis.
* Why This Matters intelligence section.
* Who Controls The Rail intelligence section.
* Downloadable intelligence data.
* Advanced filtering controls.

### Route Density Analytics

* Real route corridors derived from live aircraft data.
* Synthetic route generation fallback.
* Identification of major traffic corridors.

### Alert Intelligence Engine

Live anomaly detection based on:

* Speed deviations
* Altitude anomalies
* Route divergence
* Signal loss conditions

Fallback synthetic alert generation is available when live feeds are unavailable.

### Historical Replay

* Replay previous intelligence snapshots.
* Live replay generation from OpenSky-derived data.
* Synthetic replay generation fallback.

### Airport Intelligence Drill-Down

* Airport-specific traffic summaries.
* Flight activity monitoring.
* Alert overview.
* Operational analytics.

### Data Export

* Download intelligence datasets as JSON.
* Export filtered dashboard information.

---

## Technology Stack

### Frontend

* Next.js
* React
* TypeScript
* Leaflet
* Tailwind CSS

### Backend

* Python
* FastAPI
* Uvicorn

### Data Sources

* OpenSky Network (Live)
* Synthetic Intelligence Engine (Fallback)

---

## Architecture

Next.js Dashboard
↓
FastAPI Backend
↓
Live OpenSky Adapter
+
Synthetic Intelligence Engine
↓
Intelligence Layer
↓
Visualization & Analytics

---

## Data Refresh Strategy

### Live Mode

* Flights refresh every 15 seconds.
* Route Density derives from live aircraft.
* Alerts derive from live aircraft anomalies.
* Historical Replay derives from live aircraft states.

## Mock Data Package

The project includes a dedicated mock-data package for development,
testing, demonstrations, and fallback operation.

Features:

- Data dictionary and schema definitions
- Synthetic flight, alert, route, and airport datasets
- CSV export support
- JSON export support
- Edge-case simulation scenarios
- Explicit synthetic-data labeling

All synthetic records include a `SYNTHETIC_LABEL` field to ensure
they can be clearly distinguished from live OpenSky data.

---

## Installation

### Backend

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend:

http://localhost:8000

### Frontend

```bash
cd frontend

npm install

npm run dev
```

Frontend:

http://localhost:3000

---

## API Endpoints

GET /api/flights

GET /api/alerts

GET /api/routes

GET /api/airports

GET /api/airport/{code}

GET /api/replay

GET /api/download

---

## Future Enhancements

* ADS-B Exchange integration
* Enhanced anomaly detection models
* Aircraft search functionality
* Full WebSocket frontend integration
* Cloud deployment
* Predictive aviation analytics

---

## Disclaimer

This platform combines live aviation information and synthetic demonstration data.

Synthetic data is clearly labeled and exists solely for educational, research, and demonstration purposes.
