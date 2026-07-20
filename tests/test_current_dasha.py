"""Integration tests for the compact current Vimshottari endpoint."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
LEVELS = ("mahadasha", "antardasha", "pratyantardasha", "sookshma")


def _birth() -> dict[str, object]:
    return {
        "local_datetime": "1998-10-26T10:28:00",
        "timezone": "Asia/Kolkata",
        "latitude": 16.575,
        "longitude": 79.312,
        "altitude_meters": 120,
    }


def _payload() -> dict[str, object]:
    return {
        "birth": _birth(),
        "as_of": {
            "local_datetime": "2026-07-20T12:00:00",
            "timezone": "Asia/Kolkata",
        },
        "calculation_profile": "south_indian_drik_lahiri_v1",
    }


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_current_vimshottari_returns_only_active_nested_chain() -> None:
    response = client.post("/v1/dashas/vimshottari/current", json=_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["request_id"].startswith("req_")
    assert payload["year_length_days"] == 365.25
    assert 20 < payload["ayanamsha_degrees"] < 30

    target_utc = _parse_datetime(payload["query_time"]["utc_datetime"])
    cycle_start = _parse_datetime(payload["cycle_start_utc"])
    cycle_end = _parse_datetime(payload["cycle_end_utc"])
    assert cycle_start < target_utc < cycle_end

    periods = [payload[level] for level in LEVELS]
    for period in periods:
        start = _parse_datetime(period["start_utc"])
        end = _parse_datetime(period["end_utc"])
        assert start <= target_utc < end
        assert 1 <= period["sequence_number"] <= 9
        assert 0 <= period["progress_percent"] < 100
        assert period["elapsed_as_of_years"] + period["remaining_as_of_years"] == (
            pytest.approx(period["duration_years"], abs=3e-8)
        )

    for parent, child in zip(periods[:-1], periods[1:], strict=True):
        assert _parse_datetime(parent["start_utc"]) <= _parse_datetime(child["start_utc"])
        assert _parse_datetime(child["end_utc"]) <= _parse_datetime(parent["end_utc"])

    assert payload["metadata"]["zodiac"] == "sidereal"
    assert (
        payload["metadata"]["ayanamsha"]
        == "lahiri_chitrapaksha_spica_apparent_v1"
    )
    assert payload["metadata"]["ephemeris_sources"] == ["jpl_de440s"]


def test_current_vimshottari_matches_birth_active_full_tree() -> None:
    current_payload = {
        "birth": _birth(),
        "as_of": {
            "local_datetime": "1998-10-26T10:28:00",
            "timezone": "Asia/Kolkata",
        },
        "calculation_profile": "south_indian_drik_lahiri_v1",
    }
    current_response = client.post(
        "/v1/dashas/vimshottari/current",
        json=current_payload,
    )
    current = current_response.json()
    assert current_response.status_code == 200, current

    full_response = client.post(
        "/v1/dashas/vimshottari",
        json={
            "birth": _birth(),
            "calculation_profile": "south_indian_drik_lahiri_v1",
            "depth": "sookshma",
        },
    )
    full = full_response.json()
    assert full_response.status_code == 200, full

    mahadasha = next(item for item in full["mahadashas"] if item["active_at_birth"])
    antardasha = next(
        item for item in mahadasha["antardashas"] if item["active_at_birth"]
    )
    pratyantardasha = next(
        item
        for item in antardasha["pratyantardashas"]
        if item["active_at_birth"]
    )
    sookshma = next(
        item
        for item in pratyantardasha["sookshmadashas"]
        if item["active_at_birth"]
    )

    for level, expected in zip(
        LEVELS,
        (mahadasha, antardasha, pratyantardasha, sookshma),
        strict=True,
    ):
        actual = current[level]
        assert actual["lord"] == expected["lord"]
        assert actual["sequence_number"] == expected["sequence_number"]
        assert actual["start_utc"] == expected["start_utc"]
        assert actual["end_utc"] == expected["end_utc"]


def test_current_vimshottari_rejects_pre_birth_and_out_of_cycle_queries() -> None:
    before_birth = _payload()
    before_birth["as_of"] = {
        "local_datetime": "1990-01-01T12:00:00",
        "timezone": "Asia/Kolkata",
    }
    before_response = client.post(
        "/v1/dashas/vimshottari/current",
        json=before_birth,
    )
    assert before_response.status_code == 422
    assert "at or after the birth time" in before_response.json()["detail"]

    after_cycle = _payload()
    after_cycle["as_of"] = {
        "local_datetime": "2200-01-01T12:00:00",
        "timezone": "Asia/Kolkata",
    }
    after_response = client.post(
        "/v1/dashas/vimshottari/current",
        json=after_cycle,
    )
    assert after_response.status_code == 422
    assert "120-year" in after_response.json()["detail"]


def test_current_vimshottari_rejects_ambiguous_query_time_without_fold() -> None:
    payload = _payload()
    payload["as_of"] = {
        "local_datetime": "2024-11-03T01:30:00",
        "timezone": "America/New_York",
    }

    response = client.post("/v1/dashas/vimshottari/current", json=payload)

    assert response.status_code == 422
    assert "ambiguous" in response.json()["detail"].lower()
