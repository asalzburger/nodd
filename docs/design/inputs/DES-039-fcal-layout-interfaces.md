# DES-039 — Common FCAL layout interface dossier

- Assignment: `FCAL-SysArch-01`; role: SysArch, explicitly supplied mandate.
- Status: **DRAFT / PROTOTYPE**; date: 2026-10-17.
- Input revision: `33a607b70214532cd265623241b0c250ca0da361`.
- LAYOUT-002 comparison revision: `72d37ee9a56182e4ba974791a848a738c19cf092`.
- Numerical design approvers: none; machine, engineering and performance review pending.
- Scope: physical interface assessment for the common warm tungsten/quartz
  concept. No production geometry, tracker, magnet or existing ECAL change.

## Evidence and interpretation

All source claims below are **FACT about pinned repository prototypes**, rather
than independently verified experimental measurements. Dimensions proposed here
are **NODD DESIGN CHOICE**, with approval pending. Ray arithmetic is **INFERENCE**
from those dimensions, assuming a point interaction at the origin and straight
trajectories. Material depth and installed performance require separate evidence.

| Evidence | Revision and precise locator | Used here |
| --- | --- | --- |
| Si–W forward and service allocation | `33a607b70214532cd265623241b0c250ca0da361:docs/design/DES-034-siw-service-envelopes.md`, sections “External backbone and HCAL interfaces” and “Forward reservation” | ECAL back 4.4832 m; FCAL reservation R80–290 mm, z4.5332–6.3791 m; HCAL aperture and service break |
| Candidate 01 dimensions | same revision, `docs/layouts/LAYOUT-001.json`, objects `ecal`, `hcal`, `beam_pipe`, `services`, `forward_reservations` | Polygon apothems distinguished from cylindrical radii |
| Candidate 02 endcap and forward allocation | `72d37ee9a56182e4ba974791a848a738c19cf092:docs/design/DES-033-allegro-lar-endcaps.md`, sections “Cryostat, electronics space and HCAL interfaces”, “Forward region and response limits” and “Forward and transition geometry interpretation” | LAr warm bore R301 mm, front/back z4.9/5.86 m; HCAL front/back z6.36/7.8559 m; unbuilt collar |
| Candidate 02 dimensions | same comparison revision, `docs/layouts/LAYOUT-002.json`, objects `ecal`, `hcal`, `beam_pipe`, `services`, `forward_reservations` | Collar R80–450 mm, z4.4–4.85 m; FCAL R80–290 mm, z4.85–7.8559 m |
| Pipe configuration | `7c6d453fef12c3207b468c4fc99633fb393072a4:detector/config/beampipe.json`, all parameters; identical values inspected at input revision | R27 mm inner, 0.8 mm wall, half-length 4 m |
| Pipe construction | input revision, `detector/src/BeamPipe.cpp`, `Tube(ri, ro, hz)` | Straight cylindrical wall and vacuum; no downstream flare |
| Coverage direction and forward obligations | input revision, `docs/decisions/ADR-006-global-envelope-and-field-hypotheses.md`, “Context and review direction”, proposed decisions 5–7 | Calorimetry investigation to absolute eta5; separate beamline/support/service obligations |
| Earlier forward boundary assessment | input revision, `docs/design/inputs/DES-003-calorimeter-review-1.md`, sections 2–5 | Envelope traversal does not establish shower containment; compact forward region affects future muons |
| Public-source register | input revision, `reference/manifest.yaml` | Reviewed catalogue context; no new literature fact is asserted by this dossier |

**NODD DESIGN CHOICE:** the coordinator's frozen common package, communicated during this assignment,
has 1.800 m overall length and 1.200 m sampling length. It supersedes this
assignment's preliminary 1.600 m sampling-length exploration. Its material
lattice and response assumptions belong to the main DES-039 proposal.

## Preferred common package and placements

**NODD DESIGN CHOICE:** retain the 290 mm cylindrical outer boundary and current
ECAL/HCAL placements. Amend only the unsigned forward reservation's inner bore
from R80 to R50 mm. Place the first sampling material at R55 mm. Use R270 mm as
the sampling outer envelope and allocate the remaining radial space explicitly.
These are physical planning boundaries, not a guaranteed sensitive annulus.

