# DES-004 — Tracker magnetic-study input

**2026-09-24 sizing amendment:** [Current constraints and dimensions](DES-004-magnet-sizing-review.md)
supersede earlier winding/vessel and MAG-03/04 radial allocations below.
Earlier numerical results remain historical; complete-system engineering is open.

- Date: 2026-09-17; status: DRAFT; human reviewer/approver: pending.
- Scope: tracker requirements for magnetic research, not production geometry or
  a detector-performance result.
- Context: [candidate cards](../DES-004-magnetic-configurations.md),
  [physics comparison contract](DES-004-physics-validation.md),
  [System Architect input](DES-004-system-architecture.md),
  [tracker envelope evidence](DES-003-tracker-envelope-input.md).

## 1. Requirement: useful measurements throughout the tracking acceptance

**FACT about the project record:** the E1-R2 tracker allocation is
0.025≤r≤1.140 m, |z|≤3.150 m. Tracking to |η|=4 is an investigation objective;
it is not established by this bounding volume. The first magnetic comparison
normalizes MAG-01 and MAG-03 to Bz(0)=3 T while retaining that allocation.

**FACT — historical evidence:** SRC-CMS-TDR-014 §4.1/PDF71 links forward tracking
to pile-up mitigation in endcap calorimeters; §3.1/PDF25 specifies outer-tracker
coverage using crossed modules and notes a barrel/endcap weakness. SRC-ATLAS-TDR-030
§2.1.1/PDF27 (printed5) describes field/material-aware fast layout estimates
followed by Geant4 studies. These establish why the forward field, actual
measurements and transition regions need joint study; neither prescribes nODD
performance. Source identities and local editions are in the
[catalogue](../../../reference/manifest.yaml).

**INFERENCE — straight-line geometry:** for a prompt trajectory,
`r=z/sinh(η)`. At η=4 and z=3.150 m, r≈0.1154 m. Forward tracks therefore do
not exploit the full 1.140 m radial allocation. A track directed to the outer
corner (r,z)=(1.140,3.150) m instead has η≈1.741. Curvature and displaced origins
modify these paths. Neither example supplies hits or a resolution prediction.

For the physics contract's fixed-total-momentum scan, pT=p/cosh(η). At η=4,
cosh(η)≈27.31; label that scan accordingly. Supplement it later with a separately
specified fixed-pT scan if the physics question requires it; do not mix their
populations when comparing forward and central performance.

## 2. What the first field result says

**INFERENCE — numerical vacuum-model outputs:** the
[retained benchmark](../../validation/DES-004-solenoid-benchmark.json),
`results[candidate.id].checks`, reports the following. Values are rounded here;
the JSON retains calculation identity, quadrature settings and diagnostics.

| Position (r,z) [m] | MAG-01 (Br,Bz) [T] | MAG-03 (Br,Bz) [T] |
| --- | --- | --- |
| (0,0) | (0,3.000) | (0,3.000) |
| (0,3.150) | (0,1.766) | (0,2.743) |
| (1.140,3.150) | (0.871,1.967) | (0.101,2.767) |

These values show that central normalization does not produce a uniform 3 T
tracking field. The axis endpoint is a diagnostic, not a hit on an η=4 track;
the outer corner samples a different angular region. No field value at the
η=4 trajectory is inferred by treating either sample as that trajectory.

**INFERENCE — Lorentz-force geometry:** the relevant local bend is proportional
to `u×B`, not |B| or Bz alone. For a prompt meridional direction in an axisymmetric
field, the azimuthal component is `u_z Br - u_r Bz`. Radial end field can reinforce
or oppose the axial-field contribution depending on trajectory and position.
An almost axial forward trajectory has a small transverse projection even in
a substantial axial field. Only propagation through the vector field, followed
by measurement-response analysis, can establish the usable leverage.

MAG-03's smaller axial falloff in these vacuum samples is not a demonstrated
tracking advantage at equal resource cost. Its larger coil, surrounding
calorimeter steel, material changes and engineering requirements are separate
questions. Both vacuum models omit ferromagnetic response; neither is a physical
detector field map. No uniform-field extrapolation may replace their end fields.

## 3. Tracker handoff to propagation and validation

The following are **NODD DESIGN CHOICE — proposed research requirements; human
approval pending**, extending the common physics contract without selecting
production layers or tolerances.

1. Propagate both charges through the complete vector field to the common
   cylinder/disk fixtures. Record first outward crossings, later recrossings,
   local position/direction, path length, and signed displacement derivatives
   versus q/p. Preserve the fixed-layout result before optimizing surfaces.
2. Report Br/Bz and signed bending between actual crossings, transverse radial
   span and longitudinal span of measured surfaces, and response in their local
   coordinates. A large total path length or unsigned field integral is not
   automatically useful transverse momentum leverage.
3. Retain missing crossings and propagation failures with explicit reasons:
   geometric aperture, curling/turnaround, step/path limit, field-domain failure
   or numerical failure. Keep them in the sample denominator. The diagnostic
   field atlas's masked cells and current-sheet exclusion band are not licensed
   transport holes; define a continuous evaluable domain or record failure.
4. Inspect forward disks, barrel/endcap transitions and displaced/shifted vertices
   separately. Distinguish surface intersections from efficient sensitive hits,
   paired sensors from independent measurements, and fixture intersections from
   real detector overlaps. Measure the consequence of losing a surface before
   asserting redundancy.
5. Validate zero-field and uniform-field controls, charge/field sign conventions,
   map interpolation, numerical step convergence and the propagation domain
   before comparing candidate differences. Agree measurement covariance and
   alignment before any fit-based resolution or charge-significance statement.
6. Treat timing association as a separate interface: retain path length and
   arrival position, then define timing surfaces, particle mass/β assumptions,
   common time origin, efficiencies and time uncertainties. Magnetic bending
   changes path length and which surface is reached; it does not establish
   a timing measurement. No timing layer or timing precision is selected here.
7. Keep field-only, common-material and candidate-dependent material studies
   distinct. Later tracker-only fits must be distinguishable from combined fits
   and any vertex prior. Scattering, energy loss and service material belong in
   the physical interpretation before a detector-performance ranking.

## 4. Next questions and verification

- Does the forward measurement pattern retain sufficient q/p response with the
  inner-solenoid end field, at the intended momenta and vertex distribution?
- Which disk positions/apertures provide useful additional information, and what
  supports/services and timing interfaces would they require?
- How much of any MAG-03 gain survives realistic material and common measurement
  assumptions, and what resource cost buys it?
- Which forward/transition losses are geometric, magnetic or reconstruction
  effects? These require different remedies.

This input inspected the candidate cards, physics contract, source-located tracker
memo and retained benchmark; it did not rerun the field solver or propagate
particles. Straight-line geometry conversions were independently calculated with
Python. All performance questions above remain open. Parent session and dashboard
records cover this bounded contribution; no new source registration is required.
