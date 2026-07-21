"""System endpoints for service discovery and health monitoring."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app import __version__
from app.core.jpl_ephemeris import inspect_jpl_ephemeris
from app.core.security import inspect_api_security

router = APIRouter(tags=["System"])
_UNAVAILABLE_RESPONSES = {503: {"description": "A production dependency is not ready"}}


class RootResponse(BaseModel):
    """Public service metadata."""

    name: str
    version: str
    status: str
    documentation: str


class HealthResponse(BaseModel):
    """Process-liveness response used by humans and deployment probes."""

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


class SecurityHealthResponse(BaseModel):
    """Non-secret readiness details for calculation-route authentication."""

    status: str
    ready: bool
    protection_enabled: bool
    required: bool
    configured: bool
    valid_length: bool
    scheme: str
    minimum_key_length: int


class ReadinessResponse(BaseModel):
    """Combined production readiness for astronomy data and service authentication."""

    status: str
    ready: bool
    ephemeris: EphemerisHealthResponse
    security: SecurityHealthResponse


@router.get("/", response_model=RootResponse, summary="API information")
def root() -> RootResponse:
    """Return basic information about the Jyothisyam API."""

    return RootResponse(
        name="Jyothisyam API",
        version=__version__,
        status="running",
        documentation="/docs",
    )


@router.get("/health", response_model=HealthResponse, summary="Process liveness check")
def health_check() -> HealthResponse:
    """Confirm that the API process is alive without asserting dependency readiness."""

    return HealthResponse(
        status="healthy",
        service="jyothisyam-api",
        version=__version__,
        timestamp=datetime.now(UTC),
    )


def _ephemeris_payload() -> EphemerisHealthResponse:
    report = inspect_jpl_ephemeris()
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


def _security_payload() -> SecurityHealthResponse:
    report = inspect_api_security()
    return SecurityHealthResponse(
        status=report.status,
        ready=report.ready,
        protection_enabled=report.protection_enabled,
        required=report.required,
        configured=report.configured,
        valid_length=report.valid_length,
        scheme=report.scheme,
        minimum_key_length=report.minimum_key_length,
    )


@router.get(
    "/health/ephemeris",
    response_model=EphemerisHealthResponse,
    summary="Production JPL ephemeris readiness and integrity check",
    responses=_UNAVAILABLE_RESPONSES,
)
def ephemeris_health_check(response: Response) -> EphemerisHealthResponse:
    """Report whether the production DE440s kernel is present and verified."""

    payload = _ephemeris_payload()
    if not payload.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return payload


@router.get(
    "/health/ephemeris/jpl",
    response_model=EphemerisHealthResponse,
    summary="JPL ephemeris readiness compatibility route",
    responses=_UNAVAILABLE_RESPONSES,
)
def jpl_ephemeris_health_check(response: Response) -> EphemerisHealthResponse:
    """Retain the earlier JPL-specific readiness URL as an additive alias."""

    return ephemeris_health_check(response)


@router.get(
    "/health/security",
    response_model=SecurityHealthResponse,
    summary="Calculation-route authentication readiness",
    responses=_UNAVAILABLE_RESPONSES,
)
def security_health_check(response: Response) -> SecurityHealthResponse:
    """Report authentication readiness without exposing the configured service key."""

    payload = _security_payload()
    if not payload.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return payload


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Combined production readiness",
    responses=_UNAVAILABLE_RESPONSES,
)
def readiness_check(response: Response) -> ReadinessResponse:
    """Require both verified JPL data and a ready API-key policy."""

    ephemeris = _ephemeris_payload()
    security = _security_payload()
    ready = ephemeris.ready and security.ready
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponse(
        status="ready" if ready else "degraded",
        ready=ready,
        ephemeris=ephemeris,
        security=security,
    )
