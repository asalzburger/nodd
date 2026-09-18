# DES-004 — Independent physics comparison contract

- Date: 2026-09-17; status: DRAFT; unsigned PROTOTYPE study settings.
- Scope: first magnetic research increment and its later comparison prerequisites.
- Governing context: [magnetic research plan](../../MAGNET_RESEARCH_PLAN.md),
  [DES-003](../DES-003-global-envelopes.md), [validation catalogue](../../validation/DES-003-study-catalogue.md),
  [ADR-003](../../decisions/ADR-003-validation-and-artifact-policy.md).
- Owner: Physics and Performance Validation; implementation/evidence: Software
  Engineer; human reviewer/approver: pending.

## 1. Boundary of the first result

User-authorized research starts with candidate cards, verified ACTS setup and a
vacuum-solenoid benchmark. A verified vacuum field is **not** a validated MAG-01
physical detector: even an architecture without a dedicated yoke contains
calorimeter/support steel. The first increment must not rank magnet candidates,
quote detector momentum resolution, or infer shower containment.

The agreed investigation is 14 TeV proton collisions, tracker |η|<4, calorimeters
|η|<5, muons |η|<3 with a 3.5 stretch objective. These are scope boundaries, not
proof of efficiency. Compare MAG-01 through MAG-06 from the research plan at
3 T centrally initially, while reporting differences in coil size, current,
material and field energy. Equal central field is not equal magnetic leverage
or equal engineering demand.

## 2. Shared diagnostic surfaces for subsequent propagation

All dimensions below are **NODD DESIGN CHOICE — proposed test-fixture values**,
with no approving humans. They are deliberately simple samples of the E1-R2
host, not selected detector layers; no production geometry may consume them.

| Diagnostic surfaces | Extent | Purpose |
| --- | --- | --- |
| Tracker cylinders r=0.05, 0.20, 0.50, 1.00 m | |z|≤3.10 m | Inner/outer transverse leverage |
| Tracker disks z=±0.50, ±1.50, ±2.50, ±3.00 m | 0.03≤r≤1.10 m | Forward progression and end-field sensitivity |
| Muon cylinders r=4.50, 5.50, 6.50 m | |z|≤7.00 m | Three separated outer measurements |
| Muon disks z=±7.50, ±8.70, ±10.00 m | 0.40≤r≤6.90 m | Endcap lever arm and aperture losses |

**Compatibility limit:** the r=4.50 m muon cylinder coincides with the MAG-03
vacuum current sheet and conflicts with its physical coil allocation. It is a
fixed diagnostic fixture only and cannot count as a realizable measurement there.
Report it as excluded/incompatible, not a missing chamber efficiency. Before
fits, agree an architecture-compatible common station set or explicitly separate
a revised-layout comparison; do not silently move this station for one candidate.

Keep each surface's local coordinates and normal explicit. Cylinders measure
arc coordinate rφ and z; disks use two local Cartesian coordinates. These are
zero-thickness diagnostic surfaces, not material or chamber models. Count first
outward crossings separately from later recrossings; preserve curling tracks,
missing intersections and propagation failures in the denominator. Crossing a
surface is not obtaining a sensitive hit. The tracker cylinder/disk intersections
are artificial; handle duplicate/coincident crossings explicitly.

Before fitting, freeze common measurement covariance and alignment assumptions in
a versioned fixture. No detector-specific precision is selected here. Start with
exact crossing coordinates and geometric response derivatives, then a separately
labelled simplified measurement model. Change surfaces only in an explicit
second, architecture-optimized comparison. Never conceal moving stations inside
a supposedly fixed-layout field comparison.

## 3. Minimal sample, chosen before ranking

**NODD DESIGN CHOICE — proposed diagnostic values:** use muons of both charges,
origin (0,0,0), total momenta **10, 100, 1000 GeV/c**, and
|η|=**0, 0.8, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0**, with both longitudinal signs
except η=0. Use φ=**0, π/8, π/4, π/2** initially. These are sparse tests, not
collision spectra, acceptance integration or a claim that these are optimal bins.
The momentum decades expose curling/strong bending and the high-momentum limit;
η points sample central, transition and stated forward objectives. Report both
p and pT=p/coshη: fixed total momentum gives very different pT in the forward
region. Do not silently label this a fixed-pT scan.

