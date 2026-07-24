from datetime import datetime

import pytest

import app.engine.compatibility_report as compatibility_report_module
from app.engine.compatibility_report import calculate_compatibility_report
from app.schemas.compatibility import (
    ASHTAKOOTA_MAXIMUM_POINTS,
    AshtakootaComponent,
    AshtakootaComponentFact,
    CompatibilityFactsResponse,
    CompatibilityNatalFacts,
    ComponentEvaluationStatus,
    DualChartCompatibilityRequest,
    ManglikFact,
    ManglikReferencePoint,
    TraditionalCompatibilityRole,
)
from app.schemas.positions import BirthInput, CalculationProfile, EngineMetadata


def request(*, with_roles: bool) -> DualChartCompatibilityRequest:
    return DualChartCompatibilityRequest(
        subject_birth=BirthInput(
            local_datetime=datetime(1998, 10, 26, 10, 28),
            timezone="Asia/Kolkata",
            latitude=16.575,
            longitude=79.312,
        ),
        partner_birth=BirthInput(
            local_datetime=datetime(1999, 5, 14, 8, 15),
            timezone="Asia/Kolkata",
            latitude=17.385,
            longitude=78.487,
        ),
        subject_role=(
            TraditionalCompatibilityRole.BRIDE
            if with_roles
            else TraditionalCompatibilityRole.UNSPECIFIED
        ),
        partner_role=(
            TraditionalCompatibilityRole.GROOM
            if with_roles
            else TraditionalCompatibilityRole.UNSPECIFIED
        ),
    )


def natal(fingerprint: str) -> CompatibilityNatalFacts:
    return CompatibilityNatalFacts(
        chart_fingerprint=fingerprint,
        ascendant_sign_index=1,
        moon_sign_index=2,
        moon_degree_in_sign=10.5,
        moon_nakshatra_index=3,
        moon_nakshatra="Krittika",
        moon_pada=2,
        planet_sign_indices={
            "sun": 1,
            "moon": 2,
            "mars": 3,
            "mercury": 4,
            "jupiter": 5,
            "venus": 6,
            "saturn": 7,
        },
    )


def manglik(reference: ManglikReferencePoint, flagged: bool) -> ManglikFact:
    return ManglikFact(
        reference_point=reference,
        mars_house=7 if flagged else 3,
        flagged=flagged,
        rule_ids=["ASTRO-CONV-MANGLIK-HOUSE-FACTS-001"],
        notes=["Context only."],
    )


def facts(*, complete: bool) -> CompatibilityFactsResponse:
    directional = {
        AshtakootaComponent.VARNA,
        AshtakootaComponent.VASHYA,
        AshtakootaComponent.GANA,
    }
    components = [
        AshtakootaComponentFact(
            component=component,
            status=(
                ComponentEvaluationStatus.EVALUATED
                if complete or component not in directional
                else ComponentEvaluationStatus.ABSTAINED
            ),
            achieved_points=(
                maximum / 2 if complete or component not in directional else None
            ),
            maximum_points=maximum,
            rule_ids=[f"ASTRO-{component.value.upper()}"],
            source_kind="convention",
            abstention_reason=(
                None
                if complete or component not in directional
                else "Traditional roles were absent."
            ),
            calculation_notes=["Frozen convention."],
        )
        for component, maximum in ASHTAKOOTA_MAXIMUM_POINTS.items()
    ]
    evaluated = [
        item for item in components if item.status is ComponentEvaluationStatus.EVALUATED
    ]
    subject_fingerprint = "a" * 64
    partner_fingerprint = "b" * 64
    return CompatibilityFactsResponse(
        request_id="compat_test",
        calculation_profile=(
            CalculationProfile.SOUTH_INDIAN_DRIK_LAHIRI_JPL_DE440S_V1
        ),
        subject_fingerprint=subject_fingerprint,
        partner_fingerprint=partner_fingerprint,
        pair_fingerprint="c" * 64,
        subject=natal(subject_fingerprint),
        partner=natal(partner_fingerprint),
        ashtakoota_components=components,
        total_achieved_points=sum(item.achieved_points or 0 for item in evaluated),
        evaluated_maximum_points=sum(item.maximum_points for item in evaluated),
        complete_36_point_evaluation=complete,
        subject_manglik_factors=[
            manglik(ManglikReferencePoint.LAGNA, True),
            manglik(ManglikReferencePoint.MOON, False),
            manglik(ManglikReferencePoint.VENUS, True),
        ],
        partner_manglik_factors=[
            manglik(ManglikReferencePoint.LAGNA, False),
            manglik(ManglikReferencePoint.MOON, False),
            manglik(ManglikReferencePoint.VENUS, True),
        ],
        rule_ids=["ASTRO-COMPATIBILITY-FACTS-ASSEMBLER-001"],
        metadata=EngineMetadata(
            engine="jyothisyam-api",
            engine_version="test",
            astronomical_provider="skyfield_jpl",
            provider_version="1.54",
            ephemeris_model="de440s",
            zodiac="sidereal",
            ayanamsha="lahiri",
            node_type="true_osculating",
            house_system="whole_sign",
            ephemeris_sources=["jpl_de440s"],
        ),
        caveats=["Traditional calculation facts only."],
    )


def test_complete_report_preserves_facts_and_adds_interpretation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_facts = facts(complete=True)
    monkeypatch.setattr(
        compatibility_report_module,
        "calculate_compatibility_facts",
        lambda _request: raw_facts,
    )

    report = calculate_compatibility_report(request(with_roles=True))

    assert report.facts == raw_facts
    assert report.interpretation.complete_36_point_evaluation
    assert report.interpretation.evaluated_maximum_points == 36
    assert report.interpretation.partnership_index.score is not None
    assert len(report.interpretation.components) == 8
    assert report.interpretation.manglik_context.subject_flagged_count == 2
    assert "not a probability" in report.interpretation.disclaimer


def test_partial_report_keeps_directional_abstentions_and_27_point_coverage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_facts = facts(complete=False)
    monkeypatch.setattr(
        compatibility_report_module,
        "calculate_compatibility_facts",
        lambda _request: raw_facts,
    )

    report = calculate_compatibility_report(request(with_roles=False))

    assert not report.interpretation.complete_36_point_evaluation
    assert report.interpretation.evaluated_maximum_points == 27
    assert report.interpretation.partnership_index.coverage == 0.75
    assert sum(
        item.status == "abstained" for item in report.interpretation.components
    ) == 3
    assert any("partial" in item.lower() for item in report.interpretation.cautions)


def test_report_response_contains_no_raw_birth_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        compatibility_report_module,
        "calculate_compatibility_facts",
        lambda _request: facts(complete=True),
    )

    serialized = calculate_compatibility_report(request(with_roles=True)).model_dump_json()

    assert "subject_birth" not in serialized
    assert "partner_birth" not in serialized
    assert "local_datetime" not in serialized
    assert "birth_place" not in serialized
