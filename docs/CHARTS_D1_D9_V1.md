# D1 Rasi and D9 Navamsa Contract v1

## Endpoints

- `POST /v1/charts/d1`
- `POST /v1/charts/d9`

Both endpoints accept the standard birth input and the immutable
`south_indian_drik_lahiri_v1` calculation profile.

## Calculation basis

- Sidereal zodiac
- Lahiri ayanamsha
- True Rahu and opposite Ketu
- Whole-sign houses counted from the Lagna of the returned chart
- UTC-normalized birth instant with explicit IANA timezone handling

## D1 Rasi

D1 uses each point's Lahiri sidereal longitude directly.

```text
rasi_longitude = source_longitude mod 360
```

## D9 Navamsa

D9 uses the standard Parashari equal Navamsa division. Each zodiac sign is
split into nine parts of 3°20′. The divisional longitude is:

```text
navamsa_longitude = source_longitude × 9 mod 360
```

This produces the traditional movable, fixed, and dual sign starting sequence.
The degree inside the D9 sign is retained, rather than returning only a sign
bucket.

## South Indian layout

The API returns all twelve signs with fixed coordinates in a 4-by-4 South
Indian chart frame:

```text
12  1  2  3
11        4
10        5
 9  8  7  6
```

Each sign cell contains:

- sign index and name
- fixed grid row and column
- house number from that chart's Lagna
- occupant names

## Point data

The Ascendant, seven visible planets, Rahu, and Ketu include:

- source sidereal longitude
- divisional-chart longitude
- sign and degree within sign
- whole-sign house
- retrograde state where applicable

## Guarantees

- Exactly twelve fixed sign cells
- Exactly one Lagna with house number 1
- D1 longitudes match the source sidereal positions
- D9 longitudes follow the ninefold Parashari mapping
- Rahu and Ketu remain exactly opposite
- Every returned point appears in exactly one sign cell
- Production ephemeris licensing and strict-source checks are inherited from
  the planetary-position engine
