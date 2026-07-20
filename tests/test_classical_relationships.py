"""Integration and invariant tests for Brihat Jataka planetary relationships."""

from fastapi.testclient import TestClient

from app.engine.classical_relationships import (
    CLASSICAL_GRAHAS,
    TEMPORARY_FRIEND_HOUSES,
    compound_relationship,
)
from app.main import app
from app.schemas.classical_relationships import (
    CompoundRelationship,
    NaturalRelationship,
    TemporaryRelationship,
)

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1"

REQUEST_BODY = {
    "birth": {
        "local_datetime": "1998-10-26T10:28:00",
        "timezone": "Asia/Kolkata",
        "latitude": 16.575,
        "longitude": 79.312,
        "altitude_meters": 120,
    },
    "calculation_profile": "south_indian_drik_lahiri_v1",
}

EXPECTED_NATURAL = {
    "sun": {
        "moon": "friend",
        "mars": "friend",
        "mercury": "neutral",
        "jupiter": "friend",
        "venus": "enemy",
        "saturn": "enemy",
    },
    "moon": {
        "sun": "friend",
        "mars": "neutral",
        "mercury": "friend",
        "jupiter": "neutral",
        "venus": "neutral",
        "saturn": "neutral",
    },
    "mars": {
        "sun": "friend",
        "moon": "friend",
        "mercury": "enemy",
        "jupiter": "friend",
        "venus": "neutral",
        "saturn": "neutral",
    },
    "mercury": {
        "sun": "friend",
        "moon": "enemy",
        "mars": "neutral",
        "jupiter": "neutral",
        "venus": "friend",
        "saturn": "neutral",
    },
    "jupiter": {
        "sun": "friend",
        "moon": "friend",
        "mars": "friend",
        "mercury": "enemy",
        "venus": "enemy",
        "saturn": "neutral",
    },
    "venus": {
        "sun": "enemy",
        "moon": "enemy",
        "mars": "neutral",
        "mercury": "friend",
        "jupiter": "neutral",
        "saturn": "friend",
    },
    "saturn": {
        "sun": "enemy",
        "moon": "enemy",
        "mars": "enemy",
        "mercury": "friend",
        "jupiter": "neutral",
        "venus": "friend",
    },
}


def test_relationship_endpoint_returns_complete_matrices() -> None:
    response = client.post(f"{BASE_PATH}/relationships", json=REQUEST_BODY)
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["profile_id"] == "varahamihira_v1"
    assert payload["excluded_points"] == ["rahu", "ketu"]
    assert payload["scoring_applied"] is False
    assert len(payload["positions"]) == 7
    assert len(payload["directed_relationships"]) == 42
    assert len(payload["mutual_pairs"]) == 21
    assert [position["graha"] for position in payload["positions"]] == list(
        CLASSICAL_GRAHAS
    )


def test_natural_relationship_table_matches_verses_216_and_217() -> None:
    payload = client.post(f"{BASE_PATH}/relationships", json=REQUEST_BODY).json()
    actual = {
        (item["source_graha"], item["target_graha"]): item[
            "natural_relationship"
        ]
        for item in payload["directed_relationships"]
    }

    for source, targets in EXPECTED_NATURAL.items():
        for target, expected in targets.items():
            assert actual[(source, target)] == expected


def test_positions_and_relative_houses_match_d1_chart() -> None:
    relationships = client.post(
        f"{BASE_PATH}/relationships",
        json=REQUEST_BODY,
    ).json()
    d1 = client.post("/v1/charts/d1", json=REQUEST_BODY).json()
    d1_points = {point["name"]: point for point in d1["points"]}
    positions = {item["graha"]: item for item in relationships["positions"]}

    for graha in CLASSICAL_GRAHAS:
        assert positions[graha]["source_longitude"] == d1_points[graha][
            "source_longitude"
        ]
        assert positions[graha]["sign_index"] == d1_points[graha]["sign_index"]
        assert positions[graha]["house"] == d1_points[graha]["house"]

    for item in relationships["directed_relationships"]:
        source_index = positions[item["source_graha"]]["sign_index"]
        target_index = positions[item["target_graha"]]["sign_index"]
        expected_house = ((target_index - source_index) % 12) + 1
        assert item["target_relative_house"] == expected_house
        expected_temporary = (
            "friend" if expected_house in TEMPORARY_FRIEND_HOUSES else "enemy"
        )
        assert item["temporary_relationship"] == expected_temporary


def test_temporary_relationship_is_symmetric_for_all_pairs() -> None:
    payload = client.post(f"{BASE_PATH}/relationships", json=REQUEST_BODY).json()
    directed = {
        (item["source_graha"], item["target_graha"]): item
        for item in payload["directed_relationships"]
    }

    for pair in payload["mutual_pairs"]:
        a_to_b = directed[(pair["graha_a"], pair["graha_b"])]
        b_to_a = directed[(pair["graha_b"], pair["graha_a"])]
        assert a_to_b["temporary_relationship"] == b_to_a[
            "temporary_relationship"
        ]
        assert pair["temporary_relationship"] == a_to_b[
            "temporary_relationship"
        ]
        assert pair["a_to_b_compound"] == a_to_b["compound_relationship"]
        assert pair["b_to_a_compound"] == b_to_a["compound_relationship"]
        assert (
            pair["a_relative_house_from_b"]
            == b_to_a["target_relative_house"]
        )
        assert (
            pair["b_relative_house_from_a"]
            == a_to_b["target_relative_house"]
        )


def test_all_six_compound_combinations_are_fixed() -> None:
    expected = {
        (NaturalRelationship.FRIEND, TemporaryRelationship.FRIEND): (
            CompoundRelationship.GREAT_FRIEND
        ),
        (NaturalRelationship.FRIEND, TemporaryRelationship.ENEMY): (
            CompoundRelationship.NEUTRAL
        ),
        (NaturalRelationship.NEUTRAL, TemporaryRelationship.FRIEND): (
            CompoundRelationship.FRIEND
        ),
        (NaturalRelationship.NEUTRAL, TemporaryRelationship.ENEMY): (
            CompoundRelationship.ENEMY
        ),
        (NaturalRelationship.ENEMY, TemporaryRelationship.FRIEND): (
            CompoundRelationship.NEUTRAL
        ),
        (NaturalRelationship.ENEMY, TemporaryRelationship.ENEMY): (
            CompoundRelationship.GREAT_ENEMY
        ),
    }

    for inputs, result in expected.items():
        assert compound_relationship(*inputs) == result


def test_relationship_endpoint_rejects_unknown_timezone() -> None:
    request = {
        **REQUEST_BODY,
        "birth": {
            **REQUEST_BODY["birth"],
            "timezone": "Mars/Olympus_Mons",
        },
    }
    response = client.post(f"{BASE_PATH}/relationships", json=request)

    assert response.status_code == 422


def test_openapi_lists_relationship_route() -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert f"{BASE_PATH}/relationships" in paths
