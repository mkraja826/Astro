"""Versioned public routes for classical Jyothisha reference data."""

from fastapi import APIRouter, status

from app.engine.classical_reference import (
    get_varahamihira_grahas,
    get_varahamihira_profile,
    get_varahamihira_rashis,
    get_varahamihira_rules,
)
from app.schemas.classical import (
    ClassicalProfileResponse,
    GrahaReferenceResponse,
    RashiReferenceResponse,
    RuleRegistryResponse,
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

    return get_varahamihira_profile()


@router.get(
    "/rules",
    response_model=RuleRegistryResponse,
    status_code=status.HTTP_200_OK,
    summary="Read the Varahamihira v1 rule registry",
)
def varahamihira_rules() -> RuleRegistryResponse:
    """Return source-traceable Chapter 1 and Chapter 2 rule registrations."""

    return get_varahamihira_rules()


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
