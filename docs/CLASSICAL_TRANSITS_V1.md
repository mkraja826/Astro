# Classical Transit Evaluation v1

## Endpoint

```http
POST /v1/classical/varahamihira_v1/transits/evaluate
```

This endpoint combines the deterministic JPL-backed transit snapshot with each
classical Graha's natal Chapter 9 Bhinnashtakavarga.

## Source rule

The pinned N. Chidambaram Aiyar edition describes the Chapter 9 houses as
benefic or malefic places, then explains that a transiting Graha produces the
balance between the benefic dots and complementary lines in its own
Bhinnashtakavarga. The edition's worked Mars example expresses this difference
in eighths of the Graha's power.

Primary text:

`https://archive.org/stream/brihatjataka00varaiala/brihatjataka00varaiala_djvu.txt`

The implementation registers:

`VM-BJ-C09-TRANSIT-BAV-BALANCE-001`

with chapter-level precision because the transit explanation appears in the
edition notes following the seven verse-level tables rather than as a separate
numbered stanza.

## Arithmetic

For a classical Graha transiting sign `s`:

```text
bindus = graha_bhinnashtakavarga[s]
rekhas = 8 - bindus
net_eighths = bindus - rekhas = 2 * bindus - 8
normalized_balance = net_eighths / 8
```

- positive balance is `supporting`;
- negative balance is `challenging`;
- zero balance is `contextual`.

## Deliberate exclusions

- Rahu and Ketu, because Chapter 9 supplies seven Graha tables;
- Trikona and Ekadhipatya reductions;
- Upachaya, own-sign, friendly-sign, exaltation, inimical-sign, and
  debilitation overrides;
- life-domain mapping;
- daśā combination;
- event claims;
- daily, weekly, monthly, or clock-time window selection.

The disabled overrides require their own source registration and conflict
policy. They are not silently mixed into this evaluator.
