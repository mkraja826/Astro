"""Integration tests for the Varahamihira classical reference foundation."""

from collections import defaultdict

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE_PATH = "/v1/classical/varahamihira_v1"


def test_varahamihira_profile_is_source_pinned_and_non_calculating() -> None:
    response = client.get(f"{BASE_PATH}/profile")
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["profile_id"] == "varahamihira_v1"
    assert payload["profile_version"] == "1.0.0"
    assert payload["status"] == "reference_foundation"
    assert payload["source"]["archive_identifier"] == "brihatjataka00varaiala"
    assert payload["source"]["publication_year"] == 1905
    assert payload["implemented_chapters"] == [1, 2]
    assert payload["astronomical_profile_dependency"] == "south_indian_drik_lahiri_v1"
    assert payload["calculation_engine_impact"] == "none"
    assert payload["interpretation_enabled"] is False
    assert payload["dignity_evaluator_enabled"] is False
    assert len(payload["endpoints"]) == 4


def test_rule_registry_has_unique_traceable_chapter_rules() -> None:
    response = client.get(f"{BASE_PATH}/rules")
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["profile_id"] == "varahamihira_v1"
    rules = payload["rules"]
    rule_ids = [rule["rule_id"] for rule in rules]

    assert len(rules) == 7
    assert len(rule_ids) == len(set(rule_ids))
    assert {rule["chapter"] for rule in rules} == {1, 2}
    assert {rule["source_id"] for rule in rules} == {
        "brihat_jataka_chidambaram_aiyar_1905"
    }
    assert {rule["citation_precision"] for rule in rules} == {"chapter"}
    assert {rule["implementation_status"] for rule in rules} == {"reference_data"}
    assert all(rule["data_keys"] for rule in rules)


def test_chapter_one_returns_complete_rashi_reference_table() -> None:
    response = client.get(f"{BASE_PATH}/rashis")
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["chapter"] == 1
    rashis = payload["rashis"]

    assert len(rashis) == 12
    assert [rashi["index"] for rashi in rashis] == list(range(1, 13))
    assert len({rashi["canonical_id"] for rashi in rashis}) == 12
    assert [rashi["modality"] for rashi in rashis] == [
        "movable",
        "fixed",
        "dual",
    ] * 4
    assert [rashi["element"] for rashi in rashis] == [
        "fire",
        "earth",
        "air",
        "water",
    ] * 3

    for rashi in rashis:
        expected_parity = "odd" if rashi["index"] % 2 else "even"
        expected_gender = "masculine" if expected_parity == "odd" else "feminine"
        assert rashi["parity"] == expected_parity
        assert rashi["gender"] == expected_gender
        assert len(rashi["rule_ids"]) == 4

    assert rashis[0]["canonical_id"] == "aries"
    assert rashis[0]["lord"] == "mars"
    assert rashis[0]["kalapurusha_body_part"] == "head"
    assert rashis[-1]["canonical_id"] == "pisces"
    assert rashis[-1]["lord"] == "jupiter"
    assert rashis[-1]["kalapurusha_body_part"] == "feet"


def test_chapter_two_graha_lordships_match_rashi_table() -> None:
    rashi_payload = client.get(f"{BASE_PATH}/rashis").json()
    response = client.get(f"{BASE_PATH}/grahas")
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["chapter"] == 2
    assert payload["included_grahas"] == 7
    assert payload["excluded_points"] == ["rahu", "ketu"]

    grahas = payload["grahas"]
    assert [graha["index"] for graha in grahas] == list(range(1, 8))
    assert [graha["canonical_id"] for graha in grahas] == [
        "sun",
        "moon",
        "mars",
        "mercury",
        "jupiter",
        "venus",
        "saturn",
    ]

    signs_by_lord: dict[str, list[str]] = defaultdict(list)
    for rashi in rashi_payload["rashis"]:
        signs_by_lord[rashi["lord"]].append(rashi["canonical_id"])

    for graha in grahas:
        assert graha["owned_signs"] == signs_by_lord[graha["canonical_id"]]
        assert len(graha["rule_ids"]) == 3

    grahas_by_id = {graha["canonical_id"]: graha for graha in grahas}
    assert grahas_by_id["moon"]["natural_tendency"] == "conditional"
    assert grahas_by_id["moon"]["tendency_note"]
    assert grahas_by_id["mercury"]["natural_tendency"] == "conditional"
    assert grahas_by_id["mercury"]["tendency_note"]
    assert grahas_by_id["jupiter"]["natural_tendency"] == "benefic"
    assert grahas_by_id["saturn"]["natural_tendency"] == "malefic"


def test_exaltation_and_debilitation_points_are_opposite() -> None:
    response = client.get(f"{BASE_PATH}/grahas")
    payload = response.json()
    sign_indices = {
        "aries": 1,
        "taurus": 2,
        "gemini": 3,
        "cancer": 4,
        "leo": 5,
        "virgo": 6,
        "libra": 7,
        "scorpio": 8,
        "sagittarius": 9,
        "capricorn": 10,
        "aquarius": 11,
        "pisces": 12,
    }

    assert response.status_code == 200, payload
    for graha in payload["grahas"]:
        exaltation_index = sign_indices[graha["exaltation_sign"]]
        debilitation_index = sign_indices[graha["debilitation_sign"]]
        assert (debilitation_index - exaltation_index) % 12 == 6
        assert graha["debilitation_degree"] == graha["exaltation_degree"]


def test_openapi_lists_all_classical_reference_routes() -> None:
    payload = client.get("/openapi.json").json()
    paths = payload["paths"]

    assert f"{BASE_PATH}/profile" in paths
    assert f"{BASE_PATH}/rules" in paths
    assert f"{BASE_PATH}/rashis" in paths
    assert f"{BASE_PATH}/grahas" in paths
