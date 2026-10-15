# DES038 analytical endcap HCAL design

**PROTOTYPE / DRAFT.** This is an unsigned proposal using the unchanged
[DES036 common readout module](../../docs/design/DES-036-hcal-common-readout-module.md)
under [DES038](../../docs/design/DES-038-hcal-endcap-common-module.md). The operating
energy is 14 TeV. Radiation, occupancy and lifetime exposure are unresolved.
No production detector, native endcap, shower response or engineering qualification
is delivered by this tool.

## Execute

The Python standard library is sufficient; no DD4hep, ACTS, installation or
runtime activation is needed:

```sh
python3 -B tools/hcal_endcap/design.py --output build/hcal-endcap
python3 -B -m unittest discover -s tools/hcal_endcap -p test_design.py -v
```

Generated layouts and sample tables belong in ignored `build/` output. The
coordinator maintains compact evidence, drawings, tracking and the design record.

## Construction and ownership

The tool imports `tools/hcal_readout/readout.py` under the unique
`_des038_common_readout` alias and calls `build(absorber=False)`. Its actual parts,
material totals, channel ownership, service ports and continuous budgets are
reused. Their executed source hashes must match the corresponding subset of
retained `docs/validation/DES-036/budgets.json` source hashes, and current file bytes
are rechecked before reuse. A changed working common baseline fails explicitly.
No material recipe or common hardware dimensions are duplicated here.
The 30 mm rectangular unit-test absorber is explicitly absent.

Each end has 36 periods of 30 mm steel, the 12 mm carrier and 1 mm installation
allowance, followed by one 10 mm rear cover. The total proposed depth is 1558 mm,
from |z| = 4883.2 to 6441.2 mm. The 16-gon apothems are 300 and 4148 mm, with
10 mm inner and 20 mm outer aluminium frames. Regular-polygon apothems, rather
than circular radii, govern containment and mass. Face normals start along +x.

Whole 380 × 240 mm carriers are selected by exact corner containment in the
4128 mm outer polygon and convex separating-axis exclusion of the 310 mm inner
polygon. Carrier orientations before the layer rotation have global x/y axes;
centre locations are reflected into all four quadrants. Each positive-quadrant
column starts at x = 200 + 400i mm. Its first y front is max(10 mm, the exact
supporting-halfplane aperture-safe front), with subsequent rows 260 mm apart.
The grid preserves 20 mm empty column/row collector reservations. The spaces
are geometric allowances, with no installed material or certified connectivity.

The steel is four polygon-annulus quarters per layer, clipped at x ≥ 10 and
y ≥ 10 mm before their 90° rotations. The axis joints remove steel; empty
collector trunks do **not** remove steel. The inner/outer annular aluminium frames
span the 1548 mm sampling stack, and one annular back cover follows it. Their
exclusive material volumes do not overlap the clipped steel or carrier interiors.
Frame crossing ports, bolts, bearings, collectors, external cables, mounts and
associated masses are absent and explicitly unqualified.

The selected whole-layer patterns cycle through 0°, 22.5°, 45° and 67.5°, rotating
carriers, steel quarter joints and empty reservations together. The 16-gon is
invariant under those rotations. A layer quarter is a grouping, not proof of an
independently extractable quadrant stack. The negative end is the proper global
Rx(π) transform of the entire positive end, including water directions and
connector positions. Frames have determinant +1.

Controls compare aligned uniform rows (`uniform`), aligned aperture-adaptive
rows (`adaptive`), the selected adaptive phase cycle (`staggered`), and adaptive
carriers filtered from the same global adaptive grid to forbid crossing angular
ID-sector boundaries (`narrow_wedge`). It is not an optimized wedge packer. The
wedge case is a packing control: it adds no new wedge material or services.
Sectors in the selected design are angular addresses assigned by carrier centre;
carriers can cross their boundaries and are never cut to fit an address.

## Interfaces and output schema

