"""Schemas for deterministic Varahamihira planetary relationships."""

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


class NaturalRelationship(StrEnum):
    """Directional permanent relationship defined in Brihat Jataka 2.16-2.17."""

    FRIEND = "friend"
    NEUTRAL = "neutral"
    ENEMY = "enemy"


class TemporaryRelationship(StrEnum):
    """Mutual relationship produced by natal sign separation."""

    FRIEND = "friend"
    ENEMY = "enemy"


class CompoundRelationship(StrEnum):
    """Fivefold result obtained by combining natural and temporary relations."""

    GREAT_FRIEND = "great_friend"
    FRIEND = "friend"
    NEUTRAL = "neutral"
    ENEMY = "enemy"
    GREAT_ENEMY = "great_enemy"


class ClassicalRelationshipsRequest(BaseModel):
    """Birth data used to evaluate the seven classical Grahas."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )


class RelationshipGrahaPosition(BaseModel):
    """Natal position used by the temporary-relationship calculation."""

    model_config = ConfigDict(extra="forbid")

    graha: str
    source_longitude: float = Field(ge=0.0, lt=360.0)
    sign_index: int = Field(ge=1, le=12)
    sign: str
    house: int = Field(ge=1, le=12)


class DirectedGrahaRelationship(BaseModel):
    """One source-to-target natural, temporary, and compound relationship."""

    model_config = ConfigDict(extra="forbid")

    source_graha: str
    target_graha: str
    source_sign_index: int = Field(ge=1, le=12)
    source_sign: str
    target_sign_index: int = Field(ge=1, le=12)
    target_sign: str
    target_relative_house: int = Field(ge=1, le=12)
    natural_relationship: NaturalRelationship
    temporary_relationship: TemporaryRelationship
    compound_relationship: CompoundRelationship
    rule_ids: list[str]
    reason: str


class MutualGrahaPair(BaseModel):
    """One unordered pair showing symmetry and both directed compound results."""

    model_config = ConfigDict(extra="forbid")

    graha_a: str
    graha_b: str
    a_relative_house_from_b: int = Field(ge=1, le=12)
    b_relative_house_from_a: int = Field(ge=1, le=12)
    temporary_relationship: TemporaryRelationship
    a_to_b_compound: CompoundRelationship
    b_to_a_compound: CompoundRelationship
    rule_ids: list[str]


class ClassicalRelationshipsResponse(BaseModel):
    """Complete relationship matrix for the seven classical Grahas."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_id: ClassicalProfileId
    calculation_profile: CalculationProfile
    time: NormalizedTime
    coordinates: Coordinates
    ayanamsha_degrees: float
    positions: list[RelationshipGrahaPosition] = Field(min_length=7, max_length=7)
    directed_relationships: list[DirectedGrahaRelationship] = Field(
        min_length=42,
        max_length=42,
    )
    mutual_pairs: list[MutualGrahaPair] = Field(min_length=21, max_length=21)
    excluded_points: list[str]
    scoring_applied: bool
    metadata: EngineMetadata
    caveats: list[str]
