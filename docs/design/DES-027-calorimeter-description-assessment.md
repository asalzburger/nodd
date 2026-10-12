# DES-027 — Calorimeter hardware description: ODD inheritance and nODD gaps

- Status: DRAFT
- Date: 2026-10-12
- Scope: realistic physical description, assemblies, materials and services.
- Human request: assess nODD and its ODD origin to the same level of hardware
  description as the tracker. Performance and reconstruction upgrades follow later.
- Human design approval: pending. This assessment selects no new calorimeter technology.


## Executive summary

ODD already describes the calorimeter sampling layers and logical cells. To make nODD as
physically explicit as its tracker, we need to describe the hardware that holds, cools,
powers and reads out those layers. The maintained nODD assembly currently contains the
beam pipe and tracker; a complete calorimeter hardware baseline is still to be
established.

The largest gaps are physical sensor/tile modules and cassettes, load-bearing supports,
cooling circuits, electronics and power distribution, service routes, and their
interfaces to the new inner solenoid. The inherited copper-rich HCAL PCB mixture also
needs a hardware/material justification. Cryostat requirements depend on the chosen
technology: silicon/scintillator calorimeters need an operating and cooling design,
while the superconducting solenoid needs an explicit cryogenic vessel and service
system.

The proposed sequence is to agree the technology, operating conditions, material ledger
and shared interfaces; design one realistic ECAL cassette and one HCAL cassette; then
build sectors and complete barrel/endcap assemblies with reproducible geometry, mass and
material checks. This PR supplies the assessment and that staged plan. Calorimeter
response, reconstruction, jets and particle flow follow as a separate programme.

## Evidence boundary and meaning of “current”

**FACT — repository inspection:** starting revision
`da5c469f4d64a711c4f466cac79ff51e83244859`, `detector/CMakeLists.txt`,
`detector/src/`, `detector/config/`, and `tools/tracker_dd4hep/export.py` build
and assemble the beam pipe and pixel/strip systems. There is no calorimeter
factory target, maintained nODD calorimeter parameter file or calorimeter
assembly export in that entry point. This is a bounded inspection of that
revision, not a claim about every external ACTS installation or branch.

**FACT — SRC-ODD-UPSTREAM:** the reproducible inventory pins the already
catalogued clean ODD snapshot
`c167363f3d4ad1540a577af99071283caf54f3a6`. Exact XML/factory hashes are in
[odd-inventory.json](../validation/DES-027/odd-inventory.json).
The audit checks file bytes against that Git revision. Current public v6.0.2
ECAL/HCAL XML was also read at
`d70556f33b1c36abdf101a07ad8cf57eb56fbdf1`; the two sampling files are byte-identical to the pinned audit inputs. This does not substitute the newer whole detector for the
pinned comparison configuration. No native ODD geometry was constructed here.

**FACT — DES003:** [global envelope inputs](DES-003-envelopes.json) and its
[calorimeter input](inputs/DES-003-calorimeter-envelope-input.md) describe
DRAFT allocations. Their dimensions are not as-built hardware or the original
ODD XML. **FACT — DES025:** the [tracker assembly](DES-025-tracker-dd4hep-gen3.md)
has component exporters, constituent inventories, explicit services,
sensitive IDs and retained native validation. It still has documented
engineering limits; “comparable” does not mean construction certification.

The separate ActsExamples calorimeter reconstruction work consumes hits/cells
and prepares clustering/particle flow. It does not establish physical modules,
power dissipation, support masses or cryostat geometry. This PR reviews
hardware only; no jet/PF, shower-response, digitization or resolution claim is
used to accept a physical design.

## What ODD actually describes

The following entries are **FACT**, at the pinned ODD paths and XML nodes shown.
Derived totals are explicitly marked **INFERENCE**. Values are comparison
inputs, not newly selected nODD parameters.

