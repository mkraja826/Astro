"""Immutable Varahamihira/Brihat Jataka source and reference registry."""

from app.schemas.classical import (
    CitationPrecision,
    ClassicalProfileId,
    ClassicalProfileResponse,
    ClassicalRuleReference,
    GrahaElement,
    GrahaGender,
    GrahaReference,
    GrahaReferenceResponse,
    NaturalTendency,
    ProfileStatus,
    RashiElement,
    RashiGender,
    RashiModality,
    RashiReference,
    RashiReferenceResponse,
    RuleImplementationStatus,
    RuleRegistryResponse,
    SourceEdition,
)

PROFILE_ID = ClassicalProfileId.VARAHAMIHIRA_V1
SOURCE_ID = "brihat_jataka_chidambaram_aiyar_1905"

_SOURCE = SourceEdition(
    source_id=SOURCE_ID,
    work_title="Bṛhat Jātaka",
    author="Varāhamihira",
    edition_title="The Brihat Jataka, second enlarged edition",
    translator="N. Chidambaram Aiyar",
    publication_year=1905,
    publisher="Thompson & Co.",
    publication_place="Madras",
    language="English with Sanskrit source material",
    archive_identifier="brihatjataka00varaiala",
    rights_status="public_domain",
    reference_scope=[
        "Chapter 1: Zodiac Signs",
        "Chapter 2: Planets",
    ],
    notes=[
        "This edition is the pinned baseline for varahamihira_v1.",
        "Chapter-level citations are authoritative for this milestone.",
        (
            "Verse-level locators remain pending reconciliation with the user's "
            "preferred edition."
        ),
    ],
)

