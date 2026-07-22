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
            "calculation_profile": "south_indian_drik_lahiri_jpl_de440s_v1"
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

    assert response.engine_version == "horos_brihat_jataka_v1"
    assert results["career"].outlook == "challenging"
    assert "negative" in results["career"].statement
    assert response.disclaimer
