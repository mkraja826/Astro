# Jagannatha Hora Source 1 comparison report

## Validation identity

- Case ID: `gc_india_nagarjuna_sagar_1998`
- Source: Jagannatha Hora
- Source version: `8.0`
- Author shown by source: P.V.R. Narasimha Rao
- Comparison date: 2026-07-21
- API commit: `7abb4728b3b66f20c5a7fd1b0e7bd680a6a4be6c`
- API validation profile: `varahamihira_v1`
- Normalization profile: `jyothisyam_external_snapshot_normalizer_v1`
- Evidence decision: `sufficient_for_formal_comparison`
- Reviewer decision: `approved`
- Approval status: Source 1 approved by project owner / `mkraja826` on 2026-07-21
- Approval scope: external Source 1 only
- Approved source: Jagannatha Hora 8.0

**Source 1 is approved.**

**The frozen case is not yet fully externally validated. A second independent approved source is still required.**

This approval applies only to Jagannatha Hora 8.0 as external Source 1 for case `gc_india_nagarjuna_sagar_1998`.

## Evidence files recovered

| File | Evidence role |
|---|---|
| `01-software-version.png` | Jagannatha Hora identity, Version 8.0, P.V.R. Narasimha Rao |
| `02-birth-input-partial-city-label-not-clean.png` | Manual Gregorian birth input, timezone, coordinates, altitude, LMT unchecked |
| `03-coordinates-timezone-summary.png` | Supporting input summary; not the final longitude table |
| `04-ayanamsha-settings.png` | True Lahiri/Chitrapaksha and zero custom correction |
| `05-final-planet-settings.png` | Final calculation settings |
| `01-options-superseded-true-positions-mean-nodes.png` | Retained for audit context only; not used for final settings proof |
| `06-planetary-longitudes.png` | Primary final table for longitudes, D1, D9, nakshatra and pada |
| `07-d1-bhinnashtakavarga-supporting.png` | Supporting D1 evidence |
| `05-natal-chart-key-info-ayanamsa.png` | Natal key info, summary coordinates and ayanamsha value |
| `06-rasi-navamsa-chart-support.png` | Supporting D1/D9 chart evidence |
| `README-recovered-evidence.md` | Recovered evidence notes |

## Final settings proof

`05-final-planet-settings.png` visibly proves:

- `Geocentric positions`
- `Apparent positions`
- `Don't use refraction`
- `Use annual aberration of light`
- `Use gravitational deflection`
- `Use nutation`
- `True nodes`

The earlier `01-options-superseded-true-positions-mean-nodes.png` screenshot shows pre-final settings and is not used as proof of final apparent-position or node mode.

## Remaining evidence limitations

- The city-search text field in the partial birth-input screenshot contains stale text (`hyde`).
- The natal summary displays longitude rounded/truncated to whole seconds: `79 E 18' 43"`.
- The authoritative manual birth-data form shows the exact longitude seconds value: `79 E 18' 43.2"`.
- The natal summary place label is `Unknown country`.
- The exact manual input form is treated as authoritative for date, time, timezone, coordinates and altitude.

These limitations are recorded for audit clarity and do not prevent formal comparison.

## Evidence sufficiency

`sufficient_for_formal_comparison`

The recovered source identity, birth-input, ayanamsha and final calculation-settings evidence resolves the earlier formal-evidence caveats. The project owner has completed human review and approved this source as external Source 1. Source 2 remains required before the frozen case is fully externally validated.

## Transcription verification

The planetary table in `06-planetary-longitudes.png` was independently checked against the expected values supplied for this task.

Result: all longitudes, D1 signs, D9 signs, nakshatras and padas matched the expected transcription. No transcription stop-condition was triggered.

## Fields compared

31 scalar fields were compared:

- `ayanamsha_degrees`
- `ascendant_longitude`
- 9 point longitudes: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
- 10 D1 signs: ascendant, Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
- 10 D9 signs: ascendant, Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu

## Lint and test results

Commands were run from `C:\Astro` with the project virtual environment first on `PATH`.

| Command | Result |
|---|---|
| `python -m ruff check .` | Passed: `All checks passed!` |
| `python -m pytest` | Passed: `119 passed, 1 warning` |
| `python -m pytest tests/test_jpl_golden_baselines.py -v` | Passed: `6 passed, 1 warning` |

The repeated warning was `StarletteDeprecationWarning` from `fastapi.testclient`; no test failed.

