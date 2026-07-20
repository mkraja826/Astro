"""Deterministic Varahamihira Chapter 9 Ashtakavarga calculations."""

from uuid import uuid4

from app.engine.charts import calculate_chart
from app.engine.classical_reference import (
    PROFILE_ID,
    get_varahamihira_rashis,
)
from app.schemas.charts import ChartRequest, ChartType
from app.schemas.classical_ashtakavarga import (
    AshtakavargaContributorPosition,
    AshtakavargaRequest,
    AshtakavargaResponse,
    AshtakavargaSignSummary,
    BhinnashtakavargaRecord,
    ContributorBinduRow,
    SarvashtakavargaRecord,
)

CLASSICAL_GRAHAS = (
    "sun",
    "moon",
    "mars",
    "mercury",
    "jupiter",
    "venus",
    "saturn",
)
CONTRIBUTORS = (*CLASSICAL_GRAHAS, "lagna")

VERSE_BY_GRAHA = {
    "sun": "9.1",
    "moon": "9.2",
    "mars": "9.3",
    "mercury": "9.4",
    "jupiter": "9.5",
    "venus": "9.6",
    "saturn": "9.7",
}

EXPECTED_TOTALS = {
    "sun": 48,
    "moon": 49,
    "mars": 39,
    "mercury": 54,
    "jupiter": 56,
    "venus": 52,
    "saturn": 39,
}
EXPECTED_SARVASHTAKAVARGA_TOTAL = sum(EXPECTED_TOTALS.values())

