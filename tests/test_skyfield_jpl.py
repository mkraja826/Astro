"""Tests for the Skyfield/JPL DE440s provider foundation."""

from datetime import UTC, datetime
from math import radians
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.engine.positions import _calculate_swiss_positions, calculate_positions
from app.engine.skyfield_jpl import (
    SkyfieldJplProvider,
    _ascendant_from_sidereal_time,
    _julian_day_utc,
    _signed_angular_difference,
)
from app.main import app
from app.schemas.positions import PositionsRequest

client = TestClient(app)
PROFILE = "south_indian_drik_lahiri_skyfield_de440s_v1"


def _payload() -> dict[str, object]:
    return {
        "birth": {
            "local_datetime": "1998-10-26T10:28:00",
            "timezone": "Asia/Kolkata",
            "latitude": 16.575,
            "longitude": 79.312,
            "altitude_meters": 120,
        },
        "calculation_profile": PROFILE,
    }


def test_skyfield_profile_dispatches_to_the_new_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    request = PositionsRequest.model_validate(_payload())
    sentinel = object()

    monkeypatch.setattr(
        SkyfieldJplProvider,
        "calculate",
        lambda _self, _request: sentinel,
    )

    assert calculate_positions(request) is sentinel


def test_julian_day_converter_matches_j2000_noon() -> None:
    instant = datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC)

    assert _julian_day_utc(instant) == pytest.approx(2451545.0, abs=1e-9)


def test_signed_angular_difference_handles_zero_crossing() -> None:
    assert _signed_angular_difference(1.0, 359.0) == pytest.approx(2.0)
    assert _signed_angular_difference(359.0, 1.0) == pytest.approx(-2.0)


def test_ascendant_helper_selects_the_eastern_horizon_intersection() -> None:
    obliquity = radians(23.4393)

    assert _ascendant_from_sidereal_time(0.0, 0.0, obliquity) == pytest.approx(90.0)
    assert _ascendant_from_sidereal_time(6.0, 0.0, obliquity) == pytest.approx(180.0)


def test_jpl_health_is_degraded_when_kernel_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-de440s.bsp"
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(missing))

    response = client.get("/health/ephemeris/jpl")
    payload = response.json()

    assert response.status_code == 503
    assert payload["ready"] is False
    assert payload["provider"] == "skyfield_jpl"
    assert payload["model"] == "de440s"
    assert payload["automatic_download_enabled"] is False
    assert payload["file_exists"] is False
    assert payload["issues"]


def test_positions_fail_clearly_when_jpl_kernel_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-de440s.bsp"
    monkeypatch.setenv("JYOTHISYAM_JPL_EPHEMERIS_PATH", str(missing))

    response = client.post("/v1/positions", json=_payload())

    assert response.status_code == 503
    assert "DE440s kernel is missing" in response.json()["detail"]


def test_provider_comparison_route_is_additive_and_does_not_change_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        SkyfieldJplProvider,
        "calculate",
        lambda _self, request: _calculate_swiss_positions(request),
    )

    response = client.post(
        "/v1/positions/providers/compare",
        json={"birth": _payload()["birth"]},
    )
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["passed"] is True
    assert payload["compared_point_count"] == 9
    assert payload["longitude_match_count"] == 9
    assert payload["sign_match_count"] == 9
    assert payload["retrograde_match_count"] == 9
    assert payload["production_default_changed"] is False


def test_panchanga_rejects_unmigrated_jpl_profile() -> None:
    response = client.post(
        "/v1/panchanga",
        json={
            "location": {
                "local_date": "2026-07-21",
                "timezone": "Asia/Kolkata",
                "latitude": 16.575,
                "longitude": 79.312,
                "altitude_meters": 120,
            },
            "calculation_profile": PROFILE,
        },
    )

    assert response.status_code == 422
    assert "Skyfield/JPL Panchanga is not implemented yet" in str(response.json())
