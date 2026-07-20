"""Versioned public route for sidereal planetary positions."""

from fastapi import APIRouter, HTTPException, status

from app.engine.positions import BirthTimeError, calculate_positions
from app.schemas.positions import PositionsRequest, PositionsResponse

router = APIRouter(prefix="/v1", tags=["Astronomy"])


@router.post(
    "/positions",
    response_model=PositionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate sidereal planetary positions",
    responses={
        422: {
            "description": "Invalid coordinates, timezone, or local civil time",
        }
    },
)
def positions(request: PositionsRequest) -> PositionsResponse:
    """Return Lahiri sidereal positions for the supported calculation profile."""

    try:
        return calculate_positions(request)
    except BirthTimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
