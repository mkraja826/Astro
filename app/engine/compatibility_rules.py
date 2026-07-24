"""Direction-independent Phase 4 Ashtakoota calculation conventions.

These evaluators expose raw calculation facts only. They do not interpret a
relationship, guarantee an outcome, or decide whether a match should proceed.
Directional components remain disabled until the request contract carries an
explicit traditional role model. Tara remains disabled until its reciprocal
counting and Janma convention are frozen.
"""

from __future__ import annotations

from app.schemas.compatibility import (
    AshtakootaComponent,
    AshtakootaComponentFact,
    CompatibilityNatalFacts,
)

COMPATIBILITY_CONVENTION_PROFILE = "north_indian_ashtakoota_tables_v1"

DIRECTIONAL_COMPONENTS = (
    AshtakootaComponent.VARNA,
    AshtakootaComponent.VASHYA,
    AshtakootaComponent.GANA,
)
PENDING_CONVENTION_COMPONENTS = (AshtakootaComponent.TARA,)
EVALUATED_COMPONENTS = (
    AshtakootaComponent.YONI,
    AshtakootaComponent.GRAHA_MAITRI,
    AshtakootaComponent.BHAKOOT,
    AshtakootaComponent.NADI,
)

_YONI_NAMES = (
    "horse", "elephant", "sheep", "serpent", "dog", "cat", "rat",
    "cow", "buffalo", "tiger", "deer", "monkey", "mongoose", "lion",
)
_YONI_BY_NAKSHATRA = (
    0, 1, 2, 3, 3, 4, 5, 2, 5, 6, 6, 7, 8, 9, 8, 9, 10, 10,
    4, 11, 12, 11, 13, 0, 13, 7, 1,
)
_YONI_POINTS = (
    (4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 1, 3, 2, 1),
    (2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0),
    (2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1),
    (3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2),
    (2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1),
    (2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1),
    (2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2),
    (1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1),
    (0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1),
    (1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1),
    (1, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1),
    (3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2),
    (2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2),
    (1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4),
)

_PLANET_NAMES = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn")
_MOON_SIGN_LORD = (2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4)
_GRAHA_MAITRI_POINTS = (
    (5.0, 5.0, 5.0, 4.0, 5.0, 0.0, 0.0),
    (5.0, 5.0, 4.0, 1.0, 4.0, 0.5, 0.5),
    (5.0, 4.0, 5.0, 0.5, 5.0, 3.0, 0.5),
    (4.0, 1.0, 0.5, 5.0, 0.5, 5.0, 4.0),
    (5.0, 4.0, 5.0, 0.5, 5.0, 0.5, 3.0),
    (0.0, 0.5, 3.0, 5.0, 0.5, 5.0, 5.0),
    (0.0, 0.5, 0.5, 4.0, 3.0, 5.0, 5.0),
)

_NADI_NAMES = ("adi", "madhya", "antya")
_NADI_BY_NAKSHATRA = (
    0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0,
    0, 1, 2, 2, 1, 0, 0, 1, 2,
)


def _fact(
    component: AshtakootaComponent,
    points: float,
    rule_id: str,
    *notes: str,
) -> AshtakootaComponentFact:
    maximums = {
        AshtakootaComponent.YONI: 4,
        AshtakootaComponent.GRAHA_MAITRI: 5,
        AshtakootaComponent.BHAKOOT: 7,
        AshtakootaComponent.NADI: 8,
    }
    return AshtakootaComponentFact(
        component=component,
        achieved_points=points,
        maximum_points=maximums[component],
        rule_ids=[rule_id],
        source_kind="convention",
        calculation_notes=[
            f"Convention profile: {COMPATIBILITY_CONVENTION_PROFILE}.",
            *notes,
        ],
    )


