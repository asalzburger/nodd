# Gen3 truth-associated tracking baseline

This isolated **PROTOTYPE** characterizes the PR100 Gen3 nODD tracker using
Geant4 or Fatras, geometric digitization and a native truth-associated Kalman
fit. It follows the ACTS full-chain and truth-tracking examples. Geometry and
keyed material-map identities must match. This is not pattern-recognition
performance or an untouched upstream ODD detector.

The human selected a constant **3 T** field. [campaign.json](campaign.json)
centralizes one muon per event, random charge, origin vertex, uniform eta
[-4,4], full phi and fixed pT 1/10/100 GeV. Each performance case has 20,000
events. Pixels use 50×50 micrometre cells; short strips 75 micrometre ×0.5 mm
cells; each long-strip face measures one coordinate with 80 micrometre pitch.
Stereo comes from the physical geometry. The geometric digitizer needs two
physical segmentation axes, including one full-length unmeasured-axis bin for
long strips.

Use the [native build/run guide](../../source/ActsExamples/TruthTracking/README.md).
Source software/env/truth_tracking.sh in a fresh zsh to activate the existing
native venv without copying assets into shared installations. Native outputs
remain under ignored build/truth-tracking-baseline. Keep installed binaries,
source revisions and executed content hashes distinct.

## Independent hit-error training

Run nodd_truth_tracking.py with --training: 50,000 independent Fatras events,
log-uniform pT 1–100 GeV, seed 142042. ROOT measurement output retains measured
coordinates, truth, variances and cluster sizes. Training events do not enter
reported performance or fitted-pull tuning.

~~~sh
uv venv --python python3.11 build/truth-tracking-baseline/analysis-venv
uv pip install --python build/truth-tracking-baseline/analysis-venv/bin/python \
  -r software/analysis/truth_tracking/requirements.txt

build/truth-tracking-baseline/analysis-venv/bin/python \
  software/analysis/truth_tracking/calibrate_errors.py \
  --training build/truth-tracking-baseline/training-fatras \
  --acts-source ../nodd-software-layout/software/submodules/acts \
  --output docs/validation/truth-tracking-baseline
~~~

The upstream filename uses British spelling, error_parameterisation.py.
The wrapper executes its unchanged function with the exact scalar columns it
uses, avoiding unrelated jagged barcode columns. Raw script JSON is retained.
The pinned script stores an exact-size width before pooling the last plotted
group; native lookup applies that entry to all larger sizes. The audited table
recomputes exact-size groups below the final entry and a pooled overflow group
at that entry. An unsupported internal size explicitly starts a merged tail.
Each group retains count, bias, population SD and uncentered RMS.

The JSON field rms follows the upstream convention of centered population SD,
in mm. Native loading squares it once. Both backends use one frozen file.
Native cluster merging recomputes covariance, so the isolated adapter applies
the table after clustering, preserving measurement IDs, positions and
associations. Only measured marginal variances change. The table supplies no
coordinate correlations or incidence dependence.

The native CLI takes --simulation, --pt, --events, --manifest, --nodd-dir,
--build-dir, --error-table and --output. Pass the retained
hit-error-parameterization.json to all six performance cases. The Geant4
persistent-run adapter is used only after a standard/persistent comparison:
every ACTS event still contains one independent Geant4 event, with identical
physics list, cuts, geometry and per-event seeds.

The task-local truth adapter corrects a pinned double sim-hit-index lookup and
uses unique primary/measurement pairs before seven-measurement selection,
truth matching and proto-track ordering. Full measurement/simhit contributions
remain for truth averages. Native simulation, clustering positions and Kalman
fitting remain in ACTS/Geant4.

## Performance reduction and replay

~~~sh
build/truth-tracking-baseline/analysis-venv/bin/python \
  software/analysis/truth_tracking/export_profiles.py \
  --input build/truth-tracking-baseline \
  --output docs/validation/truth-tracking-baseline/profiles.json.gz

build/truth-tracking-baseline/analysis-venv/bin/python \
  software/analysis/truth_tracking/plot_profiles.py \
  --data docs/validation/truth-tracking-baseline/profiles.json.gz \
  --output docs/validation/truth-tracking-baseline/figures

build/truth-tracking-baseline/analysis-venv/bin/python -m unittest discover \
  -s software/analysis/truth_tracking -p 'test_*.py' -v
~~~

Reduction verifies input hashes, generated momenta, primary identities, at most
one fitted track per event, native attrition counts, and every written
measurement variance against the table. Residuals are independently calculated
from generated truth and fitted parameters, with wrapped phi. The pT pull
includes the full theta–q/p covariance and both charge signs.

Missing fits remain in generated-event denominators. Pulls require finite,
symmetric, positive-definite five-parameter covariance; residuals remain when
covariance is invalid. Bins with fewer than 30 finite entries have null
estimates. Resolution is the central 68.27% half-width; full sample SD/RMS and
biases are also retained without tail cuts. Pull widths use full sample SD.
Errors use an event bootstrap (mean SE uses SD/sqrt(N)); fractions use Wilson
z=1 intervals. Training and detector-model systematics are omitted.

Figures show signed eta for all momenta/backends and pT in three eta slices.
All eight absolute-eta slices remain in compressed data and CSV. Replay checks
analysis/configuration identities and count partitions; retained summaries do
not replace native ROOT provenance.

Production schedules the native truth-parameter extractor and zero-smearing
seed stage directly. The pinned original TruthTrackFinder is excluded because
its faulty double-index lookup can dereference invalid hit pointers; only the
corrected unique-measurement proto finder is scheduled. Earlier completed and
crashed campaigns are retained under ignored pre-reference-removal-controls and
are excluded from the final profiles. The original-reference count is explicitly
disabled in final native reports; zero there is a sentinel, not a measurement.

Retained provenance omits machine-local absolute paths while preserving file
roles, basenames, SHA256 identities and the original report hash. Offline CI
checks retained training/table group consistency and replays all figures; the
independent native ROOT assessment is recorded separately.

Native double-matching completeness can mark partial fits Fake and omit writer
truth. The reducer retains seed-associated residuals for only the guarded
single-primary/single-proto/single-output case, verifies selected ROOT barcodes,
counts native unmatched/Fake fits explicitly and rejects any nonzero conflicting
barcode. Generated truth supplies all residuals. These fits do not count as
native-matched efficiency, and no completeness cut removes their tails.

The all-eta full-distribution follow-up uses export_pulls.py and plot_pulls.py,
with pulls_config.json controlling common linear-core/log-tail bins. These
histograms use the requested truth-minus-reconstructed sign; prior profile
figures keep their original sign. All six bound parameters (including explicitly
unmeasured time) and derived pT are retained, with full-range/core views and
all finite tails in normalization. See docs/validation/truth-tracking-baseline/
pulls/README.md for commands and limitations.
