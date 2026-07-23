"""Integration tests for source-traceable Chapter 9 transit balance."""

from fastapi.testclient import TestClient

from app.engine.classical_transits import _sample_datetimes
from app.main import app
from app.schemas.classical_transits import ClassicalTransitHorizonRequest

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1"
PROFILE = "south_indian_drik_lahiri_jpl_de440s_v1"


def _payload() -> dict[str, object]:
    return {
        "birth": {
            "local_datetime": "1998-10-26T10:28:00",
            "timezone": "Asia/Kolkata",
            "latitude": 16.575,
            "longitude": 79.312,
            "altitude_meters": 120,
        },
        "as_of": {
            "local_datetime": "2026-07-23T12:00:00",
            "timezone": "Asia/Kolkata",
        },
        "calculation_profile": PROFILE,
    }


def test_classical_transit_balance_matches_raw_bhinnashtakavarga() -> None:
    result_response = client.post(f"{BASE_PATH}/transits/evaluate", json=_payload())
    result = result_response.json()
    ashtakavarga_response = client.post(
        f"{BASE_PATH}/ashtakavarga",
        json={
            "birth": _payload()["birth"],
            "calculation_profile": PROFILE,
        },
    )
    ashtakavarga = ashtakavarga_response.json()

    assert result_response.status_code == 200, result
    assert ashtakavarga_response.status_code == 200, ashtakavarga
    assert result["interpretation_applied"] is True
    assert result["domain_prediction_applied"] is False
    assert result["timing_window_applied"] is False
    assert result["excluded_points"] == ["rahu", "ketu"]
    assert len(result["factors"]) == 7

    bav = {
        record["graha"]: record for record in ashtakavarga["bhinnashtakavargas"]
    }
    transit = {
        point["body"]: point for point in result["snapshot"]["transit"]["planets"]
    }
    for factor in result["factors"]:
        body = factor["body"]
        bindus = bav[body]["bindus_by_sign"][transit[body]["sign_index"] - 1]
        assert factor["bindus"] == bindus
        assert factor["rekhas"] == 8 - bindus
        assert factor["net_eighths"] == (2 * bindus) - 8
        assert factor["normalized_balance"] == ((2 * bindus) - 8) / 8
        assert "VM-BJ-C09-TRANSIT-BAV-BALANCE-001" in factor["rule_ids"]
        expected_polarity = (
            "supporting"
            if bindus > 4
            else "challenging"
            if bindus < 4
            else "contextual"
        )
        assert factor["polarity"] == expected_polarity


def test_profile_and_registry_advertise_transit_evaluator() -> None:
    profile = client.get(f"{BASE_PATH}/profile").json()
    registry = client.get(f"{BASE_PATH}/rules").json()

    assert f"{BASE_PATH}/transits/evaluate" in profile["endpoints"]
    rule = next(
        item
        for item in registry["rules"]
        if item["rule_id"] == "VM-BJ-C09-TRANSIT-BAV-BALANCE-001"
    )
    assert rule["chapter"] == 9
    assert rule["citation_precision"] == "chapter"


def test_openapi_lists_classical_transit_evaluator() -> None:
    assert f"{BASE_PATH}/transits/evaluate" in app.openapi()["paths"]
    assert f"{BASE_PATH}/transits/horizon" in app.openapi()["paths"]


def test_horizon_sample_grids_are_frozen_in_local_civil_time() -> None:
    base = _payload()
    expected = {
        "daily": (4, [0, 6, 12, 18]),
        "weekly": (7, [12] * 7),
        "monthly": (30, [12] * 30),
    }
    for period, (count, hours) in expected.items():
        request = ClassicalTransitHorizonRequest.model_validate(
            {**base, "period": period}
        )
        samples = _sample_datetimes(request)
        assert len(samples) == count
        assert [sample.hour for sample in samples] == hours
        assert samples[0].date().isoformat() == "2026-07-23"
        assert all(
            (current - previous).total_seconds()
            == (6 * 3600 if period == "daily" else 24 * 3600)
            for previous, current in zip(samples, samples[1:], strict=False)
        )
