"""Compose existing Astro evidence into direct Varahamihira-engine findings."""

from varahamihira_engine import evaluate, request_from_astro_analysis

from app.engine.classical_transits import calculate_varahamihira_transit_horizon
from app.engine.classical_weighting_integrations import (
    calculate_varahamihira_weighted_career,
    calculate_varahamihira_weighted_dasha,
)
from app.schemas.classical_prediction import (
    ClassicalPredictionRequest,
    ClassicalPredictionResponse,
)
from app.schemas.classical_transits import (
    ClassicalTransitHorizonRequest,
    TransitHorizonPeriod,
)
from app.schemas.classical_weighting import (
    ClassicalWeightedDashaRequest,
    ClassicalWeightedStrengthRequest,
)


def calculate_varahamihira_prediction(
    request: ClassicalPredictionRequest,
) -> ClassicalPredictionResponse:
    """Calculate Astro evidence once and resolve it without changing its direction."""

    weighted_career = calculate_varahamihira_weighted_career(
        ClassicalWeightedStrengthRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )
    weighted_dasha = calculate_varahamihira_weighted_dasha(
        ClassicalWeightedDashaRequest(
            birth=request.birth,
            as_of=request.as_of,
            calculation_profile=request.calculation_profile,
        )
    )
    transit_horizon = (
        None
        if request.period.value == "natal"
        else calculate_varahamihira_transit_horizon(
            ClassicalTransitHorizonRequest(
                birth=request.birth,
                as_of=request.as_of,
                period=TransitHorizonPeriod(request.period.value),
                calculation_profile=request.calculation_profile,
            )
        )
    )
    as_of = f"{request.as_of.local_datetime.isoformat()}[{request.as_of.timezone}]"
    engine_request = request_from_astro_analysis(
        period=request.period.value,
        as_of=as_of,
        weighted_career=weighted_career.model_dump(mode="json"),
        weighted_dasha=weighted_dasha.model_dump(mode="json"),
        transit_horizon=(
            transit_horizon.model_dump(mode="json")
            if transit_horizon is not None
            else None
        ),
    )
    return ClassicalPredictionResponse.model_validate(evaluate(engine_request).as_dict())
