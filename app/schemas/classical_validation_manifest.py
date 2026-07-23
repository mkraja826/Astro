"""Schemas for committed external-validation evidence and approval summaries."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.classical import ClassicalProfileId
from app.schemas.classical_validation import ExternalReferenceSource, ValidationSourceKind
from app.schemas.positions import CalculationProfile


class ExternalValidationReviewStatus(StrEnum):
    """Review state of one committed external snapshot."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExternalValidationSnapshotRecord(BaseModel):
    """Provenance and review state for one committed external snapshot file."""

    model_config = ConfigDict(extra="forbid")

    snapshot_id: str = Field(min_length=1, max_length=160, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    case_id: str = Field(min_length=1, max_length=160)
    source_id: str = Field(min_length=1, max_length=160, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    source: ExternalReferenceSource
    snapshot_path: str = Field(min_length=1, max_length=240)
    snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    review_status: ExternalValidationReviewStatus
    reviewed_by: str | None = Field(default=None, min_length=1, max_length=160)
    reviewed_at: datetime | None = None
    review_notes: list[str] = Field(default_factory=list)

    @field_validator("snapshot_path")
    @classmethod
    def require_safe_snapshot_path(cls, value: str) -> str:
        """Keep evidence files inside the versioned external validation directory."""

        normalized = value.replace("\\", "/")
        if normalized.startswith("/") or ".." in normalized.split("/"):
            raise ValueError("snapshot_path must be a safe relative path")
        if not normalized.startswith("app/data/validation/external_v1/"):
            raise ValueError(
                "snapshot_path must remain under app/data/validation/external_v1/"
            )
        if not normalized.endswith(".json"):
            raise ValueError("snapshot_path must reference a JSON file")
        return normalized

    @model_validator(mode="after")
    def enforce_external_review_contract(self) -> "ExternalValidationSnapshotRecord":
        """Reject internal baselines and incomplete approval metadata."""

        if self.source.source_kind == ValidationSourceKind.INTERNAL_BASELINE:
            raise ValueError("external validation records cannot use internal baselines")
        if (
            self.review_status == ExternalValidationReviewStatus.APPROVED
            and (self.reviewed_by is None or self.reviewed_at is None)
        ):
            raise ValueError("approved snapshots require reviewed_by and reviewed_at")
        return self


class ExternalValidationManifest(BaseModel):
    """Versioned ledger of committed independent validation evidence."""

    model_config = ConfigDict(extra="forbid")

    manifest_id: str
    manifest_version: str
    profile_id: ClassicalProfileId
    calculation_profile: CalculationProfile
    case_set_id: str
    case_set_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    required_external_sources_per_case: int = Field(ge=2)
    records: list[ExternalValidationSnapshotRecord] = Field(default_factory=list)
    policy_notes: list[str] = Field(default_factory=list)


class ExternalValidationManifestSummary(BaseModel):
    """Derived validation maturity; no count is trusted from hand-edited JSON."""

    manifest: ExternalValidationManifest
    manifest_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    committed_external_snapshot_count: int = Field(ge=0)
    approved_external_snapshot_count: int = Field(ge=0)
    externally_validated_case_count: int = Field(ge=0)
    validated_case_ids: list[str]
    approved_source_counts_by_case: dict[str, int]
    external_reference_validation_complete: bool
