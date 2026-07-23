"""Load, verify, and summarize the committed external-validation ledger."""

import json
from hashlib import sha256
from pathlib import Path

from pydantic import ValidationError

from app.schemas.classical import ClassicalProfileId
from app.schemas.classical_validation_manifest import (
    ExternalValidationManifest,
    ExternalValidationManifestSummary,
    ExternalValidationReviewStatus,
)
from app.schemas.positions import CalculationProfile

_MANIFEST_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "validation"
    / "external_v1"
    / "manifest.json"
)
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class ExternalValidationManifestError(ValueError):
    """Raised when committed validation evidence violates the approval contract."""


def _logical_digest(manifest: ExternalValidationManifest) -> str:
    payload = manifest.model_dump(mode="json")
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


def _verify_record_file(snapshot_path: str, expected_sha256: str) -> None:
    path = (_REPOSITORY_ROOT / snapshot_path).resolve()
    evidence_root = (
        _REPOSITORY_ROOT / "app" / "data" / "validation" / "external_v1"
    ).resolve()
    if evidence_root not in path.parents:
        raise ExternalValidationManifestError(
            f"External snapshot path escapes evidence directory: {snapshot_path}"
        )
    if not path.is_file():
        raise ExternalValidationManifestError(
            f"External snapshot file is missing: {snapshot_path}"
        )
    actual_sha256 = sha256(path.read_bytes()).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ExternalValidationManifestError(
            f"External snapshot digest mismatch for {snapshot_path}"
        )


def summarize_external_validation_manifest(
    manifest: ExternalValidationManifest,
    *,
    expected_profile_id: ClassicalProfileId,
    expected_calculation_profile: CalculationProfile,
    expected_case_set_id: str,
    expected_case_set_digest: str,
    expected_case_ids: set[str],
    verify_record_files: bool = True,
) -> ExternalValidationManifestSummary:
    """Validate identity, provenance, storage, and independent-source completion."""

    if manifest.profile_id != expected_profile_id:
        raise ExternalValidationManifestError("External manifest profile_id is not canonical")
    if manifest.calculation_profile != expected_calculation_profile:
        raise ExternalValidationManifestError(
            "External manifest calculation_profile is not canonical"
        )
    if manifest.case_set_id != expected_case_set_id:
        raise ExternalValidationManifestError("External manifest case_set_id is stale")
    if manifest.case_set_digest != expected_case_set_digest:
        raise ExternalValidationManifestError("External manifest case_set_digest is stale")

    snapshot_ids: set[str] = set()
    snapshot_paths: set[str] = set()
    case_sources: set[tuple[str, str]] = set()
    approved_sources_by_case: dict[str, set[str]] = {
        case_id: set() for case_id in sorted(expected_case_ids)
    }

    for record in manifest.records:
        if record.case_id not in expected_case_ids:
            raise ExternalValidationManifestError(
                f"External snapshot references unknown case: {record.case_id}"
            )
        if record.snapshot_id in snapshot_ids:
            raise ExternalValidationManifestError(
                f"Duplicate external snapshot_id: {record.snapshot_id}"
            )
        if record.snapshot_path in snapshot_paths:
            raise ExternalValidationManifestError(
                f"Duplicate external snapshot_path: {record.snapshot_path}"
            )
        case_source = (record.case_id, record.source_id)
        if case_source in case_sources:
            raise ExternalValidationManifestError(
                "A source may contribute only one committed record per frozen case: "
                f"{record.case_id}/{record.source_id}"
            )

        snapshot_ids.add(record.snapshot_id)
        snapshot_paths.add(record.snapshot_path)
        case_sources.add(case_source)
        if verify_record_files:
            _verify_record_file(record.snapshot_path, record.snapshot_sha256)
        if record.review_status == ExternalValidationReviewStatus.APPROVED:
            approved_sources_by_case[record.case_id].add(record.source_id)

    approved_source_counts = {
        case_id: len(source_ids)
        for case_id, source_ids in approved_sources_by_case.items()
    }
    validated_case_ids = sorted(
        case_id
        for case_id, count in approved_source_counts.items()
        if count >= manifest.required_external_sources_per_case
    )
    approved_snapshot_count = sum(
        record.review_status == ExternalValidationReviewStatus.APPROVED
        for record in manifest.records
    )

    return ExternalValidationManifestSummary(
        manifest=manifest,
        manifest_digest=_logical_digest(manifest),
        committed_external_snapshot_count=len(manifest.records),
        approved_external_snapshot_count=approved_snapshot_count,
        externally_validated_case_count=len(validated_case_ids),
        validated_case_ids=validated_case_ids,
        approved_source_counts_by_case=approved_source_counts,
        external_reference_validation_complete=(
            bool(expected_case_ids) and len(validated_case_ids) == len(expected_case_ids)
        ),
    )


def load_external_validation_manifest(
    *,
    expected_profile_id: ClassicalProfileId,
    expected_calculation_profile: CalculationProfile,
    expected_case_set_id: str,
    expected_case_set_digest: str,
    expected_case_ids: set[str],
) -> ExternalValidationManifestSummary:
    """Read the committed JSON manifest and derive its truthful maturity summary."""

    try:
        payload = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest = ExternalValidationManifest.model_validate(payload)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise ExternalValidationManifestError(
            "Committed external validation manifest is unavailable or invalid"
        ) from exc

    return summarize_external_validation_manifest(
        manifest,
        expected_profile_id=expected_profile_id,
        expected_calculation_profile=expected_calculation_profile,
        expected_case_set_id=expected_case_set_id,
        expected_case_set_digest=expected_case_set_digest,
        expected_case_ids=expected_case_ids,
    )
