"""
Realistic sample rows for the Global Flight Intelligence Dashboard.

These rows are examples for documentation, tests, and reviewers. They are
synthetic and should not be mixed with live OpenSky records.
"""

SYNTHETIC_LABEL = "SYNTHETIC - not a real operational record"

SAMPLE_ROWS = {
    "Flight": [
        {
            "id": "mock-sample-001",
            "callsign": "AI302",
            "country": "India",
            "lat": 33.4127,
            "lng": 56.3842,
            "altitude": 10950,
            "speed": 487,
            "heading": 286,
            "origin": "DEL",
            "dest": "LHR",
            "source": "Synthetic (mock)",
            "SYNTHETIC_LABEL": SYNTHETIC_LABEL,
        },
        {
            "id": "mock-sample-002",
            "callsign": "EK511",
            "country": "UAE",
            "lat": 24.9912,
            "lng": 61.4724,
            "altitude": 11620,
            "speed": 512,
            "heading": 94,
            "origin": "DXB",
            "dest": "SIN",
            "source": "Synthetic (mock)",
            "SYNTHETIC_LABEL": SYNTHETIC_LABEL,
        },
    ],
    "Alert": [
        {
            "id": "alert-sample-001",
            "callsign": "SQ781",
            "type": "Speed Deviation",
            "severity": "medium",
            "airport": "SIN",
            "message": "Speed Deviation detected near Singapore",
            "timestamp": "2026-06-16T12:30:00+00:00",
            "source": "Synthetic alert engine (mock)",
            "SYNTHETIC_LABEL": SYNTHETIC_LABEL,
        }
    ],
    "Route": [
        {
            "from": "DEL",
            "to": "DXB",
            "fromLat": 28.56,
            "fromLng": 77.10,
            "toLat": 25.25,
            "toLng": 55.36,
            "flights": 28,
            "source": "Synthetic (mock)",
            "SYNTHETIC_LABEL": SYNTHETIC_LABEL,
        }
    ],
    "Airport": [
        {
            "code": "DEL",
            "name": "Indira Gandhi Intl",
            "lat": 28.56,
            "lng": 77.10,
            "city": "Delhi",
            "country": "India",
            "source": "Synthetic seed reference",
            "SYNTHETIC_LABEL": SYNTHETIC_LABEL,
        }
    ],
    "AirportDetail": [
        {
            "airport": {
                "code": "DEL",
                "name": "Indira Gandhi Intl",
                "lat": 28.56,
                "lng": 77.10,
                "city": "Delhi",
                "country": "India",
                "source": "Synthetic seed reference",
                "SYNTHETIC_LABEL": SYNTHETIC_LABEL,
            },
            "flights": [],
            "alerts": [],
            "traffic": 246,
            "source": "Synthetic - Flight Intelligence Analytics Layer",
            "SYNTHETIC_LABEL": SYNTHETIC_LABEL,
        }
    ],
    "ReplaySnapshot": [
        {
            "timestamp": "2026-06-16T12:30:00+00:00",
            "flights": [],
            "alerts": [],
            "source": "Synthetic - Flight Intelligence Replay Layer",
            "SYNTHETIC_LABEL": SYNTHETIC_LABEL,
        }
    ],
}
