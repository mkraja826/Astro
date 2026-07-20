# Controlled Strength Weighting v1

## Status

`transparent_strength_weighting_v1` is an API convention layered over the raw
`varahamihira_v1` strength facts. It is not presented as a quotation from
*Brihat Jataka* and it is not added to the classical verse registry.

## Endpoints

```http
GET  /v1/classical/varahamihira_v1/weighting/profile
POST /v1/classical/varahamihira_v1/strength/weighted
POST /v1/classical/varahamihira_v1/career/weighted
POST /v1/classical/varahamihira_v1/dasha/current/weighted
```

The original `/strength`, `/career`, and `/dasha/current` contracts remain
unchanged.

## Weighted components

Each classical Graha receives six visible components:

1. Dignity: exaltation `+4`, own sign `+3`, ordinary `0`, debilitation `-4`.
2. Exact deep point: deep exaltation `+1`, none `0`, deep debilitation `-1`.
3. Vargottama: `+2` when present.
4. Occupied-sign-lord relationship: great friend `+2`, friend `+1`, neutral
   `0`, enemy `-1`, great enemy `-2`, self `0`.
5. Bhinnashtakavarga: `(bindus - 4) * 0.5`.
6. Sarvashtakavarga: `clamp((bindus - 28) / 7, -2, 2)`.

The response returns the raw input, formula, contribution, classical rule IDs,
and convention profile for every component.

## Score-neutral facts

The following remain visible but do not change the score in v1:

- retrograde state;
- resolved Moon or Mercury tendency;
- received aspect totals;
- conjunctions;
- cancellation candidates.

Aspect and conjunction direction is not weighted until a separately validated
benefic/malefic influence convention exists.

## Ranking

Scores are rounded to six decimal places. Grahas are sorted by descending score
and receive competition ranks. Equal scores share the same rank. Only the seven
classical Grahas are ranked. Rahu and Ketu return an unavailable snapshot in
weighted Dasha integration.

A higher score is not a guaranteed favourable outcome and is not a profession,
event, health, relationship, or longevity prediction.

## Cancellation boundary

No cancellation adjustment is applied. The source-strict cancellation policy
from `/strength` remains authoritative. Debilitation is not cancelled by later
or cross-text conventions unless a separate source profile is created.

## Golden fixtures

`tests/fixtures/controlled_strength_weighting_v1.json` freezes three formula
fixtures:

- `exalted_vargottama_friendly`;
- `debilitated_hostile`;
- `own_sign_neutral_context`.

They verify each component and the final total independently of live ephemeris
output. These are internal formula fixtures, not a claim of completed external
multi-software chart validation.

## External validation status

External reference-chart validation remains incomplete. Before using the score
for commercial interpretation, the project should freeze a larger chart set,
record independent software outputs, document disagreements, and version any
resulting convention changes.
