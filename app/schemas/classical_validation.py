"""Schemas for external golden-chart validation and discrepancy reporting."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.classical import ClassicalProfileId
from app.schemas.positions import BirthInput, CalculationProfile


class ValidationSourceKind(StrEnum):
    """Kinds of reference material accepted by the validation harness."""

    EXTERNAL_SOFTWARE = "external_software"
    MANUAL_REFERENCE = "manual_reference"
    INTERNAL_BASELINE = "internal_baseline"


class ValidationFieldStatus(StrEnum):
    """Comparison state for one flattened snapshot field."""

    MATCH = "match"
    MISMATCH = "mismatch"


class GoldenChartCase(BaseModel):
    """One immutable birth input selected for broad calculation coverage."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    label: str
    birth: BirthInput
    coverage_tags: list[str]


class GoldenChartCaseSetResponse(BaseModel):
    """Frozen validation-case set advertised by the public API."""

    profile_id: ClassicalProfileId
    case_set_id: str
    case_set_version: str
    case_set_digest: str
    cases: list[GoldenChartCase]


class ExternalReferenceSource(BaseModel):
    """Provenance for one imported comparison snapshot."""

    model_config = ConfigDict(extra="forbid")

    source_name: str = Field(min_length=1, max_length=100)
    source_version: str = Field(min_length=1, max_length=100)
    source_kind: ValidationSourceKind
    calculation_notes: list[str] = []


class GoldenChartSnapshot(BaseModel):
    """Normalized, partially populated chart snapshot used for comparison."""

    model_config = ConfigDict(extra="forbid")

    ayanamsha_degrees: float | None = None
    ascendant_longitude: float | None = Field(default=None, ge=0.0, lt=360.0)
    point_longitudes: dict[str, float] | None = None
    d1_signs: dict[str, int] | None = None
    d9_signs: dict[str, int] | None = None
    dignity: dict[str, str] | None = None
    vargottama: dict[str, bool] | None = None
    compound_relationships: dict[str, str] | None = None
    bhinnashtakavarga: dict[str, list[int]] | None = None
    sarvashtakavarga: list[int] | None = None
    weighted_scores: dict[str, float] | None = None
    weighted_ranks: dict[str, int] | None = None

    @model_validator(mode="after")
    def require_at_least_one_group(self) -> "GoldenChartSnapshot":
        """Reject empty snapshots because they cannot validate anything."""

        if not self.model_dump(exclude_none=True):
            raise ValueError("reference_snapshot must contain at least one field group")
        return self


class ValidationTolerances(BaseModel):
    """Field-specific tolerances used by numeric comparisons."""

    model_config = ConfigDict(extra="forbid")

    longitude_degrees: float = Field(default=0.01, ge=0.0, le=1.0)
    ayanamsha_degrees: float = Field(default=0.01, ge=0.0, le=1.0)
    score: float = Field(default=0.000001, ge=0.0, le=0.1)


class GoldenChartComparisonRequest(BaseModel):
    """Compare one external or manual snapshot with a frozen chart case."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    source: ExternalReferenceSource
    reference_snapshot: GoldenChartSnapshot
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_V1
    )
    tolerances: ValidationTolerances = ValidationTolerances()


class FieldComparison(BaseModel):
    """One scalar field comparison with transparent tolerance handling."""

    model_config = ConfigDict(extra="forbid")

    path: str
    status: ValidationFieldStatus
    actual_value: str
    reference_value: str
    absolute_difference: float | None = None
    tolerance: float | None = None
    reason: str


class GoldenChartComparisonResponse(BaseModel):
    """Field-by-field report for one reference snapshot."""

    profile_id: ClassicalProfileId
    case: GoldenChartCase
    source: ExternalReferenceSource
    actual_snapshot: GoldenChartSnapshot
    compared_field_count: int = Field(ge=1)
    matched_field_count: int = Field(ge=0)
    mismatched_field_count: int = Field(ge=0)
    skipped_field_groups: list[str]
    passed: bool
    comparisons: list[FieldComparison]
    external_reference_validation_complete: bool
    caveats: list[str]


class ValidationProfileResponse(BaseModel):
    """Maturity and completion state of the external validation program."""

    profile_id: ClassicalProfileId
    harness_version: str
    case_set_id: str
    case_set_version: str
    frozen_case_count: int = Field(ge=1)
    required_external_sources_per_case: int = Field(ge=2)
    committed_external_snapshot_count: int = Field(ge=0)
    externally_validated_case_count: int = Field(ge=0)
    external_reference_validation_complete: bool
    supported_field_groups: list[str]
    comparison_policy: list[str]
    caveats: list[str]
