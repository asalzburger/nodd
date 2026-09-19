# DES-006 input — PhysVal assessment of inclined strip modules

- Date: 2026-09-18.
- Status: **DRAFT / PROTOTYPE**; independent AI-assisted assessment, no human sign-off.
- Governing proposal: [DES-006](../DES-006-first-tracker-layouts.md).
- Baseline evidence and covariance limitations: [original PhysVal input](DES-006-physval.md).
- Technical proposal: [TrackTech inclined-row assessment](DES-006-inclined-tracktech.md).
- Scope: the review request for double-sided strip accounting and a more aggressive inclined alternative. This assessment does not answer the comment directed to Noemi.

## Comparison contract

**NODD DESIGN CHOICE — proposed, no approving humans:** keep A as the controlled
reference; test C by inclining the outer portions of its six strip barrel station
families. Keep pixels, endcap disks, response scenarios, field scenarios and
normal material allowances unchanged. Inclination must be assessed together
with its vertex coverage, sensor area and overlaps. A lower normal-incidence
path at one vertex alone is insufficient to select a layout.

The geometrical representation is an axisymmetric set of inclined row rings.
Each ring is the surface of revolution of a finite straight segment in the
`(r,z)` plane. This represents the envelope of flat module rows, not an actual
continuous conical sensor. It omits azimuthal segmentation, inactive edges,
faceting and routing. Those omissions prevent a buildability or tracking
acceptance claim. All dimensions and inclinations remain proposed project
choices, not measured technology capabilities.

## Double-sided long-strip accounting

**INFERENCE — PV6-I01:** from the [A/B layer catalogue](../DES-006-layouts.json),
each candidate has two long-strip barrel pair-reference surfaces and twelve
signed endcap pair-reference surfaces: **14 pair surfaces and 28 silicon faces**.
Their ideal pair-reference area is `55.9304023304 m²`; counting both faces gives
`111.860804661 m²` of ideal long-strip sensor area before tiling and overlaps.
A count of globally distinct surfaces is not the number crossed by one track.

At the central origin ray, A has four pixel stations, four strixel stations and
two stereo-pair stations: **10 stations, 12 sensor-face crossings, and 20 scalar
measurement coordinates** under C04's ideal response. Each pixel or strixel
station provides two coordinates on one sensor; each long-strip pair supplies
two scalar measurements on two sensors. The long-strip pair's effective
coordinate errors already derive from those two scalar measurements. Duplicating
that effective two-coordinate response would double-count information.

The C05 `2% X0` normal allowance belongs to the whole long-strip pair. It is
counted once per physical paired-module crossing; it is not doubled because
there are two faces. Conversely, sensor area must include both faces. No
silicon thickness, mass or engineering budget follows from this effective
material allowance.

**NODD DESIGN CHOICE — comparison convention:** C may overlap adjacent rows in
the same parent station family. Report both all physical module crossings and
the number of distinct parent station families crossed. The latter allows a
controlled coverage comparison with A. Two overlapped modules can provide
additional measurements, but they do not create a new radial station family;
all their physical material and sensor area must nevertheless be counted.
Neither count is a reconstructed-hit efficiency.

## Independent analytical checks

**INFERENCE — PV6-I02:** let a meridional ring segment have endpoints
`(r1,z1)` and `(r2,z2)`, length `L=hypot(r2-r1,z2-z1)`, and unit normal
`n=(nr,nz)=((z2-z1)/L, -(r2-r1)/L)`. Its sign does not affect incidence.
A straight ray from the beam axis obeys `z=zv+r*sinh(eta)`. The candidate
intersection is

```text
r = [nr*r1 + nz*(z1-zv)] / [nr + nz*sinh(eta)]
z = zv + r*sinh(eta)
cos(incidence) = abs(nr + nz*sinh(eta)) / cosh(eta)
ring area = pi * (r1+r2) * L
path X/X0 = normal X/X0 / cos(incidence)
```

Require a forward radius, a point within the finite segment, and a nonzero
incidence cosine; a line lying in the surface is not a finite material
crossing. The area is the exact surface-of-revolution area, not its axial or
radial projection. It must be summed over both detector ends; long-strip
sensor area includes both faces.