| Property | ECAL | HCAL | Source locator |
| --- | --- | --- | --- |
| Absorber / active medium | TungstenDens24 / Silicon | Steel235 / Polystyrene | `xml/detectors/Calorimeter{E,H}Cal.xml`, detector/layer/slice |
| Number of repeated layers | 48 | 36 | Same files, barrel and endcap `layer@repeat` |
| Logical grid pitch | 5.1 mm | 30 mm | `define/constant`, readout segmentation |
| Barrel / endcap segmentation | CartesianGridXY / CartesianGridXZ | Same | `readouts/readout/segmentation` |
| Polygon symmetry | 16 staves/sectors | 16 | `OpenDataDetectorEnvelopes.xml`, `ecal_*_symmetry`, `hcal_*_symmetry`; factory placement loops |
| Barrel input rmin, nominal rmax, half length | 1.250 m, 1.500 m, 3.050 m | 1.600 m, 3.436 m, 3.450 m | Envelope constants; actual stack sets outer barrel apothem |
| Endcap input inner radius, outer radius, z-front, nominal z-back | 0.315 m, 1.500 m, 3.200 m, 3.450 m | 0.355 m, 3.436 m, 3.600 m, 5.436 m | `*_e_inner_radius`, `*_e_outer_radius`, `*_e_min_z`, `*_e_max_z` |
| Stave gap parameter | barrel0; endcap2.5 mm | barrel0; endcap2.5 mm | Detector `gap` attributes; factory reduces each stave half width |

### Sampling composition and effective material

**FACT — ECAL XML layer/slice:** one repeat contains the following normal
thicknesses. **INFERENCE:** multiplying by48 gives the last column.

| Slice | Thickness per repeat [mm] | Integrated thickness [mm] |
| --- | ---: | ---: |
| TungstenDens24 | 1.90 | 91.2 |
| G10 | 0.15 | 7.2 |
| GroundOrHVMix | 0.10 | 4.8 |
| Silicon, sensitive | 0.50 | 24.0 |
| Air | 0.10 | 4.8 |
| siPCBMix | 1.30 | 62.4 |
| Air | 0.25 | 12.0 |
| G10 | 0.75 | 36.0 |
| **Total** | **5.05** | **242.4** |

**FACT — HCAL XML layer/slice:** one repeat contains30mm Steel235,
16mm siPCBMix,3mm Polystyrene and2mm Air (the XML comment calls the Air space
services). **INFERENCE:** a51mm repeat gives1836mm total over36 layers:
1080mm steel,576mm PCB mixture,108mm scintillator and72mm air.
The barrel and endcap use the same longitudinal recipe within each subsystem.

**FACT — materials XML, material `siPCBMix`:** density5.05076923076923g/cm³
and copper mass fraction0.818763326226013. Other listed elemental mass
fractions normalize to unity. **INFERENCE:** at normal incidence the HCAL PCB
allocation alone is **290.924 g/cm²**, of which **238.198 g/cm² is copper**,
from `57.6 cm × density × copper fraction`. The ECAL corresponding mixture
allocation is31.517g/cm². These are areal masses of a continuous model column,
not total installed detector masses and not a radiation/interaction-length
calculation.

That HCAL “PCB” allocation is too consequential to inherit without explaining
what it represents. A16mm homogeneous slice can stand for electronics,
conductors, cooling plates or an effective service assembly, but the source
recipe by itself gives neither a hardware breakdown nor normalization to such
parts. **NODD DESIGN CHOICE — proposed review priority:** obtain its original
rationale and define a representative cassette bill of materials. Retain the
old model as a comparison; do not silently replace16mm by1.6mm, reinterpret it
as empty space, or remove copper to improve a performance plot.

TungstenDens24 is itself an alloy mixture: **FACT**, material node density
17.8g/cm³, mass fractions W0.93/Ni0.061/Fe0.009. GroundOrHVMix and G10 also
need explicit ownership when separating electrodes, electronics and structural
skins. Preserve composition and mass if an effective representation is retained;
otherwise record a justified design change rather than a refactor.

