"""
mock_data — Synthetic data package for Global Flight Intelligence Dashboard
============================================================================
All records produced by this package are SYNTHETIC / SIMULATED.
No record represents a real flight, real alert, or real airport event.

Package structure:
    schema.py       — Data dictionary & field definitions for all entities
    generators.py   — Functions that produce realistic synthetic rows
    edge_cases.py   — Edge-case / error-state scenarios
    export.py       — CSV + JSON export utilities
    seeds.py        — Static seed data (airports, airlines, countries)
"""

from .generators import (
    make_mock_flights,
    make_mock_alerts,
    make_route_density,
    make_historical_replay,
    make_airport_detail,
)
from .export import export_json, export_csv
from .schema import DATA_DICTIONARY
from .samples import SAMPLE_ROWS

__all__ = [
    "make_mock_flights",
    "make_mock_alerts",
    "make_route_density",
    "make_historical_replay",
    "make_airport_detail",
    "export_json",
    "export_csv",
    "DATA_DICTIONARY",
    "SAMPLE_ROWS",
]
