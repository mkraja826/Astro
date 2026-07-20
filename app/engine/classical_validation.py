"""External golden-chart case registry, snapshot builder, and comparator."""

import json
from datetime import datetime
from hashlib import sha256
from typing import Any

from app.engine.charts import calculate_chart
from app.engine.classical_ashtakavarga import calculate_varahamihira_ashtakavarga
from app.engine.classical_conditions import calculate_varahamihira_conditions
from app.engine.classical_reference import PROFILE_ID
from app.engine.classical_relationships import calculate_varahamihira_relationships
from app.engine.classical_weighting import calculate_varahamihira_weighted_strength
from app.schemas.charts import ChartRequest, ChartType
from app.schemas.classical_ashtakavarga import AshtakavargaRequest
from app.schemas.classical_conditions import ClassicalConditionsRequest
from app.schemas.classical_relationships import ClassicalRelationshipsRequest
from app.schemas.classical_validation import (
    FieldComparison,
    GoldenChartCase,
    GoldenChartCaseSetResponse,
    GoldenChartComparisonRequest,
    GoldenChartComparisonResponse,
    GoldenChartSnapshot,
    ValidationFieldStatus,
    ValidationProfileResponse,
    ValidationTolerances,
)
from app.schemas.classical_weighting import ClassicalWeightedStrengthRequest
from app.schemas.positions import BirthInput

HARNESS_VERSION = "1.0.0"
CASE_SET_ID = "jyothisyam_external_golden_cases_v1"
CASE_SET_VERSION = "1.0.0"
_REQUIRED_EXTERNAL_SOURCES = 2


def _birth(
    local_datetime: str,
    timezone: str,
    latitude: float,
    longitude: float,
    altitude_meters: float = 0.0,
) -> BirthInput:
    return BirthInput(
        local_datetime=datetime.fromisoformat(local_datetime),
        timezone=timezone,
        latitude=latitude,
        longitude=longitude,
        altitude_meters=altitude_meters,
    )


_FROZEN_CASES = (
    GoldenChartCase(
        case_id="gc_india_nagarjuna_sagar_1998",
        label="Nagarjuna Sagar reference",
        birth=_birth("1998-10-26T10:28:00", "Asia/Kolkata", 16.575, 79.312, 120),
        coverage_tags=["india", "northern_hemisphere", "non_dst", "primary_fixture"],
    ),
    GoldenChartCase(
        case_id="gc_india_chennai_1985",
        label="Chennai early-morning case",
        birth=_birth("1985-01-15T06:45:00", "Asia/Kolkata", 13.0827, 80.2707, 7),
        coverage_tags=["india", "coastal", "early_morning", "non_dst"],
    ),
    GoldenChartCase(
        case_id="gc_india_delhi_2000",
        label="Delhi equinox-noon case",
        birth=_birth("2000-03-21T12:00:00", "Asia/Kolkata", 28.6139, 77.2090, 216),
        coverage_tags=["india", "equinox_window", "midday", "non_dst"],
    ),
    GoldenChartCase(
        case_id="gc_uk_london_1990",
        label="London summer-time case",
        birth=_birth("1990-06-15T14:30:00", "Europe/London", 51.5074, -0.1278, 11),
        coverage_tags=["europe", "dst", "western_longitude", "high_latitude"],
    ),
    GoldenChartCase(
        case_id="gc_usa_new_york_1975",
        label="New York standard-time case",
        birth=_birth("1975-11-05T09:15:00", "America/New_York", 40.7128, -74.0060, 10),
        coverage_tags=["north_america", "dst_zone", "western_longitude"],
    ),
    GoldenChartCase(
        case_id="gc_usa_los_angeles_2001",
        label="Los Angeles near-midnight case",
        birth=_birth("2001-08-12T23:40:00", "America/Los_Angeles", 34.0522, -118.2437, 71),
        coverage_tags=["north_america", "dst", "near_midnight", "western_longitude"],
    ),
    GoldenChartCase(
        case_id="gc_australia_sydney_1988",
        label="Sydney leap-year case",
        birth=_birth("1988-02-29T04:20:00", "Australia/Sydney", -33.8688, 151.2093, 58),
        coverage_tags=["southern_hemisphere", "leap_day", "dst", "early_morning"],
    ),
    GoldenChartCase(
        case_id="gc_japan_tokyo_2010",
        label="Tokyo year-end boundary case",
        birth=_birth("2010-12-31T23:59:00", "Asia/Tokyo", 35.6762, 139.6503, 40),
        coverage_tags=["east_asia", "non_dst", "year_boundary", "near_midnight"],
    ),
    GoldenChartCase(
        case_id="gc_kenya_nairobi_1995",
        label="Nairobi equatorial case",
        birth=_birth("1995-05-10T16:05:00", "Africa/Nairobi", -1.2921, 36.8219, 1795),
        coverage_tags=["africa", "equatorial", "southern_hemisphere", "high_altitude"],
    ),
    GoldenChartCase(
        case_id="gc_iceland_reykjavik_1969",
        label="Reykjavik high-latitude case",
        birth=_birth("1969-07-20T20:17:00", "Atlantic/Reykjavik", 64.1466, -21.9426, 61),
        coverage_tags=["high_latitude", "non_dst", "western_longitude"],
    ),
    GoldenChartCase(
        case_id="gc_norway_tromso_2005",
        label="Tromso polar-night case",
        birth=_birth("2005-12-21T12:00:00", "Europe/Oslo", 69.6492, 18.9553, 10),
        coverage_tags=["arctic", "high_latitude", "polar_night", "dst_zone"],
    ),
    GoldenChartCase(
        case_id="gc_ecuador_quito_1999",
        label="Quito equator and altitude case",
        birth=_birth("1999-09-09T09:09:00", "America/Guayaquil", -0.1807, -78.4678, 2850),
        coverage_tags=["south_america", "equatorial", "high_altitude", "non_dst"],
    ),
)
_CASES_BY_ID = {case.case_id: case for case in _FROZEN_CASES}