| Common component | Radius or axial allocation | Interface meaning |
| --- | --- | --- |
| Physical central bore | R0–50 mm | Empty machine reservation; no detector support or cable intrusion |
| Inner enclosure | R50–55 mm | 5 mm radial allowance, including the inner wall and separation from sampling |
| Sampling envelope | R55–270 mm; 1,200 mm axial | Actual tungsten/quartz finite-volume paths must be evaluated inside this envelope |
| Sampling block outer case | R270–276 mm | Case boundary supplied by common package design |
| Outer service/structure allowance | Inside R276–290 mm | Subdivide material, longitudinal optical tails and load-bearing members; its whole volume is not simultaneously available to each owner |
| Front closure | 20 mm axial | Sampling starts behind this allowance |
| Fibre fanout | 300 mm axial after sampling | Rear collection rather than side-mounted photomultipliers |
| Sensor cassette | 90 mm axial | 96 sensor cartridges per end under the coordinator's packing hypothesis |
| Front-end and cooler | 100 mm axial | Distinct axial pipe and sensor intervals required |
| Service interface | 70 mm axial | Local connector/handoff allowance |
| Rear closure | 20 mm axial | Total rear allocation 580 mm; total package 1,800 mm |

| Placement, on both z signs | LAYOUT-001 | LAYOUT-002 |
| --- | ---: | ---: |
| Physical front/back absolute z, m | 4.5332–6.3332 | 4.8500–6.6500 |
| Sampling front/back absolute z, m | 4.5532–5.7532 | 4.8700–6.0700 |
| Fanout absolute z, m | 5.7532–6.0532 | 6.0700–6.3700 |
| Sensor cassette absolute z, m | 6.0532–6.1432 | 6.3700–6.4600 |
| Front-end/cooler absolute z, m | 6.1432–6.2432 | 6.4600–6.5600 |
| Service interface absolute z, m | 6.2432–6.3132 | 6.5600–6.6300 |
| Rear closure absolute z, m | 6.3132–6.3332 | 6.6300–6.6500 |
| Clearance behind existing ECAL, mm | 50.0 | Core lies inside R301 mm warm bore; no axial separation claimed |
| Clearance to HCAL minimum circular bore, mm | 10.0 | 10.0 |
| Clearance to LAr warm bore, mm | Not applicable | 11.0 |
| Space from core rear to old forward-reservation back, mm | 45.9 | 1,205.9 |

**INFERENCE:** known enclosing surfaces do not overlap these cylindrical package
bounds. This checks the specified envelopes only: the common assembly has not
been combined with native ECAL/HCAL geometry, port hardware, mounting keys or a
machine pipe. Tracker and solenoid are unchanged and end upstream of the FCAL.
Reflection in z must mirror longitudinal ordering, readout ends and interface
coordinates deliberately rather than reverse the sampling/readout roles.

## Beamline and eta5 aperture amendment

**FACT about the configuration:** the current pipe outer radius is **27.8 mm**,
not 38 mm. The checked factory contains no conical continuation. Its |z|=4 m
termination is a simulation boundary, not evidence that the downstream region is
empty or that the beamline can be extended unchanged.

**NODD DESIGN CHOICE / conditional machine assumption:** reserve a straight
R50 mm detector bore throughout the core and its downstream service tail. If a
future pipe retained R27.8 mm, radial allowance to the FCAL physical inner wall
would be 22.2 mm. This allowance must accommodate pipe supports, alignment,
thermal motion, transitions, vacuum equipment and machine clearance; no machine
approval or shielding allowance is established. A larger required machine
envelope triggers a documented aperture amendment and renewed coverage checks.

**INFERENCE:** for an origin ray, `r = |z| / sinh(|eta|)`. Full axial traversal
of a cylindrical annular sampling envelope requires
`asinh(z_back/R_outer) <= |eta| <= asinh(z_front/R_inner)`.

