# Jagannatha Hora Source 1 evidence transcription

## Evidence status

- Case ID: `gc_india_nagarjuna_sagar_1998`
- Source: Jagannatha Hora
- Version: 8.0
- Evidence decision: `sufficient_for_formal_comparison`
- Reviewer decision: `approved`
- Approval scope: external Source 1 only
- Approved source: Jagannatha Hora 8.0
- Approved by: project owner / `mkraja826`
- Approval date: 2026-07-21
- Diagnostic result: 31/31 matched
- Strict result: 31/31 matched
- D1 result: 10/10 matched
- D9 result: 10/10 matched
- Transcription date: 2026-07-21
- Transcription method: values read visually from the copied screenshots, then compared against the expected readings supplied in the validation request.

**Source 1 is approved.**

**The frozen case is not yet fully externally validated. A second independent approved source is still required.**

## Primary recovered evidence files

| File | Contents | Evidence role |
|---|---|---|
| `01-software-version.png` | About window | Proves Jagannatha Hora, Version 8.0, and P.V.R. Narasimha Rao attribution |
| `02-birth-input-partial-city-label-not-clean.png` | Birth data form | Proves Gregorian calendar, date, time, timezone, longitude, latitude, altitude and LMT unchecked |
| `03-coordinates-timezone-summary.png` | Main screen summary before final settings change | Supporting input summary only; not used as final longitude table |
| `04-ayanamsha-settings.png` | Select Ayanamsa dialog | Proves True Lahiri/Chitrapaksha and no non-zero custom correction |
| `05-final-planet-settings.png` | Final Planet Calculation Options | Proves final geocentric, apparent, no-refraction, aberration, deflection, nutation and true-node settings |
| `01-options-superseded-true-positions-mean-nodes.png` | Earlier Planet Calculation Options | Explicitly excluded from final settings proof |
| `06-planetary-longitudes.png` | Final longitudes/table and dashboard | Primary numerical transcription source |
| `07-d1-bhinnashtakavarga-supporting.png` | D-1 BAV page | Supporting D1 evidence |
| `05-natal-chart-key-info-ayanamsa.png` | Natal chart key info pane | Proves displayed date, time, timezone, whole-second coordinate summary and ayanamsha value |
| `06-rasi-navamsa-chart-support.png` | Rasi and Navamsa charts | Supporting D1 and D9 chart evidence |
| `README-recovered-evidence.md` | Recovered ZIP README | Recovery notes and evidence-file classification |

## Source identity

| Required item | Visibly proven? | Evidence file | Transcribed value |
|---|---:|---|---|
| Software name | Yes | `01-software-version.png` | `JAGANNATHA HORA` |
| Version | Yes | `01-software-version.png` | `Version 8.0` |
| Author | Yes | `01-software-version.png` | `P.V.R. Narasimha Rao` |

## Frozen birth input

| Required item | Visibly proven? | Evidence file(s) | Transcribed value / note |
|---|---:|---|---|
| Date 26 October 1998 | Yes | `02-birth-input-partial-city-label-not-clean.png`, `05-natal-chart-key-info-ayanamsa.png` | Birth form: `October 26, 1998`; natal summary: `October 26, 1998` |
| Time 10:28:00 | Yes | `02-birth-input-partial-city-label-not-clean.png`, `05-natal-chart-key-info-ayanamsa.png` | Birth form: `10 : 28 : 0`; natal summary: `10:28:00` |
| Gregorian calendar | Yes | `02-birth-input-partial-city-label-not-clean.png` | `Calendar used: Gregorian` |
| Timezone UTC+05:30 East of GMT | Yes | `02-birth-input-partial-city-label-not-clean.png`, `05-natal-chart-key-info-ayanamsa.png` | Birth form: `5 : 30 East of GMT`; natal summary: `5:30:00 (East of GMT)` |
| Longitude 79°18′43.2″ E | Yes | `02-birth-input-partial-city-label-not-clean.png` | `79 E 18 43.2` |
| Longitude summary display | Yes | `05-natal-chart-key-info-ayanamsa.png` | `79 E 18' 43"`; natal summary rounds/truncates to whole seconds |
| Latitude 16°34′30″ N | Yes | `02-birth-input-partial-city-label-not-clean.png`, `05-natal-chart-key-info-ayanamsa.png` | `16 N 34 30` |
| Altitude 120 metres | Yes | `02-birth-input-partial-city-label-not-clean.png` | `120 meters above sea-level` |
| LMT unchecked | Yes | `02-birth-input-partial-city-label-not-clean.png` | `Use LMT instead...` checkbox is unchecked |

