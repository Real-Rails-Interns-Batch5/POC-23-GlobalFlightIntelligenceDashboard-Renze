"""
generators.py — Synthetic data generators for Global Flight Intelligence Dashboard
====================================================================================
All functions return SYNTHETIC data.
Every record includes a 'SYNTHETIC_LABEL' field so downstream consumers
(UI, tests, exporters) can always identify mock data unambiguously.

Usage:
    from mock_data import make_mock_flights, make_mock_alerts, ...
"""

import random
from datetime import datetime, timedelta, timezone

from .seeds import AIRPORTS, AIRLINES, ALERT_TYPES, SEVERITIES, AIRPORT_BY_CODE
from .edge_cases import FLIGHT_EDGE_CASES, ALERT_EDGE_CASES, ROUTE_EDGE_CASES

_SYNTHETIC_LABEL = "SYNTHETIC - not a real operational record"


# ─────────────────────────────────────────────────────────────
# Flights
# ─────────────────────────────────────────────────────────────

def make_mock_flights(count: int = 60, edge_cases: bool = False) -> list[dict]:
    """
    Generate `count` synthetic flight position records.

    Fields per record (see schema.py → Flight for full definitions):
        id, callsign, country, lat, lng, altitude, speed, heading,
        origin, dest, source, SYNTHETIC_LABEL

    Args:
        count:       Number of normal records to generate (default 60).
        edge_cases:  If True, appends FLIGHT_EDGE_CASES records (5 extra).
    """
    flights = []
    for i in range(count):
        airline = random.choice(AIRLINES)
        num     = random.randint(100, 999)
        origin  = random.choice(AIRPORTS)
        dest = random.choice(
    [a for a in AIRPORTS if a["code"] != origin["code"]]
)
        frac    = random.random()
        lat     = origin["lat"] + frac * (dest["lat"] - origin["lat"]) + random.uniform(-2, 2)
        lng     = origin["lng"] + frac * (dest["lng"] - origin["lng"]) + random.uniform(-2, 2)

        flights.append({
            "id":               f"mock-{i}",
            "callsign":         f"{airline['iata']}{num}",
            "country":          origin["country"],
            "lat":              round(lat, 4),
            "lng":              round(lng, 4),
            "altitude":         random.randint(8000, 12500),
            "speed":            random.randint(420, 560),
            "heading":          random.randint(0, 359),
            "origin":           origin["code"],
            "dest":             dest["code"],
            "source":           "Synthetic (mock)",
            "SYNTHETIC_LABEL":  _SYNTHETIC_LABEL,
        })

    if edge_cases:
        flights.extend(FLIGHT_EDGE_CASES)

    return flights


# ─────────────────────────────────────────────────────────────
# Alerts
# ─────────────────────────────────────────────────────────────

def make_mock_alerts(count: int = 6, edge_cases: bool = False) -> list[dict]:
    """
    Generate `count` synthetic alert records, sorted high → low severity.

    Fields per record (see schema.py → Alert for full definitions):
        id, callsign, type, severity, airport, message,
        timestamp, source, SYNTHETIC_LABEL

    Args:
        count:       Number of normal records (default 6).
        edge_cases:  If True, appends ALERT_EDGE_CASES records (4 extra).
    """
    alerts = []
    for i in range(count):
        airline  = random.choice(AIRLINES)
        num      = random.randint(100, 999)
        airport  = random.choice(AIRPORTS)
        severity = random.choice(SEVERITIES)
        atype    = random.choice(ALERT_TYPES)

        alerts.append({
            "id":              f"alert-{i}",
            "callsign":        f"{airline['iata']}{num}",
            "type":            atype,
            "severity":        severity,
            "airport":         airport["code"],
            "message":         f"{atype} detected near {airport['city']}",
            "timestamp":       (
                datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 30))
            ).isoformat(),
            "source":          "Synthetic alert engine (mock)",
            "SYNTHETIC_LABEL": _SYNTHETIC_LABEL,
        })

    if edge_cases:
        alerts.extend(ALERT_EDGE_CASES)

    # Sort high → medium → low
    return sorted(alerts, key=lambda x: ["high", "medium", "low"].index(x["severity"]))


