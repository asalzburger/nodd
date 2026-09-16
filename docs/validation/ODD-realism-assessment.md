# ODD realism and suitability as an HL-LHC reference

- ID: M0-ODD-REALISM
- Status: DRAFT — source assessment; expert review pending
- Date: 2026-09-16
- Scope: full detector; simulation-relevant component usage, not manufacturing CAD
- Related: [PROJECT](../../PROJECT.md), [ADR-001](../decisions/ADR-001-upstream-baseline.md), [ADR-003](../decisions/ADR-003-validation-and-artifact-policy.md), [M0-BASELINE](M0-baseline-specification.md)
- Reviewer / issue: unassigned / not created
- Source: SRC-ODD-UPSTREAM, study revision `c167363f3d4ad1540a577af99071283caf54f3a6`
- Evidence: [static inventory](odd-realism-evidence.json), [source snapshot](../../reference/odd-study-snapshot-2026-09-16.json), [catalogue](../../reference/manifest.yaml)

## Executive assessment

**INFERENCE:** ODD is a valuable open detector and algorithm-development reference,
with appreciably more physical structure than a collection of ideal measurement
surfaces. Its reusable factories, explicit passive tracker components, sampling
calorimeters, muon tubes and existing simulation/reconstruction checks make it a
credible starting point for nODD. Its principal strength is a public, inspectable
experimental environment for studying algorithms and simulation workflows.

**It is not yet justified to treat this ODD revision as a quantitatively faithful
HL-LHC detector reference across all subsystems.** The weakest points are the
physical justification of component/material choices, coherent magnet and service
integration, dedicated precision timing, and demonstrated response under operating
conditions. Fine segmentation and Geant4 transport alone do not establish those.
This conclusion concerns applicability, not whether ODD meets its own stated
algorithmic-demonstrator purpose [E01].

There is no defensible single “realism percentage”. Use the following judgments
per use case. These are **INFERENCE**, based on the evidence below, not acceptance
scores or measured performance.

| Use case | Assessment | Boundary on conclusions |
| --- | --- | --- |
| Public DD4hep/ACTS development, regression, teaching | Strong foundation | Pin the complete environment and reproduce the relevant tests |
| Tracking and ML at high hit multiplicity | Useful, with configuration-dependent realism | Check occupancy, material, digitization and truth selection; do not transfer efficiencies directly to ATLAS/CMS |
| Generic calorimeter shower and clustering research | Useful sampling geometry | Detector-specific calibration, service material, leakage, saturation and noise remain important |
| Comparing realistic component/layout choices | Useful starting framework; insufficient evidence as-is | Establish physical provenance and material/acceptance budgets before interpreting a change |
| Precision timing / four-dimensional pile-up rejection | Dedicated capability absent from inspected geometry | Hit timestamps or smeared time do not establish a precision timing detector |
| Standalone muon performance / detector-wide missing energy | Weakly substantiated | Field integral, chamber response, forward losses and integrated reconstruction need evidence |
| Predicting ATLAS/CMS Phase-2 performance or lifetime | Unsupported by this assessment | Requires experiment-specific validation or an explicitly bounded surrogate argument |

## Method and limits

This is a static inspection of XML, factories, materials, configuration and CI,
plus existing experimental reading records and a versioned external production
paper. The study checkout is **not** the selected nODD baseline. Upstream file
hashes were checked against the retained snapshot. XML parsing only establishes
well-formedness; it does not execute DD4hep expressions or construct volumes.

**NOT RUN:** DD4hep build/construction, overlaps, mass extraction, directional
material scans, sensitive coverage, Geant4 transport, field sampling, ACTS
conversion, digitization or reconstruction. No physical defect, accuracy margin
or acceptance failure is claimed as a measured result. Upstream CI definitions
are credited as implemented checks, not as proof of a successful run at this SHA.

**FACT** below means an observation about a named source at the recorded version.
**INFERENCE** identifies its likely consequence or the evidence needed. Absence
claims are limited to the inspected included geometry and repository configuration;
external applications can add behavior. Proposed follow-up is advice, not an
approved **NODD DESIGN CHOICE**.

HL-LHC relevance has separate requirements: event density and time structure;
credible technologies and their material/services; response and radiation/ageing
assumptions; coherent fields and acceptance; and validated reconstruction. Meeting
one does not establish the others. We do not require an ATLAS/CMS replica, nor
penalize the omission of CAD features without a material or response consequence.

