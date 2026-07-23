"""Tests for the external golden-chart validation harness."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.engine import classical_validation
from app.engine.classical_validation import (
    GoldenChartCaseError,
    build_actual_snapshot,
    compare_golden_chart,
    get_validation_cases,
)
from app.main import app
from app.schemas.classical_validation import (
    ExternalReferenceSource,
    GoldenChartComparisonRequest,
    GoldenChartSnapshot,
    ValidationSourceKind,
)
from app.schemas.positions import CalculationProfile

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1/validation"
EXPECTED_CASE_SET_DIGEST = (
    "5dcd67cd142e49127cdb62165ca8e1ccb7b28f58fabbf3612eeca42c5392f624"
)


def _source() -> ExternalReferenceSource:
    return ExternalReferenceSource(
        source_name="Independent Jyotisha Program",
        source_version="test-export-1",
        source_kind=ValidationSourceKind.EXTERNAL_SOFTWARE,
        calculation_notes=["Lahiri sidereal", "true node"],
    )


def test_validation_profile_is_explicitly_incomplete() -> None:
    response = client.get(f"{BASE_PATH}/profile")
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["harness_version"] == "1.0.0"
    assert payload["frozen_case_count"] == 12
    assert payload["required_external_sources_per_case"] == 2
    assert payload["committed_external_snapshot_count"] == 1
    assert payload["externally_validated_case_count"] == 0
    assert payload["external_reference_validation_complete"] is False
    assert "point_longitudes" in payload["supported_field_groups"]
    assert "bhinnashtakavarga" in payload["supported_field_groups"]
    assert "weighted_scores" in payload["supported_field_groups"]


def test_frozen_case_set_is_diverse_unique_and_digest_locked() -> None:
    response = client.get(f"{BASE_PATH}/cases")
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["case_set_id"] == "jyothisyam_external_golden_cases_v1"
    assert payload["case_set_version"] == "1.0.0"
    assert payload["case_set_digest"] == EXPECTED_CASE_SET_DIGEST

    cases = payload["cases"]
    assert len(cases) == 12
    assert len({case["case_id"] for case in cases}) == 12
    assert len({case["birth"]["timezone"] for case in cases}) >= 10
    assert any(case["birth"]["latitude"] < 0 for case in cases)
    assert any(case["birth"]["latitude"] > 60 for case in cases)
    assert any("equatorial" in case["coverage_tags"] for case in cases)
    assert any("leap_day" in case["coverage_tags"] for case in cases)
    assert any("near_midnight" in case["coverage_tags"] for case in cases)
    assert any("polar_night" in case["coverage_tags"] for case in cases)


def test_empty_reference_snapshot_is_rejected() -> None:
    with pytest.raises(ValidationError, match="at least one field group"):
        GoldenChartSnapshot()


def test_actual_snapshot_contains_every_supported_core_group() -> None:
    case = get_validation_cases().cases[0]
    snapshot = build_actual_snapshot(
        case,
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1,
    )

    assert snapshot.ayanamsha_degrees is not None
    assert snapshot.ascendant_longitude is not None
    assert len(snapshot.point_longitudes or {}) == 10
    assert len(snapshot.d1_signs or {}) == 10
    assert len(snapshot.d9_signs or {}) == 10
    assert len(snapshot.dignity or {}) == 7
    assert len(snapshot.vargottama or {}) == 7
    assert len(snapshot.compound_relationships or {}) == 42
    assert len(snapshot.bhinnashtakavarga or {}) == 7
    assert all(len(row) == 12 for row in (snapshot.bhinnashtakavarga or {}).values())
    assert len(snapshot.sarvashtakavarga or []) == 12
    assert len(snapshot.weighted_scores or {}) == 7
    assert len(snapshot.weighted_ranks or {}) == 7


def test_partial_snapshot_comparison_uses_tolerances_and_exact_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = get_validation_cases().cases[0]
    actual = GoldenChartSnapshot(
        ayanamsha_degrees=24.1234,
        point_longitudes={"sun": 210.0},
        d1_signs={"sun": 8},
        weighted_scores={"sun": 3.25},
    )
    monkeypatch.setattr(
        classical_validation,
        "build_actual_snapshot",
        lambda frozen_case, calculation_profile: actual,
    )

    request = GoldenChartComparisonRequest(
        case_id=case.case_id,
        source=_source(),
        reference_snapshot=GoldenChartSnapshot(
            ayanamsha_degrees=24.128,
            point_longitudes={"sun": 210.009},
            d1_signs={"sun": 8},
            weighted_scores={"sun": 3.2500005},
        ),
    )
    result = compare_golden_chart(request)

    assert result.passed is True
    assert result.compared_field_count == 4
    assert result.matched_field_count == 4
    assert result.mismatched_field_count == 0
    assert "d9_signs" in result.skipped_field_groups
    assert {item.status.value for item in result.comparisons} == {"match"}


def test_mismatch_is_reported_without_majority_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = get_validation_cases().cases[0]
    actual = GoldenChartSnapshot(
        d1_signs={"sun": 8},
        weighted_ranks={"sun": 2},
    )
    monkeypatch.setattr(
        classical_validation,
        "build_actual_snapshot",
        lambda frozen_case, calculation_profile: actual,
    )
    request = GoldenChartComparisonRequest(
        case_id=case.case_id,
        source=_source(),
        reference_snapshot=GoldenChartSnapshot(
            d1_signs={"sun": 7},
            weighted_ranks={"sun": 2},
        ),
    )

    result = compare_golden_chart(request)

    assert result.passed is False
    assert result.matched_field_count == 1
    assert result.mismatched_field_count == 1
    mismatch = next(item for item in result.comparisons if item.status == "mismatch")
    assert mismatch.path == "d1_signs.sun"
    assert mismatch.tolerance == 0.0


def test_unknown_case_is_rejected_before_calculation() -> None:
    request = GoldenChartComparisonRequest(
        case_id="missing_case",
        source=_source(),
        reference_snapshot=GoldenChartSnapshot(d1_signs={"sun": 1}),
    )

    with pytest.raises(GoldenChartCaseError, match="Unknown golden-chart case_id"):
        compare_golden_chart(request)


def test_validation_routes_are_in_profile_and_openapi() -> None:
    profile = client.get("/v1/classical/varahamihira_v1/profile").json()
    assert profile["profile_version"] == "1.10.0"
    expected_endpoints = {
        f"{BASE_PATH}/profile",
        f"{BASE_PATH}/cases",
        f"{BASE_PATH}/compare",
        f"{BASE_PATH}/baseline/manifest",
        f"{BASE_PATH}/baseline/integrity",
        f"{BASE_PATH}/baseline/cases/{{case_id}}",
        f"{BASE_PATH}/baseline/verify-current",
    }
    assert expected_endpoints.issubset(profile["endpoints"])

    paths = client.get("/openapi.json").json()["paths"]
    assert expected_endpoints.issubset(paths)


def test_weighting_conventions_do_not_enter_classical_rule_registry() -> None:
    rules = client.get("/v1/classical/varahamihira_v1/rules").json()["rules"]
    rule_ids = {rule["rule_id"] for rule in rules}

    assert len(rules) == 42
    assert not any("GOLDEN" in rule_id or "WEIGHTING" in rule_id for rule_id in rule_ids)
