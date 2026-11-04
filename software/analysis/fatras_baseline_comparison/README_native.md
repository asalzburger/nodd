# Native old/current Fatras truth-fit comparison

This PROTOTYPE compares the exact old PR100 geometry/material map and current
PR110+112 DES043 geometry/map. It uses the maintained
`software/running/nodd_truth_tracking.py:run()` performance chain without
copying or modifying the fitter. Each case has 20,000 one-muon events, fixed
pT 1/5/10/100 GeV, random charge, origin, uniform eta[-4,4], full phi, seed42042,
one thread and constant Bz=3T for both Fatras and Kalman propagation.

Pixels use50µm×50µm geometric digital cells. Short strips use75µm×0.5mm old,
75µm×2mm current; long strips measure80µm loc0 on the actual stereo faces.
Native clustering, unique measurement associations, seven-measurement primary
selection, corrected truth proto finder, native truth seed and Kalman smoother
are preserved. Every fit, including wrong-charge fits and tails, remains in ROOT.

`prepare` checks compact/material/all-five-factory hashes against retained native
reports, matching sidecar source/binary hashes and pybind11 ABI11, and copies the
observer into separate ignored old/current directories. The expanded matching
maps therefore cannot conflict. Native material setup clears previous sensor,
pipe and volume slabs and validates exact keyed map reload/binning dynamically.

The old frozen error table is accepted only with its audited training report,
training measurement hash, exact current-old native digitization bytes and
matching response/settings. It cannot be used for the current2mm geometry.
Current calibration uses an independent50,000-event Fatras measurement-only
sample, seed142042 and log-uniform pT1..100GeV. The native generation, Fatras,
digitization, unique-association and measurement-writer prefix is preserved;
unneeded selection/seeding/Kalman stages are omitted. No fitted pull tunes errors.
The unchanged calibration wrapper runs the pinned ACTS script and population-SD
and cluster-overflow audit, including full sensitive-volume/coordinate coverage.

Run in a fresh zsh using existing installations:

```sh
source software/env/truth_tracking.sh
native_tool=software/analysis/fatras_baseline_comparison/run_native.py
python -B "$native_tool" prepare
python -B "$native_tool" case --baseline old --pt 5 --events 100 --pilot \
  --output build/fatras-baseline-comparison/pilot-old-pt5
python -B "$native_tool" train --baseline current --events 100 --pilot \
  --output build/fatras-baseline-comparison/pilot-current-training
```

Before expensive jobs, commit the executing source and record its full SHA.
The following `execution_revision` is supplied by the coordinator. Each job
checks all executing tracked files against it before and after execution;
unrelated later analysis/journal commits do not rewrite that source identity.

```sh
python -B "$native_tool" train --baseline current \
  --source-revision "$execution_revision"

# Existing analysis interpreter; no package installation.
export MPLCONFIGDIR="$PWD/build/fatras-baseline-comparison/plot-cache/matplotlib"
export XDG_CACHE_HOME="$PWD/build/fatras-baseline-comparison/plot-cache/xdg"
python -B "$native_tool" calibrate \
  --analysis-python ../nodd-gen3-material-mapping/build/truth-tracking-baseline/analysis-venv/bin/python

# Repeat for old/current and pT1,5,10,100; at most two native jobs concurrently.
python -B "$native_tool" case --baseline current --pt 5 \
  --source-revision "$execution_revision"
```

The calibration script is executed as a byte-identical copy under the owned
`calibration-source/software/analysis/truth_tracking` tree so its relative
upstream plot/cache outputs also remain local. Original and executed-copy hashes
and exact command are recorded; the algorithm is unchanged.

Cases are `build/fatras-baseline-comparison/performance/{old,current}-pt{1,5,10,100}`.
Current training and calibration are `training-current` and `calibration-current`.
Every case retains local `error-table.json`, complete ROOT outputs, inventories,
event/fit audit counts, map/calibration identities, tracked source hashes and
separate native-binary/output hashes. Existing reports reject replacement; use
a fresh directory after a failed attempt or source correction. Large payloads
remain ignored. No detector acceptance follows from successful execution.

```sh
python3 -B -m unittest discover \
  -s software/analysis/fatras_baseline_comparison -p test_native.py -v
```