### Geometry, gaps and identifiers

**FACT — factory interpretation:**
`factory/calorimeter/ODDPolyhedraBarrelCalorimeter_geo.cpp`, `create_detector`,
uses `dimensions.rmin`, the layer sum and trapezoidal stave widths; outer
apothem is `rmin + totalThickness`. The endcap factory converts input `rmax`
to `rmax*cos(pi/numsides)` before constructing its trapezoids. Both factories
create repeated layer/slice volumes and attach calorimeter sensitive detectors
and DDRec `LayeredCalorimeterData`.

**INFERENCE — analytic bounds at zero barrel gap:** a16-sided polygon's
outer corner is outer apothem divided by `cos(pi/16)`. The derived boundaries
are:

| Constructed stack quantity | ECAL | HCAL |
| --- | ---: | ---: |
| Barrel outer apothem | 1.4924 m | 3.4360 m |
| Barrel outer corner radius | 1.521638 m | 3.503315 m |
| Endcap outer apothem | 1.471178 m | 3.369978 m |
| Endcap outer corner input | 1.5000 m | 3.4360 m |
| Endcap back from layer sum | \|z\|=3.4424 m | \|z\|=5.4360 m |

Do not compare an imported polygon apothem to a circular solenoid's outer
radius or to DES003's axisymmetric corner-bounding rmax as if all were the
same convention. ECAL's nominal250mm envelope span is not242.4mm of active
sampling plus an identified7.6mm hardware package. No support or cooling is
implicitly supplied by the difference. Barrel/endcap transition gaps, corners,
service cracks and future cassette edges need explicit boundary contracts and
native checks. The static inventory does not prove overlap-free construction.

**FACT — XML readout IDs:** fields include system, barrel, module, stave,
layer, slice and signed grid coordinates. Physical factories assign system,
barrel/module/layer/slice placement IDs. **INFERENCE:** logical5.1/30mm grid
cells do not imply individual5.1mm silicon dies or30mm physical scintillator
tiles. Sensitive slices span the trapezoidal sampling region without a physical
wafer/tile tiling, inactive borders, cassette joints or per-tile optical package.
Future physical placement IDs must remain distinct from cell segmentation.
**FACT — both factory `placeStaves` loops:** module indices run1–16, while
readouts declare `module:4`. **INFERENCE:** value16 exceeds the unsigned4-bit
range0–15; audit native encoding/decoding and uniqueness before reusing this
contract. This static range concern is not a reported native runtime failure.

## Public hardware precedents and their use

These sources identify necessary hardware categories. They do not select an
ATLAS/CMS geometry, coolant temperature or electronics design for nODD.
The [catalogue](../../reference/manifest.yaml) records exact references.

| Evidence | FACT and precise locator | Implication for this assessment |
| --- | --- | --- |
| SRC-CMS-TDR-019, inspected2018 edition | §4.2, PDF58: sensor/cooling-plate cassettes and structural interfaces; §4.4, PDF63: cooling/environment; §4.5, PDF64–65: fluid, electrical, optical and dry-gas services | A credible granular calorimeter description includes mechanical and service inventories around the sampling elements |
| SRC-CMS-HGCAL-STRUCTURE-2025 | CMS public construction note,2025-12-16, assembly paragraphs: self-supporting electromagnetic cassettes, steel hadronic supports, endcap flange and structural wedges, thermal panels with CO₂ cooling | Separate local cassettes from the global load path; current construction evidence matters as well as TDR concepts |
| SRC-CMS-HGCAL-FORCES-2024 | V. Klyukhin, arXiv2401.02793v1, abstract: stainless absorber plates with relative permeability below1.05 still assessed for forces in the CMS field | “Low permeability” is not a substitute for computing material-dependent forces and interfaces |
| SRC-ATLAS-JINST-2008 | §5.5, PDF165–166, Fig5.25 and instrumentation/service passages: liquid-argon cryostat, warm/cold vessels and feedthroughs | Cryostat and feedthrough material is technology-specific; a LAr choice brings a substantial vessel/service architecture |
| SRC-ATLAS-SOLENOID-2007 | Abstract/Table I and §§I–II, PDF1: superconducting solenoid and shared cryostat | An inner superconducting magnet needs cold/warm interfaces even if calorimeter active media are warm solids |

