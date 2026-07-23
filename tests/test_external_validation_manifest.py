"""Tests for the committed external-validation approval ledger."""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.engine.classical_validation import get_validation_cases
from app.engine.classical_validation_manifest import (
    ExternalValidationManifestError,
    load_external_validation_manifest,
    summarize_external_validation_manifest,
)
from app.main import app
from app.schemas.classical_validation import ExternalReferenceSource, ValidationSourceKind
from app.schemas.classical_validation_manifest import (
    ExternalValidationManifest,
    ExternalValidationReviewStatus,
    ExternalValidationSnapshotRecord,
)
from app.schemas.positions import CalculationProfile

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1/validation"


def _source(name: str, kind: ValidationSourceKind = ValidationSourceKind.EXTERNAL_SOFTWARE):
    return ExternalReferenceSource(
        source_name=name,
        source_version="1.0",
        source_kind=kind,
        calculation_notes=["Lahiri sidereal", "true node"],
    )


def _record(case_id: str, source_id: str) -> ExternalValidationSnapshotRecord:
    return ExternalValidationSnapshotRecord(
        snapshot_id=f"{case_id}_{source_id}",
        case_id=case_id,
        source_id=source_id,
        source=_source(source_id),
        snapshot_path=f"app/data/validation/external_v1/{case_id}_{source_id}.json",
        snapshot_sha256="0" * 64,
        review_status=ExternalValidationReviewStatus.APPROVED,
        reviewed_by="validation-reviewer",
        reviewed_at=datetime(2026, 7, 23, 12, 0, tzinfo=UTC),
        review_notes=["Calculation settings and field discrepancies reviewed."],
    )


def _manifest(records: list[ExternalValidationSnapshotRecord]) -> ExternalValidationManifest:
    cases = get_validation_cases()
    return ExternalValidationManifest(
        manifest_id="jyothisyam_external_validation_manifest_v1",
        manifest_version="1.0.0",
        profile_id=cases.profile_id,
        calculation_profile=(
            CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
        ),
        case_set_id=cases.case_set_id,
        case_set_digest=cases.case_set_digest,
        required_external_sources_per_case=2,
        records=records,
        policy_notes=[],
    )


def _summary(manifest: ExternalValidationManifest):
    cases = get_validation_cases()
    return summarize_external_validation_manifest(
        manifest,
        expected_profile_id=cases.profile_id,
        expected_calculation_profile=(
            CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
        ),
        expected_case_set_id=cases.case_set_id,
        expected_case_set_digest=cases.case_set_digest,
        expected_case_ids={case.case_id for case in cases.cases},
        verify_record_files=False,
    )


def test_committed_manifest_is_truthfully_empty_and_digest_locked() -> None:
    cases = get_validation_cases()
    result = load_external_validation_manifest(
        expected_profile_id=cases.profile_id,
        expected_calculation_profile=(
            CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
        ),
        expected_case_set_id=cases.case_set_id,
        expected_case_set_digest=cases.case_set_digest,
        expected_case_ids={case.case_id for case in cases.cases},
    )

    assert result.manifest.manifest_id == "jyothisyam_external_validation_manifest_v1"
    assert len(result.manifest_digest) == 64
    assert result.committed_external_snapshot_count == 0
    assert result.approved_external_snapshot_count == 0
    assert result.externally_validated_case_count == 0
    assert result.validated_case_ids == []
    assert result.external_reference_validation_complete is False
    assert set(result.approved_source_counts_by_case) == {
        case.case_id for case in cases.cases
    }


def test_manifest_endpoint_and_profile_use_committed_ledger() -> None:
    manifest_response = client.get(f"{BASE_PATH}/external/manifest")
    manifest_payload = manifest_response.json()
    assert manifest_response.status_code == 200, manifest_payload
    assert manifest_payload["committed_external_snapshot_count"] == 0
    assert manifest_payload["approved_external_snapshot_count"] == 0
    assert manifest_payload["externally_validated_case_count"] == 0

    profile_response = client.get(f"{BASE_PATH}/profile")
    profile_payload = profile_response.json()
    assert profile_response.status_code == 200, profile_payload
    assert profile_payload["committed_external_snapshot_count"] == 0
    assert profile_payload["externally_validated_case_count"] == 0
    assert profile_payload["external_reference_validation_complete"] is False

    paths = client.get("/openapi.json").json()["paths"]
    assert f"{BASE_PATH}/external/manifest" in paths


def test_internal_baseline_cannot_enter_external_ledger() -> None:
    case_id = get_validation_cases().cases[0].case_id
    with pytest.raises(ValidationError, match="cannot use internal baselines"):
        ExternalValidationSnapshotRecord(
            snapshot_id="invalid_internal_record",
            case_id=case_id,
            source_id="internal_jpl",
            source=_source("internal", ValidationSourceKind.INTERNAL_BASELINE),
            snapshot_path="app/data/validation/external_v1/internal.json",
            snapshot_sha256="0" * 64,
            review_status=ExternalValidationReviewStatus.PENDING,
        )


def test_approved_snapshot_requires_reviewer_and_timestamp() -> None:
    case_id = get_validation_cases().cases[0].case_id
    with pytest.raises(ValidationError, match="require reviewed_by and reviewed_at"):
        ExternalValidationSnapshotRecord(
            snapshot_id="missing_review_metadata",
            case_id=case_id,
            source_id="source_a",
            source=_source("source_a"),
            snapshot_path="app/data/validation/external_v1/missing_review.json",
            snapshot_sha256="0" * 64,
            review_status=ExternalValidationReviewStatus.APPROVED,
        )


def test_two_distinct_approved_sources_validate_one_case_only() -> None:
    cases = get_validation_cases()
    case_id = cases.cases[0].case_id
    result = _summary(_manifest([_record(case_id, "source_a"), _record(case_id, "source_b")]))

    assert result.committed_external_snapshot_count == 2
    assert result.approved_external_snapshot_count == 2
    assert result.externally_validated_case_count == 1
    assert result.validated_case_ids == [case_id]
    assert result.approved_source_counts_by_case[case_id] == 2
    assert result.external_reference_validation_complete is False


def test_same_source_cannot_be_counted_twice_for_one_case() -> None:
    case_id = get_validation_cases().cases[0].case_id
    duplicate = _record(case_id, "source_a").model_copy(
        update={
            "snapshot_id": "duplicate_revision",
            "snapshot_path": "app/data/validation/external_v1/duplicate_revision.json",
        }
    )

    with pytest.raises(ExternalValidationManifestError, match="only one committed record"):
        _summary(_manifest([_record(case_id, "source_a"), duplicate]))
