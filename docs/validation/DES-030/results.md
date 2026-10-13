# DES030 — Custom ECAL edge sensor prototype checks

Status: **DRAFT / PROTOTYPE**. No engineering sign-off, detector acceptance or
calorimetric performance qualification. All evidence is from the existing local
DD4hep1.38, ROOT6.40.04 and Geant4 11.4.2 installation; no new dependency.
Spack registry fingerprints differed; fresh setup, imports, compilation and
configured Geant4 datasets were verified before execution.

| Quantity | Compact squares | Squares + custom edges |
| --- | ---: | ---: |
| Sensors per quadrant/layer | 423 | 462 |
| Native physical sensor volume IDs checked | 162432 | 177408 |
| All logical electrode references checked | 108288 | 114813 |
| Raw electrode fragments checked | 108288 | 114897 |
| Polygon boundary ties checked | 3384 | 3706 |
| Logical channels, both48-layer endcaps | 41582592 | 44088192 |
| Active nominal face fraction | 83.47% | 88.12% |
| Native mass, both endcaps | 100.596492 t | 101.031654 t |
| Continuous heat hypothesis, both endcaps | 81.282 kW | 87.053 kW |
| Full ROOT overlaps, tolerance1e-5mm | **0** | **0** |

[Native squares report](native-squares.json) and [native edge report](native-edges.json)
retain exact source/compact/expected/library/ROOT-artifact hashes, actual material
rays and runtime versions. Runs used the recorded source snapshot on parent
cfa20cf with the working tree dirty; exact source hashes identify the submitted
implementation. This is not a claim to have tested a future merge commit.

The audit reads actual native primitive dimensions/capacities, densities and
compositions, verifies all logical placements and physical replicas, and scales
actual capacities by observed replicas. Boolean subtraction capacities require
contained cutters and disjoint transformed bounding boxes. Maximum elemental
mass-fraction discrepancy is1.11e-16. All sensitive
volume IDs round trip; disjoint parent field ranges plus all logical pad IDs
prove replicated channel uniqueness without claiming44 million exhaustive
cell-position tests. Full ROOT overlap checking was executed in each layout;
its final checking phases took50.0179s/46.477s on this node.

The custom catalogue has22 oriented profiles and39 placements per quadrant;
6 undersized/narrow remainders are rejected. Minimum retained pad area is
6.150155mm2.84 small electrode groups per
quadrant merge connected raw fragments. Closed grid boundaries map to existing
interior references; no ghost-bin or outside-mask reference is returned.
Every installed ASIC channel is included in the heat budget, including1155
unbonded channels per quadrant/layer. Interface capacity8192channels/2W and
converter efficiency0.9 are prototype hypotheses, not electronics qualification.

[Directional samples](directional-coverage.json) use360 one-degree azimuth bins,
centred at0.5,1.5,... degrees, at each listed eta. At eta4 both new masks average
43.58 active layers;95.56% of sampled phi crosses at least one layer and80%
crosses at least40/48. Narrow aligned seams/board gaps remain, including zero-hit
rays. Native probes at eta4/phi0.4 and pi/4-0.003 cross48 layers on both ends;
phi0.03 and pi/2-0.003 cross none. Custom perimeter sensors improve sampling near
the outer endcap boundary; the new aperture/carrier/grid supplies forward reach.
The scan excludes the unchanged barrel and is not an efficiency prediction.

[Saved transport checks](transport.json) verify two seeded10GeV mu- events
(seeds43/44, zero field, FTFP_BERT): one custom-triangle module in a single layer,
proper positive/negative placements and retained plate/cooling/interface material.
Both saved one positive-energy hit with the expected parent/module/pad ID.
Other sensor boards and continuous frames were removed from this sparse fixture.
No full-detector transport or silicon charge response qualification is claimed.

The existing cassette regression also passed:859 native material parts,
148 sensitive IDs,1168 checked cells and zero overlaps.21 standard-library
hardware controls and28 project-record controls passed. Earlier checks exposed
TubeSeg handling and unstable inserted-module IDs; those were repaired without
relaxing tolerances. A stale assertion diff formatter was interrupted after the
ID fix; the final bounded controls pass. Geometry checks were repeated after
ID stabilization, boundary-tie handling and retention of the rear cover.

The [four-stage SVG](../../design/figures/DES-030/four-stage-coverage.svg) is a
source/placement-derived drawing, visually inspected with its PNG preview.
Historical ODD and nODD retain their own dimensions and denominator definitions.
C/D share the same new denominator, including support/service losses. No new
native ODD construction is claimed. Manufacturer masks/guards/tip treatment,
machine/forward aperture, support strength, hydraulic connections/thermal
performance and digitization/reconstruction remain subjects for review.
