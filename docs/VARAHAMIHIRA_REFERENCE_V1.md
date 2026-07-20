# Varahamihira Reference Profile v1

## Purpose

`varahamihira_v1` is a versioned classical reference layer for the Jyothisyam API.
It does not replace the astronomical calculation profile and does not modify the
working D1 Rasi or D9 Navamsa engines.

The profile provides a traceable foundation for later dignity, condition,
aspect, career, Ashtakavarga, Dasha-interpretation, cancellation, and strength
modules.

## Pinned source edition

The initial baseline is:

- Work: *Brihat Jataka*
- Author: Varahamihira
- Translation: N. Chidambaram Aiyar
- Edition: second enlarged edition
- Publisher: Thompson & Co., Madras
- Publication year: 1905
- Archive identifier: `brihatjataka00varaiala`
- Rights status: public domain

The initial source scope is limited to:

- Chapter 1: Zodiac Signs
- Chapter 2: Planets

This milestone uses chapter-level references. Verse-level locators must be added
only after the pinned edition is reconciled with the user's preferred source
copy. The API must never invent verse numbers.

## Relationship to astronomical calculations

The classical profile depends on:

```text
south_indian_drik_lahiri_v1
```

That dependency means future evaluators may consume the already calculated
Lahiri sidereal positions and charts. It does not mean the historical text is
being presented as the source of modern ephemeris or timezone calculations.

Current calculation-engine impact:

```text
none
```

No files in the D1 or D9 calculation engine are changed by this profile.

## Public endpoints

```http
GET /v1/classical/varahamihira_v1/profile
GET /v1/classical/varahamihira_v1/rules
GET /v1/classical/varahamihira_v1/rashis
GET /v1/classical/varahamihira_v1/grahas
```

### Profile endpoint

Returns the pinned edition, implemented chapters, maturity status, astronomical
profile dependency, endpoint list, and explicit caveats.

### Rule registry endpoint

Each rule registration includes:

- immutable rule ID
- profile ID
- source ID
- chapter
- optional verse locator
- citation precision
- topic
- normalized statement
- implementation status
- confidence
- fields governed by the rule
- ambiguity or scope notes

Initial rule IDs follow this structure:

```text
VM-BJ-C<chapter>-<topic>-<revision>
```

Examples:

```text
VM-BJ-C01-LORDS-001
VM-BJ-C02-DIGNITY-001
```

Rule IDs must remain stable after release. A materially different rule or source
resolution requires a new ID or profile version.

## Chapter 1 Rashi reference data

The Rashi endpoint returns exactly twelve ordered signs with:

- canonical ID
- Sanskrit and English names
- traditional lord
- movable, fixed, or dual modality
- masculine or feminine classification
- fire, earth, air, or water element
- odd or even parity
- Kalapurusha body correspondence
- source rule IDs

The endpoint is reference data only. It does not judge strength or produce a
prediction.

## Chapter 2 Graha reference data

The Graha endpoint returns exactly seven classical Grahas:

- Sun
- Moon
- Mars
- Mercury
- Jupiter
- Venus
- Saturn

For each Graha it returns:

- canonical ID
- Sanskrit and English names
- owned signs
- gender
- element
- natural tendency
- conditional-tendency note where required
- weekday
- exaltation sign and degree
- debilitation sign and degree
- source rule IDs

Rahu and Ketu are deliberately excluded from this Chapter 2 seven-Graha table.
They remain available in astronomical and chart endpoints. This separation
prevents a modern node implementation from being silently inserted into a
source table whose present scope is the seven classical Grahas.

## Conditional classifications

The reference data does not flatten conditional cases:

- Moon is marked `conditional`; waxing and waning state must be evaluated later.
- Mercury is marked `conditional`; association and other selected rules must be
  evaluated later.

The future condition evaluator must resolve these cases with evidence instead
of replacing them with a permanent benefic or malefic label.

## Current non-goals

This milestone does not yet implement:

- planetary dignity evaluation against a birth chart
- Moolatrikona evaluation
- combustion
- planetary war
- aspects
- house influence
- Yoga detection
- career interpretation
- Ashtakavarga
- Dasha interpretation
- cancellation rules
- strength weighting
- longevity or birth-risk interpretation

## Validation guarantees

Automated tests verify:

- one immutable profile
- seven unique source rules
- exactly twelve Rashi in canonical order
- exactly seven classical Grahas
- Rashi lordships match Graha ownership tables
- odd-even parity and gender remain consistent
- modality and element cycles are complete
- exaltation and debilitation points are opposite
- Rahu and Ketu exclusion is explicit
- all four endpoints appear in OpenAPI

## Next milestone

The next evaluator should consume the existing D1 and D9 responses plus these
reference tables to produce deterministic, evidence-bearing conditions:

1. own-sign status
2. exaltation and debilitation status
3. Moolatrikona status after its source table is pinned
4. Vargottama status between D1 and D9
5. conditional Moon and Mercury tendency
6. source rule IDs and human-readable reasons for every result
