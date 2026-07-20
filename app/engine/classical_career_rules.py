"""Rule registrations and profile extension for Karmājīva career analysis."""

from app.engine.classical_aspect_rules import (
    extend_varahamihira_profile as extend_aspect_profile,
)
from app.engine.classical_aspect_rules import (
    extend_varahamihira_rules as extend_aspect_rules,
)
from app.engine.classical_reference import PROFILE_ID, SOURCE_ID
from app.schemas.classical import (
    CitationPrecision,
    ClassicalProfileResponse,
    ClassicalRuleReference,
    RuleImplementationStatus,
    RuleRegistryResponse,
)

CAREER_ENDPOINT = "/v1/classical/varahamihira_v1/career"

CAREER_RULES = (
    ClassicalRuleReference(
        rule_id="VM-BJ-C10-INCOME-SOURCE-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=10,
        verse_reference="10.1",
        citation_precision=CitationPrecision.VERSE,
        topic="tenth_house_income_sources",
        statement=(
            "Classical Grahas occupying the 10th sign from Lagna or Moon indicate "
            "source relationships for acquiring wealth."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "reference_point",
            "tenth_sign",
            "tenth_house_occupants",
            "income_source_indications",
        ],
        notes=[
            "Multiple occupants and both reference points are retained as multiple sources.",
            "Rahu and Ketu are excluded from the seven-Graha mapping.",
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C10-NAVAMSA-LORD-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=10,
        verse_reference="10.1",
        citation_precision=CitationPrecision.VERSE,
        topic="karmājīva_indicator_derivation",
        statement=(
            "For the 10th signs from Lagna, Moon, and Sun, the lord of the Navamsa "
            "occupied by each 10th lord supplies a vocation indicator."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "tenth_lord",
            "tenth_lord_d9_sign",
            "karmājīva_indicator_graha",
        ],
        notes=[
            "All three channels are returned; this milestone does not select one winner.",
            "D9 uses the existing ninefold Navamsa calculation contract.",
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C10-VOCATION-SUN-MERCURY-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=10,
        verse_reference="10.2",
        citation_precision=CitationPrecision.VERSE,
        topic="vocation_themes_sun_to_mercury",
        statement=(
            "Sun, Moon, Mars, and Mercury indicators map to the vocation themes "
            "enumerated in Chapter 10.2."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=["karmājīva_indicator_graha", "vocation_themes"],
        notes=[
            "Modern examples are explanatory labels, not additional classical rules.",
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C10-VOCATION-JUPITER-SATURN-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=10,
        verse_reference="10.3",
        citation_precision=CitationPrecision.VERSE,
        topic="vocation_themes_jupiter_to_saturn",
        statement=(
            "Jupiter, Venus, and Saturn indicators map to the vocation themes "
            "enumerated in Chapter 10.3."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=["karmājīva_indicator_graha", "vocation_themes"],
        notes=[
            "Archaic occupational language is preserved in classical_terms and "
            "modernized cautiously in modern_examples."
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C10-SUPPORT-FACTS-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=10,
        verse_reference="10.4",
        citation_precision=CitationPrecision.VERSE,
        topic="career_support_facts",
        statement=(
            "Dignity, placement, conjunction, and benefic support are reported as "
            "transparent facts without applying a final strength ranking."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="medium",
        data_keys=[
            "indicator_condition",
            "aspects_to_tenth_sign",
            "ranking_applied",
        ],
        notes=[
            "Natural friendship, cancellations, and weighted strength are later milestones.",
            "No profession is guaranteed or ranked in this version.",
        ],
    ),
)


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Add Karmājīva capability after all earlier profile extensions."""

    extended = extend_aspect_profile(profile)
    endpoints = list(extended.endpoints)
    if CAREER_ENDPOINT not in endpoints:
        endpoints.append(CAREER_ENDPOINT)

    implemented_chapters = sorted({*extended.implemented_chapters, 10})
    source = extended.source.model_copy(
        update={
            "reference_scope": [
                *extended.source.reference_scope,
                "Chapter 10: Vocation (Karmājīva)",
            ]
        }
    )

    return extended.model_copy(
        update={
            "profile_version": "1.3.0",
            "source": source,
            "implemented_chapters": implemented_chapters,
            "career_analysis_enabled": True,
            "endpoints": endpoints,
            "caveats": [
                "Career output is source-traceable, plural, and non-exclusive.",
                "All Lagna, Moon, and Sun Karmājīva channels are retained.",
                "No primary profession is selected before strength weighting is validated.",
                "The evaluator does not alter D1, D9, Panchanga, or Vimshottari results.",
                "Ashtakavarga, Dasha interpretation, cancellations, and longevity are separate.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Append Chapter 10 rules after all condition and aspect rules."""

    extended = extend_aspect_rules(registry)
    return RuleRegistryResponse(
        profile_id=extended.profile_id,
        rules=[
            *extended.rules,
            *(rule.model_copy(deep=True) for rule in CAREER_RULES),
        ],
    )
