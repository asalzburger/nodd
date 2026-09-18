# DES-005 input — PhysVal tracker-system study contract

- Date: 2026-09-18.
- Status: **DRAFT — proposed research and validation plan; no human sign-off**.
- Owner: Physics and Performance Validation (`PhysVal`); coordinating roles:
  `SysArch`, `TrackTech`, `SoftEng`. Human technical reviewer: pending.
- Context: [PROJECT](../../../PROJECT.md), [development plan](../../DEVELOPMENT_PLAN.md),
  [DES-003](../DES-003-global-envelopes.md),
  [ADR-003](../../decisions/ADR-003-validation-and-artifact-policy.md), and
  [ODD assessment](../../validation/ODD-realism-assessment.md).
- Existing pixel work: PR #8 / issue #7; branch revision verified by the
  coordinating agent: `d237f146b578915cc032b30efa50044cf6344d5f`.
  The parent plan retains the verified pixel document and dependency links.
- Magnetic input inspected at `040337c2d6129014655a7534e0ea79c6ef693bc2`,
  `docs/design/DES-004-magnetic-configurations.md` and
  `docs/design/inputs/DES-004-physics-validation.md` on
  `origin/research/magnetic-configurations`. These are branch research inputs,
  not merged or accepted tracker performance evidence.

## Position and provenance

**NODD DESIGN CHOICE — human-directed scope:** tracking must cover `|eta| < 4`;
the E1-R2 tracker assembly envelope bounds the study. Pixels, short strips
(strixels) and stereo long strips are the ODD-guided starting architecture.
Layer counts, subsystem boundaries, radii, disk positions and timing remain
research questions. The 25 mm inner host boundary is not a sensor radius.
An inherited outermost-layer timing hypothesis must be tested alongside a
no-timing control and motivated alternatives. No reduction of the fixed tracker
coverage requirement is proposed.

Unless explicitly labelled FACT or INFERENCE, the protocol choices below are
**NODD DESIGN CHOICE — proposed; approving humans pending**. They do not select
numerical detector parameters or acceptance thresholds.

| Evidence | Classification and locator | Consequence for this study |
| --- | --- | --- |
| ODD measurement representations differ | **FACT:** SRC-ODD-UPSTREAM at `c167363f3d4ad1540a577af99071283caf54f3a6`; [ODD assessment](../../validation/ODD-realism-assessment.md), E03/E04 and “Outer tracker”; precise source paths in its evidence ledger | XML segmentation, ACTS geometric digitization and smearing must be distinguished before importing measurement errors or claiming stereo information. |
| Layer iteration can precede full simulation | **FACT:** SRC-ATLAS-TDR-030, §2.1.1–2.1.2, physical PDF pp.27–29, as recorded in [tracker envelope input](DES-003-tracker-envelope-input.md) | Historical design uses field/material-aware fast estimates followed by Geant4; this motivates a progressive process, not adoption of its layout. |
| Coverage depends on luminous region and measurement definition | **FACT:** SRC-CMS-TDR-014, §3.1, physical PDF p.25; SRC-ATLAS-TDR-030, §2.1, physical PDF pp.25–26; [tracker input](DES-003-tracker-envelope-input.md) | Existing designs distinguish pixel/strip reach and state luminous-region assumptions. Their hit-count targets and beamspot are not nODD requirements. |
| Timing requires dedicated response and complete hardware | **FACT:** SRC-CMS-TDR-020, §1.4.1/PDF21 and §2.1/PDF29; SRC-ATLAS-TDR-031, abstract/PDF5 and §2.2/PDF31–32; [physics review](DES-003-physics-review-1.md), §2 | Timing benefit cannot be inferred from spatial hit timestamps; sensor/readout, supports, cooling, ageing and association belong in the comparison. |

Source identities and public links are in the [catalogue](../../../reference/manifest.yaml).
These are existing source observations, not newly verified operating performance.

## Sample and metric contract before candidate ranking

Start with prompt charged particles of both charge signs, both longitudinal
hemispheres and full azimuth. Specify momentum direction at the production vertex;
report both total momentum and transverse momentum. Define the sampled `eta`,
`phi`, momentum and production-position distributions explicitly. Increase
sampling around barrel/endcap transitions, disk inner edges, support/service
sectors and coverage boundaries, retaining the original comparison grid.

Use deterministic origin and displaced-longitudinal-origin tests for initial
geometry debugging. They are not a beamspot model. Before a layout is frozen,
specify a sourced reference luminous distribution, longitudinal/transverse widths,
offsets, correlations and crossing-angle assumptions where relevant; record tail
treatment and test both conditional coverage versus vertex and the distribution-
weighted result. No beamspot width is selected here. A final beamspot study is a
revalidation of an input already used in layout selection, not its first use.

