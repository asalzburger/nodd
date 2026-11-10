# Reusable Si–W wedges in LAYOUT-001

The maintained LAYOUT-001 export places one real logical barrel wedge 16
times and one logical endcap wedge 32 times. The new mothers use the actual
enclosing material. The physical leaves, materials, readouts and replica
poses retain the DES-030 and DES-031 working baseline. Older compacts
without a wedge envelope still use their assembly hierarchy.

## Executed checks

The measured implementation is `2bd57912350e9e88b1918e0221b205153545346e`.
A fresh LAYOUT-001 export used the maintained tracker and both Si–W
components. An independent XML check confirmed that removing only the
new envelopes restores both stock ECAL detector subtrees and all 2,352
replica declarations. The integrated material file and readouts match stock.

In a single-thread ECAL-only DDSim probe extracted from this export, the
volume manager built **531,936 paths in 23.0 seconds**. The retained stock
ECAL-only measurement on the same Mac Studio was **3,953.8 seconds**.
The comparison times the Geant4 map build, with initialization and
readback separately measured. DD4hep was 1.38 /3yd4hz3, Geant4 was
11.4.3 /wfg55xi and ROOT was 6.40.04.

The complete Geant4 sensor inventory agrees with stock XML for every
ID, position, rotation and material. The separate native DD4hep
`VolumeManager` also agrees with the Geant4 touchables on all sensor
centres and axes and resolves the same context when a pad bit is set.
All 65 material rays through the actual tracker-plus-ECAL compact agree
with the stock reference within the recorded tolerances. The stock
compact was constructed with the new factory through its legacy path.

[Results](results.json) records the measured quantities and source hashes.
Geant4 gains same-material boundaries, so geometry equivalence and
transport smoke evidence leave shower-response equivalence for a
dedicated study.

## Reproduce

Use the node-verified Spack runtime and run from the repository root. For
the stock reference, export LAYOUT-001 at
`0bc37ca08fed0bd7b121d6eebd5794dd3b584877` from a separate checkout. Set
`stock_compact` to its full tracker-plus-ECAL `detector.xml`.

```sh
repo="$PWD"
proof="$repo/docs/validation/siw-real-wedge-default"
work="$repo/build/siw-real-wedge-default"
python3 -B tools/calorimeter_baselines/export.py --layout LAYOUT-001 --output "$work/layout001"
software/env/run.sh cmake -S prototypes/calorimeter -B "$work/calo" -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$work/calo" --target Components_nODDCalorimeterPrototype --parallel 3
software/env/run.sh cmake -S . -B "$work/tracker" -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
software/env/run.sh cmake --build "$work/tracker" --parallel 3 --target \
  Components_nODDPixelBarrel Components_nODDBeamPipe Components_nODDShortStripBarrel \
  Components_nODDShortStripEndcap Components_nODDLongStrip

calo="$work/calo/libnODDCalorimeterPrototype.dylib"
libs=("$work"/tracker/detector/libnODD*.dylib "$calo")
software/env/run.sh python3 -B "$proof/probe.py" "$work/layout001" "$calo" "$work/ecal-probe"
python3 -B "$proof/compare_sensors.py" "$stock_compact" "$work/ecal-probe/sensors.tsv" "$work/sensor-comparison.json"
software/env/run.sh python3 -B "$proof/material_rays.py" trace "$stock_compact" "$work/stock-rays.json" "${libs[@]}"
software/env/run.sh python3 -B "$proof/material_rays.py" trace "$work/layout001/detector.xml" "$work/wedge-rays.json" "${libs[@]}"
python3 -B "$proof/material_rays.py" compare "$work/stock-rays.json" "$work/wedge-rays.json" "$work/ray-comparison.json"

native_args=()
for lib in "${libs[@]}"; do native_args+=(--library "$lib"); done
software/env/run.sh python3 -u tools/calorimeter_baselines/native.py --directory "$work/layout001" \
  "${native_args[@]}" --output "$work/native-overlaps.json"
```

Use the platform's library suffix where needed. For transport, create a
fresh smoke directory, then run the fixed gun macro with the maintained
native field, cut and step audit.

```sh
mkdir "$work/smoke"
software/env/run.sh zsh -c '
  set -e
  repo=$1; work=$2; proof=$3
  export DD4HEP_LIBRARY_PATH="$work/calo:$work/tracker/detector:${DD4HEP_LIBRARY_PATH:-}"
  export DYLD_LIBRARY_PATH="$work/calo:$work/tracker/detector:${DYLD_LIBRARY_PATH:-}"
  export I118_TRANSPORT_AUDIT="$work/smoke/native-transport-audit.json"
  cd "$work/smoke"
  python3 -u "$(command -v ddsim)" --compactFile "$work/layout001/detector.xml" \
    --steeringFile "$repo/software/analysis/calorimeter_digitization/nodd_transport.py" \
    --runType run --enableG4Gun --macroFile "$proof/smoke.mac" --numberOfThreads 1 \
    --random.seed 24019999 --physics.list FTFP_BERT --physics.rangecut 0.7 \
    --part.userParticleHandler "" --outputConfig.forceEDM4HEP --outputFile unused.root
' wedge-smoke "$repo" "$work" "$proof"
software/env/run.sh python3 -B "$proof/audit_smoke.py" "$work/smoke" "$work/ecal-probe/sensors.tsv"
```

Geometry compacts, sensor dumps, raw events and full logs stay in
ignored build storage. The compact result supports review of the
reported measurements. Re-run the recipe for per-sensor and per-event checks.
