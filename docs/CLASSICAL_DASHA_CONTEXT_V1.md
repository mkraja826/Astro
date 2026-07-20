# Classical Daśā Context v1

## Endpoint

```http
POST /v1/classical/varahamihira_v1/dasha/current
```

This endpoint composes the existing active Vimśottarī timing result with the
already versioned `varahamihira_v1` reference and evaluator layers.

## Important source boundary

Vimśottarī supplies the period timing. The API does **not** claim that Bṛhat
Jātaka defines the Vimśottarī timing system used here.

The Varāhamihira profile contributes only these contextual facts:

- Chapter 1 Rāśi ownership and whole-sign house lordship
- Chapter 2 dignity, conditional tendency, conjunction, and aspect facts
- Chapter 9 raw Bhinnāṣṭakavarga and Sarvāṣṭakavarga bindus
- Chapter 10 Karmājīva indicator links

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
  "as_of": {
    "local_datetime": "2026-07-20T12:00:00",
    "timezone": "Asia/Kolkata"
  },
  "calculation_profile": "south_indian_drik_lahiri_v1"
}
```

The same timezone, DST-fold, birth-time, and 120-year-cycle validation used by
`POST /v1/dashas/vimshottari/current` applies here.

## Response structure

The response contains the unchanged current Vimśottarī result under `timing`
and exactly four contextual records:

1. Mahādaśā
2. Antardaśā
3. Pratyantardaśā
4. Sūkṣma Daśā

Each level returns:

- active period boundaries, progress, elapsed time, and remaining time
- lord's D1 longitude, sign, and house
- signs and whole-sign houses owned by the lord
- dignity, Vargottama, retrograde, and resolved-tendency facts when supported
- same-sign co-occupants and classical conjunctions
- aspects cast and aspects received at the occupied sign
- raw planetary bindus in the occupied sign when available
- raw Sarvāṣṭakavarga bindus in the occupied sign
- matching Karmājīva channels and vocation-theme identifiers
- supporting, challenging, and contextual evidence arrays
- source and integration rule IDs

## Rahu and Ketu

Rahu and Ketu are valid Vimśottarī lords, but they are outside the seven-Graha
Chapter 2 condition and Chapter 9 planetary Bhinnāṣṭakavarga tables used by
this profile.

For node periods the API therefore returns:

- timing
- natal D1 longitude, sign, and house
- same-sign co-occupants
- classical aspects received at the occupied sign
- raw Sarvāṣṭakavarga bindus for that sign

It deliberately returns `null` or empty values for unsupported dignity,
ownership, natural-tendency, and planetary Bhinnāṣṭakavarga fields.

## Evidence buckets

`supporting_evidence` currently contains only directly positive registered
conditions such as exaltation-sign occupancy, own-sign occupancy, and
Vargottama.

`challenging_evidence` currently contains directly adverse registered
conditions such as debilitation-sign occupancy.

`contextual_evidence` contains unweighted facts such as house ownership,
retrogression, co-occupants, aspects, bindus, and Karmājīva links.

These buckets are not scores. No evidence count is treated as strength.

## Explicit non-features

This version does not apply:

- guaranteed event prediction
- profession selection
- natural or temporary friendship scoring
- cancellation rules
- strength weighting
- Aṣṭakavarga reductions or transit thresholds
- health, relationship, financial, or longevity outcomes

The response flags remain:

```json
{
  "interpretation_mode": "evidence_only",
  "prediction_applied": false,
  "cancellations_applied": false,
  "strength_weighting_applied": false
}
```
