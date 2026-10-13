# DES-004 — Energy-based cold-mass and vessel sizing

- Date: 2026-09-24; status: DRAFT / isolated PROTOTYPE, no design sign-off.
- Reviewer: `mgtmentink`; [new constraints](https://github.com/asalzburger/nodd/pull/6#issuecomment-5809476152).
- Inspected PR head: `35047957ea565ea0fca53e57c32379d5f0e5fc91`. The issue comment
  does not identify its reviewed commit; do not infer an exact human target.
- Supersedes the numerical winding/enclosure choices in the
  [2026-09-22 response](DES-004-magnet-expert-review.md), which remains historical.
- Parent: [DES-004](../DES-004-magnetic-configurations.md); related ADR-006 and issue #9.

## Executive response

The review constraints are now persistent in [AGENTS.md](../../../AGENTS.md#magnetic-sizing-constraints),
[a central policy file](../../../tools/magnetic_study/sizing-policy.json), the
sizing/field/layout validators and CI. All five active candidates use updated
main-coil bounds and drawings. MAG-06 remains withdrawn.

The finite-winding calculation now supplies **stored energy of the complete
vacuum field**, including fringe/return space, rather than the previous
uniform-bore proxy. Cold-mass thickness and winding current are solved together.
At 3 T, the inner/outer energy is about **132.576 MJ / 3624.582 MJ**. The resulting
vessel outer radii are **1.559419 m / 5.400309 m**. Outer-solenoid muon hosts
therefore move outward by **0.600309 m**, preserving their radial budgets and
0.15 m vessel-to-host gap. This is an explicit research-envelope amendment;
DES-003's reference remains unchanged.

**Open interpretation:** the expert's formula contains undefined `RCM` in
`RVo = RCMo + 1.75 (RCM − RVi)`. This implementation provisionally means
`RCM = RCMi`, i.e. the inner cold-mass/vessel separation. Confirmation was
requested; no human confirmation is inferred. If another radius was intended,
regenerate the vessel and downstream allocations before acceptance.

## Axial lengths: what was actually assumed

**FACT S-F01, project history:** the original 6.60 m / 13.00 m current lengths
came from the inner/outer field study hypotheses. Vessel full lengths 7.10 m /
13.60 m added 0.25 m / 0.30 m at **each** end. These were explicit planning
reservations, not derived end-cover, suspension, thermal-contraction or lead-exit
requirements. Previous files did not separately engineer a cold-mass axial extent.

**NODD DESIGN CHOICE S-C01, proposed; approving humans: none:** make the provisional
closure explicit: `Lcold = Lwinding`; `Lvessel = Lcold + 2 gend`, with the retained
end allowances above. No new radial rule determines an axial length. The annular
cold-mass volume is `pi (RCMo² − RCMi²) Lcold`; it excludes the vessel and vacuum
gaps. This is a bulk geometric cold-assembly volume, not an aluminium mass or
conductor volume. Axial cold support/end turns not represented by this straight
annulus require a revised volume and field model; do not claim they fit in the
allowance without engineering. The dimensions are study coordinates, without a
warm-to-cold contraction or manufacturing-tolerance calculation.

Required next input: winding end/lead geometry, cold support and thermal shield
extensions, axial restraint, cooldown motion, warm end closures and routes.
The earlier lengths remain conditional until those inputs are reviewed.

## Constraint and provenance contract

**FACT S-F02:** SRC-NODD-MAGNET-REVIEW-20260924 records the expert's requested
coefficients, energy/volume relation, central cap and preferred range. The
comment attributes the fits to ATLAS/CMS technical designs. This response does
**not** independently reconstruct those fits or claim an experimental uncertainty.
The constraints are review-directed project rules, not universal magnet laws.

**NODD DESIGN CHOICE S-C02, review-directed:** apply

```text
RCMi = 1.065 RVi + 0.0072 m
U = (30 × 10^6 J/m³) pi (RCMo² − RCMi²) Lcold
RVo = RCMo + 1.75 (RCMi − RVi)  [provisional symbol interpretation]
|Btotal(0)| ≤ 5 T; preferred free-bore study range 1–4 T
```

All current main-coil controls use +3 T. The cap is enforced for either polarity,
rejects nonfinite values, and applies to the **total** central field when further
magnets/iron are added. A central cap is not a peak conductor-field criterion or
a demonstrated NbTi current/temperature/load margin. The expert's preference does
not establish a prohibition outside 1–4 T when still within the hard cap.

**NODD DESIGN CHOICE S-C03, proposed; approving humans: none:** preserve the earlier
2:1 radial winding/support split: the homogeneous winding starts at RCMi and
occupies two thirds of the cold thickness; the outer third reserves cold support
and cooling. This closes an otherwise underdetermined geometry/energy problem.
It is not a conductor fill factor or optimized mechanical design. J is uniform
through the finite winding pack and normalized analytically to the requested
central field at every iteration. Inner J rises to 49.643 A/mm²; this consequence
needs conductor/protection review, not an implicit claim of feasibility.

## Stored energy and coupled solution

**FACT S-F03:** SRC-FITZPATRICK-MAGNETIC-ENERGY, Eqs. 961–966, derives the vacuum
identity `U = 1/2 integral J·A dV = integral B²/(2 mu0) dV` over all space. No
uniform-field approximation is made by that identity. For nonlinear steel, use
the appropriate constitutive magnetization/energization solution; the vacuum
identity cannot certify the installed detector energy.

**INFERENCE S-I01:** for a constant azimuthal J in `a≤r≤b`, `−L/2≤z≤L/2`, the
Neumann loop-pair integral reduces to

```text
d² = (r − r')² + 4 r r' sin²(phi/2)
G(d) = L asinh(L/d) − hypot(L,d) + d
U = mu0 J² integral_a^b dr integral_a^b dr' r r'
              integral_0^pi cos(phi) G(d) dphi
J = B0 / {mu0 (L/2) [asinh(2b/L) − asinh(2a/L)]}
```

Here `G = integral_0^L (L−s)/sqrt(d²+s²) ds` performs both axial source integrals
analytically; reflection performs half the azimuth integral. The factor 1/2 in
energy is retained in the derivation. The remaining logarithmic coincidence is
integrable; endpoint-free Gauss–Legendre quadrature and refinement avoid filament
self-energy insertion. This computes the all-space energy without cutting off a
field map, excluding the winding volume or reusing the field solver's near-pack
mask. The vacuum current and geometry are identical to those in the field tool.

Solve `U(RCMo) − 30 MJ/m³ × Vcold(RCMo) = 0` by bracketed bisection; at each step
change winding thickness under S-C03 and re-normalize constant J. Nominal radial/
azimuth orders are 48/192. Compare 24/96 and 96/384; the declared numerical screen
is 5e-4 relative refinement, root residual 1e-8. These are numerical tolerances,
not engineering safety margins. Retained relative refinement is 3.10e-6 / 4.19e-6.

Tests independently check the analytic axial integral, exact infinite-solenoid
radial field-energy limit, B² and geometric-volume scaling, polarity invariance,
root closure, refinement, hard-field rejection and invalid geometry. The generic
finite-winding field checks remain separate. No full-volume transport map is
claimed.

## Executed geometry update

All numerical results below are **INFERENCE S-I02**, conditional on S-C01–03.
Coordinates are metres, energy MJ, J A/mm². Rounding here is for display; JSON
retains full precision.

| Main-coil family | RVi | RCMi | RCMo | RVo | Lcold / Lvessel | U [MJ] | Vcold [m³] | J |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Inner: MAG-01/02/05 | 1.240000 | 1.327800 | 1.405769 | 1.559419 | 6.600 / 7.100 | 132.576 | 4.419216 | 49.6432 |
| Outer: MAG-03/04 | 4.300000 | 4.586700 | 4.898584 | 5.400309 | 13.000 / 13.600 | 3624.582 | 120.819401 | 14.1592 |

Winding outer radii: 1.379779 / 4.794623 m; total ampere-turns:
17.030759 / 38.272374 MA-turn. The inner radial vessel reservation shrinks by
0.080581 m; the calorimeter is **not** moved to consume the freed space. The
inner-vessel-to-ECal gap becomes 0.140581 m and remains unassigned study space.

| Active option | Main sizing applied | Muon barrel r [m] | Wide endcap outer r [m] | Outstanding full-system sizing |
| --- | --- | --- | ---: | --- |
| MAG-01 | Inner vacuum coil | 4.350–6.762 | 7.000 | Installed calorimeter/support steel and structural/conductor design |
| MAG-02 | Inner vacuum coil | 4.350–7.500 | 7.500 | Nonlinear return-iron and calorimeter field/energy; re-normalize and resize |
| MAG-03 | Outer vacuum coil | 5.550309–8.100309 | 8.100309 | Installed calorimeter/support steel and structural/conductor design |
| MAG-04 | Outer vacuum coil | 5.550309–10.600309 | 10.600309 | Nonlinear return-iron and calorimeter field/energy; re-normalize and resize |
| MAG-05 | Inner vacuum coil | 4.350–9.000 | 9.000 | Explicit toroid windings, coupled fields/energy and suitable per-magnet cold-volume accounting |

**NODD DESIGN CHOICE S-C04, proposed; approving humans: none:** translate MAG-03/04
barrel radial budgets and trial steel bands outward by the same 0.600309 m; grow
the upstream endcap outer radius to 5.400309 m and downstream outer radius as
shown. Keep the 0.4 m inner apertures, axial starts and ends, calorimeters and
tracker fixed. This preserves existing radial station/service reservations and
the 0.15 m step-to-barrel gap while avoiding a vessel clash. It increases the
overall detector radius and resource burden; no chamber placement or return-flux
closure follows merely from this translation. All five composite layouts pass
positive-intersection and sized-winding/vessel-containment checks.

## Evidence, reproducibility and remaining gate

- [Energy/size results](../../validation/DES-004-magnet-sizing.json),
  [current windings](../../../tools/magnetic_study/windings.json),
  [current composite allocations](../../../tools/magnetic_study/muon-layouts.json).
- [Updated field benchmark](../../validation/DES-004-sized-winding-benchmark.json)
  and [five-layout check report](../../validation/DES-004-muon-envelope-proposals.json).
- [Code and commands](../../../tools/magnetic_study/README.md),
  [source catalogue](../../../reference/manifest.yaml).

![Sized cold masses, vessels and amended muon hosts](../figures/DES-004-muon-envelopes-comparison-rz.png)

The 2026-09-22 winding benchmark/figure remains unchanged historical evidence;
the old composite report and drawings remain in Git at the inspected PR head.
The reference DES-003 geometry and withdrawn MAG-06 are not silently regenerated.
Future active proposals must use these constraints, with missing complete-field
solutions reported as blockers rather than passing from a vacuum surrogate.

Requested expert confirmation: the `RCM` interpretation, axial allowance and
2:1 winding/support closure, followed by conductor margin and full-system energy
calculations. Nothing here advances a document to SIGNED OFF or closes review
conditions on the expert's behalf.
