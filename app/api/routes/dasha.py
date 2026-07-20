"""Versioned public routes for Dasha calculations."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.current_dasha import DashaQueryError, calculate_current_vimshottari
from app.engine.dasha import calculate_vimshottari
from app.engine.positions import BirthTimeError
from app.schemas.dasha import (
    CurrentVimshottariRequest,
    CurrentVimshottariResponse,
    VimshottariRequest,
    VimshottariResponse,
)

router = APIRouter(prefix="/v1/dashas", tags=["Dasha"])


@router.post(
    "/vimshottari",
    response_model=VimshottariResponse,
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


@router.post(
    "/vimshottari/current",
    response_model=CurrentVimshottariResponse,
    status_code=status.HTTP_200_OK,
    summary="Return the active Vimshottari chain at a requested instant",
    responses={
        422: {
            "description": (
                "Invalid birth/query time, ambiguous civil time, or instant outside "
                "the first 120-year cycle"
            ),
        },
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable",
        },
    },
)
def current_vimshottari(
    request: CurrentVimshottariRequest,
) -> CurrentVimshottariResponse:
    """Return only the active Mahadasha through Sookshma chain."""

    try:
        return calculate_current_vimshottari(request)
    except (BirthTimeError, DashaQueryError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
