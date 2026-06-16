"""
Static reference data used by the mock-data generators.

Airport and airline names are realistic labels for the demo. They do not carry
live operational metrics, and every airport seed is explicitly marked synthetic.
"""

SYNTHETIC_LABEL = "SYNTHETIC - not a real operational record"
SEED_SOURCE = "Synthetic seed reference"

AIRPORTS = [
    {"code": "DEL", "name": "Indira Gandhi Intl", "lat": 28.56, "lng": 77.10, "city": "Delhi", "country": "India"},
    {"code": "BOM", "name": "Chhatrapati Shivaji Intl", "lat": 19.09, "lng": 72.87, "city": "Mumbai", "country": "India"},
    {"code": "DXB", "name": "Dubai International", "lat": 25.25, "lng": 55.36, "city": "Dubai", "country": "UAE"},
    {"code": "SIN", "name": "Changi Airport", "lat": 1.36, "lng": 103.99, "city": "Singapore", "country": "Singapore"},
    {"code": "LHR", "name": "Heathrow", "lat": 51.47, "lng": -0.46, "city": "London", "country": "United Kingdom"},
    {"code": "JFK", "name": "John F Kennedy Intl", "lat": 40.64, "lng": -73.78, "city": "New York", "country": "United States"},
    {"code": "CDG", "name": "Charles de Gaulle", "lat": 49.01, "lng": 2.55, "city": "Paris", "country": "France"},
    {"code": "NRT", "name": "Narita International", "lat": 35.77, "lng": 140.39, "city": "Tokyo", "country": "Japan"},
    {"code": "SYD", "name": "Kingsford Smith", "lat": -33.94, "lng": 151.18, "city": "Sydney", "country": "Australia"},
    {"code": "GRU", "name": "Guarulhos International", "lat": -23.43, "lng": -46.47, "city": "Sao Paulo", "country": "Brazil"},
]

for airport in AIRPORTS:
    airport["source"] = SEED_SOURCE
    airport["SYNTHETIC_LABEL"] = SYNTHETIC_LABEL

AIRPORT_BY_CODE = {airport["code"]: airport for airport in AIRPORTS}

AIRLINES = [
    {"iata": "AI", "name": "Air India", "country": "India"},
    {"iata": "EK", "name": "Emirates", "country": "UAE"},
    {"iata": "SQ", "name": "Singapore Airlines", "country": "Singapore"},
    {"iata": "BA", "name": "British Airways", "country": "United Kingdom"},
    {"iata": "AF", "name": "Air France", "country": "France"},
    {"iata": "UA", "name": "United Airlines", "country": "United States"},
    {"iata": "LH", "name": "Lufthansa", "country": "Germany"},
    {"iata": "QF", "name": "Qantas", "country": "Australia"},
    {"iata": "TK", "name": "Turkish Airlines", "country": "Turkey"},
    {"iata": "CX", "name": "Cathay Pacific", "country": "Hong Kong"},
]

ALERT_TYPES = [
    "Altitude Anomaly",
    "Speed Deviation",
    "Route Divergence",
    "Squawk 7700",
    "No Signal",
]

SEVERITIES = ["low", "medium", "high"]
