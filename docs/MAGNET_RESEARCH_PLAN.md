# Magnetic configuration research — proposed work plan

**2026-09-22 review amendment:** active scope is MAG-01 through MAG-05.
MAG-06 is withdrawn following the magnetic-field expert's request; its original
plan below is historical. Use [finite homogeneous main windings](design/inputs/DES-004-magnet-expert-review.md)
for new calculations, and replace provisional enclosure allowances with an
engineering assessment before claiming fit. No production change is authorized.

- Date: 2026-09-17; status: **DRAFT research protocol**, execution authorized by the user on 2026-09-17.
- Basis: E1-R2 at `cb654ee91457b22d899a898faf2c8bf6e0fc275e`, approved in [PR #4](https://github.com/asalzburger/nodd/pull/4) and merged as `b106610b929cdfa603dd5f1ef2a6e79dbb633a7f`.
- Execution branch: `research/magnetic-configurations`, synchronized with main at `60ef366`; previous planning state remains in Git. Design sign-off states are unchanged.
- Scope: propose a physically credible magnetic architecture and comparison method; isolated PROTOTYPE tools and dependency installation authorized; no production detector changes.
- All candidate definitions, comparison settings and work sequencing below are **NODD DESIGN CHOICE — proposed**, pending discussion. Physical consequences are hypotheses to test, not measured nODD performance.

## 1. Research question and boundaries

Which magnetic architecture best supports the agreed 14 TeV programme: tracking
to |eta|<4, calorimetry to |eta|<5, and muons to |eta|<3 with 3.5 stretch, within
credible space, material and magnet demands? Independent muon momentum remains
the baseline investigation, with combined measurement retained as an alternative.

Use E1-R2 as the reference. Keep tracker dimensions and nominal measurement
assumptions common initially. Candidate-specific envelope changes must be explicit;
outer coils cannot simply occupy the existing calorimeter/muon gap. Record whether
an outer coil surrounds barrel calorimeters only or also their endcaps. Detached
forward calorimetry remains outside the central-magnet terminology.

## 2. Six starting candidates

| ID | Configuration | Question |
| --- | --- | --- |
| MAG-01 | Inner solenoid, no dedicated return yoke | How far can tracker plus fringe-field/combined muon measurements go? |
| MAG-02 | Inner solenoid plus dedicated instrumented iron return | Does return-field bending justify mass, scattering and space? |
| MAG-03 | Solenoid outside central calorimeters, no dedicated return yoke | Can longer combined-measurement leverage avoid a separate muon magnet? |
| MAG-04 | Outer solenoid plus instrumented iron return | What does a CMS-like topology offer at nODD scale? |
| MAG-05 | Inner solenoid plus air-core barrel/endcap toroids | Can standalone-compatible muon bending fit the allocated host and forward reach? |
| MAG-06 | Solenoid plus active return/shielding coils | Can controlled return flux reduce dependence on a massive dedicated yoke? |

MAG-06 is withdrawn; no further feasibility screen is scheduled. End
compensation coils, iron-dominated toroids and hybrid arrangements form a short
brainstorming reserve; add a candidate only when it tests a distinct benefit.
No dedicated yoke does not mean an iron-free detector: calorimeter/support steel
must enter the physical model. Current-only fields are explicit diagnostic controls.

Compare first at **3 T centrally**, then at credible current, material, size and
energy demands. Equal central field is a normalization, not equal performance or
equal resources. Scan other strengths only after the topology comparison is useful.

## 3. Team assignments

| Role | Responsibility and deliverable |
| --- | --- |
| Project Coordinator | Candidate definitions, common assumptions, sequencing, tradeoff matrix and decisions requiring human input |
| System Architect, supporting coordinator | Coil/yoke/toroid space and service interfaces, feasible candidate geometry, explicit envelope-amendment requests |
| Calorimeter engineer | Inside/outside-coil consequences: upstream conversions/showers, dead material, leakage, field exposure, supports and service exits; central versus forward systems |
| Muon engineer | Conditional preference for standalone/combined purposes; station leverage, toroid sectors, return-field bending, scattering and forward gaps |
| Tracker engineer | Spatial vector field and useful bending to eta 4, finite-solenoid end losses, transverse lever arm, low-momentum reach and timing-surface crossings |
| Physics and Performance office | Particle/vertex/charge/momentum/angular samples, independent criteria, uncertainty and fair comparison; separate tracker-only, standalone, vertex-constrained and combined results |
| Software coordinator | Reproducible field models/maps, ACTS integration, numerical verification, propagation and displays |
| Publication office | One coherent report, source ledger, candidate cards, figure provenance, decisions and unresolved questions; eventual TDR-ready material |

Specialist inputs run concurrently where independent. Architect reconciliation
precedes propagation comparisons; Physics challenges the conclusions independently.
Publication proceeds throughout, without implying that all roles must run at once.

## 4. Staged execution, with review points

### A — Candidate cards and shared comparison contract

For each candidate record coil geometry and current, return path, ferromagnetic
material assumptions, measurement regions, field target, space/material demands,
source precedents and unknowns. Use public built-system/operational evidence before
advanced concepts. Agree diagnostic barrel cylinders, forward disks and muon
surfaces, explicitly not a selected detector-layer design. Fix common measurement
uncertainties and fitting constraints. Physics proposes the sampling grid and
criteria before seeing rankings. **Review point:** shortlist and comparison contract.

### B — Verified field and propagation foundations

Separate field calculation from particle propagation. Use finite-current
Biot–Savart integration/analytic checks for vacuum solenoid models. Dedicated
ferromagnetic returns require magnetostatic treatment with B–H curves and
saturation; a constant-permeability multiplier is not a sufficient substitute.
Select an open reproducible solver after a platform and benchmark check; a blocked
solver must leave the yoke comparison explicitly incomplete, not silently idealized.
Discrete toroids require three-dimensional coil/field structure.

Represent justified axisymmetric cases with Br(r,z), Bz(r,z), and discrete/asymmetric
cases with full 3D vectors. Retain units, coordinates, signs, map boundaries,
interpolation, current normalization, source/model hashes and out-of-domain policy.

ACTS setup is a first execution task, not assumed available. **FACT —
SRC-PYPI-ACTS-NAME:** public PyPI `acts` is Android Comms Test Suite; plain
`pip install acts` does not select tracking ACTS. The user identified `pyacts`.
**FACT — SRC-PYPI-PYACTS:** the official ACTS README recommends
`pip install pyacts` (import name `acts`). Verify and pin that distribution first,
using a source build only if needed. **FACT —
SRC-ACTS-SOFTWARE-DOCS:** ACTS documents straight-line and fourth-order Runge–Kutta
steppers and field providers. Verify bindings/API and compiler/Python/platform
compatibility in the chosen release. Do not substitute an unverified custom RK4
for the requested ACTS propagation.

Checks: zero-field lines, uniform-field helices, finite-solenoid axis values,
charge/field reversal, symmetry/divergence diagnostics away from singularities,
map versus direct evaluation, and integration/mesh/interpolation convergence.
**Review point:** numerical trustworthiness before architecture ranking.

### C — Field atlas and vacuum propagation

Produce matched-scale r–z and x–y field plots, component/sign maps, field lines,
coil/material overlays and toroid-sector slices. Add a lightweight interactive
viewer if useful; retain publication-ready SVG/PNG/PDF exports.

For identical diagnostic surfaces and particle samples, propagate both charges,
central/transition/forward directions, several momenta and relevant phi sectors.
Report signed bending between measured surfaces, deflection and displacement,
field reversals, crossings, coverage gaps and momentum-information proxies.
Central B and an unsigned field integral alone cannot rank forward tracking.
Treat missing crossings as outcomes rather than dropping those trajectories.

### D — Material and measurement consequences; shortlist

Compare field-only controls, then stated coil/yoke/calorimeter material scenarios
and simplified fits with common measurement assumptions. Distinguish tracker-only,
tracker-combined, muon-only with a vertex constraint, and unconstrained standalone
results. Any quoted resolution is conditional on that diagnostic detector.

Assess pre-ECal material and conversion risk, scattering/energy loss to muons,
stray-field extent, current/conductor plausibility, stored-energy and force scales,
space and services. ACTS propagation does not establish shower containment;
Geant4 leakage/punch-through studies remain a separate dependent work package.

Start with fixed-layout comparisons; show separately what improves after an
architecture-specific layout change. Report tradeoffs and uncertainties rather
than choosing arbitrary score weights. **Review point:** recommend a short list
and remaining evidence, not forced acceptance of a single magnet design.

## 5. Deliverables and proposed first increment

Research branch after discussion: `research/magnetic-configurations`.
Create the next available design/ADR IDs after synchronizing and checking the
register. Keep unsigned computational work isolated and labelled PROTOTYPE.

Deliverables: six candidate cards; source/assumption ledger; reproducible field
and propagation harness; field atlas; subsystem comparison table; requested
envelope amendments; decision memo and proposed TDR section outline.

First increment should deliver candidate cards, verified ACTS setup and the
vacuum-solenoid benchmark. That establishes a trustworthy path before expensive
3D/yoke/toroid studies. A later PR presents the comparison and recommendation;
execution of the first increment is now authorized. Review its evidence before
expensive yoke/toroid modelling and architecture ranking.
