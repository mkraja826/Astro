"""Tests for Varahamihira dignity and planetary-condition evaluation."""

import pytest
from fastapi.testclient import TestClient

from app.engine.classical_conditions import evaluate_dignity
from app.engine.classical_reference import get_varahamihira_grahas
from app.main import app

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1"
CLASSICAL_ORDER = [
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
]


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


def test_conditions_cross_check_existing_d1_and_reference_tables() -> None:
    response = client.post(f"{BASE_PATH}/conditions", json=_payload())
    payload = response.json()
    d1_response = client.post("/v1/charts/d1", json=_payload())
    d1 = d1_response.json()
    references = client.get(f"{BASE_PATH}/grahas").json()

    assert response.status_code == 200, payload
    assert d1_response.status_code == 200, d1
    assert payload["profile_id"] == "varahamihira_v1"
    assert payload["excluded_points"] == ["rahu", "ketu"]
    assert [item["graha"] for item in payload["grahas"]] == CLASSICAL_ORDER

    d1_points = {item["name"]: item for item in d1["points"]}
    reference_by_name = {
        item["canonical_id"]: item for item in references["grahas"]
    }

    for condition in payload["grahas"]:
        name = condition["graha"]
        point = d1_points[name]
        reference = reference_by_name[name]
        expected_d9_longitude = (condition["source_longitude"] * 9.0) % 360.0

        assert condition["source_longitude"] == point["source_longitude"]
        assert condition["d1_sign_index"] == point["sign_index"]
        assert condition["d1_degree_in_sign"] == point["degree_in_sign"]
        assert condition["d1_house"] == point["house"]
        assert condition["d9_longitude"] == pytest.approx(
            expected_d9_longitude,
            abs=1e-7,
        )
        assert condition["d9_sign_index"] == int(expected_d9_longitude // 30.0) + 1
        assert condition["own_sign"] == (
            condition["d1_sign"] in reference["owned_signs"]
        )
        assert condition["in_exaltation_sign"] == (
            condition["d1_sign"] == reference["exaltation_sign"]
        )
        assert condition["in_debilitation_sign"] == (
            condition["d1_sign"] == reference["debilitation_sign"]
        )
        assert condition["vargottama"] == (
            condition["d1_sign"] == condition["d9_sign"]
        )
        assert len(condition["evidence"]) == 7
        assert all(item["rule_id"].startswith("VM-BJ-") for item in condition["evidence"])


def test_deep_dignity_points_are_distinct_from_sign_level_dignity() -> None:
    references = {
        item.canonical_id: item for item in get_varahamihira_grahas().grahas
    }
    sun = references["sun"]

    exalted = evaluate_dignity("aries", 10.0, sun)
    assert exalted.in_exaltation_sign is True
    assert exalted.at_deep_exaltation_point is True
    assert exalted.dignity == "exaltation_sign"

    exaltation_sign_only = evaluate_dignity("aries", 11.0, sun)
    assert exaltation_sign_only.in_exaltation_sign is True
    assert exaltation_sign_only.at_deep_exaltation_point is False

    debilitated = evaluate_dignity("libra", 10.0, sun)
    assert debilitated.in_debilitation_sign is True
    assert debilitated.at_deep_debilitation_point is True
    assert debilitated.dignity == "debilitation_sign"

    own_sign = evaluate_dignity("leo", 12.0, sun)
    assert own_sign.own_sign is True
    assert own_sign.dignity == "own_sign"


def test_moon_phase_resolution_matches_sun_moon_elongation() -> None:
    response = client.post(f"{BASE_PATH}/conditions", json=_payload())
    payload = response.json()
    by_name = {item["graha"]: item for item in payload["grahas"]}

    assert response.status_code == 200, payload
    expected = (by_name["moon"]["source_longitude"] - by_name["sun"]["source_longitude"]) % 360.0
    assert payload["moon_phase"]["elongation_degrees"] == pytest.approx(
        expected,
        abs=1e-7,
    )

    if 0.0 < expected < 180.0:
        assert payload["moon_phase"]["phase"] == "waxing"
        assert payload["moon_phase"]["resolved_tendency"] == "benefic"
    elif 180.0 < expected < 360.0:
        assert payload["moon_phase"]["phase"] == "waning"
        assert payload["moon_phase"]["resolved_tendency"] == "malefic"

    assert by_name["moon"]["resolved_tendency"] == payload["moon_phase"][
        "resolved_tendency"
    ]


def test_mercury_association_uses_same_sign_classical_grahas_only() -> None:
    response = client.post(f"{BASE_PATH}/conditions", json=_payload())
    payload = response.json()
    by_name = {item["graha"]: item for item in payload["grahas"]}
    mercury = by_name["mercury"]
    expected = [
        name
        for name in CLASSICAL_ORDER
        if name != "mercury" and by_name[name]["d1_sign"] == mercury["d1_sign"]
    ]

    assert response.status_code == 200, payload
    association = payload["mercury_association"]
    assert association["associated_grahas"] == expected
    assert mercury["associations"] == expected
    assert "rahu" not in expected
    assert "ketu" not in expected

    categorized = (
        association["benefic_associations"]
        + association["malefic_associations"]
        + association["conditional_associations"]
    )
    assert sorted(categorized) == sorted(expected)
    assert mercury["resolved_tendency"] == association["resolved_tendency"]


def test_conditions_reject_unknown_timezone() -> None:
    payload = _payload()
    payload["birth"]["timezone"] = "India/Not-A-Timezone"  # type: ignore[index]

    response = client.post(f"{BASE_PATH}/conditions", json=payload)

    assert response.status_code == 422
    assert "Unknown IANA timezone" in response.json()["detail"]
