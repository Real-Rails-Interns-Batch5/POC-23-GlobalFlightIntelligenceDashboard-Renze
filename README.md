# Global Flight Intelligence Dashboard

## Overview

Global Flight Intelligence Dashboard is a production-style aviation intelligence platform that combines flight tracking, route intelligence, anomaly detection, airport analytics, and historical replay capabilities in a modern intelligence dashboard.

The platform integrates aviation data from OpenSky Network and automatically falls back to a synthetic intelligence engine when live data is unavailable. This supports uninterrupted demonstrations and analysis while distinguishing synthetic records from live data.

The dashboard follows the Real Rails intelligence-layer architecture, featuring a 70/30 layout with a primary visualization stage and a dedicated intelligence sidebar.

## Core Features

### Live Flight Intelligence
- Flight tracking using OpenSky Network data.
- Up to 80 live aircraft state vectors.
- Country, altitude, heading, speed, and callsign information.
- Automatic refresh every 15 seconds.

### Synthetic Intelligence Engine
- Generates realistic flight movements.
- Generates route density data and intelligence alerts.
- Generates historical replay snapshots.
- Activates as a fallback when live data is unavailable.

### Intelligence Layer
- Active alerts panel.
- Route density analysis.
- “Why This Matters” intelligence section.
- “Who Controls The Rail” intelligence section.
- Downloadable intelligence data.
- Advanced filtering controls.

### Route Density Analytics
- Route corridors derived from available flight data.
- Synthetic route generation fallback.
- Identification of major traffic corridors.

### Alert Intelligence Engine
Anomaly detection covers:
- Speed deviations.
- Altitude anomalies.
- Route divergence.
- Signal loss conditions.

Synthetic alert generation is available when live feeds are unavailable.

### Historical Replay
- Replay of previous intelligence snapshots.
- Replay generation using available flight data.
- Synthetic replay generation fallback.

### Airport Intelligence Drill-Down
- Airport-specific traffic summaries.
- Flight activity monitoring.
- Alert overview.
- Operational analytics.

### Data Export
- Download intelligence datasets as JSON.
- Export filtered dashboard information.

## Technology Stack

### Frontend
- Next.js
- React
- TypeScript
- Leaflet
- Tailwind CSS

### Backend
- Python
- FastAPI
- Uvicorn

### Containerization
- Docker
- Separate frontend and backend container images

### Data Sources
- OpenSky Network
- Synthetic Intelligence Engine (fallback)

## Architecture

```text
Browser
   |
   v
Next.js Dashboard
   |
   v
FastAPI Backend
   |
   +-----------------------+
   |                       |
   v                       v
OpenSky Data Adapter   Synthetic Intelligence
   |                       |
   +-----------+-----------+
               |
               v
      Intelligence APIs
               |
               v
     Dashboard Visualizations
```

The frontend communicates with the FastAPI backend through HTTP API endpoints. The backend provides flight information, alerts, route data, airport analytics, and replay data.

## Data Refresh Strategy

### Live Mode
- Flight information refreshes every 15 seconds in the dashboard.
- Route density derives from available flight data.
- Alerts are generated from available aircraft information and anomaly rules.
- Historical replay uses available flight-state information.

Live data availability depends on the upstream data source. Synthetic fallback data may be used when live data is unavailable.

## Mock Data Package

The project includes a dedicated mock-data package for development, testing, demonstrations, and fallback operation.

Features include:
- Data dictionary and schema definitions.
- Synthetic flight, alert, route, and airport datasets.
- CSV export support.
- JSON export support.
- Edge-case simulation scenarios.
- Explicit synthetic-data labeling.

Synthetic records include a `SYNTHETIC_LABEL` field so they can be distinguished from live OpenSky data.

## Prerequisites

For normal local development:
- Python 3.10 or a compatible version supported by the backend dependencies.
- Node.js and npm.
- Git.

For Docker-based execution:
- Docker Desktop on Windows or macOS, or Docker Engine on Linux.

## Installation and Local Development

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd flight-intelligence
```

Replace `<YOUR_REPOSITORY_URL>` with the actual Git repository URL.

### 2. Start the backend

Open a terminal in the project root:

```powershell
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the API server:

```powershell
uvicorn main:app --reload --port 8000
```

Backend:
- API base URL: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs

Keep this terminal running.

### 3. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

The frontend uses `NEXT_PUBLIC_API_BASE_URL` to configure its backend API address. For local development, the default is:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

If needed, create `frontend/.env.local` with this setting. Restart the frontend development server after changing environment variables.

## Running with Docker

The repository contains separate Dockerfiles for the frontend and backend. This allows each service to be built and run independently without manually installing its application dependencies on the host.

### 1. Build the backend image

Run these commands from the project root:

```powershell
docker build -f backend/Dockerfile -t flight-backend ./backend
```

### 2. Start the backend container

```powershell
docker run -d --name flight-backend-test -p 8000:8000 flight-backend
```

Check the running container:

```powershell
docker ps
```

Test the backend at http://localhost:8000/docs.

### 3. Build the frontend image

From the project root:

```powershell
docker build -f frontend/Dockerfile -t flight-frontend ./frontend
```

The frontend image uses a production Next.js build.

### 4. Start the frontend container

```powershell
docker run -d --name flight-frontend-test -p 3000:3000 flight-frontend
```

Open http://localhost:3000 in a browser.

For the dashboard to load data, the frontend must be configured to reach the backend API at `http://localhost:8000` in this local-browser setup.

### 5. Stop and remove the test containers

When finished, run:

```powershell
docker stop flight-frontend-test flight-backend-test
docker rm flight-frontend-test flight-backend-test
```

These commands remove the containers, not the Docker images or source code.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/flights` | Flight data |
| GET | `/api/alerts` | Intelligence alerts |
| GET | `/api/routes` | Route data |
| GET | `/api/airports` | Airport data |
| GET | `/api/airport/{code}` | Airport-specific information |
| GET | `/api/replay` | Historical replay data |
| GET | `/api/download` | Downloadable intelligence data |

Interactive endpoint documentation is available at `/docs` while the backend is running.

## Repository Structure

```text
flight-intelligence/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── mock_data/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.ts
│   └── Dockerfile
├── .gitignore
└── README.md
```

This is a representative structure; additional project files may be present.

## Configuration and Security

- Do not commit `.env.local`, API credentials, access tokens, or other secrets.
- Do not commit Python virtual environments or `node_modules`.
- Configure the frontend API URL appropriately for local development and deployment.
- For production deployment, configure the backend CORS policy to allow the deployed frontend origin.
- The frontend's `NEXT_PUBLIC_` environment variables are embedded during the Next.js build, so the correct API URL must be supplied when producing a production image.

## Deployment Status

The frontend and backend Docker images have been built and tested locally. The dashboard has been verified to load its flight data, alerts, and map in the local container setup.

**Azure deployment is a separate pending step.** The project is being prepared for deployment using Azure Container Apps.

## Future Enhancements

- ADS-B Exchange integration.
- Enhanced anomaly detection models.
- Aircraft search functionality.
- Full WebSocket frontend integration.
- Predictive aviation analytics.
- Cloud deployment and monitoring.

## Disclaimer

This platform combines live aviation information and synthetic demonstration data. Synthetic data is intended for educational, research, development, and demonstration purposes and should not be interpreted as verified live aviation information.
