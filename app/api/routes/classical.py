"""Versioned public routes for classical Jyothisha data and evaluators."""

from fastapi import APIRouter, HTTPException, status

from app.core.ephemeris import EphemerisConfigurationError, EphemerisUnavailableError
from app.engine.classical_ashtakavarga import calculate_varahamihira_ashtakavarga
from app.engine.classical_aspects import calculate_varahamihira_aspects
from app.engine.classical_career import calculate_varahamihira_career
from app.engine.classical_conditions import calculate_varahamihira_conditions
from app.engine.classical_dasha import calculate_varahamihira_dasha_context
from app.engine.classical_dasha_rules import (
    extend_varahamihira_profile,
    extend_varahamihira_rules,
)
from app.engine.classical_reference import (
    get_varahamihira_grahas,
    get_varahamihira_profile,
    get_varahamihira_rashis,
    get_varahamihira_rules,
)
from app.engine.current_dasha import DashaQueryError
from app.engine.positions import BirthTimeError
from app.schemas.classical import (
    ClassicalProfileResponse,
    GrahaReferenceResponse,
    RashiReferenceResponse,
    RuleRegistryResponse,
)
from app.schemas.classical_ashtakavarga import (
    AshtakavargaRequest,
    AshtakavargaResponse,
)
from app.schemas.classical_aspects import (
    ClassicalAspectsRequest,
    ClassicalAspectsResponse,
)
from app.schemas.classical_career import (
    ClassicalCareerRequest,
    ClassicalCareerResponse,
)
from app.schemas.classical_conditions import (
    ClassicalConditionsRequest,
    ClassicalConditionsResponse,
)
from app.schemas.classical_dasha import (
    ClassicalDashaRequest,
    ClassicalDashaResponse,
)

router = APIRouter(
    prefix="/v1/classical/varahamihira_v1",
    tags=["Classical Reference"],
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
    """Return all source-traceable rules implemented by the profile."""

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
        422: {"description": "Invalid coordinates, timezone, or local civil time"},
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable"
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
        raise _unprocessable(exc) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise _ephemeris_unavailable(exc) from exc


@router.post(
    "/aspects",
    response_model=ClassicalAspectsResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate classical aspects and whole-sign house influence",
    responses={
        422: {"description": "Invalid coordinates, timezone, or local civil time"},
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable"
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
        raise _unprocessable(exc) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise _ephemeris_unavailable(exc) from exc


@router.post(
    "/career",
    response_model=ClassicalCareerResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Chapter 10 Karmājīva vocation channels",
    responses={
        422: {"description": "Invalid coordinates, timezone, or local civil time"},
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable"
        },
    },
)
def varahamihira_career(
    request: ClassicalCareerRequest,
) -> ClassicalCareerResponse:
    """Return unweighted Lagna, Moon, and Sun Karmājīva channels."""

    try:
        return calculate_varahamihira_career(request)
    except BirthTimeError as exc:
        raise _unprocessable(exc) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise _ephemeris_unavailable(exc) from exc


@router.post(
    "/ashtakavarga",
    response_model=AshtakavargaResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Chapter 9 Bhinnashtakavarga and Sarvashtakavarga",
    responses={
        422: {"description": "Invalid coordinates, timezone, or local civil time"},
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable"
        },
    },
)
def varahamihira_ashtakavarga(
    request: AshtakavargaRequest,
) -> AshtakavargaResponse:
    """Return raw contributor rows, planetary bindus, and aggregate bindus."""

    try:
        return calculate_varahamihira_ashtakavarga(request)
    except BirthTimeError as exc:
        raise _unprocessable(exc) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise _ephemeris_unavailable(exc) from exc


@router.post(
    "/dasha/current",
    response_model=ClassicalDashaResponse,
    status_code=status.HTTP_200_OK,
    summary="Annotate the active Vimshottari chain with classical evidence",
    responses={
        422: {
            "description": (
                "Invalid birth/query time, ambiguous civil time, or instant outside "
                "the first 120-year cycle"
            )
        },
        503: {
            "description": "Required licensed ephemeris configuration or data unavailable"
        },
    },
)
def varahamihira_dasha_current(
    request: ClassicalDashaRequest,
) -> ClassicalDashaResponse:
    """Return current Dasha timing with unweighted classical context."""

    try:
        return calculate_varahamihira_dasha_context(request)
    except (BirthTimeError, DashaQueryError) as exc:
        raise _unprocessable(exc) from exc
    except (EphemerisConfigurationError, EphemerisUnavailableError) as exc:
        raise _ephemeris_unavailable(exc) from exc
