"""Tests for local JPL ephemeris readiness policies."""

from hashlib import sha256
from pathlib import Path

import pytest

from app.core.ephemeris import EphemerisUnavailableError
from app.core.jpl_ephemeris import inspect_jpl_ephemeris, require_jpl_ephemeris


def _configure_fixture_kernel(
    monkeypatch: pytest.MonkeyPatch,
    path: Path,
    payload: bytes,
) -> None:
    path.write_bytes(payload)
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(path))
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_SHA256", sha256(payload).hexdigest())


def test_readiness_reports_missing_kernel(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-de440s.bsp"
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(missing))

    report = inspect_jpl_ephemeris()

    assert report.ready is False
    assert report.status == "degraded"
    assert report.provider == "skyfield_jpl"
    assert report.model == "de440s"
    assert report.file_exists is False
    assert report.automatic_download_enabled is False
    assert report.issues


def test_readiness_accepts_verified_nonempty_bsp_kernel(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    kernel = tmp_path / "de440s.bsp"
    payload = b"test fixture"
    _configure_fixture_kernel(monkeypatch, kernel, payload)

    report = inspect_jpl_ephemeris()

    assert report.ready is True
    assert report.status == "ready"
    assert report.file_exists is True
    assert report.file_size_bytes == len(payload)
    assert report.expected_sha256 == sha256(payload).hexdigest()
    assert report.actual_sha256 == sha256(payload).hexdigest()
    assert report.integrity_verified is True
    assert report.issues == ()


def test_readiness_rejects_wrong_extension(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    kernel = tmp_path / "de440s.dat"
    payload = b"test fixture"
    _configure_fixture_kernel(monkeypatch, kernel, payload)

    report = inspect_jpl_ephemeris()

    assert report.ready is False
    assert any(".bsp" in issue for issue in report.issues)


def test_readiness_rejects_empty_kernel(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    kernel = tmp_path / "de440s.bsp"
    kernel.write_bytes(b"")
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(kernel))

    report = inspect_jpl_ephemeris()

    assert report.ready is False
    assert any("empty" in issue for issue in report.issues)


def test_require_jpl_fails_before_skyfield_opens_missing_data(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-de440s.bsp"
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(missing))

    with pytest.raises(EphemerisUnavailableError, match="DE440s kernel is missing"):
        require_jpl_ephemeris()


def test_legacy_swiss_environment_variables_do_not_affect_jpl_readiness(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    kernel = tmp_path / "de440s.bsp"
    _configure_fixture_kernel(monkeypatch, kernel, b"test fixture")
    monkeypatch.setenv("JYOTHISYAM_SWISS_LICENSE_MODE", "unset")
    monkeypatch.setenv("JYOTHISYAM_REQUIRE_SWISS_EPHEMERIS", "true")

    assert inspect_jpl_ephemeris().ready is True
