from collections import Counter
from datetime import datetime, timedelta, timezone
import asyncio
import json
import math
import time

from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import httpx

from mock_data import (
    DATA_DICTIONARY,
    SAMPLE_ROWS,
    export_csv,
    export_json,
    make_airport_detail,
    make_historical_replay,
    make_mock_alerts,
    make_mock_flights,
    make_route_density,
)
from mock_data.seeds import AIRPORTS

app = FastAPI(title="Flight Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LIVE_SOURCE = "Live OpenSky Network"
MOCK_FLIGHT_SOURCE = "Mock fallback - OpenSky unavailable or rate-limited"
DEMO_RULE_SOURCE = "Demo anomaly rules over live OpenSky positions - mock thresholds"
MOCK_ALERT_SOURCE = "Mock fallback alert engine - synthetic thresholds/anomaly labels"
ROUTE_LIVE_SOURCE = "Live OpenSky-derived route density - inferred corridors, not filed routes"
ROUTE_MOCK_SOURCE = "Mock fallback route density - synthetic"
REPLAY_LIVE_SOURCE = "Live OpenSky replay simulation - current snapshot projected backward, not historical archive"
REPLAY_MOCK_SOURCE = "Mock fallback historical replay - synthetic"

_opensky_cache = {"time": 0.0, "flights": []}
_CACHE_SECONDS = 25


async def fetch_opensky_flights():
    """
    Fetch live aircraft states from OpenSky Network.
    OpenSky is the first practical live source here because ADS-B Exchange
    generally requires an API key/commercial access.
    """
    now = time.time()
    if now - _opensky_cache["time"] < _CACHE_SECONDS:
        return _opensky_cache["flights"]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://opensky-network.org/api/states/all")
            if resp.status_code == 429:
                print("OpenSky fetch rate-limited")
                return []
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        print(f"OpenSky fetch failed: {exc}")
        return []

    flights = []
    for state in (data or {}).get("states") or []:
        if state[5] is None or state[6] is None:
            continue

        flights.append(
            {
                "id": state[0] or "unknown",
                "callsign": (state[1] or "N/A").strip(),
                "country": state[2] or "Unknown",
                "lng": state[5],
                "lat": state[6],
                "altitude": round(state[7] or 0),
                "speed": round((state[9] or 0) * 1.94),
                "heading": round(state[10] or 0),
                "origin": None,
                "dest": None,
                "source": LIVE_SOURCE,
            }
        )

        if len(flights) >= 80:
            break

    _opensky_cache["time"] = now
    _opensky_cache["flights"] = flights
    return flights


def source_payload(mode, source, detail=None):
    return {
        "mode": mode,
        "source": source,
        "detail": detail or source,
    }


async def get_best_flights():
    live = await fetch_opensky_flights()
    if live:
        return live, source_payload("live", LIVE_SOURCE)

    mock = make_mock_flights(60)
    return mock, source_payload("mock", MOCK_FLIGHT_SOURCE)


def distance_km(lat1, lng1, lat2, lng2):
    radius = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(a))


def nearest_airports(lat, lng, limit=2):
    return sorted(
        AIRPORTS,
        key=lambda airport: distance_km(lat, lng, airport["lat"], airport["lng"]),
    )[:limit]