The2018 HGCAL TDR,2024 force study and2025 construction note describe dated
configurations. We use their hardware lessons, not a hybrid set of layer counts
or operating parameters. ODD's HCAL comment cites HGCAL, CLD, AHCAL and SiD;
that inspiration is not a quantified cassette design or bill of materials.

## Missing description, consequences and minimum faithful representation

The following is a **NODD DESIGN CHOICE — proposed work inventory**. No
numerical sensor size, temperature, cable count, mass or support thickness is
selected here. P0 items constrain the coherent baseline; P1 items complete
representative assemblies before full integration. Named human ownership and
approval remain to be assigned.

| Priority / topic | Present evidence and gap | Physical representation needed | Review/verification needed |
| --- | --- | --- | --- |
| P0 — technology and operating contract | ODD provides Si–W ECAL and scintillator/steel HCAL, but no nODD adoption or operating point | Signed technology scope, sensor/tile family, thermal conditions, electrical power class and supported effective approximations | Public components and operating references; clarify what is inherited versus replaced |
| P0 — constituent material ledger | Thick effective PCB mixtures and passive slices lack a hardware normalization target | One part/region ledger with composition, density, volume/mass, role, source, owner and effective-detail policy | Original rationale plus independent volume/constituent mass sums; no duplicated copper, skins, coolant or air |
| P0 — calorimeter/magnet interface | Original ECAL barrel starts1.25m; proposed inner magnet needs a larger reservation | ECAL inner/outer polygon boundaries, coil/vessel/service boundary, endcap front/recess, clearance and installation route | Joint r–z/phi clearance audit; conserve sampling depth when fronts move |
| P0 — structural load path | Layer trapezoids and Air mothers do not specify frames, end plates, attachment or feet | Cassette skin/backplate, absorber joining, rings/rails/flanges, barrel/endcap support and support-to-external-structure interfaces | Weight and magnetic load envelopes, sag/alignment allowances, contraction and installation/replacement sequence |
| P0 — thermal architecture | No circuit, local thermal interface, coolant inventory or dissipated-power ledger | Sensor/ASIC → spreader/plate → pipe → manifold → external plant path; fluid/pipe/insulation volumes and regions | Component power and allowable temperature; circuit capacity and pressure/material assumptions; public evidence for selected coolant |
| P0 — power and readout distribution | Logical cell grids; mixtures do not identify physical electronics | ASIC/board/passive envelopes, bias/HV/LV routes, return/grounding, connectors, conversion/shielding and service exits | Counts/power by module/cassette/sector; conductor area and route capacity; address inactive electronics regions |
| P0 — steel and magnet coupling | Steel235 absorber definition does not provide measured B–H behavior or magnetic force inventory | Steel grade/properties, absorber/support identity, complete field model and mechanically owned force paths | Source or bracket permeability/nonlinear B–H; nonlinear installed-field and force calculation where needed |
| P1 — ECAL sensor/module | Continuous0.5mm silicon slices plus coarse passive layers | Physical wafer/sensor outlines, inactive edge, inter-sensor gap, attachment, interconnect, readout board and cooling contact | Dimensions and component/source record; active/passive counts and sensitive IDs consistent with segmentation |
| P1 — HCAL tile/readout assembly | Continuous3mm polystyrene; no tile boundaries or optical package | Tile size/cutouts/gaps, reflector/wrapping, SiPM/readout footprint, optical coupling and board; fibres only if chosen architecture uses them | Geometry and material quantities for a representative tile/cassette; optical response parameters deferred |
| P1 — cassettes and repeated structures | Repeated ideal slices/staves; no cassette bill of materials | Assembled serviceable unit, cover/skin/fasteners where consequential, dead rims, manifold/connector zones and controlled repetitions | Independent single-cassette construction, counts/masses, overlap and bounding-envelope checks |
| P1 — cryogenic/environmental enclosure | No calorimeter cryostat in solid Si/scintillator inheritance; solenoid requires one | Technology-specific dry-gas/thermal/dew-point enclosure or reviewed cryostat; separate ownership of solenoid warm/cold structures | Decide standalone versus shared vessel; prove thermal, feedthrough and contraction space without double-counting material |
| P1 — barrel/endcap cracks and access | Zero barrel stave gap and simple endcap gap parameter | Physical cassette seams, support ribs, axial cracks, service penetrations, tolerance/assembly allowances | Native extrema/overlaps including polygon corners and adverse tolerance states; documented installation/access assumptions |
| P1 — service corridors | Air slices labeled services without cable/pipe/fibre inventory | Local collection, sector trunks and exits with bounding volumes, constituent inventories, fill limits and ownership | Volume conservation, worst-route capacity and cross-subsystem intersections; air counted once |
| P1 — forward region | DES003 reserves a forward region; no maintained nODD forward hardware assembly | Technology, active/passive boundaries, beam aperture, shield/support, cooling/power/readout and transition to endcaps | Separate sourced design and beamline/magnet/tracker interface; reservation is not an implemented forward calorimeter |
| P1 — provenance and native release evidence | Static ODD source; no maintained nODD calorimeter release audit | Versioned config/factories/inputs, stable identifiers, dimensions/placements and material ledger | Reproducible export, native construction/overlap/count/mass/material-direction checks pinned to exact revisions |

