"""Integration tests for the sunrise-based Panchanga endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _payload() -> dict[str, object]:
    return {
        "location": {
            "local_date": "2026-07-20",
            "timezone": "Asia/Kolkata",
            "latitude": 16.575,
            "longitude": 79.312,
            "altitude_meters": 120,
        },
        "calculation_profile": "south_indian_drik_lahiri_v1",
    }


def test_panchanga_returns_five_limbs_at_sunrise() -> None:
    response = client.post("/v1/panchanga", json=_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["request_id"].startswith("req_")
    assert payload["local_date"] == "2026-07-20"
    assert payload["timezone"] == "Asia/Kolkata"
    assert payload["vara"]["name"] == "Somavara"

    sunrise = payload["solar_times"]["sunrise_local"]
    sunset = payload["solar_times"]["sunset_local"]
    assert sunrise.startswith("2026-07-20T")
    assert sunset.startswith("2026-07-20T")
    assert payload["evaluated_at_local"] == sunrise

    assert 1 <= payload["tithi"]["index"] <= 30
    assert payload["tithi"]["paksha"] in {"Shukla", "Krishna"}
    assert 1 <= payload["nakshatra"]["index"] <= 27
    assert 1 <= payload["nakshatra"]["pada"] <= 4
    assert 1 <= payload["yoga"]["index"] <= 27
    assert 1 <= payload["karana"]["index"] <= 60

    for key in ("tithi", "nakshatra", "yoga", "karana"):
        assert 0 <= payload[key]["progress_percent"] < 100

    assert 20 < payload["ayanamsha_degrees"] < 30
    assert payload["metadata"]["zodiac"] == "sidereal"
    assert payload["metadata"]["ayanamsha"] == "lahiri"
    assert payload["metadata"]["ephemeris_sources"]


def test_panchanga_rejects_unknown_timezone() -> None:
    payload = _payload()
    payload["location"]["timezone"] = "India/Not-A-Timezone"  # type: ignore[index]

    response = client.post("/v1/panchanga", json=payload)

    assert response.status_code == 422
    assert "Unknown IANA timezone" in response.json()["detail"]


def test_panchanga_rejects_out_of_range_coordinates() -> None:
    payload = _payload()
    payload["location"]["longitude"] = 181  # type: ignore[index]

    response = client.post("/v1/panchanga", json=payload)

    assert response.status_code == 422


def test_openapi_lists_panchanga_endpoint() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/v1/panchanga" in response.json()["paths"]
