# Reproduce the conditional gap comparison

Follow [the frozen protocol](protocol.md) and [verified environment](environment.json).
This is an isolated ECAL-only, zero-field response experiment. It preserves the
barrel and all internal endcap shapes, materials, local services and readout;
only signed root-relative endcap z placements change by400mm toward the IP.
Unresolved routing overlay and external systems are absent from both variants.

The executed node used existing Spack DD4hep1.38, Geant411.4.3, ROOT6.40.04,
EDM4hep1.1.1 and podio1.8. Run the acts-spack preflight and actual runtime checks
first; the setup/lock drift warning was reported and directly reverified.
No shared package install, staging or update is needed. Commands are for the
retained macOS node (.dylib); fresh software/env/run.sh activation is per process.

The verified800mm reference remains under
`../nodd-lar-10k-response/build/lar10k-resume/{sample,production12,layout002}`.
It contains the exact standard10k primaries and all retained local services.
The reference transport ran clean at327dd042b6b3d1be1a4325af3d444c38dd70f720.
Its earlier sample/component preparation declared5ef3db3 with dirty component
exports; exact producer bytes60708dbf... are pinned at
e2222482eb6c267fe1db4e4a871280469d49f7f9:software/analysis/lar_response/transport.py.
These observations are distinct; the helper verifies frozen artifacts, actual
producer/source/library bytes and current geometry, without claiming clean
original sample generation. Source bindings include the exact full digests.

All output directories must be fresh and ignored. Keep tracked sources clean
and unchanged through prepare, native checks, controls and production.

```sh
work=build/lar-gap10k-replay
ref=../nodd-lar-10k-response/build/lar10k-resume
barrel_library=../nodd-lar-geant4-placement/build/lar-placement/factories/libnODDLArBarrelPrototype.dylib
endcap_library=../nodd-lar-geant4-placement/build/lar-placement/factories/libnODDLArEndcapPrototype.dylib
audit_library="$ref/audit/libnODDLArResponseAudit.dylib"
mkdir -p "$work"
python3 -B software/analysis/lar_gap/geometry.py prepare \
  --reference-sample "$ref/sample" --reference-run "$ref/production12" \
  --output "$work/sample400"
software/env/run.sh python3 -B software/analysis/lar_gap/native.py snapshot \
  --sample "$ref/sample" --reference-run "$ref/production12" \
  --barrel-library "$barrel_library" --endcap-library "$endcap_library" \
  --output "$work/native-standard"
software/env/run.sh python3 -B software/analysis/lar_gap/native.py snapshot \
  --sample "$work/sample400" --reference-run "$ref/production12" \
  --barrel-library "$barrel_library" --endcap-library "$endcap_library" \
  --output "$work/native-candidate"
python3 -B software/analysis/lar_gap/native.py compare \
  --reference "$work/native-standard" --candidate "$work/native-candidate" \
  --output "$work/native-comparison.json"
```

Native snapshots preserve full placement and solid-definition ledgers locally.
They compare290216 placements,82598 signed endcap descendants and166 defining
solid signatures. Both native union scans use10nm tolerance; translations use
an explicit1e-7mm absolute tolerance. Shapes, recipes, topology and rotations
are exact invariants. Constituent conservation is a rigid-region bijection;
retained analytical component inventories are not a new native absolute mass
measurement. Boolean Capacity subtraction is intentionally not used.

The retained native/transport execution checkpoint is
b24f9db24b52f79c7586a52d0ca9b35e792606b9 (clean). Later reporting-only commits
preserve the exact helper/protocol hashes. The failed earlier Capacity-based
native audit is retained under ignored build/lar-gap10k/final/; no showers ran
there. Corrected successful outputs are under build/lar-gap10k/corrected/.

```sh
gap_run() {
  software/env/run.sh python3 -B software/analysis/lar_response/transport.py run \
    --sample "$work/sample400" --output "$work/$3" \
    --geometry-library "$barrel_library" --geometry-library "$endcap_library" \
    --audit-library "$audit_library" --events "$1" --threads "$2" \
    --seed 133812341 --max-step-mm 5 --reserve-gib 30
  software/env/run.sh python3 -B software/analysis/lar_response/transport.py audit \
    --sample "$work/sample400" --run "$work/$3"
}
gap_run 24 1 control-serial24
gap_run 24 12 control-mt24
software/env/run.sh python3 -B software/analysis/lar_gap/controls.py \
  --sample "$work/sample400" --serial "$work/control-serial24" \
  --mt "$work/control-mt24" --output "$work/serial-mt.json"
gap_run 100 12 pilot100
# Continue only after native, exact serial/MT and saved-data pilot checks pass.
gap_run 10000 12 production12
```

The comparison checks full ROOT/event-summary/receipt/input/worker/log/source
and library hashes, all10000 primary IDs and the frozen transform. Serially
initialised43648 native contexts precede workers. All events, including zeros,
remain in the denominator. The reference full ROOT was explicitly rehashed,
not merely trusted from its stored receipt. On another node regenerate the
standard reference and factories with the [standard recipe](../lar10k/reproduce.md)
first, retaining actual library hashes and versions; require the exact frozen
primary/physical compact/material hashes before comparing. Distinct runtime or
source versions are a new execution, not the retained-node result.

## Complete sensitive-deposit accounting

