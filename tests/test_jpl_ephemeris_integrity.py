"""Tests for pinned JPL ephemeris integrity reporting."""

from hashlib import sha256

from app.core.jpl_ephemeris import inspect_jpl_ephemeris, require_jpl_ephemeris
from app.core.ephemeris import EphemerisUnavailableError


def _configure_kernel(monkeypatch, path, expected_sha256: str) -> None:
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(path))
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_SHA256", expected_sha256)


def test_ephemeris_ready_when_digest_matches(tmp_path, monkeypatch) -> None:
    kernel = tmp_path / "de440s.bsp"
    payload = b"verified-test-kernel"
    kernel.write_bytes(payload)
    expected = sha256(payload).hexdigest()
    _configure_kernel(monkeypatch, kernel, expected)

    report = inspect_jpl_ephemeris()

    assert report.ready is True
    assert report.status == "ready"
    assert report.file_exists is True
    assert report.file_size_bytes == len(payload)
    assert report.expected_sha256 == expected
    assert report.actual_sha256 == expected
    assert report.integrity_verified is True
    assert report.issues == ()
    assert require_jpl_ephemeris().data_path == kernel


def test_ephemeris_rejected_when_digest_mismatches(tmp_path, monkeypatch) -> None:
    kernel = tmp_path / "de440s.bsp"
    kernel.write_bytes(b"unexpected-kernel")
    expected = sha256(b"approved-kernel").hexdigest()
    _configure_kernel(monkeypatch, kernel, expected)

    report = inspect_jpl_ephemeris()

    assert report.ready is False
    assert report.status == "degraded"
    assert report.integrity_verified is False
    assert report.actual_sha256 == sha256(b"unexpected-kernel").hexdigest()
    assert any("SHA-256 mismatch" in issue for issue in report.issues)

    try:
        require_jpl_ephemeris()
    except EphemerisUnavailableError as error:
        assert "SHA-256 mismatch" in str(error)
    else:
        raise AssertionError("require_jpl_ephemeris() accepted an unverified kernel")


def test_ephemeris_rejected_when_expected_digest_is_invalid(tmp_path, monkeypatch) -> None:
    kernel = tmp_path / "de440s.bsp"
    kernel.write_bytes(b"kernel")
    _configure_kernel(monkeypatch, kernel, "not-a-sha256")

    report = inspect_jpl_ephemeris()

    assert report.ready is False
    assert report.integrity_verified is False
    assert report.actual_sha256 is None
    assert any("64 hexadecimal characters" in issue for issue in report.issues)


def test_ephemeris_rejected_when_file_is_missing(tmp_path, monkeypatch) -> None:
    kernel = tmp_path / "de440s.bsp"
    expected = sha256(b"missing").hexdigest()
    _configure_kernel(monkeypatch, kernel, expected)

    report = inspect_jpl_ephemeris()

    assert report.ready is False
    assert report.file_exists is False
    assert report.actual_sha256 is None
    assert report.integrity_verified is False
    assert any("kernel is missing" in issue for issue in report.issues)