| Sampling-envelope consequence | LAYOUT-001 | LAYOUT-002 |
| --- | ---: | ---: |
| Full axial traversal band for R55–270 mm | 3.752787–5.109436 | 3.806333–5.176695 |
| Eta5 radius at sampling front/back, mm | 61.361 / 77.533 | 65.631 / 81.802 |
| Eta5 nominal sampling inner-edge margin at entry, mm | 6.361 | 10.631 |

These margins are small. They certify neither transverse shower containment nor
an eta5 energy response. Vertex displacement, beam crossing, alignment, finite
sampling faces, inner support material and showers near the bore remain required
studies. For a displaced axial vertex, replace z with `z - z_vertex`; the nominal
margin must not be reused unchanged. No numerical beamspot envelope is assumed.

**Conservative retained-envelope control:** with the old R80 mm inner boundary,
the eta5 ray first reaches the calorimeter radius at |z|=5.936257 m. The original
01 reservation then leaves only **442.843 mm** before z6.3791 m; the original 02
reservation leaves 1,919.643 mm before z7.8559 m. In the frozen common package's
sampling intervals, eta5 traverses **zero** sampling-envelope length in 01 and
only **133.743 mm** in 02. The original empty reservations therefore do not
establish a common eta5 calorimeter. Retaining R80 is a valid lower-coverage
control, not the preferred eta5 design.

## ECAL and HCAL transition

**INFERENCE:** 01's Si–W ECAL already precedes the core. Treating its R100 mm
inner apothem as a 16-gon hole gives a worst-azimuth full axial envelope upper
edge near eta4.350 and any-intersection edge near eta4.496. Faces, inactive seams
and service material reduce actual paths. Thus a ray can traverse both the main
EM calorimeter and the FCAL EM section: combined energy accounting must preserve
their distinct deposits and upstream shower development.

**FACT about DES-033:** 02's LAr endcap has full axial annular-envelope containment
only to approximately eta3.198 and any intersection to approximately eta3.284.

**INFERENCE:** the narrow core admits its front-face envelope only above approximately eta3.586.
Consequently a **forward EM transition gap remains near eta3.28–3.59** without
the optional collar. The core accommodates eta4 and eta5 directions, but this
does not repair the intermediate directions or establish full calorimeter
coverage. Front interception, complete axial traversal and material depth are
separate observables.

**INFERENCE:** for the 16-gon HCAL inner apothem a=300 mm, the inner boundary along a ray varies
from 300 mm at a side centre to `a/cos(pi/16)=305.877 mm` at a corner. Full axial
HCAL-envelope traversal therefore extends only to eta3.464498 in 01 and
eta3.728324 in 02 at the least favourable azimuth. Any side-centre intersection
ends near eta3.750699 / eta3.958749, respectively. This aperture is unchanged.

The following are **INFERENCE: axial lengths inside bounding envelopes**, in mm.
HCAL columns bracket polygon azimuth. They are not interaction lengths or a sum
of compatible calibrated responses; actual path lengths include `1/cos(theta)`
and finite sampling/material geometry. Main ECAL deposits are omitted from this
table and must be included in the combined simulation.

| Absolute eta | 01 FCAL sampling envelope | 01 HCAL envelope min–max | 02 FCAL sampling envelope | 02 HCAL envelope min–max |
| --- | ---: | ---: | ---: | ---: |
| 3.2 | 0.000 | 1,495.900–1,495.900 | 0.000 | 1,495.900–1,495.900 |
| 3.4 | 0.000 | 1,495.900–1,495.900 | 0.000 | 1,495.900–1,495.900 |
| 3.5 | 0.000 | 1,319.085–1,416.312 | 0.000 | 1,495.900–1,495.900 |
| 3.6 | 383.873 | 785.993–893.463 | 67.073 | 1,495.900–1,495.900 |
| 3.7 | 903.848 | 196.924–315.713 | 587.048 | 1,495.900–1,495.900 |
| 3.8 | 1,200.000 | 0.000–0.000 | 1,161.640 | 1,022.781–1,154.078 |
| 4.0 | 1,200.000 | 0.000–0.000 | 1,200.000 | 0.000–0.000 |
| 5.0 | 1,200.000 | 0.000–0.000 | 1,200.000 | 0.000–0.000 |