Keep prompt performance with and without an explicit vertex prior separate.
Define displaced-track stress cases independently; a displaced validation sample
does not silently establish a new displaced-physics requirement. Later event
samples require explicit collision energy, pile-up distribution, bunch/time
structure and response assumptions. No pile-up multiplicity is selected here.

| Proposed benchmark | Reported observables | Decision supported / limitation |
| --- | --- | --- |
| Geometric prompt and vertex-shift probes | Distinct active sensors, independent measurement coordinates, pixel/stereo redundancy, holes, longest gaps, transverse and longitudinal lever arms, angular maps | Reject geometrically inadequate arrangements; crossing counts alone do not demonstrate reconstructibility. |
| Isolated charged-particle transport and fast fits | Bias and residual distributions in `q/p`, transverse momentum, impact parameters, direction and extrapolated position; pulls, tail fractions, charge mistakes, fit success | Compare information and material tradeoffs with common response assumptions; truth-seeded fits do not measure pattern recognition. |
| Barrel/endcap and forward stress samples | Same metrics versus `eta`, `phi`, vertex, momentum and named interface regions | Expose weak bins hidden by global averages, especially forward lever arms. |
| Material/response/field/alignment variations | Changes in efficiency, residuals/pulls, tails and fitted-parameter correlations | Determine whether a candidate advantage survives uncertainty rather than relying on one nominal curve. |
| Occupancy and reconstruction samples | Hit/channel occupancy, cluster overlap or merged hits where modeled, efficiency, fake/duplicate rate, timing association, runtime/memory | Select viable granularity and pattern recognition under an explicit event model. Single-particle transport cannot settle this. |
| Timing alternatives | Track-to-vertex association, vertex separation/assignment, timing efficiency and resolution versus kinematics, impact on spatial tracking | Decide whether timing earns its material, power and coverage costs under a sourced response model. |
| Later physics-use-case samples | Reviewed vertexing, heavy-flavour/displaced diagnostics if in scope, forward association, isolation or pile-up rejection observables | Connect tracking improvements to intended analyses; high-level gains require the corresponding reconstruction and subsystem models. |

For every metric define denominator, truth selection, matching, reconstructed
track quality, units, binning and uncertainty calculation before the comparison.
Show all generated probes, losses, out-of-domain propagation, missing hits,
failed fits and surviving-track conditional precision separately. Do not obtain
apparently better resolution by silently removing failed or badly measured tracks.
Use confidence intervals and tail-sensitive summaries; record the chosen
interval/quantile definitions before running a selection comparison.

## Increasing fidelity and evidence gates

| Gate | Work and necessary inputs | Evidence required to proceed |
| --- | --- | --- |
| PV-A: comparison contract | Pin the ODD control and candidate catalogue; define measurement coordinates, units, material ownership, field identity and sample/metric contract; list missing inputs | `PhysVal` reviews comparison validity; `SysArch` and `TrackTech` agree buildable study bounds. Missing quantitative requirements are explicit. |
| PV-B: parametric screen | Analytic estimates and IdRes if its availability/capabilities are verified; vary layer/disk placement, sensor precision, material and simple field assumptions | Reproducible covariance/lever-arm trends, central/forward differences, beamspot sensitivity and a shortlist with rejected alternatives explained. No realistic efficiency claim. |
| PV-C: ACTS geometry and transport | Active module extents, inactive edges, orientations/stereo pairing, supports/services and explicit field domains; begin with verified zero/uniform-field controls, then available DES-004 fields | Crossings/holes and material maps versus kinematics/vertex/azimuth; independent measurement rank and numerical checks; no unexplained gaps or silent exclusions. |
| PV-D: fast fit and reconstruction | Measurement covariance, response inefficiency, material effects, realistic vector fields and alignment scenarios | First truth-seeded fit residuals/pulls; separately pattern recognition with occupancy/background scenarios. Demonstrate shortlist robustness before requesting layout freeze. |
| PV-E: later detailed transport | Signed-off designs and integration prerequisites; DD4hep with Geant4 backend, digitization and ACTS conversion | Detailed construction/material/coverage consistency; single-particle and then event-level comparisons; explain differences from fast models and retain applicability limits. |

