"""Tests for Swiss Ephemeris production-readiness policies."""

from pathlib import Path

import pytest

from app.core.ephemeris import (
    EphemerisConfigurationError,
    EphemerisSettings,
    EphemerisUnavailableError,
    REQUIRED_V1_FILES,
    configure_ephemeris,
    enforce_ephemeris_source,
    inspect_ephemeris,
)


def _set_environment(
    monkeypatch: pytest.MonkeyPatch,
    data_path: Path,
    *,
    environment: str,
    license_mode: str,
    require_swiss: str,
) -> None:
    monkeypatch.setenv("APP_ENV", environment)
    monkeypatch.setenv("JYOTHISYAM_EPHEMERIS_PATH", str(data_path))
    monkeypatch.setenv("JYOTHISYAM_SWISS_LICENSE_MODE", license_mode)
    monkeypatch.setenv("JYOTHISYAM_REQUIRE_SWISS_EPHEMERIS", require_swiss)


def test_readiness_reports_missing_license_and_data(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    data_path = tmp_path / "missing"
    _set_environment(
        monkeypatch,
        data_path,
        environment="development",
        license_mode="unset",
        require_swiss="false",
    )

    report = inspect_ephemeris()

    assert report.ready is False
    assert report.status == "degraded"
    assert report.data_directory_exists is False
    assert any("license mode" in issue for issue in report.issues)
    assert any("does not exist" in issue for issue in report.issues)


def test_readiness_accepts_declared_license_and_required_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    for filename in REQUIRED_V1_FILES:
        (tmp_path / filename).write_bytes(b"test fixture")

    _set_environment(
        monkeypatch,
        tmp_path,
        environment="production",
        license_mode="professional",
        require_swiss="true",
    )

    report = inspect_ephemeris()

    assert report.ready is True
    assert report.status == "ready"
    assert report.strict_source_required is True
    assert set(REQUIRED_V1_FILES).issubset(report.detected_files)


def test_production_configuration_requires_declared_license(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _set_environment(
        monkeypatch,
        tmp_path,
        environment="production",
        license_mode="unset",
        require_swiss="true",
    )

    with pytest.raises(EphemerisConfigurationError, match="Production requires"):
        configure_ephemeris()


def test_strict_mode_rejects_silent_moshier_fallback(tmp_path: Path) -> None:
    settings = EphemerisSettings(
        environment="production",
        data_path=tmp_path,
        require_swiss=True,
        license_mode="professional",
    )

    with pytest.raises(EphemerisUnavailableError, match="moshier"):
        enforce_ephemeris_source("moshier", "sun", settings)


def test_non_strict_development_mode_allows_fallback(tmp_path: Path) -> None:
    settings = EphemerisSettings(
        environment="development",
        data_path=tmp_path,
        require_swiss=False,
        license_mode="unset",
    )

    enforce_ephemeris_source("moshier", "sun", settings)
