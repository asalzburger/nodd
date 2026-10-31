# STRIXEL-GBTS-PhysVal-01 — protocol assessment

Independent read-only child `/root/strixel_gbts_physval`, explicit profile mandate
fallback. Reviewed `4ea4af17727020bac2ba8f5e2f6172378711c15a`; all eleven pinned
input hashes matched. Additional same-revision inputs: development mandate,
workflow, ADR-003, prior DES042 results, pooled widths, old geometry mapping,
smearing/metrics/material, campaigns/species report and Reconstruction.cpp.
No files changed, simulations executed or further delegation. Exact client
usage unavailable. Separate final evidence review remains required.

## Recommendation and findings

Proceed as a qualified frozen effective-response reconstruction sensitivity,
not physical sensor calibration, design selection or transport-model equivalence.
The 80 cases are 80,000 processed case-events, not one pooled independent sample.

- **High: pairing.** Same seeds or simhit counts are insufficient. Require event
  identities, exact native generated/simulated-particle records and all-hit
  payload equality. End-of-order RootSimHitWriter is adequate if declared as
  persisted float32 equality, including all secondaries, IDs/order/counts,
  column dtypes and maximum float32 ULP. Do not claim native float64 identity.
- **High: realized response.** Fixed sigmas do not ensure fixed measured pixel,
  fine-u or long-strip values. Boundary retries can change subsequent draws.
  Compare measured pixels, space points, ordered seeds and physical measurement
  associations, avoiding index-only alignment after drops. Zero losses do not
  establish zero retries. If changed, describe an end-to-end RNG-mediated effect;
  strict CKF-only causal claims would require independently fixed pixel inputs.
- **Medium: precision.** 1,000/case is screening: zero fake events implies
  one-sided95 upper0.2991%; Wilson95 half-width about1.86 percentage points at90%
  efficiency. Preserve undefined widths below30 entries. Use jointly resampled
  generated-event bootstrap, gain/loss contingency counts and common-success
  controls. No equivalence claim without a margin/power criterion.
- **Medium: response.** Pooled baseline strixel-v sigma is81.12–102.46um barrel
  and125.94–137.08um EC, versus binary144.34um. Linear factors1/2/3/4 preserve
  these layer-dependent fractions of binary width. They are effective frozen
  training widths; old means/RMS/entries must not be relabeled as new coarse
  calibration. Only native v variance scales1/4/9/16.
- **Medium: truth comparison.** Earlier geometric and nominal-binary Gaussian
  truth scans use different response models and truth-assisted fitting. They
  supply qualified context, not a quantitative prediction or monotonicity gate.

## Required checks and observables

Identical geometry/material/3T/native sensor inventory and exact GBTS profile;
all native marginal variances match intended errors;2D pixels/strixels and1D
long strips; no merging; all seven CKF systems; complete Geant4 mapping/event
counts; unchanged FPE policy; SafeFatras identity; electron one-way and muon/pion
two-way policy; strict ambiguity survivors<3 shared measurements before quality.

Keep all-generated efficiency plus >=6 sensor/>=3 pixel-group and nested>=4
conditional denominators. Retain generated→measured→seed→estimated→CKF→ambiguity
and quality counts, candidate multiplicities/rejections/invalid covariance,
primary/secondary/fake/duplicate/wrong-charge separation, inliers/holes/outliers
and runtime. Deterministic primary representative, matching purity/completeness
>=0.5 and minimum7 unique inliers remain frozen. No-output diagnostics are not
per-seed failure counts when seed deduplication is active.

Report z0/theta and d0/wrapped phi/qoverp/relative-pT residuals, six bound pulls,
mean/median, central width, SD/RMS/tails/finite counts. Preserve truth-minus-fit
sign of DES041; prior DES042 truth scan has opposite bias sign. Distinguish the
frozen analyzer q16/q84 width from new central68.268949% widths. Do not derive
relative-pT pulls without theta–qoverp covariance. Use Wilson68/95 event rates,
exact zero-event upper bounds, event-block candidate fractions and paired
contrasts. Existing5000-event baseline stays byte-identical; compare0.5mm fresh
first1000-event subset explicitly, accounting for ambiguity cap difference.

Limits: statistical-only single-particle/unmerged Gaussian sensitivity; no
material savings, occupancy, ASIC/capacitance or calibrated coarse-sensor claim.
Fatras electron approximation/0.5GeV cutoff, Geant4 25ns/outer-volume stops,
effective-vs-detailed material, electron momentum tails and pion descendant
matching remain visible. Recommendation grants no human acceptance/sign-off.

## Actual checks

Pinned Git source/hash inspection, width/binary and sample precision arithmetic;
session validation217 records and summary passed. No native runtime/build check.
