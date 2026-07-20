"""Schemas for versioned classical Jyothisha reference data."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ClassicalProfileId(StrEnum):
    """Classical source profiles supported by the public API."""

    VARAHAMIHIRA_V1 = "varahamihira_v1"


class ProfileStatus(StrEnum):
    """Maturity status of a classical source profile."""

    REFERENCE_FOUNDATION = "reference_foundation"
    VALIDATED = "validated"


class CitationPrecision(StrEnum):
    """Precision available for a registered textual citation."""

    CHAPTER = "chapter"
    VERSE = "verse"


class RuleImplementationStatus(StrEnum):
    """Implementation state of a registered classical rule."""

    REFERENCE_DATA = "reference_data"
    PLANNED_EVALUATOR = "planned_evaluator"
    IMPLEMENTED_EVALUATOR = "implemented_evaluator"


class RashiModality(StrEnum):
    """Threefold sign modality."""

    MOVABLE = "movable"
    FIXED = "fixed"
    DUAL = "dual"


class RashiGender(StrEnum):
    """Traditional sign gender classification."""

    MASCULINE = "masculine"
    FEMININE = "feminine"


class RashiElement(StrEnum):
    """Fourfold sign element classification."""

    FIRE = "fire"
    EARTH = "earth"
    AIR = "air"
    WATER = "water"


class GrahaGender(StrEnum):
    """Traditional planetary gender classification."""

    MASCULINE = "masculine"
    FEMININE = "feminine"
    NEUTER = "neuter"


class GrahaElement(StrEnum):
    """Traditional planetary element classification."""

    FIRE = "fire"
    EARTH = "earth"
    AIR = "air"
    WATER = "water"
    ETHER = "ether"


class NaturalTendency(StrEnum):
    """Unconditioned or conditional natural planetary tendency."""

    BENEFIC = "benefic"
    MALEFIC = "malefic"
    CONDITIONAL = "conditional"


class SourceEdition(BaseModel):
    """Pinned source edition used by a classical profile."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    work_title: str
    author: str
    edition_title: str
    translator: str
    publication_year: int = Field(ge=0)
    publisher: str
    publication_place: str
    language: str
    archive_identifier: str
    rights_status: str
    reference_scope: list[str]
    notes: list[str]


class ClassicalProfileResponse(BaseModel):
    """Metadata describing one immutable classical source profile."""

    model_config = ConfigDict(extra="forbid")

    profile_id: ClassicalProfileId
    profile_version: str
    display_name: str
    status: ProfileStatus
    tradition: str
    source: SourceEdition
    astronomical_profile_dependency: str
    calculation_engine_impact: str
    implemented_chapters: list[int]
    interpretation_enabled: bool
    dignity_evaluator_enabled: bool
    aspects_evaluator_enabled: bool = False
    house_influence_evaluator_enabled: bool = False
    career_analysis_enabled: bool = False
    ashtakavarga_enabled: bool = False
    dasha_interpretation_enabled: bool = False
    relationships_enabled: bool = False
    endpoints: list[str]
    caveats: list[str]


class ClassicalRuleReference(BaseModel):
    """Traceable rule or reference-table registration."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str
    profile_id: ClassicalProfileId
    source_id: str
    chapter: int = Field(ge=1)
    verse_reference: str | None = None
    citation_precision: CitationPrecision
    topic: str
    statement: str
    implementation_status: RuleImplementationStatus
    confidence: str
    data_keys: list[str]
    notes: list[str]


class RuleRegistryResponse(BaseModel):
    """Rule registry for one immutable classical profile."""

    profile_id: ClassicalProfileId
    rules: list[ClassicalRuleReference]


class RashiReference(BaseModel):
    """Deterministic Chapter 1 reference data for one zodiac sign."""

    model_config = ConfigDict(extra="forbid")

    index: int = Field(ge=1, le=12)
    canonical_id: str
    sanskrit_name: str
    english_name: str
    lord: str
    modality: RashiModality
    gender: RashiGender
    element: RashiElement
    parity: str
    kalapurusha_body_part: str
    rule_ids: list[str]


class RashiReferenceResponse(BaseModel):
    """Complete Chapter 1 Rashi reference table."""

    profile_id: ClassicalProfileId
    chapter: int
    source_id: str
    rashis: list[RashiReference]


class GrahaReference(BaseModel):
    """Deterministic Chapter 2 reference data for one classical Graha."""

    model_config = ConfigDict(extra="forbid")

    index: int = Field(ge=1, le=7)
    canonical_id: str
    sanskrit_name: str
    english_name: str
    owned_signs: list[str]
    gender: GrahaGender
    element: GrahaElement
    natural_tendency: NaturalTendency
    tendency_note: str | None = None
    weekday: str
    exaltation_sign: str
    exaltation_degree: float = Field(ge=0, lt=30)
    debilitation_sign: str
    debilitation_degree: float = Field(ge=0, lt=30)
    rule_ids: list[str]


class GrahaReferenceResponse(BaseModel):
    """Complete Chapter 2 Graha reference table."""

    profile_id: ClassicalProfileId
    chapter: int
    source_id: str
    included_grahas: int
    excluded_points: list[str]
    exclusion_note: str
    grahas: list[GrahaReference]