## Input evidence limitations

- The city-search text field in `02-birth-input-partial-city-label-not-clean.png` contains stale text (`hyde`). This is recorded as a cosmetic capture imperfection, not a calculation-input mismatch, because the manually entered date, time, timezone, longitude, latitude and altitude are visible.
- The natal summary displays the longitude at whole-second precision (`79 E 18' 43"`), while the authoritative manual birth-data form shows `79°18′43.2″ E`.
- The natal summary place label is `Unknown country`.
- The exact manual input form is the authoritative input evidence.

## Ayanamsha

| Required item | Visibly proven? | Evidence file | Transcribed value / note |
|---|---:|---|---|
| True Lahiri/Chitrapaksha | Yes | `04-ayanamsha-settings.png` | `True Lahiri/Chitrapaksha (Spica in the middle of Chitra always)` |
| No custom ayanamsha correction | Yes | `04-ayanamsha-settings.png` | Correction checkbox is unchecked; correction amount fields show `0` deg, `0` min, `0` sec |
| Ayanamsha displayed in chart | Yes | `05-natal-chart-key-info-ayanamsa.png` | `23-49-09.05` |

## Final planet calculation settings

The final settings screenshot is `05-final-planet-settings.png`. It visibly proves:

- `Geocentric positions`
- `Apparent positions`
- `Don't use refraction`
- `Use annual aberration of light`
- `Use gravitational deflection`
- `Use nutation`
- `True nodes`

The older screenshot `01-options-superseded-true-positions-mean-nodes.png` is not used as proof of final node mode or final apparent/geometric mode.

## Ayanamsha and Lagna transcription

| Quantity | Displayed value | Decimal degrees | Expected decimal degrees | Match against expected? |
|---|---:|---:|---:|---:|
| Ayanamsha | `23-49-09.05` | 23.819180555556 | 23.819180555556 | Yes |
| Lagna | `6 Sg 53' 09.41"` | 246.885947222222 | 246.885947222222 | Yes |

## Planetary longitude table transcription

| Point | Displayed value | Nakshatra | Pada | D1/Rasi | D9/Navamsa | Decimal degrees | Expected decimal degrees | Match against expected? |
|---|---:|---|---:|---|---|---:|---:|---:|
| Sun | `8 Li 45' 28.98"` | Swati | 1 | Libra | Sagittarius | 188.758050000000 | 188.758050000000 | Yes |
| Moon | `12 Sg 15' 13.55"` | Moola | 4 | Sagittarius | Cancer | 252.253763888889 | 252.253763888889 | Yes |
| Mars | `17 Le 29' 08.98"` | Purva Phalguni | 2 | Leo | Virgo | 137.485827777778 | 137.485827777778 | Yes |
| Mercury | `27 Li 18' 38.67"` | Vishakha | 3 | Libra | Gemini | 207.310741666667 | 207.310741666667 | Yes |
| Jupiter | `24 Aq 54' 49.52"` | Purva Bhadrapada | 2 | Aquarius | Taurus | 324.913755555556 | 324.913755555556 | Yes |
| Venus | `7 Li 44' 35.60"` | Swati | 1 | Libra | Sagittarius | 187.743222222222 | 187.743222222222 | Yes |
| Saturn | `6 Ar 08' 58.44"` | Ashwini | 2 | Aries | Taurus | 6.149566666667 | 6.149566666667 | Yes |
| Rahu | `5 Le 12' 26.05"` | Magha | 2 | Leo | Taurus | 125.207236111111 | 125.207236111111 | Yes |
| Ketu | `5 Aq 12' 26.05"` | Dhanishtha | 4 | Aquarius | Scorpio | 305.207236111111 | 305.207236111111 | Yes |

