"""Schemas for sidereal planetary-position calculations."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CalculationProfile(StrEnum):
    """Immutable calculation profiles accepted by the public API.

    The two older values remain accepted as compatibility aliases. All three
    values are calculated by the Skyfield/JPL DE440s production provider.
    """

    SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1 = (
        "south_indian_drik_lahiri_jpl_de440s_v1"
    )
    SOUTH_INDIAN_DRIK_LAHIRI_V1 = "south_indian_drik_lahiri_v1"
    SOUTH_INDIAN_DRIK_LAHIRI_SKYFIELD_DE440S_V1 = (
        "south_indian_drik_lahiri_skyfield_de440s_v1"
    )


class BirthInput(BaseModel):
    """Civil birth time and geographic location supplied by the caller."""

    model_config = ConfigDict(extra="forbid")

    local_datetime: datetime = Field(
        examples=["1998-10-26T10:28:00"],
        description="Naive local civil time; timezone is supplied separately.",
    )
    timezone: str = Field(
        min_length=1,
        max_length=64,
        examples=["Asia/Kolkata"],
        description="IANA timezone identifier.",
    )
    latitude: float = Field(ge=-90, le=90, examples=[16.575])
    longitude: float = Field(ge=-180, le=180, examples=[79.312])
    altitude_meters: float = Field(default=0, ge=-500, le=10000)
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


class PositionsRequest(BaseModel):
    """Request contract for astronomical calculations."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
    )


class ZodiacPosition(BaseModel):
    """A point expressed in the sidereal zodiac."""

    longitude: float
    sign_index: int
    sign: str
    degree_in_sign: float
    nakshatra_index: int
    nakshatra: str
    pada: int
    whole_sign_house: int


class PlanetPosition(ZodiacPosition):
    """A planet or lunar node with motion metadata."""

    body: str
    latitude: float
    distance_au: float | None
    speed_longitude: float
    retrograde: bool


class NormalizedTime(BaseModel):
    """Reproducible time-conversion details used by the engine."""

    local_datetime: datetime
    utc_datetime: datetime
    timezone: str
    fold: int
    julian_day_ut: float


class Coordinates(BaseModel):
    """Validated observer coordinates."""

    latitude: float
    longitude: float
    altitude_meters: float


class EngineMetadata(BaseModel):
    """Calculation provenance returned with every result."""

    engine: str
    engine_version: str
    astronomical_provider: str = "skyfield_jpl"
    provider_version: str | None = None
    ephemeris_model: str | None = None
    swiss_ephemeris_version: str | None = Field(
        default=None,
        deprecated=True,
        description="Deprecated compatibility field; always null in the JPL-only engine.",
    )
    zodiac: str
    ayanamsha: str
    node_type: str
    house_system: str
    ephemeris_sources: list[str]


class PositionsResponse(BaseModel):
    """Complete response from ``POST /v1/positions``."""

    request_id: str
    calculation_profile: CalculationProfile
    time: NormalizedTime
    coordinates: Coordinates
    ayanamsha_degrees: float
    ascendant: ZodiacPosition
    planets: list[PlanetPosition]
    metadata: EngineMetadata