Start axisymmetric vacuum diagnostics with φ=0 and a rotated duplicate; retain
all azimuths when discrete coils are introduced. Add coil-centre and inter-coil
sector directions from each candidate, together with their common union, before
toroid comparisons. A few selected φ directions cannot establish full hermeticity.

Run prompt particles first. Then use **diagnostic** z vertices ±0.10 m and a
separate displaced origin (x,y,z)=(0.10,0,0) m, with momentum direction specified
independently. These stress boundaries/constraints; they are not a luminous-region
or decay distribution. Refine samples around turning points, field reversals,
apertures and missing crossings after the initial grid, retaining the initial
results. Physically weighted collision/pile-up studies remain later work.

## 4. Observables and fair controls

**INFERENCE — Lorentz force:** the local direction change satisfies
`d u/ds = (q/p) 0.299792458 (u × B)` for p in GeV/c, B in tesla and s in metres,
with q in units of elementary charge and negligible energy loss. Record signed
components of `∫(u × B) ds` in a fixed, documented basis between named surfaces,
as well as `∫|u × B| ds`. Opposite contributions may cancel in the former while
the latter stays large. Also report positions/directions at crossings and
signed displacement derivatives versus q/p; spatially separated opposing bends
can retain measurement information even if their net direction change cancels.
No single field integral is a momentum-resolution estimate.

For small η, axial solenoidal field gives transverse bending; forward trajectories
can run almost along that field. Report Br, Bz and the full vector, field reversals,
transverse measurement leverage and crossing multiplicity, not Bz(0,0) alone.

Separate the later fit outputs:

1. Tracker-only, without muon measurements.
2. Muon-only unconstrained standalone, with no tracker or interaction-point prior.
3. Muon-only with an explicitly specified vertex prior.
4. Combined tracker and muon fit; state any vertex prior independently.

Rank neither resolutions nor charge significance before specifying the measurement
model, its uncertainties and failures. No vertex prior may leak into the
standalone result. Keep vacuum field-only, fixed-material and physically
candidate-dependent material comparisons distinct. Scattering/energy loss can
change both surviving-track populations and precision; report survival and
conditional performance separately. Geant4 shower/leakage work remains CAL-V02/03,
not a result of ACTS field propagation.

## 5. Numerical verification contract

These checks implement FIELD-V01, PROP-V01 and MU-V03; they do not complete
MU-V07 performance validation. First distinguish closed-form references from
comparisons that share the same implementation.

| Check | Independent reference / failure exposed |
| --- | --- |
| Vacuum finite solenoid on axis | Analytic finite-current-sheet formula; normalization, length and units |
| Zero-field transport | Straight-line intersections; navigation and unit errors |
| Uniform field transport | Analytic helix; charge, curvature, momentum and path conventions |
| Reversing current | Field reverses at the same position; hidden unsigned operations |
| Reversing both charge and field | Same vacuum spatial trajectory with the same initial state |
| Current scaling | Linear field response only for the vacuum/current-source model |
| Reflection/rotation | Model-specific Br/Bz parity and cylindrical covariance; not universal toroid symmetry |
| Integration refinement | Direct field converges as current quadrature is refined |
| Map versus direct evaluation | Interpolation error at held-out positions; boundary/out-of-domain policy |
| Divergence/curl away from sources | Numerical consistency in vacuum; exclude coil singularities and unsuitable stencils |

**NODD DESIGN CHOICE — proposed numerical screening threshold:** for a smooth
vacuum field benchmark, test component/axis discrepancies against
`1e-6 T + 1e-5 × |B_reference|`. The absolute term handles field zeros and the
relative term demands substantially finer agreement than percent-level architecture
effects; neither is a detector field-calibration requirement. Specify checked
positions, quadrature and refinement in the executable test. If this is not
attainable near a model singularity, diagnose the model/domain rather than silently
loosening the test. Conservation, interpolation and transport checks need their
own dimensioned thresholds before execution; this memo does not invent universal
position/momentum tolerances without knowing the implementation.

