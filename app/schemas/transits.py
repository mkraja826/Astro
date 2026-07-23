"""Schemas for deterministic, non-interpretive transit snapshots."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.dasha import DashaQueryTime
from app.schemas.positions import BirthInput, CalculationProfile, PositionsResponse


class TransitSnapshotRequest(BaseModel):
    """Natal coordinates and the civil instant at which transits are calculated."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    as_of: DashaQueryTime
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
    )


class TransitReferenceRelation(BaseModel):
    """Whole-sign geometry between one transit point and natal references."""

    model_config = ConfigDict(extra="forbid")

    body: str
    natal_sign_index: int = Field(ge=1, le=12)
    transit_sign_index: int = Field(ge=1, le=12)
    whole_sign_distance_from_natal_position: int = Field(ge=1, le=12)
    whole_sign_house_from_natal_ascendant: int = Field(ge=1, le=12)
    whole_sign_house_from_natal_moon: int = Field(ge=1, le=12)


class TransitSnapshotResponse(BaseModel):
    """Raw natal/transit positions plus deterministic reference-frame geometry."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    calculation_profile: CalculationProfile
    natal: PositionsResponse
    transit: PositionsResponse
    relations: list[TransitReferenceRelation] = Field(min_length=9, max_length=9)
    interpretation_applied: bool
    timing_window_applied: bool
    caveats: list[str]
