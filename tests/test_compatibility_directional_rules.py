import pytest

from app.engine.compatibility_directional_rules import (
    DIRECTIONAL_RULE_PROFILE,
    evaluate_ashtakoota_components,
    evaluate_gana,
    evaluate_varna,
    evaluate_vashya,
    summarize_ashtakoota_coverage,
)
from app.schemas.compatibility import (
    AshtakootaComponent,
    CompatibilityNatalFacts,
    ComponentEvaluationStatus,
    TraditionalCompatibilityRole,
)


def natal(
    fingerprint: str,
    *,
    moon_sign: int,
    moon_degree: float,
    nakshatra: int,
) -> CompatibilityNatalFacts:
    return CompatibilityNatalFacts(
        chart_fingerprint=fingerprint,
        ascendant_sign_index=1,
        moon_sign_index=moon_sign,
        moon_degree_in_sign=moon_degree,
        moon_nakshatra_index=nakshatra,
        moon_nakshatra=f"Nakshatra {nakshatra}",
        moon_pada=1,
        planet_sign_indices={
            "sun": 1,
            "moon": moon_sign,
            "mars": 3,
            "mercury": 4,
            "jupiter": 5,
            "venus": 6,
            "saturn": 7,
        },
    )


def test_varna_is_directional_and_uses_bride_groom_roles() -> None:
    water = natal("a" * 64, moon_sign=4, moon_degree=10, nakshatra=8)
    fire = natal("b" * 64, moon_sign=1, moon_degree=10, nakshatra=1)

    lower_groom = evaluate_varna(
        water,
        fire,
        subject_role=TraditionalCompatibilityRole.BRIDE,
        partner_role=TraditionalCompatibilityRole.GROOM,
    )
    higher_groom = evaluate_varna(
        water,
        fire,
        subject_role=TraditionalCompatibilityRole.GROOM,
        partner_role=TraditionalCompatibilityRole.BRIDE,
    )

    assert lower_groom.achieved_points == 0
    assert higher_groom.achieved_points == 1
    assert lower_groom.maximum_points == 1


def test_vashya_uses_directional_matrix_and_half_sign_boundaries() -> None:
    sagittarius_first_half = natal(
        "a" * 64,
        moon_sign=9,
        moon_degree=14.999,
        nakshatra=19,
    )
    sagittarius_second_half = natal(
        "c" * 64,
        moon_sign=9,
        moon_degree=15.0,
        nakshatra=20,
    )
    aries = natal("b" * 64, moon_sign=1, moon_degree=10, nakshatra=1)

    human_to_quadruped = evaluate_vashya(
        sagittarius_first_half,
        aries,
        subject_role=TraditionalCompatibilityRole.BRIDE,
        partner_role=TraditionalCompatibilityRole.GROOM,
    )
    quadruped_to_quadruped = evaluate_vashya(
        sagittarius_second_half,
        aries,
        subject_role=TraditionalCompatibilityRole.BRIDE,
        partner_role=TraditionalCompatibilityRole.GROOM,
    )

    assert human_to_quadruped.achieved_points == 1
    assert quadruped_to_quadruped.achieved_points == 2
    assert any("split at 15 degrees" in note for note in human_to_quadruped.calculation_notes)


def test_gana_preserves_directional_bride_row_groom_column_scores() -> None:
    deva = natal("a" * 64, moon_sign=1, moon_degree=5, nakshatra=1)
    manushya = natal("b" * 64, moon_sign=2, moon_degree=5, nakshatra=2)

    deva_bride = evaluate_gana(
        deva,
        manushya,
        subject_role=TraditionalCompatibilityRole.BRIDE,
        partner_role=TraditionalCompatibilityRole.GROOM,
    )
    manushya_bride = evaluate_gana(
        deva,
        manushya,
        subject_role=TraditionalCompatibilityRole.GROOM,
        partner_role=TraditionalCompatibilityRole.BRIDE,
    )

    assert deva_bride.achieved_points == 6
    assert manushya_bride.achieved_points == 5
    assert any(DIRECTIONAL_RULE_PROFILE in note for note in deva_bride.calculation_notes)


def test_directional_evaluators_reject_missing_or_duplicate_roles() -> None:
    subject = natal("a" * 64, moon_sign=1, moon_degree=5, nakshatra=1)
    partner = natal("b" * 64, moon_sign=2, moon_degree=5, nakshatra=2)

    with pytest.raises(ValueError, match="one bride role and one groom role"):
        evaluate_varna(
            subject,
            partner,
            subject_role=TraditionalCompatibilityRole.UNSPECIFIED,
            partner_role=TraditionalCompatibilityRole.UNSPECIFIED,
        )


def test_aggregate_abstains_without_roles_and_reports_27_point_coverage() -> None:
    subject = natal("a" * 64, moon_sign=1, moon_degree=5, nakshatra=1)
    partner = natal("b" * 64, moon_sign=3, moon_degree=5, nakshatra=2)

    components = evaluate_ashtakoota_components(subject, partner)
    achieved, evaluated_maximum, complete = summarize_ashtakoota_coverage(components)

    assert tuple(item.component for item in components) == tuple(AshtakootaComponent)
    assert evaluated_maximum == 27
    assert not complete
    assert achieved >= 0
    assert sum(
        item.status is ComponentEvaluationStatus.ABSTAINED for item in components
    ) == 3


def test_aggregate_with_roles_returns_complete_36_point_fact_set() -> None:
    subject = natal("a" * 64, moon_sign=1, moon_degree=5, nakshatra=1)
    partner = natal("b" * 64, moon_sign=3, moon_degree=5, nakshatra=2)

    components = evaluate_ashtakoota_components(
        subject,
        partner,
        subject_role=TraditionalCompatibilityRole.BRIDE,
        partner_role=TraditionalCompatibilityRole.GROOM,
    )
    achieved, evaluated_maximum, complete = summarize_ashtakoota_coverage(components)

    assert evaluated_maximum == 36
    assert complete
    assert 0 <= achieved <= 36
    assert all(
        item.status is ComponentEvaluationStatus.EVALUATED for item in components
    )
