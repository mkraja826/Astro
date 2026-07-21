"""Schemas for normalizing external Jyotisha software exports."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.classical import ClassicalProfileId
from app.schemas.classical_validation import ExternalReferenceSource, GoldenChartSnapshot


class ExternalSnapshotFormat(StrEnum):
    """External snapshot formats accepted by the normalization layer."""

    GENERIC_JSON_V1 = "generic_json_v1"


class ExternalSnapshotImportRequest(BaseModel):
    """One external export and its source provenance."""

    model_config = ConfigDict(extra="forbid")

    source: ExternalReferenceSource
    format: ExternalSnapshotFormat = ExternalSnapshotFormat.GENERIC_JSON_V1
    payload: dict[str, Any] = Field(min_length=1)


class ExternalSnapshotImportResponse(BaseModel):
    """Normalized snapshot ready for the existing comparison endpoint."""

    model_config = ConfigDict(extra="forbid")

    profile_id: ClassicalProfileId
    normalization_profile: str
    format: ExternalSnapshotFormat
    source: ExternalReferenceSource
    snapshot: GoldenChartSnapshot
    normalized_aliases: dict[str, str]
    ignored_paths: list[str]
    warnings: list[str]
