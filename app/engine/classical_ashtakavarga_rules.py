"""Rule registrations and profile extension for Chapter 9 Ashtakavarga."""

from app.engine.classical_career_rules import (
    extend_varahamihira_profile as extend_career_profile,
)
from app.engine.classical_career_rules import (
    extend_varahamihira_rules as extend_career_rules,
)
from app.engine.classical_reference import PROFILE_ID, SOURCE_ID
from app.schemas.classical import (
    CitationPrecision,
    ClassicalProfileResponse,
    ClassicalRuleReference,
    RuleImplementationStatus,
    RuleRegistryResponse,
)

ASHTAKAVARGA_ENDPOINT = "/v1/classical/varahamihira_v1/ashtakavarga"

_PLANET_VERSES = (
    ("SUN", "Sun", "9.1", 48),
    ("MOON", "Moon", "9.2", 49),
    ("MARS", "Mars", "9.3", 39),
    ("MERCURY", "Mercury", "9.4", 54),
    ("JUPITER", "Jupiter", "9.5", 56),
    ("VENUS", "Venus", "9.6", 52),
    ("SATURN", "Saturn", "9.7", 39),
)

ASHTAKAVARGA_RULES = tuple(
    ClassicalRuleReference(
        rule_id=f"VM-BJ-C09-{canonical}-BAV-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=9,
        verse_reference=verse,
        citation_precision=CitationPrecision.VERSE,
        topic=f"{display.lower()}_bhinnashtakavarga",
        statement=(
            f"Chapter 9 verse {verse} supplies the favorable relative houses "
            f"used to construct the {display} Bhinnashtakavarga from the seven "
            "classical Grahas and Lagna."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "contributor",
            "source_sign_index",
            "favorable_relative_houses",
            "bindus_by_sign",
            "total_bindus",
        ],
        notes=[
            f"The fixed raw bindu total for {display} is {expected_total}.",
            "Relative houses are rotated from each contributor's natal D1 sign.",
        ],
    )
    for canonical, display, verse, expected_total in _PLANET_VERSES
) + (
    ClassicalRuleReference(
        rule_id="VM-BJ-C09-SARVA-AGGREGATION-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=9,
        verse_reference="9.8",
        citation_precision=CitationPrecision.VERSE,
        topic="raw_sarvashtakavarga_aggregation",
        statement=(
            "The seven raw planetary Bhinnashtakavarga arrays are summed sign by "
            "sign to expose the Sarvashtakavarga bindu distribution."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "bhinnashtakavargas",
            "bindus_by_sign",
            "sarvashtakavarga_bindus",
            "total_bindus",
        ],
        notes=[
            "The raw seven-planet Sarvashtakavarga total is 337.",
            "No Trikona or Ekadhipatya reduction is applied in this version.",
            "The arithmetic output is not a transit or prediction score.",
        ],
    ),
)


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Add Ashtakavarga capability after all earlier profile extensions."""

    extended = extend_career_profile(profile)
    endpoints = list(extended.endpoints)
    if ASHTAKAVARGA_ENDPOINT not in endpoints:
        endpoints.append(ASHTAKAVARGA_ENDPOINT)

    implemented_chapters = sorted({*extended.implemented_chapters, 9})
    reference_scope = list(extended.source.reference_scope)
    chapter_scope = "Chapter 9: Ashtakavarga"
    if chapter_scope not in reference_scope:
        reference_scope.append(chapter_scope)
    source = extended.source.model_copy(
        update={"reference_scope": reference_scope}
    )

    return extended.model_copy(
        update={
            "profile_version": "1.4.0",
            "source": source,
            "implemented_chapters": implemented_chapters,
            "ashtakavarga_enabled": True,
            "endpoints": endpoints,
            "caveats": [
                "Ashtakavarga output is raw, deterministic bindu arithmetic.",
                "Seven Grahas and Lagna contribute to each planetary array.",
                "Sarvashtakavarga is the unweighted sum of seven planetary arrays.",
                "No reductions, transit judgment, or predictive ranking is included.",
                "The evaluator does not alter any existing calculation endpoint.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Append Chapter 9 rules after all earlier source-profile rules."""

    extended = extend_career_rules(registry)
    return RuleRegistryResponse(
        profile_id=extended.profile_id,
        rules=[
            *extended.rules,
            *(rule.model_copy(deep=True) for rule in ASHTAKAVARGA_RULES),
        ],
    )
