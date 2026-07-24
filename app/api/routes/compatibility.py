"""Protected Phase 4 route for anonymous compatibility calculation facts."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.compatibility_facts import calculate_compatibility_facts
from app.engine.positions import BirthTimeError
from app.schemas.compatibility import (
    CompatibilityFactsResponse,
    DualChartCompatibilityRequest,
)

router = APIRouter(
    prefix="/v1/classical/varahamihira_v1/compatibility",
    tags=["Classical Compatibility"],
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


@router.post(
    "/facts",
    response_model=CompatibilityFactsResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate anonymous Kundli compatibility facts",
    responses={
        422: {
            "description": "Invalid birth input, timezone, roles, or compatibility facts",
        },
        503: {
            "description": "Required local JPL ephemeris data is unavailable",
        },
    },
)
def compatibility_facts(
    request: DualChartCompatibilityRequest,
) -> CompatibilityFactsResponse:
    """Return raw Ashtakoota facts without relationship interpretation."""

    try:
        return calculate_compatibility_facts(request)
    except (BirthTimeError, ValueError) as exc:
        raise _unprocessable(exc) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise _ephemeris_unavailable(exc) from exc