For a uniform-field first-outward helix, parameterize transverse arc length
`sT` with `rho=pT/(0.299792458*abs(B))`:

```text
r(sT) = 2*rho*sin(sT/(2*rho))
z(sT) = zv + sT*sinh(eta)
cos(incidence) = abs(nr*cos(sT/(2*rho)) + nz*sinh(eta)) / cosh(eta)
```

Find roots of the surface equation before the first radial turning point;
then apply the finite segment bounds. These equations show why a cylinder or
disk incidence correction cannot be reused unchanged for a tilted row.

The useful limiting checks are:

1. A vertical segment recovers the cylinder crossing and incidence. A horizontal
   segment recovers the disk crossing and incidence.
2. A ring normal aimed at the origin has unit incidence cosine for the straight
   origin ray passing through its center; its material path equals its normal
   allowance. This benefit changes with vertex position and curvature.
3. Reflection of ring z coordinates, eta and vertex z preserves radius, path
   material and crossing count. Reversing field sign preserves this ideal
   axisymmetric geometry.
4. Segment edges and small steps on either side identify clipping mistakes;
   intervals between rows need dense eta scans at all stated vertex probes.
5. Overlap additions increase area and material even if the distinct parent
   station count does not change. Every retained ring endpoint must stay inside
   the inherited host and be checked against neighboring ideal surfaces.

These are numerical consistency checks, not tolerances on an approved detector.

## Performance interpretation and recommendation

Tilting can reduce the path through a strip row at oblique incidence and shorten
its area for a given solid-angle coverage from the chosen origin. Extending rows
to cover displaced vertices consumes some of that area saving and can add
multiple physical crossings in overlap regions. A design-wide statement must
therefore quote area, coverage minima and material profiles together, including
unfavorable eta and vertex bins.

The extra practical costs are changed module orientations and supports, more
row boundaries and alignment transforms, possible services through overlap
regions, and finite-module clearance constraints. Their magnitude is unknown;
an ideal area ratio is neither a monetary cost ratio nor a power estimate.
Keeping the same reusable sensor/module types is plausible as a design aim,
but a meridional ring model does not establish that those modules can be tiled
without gaps or clashes.

**INFERENCE — PV6-I03:** C's unchanged pixel system cannot repair A's pixel
transition weakness or extend its far-forward pixel lever arm. Improved strip
incidence is a separate benefit. Existing A/B IdRes covariance output supports
only its original cylinder/disk layouts. C must not inherit those covariance
curves, be silently flattened into them, or be claimed to have better momentum
resolution from a lower thin-layer material sum alone. An explicitly stated
measurement-only transverse control could test one information component; it
would not validate scattering, the rotated second coordinate, or reconstruction.

**NODD DESIGN CHOICE — recommended next step, no approving humans:** retain C
as an aggressive module-orientation prototype alongside A. Advance it to finite
module tiling and realistic material/support accounting if it preserves the
stated coverage screen with an attractive area/material trade-off. Keep A as
the control and keep B's forward pixel question separate. A production choice
requires human physics priorities, validated interfaces and the usual design
review; this assessment grants none of those approvals.

## Provenance and verification status

The formulas and counts above are **INFERENCE** from the stated ideal geometry,
C04/C05 and the catalogue. No new external detector parameter or source is
introduced. The existing catalogue provenance and source manifest remain
applicable. Numerical geometry settings for C belong to its TrackTech proposal
and are **NODD DESIGN CHOICE**, with human approval pending.

The long-strip surface inventory, cylinder/annulus areas and central scalar
measurement accounting were recomputed independently with Python's standard
library; no shared geometry function was imported. C-specific checks used the
independently reconstructed recipe: six row centers
at `|z|=0.65,0.75,...,1.15 m`, capped `45 degree` normals, origin-angular
boundaries, and tangent extensions of `0/5/10 mm`. These are C07's proposed
settings and two explicitly named numerical comparison controls, not detector
requirements. Temporary diagnostics ran with Python 3.14.7, no random sampling,
on starting revision `243b138ffd78844c020604e103f5c2a6e893d988` with the worktree
containing the new prototype. Initial temporary diagnostics were subsequently
retained as the [independent audit script](../../../tools/tracker_layout/audit_inclined.py).
The executed command `python3 -B tools/tracker_layout/audit_inclined.py` generated
[structured independent evidence](../../validation/DES-006-inclined-independent.json),
including input, audit-code and comparison-code hashes, exact interpreter command,
units, controls and numerical differences. The retained code independently
constructs the row endpoints and area ledger for the straight-ray scan; it imports
the shared ring function only as the finite-field comparison target.

