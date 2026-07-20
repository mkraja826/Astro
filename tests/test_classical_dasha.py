"""Integration tests for classical context on the active Vimshottari chain."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1"


def _birth() -> dict[str, object]:
    return {
        "local_datetime": "1998-10-26T10:28:00",
        "timezone": "Asia/Kolkata",
        "latitude": 16.575,
        "longitude": 79.312,
        "altitude_meters": 120,
    }


def _payload(as_of: str = "2026-07-20T12:00:00", timezone: str = "Asia/Kolkata") -> dict[str, object]:
    return {
        "birth": _birth(),
        "as_of": {
            "local_datetime": as_of,
            "timezone": timezone,
        },
        "calculation_profile": "south_indian_drik_lahiri_v1",
    }


def test_classical_dasha_matches_existing_timing_and_context_endpoints() -> None:
    payload = _payload()
    response = client.post(f"{BASE_PATH}/dasha/current", json=payload)
    result = response.json()

    timing_response = client.post("/v1/dashas/vimshottari/current", json=payload)
    timing = timing_response.json()
    chart = client.post(
        "/v1/charts/d1",
        json={
            "birth": payload["birth"],
            "calculation_profile": payload["calculation_profile"],
        },
    ).json()
    conditions = client.post(
        f"{BASE_PATH}/conditions",
        json={
            "birth": payload["birth"],
            "calculation_profile": payload["calculation_profile"],
        },
    ).json()
    ashtakavarga = client.post(
        f"{BASE_PATH}/ashtakavarga",
        json={
            "birth": payload["birth"],
            "calculation_profile": payload["calculation_profile"],
        },
    ).json()

    assert response.status_code == 200, result
    assert timing_response.status_code == 200, timing
    assert result["timing"] == timing
    assert result["interpretation_mode"] == "evidence_only"
    assert result["prediction_applied"] is False
    assert result["cancellations_applied"] is False
    assert result["strength_weighting_applied"] is False

    expected_levels = [
        "mahadasha",
        "antardasha",
        "pratyantardasha",
        "sookshma",
    ]
    assert [item["level"] for item in result["levels"]] == expected_levels

    chart_points = {point["name"]: point for point in chart["points"]}
    conditions_by_graha = {
        condition["graha"]: condition for condition in conditions["grahas"]
    }
    bav_by_graha = {
        record["graha"]: record
        for record in ashtakavarga["bhinnashtakavargas"]
    }
    sav_by_sign = {
        summary["sign_index"]: summary
        for summary in ashtakavarga["sarvashtakavarga"]["signs"]
    }

    for level, item in zip(expected_levels, result["levels"], strict=True):
        lord = item["lord"]
        point = chart_points[lord]
        assert item["period"] == timing[level]
        assert item["source_longitude"] == point["source_longitude"]
        assert item["d1_sign_index"] == point["sign_index"]
        assert item["d1_house"] == point["house"]
        assert item["sarvashtakavarga_bindus_in_occupied_sign"] == sav_by_sign[
            point["sign_index"]
        ]["sarvashtakavarga_bindus"]

        if lord in conditions_by_graha:
            condition = conditions_by_graha[lord]
            assert item["classical_condition_available"] is True
            assert item["dignity"] == condition["dignity"]
            assert item["own_sign"] == condition["own_sign"]
            assert item["vargottama"] == condition["vargottama"]
            assert item["bhinnashtakavarga_bindus_in_occupied_sign"] == (
                bav_by_graha[lord]["bindus_by_sign"][point["sign_index"] - 1]
            )
        else:
            assert lord in {"rahu", "ketu"}
            assert item["classical_condition_available"] is False
            assert item["dignity"] is None
            assert item["owned_signs"] == []
            assert item["owned_houses"] == []
            assert item["bhinnashtakavarga_bindus_in_occupied_sign"] is None

        categories = {
            evidence["category"]
            for evidence in [
                *item["supporting_evidence"],
                *item["challenging_evidence"],
                *item["contextual_evidence"],
            ]
        }
        assert categories <= {"supporting", "challenging", "contextual"}
        assert item["rule_ids"]


def test_rahu_period_has_neutral_placement_without_classical_dignity() -> None:
    full_response = client.post(
        "/v1/dashas/vimshottari",
        json={
            "birth": _birth(),
            "calculation_profile": "south_indian_drik_lahiri_v1",
        },
    )
    full = full_response.json()
    assert full_response.status_code == 200, full

    rahu_period = next(
        period for period in full["mahadashas"] if period["lord"] == "rahu"
    )
    query_utc = datetime.fromisoformat(rahu_period["start_utc"]).astimezone(UTC) + timedelta(
        days=1
    )
    payload = _payload(
        as_of=query_utc.replace(tzinfo=None).isoformat(),
        timezone="UTC",
    )

    response = client.post(f"{BASE_PATH}/dasha/current", json=payload)
    result = response.json()

    assert response.status_code == 200, result
    rahu = result["levels"][0]
    assert rahu["level"] == "mahadasha"
    assert rahu["lord"] == "rahu"
    assert rahu["classical_condition_available"] is False
    assert rahu["dignity"] is None
    assert rahu["resolved_tendency"] is None
    assert rahu["bhinnashtakavarga_bindus_in_occupied_sign"] is None
    assert any(
        evidence["fact"] == "classical_node_coverage"
        for evidence in rahu["contextual_evidence"]
    )


def test_classical_dasha_reuses_current_query_validation() -> None:
    payload = _payload()
    payload["as_of"]["timezone"] = "India/Not-A-Timezone"  # type: ignore[index]

    response = client.post(f"{BASE_PATH}/dasha/current", json=payload)

    assert response.status_code == 422
    assert "Unknown IANA timezone" in response.json()["detail"]


def test_openapi_lists_classical_dasha_endpoint() -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert f"{BASE_PATH}/dasha/current" in paths
