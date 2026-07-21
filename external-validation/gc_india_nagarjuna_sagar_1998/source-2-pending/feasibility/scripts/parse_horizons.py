"""Parse feasibility values only from retained, hashed Horizons responses."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

FEASIBILITY_DIRECTORY = Path(__file__).resolve().parents[1]
RAW_DIRECTORY = FEASIBILITY_DIRECTORY / "raw-responses"


def response_text(path: Path) -> tuple[dict[str, Any], str]:
    """Load a retained Horizons JSON response and return its result text."""

    raw_bytes = path.read_bytes()
    payload = json.loads(raw_bytes)
    if "error" in payload:
        raise RuntimeError(f"Horizons error in {path.name}: {payload['error']}")
    return payload, payload["result"]


def table_header_and_row(result: str) -> tuple[list[str], list[str]]:
    """Extract the CSV header and single retained data row from a Horizons table."""

    before, after = result.split("$$SOE", maxsplit=1)
    data_block, _ = after.split("$$EOE", maxsplit=1)
    data_line = next(line for line in data_block.splitlines() if line.strip())
    header_line = next(
        line
        for line in reversed(before.splitlines())
        if "," in line and ("ObsEcLon" in line or "JDTDB" in line)
    )
    header = [item.strip() for item in next(csv.reader([header_line]))]
    row = [item.strip() for item in next(csv.reader([data_line]))]
    if len(row) != len(header):
        raise RuntimeError(
            f"Horizons CSV width mismatch: {len(header)} headers, {len(row)} values"
        )
    return header, row


def mapped_row(result: str) -> dict[str, str]:
    """Map non-empty Horizons column labels to retained string values."""

    header, row = table_header_and_row(result)
    return {key: value for key, value in zip(header, row, strict=True) if key}


def extract_line(result: str, label: str) -> str | None:
    """Extract one descriptive header line without interpreting its value."""

    for line in result.splitlines():
        if line.strip().startswith(label):
            return line.strip()
    return None


def parse_observer(path: Path) -> dict[str, Any]:
    """Parse quantity 31 from one retained observer response."""

    payload, result = response_text(path)
    row = mapped_row(result)
    return {
        "response_filename": path.name,
        "response_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "api_version": payload["signature"]["version"],
        "api_source": payload["signature"]["source"],
        "target": extract_line(result, "Target body name:"),
        "center": extract_line(result, "Center body name:"),
        "center_site": extract_line(result, "Center-site name:"),
        "start_time": extract_line(result, "Start time"),
        "time_column": next(value for key, value in row.items() if "Date" in key),
        "apparent_tropical_ecliptic_longitude_degrees": float(row["ObsEcLon"]),
        "apparent_tropical_ecliptic_latitude_degrees": float(row["ObsEcLat"]),
    }


def parse_elements(path: Path) -> dict[str, Any]:
    """Parse Moon OM while retaining its frame caveat and exact source row."""

    payload, result = response_text(path)
    row = mapped_row(result)
    reference = next(
        (
            line.strip()
            for line in result.splitlines()
            if "Reference frame" in line or "Ecliptic" in line and "J2000" in line
        ),
        None,
    )
    return {
        "response_filename": path.name,
        "response_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "api_version": payload["signature"]["version"],
        "api_source": payload["signature"]["source"],
        "target": extract_line(result, "Target body name:"),
        "center": extract_line(result, "Center body name:"),
        "reference_plane_or_frame_line": reference,
        "epoch_jd_tdb": float(row["JDTDB"]),
        "osculating_ascending_node_om_degrees": float(row["OM"]),
        "true_node_status": "unresolved",
        "reason": (
            "Horizons OM is an osculating node relative to the selected "
            "ecliptic/equinox; equivalence to apparent Jyotisha true Rahu has "
            "not been established."
        ),
        "ketu_derived": False,
    }


def main() -> None:
    """Parse all retained Horizons responses into a generated feasibility result."""

    observer_results: dict[str, Any] = {}
    for path in sorted(RAW_DIRECTORY.glob("horizons-observer-*.json")):
        body = re.fullmatch(r"horizons-observer-(.+)\.json", path.name).group(1)
        observer_results[body] = parse_observer(path)

    result = {
        "schema_version": "1.0.0",
        "purpose": "source_2_feasibility_parsed_horizons_fields",
        "comparison_performed": False,
        "observer_quantity_31": observer_results,
        "lunar_elements": parse_elements(RAW_DIRECTORY / "horizons-elements-moon.json"),
    }
    (FEASIBILITY_DIRECTORY / "parsed-horizons.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