FAVORABLE_HOUSES: dict[str, dict[str, tuple[int, ...]]] = {
    "sun": {
        "sun": (1, 2, 4, 7, 8, 9, 10, 11),
        "moon": (3, 6, 10, 11),
        "mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "mercury": (3, 5, 6, 9, 10, 11, 12),
        "jupiter": (5, 6, 9, 11),
        "venus": (6, 7, 12),
        "saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "lagna": (3, 4, 6, 10, 11, 12),
    },
    "moon": {
        "sun": (3, 6, 7, 8, 10, 11),
        "moon": (1, 3, 6, 7, 10, 11),
        "mars": (2, 3, 5, 6, 9, 10, 11),
        "mercury": (1, 3, 4, 5, 7, 8, 10, 11),
        "jupiter": (1, 4, 7, 8, 10, 11, 12),
        "venus": (3, 4, 5, 7, 9, 10, 11),
        "saturn": (3, 5, 6, 11),
        "lagna": (3, 6, 10, 11),
    },
    "mars": {
        "sun": (3, 5, 6, 10, 11),
        "moon": (3, 6, 11),
        "mars": (1, 2, 4, 7, 8, 10, 11),
        "mercury": (3, 5, 6, 11),
        "jupiter": (6, 10, 11, 12),
        "venus": (6, 8, 11, 12),
        "saturn": (1, 4, 7, 8, 9, 10, 11),
        "lagna": (1, 3, 6, 10, 11),
    },
    "mercury": {
        "sun": (5, 6, 9, 11, 12),
        "moon": (2, 4, 6, 8, 10, 11),
        "mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "mercury": (1, 3, 5, 6, 9, 10, 11, 12),
        "jupiter": (6, 8, 11, 12),
        "venus": (1, 2, 3, 4, 5, 8, 9, 11),
        "saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "lagna": (1, 2, 4, 6, 8, 10, 11),
    },
    "jupiter": {
        "sun": (1, 2, 3, 4, 7, 8, 9, 10, 11),
        "moon": (2, 5, 7, 9, 11),
        "mars": (1, 2, 4, 7, 8, 10, 11),
        "mercury": (1, 2, 4, 5, 6, 9, 10, 11),
        "jupiter": (1, 2, 3, 4, 7, 8, 10, 11),
        "venus": (2, 5, 6, 9, 10, 11),
        "saturn": (3, 5, 6, 12),
        "lagna": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "venus": {
        "sun": (8, 11, 12),
        "moon": (1, 2, 3, 4, 5, 8, 9, 11, 12),
        "mars": (3, 5, 6, 9, 11, 12),
        "mercury": (3, 5, 6, 9, 11),
        "jupiter": (5, 8, 9, 10, 11),
        "venus": (1, 2, 3, 4, 5, 8, 9, 10, 11),
        "saturn": (3, 4, 5, 8, 9, 10, 11),
        "lagna": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    "saturn": {
        "sun": (1, 2, 4, 7, 8, 10, 11),
        "moon": (3, 6, 11),
        "mars": (3, 5, 6, 10, 11, 12),
        "mercury": (6, 8, 9, 10, 11, 12),
        "jupiter": (5, 6, 11, 12),
        "venus": (6, 11, 12),
        "saturn": (3, 5, 6, 11),
        "lagna": (1, 3, 4, 6, 10, 11),
    },
}


def favorable_sign_indices(
    source_sign_index: int,
    relative_houses: tuple[int, ...],
) -> tuple[int, ...]:
    """Rotate relative houses from a contributor's natal sign."""

    if not 1 <= source_sign_index <= 12:
        raise ValueError("source_sign_index must be between 1 and 12")
    return tuple(
        ((source_sign_index + relative_house - 2) % 12) + 1
        for relative_house in relative_houses
    )


def validate_ashtakavarga_tables() -> None:
    """Verify contributor coverage and canonical fixed totals."""

    if set(FAVORABLE_HOUSES) != set(CLASSICAL_GRAHAS):
        raise RuntimeError("Ashtakavarga target Graha table is incomplete")

    for graha in CLASSICAL_GRAHAS:
        rows = FAVORABLE_HOUSES[graha]
        if set(rows) != set(CONTRIBUTORS):
            raise RuntimeError(f"Ashtakavarga contributors are incomplete for {graha}")
        calculated_total = sum(len(rows[contributor]) for contributor in CONTRIBUTORS)
        if calculated_total != EXPECTED_TOTALS[graha]:
            raise RuntimeError(
                f"Ashtakavarga fixed total mismatch for {graha}: "
                f"{calculated_total} != {EXPECTED_TOTALS[graha]}"
            )


validate_ashtakavarga_tables()


def calculate_varahamihira_ashtakavarga(
    request: AshtakavargaRequest,
) -> AshtakavargaResponse:
    """Calculate raw Bhinnashtakavarga and Sarvashtakavarga arrays."""

    d1 = calculate_chart(
        ChartRequest(
            birth=request.birth,
            calculation_profile=request.calculation_profile,
        ),
        ChartType.D1_RASI,
    )
    rashis = get_varahamihira_rashis().rashis
    rashi_by_index = {rashi.index: rashi for rashi in rashis}
    canonical_by_english = {
        rashi.english_name.lower(): rashi.canonical_id for rashi in rashis
    }
    points = {
        point.name: point for point in d1.points if point.name in CLASSICAL_GRAHAS
    }

    contributor_sign_indices = {
        graha: points[graha].sign_index for graha in CLASSICAL_GRAHAS
    }
    contributor_sign_indices["lagna"] = d1.ascendant.sign_index
    contributor_longitudes = {
        graha: points[graha].source_longitude for graha in CLASSICAL_GRAHAS
    }
    contributor_longitudes["lagna"] = d1.ascendant.source_longitude

    contributor_positions = [
        AshtakavargaContributorPosition(
            contributor=contributor,
            sign_index=contributor_sign_indices[contributor],
            sign=rashi_by_index[contributor_sign_indices[contributor]].canonical_id,
            source_longitude=contributor_longitudes[contributor],
        )
        for contributor in CONTRIBUTORS
    ]

    bhinnashtakavargas: list[BhinnashtakavargaRecord] = []
    aggregate_by_graha: dict[str, list[int]] = {}
    for graha in CLASSICAL_GRAHAS:
        rule_id = f"VM-BJ-C09-{graha.upper()}-BAV-001"
        aggregate = [0] * 12
        rows: list[ContributorBinduRow] = []

        for contributor in CONTRIBUTORS:
            relative_houses = FAVORABLE_HOUSES[graha][contributor]
            sign_indices = favorable_sign_indices(
                contributor_sign_indices[contributor],
                relative_houses,
            )
            sign_index_set = set(sign_indices)
            vector = [
                1 if sign_index in sign_index_set else 0
                for sign_index in range(1, 13)
            ]
            aggregate = [
                current + contribution
                for current, contribution in zip(
                    aggregate,
                    vector,
                    strict=True,
                )
            ]
            rows.append(
                ContributorBinduRow(
                    contributor=contributor,
                    source_sign_index=contributor_sign_indices[contributor],
                    source_sign=(
                        rashi_by_index[
                            contributor_sign_indices[contributor]
                        ].canonical_id
                    ),
                    favorable_relative_houses=list(relative_houses),
                    bindu_sign_indices=list(sign_indices),
                    bindu_signs=[
                        rashi_by_index[sign_index].canonical_id
                        for sign_index in sign_indices
                    ],
                    bindus_by_sign=vector,
                    total_bindus=sum(vector),
                    rule_ids=[rule_id],
                )
            )

        total = sum(aggregate)
        expected_total = EXPECTED_TOTALS[graha]
        aggregate_by_graha[graha] = aggregate
        bhinnashtakavargas.append(
            BhinnashtakavargaRecord(
                graha=graha,
                verse_reference=VERSE_BY_GRAHA[graha],
                contributor_rows=rows,
                bindus_by_sign=aggregate,
                rekhas_by_sign=[8 - value for value in aggregate],
                total_bindus=total,
                expected_total_bindus=expected_total,
                total_valid=total == expected_total,
                rule_ids=[rule_id],
            )
        )

    sarva = [
        sum(aggregate_by_graha[graha][sign_offset] for graha in CLASSICAL_GRAHAS)
        for sign_offset in range(12)
    ]
    sarva_total = sum(sarva)
    sign_summaries = [
        AshtakavargaSignSummary(
            sign_index=sign_index,
            sign=rashi_by_index[sign_index].canonical_id,
            house_from_lagna=(
                (sign_index - d1.ascendant.sign_index) % 12
            )
            + 1,
            bindus_by_graha={
                graha: aggregate_by_graha[graha][sign_index - 1]
                for graha in CLASSICAL_GRAHAS
            },
            sarvashtakavarga_bindus=sarva[sign_index - 1],
        )
        for sign_index in range(1, 13)
    ]

    return AshtakavargaResponse(
        request_id=f"req_{uuid4().hex}",
        profile_id=PROFILE_ID,
        calculation_profile=request.calculation_profile,
        time=d1.time,
        coordinates=d1.coordinates,
        ayanamsha_degrees=d1.ayanamsha_degrees,
        ascendant_sign_index=d1.ascendant.sign_index,
        ascendant_sign=canonical_by_english[d1.ascendant.sign.lower()],
        contributor_positions=contributor_positions,
        bhinnashtakavargas=bhinnashtakavargas,
        sarvashtakavarga=SarvashtakavargaRecord(
            bindus_by_sign=sarva,
            total_bindus=sarva_total,
            expected_total_bindus=EXPECTED_SARVASHTAKAVARGA_TOTAL,
            total_valid=sarva_total == EXPECTED_SARVASHTAKAVARGA_TOTAL,
            signs=sign_summaries,
            rule_ids=["VM-BJ-C09-SARVA-AGGREGATION-001"],
        ),
        excluded_points=["rahu", "ketu"],
        metadata=d1.metadata,
        caveats=[
            "This endpoint returns raw Chapter 9 bindu arithmetic, not predictions.",
            "Each Bhinnashtakavarga uses seven Grahas plus Lagna as contributors.",
            "Bindu means a favorable point; rekha is returned as eight minus bindus.",
            "Sarvashtakavarga is the sign-wise sum of seven planetary arrays.",
            "No Trikona or Ekadhipatya reduction is applied in this version.",
            "Rahu and Ketu are excluded from the Chapter 9 contributor tables.",
        ],
    )
