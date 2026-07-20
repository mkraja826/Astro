"""Rule registrations and profile extensions for classical condition evaluation."""

from app.engine.classical_reference import PROFILE_ID, SOURCE_ID
from app.schemas.classical import (
    CitationPrecision,
    ClassicalProfileResponse,
    ClassicalRuleReference,
    RuleImplementationStatus,
    RuleRegistryResponse,
)

CONDITIONS_ENDPOINT = "/v1/classical/varahamihira_v1/conditions"

CONDITION_RULES = (
    ClassicalRuleReference(
        rule_id="VM-BJ-C01-OWN-SIGN-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=1,
        citation_precision=CitationPrecision.CHAPTER,
        topic="own_sign_evaluation",
        statement="A Graha occupying a Rashi it owns is marked as occupying its own sign.",
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=["d1_sign", "owned_signs", "own_sign"],
        notes=["The evaluator uses the immutable Chapter 1 lordship table."],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C01-VARGOTTAMA-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=1,
        citation_precision=CitationPrecision.CHAPTER,
        topic="vargottama_evaluation",
        statement=(
            "A Graha is marked Vargottama when its D1 Rashi and D9 Navamsa Rashi "
            "are identical."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=["d1_sign", "d9_sign", "vargottama"],
        notes=["The existing D1 and D9 calculation engine remains unchanged."],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-DIGNITY-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="dignity_evaluation",
        statement=(
            "A Graha is evaluated against its registered exaltation and debilitation "
            "signs and exact deep-dignity degrees."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=[
            "d1_sign",
            "d1_degree_in_sign",
            "in_exaltation_sign",
            "at_deep_exaltation_point",
            "in_debilitation_sign",
            "at_deep_debilitation_point",
        ],
        notes=[
            "Sign-level dignity and the exact deep point are returned as separate fields."
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-MOON-PHASE-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="moon_conditional_tendency",
        statement=(
            "The Moon's conditional tendency is resolved from its angular elongation "
            "from the Sun as waxing, waning, or an exact phase boundary."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="high",
        data_keys=["elongation_degrees", "phase", "resolved_tendency"],
        notes=[
            "Exact new Moon remains conditional; exact full Moon resolves as benefic."
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-MERCURY-ASSOC-EVAL-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="mercury_conditional_tendency",
        statement=(
            "Mercury's conditional tendency is evaluated from same-sign association "
            "with the other six classical Grahas."
        ),
        implementation_status=RuleImplementationStatus.IMPLEMENTED_EVALUATOR,
        confidence="medium",
        data_keys=[
            "associated_grahas",
            "benefic_associations",
            "malefic_associations",
            "conditional_associations",
            "resolved_tendency",
        ],
        notes=[
            "Same-sign association is a versioned API convention for this evaluator.",
            "Mixed, conditional, or unassociated cases are not forced into a judgment.",
            "Rahu and Ketu are excluded from this seven-Graha association pass.",
        ],
    ),
)


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Expose the evaluator without mutating the immutable base profile object."""

    endpoints = list(profile.endpoints)
    if CONDITIONS_ENDPOINT not in endpoints:
        endpoints.append(CONDITIONS_ENDPOINT)

    return profile.model_copy(
        update={
            "profile_version": "1.1.0",
            "dignity_evaluator_enabled": True,
            "endpoints": endpoints,
            "caveats": [
                "The conditions endpoint is deterministic and non-predictive.",
                "It does not alter D1, D9, Panchanga, or Vimshottari calculations.",
                "Mercury association uses an explicit same-sign v1 convention.",
                "Yoga, career, Ashtakavarga, and longevity judgments are not included.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Append evaluator rules to the immutable Chapter 1 and Chapter 2 registry."""

    return RuleRegistryResponse(
        profile_id=registry.profile_id,
        rules=[
            *registry.rules,
            *(rule.model_copy(deep=True) for rule in CONDITION_RULES),
        ],
    )