The 01 handover around eta3.5–3.75 is a clear mixed/partial-depth region. The 02
handover also mixes partial FCAL and HCAL stacks; the larger HCAL z makes its
geometric overlap stronger. The R270–300/305.877 mm interval contains case,
service space and radial clearance rather than a continuous active bridge.
Shower leakage through this interval or out of the FCAL outer edge cannot be
inferred from the lengths. A continuous eta3.2–5 containment claim is unsupported.

## Optional collars and alternatives

The preferred **physical core fit requires neither collar**. A collar is a
separate forward EM extension requiring its own layers, material, support and
service budget; it is not added implicitly to an empty reservation.

| Optional draft reservation | Concrete placement | Consequence and limit |
| --- | --- | --- |
| 01 short collar | R300–450 mm; absolute z4.5332–4.8332 m | Entirely behind the existing Si–W back, 50 mm before HCAL front, radially outside the R290 mm core. Full axial envelope band eta3.069–3.410, any intersection about 3.006–3.474. It duplicates much of existing Si–W coverage and cannot repair the eta3.5–3.8 hadronic handover. No preferred implementation at this stage. |
| 02 EM collar | R50–450 mm physical, R55 mm sampling inner boundary; absolute z4.4000–4.8400 m | Amend old R80 mm collar bore and shorten its rear by 10 mm to keep 10 mm axial separation to the core. Sampling thickness/skins not selected here. The physical annulus is 60 mm before the LAr warm front and 300 mm after barrel warm end. Using the whole 440 mm envelope as an upper bound gives full axial band eta3.071–5.075 for R55–450 mm. It can geometrically bridge the LAr/core EM gap; it supplies no full hadronic-depth repair. |

**NODD DESIGN CHOICE:** if the 02 collar proceeds, split the 800 mm front service
gap explicitly: its inner R<450 mm region hosts the collar, while existing
outer cryogenic/routing corridors retain their documented radii. No complete
radial access corridor through that gap can then be assumed. Collar rear
collectors may join the core's declared longitudinal service allowance through
a designed transfer; they must not cross sampling material or occupy the same
space as the core housing. The 01 collar, if studied, similarly needs its own
route within the inner rear break. Neither collar receives an unexamined share
of the established Si–W/LAr external egress lanes.

**Alternative needing a new envelope:** obtaining a full 1.2 m sampling-envelope
traversal already at eta3.2 would require sampling outer radii of at least
469.807 mm (01) and 495.677 mm (02), before lateral shower margin and housings.
This is incompatible with a R290 mm neck beside the existing HCAL and with the
R301 mm LAr warm bore in02. A widened body, reshaped HCAL inner boundary, or a
downstream wide module would require an explicit cross-system amendment. A
downstream shift alone increases the radius required at fixed eta and cannot
fix this conflict. Retain the narrow common prototype with its stated transition
limits while those alternatives are judged by material/response evidence.

## Optical, readout and cooling packing

**NODD DESIGN CHOICE supplied by the common package:** 96 nominal 30×30 mm sensor
cartridges per end sit at six radial centre rows95,130,165,200,235,270 mm and 16
azimuths. A square aligned in radial/tangential coordinates has worst outer
corner `sqrt((270+15)^2+15^2)=285.394 mm`. A rear housing inner radius 288 mm leaves
2.606 mm nominal radial corner clearance. This is a box-envelope result; mounting
lugs, connectors, tolerances and optical coupling are not thereby qualified.

The rear 6 mm OD cooling pipes centred at R284 mm occupy radial 281–287 mm. They
therefore overlap the outer cartridge radial range and **must have distinct
axial intervals** in the cooler bay. The pipes' radius cannot justify a shared
sensor-plane route. The case ending R276 mm leaves5 mm radial separation to
their inner surface, subject to their actual axial placement and connections.
The 300 mm fanout space, 90 mm sensor bay and subsequent electronics/cooler bay
must be partitioned in the model rather than represented as simultaneous free
capacity. Radiation, field, temperature and light-yield suitability of sensors
remain subsystem response/engineering questions.

