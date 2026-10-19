# DES-039 — Twelve-fold barrel and endcap toroid prototype

- Status: DRAFT
- Created: 2026-10-16
- Scope: isolated magnetic/outline PROTOTYPE; no engineering sign-off or production integration.

## Scope and governing inputs

Human direction: use PR86 to design an ATLAS-like 12-fold toroidal system,
supporting a 3 m first-to-last measurement span, three barrel chamber layers and
three chamber disks per end. Chambers are outline reservations only. Calculate
the joint 3 T solenoid plus barrel/endcap toroid vector field.

PR86 input revision: `e8108f997bb663670db745e57d61d66c2cea9437`.
The [MUON-001 compact-span study](../validation/MUON-001/compact-span/results.md)
gives 1 T / 3 m as a useful standalone comparison and 1.4 T as the stronger
intrinsic-precision reference. These are benchmark fields, not a coil design.
The existing DES026 solenoid and PR81/84/85 HCAL prototypes remain pinned inputs.
[DES004 sizing policy](inputs/DES-004-magnet-sizing-review.md) governs central
field, all-space energy and cold-volume accounting.

## Initial prototype choices (superseded by the coverage amendment)

**NODD DESIGN CHOICE, proposed:** use air-core racetrack coils in meridional
planes: twelve around the barrel and twelve in each endcap. Endcap coil planes
are rotated by half a sector, 15 degrees, relative to the barrel. The source
current density is uniform within each finite winding pack. Three nested
measurement shells have barrel radii 4.7/6.2/7.7 m and corresponding endcap
planes at absolute z=7.5/9.0/10.5 m. Middle measurements are halfway along both
3 m spans. Coil/case exclusions and barrel-to-disk seams must be explicit.

The caps allow mixed barrel/disk trajectories in the transition. They do not
establish complete three-hit acceptance: finite outlines, coil obstructions,
forward apertures and station corners must be checked. No MDT tubes, materials,
readout or chamber internals are designed here.

**FACT about pinned prototype envelopes:** HCAL barrel front/outer apothems are
2.600/4.158 m, corner radius 4.23946 m and half-length 4.4832 m. HCAL endcaps
span absolute z=4.8832–6.4412 m. Source dimensions and unknown interfaces are
retained in MUON-001; the new toroids must preserve space for their services.

## Field and numerical contract

**INFERENCE method:** integrate Biot–Savart and vector potential for finite
closed current packs, using exact straight-segment kernels and refined curved
path/cross-section quadrature. Sum signed Cartesian vectors from the solenoid,
barrel and both endcaps. Export all three vector components and source masks;
the cylindrical map uses one 30-degree periodic sector with a documented
rotation convention. Check the complete central-field cap of 5 T.

Normalize current using signed precision-coordinate sagitta response across the
three actual station crossings. The relevant bending coordinate is the MDT
R–Z precision coordinate; the solenoid's bending in azimuth is recorded in the
full vector field but must not be silently counted as equally precise MDT data.
Stored vacuum energy must include self and mutual contributions over all space,
with finite-pack convergence; no map-volume truncation or omitted self-energy.

The detector contains ferromagnetic HCAL steel. Its grade and B–H curve are not
specified by the prototype. The first numerical map is therefore the **joint
coil field in vacuum**, not a certified installed-detector field or nonlinear
energy solution. Magnetic material, conductor margin, force balance, quench,
thermal and mechanical qualification remain explicit engineering work.

## Deliverables and validation

Retain exact coil, case and chamber-outline parameters; source provenance;
3D/R–Z/transverse drawings; calculated joint field grid; direct-evaluation and
map conventions; field/sagitta acceptance diagnostics; all-space vacuum energy
and cold-volume allocation; numerical controls and independent review.
Final dimensions and numerical results follow the calculations, with discarded
trial inputs distinguished from the final prototype. No computation grants
human design acceptance.


## Calculated proposal

### 2026-10-19 PR87 coverage amendment — DRAFT

The two PR87 comments request true XY/RZ sections of finite occupied coil space,
its interleaving with the chambers, and coverage over the acceptance range.
The reviewed starting point is immutable revision
`71406b09fa2d3fbfa119dba61e436f8fad1d11ac`; its calculations remain reproducible
from that revision. The following proposal supersedes its physical dimensions
before recalculation. It is not human acceptance or construction approval.

**NODD DESIGN CHOICE:** enlarge the barrel coil window to leg centres
4.60/8.80 m and move the three 500 mm chamber envelopes to radii
5.20/6.70/8.20 m. The old 4.85–7.85 m warm window could accommodate only a
2.40 m measurement span after chamber half-depth and 50 mm clearance, so it
could not provide the requested 3 m span at every azimuth. The enlarged window
leaves 100 mm chamber-to-case separation in the straight-leg coil plane
(about 91 mm minimum radial separation after the inner leg's full tangential
extent is included).
Retain three disks per end, at |z|=8.00/9.50/11.00 m, with outer radii
R_station+0.250 m and inner radius 0.700 m. End the corresponding barrels
0.300 m before the disk centres: this leaves 50 mm between their full-depth
faces while closing the nominal centre-surface barrel/disk gaps.

