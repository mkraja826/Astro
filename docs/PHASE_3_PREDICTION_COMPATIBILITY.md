# Phase 3 prediction compatibility

This development-only integration pins Varahamihira commit
`152baad8710b40e781355cbb8ac3b762a51faa1a` and accepts
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

## Release restriction

This branch depends on an unmerged development engine commit. It must not be deployed
to production. Production remains pinned to the validated v2 engine until Phase 3A–3D
and hosted release gates pass.
