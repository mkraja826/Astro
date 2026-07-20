"""Local JPL SPK data configuration for the Skyfield provider."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from pathlib import Path

from app.core.ephemeris import EphemerisUnavailableError

JPL_EPHEMERIS_MODEL = "de440s"
JPL_EPHEMERIS_FILENAME = "de440s.bsp"


@dataclass(frozen=True)
class JplEphemerisSettings:
    """Runtime path and model selected for the Skyfield/JPL provider."""

    data_path: Path
    model: str = JPL_EPHEMERIS_MODEL


@dataclass(frozen=True)
class JplEphemerisStatus:
    """Serializable readiness report for local JPL SPK data."""

    status: str
    ready: bool
    provider: str
    model: str
    configured_path: str
    file_exists: bool
    file_size_bytes: int | None
    automatic_download_enabled: bool
    issues: tuple[str, ...]


def _default_jpl_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "jpl" / JPL_EPHEMERIS_FILENAME


def load_jpl_ephemeris_settings() -> JplEphemerisSettings:
    """Read the local SPK path without initiating any network download."""

    configured = getenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(_default_jpl_path()))
    return JplEphemerisSettings(data_path=Path(configured).expanduser())


def inspect_jpl_ephemeris() -> JplEphemerisStatus:
    """Return a non-throwing readiness report for Skyfield/JPL calculations."""

    settings = load_jpl_ephemeris_settings()
    issues: list[str] = []
    exists = settings.data_path.is_file()
    size = settings.data_path.stat().st_size if exists else None

    if not exists:
        issues.append(
            "JPL DE440s kernel is missing; download de440s.bsp and set "
            "JYOTHISYAM_JPL_EPHEMERIS_PATH"
        )
    elif settings.data_path.suffix.lower() != ".bsp":
        issues.append("JPL ephemeris path must point to a .bsp SPK kernel")
    elif size is not None and size == 0:
        issues.append("JPL ephemeris file is empty")

    ready = not issues
    return JplEphemerisStatus(
        status="ready" if ready else "degraded",
        ready=ready,
        provider="skyfield_jpl",
        model=settings.model,
        configured_path=str(settings.data_path),
        file_exists=exists,
        file_size_bytes=size,
        automatic_download_enabled=False,
        issues=tuple(issues),
    )


def require_jpl_ephemeris() -> JplEphemerisSettings:
    """Return validated settings or fail before Skyfield attempts to open a kernel."""

    report = inspect_jpl_ephemeris()
    if not report.ready:
        raise EphemerisUnavailableError("; ".join(report.issues))
    return load_jpl_ephemeris_settings()
