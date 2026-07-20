"""Schemas for Varahamihira aspect and house-influence evaluation."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.classical import ClassicalProfileId
from app.schemas.positions import (
    BirthInput,
    CalculationProfile,
    Coordinates,
    EngineMetadata,
    NormalizedTime,
)


class AspectStrengthLabel(StrEnum):
    """Named aspect strengths defined by Bṛhat Jātaka 2.13."""

    QUARTER = "quarter"
    HALF = "half"
    THREE_QUARTERS = "three_quarters"
    FULL = "full"


class ClassicalAspectsRequest(BaseModel):
    """Birth data used by the Varahamihira aspect evaluator."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )


class AspectRay(BaseModel):
    """One directed whole-sign Graha aspect with explicit strength."""

    source_graha: str
    source_sign_index: int = Field(ge=1, le=12)
    source_sign: str
    source_house: int = Field(ge=1, le=12)
    relative_house: int = Field(ge=1, le=12)
    target_sign_index: int = Field(ge=1, le=12)
    target_sign: str
    target_house: int = Field(ge=1, le=12)
    strength_fraction: float = Field(ge=0.0, le=1.0)
    strength_label: AspectStrengthLabel
    is_special_full: bool
    target_grahas: list[str]
    rule_ids: list[str]
    reason: str


class ConjunctionRecord(BaseModel):
    """One same-sign conjunction pair among the seven classical Grahas."""

    grahas: list[str] = Field(min_length=2, max_length=2)
    sign_index: int = Field(ge=1, le=12)
    sign: str
    house: int = Field(ge=1, le=12)
    angular_separation_degrees: float = Field(ge=0.0, le=180.0)
    rule_ids: list[str]
    reason: str


class HouseAspectInfluence(BaseModel):
    """One Graha aspect received by a house."""

    source_graha: str
    relative_house: int = Field(ge=1, le=12)
    strength_fraction: float = Field(ge=0.0, le=1.0)
    strength_label: AspectStrengthLabel
    is_special_full: bool
    rule_ids: list[str]


class HouseInfluence(BaseModel):
    """Deterministic occupants, lord placement, and aspects for one whole-sign house."""

    house: int = Field(ge=1, le=12)
    sign_index: int = Field(ge=1, le=12)
    sign: str
    contains_ascendant: bool
    lord: str
    lord_placement_sign: str
    lord_placement_house: int = Field(ge=1, le=12)
    occupants: list[str]
    conjunction_pairs: list[list[str]]
    aspects_received: list[HouseAspectInfluence]
    total_aspect_weight: float = Field(ge=0.0)
    full_aspect_sources: list[str]
    rule_ids: list[str]
    reason: str


class ClassicalAspectsResponse(BaseModel):
    """Complete non-predictive Varahamihira aspect and house-influence result."""

    request_id: str
    profile_id: ClassicalProfileId
    calculation_profile: CalculationProfile
    time: NormalizedTime
    coordinates: Coordinates
    ayanamsha_degrees: float
    ascendant_sign_index: int = Field(ge=1, le=12)
    ascendant_sign: str
    aspects: list[AspectRay]
    conjunctions: list[ConjunctionRecord]
    houses: list[HouseInfluence]
    excluded_points: list[str]
    metadata: EngineMetadata
    caveats: list[str]
