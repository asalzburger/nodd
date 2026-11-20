# Reproduce HCAL barrel-edge and fixed-direction response

Transport and statistical producers ran at frozen source7059bf6c. Use that
source for an exact new simulation/statistics replay. The later compact replay
wrapper is provided at this PR head and calls the same fixed-plot function.
Use fresh output directories; receipts and sample/analysis stages refuse
overwrite. Existing environment:
DD4hep1.38/3yd4hz3, Geant411.4.3/wfg55xi, ROOT6.40.04, Python3.14.5;
NumPy2.5.4/Matplotlib3.11.2 in the existing ACTS Python environment. The
acts-spack registry fingerprints differed; actual imports/packages/dataset
presence were reverified. No shared dependency was changed. All full event,
ROOT, geometry, scan-candidate payloads and bulky logs remain ignored/local.

```sh
python3 -B tools/hcal_response/export.py --output build/hcal50-edge/geometry-final
software/env/run.sh cmake -S prototypes/hcal_response -B build/hcal50-edge/factories -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build build/hcal50-edge/factories --parallel 3
software/env/run.sh cmake -S software/analysis/hcal_response -B build/hcal50-edge/audit -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build build/hcal50-edge/audit --parallel 3
software/env/run.sh python3 -B tools/hcal_response/native.py --directory build/hcal50-edge/geometry-final --library build/hcal50-edge/factories/libnODDHCALResponsePrototype.dylib --output build/hcal50-edge/native.json
```

```sh
software/env/run.sh python3 -B tools/hcal_response/direction.py --directory build/hcal50-edge/geometry-final --library build/hcal50-edge/factories/libnODDHCALResponsePrototype.dylib --output build/hcal50-edge/direction
```

The selector invocation is also recorded by its source-bound direction receipt.
Its source-bound5551candidate scan uses only finite geometric intersections;
ROOT independently confirms the winning direction and all nine sampled
neighbours before any showers. Preserve the complete prospective protocol and
immutable direction receipt, rather than replacing the direction after results.
Use actual platform library suffixes. Source/build hashes bind the libraries.

Prepare angular primaries with seed20261120, or `--primary-sample` pointing to
the retained original10k input directory for byte-identical HEPEvt/truth reuse.
Prepare separate2000calibration and10000validation samples at the frozen winner,
using `--fixed-eta 0 --fixed-phi -0.013089969389957472 --direction-receipt ...`
and distinct `--sample-role calibration|validation`/`--sample-id` values.
The cohort guards require their exact populations, successful native direction
receipt and exact physical geometry/hash correspondence.

Run angular24-event serial1/MT12 controls with transportseed202650001 and
compare the audited outputs before production. Every run uses
`--geometry-library ... --audit-library ... --max-step-mm 5 --reserve-gib 30`;
production uses12workers. Commands follow the shared transport README.

Run10000angular events atseed202650001 and audit all saved hits. Run2000fixed
calibration events atseed202650102, audit, then freeze the response factor with
`analyze.py calibrate --run ... --output .../calibration.json --bootstrap 1000`.
Only after this receipt exists, run10000fixed validation events atseed202650103
and audit. Reusing the independent calibration seed or validation events for
calibration is not allowed. No optical, SiPM, noise, threshold or digitization
model is added; all valid zeros and tails are included.

```sh
plot_python=/Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python
MPLCONFIGDIR="$PWD/build/hcal50-edge/mpl" "$plot_python" -B software/analysis/hcal_response/analyze.py analyze --run build/hcal50-edge/angular12 --output build/hcal50-edge/angular-analysis --baseline-run ../nodd-hcal-pion50/build/hcal50/production12 --bootstrap 1000 --seed 13001000
MPLCONFIGDIR="$PWD/build/hcal50-edge/mpl" "$plot_python" -B software/analysis/hcal_response/analyze.py fixed-analyze --run build/hcal50-edge/fixed12 --calibration-run build/hcal50-edge/calibration12 --calibration build/hcal50-edge/calibration.json --output build/hcal50-edge/fixed-analysis --bootstrap 1000
python3 -B -m unittest discover -s tools/hcal_response -p 'test_*.py' -v
"$plot_python" -B -m unittest discover -s software/analysis/hcal_response -p 'test_*.py' -v
```

The angular comparison jointly resamples matched primary IDs. The fixed result
independently resamples calibration/validation populations with seeds13001002
and13001001; every replicate refits the scalar factor and verifies the invariant
SD/mean. Compact summaries contain all histogram/bin widths, counts/zeros,
intervals, covariance and source bindings for replotting without event files.
Full physical cell/step/native/saved closure audits require the retained full
run data or a new simulation. Scalar calibration is an effective50GeV pion
response factor for the chosen direction; it is not intrinsic compensation or
an independent material-only sampling-fraction measurement.

Replay the published figures without any event files:

```sh
MPLCONFIGDIR="$PWD/build/hcal50-edge/mpl" "$plot_python" -B software/analysis/hcal_response/analyze.py plot --summary docs/validation/hcal50-edge/angular-summary.json --output build/hcal50-edge/replay-angular
MPLCONFIGDIR="$PWD/build/hcal50-edge/mpl" "$plot_python" -B software/analysis/hcal_response/replot_fixed.py --summary docs/validation/hcal50-edge/fixed-summary.json --output build/hcal50-edge/replay-fixed
```

`replot_fixed.py` only exposes the unchanged fixed-plot function as a compact
summary replay command; it does not rerun statistics or change the frozen
transport/analysis producer.