Use longitudinal optical tails towards the rear, with named per-sector
allocations inside the declared housing. No side-mounted PMT assembly is assumed
to fit within20 mm of radial allowance. Optical bend radius, fibre count,
connector access and light losses must be evaluated against the actual selected
quartz/readout architecture. A common material lattice does not establish a
common calibrated response when the upstream ECAL and collar histories differ.

## Rear egress and mechanical load paths

The core rear is upstream of the HCAL rear in both candidates. An outward
radial turn at the sensor cassette would intersect HCAL material. **NODD DESIGN
CHOICE:** continue service tails axially within the declared R270–290 mm forward
service envelope to 50 mm beyond the HCAL rear, then reserve a new 150 mm axial
plane for radial routing. Material-filled sampling/case sectors cannot also be
counted as empty tail lanes: the exact service subinterval is an open packing
item. Cooling routes begin in the rear cooler bay and need a connected return.

| New downstream service reservation | LAYOUT-001 | LAYOUT-002 |
| --- | ---: | ---: |
| Axial tails from physical core rear to, absolute z m | 6.4291 | 7.9059 |
| Radial handoff plane, absolute z m | 6.4291–6.5791 | 7.9059–8.0559 |
| Core-rear to turn-plane front distance, mm | 95.9 | 1,255.9 |
| Provisional radial handoff edge | R4.300 m | R4.850 m |

The01 R4.300 m edge matches the documented external service handoff radius but
uses a **new downstream axial plane**, not the occupied Si–W rear break. The02
R4.850 m edge is a new draft choice beyond the HCAL maximum corner radius
approximately4.7165 m. These planes are additional detector extent and must be
shown in drawings and future muon/forward shielding reservations. A 150 mm plane
is a routing allocation, not a demonstrated bend allowance for arbitrary pipes
or connectors. Assign individual routes and reject any that need larger bends.

**NODD DESIGN CHOICE / load-path requirement:** each end's absorber/quartz stack,
collar if present, optical package and cooling loads transfer through its own
case and axial structural members to named common-calorimeter mounting sockets.
Neither the beam pipe, tracker nor LAr inner closure carries those loads. The
10 mm HCAL radial clearance is installation space, not a qualified rail. Front
and rear sockets, support penetrations and mounting-key sectors must be reserved
jointly with HCAL; the02 upstream overhang through the LAr bore makes this
especially important. Do not assume an unanalysed 1.8–3.0 m cantilever is valid.

**INFERENCE:** the common sampling annulus envelope volume is 0.263423 m³ per end; enclosure
annulus volume over 1.8 m is 0.461437 m³ per end. They are geometric capacities,
not material volumes or masses. Use the explicit stack inventory for gravity,
magnetic force, seismic/handling, cooling and socket loads. No support strength,
deflection, thermal circuit, shielding mass or field perturbation is established.

## Interface register and verification

| Interface / endpoint owners | Contract and current status | Required verification |
| --- | --- | --- |
| Machine/pipe ↔ FCAL; SysArch and machine owner ↔ CaloTech | Global cylindrical frame; R50 mm clear bore; downstream pipe missing; conditional fit | Beamline model and machine aperture/transition review; signed eta/phi material scans |
| Existing ECAL ↔ FCAL; CaloTech and SysArch | Existing ECAL unchanged;50 mm axial clearance in01,11 mm radial warm-bore clearance in02; optional collars separately budgeted | Native combined construction, tolerance/installation sweep; upstream shower accounting |
| HCAL ↔ FCAL; CaloTech and common mechanics | R290 mm body inside300 mm minimum HCAL bore; sockets/rails not yet engineered; partial-depth angular handover | Full3D overlap check including polygon corners, ports and supports; finite-material path and response scans |
| Local optics/electronics ↔ common services; CaloTech ↔ SysArch | Rear fanout/readout/cooling with axial tails and new rear radial plane; no preassigned capacity in ECAL egress | Channel/fibre/cable/pipe packing; bends/connectors; power/heat/flow and connected hydraulic return |
| FCAL mechanics ↔ common structure; CaloTech ↔ SysArch/HCAL | Independent case/rails and joint sockets; no pipe or cryostat loading | Inventory-derived loads, deflection/thermal motion and installation/removal studies |
| Forward shield/rear plane ↔ future muons; SysArch ↔ MuonTech | New rear extent6.5791/8.0559 m; future muon placement and shielding unresolved | Joint envelope/material review, leakage/punch-through simulation and complete-field assessment |
| Deposits/identifiers ↔ downstream readout; CaloTech ↔ SoftEng/PhysVal | Preserve separate core EM/HAD, ECAL and optional collar energy; both signs of z | Stable IDs, explicit coordinate/reflection convention, hit mapping and combined calibration model |

