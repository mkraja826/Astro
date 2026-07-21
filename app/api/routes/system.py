"""System endpoints for service discovery and health monitoring."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app import __version__
from app.core.jpl_ephemeris import inspect_jpl_ephemeris

router = APIRouter(tags=["System"])
_EPHEMERIS_UNAVAILABLE_RESPONSES = {
    503: {
        "description": "Local JPL DE440s kernel is not ready or failed integrity",
    }
}


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


class EphemerisHealthResponse(BaseModel):
    """Readiness and integrity response for the local Skyfield/JPL kernel."""

    status: str
    ready: bool
    provider: str
    model: str
    configured_path: str
    file_exists: bool
    file_size_bytes: int | None
    expected_sha256: str
    actual_sha256: str | None
    integrity_verified: bool
    automatic_download_enabled: bool
    issues: tuple[str, ...]


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


def _jpl_health(response: Response) -> EphemerisHealthResponse:
    report = inspect_jpl_ephemeris()
    if not report.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return EphemerisHealthResponse(
        status=report.status,
        ready=report.ready,
        provider=report.provider,
        model=report.model,
        configured_path=report.configured_path,
        file_exists=report.file_exists,
        file_size_bytes=report.file_size_bytes,
        expected_sha256=report.expected_sha256,
        actual_sha256=report.actual_sha256,
        integrity_verified=report.integrity_verified,
        automatic_download_enabled=report.automatic_download_enabled,
        issues=report.issues,
    )


@router.get(
    "/health/ephemeris",
    response_model=EphemerisHealthResponse,
    summary="Production JPL ephemeris readiness and integrity check",
    responses=_EPHEMERIS_UNAVAILABLE_RESPONSES,
)
def ephemeris_health_check(response: Response) -> EphemerisHealthResponse:
    """Report whether the production DE440s kernel is present and verified."""

    return _jpl_health(response)


@router.get(
    "/health/ephemeris/jpl",
    response_model=EphemerisHealthResponse,
    summary="JPL ephemeris readiness compatibility route",
    responses=_EPHEMERIS_UNAVAILABLE_RESPONSES,
)
def jpl_ephemeris_health_check(response: Response) -> EphemerisHealthResponse:
    """Retain the earlier JPL-specific readiness URL as an additive alias."""

    return _jpl_health(response)
