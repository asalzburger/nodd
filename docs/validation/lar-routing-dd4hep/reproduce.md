# Reproduce the isolated DD4hep routing prototype

Use the source revision recorded in `results.json`, with existing node-specific
DD4hep/DDG4, Geant4 and nlohmann_json packages. Follow the repository acts-spack
preflight first; a registry fingerprint warning requires direct verification,
not an installation or silent substitute. [Recorded environment](environment.json).
Commands below are for the verified macOS node; the built library suffix is
`.dylib`. `software/env/run.sh` activates dependencies in each fresh process.

Choose a fresh ignored output directory. The exporter/transport runner refuse
to overwrite existing evidence. No raw file is added to Git.

```sh
routing_work=build/lar-routing-replay
mkdir -p "$routing_work"
software/env/run.sh cmake -S prototypes/lar_routing -B "$routing_work/factory" \
  -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$routing_work/factory" --parallel 3 \
  --target Components_nODDLArRoutingPrototype
python3 -B -m unittest discover -s tools/lar_calorimeter -p 'test_routing.py' -v

for variant in old new; do
  python3 -B tools/lar_calorimeter/routing.py --variant "$variant" \
    --output "$routing_work/$variant"
  software/env/run.sh python3 -B tools/lar_calorimeter/routing_native.py \
    --compact "$routing_work/$variant/routing.xml" \
    --expected "$routing_work/$variant/expected.json" \
    --library "$routing_work/factory/libnODDLArRoutingPrototype.dylib" \
    --output "$routing_work/$variant/native.json"
  software/env/run.sh python3 -B tools/lar_calorimeter/routing_transport.py run \
    --compact "$routing_work/$variant/routing.xml" \
    --expected "$routing_work/$variant/expected.json" \
    --library "$routing_work/factory/libnODDLArRoutingPrototype.dylib" \
    --output "$routing_work/$variant-smoke"
done
```

Exports contain `routing.xml`, `materials.xml` and a full source-bound expected
inventory. Inspect the material and empty-envelope fields before interpretation.
Native JSON/ROOT and smoke JSONL/ROOT/logs remain ignored. Existing retained smoke
data can be re-audited with `routing_transport.py audit --directory DIRECTORY`.

For a finer construction, export into a new directory with `--arc-step-deg 2.5`
and run the same native auditor. Preserve the analytic inventory target and
report the new sagitta; no per-ray convergence is inferred merely from mass.

## Separate unchanged-ECAL occupancy diagnostic

Build/load existing calorimeter factories; do not include the new routing into
the calorimeter world or cut existing material to hide contacts:

```sh
software/env/run.sh cmake -S prototypes/calorimeter -B "$routing_work/context-factories" \
  -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$routing_work/context-factories" --parallel 3 \
  --target Components_nODDLArBarrelPrototype Components_nODDLArEndcapPrototype
python3 -B tools/lar_calorimeter/barrel_export.py \
  --output "$routing_work/context/barrel" \
  --services tools/lar_calorimeter/barrel_services.py --real-periods
python3 -B tools/lar_calorimeter/endcap_export.py \
  --output "$routing_work/context/endcap" \
  --services tools/lar_calorimeter/endcap_services.py --real-periods
```

Merge these two components with the existing ECAL-only builder:

```sh
python3 - "$routing_work/context" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, 'tools/lar_calorimeter')
from combined_native import build
p=Path(sys.argv[1])
build(p/'barrel/barrel.xml', p/'barrel/expected.json',
      p/'endcap/endcaps.xml', p/'endcap/expected.json', p/'native-ecal')
PY
software/env/run.sh python3 -B tools/lar_calorimeter/routing_context.py \
  --context "$routing_work/context/native-ecal" \
  --library "$routing_work/context-factories/libnODDLArBarrelPrototype.dylib" \
  --library "$routing_work/context-factories/libnODDLArEndcapPrototype.dylib" \
  --route "$routing_work/old" --route "$routing_work/new" \
  --output "$routing_work/context-occupancy.json"
```

This exits successfully when the diagnostic completes, even when contacts are
found. Its `fit_accepted` is false and status is diagnostic. Interpret the
physical-pipe and unmaterialised-envelope counters separately. Preserve
component/source/library and compact hashes; the source guards reject stale
artifacts or inputs changed during the check.
