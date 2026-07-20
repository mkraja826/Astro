"""System endpoints for service discovery and health monitoring."""

from datetime import UTC, datetime

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from app import __version__
from app.core.ephemeris import inspect_ephemeris
from app.core.jpl_ephemeris import inspect_jpl_ephemeris

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


class EphemerisHealthResponse(BaseModel):
    """Readiness response for licensed Swiss Ephemeris calculations."""

    status: str
    ready: bool
    environment: str
    strict_source_required: bool
    license_mode: str
    data_directory_exists: bool
    required_files: tuple[str, ...]
    detected_files: tuple[str, ...]
    issues: tuple[str, ...]


class JplEphemerisHealthResponse(BaseModel):
    """Readiness response for the local Skyfield/JPL kernel."""

    status: str
    ready: bool
    provider: str
    model: str
    configured_path: str
    file_exists: bool
    file_size_bytes: int | None
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


@router.get(
    "/health/ephemeris",
    response_model=EphemerisHealthResponse,
    summary="Swiss Ephemeris readiness check",
    responses={503: {"description": "Licensed Swiss Ephemeris data is not ready"}},
)
def ephemeris_health_check(response: Response) -> EphemerisHealthResponse:
    """Report whether the original Swiss calculation profile is production-ready."""

    report = inspect_ephemeris()
    if not report.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return EphemerisHealthResponse(
        status=report.status,
        ready=report.ready,
        environment=report.environment,
        strict_source_required=report.strict_source_required,
        license_mode=report.license_mode,
        data_directory_exists=report.data_directory_exists,
        required_files=report.required_files,
        detected_files=report.detected_files,
        issues=report.issues,
    )


@router.get(
    "/health/ephemeris/jpl",
    response_model=JplEphemerisHealthResponse,
    summary="Skyfield/JPL ephemeris readiness check",
    responses={503: {"description": "Local JPL DE440s kernel is not ready"}},
)
def jpl_ephemeris_health_check(response: Response) -> JplEphemerisHealthResponse:
    """Report whether the local DE440s kernel is available without downloading it."""

    report = inspect_jpl_ephemeris()
    if not report.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return JplEphemerisHealthResponse(
        status=report.status,
        ready=report.ready,
        provider=report.provider,
        model=report.model,
        configured_path=report.configured_path,
        file_exists=report.file_exists,
        file_size_bytes=report.file_size_bytes,
        automatic_download_enabled=report.automatic_download_enabled,
        issues=report.issues,
    )