### Cryostat, cooling and powering are separate questions

**INFERENCE from active media:** silicon/tungsten and polystyrene/steel do not
inherently require a liquid-argon bath or calorimeter cryostat. Cooling may
still require pipes, cold plates, insulation and a dry environment, depending
on selected sensor operation, radiation/power assumptions and condensation
control. No nODD operating temperature is selected by this assessment.
If LAr or another cryogenic active medium is proposed later, add its active
fluid, vessel walls, insulation vacuum, cold supports, feedthroughs and service
volume as a deliberate technology change.

**NODD DESIGN CHOICE — ownership proposal:** the superconducting solenoid owns
its cold-mass cooling, vacuum vessel, thermal shields, leads and penetrations.
Calorimeter modules own local thermal/electrical hardware. The system architect
owns shared routes and any common vessel/support interface. A shared ATLAS-like
cryostat is an option only after active technology and thermal requirements
justify it. Avoid adding an “ATLAS cryostat” layer to a warm Si/scintillator
stack while also retaining a separate full magnet vessel.

For every prototype unit, record dissipated power in W, voltage/current classes,
local conversion losses, channel/ASIC counts and operating duty assumptions;
propagate them to cassette, sector and full-detector totals. Select conductor
and coolant inventories from those loads rather than inventing a uniform
“services thickness.” Thermal capacity and cable packing require engineering
checks, while the detector description records their geometry/material effects.
Front-end timing, pulse shaping, digitization and calibration are separate work.

### Whole-detector fit and magnetic material

**FACT — DES003 E1-R2 reservation:** the coil/cryostat outer allocation is1.64m
and ECAL entrance1.70m; these supersede the original ODD1.25m entrance in that
architecture study. The current tracker software truth region is larger than
DES003's historic tracker reservation (`detector/config/tracker.json` versus
DES003 JSON). Those snapshots cannot be assembled as one current detector
without a joint interface revision.

