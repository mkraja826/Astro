"""Schemas for the separately versioned controlled strength-weighting convention."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.classical import ClassicalProfileId
from app.schemas.classical_career import ClassicalCareerResponse
from app.schemas.classical_dasha import ClassicalDashaResponse, DashaInterpretationLevel
from app.schemas.classical_strength import ClassicalStrengthResponse
from app.schemas.dasha import DashaQueryTime
from app.schemas.positions import (
    BirthInput,
    CalculationProfile,
    Coordinates,
    EngineMetadata,
    NormalizedTime,
)


class WeightingProfileId(StrEnum):
    """Non-textual weighting conventions available to the API."""

    TRANSPARENT_STRENGTH_WEIGHTING_V1 = "transparent_strength_weighting_v1"


class WeightingSourceStatus(StrEnum):
    """Distinguish API convention from a classical textual rule."""

    API_CONVENTION_NOT_TEXTUAL_RULE = "api_convention_not_textual_rule"


class ClassicalWeightedStrengthRequest(BaseModel):
    """Birth data and the explicitly selected weighting convention."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )
    weighting_profile: WeightingProfileId = (
        WeightingProfileId.TRANSPARENT_STRENGTH_WEIGHTING_V1
    )


class ClassicalWeightedDashaRequest(BaseModel):
    """Active-chain query with an explicitly selected weighting convention."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    as_of: DashaQueryTime
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )
    weighting_profile: WeightingProfileId = (
        WeightingProfileId.TRANSPARENT_STRENGTH_WEIGHTING_V1
    )


class WeightingComponent(BaseModel):
    """One transparent numeric contribution produced from a raw classical fact."""

    model_config = ConfigDict(extra="forbid")

    component_id: str
    raw_value: str
    contribution: float
    formula: str
    classical_rule_ids: list[str]
    convention_profile: WeightingProfileId
    reason: str


class CompactStrengthSnapshot(BaseModel):
    """Small weighting result embedded into other evaluators."""

    model_config = ConfigDict(extra="forbid")

    graha: str
    available: bool
    weighting_profile: WeightingProfileId | None = None
    total_score: float | None = None
    rank: int | None = Field(default=None, ge=1, le=7)
    tied_with: list[str]
    reason: str


class WeightedGrahaStrength(BaseModel):
    """Complete controlled score for one of the seven classical Grahas."""

    model_config = ConfigDict(extra="forbid")

    graha: str
    total_score: float
    rank: int = Field(ge=1, le=7)
    tied_with: list[str]
    components: list[WeightingComponent]
    neutral_context_factor_ids: list[str]
    cancellation_adjustment: float
    cancellation_applied: bool


class WeightedCareerChannelSummary(BaseModel):
    """Controlled strength summaries attached to one Karmājīva channel."""

    model_config = ConfigDict(extra="forbid")

    reference_point: str
    tenth_lord: CompactStrengthSnapshot
    indicator_graha: CompactStrengthSnapshot


class WeightedCareerCandidateSummary(BaseModel):
    """Controlled strength summary for one repeated career indicator candidate."""

    model_config = ConfigDict(extra="forbid")

    graha: str
    repetition_count: int = Field(ge=1, le=3)
    strength: CompactStrengthSnapshot


class WeightedDashaLevelSummary(BaseModel):
    """Controlled strength summary for one active Vimshottari level lord."""

    model_config = ConfigDict(extra="forbid")

    level: DashaInterpretationLevel
    lord: str
    strength: CompactStrengthSnapshot


class WeightingProfileResponse(BaseModel):
    """Immutable metadata and formulas for one API weighting convention."""

    model_config = ConfigDict(extra="forbid")

    weighting_profile: WeightingProfileId
    version: str
    source_status: WeightingSourceStatus
    classical_profile_dependency: ClassicalProfileId
    calculation_profile_dependency: CalculationProfile
    dignity_weights: dict[str, float]
    deep_dignity_weights: dict[str, float]
    vargottama_weight: float
    relationship_weights: dict[str, float]
    bhinnashtakavarga_formula: str
    sarvashtakavarga_formula: str
    score_neutral_factors: list[str]
    cancellation_adjustment_enabled: bool
    golden_fixture_ids: list[str]
    golden_fixture_count: int = Field(ge=1)
    external_reference_validation_complete: bool
    caveats: list[str]


class ClassicalWeightedStrengthResponse(BaseModel):
    """Raw evidence plus transparent controlled scores and ranking."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_id: ClassicalProfileId
    weighting_profile: WeightingProfileId
    weighting_version: str
    calculation_profile: CalculationProfile
    time: NormalizedTime
    coordinates: Coordinates
    ayanamsha_degrees: float
    raw_strength: ClassicalStrengthResponse
    weighted_grahas: list[WeightedGrahaStrength] = Field(min_length=7, max_length=7)
    highest_ranked_grahas: list[str]
    excluded_points: list[str]
    weights_applied: bool
    ranking_applied: bool
    cancellations_applied: bool
    prediction_applied: bool
    metadata: EngineMetadata
    caveats: list[str]


class ClassicalWeightedCareerResponse(BaseModel):
    """Original career evidence plus controlled strength summaries."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_id: ClassicalProfileId
    weighting_profile: WeightingProfileId
    career: ClassicalCareerResponse
    weighted_strength: ClassicalWeightedStrengthResponse
    channel_strengths: list[WeightedCareerChannelSummary] = Field(
        min_length=3,
        max_length=3,
    )
    candidate_strengths: list[WeightedCareerCandidateSummary]
    career_ranking_applied: bool
    prediction_applied: bool
    caveats: list[str]


class ClassicalWeightedDashaResponse(BaseModel):
    """Original active-chain evidence plus controlled lord-strength summaries."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_id: ClassicalProfileId
    weighting_profile: WeightingProfileId
    dasha: ClassicalDashaResponse
    weighted_strength: ClassicalWeightedStrengthResponse
    level_strengths: list[WeightedDashaLevelSummary] = Field(min_length=4, max_length=4)
    event_prediction_applied: bool
    cancellations_applied: bool
    caveats: list[str]
