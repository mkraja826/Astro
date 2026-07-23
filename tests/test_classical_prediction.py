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
                "cancellation_policy": {
                    "confirmed_rule_count": 0,
                    "cancellation_rules_enabled": False,
                    "supported_rule_ids": [],
                },
                "cancellations_applied": False,
                "grahas": [
                    {
                        "graha": name,
                        "d1_sign_index": index,
                        "d1_house": index,
                        "vargottama": name == "jupiter",
                        "cancellation": {
                            "status": (
                                "unsupported_by_profile"
                                if name == "saturn"
                                else "not_applicable"
                            ),
                            "applicable": name == "saturn",
                            "cancellation_applied": False,
                        },
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
                    "cancellation_adjustment": 0.0,
                    "cancellation_applied": False,
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


def _transit_horizon_payload() -> dict:
    return {
        "period": "daily",
        "sample_count": 4,
        "sampling_applied": True,
        "exact_ingress_egress_applied": False,
        "samples": [
            {
                "sample_index": sample_index,
                "local_datetime": f"2026-07-23T{hour:02d}:00:00",
                "timezone": "Asia/Kolkata",
                "factors": [
                    {
                        "body": name,
                        "transit_sign_index": house,
                        "house_from_natal_ascendant": house,
                        "house_from_natal_moon": house,
                        "bindus": bindus,
                        "rekhas": 8 - bindus,
                        "net_eighths": (2 * bindus) - 8,
                        "normalized_balance": ((2 * bindus) - 8) / 8,
                        "polarity": (
                            "supporting"
                            if bindus > 4
                            else "challenging"
                            if bindus < 4
                            else "contextual"
                        ),
                        "rule_ids": [
                            "VM-BJ-C09-TRANSIT-BAV-BALANCE-001",
                            f"VM-BJ-C09-{name.upper()}-BAV-001",
                        ],
                        "reason": "Synthetic transit fixture.",
                    }
                    for name, house, bindus in (
                        ("sun", 1, 4),
                        ("moon", 4, 5),
                        ("mars", 10, 2),
                        ("mercury", 5, 5),
                        ("jupiter", 9, 6),
                        ("venus", 7, 3),
                        ("saturn", 10, 2),
                    )
                ],
            }
            for sample_index, hour in enumerate((0, 6, 12, 18), start=1)
        ],
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
    monkeypatch.setattr(
        classical_prediction,
        "calculate_varahamihira_transit_horizon",
        lambda request: SimpleNamespace(
            model_dump=lambda mode: _transit_horizon_payload()
        ),
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
    assert results["career"].timing_status == "evaluated"
    assert results["career"].favourable_timing is None
    assert results["career"].challenging_timing
    assert results["money_resources"].outlook == "challenging"
    assert results["travel_change"].outlook == "challenging"
    assert results["family_home"].outlook == "favourable"
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
    saturn_boundary = next(
        factor
        for factor in results["career"].challenging_factors
        if factor.independence_key == "natal-career-saturn-controlled-strength"
    )
    assert "Cancellation boundary" in saturn_boundary.reason
    assert "No cancellation or score adjustment was applied" in saturn_boundary.reason
    assert "VM-BJ-C02-CANCELLATION-SOURCE-BOUNDARY-001" in (
        saturn_boundary.source_rule_ids
    )
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
    assert all(result.timing_status == "evaluated" for result in response.results)
    assert response.disclaimer
