from app.engine.compatibility_rules import (
    COMPATIBILITY_CONVENTION_PROFILE,
    DIRECTIONAL_COMPONENTS,
    EVALUATED_COMPONENTS,
    PENDING_CONVENTION_COMPONENTS,
    evaluate_all_components_with_abstentions,
    evaluate_bhakoot,
    evaluate_direction_independent_components,
    evaluate_graha_maitri,
    evaluate_nadi,
    evaluate_tara,
    evaluate_yoni,
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
    nakshatra: int,
) -> CompatibilityNatalFacts:
    return CompatibilityNatalFacts(
        chart_fingerprint=fingerprint,
        ascendant_sign_index=1,
        moon_sign_index=moon_sign,
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


def test_component_release_boundary_covers_all_eight_without_overlap() -> None:
    groups = (
        set(DIRECTIONAL_COMPONENTS),
        set(PENDING_CONVENTION_COMPONENTS),
        set(EVALUATED_COMPONENTS),
    )

    assert groups[0].isdisjoint(groups[1])
    assert groups[0].isdisjoint(groups[2])
    assert groups[1].isdisjoint(groups[2])
    assert set.union(*groups) == set(AshtakootaComponent)
    assert PENDING_CONVENTION_COMPONENTS == ()
    assert AshtakootaComponent.TARA in EVALUATED_COMPONENTS


def test_tara_uses_reciprocal_inclusive_counts_and_is_symmetric() -> None:
    janma = evaluate_tara(1, 1)
    one_challenging_direction = evaluate_tara(1, 3)
    reversed_pair = evaluate_tara(3, 1)

    assert janma.achieved_points == 3
    assert one_challenging_direction.achieved_points == 1.5
    assert reversed_pair.achieved_points == one_challenging_direction.achieved_points
    assert one_challenging_direction.maximum_points == 3
    assert any("remainders 3, 5, and 7" in note for note in janma.calculation_notes)


def test_yoni_table_is_symmetric_and_preserves_full_and_zero_boundaries() -> None:
    same = evaluate_yoni(1, 24)  # Ashwini and Shatabhisha: horse/horse
    enemy = evaluate_yoni(1, 13)  # Ashwini horse and Hasta buffalo
    reversed_enemy = evaluate_yoni(13, 1)

    assert same.achieved_points == 4
    assert enemy.achieved_points == 0
    assert reversed_enemy.achieved_points == enemy.achieved_points
    assert same.maximum_points == 4


def test_graha_maitri_uses_moon_sign_lord_table_symmetrically() -> None:
    same_lord = evaluate_graha_maitri(1, 8)  # Aries and Scorpio: Mars
    mixed = evaluate_graha_maitri(1, 2)  # Mars and Venus
    reversed_mixed = evaluate_graha_maitri(2, 1)

    assert same_lord.achieved_points == 5
    assert mixed.achieved_points == 3
    assert reversed_mixed.achieved_points == mixed.achieved_points
    assert mixed.maximum_points == 5


def test_bhakoot_blocks_configured_axes_and_is_symmetric() -> None:
    two_twelve = evaluate_bhakoot(1, 2)
    reversed_two_twelve = evaluate_bhakoot(2, 1)
    three_eleven = evaluate_bhakoot(1, 3)

    assert two_twelve.achieved_points == 0
    assert reversed_two_twelve.achieved_points == 0
    assert three_eleven.achieved_points == 7
    assert three_eleven.maximum_points == 7


def test_nadi_uses_fixed_groups_without_applying_cancellation_rules() -> None:
    same_group = evaluate_nadi(1, 6)  # Ashwini and Ardra: Adi
    different_group = evaluate_nadi(1, 2)  # Ashwini Adi, Bharani Madhya
    reversed_different = evaluate_nadi(2, 1)

    assert same_group.achieved_points == 0
    assert different_group.achieved_points == 8
    assert reversed_different.achieved_points == different_group.achieved_points
    assert different_group.maximum_points == 8
    assert any("No same-star" in note for note in same_group.calculation_notes)


def test_combined_evaluator_returns_five_released_raw_facts() -> None:
    subject = natal("a" * 64, moon_sign=1, nakshatra=1)
    partner = natal("b" * 64, moon_sign=3, nakshatra=2)

    facts = evaluate_direction_independent_components(subject, partner)

    assert tuple(item.component for item in facts) == EVALUATED_COMPONENTS
    assert sum(item.maximum_points for item in facts) == 27
    assert all(item.status is ComponentEvaluationStatus.EVALUATED for item in facts)
    assert all(item.source_kind == "convention" for item in facts)
    assert all(len(item.rule_ids) == 1 for item in facts)
    assert all(
        any(COMPATIBILITY_CONVENTION_PROFILE in note for note in item.calculation_notes)
        for item in facts
    )


def test_all_component_evaluator_abstains_for_directional_points_without_imputation() -> None:
    subject = natal("a" * 64, moon_sign=1, nakshatra=1)
    partner = natal("b" * 64, moon_sign=3, nakshatra=2)

    facts = evaluate_all_components_with_abstentions(subject, partner)

    assert tuple(item.component for item in facts) == tuple(AshtakootaComponent)
    abstained = [
        item for item in facts if item.status is ComponentEvaluationStatus.ABSTAINED
    ]
    evaluated = [
        item for item in facts if item.status is ComponentEvaluationStatus.EVALUATED
    ]
    assert {item.component for item in abstained} == set(DIRECTIONAL_COMPONENTS)
    assert all(item.achieved_points is None for item in abstained)
    assert sum(item.maximum_points for item in evaluated) == 27


def test_roles_change_abstention_reason_but_do_not_invent_directional_scores() -> None:
    subject = natal("a" * 64, moon_sign=1, nakshatra=1)
    partner = natal("b" * 64, moon_sign=3, nakshatra=2)

    facts = evaluate_all_components_with_abstentions(
        subject,
        partner,
        subject_role=TraditionalCompatibilityRole.BRIDE,
        partner_role=TraditionalCompatibilityRole.GROOM,
    )

    directional = [item for item in facts if item.component in DIRECTIONAL_COMPONENTS]
    assert all(item.status is ComponentEvaluationStatus.ABSTAINED for item in directional)
    assert all("not released" in (item.abstention_reason or "") for item in directional)
