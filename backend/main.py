from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
import json
import random
from datetime import datetime, timedelta

app = FastAPI(title="Flight Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────
# OPENSKY ADAPTER
# ──────────────────────────────────────────
async def fetch_opensky_flights():
    url = "https://opensky-network.org/api/states/all"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            data = resp.json()
            flights = []
            if data and "states" in data and data["states"]:
                for s in data["states"][:80]:
                    if s[5] is None or s[6] is None:
                        continue
                    flights.append({
                        "id":       s[0] or "unknown",
                        "callsign": (s[1] or "N/A").strip(),
                        "country":  s[2] or "Unknown",
                        "lng":      s[5],
                        "lat":      s[6],
                        "altitude": round(s[7] or 0),
                        "speed":    round((s[9] or 0) * 1.94),
                        "heading":  round(s[10] or 0),
                        "source":   "OpenSky (live)"
                    })
            return flights
    except Exception as e:
        print(f"OpenSky fetch failed: {e}")
        return []

# ──────────────────────────────────────────
# STATIC DATA
# ──────────────────────────────────────────
AIRPORTS = [
    {"code": "DEL", "name": "Indira Gandhi Intl",  "lat": 28.56,  "lng": 77.10,  "city": "Delhi"},
    {"code": "BOM", "name": "Chhatrapati Shivaji", "lat": 19.09,  "lng": 72.87,  "city": "Mumbai"},
    {"code": "DXB", "name": "Dubai Intl",           "lat": 25.25,  "lng": 55.36,  "city": "Dubai"},
    {"code": "SIN", "name": "Changi Airport",       "lat": 1.36,   "lng": 103.99, "city": "Singapore"},
    {"code": "LHR", "name": "Heathrow",             "lat": 51.47,  "lng": -0.46,  "city": "London"},
    {"code": "JFK", "name": "John F Kennedy",       "lat": 40.64,  "lng": -73.78, "city": "New York"},
    {"code": "CDG", "name": "Charles de Gaulle",    "lat": 49.01,  "lng": 2.55,   "city": "Paris"},
    {"code": "NRT", "name": "Narita Intl",          "lat": 35.77,  "lng": 140.39, "city": "Tokyo"},
    {"code": "SYD", "name": "Kingsford Smith",      "lat": -33.94, "lng": 151.18, "city": "Sydney"},
    {"code": "GRU", "name": "Guarulhos Intl",       "lat": -23.43, "lng": -46.47, "city": "São Paulo"},
]

AIRLINES    = ["AI", "EK", "SQ", "BA", "AF", "UA", "LH", "QF", "TK", "CX"]
ALERT_TYPES = ["Altitude Anomaly", "Speed Deviation", "Route Divergence", "Squawk 7700", "No Signal"]
SEVERITIES  = ["low", "medium", "high"]
COUNTRIES = {
    "DEL": "India", "BOM": "India", "DXB": "UAE", "SIN": "Singapore",
    "LHR": "United Kingdom", "JFK": "United States", "CDG": "France",
    "NRT": "Japan", "SYD": "Australia", "GRU": "Brazil",
}

# ──────────────────────────────────────────
# MOCK DATA ENGINE
# ──────────────────────────────────────────
def make_mock_flights(count=60):
    flights = []
    for i in range(count):
        airline = random.choice(AIRLINES)
        num     = random.randint(100, 999)
        origin  = random.choice(AIRPORTS)
        dest    = random.choice(AIRPORTS)
        frac    = random.random()
        lat     = origin["lat"] + frac * (dest["lat"] - origin["lat"]) + random.uniform(-2, 2)
        lng     = origin["lng"] + frac * (dest["lng"] - origin["lng"]) + random.uniform(-2, 2)
        flights.append({
            "id":       f"mock-{i}",
            "callsign": f"{airline}{num}",
            "country":  COUNTRIES.get(origin["code"], "Unknown"),
            "lat":      round(lat, 4),
            "lng":      round(lng, 4),
            "altitude": random.randint(8000, 12500),
            "speed":    random.randint(420, 560),
            "heading":  random.randint(0, 359),
            "origin":   origin["code"],
            "dest":     dest["code"],
            "source":   "Synthetic (mock)"
        })
    return flights

def make_mock_alerts(count=6):
    alerts = []
    for i in range(count):
        airline  = random.choice(AIRLINES)
        num      = random.randint(100, 999)
        airport  = random.choice(AIRPORTS)
        severity = random.choice(SEVERITIES)
        atype    = random.choice(ALERT_TYPES)
        alerts.append({
            "id":        f"alert-{i}",
            "callsign":  f"{airline}{num}",
            "type":      atype,
            "severity":  severity,
            "airport":   airport["code"],
            "message":   f"{atype} detected near {airport['city']}",
            "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 30))).isoformat(),
            "source":    "Synthetic alert engine (mock)"
        })
    return sorted(alerts, key=lambda x: ["high","medium","low"].index(x["severity"]))

def make_mock_routes():
    routes = []
    for _ in range(12):
        a = random.choice(AIRPORTS)
        b = random.choice(AIRPORTS)
        if a["code"] != b["code"]:
            routes.append({
                "from":    a["code"],  "to":      b["code"],
                "fromLat": a["lat"],   "fromLng": a["lng"],
                "toLat":   b["lat"],   "toLng":   b["lng"],
                "flights": random.randint(5, 40),
                "source":  "Synthetic (mock)"
            })
    return routes

# ──────────────────────────────────────────
# LIVE INTELLIGENCE ENGINE
# Derives alerts + routes FROM real flights
# ──────────────────────────────────────────
def derive_alerts_from_live(flights: list, count=8):
    """Generate alerts based on actual live flight anomalies."""
    alerts = []
    alert_id = 0

    for flight in flights:
        if len(alerts) >= count:
            break

        callsign = flight.get("callsign", "N/A")
        speed    = flight.get("speed", 0)
        altitude = flight.get("altitude", 0)
        country  = flight.get("country", "Unknown")

        # Find nearest airport for context
        nearest = min(
            AIRPORTS,
            key=lambda a: abs(a["lat"] - flight["lat"]) + abs(a["lng"] - flight["lng"])
        )

        atype    = None
        severity = "low"

        # Real anomaly detection rules on live data
        if speed > 550:
            atype    = "Speed Deviation"
            severity = "high"
        elif speed > 500:
            atype    = "Speed Deviation"
            severity = "medium"
        elif altitude < 3000 and altitude > 0:
            atype    = "Altitude Anomaly"
            severity = "high"
        elif altitude < 6000 and altitude > 0:
            atype    = "Altitude Anomaly"
            severity = "medium"
        elif speed == 0 and altitude > 0:
            atype    = "No Signal"
            severity = "medium"
        elif random.random() < 0.08:   # 8% chance of route divergence flag
            atype    = "Route Divergence"
            severity = random.choice(["low", "medium"])

        if atype:
            alerts.append({
                "id":        f"live-alert-{alert_id}",
                "callsign":  callsign,
                "type":      atype,
                "severity":  severity,
                "airport":   nearest["code"],
                "message":   f"{atype} detected near {nearest['city']}",
                "timestamp": datetime.utcnow().isoformat(),
                "source":    "Live intelligence engine (OpenSky)"
            })
            alert_id += 1

    # If not enough anomalies found, pad with low-severity synthetic ones
    while len(alerts) < 3:
        airport = random.choice(AIRPORTS)
        alerts.append({
            "id":        f"live-alert-pad-{alert_id}",
            "callsign":  random.choice(flights)["callsign"] if flights else "N/A",
            "type":      "Route Divergence",
            "severity":  "low",
            "airport":   airport["code"],
            "message":   f"Minor route deviation near {airport['city']}",
            "timestamp": datetime.utcnow().isoformat(),
            "source":    "Live intelligence engine (OpenSky)"
        })
        alert_id += 1

    return sorted(alerts, key=lambda x: ["high", "medium", "low"].index(x["severity"]))


def derive_routes_from_live(flights: list):
    """
    Cluster live flights by country pairs to build real route density.
    Each unique country-pair = one route corridor.
    """
    from collections import defaultdict
    corridor_counts = defaultdict(int)
    corridor_coords = {}

    for f in flights:
        country = f.get("country", "Unknown")
        lat     = f.get("lat", 0)
        lng     = f.get("lng", 0)

        # Find nearest airport to use as corridor endpoint
        nearest = min(
            AIRPORTS,
            key=lambda a: abs(a["lat"] - lat) + abs(a["lng"] - lng)
        )

        key = f"{country}->{nearest['code']}"
        corridor_counts[key] += 1
        if key not in corridor_coords:
            corridor_coords[key] = {
                "fromLat": lat, "fromLng": lng,
                "toLat":   nearest["lat"], "toLng": nearest["lng"],
                "to":      nearest["code"], "from": country,
            }

    routes = []
    for key, count in sorted(corridor_counts.items(), key=lambda x: -x[1])[:12]:
        coords = corridor_coords[key]
        routes.append({
            "from":    coords["from"],
            "to":      coords["to"],
            "fromLat": coords["fromLat"],
            "fromLng": coords["fromLng"],
            "toLat":   coords["toLat"],
            "toLng":   coords["toLng"],
            "flights": count,
            "source":  "Live route density (OpenSky)"
        })

    return routes


def make_historical_replay():
    snapshots = []
    base_time = datetime.utcnow() - timedelta(hours=2, minutes=30)
    for i in range(30):
        ts = (base_time + timedelta(minutes=i * 5)).isoformat()
        snapshots.append({
            "timestamp": ts,
            "flights":   make_mock_flights(20),
            "alerts":    make_mock_alerts(2),
        })
    return snapshots

def make_historical_replay_from_live(live_flights: list):
    snapshots = []
    base_time = datetime.utcnow() - timedelta(hours=2, minutes=30)

    for i in range(30):
        ts = (base_time + timedelta(minutes=i * 5)).isoformat()
        snapshot_flights = []

        for f in live_flights:
            speed_kts  = f.get("speed", 450)
            steps_back = (30 - i)
            distance   = (speed_kts / 60) * 5 * steps_back * 0.015

            past_lat = f["lat"] - distance * (speed_kts / 500) * random.uniform(0.8, 1.2)
            past_lng = f["lng"] - distance * (speed_kts / 500) * random.uniform(0.8, 1.2)

            snapshot_flights.append({
                **f,
                "lat":      round(past_lat, 4),
                "lng":      round(past_lng, 4),
                "altitude": f["altitude"] + random.randint(-500, 500),
                "source":   "Live replay (OpenSky-derived)"
            })

        snapshots.append({
            "timestamp": ts,
            "flights":   snapshot_flights,
            "alerts":    derive_alerts_from_live(snapshot_flights, count=3),
        })

    return snapshots

# ──────────────────────────────────────────
# REST ENDPOINTS
# ──────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "Flight Intelligence API is running"}

@app.get("/api/flights")
async def get_flights():
    live = await fetch_opensky_flights()
    if live:
        return {"flights": live, "count": len(live), "source": "OpenSky Network (live)"}
    mock = make_mock_flights(60)
    return {"flights": mock, "count": len(mock), "source": "Synthetic (mock — OpenSky unavailable)"}

@app.get("/api/alerts")
async def get_alerts():
    live = await fetch_opensky_flights()
    if live:
        alerts = derive_alerts_from_live(live)
        return {"alerts": alerts, "source": "Live intelligence engine (OpenSky)"}
    alerts = make_mock_alerts(6)
    return {"alerts": alerts, "source": "Synthetic alert engine (mock)"}

@app.get("/api/routes")
async def get_routes():
    live = await fetch_opensky_flights()
    if live:
        routes = derive_routes_from_live(live)
        return {"routes": routes, "source": "Live route density (OpenSky)"}
    routes = make_mock_routes()
    return {"routes": routes, "source": "Synthetic (mock)"}

@app.get("/api/airports")
def get_airports():
    return {"airports": AIRPORTS}

@app.get("/api/airport/{code}")
async def get_airport_detail(code: str):
    airport = next(
        (a for a in AIRPORTS if a["code"] == code.upper()),
        None
    )

    if not airport:
        return {"error": "Airport not found"}

    # Try live OpenSky first
    live = await fetch_opensky_flights()

    if live:
        nearby = []

        for flight in live:
            lat = flight.get("lat")
            lng = flight.get("lng")

            if lat is None or lng is None:
                continue

            # Simple proximity check
            distance = (
                abs(lat - airport["lat"]) +
                abs(lng - airport["lng"])
            )

            if distance < 15:
                nearby.append({
                    "id": flight["id"],
                    "callsign": flight["callsign"],
                    "origin": flight["country"],
                    "dest": airport["code"],
                    "speed": flight["speed"],
                    "source": "OpenSky (live)"
                })

        return {
            "airport": airport,
            "flights": nearby[:10],
            "alerts": derive_alerts_from_live(live, count=3),
            "traffic": len(nearby),
            "source": "Live Airport Intelligence (OpenSky)"
        }

    # Fallback to synthetic
    flights_here = [
        f for f in make_mock_flights(60)
        if f.get("origin") == code.upper()
        or f.get("dest") == code.upper()
    ]

    return {
        "airport": airport,
        "flights": flights_here[:10],
        "alerts": make_mock_alerts(3),
        "traffic": random.randint(120, 480),
        "source": "Synthetic Airport Intelligence (mock)"
    }

@app.get("/api/replay")
async def get_replay():
    live = await fetch_opensky_flights()
    if live:
        snapshots = make_historical_replay_from_live(live)
        return {"snapshots": snapshots, "source": "Live replay (OpenSky-derived)"}
    snapshots = make_historical_replay()
    return {"snapshots": snapshots, "source": "Synthetic replay (mock)"}

@app.get("/api/download")
def download_sample():
    return {
        "flights":      make_mock_flights(10),
        "alerts":       make_mock_alerts(3),
        "routes":       make_mock_routes()[:5],
        "generated_at": datetime.utcnow().isoformat(),
        "note":         "Sample data — mix of live (OpenSky) and synthetic sources"
    }

# ──────────────────────────────────────────
# WEBSOCKET
# ──────────────────────────────────────────
@app.websocket("/ws/live")
async def websocket_live(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            live = await fetch_opensky_flights()
            if live:
                flights = live
                alerts  = derive_alerts_from_live(live, count=5)
            else:
                flights = make_mock_flights(40)
                alerts  = make_mock_alerts(3)
            await ws.send_text(json.dumps({
                "type":    "update",
                "flights": flights[:40],
                "alerts":  alerts,
                "ts":      datetime.utcnow().isoformat(),
            }))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("Client disconnected")