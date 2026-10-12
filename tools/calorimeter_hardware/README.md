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

## Sectors and complete assemblies (DES029)

```sh
python3 -B tools/calorimeter_hardware/assembly_export.py --output build/calorimeter/full
python3 -B tools/calorimeter_hardware/assembly_native.py \
  --compact build/calorimeter/full/calorimeter.xml \
  --expected build/calorimeter/full/expected.json \
  --library build/calorimeter/factory/libnODDCalorimeterPrototype.dylib \
  --output build/calorimeter/full/native.json
```

The full model reuses logical cassette and sector volumes. The audit checks
all logical placements and every physical replica, audits native capacities,
and scales by actual counts. All sensor indices and disjoint parent ranges
prove uniqueness;384 inherited-ID round trips cover first/last parents/sensors
in each physical sector. This avoids expanding37 million nodes into JSON.
The **full ROOT overlap check is actually run**, not replaced with that proof;
at10 nm it took approximately7 minutes on the verified node. Source/compact/
library hashes and57 ROOT rays are retained in DES029 evidence.

`assemblies.json` uses apothems throughout. Endcap side2 uses a proper rotation,
not a reflection. Supports and sector absorber plates have distinct ownership.
Uniform rectangle packing has substantial active gaps, especially in endcaps;
reported plate-area fractions are geometric coverage, not calorimeter efficiency.
External manifolds/cabling, connectors and engineering strength/thermal analysis
are excluded. Aggregate budgets expose continuous-power scale before qualification.

DES029 amends unit fixtures with rail ports and flush tube ends. Original DES028
execution remains in Git and its report; amended unit evidence is retained in
DES029. To regenerate drawings with the existing plotting environment:

```sh
python3 -B tools/calorimeter_hardware/assembly_plot.py \
  --output docs/design/figures/DES-029 --native build/calorimeter/full/native.json
```

The sparse Geant4 smoke fixture retains physical sector0, all plates/frames,
but one selected cassette per layer (eta0.5 barrel, eta2 endcap, phi0.03):

```sh
python3 -B tools/calorimeter_hardware/sector_fixture.py \
  --compact build/calorimeter/full/calorimeter.xml \
  --expected build/calorimeter/full/expected.json \
  --output build/calorimeter/full/sector-fixture.xml
# Use the verified active Python to invoke the installed DDSim script.
# Add the factory directory to LD_LIBRARY_PATH / DYLD_LIBRARY_PATH as applicable.
python3 "$(command -v ddsim)" \
  --compactFile build/calorimeter/full/sector-fixture.xml \
  --runType batch --numberOfEvents 1 --enableGun --gun.particle mu- \
  --gun.energy '10*GeV' --gun.position '0 0 0' \
  --gun.direction '0.886419 0.0266 0.462117' --random.seed 42 \
  --part.userParticleHandler '' --outputFile build/calorimeter/full/barrel-smoke.root
```

Save stdout/stderr to `barrel-smoke.log`. Repeat with directions
`0.265683 0.007973 0.964028` and `0.265683 0.007973 -0.964028` into
`positive-smoke` / `negative-smoke` outputs/logs, then run
`assembly_transport.py --directory build/calorimeter/full --output transport.json`.
Saved hit IDs and positive energies verify hierarchical readout and both endcap
orientations. Default DDSim calorimeter actions are smoke-test machinery, not a
validated silicon/scintillator response model. Complete sectors first converted
to Geant4, but their initialization was stopped after several minutes; only
sparse fixtures completed event transport. Full detector transport remains open.
