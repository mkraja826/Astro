"""Schemas for source-traceable Bṛhat Jātaka prediction output."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.dasha import DashaQueryTime
from app.schemas.positions import BirthInput, CalculationProfile


class PredictionPeriod(StrEnum):
    """Consumer periods accepted by the v1 prediction endpoint."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NATAL = "natal"


class ClassicalPredictionRequest(BaseModel):
    """Birth data and requested instant for deterministic interpretation."""

    model_config = ConfigDict(extra="forbid")

    birth: BirthInput
    as_of: DashaQueryTime
    period: PredictionPeriod
    calculation_profile: CalculationProfile = (
        CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
    )


class PredictionEvidence(BaseModel):
    """One preserved supporting, challenging, or contextual factor."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    domain: str
    statement: str
    polarity: str
    weight: float = Field(ge=0.0, le=1.0)
    source_rule_ids: list[str]
    source_kind: str
    reason: str


class PredictionDomainResult(BaseModel):
    """Direct conclusion for one supported prediction domain."""

    model_config = ConfigDict(extra="forbid")

    domain: str
    outlook: str
    strength: str
    supporting_score: float
    challenging_score: float
    net_score: float
    statement: str
    supporting_factors: list[PredictionEvidence]
    challenging_factors: list[PredictionEvidence]
    contextual_factors: list[PredictionEvidence]


class ClassicalPredictionResponse(BaseModel):
    """Versioned result consumed by the Horos gateway."""

    model_config = ConfigDict(extra="forbid")

    engine_version: str
    calculation_profile: str
    classical_profile: str
    period: PredictionPeriod
    as_of: str
    results: list[PredictionDomainResult]
    disclaimer: str
