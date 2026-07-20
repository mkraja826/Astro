"""Integration tests for the Varahamihira classical source profile."""

from collections import defaultdict

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1"


def test_varahamihira_profile_is_source_pinned_and_versioned() -> None:
    response = client.get(f"{BASE_PATH}/profile")
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["profile_id"] == "varahamihira_v1"
    assert payload["profile_version"] == "1.9.0"
    assert payload["status"] == "reference_foundation"
    assert payload["source"]["archive_identifier"] == "brihatjataka00varaiala"
    assert payload["source"]["publication_year"] == 1905
    assert payload["implemented_chapters"] == [1, 2, 9, 10]
    assert "Chapter 9: Ashtakavarga" in payload["source"]["reference_scope"]
    assert "Chapter 10: Vocation (Karmājīva)" in payload["source"][
        "reference_scope"
    ]
    assert payload["astronomical_profile_dependency"] == (
        "south_indian_drik_lahiri_v1"
    )
    assert payload["calculation_engine_impact"] == "none"
    assert payload["interpretation_enabled"] is False
    assert payload["dignity_evaluator_enabled"] is True
    assert payload["aspects_evaluator_enabled"] is True
    assert payload["house_influence_evaluator_enabled"] is True
    assert payload["career_analysis_enabled"] is True
    assert payload["ashtakavarga_enabled"] is True
    assert payload["dasha_interpretation_enabled"] is True
    assert payload["relationships_enabled"] is True
    assert len(payload["endpoints"]) == 18
    assert f"{BASE_PATH}/conditions" in payload["endpoints"]
    assert f"{BASE_PATH}/aspects" in payload["endpoints"]
    assert f"{BASE_PATH}/career" in payload["endpoints"]
    assert f"{BASE_PATH}/career/weighted" in payload["endpoints"]
    assert f"{BASE_PATH}/ashtakavarga" in payload["endpoints"]
    assert f"{BASE_PATH}/dasha/current" in payload["endpoints"]
    assert f"{BASE_PATH}/dasha/current/weighted" in payload["endpoints"]
    assert f"{BASE_PATH}/relationships" in payload["endpoints"]
    assert f"{BASE_PATH}/strength" in payload["endpoints"]
    assert f"{BASE_PATH}/strength/weighted" in payload["endpoints"]
    assert f"{BASE_PATH}/weighting/profile" in payload["endpoints"]
    assert f"{BASE_PATH}/validation/profile" in payload["endpoints"]
    assert f"{BASE_PATH}/validation/cases" in payload["endpoints"]
    assert f"{BASE_PATH}/validation/compare" in payload["endpoints"]