## API health verification

- `GET /health`: healthy
- `GET /health/ephemeris`: ready
- Ephemeris provider: `skyfield_jpl`
- Ephemeris model: `de440s`
- Ephemeris file: `C:\Astro\app\data\jpl\de440s.bsp`
- API process: started locally for validation and stopped after endpoint outputs were saved

## Normalization result

- Endpoint: `POST /v1/classical/varahamihira_v1/validation/normalize/external`
- Output file: `normalized.json`
- Profile ID: `varahamihira_v1`
- Normalization profile: `jyothisyam_external_snapshot_normalizer_v1`
- Format: `generic_json_v1`
- Ignored paths: none
- Warnings: none

## Diagnostic comparison

- Endpoint: `POST /v1/classical/varahamihira_v1/validation/compare`
- API case ID: `gc_india_nagarjuna_sagar_1998`
- Longitude tolerance: `0.05°`
- Ayanamsha tolerance: `0.02°`
- Score tolerance: `0.000001`
- Fields compared: 31
- Matches: 31
- Mismatches: 0
- Passed: true

Diagnostic mismatches: none.

## Strict comparison

- Endpoint: `POST /v1/classical/varahamihira_v1/validation/compare`
- API case ID: `gc_india_nagarjuna_sagar_1998`
- Longitude tolerance: `0.01°`
- Ayanamsha tolerance: `0.01°`
- Score tolerance: `0.000001`
- Fields compared: 31
- Matches: 31
- Mismatches: 0
- Passed: true

Strict mismatches: none.

## D1 and D9 agreement

- D1 / Rasi agreement: 10 of 10 compared signs match.
- D9 / Navamsa agreement: 10 of 10 compared signs match.

## Ayanamsha, Rahu and Ketu differences

| Field | Jyothisyam | Jagannatha Hora | Absolute difference | Strict tolerance | Result |
|---|---:|---:|---:|---:|---|
| `ayanamsha_degrees` | 23.81619793 | 23.819180555556 | 0.0029826256 | 0.01 | match |
| `point_longitudes.rahu` | 125.20717069 | 125.207236111111 | 0.0000654211 | 0.01 | match |
| `point_longitudes.ketu` | 305.20717069 | 305.207236111111 | 0.0000654211 | 0.01 | match |

## Largest five differences

| Rank | Field | Jyothisyam | Jagannatha Hora | Absolute difference | Strict tolerance | Strict result |
|---:|---|---:|---:|---:|---:|---|
| 1 | `ayanamsha_degrees` | 23.81619793 | 23.819180555556 | 0.0029826256 | 0.01 | match |
| 2 | `ascendant_longitude` | 246.88818395 | 246.885947222222 | 0.0022367278 | 0.01 | match |
| 3 | `point_longitudes.ketu` | 305.20717069 | 305.207236111111 | 0.0000654211 | 0.01 | match |
| 4 | `point_longitudes.rahu` | 125.20717069 | 125.207236111111 | 0.0000654211 | 0.01 | match |
| 5 | `point_longitudes.moon` | 252.2537349 | 252.253763888889 | 0.0000289889 | 0.01 | match |

## Files created or updated

- `01-software-version.png`
- `02-birth-input-partial-city-label-not-clean.png`
- `03-coordinates-timezone-summary.png`
- `04-ayanamsha-settings.png`
- `05-final-planet-settings.png`
- `01-options-superseded-true-positions-mean-nodes.png`
- `06-planetary-longitudes.png`
- `07-d1-bhinnashtakavarga-supporting.png`
- `05-natal-chart-key-info-ayanamsa.png`
- `06-rasi-navamsa-chart-support.png`
- `README-recovered-evidence.md`
- `evidence-transcription.md`
- `raw.json`
- `normalized.json`
- `comparison-diagnostic.json`
- `comparison-strict.json`
- `comparison-report.md`

## Reviewer decision

`approved`

- Approved source: Jagannatha Hora 8.0
- Case ID: `gc_india_nagarjuna_sagar_1998`
- Approved by: project owner / `mkraja826`
- Approval date: 2026-07-21
- Approval scope: external Source 1 only
- Diagnostic result: 31/31 matched
- Strict result: 31/31 matched
- D1 result: 10/10 matched
- D9 result: 10/10 matched

Source 1 is approved. The frozen case is not yet fully externally validated. A second independent approved source is still required.
