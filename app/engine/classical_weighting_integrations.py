"""Add controlled strength summaries to career and active-Dasha evidence."""

from uuid import uuid4

from app.engine.classical_career import calculate_varahamihira_career
from app.engine.classical_dasha import calculate_varahamihira_dasha_context
from app.engine.classical_reference import PROFILE_ID
from app.engine.classical_weighting import (
    WEIGHTING_PROFILE_ID,
    calculate_varahamihira_weighted_strength,
    compact_strength_snapshot,
)
from app.schemas.classical_career import ClassicalCareerRequest
from app.schemas.classical_dasha import ClassicalDashaRequest
from app.schemas.classical_weighting import (
    ClassicalWeightedCareerResponse,
    ClassicalWeightedDashaRequest,
    ClassicalWeightedDashaResponse,
    ClassicalWeightedStrengthRequest,
    WeightedCareerCandidateSummary,
    WeightedCareerChannelSummary,
    WeightedDashaLevelSummary,
)


def calculate_varahamihira_weighted_career(
    request: ClassicalWeightedStrengthRequest,
) -> ClassicalWeightedCareerResponse:
    """Return original Karmājīva evidence plus controlled strength summaries."""

    career = calculate_varahamihira_career(
        ClassicalCareerRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        )
    )
    weighted = calculate_varahamihira_weighted_strength(request)
    lookup = {item.graha: item for item in weighted.weighted_grahas}

    channel_strengths = [
        WeightedCareerChannelSummary(
            reference_point=channel.reference_point.value,
            tenth_lord=compact_strength_snapshot(channel.tenth_lord, lookup),
            indicator_graha=compact_strength_snapshot(
                channel.karmājīva_indicator_graha,
                lookup,
            ),
        )
        for channel in career.channels
    ]
    candidate_strengths = [
        WeightedCareerCandidateSummary(
            graha=candidate.graha,
            repetition_count=candidate.repetition_count,
            strength=compact_strength_snapshot(candidate.graha, lookup),
        )
        for candidate in career.candidates
    ]

    return ClassicalWeightedCareerResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        weighting_profile=WEIGHTING_PROFILE_ID,
        career=career,
        weighted_strength=weighted,
        channel_strengths=channel_strengths,
        candidate_strengths=candidate_strengths,
        career_ranking_applied=False,
        prediction_applied=False,
        caveats=[
            "The convention ranks Grahas, not professions or career outcomes.",
            "Lagna, Moon, and Sun Karmājīva channels remain plural and non-exclusive.",
            "A higher indicator score does not guarantee a vocation or event.",
            "No cancellation adjustment or predictive timing rule is applied.",
        ],
    )


def calculate_varahamihira_weighted_dasha(
    request: ClassicalWeightedDashaRequest,
) -> ClassicalWeightedDashaResponse:
    """Return original active-chain evidence plus controlled lord-strength summaries."""

    dasha = calculate_varahamihira_dasha_context(
        ClassicalDashaRequest(
            birth=request.birth,
            as_of=request.as_of,
            calculation_profile=request.calculation_profile,
        )
    )
    weighted = calculate_varahamihira_weighted_strength(
        ClassicalWeightedStrengthRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
            weighting_profile=request.weighting_profile,
        )
    )
    lookup = {item.graha: item for item in weighted.weighted_grahas}
    level_strengths = [
        WeightedDashaLevelSummary(
            level=level.level,
            lord=level.lord,
            strength=compact_strength_snapshot(level.lord, lookup),
        )
        for level in dasha.levels
    ]

    return ClassicalWeightedDashaResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        weighting_profile=WEIGHTING_PROFILE_ID,
        dasha=dasha,
        weighted_strength=weighted,
        level_strengths=level_strengths,
        event_prediction_applied=False,
        cancellations_applied=False,
        caveats=[
            "Vimshottari supplies timing; the convention only summarizes natal Graha factors.",
            "Rahu and Ketu active levels remain unweighted and explicitly unavailable.",
            "A higher natal score does not guarantee a favourable Dasha event.",
            "No cancellation, transit, health, relationship, or longevity prediction is applied.",
        ],
    )
