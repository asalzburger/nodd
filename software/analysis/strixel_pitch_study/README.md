# Strixel pitch sensitivity — DES-042

Isolated **PROTOTYPE**: PR104 balanced geometry, unchanged transported effective
material, constant 3 T, one muon/event, pT 1/10/100 GeV, random charge,
uniform eta [-4,4] and full phi. Compare local-v pitches 0.5/1/1.5/2 mm at
fixed 75 µm fine pitch. Local-v means barrel z and endcap radial direction.

Native ACTS geometric digitization changes measured positions and clustered
covariance together. Single-cell variance is p²/12. No old 0.5 mm calibration
is reused. Truth-associated fitting measures ideal response sensitivity;
pattern recognition, occupancy, calibrated electronics, and a smaller material
budget are outside this fixed-material scan.

## Repeat native runs

Follow `skills/acts-spack/SKILL.md` and run preflight, then verify actual imports.
Use the existing built adapters; do not modify shared dependencies to run this
study. The supplier arguments are explicit so another checkout/build can be
selected and its identity recorded. Current machine paths are examples, not
portable dependencies. From this repository root, in one fresh zsh:

```sh
source software/env/truth_tracking.sh
python software/analysis/strixel_pitch_study/run_campaign.py \
  --tag repeat1 --jobs 3 --events 20000 \
  --nodd-dir ../nodd-software-layout \
  --build-dir ../nodd-gen3-material-mapping/build/balanced-baseline/dd4hep \
  --native-module-dir ../nodd-gen3-material-mapping/build/gen3-material-map-run/native \
  --observer-module-dir ../nodd-gen3-material-mapping/build/truth-tracking-baseline/native \
  --material-module-dir ../nodd-gen3-material-mapping/build/tracker-resolution-optimization/native \
  --comparison-dir ../nodd-gen3-material-mapping/build/tracker-resolution-optimization/confirmation/gaussian/balanced-pt10
```

Add `--dry-run` to inspect the twelve commands without importing ACTS or writing
outputs. Use a fresh tag for each repeat; completed results are never replaced.
Use `--events 100` for a transport/fit smoke, not reported precision estimates.
Raw ROOT, exported inputs and full truth/fitted/covariance arrays stay in ignored
`build/strixel-pitch-study`. Each native run fingerprints code, native libraries,
compact/material inputs, generator and exact simulated-hit payloads. Pairing is
verified from data rather than seed equality alone.

The initial campaign used the equivalent ignored launcher with `full-v3-*`
labels, three concurrent one-thread processes and source commit
`8b7c147b3b0da4bd40dcd9ad06c98abcb2de58f9`. The portable launcher above was
added without changing the executed native runner. Original v1/v2 pilot report
metadata advertised the wrong residual sign; arrays were always fitted−truth.
The defect was corrected and regression-tested before v3 production.

## Retain, analyze and plot

Use Python 3.11+ with `requirements.txt` installed in a task-owned analysis venv.
This can reuse the established analysis venv; it does not need ACTS to replay.

```sh
python software/analysis/strixel_pitch_study/services.py \
  --output docs/validation/DES-042/services.json
python software/analysis/strixel_pitch_study/analyze.py \
  --source build/strixel-pitch-study --pattern 'full-v3-*' \
  --output docs/validation/DES-042 --replicates 400
python software/analysis/strixel_pitch_study/report.py
python software/analysis/strixel_pitch_study/plot.py \
  --output docs/validation/DES-042/figures
```

For a repeated run use `--pattern 'full-repeat1-*'` and a fresh output directory.
After retention, omit `--source` to recompute every statistic from the portable
NPZ event arrays. The retainer first recomputes all residuals/pulls/flags from
the full native fitted parameters, truth and covariance. Machine-local absolute
paths are replaced by logical roles in retained reports; original report hashes
remain available. Retained events include unsuccessful fits, all diagnostic
flags and every uncut residual/pull, but omit redundant full covariance arrays.

The native preparation source list omitted `truth_tracking/metrics.py`; the
campaign separately checked its exact launch-commit blob/hash and its unchanged
completion bytes. Retention fingerprints it explicitly and replays all outputs
exactly from full native inputs. Keep this provenance limitation visible.

Signed-eta bins are 0.25 wide. Also retain absolute-eta bins and summary regions
0–1 / 1–2.5 / 2.5–4. Width is the central 68.27% half-width, with uncut SD/RMS
and bias retained. Ratios use the same generated-event bootstrap indices across
all four pitches; a separate intersection-of-successes result exposes survivor
effects. Under 30 finite entries remains undefined. Fit and native-match
fractions use every generated muon. Statistical errors omit model systematics.

Raw NPZ/CSV units are mm for d0/z0, radians for phi/theta, GeV⁻¹ for q/p,
and a dimensionless fraction for relative pT. Plot labels convert those units.
Run `verify.py --bootstrap` to repeat every paired-bootstrap uncertainty as well
as the faster point-statistic/source/accounting audit.

The plotter uses `unrooted.ScatterData` and its Matplotlib renderer for profile
points, with Matplotlib lines/error bars and standalone PNG/PDF artifacts.

## Service assumptions

The power/cable model is separate from the tracking run. It scans the two
existing unqualified electronic-load normalizations and the fraction of that
load which depends on channel count. Sensor leakage and network boards remain
fixed, and local LV rail I²R loss is recomputed. There is no power measurement.

Unchanged hardware saves zero installed cable, pipe or tray space. A separate
power-only reaggregation estimates whole 13.4 mm bundle removal within each
network, keeping fibres/cooling fixed. It requires redesigned LV/HV/control
fanout and connectors; neither its current capacity nor the new cable is
qualified. Report gross cable-envelope litres separately from effective Cu/PI
and internal void. Area-equivalent widths omit walls, bends and connectors and
do not certify a narrower corridor. Baseline native worst-sector demand already
exceeds the inherited 73 mm corridor packing budget.

```sh
python -m unittest discover -s software/analysis/strixel_pitch_study -p 'test_*.py' -v
```

See [DES-042](../../../docs/design/DES-042-strixel-pitch-study.md) and the
[retained results](../../../docs/validation/DES-042/results.md).