class GoldenChartCaseError(ValueError):
    """Raised when a comparison references an unknown frozen case."""


def _case_set_digest() -> str:
    payload = [case.model_dump(mode="json") for case in _FROZEN_CASES]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()


def get_validation_cases() -> GoldenChartCaseSetResponse:
    """Return the immutable, globally diverse chart-input set."""

    return GoldenChartCaseSetResponse(
        profile_id=PROFILE_ID,
        case_set_id=CASE_SET_ID,
        case_set_version=CASE_SET_VERSION,
        case_set_digest=_case_set_digest(),
        cases=[case.model_copy(deep=True) for case in _FROZEN_CASES],
    )


def get_validation_profile() -> ValidationProfileResponse:
    """Return validation maturity without overstating external completion."""

    return ValidationProfileResponse(
        profile_id=PROFILE_ID,
        harness_version=HARNESS_VERSION,
        case_set_id=CASE_SET_ID,
        case_set_version=CASE_SET_VERSION,
        frozen_case_count=len(_FROZEN_CASES),
        required_external_sources_per_case=_REQUIRED_EXTERNAL_SOURCES,
        committed_external_snapshot_count=0,
        externally_validated_case_count=0,
        external_reference_validation_complete=False,
        supported_field_groups=list(GoldenChartSnapshot.model_fields),
        comparison_policy=[
            "Compare only fields explicitly supplied by the reference source.",
            "Use field-specific tolerances for ayanamsha, longitudes, and API scores.",
            "Treat categorical, sign, rank, and bindu values as exact comparisons.",
            "Record disagreements; never resolve them by majority vote alone.",
            "Require two independent external sources per frozen case before completion.",
        ],
        caveats=[
            "No third-party software snapshots are committed in version 1.0.0.",
            "The harness is ready, but external validation remains incomplete.",
            "Weighted scores are an API convention and may be omitted by external software.",
            "Sensitive birth-risk and longevity outputs remain outside validation scope.",
        ],
    )


