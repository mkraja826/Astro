# Classical Aspects and House Influence v1

## Endpoint

```http
POST /v1/classical/varahamihira_v1/aspects
```

This endpoint applies the `varahamihira_v1` classical source profile to the
existing D1 Lahiri sidereal chart. It does not alter planetary positions, D1,
D9, Panchanga, or Vimshottari calculations.

## Source basis

The profile pins N. Chidambaram Aiyar's 1905 public-domain English edition of
*Brihat Jataka* (`brihatjataka00varaiala`). Aspect strengths are registered at
verse precision against Chapter 2, stanza 13.

## Aspect table

All seven classical Grahas cast these whole-sign aspects, counted inclusively
from the Graha's D1 sign:

| Relative house | General strength |
|---:|---:|
| 3 | 1/4 |
| 4 | 3/4 |
| 5 | 1/2 |
| 7 | Full |
| 8 | 3/4 |
| 9 | 1/2 |
| 10 | 1/4 |

Special full aspects override the general fractional value:

- Mars: 4th and 8th
- Jupiter: 5th and 9th
- Saturn: 3rd and 10th

Therefore, each request returns exactly 49 directed aspect rays: seven aspect
positions for each of the seven classical Grahas.

## Request

```json
{
  "birth": {
    "local_datetime": "1998-10-26T10:28:00",
    "timezone": "Asia/Kolkata",
    "latitude": 16.575,
    "longitude": 79.312,
    "altitude_meters": 120
  },
  "calculation_profile": "south_indian_drik_lahiri_v1"
}
```

## Aspect records

Each aspect ray returns:

- source Graha, sign, and whole-sign house
- relative house counted from the Graha
- target sign and target house
- fractional strength and named strength
- whether a special full-aspect rule applied
- classical Grahas occupying the target sign
- rule IDs and a deterministic reason

The API retains fractional aspects. It does not simplify the model to only the
7th and special full aspects.

## Conjunction convention

A conjunction is registered when two of the seven classical Grahas occupy the
same D1 sign. The exact angular separation is also returned. No orb cutoff or
interpretive judgment is applied.

This same-sign rule is an explicit `varahamihira_v1` API convention and is
registered separately from the verse-2.13 aspect rules.

## House influence records

The endpoint returns exactly twelve whole-sign house records. House 1 begins at
the D1 ascendant sign. Each record contains:

- sign and sign lord
- the lord's D1 sign and house placement
- classical Graha occupants
- conjunction pairs in the house
- every fractional or full aspect received
- the arithmetic sum of received aspect fractions
- the Grahas casting full aspects

`total_aspect_weight` is a transparent arithmetic total. It is not a strength
score, prediction, benefic/malefic judgment, or cancellation result.

## Scope and exclusions

The evaluator covers Sun, Moon, Mars, Mercury, Jupiter, Venus, and Saturn.
Rahu and Ketu remain available in the astronomical chart endpoints but are
excluded from this Chapter 2 seven-Graha aspect pass.

The endpoint does not yet provide:

- aspect-result interpretation
- benefic or malefic house scoring
- aspect cancellations
- orb-based conjunction strength
- Bhava cusp aspects
- Karmājīva career conclusions
- Aṣṭakavarga
- Daśā interpretation
- longevity or birth-risk judgments

## Error behavior

- HTTP `422`: invalid coordinates, timezone, or ambiguous/nonexistent local time
- HTTP `503`: required production ephemeris configuration or data unavailable
