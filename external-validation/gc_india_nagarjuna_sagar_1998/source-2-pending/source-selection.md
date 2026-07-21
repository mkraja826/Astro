# Source 2 selection and acceptance criteria

## Decision state

- Case ID: `gc_india_nagarjuna_sagar_1998`
- Candidate source: not selected
- Decision: `pending`
- Human approval: not granted

Selection makes a source eligible for evidence capture; it does not approve the source and does not complete external validation.

## Mandatory acceptance criteria

A candidate must satisfy every criterion below before it can enter formal Source 2 comparison:

1. **Independent implementation:** The candidate must use a genuinely independent calculation implementation, not Jagannatha Hora 8.0, a wrapper around Jagannatha Hora, Jyothisyam, or a repackaging of Jyothisyam output.
2. **Exact manual coordinates:** The source must visibly accept or formally record latitude `16.575 N` and longitude `79.312 E`. Selecting a place name without proof of the resolved coordinates is insufficient.
3. **Exact timezone:** The source must visibly accept or formally record `Asia/Kolkata` or `UTC+05:30`, with no daylight-saving adjustment for this event.
4. **Gregorian confirmation:** The source must visibly establish that `1998-10-26 10:28:00` is interpreted using the Gregorian calendar.
5. **Ayanamsha convention:** Lahiri / Chitrapaksha must be visibly selected or formally documented by authoritative source material. Any custom correction must be shown and recorded.
6. **Node convention:** True lunar nodes must be visibly selected or formally documented. An output labelled only as node, Rahu, or Ketu without convention disclosure is insufficient.
7. **Position conventions:** Apparent versus true/geometric and geocentric versus topocentric modes must be documented wherever configurable. The target is apparent geocentric positions. Refraction and other correction settings must also be recorded when exposed.
8. **Ascendant precision:** Ascendant / Lagna longitude must be available with enough precision for the declared comparison tolerance.
9. **Ayanamsha value:** The calculated ayanamsha value must be available, not merely the ayanamsha name.
10. **Nine longitudes:** Longitudes must be available for Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, and Ketu.
11. **D1 signs:** D1 / Rasi signs must be available for Lagna and all nine planetary/node points.
12. **D9 signs:** D9 / Navamsa signs must be available for Lagna and all nine planetary/node points.
13. **Nakshatra and pada:** Nakshatra and pada must be displayed by the source or independently derivable from the source-supplied longitude at adequate precision.
14. **Identity and version:** Software or site identity and version/build must be visibly established. For a hosted service, retain the service identity, retrieval date, and any published calculation/version documentation.
15. **Unchanged evidence:** Original screenshots, exports, reports, or machine-readable output must be retained unchanged and assigned clear evidence filenames.
16. **Independent values:** No output values may be copied from Jyothisyam, an internal baseline, Jagannatha Hora, or Source 1 evidence. Transcription must be performed independently from the Source 2 evidence.

The candidate must also disclose how altitude `120 metres` is entered or treated. If altitude is not supported or does not affect the exposed geocentric calculation, that limitation must be documented rather than assumed.

## Rejection reasons

Use one or more of these exact identifiers when rejecting a candidate:

| Reason | Apply when |
|---|---|
| `input_mismatch` | The date, time, calendar, coordinates, timezone, altitude treatment, or other required input differs from the frozen case. |
| `undisclosed_coordinates` | Exact resolved latitude and longitude are not visible or formally available. |
| `undisclosed_timezone` | The exact timezone or UTC offset cannot be proven. |
| `undisclosed_node_convention` | True versus mean lunar nodes cannot be proven. |
| `ayanamsha_not_proven` | Lahiri / Chitrapaksha selection or its formal implementation cannot be proven. |
| `insufficient_precision` | Ascendant, ayanamsha, longitudes, or derivable classifications lack sufficient precision for meaningful comparison. |
| `not_independent` | The candidate reuses Jagannatha Hora, Jyothisyam, Source 1 results, or another non-independent implementation. |
| `incomplete_output` | One or more required outputs or evidence groups are unavailable. |
| `inaccessible_reproduction` | The source, version, configuration, export, or reproduction path cannot be accessed and retained for review. |

AstroSage remains diagnostic-only and rejected. Its existing capture does not prove exact coordinates, altitude treatment, and node convention well enough for Source 2 acceptance.

## Selection record

Complete only after reviewing all evidence:

| Field | Decision |
|---|---|
| Candidate name | |
| Candidate version/build | |
| Installation/download or service URL | |
| Independent implementation proven by | |
| All acceptance criteria satisfied | |
| Rejection reason(s), if any | |
| Reviewer | |
| Review date | |
| Result (`accepted_for_capture` or `rejected`) | |

`accepted_for_capture` is not human approval and must not be described as approved Source 2.
