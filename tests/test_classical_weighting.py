"""Golden-fixture and integration tests for controlled strength weighting."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.engine.classical_weighting import (
    compact_strength_snapshot,
    weight_assessment,
)
from app.main import app
from app.schemas.classical_conditions import DignityState, ResolvedTendency
from app.schemas.classical_relationships import (
    CompoundRelationship,
    NaturalRelationship,
    TemporaryRelationship,
)
from app.schemas.classical_strength import (
    CancellationEvaluation,
    CancellationStatus,
    GrahaStrengthAssessment,
    SignLordRelationshipSnapshot,
    StrengthFactor,
    StrengthFactorCategory,
)

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1"
FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "controlled_strength_weighting_v1.json"
)

BIRTH = {
    "local_datetime": "1998-10-26T10:28:00",
    "timezone": "Asia/Kolkata",
    "latitude": 16.575,
    "longitude": 79.312,
    "altitude_meters": 120,
}
BASE_REQUEST = {
    "birth": BIRTH,
    "calculation_profile": "south_indian_drik_lahiri_v1",
    "weighting_profile": "transparent_strength_weighting_v1",
}


def _factor(factor_id: str) -> StrengthFactor:
    return StrengthFactor(
        factor_id=factor_id,
        category=StrengthFactorCategory.CONTEXTUAL,
        value="fixture",
        reason="Golden fixture source fact.",
        rule_ids=[f"FIXTURE-{factor_id}"],
        numeric_weight=None,
    )


def _assessment(fixture: dict[str, object]) -> GrahaStrengthAssessment:
    dignity = DignityState(str(fixture["dignity"]))
    deep = str(fixture["deep_dignity"])
    relationship_value = str(fixture["relationship"])
    vargottama = bool(fixture["vargottama"])

    dignity_factor_id = {
        DignityState.EXALTATION_SIGN: "dignity_exaltation_sign",
        DignityState.OWN_SIGN: "dignity_own_sign",
        DignityState.ORDINARY: "dignity_ordinary",
        DignityState.DEBILITATION_SIGN: "dignity_debilitation_sign",
    }[dignity]
    factors = [_factor(dignity_factor_id)]
    if deep == "deep_exaltation":
        factors.append(_factor("deep_exaltation_point"))
    elif deep == "deep_debilitation":
        factors.append(_factor("deep_debilitation_point"))
    if vargottama:
        factors.append(_factor("vargottama"))
    factors.extend(
        [
            _factor("occupied_sign_lord_relationship"),
            _factor("bhinnashtakavarga_raw"),
            _factor("sarvashtakavarga_raw"),
            _factor("resolved_tendency"),
            _factor("aspects_received_raw"),
            _factor("conjunctions_raw"),
        ]
    )

    if relationship_value == "self":
        relationship = SignLordRelationshipSnapshot(
            sign_lord="jupiter",
            self_relationship=True,
            rule_ids=["FIXTURE-RELATIONSHIP"],
        )
        occupied_sign_lord = "jupiter"
    else:
        natural = (
            NaturalRelationship.FRIEND
            if relationship_value == "great_friend"
            else NaturalRelationship.ENEMY
        )
        temporary = (
            TemporaryRelationship.FRIEND
            if relationship_value == "great_friend"
            else TemporaryRelationship.ENEMY
        )
        relationship = SignLordRelationshipSnapshot(
            sign_lord="mars",
            natural_relationship=natural,
            temporary_relationship=temporary,
            compound_relationship=CompoundRelationship(relationship_value),
            self_relationship=False,
            rule_ids=["FIXTURE-RELATIONSHIP"],
        )
        occupied_sign_lord = "mars"

    debilitated = dignity == DignityState.DEBILITATION_SIGN
    cancellation = CancellationEvaluation(
        candidate_id="debilitation_cancellation",
        status=(
            CancellationStatus.UNSUPPORTED_BY_PROFILE
            if debilitated
            else CancellationStatus.NOT_APPLICABLE
        ),
        applicable=debilitated,
        cancellation_applied=False,
        reason="Golden fixture cancellation boundary.",
        unsupported_conventions=["fixture"] if debilitated else [],
    )

    return GrahaStrengthAssessment(
        graha="jupiter",
        source_longitude=0.0,
        d1_sign_index=1,
        d1_sign="aries",
        d1_degree_in_sign=0.0,
        d1_house=1,
        dignity=dignity,
        own_sign=dignity == DignityState.OWN_SIGN,
        in_exaltation_sign=dignity == DignityState.EXALTATION_SIGN,
        at_deep_exaltation_point=deep == "deep_exaltation",
        in_debilitation_sign=debilitated,
        at_deep_debilitation_point=deep == "deep_debilitation",
        vargottama=vargottama,
        retrograde=False,
        resolved_tendency=ResolvedTendency.BENEFIC,
        occupied_sign_lord=occupied_sign_lord,
        sign_lord_relationship=relationship,
        bhinnashtakavarga_bindus_in_occupied_sign=int(
            fixture["bhinnashtakavarga_bindus"]
        ),
        sarvashtakavarga_bindus_in_occupied_sign=int(
            fixture["sarvashtakavarga_bindus"]
        ),
        full_aspects_received=0,
        total_fractional_aspect_weight_received=0.0,
        conjunctions=[],
        factors=factors,
        cancellation=cancellation,
    )


def test_golden_weighting_fixtures_match_every_component_and_total() -> None:
    fixture_document = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert fixture_document["profile"] == "transparent_strength_weighting_v1"
    assert fixture_document["version"] == "1.0.0"
    assert len(fixture_document["fixtures"]) == 3

    for fixture in fixture_document["fixtures"]:
        components, total, neutral = weight_assessment(_assessment(fixture))
        actual = {item.component_id: item.contribution for item in components}

        assert actual == fixture["expected_components"]
        assert total == fixture["expected_total"]
        assert "resolved_tendency" in neutral
        assert "aspects_received_raw" in neutral
        assert "conjunctions_raw" in neutral


def test_weighting_profile_is_explicitly_non_textual_and_source_separated() -> None:
    response = client.get(f"{BASE_PATH}/weighting/profile")
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["weighting_profile"] == "transparent_strength_weighting_v1"
    assert payload["version"] == "1.0.0"
    assert payload["source_status"] == "api_convention_not_textual_rule"
    assert payload["classical_profile_dependency"] == "varahamihira_v1"
    assert payload["cancellation_adjustment_enabled"] is False
    assert payload["golden_fixture_count"] == 3
    assert payload["external_reference_validation_complete"] is False


def test_weighted_strength_embeds_raw_evidence_and_transparent_ranking() -> None:
    response = client.post(f"{BASE_PATH}/strength/weighted", json=BASE_REQUEST)
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["weighting_profile"] == "transparent_strength_weighting_v1"
    assert payload["weighting_version"] == "1.0.0"
    assert payload["weights_applied"] is True
    assert payload["ranking_applied"] is True
    assert payload["cancellations_applied"] is False
    assert payload["prediction_applied"] is False
    assert len(payload["weighted_grahas"]) == 7
    assert payload["raw_strength"]["weights_applied"] is False

    rank_one = []
    for item in payload["weighted_grahas"]:
        assert len(item["components"]) == 6
        assert round(
            sum(component["contribution"] for component in item["components"]),
            6,
        ) == item["total_score"]
        assert item["cancellation_adjustment"] == 0.0
        assert item["cancellation_applied"] is False
        if item["rank"] == 1:
            rank_one.append(item["graha"])

    assert payload["highest_ranked_grahas"] == rank_one


def test_weighted_career_keeps_plural_channels_and_only_ranks_grahas() -> None:
    response = client.post(f"{BASE_PATH}/career/weighted", json=BASE_REQUEST)
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["career"]["ranking_applied"] is False
    assert payload["career_ranking_applied"] is False
    assert payload["prediction_applied"] is False
    assert len(payload["channel_strengths"]) == 3

    weighted_lookup = {
        item["graha"]: item for item in payload["weighted_strength"]["weighted_grahas"]
    }
    for channel, summary in zip(
        payload["career"]["channels"],
        payload["channel_strengths"],
        strict=True,
    ):
        assert summary["reference_point"] == channel["reference_point"]
        assert summary["tenth_lord"]["graha"] == channel["tenth_lord"]
        assert summary["indicator_graha"]["graha"] == (
            channel["karmājīva_indicator_graha"]
        )
        assert summary["tenth_lord"]["total_score"] == weighted_lookup[
            channel["tenth_lord"]
        ]["total_score"]


def test_weighted_dasha_preserves_active_chain_and_excludes_nodes_from_scoring() -> None:
    request = {
        **BASE_REQUEST,
        "as_of": {
            "local_datetime": "2026-07-20T12:00:00",
            "timezone": "Asia/Kolkata",
        },
    }
    response = client.post(f"{BASE_PATH}/dasha/current/weighted", json=request)
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["event_prediction_applied"] is False
    assert payload["cancellations_applied"] is False
    assert len(payload["dasha"]["levels"]) == 4
    assert len(payload["level_strengths"]) == 4

    weighted_lookup = {
        item["graha"]: item for item in payload["weighted_strength"]["weighted_grahas"]
    }
    for level, summary in zip(
        payload["dasha"]["levels"],
        payload["level_strengths"],
        strict=True,
    ):
        assert summary["level"] == level["level"]
        assert summary["lord"] == level["lord"]
        if level["lord"] in weighted_lookup:
            assert summary["strength"]["available"] is True
            assert summary["strength"]["total_score"] == weighted_lookup[
                level["lord"]
            ]["total_score"]
        else:
            assert level["lord"] in {"rahu", "ketu"}
            assert summary["strength"]["available"] is False


def test_node_snapshot_is_explicitly_unavailable() -> None:
    snapshot = compact_strength_snapshot("rahu", {})

    assert snapshot.available is False
    assert snapshot.weighting_profile is None
    assert snapshot.total_score is None
    assert snapshot.rank is None


def test_unknown_weighting_profile_is_rejected() -> None:
    response = client.post(
        f"{BASE_PATH}/strength/weighted",
        json={**BASE_REQUEST, "weighting_profile": "unregistered_weighting_v9"},
    )

    assert response.status_code == 422


def test_openapi_lists_all_controlled_weighting_routes() -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert f"{BASE_PATH}/weighting/profile" in paths
    assert f"{BASE_PATH}/strength/weighted" in paths
    assert f"{BASE_PATH}/career/weighted" in paths
    assert f"{BASE_PATH}/dasha/current/weighted" in paths