**INFERENCE:** moving the ECAL entrance outward while keeping its old outer
boundary destroys the available sampling depth. Moving whole ECAL/HCAL stacks
preserves depth but increases detector size and changes support, muon, forward
and service interfaces. A longer solenoid also requires a later endcap front
or a shaped recess. Carry these as coupled proposals, with corner-bounding
radii and locally routed services; do not hide intersections in a drawing.
The companion solenoid baseline PR provides the new proposed dimensions for
joint review; this independent assessment does not adopt its unsigned values.

**INFERENCE:** material assigned for Geant4 tracking is not automatically a
magnetic constitutive model. HCAL absorber, support steel and return structures
must participate in the installed field/force calculation, including magnetic
history/saturation where relevant. A3T vacuum coil estimate cannot certify the
installed central/peak fields or energy, and an effective PCB slice cannot stand
in for a force-bearing support. Assign each part to one material and load ledger.

## Manageable implementation sequence after design decisions

All entries are **NODD DESIGN CHOICE — proposed programme**, subject to human
review. Detector production integration follows signed designs; each prototype
must stay isolated until then. Reuse the tracker approach and existing local
XML/geometry validation patterns; no new external package is requested here.

| Step / bounded PR | Deliverable | Entry and exit evidence |
| --- | --- | --- |
| C0 — hardware/interface contract | ECAL/HCAL technology/operating scope, 3D envelope conventions, solenoid ownership, service exits and prioritized material ledger | Resolve P0 decisions and effective-mixture rationale; reviewed dimension/material/source table with uncertainties |
| C1 — one ECAL module/cassette | Explicit sensor boundaries, absorber/support, readout footprint, cooling and local power inventory | C0 contract; independent count/mass/extent ledger, native single-unit overlap check and sensitive-ID audit |
| C2 — one HCAL tile/cassette | Physical scintillator/readout package, justified absorber/electronics materials, thermal and electrical inventories | C0 contract; compare retained ODD mixture to component mass without response tuning; native unit audit |
| C3 — one barrel sector and one endcap sector | Repeated cassettes, seams/ribs/frames/manifolds/trunks, load-bearing and installation interfaces | Unit evidence; mass/load/power/coolant conservation, extrema and sector routing/packing checks |
| C4 — full barrel/endcaps and shared interfaces | Deterministic complete calorimeter compact/exporter, supports, service exits, magnet/tracker/muon/forward boundaries | Sector evidence; all placements/IDs/materials, full overlap and directional material checks at reviewed tolerances |
| C5 — independent description review | Evidence pack comparable to DES025, approximations/uncertainties and unresolved engineering register | Native DD4hep/Geant4 transport smoke, material/solid/count regressions, source hashes and human review; hardware acceptance only |

Reusable starting points are ODD sampling/readout/factory concepts (MPL-2.0,
retain provenance if copied), the nODD material/source ledger conventions,
parameterized component exporters, shared-service conservation and native
DD4hep overlap/count/mass tools. Reuse does not imply that old radii, mixture
thicknesses or Air placeholders are justified. Additional external calorimeter
frameworks are unnecessary for this assessment. Any future external dependency
must be checked with the user before adoption.

Performance work follows separately: transport response, digitization,
calibration, shower clustering, jets and particle flow. It may reveal a required
hardware amendment, but physical choices must remain independently sourced.
Neither ActsExamples nor Gaudi determines whether supports/cooling/materials
are faithfully described.

## Reproduction and review deliverables

See [audit instructions](../../tools/calorimeter_audit/README.md) and
[inspection evidence](../validation/DES-027/results.md). The static audit uses
Python's standard library, checks pinned source hashes, evaluates only
whitelisted arithmetic/units, sums all repeated layers, checks mixture
normalization and records derived polygon/stack bounds. Four controls cover
unit conversion, unsafe/unknown expressions, nonuniform repeats and invalid
thickness/repetition. No ODD runtime, structural calculation or performance
validation is claimed.

The review should decide C0 priorities and named subsystem/interface owners,
then commission the two representative cassette designs. Unassigned dimensions,
operating parameters and engineering loads remain unknown. No human sign-off
is inferred from this assessment or from merging its PR.
