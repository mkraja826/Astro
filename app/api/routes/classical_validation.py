"""Public routes for golden-chart validation and internal JPL baselines."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.classical_validation import (
    GoldenChartCaseError,
    compare_golden_chart,
    get_validation_cases,
    get_validation_profile,
)
from app.engine.classical_validation_baselines import (
    BaselineIntegrityError,
    get_jpl_baseline_case,
    load_jpl_baseline_manifest,
    verify_current_jpl_baselines,
    verify_jpl_baseline_storage,
)
from app.engine.classical_validation_imports import (
    ExternalSnapshotNormalizationError,
    normalize_external_snapshot,
)
from app.engine.classical_validation_manifest import (
    ExternalValidationManifestError,
    load_external_validation_manifest,
)
from app.engine.positions import BirthTimeError
from app.schemas.classical_validation import (
    GoldenChartCaseSetResponse,
    GoldenChartComparisonRequest,
    GoldenChartComparisonResponse,
    ValidationProfileResponse,
)
from app.schemas.classical_validation_baselines import (
    JplBaselineCaseResponse,
    JplBaselineManifest,
    JplBaselineRuntimeVerificationResponse,
    JplBaselineStorageVerificationResponse,
)
from app.schemas.classical_validation_imports import (
    ExternalSnapshotImportRequest,
    ExternalSnapshotImportResponse,
)
from app.schemas.classical_validation_manifest import ExternalValidationManifestSummary
from app.schemas.positions import CalculationProfile

router = APIRouter(
    prefix="/v1/classical/varahamihira_v1/validation",
    tags=["Classical Validation"],
)


def _unprocessable(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=str(exc),
    )


def _ephemeris_unavailable(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=str(exc),
    )


def _not_found(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=str(exc),
    )


def _external_manifest_summary() -> ExternalValidationManifestSummary:
    case_set = get_validation_cases()
    return load_external_validation_manifest(
        expected_profile_id=case_set.profile_id,
        expected_calculation_profile=(
            CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
        ),
        expected_case_set_id=case_set.case_set_id,
        expected_case_set_digest=case_set.case_set_digest,
        expected_case_ids={case.case_id for case in case_set.cases},
    )


@router.get(
    "/profile",
    response_model=ValidationProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Read external golden-chart validation maturity",
    responses={503: {"description": "Committed external validation manifest is invalid"}},
)
def validation_profile() -> ValidationProfileResponse:
    """Return maturity derived from committed, reviewed external evidence."""

    try:
        summary = _external_manifest_summary()
    except ExternalValidationManifestError as exc:
        raise _ephemeris_unavailable(exc) from exc

    profile = get_validation_profile()
    return profile.model_copy(
        update={
            "committed_external_snapshot_count": (
                summary.committed_external_snapshot_count
            ),
            "externally_validated_case_count": summary.externally_validated_case_count,
            "external_reference_validation_complete": (
                summary.external_reference_validation_complete
            ),
        }
    )


@router.get(
    "/cases",
    response_model=GoldenChartCaseSetResponse,
    status_code=status.HTTP_200_OK,
    summary="Read the frozen golden-chart case set",
)
def validation_cases() -> GoldenChartCaseSetResponse:
    """Return twelve immutable, globally diverse birth inputs."""

    return get_validation_cases()


@router.get(
    "/external/manifest",
    response_model=ExternalValidationManifestSummary,
    status_code=status.HTTP_200_OK,
    summary="Read and verify committed external validation evidence",
    responses={503: {"description": "Committed external validation evidence is invalid"}},
)
def validation_external_manifest() -> ExternalValidationManifestSummary:
    """Return the ledger plus counts derived from approved independent sources."""

    try:
        return _external_manifest_summary()
    except ExternalValidationManifestError as exc:
        raise _ephemeris_unavailable(exc) from exc


@router.post(
    "/normalize/external",
    response_model=ExternalSnapshotImportResponse,
    status_code=status.HTTP_200_OK,
    summary="Normalize an external Jyotisha software export",
    responses={
        422: {
            "description": (
                "Unsupported aliases, malformed values, or an empty normalized snapshot"
            )
        }
    },
)
def validation_normalize_external(
    request: ExternalSnapshotImportRequest,
) -> ExternalSnapshotImportResponse:
    """Normalize aliases without persisting or approving the supplied snapshot."""

    try:
        return normalize_external_snapshot(request)
    except ExternalSnapshotNormalizationError as exc:
        raise _unprocessable(exc) from exc


@router.post(
    "/compare",
    response_model=GoldenChartComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare an external snapshot with one frozen case",
    responses={
        422: {"description": "Unknown case, empty snapshot, or invalid comparison input"},
        503: {"description": "Required JPL ephemeris data is unavailable"},
    },
)
def validation_compare(
    request: GoldenChartComparisonRequest,
) -> GoldenChartComparisonResponse:
    """Return transparent matches and mismatches for all supplied scalar fields."""

    try:
        return compare_golden_chart(request)
    except (GoldenChartCaseError, BirthTimeError) as exc:
        raise _unprocessable(exc) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise _ephemeris_unavailable(exc) from exc


@router.get(
    "/baseline/manifest",
    response_model=JplBaselineManifest,
    status_code=status.HTTP_200_OK,
    summary="Read the immutable JPL golden baseline manifest",
    responses={503: {"description": "Committed baseline manifest is unavailable or invalid"}},
)
def baseline_manifest() -> JplBaselineManifest:
    """Return the versioned manifest without recalculating chart outputs."""

    try:
        return load_jpl_baseline_manifest()
    except BaselineIntegrityError as exc:
        raise _ephemeris_unavailable(exc) from exc


@router.get(
    "/baseline/integrity",
    response_model=JplBaselineStorageVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify committed JPL golden baseline storage",
    responses={503: {"description": "Committed baseline storage cannot be parsed"}},
)
def baseline_integrity() -> JplBaselineStorageVerificationResponse:
    """Verify case membership, per-case hashes, and the full logical-set digest."""

    try:
        return verify_jpl_baseline_storage()
    except BaselineIntegrityError as exc:
        raise _ephemeris_unavailable(exc) from exc


@router.get(
    "/baseline/cases/{case_id}",
    response_model=JplBaselineCaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Read one immutable JPL golden baseline",
    responses={
        404: {"description": "Unknown frozen case ID"},
        503: {"description": "Committed baseline storage failed integrity checks"},
    },
)
def baseline_case(case_id: str) -> JplBaselineCaseResponse:
    """Return one trusted internal regression snapshot by case ID."""

    try:
        return get_jpl_baseline_case(case_id)
    except GoldenChartCaseError as exc:
        raise _not_found(exc) from exc
    except BaselineIntegrityError as exc:
        raise _ephemeris_unavailable(exc) from exc


@router.post(
    "/baseline/verify-current",
    response_model=JplBaselineRuntimeVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Recalculate and verify all JPL golden baselines",
    responses={
        503: {"description": "JPL data or committed baseline storage is unavailable"}
    },
)
def baseline_verify_current() -> JplBaselineRuntimeVerificationResponse:
    """Run the current engine over all twelve cases and compare exact snapshots."""

    try:
        return verify_current_jpl_baselines()
    except (
        BaselineIntegrityError,
        EphemerisConfigurationError,
        EphemerisUnavailableError,
    ) as exc:
        raise _ephemeris_unavailable(exc) from exc