def evaluate_yoni(
    subject_nakshatra_index: int,
    partner_nakshatra_index: int,
) -> AshtakootaComponentFact:
    """Return the symmetric North Indian Yoni table score."""

    subject_yoni = _YONI_BY_NAKSHATRA[subject_nakshatra_index - 1]
    partner_yoni = _YONI_BY_NAKSHATRA[partner_nakshatra_index - 1]
    points = float(_YONI_POINTS[subject_yoni][partner_yoni])
    return _fact(
        AshtakootaComponent.YONI,
        points,
        "ASTRO-CONV-ASHTAKOOTA-YONI-001",
        f"Subject Yoni: {_YONI_NAMES[subject_yoni]}.",
        f"Partner Yoni: {_YONI_NAMES[partner_yoni]}.",
        "The table is symmetric and is exposed as a raw comparison fact only.",
    )


def evaluate_graha_maitri(
    subject_moon_sign_index: int,
    partner_moon_sign_index: int,
) -> AshtakootaComponentFact:
    """Return the Moon-sign-lord friendship table score."""

    subject_lord = _MOON_SIGN_LORD[subject_moon_sign_index - 1]
    partner_lord = _MOON_SIGN_LORD[partner_moon_sign_index - 1]
    points = _GRAHA_MAITRI_POINTS[subject_lord][partner_lord]
    return _fact(
        AshtakootaComponent.GRAHA_MAITRI,
        points,
        "ASTRO-CONV-ASHTAKOOTA-GRAHA-MAITRI-001",
        f"Subject Moon-sign lord: {_PLANET_NAMES[subject_lord]}.",
        f"Partner Moon-sign lord: {_PLANET_NAMES[partner_lord]}.",
        "Natural-lord relationship is a convention table, not a measured probability.",
    )


def evaluate_bhakoot(
    subject_moon_sign_index: int,
    partner_moon_sign_index: int,
) -> AshtakootaComponentFact:
    """Return seven points except for the configured 2/12, 5/9, and 6/8 axes."""

    subject_to_partner = ((partner_moon_sign_index - subject_moon_sign_index) % 12) + 1
    partner_to_subject = ((subject_moon_sign_index - partner_moon_sign_index) % 12) + 1
    blocked_distances = {2, 5, 6, 8, 9, 12}
    points = 0.0 if subject_to_partner in blocked_distances else 7.0
    return _fact(
        AshtakootaComponent.BHAKOOT,
        points,
        "ASTRO-CONV-ASHTAKOOTA-BHAKOOT-001",
        f"Subject-to-partner inclusive sign count: {subject_to_partner}.",
        f"Partner-to-subject inclusive sign count: {partner_to_subject}.",
        "Configured challenging axes are 2/12, 5/9, and 6/8; no cancellation is applied.",
    )


def evaluate_nadi(
    subject_nakshatra_index: int,
    partner_nakshatra_index: int,
) -> AshtakootaComponentFact:
    """Return zero for equal Nadi groups and eight for different groups."""

    subject_nadi = _NADI_BY_NAKSHATRA[subject_nakshatra_index - 1]
    partner_nadi = _NADI_BY_NAKSHATRA[partner_nakshatra_index - 1]
    points = 0.0 if subject_nadi == partner_nadi else 8.0
    return _fact(
        AshtakootaComponent.NADI,
        points,
        "ASTRO-CONV-ASHTAKOOTA-NADI-001",
        f"Subject Nadi: {_NADI_NAMES[subject_nadi]}.",
        f"Partner Nadi: {_NADI_NAMES[partner_nadi]}.",
        "No same-star, same-sign, or other cancellation convention is applied in v1.",
    )


def evaluate_direction_independent_components(
    subject: CompatibilityNatalFacts,
    partner: CompatibilityNatalFacts,
) -> tuple[AshtakootaComponentFact, ...]:
    """Evaluate only components that do not require traditional role assignment."""

    return (
        evaluate_yoni(subject.moon_nakshatra_index, partner.moon_nakshatra_index),
        evaluate_graha_maitri(subject.moon_sign_index, partner.moon_sign_index),
        evaluate_bhakoot(subject.moon_sign_index, partner.moon_sign_index),
        evaluate_nadi(subject.moon_nakshatra_index, partner.moon_nakshatra_index),
    )
