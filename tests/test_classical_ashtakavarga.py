"""Tests for Varahamihira Chapter 9 Ashtakavarga calculations."""

from fastapi.testclient import TestClient

from app.engine.classical_ashtakavarga import (
    CLASSICAL_GRAHAS,
    CONTRIBUTORS,
    EXPECTED_SARVASHTAKAVARGA_TOTAL,
    EXPECTED_TOTALS,
    FAVORABLE_HOUSES,
    favorable_sign_indices,
    validate_ashtakavarga_tables,
)
from app.main import app

client = TestClient(app)
BASE_PATH = "/v1/classical/varahamihira_v1"


def _payload() -> dict[str, object]:
    return {
        "birth": {
            "local_datetime": "1998-10-26T10:28:00",
            "timezone": "Asia/Kolkata",
            "latitude": 16.575,
            "longitude": 79.312,
            "altitude_meters": 120,
        },
        "calculation_profile": "south_indian_drik_lahiri_v1",
    }


def test_chapter_nine_tables_have_complete_contributors_and_fixed_totals() -> None:
    validate_ashtakavarga_tables()

    assert tuple(FAVORABLE_HOUSES) == CLASSICAL_GRAHAS
    assert EXPECTED_TOTALS == {
        "sun": 48,
        "moon": 49,
        "mars": 39,
        "mercury": 54,
        "jupiter": 56,
        "venus": 52,
        "saturn": 39,
    }
    assert EXPECTED_SARVASHTAKAVARGA_TOTAL == 337

    for graha in CLASSICAL_GRAHAS:
        assert tuple(FAVORABLE_HOUSES[graha]) == CONTRIBUTORS
        assert sum(
            len(FAVORABLE_HOUSES[graha][contributor])
            for contributor in CONTRIBUTORS
        ) == EXPECTED_TOTALS[graha]
        for relative_houses in FAVORABLE_HOUSES[graha].values():
            assert len(relative_houses) == len(set(relative_houses))
            assert all(1 <= house <= 12 for house in relative_houses)


def test_relative_house_rotation_wraps_across_pisces_and_aries() -> None:
    assert favorable_sign_indices(12, (1, 2, 12)) == (12, 1, 11)
    assert favorable_sign_indices(1, (1, 7, 12)) == (1, 7, 12)


def test_ashtakavarga_returns_all_raw_arrays_and_canonical_totals() -> None:
    response = client.post(f"{BASE_PATH}/ashtakavarga", json=_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["profile_id"] == "varahamihira_v1"
    assert payload["calculation_profile"] == "south_indian_drik_lahiri_v1"
    assert payload["excluded_points"] == ["rahu", "ketu"]
    assert len(payload["contributor_positions"]) == 8
    assert [position["contributor"] for position in payload["contributor_positions"]] == list(
        CONTRIBUTORS
    )

    records = payload["bhinnashtakavargas"]
    assert [record["graha"] for record in records] == list(CLASSICAL_GRAHAS)
    assert len(records) == 7

    for record in records:
        graha = record["graha"]
        assert len(record["contributor_rows"]) == 8
        assert len(record["bindus_by_sign"]) == 12
        assert len(record["rekhas_by_sign"]) == 12
        assert all(0 <= bindus <= 8 for bindus in record["bindus_by_sign"])
        assert record["rekhas_by_sign"] == [
            8 - bindus for bindus in record["bindus_by_sign"]
        ]
        assert record["total_bindus"] == EXPECTED_TOTALS[graha]
        assert record["expected_total_bindus"] == EXPECTED_TOTALS[graha]
        assert record["total_valid"] is True
        assert sum(record["bindus_by_sign"]) == EXPECTED_TOTALS[graha]

        for row in record["contributor_rows"]:
            assert len(row["bindus_by_sign"]) == 12
            assert set(row["bindus_by_sign"]) <= {0, 1}
            assert row["total_bindus"] == len(row["favorable_relative_houses"])
            assert sum(row["bindus_by_sign"]) == row["total_bindus"]
            expected_indices = favorable_sign_indices(
                row["source_sign_index"],
                tuple(row["favorable_relative_houses"]),
            )
            assert row["bindu_sign_indices"] == list(expected_indices)

    sarva = payload["sarvashtakavarga"]
    assert len(sarva["bindus_by_sign"]) == 12
    assert sarva["total_bindus"] == EXPECTED_SARVASHTAKAVARGA_TOTAL
    assert sarva["expected_total_bindus"] == EXPECTED_SARVASHTAKAVARGA_TOTAL
    assert sarva["total_valid"] is True
    assert sum(sarva["bindus_by_sign"]) == EXPECTED_SARVASHTAKAVARGA_TOTAL
    assert len(sarva["signs"]) == 12

    records_by_graha = {record["graha"]: record for record in records}
    for offset, sign in enumerate(sarva["signs"]):
        expected_by_graha = {
            graha: records_by_graha[graha]["bindus_by_sign"][offset]
            for graha in CLASSICAL_GRAHAS
        }
        assert sign["sign_index"] == offset + 1
        assert sign["bindus_by_graha"] == expected_by_graha
        assert sign["sarvashtakavarga_bindus"] == sum(
            expected_by_graha.values()
        )
        assert sarva["bindus_by_sign"][offset] == sign[
            "sarvashtakavarga_bindus"
        ]


def test_contributor_positions_match_existing_d1_chart() -> None:
    ashtakavarga_response = client.post(
        f"{BASE_PATH}/ashtakavarga",
        json=_payload(),
    )
    d1_response = client.post("/v1/charts/d1", json=_payload())
    ashtakavarga = ashtakavarga_response.json()
    d1 = d1_response.json()

    assert ashtakavarga_response.status_code == 200, ashtakavarga
    assert d1_response.status_code == 200, d1

    positions = {
        position["contributor"]: position
        for position in ashtakavarga["contributor_positions"]
    }
    d1_points = {point["name"]: point for point in d1["points"]}
    for graha in CLASSICAL_GRAHAS:
        assert positions[graha]["sign_index"] == d1_points[graha]["sign_index"]
        assert positions[graha]["source_longitude"] == d1_points[graha][
            "source_longitude"
        ]

    assert positions["lagna"]["sign_index"] == d1["ascendant"]["sign_index"]
    assert positions["lagna"]["source_longitude"] == d1["ascendant"][
        "source_longitude"
    ]
    assert ashtakavarga["ascendant_sign_index"] == d1["ascendant"]["sign_index"]

    for sign in ashtakavarga["sarvashtakavarga"]["signs"]:
        expected_house = (
            (sign["sign_index"] - d1["ascendant"]["sign_index"]) % 12
        ) + 1
        assert sign["house_from_lagna"] == expected_house


def test_ashtakavarga_rejects_unknown_timezone() -> None:
    payload = _payload()
    payload["birth"]["timezone"] = "India/Not-A-Timezone"  # type: ignore[index]

    response = client.post(f"{BASE_PATH}/ashtakavarga", json=payload)

    assert response.status_code == 422
    assert "Unknown IANA timezone" in response.json()["detail"]
