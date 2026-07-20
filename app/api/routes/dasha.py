"""Versioned public routes for Dasha calculations."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.dasha import calculate_vimshottari
from app.engine.positions import BirthTimeError
from app.schemas.dasha import VimshottariRequest, VimshottariResponse

router = APIRouter(prefix="/v1/dashas", tags=["Dasha"])


@router.post(
    "/vimshottari",
    response_model=VimshottariResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Calculate Vimshottari timelines through optional Sookshma Dasha",
    responses={
        422: {
            "description": "Invalid coordinates, timezone, or local civil time",
        },
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable",
        },
    },
)
def vimshottari(request: VimshottariRequest) -> VimshottariResponse:
    """Return birth balance and Vimshottari timelines to the requested depth."""

    try:
        return calculate_vimshottari(request)
    except BirthTimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
