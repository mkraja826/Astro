# Varahamihira Classical Conditions v1

## Endpoint

```http
POST /v1/classical/varahamihira_v1/conditions
```

This endpoint evaluates deterministic D1/D9 dignity and planetary-condition
facts using the existing `south_indian_drik_lahiri_v1` astronomical profile and
the pinned `varahamihira_v1` Chapter 1/2 reference registry.

It does not modify the D1 or D9 chart engine and it does not produce predictive
judgments.

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

## Included Grahas

The evaluator covers the seven classical Grahas registered in Chapter 2:

- Sun
- Moon
- Mars
- Mercury
- Jupiter
- Venus
- Saturn

Rahu and Ketu remain available in the astronomical chart endpoints but are
excluded from this seven-Graha condition pass.

## Dignity rules

For each Graha the response reports:

- own-sign occupancy
- exaltation-sign occupancy
- exact deep-exaltation point
- debilitation-sign occupancy
- exact deep-debilitation point
- one primary sign-level dignity state

Sign-level dignity and the exact deep point are intentionally distinct. A Graha
may occupy its exaltation sign without occupying the registered exact degree.

The exact-degree comparison tolerance is `0.0000001` degree.

## Vargottama

A Graha is marked Vargottama when its canonical D1 Rashi and canonical D9
Navamsa Rashi are identical.

D9 is derived from the same source longitude used by D1:

```text
D9 longitude = source sidereal longitude × 9 mod 360
```

## Moon phase convention

The elongation is calculated as:

```text
Moon longitude − Sun longitude mod 360
```

The v1 resolution is:

- exact new-Moon boundary: conditional
- greater than 0° and less than 180°: waxing and benefic
- exact 180° full-Moon boundary: benefic
- greater than 180° and less than 360°: waning and malefic

The exact boundary tolerance is the same `0.0000001` degree used by the dignity
point evaluator.

## Mercury association convention

Mercury is evaluated using an explicit versioned convention:

- association means occupation of the same D1 sign
- only the other six classical Grahas are considered
- Rahu and Ketu are excluded
- benefic-only association resolves as benefic
- malefic-only association resolves as malefic
- mixed, conditional, or unassociated cases remain conditional

This convention is returned in profile caveats and rule notes. It must not be
silently changed inside `varahamihira_v1`; a different convention requires a new
profile or evaluator version.

## Evidence

Every Graha condition includes evidence objects containing:

- rule ID
- tested condition
- whether it applies
- deterministic reason

The evaluator rules are registered by `GET /v1/classical/varahamihira_v1/rules`.

## Non-goals

This endpoint does not yet evaluate:

- classical aspects
- house influence
- Karmājīva career rules
- Aṣṭakavarga
- Yoga cancellation
- strength weighting
- Daśā interpretation
- longevity or birth-risk material
