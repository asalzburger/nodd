# DES032 — executed LAYOUT-002 barrel prototype checks

Status: **PROTOTYPE**, no engineering/response acceptance. Execution source:
ced5a39183f4335b426a6b10fd03eb83a603df42; the recorded dirty flag includes the
prepared review journal. Scientific producer files are bound individually by
SHA-256 in the retained reports and ignored compact/expected artifacts.

| Actual check | Result |
| --- | --- |
| C++ build, isolated DD4hep barrel plugin | PASS after qualified DDSegmentation base-name correction |
| Python geometry/readout/service negative controls |12 passed |
| Complete native barrel, both end closures and all service daughters | PASS |
| Full ROOT overlaps/extrusions,10nm,seed37 |0 |
| Native sensitive raw volume IDs / logical merged channels |33,792 /2,285,568 |
| Native canonical reference keys / grouped hit inverse checks |2,976 /23,808 |
| End-grid ghost rejections |22 |
| Complete model material mass |252.507699t |
| Actual native boundary rays |45 signed-eta/fixed-phi rays |
| Geant4 sparse fixture transport and saved IDs/energy |1 seeded10GeV mu− event;1 positive-energy canonical hit |

Reports: [native](native.json), [services](services.json),
[transport](transport.json).
[Service cross-section](../../design/figures/DES-032/barrel-service-packing.png)
and [material rays](../../design/figures/DES-032/barrel-material.png) were
rendered and visually inspected. Sparse ray lines connect sampled points, not
an interpolated acceptance measurement.

The native audit verifies every replica transform/raw ID and shared shape,
actual circle/polygon vertices/depths, two-section unshifted/unit-scale
extrusions, full-azimuth native tubes and Boolean placement. It integrates
native polygon–circle sections analytically; ROOT's stochastic Boolean
Capacity is not used as an exact mass. Mother mass excludes its actual daughter
capacities; elemental mass fractions and densities are checked. Both active
gaps share canonical merged cells only after separately validating physical
raw IDs and inverse/reference positions.

The saved Geant4 fixture contains two complete adjacent inclined periods and
starts a muon inside a layer5 gap. It omits the cryostat/services and proves
sensitive-hit serialization/canonical fields, not complete-barrel transport.
Existing DD4hep1.38 / ROOT6.40.04 / Geant411.4.2,FTFP_BERT,B=0,seed42 were used.
No external package or physics response model was imported.

## Reproduction and retained boundaries

See [workflow](../../../tools/lar_calorimeter/README.md) for export/build/native
commands. Native library, compact, material, expected inventory, ROOT output
and checker hashes are retained. Generated build artifacts are ignored, not
pretended to be public reusable binaries. Runtime activation follows acts-spack.

Preflight found changed Spack setup/lock fingerprints (exit2); actual installed
imports/data paths and native capabilities were verified before these runs.
Earlier build failed on ambiguous Segmentation; native audit initially rejected
a full-circle TGeoTubeSeg; the guard now verifies full360degrees explicitly,
with no overlap tolerance relaxation. First saved-hit checker used the wrong
EDM4hep tree/member names; corrected to the observed events/energy schema,
then the actual event was checked. Failures are retained in the paired journal.

No complete detector cross-system construction, pressure vessel, radiation,
electrical/thermal/hydraulic network, headers/feedthroughs, shower calibration,
ACTS conversion, jets/particle flow or enlarged-HCAL field solution is claimed.
Independent assessments refer to the exact implementation revision; their
findings and remediation are curated below and in the session journal.

## Exact-revision independent findings and corrections

SysArch and PhysVal read ced5a39183f4335b426a6b10fd03eb83a603df42 without
editing or running native jobs. Both passed12 in-memory controls. PhysVal
independently integrated all88 straight-face sections to4.88e-11 relative
agreement with the polygon/circle kernel. SysArch checked board/ring/cooling
clearance, lane area and HCAL corner convention; no P1 default placement defect.

Corrections: unsupported named packing amendments now fail explicitly rather
than silently leaving literal geometry; nominal electrical loop is40m for20m
one-way routing (1.19V/103.7W station loss);1.246mm gap is labelled as the
thinner source control;50kHz is maximum triggering rate with a chosen64-bit
hit payload. S-bend reports separately identify centreline and full-OD envelope
inflation. Saved hits must belong to real constructed theta groups and a bound
successful DDSim invocation; ghost-cell controls were added. Native rays now
enforce finite-volume crossing, active-LAr bounds, finite/nonnegative material
and expected full compartment depth for rays geometrically contained in it.

The258kW adverse planning case versus200kW cooling, cold-converter loss and
missing actual chip/spreader thermal contact are retained as unresolved
engineering limits. No agent supplied human sign-off.
