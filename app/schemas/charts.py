"""Schemas for divisional chart calculations."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from app.schemas.positions import (
    BirthInput,
    CalculationProfile,
    Coordinates,
    EngineMetadata,
    NormalizedTime,
)


class ChartType(StrEnum):
    """Divisional charts supported by the public API."""

    D1_RASI = "d1_rasi"
    D9_NAVAMSA = "d9_navamsa"


class ChartRequest(BaseModel):
    """Input for a divisional chart calculation."""

    model_config = ConfigDict(extra="forbid")
    birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )


class ChartPoint(BaseModel):
    """One calculated point in a divisional chart."""

    name: str
    kind: str
    source_longitude: float
    chart_longitude: float
    sign_index: int
    sign: str
    degree_in_sign: float
    house: int
    retrograde: bool | None = None


class SouthIndianSignCell(BaseModel):
    """One fixed-sign cell in the South Indian chart layout."""

    sign_index: int
    sign: str
    grid_row: int
    grid_column: int
    house_from_lagna: int
    occupants: list[str]


class ChartResponse(BaseModel):
    """A D1 or D9 chart with South Indian sign-grid metadata."""

    request_id: str
    chart_type: ChartType
    division: int
    calculation_profile: CalculationProfile
    time: NormalizedTime
    coordinates: Coordinates
    ayanamsha_degrees: float
    ascendant: ChartPoint
    points: list[ChartPoint]
    signs: list[SouthIndianSignCell]
    metadata: EngineMetadata
