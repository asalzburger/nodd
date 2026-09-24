# DES-004 — Magnetic-field expert review response

**2026-09-24 sizing amendment:** [Current constraints and dimensions](DES-004-magnet-sizing-review.md)
supersede earlier winding/vessel and MAG-03/04 radial allocations below.
Earlier numerical results remain historical; complete-system engineering is open.

- Date: 2026-09-22; status: DRAFT / isolated PROTOTYPE; no design sign-off.
- Reviewer: `mgtmentink`, magnetic-field expert identified by the user.
- Evidence: [three-part PR #6 comment](https://github.com/asalzburger/nodd/pull/6#issuecomment-5774198540).
- Inspected PR head: `2530c5543da6b2c474ccadc6c67ce431d69d2e0f`. The general
  comment does not itself identify an exact reviewed commit; this is the head
  inspected when responding, not an assertion of the reviewer's target revision.
- Parent: [DES-004](../DES-004-magnetic-configurations.md); related: DES-003,
  ADR-006, ADR-003 and [muon follow-up issue #9](https://github.com/asalzburger/nodd/issues/9).

## 1. Vacuum-vessel reservation and radius scaling

**FACT about the prior project prescription:** the
[inner-solenoid space budget](DES-003-solenoid-space-budget.md) allocated a
0.40 m radial assembly: 0.10 m inner cryostat/interfaces, 0.15 m cold assembly,
0.10 m outer cryostat/support interfaces and 0.05 m unassigned margin. Its
0.25 m allowance at each end was also a planning choice. The
[outer-solenoid input](DES-004-system-architecture.md#3-mag-03-explicit-outer-coil-amendment)
reserved 0.50 m radially and 0.30 m beyond each winding end without a component
decomposition or radius-scaling calculation.

**Answer:** neither complete enclosure was calculated as a vacuum vessel.
The quoted widths include vacuum/thermal gaps, shields, supports and interfaces;
they are not metal wall thicknesses. There is **no established vacuum-vessel
scaling with radius** behind 0.40 m versus 0.50 m. They remain unverified space
reservations, and their adequacy is an open engineering question.

**INFERENCE — scope of the earlier scaling:** `p = B²/(2μ0)` and
`t = pR/σ_allow` give `t ∝ B²R` for an ideal thin load-bearing cylinder under
magnetic hoop loading at fixed allowable stress. Applying this to entire
historical cold-mass widths was only a crude sizing proxy for the cold assembly.
It is not a vacuum-shell stability calculation and supplies no pressure-vessel
wall, end-cover or safety-factor prescription. It must not be extended to the
whole cryostat or used to certify the larger outer coil.

**FACT anchors:** SRC-ATLAS-SOLENOID-2007, abstract and §I/PDF1, describes a
45 mm cold mass and a shared calorimeter cryostat; SRC-CMS-JINST-2008,
§2.1/PDF33 and Table 2.1/PDF35, distinguishes the cold mass from the vacuum
enclosure. These are construction examples, not nODD scaling laws. Source
identities and public links remain in the [manifest](../../../reference/manifest.yaml).

**NODD DESIGN CHOICE — proposed engineering follow-up:** separately size the
inner/outer warm shells and annular end closures using their actual pressure
differences and load directions, unsupported lengths/stiffeners, material
properties, fabrication imperfections, joints and penetrations. Check stability,
stress/deflection, support reactions, cooldown movement, insulation/shield gaps
and cryogenic/current routes. Agree engineering criteria with the expert before
claiming that either host fits. No new wall thickness or guaranteed upper bound
is inferred in this response; a failed fit requires an explicit envelope amendment.

## 2. Homogeneous current in a finite winding

**FACT about the old calculation:** `solenoid.py` integrates a uniform azimuthal
surface current `Kφ = NI/(2h)` at one radius. It is homogeneous in z and azimuth,
but has zero radial thickness; it did not model a finite winding-pack `Jφ`.
The old benchmark and atlas remain historical numerical controls.

**NODD DESIGN CHOICE — unsigned prototype amendment:** use the following
rectangular winding cross-sections with constant azimuthal **winding-pack
average** `Jφ` throughout each pack. All coordinates are metres. This is an
effective current representation, not a material or cable prescription.

| Main winding / applicable candidates | Radial winding bounds | Full winding length | Retained complete host | Allocation rationale |
| --- | --- | --- | --- | --- |
| Inner / MAG-01, MAG-02, MAG-05 | 1.34–1.44 | 6.60 | r=1.24–1.64, absolute z≤3.55 | Use the earlier explicit 0.10 m winding scenario; leave 1.44–1.49 for cold support/cooling. Retain the other DES-003 allowances. The winding midpoint moves from the old 1.415 m sheet to 1.390 m. |
| Outer / MAG-03, MAG-04 | 4.40–4.60 | 13.00 | r=4.30–4.80, absolute z≤6.80 | Trial 0.20 m pack about the old 4.50 m sheet; 4.30–4.40 inner cryostat/interfaces, 4.60–4.70 cold support/cooling, 4.70–4.80 outer cryostat/interfaces. No unassigned radial margin remains. |

The outer split supplies an explicit study input, not a derived radius scaling
or proven structure. Neither split establishes conductor fill, permissible
current density, critical-current margin or quench protection. Pack current is
spread through the pack's homogenized cross-section; strand current density
requires conductor, stabilizer and insulation fractions. Current is zero in the
separately reserved supports, vacuum and cryostat. The same value of J is not
imposed between the two different coils: each constant is independently
normalized to +3 T at the origin **in vacuum**. No longitudinal grading or
separately tuned radial layers are used.

**INFERENCE — derivation:** for pack radii `a≤ρ≤b` and `−h≤ζ≤h`, a slice
`dρ dζ` carries azimuthal loop current `dI = Jφ dρ dζ`. Integrating Biot–Savart
over ρ, ζ and azimuth φ gives, at observation `(r,0,z)`,

```text
D² = ρ² + r² − 2ρr cosφ + (z−ζ)²
(Br, Bz) = μ0 Jφ/(4π) ∫a^b dρ ∫−h^h dζ ∫0^2π dφ
           (ρ cosφ (z−ζ), ρ²−ρr cosφ) / D³
NI = Jφ (b−a) 2h
Bz(0,0) = μ0 Jφ h [asinh(b/h) − asinh(a/h)]
```

There is no extra radial weighting of loop current: the ρ factor from the
cylindrical volume element is already present in the cross-product numerator.
The independent closed-form axis integral is `μ0 Jφ [F(z+h)−F(z−h)]/2`, where
`F(u)=u[asinh(b/|u|)−asinh(a/|u|)]` with continuous value `F(0)=0`.
Units are metres, tesla, A/m² and ampere-turns. The diagnostic constant is
`μ0≈4π×10⁻⁷ H/m`, as in the historical control.

Implementation: [winding definitions](../../../tools/magnetic_study/windings.json),
[integrator](../../../tools/magnetic_study/finite_winding.py) and
[independent tests](../../../tools/magnetic_study/test_finite_winding.py).
The radial Gauss–Legendre integral reuses the old sheet's z/azimuth quadrature
kernel; each radial weight carries `d(NI)=Jφ 2h dρ`. Pack normalization uses
the analytic central formula, not a fitted quadrature value.

Numerical validation compares 4×48×64, 8×96×128 and 16×192×256 orders in
radius/z/azimuth at the six historical points, using the existing test setting
`1e-6 T + 1e-5 norm(B_fine)` and `1e-10 T` axis agreement. Tests also cover
reflection, current reversal, the thin-pack limit, vacuum Maxwell identities,
the far-field dipole moment and invalid/excluded points. The 0.12 m numerical
guard now surrounds the **whole winding pack**, not the old sheet. Interior and
near-pack evaluations are rejected rather than silently presented as accurate.
These checks do not validate transport throughout the full detector volume.

**INFERENCE — executed numerical results:** inner J=25.9051 A/mm² and
NI=17.0973 MA-turn; outer J=14.5181 A/mm² and NI=37.7469 MA-turn. All twelve
sampled checks passed. At (r,z)=(1.14,3.15) m the inner (Br,Bz) is
(0.89553,1.98871) T; outer (0.10053,2.76727) T. The inner change from the old
sheet includes its explicit 25 mm inward midpoint shift as well as finite
thickness; it must not be attributed to thickness alone. These are numerical
inferences with unassessed physical-model uncertainty, not measured fields.

Retained results: [finite-winding benchmark](../../validation/DES-004-finite-winding-benchmark.json)
and [axis comparison](../figures/DES-004-finite-winding-axis.png). Complete field
maps for MAG-02/04 still require nonlinear iron, and MAG-05 requires specified
discrete toroid windings. Any subsequent toroid calculation must likewise state
homogeneous pack current and explicit geometry; no toroid field has been
invented here. Adding steel/toroids requires re-solving and re-normalizing the
full system. Vacuum values are not assigned as physical currents for those systems.

## 3. Withdraw the active-return candidate

**NODD DESIGN CHOICE — review-directed:** interpret the request to disregard
the active-solenoid configuration as **MAG-06**, the only candidate with active
return/shielding coils. Remove it from the active candidate list, comparison
drawings and next-work recommendations. MAG-01 through MAG-05 remain under study;
ordinary main solenoids and MAG-05 toroids are not removed by this interpretation.
This is a scope withdrawal, not proof of physical impossibility or sign-off of
the remaining designs.

The old MAG-06 card, figures and source ledger remain explicitly historical.
`muon-layouts.json` keeps its inputs in `withdrawn_options`; normal generation
uses only `options`. Earlier six-option artifacts are recoverable at the
inspected head above. The current five-option allocation report records finite
winding containment; the reference E1-R2 and all external candidate host bounds
remain unchanged. Issue #9's earlier six-option discussion is superseded by this
scope decision for further work.

## Review status

The response supplies an explicit answer and numerical amendment, not closure
on behalf of the reviewer. Vacuum-vessel engineering, actual conductor and
protection design, nonlinear/3D field solutions and muon performance remain open.
No formal lifecycle state, design approval or production geometry is advanced.
