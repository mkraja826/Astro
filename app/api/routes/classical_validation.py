"""Public routes for the external golden-chart validation harness."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.classical_validation import (
    GoldenChartCaseError,
    compare_golden_chart,
    get_validation_cases,
    get_validation_profile,
)
from app.engine.positions import BirthTimeError
from app.schemas.classical_validation import (
    GoldenChartCaseSetResponse,
    GoldenChartComparisonRequest,
    GoldenChartComparisonResponse,
    ValidationProfileResponse,
)

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


@router.get(
    "/profile",
    response_model=ValidationProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Read external golden-chart validation maturity",
)
def validation_profile() -> ValidationProfileResponse:
    """Return case counts, completion requirements, and comparison policy."""

    return get_validation_profile()


@router.get(
    "/cases",
    response_model=GoldenChartCaseSetResponse,
    status_code=status.HTTP_200_OK,
    summary="Read the frozen golden-chart case set",
)
def validation_cases() -> GoldenChartCaseSetResponse:
    """Return twelve immutable, globally diverse birth inputs."""

    return get_validation_cases()


@router.post(
    "/compare",
    response_model=GoldenChartComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare an external snapshot with one frozen case",
    responses={
        422: {"description": "Unknown case, empty snapshot, or invalid comparison input"},
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable"
        },
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
