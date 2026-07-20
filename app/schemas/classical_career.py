"""Schemas for deterministic Varahamihira Karmājīva career analysis."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.classical import ClassicalProfileId
from app.schemas.classical_conditions import DignityState
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


class CareerReferencePoint(StrEnum):
    """Reference points used by Bṛhat Jātaka Chapter 10."""

    LAGNA = "lagna"
    MOON = "moon"
    SUN = "sun"


class ClassicalCareerRequest(BaseModel):
    """Birth data used by the Karmājīva evaluator."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )


class CareerEvidence(BaseModel):
    """One auditable career fact linked to a registered classical rule."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str
    condition: str
    value: str
    reason: str


class IncomeSourceIndication(BaseModel):
    """Chapter 10.1 source-of-wealth indication from a tenth-house occupant."""

    model_config = ConfigDict(extra="forbid")

    graha: str
    source_id: str
    label: str
    classical_relation: str
    rule_ids: list[str]


class VocationTheme(BaseModel):
    """Modernized but source-traceable vocation theme for one indicator Graha."""

    model_config = ConfigDict(extra="forbid")

    theme_id: str
    label: str
    classical_terms: list[str]
    modern_examples: list[str]
    rule_ids: list[str]


class CareerAspectFact(BaseModel):
    """One classical aspect reaching a channel's tenth sign."""

    model_config = ConfigDict(extra="forbid")

    source_graha: str
    relative_house: int
    strength_fraction: float
    strength_label: str
    is_special_full: bool
    rule_ids: list[str]


class IndicatorConditionSnapshot(BaseModel):
    """Unweighted condition facts for a Karmājīva indicator Graha."""

    model_config = ConfigDict(extra="forbid")

    graha: str
    d1_sign: str
    d1_house: int
    d1_degree_in_sign: float
    dignity: DignityState
    own_sign: bool
    in_exaltation_sign: bool
    in_debilitation_sign: bool
    vargottama: bool
    retrograde: bool
    conjunctions: list[str]


class CareerRelationshipFact(BaseModel):
    """Relationship from a channel's tenth lord to its derived indicator."""

    model_config = ConfigDict(extra="forbid")

    tenth_lord: str
    indicator_graha: str
    available: bool
    target_relative_house: int | None = Field(default=None, ge=1, le=12)
    natural_relationship: NaturalRelationship | None = None
    temporary_relationship: TemporaryRelationship | None = None
    compound_relationship: CompoundRelationship | None = None
    rule_ids: list[str]
    reason: str


class CareerChannel(BaseModel):
    """One Karmājīva derivation from Lagna, Moon, or Sun."""

    model_config = ConfigDict(extra="forbid")

    reference_point: CareerReferencePoint
    reference_sign_index: int
    reference_sign: str
    tenth_sign_index: int
    tenth_sign: str
    tenth_house_occupants: list[str]
    income_source_indications: list[IncomeSourceIndication]
    tenth_lord: str
    tenth_lord_d1_sign: str
    tenth_lord_d1_house: int
    tenth_lord_d1_degree_in_sign: float
    tenth_lord_d9_sign_index: int
    tenth_lord_d9_sign: str
    tenth_lord_d9_degree_in_sign: float
    karmājīva_indicator_graha: str
    tenth_lord_to_indicator_relationship: CareerRelationshipFact
    vocation_themes: list[VocationTheme]
    indicator_condition: IndicatorConditionSnapshot
    aspects_to_tenth_sign: list[CareerAspectFact]
    evidence: list[CareerEvidence]


class CareerCandidate(BaseModel):
    """Aggregated unweighted indicator repeated across one or more channels."""

    model_config = ConfigDict(extra="forbid")

    graha: str
    derived_from: list[CareerReferencePoint]
    repetition_count: int
    vocation_themes: list[VocationTheme]
    indicator_condition: IndicatorConditionSnapshot
    rule_ids: list[str]


class ClassicalCareerResponse(BaseModel):
    """Complete non-exclusive Karmājīva career analysis."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_id: ClassicalProfileId
    calculation_profile: CalculationProfile
    time: NormalizedTime
    coordinates: Coordinates
    ayanamsha_degrees: float
    channels: list[CareerChannel]
    candidates: list[CareerCandidate]
    primary_indicator: str | None = None
    ranking_applied: bool
    excluded_points: list[str]
    metadata: EngineMetadata
    caveats: list[str]
