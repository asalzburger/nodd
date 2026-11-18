# Reproduce restored1.8mmPb LAr controls

Physical model source53797385c374118838b2ade1ec3362328683cf75; native/contracts
frozen9913d9583e1d60c6d74f5367c59bcc138735d23d. Existing verified runtime
DD4hep1.38/Geant411.4.3/ROOT6.40.04; follow acts-spack preflight/reverification.
No new dependency/shared installation. Full events/XML/logs/libraries remain
under ignored build/. Use fresh output directories and exact original inputbytes;
contracts pin HEPEvt/truth and both metadata origins. macOS libraries below;
use actual.so equivalents on another verified node.

```sh
run_root=build/lar-restored-repeat
mkdir -p "$run_root"
python3 -B tools/lar_calorimeter/compact_prototype.py \
  --spec tools/lar_calorimeter/restored-sampling.json --output "$run_root/model"
software/env/run.sh cmake -S prototypes/calorimeter -B "$run_root/factories" -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$run_root/factories" \
  --target Components_nODDLArBarrelPrototype Components_nODDLArEndcapPrototype --parallel 4
software/env/run.sh cmake -S software/analysis/lar_response -B "$run_root/audit" -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build "$run_root/audit" --parallel 3
python3 -B software/analysis/lar_response/transport.py prepare \
  --baseline "$run_root/model/combined" \
  --primary-sample ../nodd-ecal10k/build/ecal10k/production-input --output "$run_root/sample"
```

Run the component and combined native audit commands from the
[original compact recipe](../lar-compact/reproduce.md), substituting this run_root.
Run compact_depth.py with both expected models/libraries, as in that recipe;
require the complete actual-period9088-ray scan. Native reports bind exact
compact/material/library/source hashes. Preserve original/dense/maintained models.

Before full production, repeat24events with1/12workers,100events with native
step limits and100events with the fixed5mm cap, each in a separate run directory;
audit each saved result. Require compact_controls.py exact serial/MT hits.
The production commands are:

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

Use existing analysis Python with NumPy2.5.4/Matplotlib3.11.2, not a new install.
Original reference run:
`../nodd-lar-10k-response/build/lar10k-resume/production12`.
Dense reference run: `build/lar-compact/production12`, whose independent
regeneration is in the original compact recipe. Repeat both comparisons:

```sh
plot_python=/path/to/existing/analysis/python
reference_run=../nodd-lar-10k-response/build/lar10k-resume/production12
contract=docs/validation/lar-restored/contract.json
comparison=original
OPENBLAS_NUM_THREADS=1 "$plot_python" -B software/analysis/lar_response/compact_compare.py analyze \
  --reference-run "$reference_run" --candidate-run "$run_root/production12" \
  --contract "$contract" --bootstrap 1000 --seed 13001000 --output "$run_root/raw-$comparison"
OPENBLAS_NUM_THREADS=1 "$plot_python" -B software/analysis/lar_response/compact_calibrate.py analyze \
  --reference-run "$reference_run" --candidate-run "$run_root/production12" \
  --contract "$contract" --output "$run_root/calibration-$comparison"
```

Repeat with reference_run=build/lar-compact/production12,
contract=docs/validation/lar-restored/dense-contract.json and comparison=dense.
The fixed calibration family/seed rules are in [protocol.md](protocol.md); no
new family search or tail cuts. Evaluated fold models and full-fit reuse tables
are separate, geometry/material-bound artifacts. Use compact_public.py to retain
all bin statistics/histograms and exact principal covariance submatrices without
publishing full event payloads. Source/render commands and hashes for final
three-model plots will accompany their results.


Production and statistical source was frozen at
`ec8815821a6530bbb6c6133332a5369d795b59f3` before any new outcomes. After each
paired analysis, curate with compact_public.py; published filenames are
original-summary.json/dense-summary.json and
original-calibrated-summary.json/dense-calibrated-summary.json. Keep original
and dense calibration-models.json artifacts separately. compact_diagnose.py
analyze/plot takes the original/restored saved runs, the original contract and
its raw/calibrated summaries/model artifact, as in the prior diagnosis recipe.
No refit is performed by diagnosis or overlay.

The final three-way overlay reads only committed aggregates:

```sh
MPLCONFIGDIR=build/lar-restored/mpl-cache XDG_CACHE_HOME=build/lar-restored/cache \
  "$plot_python" -B software/analysis/lar_response/restored_overlay.py \
  --original-dense-raw docs/validation/lar-compact/summary.json \
  --original-dense-calibrated docs/validation/lar-compact/calibrated-summary.json \
  --original-restored-raw docs/validation/lar-restored/original-summary.json \
  --original-restored-calibrated docs/validation/lar-restored/original-calibrated-summary.json \
  --dense-restored-raw docs/validation/lar-restored/dense-summary.json \
  --dense-restored-calibrated docs/validation/lar-restored/dense-calibrated-summary.json \
  --original-dense-diagnosis docs/validation/lar-compact/diagnosis-summary.json \
  --original-restored-diagnosis docs/validation/lar-restored/diagnosis-summary.json \
  --output build/lar-restored/overlay-repeat
```

Only resulting scientific figures and render/source hashes are published from
that output; the large duplicate overlayJSON remains local. Every underlying
statistic is already in the paired compact summaries. Use compact_compare.py
plot for original-summary.json into a fresh raw-figures directory, and
compact_calibrate.py plot for original-calibrated-summary.json into a separate
fresh calibrated-figures directory. These preserve signedeta/fullphi/tails,
transition and ten-bin underlying distribution controls.

The reusable restored table is
`calibration-models.json:models.candidate.full_fit_reuse_only`; evaluated fold
models are separate. Its compactSHA256 is
`2cfd36df7483b5382276ae1c77bb30d485a28ff8fd07865a929483ef517eda0c`,
materialsSHA256
`a074b67a8d0b96b6ebb80742088474a4d46ae639b77693fc240650268efc7353`.
Application accepts signal_GeV/eta/matching geometry, no true-energy input;
fresh validation is required before reuse outside the recorded ECAL-onlyB0
10–80GeV scope. SVG/PDF/PNG rendering may vary with plotting runtime; data/source
hashes and exported artifacts are retained.
