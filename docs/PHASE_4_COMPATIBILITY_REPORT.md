# Phase 4 compatibility report orchestration

Endpoint: `POST /v1/classical/varahamihira_v1/compatibility/report`

The report endpoint performs one anonymous dual-chart calculation and returns two strictly separated objects:

- `facts`: the immutable `compatibility_facts_v2` Astro calculation contract
- `interpretation`: the `compatibility_interpretation_v1` Varahamihira report contract

The interpretation consumes the serialized facts through the strict Varahamihira Astro adapter. Unsupported versions, profiles, fields, fingerprints, totals, component states, or Manglik facts fail closed.

## Release boundaries

- no names or birth-place labels are accepted or returned
- no partner data is persisted
- no marriage success/failure prediction
- no pass/fail threshold
- no medical, fertility, lifespan, wealth, divorce, or event-timing certainty
- no remedy recommendation
- the existing `/compatibility/facts` endpoint remains available and unchanged
- production v2 horoscope behavior remains unchanged
