"""Versioned public route for sidereal planetary positions."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.positions import BirthTimeError, calculate_positions
from app.schemas.positions import PositionsRequest, PositionsResponse

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
    summary="Calculate sidereal planetary positions with JPL DE440s",
    responses={
        422: {
            "description": "Invalid coordinates, timezone, or local civil time",
        },
        503: {
            "description": "Required local JPL ephemeris data is unavailable",
        },
    },
)
def positions(request: PositionsRequest) -> PositionsResponse:
    """Return sidereal positions from the Skyfield/JPL production provider."""

    try:
        return calculate_positions(request)
    except BirthTimeError as exc:
        raise _unprocessable(exc) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise _ephemeris_unavailable(exc) from exc