def make_demo_alerts_from_live(flights, limit=8):
    """Demo-only anomaly labels based on OpenSky positions."""
    alerts = []
    now = datetime.now(timezone.utc).isoformat()

    for flight in flights:
        alert_type = None
        severity = "low"
        message = None

        if flight["altitude"] >= 12000:
            alert_type = "Demo Altitude Anomaly"
            severity = "high"
            message = "Mock threshold: altitude at or above 12,000 m"
        elif flight["speed"] >= 575:
            alert_type = "Demo Speed Deviation"
            severity = "medium"
            message = "Mock threshold: speed at or above 575 kts"
        elif flight["altitude"] > 1000 and flight["speed"] <= 90:
            alert_type = "Demo Low-Speed Airborne"
            severity = "medium"
            message = "Mock threshold: airborne aircraft moving at or below 90 kts"

        if not alert_type:
            continue

        airport = nearest_airports(flight["lat"], flight["lng"], 1)[0]
        alerts.append(
            {
                "id": f"demo-live-{flight['id']}",
                "callsign": flight["callsign"],
                "type": alert_type,
                "severity": severity,
                "airport": airport["code"],
                "message": message,
                "timestamp": now,
                "source": DEMO_RULE_SOURCE,
                "ANALYTICS_LABEL": "Demo anomaly label; not an operational alert",
            }
        )

    if not alerts and flights:
        sample = flights[0]
        airport = nearest_airports(sample["lat"], sample["lng"], 1)[0]
        alerts.append(
            {
                "id": f"demo-live-watch-{sample['id']}",
                "callsign": sample["callsign"],
                "type": "Demo Watchlist Sample",
                "severity": "low",
                "airport": airport["code"],
                "message": "Mock threshold sample generated to demonstrate alert cards",
                "timestamp": now,
                "source": DEMO_RULE_SOURCE,
                "ANALYTICS_LABEL": "Demo anomaly label; not an operational alert",
            }
        )

    return sorted(alerts[:limit], key=lambda item: ["high", "medium", "low"].index(item["severity"]))


def make_routes_from_live(flights, limit=12):
    """
    OpenSky public states do not include filed origin/destination.
    This derives density from nearest-airport corridors and labels it as inferred.
    """
    airport_lookup = {airport["code"]: airport for airport in AIRPORTS}
    counts = Counter()

    for flight in flights:
        nearest = nearest_airports(flight["lat"], flight["lng"], 2)
        if len(nearest) < 2:
            continue
        counts[(nearest[0]["code"], nearest[1]["code"])] += 1

    routes = []
    for (origin, dest), count in counts.most_common(limit):
        start = airport_lookup[origin]
        end = airport_lookup[dest]
        routes.append(
            {
                "from": origin,
                "to": dest,
                "fromLat": start["lat"],
                "fromLng": start["lng"],
                "toLat": end["lat"],
                "toLng": end["lng"],
                "flights": count,
                "source": ROUTE_LIVE_SOURCE,
                "ANALYTICS_LABEL": "Inferred from nearest airport corridor; not filed route data",
            }
        )

    return routes


def make_replay_from_live(flights, snapshots=12):
    """
    OpenSky's unauthenticated public state endpoint is live, not historical.
    The replay panel receives projected snapshots from the current live state.
    """
    base_time = datetime.now(timezone.utc) - timedelta(minutes=(snapshots - 1) * 5)
    sample = flights[:25]
    result = []

    for index in range(snapshots):
        minutes_back = (snapshots - 1 - index) * 5
        replay_flights = []

        for flight in sample:
            heading = math.radians(flight.get("heading") or 0)
            distance_nm = (flight.get("speed") or 0) * (minutes_back / 60)
            distance_deg = distance_nm / 60
            replay_flights.append(
                {
                    **flight,
                    "id": f"replay-{index}-{flight['id']}",
                    "lat": round(max(-85, min(85, flight["lat"] - math.cos(heading) * distance_deg)), 4),
                    "lng": round(max(-180, min(180, flight["lng"] - math.sin(heading) * distance_deg)), 4),
                    "source": REPLAY_LIVE_SOURCE,
                }
            )

        result.append(
            {
                "timestamp": (base_time + timedelta(minutes=index * 5)).isoformat(),
                "flights": replay_flights,
                "alerts": make_demo_alerts_from_live(replay_flights, 3),
                "source": REPLAY_LIVE_SOURCE,
            }
        )

    return result


@app.get("/")
def root():
    return {"status": "Flight Intelligence API is running"}


@app.get("/api/flights")
async def get_flights():
    flights, status = await get_best_flights()
    return {"flights": flights, "count": len(flights), **status}


