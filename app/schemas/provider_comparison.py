"""Schemas for side-by-side astronomical provider validation."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.positions import BirthInput, CalculationProfile, EngineMetadata


class ProviderComparisonRequest(BaseModel):
    """One birth input and explicit migration tolerances."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    longitude_tolerance_degrees: float = Field(default=0.05, ge=0.0, le=5.0)
    ascendant_tolerance_degrees: float = Field(default=0.10, ge=0.0, le=5.0)
    ayanamsha_tolerance_degrees: float = Field(default=0.02, ge=0.0, le=5.0)


class ScalarAngularComparison(BaseModel):
    """Comparison of one circular angular result."""

    swiss_value: float
    skyfield_value: float
    signed_difference_degrees: float
    absolute_difference_degrees: float
    tolerance_degrees: float
    matched: bool


class ProviderPointComparison(BaseModel):
    """One planet or node compared across the two providers."""

    body: str
    longitude: ScalarAngularComparison
    swiss_sign_index: int
    skyfield_sign_index: int
    sign_matched: bool
    swiss_retrograde: bool
    skyfield_retrograde: bool
    retrograde_matched: bool


class ProviderComparisonResponse(BaseModel):
    """Transparent migration report for Swiss versus Skyfield/JPL."""

    request_id: str
    swiss_profile: CalculationProfile
    skyfield_profile: CalculationProfile
    swiss_metadata: EngineMetadata
    skyfield_metadata: EngineMetadata
    ayanamsha: ScalarAngularComparison
    ascendant: ScalarAngularComparison
    points: list[ProviderPointComparison]
    compared_point_count: int
    longitude_match_count: int
    sign_match_count: int
    retrograde_match_count: int
    passed: bool
    production_default_changed: bool
    caveats: list[str]
