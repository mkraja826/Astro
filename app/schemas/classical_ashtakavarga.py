"""Schemas for deterministic Varahamihira Ashtakavarga calculations."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.classical import ClassicalProfileId
from app.schemas.positions import (
    BirthInput,
    CalculationProfile,
    Coordinates,
    EngineMetadata,
    NormalizedTime,
)


class AshtakavargaRequest(BaseModel):
    """Input used by the Chapter 9 Ashtakavarga evaluator."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )


class AshtakavargaContributorPosition(BaseModel):
    """Natal source position used as one of the eight contributors."""

    contributor: str
    sign_index: int = Field(ge=1, le=12)
    sign: str
    source_longitude: float = Field(ge=0, lt=360)


class ContributorBinduRow(BaseModel):
    """One contributor row inside a planetary Bhinnashtakavarga."""

    contributor: str
    source_sign_index: int = Field(ge=1, le=12)
    source_sign: str
    favorable_relative_houses: list[int]
    bindu_sign_indices: list[int]
    bindu_signs: list[str]
    bindus_by_sign: list[int] = Field(min_length=12, max_length=12)
    total_bindus: int = Field(ge=0, le=12)
    rule_ids: list[str]


class BhinnashtakavargaRecord(BaseModel):
    """Raw eight-contributor bindu array for one classical Graha."""

    graha: str
    verse_reference: str
    contributor_rows: list[ContributorBinduRow] = Field(min_length=8, max_length=8)
    bindus_by_sign: list[int] = Field(min_length=12, max_length=12)
    rekhas_by_sign: list[int] = Field(min_length=12, max_length=12)
    total_bindus: int
    expected_total_bindus: int
    total_valid: bool
    rule_ids: list[str]


class AshtakavargaSignSummary(BaseModel):
    """Planetary and aggregate bindus for one zodiac sign."""

    sign_index: int = Field(ge=1, le=12)
    sign: str
    house_from_lagna: int = Field(ge=1, le=12)
    bindus_by_graha: dict[str, int]
    sarvashtakavarga_bindus: int = Field(ge=0, le=56)


class SarvashtakavargaRecord(BaseModel):
    """Sign-wise sum of the seven raw Bhinnashtakavarga arrays."""

    bindus_by_sign: list[int] = Field(min_length=12, max_length=12)
    total_bindus: int
    expected_total_bindus: int
    total_valid: bool
    signs: list[AshtakavargaSignSummary] = Field(min_length=12, max_length=12)
    rule_ids: list[str]


class AshtakavargaResponse(BaseModel):
    """Complete raw Chapter 9 Bhinnashtakavarga and Sarvashtakavarga result."""

    request_id: str
    profile_id: ClassicalProfileId
    calculation_profile: CalculationProfile
    time: NormalizedTime
    coordinates: Coordinates
    ayanamsha_degrees: float
    ascendant_sign_index: int = Field(ge=1, le=12)
    ascendant_sign: str
    contributor_positions: list[AshtakavargaContributorPosition] = Field(
        min_length=8,
        max_length=8,
    )
    bhinnashtakavargas: list[BhinnashtakavargaRecord] = Field(
        min_length=7,
        max_length=7,
    )
    sarvashtakavarga: SarvashtakavargaRecord
    excluded_points: list[str]
    metadata: EngineMetadata
    caveats: list[str]
