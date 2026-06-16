"""
export.py — CSV + JSON export utilities for synthetic mock data
===============================================================
All exported files include a SYNTHETIC_LABEL header/field so any
consumer of the exported file knows the data is not real.
"""

import csv
import json
import io
from datetime import datetime, timezone


_EXPORT_HEADER_COMMENT = (
    "# ============================================================\n"
    "# SYNTHETIC DATA — Global Flight Intelligence Dashboard\n"
    "# Generated at: {timestamp}\n"
    "# WARNING: This file contains SIMULATED data only.\n"
    "#          No record represents a real flight or real event.\n"
    "# ============================================================\n"
)


def export_json(data: dict | list, indent: int = 2) -> str:
    """
    Serialize `data` to a JSON string with a synthetic-data envelope.

    The envelope adds:
        _meta.generated_at    — UTC timestamp
        _meta.synthetic       — True
        _meta.warning         — Human-readable disclaimer
        data                  — The actual payload

    Args:
        data:    Any JSON-serialisable dict or list.
        indent:  JSON indentation level (default 2).

    Returns:
        JSON string ready to write to a file or HTTP response.
    """
    envelope = {
        "_meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "synthetic":    True,
            "warning":      "SYNTHETIC DATA - not a real operational record.",
            "source":       "Global Flight Intelligence Dashboard — mock_data package",
        },
        "data": data,
    }
    return json.dumps(envelope, indent=indent, default=str)


def export_csv(rows: list[dict], extra_fields: list[str] | None = None) -> str:
    """
    Serialize a list of flat dicts to CSV string.

    Automatically adds a SYNTHETIC_LABEL column to every row so the
    exported CSV is unambiguously marked as mock data.

    Args:
        rows:          List of flat dicts (one per CSV row).
        extra_fields:  Additional column names to include (optional).

    Returns:
        CSV string (including header row) ready to write to a .csv file.
    """
    if not rows:
        return ""

    # Force SYNTHETIC_LABEL into every row
    labeled_rows = []
    for r in rows:
        row = dict(r)
        row.setdefault("SYNTHETIC_LABEL", "SYNTHETIC — not a real record")
        labeled_rows.append(row)

    # Determine columns: all keys from first row + any extras
    fieldnames = list(labeled_rows[0].keys())
    if extra_fields:
        for f in extra_fields:
            if f not in fieldnames:
                fieldnames.append(f)

    buf = io.StringIO()

    # Write the comment header (most spreadsheet apps ignore # lines)
    buf.write(_EXPORT_HEADER_COMMENT.format(
        timestamp=datetime.now(timezone.utc).isoformat()
    ))

    writer = csv.DictWriter(
        buf,
        fieldnames=fieldnames,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(labeled_rows)

    return buf.getvalue()