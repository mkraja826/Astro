"""Versioned public route for deterministic transit snapshots."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.positions import BirthTimeError
from app.engine.transits import calculate_transit_snapshot
from app.schemas.transits import TransitSnapshotRequest, TransitSnapshotResponse

router = APIRouter(prefix="/v1", tags=["Astronomy"])


@router.post(
    "/transits/snapshot",
    response_model=TransitSnapshotResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate a non-interpretive sidereal transit snapshot",
    responses={
        422: {"description": "Invalid coordinates, timezone, or local civil time"},
        503: {"description": "Required local JPL ephemeris data is unavailable"},
    },
)
def transit_snapshot(request: TransitSnapshotRequest) -> TransitSnapshotResponse:
    """Return natal/transit positions and whole-sign reference geometry."""

    try:
        return calculate_transit_snapshot(request)
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