# ─────────────────────────────────────────────────────────────
# Route Density
# ─────────────────────────────────────────────────────────────

def make_route_density(count: int = 12, edge_cases: bool = False) -> list[dict]:
    """
    Generate `count` synthetic origin–destination route records.

    Fields per record (see schema.py → Route for full definitions):
        from, to, fromLat, fromLng, toLat, toLng, flights, source

    Args:
        count:       Number of normal route records (default 12).
        edge_cases:  If True, appends ROUTE_EDGE_CASES records (3 extra).
    """
    routes = []
    attempts = 0
    while len(routes) < count and attempts < count * 3:
        attempts += 1
        a = random.choice(AIRPORTS)
        b = random.choice(AIRPORTS)
        if a["code"] == b["code"]:
            continue
        routes.append({
            "from":    a["code"],
            "to":      b["code"],
            "fromLat": a["lat"],
            "fromLng": a["lng"],
            "toLat":   b["lat"],
            "toLng":   b["lng"],
            "flights": random.randint(5, 40),
            "source":  "Synthetic (mock)",
            "SYNTHETIC_LABEL": _SYNTHETIC_LABEL,
        })

    if edge_cases:
        routes.extend(ROUTE_EDGE_CASES)

    return routes


# ─────────────────────────────────────────────────────────────
# Historical Replay
# ─────────────────────────────────────────────────────────────

def make_historical_replay(snapshots: int = 30, edge_cases: bool = False) -> list[dict]:
    """
    Generate a list of ReplaySnapshot records covering 2.5 hours of activity
    at 5-minute intervals.

    Fields per snapshot (see schema.py → ReplaySnapshot):
        timestamp, flights (list), alerts (list)

    Args:
        snapshots:   Number of time-step snapshots (default 30 = 2.5 hrs at 5 min).
        edge_cases:  If True, injects edge-case flights/alerts into the last snapshot.
    """
    result     = []
    base_time  = datetime.now(timezone.utc) - timedelta(hours=2, minutes=30)

    for i in range(snapshots):
        ts  = (base_time + timedelta(minutes=i * 5)).isoformat()
        ec  = edge_cases and (i == snapshots - 1)   # inject only into last snapshot
        result.append({
            "timestamp": ts,
            "flights":   make_mock_flights(20, edge_cases=ec),
            "alerts":    make_mock_alerts(2,  edge_cases=ec),
            "source":    "Synthetic - Flight Intelligence Replay Layer",
            "SYNTHETIC_LABEL": _SYNTHETIC_LABEL,
        })

    return result


# ─────────────────────────────────────────────────────────────
# Airport Detail
# ─────────────────────────────────────────────────────────────

def make_airport_detail(code: str, edge_cases: bool = False) -> dict | None:
    """
    Return detail record for a single airport including nearby flights & alerts.

    Args:
        code:        IATA airport code (e.g. 'DEL').
        edge_cases:  If True, includes edge-case flights and alerts.

    Returns:
        Dict with keys: airport, flights, alerts, traffic, source
        None if the code is not found in seed data.
    """
    airport = AIRPORT_BY_CODE.get(code.upper())
    if not airport:
        return None

    all_flights  = make_mock_flights(60, edge_cases=edge_cases)
    nearby       = [
        f for f in all_flights
        if f.get("origin") == code.upper() or f.get("dest") == code.upper()
    ]

    return {
        "airport":         airport,
        "flights":         nearby[:10],
        "alerts":          make_mock_alerts(3, edge_cases=edge_cases),
        "traffic":         random.randint(120, 480),
        "source":          "Synthetic - Flight Intelligence Analytics Layer",
        "SYNTHETIC_LABEL": _SYNTHETIC_LABEL,
    }
