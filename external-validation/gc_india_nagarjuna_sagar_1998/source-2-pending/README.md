# External validation — Source 2 pending

## Status

`awaiting_independent_source_selection`

No Source 2 has been selected, captured, normalized, compared, or approved. This directory contains instructions and empty templates only. Do not create `raw.json` until a qualifying independent source has been selected and its unchanged evidence has been retained.

The frozen case is not yet fully externally validated. Human approval of a qualifying Source 2 is still required.

## Case

- Case ID: `gc_india_nagarjuna_sagar_1998`
- Gregorian date: `1998-10-26`
- Local civil time: `10:28:00`
- Timezone: `Asia/Kolkata` / `UTC+05:30`
- Latitude: `16.575 N`
- Longitude: `79.312 E`
- Altitude: `120 metres`

These inputs are fixed. A candidate source must show exact manual entry or supply machine-readable input provenance that proves the same values.

## Independence boundary

Approved Source 1 is Jagannatha Hora 8.0. It must not be reused, relabelled, or used as the value provider for Source 2.

AstroSage is retained elsewhere as rejected diagnostic-only evidence. It must not be promoted because the captured coordinates, altitude disclosure, and node convention were insufficient.

A Source 2 candidate must be a genuinely independent calculation implementation. Its values must be transcribed from its own unchanged evidence, never copied from Jyothisyam, its internal JPL baseline, Jagannatha Hora, or the Source 1 files.

## Required conventions and output

- Gregorian calendar
- Exact manual coordinates, altitude, local time, and timezone
- Lahiri / Chitrapaksha ayanamsha
- Geocentric positions where configurable
- Apparent positions where configurable
- Atmospheric refraction disabled where configurable
- True lunar nodes
- Ayanamsha value
- Ascendant / Lagna longitude
- Longitudes for Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, and Ketu
- D1 / Rasi signs
- D9 / Navamsa signs
- Nakshatra and pada, either displayed by the source or independently derived from the source-supplied longitude

Any unavailable or non-configurable convention must be formally documented from authoritative source material. It must not be assumed.

## Files in this pending workspace

- `source-selection.md`: acceptance criteria and rejection rules
- `capture-checklist.md`: evidence and workflow gate checklist
- `capture-sheet.md`: blank transcription worksheet
- `raw-template.json`: unpopulated `generic_json_v1` normalization template

## Workflow

1. Review a candidate against every requirement in `source-selection.md`.
2. Reject the candidate immediately if a listed rejection reason applies.
3. Preserve original screenshots or machine-readable output unchanged.
4. Complete `capture-checklist.md` and `capture-sheet.md` independently from that evidence.
5. Verify the transcription before creating a populated `raw.json` from `raw-template.json`.
6. Submit the populated file to `POST /v1/classical/varahamihira_v1/validation/normalize/external` and retain the response.
7. Review normalization aliases, ignored paths, and warnings.
8. Submit the normalized `snapshot` to `POST /v1/classical/varahamihira_v1/validation/compare` for diagnostic and strict comparisons.
9. Investigate every mismatch and convention difference.
10. Obtain explicit human approval before identifying the candidate as approved Source 2 or claiming complete external validation.

The normalization contract does not contain nakshatra or pada fields. Preserve those fields in screenshots, machine-readable output, and the capture sheet; verify them independently against the candidate source longitudes.

## Repository boundaries

This workspace must not modify calculation-engine code, tests, frozen cases, internal JPL baselines or digests, calculation profiles, Source 1 evidence, or rejected AstroSage evidence. Do not commit, push, or merge as part of capture preparation.
