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

## Prototype choices before field calculation

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
| Straight-leg centre radii [m] | 4.60 / 8.10 | 0.80 / 7.80 |
| Axial coil-centre bounds [m] | −11.8 to +11.8 | ±(6.8 to 11.2) |
| Rounded-corner radius [m] | 1.0 | 0.6 |
| Uniform current-pack section [m] | 0.20 × 0.30 | 0.20 × 0.30 |
| Ampere-turns per coil [MA-turn] | 2.88509 | 1.65132 |
| Averaged winding-pack J [A/mm²] | 48.0848 | 27.5219 |

The three barrel measurement radii are 4.7, 6.2 and 7.7 m. Corresponding disk
centres are at |z|=7.5, 9.0 and 10.5 m, with inner radius 0.70 m and outer radius
R_station+0.250 m. Each barrel ends 0.500 m before its disk centre. All chamber
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
48.1 A/mm² cannot accommodate the cited ATLAS 57 × 12 mm² conductor at 20.5 kA
with the required ampere-turns. Neither ATLAS conductor adoption nor critical
current/temperature margin is established. Turns, circuit current, forces,
quench protection and mechanical support remain to be engineered.

The 500 mm chamber depth is a provisional nODD outline allowance, guided by the
ATLAS two multilayers of 3/4 planes of 30 mm tubes and spacers up to 317 mm. It is not a published ATLAS
whole-chamber depth. Multilayer separation, support depth and installation
clearance need detailed design; 35 μm chamber precision remains a source-based
response assumption, not a performance result of this empty envelope.
