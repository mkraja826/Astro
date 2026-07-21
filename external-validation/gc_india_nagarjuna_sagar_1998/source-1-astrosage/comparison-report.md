# AstroSage comparison report

## Validation identity

- Case ID: requested evidence folder `gc_india-nagarjuna-sagar-1998`; Jyothisyam frozen registry/API case ID `gc_india_nagarjuna_sagar_1998`
- Source: AstroSage generated Kundli PDF
- PDF: `C:\Astro\external-validation\gc_india-nagarjuna-sagar-1998\source-1-astrosage\astrosage-full-kundli.pdf`
- Comparison date: 2026-07-21
- API commit: `51c1428f5b066c43efa7ae83fa751dd390dc01e9`
- Calculation profile: `south_indian_drik_lahiri_jpl_de440s_v1`
- Formal source status: `rejected_input_mismatch`

## Source settings

- Traditional section ayanamsha: Lahiri, `023-50-24`
- Zodiac mode: not explicitly disclosed by source PDF
- Node convention: not disclosed by source PDF
- Geocentric/topocentric mode: not disclosed by source PDF
- Apparent/geometric mode: not disclosed by source PDF
- House system: not disclosed by source PDF
- Important note: page 45 contains a separate KP section with Ayan Type `K. P. New` and Ayan `023-45-00`; this is not used for the Traditional/Lahiri extraction.

## Normalization result

The AstroSage raw export was normalized for diagnostic use only.

- Normalization profile: `jyothisyam_external_snapshot_normalizer_v1`
- Normalized field groups: `ayanamsha_degrees`, `ascendant_longitude`, `point_longitudes`, `d1_signs`, `d9_signs`
- Ignored paths: none
- Normalizer warnings: none
- Rahu/Ketu convention warnings: none from the normalizer, because the source used plain `Rahu` and `Ketu` labels rather than `true_node` or `mean_node` aliases

This does not override the formal rejection. The PDF still shows `16 : 34 : N`, `79 : 19 : E`, and no altitude; the frozen case requires `16.575 N`, `79.312 E`, altitude `120 m`.

## Diagnostic-only comparison

Diagnostic comparison was run to document the difference pattern, not to approve the source.

- Endpoint: `POST /v1/classical/varahamihira_v1/validation/compare`
- API case ID used: `gc_india_nagarjuna_sagar_1998`
- Longitude tolerance: `0.05°`
- Ayanamsha tolerance: `0.02°`
- Score tolerance: `0.000001`

## Diagnostic tolerance result

- Fields compared: 31
- Matches: 28
- Mismatches: 3
- Passed: false

Diagnostic mismatches:

- `ayanamsha_degrees`
- `point_longitudes.rahu`
- `point_longitudes.ketu`

## Strict tolerance result

- Fields compared: 31
- Matches: 23
- Mismatches: 8
- Passed: false

Strict mismatches:

- `ascendant_longitude`
- `ayanamsha_degrees`
- `point_longitudes.ketu`
- `point_longitudes.mars`
- `point_longitudes.moon`
- `point_longitudes.rahu`
- `point_longitudes.saturn`
- `point_longitudes.sun`

## Field-by-field differences

| Field | Jyothisyam | AstroSage | Absolute difference | Diagnostic tolerance | Strict tolerance | Result |
|---|---:|---:|---:|---:|---:|---|
| ascendant_longitude | 246.88818395 | 246.869166667 | 0.019017283 | 0.05 | 0.01 | diagnostic match; strict mismatch |
| ayanamsha_degrees | 23.81619793 | 23.84 | 0.02380207 | 0.02 | 0.01 | diagnostic mismatch; strict mismatch |
| d1_signs.ascendant | 9 | 9 | 0 | 0 | 0 | diagnostic match; strict match |
| d1_signs.jupiter | 11 | 11 | 0 | 0 | 0 | diagnostic match; strict match |
| d1_signs.ketu | 11 | 11 | 0 | 0 | 0 | diagnostic match; strict match |
| d1_signs.mars | 5 | 5 | 0 | 0 | 0 | diagnostic match; strict match |
| d1_signs.mercury | 7 | 7 | 0 | 0 | 0 | diagnostic match; strict match |
| d1_signs.moon | 9 | 9 | 0 | 0 | 0 | diagnostic match; strict match |
| d1_signs.rahu | 5 | 5 | 0 | 0 | 0 | diagnostic match; strict match |
| d1_signs.saturn | 1 | 1 | 0 | 0 | 0 | diagnostic match; strict match |
| d1_signs.sun | 7 | 7 | 0 | 0 | 0 | diagnostic match; strict match |
| d1_signs.venus | 7 | 7 | 0 | 0 | 0 | diagnostic match; strict match |
| d9_signs.ascendant | 3 | 3 | 0 | 0 | 0 | diagnostic match; strict match |
| d9_signs.jupiter | 2 | 2 | 0 | 0 | 0 | diagnostic match; strict match |
| d9_signs.ketu | 8 | 8 | 0 | 0 | 0 | diagnostic match; strict match |
| d9_signs.mars | 6 | 6 | 0 | 0 | 0 | diagnostic match; strict match |
| d9_signs.mercury | 3 | 3 | 0 | 0 | 0 | diagnostic match; strict match |
| d9_signs.moon | 4 | 4 | 0 | 0 | 0 | diagnostic match; strict match |
| d9_signs.rahu | 2 | 2 | 0 | 0 | 0 | diagnostic match; strict match |
| d9_signs.saturn | 2 | 2 | 0 | 0 | 0 | diagnostic match; strict match |
| d9_signs.sun | 9 | 9 | 0 | 0 | 0 | diagnostic match; strict match |
| d9_signs.venus | 9 | 9 | 0 | 0 | 0 | diagnostic match; strict match |
| point_longitudes.jupiter | 324.9137552 | 324.915 | 0.0012448 | 0.05 | 0.01 | diagnostic match; strict match |
| point_longitudes.ketu | 305.20717069 | 304.091666667 | 1.115504023 | 0.05 | 0.01 | diagnostic mismatch; strict mismatch |
| point_longitudes.mars | 137.48582616 | 137.469444444 | 0.016381716 | 0.05 | 0.01 | diagnostic match; strict mismatch |
| point_longitudes.mercury | 207.31073938 | 207.300833333 | 0.009906047 | 0.05 | 0.01 | diagnostic match; strict match |
| point_longitudes.moon | 252.2537349 | 252.228333333 | 0.025401567 | 0.05 | 0.01 | diagnostic match; strict mismatch |
| point_longitudes.rahu | 125.20717069 | 124.091666667 | 1.115504023 | 0.05 | 0.01 | diagnostic mismatch; strict mismatch |
| point_longitudes.saturn | 6.14956735 | 6.105833333 | 0.043734017 | 0.05 | 0.01 | diagnostic match; strict mismatch |
| point_longitudes.sun | 188.75805003 | 188.744166667 | 0.013883363 | 0.05 | 0.01 | diagnostic match; strict mismatch |
| point_longitudes.venus | 187.74322029 | 187.734444444 | 0.008775846 | 0.05 | 0.01 | diagnostic match; strict match |

