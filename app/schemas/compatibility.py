"""Versioned, non-interpretive contracts for dual-chart compatibility facts."""

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.positions import BirthInput, CalculationProfile, EngineMetadata

COMPATIBILITY_FACTS_VERSION = "compatibility_facts_v2"
COMPATIBILITY_PROFILE = "ashtakoota_v2"
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


class TraditionalCompatibilityRole(StrEnum):
    """Optional roles required only by directional convention tables."""

    UNSPECIFIED = "unspecified"
    BRIDE = "bride"
    GROOM = "groom"


class ComponentEvaluationStatus(StrEnum):
    """Whether a component produced points or explicitly abstained."""

    EVALUATED = "evaluated"
    ABSTAINED = "abstained"


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
    subject_role: TraditionalCompatibilityRole = TraditionalCompatibilityRole.UNSPECIFIED
    partner_role: TraditionalCompatibilityRole = TraditionalCompatibilityRole.UNSPECIFIED
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
    )

    @field_validator("calculation_profile")
    @classmethod
    def require_pinned_profile(cls, value: CalculationProfile) -> CalculationProfile:
        if value is not CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1:
            raise ValueError("compatibility facts require the pinned JPL DE440s profile")
        return value

    @model_validator(mode="after")
    def validate_traditional_roles(self) -> Self:
        subject_unspecified = self.subject_role is TraditionalCompatibilityRole.UNSPECIFIED
        partner_unspecified = self.partner_role is TraditionalCompatibilityRole.UNSPECIFIED
        if subject_unspecified != partner_unspecified:
            raise ValueError("traditional roles must be supplied for both people or neither")
        if not subject_unspecified and self.subject_role is self.partner_role:
            raise ValueError("traditional roles must be one bride and one groom")
        return self


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
    """One raw component result or explicit abstention with its rule boundary."""

    model_config = ConfigDict(extra="forbid")

    component: AshtakootaComponent
    status: ComponentEvaluationStatus = ComponentEvaluationStatus.EVALUATED
    achieved_points: float | None = Field(default=None, ge=0)
    maximum_points: int = Field(ge=1, le=8)
    rule_ids: list[str] = Field(min_length=1)
    source_kind: str = Field(pattern=r"^(classical|convention)$")
    abstention_reason: str | None = None
    calculation_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_component_result(self) -> Self:
        expected_maximum = ASHTAKOOTA_MAXIMUM_POINTS[self.component]
        if self.maximum_points != expected_maximum:
            raise ValueError(
                f"{self.component.value} maximum_points must be {expected_maximum}"
            )
        if any(not rule_id.strip() for rule_id in self.rule_ids):
            raise ValueError("rule IDs must not be blank")

        if self.status is ComponentEvaluationStatus.EVALUATED:
            if self.achieved_points is None:
                raise ValueError("evaluated components require achieved_points")
            if self.achieved_points > self.maximum_points:
                raise ValueError("achieved_points cannot exceed maximum_points")
            if self.abstention_reason is not None:
                raise ValueError("evaluated components cannot include an abstention reason")
        else:
            if self.achieved_points is not None:
                raise ValueError("abstained components cannot include achieved_points")
            if self.abstention_reason is None or not self.abstention_reason.strip():
                raise ValueError("abstained components require an abstention reason")
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
    evaluated_maximum_points: int = Field(
        default=ASHTAKOOTA_TOTAL_POINTS,
        ge=0,
        le=ASHTAKOOTA_TOTAL_POINTS,
    )
    total_maximum_points: int = Field(
        default=ASHTAKOOTA_TOTAL_POINTS,
        ge=ASHTAKOOTA_TOTAL_POINTS,
        le=ASHTAKOOTA_TOTAL_POINTS,
    )
    complete_36_point_evaluation: bool = True
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

        evaluated = [
            item
            for item in self.ashtakoota_components
            if item.status is ComponentEvaluationStatus.EVALUATED
        ]
        achieved_total = sum(item.achieved_points or 0.0 for item in evaluated)
        if abs(achieved_total - self.total_achieved_points) > 1e-6:
            raise ValueError("total_achieved_points does not match evaluated component facts")
        evaluated_maximum = sum(item.maximum_points for item in evaluated)
        if evaluated_maximum != self.evaluated_maximum_points:
            raise ValueError(
                "evaluated_maximum_points does not match evaluated component facts"
            )

        maximum_total = sum(item.maximum_points for item in self.ashtakoota_components)
        if maximum_total != ASHTAKOOTA_TOTAL_POINTS:
            raise ValueError("Ashtakoota component maximums must total 36")
        expected_complete = evaluated_maximum == ASHTAKOOTA_TOTAL_POINTS
        if self.complete_36_point_evaluation is not expected_complete:
            raise ValueError(
                "complete_36_point_evaluation does not match evaluated component coverage"
            )
        return self
