# Classical Strength Framework v1

## Endpoint

```http
POST /v1/classical/varahamihira_v1/strength
```

This endpoint assembles validated `varahamihira_v1` facts into a transparent,
unweighted factor inventory for the seven classical Grahas.

## Returned facts

For every Graha it returns:

- D1 sign, degree, and house
- dignity and deep-dignity flags
- Vargottama and retrograde status
- resolved tendency
- relationship to the occupied-sign lord
- raw Bhinnashtakavarga and Sarvashtakavarga values
- aspects received and same-sign conjunctions
- supporting, challenging, and contextual factors

Every factor has `numeric_weight: null`.

## Sign-lord relationship

When the Graha differs from the occupied-sign lord, the endpoint reuses the
registered natural, temporary, and compound relationship engine. A Graha in a
sign it owns receives no artificial self-relationship.

## Cancellation boundary

The current immutable source profile contains no registered verse-level
formula for debilitation cancellation. Therefore the response declares:

```json
{
  "confirmed_rule_count": 0,
  "cancellation_rules_enabled": false,
  "cancellations_applied": false
}
```

A debilitated Graha is marked `unsupported_by_profile`; no rule from another
text is imported silently. Common cross-text conventions are listed only as
unsupported identifiers so that clients can see the boundary explicitly.

## No combined score

The endpoint declares:

```json
{
  "weights_applied": false,
  "ranking_applied": false,
  "cancellations_applied": false
}
```

It does not calculate Shadbala, select a strongest planet, rank professions, or
produce event predictions.

## Registered rules

- `VM-BJ-C02-STRENGTH-FACTOR-FRAMEWORK-001`
- `VM-BJ-C09-STRENGTH-BINDU-CONTEXT-001`
- `VM-BJ-C02-CANCELLATION-SOURCE-BOUNDARY-001`

These framework registrations organize and protect already registered source
facts; they are not presented as newly discovered source verses.