@app.get("/api/alerts")
async def get_alerts():
    live = await fetch_opensky_flights()
    if live:
        return {
            "alerts": make_demo_alerts_from_live(live),
            **source_payload(
                "live",
                DEMO_RULE_SOURCE,
                "OpenSky positions with demo-only anomaly thresholds",
            ),
        }

    return {
        "alerts": make_mock_alerts(6),
        **source_payload("mock", MOCK_ALERT_SOURCE),
    }


@app.get("/api/routes")
async def get_routes():
    live = await fetch_opensky_flights()
    if live:
        routes = make_routes_from_live(live)
        if routes:
            return {"routes": routes, **source_payload("live", ROUTE_LIVE_SOURCE)}

    return {
        "routes": make_route_density(),
        **source_payload("mock", ROUTE_MOCK_SOURCE),
    }


@app.get("/api/airports")
def get_airports():
    return {"airports": AIRPORTS, **source_payload("reference", "Static airport reference data")}


@app.get("/api/airport/{code}")
async def get_airport_detail(code: str):
    airport = next((item for item in AIRPORTS if item["code"] == code.upper()), None)
    if airport:
        live = await fetch_opensky_flights()
        nearby = [
            flight
            for flight in live
            if distance_km(airport["lat"], airport["lng"], flight["lat"], flight["lng"]) <= 500
        ]
        if nearby:
            return {
                "airport": airport,
                "flights": nearby[:10],
                "alerts": make_demo_alerts_from_live(nearby, 3),
                "traffic": len(nearby),
                **source_payload("live", "Live OpenSky airport drill-down - flights within 500 km"),
            }

    detail = make_airport_detail(code)
    if not detail:
        return {"error": f"Airport '{code}' not found"}

    detail["mode"] = "mock"
    detail["source"] = "Mock fallback airport drill-down - synthetic"
    return detail


@app.get("/api/replay")
async def get_replay():
    live = await fetch_opensky_flights()
    if live:
        return {
            "snapshots": make_replay_from_live(live),
            **source_payload("live", REPLAY_LIVE_SOURCE),
        }

    return {
        "snapshots": make_historical_replay(),
        **source_payload("mock", REPLAY_MOCK_SOURCE),
    }


@app.get("/api/download/json")
def download_json():
    payload = {
        "flights": make_mock_flights(10),
        "alerts": make_mock_alerts(3),
        "routes": make_route_density(5),
    }
    content = export_json(payload)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=flight-intelligence-sample.json"},
    )


@app.get("/api/download/csv/flights")
def download_csv_flights():
    rows = make_mock_flights(20)
    content = export_csv(rows)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=synthetic-flights.csv"},
    )


@app.get("/api/download/csv/alerts")
def download_csv_alerts():
    rows = make_mock_alerts(10)
    content = export_csv(rows)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=synthetic-alerts.csv"},
    )


@app.get("/api/schema")
def get_schema():
    return DATA_DICTIONARY


@app.get("/api/samples")
def get_sample_rows():
    return {
        "samples": SAMPLE_ROWS,
        "source": "Synthetic sample rows from mock_data package",
        "SYNTHETIC_LABEL": "SYNTHETIC - not a real operational record",
    }


@app.get("/api/edge-cases/flights")
def get_edge_case_flights():
    return make_mock_flights(0, edge_cases=True)


@app.get("/api/edge-cases/alerts")
def get_edge_case_alerts():
    return make_mock_alerts(0, edge_cases=True)


@app.get("/api/edge-cases/routes")
def get_edge_case_routes():
    return make_route_density(0, edge_cases=True)


@app.websocket("/ws/live")
async def websocket_live(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            flights, status = await get_best_flights()
            await ws.send_text(
                json.dumps(
                    {
                        "type": "update",
                        "flights": flights[:40],
                        "alerts": (
                            make_demo_alerts_from_live(flights[:40], 3)
                            if status["mode"] == "live"
                            else make_mock_alerts(3)
                        ),
                        **status,
                    }
                )
            )
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        print("Client disconnected")
