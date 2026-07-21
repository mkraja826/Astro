# External validation — source 1

## Case

- Case ID: `gc_india_nagarjuna_sagar_1998`
- Local date and time: `1998-10-26 10:28:00`
- Timezone: `Asia/Kolkata` (`UTC+05:30`, no DST)
- Latitude: `16.575` north
- Longitude: `79.312` east
- Altitude: `120` metres

## Independent source

- Software: Jagannatha Hora
- Version: 8.0
- Author: P.V.R. Narasimha Rao
- Official source: `https://vedicastrologer.org/jh/index.htm`
- Source kind: `external_software`

## Required calculation settings

Record the exact labels shown by the software. Do not silently alter settings to force agreement.

- Sidereal zodiac
- Lahiri / Chitrapaksha ayanamsha
- Geocentric planetary positions
- True lunar node
- No daylight-saving adjustment
- D1 / Rasi
- D9 / Navamsa

Also record whether the program exposes apparent/geometric position options, ephemeris details, house settings, rounding precision, or any other convention that could affect comparison.

## Required evidence

Capture original screenshots or exports for:

1. Software version/about screen
2. Birth input and coordinates
3. Calculation settings
4. Planetary longitude table including Ascendant, Rahu and Ketu
5. D1 / Rasi chart
6. D9 / Navamsa chart
7. Ayanamsha value
8. Nakshatra and Pada table, if available

## Review status

`awaiting_capture`

This directory is only an evidence workspace. It is not an approved external snapshot, does not count toward independent validation, and must not alter the frozen case or internal JPL baselines.

## Workflow

1. Fill `capture-sheet.md` directly from the external software.
2. Replace placeholders in `raw.template.json` and save the completed copy as `raw.json`.
3. Submit `raw.json` to `POST /v1/classical/varahamihira_v1/validation/normalize/external`.
4. Save the returned body as `normalized.json`.
5. Submit its `snapshot` to `POST /v1/classical/varahamihira_v1/validation/compare` with the frozen case ID.
6. Save the response as `comparison.json`.
7. Investigate every material mismatch before review or approval.