Numerical uncertainty must be below a claimed candidate difference; otherwise
report the difference as unresolved. A passing arithmetic threshold cannot validate
conductor feasibility, magnetic saturation, material response or physical accuracy.
Do not adapt performance acceptance thresholds to the observed winning candidate.

## 6. Provenance and review gate

Retain field definitions, input hashes, source revision, tool versions, units,
normalization, sample/fixture, map bounds, interpolation policy, commands,
quadrature/step settings and exact checks. Record failures and checks not run.
Random seeds are required when stochastic material or measurement smearing begins;
the deterministic first benchmark needs none. Physics reviews the vacuum-solenoid
report against this contract before any candidate ranking.

Existing source context: SRC-CMS-JINST-2008 §2.1/Table2.1, PDF33/35, establishes
that cold mass and return steel are explicit magnet components;
SRC-ATLAS-SOLENOID-2007 §IV.A, PDF2, distinguishes air-core testing from operation
with surrounding calorimeter iron. These facts motivate keeping vacuum diagnostic
and physical detector models separate. New fixture numbers above derive from
sampling the approved envelope scale, not from either experiment's layer design.

Initial protocol drafting inspected the repository plan, E1-R2 allocations and
validation catalogue. The independent numerical review performed afterward is
recorded below; ACTS execution is reported separately by the software engineer.


## 7. Independent review of the first vacuum benchmark

Review date: 2026-09-17. Inspected `solenoid.py`, `test_solenoid.py` and the
retained `DES-004-solenoid-benchmark.json`. The current-sheet Biot–Savart integrands,
normalization and near-sheet exclusion are consistent with the stated model;
no blocking mathematical defect was identified in this bounded review.

Actual checks run with `reference/cache/envelope-venv/bin/python -B`:

- All six `test_solenoid.py` tests passed (axis, reversal/reflection, vacuum
  Maxwell identities, quadrature, far-field dipole, invalid-domain handling).
- Retained report configuration and script SHA-256 values matched the files.
- Independently increased quadrature to **384×512**, twice the report's fine
  setting in each dimension, and reevaluated its six positions per candidate.
  Every discrepancy from retained nominal values met the recorded threshold.
  Maximum differences were about **3.23×10⁻¹² T for MAG-01** and
  **3.20×10⁻¹⁴ T for MAG-03**. This is an extra numerical convergence check
  using the same integrand, not an independent magnetostatic solver.

Review limitations and follow-ups:

- The initial unit convergence test used a looser 10⁻⁴ T absolute check.
  It now uses the same `1e-6 T + 1e-5 norm(B_reference)` criterion as the
  retained benchmark and independent reevaluation; the coordinator reran it.
- The atlas masks 26 additional MAG-01 points and 329 MAG-03 points for failed
  nominal/fine convergence, besides the ideal-sheet exclusion. The report's
  largest pre-mask discrepancy is about 0.243 T for MAG-03. Masking is appropriate
  for this display, but those locations are unresolved, not low-field regions.
  This review did not rerun the complete atlas or validate interpolation.
- Nominal/fine agreement does not alone guarantee accuracy at every retained
  off-axis pixel. More refinement or an independent formulation is needed
  before this atlas becomes a propagation map.
- Fixed ±3 T colour limits can saturate larger local components; colours are
  display choices, not assertions that local fields are bounded by 3 T.
- No ACTS trajectory, measurement fit, iron response or detector performance
  was verified by these six field tests. The r=4.50 m measurement conflict above
  remains a prerequisite to meaningful MAG-03 station comparisons.

Result: the sampled vacuum benchmark is numerically supported within its declared
scope; no physical candidate selection or human sign-off follows from this review.

Post-review correction: the coordinator aligned the quadrature unit test with the
benchmark screening threshold and added colour-bar extension markers to show
clipping beyond ±3 T. These changes do not resolve masked field regions.
