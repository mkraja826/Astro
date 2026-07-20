"""Schemas for the Varahamihira dignity and condition evaluator."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from app.schemas.classical import ClassicalProfileId, NaturalTendency
from app.schemas.positions import (
    BirthInput,
    CalculationProfile,
    Coordinates,
    EngineMetadata,
    NormalizedTime,
)


class DignityState(StrEnum):
    """Primary sign-level dignity assigned by the evaluator."""

    EXALTATION_SIGN = "exaltation_sign"
    DEBILITATION_SIGN = "debilitation_sign"
    OWN_SIGN = "own_sign"
    ORDINARY = "ordinary"


class ResolvedTendency(StrEnum):
    """Resolved or intentionally unresolved natural tendency."""

    BENEFIC = "benefic"
    MALEFIC = "malefic"
    CONDITIONAL = "conditional"


class MoonPhaseState(StrEnum):
    """Lunar phase state used by the conditional Moon evaluator."""

    WAXING = "waxing"
    WANING = "waning"
    NEW_MOON_BOUNDARY = "new_moon_boundary"
    FULL_MOON_BOUNDARY = "full_moon_boundary"


class MercuryAssociationState(StrEnum):
    """Same-sign association state used by the Mercury evaluator."""

    UNASSOCIATED = "unassociated"
    BENEFIC_ONLY = "benefic_only"
    MALEFIC_ONLY = "malefic_only"
    MIXED = "mixed"
    CONDITIONAL = "conditional"


class ClassicalConditionsRequest(BaseModel):
    """Birth data used by the Varahamihira condition evaluator."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )


class ConditionEvidence(BaseModel):
    """One auditable condition result linked to a registered rule."""

    rule_id: str
    condition: str
    applies: bool
    reason: str


class MoonPhaseCondition(BaseModel):
    """Conditional Moon tendency resolved from Sun-Moon elongation."""

    elongation_degrees: float
    phase: MoonPhaseState
    resolved_tendency: ResolvedTendency
    reason: str
    rule_ids: list[str]


class MercuryAssociationCondition(BaseModel):
    """Conditional Mercury state resolved from same-sign associations."""

    d1_sign: str
    associated_grahas: list[str]
    benefic_associations: list[str]
    malefic_associations: list[str]
    conditional_associations: list[str]
    state: MercuryAssociationState
    resolved_tendency: ResolvedTendency
    reason: str
    rule_ids: list[str]


class GrahaCondition(BaseModel):
    """Dignity, Vargottama, and tendency results for one classical Graha."""

    graha: str
    source_longitude: float
    d1_sign_index: int
    d1_sign: str
    d1_degree_in_sign: float
    d1_house: int
    d9_longitude: float
    d9_sign_index: int
    d9_sign: str
    d9_degree_in_sign: float
    d9_house: int
    retrograde: bool
    own_sign: bool
    in_exaltation_sign: bool
    at_deep_exaltation_point: bool
    in_debilitation_sign: bool
    at_deep_debilitation_point: bool
    dignity: DignityState
    vargottama: bool
    natural_tendency_reference: NaturalTendency
    resolved_tendency: ResolvedTendency
    tendency_reason: str
    associations: list[str]
    evidence: list[ConditionEvidence]


class ClassicalConditionsResponse(BaseModel):
    """Complete non-predictive Varahamihira dignity and condition evaluation."""

    request_id: str
    profile_id: ClassicalProfileId
    calculation_profile: CalculationProfile
    time: NormalizedTime
    coordinates: Coordinates
    ayanamsha_degrees: float
    moon_phase: MoonPhaseCondition
    mercury_association: MercuryAssociationCondition
    grahas: list[GrahaCondition]
    excluded_points: list[str]
    metadata: EngineMetadata
    caveats: list[str]
