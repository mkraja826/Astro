from datetime import UTC, datetime

import pytest

import app.engine.compatibility_facts as compatibility_facts_module
from app.engine.compatibility_facts import calculate_compatibility_facts
from app.schemas.compatibility import (
    ComponentEvaluationStatus,
    DualChartCompatibilityRequest,
    TraditionalCompatibilityRole,
)
from app.schemas.positions import (
    BirthInput,
    CalculationProfile,
    Coordinates,
    EngineMetadata,
    NormalizedTime,
    PlanetPosition,
    PositionsResponse,
    ZodiacPosition,
)


def birth(day: int) -> BirthInput:
    return BirthInput(
        local_datetime=datetime(1998, 10, day, 10, 28),
        timezone="Asia/Kolkata",
        latitude=16.575 + (day - 26),
        longitude=79.312,
        altitude_meters=100,
    )


def zodiac(
    *,
    sign_index: int,
    nakshatra_index: int = 1,
    degree: float = 5.0,
) -> dict[str, object]:
    return {
        "longitude": ((sign_index - 1) * 30.0) + degree,
        "sign_index": sign_index,
        "sign": f"Sign {sign_index}",
        "degree_in_sign": degree,
        "nakshatra_index": nakshatra_index,
        "nakshatra": f"Nakshatra {nakshatra_index}",
        "pada": 1,
        "whole_sign_house": 1,
    }


def planet(
    body: str,
    *,
    sign_index: int,
    nakshatra_index: int = 1,
    degree: float = 5.0,
) -> PlanetPosition:
    return PlanetPosition(
        body=body,
        latitude=0.0,
        distance_au=1.0,
        speed_longitude=1.0,
        retrograde=False,
        **zodiac(
            sign_index=sign_index,
            nakshatra_index=nakshatra_index,
            degree=degree,
        ),
    )


def metadata(*, provider_version: str = "test") -> EngineMetadata:
    return EngineMetadata(
        engine="jyothisyam-api",
        engine_version="test",
        astronomical_provider="skyfield_jpl",
        provider_version=provider_version,
        ephemeris_model="de440s",
        swiss_ephemeris_version=None,
        zodiac="sidereal",
        ayanamsha="lahiri",
        node_type="true_osculating",
        house_system="whole_sign",
        ephemeris_sources=["jpl_de440s"],
    )


def positions(
    request_id: str,
    *,
    moon_sign: int,
    moon_nakshatra: int,
    moon_degree: float = 5.0,
    provider_version: str = "test",
) -> PositionsResponse:
    signs = {
        "sun": 1,
        "moon": moon_sign,
        "mars": 3,
        "mercury": 4,
        "jupiter": 5,
        "venus": 6,
        "saturn": 7,
    }
    planets = [
        planet(
            body,
            sign_index=sign_index,
            nakshatra_index=moon_nakshatra if body == "moon" else 1,
            degree=moon_degree if body == "moon" else 5.0,
        )
        for body, sign_index in signs.items()
    ]
    return PositionsResponse(
        request_id=request_id,
        calculation_profile=(
            CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
        ),
        time=NormalizedTime(
            local_datetime=datetime(1998, 10, 26, 10, 28, tzinfo=UTC),
            utc_datetime=datetime(1998, 10, 26, 4, 58, tzinfo=UTC),
            timezone="Asia/Kolkata",
            fold=0,
            julian_day_ut=2451112.7,
        ),
        coordinates=Coordinates(
            latitude=16.575,
            longitude=79.312,
            altitude_meters=100,
        ),
        ayanamsha_degrees=23.8,
        ascendant=ZodiacPosition(**zodiac(sign_index=1)),
        planets=planets,
        metadata=metadata(provider_version=provider_version),
    )


def install_fake_positions(monkeypatch: pytest.MonkeyPatch) -> list[object]:
    responses = iter(
        [
            positions("subject", moon_sign=1, moon_nakshatra=1),
            positions("partner", moon_sign=3, moon_nakshatra=2),
        ]
    )
    calls: list[object] = []

    def fake_calculate(request: object) -> PositionsResponse:
        calls.append(request)
        return next(responses)

    monkeypatch.setattr(
        compatibility_facts_module,
        "calculate_positions",
        fake_calculate,
    )
    return calls


def test_assembler_calculates_two_charts_and_abstains_without_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_fake_positions(monkeypatch)
    request = DualChartCompatibilityRequest(
        subject_birth=birth(26),
        partner_birth=birth(27),
    )

    result = calculate_compatibility_facts(request)

    assert len(calls) == 2
    assert calls[0].birth == request.subject_birth
    assert calls[1].birth == request.partner_birth
    assert result.request_id.startswith("compat_")
    assert result.evaluated_maximum_points == 27
    assert not result.complete_36_point_evaluation
    assert sum(
        item.status is ComponentEvaluationStatus.ABSTAINED
        for item in result.ashtakoota_components
    ) == 3
    assert len(result.subject_fingerprint) == 64
    assert len(result.partner_fingerprint) == 64

    serialized = result.model_dump_json()
    assert "subject_birth" not in serialized
    assert "partner_birth" not in serialized
    assert "local_datetime" not in serialized


def test_assembler_returns_complete_36_point_facts_with_explicit_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_fake_positions(monkeypatch)
    request = DualChartCompatibilityRequest(
        subject_birth=birth(26),
        partner_birth=birth(27),
        subject_role=TraditionalCompatibilityRole.BRIDE,
        partner_role=TraditionalCompatibilityRole.GROOM,
    )

    result = calculate_compatibility_facts(request)

    assert result.evaluated_maximum_points == 36
    assert result.complete_36_point_evaluation
    assert all(
        item.status is ComponentEvaluationStatus.EVALUATED
        for item in result.ashtakoota_components
    )
    assert 0 <= result.total_achieved_points <= 36
    assert len(result.subject_manglik_factors) == 3
    assert len(result.partner_manglik_factors) == 3
    assert all(item.rule_ids for item in result.subject_manglik_factors)
    assert any("not rejection rules" in caveat for caveat in result.caveats)


def test_assembler_rejects_mismatched_engine_provenance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = iter(
        [
            positions("subject", moon_sign=1, moon_nakshatra=1),
            positions(
                "partner",
                moon_sign=3,
                moon_nakshatra=2,
                provider_version="different",
            ),
        ]
    )
    monkeypatch.setattr(
        compatibility_facts_module,
        "calculate_positions",
        lambda _request: next(responses),
    )

    with pytest.raises(ValueError, match="different engine provenance"):
        calculate_compatibility_facts(
            DualChartCompatibilityRequest(
                subject_birth=birth(26),
                partner_birth=birth(27),
            )
        )
