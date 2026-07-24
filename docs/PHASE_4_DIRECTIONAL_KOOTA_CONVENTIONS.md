# Phase 4 directional Koota conventions

Status: calculation facts only; no public route and no relationship interpretation.

## Profile

- compatibility convention: `north_indian_ashtakoota_tables_v2`
- directional rule profile: `saravali_maitreya_directional_tables_v1`
- calculation profile: `south_indian_drik_lahiri_jpl_de440s_v1`
- bride/groom roles are optional at request level, but required for directional points
- absent roles produce explicit abstentions and never zero-point substitutions

## Varna

Rule ID: `ASTRO-CONV-ASHTAKOOTA-VARNA-001`

Moon-sign classes and hierarchy:

1. Brahmin: Cancer, Scorpio, Pisces
2. Kshatriya: Aries, Leo, Sagittarius
3. Vaishya: Gemini, Libra, Aquarius
4. Shudra: Taurus, Virgo, Capricorn

One point is returned when the groom class is equal to or higher than the bride class; otherwise zero. This is preserved as a historical directional convention, not a social judgement or user-facing personal label.

## Vashya

Rule ID: `ASTRO-CONV-ASHTAKOOTA-VASHYA-001`

Categories:

- Human: Gemini, Virgo, Libra, Aquarius, Sagittarius 0°–15°
- Quadruped: Aries, Taurus, Sagittarius 15°–30°, Capricorn 0°–15°
- Jalachara: Cancer, Pisces, Capricorn 15°–30°
- Leo
- Scorpio

The bride category selects the matrix row and the groom category selects the column. The exact Moon degree is required for Sagittarius and Capricorn; no Nakshatra/Pada midpoint estimate is allowed.

## Gana

Rule ID: `ASTRO-CONV-ASHTAKOOTA-GANA-001`

The 27 Nakshatras are frozen into Deva, Manushya, and Rakshasa groups. The bride group selects the matrix row and the groom group selects the column. No cancellation or remedial override is applied in this calculation layer.

## Sources and boundaries

The sign classes and directional matrices are registered from the Saravali/Maitreya documentation pages for Varna, Vashya, and Gana Koota. The Sagittarius half-sign allocation is included from the Drik Panchang Vashya documentation. These are product convention sources rather than claims of a single universally accepted table.

Excluded from this version:

- pass/fail thresholds
- claims of marriage success, failure, fertility, health, lifespan, wealth, or event timing
- cancellation rules
- name-based matching
- inferred gender or role from account identity
- zero points substituted for missing roles
