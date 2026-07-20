# Classical Planetary Relationships v1

## Endpoint

```http
POST /v1/classical/varahamihira_v1/relationships
```

This endpoint evaluates the natural, temporary, and compound relationships
among the seven classical Grahas without assigning numerical strength or
predicting an event.

## Source scope

The profile uses the pinned `varahamihira_v1` source registry:

- Bṛhat Jātaka 2.16-2.17: directional natural relationships
- Bṛhat Jātaka 2.18: temporary relationships and compound classification

The alternate opinion in 2.18 that uses another Graha's exaltation sign is
recorded as a source note but is not enabled in this profile revision.

## Included Grahas

- Sun
- Moon
- Mars
- Mercury
- Jupiter
- Venus
- Saturn

Rahu and Ketu are excluded because the pinned Chapter 2 relationship table is
a seven-Graha table. Their astronomical positions and Vimśottarī periods remain
available through the existing endpoints.

## Natural relationship

Natural relationship is directional. For example, the Moon can treat another
Graha differently from how that Graha treats the Moon. The API therefore
returns every ordered source-to-target pair rather than assuming symmetry.

The endpoint returns 42 directed records:

```text
7 source Grahas × 6 different target Grahas = 42
```

Each record contains:

- source and target Graha
- source and target D1 sign
- natural friend, neutral, or enemy classification
- source rule ID

## Temporary relationship

The target's inclusive whole-sign distance from the source is calculated as:

```text
((target_sign_index - source_sign_index) mod 12) + 1
```

Temporary friends occupy the following relative signs:

```text
2, 3, 4, 10, 11, 12
```

The other separations are temporary enemies:

```text
1, 5, 6, 7, 8, 9
```

These two sets are complementary under reversal, so temporary relationship is
mutual. The response includes 21 unordered pair summaries as an explicit
symmetry check.

## Compound relationship

The v1 compound table is fixed as follows:

| Natural | Temporary | Compound |
|---|---|---|
| friend | friend | great_friend |
| friend | enemy | neutral |
| neutral | friend | friend |
| neutral | enemy | enemy |
| enemy | friend | neutral |
| enemy | enemy | great_enemy |

The compound result remains directional because natural relationship is
directional.

## Response shape

The response contains:

- seven source positions
- 42 directed relationship records
- 21 mutual pair summaries
- rule IDs and reasons
- explicit node exclusion
- `scoring_applied: false`

## Karmājīva integration

Every Chapter 10 Karmājīva channel now includes:

```text
tenth_lord_to_indicator_relationship
```

This is the directional relationship from the channel's tenth lord to the
Navāṁśa-derived Karmājīva indicator. When both are the same Graha, the field is
marked unavailable instead of inventing a self-relationship.

The relationship is evidence only. It does not select a profession or alter the
existing `ranking_applied: false` contract.

## Vimśottarī integration

The classical current-Daśā endpoint now returns:

```text
relationships_between_levels
```

It contains all 12 ordered relationships among Mahādaśā, Antardaśā,
Pratyantardaśā, and Sūkṣma level lords.

A record is marked unavailable when:

- both levels have the same lord, or
- either lord is Rahu or Ketu.

Vimśottarī continues to supply timing only. The relationship layer does not
claim that Bṛhat Jātaka defines the timing system.

## Deliberate exclusions

This version does not apply:

- numeric relationship weights
- cancellation rules
- Shadbala
- final planetary strength
- profession ranking
- event prediction
- health or longevity judgment

Those features require separately versioned rules and validation.
