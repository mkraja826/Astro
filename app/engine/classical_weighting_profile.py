"""Profile extension for the separately versioned controlled weighting convention."""

from app.engine.classical_strength_rules import (
    extend_varahamihira_profile as extend_strength_profile,
)
from app.engine.classical_strength_rules import (
    extend_varahamihira_rules as extend_strength_rules,
)
from app.schemas.classical import ClassicalProfileResponse, RuleRegistryResponse

WEIGHTING_PROFILE_ENDPOINT = "/v1/classical/varahamihira_v1/weighting/profile"
WEIGHTED_STRENGTH_ENDPOINT = "/v1/classical/varahamihira_v1/strength/weighted"
WEIGHTED_CAREER_ENDPOINT = "/v1/classical/varahamihira_v1/career/weighted"
WEIGHTED_DASHA_ENDPOINT = "/v1/classical/varahamihira_v1/dasha/current/weighted"


def extend_varahamihira_profile(
    profile: ClassicalProfileResponse,
) -> ClassicalProfileResponse:
    """Advertise weighting endpoints without treating weights as source rules."""

    extended = extend_strength_profile(profile)
    endpoints = list(extended.endpoints)
    weighting_endpoints = (
        WEIGHTING_PROFILE_ENDPOINT,
        WEIGHTED_STRENGTH_ENDPOINT,
        WEIGHTED_CAREER_ENDPOINT,
        WEIGHTED_DASHA_ENDPOINT,
    )
    for endpoint in weighting_endpoints:
        if endpoint not in endpoints:
            endpoints.append(endpoint)

    return extended.model_copy(
        update={
            "profile_version": "1.8.0",
            "endpoints": endpoints,
            "caveats": [
                "The controlled weighting profile is an API convention, not a textual rule.",
                "Every weighted result embeds its raw unweighted strength evidence.",
                "Career and Dasha weighting use additive endpoints; original contracts remain unchanged.",
                "Rahu and Ketu are excluded from seven-Graha ranking.",
                "Cancellation adjustments and predictions remain disabled.",
                "External multi-software golden-chart validation remains incomplete.",
            ],
        }
    )


def extend_varahamihira_rules(
    registry: RuleRegistryResponse,
) -> RuleRegistryResponse:
    """Preserve the classical rule registry without registering API weights as verses."""

    return extend_strength_rules(registry)