## Planetary difference pattern

Most non-node planetary longitudes are close at the diagnostic tolerance:

- Jupiter: `0.0012448°`
- Venus: `0.008775846°`
- Mercury: `0.009906047°`
- Sun: `0.013883363°`
- Mars: `0.016381716°`
- Moon: `0.025401567°`
- Saturn: `0.043734017°`

This pattern is compatible with small differences in ayanamsha implementation, ephemeris details, apparent/geometric settings, coordinate display precision, or rounding. The PDF does not disclose enough settings to confirm a cause.

D1 placements agree fully: 10 of 10 compared signs match.
D9 placements agree fully: 10 of 10 compared signs match.

## Rahu/Ketu convention discrepancy

Rahu and Ketu are the material outliers:

- Rahu difference: `1.115504023°`
- Ketu difference: `1.115504023°`

Both are offset by the same amount and both fail diagnostic and strict tolerances. This may indicate a true-node versus mean-node convention difference, or another source-specific node convention. The PDF does not disclose the node convention, so this remains an unresolved likely convention discrepancy, not a proven engine error.

## Coordinate-rounding effect on Lagna

The Ascendant/Lagna longitude differs by `0.019017283°`. It passes the diagnostic `0.05°` tolerance but fails the strict `0.01°` tolerance.

Because the PDF displays `16 : 34 : N`, `79 : 19 : E`, and omits altitude, while the frozen case uses `16.575 N`, `79.312 E`, altitude `120 m`, coordinate precision or place lookup may contribute to the Lagna difference. This effect cannot be isolated from this PDF alone.

## Why this source cannot be approved

The source remains rejected for formal validation because:

- The PDF coordinates do not exactly match the frozen case coordinates.
- The PDF does not disclose altitude.
- The PDF does not disclose true-node versus mean-node convention.
- The PDF does not disclose apparent/geometric or geocentric/topocentric mode.
- The source contains a separate KP section with different ayanamsha, which must not be mixed with the Traditional/Lahiri table.
- The diagnostic comparison fails.
- The strict comparison fails.

Input mismatch details:

| Field | Frozen case | AstroSage | Difference | Required status |
|---|---:|---:|---:|---|
| Birth latitude | 16.575 | 16:34 N = 16.566666667 | 0.008333333° | exact input match required |
| Birth longitude | 79.312 | 79:19 E = 79.316666667 | 0.004666667° | exact input match required |
| Birth altitude metres | 120 | not disclosed | not comparable | exact input match required |

## Value of this source as supporting evidence

AstroSage remains useful diagnostic supporting evidence because the D1 and D9 sign placements fully agree, and most non-node longitudes are close under a broad diagnostic tolerance. It is especially useful for investigating:

- Lahiri ayanamsha implementation differences
- Node convention differences
- Rounding/display precision
- Lagna sensitivity to coordinate precision

It is not formal validation evidence for approval.

## Reviewer decision

rejected_input_mismatch

## Important conclusion

AstroSage is retained as diagnostic supporting evidence only.
It is rejected as formal Source 1 because the exact frozen coordinates,
altitude and node convention are not established.

This is source 1 of the required 2 independent sources.
This report alone does not complete external validation.
