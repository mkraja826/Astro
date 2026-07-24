import pytest

from app.engine.manglik_facts import (
    MANGLIK_FLAGGED_HOUSES,
    evaluate_manglik_factors,
)
from app.schemas.compatibility import CompatibilityNatalFacts, ManglikReferencePoint


def natal(
    *,
    lagna_sign: int,
    moon_sign: int,
    venus_sign: int,
    mars_sign: int,
) -> CompatibilityNatalFacts:
    return CompatibilityNatalFacts(
        chart_fingerprint="a" * 64,
        ascendant_sign_index=lagna_sign,
        moon_sign_index=moon_sign,
        moon_degree_in_sign=5.0,
        moon_nakshatra_index=1,
        moon_nakshatra="Ashwini",
        moon_pada=1,
        planet_sign_indices={
            "sun": 1,
            "moon": moon_sign,
            "mars": mars_sign,
            "mercury": 4,
            "jupiter": 5,
            "venus": venus_sign,
            "saturn": 7,
        },
    )


def test_manglik_factors_are_independent_from_lagna_moon_and_venus() -> None:
    factors = evaluate_manglik_factors(
        natal(lagna_sign=1, moon_sign=12, venus_sign=8, mars_sign=2)
    )

    assert tuple(item.reference_point for item in factors) == (
        ManglikReferencePoint.LAGNA,
        ManglikReferencePoint.MOON,
        ManglikReferencePoint.VENUS,
    )
    assert tuple(item.mars_house for item in factors) == (2, 3, 7)
    assert tuple(item.flagged for item in factors) == (True, False, True)
    assert all(len(item.rule_ids) == 1 for item in factors)
    assert all(
        any("No cancellation" in note for note in item.notes) for item in factors
    )


def test_all_six_configured_houses_are_flagged() -> None:
    for expected_house in sorted(MANGLIK_FLAGGED_HOUSES):
        mars_sign = ((expected_house - 1) % 12) + 1
        lagna_factor = evaluate_manglik_factors(
            natal(lagna_sign=1, moon_sign=1, venus_sign=1, mars_sign=mars_sign)
        )[0]

        assert lagna_factor.mars_house == expected_house
        assert lagna_factor.flagged


def test_non_configured_houses_are_not_flagged() -> None:
    for expected_house in {3, 5, 6, 9, 10, 11}:
        mars_sign = expected_house
        lagna_factor = evaluate_manglik_factors(
            natal(lagna_sign=1, moon_sign=1, venus_sign=1, mars_sign=mars_sign)
        )[0]

        assert lagna_factor.mars_house == expected_house
        assert not lagna_factor.flagged


def test_missing_mars_or_venus_abstains_by_error_instead_of_guessing() -> None:
    facts = natal(lagna_sign=1, moon_sign=1, venus_sign=6, mars_sign=3)

    for missing_planet in ("mars", "venus"):
        incomplete = facts.model_copy(
            update={
                "planet_sign_indices": {
                    name: sign
                    for name, sign in facts.planet_sign_indices.items()
                    if name != missing_planet
                }
            }
        )
        with pytest.raises(ValueError, match=missing_planet):
            evaluate_manglik_factors(incomplete)
