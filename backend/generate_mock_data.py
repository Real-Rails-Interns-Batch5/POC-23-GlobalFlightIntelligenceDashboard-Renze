"""
generate_mock_data.py — Run this manually to (re)generate the static
mock-data files that main.py reads from at runtime.

This keeps the served data as static JSON/CSV instead of live Python
generator calls, per reviewer feedback.

Usage:
    python generate_mock_data.py
"""
import json
import os

from mock_data import (
    make_mock_flights,
    make_mock_alerts,
    make_route_density,
    make_historical_replay,
    make_airport_detail,
    export_csv,
)
from mock_data.seeds import AIRPORTS
from mock_data.edge_cases import FLIGHT_EDGE_CASES, ALERT_EDGE_CASES, ROUTE_EDGE_CASES

OUT_DIR = os.path.join(os.path.dirname(__file__), "mock_data", "data")
os.makedirs(OUT_DIR, exist_ok=True)


def write_json(filename, payload):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"wrote {path}")


def write_csv(filename, content):
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", newline="") as f:
        f.write(content)
    print(f"wrote {path}")


def main():
    write_json("flights.json", make_mock_flights(60))
    write_csv("flights.csv", export_csv(make_mock_flights(20)))

    write_json("alerts.json", make_mock_alerts(6))
    write_csv("alerts.csv", export_csv(make_mock_alerts(10)))

    write_json("routes.json", make_route_density())
    write_json("replay.json", make_historical_replay())

    airport_details = {
        a["code"]: make_airport_detail(a["code"]) for a in AIRPORTS
    }
    write_json("airport_details.json", airport_details)

    write_json("edge_case_flights.json", FLIGHT_EDGE_CASES)
    write_json("edge_case_alerts.json", ALERT_EDGE_CASES)
    write_json("edge_case_routes.json", ROUTE_EDGE_CASES)

    write_json("download_bundle.json", {
        "flights": make_mock_flights(10),
        "alerts": make_mock_alerts(3),
        "routes": make_route_density(5),
    })


if __name__ == "__main__":
    main()