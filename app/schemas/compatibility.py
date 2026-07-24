"""Versioned, non-interpretive contracts for dual-chart compatibility facts."""

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.positions import BirthInput, CalculationProfile, EngineMetadata

COMPATIBILITY_FACTS_VERSION = "compatibility_facts_v1"
COMPATIBILITY_PROFILE = "ashtakoota_v1"
ASHTAKOOTA_TOTAL_POINTS = 36
_FINGERPRINT_PATTERN = r"^[0-9a-f]{64}$"


class AshtakootaComponent(StrEnum):
    """The eight traditional compatibility components."""

    VARNA = "varna"
    VASHYA = "vashya"
    TARA = "tara"
    YONI = "yoni"
    GRAHA_MAITRI = "graha_maitri"
    GANA = "gana"
    BHAKOOT = "bhakoot"
    NADI = "nadi"


ASHTAKOOTA_MAXIMUM_POINTS: dict[AshtakootaComponent, int] = {
    AshtakootaComponent.VARNA: 1,
    AshtakootaComponent.VASHYA: 2,
    AshtakootaComponent.TARA: 3,
    AshtakootaComponent.YONI: 4,
    AshtakootaComponent.GRAHA_MAITRI: 5,
    AshtakootaComponent.GANA: 6,
    AshtakootaComponent.BHAKOOT: 7,
    AshtakootaComponent.NADI: 8,
}


class ManglikReferencePoint(StrEnum):
    """Reference points evaluated independently for Kuja/Manglik facts."""

    LAGNA = "lagna"
    MOON = "moon"
    VENUS = "venus"


class DualChartCompatibilityRequest(BaseModel):
    """Two anonymous birth inputs used for compatibility calculation facts."""

    model_config = ConfigDict(extra="forbid")

    subject_birth: BirthInput
    partner_birth: BirthInput
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
    )

    @field_validator("calculation_profile")
    @classmethod
    def require_pinned_profile(cls, value: CalculationProfile) -> CalculationProfile:
        if value is not CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1:
            raise ValueError("compatibility facts require the pinned JPL DE440s profile")
        return value


class CompatibilityNatalFacts(BaseModel):
    """Minimal anonymized natal facts consumed by compatibility evaluators."""

    model_config = ConfigDict(extra="forbid")

    chart_fingerprint: str = Field(pattern=_FINGERPRINT_PATTERN)
    ascendant_sign_index: int = Field(ge=1, le=12)
    moon_sign_index: int = Field(ge=1, le=12)
    moon_nakshatra_index: int = Field(ge=1, le=27)
    moon_nakshatra: str = Field(min_length=1)
    moon_pada: int = Field(ge=1, le=4)
    planet_sign_indices: dict[str, int] = Field(min_length=7)

    @field_validator("planet_sign_indices")
    @classmethod
    def validate_planet_signs(cls, value: dict[str, int]) -> dict[str, int]:
        if any(not name.strip() for name in value):
            raise ValueError("planet names must not be blank")
        if any(sign_index < 1 or sign_index > 12 for sign_index in value.values()):
            raise ValueError("planet sign indices must be between 1 and 12")
        return value


class AshtakootaComponentFact(BaseModel):
    """One raw scored component with its registered source boundary."""

    model_config = ConfigDict(extra="forbid")

    component: AshtakootaComponent
    achieved_points: float = Field(ge=0)
    maximum_points: int = Field(ge=1, le=8)
    rule_ids: list[str] = Field(min_length=1)
    source_kind: str = Field(pattern=r"^(classical|convention)$")
    calculation_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_component_points(self) -> Self:
        expected_maximum = ASHTAKOOTA_MAXIMUM_POINTS[self.component]
        if self.maximum_points != expected_maximum:
            raise ValueError(
                f"{self.component.value} maximum_points must be {expected_maximum}"
            )
        if self.achieved_points > self.maximum_points:
            raise ValueError("achieved_points cannot exceed maximum_points")
        if any(not rule_id.strip() for rule_id in self.rule_ids):
            raise ValueError("rule IDs must not be blank")
        return self


class ManglikFact(BaseModel):
    """A separate Kuja/Manglik calculation fact, never part of the 36-point total."""

    model_config = ConfigDict(extra="forbid")

    reference_point: ManglikReferencePoint
    mars_house: int = Field(ge=1, le=12)
    flagged: bool
    rule_ids: list[str] = Field(min_length=1)
    notes: list[str] = Field(default_factory=list)


class CompatibilityFactsResponse(BaseModel):
    """Complete non-interpretive compatibility fact response."""

    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=1)
    facts_version: str = COMPATIBILITY_FACTS_VERSION
    calculation_profile: CalculationProfile
    compatibility_profile: str = COMPATIBILITY_PROFILE
    subject_fingerprint: str = Field(pattern=_FINGERPRINT_PATTERN)
    partner_fingerprint: str = Field(pattern=_FINGERPRINT_PATTERN)
    pair_fingerprint: str = Field(pattern=_FINGERPRINT_PATTERN)
    subject: CompatibilityNatalFacts
    partner: CompatibilityNatalFacts
    ashtakoota_components: list[AshtakootaComponentFact] = Field(
        min_length=8,
        max_length=8,
    )
    total_achieved_points: float = Field(ge=0, le=ASHTAKOOTA_TOTAL_POINTS)
    total_maximum_points: int = Field(
        default=ASHTAKOOTA_TOTAL_POINTS,
        ge=ASHTAKOOTA_TOTAL_POINTS,
        le=ASHTAKOOTA_TOTAL_POINTS,
    )
    subject_manglik_factors: list[ManglikFact] = Field(default_factory=list)
    partner_manglik_factors: list[ManglikFact] = Field(default_factory=list)
    rule_ids: list[str] = Field(min_length=1)
    metadata: EngineMetadata
    caveats: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_complete_contract(self) -> Self:
        if self.facts_version != COMPATIBILITY_FACTS_VERSION:
            raise ValueError("unsupported compatibility facts version")
        if self.compatibility_profile != COMPATIBILITY_PROFILE:
            raise ValueError("unsupported compatibility profile")
        if (
            self.calculation_profile
            is not CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
        ):
            raise ValueError("compatibility facts require the pinned JPL DE440s profile")
        if self.subject.chart_fingerprint != self.subject_fingerprint:
            raise ValueError("subject fingerprint mismatch")
        if self.partner.chart_fingerprint != self.partner_fingerprint:
            raise ValueError("partner fingerprint mismatch")

        components = [item.component for item in self.ashtakoota_components]
        if len(set(components)) != len(AshtakootaComponent):
            raise ValueError("all eight Ashtakoota components must appear exactly once")
        if set(components) != set(AshtakootaComponent):
            raise ValueError("the Ashtakoota component set is incomplete")

        achieved_total = sum(item.achieved_points for item in self.ashtakoota_components)
        if abs(achieved_total - self.total_achieved_points) > 1e-6:
            raise ValueError("total_achieved_points does not match component facts")
        maximum_total = sum(item.maximum_points for item in self.ashtakoota_components)
        if maximum_total != ASHTAKOOTA_TOTAL_POINTS:
            raise ValueError("Ashtakoota component maximums must total 36")
        return self