def build_actual_snapshot(
    case: GoldenChartCase,
    calculation_profile: Any,
) -> GoldenChartSnapshot:
    """Calculate one normalized snapshot from existing validated engines."""

    chart_request = ChartRequest(
        birth=case.birth,
        calculation_profile=calculation_profile,
    )
    d1 = calculate_chart(chart_request, ChartType.D1_RASI)
    d9 = calculate_chart(chart_request, ChartType.D9_NAVAMSA)
    conditions = calculate_varahamihira_conditions(
        ClassicalConditionsRequest(
            birth=case.birth,
            calculation_profile=calculation_profile,
        )
    )
    relationships = calculate_varahamihira_relationships(
        ClassicalRelationshipsRequest(
            birth=case.birth,
            calculation_profile=calculation_profile,
        )
    )
    ashtakavarga = calculate_varahamihira_ashtakavarga(
        AshtakavargaRequest(
            birth=case.birth,
            calculation_profile=calculation_profile,
        )
    )
    weighted = calculate_varahamihira_weighted_strength(
        ClassicalWeightedStrengthRequest(
            birth=case.birth,
            calculation_profile=calculation_profile,
        )
    )

    d1_points = {point.name: point for point in d1.points}
    d9_points = {point.name: point for point in d9.points}
    point_longitudes = {"ascendant": d1.ascendant.source_longitude}
    point_longitudes.update(
        {name: point.source_longitude for name, point in d1_points.items()}
    )
    d1_signs = {"ascendant": d1.ascendant.sign_index}
    d1_signs.update({name: point.sign_index for name, point in d1_points.items()})
    d9_signs = {"ascendant": d9.ascendant.sign_index}
    d9_signs.update({name: point.sign_index for name, point in d9_points.items()})

    return GoldenChartSnapshot(
        ayanamsha_degrees=d1.ayanamsha_degrees,
        ascendant_longitude=d1.ascendant.source_longitude,
        point_longitudes=point_longitudes,
        d1_signs=d1_signs,
        d9_signs=d9_signs,
        dignity={item.graha: item.dignity.value for item in conditions.grahas},
        vargottama={item.graha: item.vargottama for item in conditions.grahas},
        compound_relationships={
            f"{item.source_graha}>{item.target_graha}": item.compound_relationship.value
            for item in relationships.directed_relationships
        },
        bhinnashtakavarga={
            record.graha: list(record.bindus_by_sign)
            for record in ashtakavarga.bhinnashtakavargas
        },
        sarvashtakavarga=list(ashtakavarga.sarvashtakavarga.bindus_by_sign),
        weighted_scores={
            item.graha: item.total_score for item in weighted.weighted_grahas
        },
        weighted_ranks={item.graha: item.rank for item in weighted.weighted_grahas},
    )


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    if isinstance(value, dict):
        for key in sorted(value):
            path = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(_flatten(value[key], path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            path = f"{prefix}[{index}]"
            flattened.update(_flatten(item, path))
    else:
        flattened[prefix] = value
    return flattened


def _tolerance_for(path: str, tolerances: ValidationTolerances) -> float | None:
    if path == "ayanamsha_degrees":
        return tolerances.ayanamsha_degrees
    if "longitude" in path:
        return tolerances.longitude_degrees
    if path.startswith("weighted_scores"):
        return tolerances.score
    return None


def _compare_value(
    path: str,
    actual: Any,
    reference: Any,
    tolerances: ValidationTolerances,
) -> FieldComparison:
    tolerance = _tolerance_for(path, tolerances)
    if (
        isinstance(actual, (int, float))
        and not isinstance(actual, bool)
        and isinstance(reference, (int, float))
        and not isinstance(reference, bool)
    ):
        difference = abs(float(actual) - float(reference))
        allowed = tolerance if tolerance is not None else 0.0
        matched = difference <= allowed
        return FieldComparison(
            path=path,
            status=(
                ValidationFieldStatus.MATCH
                if matched
                else ValidationFieldStatus.MISMATCH
            ),
            actual_value=str(actual),
            reference_value=str(reference),
            absolute_difference=round(difference, 10),
            tolerance=allowed,
            reason=(
                f"Numeric difference {difference} is within tolerance {allowed}."
                if matched
                else f"Numeric difference {difference} exceeds tolerance {allowed}."
            ),
        )

    matched = actual == reference
    return FieldComparison(
        path=path,
        status=(
            ValidationFieldStatus.MATCH
            if matched
            else ValidationFieldStatus.MISMATCH
        ),
        actual_value=str(actual),
        reference_value=str(reference),
        reason="Exact values match." if matched else "Exact values differ.",
    )


def _missing_actual(path: str, reference: Any) -> FieldComparison:
    return FieldComparison(
        path=path,
        status=ValidationFieldStatus.MISMATCH,
        actual_value="<missing>",
        reference_value=str(reference),
        reason="The supplied reference path is not available in the normalized snapshot.",
    )


def compare_golden_chart(
    request: GoldenChartComparisonRequest,
) -> GoldenChartComparisonResponse:
    """Compare supplied external fields against one frozen case calculation."""

    try:
        case = _CASES_BY_ID[request.case_id]
    except KeyError as exc:
        raise GoldenChartCaseError(
            f"Unknown golden-chart case_id: {request.case_id}"
        ) from exc

    actual = build_actual_snapshot(case, request.calculation_profile)
    reference_groups = request.reference_snapshot.model_dump(exclude_none=True)
    actual_flat = _flatten(actual.model_dump())
    reference_flat = _flatten(reference_groups)
    comparisons = [
        (
            _compare_value(
                path,
                actual_flat[path],
                reference_value,
                request.tolerances,
            )
            if path in actual_flat
            else _missing_actual(path, reference_value)
        )
        for path, reference_value in reference_flat.items()
    ]
    matched = sum(item.status == ValidationFieldStatus.MATCH for item in comparisons)
    mismatched = len(comparisons) - matched
    skipped = [
        field_name
        for field_name in GoldenChartSnapshot.model_fields
        if field_name not in reference_groups
    ]

    return GoldenChartComparisonResponse(
        profile_id=PROFILE_ID,
        case=case.model_copy(deep=True),
        source=request.source,
        actual_snapshot=actual,
        compared_field_count=len(comparisons),
        matched_field_count=matched,
        mismatched_field_count=mismatched,
        skipped_field_groups=skipped,
        passed=mismatched == 0,
        comparisons=comparisons,
        external_reference_validation_complete=False,
        caveats=[
            "A passing comparison validates only the supplied field groups.",
            "The request is not persisted as an approved external snapshot.",
            "Two independent approved sources per case are required for completion.",
            "Disagreements must be resolved from calculation contracts, not majority vote.",
        ],
    )
