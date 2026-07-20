"""Schemas for transparent, unweighted classical strength factors."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.classical import ClassicalProfileId
from app.schemas.classical_conditions import DignityState, ResolvedTendency
from app.schemas.classical_relationships import (
    CompoundRelationship,
    NaturalRelationship,
    TemporaryRelationship,
)
from app.schemas.positions import (
    BirthInput,
    CalculationProfile,
    Coordinates,
    EngineMetadata,
    NormalizedTime,
)


class StrengthFactorCategory(StrEnum):
    """Evidence buckets that remain separate from numeric weighting."""

    SUPPORTING = "supporting"
    CHALLENGING = "challenging"
    CONTEXTUAL = "contextual"


class CancellationStatus(StrEnum):
    """Source-aware cancellation result for one Graha."""

    NOT_APPLICABLE = "not_applicable"
    UNSUPPORTED_BY_PROFILE = "unsupported_by_profile"
    CONFIRMED = "confirmed"


class ClassicalStrengthRequest(BaseModel):
    """Birth data used by the transparent strength framework."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )


class StrengthFactor(BaseModel):
    """One auditable, unweighted factor."""

    model_config = ConfigDict(extra="forbid")

    factor_id: str
    category: StrengthFactorCategory
    value: str
    reason: str
    rule_ids: list[str]
    numeric_weight: float | None = None


class SignLordRelationshipSnapshot(BaseModel):
    """Directional relationship from a Graha to the lord of its occupied sign."""

    model_config = ConfigDict(extra="forbid")

    sign_lord: str
    natural_relationship: NaturalRelationship | None = None
    temporary_relationship: TemporaryRelationship | None = None
    compound_relationship: CompoundRelationship | None = None
    self_relationship: bool
    rule_ids: list[str]


class CancellationEvaluation(BaseModel):
    """One explicit cancellation-policy result."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    status: CancellationStatus
    applicable: bool
    cancellation_applied: bool
    source_rule_id: str | None = None
    reason: str
    unsupported_conventions: list[str]


class GrahaStrengthAssessment(BaseModel):
    """Transparent factor inventory for one classical Graha."""

    model_config = ConfigDict(extra="forbid")

    graha: str
    source_longitude: float = Field(ge=0.0, lt=360.0)
    d1_sign_index: int = Field(ge=1, le=12)
    d1_sign: str
    d1_degree_in_sign: float = Field(ge=0.0, lt=30.0)
    d1_house: int = Field(ge=1, le=12)
    dignity: DignityState
    own_sign: bool
    in_exaltation_sign: bool
    at_deep_exaltation_point: bool
    in_debilitation_sign: bool
    at_deep_debilitation_point: bool
    vargottama: bool
    retrograde: bool
    resolved_tendency: ResolvedTendency
    occupied_sign_lord: str
    sign_lord_relationship: SignLordRelationshipSnapshot
    bhinnashtakavarga_bindus_in_occupied_sign: int = Field(ge=0, le=8)
    sarvashtakavarga_bindus_in_occupied_sign: int = Field(ge=0, le=56)
    full_aspects_received: int = Field(ge=0)
    total_fractional_aspect_weight_received: float = Field(ge=0.0)
    conjunctions: list[str]
    factors: list[StrengthFactor]
    cancellation: CancellationEvaluation


class CancellationPolicy(BaseModel):
    """Profile-wide statement of what cancellation rules are enabled."""

    model_config = ConfigDict(extra="forbid")

    policy_id: str
    confirmed_rule_count: int = Field(ge=0)
    cancellation_rules_enabled: bool
    supported_rule_ids: list[str]
    unsupported_conventions: list[str]
    reason: str


class ClassicalStrengthResponse(BaseModel):
    """Unweighted strength-factor response for the seven classical Grahas."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_id: ClassicalProfileId
    calculation_profile: CalculationProfile
    time: NormalizedTime
    coordinates: Coordinates
    ayanamsha_degrees: float
    grahas: list[GrahaStrengthAssessment] = Field(min_length=7, max_length=7)
    cancellation_policy: CancellationPolicy
    excluded_points: list[str]
    weights_applied: bool
    ranking_applied: bool
    cancellations_applied: bool
    metadata: EngineMetadata
    caveats: list[str]