## Subsystem findings

### Pixels: useful geometry, incomplete hybrid-module representation

**FACT [E02]:** the XML defines four barrel layers and seven disks on each side,
with 0.05 mm × 0.05 mm readout cells. The barrel module consists of a silicon
sensor, Kapton board and aluminium connector. The helper uses half the supplied
`dx/dy/dz` when constructing a Box: the sensor is 16.8 mm × 72 mm × 0.125 mm,
not twice those dimensions. Endcap sensors are trapezoidal. Staves, carbon
supports, titanium pipe shells and copper cable volumes are present.

**INFERENCE:** this supports discrete hits, realistic incidence effects and
nonzero local/service material. Calling it a bare-sensor toy would be unfair.
However, no explicit readout die, chip periphery, bump-bond layer or chip tiling
appears in these pixel module definitions. The board/connector materials do not
by themselves document an effective replacement for that assembly. A 50 μm cell
pitch does not make it an RD53 module. Trapezoidal sensors require an explicit
readout/tiling rationale before being treated as hybrid-pixel hardware.

The already-read CMS TDR §4.2/PDF 74 describes sensor/chip bonding, flex and mounting
strips; §4.2.2/PDF 81–83 relates readout to remote optical conversion and powering
[SRC-CMS-TDR-014; E11]. These establish concrete comparison questions, not new
nODD dimensions. Missing chip material can affect scattering and conversions;
missing inactive periphery can affect coverage. The size and even net direction
of the total material bias cannot be inferred without an accounting comparison.

### Outer tracker: real stereo structure, ambiguous measurement contract

**FACT [E03]:** short strips have four barrel layers and six disks per side;
long strips have two barrel layers and six disks per side. Long-strip barrel
modules contain two sensitive sensors, one with `alpha=0.04`, and passive
board/connector/support components. XML readouts use two-dimensional Cartesian
cells: 0.075 mm × 0.5 mm for short strips and 0.15 mm × 1.5 mm for long strips.

**FACT [E04]:** the separate ACTS geometric digitization file specifies short-strip
bin widths of 0.08 mm × 0.5 mm, and a single measured index for long strips with
first-coordinate bin widths of 0.10 mm in the barrel and 0.125 mm in endcaps.
Widths here are calculated as `(max-min)/bins`; the remaining long-strip bin
spans the sensor and is not a second measured coordinate. The included tracking
CI instead selects the smearing configuration.

**INFERENCE:** these are distinct readout/digitization contracts. They may be
intentional representations for different applications; they are not automatically
a bug. They must be mapped explicitly before quoting occupancy, channel counts,
resolution or cross-chain agreement. Paired/stereo sensors are a strength, but do
not establish a CMS momentum-selecting module or an ATLAS strip architecture.
Physical strip lengths, measurement dimensionality, hybrid material and any
trigger assumption need an explicit technology choice and comparison.

### Timing: a clear missing subsystem

**FACT [E01, E04]:** the included detector tree has tracking, calorimeters and
muons, with no dedicated timing assembly. A tracker smearing configuration
includes a time-coordinate entry; that is a response setting, not timing hardware.

**INFERENCE:** precision timing studies need a reviewed coverage and technology
model, its passive/services material and time response. Timestamp availability
alone cannot support timing-assisted pile-up rejection claims. Existing registered
HGTD/MTD sources are follow-up inputs, not evidence that ODD implements them.

### Electromagnetic calorimeter: detailed sampling, generic hardware

**FACT [E05]:** both barrel and endcap define 48 repetitions with tungsten-alloy,
G10, ground/HV mixture, 0.50 mm sensitive silicon, air and PCB mixture slices.
Readout cell size is 5.1 mm. The header identifies a lepton-collider/DD4hep design
lineage. The barrel gap parameter is zero; the endcap gap parameter is 0.25 cm.
Factories explicitly create layer/slice volumes and layered calorimeter metadata.

**INFERENCE:** this is substantial shower-simulation structure, including passive
electronics mixtures. It is useful for high-granularity calorimetry research.
It does not establish a realistic ATLAS or CMS barrel/endcap implementation.
Physical wafer edges, module cassettes, cooling, connectors, service exits and
transition material need justification. A uniform cell grid is a logical readout,
not proof that physical sensors can tile every sensitive slice without losses.
Zero configured barrel gap must not become an implicit claim of gap-free hardware.
Validate upstream material, cracks, shower profiles, leakage and calibration
before interpreting energy resolution or particle-flow confusion quantitatively.

