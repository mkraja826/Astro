"""Local JPL SPK data configuration for the Skyfield provider."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from hmac import compare_digest
from os import getenv
from pathlib import Path

from app.core.ephemeris import EphemerisUnavailableError

JPL_EPHEMERIS_MODEL = "de440s"
JPL_EPHEMERIS_FILENAME = "de440s.bsp"
JPL_EPHEMERIS_SHA256 = "c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2"
_SHA256_HEX = frozenset("0123456789abcdef")
_CHUNK_SIZE = 1024 * 1024


@dataclass(frozen=True)
class JplEphemerisSettings:
    """Runtime path, model, and digest selected for the Skyfield/JPL provider."""

    data_path: Path
    expected_sha256: str
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
    expected_sha256: str
    actual_sha256: str | None
    integrity_verified: bool
    automatic_download_enabled: bool
    issues: tuple[str, ...]


def _default_jpl_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "jpl" / JPL_EPHEMERIS_FILENAME


def _normalize_sha256(value: str) -> str:
    return value.strip().lower()


def _is_valid_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in _SHA256_HEX for character in value)


def load_jpl_ephemeris_settings() -> JplEphemerisSettings:
    """Read the local SPK path and expected digest without initiating a download."""

    configured = getenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(_default_jpl_path()))
    expected_sha256 = _normalize_sha256(
        getenv("JYOTHISYAM_JPL_EPHEMERIS_SHA256", JPL_EPHEMERIS_SHA256)
    )
    return JplEphemerisSettings(
        data_path=Path(configured).expanduser(),
        expected_sha256=expected_sha256,
    )


@lru_cache(maxsize=16)
def _cached_file_sha256(path_text: str, file_size: int, modified_ns: int) -> str:
    """Hash a stable file identity and cache the result between readiness probes."""

    del file_size, modified_ns
    digest = sha256()
    with Path(path_text).open("rb") as source:
        while chunk := source.read(_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_jpl_ephemeris() -> JplEphemerisStatus:
    """Return a non-throwing readiness and integrity report for JPL calculations."""

    settings = load_jpl_ephemeris_settings()
    issues: list[str] = []
    data_path = settings.data_path
    exists = data_path.is_file()
    size: int | None = None
    modified_ns: int | None = None
    actual_sha256: str | None = None
    integrity_verified = False

    if not _is_valid_sha256(settings.expected_sha256):
        issues.append(
            "JYOTHISYAM_JPL_EPHEMERIS_SHA256 must contain exactly 64 hexadecimal characters"
        )

    if not exists:
        issues.append(
            "JPL DE440s kernel is missing; install the verified de440s.bsp file and set "
            "JYOTHISYAM_JPL_EPHEMERIS_PATH"
        )
    else:
        try:
            stat_result = data_path.stat()
            size = stat_result.st_size
            modified_ns = stat_result.st_mtime_ns
        except OSError as error:
            issues.append(f"JPL ephemeris metadata could not be read: {error}")

        if data_path.suffix.lower() != ".bsp":
            issues.append("JPL ephemeris path must point to a .bsp SPK kernel")
        if size == 0:
            issues.append("JPL ephemeris file is empty")

        if (
            size is not None
            and size > 0
            and modified_ns is not None
            and _is_valid_sha256(settings.expected_sha256)
        ):
            try:
                actual_sha256 = _cached_file_sha256(str(data_path.resolve()), size, modified_ns)
            except OSError as error:
                issues.append(f"JPL ephemeris file could not be hashed: {error}")
            else:
                integrity_verified = compare_digest(actual_sha256, settings.expected_sha256)
                if not integrity_verified:
                    issues.append(
                        "JPL ephemeris SHA-256 mismatch: expected "
                        f"{settings.expected_sha256}, received {actual_sha256}"
                    )

    ready = not issues and integrity_verified
    return JplEphemerisStatus(
        status="ready" if ready else "degraded",
        ready=ready,
        provider="skyfield_jpl",
        model=settings.model,
        configured_path=str(data_path),
        file_exists=exists,
        file_size_bytes=size,
        expected_sha256=settings.expected_sha256,
        actual_sha256=actual_sha256,
        integrity_verified=integrity_verified,
        automatic_download_enabled=False,
        issues=tuple(issues),
    )


def require_jpl_ephemeris() -> JplEphemerisSettings:
    """Return validated settings or fail before Skyfield attempts to open a kernel."""

    report = inspect_jpl_ephemeris()
    if not report.ready:
        raise EphemerisUnavailableError("; ".join(report.issues))
    return load_jpl_ephemeris_settings()