_RULES = (
    ClassicalRuleReference(
        rule_id="VM-BJ-C01-ZODIAC-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=1,
        citation_precision=CitationPrecision.CHAPTER,
        topic="zodiac_sequence",
        statement="The zodiac contains twelve ordered Rāśis beginning with Meṣa.",
        implementation_status=RuleImplementationStatus.REFERENCE_DATA,
        confidence="high",
        data_keys=["index", "canonical_id", "sanskrit_name", "english_name"],
        notes=[],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C01-LORDS-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=1,
        citation_precision=CitationPrecision.CHAPTER,
        topic="rashi_lordship",
        statement="Each Rāśi is associated with its traditional planetary lord.",
        implementation_status=RuleImplementationStatus.REFERENCE_DATA,
        confidence="high",
        data_keys=["lord"],
        notes=["Rahu and Ketu are not assigned Rāśi lordship in this table."],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C01-CLASS-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=1,
        citation_precision=CitationPrecision.CHAPTER,
        topic="rashi_classification",
        statement=(
            "Rāśis are classified by modality, gender, element, and odd-even parity."
        ),
        implementation_status=RuleImplementationStatus.REFERENCE_DATA,
        confidence="high",
        data_keys=["modality", "gender", "element", "parity"],
        notes=[],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C01-KALAPURUSHA-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=1,
        citation_precision=CitationPrecision.CHAPTER,
        topic="kalapurusha_body",
        statement="The twelve Rāśis correspond in order to parts of Kālapuruṣa.",
        implementation_status=RuleImplementationStatus.REFERENCE_DATA,
        confidence="high",
        data_keys=["kalapurusha_body_part"],
        notes=[
            "Labels follow the pinned English edition's chapter-level terminology."
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-GRAHAS-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="classical_grahas",
        statement="The Chapter 2 reference table covers the seven classical Grahas.",
        implementation_status=RuleImplementationStatus.REFERENCE_DATA,
        confidence="high",
        data_keys=["canonical_id", "sanskrit_name", "english_name"],
        notes=["Rahu and Ketu are explicitly excluded from this seven-Graha table."],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-ATTRIBUTES-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="graha_attributes",
        statement=(
            "Grahas are registered with lordship, gender, element, weekday, and "
            "natural tendency."
        ),
        implementation_status=RuleImplementationStatus.REFERENCE_DATA,
        confidence="high",
        data_keys=[
            "owned_signs",
            "gender",
            "element",
            "weekday",
            "natural_tendency",
        ],
        notes=[
            (
                "Moon and Mercury are represented as conditional rather than "
                "flattened into one class."
            )
        ],
    ),
    ClassicalRuleReference(
        rule_id="VM-BJ-C02-DIGNITY-001",
        profile_id=PROFILE_ID,
        source_id=SOURCE_ID,
        chapter=2,
        citation_precision=CitationPrecision.CHAPTER,
        topic="exaltation_debilitation",
        statement=(
            "Each classical Graha has registered exaltation and debilitation points."
        ),
        implementation_status=RuleImplementationStatus.REFERENCE_DATA,
        confidence="high",
        data_keys=[
            "exaltation_sign",
            "exaltation_degree",
            "debilitation_sign",
            "debilitation_degree",
        ],
        notes=[
            "Evaluation against birth charts is intentionally deferred to the next milestone."
        ],
    ),
)

_RASHI_DATA = (
    (
        1,
        "aries",
        "Meṣa",
        "Aries",
        "mars",
        "movable",
        "masculine",
        "fire",
        "odd",
        "head",
    ),
    (
        2,
        "taurus",
        "Vṛṣabha",
        "Taurus",
        "venus",
        "fixed",
        "feminine",
        "earth",
        "even",
        "face",
    ),
    (
        3,
        "gemini",
        "Mithuna",
        "Gemini",
        "mercury",
        "dual",
        "masculine",
        "air",
        "odd",
        "chest",
    ),
    (
        4,
        "cancer",
        "Karka",
        "Cancer",
        "moon",
        "movable",
        "feminine",
        "water",
        "even",
        "heart",
    ),
    (
        5,
        "leo",
        "Siṃha",
        "Leo",
        "sun",
        "fixed",
        "masculine",
        "fire",
        "odd",
        "belly",
    ),
    (
        6,
        "virgo",
        "Kanyā",
        "Virgo",
        "mercury",
        "dual",
        "feminine",
        "earth",
        "even",
        "waist",
    ),
    (
        7,
        "libra",
        "Tulā",
        "Libra",
        "venus",
        "movable",
        "masculine",
        "air",
        "odd",
        "lower_belly",
    ),
    (
        8,
        "scorpio",
        "Vṛścika",
        "Scorpio",
        "mars",
        "fixed",
        "feminine",
        "water",
        "even",
        "sexual_organs",
    ),
    (
        9,
        "sagittarius",
        "Dhanuṣ",
        "Sagittarius",
        "jupiter",
        "dual",
        "masculine",
        "fire",
        "odd",
        "thighs",
    ),
    (
        10,
        "capricorn",
        "Makara",
        "Capricorn",
        "saturn",
        "movable",
        "feminine",
        "earth",
        "even",
        "knees",
    ),
    (
        11,
        "aquarius",
        "Kumbha",
        "Aquarius",
        "saturn",
        "fixed",
        "masculine",
        "air",
        "odd",
        "buttocks",
    ),
    (
        12,
        "pisces",
        "Mīna",
        "Pisces",
        "jupiter",
        "dual",
        "feminine",
        "water",
        "even",
        "feet",
    ),
)

_GRAHA_DATA = (
    (
        1,
        "sun",
        "Sūrya",
        "Sun",
        ["leo"],
        "masculine",
        "fire",
        "malefic",
        None,
        "sunday",
        "aries",
        10.0,
        "libra",
        10.0,
    ),
    (
        2,
        "moon",
        "Candra",
        "Moon",
        ["cancer"],
        "feminine",
        "water",
        "conditional",
        "Waxing and waning condition must be evaluated before final tendency.",
        "monday",
        "taurus",
        3.0,
        "scorpio",
        3.0,
    ),
    (
        3,
        "mars",
        "Maṅgala",
        "Mars",
        ["aries", "scorpio"],
        "masculine",
        "fire",
        "malefic",
        None,
        "tuesday",
        "capricorn",
        28.0,
        "cancer",
        28.0,
    ),
    (
        4,
        "mercury",
        "Budha",
        "Mercury",
        ["gemini", "virgo"],
        "neuter",
        "earth",
        "conditional",
        "Association and selected conditions must be evaluated before final tendency.",
        "wednesday",
        "virgo",
        15.0,
        "pisces",
        15.0,
    ),
    (
        5,
        "jupiter",
        "Bṛhaspati",
        "Jupiter",
        ["sagittarius", "pisces"],
        "masculine",
        "ether",
        "benefic",
        None,
        "thursday",
        "cancer",
        5.0,
        "capricorn",
        5.0,
    ),
    (
        6,
        "venus",
        "Śukra",
        "Venus",
        ["taurus", "libra"],
        "feminine",
        "water",
        "benefic",
        None,
        "friday",
        "pisces",
        27.0,
        "virgo",
        27.0,
    ),
    (
        7,
        "saturn",
        "Śani",
        "Saturn",
        ["capricorn", "aquarius"],
        "neuter",
        "air",
        "malefic",
        None,
        "saturday",
        "libra",
        20.0,
        "aries",
        20.0,
    ),
)


def get_varahamihira_profile() -> ClassicalProfileResponse:
    """Return metadata for the immutable Varahamihira source profile."""

    return ClassicalProfileResponse(
        profile_id=PROFILE_ID,
        profile_version="1.0.0",
        display_name="Varāhamihira Bṛhat Jātaka Reference Profile v1",
        status=ProfileStatus.REFERENCE_FOUNDATION,
        tradition="Bṛhat Jātaka classical reference layer",
        source=_SOURCE.model_copy(deep=True),
        astronomical_profile_dependency="south_indian_drik_lahiri_v1",
        calculation_engine_impact="none",
        implemented_chapters=[1, 2],
        interpretation_enabled=False,
        dignity_evaluator_enabled=False,
        endpoints=[
            "/v1/classical/varahamihira_v1/profile",
            "/v1/classical/varahamihira_v1/rules",
            "/v1/classical/varahamihira_v1/rashis",
            "/v1/classical/varahamihira_v1/grahas",
        ],
        caveats=[
            "This milestone exposes source-backed reference data only.",
            "It does not alter D1, D9, Panchanga, or Vimshottari calculations.",
            "It does not yet produce dignity, condition, Yoga, or predictive judgments.",
        ],
    )


def get_varahamihira_rules() -> RuleRegistryResponse:
    """Return all rules registered in the initial Chapter 1 and 2 scope."""

    return RuleRegistryResponse(
        profile_id=PROFILE_ID,
        rules=[rule.model_copy(deep=True) for rule in _RULES],
    )


def get_varahamihira_rashis() -> RashiReferenceResponse:
    """Return the immutable Chapter 1 Rashi table."""

    rashis = [
        RashiReference(
            index=index,
            canonical_id=canonical_id,
            sanskrit_name=sanskrit_name,
            english_name=english_name,
            lord=lord,
            modality=RashiModality(modality),
            gender=RashiGender(gender),
            element=RashiElement(element),
            parity=parity,
            kalapurusha_body_part=body_part,
            rule_ids=[
                "VM-BJ-C01-ZODIAC-001",
                "VM-BJ-C01-LORDS-001",
                "VM-BJ-C01-CLASS-001",
                "VM-BJ-C01-KALAPURUSHA-001",
            ],
        )
        for (
            index,
            canonical_id,
            sanskrit_name,
            english_name,
            lord,
            modality,
            gender,
            element,
            parity,
            body_part,
        ) in _RASHI_DATA
    ]
    return RashiReferenceResponse(
        profile_id=PROFILE_ID,
        chapter=1,
        source_id=SOURCE_ID,
        rashis=rashis,
    )


def get_varahamihira_grahas() -> GrahaReferenceResponse:
    """Return the immutable Chapter 2 seven-Graha table."""

    grahas = [
        GrahaReference(
            index=index,
            canonical_id=canonical_id,
            sanskrit_name=sanskrit_name,
            english_name=english_name,
            owned_signs=owned_signs,
            gender=GrahaGender(gender),
            element=GrahaElement(element),
            natural_tendency=NaturalTendency(tendency),
            tendency_note=tendency_note,
            weekday=weekday,
            exaltation_sign=exaltation_sign,
            exaltation_degree=exaltation_degree,
            debilitation_sign=debilitation_sign,
            debilitation_degree=debilitation_degree,
            rule_ids=[
                "VM-BJ-C02-GRAHAS-001",
                "VM-BJ-C02-ATTRIBUTES-001",
                "VM-BJ-C02-DIGNITY-001",
            ],
        )
        for (
            index,
            canonical_id,
            sanskrit_name,
            english_name,
            owned_signs,
            gender,
            element,
            tendency,
            tendency_note,
            weekday,
            exaltation_sign,
            exaltation_degree,
            debilitation_sign,
            debilitation_degree,
        ) in _GRAHA_DATA
    ]
    return GrahaReferenceResponse(
        profile_id=PROFILE_ID,
        chapter=2,
        source_id=SOURCE_ID,
        included_grahas=len(grahas),
        excluded_points=["rahu", "ketu"],
        exclusion_note=(
            "Rahu and Ketu remain available in astronomical chart endpoints but are not "
            "part of this Chapter 2 seven-Graha reference table."
        ),
        grahas=grahas,
    )