### Independent straight-ray results

**INFERENCE — PV6-I04:** the closed-form intersection above was evaluated on
8,001 signed eta points at step `0.001` for each of the three specified vertices,
for each extension control. It did not import the shared geometry functions.

| Tangent extension per edge | Origin bins losing a parent station vs A | Bins losing a parent station at each shifted vertex | Maximum station loss at a shifted vertex |
| --- | --- | --- | --- |
| 0 mm control | 0 | 393 | 3 |
| 5 mm control | 0 | 1, at signed eta matching the vertex sign with magnitude 0.809 | 1 |
| 10 mm C proposal | 0 | 0 | 0 |

The global minimum alone misses this issue: each control still has the same
minimum of seven stations at the origin and six at either shifted vertex.
The 10 mm extension therefore has a coverage rationale beyond the origin
construction, but this sampled screen does not prove continuous hermeticity.

Independent full-system areas, including unchanged endcaps, agree with the
[retained inclined report](../../validation/DES-006-inclined-screen.json):

| Ideal sensor area [m²] | A | C | C/A change |
| --- | --- | --- | --- |
| Pixel | 4.901984 | 4.901984 | unchanged |
| Strixel | 43.953394 | 39.938846 | -9.13% |
| Long strip, **both faces** | 111.860805 | 109.665176 | -1.96% |

The corresponding barrel-only area benefits are larger because the unchanged
endcaps dilute the totals; TrackTech reports those separately. The small total
long-strip saving is particularly vulnerable to extra support or overlap costs.

The independently calculated zero-field origin material at eta 1.5 falls from
`26.071834% X0` in A to `22.203975% X0` in C. At the same eta with vertex
`+0.150 m`, it instead rises from `26.409990%` to `27.326185%`: C has fourteen
physical module crossings from twelve parent families, versus A's eleven.
Over the dense straight-ray grid, the largest C-minus-A increase is
`3.780469` percentage points at a shifted vertex. These are sums of the
provisional local allowances, not complete detector budgets.

### Independent finite-field implementation audit

The audit derived each normal directly from the stored segment endpoints and
used a Newton solution of the helical surface equation, independently of the
shared bracket/bisection implementation. It compared all 72 rings at eta
`-4..4` in steps of `0.1`, vertices `-0.150/0/+0.150 m`, pT `1/10/100 GeV`
and field `0/2/3/4 T`: **209,952 queries, 3,456 finite crossings, zero crossing
presence disagreements**. Maximum absolute differences were `2.22e-15 m` in
radius, `1.33e-15 m` in z, `2.66e-15 m` in path and `3.55e-15` percentage
points in material. These are observed numerical differences, not approved
physical tolerances. The audited configuration SHA-256 is
`71f197722075702378ab893d108f7a6e1b95580359e4b030b13f8dbdfc4ca1c0`.

The first temporary Newton diagnostic lacked the forward longitudinal-reach
check and produced a spurious wrong-endcap solution. Adding that domain check
to the independent diagnostic removed the discrepancy; the shared ring code
already excluded it. When retaining the audit, an explicit Newton convergence
check also exposed targets unreachable before the first radial turning point.
The retained audit now rejects those targets analytically before iteration.
The complete retained run passed after these diagnostic domain corrections;
the numerical differences above are unchanged. These corrections affected the
independent audit, not the shared geometry implementation.

The coordinating retained scan uses finite fields, signed eta step `0.01` and
the same three vertices and pT values. It reports no sampled parent-station loss
against A, and C/A material ratios ranging from `0.7794` to `1.2371` across its
bins. These retained outputs were inspected; the independent numerical audit
above tests the ring solver, and the denser straight-ray calculation provides
a separate check. Neither process executes a scattering fit, module-aware ACTS
propagation, DD4hep/Geant4 construction, or reconstructed tracking performance.
