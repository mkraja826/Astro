# Panchanga v1 calculation contract

`POST /v1/panchanga` calculates a daily South Indian Drik Panchanga for a local calendar date and geographic location.

## Evaluation instant

The five limbs are evaluated at local Hindu sunrise, calculated with Swiss Ephemeris using disc center, no atmospheric refraction and geocentric solar latitude handling (`BIT_HINDU_RISING`).

## Definitions

- **Vara:** weekday of the requested local calendar date.
- **Tithi:** elongation of the sidereal Moon from the sidereal Sun, divided into 30 segments of 12 degrees.
- **Nakshatra:** Lahiri sidereal lunar longitude divided into 27 equal segments; Pada divides each Nakshatra into four quarters.
- **Yoga:** sum of Lahiri sidereal solar and lunar longitudes, normalized to 360 degrees and divided into 27 equal segments.
- **Karana:** Tithi elongation divided into 60 half-Tithi segments of 6 degrees, mapped to the seven movable and four fixed Karanas.

## Output guarantees

The response includes local and UTC sunrise/sunset, progress through each angular element, coordinates, ayanamsha, calculation profile, Swiss Ephemeris version and actual ephemeris sources used for the Sun and Moon.

Polar locations or dates without a resolvable sunrise or sunset return HTTP 422 rather than fabricating a result. Production strict-source and licensing rules are inherited from the ephemeris readiness policy.
