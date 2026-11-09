# PR118 nODD pre-analysis clarifications

Date: 2026-11-09. **PROTOTYPE; no detector acceptance.**

These source-review clarifications precede all new native digitization and
scientific response outputs. The active transport protocol/producer at
`5afb019eac6e152608639d02223dda73098a197f` remains frozen. No raw sample,
response coefficient, event selection or statistical gate changes here.

- Native response seed convention: population base `125500+100*index`, with
  collection offsets 0/1, as actually implemented. D has zero pair/noise
  coefficients and no stochastic output dependence. PN is the sole stochastic
  output mode in the raw/D/PN response campaign, and uses that collection seed;
  raw has no response RNG. There are no distinct stochastic D/PN streams or
  paired random variates to claim. The bootstrap pairs the generated event.
  The separate original/native P/PN replay study retains all its independently
  configured streams and actual effective-seed audits. This makes the earlier
  protocol's mode-offset wording explicit without changing a draw or gate.
- Source review found that ODD physical module numbers 1–16 must be mapped
  through the **actual DD4hep readout encoder**, whose four-bit module field
  encodes physical 16 as 0. Preserve every physical/decoded field and reject
  collisions; do not change geometry, IDs or simply relax a range assertion.
- An entirely empty shower population retains all generated events, zero sums,
  empty observed longitudinal axes and undefined ratio/spread diagnostics.
  Absence of a recorded hit axis is not an inventory of constructed channels.
- Read-time native validation binds current configuration JSON and receipt
  identity to the frozen MIP/noise/threshold/range, collection names, population
  order/seed and actual raw input hash, alongside source/binary/output hashes.
  It also rejects outer geometry/population labels that disagree with that
  bound sample, preventing metadata from reversing a geometry comparison or
  promoting test events to calibration events.
- The first nODD launch failed before events because tracker plugin registration
  targets had not been built. Generate their `Components_*` targets, verify that
  all factory binaries remain byte-identical to the native audit, and retain
  registration hashes in `plugin-registration-audit.json`. The failed attempt
  was relocated with byte hashes and its original paths recorded before retry;
  no failed output enters a response denominator. The compact, materials,
  physical parameters and active transport producer remain unchanged.
- Execution-order clarification before any new native response output: once
  both three-population muon groups close, analyze their six held-out populations
  while shower transport continues. A separate immutable muon manifest includes
  both closed receipts and all six unchanged sample records. The explicit
  `--population muons` scope retains every source/RNG/raw/receipt/native-PASS
  check and uses the original **global** population indices 38–43, never a
  renumbered subset. The full default still requires all 48 populations.
  Geometry and 1,000-replicate fits use this closed six-population manifest.
  Reusing their compact result in the final analysis requires its completion
  digest, source/settings/pedestal identity, preserved run snapshot, selected
  input-manifest hash and exact six native row bindings to match the newly
  verified complete run inventory. No event selection, random draw, fit model,
  coefficient, uncertainty method or statistical gate changes.
