"""Swiss Ephemeris licensing, data-path, and source enforcement policies."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from pathlib import Path

import swisseph as swe

SUPPORTED_LICENSE_MODES = {"agpl", "professional"}
REQUIRED_V1_FILES = ("sepl_18.se1", "semo_18.se1")
_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


class EphemerisConfigurationError(RuntimeError):
    """Raised when the service ephemeris configuration is invalid."""


class EphemerisUnavailableError(RuntimeError):
    """Raised when the requested production-grade ephemeris source is unavailable."""


@dataclass(frozen=True)
class EphemerisSettings:
    """Runtime settings controlling Swiss Ephemeris use."""

    environment: str
    data_path: Path
    require_swiss: bool
    license_mode: str

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def license_declared(self) -> bool:
        return self.license_mode in SUPPORTED_LICENSE_MODES


@dataclass(frozen=True)
class EphemerisStatus:
    """Serializable readiness report for operations and deployment probes."""

    status: str
    ready: bool
    environment: str
    strict_source_required: bool
    license_mode: str
    data_directory_exists: bool
    required_files: tuple[str, ...]
    detected_files: tuple[str, ...]
    issues: tuple[str, ...]


def _default_data_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "ephe"


def _parse_bool(name: str, value: str | None, *, default: bool) -> bool:
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False

    raise EphemerisConfigurationError(
        f"{name} must be one of: true, false, 1, 0, yes, no, on, off"
    )


def load_ephemeris_settings() -> EphemerisSettings:
    """Read and strictly validate runtime ephemeris settings."""

    environment = getenv("APP_ENV", "development").strip().lower()
    data_path = Path(
        getenv("JYOTHISYAM_EPHEMERIS_PATH", str(_default_data_path()))
    ).expanduser()
    license_mode = getenv("JYOTHISYAM_SWISS_LICENSE_MODE", "unset").strip().lower()
    require_swiss = _parse_bool(
        "JYOTHISYAM_REQUIRE_SWISS_EPHEMERIS",
        getenv("JYOTHISYAM_REQUIRE_SWISS_EPHEMERIS"),
        default=environment == "production",
    )

    return EphemerisSettings(
        environment=environment,
        data_path=data_path,
        require_swiss=require_swiss,
        license_mode=license_mode,
    )


def inspect_ephemeris() -> EphemerisStatus:
    """Return a non-throwing readiness report for health checks."""

    issues: list[str] = []
    environment = getenv("APP_ENV", "development").strip().lower()
    license_mode = getenv("JYOTHISYAM_SWISS_LICENSE_MODE", "unset").strip().lower()
    data_path = Path(
        getenv("JYOTHISYAM_EPHEMERIS_PATH", str(_default_data_path()))
    ).expanduser()

    try:
        require_swiss = _parse_bool(
            "JYOTHISYAM_REQUIRE_SWISS_EPHEMERIS",
            getenv("JYOTHISYAM_REQUIRE_SWISS_EPHEMERIS"),
            default=environment == "production",
        )
    except EphemerisConfigurationError as exc:
        require_swiss = True
        issues.append(str(exc))

    data_directory_exists = data_path.is_dir()
    detected_files = (
        tuple(sorted(path.name for path in data_path.glob("*.se1")))
        if data_directory_exists
        else ()
    )
    missing_files = tuple(name for name in REQUIRED_V1_FILES if name not in detected_files)

    if license_mode not in SUPPORTED_LICENSE_MODES:
        issues.append(
            "Swiss Ephemeris license mode is not declared; choose agpl or professional "
            "before activating a public service"
        )
    if not data_directory_exists:
        issues.append("Swiss Ephemeris data directory does not exist")
    elif missing_files:
        issues.append(f"Missing required v1 ephemeris files: {', '.join(missing_files)}")

    ready = not issues
    return EphemerisStatus(
        status="ready" if ready else "degraded",
        ready=ready,
        environment=environment,
        strict_source_required=require_swiss,
        license_mode=license_mode,
        data_directory_exists=data_directory_exists,
        required_files=REQUIRED_V1_FILES,
        detected_files=detected_files,
        issues=tuple(issues),
    )


def configure_ephemeris() -> EphemerisSettings:
    """Configure the native engine and enforce production licensing declarations."""

    settings = load_ephemeris_settings()
    if settings.is_production and not settings.license_declared:
        raise EphemerisConfigurationError(
            "Production requires JYOTHISYAM_SWISS_LICENSE_MODE=agpl or professional"
        )

    swe.set_ephe_path(str(settings.data_path))
    return settings


def enforce_ephemeris_source(
    source: str,
    body: str,
    settings: EphemerisSettings,
) -> None:
    """Prevent silent fallback when strict Swiss Ephemeris mode is enabled."""

    if settings.require_swiss and source != "swiss":
        raise EphemerisUnavailableError(
            f"Swiss Ephemeris data was required for {body}, but the engine used "
            f"{source!r}. Check JYOTHISYAM_EPHEMERIS_PATH and deployed data files."
        )
