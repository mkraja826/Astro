"""Schemas for Vimshottari Dasha calculations."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


class DashaDepth(StrEnum):
    """Deepest Vimshottari subdivision requested in the response."""

    PRATYANTARDASHA = "pratyantardasha"
    SOOKSHMA = "sookshma"


class VimshottariRequest(BaseModel):
    """Birth data used to derive the Vimshottari Dasha cycle."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )
    depth: DashaDepth = Field(
        default=DashaDepth.PRATYANTARDASHA,
        description=(
            "Deepest returned subdivision. Use 'sookshma' to include all 6,561 "
            "fourth-level periods; the default preserves the existing three-level response."
        ),
    )


class DashaQueryTime(BaseModel):
    """Local civil timestamp at which the active Dasha chain is requested."""

    model_config = ConfigDict(extra="forbid")

    local_datetime: datetime = Field(
        examples=["2026-07-20T12:00:00"],
        description="Naive local civil time; timezone is supplied separately.",
    )
    timezone: str = Field(
        min_length=1,
        max_length=64,
        examples=["Asia/Kolkata"],
        description="IANA timezone identifier for the requested instant.",
    )
    fold: int | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Selects the first or second occurrence of an ambiguous local time.",
    )

    @field_validator("local_datetime")
    @classmethod
    def require_naive_local_datetime(cls, value: datetime) -> datetime:
        """Reject offset-aware values because timezone is a separate field."""

        if value.tzinfo is not None:
            raise ValueError("local_datetime must not contain a UTC offset")
        return value


class CurrentVimshottariRequest(BaseModel):
    """Birth data and a requested instant for the active Vimshottari chain."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    as_of: DashaQueryTime
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


class SookshmaDashaPeriod(BaseModel):
    """One proportional fourth-level period inside a Pratyantardasha."""

    sequence_number: int = Field(ge=1, le=9)
    lord: DashaLord
    duration_years: float
    start_utc: datetime
    end_utc: datetime
    active_at_birth: bool
    elapsed_at_birth_years: float | None = None
    remaining_at_birth_years: float | None = None


class PratyantardashaPeriod(BaseModel):
    """One proportional third-level period inside an Antardasha."""

    sequence_number: int = Field(ge=1, le=9)
    lord: DashaLord
    duration_years: float
    start_utc: datetime
    end_utc: datetime
    active_at_birth: bool
    elapsed_at_birth_years: float | None = None
    remaining_at_birth_years: float | None = None
    sookshmadashas: list[SookshmaDashaPeriod] | None = None


class AntardashaPeriod(BaseModel):
    """One proportional sub-period inside a Vimshottari Mahadasha."""

    sequence_number: int = Field(ge=1, le=9)
    lord: DashaLord
    duration_years: float
    start_utc: datetime
    end_utc: datetime
    active_at_birth: bool
    elapsed_at_birth_years: float | None = None
    remaining_at_birth_years: float | None = None
    pratyantardashas: list[PratyantardashaPeriod]


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
    antardashas: list[AntardashaPeriod]


class ActiveDashaPeriod(BaseModel):
    """One active Vimshottari level at the requested instant."""

    sequence_number: int = Field(ge=1, le=9)
    lord: DashaLord
    duration_years: float
    start_utc: datetime
    end_utc: datetime
    elapsed_as_of_years: float
    remaining_as_of_years: float
    progress_percent: float = Field(ge=0, le=100)


class VimshottariResponse(BaseModel):
    """Complete birth balance and one 120-year Vimshottari cycle."""

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


class CurrentVimshottariResponse(BaseModel):
    """Only the active Vimshottari chain at one requested instant."""

    request_id: str
    calculation_profile: CalculationProfile
    birth_time: NormalizedTime
    query_time: NormalizedTime
    coordinates: Coordinates
    moon: DashaMoonPosition
    birth_lord: DashaLord
    birth_balance_years: float
    year_length_days: float
    cycle_start_utc: datetime
    cycle_end_utc: datetime
    ayanamsha_degrees: float
    mahadasha: ActiveDashaPeriod
    antardasha: ActiveDashaPeriod
    pratyantardasha: ActiveDashaPeriod
    sookshma: ActiveDashaPeriod
    metadata: EngineMetadata