Actual checks for this assignment: exact-revision `git show` inspection of all
listed inputs; current branch/HEAD/dirty-tree inspection; independent Python
standard-library ray/annulus/polygon arithmetic for the tabulated dimensions,
retained R80 control, cartridge corner and geometric volumes; positive placement,
packing and transition assertions; and whitespace/table-format checks. No native
DD4hep/Geant4 construction, material ray trace, shower simulation, field solution,
load analysis or hydraulic/optical qualification was run by SysArch. The
coordinator owns reproducible package geometry and material checks, session
logging and integration. Only this dossier is owned by this assignment.

## Conditional amendment: LAYOUT-002 forward EM collar

- Follow-up: `FCAL-SysArch-01`, 2026-10-17; same owned file and pinned layout sources.
- Status: **DRAFT / PROTOTYPE**, no numerical, machine or engineering sign-off.
- Scope: the coordinator requests closing the 02 forward EM transition within
  this design using its pre-existing collar reservation. This amendment replaces
  the earlier optional 02 collar outline and the core-only 02 EM-gap baseline.
  The earlier gap numbers remain a control describing the core without a collar.
  There is no wide collar in 01; its existing Si–W endcap supplies that EM region.

**NODD DESIGN CHOICE:** add an 02-only tungsten/quartz EM collar on both z signs,
physical R50–450 mm and absolute z4.400–4.840 m. Amend the old R80 mm collar bore
to R50 mm explicitly. Retain the common R290 mm core, case and material lattice
without modification. The collar sampling annulus uses radial boundaries
55/185/315/430 mm and a 5 mm fibre pitch, with long and short fibre populations;
the short population starts 50 mm into the 100 mm sampling block. These are
selected prototype parameters, not established operating response.

| Collar component | Axial length, mm | Absolute z interval, m |
| --- | ---: | ---: |
| Front closure | 10 | 4.400–4.410 |
| Sampling | 100 | 4.410–4.510 |
| Fibre fanout | 220 | 4.510–4.730 |
| Sensor cassette | 40 | 4.730–4.770 |
| Front-end/cooler | 40 | 4.770–4.810 |
| Service interface | 20 | 4.810–4.830 |
| Rear closure | 10 | 4.830–4.840 |
| Total physical package | 440 | 4.400–4.840 |

**INFERENCE:** using only the R55–430 mm sampling-envelope boundaries, full
axial traversal occurs for eta3.045679–5.077483 and any intersection for
eta3.023360–5.099904. The 100 mm sampling envelope is fully crossed at eta3.2,
3.284, 3.4, 3.5, 3.586, 4 and 5. It therefore bridges the main LAr/core EM gap
and overlaps the LAr annular-envelope band to eta3.198. Actual tungsten/quartz
paths, radial boundaries, skins and fibres must be traced before claiming
continuous material depth or response. In particular, the preliminary
approximately 28 X0 value is a material-budget hypothesis, not a result of this
100 mm dimensional check. The collar does not repair the hadronic transition
or establish uniform jet response.

At eta5, the sampling-front/back radii are 59.431/60.779 mm. The front inner-edge
margin is only **4.431 mm**, smaller than in the common core. This remains a
beam-hole/shower-containment limitation despite the nominal ray crossing.
The same unknown downstream machine aperture and vertex/alignment sensitivities
apply as for the common R50 mm bore.

