"""Integration tests for the first astrology calculation endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _birth_payload() -> dict[str, object]:
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


def test_positions_returns_sidereal_chart_foundation() -> None:
    response = client.post("/v1/positions", json=_birth_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["request_id"].startswith("req_")
    assert payload["calculation_profile"] == "south_indian_drik_lahiri_v1"
    assert payload["time"]["timezone"] == "Asia/Kolkata"
    assert payload["time"]["utc_datetime"].startswith("1998-10-26T04:58:00")
    assert 2450000 < payload["time"]["julian_day_ut"] < 2460000
    assert 20 < payload["ayanamsha_degrees"] < 30

    assert 1 <= payload["ascendant"]["sign_index"] <= 12
    assert 1 <= payload["ascendant"]["nakshatra_index"] <= 27
    assert 1 <= payload["ascendant"]["pada"] <= 4

    planets = {planet["body"]: planet for planet in payload["planets"]}
    assert set(planets) == {
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
        "rahu",
        "ketu",
    }

    for planet in planets.values():
        assert 0 <= planet["longitude"] < 360
        assert 1 <= planet["sign_index"] <= 12
        assert 0 <= planet["degree_in_sign"] < 30
        assert 1 <= planet["nakshatra_index"] <= 27
        assert 1 <= planet["pada"] <= 4
        assert 1 <= planet["whole_sign_house"] <= 12

    rahu = planets["rahu"]["longitude"]
    ketu = planets["ketu"]["longitude"]
    assert abs(((ketu - rahu) % 360) - 180) < 1e-7

    assert payload["metadata"]["zodiac"] == "sidereal"
    assert payload["metadata"]["ayanamsha"] == "lahiri"
    assert payload["metadata"]["node_type"] == "true"
    assert payload["metadata"]["house_system"] == "whole_sign"
    assert payload["metadata"]["ephemeris_sources"]


def test_positions_rejects_unknown_timezone() -> None:
    payload = _birth_payload()
    payload["birth"]["timezone"] = "India/Not-A-Timezone"  # type: ignore[index]

    response = client.post("/v1/positions", json=payload)

    assert response.status_code == 422
    assert "Unknown IANA timezone" in response.json()["detail"]


def test_positions_rejects_ambiguous_time_without_fold() -> None:
    payload = _birth_payload()
    payload["birth"] = {
        "local_datetime": "2024-11-03T01:30:00",
        "timezone": "America/New_York",
        "latitude": 40.7128,
        "longitude": -74.006,
    }

    response = client.post("/v1/positions", json=payload)

    assert response.status_code == 422
    assert "ambiguous" in response.json()["detail"].lower()


def test_positions_accepts_ambiguous_time_with_fold() -> None:
    payload = _birth_payload()
    payload["birth"] = {
        "local_datetime": "2024-11-03T01:30:00",
        "timezone": "America/New_York",
        "latitude": 40.7128,
        "longitude": -74.006,
        "fold": 1,
    }

    response = client.post("/v1/positions", json=payload)

    assert response.status_code == 200, response.json()
    assert response.json()["time"]["fold"] == 1


def test_positions_rejects_out_of_range_coordinates() -> None:
    payload = _birth_payload()
    payload["birth"]["latitude"] = 91  # type: ignore[index]

    response = client.post("/v1/positions", json=payload)

    assert response.status_code == 422
