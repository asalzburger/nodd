# DES-040 — Modular muon chambers, connected support frame and feet

- Status: DRAFT
- Scope: isolated chamber and warm-frame PROTOTYPE
- Created: 2026-10-19
- Governing magnetic input: PR87, `fe372194038ed2af9617c27defffba09ae6d683f`
- Human engineering acceptance: none

## Requested follow-up

The user requests a new PR following the PR87 reviews
[4313407952](https://github.com/asalzburger/nodd/pull/87#discussion_r4313407952)
and [4313456506](https://github.com/asalzburger/nodd/pull/87#discussion_r4313456506):
rectangular barrel chambers, trapezoidal endcap chambers, a realistic layout
covering the full solid angle, and a frame with feet connecting and holding the
coils. This proposal is stacked on PR87 and does not amend its magnetic system.

**FACT about recorded input:** [DES-039](DES-039-twelvefold-toroid.md) fixes
12 barrel and 12 coils per endcap, their finite winding/cold/warm reservations,
currents, and the joint solenoid/toroid vacuum field. Retain those exact bytes.
The nominal three station radii are 5.2/6.7/8.2 m and disk planes are at
|z|=8/9.5/11 m, with provisional 500 mm chamber depth. These are unsigned project
choices, not measured ATLAS dimensions. The present study replaces the ideal
continuous chamber shells by individually identified planar chamber envelopes.

## Geometry contract before implementation

**NODD DESIGN CHOICE, proposed:** represent each chamber by one whole finite
convex prism: a rectangular face in a tangential/longitudinal barrel plane, or
an isosceles trapezoid in an endcap plane. Retain outlines only, with no tubes,
gas mixture, electronics, supports inside the chamber or claimed response.
Panel segmentation may use smaller whole rectangular/trapezoidal modules around
fixed obstacles; do not clip arbitrary coil-shaped holes into a chamber and
call the result rectangular or trapezoidal. Bound minimum useful panel sizes
and edge/service reservations before generating the final layout.

**INFERENCE:** planar chambers cannot inherit cylindrical mid-surface clearance
tests. Their full depth and corners can collide with coil cases, adjacent
panels, supports or chamber ends. Validate actual convex prisms. A conservative
subdivision bound may certify separation from the exact finite coil masks;
uncertain boundary cells must be refined or rejected, never accepted from
corner/centre samples alone. Use separating-axis tests for convex panel/support
geometry, with explicit gap padding and designated support-to-case contacts.
Projection overlap is distinct from physical volume overlap.

**NODD DESIGN CHOICE, proposed:** retain finite warm support members, case
attachments, shared barrel/endcap load paths and feet to a floor plane. Every
coil case must connect to the frame and ground in a graph whose contacts are
also checked geometrically. Member dimensions/materials and resulting mass
remain concept assumptions. Connectivity and occupied-space checks do not
certify gravity deflections, magnetic loads, fatigue, buckling, quench loads,
pressure vessels or construction feasibility. Prefer explicitly nonmagnetic
support assumptions; do not silently add ferromagnetic steel to a fixed vacuum
field study.

## Coverage and physics interpretation

**INFERENCE:** a literal uninterrupted 4π detector is impossible with the beam
opening and finite supports. Treat 4π as the coverage study's denominator and
design goal, rather than substituting a conditional |eta|≤3 percentage. Sample
uniform cos(theta) and full phi over both ends; feet break twelvefold symmetry.
Retain at least one, two and three distinct station crossings, separately for
outer chamber envelopes and an assumed inward border. Multiple panels from one
station must not become multiple independent measurements.

Report polar opening bounds, all-phi/eta maps, barrel/endcap transition cracks,
coil shadows and new support shadows. Keep actual hit availability distinct
from a route free of material between hits or before the first hit. A muon can
traverse a support; no reconstructed efficiency follows from a geometric veto.
Use actual plane crossings for any lever-arm or response calculation. A nominal
3 m station-centre span does not guarantee a 3 m path or unchanged momentum
precision for planar/staggered stations.

The inherited map remains the joint coil field in vacuum. HCAL steel B–H,
actual case/support transport, chamber internals and installed-field solution
remain unresolved. New chamber geometry cannot validate the inherited 35 μm
chamber/alignment assumptions or the borrowed 1.3 X0 material proxy.

## Deliverables and independent checks

Retain source locators and FACT/INFERENCE/CHOICE classification, exact modular
parameters, chamber/support identifiers and transforms, outline geometry,
connected load graph, finite-space XY/RZ/3D views, full-sphere coverage and
station-count data, conservative collision evidence, support allocation/mass
scope, unchanged magnetic-input hashes, tests, and exact-revision technical
review. This is a proposal for review, not production integration or sign-off.

**INFERENCE, exact coil path geometry:** the finite warm racetrack tube in its
meridional plane is the filled rounded rectangle expanded by half-width a,
minus the inner rounded rectangle contracted by a, intersected with the
tangential slab of half-width b. Here a is smaller than each corner radius.
Each filled rounded rectangle is the union of two central rectangles and four
corner disks. Analytic ray/slab and ray/circle intervals therefore give the
warm path intervals without coarse path sampling. Cross-check this equivalent
representation against the existing exact distance mask at random points.

## Bounded prototype choices before generation

**FACT, public precedent:** ATLAS JINST 3 S08003 (2008), chapter 6 §6.3.2,
printed p.171, specifies rectangular barrel and trapezoidal endcap chambers.
Tables 6.3–6.4 (p.174) establish metre-scale chamber/tube dimensions and special
small chambers; those table dimensions are not complete installed envelopes.
Sections 6.1–6.2 describe overlapping sectors and explicit service/support gaps.
[Primary chapter](https://jinst.sissa.it/LHC/ATLAS/ch06.pdf), source ID
`SRC-ATLAS-JINST-2008`. These precedents guide the following unsigned choices.

**NODD DESIGN CHOICE:** use 24 aligned barrel facets per station, at phi=15°k.
For apothem R and half-depth h=0.25 m, use width
`2*(R-h)*tan(7.5°)-0.020 m`: 1.283/1.678/2.073 m. This prevents physical
overlap of adjacent full-depth rectangles; it intentionally leaves angular
cracks. Aligning all stations preserves common three-station directions.
Staggering the outer station by 5–7.5° can move its finite-depth corners within
50 mm of the fixed BT case; do not adopt a stagger from a mid-surface drawing.
Split longitudinal spans ±7.7/9.2/10.7 m into modules of at most 2 m, separated
by 20 mm. Do not change the nominal three apothems or magnetic currents.

**NODD DESIGN CHOICE:** use 24 endcap angular compartments per disk, aligned
with the barrel facets, with radial bands at most 1.5 m wide. Each trapezoid
stays inside its angular/annular compartment: inner base apothem r_min, outer
base apothem r_max*cos(7.5°), and 20 mm angular/radial separation. The nominal
inner radial bound remains 0.70 m; case clearance can require larger local
inner bounds. Allow narrow inner trapezoid bases, with forward technology and
background qualification open.

**NODD DESIGN CHOICE:** adaptively subdivide obstructed compartments into whole
rectangles or smaller trapezoids; retain only certified clear modules. Use
minimum longitudinal/radial span 0.50 m and minimum face area 0.25 m² to prevent
arbitrarily tiny patches rescuing a coverage plot. Use 50 mm clearance from
warm coil reservations and support envelopes. These numerical choices bound
this exploration; they are not accepted manufacturing/installation tolerances.
Also report an assumed 30 mm inactive edge border, independently of the 20 mm
physical intermodule gaps. Neither is a published ATLAS dimension.

**INFERENCE, two coverage definitions:** a measurement-plane footprint crossing
can enter/leave the chamber through a side. Also report the stricter condition
that the ray crosses both normal-depth faces inside the border-inset footprint.
Neither predicts actual multilayer efficiency or chamber precision. For central
barrel rays the nominal mid-face phi fractions are approximately
93.8/95.2/96.1%; the 30 mm edge proxy reduces them to 89.4/91.8/93.3%, before
coil, axial-gap and frame losses. These provide analytic regression controls.

**FACT, support precedent:** ATLAS chapter 9 §9.5.1 (printed p.275) describes
paired nonmagnetic austenitic steel feet, girders and rails; §9.6.2 (pp.279–280)
describes assembly struts/girders and load transfer to the feet. Chapter 2
§2.1.2 describes warm aluminium struts. These support a topology precedent,
not the following dimensions or energized-magnet strength.
[Primary support chapter](https://jinst.sissa.it/LHC/ATLAS/ch09.pdf), same source ID.

**NODD DESIGN CHOICE:** an external 12-sided braced frame has apothem 9.30 m,
vertices at phi=15°+30°k, five main portals z=−10.5/−5.25/0/5.25/10.5 m,
four endcap carriers z=±6.30/±12.30 m, and twelve longitudinal girders.
Outer portal/girder rectangular hollow sections are 300×400 mm with 20 mm wall;
carrier hoops/spokes use 300×300×20 mm and 72 braces use 200×200×15 mm.
Endcap inner carrier hoops have apothem 5.75 m. Local front spokes at |z|=6.30 m
cross the B2/B3 chamber region; their occupied corridors enter chamber exclusion
and material-shadow checks. Rear carriers are beyond the chambers.

**NODD DESIGN CHOICE:** 60 BT radial case ports and 96 ECT axial ports connect
all 36 coil identities to this shared frame. Ports at ECT radii 5.8/6.8 m touch
the outer warm skin at |z|=6.55/11.95 m, far from the overlapping inner sleeves.
Reuse the three shared warm assembly reservations. Do not invent 36 independent
case-wall shells: an overlapping sleeve's wall can cut a neighbouring winding.
The inherited pressure vessel and cold force closure remain unengineered.

**NODD DESIGN CHOICE:** five pairs of feet at x=±2.49193 m and the five main
portal z positions connect bottom girders via aluminium shoes and steel caps,
600×600×30 mm hollow columns, and 1.2×1.2×0.15 m baseplates to floor y=−11.50 m.
Use density proxies 2700 kg/m³ for Al and 8000 kg/m³ for low-carbon austenitic
steel, both with mu_r=1 assumed. These are mass/space surrogates, not certified
alloys or magnetic weld qualifications. Sum stock separately from joint union
volume; do not double-count intersections or infer coil/chamber deadloads from
the inherited cold-allocation volume. Geometric ground connectivity and a
self-weight estimate do not establish magnetic-force closure, stress or stiffness.

Exact parameters, contacts and engineering limits from the bounded SysArch
proposal are retained as [support input](../validation/DES-040/support-input.json).

## Numerical sampling amendment

The initial 120×360 versus 240×720 equal-solid-angle midpoint grids differed
by up to 11.2 percentage points in station-count bins. Periodic segmentation
and narrow gaps alias those grids; this is a numerical integration limitation,
not a reason to alter physical module choices. Retain 240×720 and 480×1440 grids
for maps and sensitivity, plus 1,048,576 independent iid uniform-cos(theta)/phi
rays (seed 40087) for headline fractions and binomial sampling standard errors.
Use quarter-sample controls and a paired no-frame repacking control. Do not call
the map grid converged or attach the iid sampling error to geometric uncertainty.
Similarly retain two independently seeded support-mass union sample sizes,
262,144 and 1,048,576 per material, with sampling errors separated from unknown
material/dimension uncertainty. These method refinements change no geometry.
