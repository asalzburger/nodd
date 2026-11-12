# Reproduce the staggered calibration campaign

Read the [prospective protocol](protocol.md) and follow the existing
[Spack workflow](../../../skills/acts-spack/SKILL.md). Reverify the runtime doctor
and the [original ECAL library build](../ecal10k/README.md#reproduce).
Use the frozen staggered input from [PR136](../ecal-staggering/reproduce.md).
The compact XML hash is d78ecea5c5aa5173af54a4ce392994491eede936a7f4edb87d55bc72e69a0c2b.
Native geometry/audit libraries and transport steering are reused unchanged.
Set `ECAL10K_PLOT_PYTHON` to the existing NumPy/Matplotlib Python executable.
The execution uses `/Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/python`.
Use fresh directories; never overwrite retained evidence.

```sh
python3 -B software/analysis/calorimeter_digitization/highstat_sample.py prepare \
  --source build/ecal-staggering/production-input --output build/ecal-highstat/repeat
```

Defaults produce ten training batches and two independent validation batches,
10k events each, primary seed base14410000 with1009 increments and transport seed
base144812341 with104729 increments. IDs are local0…9999 in each ROOT file;
explicit campaign offsets map them to0…119999. Preparation checks exact primary
momentum tuples are disjoint from the old10k and all new batches. Generation used
source d56c1093; later fail-closed seed/reserve/steering guards leave all default
primary bytes and seed values unchanged. Campaign manifests retain exact hashes.

Run each batch serially (names train-000…train-009,validation-000…validation-001):

```sh
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/highstat_sample.py run-batch \
  --campaign build/ecal-highstat/repeat --batch train-000 \
  --geometry-library build/ecal10k/calo/libnODDCalorimeterPrototype.dylib \
  --audit-library build/ecal10k/audit/libnODDAngularAudit.dylib
software/env/run.sh python3 -B software/analysis/calorimeter_digitization/highstat_readback.py \
  --sample build/ecal-highstat/repeat/batches/train-000/input \
  --run build/ecal-highstat/repeat/batches/train-000/run \
  --output build/ecal-highstat/repeat/batches/train-000/analysis
```

Before the campaign, run a separate24-event/12-worker pilot with the unchanged
`angular_sample.py run`, using the train-000 input and its declared transport seed,
then audit with `angular_analyze.py audit`. The pilot used
`build/ecal-highstat/pilot12`; this pilot does not replace any full campaign batch.
Readback/features may run while the next batch transports. Keep one12-worker
transport process and all disk guards. Audit validation input/physics, while
keeping its calibration performance uninspected until the complete model freezes.

After all ten training feature receipts exist:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  "$ECAL10K_PLOT_PYTHON" -B software/analysis/calorimeter_digitization/highstat_analysis.py train \
  --campaign build/ecal-highstat/repeat --output docs/validation/ecal-highstat/repeat-frozen
```

Review and commit the model JSON before inspecting fresh-validation predictions.
Pass that exact Git revision below. The evaluator verifies the committed model,
calibration/analysis source, campaign and training-feature hashes, and checks all
validation feature semantic headers before opening any validation feature array.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  "$ECAL10K_PLOT_PYTHON" -B software/analysis/calorimeter_digitization/highstat_analysis.py evaluate \
  --campaign build/ecal-highstat/repeat \
  --models docs/validation/ecal-highstat/repeat-frozen/models.json \
  --freeze-commit COMMITTED_MODEL_REVISION \
  --output build/ecal-highstat/repeat-results \
  --predictions-output build/ecal-highstat/repeat-validation-predictions.npz \
  --bootstrap 1000 --training-bootstrap 200
```

The original-method exploratory learning curve is independently reproducible:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  "$ECAL10K_PLOT_PYTHON" -B software/analysis/calorimeter_digitization/highstat_learning.py \
  --features build/ecal-staggering/staggered-features \
  --output build/ecal-highstat/repeat-learning \
  --predictions-output build/ecal-highstat/repeat-learning-predictions.npz --bootstrap 200
```

Export all scientific figures from compact summaries without ROOT or event files:

```sh
MPLCONFIGDIR="$PWD/build/ecal10k/mpl-cache" XDG_CACHE_HOME="$PWD/build/ecal10k/cache" \
  "$ECAL10K_PLOT_PYTHON" -B software/analysis/calorimeter_digitization/highstat_plots.py \
  --learning docs/validation/ecal-highstat/learning/learning-curve.json \
  --summary docs/validation/ecal-highstat/results/summary.json \
  --output build/ecal-highstat/standalone-replot
```

Omit `--summary` to render only the completed learning curve. The curator
`highstat_evidence.py --campaign ROOT --output FILE` assembles compact per-batch
provenance/resources after all120k audits pass. It never copies event payloads.

Actual narrow tests are:

```sh
software/env/run.sh python3 -B -m unittest discover -s software/analysis/calorimeter_digitization -p 'test_highstat_pipeline.py' -v
"$ECAL10K_PLOT_PYTHON" -B -m unittest discover -s software/analysis/calorimeter_digitization -p 'test_highstat_model.py' -v
"$ECAL10K_PLOT_PYTHON" -B -m unittest discover -s software/analysis/calorimeter_digitization -p 'test_highstat_analysis.py' -v
```

The native full10k equivalence check repeats highstat_readback on the retained
PR136 ROOT, then compares all identities, primary errors, worker counts and root
hash plus every feature array against `staggered-features` at1e-10 tolerance.
The full files remain ignored/local. Neither a test pass nor the final review
changes detector lifecycle/sign-off states.
