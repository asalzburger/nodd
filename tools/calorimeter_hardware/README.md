# Isolated calorimeter hardware prototypes

DES028 is DRAFT. No production CMake or compact entry point imports these files.
Python standard library is sufficient for export and controls. Native checks use
existing DD4hep1.38/ROOT6.40.04; optional figures use existing matplotlib. No new
external package is adopted.

```sh
python3 -B -m unittest discover -s tools/calorimeter_hardware -p 'test_*.py' -v
python3 -B tools/calorimeter_hardware/export.py --output build/calorimeter/units
# Activate and verify the node's acts-spack runtime in this same shell.
cmake -S prototypes/calorimeter -B build/calorimeter/factory
cmake --build build/calorimeter/factory
python3 -B tools/calorimeter_hardware/native.py \
  --compact build/calorimeter/units/calorimeter.xml \
  --expected build/calorimeter/units/expected.json \
  --library build/calorimeter/factory/libnODDCalorimeterPrototype.dylib \
  --output build/calorimeter/units/native.json
```

Linux uses `.so` instead of `.dylib`. Native ROOT outputs/build products are
ignored. Committed reports identify actual source/config/runtime hashes, checked
cells, counts and bounded rays. The independent audit computes primitive and
restricted-CSG capacities from native shapes, not model metadata. Contained,
disjoint cutters are required for exact subtraction. ROOT's overlap result is a
geometry check, not proof of mechanics, thermal conductance or optical response.

All cassette dimensions/placements are named in `cassettes.json`. Shared tracker
material helpers preserve constituent masses; package volume fractions are
explicit proxies. The sector owns absorber plates: repeated cassettes must omit
unit-fixture patches. Power is continuous; no ILC duty factor is applied. Boards,
pads and pipes have separate material entries. Logical cells and physical
sensitive volumes remain distinct.
