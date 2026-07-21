# AstroSage PDF extraction report

## Source provenance

- Website/software name: AstroSage / AstroSage.com
- Report title: Kundli PDF; page 3 section titled "Traditional"
- Source version: not disclosed by source PDF
- PDF generation date: 2026-07-21 13:36:31 India Standard Time, from PDF metadata and page footer
- Language: English
- Number of pages: 57

## PDF file

- Path: `C:\Astro\external-validation\gc_india-nagarjuna-sagar-1998\source-1-astrosage\astrosage-full-kundli.pdf`
- Filename: `astrosage-full-kundli.pdf`
- Size: 842,352 bytes
- PDF producer: iTextSharp 5.5.8
- Page count: 57
- Encrypted: no
- Main evidence pages: page 2 for birth data/settings/Panchanga, page 3 for Traditional planetary positions and Vimshottari summary, page 41 for D1/D9 Shodashvarga placements

## Birth input shown in PDF

| Field | Frozen case expectation | PDF value | Page | Status |
|---|---|---|---:|---|
| Name/profile label | not part of frozen case | Karthik Raja | 2-3 | shown |
| Date | 26 October 1998 | 26 : 10 : 1998 / 26.10.1998 | 2-3 | match |
| Time | 10:28:00 AM | 10 : 28 : 0 / 10.28.0 | 2-3 | match |
| Timezone | Asia/Kolkata / UTC+05:30 | Time Zone 5.5 | 2 | match |
| DST | none | War Time Correction 00.00.00 | 2 | match |
| Place | Nagarjuna Sagar / coordinates fixed by case | Nagarjuna Sagar Dam / Nagarjuna | 2-3 | label compatible |
| Latitude | 16.575 North | 16 : 34 : N | 2-3 | mismatch / lower precision |
| Longitude | 79.312 East | 79 : 19 : E | 2-3 | mismatch / lower precision |
| Altitude | 120 metres | not disclosed by source PDF | - | missing |

The PDF birth input does not exactly match the frozen case coordinates. Interpreted literally, `16 : 34 : N` is 16.566666667 N and `79 : 19 : E` is 79.316666667 E. The frozen case is 16.575 N, 79.312 E, altitude 120 m. Per validation instructions, this blocks formal comparison.

## Calculation settings shown in PDF

| Setting | PDF value | Page | Note |
|---|---|---:|---|
| Zodiac | not disclosed by source PDF | - | PDF shows Indian SunSign and Lahiri ayanamsha, but does not explicitly label sidereal/tropical |
| Ayanamsha name | Lahiri | 2-3 | Traditional section |
| Ayanamsha numerical value | 023-50-24 | 2-3 | Converted to 23.840000000 degrees |
| Lahiri or Chitrapaksha variant | Lahiri | 2-3 | No variant details disclosed |
| True or mean Rahu | not disclosed by source PDF | - | Rahu/Ketu are marked retrograde only |
| Geocentric/topocentric mode | not disclosed by source PDF | - | KP page has cusps; Traditional section does not disclose mode |
| Apparent/geometric positions | not disclosed by source PDF | - | Not stated |
| House system | not disclosed by source PDF | - | Bhav/Chalit table appears on page 3, but house system is not named |
| Chart style | not explicitly named by source PDF | - | Charts are shown graphically; no chart-style label extracted |
| Rounding method | not disclosed by source PDF | - | Planet table uses DMS precision |

Note: page 45 contains a separate KP System / Nakshatra Nadi section with Ayan Type `K. P. New` and Ayan `023-45-00`. This extraction uses the page 3 Traditional/Lahiri table for the comparison candidate, not the KP section.

## Planetary positions

