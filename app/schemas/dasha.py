"""Schemas for Vimshottari Dasha calculations."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.positions import (
    BirthInput,
    CalculationProfile,
    Coordinates,
    EngineMetadata,
    NormalizedTime,
)


class DashaLord(StrEnum):
    """Traditional Vimshottari planetary lords in canonical sequence."""

    KETU = "ketu"
    VENUS = "venus"
    SUN = "sun"
    MOON = "moon"
    MARS = "mars"
    RAHU = "rahu"
    JUPITER = "jupiter"
    SATURN = "saturn"
    MERCURY = "mercury"


class VimshottariRequest(BaseModel):
    """Birth data used to derive the Vimshottari Mahadasha cycle."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )


class DashaMoonPosition(BaseModel):
    """Sidereal Moon position controlling the birth Dasha balance."""

    longitude: float
    nakshatra_index: int
    nakshatra: str
    pada: int
    progress_percent: float


class MahadashaPeriod(BaseModel):
    """One major Vimshottari period on the canonical UTC timeline."""

    sequence_number: int = Field(ge=1, le=9)
    lord: DashaLord
    duration_years: float
    start_utc: datetime
    end_utc: datetime
    active_at_birth: bool
    elapsed_at_birth_years: float | None = None
    remaining_at_birth_years: float | None = None


class VimshottariResponse(BaseModel):
    """Complete birth balance and one 120-year Mahadasha cycle."""

    request_id: str
    calculation_profile: CalculationProfile
    time: NormalizedTime
    coordinates: Coordinates
    moon: DashaMoonPosition
    birth_lord: DashaLord
    birth_balance_years: float
    cycle_years: float
    year_length_days: float
    ayanamsha_degrees: float
    mahadashas: list[MahadashaPeriod]
    metadata: EngineMetadata