`build(config=None)` returns a JSON-serializable dictionary. `validate(data)` checks
its geometry/IDs/conservation. `ray_counts(data, eta, phi, scenario='staggered')`
returns `{count, layers, side}` for a straight IP direction, with phi in radians.
Negative eta uses the proper end rotation. `hit_core` provides a point lookup.

| Output | Contents |
| --- | --- |
| `summary.json` | `config`, `summary`, input revision, source hashes, actual checkout commit/dirty state, output hashes and limits |
| `layout.json` | `patterns`, full selected `placements`, `layers`, source-bound `common_prototype_parts`, source hashes |
| `coverage.json` | Per-scenario eta statistics, count and fraction minima/mean/maxima, zero/partial fractions, source hashes, mirror check, sample-file reference |
| `samples.csv` | Every scenario/eta/phi sampled core-plane count |

A pattern contains `carriers` with `index`, column/row/quadrant, signs, centres and
all corners; column origins; empty `collector_reservations`; and phase angles.
These are suitable source points for face drawings. `shared_geometry` in the
summary contains the positive-quarter outer/hole polygons and quarter rotations
for steel drawings. `layers` names absorber/carrier/core-plane z values, phase and
end frame. Full placements contain side/layer/sector/carrier IDs, phase,
`origin_mm`, local-basis row vectors, all four transformed water ports, four connectors and an
unconnected quadrant/perimeter handoff. The placement `origin_mm` is the carrier
front-face coordinate origin (z = 4913.2 mm in positive layer 0), not a solid
centre. A common physical part is placed by `origin + frame * part.center_mm`;
its `center_mm` remains its real solid centre in the carrier frame. Carrier
prototype `center_xy_mm` retains its face-centre meaning.

The DES036 descriptor is retained:
`system:8,side:2,sector:4,layer:6,carrier:12,module:2,sensor:6,x:-1,y:-1`.
System is 9, side is 1/2, layer is 0…35, sector is 0…15, carrier is unique within
side/layer/sector and below 4096, module is 0/1, and sensor is 0…35. Carrier parent
IDs plus the common module/sensor fields define all physical tile addresses.

Masses are grams. Areas/positions are mm²/mm. Power is watts. `summary` gives
whole-two-end counts and material totals, with shared steel/frames/back covers
owned once, and per-carrier current stresses scaled independently. All 156 chip
channels per pair remain powered. DAQ and trigger lane sums stay separate. These
are sums of local budgets; connector fan-in, concentration, voltage drop,
pressure drop, cooling distribution and sustained readout are unqualified.

Source hashes identify executed file bytes separately from the initial assignment
revision. The common module retains its own initial DES036 revision. No timestamp
or absolute output path is embedded. Repeated runs from identical source and
checkout state are deterministic. Source changes require regeneration before
using evidence or drawings.

## Core-plane diagnostic limits

Actual 29.7 × 29.7 mm core rectangles are sampled at common carrier local z = 2 mm,
before the rear recess. A fast lookup inverse-rotates the layer, locates its
column/row/carrier, and tests the nearest physical board/tile. It preserves board,
row, quarter and tile seams. The result is **core-plane sampling**, not finite
scintillator/recess intersection, optical response, particle efficiency, useful
hadronic depth or shower containment. Steel finite-path screening is explicitly
`NOT_RUN`; the steel mass calculation is not a material-transport scan.

The default grid samples eta = 0.9…3.8 in 0.1 steps plus eta = 4 and 5, with
720 evenly spaced phi directions. Quarter and 22.5° sector seams are included.
Min/mean/max counts have a 36-plane denominator for the corresponding fractions.
Zero and partial fractions describe this finite sample only. Negative-end checks
compare (eta, phi) with (−eta, −phi), the Rx(π) mapped ray. The existing empty
FCal reservation is unchanged; high-eta gaps remain visible.

The per-layer full-face denominator is the entire 300…4148 mm polygon annulus,
including frames, seams and packing losses. A separate packable denominator is
310…4128 mm. The common carrier itself has only 72 × 29.7² / (380 × 240) ≈ 69.64%
core area. Rotating layers changes directional sampling, not that area ceiling.