**NODD DESIGN CHOICE:** use 96 nominal 30×30 mm SiPM-array cartridges per collar,
16 azimuthal sectors × 3 radial sampling regions × long/short channels. Six sensor
centre rows are R95,160,225,290,355,420 mm. Their count is a readout allocation,
distinct from the number of individual fibres or SiPM microcells. A compact
40 mm cassette replaces the core's 90 mm cassette only in this collar; optical
coupling, electronics, connectors and thermal contact must fit the declared
bays. The outer cartridge corner is
`sqrt((420+15)^2+15^2)=435.259 mm`, leaving 14.741 mm to the R450 mm body outer
surface before allocating its housing and tolerances. Pipes at R435 mm overlap
that radial range, so pipe and sensor volumes need separate axial intervals.

### New collector and axial service neck

**NODD DESIGN CHOICE:** reserve a distinct collar rear collector at
R290–450 mm, absolute z4.840–4.890 m, followed by a new R290–298 mm longitudinal
service neck continuing to the previously proposed rear turn plane at
absolute z7.9059 m. This increases the 02 forward service envelope by **8 mm**
beyond the R290 mm core and supersedes any earlier assumption that all 02 collar
services fit inside that radius. It does not change the common core body.

The collector ends 10 mm before the LAr warm front at z4.900 m. It occupies
the outer radial region while the core begins at z4.850 m inside R290 mm.
Do not create overlapping or numerically fragile coincident annular daughters
at that boundary: actual collector solids must start outside the core case,
or share an explicitly constructed interface. Mounting lugs and connectors
cannot protrude outside the declared boundaries.

The service neck's outer envelope has nominal clearances of **3 mm** to the
R301 mm LAr warm bore and **2 mm** to the HCAL's minimum R300 mm circular bore.
These are small geometric margins requiring explicit tolerance, alignment and
support checks. The neck is an allocation for services rather than a new
continuous active absorber or qualified structural sleeve. Preserve the outer
LAr/ECAL service corridors and the downstream radial plane; do not reuse their
capacity without joint accounting.

**INFERENCE / constructive single-pipe example:** 6 mm OD pipes can run at
centre R294 mm in the neck, occupying R291–297 mm. A radial transfer from
R435 to R294 mm with two 18 mm centreline-radius quarter-circle bends needs
36 mm axial centreline drift, a 105 mm straight radial segment, and a 42 mm
axial tube envelope including OD. This fits a 50 mm collector plane analytically,
leaving 8 mm combined axial allowance. One centreline sequence in mm is:

`(R435,z4847) -> (R417,z4865) -> (R312,z4865) -> (R294,z4883)`.

The first and last portions are quarter-circle bends, with a straight radial
segment between them; incoming and outgoing tangents point downstream. The
corresponding pipe bounds are z4844–4886 mm and R291–438 mm, leaving 4 mm to
either axial collector boundary, at least 1 mm to the common core radius, and
12 mm to the collector outer radius. This is not a whole-network packing proof.
Supply and return need distinct azimuthal lanes, connected ends, bend solids,
coolant ownership and mounting clips. The 18 mm bend radius is an unsigned
manufacturing assumption, not a qualified minimum radius. Exact finite tubes
and elbow surfaces must be checked in native geometry.

### Additional interface obligations and actual checks

The collar and new neck require joint CaloTech/SysArch/HCAL ownership for route
capacity, removable supports and tolerances, with the machine owner retaining
the central R50 mm bore requirement. No collar weight transfers to the beam
pipe or LAr closure. Service neck occupancy reduces the free installation gap;
do not treat the original 10/11 mm core clearances as still wholly available.
The collar, core and main LAr deposits retain separate identifiers and upstream
shower histories for combined response studies.

No fatal **bounding-envelope** conflict was found in this amendment. Actual
checks added by SysArch were independent Python arithmetic for collar component
lengths and eta bands, edge margins, sensor corner, two-elbow transfer bounds,
neck clearances and document formatting. Native geometry, exact fibre/material
paths, cooling/optical/network qualification and shower performance remain the
coordinator's implementation and validation tasks.
