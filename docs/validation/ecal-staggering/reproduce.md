# Reproduce the physical staggering and calibration tests

Status: **PROTOTYPE**. Read the [frozen protocol](protocol.md) before running.
The original [10k input and build recipe](../ecal10k/README.md#reproduce)
provides both native libraries and the unchanged baseline run. Preserve it.
The [aggregate evidence](geometry-and-run.json) binds the original input bytes,
candidate XML, unchanged native libraries, native checks, saved-primary audit,
worker settings, disk budget and run resources. The [compact result](results/summary.json)
binds both feature receipts, model coefficients and exact analysis source hashes.

Activate and verify the [node-specific ACTS Spack environment](../../../skills/acts-spack/SKILL.md),
then run `software/env/run.sh python3 -B software/env/doctor.py`.
The executed environment supplied DD4hep/DDG4 1.38, Geant4 11.4.3, ROOT 6.40.04,
EDM4hep 1.1.1 and podio 1.8. The existing plotting Python supplied NumPy 2.5.4
and Matplotlib 3.11.2; set `ECAL10K_PLOT_PYTHON` to that executable.
There are no new shared dependencies. Local execution used
`/Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python` for plotting.

Use fresh output directories. The example uses a fresh `repeat` root; the actual
retained execution used `build/ecal-staggering` directly. The dense native checks
and feature extraction require ROOT. Plotting and statistical controls need only
NumPy/Matplotlib and the committed source.

```sh
ECAL_TEST_ROOT=build/ecal-staggering/repeat
python3 -B software/analysis/calorimeter_digitization/staggered_geometry.py \
  --source build/ecal10k/production-input --output "$ECAL_TEST_ROOT/production-input"
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/staggered_native.py \
  --sample "$ECAL_TEST_ROOT/production-input" \
  --library build/ecal10k/calo/libnODDCalorimeterPrototype.dylib \
  --output "$ECAL_TEST_ROOT/native-dev.json"
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/staggered_screen.py \
  --baseline build/ecal10k/production-input/detector.xml \
  --staggered "$ECAL_TEST_ROOT/production-input/detector.xml" \
  --output "$ECAL_TEST_ROOT/screen-dev"
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/angular_sample.py run \
  --sample "$ECAL_TEST_ROOT/production-input" --output "$ECAL_TEST_ROOT/pilot12" \
  --geometry-library build/ecal10k/calo/libnODDCalorimeterPrototype.dylib \
  --audit-library build/ecal10k/audit/libnODDAngularAudit.dylib --events 24 --threads 12
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/angular_analyze.py audit \
  --sample "$ECAL_TEST_ROOT/production-input" --run "$ECAL_TEST_ROOT/pilot12"
```

Before production, record the pilot ROOT bytes/event and require twice its 10k
projection plus 30 GiB reserve. The actual pilot used 1,204,606.875 bytes/event,
requiring 52.438 GiB. The production runner was given the slightly more
conservative 1,276,825.0833 bytes/event from the earlier continuous control.
Its live disk guard remained enabled. No retained data were deleted.

```sh
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/angular_sample.py run \
  --sample "$ECAL_TEST_ROOT/production-input" --output "$ECAL_TEST_ROOT/production12" \
  --geometry-library build/ecal10k/calo/libnODDCalorimeterPrototype.dylib \
  --audit-library build/ecal10k/audit/libnODDAngularAudit.dylib \
  --events 10000 --threads 12 --bytes-per-event 1276825.0833333333
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/angular_analyze.py audit \
  --sample "$ECAL_TEST_ROOT/production-input" --run "$ECAL_TEST_ROOT/production12"
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/staggered_features.py \
  --sample build/ecal10k/production-input --run build/ecal10k/production12 \
  --output "$ECAL_TEST_ROOT/baseline-features"
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/staggered_features.py \
  --sample "$ECAL_TEST_ROOT/production-input" --run "$ECAL_TEST_ROOT/production12" \
  --output "$ECAL_TEST_ROOT/staggered-features"
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  "$ECAL10K_PLOT_PYTHON" -B software/analysis/calorimeter_digitization/staggered_results.py compare \
  --baseline "$ECAL_TEST_ROOT/baseline-features" --staggered "$ECAL_TEST_ROOT/staggered-features" \
  --output "$ECAL_TEST_ROOT/results" --predictions-output "$ECAL_TEST_ROOT/predictions.npz" \
  --bootstrap 1000 --seed 1338000
MPLCONFIGDIR="$PWD/build/ecal10k/mpl-cache" XDG_CACHE_HOME="$PWD/build/ecal10k/cache" \
  "$ECAL10K_PLOT_PYTHON" -B software/analysis/calorimeter_digitization/staggered_plots.py \
  --summary "$ECAL_TEST_ROOT/results/summary.json" --output "$ECAL_TEST_ROOT/results"
```

`staggered_evidence.py --local-root ROOT --output DEST` curates the aggregate
geometry/run record after successful audits. It expects `disk-budget.json`
with the recorded pilot bytes/event and conservative GiB budget at ROOT.
The native validation initially ran at `3af5538f`, before source commit;
its explicit script and XML hashes bind the executed source. The frozen
production XML is byte-identical. Baseline features were likewise extracted
before their source commit; their producer hash is authoritative. The physical
preparer and packer hashes are recorded separately from the native factory.

Replot every scientific figure, including vector SVG, from committed summaries
alone, without event files or ROOT:

```sh
MPLCONFIGDIR="$PWD/build/ecal10k/mpl-cache" XDG_CACHE_HOME="$PWD/build/ecal10k/cache" \
  "$ECAL10K_PLOT_PYTHON" -B software/analysis/calorimeter_digitization/staggered_plots.py \
  --summary docs/validation/ecal-staggering/results/summary.json \
  --output build/ecal-staggering/standalone-replot
```

Actual narrow controls comprise 9 physical geometry tests, 8 existing endcap
packing regressions, 5 calibration tests and 2 statistical-moment tests:

```sh
python3 -B -m unittest discover -s software/analysis/calorimeter_digitization -p 'test_staggered_geometry.py' -v
python3 -B -m unittest discover -s tools/calorimeter_hardware -p 'test_edges.py' -v
"$ECAL10K_PLOT_PYTHON" -B -m unittest discover -s software/analysis/calorimeter_digitization -p 'test_staggered_calibration.py' -v
"$ECAL10K_PLOT_PYTHON" -B -m unittest discover -s software/analysis/calorimeter_digitization -p 'test_staggered_results.py' -v
```

A separate identical-data integration control passes the baseline features to
both geometry arguments with 5 bootstrap replicas: every layout contrast and
interval is exactly zero. This is a software control, not a staggered result.

The full ROOT files, exact input/event ledgers, feature/mask/prediction NPZ/JSON,
full 102 MB physical geometry audit, dense-ray NPZ and bulky logs remain ignored
under `build/`. Only plots, recipes and compact aggregate/binwise evidence enter
Git. Equal primary bytes and per-event seeds do not imply identical shower
histories after physical geometry/material changes. No fixed-energy resolution
certification, electronics/noise model or engineering acceptance is provided.
