"""Integration tests for the Vimshottari Dasha endpoint."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

LORDS = [
    "ketu",
    "venus",
    "sun",
    "moon",
    "mars",
    "rahu",
    "jupiter",
    "saturn",
    "mercury",
]

YEARS = {
    "ketu": 7.0,
    "venus": 20.0,
    "sun": 6.0,
    "moon": 10.0,
    "mars": 7.0,
    "rahu": 18.0,
    "jupiter": 16.0,
    "saturn": 19.0,
    "mercury": 17.0,
}


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


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_vimshottari_returns_complete_birth_cycle() -> None:
    response = client.post("/v1/dashas/vimshottari", json=_payload())
    payload = response.json()

    assert response.status_code == 200, payload
    assert payload["request_id"].startswith("req_")
    assert payload["cycle_years"] == 120.0
    assert payload["year_length_days"] == 365.25
    assert 20 < payload["ayanamsha_degrees"] < 30

    moon = payload["moon"]
    assert 1 <= moon["nakshatra_index"] <= 27
    assert 1 <= moon["pada"] <= 4
    assert 0 <= moon["progress_percent"] < 100

    expected_lord = LORDS[(moon["nakshatra_index"] - 1) % len(LORDS)]
    assert payload["birth_lord"] == expected_lord

    periods = payload["mahadashas"]
    assert len(periods) == 9
    assert sum(period["duration_years"] for period in periods) == 120.0

    expected_sequence = [
        LORDS[(LORDS.index(expected_lord) + offset) % len(LORDS)]
        for offset in range(9)
    ]
    assert [period["lord"] for period in periods] == expected_sequence

    first = periods[0]
    birth_utc = _parse_datetime(payload["time"]["utc_datetime"])
    assert first["active_at_birth"] is True
    assert _parse_datetime(first["start_utc"]) <= birth_utc
    assert birth_utc < _parse_datetime(first["end_utc"])
    assert first["duration_years"] == YEARS[expected_lord]
    assert first["remaining_at_birth_years"] == pytest.approx(
        payload["birth_balance_years"], abs=1e-9
    )
    assert (
        first["elapsed_at_birth_years"] + first["remaining_at_birth_years"]
        == pytest.approx(first["duration_years"], abs=1e-8)
    )

    for current, following in zip(periods[:-1], periods[1:], strict=True):
        assert current["end_utc"] == following["start_utc"]
        assert following["active_at_birth"] is False
        assert following["elapsed_at_birth_years"] is None
        assert following["remaining_at_birth_years"] is None

    first_pratyantardasha = first["antardashas"][0]["pratyantardashas"][0]
    assert first_pratyantardasha["sookshmadashas"] is None
    assert payload["metadata"]["zodiac"] == "sidereal"
    assert payload["metadata"]["ayanamsha"] == "lahiri"
    assert payload["metadata"]["ephemeris_sources"]


def test_vimshottari_returns_all_contiguous_subperiods() -> None:
    request_payload = _payload()
    request_payload["depth"] = "sookshma"
    response = client.post("/v1/dashas/vimshottari", json=request_payload)
    payload = response.json()

    assert response.status_code == 200, payload
    birth_utc = _parse_datetime(payload["time"]["utc_datetime"])
    active_antardashas: list[dict[str, object]] = []
    active_pratyantardashas: list[dict[str, object]] = []
    active_sookshmadashas: list[dict[str, object]] = []
    pratyantardasha_count = 0
    sookshmadasha_count = 0

    for mahadasha in payload["mahadashas"]:
        antardashas = mahadasha["antardashas"]
        assert len(antardashas) == 9
        assert antardashas[0]["start_utc"] == mahadasha["start_utc"]
        assert antardashas[-1]["end_utc"] == mahadasha["end_utc"]
        assert sum(item["duration_years"] for item in antardashas) == pytest.approx(
            mahadasha["duration_years"],
            abs=1e-7,
        )

        lord_start_index = LORDS.index(mahadasha["lord"])
        expected_sequence = [
            LORDS[(lord_start_index + offset) % len(LORDS)] for offset in range(9)
        ]
        assert [item["lord"] for item in antardashas] == expected_sequence

        for current, following in zip(
            antardashas[:-1],
            antardashas[1:],
            strict=True,
        ):
            assert current["end_utc"] == following["start_utc"]

        active_antardashas.extend(
            item for item in antardashas if item["active_at_birth"]
        )

        for antardasha in antardashas:
            pratyantardashas = antardasha["pratyantardashas"]
            pratyantardasha_count += len(pratyantardashas)
            assert len(pratyantardashas) == 9
            assert pratyantardashas[0]["start_utc"] == antardasha["start_utc"]
            assert pratyantardashas[-1]["end_utc"] == antardasha["end_utc"]
            assert sum(
                item["duration_years"] for item in pratyantardashas
            ) == pytest.approx(antardasha["duration_years"], abs=2e-8)

            sub_start_index = LORDS.index(antardasha["lord"])
            expected_subsequence = [
                LORDS[(sub_start_index + offset) % len(LORDS)]
                for offset in range(9)
            ]
            assert [item["lord"] for item in pratyantardashas] == expected_subsequence

            for current, following in zip(
                pratyantardashas[:-1],
                pratyantardashas[1:],
                strict=True,
            ):
                assert current["end_utc"] == following["start_utc"]

            active_pratyantardashas.extend(
                item for item in pratyantardashas if item["active_at_birth"]
            )

            for pratyantardasha in pratyantardashas:
                sookshmadashas = pratyantardasha["sookshmadashas"]
                sookshmadasha_count += len(sookshmadashas)
                assert len(sookshmadashas) == 9
                assert sookshmadashas[0]["start_utc"] == pratyantardasha["start_utc"]
                assert sookshmadashas[-1]["end_utc"] == pratyantardasha["end_utc"]
                assert sum(
                    item["duration_years"] for item in sookshmadashas
                ) == pytest.approx(pratyantardasha["duration_years"], abs=2e-10)

                sookshma_start_index = LORDS.index(pratyantardasha["lord"])
                expected_sookshma_sequence = [
                    LORDS[(sookshma_start_index + offset) % len(LORDS)]
                    for offset in range(9)
                ]
                assert [
                    item["lord"] for item in sookshmadashas
                ] == expected_sookshma_sequence

                for current, following in zip(
                    sookshmadashas[:-1],
                    sookshmadashas[1:],
                    strict=True,
                ):
                    assert current["end_utc"] == following["start_utc"]

                active_sookshmadashas.extend(
                    item for item in sookshmadashas if item["active_at_birth"]
                )

    assert pratyantardasha_count == 729
    assert sookshmadasha_count == 6_561
    assert len(active_antardashas) == 1
    active_antardasha = active_antardashas[0]
    assert _parse_datetime(active_antardasha["start_utc"]) <= birth_utc
    assert birth_utc < _parse_datetime(active_antardasha["end_utc"])
    assert (
        active_antardasha["elapsed_at_birth_years"]
        + active_antardasha["remaining_at_birth_years"]
        == pytest.approx(active_antardasha["duration_years"], abs=2e-8)
    )

    assert len(active_pratyantardashas) == 1
    active_pratyantardasha = active_pratyantardashas[0]
    assert _parse_datetime(active_pratyantardasha["start_utc"]) <= birth_utc
    assert birth_utc < _parse_datetime(active_pratyantardasha["end_utc"])
    assert (
        active_pratyantardasha["elapsed_at_birth_years"]
        + active_pratyantardasha["remaining_at_birth_years"]
        == pytest.approx(active_pratyantardasha["duration_years"], abs=2e-8)
    )

    assert len(active_sookshmadashas) == 1
    active_sookshmadasha = active_sookshmadashas[0]
    assert _parse_datetime(active_sookshmadasha["start_utc"]) <= birth_utc
    assert birth_utc < _parse_datetime(active_sookshmadasha["end_utc"])
    assert (
        active_sookshmadasha["elapsed_at_birth_years"]
        + active_sookshmadasha["remaining_at_birth_years"]
        == pytest.approx(active_sookshmadasha["duration_years"], abs=2e-8)
    )


def test_vimshottari_rejects_unknown_timezone() -> None:
    payload = _payload()
    payload["birth"]["timezone"] = "India/Not-A-Timezone"  # type: ignore[index]

    response = client.post("/v1/dashas/vimshottari", json=payload)

    assert response.status_code == 422
    assert "Unknown IANA timezone" in response.json()["detail"]


def test_vimshottari_rejects_ambiguous_time_without_fold() -> None:
    payload = _payload()
    payload["birth"] = {
        "local_datetime": "2024-11-03T01:30:00",
        "timezone": "America/New_York",
        "latitude": 40.7128,
        "longitude": -74.006,
    }

    response = client.post("/v1/dashas/vimshottari", json=payload)

    assert response.status_code == 422
    assert "ambiguous" in response.json()["detail"].lower()
