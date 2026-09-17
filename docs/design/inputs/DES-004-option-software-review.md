# DES-004 — Software review of six magnetic options

- Date: 2026-09-17; status: DRAFT; approving humans pending.
- Scope: tool feasibility and discriminating evidence; no new solver execution.
- Parent: [DES-004](../DES-004-magnetic-configurations.md).

**NODD DESIGN CHOICE — recommendation:** advance inexpensive current-only controls
and a nonlinear-material benchmark in parallel. Solver availability is not a
fundamental reason to reject iron; an unvalidated solve is not physical evidence.

## Concrete path by candidate

| Option | Next software work | Evidence required before physical comparison |
| --- | --- | --- |
| MAG-01 | Convert verified finite-solenoid provider to a sampled r–z vector map; propagate through common measurement surfaces | Off-axis/interpolation convergence; add calorimeter/support steel separately; quantify forward bending |
| MAG-02 | Reproduce a nonlinear iron benchmark, then model explicit barrel/endcap plates and chamber gaps | Source-backed B–H curves, current renormalization, saturation and mesh/domain convergence; field/material co-registration |
| MAG-03 | Reuse MAG-01 pipeline at the proposed outer-coil dimensions | Common-surface result plus separately amended muon layout; physical field through calorimeter steel and fringe domain |
| MAG-04 | Reuse MAG-02 nonlinear workflow with outer coil and revised host | Plate/gap dimensions, material provenance and actual return-field information; flux-area arithmetic is only screening |
| MAG-05 | Construct discrete finite barrel/endcap coils and sample a 3D vector field | Coil-centre/inter-coil/transition samples, conductor regularization, support obstructions and station crossings; axisymmetric toroid control insufficient |
| MAG-06 | Superpose finite coaxial current-only coils, then explicit end-coil variants | Shared central/exterior-field objectives, current sensitivity and usable station region; restore steel before physical ranking |

## Verified tools and limits

**FACT:** the existing [pyacts setup](../../validation/DES-004-acts-setup.md)
demonstrated propagation fixtures and ideal-solenoid axis comparisons. It did not
demonstrate nODD maps, sensitive surfaces, material transport or momentum fits.

**FACT — SRC-ELMER-MGDYN-BH:** Elmer's official
[test input](https://github.com/ElmerCSC/elmerfem/blob/devel/fem/tests/mgdyn_bh/case.sif)
uses Cartesian 3D steady state, `WhitneyAVSolver`, Newton–Raphson settings and
an iron H–B curve (`Simulation`, `Solver 2`, `Material 2`). This establishes an
available nonlinear workflow; its test curve is not nODD steel data. Pin the
revision and reproduce its benchmark before adaptation.

**FACT — SRC-NGSOLVE-COIL-TUTORIAL:** the official
[NGSolve 6.2.2402 tutorial](https://docu.ngsolve.org/v6.2.2402/i-tutorials/wta/coil.html),
“Solve magnetostatic problem”, uses a 3D curl-conforming formulation with constant
vacuum permeability. It supports a coil/air implementation path, not a claim
that this example already handles nonlinear return iron. Neither solver was
installed or run for this written review; macOS integration remains unverified.

## Sequence and gates

**NODD DESIGN CHOICE:** first implement the shared map/units/domain contract and
MAG-01/03 surface propagation. In parallel reproduce Elmer's nonlinear benchmark;
then evaluate one coarse MAG-02/04 plate/gap scenario. MAG-05 needs a coil layout
first; MAG-06 needs finite return/end-coil dimensions before meaningful scans.

Require mesh, exterior-domain, interpolation and propagation convergence, finite
values and independent analytic checks. Map holes near ideal conductors must be
reported as unmodelled regions, never silently zero-filled. Compare signed bending
and measurement response; central-field equality or a scalar field integral cannot
establish standalone resolution. Missing surfaces, steel curves or covariance
models block that claim, not the topology. No additional physics acceptance gate
was closed by this documentation review.
