"""Integration and boundary tests for the transparent strength framework."""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.engine.classical_strength import _cancellation
from app.main import app

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


def test_strength_returns_seven_unweighted_assessments() -> None:
    response = client.post(f"{BASE_PATH}/strength", json=REQUEST_BODY)
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["profile_id"] == "varahamihira_v1"
    assert payload["weights_applied"] is False
    assert payload["ranking_applied"] is False
    assert payload["cancellations_applied"] is False
    assert payload["excluded_points"] == ["rahu", "ketu"]
    assert len(payload["grahas"]) == 7
    assert payload["cancellation_policy"]["confirmed_rule_count"] == 0
    assert payload["cancellation_policy"]["cancellation_rules_enabled"] is False
    assert payload["cancellation_policy"]["supported_rule_ids"] == []
    assert payload["cancellation_policy"]["unsupported_conventions"]

    for graha in payload["grahas"]:
        assert graha["factors"]
        assert all(factor["numeric_weight"] is None for factor in graha["factors"])
        assert {
            factor["category"] for factor in graha["factors"]
        } <= {"supporting", "challenging", "contextual"}
        assert graha["cancellation"]["cancellation_applied"] is False


def test_strength_cross_checks_existing_condition_and_context_endpoints() -> None:
    strength = client.post(f"{BASE_PATH}/strength", json=REQUEST_BODY).json()
    conditions = client.post(f"{BASE_PATH}/conditions", json=REQUEST_BODY).json()
    relationships = client.post(
        f"{BASE_PATH}/relationships",
        json=REQUEST_BODY,
    ).json()
    aspects = client.post(f"{BASE_PATH}/aspects", json=REQUEST_BODY).json()
    ashtakavarga = client.post(
        f"{BASE_PATH}/ashtakavarga",
        json=REQUEST_BODY,
    ).json()
    rashis = client.get(f"{BASE_PATH}/rashis").json()["rashis"]

    conditions_by_graha = {item["graha"]: item for item in conditions["grahas"]}
    relationship_by_pair = {
        (item["source_graha"], item["target_graha"]): item
        for item in relationships["directed_relationships"]
    }
    house_by_sign = {item["sign_index"]: item for item in aspects["houses"]}
    bav_by_graha = {
        item["graha"]: item for item in ashtakavarga["bhinnashtakavargas"]
    }
    sav_by_sign = {
        item["sign_index"]: item
        for item in ashtakavarga["sarvashtakavarga"]["signs"]
    }
    rashi_by_index = {item["index"]: item for item in rashis}

    for assessment in strength["grahas"]:
        graha = assessment["graha"]
        condition = conditions_by_graha[graha]
        sign_index = condition["d1_sign_index"]
        sign_lord = rashi_by_index[sign_index]["lord"]
        house = house_by_sign[sign_index]

        assert assessment["source_longitude"] == condition["source_longitude"]
        assert assessment["dignity"] == condition["dignity"]
        assert assessment["vargottama"] == condition["vargottama"]
        assert assessment["retrograde"] == condition["retrograde"]
        assert assessment["occupied_sign_lord"] == sign_lord
        assert assessment["bhinnashtakavarga_bindus_in_occupied_sign"] == (
            bav_by_graha[graha]["bindus_by_sign"][sign_index - 1]
        )
        assert assessment["sarvashtakavarga_bindus_in_occupied_sign"] == (
            sav_by_sign[sign_index]["sarvashtakavarga_bindus"]
        )
        assert assessment["full_aspects_received"] == len(
            house["full_aspect_sources"]
        )
        assert assessment["total_fractional_aspect_weight_received"] == (
            house["total_aspect_weight"]
        )

        snapshot = assessment["sign_lord_relationship"]
        if graha == sign_lord:
            assert snapshot["self_relationship"] is True
            assert snapshot["compound_relationship"] is None
        else:
            relationship = relationship_by_pair[(graha, sign_lord)]
            assert snapshot["self_relationship"] is False
            assert snapshot["natural_relationship"] == relationship[
                "natural_relationship"
            ]
            assert snapshot["temporary_relationship"] == relationship[
                "temporary_relationship"
            ]
            assert snapshot["compound_relationship"] == relationship[
                "compound_relationship"
            ]


def test_debilitation_cancellation_is_rejected_without_registered_rule() -> None:
    result = _cancellation(
        SimpleNamespace(graha="sun", in_debilitation_sign=True)
    )

    assert result.status == "unsupported_by_profile"
    assert result.applicable is True
    assert result.cancellation_applied is False
    assert result.source_rule_id is None
    assert result.unsupported_conventions


def test_non_debilitated_graha_has_no_cancellation_candidate() -> None:
    result = _cancellation(
        SimpleNamespace(graha="sun", in_debilitation_sign=False)
    )

    assert result.status == "not_applicable"
    assert result.applicable is False
    assert result.cancellation_applied is False
    assert result.unsupported_conventions == []


def test_strength_rejects_unknown_timezone() -> None:
    request = {
        **REQUEST_BODY,
        "birth": {
            **REQUEST_BODY["birth"],
            "timezone": "Mars/Olympus_Mons",
        },
    }

    response = client.post(f"{BASE_PATH}/strength", json=request)

    assert response.status_code == 422


def test_openapi_lists_strength_endpoint() -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert f"{BASE_PATH}/strength" in paths
