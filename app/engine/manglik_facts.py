"""Deterministic, non-interpretive Manglik/Kuja placement facts."""

from __future__ import annotations

from app.schemas.compatibility import (
    CompatibilityNatalFacts,
    ManglikFact,
    ManglikReferencePoint,
)

MANGLIK_CONVENTION_PROFILE = "lagna_moon_venus_1247812_v1"
MANGLIK_FLAGGED_HOUSES = frozenset({1, 2, 4, 7, 8, 12})
MANGLIK_RULE_ID = "ASTRO-CONV-MANGLIK-HOUSE-FACTS-001"


def _house_from(reference_sign: int, mars_sign: int) -> int:
    return ((mars_sign - reference_sign) % 12) + 1


def evaluate_manglik_factors(
    natal: CompatibilityNatalFacts,
) -> tuple[ManglikFact, ManglikFact, ManglikFact]:
    """Return independent Mars-house facts from Lagna, Moon, and Venus."""

    try:
        mars_sign = natal.planet_sign_indices["mars"]
        venus_sign = natal.planet_sign_indices["venus"]
    except KeyError as exc:
        raise ValueError(f"compatibility natal facts are missing {exc.args[0]}") from exc

    references = (
        (ManglikReferencePoint.LAGNA, natal.ascendant_sign_index),
        (ManglikReferencePoint.MOON, natal.moon_sign_index),
        (ManglikReferencePoint.VENUS, venus_sign),
    )
    return tuple(
        ManglikFact(
            reference_point=reference_point,
            mars_house=(mars_house := _house_from(reference_sign, mars_sign)),
            flagged=mars_house in MANGLIK_FLAGGED_HOUSES,
            rule_ids=[MANGLIK_RULE_ID],
            notes=[
                f"Convention profile: {MANGLIK_CONVENTION_PROFILE}.",
                "Flagged houses are 1, 2, 4, 7, 8, and 12.",
                "No cancellation, severity, or relationship-outcome rule is applied.",
            ],
        )
        for reference_point, reference_sign in references
    )
