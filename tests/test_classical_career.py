"""Integration and invariant tests for Chapter 10 Karmājīva analysis."""

from fastapi.testclient import TestClient

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

CLASSICAL_GRAHAS = {
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
}


def _tenth_sign_index(reference_sign_index: int) -> int:
    return ((reference_sign_index + 8) % 12) + 1


def test_career_returns_three_unweighted_karmājīva_channels() -> None:
    response = client.post(f"{BASE_PATH}/career", json=REQUEST_BODY)
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["profile_id"] == "varahamihira_v1"
    assert payload["ranking_applied"] is False
    assert payload["primary_indicator"] is None
    assert payload["excluded_points"] == ["rahu", "ketu"]
    assert [channel["reference_point"] for channel in payload["channels"]] == [
        "lagna",
        "moon",
        "sun",
    ]
    assert len(payload["channels"]) == 3
    assert 1 <= len(payload["candidates"]) <= 3

    for channel in payload["channels"]:
        assert channel["karmājīva_indicator_graha"] in CLASSICAL_GRAHAS
        assert channel["vocation_themes"]
        assert channel["indicator_condition"]["graha"] == (
            channel["karmājīva_indicator_graha"]
        )
        assert len(channel["evidence"]) == 4


def test_channel_derivations_match_d1_and_reference_tables() -> None:
    career = client.post(f"{BASE_PATH}/career", json=REQUEST_BODY).json()
    d1 = client.post("/v1/charts/d1", json=REQUEST_BODY).json()
    rashis = client.get(f"{BASE_PATH}/rashis").json()["rashis"]

    rashi_by_index = {rashi["index"]: rashi for rashi in rashis}
    rashi_by_english = {
        rashi["english_name"].lower(): rashi["canonical_id"] for rashi in rashis
    }
    point_by_name = {point["name"]: point for point in d1["points"]}
    reference_indices = {
        "lagna": d1["ascendant"]["sign_index"],
        "moon": point_by_name["moon"]["sign_index"],
        "sun": point_by_name["sun"]["sign_index"],
    }

    for channel in career["channels"]:
        reference_index = reference_indices[channel["reference_point"]]
        tenth_index = _tenth_sign_index(reference_index)
        tenth_lord = rashi_by_index[tenth_index]["lord"]
        tenth_lord_point = point_by_name[tenth_lord]
        d9_longitude = (tenth_lord_point["source_longitude"] * 9.0) % 360.0
        d9_sign_index = int(d9_longitude // 30.0) + 1
        indicator = rashi_by_index[d9_sign_index]["lord"]

        assert channel["reference_sign_index"] == reference_index
        assert channel["tenth_sign_index"] == tenth_index
        assert channel["tenth_sign"] == rashi_by_index[tenth_index]["canonical_id"]
        assert channel["tenth_lord"] == tenth_lord
        assert channel["tenth_lord_d1_sign"] == rashi_by_english[
            tenth_lord_point["sign"].lower()
        ]
        assert channel["tenth_lord_d1_house"] == tenth_lord_point["house"]
        assert channel["tenth_lord_d9_sign_index"] == d9_sign_index
        assert channel["tenth_lord_d9_sign"] == rashi_by_index[d9_sign_index][
            "canonical_id"
        ]
        assert channel["karmājīva_indicator_graha"] == indicator


def test_tenth_occupants_and_income_sources_are_complete() -> None:
    career = client.post(f"{BASE_PATH}/career", json=REQUEST_BODY).json()
    d1 = client.post("/v1/charts/d1", json=REQUEST_BODY).json()
    classical_points = [
        point for point in d1["points"] if point["name"] in CLASSICAL_GRAHAS
    ]

    for channel in career["channels"]:
        expected_occupants = [
            point["name"]
            for point in classical_points
            if point["sign_index"] == channel["tenth_sign_index"]
        ]
        assert channel["tenth_house_occupants"] == expected_occupants
        assert [
            indication["graha"]
            for indication in channel["income_source_indications"]
        ] == expected_occupants
        assert all(
            indication["rule_ids"] == ["VM-BJ-C10-INCOME-SOURCE-EVAL-001"]
            for indication in channel["income_source_indications"]
        )


def test_career_aspects_match_full_aspect_endpoint() -> None:
    career = client.post(f"{BASE_PATH}/career", json=REQUEST_BODY).json()
    aspects = client.post(f"{BASE_PATH}/aspects", json=REQUEST_BODY).json()[
        "aspects"
    ]

    for channel in career["channels"]:
        expected = [
            {
                "source_graha": aspect["source_graha"],
                "relative_house": aspect["relative_house"],
                "strength_fraction": aspect["strength_fraction"],
                "strength_label": aspect["strength_label"],
                "is_special_full": aspect["is_special_full"],
                "rule_ids": aspect["rule_ids"],
            }
            for aspect in aspects
            if aspect["target_sign_index"] == channel["tenth_sign_index"]
        ]
        assert channel["aspects_to_tenth_sign"] == expected


def test_candidates_aggregate_repeated_indicators_without_ranking() -> None:
    payload = client.post(f"{BASE_PATH}/career", json=REQUEST_BODY).json()
    expected_references: dict[str, list[str]] = {}
    for channel in payload["channels"]:
        expected_references.setdefault(
            channel["karmājīva_indicator_graha"], []
        ).append(channel["reference_point"])

    assert {candidate["graha"] for candidate in payload["candidates"]} == set(
        expected_references
    )
    for candidate in payload["candidates"]:
        assert candidate["derived_from"] == expected_references[candidate["graha"]]
        assert candidate["repetition_count"] == len(candidate["derived_from"])
        assert candidate["vocation_themes"]
        assert candidate["indicator_condition"]["graha"] == candidate["graha"]
        assert "VM-BJ-C10-SUPPORT-FACTS-EVAL-001" in candidate["rule_ids"]


def test_career_rejects_unknown_timezone() -> None:
    request = {
        **REQUEST_BODY,
        "birth": {
            **REQUEST_BODY["birth"],
            "timezone": "Mars/Olympus_Mons",
        },
    }
    response = client.post(f"{BASE_PATH}/career", json=request)

    assert response.status_code == 422


def test_openapi_lists_career_route() -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert f"{BASE_PATH}/career" in paths
