"""Integration tests for the sunrise-based Panchanga endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PROFILE = "south_indian_drik_lahiri_jpl_de440s_v1"


def _payload() -> dict[str, object]:
    return {
        "location": {
            "local_date": "2026-07-20",
            "timezone": "Asia/Kolkata",
            "latitude": 16.575,
            "longitude": 79.312,
            "altitude_meters": 120,
        },
        "calculation_profile": PROFILE,
    }


def test_panchanga_returns_five_limbs_at_geometric_sunrise() -> None:
    response = client.post("/v1/panchanga", json=_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["request_id"].startswith("req_")
    assert payload["calculation_profile"] == PROFILE
    assert payload["local_date"] == "2026-07-20"
    assert payload["timezone"] == "Asia/Kolkata"
    assert payload["vara"]["name"] == "Somavara"

    sunrise = payload["solar_times"]["sunrise_local"]
    sunset = payload["solar_times"]["sunset_local"]
    assert sunrise.startswith("2026-07-20T")
    assert sunset.startswith("2026-07-20T")
    assert payload["evaluated_at_local"] == sunrise
    assert "0 degrees, no refraction" in payload["solar_times"]["method"]

    assert 1 <= payload["tithi"]["index"] <= 30
    assert payload["tithi"]["paksha"] in {"Shukla", "Krishna"}
    assert 1 <= payload["nakshatra"]["index"] <= 27
    assert 1 <= payload["nakshatra"]["pada"] <= 4
    assert 1 <= payload["yoga"]["index"] <= 27
    assert 1 <= payload["karana"]["index"] <= 60

    for key in ("tithi", "nakshatra", "yoga", "karana"):
        assert 0 <= payload[key]["progress_percent"] < 100

    assert 20 < payload["ayanamsha_degrees"] < 30
    metadata = payload["metadata"]
    assert metadata["astronomical_provider"] == "skyfield_jpl"
    assert metadata["ephemeris_model"] == "de440s"
    assert metadata["swiss_ephemeris_version"] is None
    assert metadata["zodiac"] == "sidereal"
    assert metadata["ayanamsha"] == "lahiri_chitrapaksha_spica_apparent_v1"
    assert metadata["ephemeris_sources"] == ["jpl_de440s"]


def test_panchanga_accepts_legacy_profile_alias() -> None:
    payload = _payload()
    payload["calculation_profile"] = "south_indian_drik_lahiri_v1"

    response = client.post("/v1/panchanga", json=payload)

    assert response.status_code == 200, response.json()
    assert response.json()["metadata"]["astronomical_provider"] == "skyfield_jpl"


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


def test_panchanga_reports_polar_night_without_fabricating_sunrise() -> None:
    payload = _payload()
    payload["location"] = {
        "local_date": "2005-12-21",
        "timezone": "Europe/Oslo",
        "latitude": 69.6492,
        "longitude": 18.9553,
        "altitude_meters": 10,
    }

    response = client.post("/v1/panchanga", json=payload)

    assert response.status_code == 422
    assert "Sunrise is unavailable" in response.json()["detail"]


def test_openapi_lists_panchanga_endpoint() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/v1/panchanga" in response.json()["paths"]
