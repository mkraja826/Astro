"""Integration tests for D1 Rasi and D9 Navamsa charts."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

EXPECTED_GRID = {
    1: (1, 2),
    2: (1, 3),
    3: (1, 4),
    4: (2, 4),
    5: (3, 4),
    6: (4, 4),
    7: (4, 3),
    8: (4, 2),
    9: (4, 1),
    10: (3, 1),
    11: (2, 1),
    12: (1, 1),
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


def _points_by_name(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {item["name"]: item for item in payload["points"]}  # type: ignore[index]


def test_d1_returns_south_indian_rasi_chart() -> None:
    response = client.post("/v1/charts/d1", json=_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["chart_type"] == "d1_rasi"
    assert payload["division"] == 1
    assert payload["ascendant"]["house"] == 1
    assert len(payload["points"]) == 9
    assert len(payload["signs"]) == 12

    occupants: list[str] = []
    for cell in payload["signs"]:
        sign_index = cell["sign_index"]
        assert (cell["grid_row"], cell["grid_column"]) == EXPECTED_GRID[sign_index]
        expected_house = ((sign_index - payload["ascendant"]["sign_index"]) % 12) + 1
        assert cell["house_from_lagna"] == expected_house
        occupants.extend(cell["occupants"])

    assert sorted(occupants) == sorted(
        [
            "ascendant",
            "sun",
            "moon",
            "mars",
            "mercury",
            "jupiter",
            "venus",
            "saturn",
            "rahu",
            "ketu",
        ]
    )

    assert payload["ascendant"]["chart_longitude"] == pytest.approx(
        payload["ascendant"]["source_longitude"], abs=1e-8
    )
    for point in payload["points"]:
        assert point["chart_longitude"] == pytest.approx(
            point["source_longitude"], abs=1e-8
        )

    points = _points_by_name(payload)
    node_separation = (
        points["ketu"]["chart_longitude"] - points["rahu"]["chart_longitude"]
    ) % 360
    assert node_separation == pytest.approx(180.0, abs=1e-7)
    assert payload["metadata"]["zodiac"] == "sidereal"
    assert payload["metadata"]["ayanamsha"] == "lahiri"
    assert payload["metadata"]["house_system"] == "whole_sign_divisional"


def test_d9_uses_parashari_navamsa_mapping() -> None:
    d1_response = client.post("/v1/charts/d1", json=_payload())
    d9_response = client.post("/v1/charts/d9", json=_payload())
    d1 = d1_response.json()
    d9 = d9_response.json()

    assert d1_response.status_code == 200, d1
    assert d9_response.status_code == 200, d9
    assert d9["chart_type"] == "d9_navamsa"
    assert d9["division"] == 9
    assert d9["ascendant"]["house"] == 1

    assert d9["ascendant"]["source_longitude"] == d1["ascendant"]["source_longitude"]
    assert d9["ascendant"]["chart_longitude"] == pytest.approx(
        (d9["ascendant"]["source_longitude"] * 9.0) % 360.0,
        abs=1e-7,
    )

    d1_points = _points_by_name(d1)
    d9_points = _points_by_name(d9)
    assert set(d9_points) == set(d1_points)

    for name, point in d9_points.items():
        assert point["source_longitude"] == d1_points[name]["source_longitude"]
        expected_longitude = (point["source_longitude"] * 9.0) % 360.0
        assert point["chart_longitude"] == pytest.approx(expected_longitude, abs=1e-7)
        assert point["sign_index"] == int(expected_longitude // 30.0) + 1
        expected_house = (
            (point["sign_index"] - d9["ascendant"]["sign_index"]) % 12
        ) + 1
        assert point["house"] == expected_house

    node_separation = (
        d9_points["ketu"]["chart_longitude"]
        - d9_points["rahu"]["chart_longitude"]
    ) % 360
    assert node_separation == pytest.approx(180.0, abs=1e-7)


def test_chart_rejects_unknown_timezone() -> None:
    payload = _payload()
    payload["birth"]["timezone"] = "India/Not-A-Timezone"  # type: ignore[index]

    response = client.post("/v1/charts/d1", json=payload)

    assert response.status_code == 422
    assert "Unknown IANA timezone" in response.json()["detail"]
