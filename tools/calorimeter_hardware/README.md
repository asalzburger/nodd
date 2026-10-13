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

The independent shape audit reads that exact persisted full ROOT artifact:

```sh
python3 -B tools/calorimeter_hardware/check_shapes.py \
  --root build/calorimeter/full/native.root \
  --native build/calorimeter/full/native.json \
  --expected build/calorimeter/full/expected.json \
  --output build/calorimeter/full/shapes.json
```

It requires both ROOT and expected-inventory hashes to match the completed
overlap audit and verifies native primitive dimensions, polygon vertices/depth
and Boolean cutter dimensions/transforms. It does not relax any overlap gate.

## Custom ECAL edge masks and optimized endcaps (DES030)

The new DRAFT prototype is isolated from DES029's historical cassette assemblies
and production entry points. Sixteen wedge carriers retain DES029 drawing B's
topology and the outer16-gon. A100mm-apothem16-gon aperture with30mm inner rim
explores the user-requested|eta|4 target; full90mm squares cannot fit there.
Single-sensor boards,2mm PCB margins/gaps and120mm outer shared service bays
follow B's compact-board approach. Grouped full/half-board engineering remains
open. Custom inner/side masks fit within one wedge. The earlier four-quadrant
alternative is preserved in `docs/validation/DES-030/quadrant-study` and the
matching figure/input archives; its results do not describe this prototype.
Square and custom-edge cases share the same reservations. Custom sensor/guard/
PCB/electrode polygons are explicit; small connected pad fragments are merged.
`nODDEdgeGrid` preserves their real ID mapping and interior reference points.

```sh
python3 -B tools/calorimeter_hardware/edge_export.py --output build/calorimeter/edges/wedges
python3 -B tools/calorimeter_hardware/edge_export.py \
  --output build/calorimeter/edges/wedge-squares --layout squares
# Activate and verify the existing acts-spack runtime in this shell.
cmake -S prototypes/calorimeter -B build/calorimeter/factory
cmake --build build/calorimeter/factory
python3 -B tools/calorimeter_hardware/edge_native.py \
  --compact build/calorimeter/edges/wedges/calorimeter.xml \
  --expected build/calorimeter/edges/wedges/expected.json \
  --library build/calorimeter/factory/libnODDCalorimeterPrototype.dylib \
  --output build/calorimeter/edges/wedges/native.json
# Repeat for wedge-squares; Linux uses .so.
```

With the existing Matplotlib environment, `edge_plot.py` produces the requested
four-stageSVG/PNG, a single-wedge before/after SVG/PNG, the profile catalogue and
eta/phi layer-count samples. Native
checks audit actual shapes/materials/replicas, every volume ID and every logical
electrode/raw fragment, closed-boundary ties, full overlaps and bounded material
rays. No native ODD construction is claimed by the source-derived ODD panel.

`edge_fixture.py --directory build/calorimeter/edges/wedges` creates a sparse
single-layer custom-inner-module fixture on each side for two10GeV mu- events.
Directions/expected electrode are saved in `fixture.json`; DDSim seeds43/44.
`edge_transport.py` checks saved positive energies and full parent/pad IDs.
The fixture retains plates/cooling/interface material; it removes other sensor
boards and structural frames. It does not validate complete-detector transport.
See DES030 for masks, operating assumptions, aperture and engineering limits.

## Detailed SiW barrel (DES031)

The isolated barrel uses 94 mm square boards on 96 mm pitch, explicit inactive
silicon guards, PCB/ASIC/thermal stacks, common 3 mm copper cooling plates and
shared lane interfaces. Seven 1000 mm slabs plus 276/468 mm end slabs retain the
48-layer envelope; alternating −96/+96 mm phases stagger axial service joints.
It does not modify the production compact, DES029 historical fixtures or endcaps.
See [DES031](../../docs/design/DES-031-siw-barrel-prototype.md) and its
[executed evidence](../../docs/validation/DES-031/results.md).

```sh
python3 -B tools/calorimeter_hardware/barrel_export.py --output build/calorimeter/barrel
# Activate the verified existing acts-spack DD4hep/Geant4 runtime first.
cmake -S prototypes/calorimeter -B build/calorimeter/barrel-factory
cmake --build build/calorimeter/barrel-factory
python3 -B tools/calorimeter_hardware/barrel_native.py \
  --compact build/calorimeter/barrel/calorimeter.xml \
  --expected build/calorimeter/barrel/expected.json \
  --library build/calorimeter/barrel-factory/libnODDCalorimeterPrototype.dylib \
  --output build/calorimeter/barrel/native.json --overlap-seed 31
python3 -B tools/calorimeter_hardware/barrel_readout.py \
  --compact build/calorimeter/barrel/calorimeter.xml \
  --expected build/calorimeter/barrel/expected.json \
  --library build/calorimeter/barrel-factory/libnODDCalorimeterPrototype.dylib \
  --output build/calorimeter/barrel/readout.json
python3 -B tools/calorimeter_hardware/barrel_compare.py \
  --expected build/calorimeter/barrel/expected.json \
  --native build/calorimeter/barrel/native.json \
  --output build/calorimeter/barrel/ray-comparison.json
python3 -B tools/calorimeter_hardware/barrel_fixture.py --directory build/calorimeter/barrel
```

Linux uses `.so`. The full native checker retains mass/material, all physical
sensor IDs and full-overlap gates. Supplemental `barrel_readout.py` covers all
logical module electrode addresses; `barrel_compare.py` independently compares
finite silicon boxes to ROOT rays, preserving centre-plane approximation results.
The factory library must be discoverable in the active runtime:

```sh
export LD_LIBRARY_PATH="$PWD/build/calorimeter/barrel-factory:${LD_LIBRARY_PATH:-}"
export DYLD_LIBRARY_PATH="$PWD/build/calorimeter/barrel-factory:${DYLD_LIBRARY_PATH:-}"
python3 - <<'PYTHON'
import json, shutil, subprocess, sys
from pathlib import Path
root = Path('build/calorimeter/barrel')
for q in json.loads((root / 'fixtures.json').read_text())['fixtures']:
    name = q['name']
    args = [sys.executable, shutil.which('ddsim'),
            '--compactFile', str(root / (name + '-fixture.xml')),
            '--runType', 'batch', '--numberOfEvents', '1', '--enableGun',
            '--gun.particle', 'mu-', '--gun.energy', '10*GeV',
            '--gun.position', '0 0 0',
            '--gun.direction', ' '.join(map(str, q['direction'])),
            '--random.seed', str(q['seed']), '--part.userParticleHandler', '',
            '--outputFile', str(root / (name + '-smoke.root'))]
    with (root / (name + '-smoke.log')).open('w') as log:
        subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, check=True)
PYTHON
python3 -B tools/calorimeter_hardware/barrel_transport.py \
  --directory build/calorimeter/barrel --output build/calorimeter/barrel/transport.json
python3 -B tools/calorimeter_hardware/barrel_plot.py \
  --directory build/calorimeter/barrel --output docs/design/figures/DES-031
```

These three single-board/single-layer fixtures use seeds 45/46/47 and zero field.
They retain local material and test saved parent/pad IDs and positive energies;
complete-barrel transport and realistic response remain open. Plotting uses the
already available Matplotlib runtime. Headers, ports, power/data routes and
thermal/structural qualification are absent; material-filled reservations must
not be read as empty service corridors.