| Point | PDF value | Sign | Degree in sign | Full longitude | Retrograde | Page |
|---|---:|---|---:|---:|---|---:|
| Lagna / ASC | Sagittarius 06-52-09 | Sagittarius | 06-52-09 | 246.869166667 | no | 3 |
| Sun | Libra 08-44-39 | Libra | 08-44-39 | 188.744166667 | no | 3 |
| Moon | Sagittarius 12-13-42 | Sagittarius | 12-13-42 | 252.228333333 | no | 3 |
| Mars | Leo 17-28-10 | Leo | 17-28-10 | 137.469444444 | no | 3 |
| Mercury | Libra 27-18-03 | Libra | 27-18-03 | 207.300833333 | no | 3 |
| Jupiter | Aquarius 24-54-54 | Aquarius | 24-54-54 | 324.915000000 | yes | 3 |
| Venus | Libra 07-44-04 | Libra | 07-44-04 | 187.734444444 | no | 3 |
| Saturn | Aries 06-06-21 | Aries | 06-06-21 | 6.105833333 | yes | 3 |
| Rahu | Leo 04-05-30 | Leo | 04-05-30 | 124.091666667 | yes | 3 |
| Ketu | Aquarius 04-05-30 | Aquarius | 04-05-30 | 304.091666667 | yes | 3 |

## D1 placements

Extracted from page 41 Shodashvarga table, row `1 Lagna`, and cross-checked with page 3 signs.

| Point | Sign number | Sign |
|---|---:|---|
| Lagna | 9 | Sagittarius |
| Sun | 7 | Libra |
| Moon | 9 | Sagittarius |
| Mars | 5 | Leo |
| Mercury | 7 | Libra |
| Jupiter | 11 | Aquarius |
| Venus | 7 | Libra |
| Saturn | 1 | Aries |
| Rahu | 5 | Leo |
| Ketu | 11 | Aquarius |

## D9 placements

Extracted from page 41 Shodashvarga table, row `6 Navamsha`.

| Point | Sign number | Sign |
|---|---:|---|
| Lagna | 3 | Gemini |
| Sun | 9 | Sagittarius |
| Moon | 4 | Cancer |
| Mars | 6 | Virgo |
| Mercury | 3 | Gemini |
| Jupiter | 2 | Taurus |
| Venus | 9 | Sagittarius |
| Saturn | 2 | Taurus |
| Rahu | 2 | Taurus |
| Ketu | 8 | Scorpio |

## Nakshatra and Pada

| Point | Nakshatra | Pada | Page |
|---|---|---:|---:|
| Lagna / ASC | Mula | 3 | 3 |
| Sun | Swati | 1 | 3 |
| Moon | Mula | 4 | 3 |
| Mars | Purvaphalgini | 2 | 3 |
| Mercury | Vishakha | 3 | 3 |
| Jupiter | Purvabhadra | 2 | 3 |
| Venus | Swati | 1 | 3 |
| Saturn | Ashvini | 2 | 3 |
| Rahu | Magha | 2 | 3 |
| Ketu | Dhanishta | 4 | 3 |

## Panchanga values

| Field | PDF value | Page |
|---|---|---:|
| Vara / Hindu Week Day | Monday | 2 |
| Tithi | Sashti | 2-3 |
| Paksha | Shukla | 2 |
| Yoga | Sukarma | 2-3 |
| Karana | Kolav | 2-3 |
| Sunrise | 06.08.06 | 2-3 |
| Sunset | 17.45.24 | 2-3 |

## Vimshottari values

| Field | PDF value | Page |
|---|---|---:|
| Birth Mahadasha | Ketu | 2-3 |
| Birth Dasha balance | Ket 0 Y 6 M 29 D | 2-3 |
| Ketu Mahadasha interval shown | 26/10/98 - 25/5/99 | 3 |
| Venus Mahadasha interval shown | 25/5/99 - 25/5/19 | 3 |
| Sun Mahadasha interval shown | 25/5/19 - 25/5/25 | 3 |

## Missing or undisclosed settings

- Exact source software version
- Explicit sidereal/tropical label
- Exact Lahiri/Chitrapaksha implementation variant
- True-node versus mean-node convention
- Geocentric versus topocentric mode
- Apparent versus geometric planetary-position mode
- House system name
- Rounding method
- Altitude
- Exact coordinate seconds matching the frozen case

## Extraction uncertainties

- The source PDF displays coordinates only to whole arcminutes. This may be a display precision issue, a place-lookup issue, or an actual input mismatch; the PDF does not disclose seconds.
- The source PDF has both a Traditional/Lahiri section and a KP section with a different ayanamsha. This report uses the Traditional/Lahiri values because they align with the intended Lahiri comparison.
- The PDF graphical chart was not used for numerical extraction because the exact planetary-position table is available.
- Page 1 and page 57 contain no extractable embedded text.

## Evidence quality verdict

insufficient for formal comparison
