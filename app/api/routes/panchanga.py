"""Versioned public route for daily Panchanga calculations."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.core.swe_compat import ensure_rise_trans_constants
from app.engine.panchanga import (
    PanchangaTimeError,
    SolarEventError,
    calculate_panchanga,
)
from app.schemas.panchanga import PanchangaRequest, PanchangaResponse

router = APIRouter(prefix="/v1", tags=["Panchanga"])


@router.post(
    "/panchanga",
    response_model=PanchangaResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate daily sunrise-based Panchanga",
    responses={
        422: {
            "description": "Invalid timezone, coordinates, date, or unavailable solar event",
        },
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable",
        },
    },
)
def panchanga(request: PanchangaRequest) -> PanchangaResponse:
    """Return Vara, Tithi, Nakshatra, Yoga and Karana at local sunrise."""

    ensure_rise_trans_constants()
    try:
        return calculate_panchanga(request)
    except (PanchangaTimeError, SolarEventError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
