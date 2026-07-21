"""Generate deterministic JPL DE440s golden-chart baseline snapshots."""

from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import skyfield

from app import __version__
from app.engine.classical_validation import build_actual_snapshot, get_validation_cases
from app.schemas.positions import CalculationProfile

BASELINE_SET_ID = "jyothisyam_jpl_de440s_golden_baselines_v1"
BASELINE_SET_VERSION = "1.0.0"
SNAPSHOT_SCHEMA_VERSION = "1.0.0"
CALCULATION_PROFILE = CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(value: Any) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def build_baseline_document() -> dict[str, Any]:
    """Calculate and normalize all frozen cases into one digest-locked document."""

    case_set = get_validation_cases()
    records: list[dict[str, Any]] = []
    for case in case_set.cases:
        snapshot = build_actual_snapshot(case, CALCULATION_PROFILE).model_dump(mode="json")
        records.append(
            {
                "case_id": case.case_id,
                "snapshot_digest": _digest(snapshot),
                "snapshot": snapshot,
            }
        )

    payload: dict[str, Any] = {
        "baseline_set_id": BASELINE_SET_ID,
        "baseline_set_version": BASELINE_SET_VERSION,
        "snapshot_schema_version": SNAPSHOT_SCHEMA_VERSION,
        "case_set_id": case_set.case_set_id,
        "case_set_version": case_set.case_set_version,
        "case_set_digest": case_set.case_set_digest,
        "calculation_profile": CALCULATION_PROFILE.value,
        "engine_version": __version__,
        "astronomical_provider": "skyfield_jpl",
        "provider_version": str(skyfield.__version__),
        "ephemeris_model": "de440s",
        "case_count": len(records),
        "cases": records,
    }
    payload["baseline_set_digest"] = _digest(payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("app/data/validation/jpl_de440s_v1.json"),
    )
    args = parser.parse_args()

    document = build_baseline_document()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Wrote {document['case_count']} JPL golden baselines to {args.output} "
        f"({document['baseline_set_digest']})"
    )


if __name__ == "__main__":
    main()
