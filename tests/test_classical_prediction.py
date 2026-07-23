from types import SimpleNamespace

from app.engine import classical_prediction
from app.schemas.classical_prediction import ClassicalPredictionRequest
from app.schemas.dasha import DashaQueryTime
from app.schemas.positions import BirthInput


def _career_payload() -> dict:
    return {
        "profile_id": "varahamihira_v1",
        "career": {
            "candidates": [
                {
                    "graha": "Saturn",
                    "rule_ids": ["VM-BJ-C10-VOCATION-JUPITER-SATURN-001"],
                }
            ]
        },
        "candidate_strengths": [
            {
                "graha": "Saturn",
                "repetition_count": 2,
                "strength": {
                    "available": True,
                    "total_score": -4.0,
                    "reason": "Synthetic adverse integration fixture.",
                },
            }
        ],
    }


def _dasha_payload() -> dict:
    empty_level = {
        "supporting_evidence": [],
        "challenging_evidence": [],
        "contextual_evidence": [],
    }
    return {
        "profile_id": "varahamihira_v1",
        "weighted_strength": {
            "calculation_profile": "south_indian_drik_lahiri_jpl_de440s_v1",
            "raw_strength": {
                "grahas": [
                    {
                        "graha": name,
                        "d1_sign_index": index,
                        "d1_house": index,
                        "vargottama": name == "jupiter",
                    }
                    for index, name in enumerate(
                        [
                            "sun",
                            "moon",
                            "mars",
                            "mercury",
                            "jupiter",
                            "venus",
                            "saturn",
                        ],
                        start=1,
                    )
                ]
            },
            "weighted_grahas": [
                {
                    "graha": name,
                    "total_score": score,
                    "components": [
                        {
                            "classical_rule_ids": [
                                "VM-BJ-C02-DIGNITY-001"
                            ]
                        }
                    ],
                }
                for name, score in {
                    "sun": 2.0,
                    "moon": 3.0,
                    "mars": -8.0,
                    "mercury": 1.0,
                    "jupiter": 4.0,
                    "venus": -4.0,
                    "saturn": -4.0,
                }.items()
            ],
        },
        "dasha": {
            "levels": [
                {
                    **empty_level,
                    "level": "mahadasha",
                    "lord": "Saturn",
                    "challenging_evidence": [
                        {
                            "fact": "dignity",
                            "value": "debilitation",
                            "reason": "Synthetic adverse integration fixture.",
                            "rule_ids": ["VM-BJ-C02-DIGNITY-001"],
                        }
                    ],
                    "contextual_evidence": [
                        {
                            "fact": "owned_houses",
                            "value": "2,3",
                            "reason": "Synthetic house ownership fixture.",
                            "rule_ids": [],
                        }
                    ],
                },
                {**empty_level, "level": "antardasha", "lord": "Jupiter"},
                {**empty_level, "level": "pratyantardasha", "lord": "Moon"},
                {**empty_level, "level": "sookshma", "lord": "Mercury"},
            ]
        },
    }


def test_prediction_composes_existing_astro_modules(monkeypatch) -> None:
    monkeypatch.setattr(
        classical_prediction,
        "calculate_varahamihira_weighted_career",
        lambda request: SimpleNamespace(model_dump=lambda mode: _career_payload()),
    )
    monkeypatch.setattr(
        classical_prediction,
        "calculate_varahamihira_weighted_dasha",
        lambda request: SimpleNamespace(model_dump=lambda mode: _dasha_payload()),
    )
    request = ClassicalPredictionRequest(
        birth=BirthInput(
            local_datetime="1998-10-26T10:28:00",
            timezone="Asia/Kolkata",
            latitude=16.575,
            longitude=79.312,
            altitude_meters=120,
        ),
        as_of=DashaQueryTime(
            local_datetime="2026-07-23T12:00:00",
            timezone="Asia/Kolkata",
        ),
        period="daily",
    )

    response = classical_prediction.calculate_varahamihira_prediction(request)
    results = {result.domain: result for result in response.results}

    assert response.engine_version == "horos_brihat_jataka_v3_dev"
    assert results["career"].outlook == "challenging"
    assert "negative" in results["career"].statement
    assert results["career"].challenging_timing
    assert results["money_resources"].outlook == "challenging"
    assert results["travel_change"].outlook == "challenging"
    assert results["family_home"].outlook == "mixed"
    assert results["spirituality"].outlook == "mixed"
    jupiter_confirmation = next(
        factor
        for factor in (
            *results["spirituality"].supporting_factors,
            *results["spirituality"].challenging_factors,
        )
        if factor.independence_key
        == "natal-spirituality-jupiter-controlled-strength"
    )
    assert "D9 confirmation" in jupiter_confirmation.reason
    assert (
        "VM-BJ-C01-VARGOTTAMA-EVAL-001"
        in jupiter_confirmation.source_rule_ids
    )
    d10_marker = next(
        factor
        for factor in results["career"].contextual_factors
        if factor.evidence_id == "coverage-varga-d10-career"
    )
    assert d10_marker.weight == 0.0
    assert "unavailable" in d10_marker.statement
    assert all(
        factor.independence_key
        for result in response.results
        for factor in (
            *result.supporting_factors,
            *result.challenging_factors,
            *result.contextual_factors,
        )
    )
    assert len(results) == 9
    assert response.disclaimer