These gates permit informative partial results. A blocked physical field model
does not block verified uniform-field controls; incomplete pixel services do not
block clearly labelled material scenarios. Partial results cannot pass the later
physical selection gate by inheriting an earlier numerical-test success.
Layouts can be shortlisted conditionally; human selection requires criteria and
disposition of unresolved dependencies. Required performance limits, statistics
and numerical tolerances must be specified and reviewed before acceptance.

**INFERENCE — measurement information:** for a linearized spatial measurement
model `m = H a + noise`, the measurement information is `H^T V^-1 H` when the
measurement covariance `V` is invertible and process noise is omitted. Its rank
and conditioning expose unconstrained or weakly measured parameter combinations.
Two strip sensors must use their actual axes and covariance/pairing model;
counting them as two independent two-dimensional hits invents information.
Material scattering requires process-noise-aware estimation beyond this screening
expression. A precise unconstrained parameter fit cannot be inferred from hit
count or a full-rank matrix alone.

**INFERENCE — forward geometry:** for a straight ray from the beam axis,
`r = |z-z_vertex| / sinh(|eta|)`. Consequently the longest available barrel
radius is not the forward track's transverse measurement lever arm. Disk inner
radii, longitudinal spacing, sensor precision and the sampled magnetic field
must be tested together. This ray relation is a geometry check, not transport
for low-momentum curved tracks or off-axis vertices.

## Material and field comparisons

Test the machinery first on explicit isolated **PROTOTYPE** fixtures with known
composition and path lengths. Then use named provisional component scenarios:
sensors/ASICs/flex, local supports, shared supports, cooling fluid and pipes,
power/data routing, beam pipe and external interfaces. Attach source or rationale,
uncertainty, ownership and replacement dependency to each approximation. Missing
components stay missing in the ledger; they do not become zero material.

Report directional `X/X0` and interaction lengths, spatial location and component
breakdown, including cumulative material before each useful measurement and
before calorimeter entry. Check mass/inventory consistency and mapped-versus-
detailed directional residuals when a detailed source exists. Integrated budget
agreement alone can hide misplaced scattering material and concentrated service
sectors. Test correlated component/routing variations, not only a global material
multiplier. Do not select target material merely to recover an ODD curve.

For field comparisons, first hold layout, response, material and samples fixed.
Keep vacuum field controls distinct from candidate physical fields with magnetic
materials; central-field equality is not a complete fairness criterion. Record
vector maps, interpolation, boundaries, numerical uncertainty, symmetry
assumptions and common simulation/reconstruction field identity. Report missing
or invalid field regions. Subsequently compare candidate-specific optimized
layouts with their resource and material consequences made explicit. Do not
merge these attribution and optimized comparisons into one performance ranking.

## Timing and coordinated challenges

Compare a physically credible no-timing layout, a timing-hardware/material case
with time information disabled, and the same case with time information enabled.
This separates the spatial cost from the time-measurement benefit. Also examine
integrated outer-layer versus separately placed barrel/forward timing when
technology evidence permits. Include time-of-flight/path correction, event time,
track association, time resolution/efficiency, ageing, occupancy and electronics
assumptions. A requirement for spatial tracking to `|eta| < 4` does not itself
require identical timing reach; report the uncovered timing regions and their
physics consequences.

- **To SysArch:** fitting inside the host is necessary but insufficient. Protect
  forward lever arms and transition redundancy; do not freeze layer positions
  before services and beamspot sensitivity are considered.
- **To TrackTech:** module realism must include measurable coordinates, covariance,
  inactive periphery and route material. A technologically attractive module can
  still produce poor forward information or unaffordable occupancy. Pixel work
  feeds the system through a versioned interface; its completion need not block
  provisional short-strip and long-strip study contracts.
- **To SoftEng:** availability of a tool or a successful propagation test is not
  physics validation. Preserve failures and distinguish ideal surfaces, active
  modules, truth-seeded fitting and actual reconstruction. Cross-check numerical
  effects against claimed candidate differences.
- **PhysVal commitment:** publish criteria before acceptance, quantify uncertainty,
  report adverse results, and allow physically justified realism changes even
  when an idealized ODD reference has a better nominal resolution.

Open human decisions: performance targets by region and use case; minimum useful
measurement redundancy; luminous distribution and tails; momentum/event/occupancy
scenarios; displaced scope; timing objectives; allowed material, alignment and
field uncertainties. These are proposed review inputs, not invented limits.

Verification for this input: inspected repository designs, source-assessment
locators, development plan, ADR-003 and magnetic research documents. No IdRes,
ACTS, DD4hep, Geant4, material scan, fit or detector-performance study was run.
The parent task records documentation checks and the paired session log.
