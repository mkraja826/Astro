"""Versioned public routes for sidereal planetary positions."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.positions import BirthTimeError, calculate_positions
from app.engine.provider_comparison import compare_position_providers
from app.schemas.positions import PositionsRequest, PositionsResponse
from app.schemas.provider_comparison import (
    ProviderComparisonRequest,
    ProviderComparisonResponse,
)

router = APIRouter(prefix="/v1", tags=["Astronomy"])


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


@router.post(
    "/positions",
    response_model=PositionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate sidereal planetary positions",
    responses={
        422: {
            "description": "Invalid coordinates, timezone, or local civil time",
        },
        503: {
            "description": "Required ephemeris configuration or data unavailable",
        },
    },
)
def positions(request: PositionsRequest) -> PositionsResponse:
    """Return sidereal positions for the selected immutable calculation profile."""

    try:
        return calculate_positions(request)
    except BirthTimeError as exc:
        raise _unprocessable(exc) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise _ephemeris_unavailable(exc) from exc


@router.post(
    "/positions/providers/compare",
    response_model=ProviderComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Swiss and Skyfield/JPL position providers",
    responses={
        422: {
            "description": "Invalid coordinates, timezone, local civil time, or tolerance",
        },
        503: {
            "description": "One of the required ephemeris providers is unavailable",
        },
    },
)
def provider_comparison(
    request: ProviderComparisonRequest,
) -> ProviderComparisonResponse:
    """Return a transparent side-by-side migration report without changing defaults."""

    try:
        return compare_position_providers(request)
    except BirthTimeError as exc:
        raise _unprocessable(exc) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise _ephemeris_unavailable(exc) from exc