def test_rule_registry_has_unique_traceable_chapter_rules() -> None:
    response = client.get(f"{BASE_PATH}/rules")
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["profile_id"] == "varahamihira_v1"
    rules = payload["rules"]
    rule_ids = [rule["rule_id"] for rule in rules]

    assert len(rules) == 42
    assert len(rule_ids) == len(set(rule_ids))
    assert {rule["chapter"] for rule in rules} == {1, 2, 9, 10}
    assert {rule["source_id"] for rule in rules} == {
        "brihat_jataka_chidambaram_aiyar_1905"
    }
    assert {rule["citation_precision"] for rule in rules} == {
        "chapter",
        "verse",
    }
    assert {rule["implementation_status"] for rule in rules} == {
        "reference_data",
        "implemented_evaluator",
    }
    assert all(rule["data_keys"] for rule in rules)
    assert "VM-BJ-C02-DIGNITY-EVAL-001" in rule_ids
    assert "VM-BJ-C02-MOON-PHASE-EVAL-001" in rule_ids
    assert "VM-BJ-C02-MERCURY-ASSOC-EVAL-001" in rule_ids
    assert "VM-BJ-C02-ASPECT-STRENGTH-EVAL-001" in rule_ids
    assert "VM-BJ-C02-SPECIAL-ASPECT-EVAL-001" in rule_ids
    assert "VM-BJ-C10-NAVAMSA-LORD-EVAL-001" in rule_ids
    assert "VM-BJ-C10-SUPPORT-FACTS-EVAL-001" in rule_ids
    assert "VM-BJ-C09-SUN-BAV-001" in rule_ids
    assert "VM-BJ-C09-SATURN-BAV-001" in rule_ids
    assert "VM-BJ-C09-SARVA-AGGREGATION-001" in rule_ids
    assert "VM-BJ-C01-DASHA-OWNERSHIP-CONTEXT-001" in rule_ids
    assert "VM-BJ-C02-DASHA-CONDITION-CONTEXT-001" in rule_ids
    assert "VM-BJ-C02-DASHA-ASPECT-CONTEXT-001" in rule_ids
    assert "VM-BJ-C09-DASHA-ASHTAKAVARGA-CONTEXT-001" in rule_ids
    assert "VM-BJ-C10-DASHA-CAREER-CONTEXT-001" in rule_ids
    assert "VM-BJ-C02-DASHA-NODE-COVERAGE-001" in rule_ids
    assert "VM-BJ-C02-NATURAL-RELATIONSHIP-EVAL-001" in rule_ids
    assert "VM-BJ-C02-TEMPORARY-RELATIONSHIP-EVAL-001" in rule_ids
    assert "VM-BJ-C02-COMPOUND-RELATIONSHIP-EVAL-001" in rule_ids
    assert "VM-BJ-C02-STRENGTH-FACTOR-FRAMEWORK-001" in rule_ids
    assert "VM-BJ-C09-STRENGTH-BINDU-CONTEXT-001" in rule_ids
    assert "VM-BJ-C02-CANCELLATION-SOURCE-BOUNDARY-001" in rule_ids

    aspect_rule = next(
        rule
        for rule in rules
        if rule["rule_id"] == "VM-BJ-C02-ASPECT-STRENGTH-EVAL-001"
    )
    assert aspect_rule["verse_reference"] == "2.13"
    assert aspect_rule["citation_precision"] == "verse"

    relationship_rules = [
        rule for rule in rules if "RELATIONSHIP-EVAL" in rule["rule_id"]
    ]
    assert len(relationship_rules) == 3
    assert {rule["verse_reference"] for rule in relationship_rules} == {
        "2.16-2.17",
        "2.18",
    }
    assert {rule["citation_precision"] for rule in relationship_rules} == {
        "verse"
    }

    strength_rules = [
        rule
        for rule in rules
        if "STRENGTH-FACTOR" in rule["rule_id"]
        or "STRENGTH-BINDU" in rule["rule_id"]
        or "CANCELLATION-SOURCE" in rule["rule_id"]
    ]
    assert len(strength_rules) == 3
    assert {rule["chapter"] for rule in strength_rules} == {2, 9}

    career_rules = [rule for rule in rules if rule["chapter"] == 10]
    assert {rule["verse_reference"] for rule in career_rules} == {
        "10.1",
        "10.2",
        "10.3",
        "10.4",
        "10.1-10.4",
    }
    assert {rule["citation_precision"] for rule in career_rules} == {"verse"}

    ashtakavarga_rules = [
        rule
        for rule in rules
        if rule["chapter"] == 9
        and "DASHA" not in rule["rule_id"]
        and "STRENGTH" not in rule["rule_id"]
    ]
    assert len(ashtakavarga_rules) == 8
    assert {rule["verse_reference"] for rule in ashtakavarga_rules} == {
        "9.1",
        "9.2",
        "9.3",
        "9.4",
        "9.5",
        "9.6",
        "9.7",
        "9.8",
    }
    assert {rule["citation_precision"] for rule in ashtakavarga_rules} == {
        "verse"
    }


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


def test_openapi_lists_all_classical_routes() -> None:
    payload = client.get("/openapi.json").json()
    paths = payload["paths"]

    assert f"{BASE_PATH}/profile" in paths
    assert f"{BASE_PATH}/rules" in paths
    assert f"{BASE_PATH}/weighting/profile" in paths
    assert f"{BASE_PATH}/rashis" in paths
    assert f"{BASE_PATH}/grahas" in paths
    assert f"{BASE_PATH}/conditions" in paths
    assert f"{BASE_PATH}/aspects" in paths
    assert f"{BASE_PATH}/career" in paths
    assert f"{BASE_PATH}/career/weighted" in paths
    assert f"{BASE_PATH}/ashtakavarga" in paths
    assert f"{BASE_PATH}/dasha/current" in paths
    assert f"{BASE_PATH}/dasha/current/weighted" in paths
    assert f"{BASE_PATH}/relationships" in paths
    assert f"{BASE_PATH}/strength" in paths
    assert f"{BASE_PATH}/strength/weighted" in paths
    assert f"{BASE_PATH}/validation/profile" in paths
    assert f"{BASE_PATH}/validation/cases" in paths
    assert f"{BASE_PATH}/validation/compare" in paths