Set each endcap coil's leg centres to 0.70/7.60 m and axial bounds to
|z|=6.80–11.70 m, retaining its 0.60 m corner radius. Moving the first disk past
the front rounded return reduces forward chamber exclusions; the outer endcap
leg stays 100 mm inside the outer barrel chamber's inner face in its coil plane
(about 94 mm including tangential extent). The complete
warm magnet still fits within |z|≤12.05 m, with its radial bound increased to
approximately 9.06 m. HCAL minimum clearances are retained. The smaller endcap
inner leg leaves only about 21 mm between adjacent current packs; shared
cold/warm sleeves are union reservations, not qualified independent vessels.

Keep the 12-fold symmetry, 15-degree staggering, uniform 0.20×0.30 m packs,
0.50×0.60 m warm reservations and signed 1.0/1.6 T response targets. Recompute
currents, all-space energy, energy-sized cold volume and the full joint vacuum
map for the new source geometry. Geometry and field plots must use that same
normalized configuration. Plot actual sections, not projected coil centrelines
presented as slices. Show winding/cold/warm occupancy and retained/excluded
chamber envelopes separately from the numerical field-map guard.

Acceptance is not yet an adopted eta requirement. Compare the old and revised
proposals over 0≤|eta|≤3 using equal azimuth bins, with explicit eta bands and
solid-angle weights. Distinguish nominal three surfaces, three retained chamber
envelopes, interstation coil material, and upstream coil shadows. Remaining
transition/forward exclusions must be visible; a case crossing alone does not
prove failure to reconstruct a muon. These are straight-ray geometric studies,
not reconstruction efficiency or full material transport.

The [calculation report](../validation/DES-039/results.md) contains the dimensions,
current normalization, field grid, energy accounting and limitations. The
[3D outline](../validation/DES-039/geometry-3d.png),
[R–Z and transverse envelopes](../validation/DES-039/geometry-rz-xy.png) and
[joint field slices](../validation/DES-039/joint-field.png) show the prototype.
The [source dossier](../validation/DES-039/sources.md) distinguishes primary ATLAS
facts from nODD choices. The endcap reference is raised to 1.6 T after calculating
the barrel-return cancellation in the transition; this is a nODD working point,
not an ATLAS operating-field claim.

| Quantity | Barrel toroid | Each endcap toroid |
|---|---:|---:|
| Coils | 12 | 12 |
| Coil-plane azimuth | 30° k | 15° + 30° k |
| Straight-leg centre radii [m] | 4.60 / 8.80 | 0.70 / 7.60 |
| Axial coil-centre bounds [m] | −11.8 to +11.8 | ±(6.8 to 11.7) |
| Rounded-corner radius [m] | 1.0 | 0.6 |
| Uniform current-pack section [m] | 0.20 × 0.30 | 0.20 × 0.30 |
| Ampere-turns per coil [MA-turn] | 2.98534 | 1.74540 |
| Averaged winding-pack J [A/mm²] | 49.7557 | 29.0899 |

The three barrel measurement radii are 5.2, 6.7 and 8.2 m. Corresponding disk
centres are at |z|=8.0, 9.5 and 11.0 m, with inner radius 0.70 m and outer radius
R_station+0.250 m. Each barrel ends 0.300 m before its disk centre. All chamber
reservations are 0.500 m thick; exported geometry consists only of their clipped
boundaries. There are three disks **per side**, six total. The first-to-last
radial/axial spans are each 3 m, with two 1.5 m station intervals. Actual path
length depends on eta; this is the interpretation of the requested 3 m gap.

The warm coil-following reservation is 0.50 m in-plane by 0.60 m tangential.
It leaves 110.5 mm minimum radial clearance to the pinned HCAL barrel corner
and 108.8 mm to the HCAL endcap back face. The chamber cutouts reserve their full provisional depth around coil exclusions. These are envelope clearances,
not a closed service-routing budget. Endcap warm sleeves overlap at the inner
legs and therefore represent a **shared union reservation**. A pressure vessel,
thermal shield and supporting structure have not been designed; a filled
annular ATLAS endcap vessel cannot be substituted without relocating chambers.

**NODD DESIGN CHOICE:** this is an air-core racetrack topology inspired by ATLAS,
with a separate, unqualified conductor/insulation assumption. The barrel pack's
49.8 A/mm² cannot accommodate the cited ATLAS 57 × 12 mm² conductor at 20.5 kA
with the required ampere-turns. Neither ATLAS conductor adoption nor critical
current/temperature margin is established. Turns, circuit current, forces,
quench protection and mechanical support remain to be engineered.

The 500 mm chamber depth is a provisional nODD outline allowance, guided by the
ATLAS two multilayers of 3/4 planes of 30 mm tubes and spacers up to 317 mm. It is not a published ATLAS
whole-chamber depth. Multilayer separation, support depth and installation
clearance need detailed design; 35 μm chamber precision remains a source-based
response assumption, not a performance result of this empty envelope.
