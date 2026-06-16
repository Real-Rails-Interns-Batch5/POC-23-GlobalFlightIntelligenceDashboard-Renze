"""
Data dictionary for the Global Flight Intelligence Dashboard mock-data package.

Every entity produced by backend.mock_data is synthetic. Real-world airport
codes and names are used only as reference labels so the internship demo feels
realistic; no operational metric in this package is sourced from a live system.
"""

SYNTHETIC_LABEL_VALUE = "SYNTHETIC - not a real operational record"

DATA_DICTIONARY = {
    "Flight": {
        "description": "Synthetic aircraft position snapshot interpolated between seed airports.",
        "fields": {
            "id": {"type": "string", "example": "mock-42", "description": "Synthetic flight identifier."},
            "callsign": {"type": "string", "example": "AI302", "description": "Synthetic airline code and flight number."},
            "country": {"type": "string", "example": "India", "description": "Synthetic country label from origin seed airport."},
            "lat": {"type": "float|null", "range": [-90, 90], "description": "Latitude. Edge cases may be null."},
            "lng": {"type": "float|null", "range": [-180, 180], "description": "Longitude. Edge cases may be null."},
            "altitude": {"type": "integer", "unit": "metres", "description": "Synthetic barometric altitude."},
            "speed": {"type": "integer", "unit": "knots", "description": "Synthetic ground speed."},
            "heading": {"type": "integer", "unit": "degrees", "description": "Synthetic true heading."},
            "origin": {"type": "string|null", "example": "DEL", "description": "Synthetic origin airport code."},
            "dest": {"type": "string|null", "example": "LHR", "description": "Synthetic destination airport code."},
            "source": {"type": "string", "value": "Synthetic (mock)", "description": "Data provenance label."},
            "SYNTHETIC_LABEL": {"type": "string", "value": SYNTHETIC_LABEL_VALUE, "description": "Required synthetic-data disclaimer."},
            "edge_case": {"type": "string", "optional": True, "description": "Present only on boundary/error rows."},
        },
        "sample_rows": "See samples.py -> SAMPLE_ROWS['Flight']",
        "edge_cases": "See edge_cases.py -> FLIGHT_EDGE_CASES",
    },
    "Alert": {
        "description": "Synthetic anomaly card used to demonstrate alert workflows.",
        "fields": {
            "id": {"type": "string", "example": "alert-0", "description": "Synthetic alert identifier."},
            "callsign": {"type": "string", "example": "EK501", "description": "Synthetic flight callsign."},
            "type": {"type": "string", "enum": ["Altitude Anomaly", "Speed Deviation", "Route Divergence", "Squawk 7700", "No Signal"], "description": "Synthetic alert category."},
            "severity": {"type": "string", "enum": ["low", "medium", "high"], "description": "Synthetic severity label."},
            "airport": {"type": "string|null", "example": "DXB", "description": "Nearest seed airport code."},
            "message": {"type": "string", "description": "Synthetic alert message."},
            "timestamp": {"type": "ISO8601", "description": "Generation timestamp."},
            "source": {"type": "string", "value": "Synthetic alert engine (mock)", "description": "Data provenance label."},
            "SYNTHETIC_LABEL": {"type": "string", "value": SYNTHETIC_LABEL_VALUE, "description": "Required synthetic-data disclaimer."},
            "edge_case": {"type": "string", "optional": True, "description": "Present only on boundary/error rows."},
        },
        "sample_rows": "See samples.py -> SAMPLE_ROWS['Alert']",
        "edge_cases": "See edge_cases.py -> ALERT_EDGE_CASES",
    },
    "Route": {
        "description": "Synthetic route-density row for visualising origin-destination volume.",
        "fields": {
            "from": {"type": "string", "example": "DEL", "description": "Synthetic origin airport code."},
            "to": {"type": "string", "example": "NRT", "description": "Synthetic destination airport code."},
            "fromLat": {"type": "float", "description": "Origin airport latitude."},
            "fromLng": {"type": "float", "description": "Origin airport longitude."},
            "toLat": {"type": "float", "description": "Destination airport latitude."},
            "toLng": {"type": "float", "description": "Destination airport longitude."},
            "flights": {"type": "integer", "description": "Synthetic count of active flights on the route."},
            "source": {"type": "string", "value": "Synthetic (mock)", "description": "Data provenance label."},
            "SYNTHETIC_LABEL": {"type": "string", "value": SYNTHETIC_LABEL_VALUE, "description": "Required synthetic-data disclaimer."},
            "edge_case": {"type": "string", "optional": True, "description": "Present only on boundary/error rows."},
        },
        "sample_rows": "See samples.py -> SAMPLE_ROWS['Route']",
        "edge_cases": "See edge_cases.py -> ROUTE_EDGE_CASES",
    },
    "Airport": {
        "description": "Synthetic seed/reference airport row. Codes and names are realistic labels only.",
        "fields": {
            "code": {"type": "string", "example": "DEL", "description": "IATA airport code used as a reference label."},
            "name": {"type": "string", "example": "Indira Gandhi Intl", "description": "Airport display name."},
            "lat": {"type": "float", "description": "Airport latitude."},
            "lng": {"type": "float", "description": "Airport longitude."},
            "city": {"type": "string", "example": "Delhi", "description": "City display name."},
            "country": {"type": "string", "example": "India", "description": "Country display name."},
            "source": {"type": "string", "value": "Synthetic seed reference", "description": "Data provenance label."},
            "SYNTHETIC_LABEL": {"type": "string", "value": SYNTHETIC_LABEL_VALUE, "description": "Required synthetic-data disclaimer."},
        },
        "sample_rows": "See samples.py -> SAMPLE_ROWS['Airport']",
    },
    "AirportDetail": {
        "description": "Synthetic drill-down payload for one airport, including synthetic nearby flights and alerts.",
        "fields": {
            "airport": {"type": "Airport", "description": "Seed airport reference."},
            "flights": {"type": "array", "items": "Flight", "description": "Synthetic flights related to the airport."},
            "alerts": {"type": "array", "items": "Alert", "description": "Synthetic alerts related to the airport."},
            "traffic": {"type": "integer", "description": "Synthetic daily movement count."},
            "source": {"type": "string", "description": "Data provenance label."},
            "SYNTHETIC_LABEL": {"type": "string", "value": SYNTHETIC_LABEL_VALUE, "description": "Required synthetic-data disclaimer."},
        },
        "sample_rows": "See samples.py -> SAMPLE_ROWS['AirportDetail']",
    },
    "ReplaySnapshot": {
        "description": "Synthetic point-in-time replay snapshot.",
        "fields": {
            "timestamp": {"type": "ISO8601", "description": "Synthetic replay timestamp."},
            "flights": {"type": "array", "items": "Flight", "description": "Synthetic flights at this replay step."},
            "alerts": {"type": "array", "items": "Alert", "description": "Synthetic alerts at this replay step."},
            "source": {"type": "string", "description": "Data provenance label."},
            "SYNTHETIC_LABEL": {"type": "string", "value": SYNTHETIC_LABEL_VALUE, "description": "Required synthetic-data disclaimer."},
        },
        "sample_rows": "See samples.py -> SAMPLE_ROWS['ReplaySnapshot']",
    },
}
