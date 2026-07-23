# Phase 3 prediction compatibility

This development-only integration pins Varahamihira commit
`b70ddc9472c848cb79f703061da5c882d02f4fe5` and accepts
`horos_brihat_jataka_v3_dev` responses.

## Contract changes

- Every prediction evidence record carries an `independence_key`.
- The weighted-strength payload must include all seven classical Graha D1 sign/house
  facts and controlled scores.
- House-lord, occupant, and Bṛhat Jātaka 2.13 aspect evidence can be evaluated.
- Chapter 10 Karmājīva is the only declared domain significator in
  `varahamihira_v1`; unsupported generic kārakas remain disabled.
- Duplicate evidence derived from one planet-strength fact is consolidated by the
  engine instead of being summed.
- D9 confirms a Graha only through Astro's existing, boundary-tested Vargottama
  fact. Confirmation is trace-only and adds no second directional weight.
- D10 is not calculated by Astro. Career output therefore carries an explicit
  zero-weight abstention marker instead of a fabricated D10 interpretation.

## Release restriction

This branch depends on an unmerged development engine commit. It must not be deployed
to production. Production remains pinned to the validated v2 engine until Phase 3A–3D
and hosted release gates pass.
