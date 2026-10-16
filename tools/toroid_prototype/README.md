# DES-039 twelvefold toroid prototype

Isolated, reproducible **vacuum** magnetostatics based on PR86. Three barrel
chamber outlines and three disks per end are clipped against the coil/case
reservations. No chamber internals, iron response or production integration.

From repository root, with Python + NumPy:

```sh
python3 -B -m unittest tools.toroid_prototype.test_field tools.toroid_prototype.test_energy tools.toroid_prototype.test_geometry tools.toroid_prototype.test_system tools.toroid_prototype.test_map
python3 -B -m tools.toroid_prototype.energy_study
python3 -B -m tools.toroid_prototype.run --skip-plots
```

The energy study takes several minutes. It retains a **1T barrel /1T endcap
reference** coupling matrix; the main run rescales every self/mutual term to the
chosen **1T barrel /1.6T endcap sagitta reference**. Linear vacuum current scaling
is exact. Source geometry and current packs stay identical.

With matplotlib, omit `--skip-plots`, or run `--plots-only` after calculation.
A local C++17 compiler accelerates the exact segment kernels; the ignored build
cache is generated from the checked-in `field_backend.cpp`. NumPy backend is
available for independent controls. No SciPy, ACTS, DD4hep, Geant4 or Spack setup
is required. `design.json` specifies geometry/targets; all units are SI except
explicit degree and A/mm² fields.

`docs/validation/DES-039/joint-field.npz` stores axes `(r,z,phi)` and cylindrical
`(Br,Bphi,Bz)` for the complete joint field, at0.0625m /0.625° spacing.
`field-components.npz` separately retains each source group on a0.125m /2.5° grid. Use the
provided bounded interpolator:

```python
from tools.toroid_prototype.map import FieldMap
f = FieldMap('docs/validation/DES-039/joint-field.npz')
B_cartesian_T = f.field([[6.2, 0.8, 0.0]])  # positions in metres
```

The 30° sector repeats by cylindrical-component periodicity. `FieldMap` rotates
to global Cartesian coordinates, rejects out-of-domain queries and rejects
**any masked interpolation corner**. NaNs mark winding packs plus a 0.10m
numerical guard. Never replace those NaNs by zero. For precision comparisons,
use `field.evaluate` with `system.toroid_sources` and `system.solenoid_sources`
and refine source quadrature; interpolation has an explicitly measured error.

The JSON/VTP geometry exports are outlines only. VTP has named line cells for
36 coil centrelines and nine chamber boundary objects (three cylinders plus
six disks). VTP shows both full-depth chamber boundary faces; JSON retains footprint
boundaries plus depth. Finite winding/cold/warm sweep dimensions are retained in the
results configuration. Geometric acceptance uses straight rays and 10mm path
sampling, not a detector navigator or reconstructed efficiency.

See [design](../../docs/design/DES-039-twelvefold-toroid.md),
[results](../../docs/validation/DES-039/results.md) and
[sources](../../docs/validation/DES-039/sources.md). The complete installed field
requires simultaneous nonlinear magnetostatics with specified HCAL steel B–H.