### Hadronic calorimeter: plausible concept, high-impact material question

**FACT [E06]:** barrel and endcap use 36 repetitions of 30 mm Steel235, 16 mm
`siPCBMix`, 3 mm sensitive polystyrene and 2 mm air, with 30 mm cells. The air slice
is commented as space for services. The material definition gives `siPCBMix`
density 5.05076923076923 g/cm³ and copper mass fraction 0.818763326226013.

**INFERENCE (arithmetic, not a measured scan):** a normal path through the repeated
PCB-mixture slices has thickness `36 × 1.6 cm = 57.6 cm`, and areal mass about
`57.6 × 5.05077 = 291 g/cm²`. This is a major passive contribution, not incidental
PCB detail. It could represent an intentional effective absorber/electronics
mixture; the name and comments do not establish its component inventory or
normalization target. Review that rationale before retaining or “correcting” it.
The calculation excludes incidence, boundaries and other layers, and is not an
interaction-length estimate.

Air reserved for services does not supply cable/coolant mass. Sensor light
collection, photosensor response and saturation are separate assumptions from
Geant4 energy deposition in polystyrene. Establish effective-material meaning,
longitudinal response, leakage, dead regions and calibration before treating this
as a realistic HL-LHC hadronic response. An arbitrary energy-scale correction
would not repair an incorrect longitudinal material distribution.

### Muons: chambers exist; a spectrometer is not yet established

**FACT [E07]:** the source includes three barrel and four layers per endcap,
with sensitive ArCO2 tube volumes and aluminium shells. Generic tracker-sensitive
behavior and 20 mm × 20 mm Cartesian readouts are configured. The barrel factory
scales alternate chamber dimensions **and tube radii** by 0.9. It attaches
calorimeter-style envelope metadata for downstream use. The ArCO2 material uses
atomic composites `Ar:1, C:1, O:2` and a specified density.

**INFERENCE:** explicit gas and tube walls are useful for transport and hit
studies. Scaling tube diameter with chamber size needs a technology rationale;
realistic inventory should explain whether these are distinct tube families.
A named gas mixture requires a documented composition convention and operating
conditions; this definition alone does not establish the intended drift-gas ratio.
Neither a sensitive gas volume nor envelope metadata establishes drift-time
response, resolution, efficiency, high-rate capability or muon reconstruction.
No explicit sense-wire volume or drift-response implementation was found in the
inspected chamber factories. The material effect of tiny wires may be negligible;
the measurement model is the more important unresolved issue.

Do not infer missing muons from the 2023 presentation's future-work language:
this revision contains them. Conversely, geometry presence does not establish a
working, field-consistent standalone spectrometer or an HL-LHC background model.

### Magnets, beam pipe and detector-wide integration: weakest physical closure

**FACT [E08]:** the solenoid is a single aluminium cylindrical shell, with radii
1160–1200 mm and half-length 3 m. The ECal barrel starts at radius 1250 mm: this
coil model is upstream of the calorimeter. Full steering selects the DD4hep
solenoid field with nominal inner/outer parameters 3 T / 0.5 T and finite axial
extent. The beam pipe is a beryllium cylinder. No separate cryostat or return-yoke
assembly is included in the inspected detector tree.

**INFERENCE:** a shell can be an acceptable effective material model if mass,
composition and angular material targets are documented. Here it does not establish
a complete coil/cryostat/service or flux-return design. These choices matter for
pre-calorimeter losses, conversions, muon scattering and bending. Do not equate
an `outer_field` parameter with a validated field in all muon stations: sample the
actual plugin field and trajectory integrals, including fringe/end regions, and
compare simulation and reconstruction. Absence of a yoke is not intrinsically
wrong, but an alternative magnet concept must explain the field/material layout.

The beam-pipe cylinder does not establish realistic forward transitions, shielding
or machine backgrounds. Full-detector claims need shared envelopes, forward
coverage, penetrations and service routes with no omissions or double counting.
Layer counts and envelope extents do not establish sensitive η/φ acceptance.

### Services and materials: modeled in places, not yet reconciled globally

