"""Rule registrations for classical context on active Vimshottari periods."""

from app.engine.classical_ashtakavarga_rules import (
    extend_varahamihira_profile as extend_ashtakavarga_profile,
)
from app.engine.classical_ashtakavarga_rules import (
    extend_varahamihira_rules as extend_ashtakavarga_rules,
)
from app.engine.classical_reference import PROFILE_ID, SOURCE_ID
from app.schemas.classical import (
    CitationPrecision,
    ClassicalProfileResponse,
    ClassicalRuleReference,
    RuleImplementationStatus,
    RuleRegistryResponse,
)

DASHA_CONTEXT_ENDPOINT = "/v1/classical/varahamihira_v1/dasha/current"

DASHA_CONTEXT_RULES = (
    ClassicalRuleReference(
        rule_id="VM-BJ-C01-DASHA-OWNERSHIP-CONTEXT-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=1,
        citation_precision=CitationPrecision.CHAPTER,
        topic="active_dasha_lord_house_ownership",
        statement=(
            "An active Vimshottari lord is annotated with the whole-sign houses ruled "
            "by its Chapter 1 Rashi lordships."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=["lord", "owned_signs", "owned_houses", "d1_house"],
        notes=[
            "Vimshottari timing is supplied by the separate timing engine.",
            "This registration adds context and does not redefine Dasha periods.",
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-DASHA-CONDITION-CONTEXT-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="active_dasha_lord_condition_context",
        statement=(
            "The seven classical Graha lords are annotated with existing dignity, "
            "Vargottama, retrograde, and resolved tendency facts."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "dignity",
            "own_sign",
            "in_exaltation_sign",
            "in_debilitation_sign",
            "vargottama",
            "resolved_tendency",
        ],
        notes=["Condition facts are grouped but not numerically weighted."],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-DASHA-ASPECT-CONTEXT-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        verse_reference="2.13",
        citation_precision=CitationPrecision.VERSE,
        topic="active_dasha_lord_aspect_context",
        statement=(
            "Classical aspect rays cast by a period lord and received at its occupied "
            "sign are attached with their original fractional strengths."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=["aspects_cast", "aspects_received", "conjunctions"],
        notes=["Aspect strengths remain transparent facts, not prediction scores."],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C09-DASHA-ASHTAKAVARGA-CONTEXT-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=9,
        verse_reference="9.1-9.8",
        citation_precision=CitationPrecision.VERSE,
        topic="active_dasha_lord_ashtakavarga_context",
        statement=(
            "The raw planetary and Sarvashtakavarga bindus of the period lord's "
            "occupied sign are attached without reductions or predictive thresholds."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "bhinnashtakavarga_bindus_in_occupied_sign",
            "sarvashtakavarga_bindus_in_occupied_sign",
        ],
        notes=["Rahu and Ketu have no planetary Bhinnashtakavarga in this profile."],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C10-DASHA-CAREER-CONTEXT-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=10,
        verse_reference="10.1-10.4",
        citation_precision=CitationPrecision.VERSE,
        topic="active_dasha_lord_karmajiiva_context",
        statement=(
            "An active period lord is linked to any existing Lagna, Moon, or Sun "
            "Karmājīva channel in which it is the derived indicator."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=["karmajiiva_channels", "vocation_theme_ids"],
        notes=["A link does not predict a career event or select a profession."],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-DASHA-NODE-COVERAGE-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="vimshottari_node_coverage_boundary",
        statement=(
            "Rahu and Ketu periods retain timing and neutral natal placement, while "
            "Chapter 2 dignity and seven-Graha condition fields remain unavailable."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=["classical_condition_available", "lord", "d1_sign", "d1_house"],
        notes=["No node dignity, beneficence, or predictive rule is invented."],
    ),
)


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Add active-Dasha context after all earlier profile extensions."""

    extended = extend_ashtakavarga_profile(profile)
    endpoints = list(extended.endpoints)
    if DASHA_CONTEXT_ENDPOINT not in endpoints:
        endpoints.append(DASHA_CONTEXT_ENDPOINT)

    return extended.model_copy(
        update={
            "profile_version": "1.5.0",
            "dasha_interpretation_enabled": True,
            "endpoints": endpoints,
            "caveats": [
                "Vimshottari timing is external to the Brihat Jataka source profile.",
                (
                    "The endpoint composes existing condition, aspect, Chapter 9, "
                    "and Chapter 10 facts."
                ),
                "Rahu and Ketu receive neutral placement context only.",
                "No cancellation, strength weighting, or event prediction is applied.",
                "The evaluator does not alter any existing calculation endpoint.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Append Dasha-context registrations after all earlier profile rules."""

    extended = extend_ashtakavarga_rules(registry)
    return RuleRegistryResponse(
        profile_id=extended.profile_id,
        rules=[
            *extended.rules,
            *(rule.model_copy(deep=True) for rule in DASHA_CONTEXT_RULES),
        ],
    )
