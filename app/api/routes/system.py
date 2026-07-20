"""System endpoints for service discovery and health monitoring."""

from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app import __version__

router = APIRouter(tags=["System"])


class RootResponse(BaseModel):
    """Public service metadata."""

    name: str
    version: str
    status: str
    documentation: str


class HealthResponse(BaseModel):
    """Health response used by humans and deployment probes."""

    status: str
    service: str
    version: str
    timestamp: datetime


@router.get("/", response_model=RootResponse, summary="API information")
def root() -> RootResponse:
    """Return basic information about the Jyothisyam API."""

    return RootResponse(
        name="Jyothisyam API",
        version=__version__,
        status="running",
        documentation="/docs",
    )


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check() -> HealthResponse:
    """Confirm that the API process is healthy."""

    return HealthResponse(
        status="healthy",
        service="jyothisyam-api",
        version=__version__,
        timestamp=datetime.now(UTC),
    )
