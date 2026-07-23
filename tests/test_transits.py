"""Tests for deterministic, non-interpretive transit snapshots."""

from fastapi.testclient import TestClient

from app.engine.transits import _whole_sign_distance
from app.main import app

client = TestClient(app)
PROFILE = "south_indian_drik_lahiri_jpl_de440s_v1"


def _payload() -> dict[str, object]:
    return {
        "birth": {
            "local_datetime": "1998-10-26T10:28:00",
            "timezone": "Asia/Kolkata",
            "latitude": 16.575,
            "longitude": 79.312,
            "altitude_meters": 120,
        },
        "as_of": {
            "local_datetime": "2026-07-23T12:00:00",
            "timezone": "Asia/Kolkata",
        },
        "calculation_profile": PROFILE,
    }


def test_whole_sign_distance_is_inclusive_and_wraps() -> None:
    assert _whole_sign_distance(1, 1) == 1
    assert _whole_sign_distance(1, 7) == 7
    assert _whole_sign_distance(12, 1) == 2
    assert _whole_sign_distance(2, 1) == 12


def test_transit_snapshot_reuses_jpl_positions_without_interpreting_them() -> None:
    response = client.post("/v1/transits/snapshot", json=_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["request_id"].startswith("req_")
    assert payload["calculation_profile"] == PROFILE
    assert payload["natal"]["time"]["utc_datetime"].startswith("1998-10-26T04:58:00")
    assert payload["transit"]["time"]["utc_datetime"].startswith("2026-07-23T06:30:00")
    assert payload["natal"]["metadata"]["ephemeris_model"] == "de440s"
    assert payload["transit"]["metadata"]["ephemeris_model"] == "de440s"
    assert payload["interpretation_applied"] is False
    assert payload["timing_window_applied"] is False

    natal = {point["body"]: point for point in payload["natal"]["planets"]}
    transit = {point["body"]: point for point in payload["transit"]["planets"]}
    relations = {item["body"]: item for item in payload["relations"]}
    assert set(relations) == set(natal) == set(transit)

    natal_moon_sign = natal["moon"]["sign_index"]
    natal_ascendant_sign = payload["natal"]["ascendant"]["sign_index"]
    for body, relation in relations.items():
        transit_sign = transit[body]["sign_index"]
        assert relation["natal_sign_index"] == natal[body]["sign_index"]
        assert relation["transit_sign_index"] == transit_sign
        assert relation["whole_sign_distance_from_natal_position"] == (
            (transit_sign - natal[body]["sign_index"]) % 12
        ) + 1
        assert relation["whole_sign_house_from_natal_ascendant"] == (
            (transit_sign - natal_ascendant_sign) % 12
        ) + 1
        assert relation["whole_sign_house_from_natal_moon"] == (
            (transit_sign - natal_moon_sign) % 12
        ) + 1


def test_transit_snapshot_rejects_unknown_as_of_timezone() -> None:
    payload = _payload()
    payload["as_of"]["timezone"] = "India/Not-A-Timezone"  # type: ignore[index]

    response = client.post("/v1/transits/snapshot", json=payload)

    assert response.status_code == 422
    assert "Unknown IANA timezone" in response.json()["detail"]


def test_openapi_lists_transit_snapshot() -> None:
    assert "/v1/transits/snapshot" in app.openapi()["paths"]
