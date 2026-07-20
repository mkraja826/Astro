# Vimshottari Dasha Contract v1

## Endpoint

`POST /v1/dashas/vimshottari`

## Calculation basis

- Sidereal zodiac
- Lahiri ayanamsha
- Birth Moon evaluated at the normalized UTC instant
- 27 equal Nakshatras of 13°20′ each
- Birth Mahadasha lord selected by the repeating nine-lord Nakshatra sequence
- Birth balance proportional to the untraversed part of the Moon's Nakshatra
- One Dasha year fixed at 365.25 days
- UTC is the canonical period timeline

## Canonical sequence

| Lord | Years |
| --- | ---: |
| Ketu | 7 |
| Venus | 20 |
| Sun | 6 |
| Moon | 10 |
| Mars | 7 |
| Rahu | 18 |
| Jupiter | 16 |
| Saturn | 19 |
| Mercury | 17 |

The complete cycle is 120 years.

## Birth balance

For the Moon's birth Nakshatra:

```text
progress_fraction = degrees_traversed_in_nakshatra / 13°20′
elapsed_years = lord_duration_years × progress_fraction
remaining_years = lord_duration_years − elapsed_years
```

The first returned Mahadasha includes its theoretical start before birth and its
end after birth. The following eight periods are contiguous and complete the
same 120-year cycle.

## Response guarantees

- Exactly nine Mahadasha periods
- Periods are ordered and contiguous
- Exactly one period is active at birth
- Elapsed plus remaining years equals the active lord's full duration
- Period source and Lahiri provenance are returned
- Ambiguous civil times require an explicit `fold`
- Production strict-source and licensing safeguards are inherited from the
  planetary engine

## Scope

This version returns Mahadashas only. Antardasha and deeper subdivisions will be
added under a later versioned contract.
