# DES030 — Sixteen-wedge ECAL prototype checks

Status: **DRAFT / PROTOTYPE**. Corrected per the human's instruction to retain
DES029 drawing B and add edge sensors inside independently produced wedges.
The initial four-quadrant alternative is retained in [its archive](quadrant-study/results.md);
its coverage and IDs do not describe the corrected prototype. No human
engineering sign-off or calorimetric performance acceptance is recorded.

The existing runtime was freshly verified: DD4hep1.38/7deaacd, ROOT6.40.04,
Geant4 11.4.2/cpge6jj, DD4hep/DDG4 imports and configured data directories.
The acts-spack preflight reported changed setup/lock fingerprints and exit2;
actual runtime checks succeeded without installing/changing dependencies.
The existing standalone factory library was reused; its C++ is unchanged.

| Quantity | Compact squares | Squares + custom masks |
| --- | ---: | ---: |
| Sensors per wedge/layer | 76 | 112 (36 custom) |
| Physical sensor volume IDs round-tripped | 116736 | 172032 |
| All logical electrode references checked | 19456 | 22830 |
| Raw fragments checked | 19456 | 23098 |
| Closed-boundary tie probes checked | 608 | 900 |
| Logical channels, both48-layer endcaps | 29884416 | 35066880 |
| Full-face active fraction | 59.98% | 69.47% |
| Native mass, both endcaps | 97.928245t | 98.948639t |
| Continuous heat hypothesis, both endcaps | 60.070kW | 71.051kW |
| Full ROOT overlaps at1e-5mm | **0** | **0** |

[Native squares](native-squares.json) and [native masks](native-edges.json)
retain actual source, expected inventory, compact, library, validator and ROOT
artifact hashes. Both final expected-inventory hashes match the completed
native audits. Execution used parent69b044e and a dirty working tree; exact
source hashes identify the submitted correction. Future merges are untested.

The audit checks actual primitive dimensions/capacities/material fractions,
restricted Boolean cutters, logical placements and proper physical replicas.
All sensor IDs round-trip through the native decoder, including all16 sector
values. Disjoint parent fields plus every logical electrode ID establish
replicated uniqueness without claiming35 million independent cell-position
checks. All raw electrode fragments, interior references and polygon boundary
ties are checked against actual ROOT masks and the C++ segmentation. Maximum
composition discrepancy is1.11e-16. Full ROOT overlap checking was executed in
both cases, not substituted with metadata-only intersection tests.

Each audit also runs64 actual ROOT material rays, including both sides of a
wedge seam. At|eta|4,phi0.03 and pi/8-0.003 cross48 active layers on each end
with custom masks; pi/16±0.003 cross none. Square-only rays at that eta all
cross none. The geometry therefore exposes real seam cracks rather than
claiming uniform forward coverage.

The [360-phi straight-ray samples](directional-coverage.json) give at eta4:
custom masks average32.36/48 active layers,68.89% of azimuth bins with at least
one layer and64.44% with at least40. Squares have zero. Masks repeat through
depth; no seam staggering or charge-response/efficiency model is assumed.
This scan is endcap-only and excludes the unchanged barrel and HCAL.

The catalogue has29 oriented custom profiles,36 custom placements per wedge
and14 small/narrow rejected remainders. Every sensor/PCB stays within a single
wedge and outside the120mm outer service bay. Standard squares are identical
in both cases, including IDs. Minimum retained pad area is6.068449mm2;158
connected electrode groups per wedge merge tiny fragments. All914 unbonded
ASIC channels per wedge/layer count toward the continuous-power hypothesis.

[Saved Geant4 readout checks](transport.json): one10GeV mu- event on each end,
seeds43/44,field0,FTFP_BERT. A custom inner trapezoid (module5,expected pad[-3,3])
saves a positive-energy hit on both sides with the correct complete parent/pad
ID. The negative placement uses a proper rotation. The sparse single-layer
fixture retains plate/cooling/interface material but removes other boards and
frames; it is not full-detector transport or silicon-response qualification.
The fixture hash still matches the completed events after the final metadata
export. All22 hardware controls passed, including independent wedge/service
containment, intact-square stability and forward/crack negative controls.
All28 project-record/document-link controls passed, and the project validator
accepted63 tasks,36 documents and19 review rounds.

The [single-wedge drawing](../../design/figures/DES-030/wedge-carrier-with-edge-sensors.svg)
and [four-stage comparison](../../design/figures/DES-030/four-stage-coverage.svg)
were visually inspected. Historic ODD/nODD retain their original sizes and
area denominators. C/D share the complete16-gon face minus its100mm-apothem
16-gon aperture, including supports/services; custom masks gain9.48points.
No new native ODD build is claimed. Mechanical/thermal/hydraulic engineering,
grouped full/half-board routing, sensor mask/process/HV qualification, machine
aperture and numerical sampling acceptance remain open.
