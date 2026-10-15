# DES036 common HCAL readout module

**PROTOTYPE / DRAFT.** This isolated module starts the user-authorized 14 TeV
hadron-collider work in [DES036](../../docs/design/DES-036-hcal-common-readout-module.md).
The production detector and the existing DES028/029 prototypes are unchanged.
No human engineering sign-off, radiation qualification, optical response,
ASIC emulation, sustained throughput, thermal/hydraulic qualification or shower
performance is implied.

## Generate and check

From the repository root, using only the Python standard library:

```sh
python3 -B tools/hcal_readout/export.py --output /private/tmp/nodd-hcal-readout
python3 -B -m unittest discover -s tools/hcal_readout -p test_readout.py -v
```

`--no-absorber` removes the optional, once-only, sector-owned 30 mm steel
reference patch. This never changes module/carrier mass or selects HCAL depth.
The separate CMake project is built explicitly by the native-validation workflow:

```sh
cmake -S prototypes/hcal_readout -B /private/tmp/nodd-hcal-readout-build
cmake --build /private/tmp/nodd-hcal-readout-build
```

DD4hep 1.38 or later and the node-specific environment preflight are required for
those CMake commands. The library/factory is `nODDHCALReadoutPrototype`; load it
before loading `readout.xml`. No production CMake includes this directory.
Native/transport checks are maintained by the coordinator in separate tools;
the standard-library tests alone do not establish their success.

## Inventory and representation

`config.json` centralizes unsigned fixture dimensions, recipes, operating choices
and source classifications. Two 184 mm square, 6 × 6 boards share a
380 × 240 × 12 mm carrier. Each has 36 connected ordinary tile inputs, 36 unused
ordinary inputs and six auxiliary channels; all 78 channels per chip are powered.
A 2 mm PCB seam and a 6.3 mm scintillator-core seam remain physical gaps.

The SiPM reference is the nominal S14160-1315PS envelope, 2.1 × 2.63 × 0.85 mm,
with package y offset −0.26 mm and active-centre offset +0.26 mm. Its optical
centre is aligned geometrically with the tile centre; no optical tracking or
alignment tolerance study is supplied. The amended effective recess is radius
3.5 mm, depth **1.1 mm**, occupying z = 2.4–3.5 mm, with a rear-reflector opening.
The nominal package occupies 2.70–3.55 mm and solder extends to 3.70 mm.
A 1 × 1 × 0.6 mm direct-front LED sits at tile x + 2.4 mm and z = 3.10–3.70 mm.
The source's maximum height, 1.0 mm, is also tested with the package back anchored
at 3.55 mm; its front is 2.55 mm. A negative control proves that the original
0.9 mm recess fails this maximum-height case. This is a geometric tolerance
screen; full assembly tolerances remain open.

`PSHost` is the distinct undoped C8H8, 1.060 g/cm³ transport material. No historical
C19H21 recipe is edited. Bulk material helpers are imported by a unique module
name. SiPM, LED, front-end/support and connector packages have explicit normalized
silicon/copper/epoxy or copper/epoxy proxy constituents. They preserve only the
selected envelope and mass model; real die, metallization, molding, LED and
connector construction are unqualified. The 0.5 W/module support allocation has
its material allowance in the front-end proxy package. Solder is explicitly
copper-equivalent; no alloy has been selected. PCB copper is an explicit
0.105 mm equivalent foil in the 1.2 mm PCB.

The carrier owns one interface/contact stack, one service board, skins, rails,
one copper plate, four connector envelopes and two Ti/water branches. The plate
has exact rotated cylindrical cuts (r = 1 mm, length = 236 mm). The 240 mm tubes
pass through 2.2 mm square rail ports to four external collector handoffs.
There is no closed supply/return or fitted collector model. Both logical data
streams share the physical `carrier_connector_data` envelope: four DAQ lanes and
eight trigger lanes in aggregate. Separate logical endpoints and budgets prevent
reusing trigger capacity for DAQ. Board-to-interface connectivity is a functional
proxy; concentrator, routing, connector ratings, pinout and protocol remain open.

## Export schema and determinism

`expected.json`, `materials.xml` and `readout.xml` are deterministically generated.
No timestamps or absolute output paths are embedded. `execution.commit` and
`execution.dirty` describe the actual checkout; `input_revision` names the pinned
DES036 assignment. `source_sha256` identifies implementation, config, factory,
bulk-material helper and element-table bytes separately from the Git revision.
`export_sha256` records material/compact XML hashes. Export again after source or
execution-revision changes before making native comparisons.

The expected inventory contains:

| Key | Contract |
| --- | --- |
| `parts` | Flat physical parts with unique `name`, `role`, `owner`, `material`, `center_mm`, `frame`, `shape_kind`, `dimensions_mm`, `cuts`, exact `volume_mm3`, `mass_g`; sensitive parts also have `module`,`sensor` |
| `frame` | Three local basis vectors expressed in carrier coordinates, as rows; transpose into XML `a00`…`a22` |
| `cuts` | `kind`, `center_mm`, `frame`, `dimensions_mm`, relative to parent solid |
| `materials` | Density, normalized composition/basis and effective volume fractions where used |
| `material_totals` | Material volume/mass including the optional fixture absorber |
| `mass_g`, `carrier_and_modules_mass_g` | Inclusive fixture mass and independent carrier/module mass |
| `module_mass_g`, `shared_carrier_mass_g` | Exclusive ownership roll-up |
| `modules`, `channel_map` | Connected/unused/auxiliary ownership, physical centres, chip/channel, volume IDs, local cell `(0,0)` |
| `services` | Cooling collector handoffs, connector ownership and distinct DAQ/trigger functional links |
| `budgets` | Continuous heat, nominal/current stress cases, ideal flow, separate interface comparison, DAQ/trigger and latency arithmetic |

The bit-field descriptor is
`system:8,side:2,sector:4,layer:6,carrier:12,module:2,sensor:6,x:-1,y:-1`.
System is 9, side/sector/layer/carrier are zero, module is 0 or 1, and sensor is
0…35. Each sensitive tile owns a 30 mm CartesianGridXY with offset zero and one
physical cell; segmentation is local to that tile and does not fill board seams.
Module bits start at bit 32, sensor bits at bit 34. No reconstruction/digitization
response or readout timing is simulated by these identifiers.

## Validation scope

The analytic capacity model admits axis-aligned boxes/cylinders and signed
permutation frames only. Subtraction cutters must be contained and disjoint;
unsupported CSG families fail explicitly. Exact primitive intersections and
partitioned cut coverage test this fixture's physical fit, including packages in
recesses and tubes replacing copper. Native TGeo/Geant4 checks independently test
the executed CSG; their results should be cited separately.

Controls reject invalid channel/auxiliary ownership, duplicated IDs/parts/shared
ownership, hidden power-pulsing, inadequate latency, invalid mixtures, module/
connector/LED overlap, wrapping clearance, uncontained/overlapping cuts, blocked
ports, shortened cooling handoffs, and corrupted masses/service budgets. Export
repeatability is tested byte for byte. The nominal DAQ budget uses 93.75% of the
assumed payload capacity; the 1 MHz stress case is explicitly **OVERLOAD** at
125%. Neither the nominal arithmetic result nor the 12-sample ideal latency
margin certifies sustained readout or timing closure.
