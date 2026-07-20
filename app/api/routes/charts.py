"""Versioned public routes for divisional charts."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.charts import calculate_chart
from app.engine.positions import BirthTimeError
from app.schemas.charts import ChartRequest, ChartResponse, ChartType

router = APIRouter(prefix="/v1/charts", tags=["Charts"])


def _calculate(request: ChartRequest, chart_type: ChartType) -> ChartResponse:
    try:
        return calculate_chart(request, chart_type)
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
    "/d1",
    response_model=ChartResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate the D1 Rasi chart",
)
def d1_chart(request: ChartRequest) -> ChartResponse:
    """Return the Lahiri sidereal D1 Rasi chart."""

    return _calculate(request, ChartType.D1_RASI)


@router.post(
    "/d9",
    response_model=ChartResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate the D9 Navamsa chart",
)
def d9_chart(request: ChartRequest) -> ChartResponse:
    """Return the Parashari D9 Navamsa chart."""

    return _calculate(request, ChartType.D9_NAVAMSA)
