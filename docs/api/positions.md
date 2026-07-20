# POST /v1/positions

Calculates the first deterministic South Indian Jyothisyam chart foundation.

## Example request

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

## Result includes

- UTC conversion and Julian day
- Lahiri ayanamsha
- Sidereal ascendant
- Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, and Ketu
- Sign and degree within sign
- Nakshatra and pada
- Whole-sign house
- Longitude speed and retrograde status
- Ephemeris provenance

The endpoint rejects invalid coordinates, unknown IANA timezones, nonexistent local times,
and ambiguous local times that do not specify `fold`.