**FACT [E02, E03, E09]:** tracker XML/helpers explicitly place support structures,
cables, cooling routes and pipe shells. The reviewed cooling helper constructs
volumes from the specified pipe material; it does not insert a separate coolant
core. Calorimeters use mixture layers and air allowances.

**INFERENCE:** the question is whether these volumes account for a believable
component inventory. Pipe shells without a documented fluid/effective equivalent,
solid copper cable bundles without a specified cable makeup, and homogeneous
boards without their component breakdown leave the material budget uncertain.
No end-to-end power/data/cooling inventory linking loads to these geometries was
established in this pass. Validate mass, composition and directional material,
including service concentrations and cross-system routes. Do not simply add
more material: some existing effective volumes may already represent it.

## Response, operating conditions and validation maturity

**FACT [E10]:** upstream CI defines construction of tracker/full detector stages,
overlaps, Geant4 smoke tests, material recording/comparison and ACTS tracking
regressions. Calorimeter CI includes photon and pion energy scans in barrel and
endcap directions. These are meaningful assets worth preserving. The tracking
script uses a two-muon gun, Fatras and smeared measurements, not a full HL-LHC
collision/pile-up validation. The inspected calorimeter jobs cover selected
energies/directions, not a detector-wide response map. Artifacts expire after
one month in these definitions; retained reference ROOT files also exist.

