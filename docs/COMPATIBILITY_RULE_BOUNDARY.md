# Phase 4 compatibility calculation boundary

## Status

This document freezes the first direction-independent calculation slice for
`compatibility_facts_v1`. It is an API convention boundary, not a claim that a
36-point total predicts relationship success.

## Convention profile

`north_indian_ashtakoota_tables_v1`

The profile exposes four raw component facts:

| Component | Maximum | v1 convention |
| --- | ---: | --- |
| Yoni | 4 | Fixed 27-Nakshatra-to-14-Yoni mapping and symmetric 14x14 points table |
| Graha Maitri | 5 | Moon-sign lord mapping and symmetric seven-lord points table |
| Bhakoot | 7 | Zero for the configured 2/12, 5/9, and 6/8 Moon-sign axes; seven otherwise |
| Nadi | 8 | Zero for the same fixed Nadi group; eight for different groups |

The four released components have a combined maximum of 24. A complete
Ashtakoota total must not be produced from this slice.

## Deliberately disabled components

- **Varna** and **Vashya** use directional tables in common North Indian
  implementations. The anonymous request does not currently assign a
  traditional bride/groom role, so these evaluators remain disabled.
- **Gana** also has directional point variants in common tables and remains
  disabled until the role and convention contract is explicit.
- **Tara** remains disabled because published practices differ on reciprocal
  counting and treatment of Janma Tara. A later version must freeze one method
  and retain comparison fixtures before enabling it.

## Source boundary

The released mappings were independently checked against public North Indian
Ashtakoota implementations and explanatory tables, including PyJHora and
multiple published compatibility references. Those external implementations
are comparison material only. This repository's constants, tests, rule IDs,
and this document are the normative API contract.

Every released fact uses `source_kind="convention"` and one of these IDs:

- `ASTRO-CONV-ASHTAKOOTA-YONI-001`
- `ASTRO-CONV-ASHTAKOOTA-GRAHA-MAITRI-001`
- `ASTRO-CONV-ASHTAKOOTA-BHAKOOT-001`
- `ASTRO-CONV-ASHTAKOOTA-NADI-001`

## Excluded behavior

Version 1 does not apply:

- Nadi, Bhakoot, or other cancellation rules
- Manglik/Kuja aggregation into Ashtakoota points
- a pass/fail threshold
- a probability or percentage interpretation
- medical, fertility, longevity, or guaranteed marriage claims
- advice to accept or reject a relationship

Interpretation belongs in the versioned Varahamihira layer after evidence,
conflict, confidence, and validation gates are satisfied.
