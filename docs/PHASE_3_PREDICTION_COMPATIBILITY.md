# Phase 3 prediction compatibility

This development-only integration pins Varahamihira commit
`6fcdb21f4f8027db101881c1f43a5132b3226cc1` and accepts
`horos_brihat_jataka_v3_dev` responses.

## Contract changes

- Every prediction evidence record carries an `independence_key`.
- The weighted-strength payload must include all seven classical Graha D1 sign/house
  facts and controlled scores.
- House-lord, occupant, and Bṛhat Jātaka 2.13 aspect evidence can be evaluated.
- Duplicate evidence derived from one planet-strength fact is consolidated by the
  engine instead of being summed.

## Release restriction

This branch depends on an unmerged development engine commit. It must not be deployed
to production. Production remains pinned to the validated v2 engine until Phase 3A–3D
and hosted release gates pass.
