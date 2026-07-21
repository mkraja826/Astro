"""Schemas for immutable internal JPL golden-chart regression baselines."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.classical import ClassicalProfileId
from app.schemas.classical_validation import GoldenChartCase, GoldenChartSnapshot
from app.schemas.positions import CalculationProfile

_SHA256_PATTERN = r"^[0-9a-f]{64}$"


class BaselineCaseReference(BaseModel):
    """Manifest pointer to one committed baseline record."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    path: str
    snapshot_digest: str = Field(pattern=_SHA256_PATTERN)


class JplBaselineManifest(BaseModel):
    """Versioned manifest for the complete internal JPL baseline set."""

    model_config = ConfigDict(extra="forbid")

    baseline_set_id: str
    baseline_set_version: str
    snapshot_schema_version: str
    case_set_id: str
    case_set_version: str
    case_set_digest: str = Field(pattern=_SHA256_PATTERN)
    calculation_profile: CalculationProfile
    engine_version: str
    astronomical_provider: str
    provider_version: str
    ephemeris_model: str
    case_count: int = Field(ge=1)
    cases: list[BaselineCaseReference]
    baseline_set_digest: str = Field(pattern=_SHA256_PATTERN)


class JplBaselineCaseRecord(BaseModel):
    """One digest-locked normalized snapshot stored in the repository."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    snapshot: GoldenChartSnapshot
    snapshot_digest: str = Field(pattern=_SHA256_PATTERN)


class JplBaselineStorageVerificationResponse(BaseModel):
    """Integrity report for the committed manifest and snapshot files."""

    profile_id: ClassicalProfileId
    baseline_set_id: str
    baseline_set_version: str
    baseline_set_digest: str
    calculation_profile: CalculationProfile
    expected_case_count: int = Field(ge=1)
    loaded_case_count: int = Field(ge=0)
    case_set_digest_match: bool
    baseline_set_digest_match: bool
    verified: bool
    missing_case_ids: list[str]
    unexpected_case_ids: list[str]
    duplicate_case_ids: list[str]
    invalid_snapshot_digest_case_ids: list[str]
    issues: list[str]
    external_reference_validation_complete: bool = False


class JplBaselineCaseResponse(BaseModel):
    """One committed internal regression baseline and its provenance."""

    profile_id: ClassicalProfileId
    baseline_set_id: str
    baseline_set_version: str
    calculation_profile: CalculationProfile
    case: GoldenChartCase
    snapshot_digest: str
    snapshot: GoldenChartSnapshot
    internal_regression_baseline: bool = True
    external_reference_validation_complete: bool = False
    caveats: list[str]


class JplBaselineRuntimeCaseResult(BaseModel):
    """Current-engine comparison against one committed JPL baseline."""

    case_id: str
    stored_snapshot_digest: str
    actual_snapshot_digest: str
    matched: bool
    mismatched_field_paths: list[str]


class JplBaselineRuntimeVerificationResponse(BaseModel):
    """Full twelve-case current-runtime regression report."""

    profile_id: ClassicalProfileId
    baseline_set_id: str
    baseline_set_version: str
    baseline_set_digest: str
    calculation_profile: CalculationProfile
    case_count: int = Field(ge=1)
    matched_case_count: int = Field(ge=0)
    mismatched_case_count: int = Field(ge=0)
    passed: bool
    cases: list[JplBaselineRuntimeCaseResult]
    external_reference_validation_complete: bool = False
    caveats: list[str]
