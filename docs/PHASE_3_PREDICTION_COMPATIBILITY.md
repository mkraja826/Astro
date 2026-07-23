# Phase 3 prediction compatibility

This development-only integration pins Varahamihira commit
`373a133d0c94928bccb9d865d430a3e4946ef7fe` and accepts
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
- The prediction adapter requires Astro's cancellation policy to remain disabled
  with zero confirmed rules and zero numeric adjustment. Unsupported debilitation
  cancellation candidates receive a non-additive boundary trace.
- Any enabled or applied cancellation fails closed. Cross-text Nīcabhaṅga
  conventions are not imported into `varahamihira_v1`.
- Daily, weekly, and monthly output exposes `timing_status: unavailable` and
  returns no favourable or challenging timing window until a separate validated
  transit channel is present.
- Natal and active-daśā evidence remains visible as capacity and broad activation;
  it is not relabeled as short-term transit timing.
- Non-natal predictions now calculate the frozen Chapter 9 daily, weekly, or
  monthly transit horizon and pass it through the strict engine adapter.
- Timing becomes `evaluated` only after sample-count, seven-Graha, rule-ID,
  polarity, range, and exact-ingress-abstention checks pass.
- Every domain exposes separate natal, daśā, and transit channel scores. Each
  channel is capped before its declared coefficient is applied, preventing
  repeated evidence from making one channel dominate by volume.
- `conflict_status` reports cross-channel disagreement instead of hiding it.
  `confidence_status` remains explicitly `uncalibrated_*`; internal scores are
  not probabilities or claims of measured accuracy.
- Phase 3D automated gates now support immutable blinded cases and prospective
  outcome metrics. Expert review and outcome gates remain pending until real
  records meet the documented minimums.

## Release restriction

This branch depends on an unmerged development engine commit. It must not be deployed
to production. Production remains pinned to the validated v2 engine until Phase 3A–3D
and hosted release gates pass.

The full checksum-verified DE440s workflow must pass on the exact candidate commit;
an earlier successful run is not transferable to a newer engine pin.
