# Transit Snapshot v1

## Endpoint

```http
POST /v1/transits/snapshot
```

This endpoint is the astronomical foundation for Phase 3B. It calculates the
natal chart instant and one requested transit instant through the existing
Skyfield/JPL DE440s provider and immutable Lahiri calculation profile.

## Returned geometry

For the Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, and Ketu it
returns the complete natal and transit position records plus:

- inclusive whole-sign distance from the body's natal sign;
- whole-sign house from the natal ascendant;
- whole-sign house from the natal Moon.

The inclusive distance formula is:

`((transit_sign - reference_sign) mod 12) + 1`

Therefore the same sign is house 1, the opposite sign is house 7, and wraparound
from Pisces to Aries is handled deterministically.

## Calculation boundary

- Both instants use apparent geocentric Skyfield/JPL DE440s positions.
- Both use `lahiri_chitrapaksha_spica_apparent_v1`.
- Lunar nodes use the existing true-osculating node calculation.
- Coordinates and altitude are inherited from the natal request; the transit
  civil instant carries its own IANA timezone and DST fold.
- The response preserves the full calculation metadata for both instants.

## Interpretation boundary

This endpoint does not classify any transit as favourable or adverse. It does
not apply Aṣṭakavarga thresholds, aspects, orb rules, daśā activation,
domain scoring, event prediction, or daily/weekly/monthly window selection.
Both `interpretation_applied` and `timing_window_applied` are false.

Interpretation requires a separately versioned source registry and validation
suite. Until that exists, the prediction engine must continue to expose
`timing_status: unavailable`.
