"""Tests for Varahamihira fractional aspects and whole-sign house influence."""

from collections import defaultdict
from itertools import combinations

import pytest
from fastapi.testclient import TestClient

from app.engine.classical_aspects import (
    aspect_specifications_for_graha,
    target_sign_index,
)
from app.main import app

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1"
CLASSICAL_GRAHAS = {
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
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


def test_general_fractional_aspect_table_matches_brihat_jataka_2_13() -> None:
    specifications = aspect_specifications_for_graha("sun")
    actual = {
        specification.relative_house: (
            specification.strength_fraction,
            specification.strength_label.value,
            specification.is_special_full,
        )
        for specification in specifications
    }

    assert actual == {
        3: (0.25, "quarter", False),
        4: (0.75, "three_quarters", False),
        5: (0.5, "half", False),
        7: (1.0, "full", False),
        8: (0.75, "three_quarters", False),
        9: (0.5, "half", False),
        10: (0.25, "quarter", False),
    }


def test_mars_jupiter_and_saturn_special_aspects_are_full() -> None:
    expected = {
        "mars": {4, 8},
        "jupiter": {5, 9},
        "saturn": {3, 10},
    }

    for graha, special_houses in expected.items():
        specifications = aspect_specifications_for_graha(graha)
        actual_specials = {
            specification.relative_house
            for specification in specifications
            if specification.is_special_full
        }
        assert actual_specials == special_houses
        for specification in specifications:
            if specification.relative_house in special_houses:
                assert specification.strength_fraction == 1.0
                assert specification.strength_label.value == "full"
                assert "VM-BJ-C02-SPECIAL-ASPECT-EVAL-001" in specification.rule_ids


def test_target_sign_counting_is_inclusive_and_wraps() -> None:
    assert target_sign_index(1, 3) == 3
    assert target_sign_index(1, 7) == 7
    assert target_sign_index(10, 3) == 12
    assert target_sign_index(10, 4) == 1
    assert target_sign_index(12, 10) == 9

    with pytest.raises(ValueError):
        target_sign_index(0, 7)
    with pytest.raises(ValueError):
        target_sign_index(1, 13)


def test_aspects_endpoint_returns_complete_fractional_matrix() -> None:
    d1_response = client.post("/v1/charts/d1", json=_payload())
    response = client.post(f"{BASE_PATH}/aspects", json=_payload())
    d1 = d1_response.json()
    payload = response.json()

    assert d1_response.status_code == 200, d1
    assert response.status_code == 200, payload
    assert payload["profile_id"] == "varahamihira_v1"
    assert payload["excluded_points"] == ["rahu", "ketu"]
    assert len(payload["aspects"]) == 49
    assert len(payload["houses"]) == 12

    d1_points = {
        point["name"]: point
        for point in d1["points"]
        if point["name"] in CLASSICAL_GRAHAS
    }
    ascendant_sign_index = d1["ascendant"]["sign_index"]
    by_source: dict[str, list[dict[str, object]]] = defaultdict(list)
    for aspect in payload["aspects"]:
        by_source[aspect["source_graha"]].append(aspect)
        expected_target_sign = target_sign_index(
            aspect["source_sign_index"],
            aspect["relative_house"],
        )
        expected_target_house = (
            (expected_target_sign - ascendant_sign_index) % 12
        ) + 1
        assert aspect["target_sign_index"] == expected_target_sign
        assert aspect["target_house"] == expected_target_house

        expected_targets = sorted(
            name
            for name, point in d1_points.items()
            if point["sign_index"] == expected_target_sign
        )
        assert sorted(aspect["target_grahas"]) == expected_targets

    assert set(by_source) == CLASSICAL_GRAHAS
    assert all(len(aspects) == 7 for aspects in by_source.values())
    assert sum(aspect["is_special_full"] for aspect in payload["aspects"]) == 6
    assert sum(
        aspect["strength_fraction"] == 1.0 for aspect in payload["aspects"]
    ) == 13


def test_conjunction_pairs_match_same_sign_classical_occupancy() -> None:
    d1 = client.post("/v1/charts/d1", json=_payload()).json()
    response = client.post(f"{BASE_PATH}/aspects", json=_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    occupants: dict[int, list[str]] = defaultdict(list)
    for point in d1["points"]:
        if point["name"] in CLASSICAL_GRAHAS:
            occupants[point["sign_index"]].append(point["name"])

    expected_pairs = {
        tuple(sorted(pair))
        for names in occupants.values()
        for pair in combinations(names, 2)
    }
    actual_pairs = {
        tuple(sorted(conjunction["grahas"]))
        for conjunction in payload["conjunctions"]
    }
    assert actual_pairs == expected_pairs
    assert all(
        conjunction["angular_separation_degrees"] <= 30.0
        for conjunction in payload["conjunctions"]
    )


def test_house_influence_matches_lords_occupants_and_received_aspects() -> None:
    d1 = client.post("/v1/charts/d1", json=_payload()).json()
    rashis = client.get(f"{BASE_PATH}/rashis").json()["rashis"]
    response = client.post(f"{BASE_PATH}/aspects", json=_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    rashi_by_index = {rashi["index"]: rashi for rashi in rashis}
    point_by_name = {
        point["name"]: point
        for point in d1["points"]
        if point["name"] in CLASSICAL_GRAHAS
    }
    ascendant_sign_index = d1["ascendant"]["sign_index"]

    for house in payload["houses"]:
        house_number = house["house"]
        expected_sign_index = (
            (ascendant_sign_index + house_number - 2) % 12
        ) + 1
        rashi = rashi_by_index[expected_sign_index]
        lord_point = point_by_name[rashi["lord"]]
        received = [
            aspect
            for aspect in payload["aspects"]
            if aspect["target_house"] == house_number
        ]

        assert house["sign_index"] == expected_sign_index
        assert house["sign"] == rashi["canonical_id"]
        assert house["contains_ascendant"] is (house_number == 1)
        assert house["lord"] == rashi["lord"]
        assert house["lord_placement_house"] == lord_point["house"]
        assert len(house["aspects_received"]) == len(received)
        assert house["total_aspect_weight"] == pytest.approx(
            sum(aspect["strength_fraction"] for aspect in received),
            abs=1e-8,
        )
        assert house["full_aspect_sources"] == sorted(
            aspect["source_graha"]
            for aspect in received
            if aspect["strength_fraction"] == 1.0
        )


def test_aspects_reject_unknown_timezone() -> None:
    payload = _payload()
    payload["birth"]["timezone"] = "India/Not-A-Timezone"  # type: ignore[index]

    response = client.post(f"{BASE_PATH}/aspects", json=payload)

    assert response.status_code == 422
    assert "Unknown IANA timezone" in response.json()["detail"]
