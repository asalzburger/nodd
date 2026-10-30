# Full tracker reconstruction (DES041 PROTOTYPE)

The maintained PR104 balanced Gen-3 tracker, Fatras, constant 3 T and the frozen
PR101 pooled Gaussian response feed **measured pixel space points → native ACTS
Core GBTS → seed parameter estimation → CKF over every tracker measurement →
greedy ambiguity resolution**. Pixels/short strips are 2D, long strips 1D. No
truth track groups, truth momentum seeds or primary-based measurement filtering
enter reconstruction. Truth is used by independent observers and scoring.

The selected profile is `pt4-nominal-triplet`: minPt 0.4 GeV,
`minSeedLevel=2`, `addTriplets=true`, `maxAbsEtaAddTriplets=4.1`, and optional
innermost z0 histogram disabled (`z0HistogramMaxBarrelOrder=-1`). Ordinary tau
cuts remain. It was chosen from13 profiles × 500 events/pT; one configuration is
frozen acrosspT 1/5/10/100 GeV. The untouched default control is retained.
The histogram sensitivity and all unsuccessful configurations remain evidence.

## Native execution

Use a verified ACTS environment and the matching source revision
`355ea68493b326956756c9386d2fd9eaf9328568`; the separate newer development
checkout does not identify the executed runtime. Read the existing acts-spack
skill and run its preflight before relying on the node. Do not install/change
shared dependencies. The current node's setup/lock fingerprints and full
DD4hep/G4 source remain unverified; installed libraries and the matching ACTS
source/binaries were checked and fingerprinted. Fatras is the simulation here.

Build the maintained tracker as described in `tools/tracker_dd4hep/README.md`
into `build/balanced-baseline/dd4hep`. The source compact is generated, not a
hand-edited input. Verify the registered baseline:

```sh
python3 -B tools/tracker_dd4hep/verify_baseline.py
source software/env/truth_tracking.sh
```

Build the GBTS helper using
`software/source/ActsExamples/TrackerGbts/README.md`. Build the observer similarly:

```sh
cmake -S software/source/ActsExamples/TrackerReconstruction \
  -B build/tracker-reconstruction/native-audit \
  -DNODD_ACTS_SOURCE=/path/to/matching/acts355ea684 \
  -DNODD_ACTS_BUILD=/path/to/existing/acts/build \
  -DPython_EXECUTABLE="$(command -v python)" \
  -Dpybind11_DIR=/path/to/installed/pybind11-3.0.4/share/cmake/pybind11
cmake --build build/tracker-reconstruction/native-audit --parallel 4
```

The existing portal-material and unique-association observers from PR100/101
and the effective-profile helper from PR104 must be present in their documented
`build/` directories. `prepare.py` recreates material/calibration by physical
role and donor, checking exact material/response payload identity against the
retained balanced confirmation. It does not apply the old map by numeric IDs.

Fresh output directories are required. Every run fingerprints code, binaries,
factory libraries and effective inputs at launch/close. The optional ROOT output
contains track summaries/full perigee covariance and measurements. Predicted,
filtered and smoothed state parameters/variances plus ordered source links are
retained in the task-owned native event audit. The stock ROOT state writer
triggered unmasked invalid-operation exceptions in a diagnostic run and is not
scheduled; FPE checks stay enabled and no masks were expanded.

```sh
python software/running/nodd_tracker_reconstruction.py \
  --pt 1 --events 100 --profile control --phase smoke \
  --output build/tracker-reconstruction/my-smoke

# Thirteen fixed profiles share exactly the same generated/smeared sample.
# Repeat separately for --pt 5, 10, 100; preparation is reused within each batch.
python software/running/nodd_tracker_reconstruction.py \
  --pt 1 --events 500 --profile all --phase tuning \
  --output build/tracker-reconstruction/my-tuning/pt1

python software/running/nodd_tracker_reconstruction.py \
  --pt 1 --events 5000 --profile pt4-nominal-triplet --phase validation \
  --campaign docs/validation/tracker-reconstruction/frozen/validation-campaign.json \
  --write-root --output build/tracker-reconstruction/my-validation/selected/pt1
```

Run all four momenta for the selected profile and `control`, with one identical
validation campaign. Source/configuration must remain unchanged during native
execution. The original seed 103042 attempt failed its FPE gate; final validation
uses fresh seed 123042, frozen before launch. Reconstruction cuts did not change.
Timing separates one-time geometry setup from sequencer execution.

## Analysis and replay

Use an isolated analysis environment with NumPy/Matplotlib, such as the existing
`build/truth-tracking-baseline/analysis-venv` or the pinned requirements in
`software/analysis/requirements-unrooted.txt`. Native ACTS is unnecessary for
retained-data replay:

```sh
python software/analysis/tracker_reconstruction/analyze.py \
  build/tracker-reconstruction/my-validation/selected/pt1 \
  --output build/tracker-reconstruction/my-analysis/selected/pt1
python software/analysis/tracker_reconstruction/select_profile.py \
  --input build/tracker-reconstruction/tuning-analysis \
  --output build/tracker-reconstruction/my-selection
python software/analysis/tracker_reconstruction/verify.py
python software/analysis/tracker_reconstruction/plot.py \
  --data docs/validation/tracker-reconstruction/validation \
  --output build/tracker-reconstruction/replayed-figures
python -B -m unittest discover -s software/analysis/tracker_reconstruction -p 'test_*.py' -v
```

Matching uses unique inlier source measurements, purity/completeness≥0.5,
separately recognizing simulated secondaries. Quality requires≥7 inliers,
reference surface, finite fit parameters/χ², positive ndf and positive-definite
bound covariance. Every generated muon stays in the headline denominator.
Conditional sets require≥6 unique sensor measurements and≥3/4 physical pixel
groups. Every completed CKF candidate and ambiguity survivor is audited;
propagation errors without output are not counted as candidate objects.

One deterministic primary representative supplies full uncut residual/pull
arrays: most inliers, then lowestχ²/ndf, then stable track index. The sign is
truth−reco with wrappedφ. Time is stored as native ct[mm] and converted to ns
for plots; it is prior dominated without measured timing. Wrong-charge fits
remain matched and are reported separately. Efficiency and fake-event intervals
use independent events; candidate fraction bootstrap resamples whole events.
Zero fake events retain an exact one-sided 95% upper limit, never zero uncertainty.
This single-muon study does not establish high-occupancy/pile-up fake performance.

See the retained [results](../../../docs/validation/tracker-reconstruction/results.md),
governing [DES041](../../../docs/design/DES-041-tracker-gbts-reconstruction.md),
frozen configuration/selection, all tuning summaries, event arrays and native
execution manifests. Human design sign-off remains pending.
