# SESSION-2026-10-13-calorimeter-edge-sensors — Physical masks and optimized ECAL

User request (exact excerpt): “Please design custom edge sensors and update the
layout. Make a svg drawing showing” the initial ODD coverage, first roughly30%
nODD coverage, optimized squares and optimized squares with edge sensors.
The user clarified: “Extend optimized layouts toward |η| = 4 (prototype target)”.
Starting source cfa20cf6e02572bc90485c78966e6d61b15d1025, clean; dedicated branch
codex/calorimeter-edge-sensors. No production integration or engineering sign-off.

DES030/ADR008 precede implementation. Four quadrant carriers, preserved outer
16-gon/front/layer pitch and a90mm-apothem square aperture with5mm inner support
explore eta4. At3950mm front, eta4 reaches144.742mm; supported aperture corner
is134.35mm. Historical ODD/first nODD apertures do not cover that direction and
are retained visibly in the four-panel comparison. Machine/forward integration
requires review. No claim of uniformly efficient eta4 acceptance is recorded.

A declared0/2/4/6mm grid-phase search prioritizes forward azimuth coverage then
area. The selected compact squares cover83.47% of the new nominal face; custom
edges increase it to88.12%.423 standard squares and39 edge sensors per quadrant
use22 oriented masks (rectangular/trapezoidal, chamfered and triangular), matching
PCBs and explicit2mm passive guards.6 undersized/narrow candidates are rejected.
Minimum pad area6.150155mm2 follows connected merging of small fragments;84
merged groups per quadrant. ASIC fit/thermal footprints are explicit. Acute tips,
dicing/HV process, radiation/charge response and mechanics remain unqualified.

New nODDEdgeGrid maps shaped electrodes/merged IDs to interior reference points
and bounds. Grid-derived module IDs keep squares stable when edge units are
added. Closed grid-edge ties map to physical interior electrodes, not ghost bins.
Full endcap stacks retain W/Si layers, supports and10mm rear covers. A3mm Cu
plate contains Ti/water channels; displaced Cu and all packages are counted.
Continuous heat includes unbonded ASIC channels; no power-pulsing saving or
unused-channel shutdown is assumed. Shared8192-channel/2W interfaces and cooling
run/port allocations are project hypotheses; external hydraulic connections,
thermal/structural and machine-interface qualification remain open.

Existing acts-spack preflight returned changed fingerprints/exit2. Fresh setup
verified DD4hep1.38/7deaacd, ROOT6.40.04, DDG4, Geant4 11.4.2/cpge6jj and
configured datasets. No shared dependency installation or new software external.
CMake compiled the additional factory/segmentation into the isolated existing
library, retaining policy/CLHEP warnings. Both full native layouts passed actual
shape/material/composition/replica/volume-ID/electrode checks and complete ROOT
overlap checks at1e-5mm. Final edge geometry checks177408 physical sensor volume
IDs,114813 logical electrodes,114897 raw fragments and3706 boundary ties;
zero overlaps. Both endcaps mass101.031654t; continuous heat hypothesis87.053kW.
The square case checks162432 volume IDs/108288 cells/3384 boundary ties, zero
overlaps,100.596492t and81.282kW. Exact hashes are in validation JSON.

The360-phi geometrical scan at eta4 averages43.58/48 active layers,95.56% with
at least one and80% with at least40; zero-hit cracks remain. Native64-ray probes
per layout confirm representative48-layer and zero-layer directions, both ends.
Edges recover the outer perimeter; the aperture/carrier/grid supplies forward
reach. The unchanged barrel is excluded from the endcap-only scan.

Two seeded10GeV mu- single-layer custom-triangle fixtures (43/44) completed
Geant4 and saved positive hits with expected parent/pad IDs on both ends. The
fixture removes other sensor boards and continuous frames, retaining plates/
cooling/interfaces. This is not complete-detector transport or response
qualification. Updated-library legacy regression passed859 parts/148 sensors/
1168 cells/zero overlaps.21 hardware controls and28 project-record controls pass.

Initial native audit rejected unhandled full-circle TubeSeg; strict360-degree
support repaired it. The first ID-stability assertion exposed insertion-based
renumbering; a stale huge dictionary diff formatter was stopped (exit130) after
repairing stable grid IDs, and bounded comparisons now pass. Native audits were
repeated after meaningful changes: ID stabilization, boundary ties and retained
rear cover. Early direct patch context errors changed no files and were repaired.
An unsupported combined document status was changed to DRAFT plus a separate
PROTOTYPE type, without weakening validation. Negative fixture direction was
corrected for the proper Rx(pi) transform before its final transport run.

The SVG/PNG shows all four requested stages, each front-plane eta contours,
explicit historical dimensions/denominators and example sensor/electrode masks.
Visual inspection found text crowding; manual spacing/title placement corrected
it. Source/placement drawings are not new native ODD renderings. Source catalogue
records the HGCal partial-mask precedent separately from new project parameters.
Files/actual check results are listed in the paired JSON. PR versioning metadata
is added after creation; no human review or sign-off is inferred.

Exact current client token counters are unavailable; usage stays empty/unknown,
not zero. No previous observations or private client state are copied.
