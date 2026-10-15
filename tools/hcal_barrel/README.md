# Barrel HCAL design screen — DES037

**DRAFT / PROTOTYPE.** Parameterized analytical layout, material ledger and
core-plane geometry for the [barrel proposal](../../docs/design/DES-037-hcal-barrel-common-module.md).
Reuses the source-checked DES036 hardware unchanged and omits its removable
reference absorber. No production detector entry point is changed.

```sh
python3 -B -m unittest discover -s tools/hcal_barrel -p 'test_*.py' -v
python3 -B tools/hcal_barrel/design.py --output build/hcal-barrel
```

Python standard library only. `config.json` centralizes unsigned choices. The
export writes `layout.json` (complete carrier placements and right-handed frames),
`summary.json` (material ownership, counts, power/current/DAQ/service budgets and
source identities), and `coverage.json` (actual core-plane masks and statistics).
Raw full placement/mask exports stay in ignored build output. Retained reports
record their hashes and the source/config revision. Later Git revisions change
execution metadata; physical quantities remain reproducible from their inputs.

Each layer retains the maximal centred column count for all controls. Requested
tangential phases are explicitly bounded by the remaining centred edge margin
minus a 1 mm clearance. Both requested and actual offsets are emitted. Compare
`staggered`, `aligned_zero` and `aligned_midplane_gap`; the latter uses a valid
130 mm axial offset to expose an empty midplane. This is a matched-count phase
comparison, not a change in packing/area.

`ray(data, eta, phi, scenario)` samples each physical 29.7 mm core rectangle at
carrier-local z=2 mm. The plane is ahead of the rear recess. Steel-only path
lengths analytically clip each absorber layer against axial and sector edges.
These are geometric diagnostics, not full finite-solid/recess intersections,
native navigation, optical response, efficiency, digitization or containment.
The report uses 720 uniform phi bins for its statistics and separate sector-boundary samples; exact
aligned structural seams and high-eta misses remain visible.

Identifier encoding retains system9, side0 and the DES036 bit layout. Carrier
indices are unique per sector/layer. Each carrier contains two common boards,
72 tile inputs and 156 powered internal channels; auxiliary/unused channels stay
paid. Constituent masses include all common local cooling/interface material,
sector steel plates, distinct aluminium rails/end flanges/back cover. External
collector/cable/plant material, fasteners, bearings and additional concentration
losses are excluded explicitly. No tolerance stack, thermal/hydraulic, load,
radiation, sustained-rate or engineering approval is implied.
