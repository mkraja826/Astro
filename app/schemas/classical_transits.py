"""Schemas for source-traceable Chapter 9 transit evaluation."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.classical import ClassicalProfileId
from app.schemas.transits import TransitSnapshotRequest, TransitSnapshotResponse


class TransitPolarity(StrEnum):
    """Directional balance of benefic dots and complementary lines."""

    SUPPORTING = "supporting"
    CHALLENGING = "challenging"
    CONTEXTUAL = "contextual"


class ClassicalTransitEvaluationRequest(TransitSnapshotRequest):
    """Birth and requested instant for Chapter 9 transit evaluation."""


class ClassicalTransitFactor(BaseModel):
    """One seven-Graha Bhinnashtakavarga transit balance."""

    model_config = ConfigDict(extra="forbid")

    body: str
    transit_sign_index: int = Field(ge=1, le=12)
    house_from_natal_ascendant: int = Field(ge=1, le=12)
    house_from_natal_moon: int = Field(ge=1, le=12)
    bindus: int = Field(ge=0, le=8)
    rekhas: int = Field(ge=0, le=8)
    net_eighths: int = Field(ge=-8, le=8)
    normalized_balance: float = Field(ge=-1.0, le=1.0)
    polarity: TransitPolarity
    rule_ids: list[str]
    reason: str


class ClassicalTransitEvaluationResponse(BaseModel):
    """Raw snapshot plus source-traceable, planet-specific transit balances."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_id: ClassicalProfileId
    snapshot: TransitSnapshotResponse
    factors: list[ClassicalTransitFactor] = Field(min_length=7, max_length=7)
    interpretation_applied: bool
    domain_prediction_applied: bool
    timing_window_applied: bool
    excluded_points: list[str]
    caveats: list[str]


class TransitHorizonPeriod(StrEnum):
    """Supported forward sampling horizons."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ClassicalTransitHorizonRequest(TransitSnapshotRequest):
    """Birth, starting instant, and deterministic sampling horizon."""

    period: TransitHorizonPeriod


class ClassicalTransitHorizonSample(BaseModel):
    """Compact source evaluation at one civil sample instant."""

    model_config = ConfigDict(extra="forbid")

    sample_index: int = Field(ge=1)
    local_datetime: datetime
    timezone: str
    factors: list[ClassicalTransitFactor] = Field(min_length=7, max_length=7)


class ClassicalTransitHorizonResponse(BaseModel):
    """Deterministic sample grid used by later domain aggregation."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    profile_id: ClassicalProfileId
    period: TransitHorizonPeriod
    sample_count: int = Field(ge=1)
    samples: list[ClassicalTransitHorizonSample] = Field(min_length=1)
    sampling_applied: bool
    exact_ingress_egress_applied: bool
    domain_prediction_applied: bool
    caveats: list[str]
