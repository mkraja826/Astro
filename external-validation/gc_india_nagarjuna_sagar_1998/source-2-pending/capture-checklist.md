# Source 2 capture checklist

Do not check an item unless it is visibly proven by retained evidence or formally documented by an authoritative source. Record the evidence filename or documentation reference beside every completed item.

## Source identity and independence

- [ ] Source name recorded: ____________________ Evidence: ____________________
- [ ] Source version/build recorded: ____________________ Evidence: ____________________
- [ ] Installation/download source or hosted-service URL recorded: ____________________
- [ ] Retrieval/download date recorded: ____________________
- [ ] Software/site identity visibly established.
- [ ] Independent calculation implementation established.
- [ ] Candidate is not Jagannatha Hora 8.0 and does not wrap or reuse it.
- [ ] Candidate is not the rejected AstroSage capture.
- [ ] No values were copied from Jyothisyam, its internal baseline, or Source 1.

## Exact frozen input

- [ ] Date is exactly `1998-10-26`. Evidence: ____________________
- [ ] Local time is exactly `10:28:00`. Evidence: ____________________
- [ ] Timezone is exactly `Asia/Kolkata` or `UTC+05:30`; DST is off/not applicable. Evidence: ____________________
- [ ] Latitude is entered manually as exactly `16.575 N`. Evidence: ____________________
- [ ] Longitude is entered manually as exactly `79.312 E`. Evidence: ____________________
- [ ] Altitude is entered or formally treated as `120 metres`. Evidence: ____________________
- [ ] Calendar is explicitly Gregorian. Evidence: ____________________
- [ ] Place-name lookup did not silently replace the manual coordinates or timezone.

## Calculation conventions

- [ ] Lahiri / Chitrapaksha ayanamsha is visibly selected or formally documented. Evidence: ____________________
- [ ] Ayanamsha value is displayed or exported. Evidence: ____________________
- [ ] Custom ayanamsha correction is disabled/zero, or its exact value is recorded. Evidence: ____________________
- [ ] Geocentric versus topocentric mode is recorded; geocentric is selected where configurable. Evidence: ____________________
- [ ] Apparent versus true/geometric position mode is recorded; apparent is selected where configurable. Evidence: ____________________
- [ ] Atmospheric refraction is recorded; disabled where configurable. Evidence: ____________________
- [ ] Annual aberration setting is recorded. Evidence: ____________________
- [ ] Gravitational deflection setting is recorded. Evidence: ____________________
- [ ] Nutation setting is recorded. Evidence: ____________________
- [ ] True versus mean nodes is recorded; true nodes are selected. Evidence: ____________________
- [ ] Any non-configurable convention is supported by authoritative documentation.

## Required outputs

- [ ] Ascendant / Lagna longitude captured at displayed precision.
- [ ] Planetary table captured with Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, and Ketu.
- [ ] D1 / Rasi signs captured for Lagna and all nine points.
- [ ] D9 / Navamsa signs captured for Lagna and all nine points.
- [ ] Nakshatra captured for Lagna and all nine points, or independently derived from supplied longitudes.
- [ ] Pada captured for Lagna and all nine points, or independently derived from supplied longitudes.
- [ ] Retrograde markers and displayed rounding precision retained where shown.

## Evidence inventory

- [ ] Evidence filenames are sequential, descriptive, and listed in `capture-sheet.md`.
- [ ] Original screenshots or machine-readable outputs are retained unchanged.
- [ ] Source identity/version evidence filename: ____________________
- [ ] Exact birth-input evidence filename: ____________________
- [ ] Calculation-settings evidence filename: ____________________
- [ ] Ayanamsha/ascendant evidence filename: ____________________
- [ ] Planetary-table evidence filename: ____________________
- [ ] D1 evidence filename: ____________________
- [ ] D9 evidence filename: ____________________
- [ ] Nakshatra/pada evidence filename: ____________________

## Transcription and validation gates

- [ ] Two-pass transcription verification completed independently against the retained evidence.
- [ ] Degree-minute-second conversions were checked without consulting Jyothisyam or Source 1 values.
- [ ] D1, D9, nakshatra, and pada were checked against the candidate's own longitudes.
- [ ] A populated `raw.json` was created only after evidence and transcription gates passed.
- [ ] `raw.json` was normalized through `POST /v1/classical/varahamihira_v1/validation/normalize/external`.
- [ ] Normalization aliases were reviewed.
- [ ] Ignored paths were reviewed.
- [ ] Normalization warnings were reviewed.
- [ ] Diagnostic comparison was run and every mismatch recorded.
- [ ] Strict comparison was run and every mismatch recorded.
- [ ] Comparison results were saved without alteration.
- [ ] Human approval was explicitly granted after evidence and comparison review.

Until the final checkbox is complete, do not claim approved Source 2 or complete external validation.
