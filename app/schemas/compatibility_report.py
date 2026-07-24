"""Versioned response contract for interpreted Kundli compatibility reports."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.compatibility import CompatibilityFactsResponse


class PartnershipOutlookIndex(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: str = Field(pattern=r"^partnership$")
    score: int | None = Field(default=None, ge=0, le=100)
    band: str | None = Field(
        default=None,
        pattern=r"^(very_challenging|challenging|mixed|supportive|very_supportive)$",
    )
    score_version: str = Field(pattern=r"^outlook_index_v1$")
    confidence_status: str = Field(
        pattern=r"^(insufficient|uncalibrated_low|uncalibrated_moderate)$"
    )
    supporting_component: float = Field(ge=0, le=1)
    challenging_component: float = Field(ge=0, le=1)
    coverage: float = Field(ge=0, le=1)
    conflict_status: str = Field(
        pattern=r"^(none|internal_conflict|cross_channel_conflict|insufficient)$"
    )
    evidence_refs: list[str] = Field(min_length=1)
    disclaimer: str = Field(min_length=1)


class CompatibilityComponentInterpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component: str = Field(
        pattern=r"^(varna|vashya|tara|yoni|graha_maitri|gana|bhakoot|nadi)$"
    )
    status: str = Field(pattern=r"^(evaluated|abstained)$")
    achieved_points: float | None = Field(default=None, ge=0)
    maximum_points: int = Field(ge=1, le=8)
    ratio: float | None = Field(default=None, ge=0, le=1)
    band: str = Field(pattern=r"^(insufficient|challenging|mixed|supportive)$")
    headline: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)


class ManglikContextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_flagged_count: int = Field(ge=0, le=3)
    partner_flagged_count: int = Field(ge=0, le=3)
    comparison: str = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)
    disclaimer: str = Field(min_length=1)


class CompatibilityInterpretationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interpretation_version: str = Field(pattern=r"^compatibility_interpretation_v1$")
    facts_version: str = Field(pattern=r"^compatibility_facts_v2$")
    evaluated_maximum_points: int = Field(ge=0, le=36)
    complete_36_point_evaluation: bool
    partnership_index: PartnershipOutlookIndex
    components: list[CompatibilityComponentInterpretation] = Field(
        min_length=8,
        max_length=8,
    )
    strengths: list[str]
    cautions: list[str]
    manglik_context: ManglikContextResponse
    disclaimer: str = Field(min_length=1)


class CompatibilityReportResponse(BaseModel):
    """Raw Astro facts and their versioned Varahamihira interpretation."""

    model_config = ConfigDict(extra="forbid")

    facts: CompatibilityFactsResponse
    interpretation: CompatibilityInterpretationResponse
