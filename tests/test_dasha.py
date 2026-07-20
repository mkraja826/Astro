"""Integration tests for the Vimshottari Dasha endpoint."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

LORDS = [
    "ketu",
    "venus",
    "sun",
    "moon",
    "mars",
    "rahu",
    "jupiter",
    "saturn",
    "mercury",
]

YEARS = {
    "ketu": 7.0,
    "venus": 20.0,
    "sun": 6.0,
    "moon": 10.0,
    "mars": 7.0,
    "rahu": 18.0,
    "jupiter": 16.0,
    "saturn": 19.0,
    "mercury": 17.0,
}


def _payload() -> dict[str, object]:
    return {
        "birth": {
            "local_datetime": "1998-10-26T10:28:00",
            "timezone": "Asia/Kolkata",
            "latitude": 16.575,
            "longitude": 79.312,
            "altitude_meters": 120,
        },
        "calculation_profile": "south_indian_drik_lahiri_v1",
    }


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_vimshottari_returns_complete_birth_cycle() -> None:
    response = client.post("/v1/dashas/vimshottari", json=_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["request_id"].startswith("req_")
    assert payload["cycle_years"] == 120.0
    assert payload["year_length_days"] == 365.25
    assert 20 < payload["ayanamsha_degrees"] < 30

    moon = payload["moon"]
    assert 1 <= moon["nakshatra_index"] <= 27
    assert 1 <= moon["pada"] <= 4
    assert 0 <= moon["progress_percent"] < 100

    expected_lord = LORDS[(moon["nakshatra_index"] - 1) % len(LORDS)]
    assert payload["birth_lord"] == expected_lord

    periods = payload["mahadashas"]
    assert len(periods) == 9
    assert sum(period["duration_years"] for period in periods) == 120.0

    expected_sequence = [
        LORDS[(LORDS.index(expected_lord) + offset) % len(LORDS)]
        for offset in range(9)
    ]
    assert [period["lord"] for period in periods] == expected_sequence

    first = periods[0]
    birth_utc = _parse_datetime(payload["time"]["utc_datetime"])
    assert first["active_at_birth"] is True
    assert _parse_datetime(first["start_utc"]) <= birth_utc
    assert birth_utc < _parse_datetime(first["end_utc"])
    assert first["duration_years"] == YEARS[expected_lord]
    assert first["remaining_at_birth_years"] == pytest.approx(
        payload["birth_balance_years"], abs=1e-9
    )
    assert (
        first["elapsed_at_birth_years"] + first["remaining_at_birth_years"]
        == pytest.approx(first["duration_years"], abs=1e-8)
    )

    for current, following in zip(periods[:-1], periods[1:], strict=True):
        assert current["end_utc"] == following["start_utc"]
        assert following["active_at_birth"] is False
        assert following["elapsed_at_birth_years"] is None
        assert following["remaining_at_birth_years"] is None

    assert payload["metadata"]["zodiac"] == "sidereal"
    assert payload["metadata"]["ayanamsha"] == "lahiri"
    assert payload["metadata"]["ephemeris_sources"]


def test_vimshottari_rejects_unknown_timezone() -> None:
    payload = _payload()
    payload["birth"]["timezone"] = "India/Not-A-Timezone"  # type: ignore[index]

    response = client.post("/v1/dashas/vimshottari", json=payload)

    assert response.status_code == 422
    assert "Unknown IANA timezone" in response.json()["detail"]


def test_vimshottari_rejects_ambiguous_time_without_fold() -> None:
    payload = _payload()
    payload["birth"] = {
        "local_datetime": "2024-11-03T01:30:00",
        "timezone": "America/New_York",
        "latitude": 40.7128,
        "longitude": -74.006,
    }

    response = client.post("/v1/dashas/vimshottari", json=payload)

    assert response.status_code == 422
    assert "ambiguous" in response.json()["detail"].lower()
