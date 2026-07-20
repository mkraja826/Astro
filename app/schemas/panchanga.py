"""Schemas for daily South Indian Panchanga calculations."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.positions import CalculationProfile, Coordinates, EngineMetadata


class PanchangaLocation(BaseModel):
    """Local calendar date and observer coordinates."""

    model_config = ConfigDict(extra="forbid")

    local_date: date = Field(examples=["2026-07-20"])
    timezone: str = Field(min_length=1, max_length=64, examples=["Asia/Kolkata"])
    latitude: float = Field(ge=-90, le=90, examples=[16.575])
    longitude: float = Field(ge=-180, le=180, examples=[79.312])
    altitude_meters: float = Field(default=0, ge=-500, le=10000)


class PanchangaRequest(BaseModel):
    """Request contract for a sunrise-based daily Panchanga."""

    model_config = ConfigDict(extra="forbid")

    location: PanchangaLocation
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )

    @field_validator("calculation_profile")
    @classmethod
    def require_supported_panchanga_profile(
        cls,
        value: CalculationProfile,
    ) -> CalculationProfile:
        """Reject profiles whose sunrise implementation has not been migrated yet."""

        if value != CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1:
            raise ValueError(
                "Skyfield/JPL Panchanga is not implemented yet; use "
                "south_indian_drik_lahiri_v1 for this endpoint"
            )
        return value


class SolarTimes(BaseModel):
    """Hindu sunrise and sunset for the requested local date."""

    sunrise_local: datetime
    sunrise_utc: datetime
    sunset_local: datetime
    sunset_utc: datetime
    method: str


class PanchangaElement(BaseModel):
    """Indexed Panchanga element evaluated at sunrise."""

    index: int
    name: str
    progress_percent: float


class TithiElement(PanchangaElement):
    """Lunar day with Paksha classification."""

    paksha: str


class NakshatraElement(PanchangaElement):
    """Lunar mansion and quarter."""

    pada: int


class KaranaElement(PanchangaElement):
    """Half-tithi division."""

    half_tithi_index: int


class PanchangaResponse(BaseModel):
    """Daily Panchanga evaluated at local sunrise."""

    request_id: str
    calculation_profile: CalculationProfile
    local_date: date
    timezone: str
    coordinates: Coordinates
    solar_times: SolarTimes
    vara: PanchangaElement
    tithi: TithiElement
    nakshatra: NakshatraElement
    yoga: PanchangaElement
    karana: KaranaElement
    evaluated_at_local: datetime
    evaluated_at_utc: datetime
    ayanamsha_degrees: float
    metadata: EngineMetadata
