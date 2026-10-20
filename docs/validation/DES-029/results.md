# DES029 — Executed sector and complete-assembly prototype checks

2026-10-12. **DRAFT / PROTOTYPE**; depends on PR67. Execution used dirty parent
revision9b409b7 (exact SHA in reports) with source/config/compact/library hashes.
Metadata/CI fixes later changed the publication parent without changing executed
geometry. [budgets.json](budgets.json) hashes the reproducible complete inventory;
large placement JSON and ROOT/event products remain ignored.

Fourteen standard-library controls pass: full logical cassette corner/wedge/depth
containment, proper rotations and endcap symmetry, parent-ID uniqueness,
absorber ownership, mass/heat conservation, explicit area loss and negative
controls for invalid dimensions/clearance/readout/material/cuts. Isolated
C++20 factory compiled with DD4hep1.38 / ROOT6.40.04 / Spack Python3.14.5.

[Full native audit](native.json):127,680 cassettes,5,608,960 physical sensitive
elements; every logical cassette/structural transform and every physical sector
replica audited. Primitive/extruded/subtraction capacities and material masses
computed from actual native shapes agree with the analytic ledger. Shared
logical capacities are multiplied by actual checked placement counts; no37M-node
JSON expansion. All native sensor indices/parent ranges checked;384 inherited
ID round trips exercise first/last parents/sensors on every physical replica.
Uniqueness follows disjoint bounded parent fields, not an exhaustive5.6M-ID set.

**Full ROOT CheckOverlaps ran on the complete geometry at1e-5 mm:**39,576,444
candidates, zero overlaps/extrusions; candidate checking418.774 s on one thread
plus about42 s generation/filling. ROOT counted37,044,995 nodes. No checks or
tolerances were relaxed. Initial Xtru reader incorrectly used the zero-argument
GetX/Y API; fixed to indexed access before the successful run.

[Amended unit audit](units-ports.json): ports cut through end rails and tubes
extend flush to faces.859 material parts,148 sensitive elements, all1168 cells,
constituent fractions, masses and10 bounded rays pass; zero overlaps at10 nm.
Each cassette mass decreases by about0.02951 g relative to DES028's original
fixture; the original execution remains in DES028/Git, not overwritten.

57 native ROOT material rays start at the IP: signed eta values0,0.5,1,1.4,
1.7,2,2.4,2.8,3.2,3.6 at three phi values sampling an interior and both sides
of a seam. Positive/negative symmetry is visible in retained data. Paths
include local support/material and physical sensitive crossings. They expose
uniform packing cracks: sampled|eta|≥2.4 has no active crossings despite
absorber traversal. This limits detector acceptance; the geometry audit's PASS
is not calorimeter acceptance or physics performance. Figures were rendered
using existing Matplotlib3.11.2 and visually inspected.

[Geant4 sparse-sector saved-hit audit](transport.json) passes for three seeded
10 GeV mu- events: barrel, positive and negative endcaps at sector0; all plates/
frames retained, one selected cassette per layer. FTFP_BERT, seed42, no field;
all saved calorimeter hits have positive energy and valid parent/cell IDs in the
fixture and full source inventory. This verifies hierarchy/rotations, not full
sector occupancy, complete detector transport or silicon/scintillator response.
Two initial complete-sector fixtures converted successfully to Geant4 but were
stopped during expensive initialization; no completed events claimed for them. ACTS tracker conversion is not applicable here;
calorimeter response/digitization, jets/PF, combined tracker/solenoid geometry,
external services, mechanics and thermal/electrical qualification remain outside
this isolated hardware prototype. No new external software was introduced.

[Reproduction guide](../../../tools/calorimeter_hardware/README.md),
[DES029](../../design/DES-029-calorimeter-assemblies.md) and the
[paired journal](../../../logs/codex/SESSION-2026-10-12-calorimeter-assemblies.md)
retain commands, classifications, failures and limits.

[Independent persisted-geometry dimension audit](shapes.json) checks1045 unique
material shapes, polygon vertices/depth, primitive dimensions and444 CSG cutter
translations/rotations at1e-7 mm tolerance. The imported ROOT hash must match
the completed full native overlap report. This supplements the mass/capacity
checks without repeating or replacing the full overlap scan. It passed.