The first saved-hit comparison found three standard-gap and two candidate
positive-energy steps rejected by the unchanged midpoint cell lookup. The
saved-hit files alone cannot recover their deposits. Preserve those outputs.
The independent observation-only extension records all accepted sensitive-step
energy A, successfully assigned energy S, and unassigned energy U. Saved
float32 cell energy H remains separate. See [the frozen observer protocol](observer-protocol.md)
and [the separate readback correction](readback-addendum.md).

The executed observer library was built from clean d31cb719 source with C++
SHA256 `3a99cc83835a1e64c013e695df210854c13e1745c728d8dc181dac34634f401f`.
The clean full replay launch revision was
`2860f2620ef84e12c21e3d6108876dd7e0609f5e`. Subsequent three-file postprocessing
correction `d3f49420d6bd776b6b6891071801bf8dd6cd1216` preserves every runtime
producer byte, explicitly binds its own auditor and resolves logical/physical
volume aliases using the actual native placement ledger. Do not relabel the
original producer identity or modify retained receipts/readbacks.

```sh
software/env/run.sh cmake -S software/analysis/lar_gap -B "$work/observer-library" \
  -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$work/observer-library" -j 4
observer_library="$work/observer-library/libnODDLArStepObserver.dylib"

observe() {
  variant=$1
  event_count=$2
  worker_count=$3
  label=$4
  if [ "$variant" = standard ]; then sample="$ref/sample"; else sample="$work/sample400"; fi
  software/env/run.sh python3 -B software/analysis/lar_gap/observed_transport.py run \
    --sample "$sample" --native-report "$work/native-comparison.json" \
    --geometry-library "$barrel_library" --geometry-library "$endcap_library" \
    --audit-library "$audit_library" --observer-library "$observer_library" \
    --events "$event_count" --threads "$worker_count" --reserve-gib 30 \
    --output "$work/observed/$variant/$label"
}
for variant in standard candidate; do
  if [ "$variant" = standard ]; then sample="$ref/sample"; else sample="$work/sample400"; fi
  observe "$variant" 24 1 serial24
  observe "$variant" 24 12 mt24
  for label in serial24 mt24; do
    software/env/run.sh python3 -B software/analysis/lar_gap/observed_transport.py audit \
      --sample "$sample" --run "$work/observed/$variant/$label"
  done
  software/env/run.sh python3 -B software/analysis/lar_gap/observed_transport.py controls \
    --serial "$work/observed/$variant/serial24" --mt "$work/observed/$variant/mt24" \
    --output "$work/observed/$variant/controls.json"
  observe "$variant" 100 12 pilot100
  software/env/run.sh python3 -B software/analysis/lar_gap/observed_transport.py audit \
    --sample "$sample" --run "$work/observed/$variant/pilot100"
done
# Require both exact serial/MT and pilot readback gates before full replay.
observe standard 10000 12 production12
observe candidate 10000 12 production12
```

Short observed controls contain no failed cell assignments and the original
reader passes. The full observed runs expose the logical/physical-name mismatch
in that reader. Use the separately versioned auditor below for full production;
it repeats all native/saved-energy, primary, map, worker, library, source and
raw-artifact checks. It creates common saved-data readback in its own output
if absent, or revalidates an existing one. Every output directory must be fresh.
It preserves original partial/failed outputs and requires exact retained-hit
replay before final inference.

```sh
software/env/run.sh python3 -B software/analysis/lar_gap/observed_reaudit.py audit \
  --sample "$ref/sample" --run "$work/observed/standard/production12" \
  --retained-run "$ref/production12" --output "$work/reaudit/standard"
software/env/run.sh python3 -B software/analysis/lar_gap/observed_reaudit.py audit \
  --sample "$work/sample400" --run "$work/observed/candidate/production12" \
  --retained-run "$work/production12" --output "$work/reaudit/candidate"

plot_python=/Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python
"$plot_python" -B -m unittest discover -s software/analysis/lar_gap -p 'test_*.py'
"$plot_python" -B software/analysis/lar_gap/observed_recompare.py analyze \
  --standard "$work/reaudit/standard" --candidate "$work/reaudit/candidate" \
  --bootstrap 1000 --seed 13001000 --output "$work/reaudit/comparison"
MPLCONFIGDIR="$work/mpl-cache" "$plot_python" -B \
  software/analysis/lar_gap/observed_recompare.py plot \
  --summary "$work/reaudit/comparison/summary.json" --output "$work/reaudit/figures"
```

Actual retained run directories are `build/lar-gap10k/observed-v2/` for the six
short controls, `build/lar-gap10k/observed-production/` for the two full replays,
and `build/lar-gap10k/reaudit/` for corrected readback and final inference.
The observer library is under `build/lar-gap10k/observed/library/`.
Native inputs and the first candidate saved-hit production remain under
`build/lar-gap10k/corrected/`.

The committed compact summary and separate covariance support inspection and
replotting without event data. For a summary-only replot use `observed_recompare.py plot`
with `--summary docs/validation/lar-gap10k/summary.json` and a fresh ignored
`--output`. Full readback, replay and bootstrap re-inference require all retained
or regenerated ROOT/input/observer/native ledgers. Figures use ECAL colour and
solid/dashed variants. Pointwise percentile intervals keep exact endpoints.
All widths mix energy, angle, dead material and shower leakage; they do not
measure fixed-energy intrinsic resolution or establish an engineered service fit.