## D1 / Rasi signs

| Point | Transcribed D1 sign | Expected D1 sign | Match? |
|---|---|---|---:|
| Lagna | Sagittarius | Sagittarius | Yes |
| Sun | Libra | Libra | Yes |
| Moon | Sagittarius | Sagittarius | Yes |
| Mars | Leo | Leo | Yes |
| Mercury | Libra | Libra | Yes |
| Jupiter | Aquarius | Aquarius | Yes |
| Venus | Libra | Libra | Yes |
| Saturn | Aries | Aries | Yes |
| Rahu | Leo | Leo | Yes |
| Ketu | Aquarius | Aquarius | Yes |

## D9 / Navamsa signs

| Point | Transcribed D9 sign | Expected D9 sign | Match? |
|---|---|---|---:|
| Lagna | Gemini | Gemini | Yes |
| Sun | Sagittarius | Sagittarius | Yes |
| Moon | Cancer | Cancer | Yes |
| Mars | Virgo | Virgo | Yes |
| Mercury | Gemini | Gemini | Yes |
| Jupiter | Taurus | Taurus | Yes |
| Venus | Sagittarius | Sagittarius | Yes |
| Saturn | Taurus | Taurus | Yes |
| Rahu | Taurus | Taurus | Yes |
| Ketu | Scorpio | Scorpio | Yes |

## Nakshatra and Pada

| Point | Transcribed Nakshatra | Pada | Expected Nakshatra | Expected Pada | Match? |
|---|---|---:|---|---:|---:|
| Lagna | Moola | 3 | Moola | 3 | Yes |
| Sun | Swati | 1 | Swati | 1 | Yes |
| Moon | Moola | 4 | Moola | 4 | Yes |
| Mars | Purva Phalguni | 2 | Purva Phalguni | 2 | Yes |
| Mercury | Vishakha | 3 | Vishakha | 3 | Yes |
| Jupiter | Purva Bhadrapada | 2 | Purva Bhadrapada | 2 | Yes |
| Venus | Swati | 1 | Swati | 1 | Yes |
| Saturn | Ashwini | 2 | Ashwini | 2 | Yes |
| Rahu | Magha | 2 | Magha | 2 | Yes |
| Ketu | Dhanishtha | 4 | Dhanishtha | 4 | Yes |

## Transcription gate result

All independently transcribed longitudes, D1 signs, D9 signs, nakshatras and padas match the expected readings supplied in the request. No transcription mismatch stop-condition was triggered.

## Evidence sufficiency conclusion

`sufficient_for_formal_comparison`

The recovered source identity, birth-input, ayanamsha and final planet-settings evidence resolves the earlier formal-evidence caveats. The remaining limitations are cosmetic or display-precision limitations recorded above and do not prevent formal comparison.

## Human reviewer decision

- Status: `approved`
- Approval scope: `external_source_1`
- Approved source: Jagannatha Hora 8.0
- Case ID: `gc_india_nagarjuna_sagar_1998`
- Approved by: project owner / `mkraja826`
- Approved on: 2026-07-21
- Diagnostic comparison: 31/31 matched
- Strict comparison: 31/31 matched
- D1 agreement: 10/10
- D9 agreement: 10/10

Source 1 is approved. This approval applies only to Jagannatha Hora 8.0 as external Source 1. The frozen case is not yet fully externally validated, because one additional independent approved source is still required.
