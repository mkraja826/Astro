"""Schemas for evidence-based classical context on active Vimshottari periods."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.classical import ClassicalProfileId
from app.schemas.classical_conditions import DignityState, ResolvedTendency
from app.schemas.classical_relationships import (
    CompoundRelationship,
    NaturalRelationship,
    TemporaryRelationship,
)
from app.schemas.dasha import (
    ActiveDashaPeriod,
    CurrentVimshottariResponse,
    DashaQueryTime,
)
from app.schemas.positions import BirthInput, CalculationProfile


class DashaInterpretationLevel(StrEnum):
    """Vimshottari levels included in the active-chain interpretation."""

    MAHADASHA = "mahadasha"
    ANTARDASHA = "antardasha"
    PRATYANTARDASHA = "pratyantardasha"
    SOOKSHMA = "sookshma"


class DashaEvidenceCategory(StrEnum):
    """Separation used to prevent unweighted facts from becoming predictions."""

    SUPPORTING = "supporting"
    CHALLENGING = "challenging"
    CONTEXTUAL = "contextual"


class ClassicalDashaRequest(BaseModel):
    """Birth data and query instant for classical context on the active chain."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    as_of: DashaQueryTime
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )


class DashaEvidence(BaseModel):
    """One auditable fact attached to an active period lord."""

    model_config = ConfigDict(extra="forbid")

    category: DashaEvidenceCategory
    fact: str
    value: str
    reason: str
    rule_ids: list[str]


class DashaAspectFact(BaseModel):
    """One classical aspect cast by or received at the lord's occupied sign."""

    model_config = ConfigDict(extra="forbid")

    source_graha: str
    target_sign: str
    target_house: int = Field(ge=1, le=12)
    relative_house: int = Field(ge=1, le=12)
    strength_fraction: float = Field(ge=0.0, le=1.0)
    strength_label: str
    is_special_full: bool
    rule_ids: list[str]


class DashaConjunctionFact(BaseModel):
    """Same-sign classical conjunction involving the active period lord."""

    model_config = ConfigDict(extra="forbid")

    other_graha: str
    sign: str
    house: int = Field(ge=1, le=12)
    angular_separation_degrees: float = Field(ge=0.0, le=180.0)
    rule_ids: list[str]


class DashaLevelRelationship(BaseModel):
    """Directed relationship from one active Dasha level lord to another."""

    model_config = ConfigDict(extra="forbid")

    source_level: DashaInterpretationLevel
    source_lord: str
    target_level: DashaInterpretationLevel
    target_lord: str
    available: bool
    target_relative_house: int | None = Field(default=None, ge=1, le=12)
    natural_relationship: NaturalRelationship | None = None
    temporary_relationship: TemporaryRelationship | None = None
    compound_relationship: CompoundRelationship | None = None
    rule_ids: list[str]
    reason: str


class DashaLordInterpretation(BaseModel):
    """Deterministic classical context for one active Vimshottari level."""

    model_config = ConfigDict(extra="forbid")

    level: DashaInterpretationLevel
    period: ActiveDashaPeriod
    lord: str
    classical_condition_available: bool
    source_longitude: float = Field(ge=0.0, lt=360.0)
    d1_sign_index: int = Field(ge=1, le=12)
    d1_sign: str
    d1_house: int = Field(ge=1, le=12)
    owned_signs: list[str]
    owned_houses: list[int]
    dignity: DignityState | None = None
    own_sign: bool | None = None
    in_exaltation_sign: bool | None = None
    in_debilitation_sign: bool | None = None
    vargottama: bool | None = None
    retrograde: bool | None = None
    resolved_tendency: ResolvedTendency | None = None
    same_sign_cooccupants: list[str]
    conjunctions: list[DashaConjunctionFact]
    aspects_cast: list[DashaAspectFact]
    aspects_received: list[DashaAspectFact]
    bhinnashtakavarga_bindus_in_occupied_sign: int | None = Field(
        default=None,
        ge=0,
        le=8,
    )
    sarvashtakavarga_bindus_in_occupied_sign: int = Field(ge=0, le=56)
    karmajiiva_channels: list[str]
    vocation_theme_ids: list[str]
    supporting_evidence: list[DashaEvidence]
    challenging_evidence: list[DashaEvidence]
    contextual_evidence: list[DashaEvidence]
    rule_ids: list[str]


class ClassicalDashaResponse(BaseModel):
    """Active Vimshottari timing plus non-predictive Varahamihira context."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_id: ClassicalProfileId
    calculation_profile: CalculationProfile
    timing: CurrentVimshottariResponse
    levels: list[DashaLordInterpretation] = Field(min_length=4, max_length=4)
    relationships_between_levels: list[DashaLevelRelationship] = Field(
        min_length=12,
        max_length=12,
    )
    unique_lords: list[str]
    repeated_lords: list[str]
    interpretation_mode: str
    prediction_applied: bool
    cancellations_applied: bool
    strength_weighting_applied: bool
    caveats: list[str]
