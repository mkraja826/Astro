"""Versioned public routes for classical Jyothisha data and evaluators."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.classical_aspect_rules import (
    extend_varahamihira_profile,
    extend_varahamihira_rules,
)
from app.engine.classical_aspects import calculate_varahamihira_aspects
from app.engine.classical_conditions import calculate_varahamihira_conditions
from app.engine.classical_reference import (
    get_varahamihira_grahas,
    get_varahamihira_profile,
    get_varahamihira_rashis,
    get_varahamihira_rules,
)
from app.engine.positions import BirthTimeError
from app.schemas.classical import (
    ClassicalProfileResponse,
    GrahaReferenceResponse,
    RashiReferenceResponse,
    RuleRegistryResponse,
)
from app.schemas.classical_aspects import (
    ClassicalAspectsRequest,
    ClassicalAspectsResponse,
)
from app.schemas.classical_conditions import (
    ClassicalConditionsRequest,
    ClassicalConditionsResponse,
)

router = APIRouter(
    prefix="/v1/classical/varahamihira_v1",
    tags=["Classical Reference"],
)


@router.get(
    "/profile",
    response_model=ClassicalProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Read the Varahamihira v1 source profile",
)
def varahamihira_profile() -> ClassicalProfileResponse:
    """Return the pinned source edition, scope, maturity, and profile caveats."""

    return extend_varahamihira_profile(get_varahamihira_profile())


@router.get(
    "/rules",
    response_model=RuleRegistryResponse,
    status_code=status.HTTP_200_OK,
    summary="Read the Varahamihira v1 rule registry",
)
def varahamihira_rules() -> RuleRegistryResponse:
    """Return source-traceable Chapter 1 and Chapter 2 rule registrations."""

    return extend_varahamihira_rules(get_varahamihira_rules())


@router.get(
    "/rashis",
    response_model=RashiReferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Read Chapter 1 Rashi reference data",
)
def varahamihira_rashis() -> RashiReferenceResponse:
    """Return deterministic Rashi names, lords, classes, and body correspondences."""

    return get_varahamihira_rashis()


@router.get(
    "/grahas",
    response_model=GrahaReferenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Read Chapter 2 Graha reference data",
)
def varahamihira_grahas() -> GrahaReferenceResponse:
    """Return deterministic seven-Graha attributes and dignity reference points."""

    return get_varahamihira_grahas()


@router.post(
    "/conditions",
    response_model=ClassicalConditionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate classical dignity and planetary conditions",
    responses={
        422: {
            "description": "Invalid coordinates, timezone, or local civil time",
        },
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable",
        },
    },
)
def varahamihira_conditions(
    request: ClassicalConditionsRequest,
) -> ClassicalConditionsResponse:
    """Return evidence-bearing D1/D9 dignity and condition results."""

    try:
        return calculate_varahamihira_conditions(request)
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
    "/aspects",
    response_model=ClassicalAspectsResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate classical aspects and whole-sign house influence",
    responses={
        422: {
            "description": "Invalid coordinates, timezone, or local civil time",
        },
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable",
        },
    },
)
def varahamihira_aspects(
    request: ClassicalAspectsRequest,
) -> ClassicalAspectsResponse:
    """Return fractional Graha aspects, conjunctions, and house influence."""

    try:
        return calculate_varahamihira_aspects(request)
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
