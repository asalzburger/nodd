# DES-003 — Validation study catalogue

- Date: 2026-09-17; status: DRAFT; human reviewers and acceptance criteria pending.
- Governing proposal: [DES-003](../design/DES-003-global-envelopes.md).
- Scope: review-1 envelope consequences for 14 TeV HL-LHC studies. No production
  implementation is authorized by this catalogue.
- Sources and derivations: [calorimeter review](../design/inputs/DES-003-calorimeter-review-1.md),
  [muon review](../design/inputs/DES-003-muon-review-1.md),
  [physics review](../design/inputs/DES-003-physics-review-1.md), and
  [software tool assessment](../design/inputs/DES-003-software-validation-input.md).

The Physics and Performance Validation role owns observable definitions and
scientific interpretation; the Software Engineer owns implementation and retained
execution evidence. Subsystem and System Architect owners supply geometry, field,
material and response assumptions. Human review owns acceptance.

## Global and calorimeter studies

| ID | Owner with software support | Inputs/dependencies | Output | Current status |
| --- | --- | --- | --- | --- |
| ENV-V01 | System Architect | Proposed symmetric rectangles and prompt η grid | Allocation overlaps, r–z drawing, path intervals; full/partial axial allocation traversal | Executed analytic prototype: [report](DES-003-envelope-diagnostics.json); no field, vertices or active geometry |
| ENV-V02 | Tracker/calorimeter/muon technicians | Active surfaces, dead edges, φ sectors, luminous-region and displaced-vertex hypotheses | Minimum distinct layers/stations and angular gap maps; finite-vertex aperture margins | Planned; no active-layout definition yet |
| ENV-V03 | System Architect | Named service handoffs, support/cable/cooling mass ranges, routing sectors | Continuity and conflicts of routes, material before/within/between detectors | Planned; empty gaps are not validated routes |
| CAL-V01 | Calorimeter + Physics | Sampling/absorber model, inactive skins, species/energy grid physically consistent with forward kinematics | X0/λI path budgets and uncertainty scenarios, distinguishing active stack and dead material | Planned; allocation depth supplies no material budget |
| CAL-V02 | Calorimeter + Physics | CAL-V01, geometry/field/physics list; actual beam hole, cracks and service paths | Shower containment/leakage distributions versus energy/η/φ/vertex, especially endcap-to-forward transition | Planned full transport; historical depths are screening inputs only |
| CAL-V03 | Calorimeter + muon + Physics | CAL-V02, station locations, shielding hypotheses | Punch-through before stations and interaction with detached calorimeter; separate upstream/downstream ordering | Planned; must precede added-absorber recommendation |
| FIELD-V01 | System Architect + Physics | Three magnet architecture hypotheses, coil/material/return assumptions | Spatial vector fields, finite-length variation, field/material/space tradeoffs | Analytic coil estimates in physics input only; no field solution executed |
| PROP-V01 | Software + Physics | Chosen field identity, active surfaces, material, momentum/charge/species/vertex grid | Full charged-particle propagation, sensitive crossings, numerical convergence and transport/reconstruction agreement | **Mandatory later**; planned ACTS installation will supply straight-line and field propagation; version/integration pending, not installed in this review |
| TIME-V01 | Tracker + Physics | Outermost tracker layer as potential timing baseline, forward coverage, supports/services, response and ageing hypotheses | Geometric and propagated association coverage; later time/vertex efficiency | Planned; outer silicon placement alone supplies no timing model |

ENV-V01 reports a full axial allocation when the ray enters at the front and
leaves at the back; corner contact can have zero margin. It does not prove active
depth or containment. E1-R2's η=5.2 forward entrance margin is only about 3.57 mm
under the prompt-ray assumption. Finite vertices, beam pipe, passive rims and
shower spread belong to ENV-V02/CAL-V02 before extension beyond the η=5 objective.

## Muon catalogue requested in PR review

These IDs preserve the muon agent's review-1 requests. All are planned except the
parent-envelope precursor to MU-V01; no active-station or transport result is
claimed. Dependencies are evidence prerequisites, not permission to implement
unsigned production geometry.

| ID | Lead owner | Required inputs/dependencies | Retained output |
| --- | --- | --- | --- |
| MU-V01 | Muon technician | Actual station active shapes/dead sectors; ENV-V02; later PROP-V01 | Distinct station intersections, entrance/exit locations and paths versus η/φ/vertex |
| MU-V02 | Muon technician + Physics | MU-V01, measurement-coordinate/readout contracts | Independent coordinates, orientations, lever arms and transition gaps; separate multiple steps from independent stations |
| MU-V03 | System Architect + Physics | FIELD-V01, measurement surfaces, PROP-V01 | Vector samples, signed bending integrals and inverse-momentum displacement response for iron-free, yoked and toroidal options |
| MU-V04 | Muon technician + Physics | Material inventory, transport configuration, MU-V01 | Material to/between stations, energy loss, scattering and stopping fractions with scenario uncertainties |
| MU-V05 | Calorimeter/muon + Physics | CAL-V02/03, particle samples then 14 TeV collision and selected pile-up spectra | Hadron leakage, punch-through, decay muons and station backgrounds before extra-steel proposals |
| MU-V06 | Muon technician + Software | MU-V01, MU-V05, response/inefficiency/occupancy model | True crossings → simulated hits → segments, with distinct denominators |
| MU-V07 | Physics | MU-V02–06, reconstruction and alignment assumptions | Identification/fakes/charge/momentum metrics: tracker-combined, vertex-constrained muon-only, unconstrained standalone; include displaced particles |
| MU-V08 | Physics + Software | MU-V03–07, shared field identity and uncertainty scenarios | Field/alignment/material systematic effects and simulation/reconstruction consistency |

## Evidence and review contract

For each execution retain configuration/input hashes, project/tool revisions,
environment, commands, species/energy or momentum/charge, η/φ/vertex distribution,
field identity, material/response assumptions, seeds, numerical settings and
denominators. Preserve failures and untested regions. Follow
[ADR-003](../decisions/ADR-003-validation-and-artifact-policy.md) for artifacts.

Define numerical convergence controls separately from physical acceptance limits.
No pass/fail detector acceptance follows from unspecified tolerances. Follow-up
decisions: realistic source spectra/pile-up and luminosity, vertex distributions,
layer/station redundancy, leakage/fake-rate targets, timing operating lifetime,
magnet alternatives and reviewer assignments. The coordinator orders these tasks;
stage-A progression is not reopened.

Review round 2 keeps this catalogue as follow-up work. Detailed magnetic-system
and dedicated muon research come next; their completion is not implied by
envelope sign-off. No ACTS installation or propagation was performed here.
