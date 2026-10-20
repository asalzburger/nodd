# DES-040 — Modular muon chambers, connected support frame and feet

- Status: DRAFT
- Scope: isolated chamber and warm-frame PROTOTYPE
- Created: 2026-10-19
- Original magnetic input: PR87, `fe372194038ed2af9617c27defffba09ae6d683f`; current shortened-ECT candidate below
- Human engineering acceptance: none

## Review request and original interface conflict (2026-10-20)

The agreed [PR90 decision](https://github.com/asalzburger/nodd/pull/90#issuecomment-6283618592)
requests full trapezoid wheels for the inner and outer endcap stations, placed
longitudinally outside the endcap toroids, with no chamber overlaps. It also
requests a new OBJ, full/endcap coverage, before/after endcap shape lists and
blue 2D inventories, and the current barrel shape inventory. This authorizes an
isolated prototype investigation; it grants no engineering acceptance.

**FACT about fixed inputs:** the current HCAL endcap back is at |z|=6.4412 m;
the endcap warm coil front is at 6.55 m. The proposed chamber depth is 0.5 m
and existing coil clearance is 0.05 m. These values are recorded in the retained
geometry/configuration and support inputs above.

**INFERENCE:** a full radial inner wheel behind the HCAL and before the toroid
has only 0.1088 m gross axial space, less than the 0.5 m chamber even with zero
clearance. With the existing 0.05 m coil clearance and a provisionally equal
HCAL margin, 0.0088 m remains, a 0.4912 m deficit. That HCAL margin is an open
interface choice, not an existing accepted calorimeter requirement. A radial
or magnet-interface change must be explicitly selected before implementing that
wheel. Barrel coil legs and the carrier frame also require full-volume checks.
The [interface study and baseline inventories](../validation/DES-040/wheels-2026-10-20/README.md)
retain the quantified alternatives and common coverage protocol.
The user subsequently selected ECT shortening; the pre-implementation contract
below records the permitted changes. Previous configurations and evidence remain
immutable historical controls.

**NODD display choice:** inventory rectangle shapes by tangential width, axial
length and depth; inventory trapezoids by radial span, inner/outer base widths
and depth. Group numerical construction duplicates on a 1 nm dimension grid,
while retaining each actual panel's full-precision dimensions and ID. These
display families confer no manufacturing tolerance or chamber response. Use
the existing blue material colour in all requested 2D shape views.

## Selected wheel revision contract (2026-10-20, before implementation)

**NODD DESIGN CHOICE, human-directed prototype:** the user selected “shorten the
Endcap toroidal to make wheel fit” after the quantified alternatives above.
Move each ECT front return outward by0.50 m, keeping the rear return fixed:
centre abs(z)=9.50 m, half-length2.20 m, centreline ends7.30/11.70 m.
Retain12-fold symmetry, phases, radii,0.60 m corner, uniform0.20×0.30 m current
packs, and0.50×0.60 m warm reservations. The warm front becomes7.05 m.
This authorizes the isolated numerical/outline candidate, not engineering sign-off.

**NODD DESIGN CHOICE:** retain the exact existing operating ampere-turns and
3 T solenoid source. Recompute the complete self/mutual vacuum energy and its
energy-sized cold allocation for the shortened source; require that allocation
to fit the retained warm reservation. Preserve homogeneous winding density.
Do not retune current against the superseded8/9.5/11 m disk response targets;
report actual changed-field/station consequences. HCAL magnetization and all
engineering qualifications remain unresolved as in DES039. Historical magnetic
artifacts stay immutable; the revised configuration/map is stored separately.

**NODD DESIGN CHOICE:** keep500 mm chamber envelopes and0.70 m endcap bore.
Put the inner wheel at abs(z)=6.7456 m, giving54.4 mm axial space to both HCAL
and the new ECT warm front; the50 mm HCAL margin remains a provisional choice.
Use12 whole trapezoids with centres15°+30°k and explicit corridors for the BT
inner legs. Select straight trapezoid edges from physical full-volume clearance,
not performance-plot tuning; record the final gap dimensions before generation.
The recorded affine corridor has10 mm half-seam at the0.70 m bore base and
360 mm half-corridor at the BT clearance-box inner edge R4.30 m; its extra10 mm
beyond the required350 mm is a prototype certification margin. Exact inner
wheel base-distance4.666416782 m and base widths0.354423346/1.901652879 m follow
from mirrored straight sides and the5.45 m outer-vertex bound. Outer-wheel
base-distance7.679008474 m and widths0.164140917/2.186062207 m follow from the
8.45 m outer-vertex bound and20 mm seams. Source inputs/configuration retain
full-precision values; no arbitrary shaped coil holes or radial fragments.
Put the outer wheel beyond the fixed rear carrier at abs(z)=12.80 m, with24
non-overlapping whole trapezoids,20 mm seams and outer bound8.45 m. The inner
wheel retains outer bound5.45 m. These whole-sector outlines supersede the1.5 m
ordinary-module radial cap only for the two new wheels; no monolithic MDT
manufacturing, sag or response claim follows. Retain the middle wheel if its
full-volume checks pass. Shorten B1 to half-length6.4456 m for the50 mm seam;
study B3 extension to12.50 m using the original whole-module packing certificates
to close the changed transition. Recalculate the actual inventory. Extend only
front ECT frame attachments to the relocated case and verify connectivity and
all physical chamber/coil/support interfaces.

**NODD computational choice:** rerun before and after geometries with common
entrance R4.35 m, half-z6.4684 m (midpoint between HCAL back6.4412 and inner
wheel front6.4956), plus the retained10 µm forward offset. The original6.50 m
cap would start inside the new wheel. Use common world half-z13.30 m and maps
extending to abs(z)=14.3125 m on the existing0.0625 m grid, with unchanged
strict invalid-stencil behavior. Extend the old field without altering old
nodes; recompute the candidate field from the changed source. Compare the
physical before/after systems honestly: geometry and field both change.
Add a separately weighted4096 iid directions per endcap cap at seed906269 for
precision, keeping the original display/4096sphere bank at seed906268.
Keep the baseline endcap angular cut abs(eta)>=1.191571051278059 and all failure
states in denominators, common direction IDs/local momenta/charges and the
existing numerical controls. A fixed-field attribution control may supplement
this physical comparison. Retain sector-gap geometric diagnostics separately
from vacuum transport availability; neither is reconstructed efficiency.

## Original chamber/frame proposal (before ECT shortening)

The user requests a new PR following the PR87 reviews
[4313407952](https://github.com/asalzburger/nodd/pull/87#discussion_r4313407952)
and [4313456506](https://github.com/asalzburger/nodd/pull/87#discussion_r4313456506):
rectangular barrel chambers, trapezoidal endcap chambers, a realistic layout
covering the full solid angle, and a frame with feet connecting and holding the
coils. This original proposal was stacked on PR87 without changing its magnetic
system; the selected wheel amendment above now changes the ECT axial extent.

**FACT about recorded input:** [DES-039](DES-039-twelvefold-toroid.md) fixes
12 barrel and 12 coils per endcap, their finite winding/cold/warm reservations,
currents, and the joint solenoid/toroid vacuum field. Retain those exact bytes.
The nominal three station radii are 5.2/6.7/8.2 m and disk planes are at
|z|=8/9.5/11 m, with provisional 500 mm chamber depth. These are unsigned project
choices, not measured ATLAS dimensions. The present study replaces the ideal
continuous chamber shells by individually identified planar chamber envelopes.

## Original geometry contract before implementation

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

## Original bounded prototype choices before generation

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

## PR90 ACTS propagation amendment (2026-10-19, before implementation)

**FACT about the request:** comments
[6268359299](https://github.com/asalzburger/nodd/pull/90#issuecomment-6268359299) and
[6268670798](https://github.com/asalzburger/nodd/pull/90#issuecomment-6268670798)
request an ACTS tracking geometry of the chamber envelopes, propagation in the
joint solenoid/toroid field, recorded global boundary intersections, XY/RZ hit
views, and entrance phi/eta maps comparing low through 1 TeV momenta. Only the
two large faces count as provisional MDT multilayer segment proxies; sides do not.
This extends validation only, preserving all chamber and magnetic input bytes.

**NODD DESIGN CHOICE, virtual study setup:** construct actual finite ACTS chamber
volumes from the retained eight vertices, with six finite native boundary portals
per chamber in a vacuum world. Use ACTS EigenStepper and Navigator; record actual
surface-reached actor positions and face ownership, including side events. A local
navigation policy may refresh candidates after position changes and conservatively
index nearby portal bounds. Validate this against exhaustive candidates and curved
fixtures; do not substitute post-processed polyline intersections for ACTS hits.
The tracking geometry contains chamber envelopes only, with no material/response,
mounts, frames or coil solids. The field still comes from the fixed joint map.

**INFERENCE and NODD DESIGN CHOICE:** the joint map rejects any eight-corner
stencil touching its winding/guard mask. A central IP ray crosses the masked
solenoid, so an IP-origin vacuum propagation cannot be the complete strict-map
benchmark. Launch on a virtual closed entrance cylinder R=4.35 m, half-z=6.50 m,
outside the pinned HCAL bounds and before the first chambers. Include barrel
and both endcaps, and label them separately. Move the start 10 micrometres forward
along the outward initial direction to avoid an on-surface ambiguity. This is a
study surface, not a changed detector envelope. Directions initially point away
from the IP; they do not claim a reconstructed incoming tracker trajectory.

**FACT about the inherited threshold:** MUON-001's 5 GeV total IP momentum is a
central candidate working point. Its central mean-loss surrogate gives about
2.65 GeV at the muon system; it is not a universal local or pT threshold.
**NODD DESIGN CHOICE:** test local total momenta 2.65, 5, 10, 100 and 1000 GeV,
both charges, with 2.65/100/1000 GeV as low/intermediate/ultimate views. These are
vacuum geometric coverage tests. No eta-dependent energy loss, scattering,
segment precision, reconstruction efficiency or material-qualified threshold is
inferred. Upstream material transport remains a separate open requirement.

**INFERENCE, counters:** literal >5 means at least six unique (chamber, large-face)
crossings. Also count three distinct stations each having both large faces of the
same chamber in a contiguous traversal. Reentries or several panels in one station
must not manufacture independent station measurements. Retain side hits, raw
events, duplicate/reentry counts, and outer-face versus 30 mm border-inset results.
An ACTS boundary crossing is only a segment proxy, not a fitted segment.

**NODD DESIGN CHOICE, numerical protocol:** use common seeded entrance directions
across momentum/charge cases, full-azimuth maps with explicit eta plotting range
and an independent full-sphere direction control. Preserve all generated tracks,
including navigation/step/path/return errors and masked/out-of-domain field lookups.
Never fill masked field nodes with zero, silently extrapolate, or drop failed
tracks. A threshold reached before a later field failure is proven, but the final
event multiplicity remains incomplete. Report lower/upper availability bounds
for unfinished tracks and conditional complete-track diagnostics separately.

The world must contain all chamber corners while remaining inside the map domain.
Use no more than 50 mm field steps initially, tighter surface/RK tolerances,
and explicit step/path budgets; compare half-step/tighter-tolerance controls.
Check field lookup against the retained Python reader including C12 seams,
mask/outside failures and SI-to-ACTS units. Validate zero/constant-field analytic
fixtures, all ACTS prism faces/IDs, native hit residuals and finite bounds, charge
reversal, side-entry/reentry counters and indexed/exhaustive navigation agreement.
Numerical refinement may change sampling, not the physical chamber/field design.
Retain ACTS source/installed-header/library identities, dirty-source boundaries,
commands, raw hit/track arrays, maps, controls and an independent fixed-revision
assessment before updating the PR.

### Native face-audit numerical amendment (2026-10-19, before implementation)

**FACT from the adverse control:** in a synthetic constant+3T fixture, a5GeV positive muon starts at (4.35,0.500001,0)m along+x. An exact prism occupies x4.36–4.86m and y/z±0.5m. The helix crosses both large faces, although the initial tangent misses the finite entry face. The initial finite-portal policy at50mmsteps and10nm targeting records only the exit. The original1micrometre targeting also exceeds ACTS portal lookup's tighter default check and aborts an assertion; assertions must remain enabled. These observations invalidate finite-tangent navigation as the scan's primary discovery method. This fixture changes no detector parameters.

**NODD DESIGN CHOICE, revised numerical method:** retain the exact finite ACTS volumes/portals as the geometric source, but use an explicit boundary-surface audit policy: propose supporting planes with infinite candidate-boundary tolerance, obtain the roots using native ACTS EigenStepper/Navigator integration, and accept an event only if the actual finite native face contains that native root. Fan out coincident-plane roots to all finite owning faces to avoid losing coplanar panels. Exclude all outside-footprint roots. This tests native face crossings in a real tracking geometry; it does not claim validation of native portal volume-switching through every chamber. No post-processed trajectory segments or fabricated roots are allowed. Retain the finite-portal mode as the adverse negative control.

Use10nm initial targeting/RK length tolerance (a tightened numerical parameter) with50mm maximum steps. Verify actual face residuals, bounds, exact straight/constant-field roots, adverse edge recovery, charge-field reversal, indexed/exhaustive agreement and half/quarter-step plus tighter-tolerance controls. Preserve mode and failure metadata and distinguish native geometry construction from the audited navigation semantics. Numerical fixes must not tune physical chamber geometry or fill masked field values.

### Native correction and curvature guard (2026-10-19, before implementation)

The initial surface-audit controls also failed step/tolerance and indexed/exhaustive agreement, and a locally parallel tangent missed a curved side entry. Preserve those executed failures in controls-initial.json. **INFERENCE from source tracing:** refreshing candidates during a pending native negative correction step discards ACTS's active target and prevents root convergence. **NODD DESIGN CHOICE:** retain that active native target through its correction and resume refresh after the native root. Do not enlarge hit tolerances.

For a planar face with signed gap g and direction component vn, vacuum constant-momentum curvature is bounded by κmax=0.299792458 |q| Bmax/p in inverse metres. The maximum valid-node field norm bounds the norm of the map's trilinear interpolant; rigid cylindrical-to-Cartesian rotation preserves the norm. Constant-field controls use their actual |B|. If no forward tangent root exists (g·vn≥0) but curvature could reach the plane, cap the next native ACTS step at0.8×2|g|/[sqrt(vn²+2κmax|g|)+|vn|], for |g| above targeting tolerance. This follows |g(s)−g−vn·s|≤κmax·s²/2. Once the tangent points toward the face, native targeting supplies the root. The public Actor step constraint limits native integration; it supplies no hit or interpolated position. Recompute it at each step, count guard use/minimum caps and near-tolerance parallel ambiguities, preserve all explicit path/step budgets, and rerun the adverse and refinement controls. These are numerical navigation choices, not detector/field changes or relaxed scientific gates.

For the no-forward-root guard, let vn point away from the plane after multiplying by sign(g). Curvature can reach the plane within the current maximum step h only if |g|+|vn|h≤κmax h²/2. Otherwise the concave lower bound stays positive throughout the step and no cap is needed. This applies the stated condition without tiny caps after ordinary normal exits. Never replace a pending native negative correction with an Actor cap.

Explicitly set `NavigatorPlainOptions::nearLimit=0`: its independent default is the ACTS100nm on-surface constant, which otherwise discards valid forward targets3.99nm away even when targeting tolerance is1nm. Native Propagator skips already-on-surface targets. This retains positive near-root candidates without enlarging surface/finite-bound tolerances or changing assertions. The discovered default/targeting mismatch is a navigation configuration correction.

### Bounded exhaustive discovery and independent integration accuracy

**FACT from controls:** an unbounded list of all infinite supporting planes oscillates between remote supports whose actual finite faces are9.9–18.5m away, producing an exhaustive-mode step limit. These are not reachable chamber faces. **NODD DESIGN CHOICE:** both primary selectors restrict supporting candidates to complete finite chamber AABBs within2·maxStep+2·targetingTolerance. The indexed selector uses Cartesian cells; the exhaustive selector scans all1560AABBs without that index and applies the same distance bound. This independently checks the grid lookup while excluding remote ghost supports. A finite face reachable within one bounded native step cannot lie outside this conservative neighbourhood. Keep an explicit unbounded-support negative mode and label this as bounded exhaustive discovery, not an all-infinite-plane reference.

**FACT from the800-track refinement:** counts/statuses agree after the native corrections, but micron trajectory integration differences amplify to66–90µm for grazing faces (|u·n|≈0.012–0.039), despite negligible face-normal residual. The10µm coordinate comparison gate stays fixed. **NODD DESIGN CHOICE:** separate numerical RK length tolerance from surface targeting: initially10pm(1e-11m) RK versus10nm targeting. Test1pm RK independently, as well as half/quarter maximum steps and1nm targeting. ACTS's native RKN local error acceptance is up to4times its step tolerance; a chosen local parameter is not a claim of global accuracy. Retain failed controls and only run the scan after the unchanged coordinate/count/status gates pass.

Pure tangential finite-face contacts remain raw events and have a separate tangent counter, but contribute to neither unique large-face crossings nor paired stations. This clarifies the declared crossing observable; a tangential touch is not a provisional segment crossing.

## Executed shortened-ECT candidate

The [selected candidate and evidence](../validation/DES-040/wheels-2026-10-20/README.md)
contain the revised joint map, 1,344 chamber outlines, connected frame, native
OBJ and paired ACTS results. B1/B2/B3 contain168/360/528 panels; both endcaps
contain24/216/48 inner/middle/outer panels. Endcap centre span is now6.0544 m,
not the original3 m. This does not establish the corresponding momentum
resolution or preserve a3 m bending path. Unresolved field-mask/native-failure
rows remain in the coverage denominators. DRAFT status and human-only engineering
acceptance are unchanged.

## Inner-sector closure feasibility (PR90 follow-up, 2026-10-20)

The [review question](https://github.com/asalzburger/nodd/pull/90#issuecomment-6285814869)
asks why inner sectors do not close and whether closure is possible. The
[bounded feasibility study](../validation/DES-040/inner-closure-2026-10-20/README.md)
separates fixed BT warm-envelope obstructions from excess gaps caused by one
long trapezoid per sector. Before generating comparison views, it records an
unadopted two-band simple-trapezoid option with the existing20 mm seams,
50 mm clearance and10 mm certification margin, and a three-band diagnostic
that violates the0.50 m useful-span rule. Both must remain separate from the
selected12-sector candidate. Radial tiling/cassette exemptions require an
explicit amendment before adoption; no minimum-span exception is granted.
Report same-module full-depth ray losses as well as planar closure, with no
transport/reconstruction improvement claim. Keep all current physical inputs,
fields, OBJ and ACTS artifacts immutable.


## Reviewer-directed chamber refinement (2026-10-20)

Human review [comment6286566047](https://github.com/asalzburger/nodd/pull/90#issuecomment-6286566047) requests closing the unnecessary inner-wheel gaps with an additional chamber type, simplifying the middle wheel to three dimension families (one full-sector family and two families around a coil-containing sector), and limiting the three inner apertures to the requested |eta|<3 coverage. This explicitly supersedes the one-trapezoid-only restriction where gap fillers are required, within the isolated unsigned PROTOTYPE. It does not authorize occupying fixed coil slots or grant engineering acceptance.

Before implementation, the NODD DESIGN CHOICE is to retain the existing magnetic sources, support bodies, barrel chambers, station centres, 500 mm depth and outer bounds. Derive aperture dimensions from eta=3 and actual nearest depth faces, accounting for finite polygon edges and seams; publish the convention and any polygonization excess. Derive new convex chamber outlines from actual rotated warm envelopes plus the retained 50 mm coil/support clearances. Prefer simple quadrilateral/trapezoid envelopes and explicitly count all added chamber types; no internal structure is designed. Whole-sector cassette size exceptions remain outline-level reservations requiring later MDT construction assessment. Every changed chamber needs fresh volume/interface checks and export/crossing validation; dated prior geometry/OBJ/transport evidence must not be overwritten or claimed for changed chambers.

The [spacing question](https://github.com/asalzburger/nodd/pull/90#issuecomment-6286557527) is assessed separately against actual BT/ECT extents and bending geometry. A change in planar coverage alone does not establish improved momentum measurement, and moving stations beyond a toroid is not selected by this question. Magnetic fields need not be recomputed when all magnetic source bytes remain unchanged.

The bounded implementation choices, recorded before construction, are: keep each station at its existing z; use nominal nearest-face aperture radius R3=(|zcentre|−0.25 m)/sinh(3) and a circumscribed polygon base to avoid whole-depth straight-ray coverage beyond |eta|=3. The resulting finite polygon loses a small band near its corners; the report must give that range rather than claim uniform acceptance to eta=3. At the middle station, fixed ECT inner-leg clearance imposes additional local opening on the three simple-quadrilateral families. Record target and actual family cutoffs separately and retain this limitation explicitly; it cannot be removed by a small station shift or by occupying the coil reservation. This is a constrained outline prototype, not proof that all directions up to eta=3 are instrumented.

For the inner wheel, retain twelve core trapezoids and add seam-centred pre-slot and post-slot filler trapezoids. A 30 mm core half-gap at the nominal bore is a NODD DESIGN CHOICE to give the fillers nonzero inner bases while retaining 20 mm normal module seams. Fillers terminate/start at local BT seam coordinates 4.29/4.91 m, giving another 10 mm axial-in-plane reserve beyond the 50 mm coil box. The remaining very small affine wedges within this localized slot band must be measured and labeled as additional slot reservation rather than physically required material. All three inner cassette families and the three middle whole-sector cassette families receive the same outline-level exemption from the ordinary 1.50 m radial-span cap as the previously selected whole wheels; this authorizes studying their envelopes, not constructing long MDT tubes. Retain the 0.50 m useful-span criterion where applicable and report any exception without hiding it. These choices follow the requested additional chamber types; structural/internal qualification remains open.

The revised geometry, fresh checks, inventories, native blue/grey OBJ and finite XY sections are collected separately in the [reviewer-refined wheel report](../validation/DES-040/refined-wheels-2026-10-20/README.md). Prior dated evidence remains the historical control. Nominal-aperture, actual coil-shadow and native crossing results must remain separate observables.


## Reviewer-directed outer-barrel overlap and longer cassettes (2026-10-20)

Human [comment6287612852](https://github.com/asalzburger/nodd/pull/90#issuecomment-6287612852) proposes improving outer-barrel coverage by angularly overlapping neighboring chambers at different radii, and reducing chamber count through greater z length. The supplied sketch shows radial staggering rather than intersecting physical volumes. This authorizes a new isolated unsigned outline PROTOTYPE; it does not grant chamber construction acceptance.

Before implementation, NODD DESIGN CHOICES are: retain the magnetic sources, all 484 support bodies, the current 192 refined endcaps, and barrel station z limits. Retain outer-station even facets on coil planes at apothem8.20 m; initially place odd inter-coil facets at8.75 m (0.55 m radial stagger). Derive odd tangential width from the actual even-facet full-depth angular limit with30 mm border, targeting0.1 degree angular overlap at each old seam. Require disjoint finite volumes with at least20 mm neighboring stagger clearance and fresh50 mm coil/support clearance. These choices must be tested over the entire prisms; projected overlap alone proves no physical separation. Report any envelope growth and keep every chamber corner belowR9.4 m within the existingR9.5 m joint-field domain. A native world boundary may grow to contain the candidate; that is not a field-source change.

Set the provisional maximum z seed length to4.0 m instead of2.0 m, retaining20 mm z seams and the existing useful-size bounds. Actual coil/frame interruptions still require finite split cassettes. Compare3/6 m seeds only as diagnostics when needed; no long MDT tube, sag, readout or structural qualification is inferred. All new dimensions are prototype choices or derived inferences, not public experimental facts. Preserve fixed-field bytes and all dated evidence; new geometry, source certificates, blue/grey OBJ, views and native crossing results belong in a separate dated report. Geometric angular/straight-ray gains are not reconstructed efficiency or momentum resolution. The previously documented middle-wheel eta3 obstruction remains open and unchanged.

The dated [barrel-overlap evidence](../validation/DES-040/barrel-overlap-2026-10-20/README.md) preserves the preceding refined-wheel candidate as its comparison baseline.

## Inner-barrel under-coil feasibility (PR90 follow-up, 2026-10-20)

Human [comment6288294033](https://github.com/asalzburger/nodd/pull/90#issuecomment-6288294033) proposes moving the inner barrel chambers on BT coil planes below those coils and increasing the tangential extent of the inter-coil chambers, analogous to the outer-barrel transverse stagger. This is an unsigned outline feasibility request, not authority to silently change the HCAL, magnetic sources or chamber depth.

Before any new trial construction, the NODD DESIGN CHOICE is to retain the current 888-chamber prototype as the active candidate, with all magnetic sources/maps, HCAL, frame, B2/B3 and endcaps fixed. First derive whether a 500 mm radial-depth inner chamber fits below the actual BT warm inner legs with the existing 50 mm HCAL/coil/support clearances. Distinguish a conservative HCAL corner envelope from actual HCAL material polygons; do not claim a material collision from an outer bound alone. If the requested placement is obstructed, report the incompatible inequalities and the physical changes needed rather than accepting an overlapping prism or changing its depth without instruction.

A conditional fixed-hardware alternative may be examined separately: retain the B1 coil-plane facets at apothem5.20 m, move inter-coil B1 facets outward provisionally to5.75 m, and derive their width for0.1 degree full-depth angular overlap including the30 mm border. Keep current B1 half-z6.4456 m,4 m maximum z seeds, nominal20 mm seams, useful-size policy and fresh whole-volume50 mm coil/support clearance; require disjoint final solids and at least20 mm neighboring stagger separation. This alternative is unselected and must not replace the active candidate, maps or exported OBJ. State its actual finite cuts, count/family/radial-envelope and any sampled gained/lost geometric directions, not just a central-slice closure. Chamber internals, structure, response and momentum measurement remain unqualified. The earlier middle-wheel eta3 obstruction remains unchanged.

The [inner-barrel feasibility report](../validation/DES-040/inner-barrel-2026-10-20/README.md) retains the actual HCAL obstruction and unselected outward alternative separately from the active candidate.

## Updated inner-barrel sketch and middle-layer offset (2026-10-20)

The updated [comment6290378667](https://github.com/asalzburger/nodd/pull/90#issuecomment-6290378667), edited at12:12:08UTC, replaces its earlier outward-trial selection with a new transverse sketch and a request to rotate the middle stations by half a sector. The actual image shows coil-plane B1 chambers retained outside the BT inner legs and the inter-coil B1 chambers moving inward between those legs. It does not request the HCAL-intersecting coil-plane inward move studied above. This is a new isolated unsigned PROTOTYPE, not engineering sign-off.

Before implementation, the NODD DESIGN CHOICES are: retain coil-plane B1 facets at apothem5.20m; provisionally move inter-coil B1 facets inward to4.63m and derive their tangential width for0.1degree full-depth angular overlap including the30mm border. The sketch does not prescribe an exact radius. The4.63m trial leaves a55mm radial gap above the known DES034 ECAL service-egress water-jacket bound4.325m, which is a design reservation rather than installed HCAL material; verify actual HCAL/service and fixed-frame interfaces rather than assume the calorimeter corner encloses all services. Complete external HCAL collectors/cabling and plant routing are absent from the source model and remain unqualified; the known jacket bound cannot certify them. R4.60m may be examined as a clearance diagnostic only; no source/clearance exception is granted. Require at least20mm physical neighbouring stagger separation,50mm HCAL/coil/support clearance, retained500mm depth,20mm seams,4m maximum z seeds and the existing area/z useful-size policy. Repack all changed B1 volumes with fresh actual-orientation proofs; preserve unaffected B3 and endcap objects exactly.

Offset B2 barrel facets by7.5degrees: half of the15degree chamber facet pitch. A15degree rotation would leave the24-facet edge set unchanged, so it would not achieve the stated edge de-alignment. Its coil/support exclusions must be freshly constructed and checked, with cache keys containing actual radius, phase and footprint. The wording's possible application to middle endcap wheels is being clarified; until explicitly included, keep endcaps fixed. Do not rotate an existing wheel blindly through fixed coil slots. Retain all magnetic sources, maps, HCAL and484support bodies; chamber-only changes require no magnetic solve.

For native crossing acquisition, re-derive the entrance boundary from the new nearest finite chamber faces. An entrance atR4.35m plus an outward start offset can start inside inward inter-coil B1; explicitly test the start points and use a smaller numerical entrance radius outside HCAL if needed. Keep world/map bounds and strict field masks explicit. Compare same-bank geometric availability at one/two/three distinct stations, gained/lost directions, finite seams/ends and actual chord-distance proxies. De-aligned edges or different radial staggering alone cannot establish constant lever arm, improved MDT momentum measurement or reconstructed efficiency. Preserve every dated earlier candidate and its evidence; new geometry, blue/grey OBJ, views and bounded native checks belong in a separate dated directory. Middle-wheel uniform eta3 remains UNMET unless independently resolved.
