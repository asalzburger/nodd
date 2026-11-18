# Reproduce the compact LAr comparison

Use frozen scientific source `afc79974ea5c407ee571048fdb71a155e2bfa87a` and
[the prospective protocol](protocol.md). Existing verified runtime: DD4hep1.38,
Geant411.4.3, ROOT6.40.04. Follow acts-spack preflight before native use; no shared
installation/change is required. macOS library names below use `.dylib`; on Linux
use the actual `.so` names. All raw XML, expected models, ROOT/events and logs
stay under ignored `build/`. Commands require fresh output directories.

The exact matching primary files are retained locally at
`../nodd-ecal10k/build/ecal10k/production-input`; see the original
[10k protocol](../ecal10k/protocol.md) and validation/source recipes for regeneration.
Their required bytes/hashes, and reference/candidate compact **and material**
identities, are frozen in [contract.json](contract.json). Do not substitute a new
random sample and call it paired. The audited old LAr run is retained at
`../nodd-lar-10k-response/build/lar10k-resume/production12`; its regeneration is
in [the original LAr recipe](../lar10k/reproduce.md).

```sh
run_root=build/lar-compact-repeat
mkdir -p "$run_root"
python3 -B tools/lar_calorimeter/compact_prototype.py --output "$run_root/model"
software/env/run.sh cmake -S prototypes/calorimeter -B "$run_root/factories" -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$run_root/factories" \
  --target Components_nODDLArBarrelPrototype Components_nODDLArEndcapPrototype --parallel 4
software/env/run.sh cmake -S software/analysis/lar_response -B "$run_root/audit" -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$run_root/audit" --parallel 3
python3 -B software/analysis/lar_response/transport.py prepare \
  --baseline "$run_root/model/combined" \
  --primary-sample ../nodd-ecal10k/build/ecal10k/production-input --output "$run_root/sample"
```

Run native shape/transform/mass/readout and overlap gates on both components,
then the actual union and role-resolved angular/within-period depth scan:

```sh
software/env/run.sh python3 -B tools/lar_calorimeter/barrel_native.py \
  --compact "$run_root/model/barrel/barrel.xml" --expected "$run_root/model/barrel/expected.json" \
  --library "$run_root/factories/libnODDLArBarrelPrototype.dylib" --output "$run_root/barrel-native.json"
software/env/run.sh python3 -B tools/lar_calorimeter/endcap_native.py \
  --compact "$run_root/model/endcaps/endcaps.xml" --expected "$run_root/model/endcaps/expected.json" \
  --library "$run_root/factories/libnODDLArEndcapPrototype.dylib" --output "$run_root/endcap-native.json"
software/env/run.sh python3 -B tools/lar_calorimeter/combined_native.py audit \
  --directory "$run_root/model/combined" \
  --barrel-library "$run_root/factories/libnODDLArBarrelPrototype.dylib" \
  --endcap-library "$run_root/factories/libnODDLArEndcapPrototype.dylib" --output "$run_root/combined-native.json"
software/env/run.sh python3 -B tools/lar_calorimeter/compact_depth.py \
  --compact "$run_root/model/combined/detector.xml" \
  --expected "$run_root/model/barrel/expected.json" --expected "$run_root/model/endcaps/expected.json" \
  --library "$run_root/factories/libnODDLArBarrelPrototype.dylib" \
  --library "$run_root/factories/libnODDLArEndcapPrototype.dylib" --output "$run_root/depth.json"
```

Before production, transport24 primaries with1/12workers and100 primaries with
native limits/5mm cap using the same `transport.py run` invocation below. Use
separate output directories, then `transport.py audit` for each. Require exact
serial/MT hits with `compact_controls.py --serial SERIAL_RUN --mt MT_RUN --output
CONTROL_JSON`. Native-limit uses `--max-step-mm 0`; retain the predeclared5mm
production cap regardless of pilot response. Successful transport and successful
readback are separate requirements.

```sh
software/env/run.sh python3 -B software/analysis/lar_response/transport.py run \
  --sample "$run_root/sample" --output "$run_root/production12" \
  --geometry-library "$run_root/factories/libnODDLArBarrelPrototype.dylib" \
  --geometry-library "$run_root/factories/libnODDLArEndcapPrototype.dylib" \
  --audit-library "$run_root/audit/libnODDLArResponseAudit.dylib" \
  --events 10000 --threads 12 --seed 133812341 --max-step-mm 5 --reserve-gib 30
software/env/run.sh python3 -B software/analysis/lar_response/transport.py audit \
  --sample "$run_root/sample" --run "$run_root/production12"
```

Existing analysis Python is the ACTS environment's `pyvenv/bin/python`, with
NumPy2.5.4/Matplotlib3.11.2 in the observed node. No native ACTS build is needed.
Use a recorded equivalent on another node. The paired analysis rehashes both
raw ROOT files and worker/primary evidence before accepting the frozen labels.

```sh
plot_python=/path/to/existing/analysis/python
"$plot_python" -B software/analysis/lar_response/compact_compare.py analyze \
  --reference-run ../nodd-lar-10k-response/build/lar10k-resume/production12 \
  --candidate-run "$run_root/production12" --contract docs/validation/lar-compact/contract.json \
  --bootstrap 1000 --seed 13001000 --output "$run_root/comparison"
MPLCONFIGDIR="$run_root/mpl-cache" XDG_CACHE_HOME="$run_root/cache" \
  "$plot_python" -B software/analysis/lar_response/compact_compare.py plot \
  --summary "$run_root/comparison/summary.json" --output "$run_root/figures"
```

Committed compact response/material summaries permit replotting without ROOT.
Regenerating paired inference and source/readback checks requires the retained
or regenerated event data. Plot source/runtime changes can alter rendering;
geometry, material, primary, analysis and artifact hashes remain explicit.
