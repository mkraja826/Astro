# Candidate Source 2 — Maitreya 8.2

## Status

```text
candidate_only_not_captured_not_approved
```

This directory prepares an independent Source 2 capture for frozen case
`gc_india_nagarjuna_sagar_1998`. It does not add a record to the external-validation
manifest and does not increase any approval count.

Maitreya is a separate open-source Vedic and western astrology program. Version 8.2
is the candidate capture version. Independence, calculation settings, and output must
still be reviewed from retained evidence before approval.

Official project references:

- https://saravali.github.io/
- https://github.com/martin-pe/maitreya8

## Frozen birth input

Enter these values manually. Do not select a nearby city or allow software defaults to
replace them.

| Field | Required value |
|---|---|
| Local date | 26 October 1998 |
| Local time | 10:28:00 |
| Timezone | Asia/Kolkata / UTC+05:30 |
| Daylight saving | Off |
| Latitude | 16.575 N |
| Longitude | 79.312 E |
| Altitude | 120 metres |
| Calendar | Gregorian |

## Target calculation settings

Capture screenshots of the exact Maitreya labels used. Do not infer a setting from the
result alone.

- Vedic/sidereal zodiac
- Lahiri/Chitrapaksha ayanamsha
- true lunar node, if Maitreya exposes a node-mode choice
- geocentric positions
- D1/Rasi chart
- D9/Navamsa chart
- whole-sign sign placement
- ephemeris/calculation mode and correction options, if exposed

If Maitreya cannot reproduce or disclose one of these settings, record that limitation
instead of silently substituting another convention.

## Required evidence files

Use stable numbered filenames.

1. `01-software-version.png` — About/version screen showing Maitreya 8.2.
2. `02-birth-input.png` — exact date, time, timezone, coordinates, and altitude.
3. `03-zodiac-ayanamsha-settings.png` — sidereal and Lahiri settings.
4. `04-node-and-ephemeris-settings.png` — true/mean node and calculation options.
5. `05-planetary-longitudes.png` — degrees for Sun through Saturn, Rahu, and Ketu.
6. `06-ascendant-and-ayanamsha.png` — ascendant longitude and ayanamsha value.
7. `07-d1-rasi.png` — D1 signs for ascendant and all nine points.
8. `08-d9-navamsa.png` — D9 signs for ascendant and all nine points.
9. `raw.json` — transcription made from the retained evidence.
10. `normalized.json` — output from Astro's external normalizer.
11. `comparison-diagnostic.json` — comparison using the documented default tolerances.
12. `comparison-strict.json` — final comparison after every discrepancy is investigated.
13. `comparison-report.md` — human review notes and decision.
14. `approval.json` — created only after a reviewer approves or rejects the source.

Do not crop away software identity, setting labels, units, signs, or degree values. Do
not include unrelated personal information.

## Normalization and comparison

1. Copy `raw.template.json` to `raw.json`.
2. Replace every `null` only with a value visible in retained evidence.
3. Normalize through `POST /v1/classical/varahamihira_v1/validation/normalize/external`.
4. Compare through `POST /v1/classical/varahamihira_v1/validation/compare`.
5. Investigate every mismatch against the frozen input and documented settings.
6. Do not alter Astro calculations merely to force agreement.
7. Commit an approved manifest record only after provenance, settings, evidence digest,
   and discrepancies have been reviewed.

## Approval threshold

A passing Source 2 comparison would complete external validation only for
`gc_india_nagarjuna_sagar_1998`, because approved Jagannatha Hora 8.0 evidence is
already Source 1 for that case. It would not complete the remaining eleven frozen
cases.

Reject or keep the candidate pending when:

- any frozen input differs;
- ayanamsha or node convention cannot be established;
- the source uses values copied from Jagannatha Hora rather than its own calculation;
- required evidence is missing or edited;
- a mismatch remains unexplained;
- the evidence-file digest does not match the reviewed file.
