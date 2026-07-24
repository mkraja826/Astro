"""Orchestrate Astro compatibility facts through Varahamihira interpretation."""

from varahamihira_engine import (
    compatibility_request_from_astro_facts,
    interpret_compatibility,
)

from app.engine.compatibility_facts import calculate_compatibility_facts
from app.schemas.compatibility import DualChartCompatibilityRequest
from app.schemas.compatibility_report import CompatibilityReportResponse


def calculate_compatibility_report(
    request: DualChartCompatibilityRequest,
) -> CompatibilityReportResponse:
    """Return raw calculation facts plus their strict versioned interpretation."""

    facts = calculate_compatibility_facts(request)
    interpretation_request = compatibility_request_from_astro_facts(
        facts.model_dump(mode="json")
    )
    interpretation = interpret_compatibility(interpretation_request)
    return CompatibilityReportResponse(
        facts=facts,
        interpretation=interpretation.as_dict(),
    )
