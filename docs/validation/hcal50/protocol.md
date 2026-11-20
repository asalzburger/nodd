# First deep-HCAL 50 GeV pion protocol

Frozen2026-11-20 before transport. Governing proposal: DES-045. DRAFT/PROTOTYPE.

- Exactly10000 pi-minus primaries (PDG−211), total energy50 GeV,
  mass0.13957039 GeV and momentum `sqrt(E²−m²)`; origin vertex. Independent
  uniform signed eta∈[−3,3] and phi∈[−pi,pi). Input seed20261120.
- Complete standalone HCAL barrel/endcaps and local carrier material only.
  No tracker, beam pipe, ECAL, FCAL, solenoid or magnetic field.
- FTFP_BERT;0.7 mm range cuts;5 mm maximum charged step in active PSHost.
  Explicitly raw deposits without Birks/optical/electronics response.
  Production12 workers and event seeding; preserve exact runtime/configuration
  hashes and declared transport seed in the receipt.
- Principal `R=sum(saved raw scintillator-hit energy)/Etrue`, with width
  `sample SD(R,ddof=1)/mean(R)`. Include zeros and tails; missing output or
  invalid identifiers fail readback. Fixed energy removes the ECAL study's
  broad incident spectrum, while angular variations and losses remain.
- Fifteen signed-eta bins over−3…3 and fifteen signed folded-phi bins over
  one22.5degree sector. Plot15% sector-width padding on each side, repeating
  existing bins without adding events. Check whether actual endcap packing
  respects this symmetry; if not, label folding as a barrel reference coordinate
  and retain full-phi controls.
-1000 whole-primary bootstrap replicates, seed13001000, jointly across both
  projections. Pointwise95% percentile intervals,30×30 width covariance,
  bin counts/means/SD/quantiles/zeros, explicit undefined cases. No calibration,
  response selection, fit or geometry retuning after observing showers.
- Plot widths, mean response, distributions, longitudinal profile and last-six
  sampling-layer fraction. Escaped kinetic energy, if observed at the world
  boundary, is a separate proxy; it is not complete calorimetric energy closure.
- Depth screen: at least8 nuclear interaction lengths of actual absorber for
  nominal full-depth face-normal rays, separately reporting transition, sector
  seam, edge and forward directions. Predeclared60 layers; do not infer an
  all-angle or high-energy containment guarantee.
- Verify exact10000 unique saved IDs, primary energy/momentum/direction, finite
  deposits, canonical cell IDs, native worker population and input/library hashes.
  Sum independent sensitive-step deposits and native hits, then compare saved
  hits within documented precision. Preserve all adverse findings.

Full ROOT/XML/event ledgers and bulky logs stay ignored and local. Commit plots,
compact aggregate statistics and exact reproduction recipes. Separate-agent
technical assessment does not grant human engineering sign-off.
