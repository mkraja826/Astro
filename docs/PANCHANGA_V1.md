# Panchanga v1 calculation contract

`POST /v1/panchanga` calculates a daily South Indian Drik Panchanga for a local
calendar date and geographic location.

## Evaluation instant

The five limbs are evaluated at local geometric sunrise calculated with
Skyfield and JPL DE440s. Sunrise and sunset use the Sun's center crossing local
altitude 0°, with no atmospheric refraction and no upper-limb correction.

The event search covers exactly the requested local calendar date. Polar-day or
polar-night dates without a real crossing return HTTP 422 rather than a
fabricated time.

## Definitions

- **Vara:** weekday of the requested local calendar date.
- **Tithi:** elongation of the sidereal Moon from the sidereal Sun, divided into
  30 segments of 12 degrees.
- **Nakshatra:** Chitrapaksha sidereal lunar longitude divided into 27 equal
  segments; Pada divides each Nakshatra into four quarters.
- **Yoga:** sum of sidereal solar and lunar longitudes, normalized to 360 degrees
  and divided into 27 equal segments.
- **Karana:** Tithi elongation divided into 60 half-Tithi segments of 6 degrees,
  mapped to the seven movable and four fixed Karanas.

## Astronomical convention

Sun and Moon are observed geocentrically using Skyfield apparent positions in
the true ecliptic of date. Ayanamsha uses the versioned apparent-Spica
Chitrapaksha convention:

```text
lahiri_chitrapaksha_spica_apparent_v1
```

## Output guarantees

The response includes local and UTC sunrise/sunset, progress through each
angular element, coordinates, ayanamsha, calculation profile, Skyfield version,
JPL model, and ephemeris source metadata.

Missing or invalid DE440s data returns HTTP 503. Application requests never
download ephemeris data.
