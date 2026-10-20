# PR90 agreed wheel revision: interface study and baseline inventories

DRAFT isolated PROTOTYPE. Starting revision `5674a7688319d6dd5179c04cd381cb59f48d36bb`.
The [agreed reviewer decision](https://github.com/asalzburger/nodd/pull/90#issuecomment-6283618592)
requests inner/outer endcap wheels outside the toroids, no overlap, a new OBJ,
full/endcap coverage and blue shape inventories. The physical interface choice
below remains pending. This directory contains preparatory evidence; no revised
layout, new OBJ or after-layout coverage has been generated.

## Completed inventories

| Current source | Envelopes | Dimension families | List and blue 2D shapes |
|---|---:|---:|---|
| Barrel |816|6|[Inventory](before-inventory/barrel.md)|
| Endcap, both ends |744|18|[Before inventory](before-inventory/endcap.md)|

Every source panel maps to a family in the JSON. Dimensions group on a 1 nm grid
to suppress floating-point construction noise; unrounded per-panel dimensions
remain available. These are envelope shapes, not manufacturing tolerances.
The colour is the retained OBJ blue, `Kd 0 0.375 0.996094`. Plot axes use metres
and a common scale per sheet. Original geometry, field, OBJ and ACTS evidence
remain unchanged.

Reproduce from the repository root with Python, NumPy and Matplotlib:

```sh
python3 -B tools/muon_layout/wheel_inventory.py \
  --geometry docs/validation/DES-040/geometry.json \
  --output docs/validation/DES-040/wheels-2026-10-20/before-inventory \
  --kind both --label 'PR90 before revision'
```

## Physical choice required before the revised layout

The retained HCAL ends at abs(z)=6.4412 m and the ECT warm envelope begins at
6.55 m. The 108.8 mm gross gap cannot contain a 500 mm chamber, even without
clearance. With the existing 50 mm coil clearance, the deficit is 441.2 mm;
a provisional additional 50 mm HCAL margin makes it 491.2 mm. The latter margin
is an open interface assumption. Shortening barrel chambers cannot change this
gap. Twelve angular sectors can reserve the BT legs in gaps, but cannot solve
this axial conflict.

The [SysArch audit](interface-audit.md) quantifies alternatives. One concrete
unselected example moves only the ECT front return 0.50 m outward, retaining the
rear return: centre abs(z)=9.50 m, half-length2.20 m and warm front7.05 m.
A wheel centre6.7456 m then has54.4 mm axial separation from both HCAL and ECT.
BT corridors, barrel repacking, frame-lug changes, coupled magnetic sizing and
a recomputed joint field are still required. This is a geometric proposal,
not a validated or approved magnetic design.

Keeping magnets fixed instead requires changing the inner wheel's radial reach:
a conservative example is an annulus R4.92–5.50 m at abs(z)=6.24 m. It loses the
small-bore forward station coverage and is not equivalent to the requested wheel.
Changing HCAL is a third, substantial calorimeter option. None is selected.

The outer full wheel can clear the existing frame with centre strictly beyond
abs(z)=12.75 m;12.80 m is an unselected rounded example. The current map/world
cannot contain it. Enlarging the domain and using a common upstream launch for
both layouts are necessary for a meaningful comparison. See the separate
[MuonTech concept assessment](chamber-concepts.md) and
[PhysVal paired-coverage protocol](coverage-plan.md). These specialist documents
assess the pinned input; illustrative alternatives confer no sign-off.

The user was asked whether to revise ECT axial extent and recalculate its field,
or keep magnets fixed and accept a different inner-wheel radial aperture. That
answer is required before generating the candidate and its after inventory/OBJ.

## Retained checks

[Interface arithmetic and full support bounds](interface-check.json) reproduce
with `interface-check.py --root . --output OUTPUT.json`; only Python's standard
library is needed. [Original inventory/domain/denominator check](baseline-check.json)
reproduces with `baseline-check.py --root . --output OUTPUT.json` and NumPy.
Both read the exact starting revision with `git show`. The latter retains the
old failure-aware endcap subset; it is not a new candidate coverage result.

[Inventory reconstruction check](inventory-check.json) covers all1,560 footprints,
CSV family quantities and station/hemisphere accounting; maximum footprint
reconstruction error is0.4973 nm on the declared1 nm grouping grid. Reproduce
with `inventory-check.py --root . --output OUTPUT.json` and NumPy. Both blue
sheets were visually inspected after correcting title/footer spacing.
