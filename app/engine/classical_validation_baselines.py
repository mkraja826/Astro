"""Load and verify committed Skyfield/JPL golden-chart regression baselines."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.engine.classical_reference import PROFILE_ID
from app.engine.classical_validation import (
    GoldenChartCaseError,
    build_actual_snapshot,
    get_validation_cases,
)
from app.schemas.classical_validation_baselines import (
    JplBaselineCaseRecord,
    JplBaselineCaseResponse,
    JplBaselineManifest,
    JplBaselineRuntimeCaseResult,
    JplBaselineRuntimeVerificationResponse,
    JplBaselineStorageVerificationResponse,
)


class BaselineIntegrityError(RuntimeError):
    """Raised when committed baseline data cannot be trusted or parsed."""


def _baseline_directory() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "validation" / "jpl_de440s_v1"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(value: Any) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BaselineIntegrityError(f"Baseline file is missing: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise BaselineIntegrityError(f"Baseline file is unreadable: {path}: {exc}") from exc


def load_jpl_baseline_manifest() -> JplBaselineManifest:
    """Parse the committed JPL baseline manifest with strict schema validation."""

    path = _baseline_directory() / "manifest.json"
    try:
        return JplBaselineManifest.model_validate(_read_json(path))
    except ValidationError as exc:
        raise BaselineIntegrityError(f"Baseline manifest is invalid: {exc}") from exc


def _safe_record_path(relative_path: str) -> Path:
    candidate = Path(relative_path)
    if (
        candidate.is_absolute()
        or candidate.name != relative_path
        or candidate.suffix.lower() != ".json"
        or relative_path == "manifest.json"
    ):
        raise BaselineIntegrityError(
            f"Baseline manifest contains an unsafe case path: {relative_path!r}"
        )
    return _baseline_directory() / candidate


def _load_record(relative_path: str) -> JplBaselineCaseRecord:
    path = _safe_record_path(relative_path)
    try:
        return JplBaselineCaseRecord.model_validate(_read_json(path))
    except ValidationError as exc:
        raise BaselineIntegrityError(f"Baseline case record is invalid: {path}: {exc}") from exc


def _manifest_payload_with_inline_cases(
    manifest: JplBaselineManifest,
    records: list[JplBaselineCaseRecord],
) -> dict[str, Any]:
    payload = manifest.model_dump(
        mode="json",
        exclude={"cases", "baseline_set_digest"},
    )
    payload["cases"] = [record.model_dump(mode="json") for record in records]
    return payload


def verify_jpl_baseline_storage() -> JplBaselineStorageVerificationResponse:
    """Verify case membership, per-snapshot hashes, and the logical set digest."""

    manifest = load_jpl_baseline_manifest()
    case_set = get_validation_cases()
    expected_ids = [case.case_id for case in case_set.cases]
    expected_id_set = set(expected_ids)
    manifest_ids = [reference.case_id for reference in manifest.cases]
    manifest_id_set = set(manifest_ids)
    duplicate_ids = sorted(
        case_id for case_id in manifest_id_set if manifest_ids.count(case_id) > 1
    )
    missing_ids = sorted(expected_id_set - manifest_id_set)
    unexpected_ids = sorted(manifest_id_set - expected_id_set)
    invalid_digest_ids: set[str] = set()
    issues: list[str] = []
    records: list[JplBaselineCaseRecord] = []

    for reference in manifest.cases:
        try:
            record = _load_record(reference.path)
        except BaselineIntegrityError as exc:
            issues.append(str(exc))
            continue

        records.append(record)
        calculated_digest = _digest(record.snapshot.model_dump(mode="json"))
        if record.case_id != reference.case_id:
            issues.append(
                f"Manifest case {reference.case_id} points to record {record.case_id}."
            )
            invalid_digest_ids.add(reference.case_id)
        if record.snapshot_digest != reference.snapshot_digest:
            issues.append(
                f"Record and manifest digests differ for {reference.case_id}."
            )
            invalid_digest_ids.add(reference.case_id)
        if calculated_digest != record.snapshot_digest:
            issues.append(f"Calculated snapshot digest differs for {reference.case_id}.")
            invalid_digest_ids.add(reference.case_id)

    case_set_digest_match = (
        manifest.case_set_id == case_set.case_set_id
        and manifest.case_set_version == case_set.case_set_version
        and manifest.case_set_digest == case_set.case_set_digest
    )
    if not case_set_digest_match:
        issues.append("Baseline manifest does not match the frozen validation case set.")

    baseline_set_digest_match = False
    if len(records) == len(manifest.cases):
        reconstructed = _manifest_payload_with_inline_cases(manifest, records)
        baseline_set_digest_match = _digest(reconstructed) == manifest.baseline_set_digest
    if not baseline_set_digest_match:
        issues.append("Logical baseline-set digest does not match the manifest.")

    if manifest.case_count != len(manifest.cases):
        issues.append("Manifest case_count does not match its case reference count.")
    if duplicate_ids:
        issues.append("Manifest contains duplicate case IDs.")
    if missing_ids:
        issues.append("Manifest is missing frozen case IDs.")
    if unexpected_ids:
        issues.append("Manifest contains unexpected case IDs.")

    verified = not (
        issues
        or duplicate_ids
        or missing_ids
        or unexpected_ids
        or invalid_digest_ids
    )
    return JplBaselineStorageVerificationResponse(
        profile_id=PROFILE_ID,
        baseline_set_id=manifest.baseline_set_id,
        baseline_set_version=manifest.baseline_set_version,
        baseline_set_digest=manifest.baseline_set_digest,
        calculation_profile=manifest.calculation_profile,
        expected_case_count=len(expected_ids),
        loaded_case_count=len(records),
        case_set_digest_match=case_set_digest_match,
        baseline_set_digest_match=baseline_set_digest_match,
        verified=verified,
        missing_case_ids=missing_ids,
        unexpected_case_ids=unexpected_ids,
        duplicate_case_ids=duplicate_ids,
        invalid_snapshot_digest_case_ids=sorted(invalid_digest_ids),
        issues=issues,
    )


def get_jpl_baseline_case(case_id: str) -> JplBaselineCaseResponse:
    """Return one trusted committed JPL baseline by frozen case ID."""

    verification = verify_jpl_baseline_storage()
    if not verification.verified:
        raise BaselineIntegrityError("Committed JPL baseline storage failed integrity checks")

    manifest = load_jpl_baseline_manifest()
    cases = {case.case_id: case for case in get_validation_cases().cases}
    try:
        case = cases[case_id]
        reference = next(item for item in manifest.cases if item.case_id == case_id)
    except (KeyError, StopIteration) as exc:
        raise GoldenChartCaseError(f"Unknown golden-chart case_id: {case_id}") from exc
    record = _load_record(reference.path)

    return JplBaselineCaseResponse(
        profile_id=PROFILE_ID,
        baseline_set_id=manifest.baseline_set_id,
        baseline_set_version=manifest.baseline_set_version,
        calculation_profile=manifest.calculation_profile,
        case=case,
        snapshot_digest=record.snapshot_digest,
        snapshot=record.snapshot,
        caveats=[
            "This is an internal deterministic JPL regression baseline.",
            "It is not an independent external software reference.",
            "External validation still requires two reviewed independent sources per case.",
        ],
    )


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    if isinstance(value, dict):
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(_flatten(value[key], path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            flattened.update(_flatten(item, f"{prefix}[{index}]"))
    else:
        flattened[prefix] = value
    return flattened


def verify_current_jpl_baselines() -> JplBaselineRuntimeVerificationResponse:
    """Recalculate all twelve cases and compare them with the committed snapshots."""

    storage = verify_jpl_baseline_storage()
    if not storage.verified:
        raise BaselineIntegrityError("Committed JPL baseline storage failed integrity checks")

    manifest = load_jpl_baseline_manifest()
    references = {item.case_id: item for item in manifest.cases}
    results: list[JplBaselineRuntimeCaseResult] = []
    for case in get_validation_cases().cases:
        reference = references[case.case_id]
        stored = _load_record(reference.path)
        actual = build_actual_snapshot(case, manifest.calculation_profile)
        actual_payload = actual.model_dump(mode="json")
        actual_digest = _digest(actual_payload)
        stored_flat = _flatten(stored.snapshot.model_dump(mode="json"))
        actual_flat = _flatten(actual_payload)
        mismatched_paths = sorted(
            path
            for path in set(stored_flat) | set(actual_flat)
            if stored_flat.get(path) != actual_flat.get(path)
        )
        results.append(
            JplBaselineRuntimeCaseResult(
                case_id=case.case_id,
                stored_snapshot_digest=stored.snapshot_digest,
                actual_snapshot_digest=actual_digest,
                matched=(
                    actual_digest == stored.snapshot_digest and not mismatched_paths
                ),
                mismatched_field_paths=mismatched_paths,
            )
        )

    matched_count = sum(result.matched for result in results)
    mismatched_count = len(results) - matched_count
    return JplBaselineRuntimeVerificationResponse(
        profile_id=PROFILE_ID,
        baseline_set_id=manifest.baseline_set_id,
        baseline_set_version=manifest.baseline_set_version,
        baseline_set_digest=manifest.baseline_set_digest,
        calculation_profile=manifest.calculation_profile,
        case_count=len(results),
        matched_case_count=matched_count,
        mismatched_case_count=mismatched_count,
        passed=mismatched_count == 0,
        cases=results,
        caveats=[
            "This verifies deterministic regression stability of the current JPL engine.",
            "A passing result does not constitute independent external validation.",
            "External approval counts remain unchanged by this operation.",
        ],
    )