**FACT [E12]:** ColliderML v1 describes 14 TeV collisions with mean pile-up 200,
Geant4 production and ACTS geometric tracker digitization. Its calorimeter model
applies timing/energy selections; additional noise/saturation modeling is deferred.
Its first-release reconstruction centers on tracking, with broader reconstruction
planned. This is evidence for an external production chain, not validation of
our study checkout. [ColliderML, §§3–5](https://arxiv.org/html/2512.15230v1)

**INFERENCE:** therefore it would be incorrect to say ODD cannot support high
pile-up, or has no digitization. The actual limitation is the lack of a demonstrated
connection between this exact geometry/configuration and the intended claims.
A demanding event sample does not supply radiation ageing, channel failures,
readout dead time, bunch-history effects or detector-specific calibration.
The sign of resulting algorithm/performance bias is not reliably predictable.
Regular geometry and idealized response can also become features learned by ML;
robustness needs controlled variations and transfer tests.

No radiation-dependent material/response or lifetime-performance contract was
established from the inspected configuration. Such models can live downstream;
record them with their versions if used. Do not interpret this inspection as an
exhaustive audit of every external ODD-based project.

## Prioritized gaps and evidence needed

Priorities below are proposed assessment follow-up, not signed-off implementation.
“First” identifies dependencies on defensible conclusions, not a numerical severity
score. Each gap has a closure artifact so that it can be reviewed and retired.

| Gap ID | Priority | Gap / risk | Required closure evidence |
| --- | --- | --- | --- |
| ODD-G01 | First, M0 | Unselected version/configuration and unknown runtime validity | ADR-001/003 selection; build, overlaps, identifier/count/coverage checks with retained logs |
| ODD-G02 | First, M0 | Field/material architecture not physically closed | Coil/cryostat/return concept inventory; field samples and trajectory integrals matched across tools |
| ODD-G03 | First, M0 | XML versus ACTS measurement contracts | Per-subsystem table of physical sensors, readout, digitization, units/axes/IDs and resolution assumptions; executable cross-checks |
| ODD-G04 | First, M0 | Material inventory and effective-mixture rationale | Mass and η/φ material scans; component accounting, especially HCal PCB mixture and cooling/services |
| ODD-G05 | Next, design | Pixel/strip module realism | Public-source comparison of die/sensor/inactive regions, hybrids, bonds, supports and services; justified effective representations |
| ODD-G06 | Next, architecture | Dedicated precision timing absent | Reviewed technology/coverage, material and response specification; quantify intended pile-up use |
| ODD-G07 | Next, design | Calorimeter mechanical/readout/response realism | Module/cassette and interface inventory; energy/angular shower scans, leakage, noise/saturation and calibration contract |
| ODD-G08 | Next, design | Muon technology/field/response unsubstantiated | Tube/gas/chamber review, active crossings and field integrals, drift/efficiency assumptions and reconstruction checks |
| ODD-G09 | Next, architecture | Forward/shared services and acceptance | Integrated section views, routed service accounting and sensitive/absorbing coverage including transitions |
| ODD-G10 | Before HL-LHC performance claims | Operating-condition and transfer validity | Selected pile-up/time/radiation scenarios; response variations, uncertainties and comparison with dated public reference observables |

The first useful deliverable is a **full-detector baseline**, not an immediate
geometry rewrite. Retain ODD as a control and measure the changes attributable to
reviewed nODD assemblies. Requirements for calo/muon/magnet interfaces should be
considered while developing the initial pixel case. A common material and response
contract matters more than adding decorative detail everywhere.

Before claiming an “HL-LHC reference”, publish an applicability statement naming
validated observables, geometrical/operating ranges, response assumptions and
known limitations. Agreement in a tracking-efficiency plot cannot certify
calorimeter response, timing or muon acceptance. Remaining experimental TDR and
production-literature extraction is needed for quantitative target setting;
this assessment has not completed that comparison or selected target tolerances.

## Evidence register

All E01–E10 paths are relative to the immutable
[SRC-ODD-UPSTREAM tree](https://gitlab.cern.ch/acts/OpenDataDetector/-/tree/c167363f3d4ad1540a577af99071283caf54f3a6).
Use the named XML elements, functions or CI jobs as precise locators; byte hashes
are retained in the linked static inventory/snapshot. Paths are source locators,
not dependencies on committing the ignored checkout.

| ID | Source locations / evidence |
| --- | --- |
| E01 | `xml/OpenDataDetector.xml`, `info`, included detector stages and `fields`; stage includes under `xml/OpenDataDetector{Tracker,Calorimeter,MuonSystem}.xml` |
| E02 | `xml/detectors/TrackerPixels.xml`, readouts, `PixelBarrelModule`, endcap `ring/module`, stave/services and layers; `factory/tracker/ODDModuleHelper.cpp`, `assembleRectangularModule`/`assembleTrapezoidalModule` |
| E03 | `xml/detectors/TrackerShortStrips.xml` and `TrackerLongStrips.xml`, readouts, barrel modules and detector/layer elements |
| E04 | `config/odd-digi-geometric-config.json`, entries 16–18, 23–25, 28–30; `config/odd-digi-smearing-config.json`; `ci/full_chain_odd.py`, `oddDigiConfig`, particle gun and `addFatras` |
| E05 | `xml/detectors/CalorimeterECal.xml`, header, readouts, detector gap and layer/slice elements; `factory/calorimeter/ODDPolyhedra{Barrel,Endcap}Calorimeter_geo.cpp`, `create_detector`/slice construction |
| E06 | `xml/detectors/CalorimeterHCal.xml`, readouts and layer/slice elements; `xml/OpenDataDetectorMaterials.xml`, `siPCBMix` and `Steel235` |
| E07 | `xml/detectors/MuonSystem.xml`, readouts/layers/chamber tube definitions; `factory/muons/ODDMuon{Barrel,EndCap}_geo.cpp`, `create_element`; materials XML `ArCO2` |
| E08 | `xml/detectors/Solenoid.xml`, `BeamPipe.xml`; `xml/OpenDataDetectorEnvelopes.xml`, `sol_*`, `ecal_b_rmin`, `bp_*`; steering XML solenoid field |
| E09 | `factory/tracker/ODDServiceHelper.hpp`, routing and cooling-ring volume construction; module helper pipe construction; tracker XML services |
| E10 | `ci/detector.yml`, construction, overlaps, material and ddsim jobs; `ci/calorimeter.yml`, ECal/HCal simulation/validation jobs; `ci/tracking.yml`, `run-full-chain`; `ci/full_chain_odd.py` |
| E11 | SRC-CMS-TDR-014, §4.2 PDF 74; §4.2.2 PDF 81–83, as recorded in [CMS reading guide](../../reference/guides/SRC-CMS-TDR-014.md). [ATLAS guide](../../reference/guides/SRC-ATLAS-TDR-030.md) gives complementary module/material extraction routes; numerical comparison deferred. |
| E12 | SRC-COLLIDERML-PAPER, arXiv:2512.15230v1, §§3.1, 4.1, 4.2, 5; version fixed to 2025-12-17, not a statement about subsequent releases |

Public GitLab web rendering returned HTTP 403 during this pass; the previously
acquired clean public-source checkout and retained hashes supplied the source
content. The external paper was accessible. No inaccessible source is the sole
basis for a required conclusion.
