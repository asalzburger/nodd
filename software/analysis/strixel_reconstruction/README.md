# DES042 native GBTS response cross-check

This isolated **PROTOTYPE** composes the unchanged DES041 native preparation,
GBTS, reconstruction, transport and SafeFatras helpers. The scientific input
revision is `4ea4af17727020bac2ba8f5e2f6172378711c15a`; the additional scope is
the GBTS amendment in `docs/design/DES-042-strixel-pitch-study.md`. No detector
design approval or calibrated coarse-pitch response is implied.

The matrix has 80 cases: pitches 0.5/1/1.5/2 mm, pT 1/5/10/100 GeV, Fatras
muons/electrons and Geant4 muons/electrons/pions, with 1,000 generated events
per case. Each native process has one ACTS thread. Seeds are 123042 for Fatras
muons, 133042 for guarded Fatras electrons and 143042 for Geant4. Electron
one-way multicomponent CKF and ordinary two-way muon/pion CKF are preserved.
The original `pt4-nominal-triplet` profile, cuts and hypotheses are unchanged;
all populations use the species protocol's converged ambiguity budget.

Preparation reconstructs the native balanced geometry and effective material
through physical roles, then requires all four frozen confirmation inputs.
Only local-v Gaussian sigma for systems 4/5 is multiplied by pitch/0.5. The
0.5 mm response equals the frozen pooled response. Pixel/fine-u/long-strip
response and `doMerge=False` remain fixed. Coarse response is a sensitivity
prescription. Bounded Gaussian rejection can change later RNG consumption;
identical seeds alone do not establish identical non-target measurements.
Even with identical pixels and seeds, strixel fine-u or long-strip noise can
change. Per-system fingerprints and the union of affected events are retained;
those cases do not isolate the longitudinal response alone.

## Execution

Use a fresh zsh in this checkout. Run the node preflight before native work;
the registry currently warns that setup/lock fingerprints changed. Do not
repair shared dependencies. Runtime imports must pass after activation.

```sh
python3 skills/acts-spack/scripts/preflight.py
source software/env/truth_tracking.sh
python -B software/analysis/strixel_reconstruction/runtime.py \
  --case fatras-muon-pt10-pitch0.5 --events 2 \
  --output /private/tmp/nodd-strixel-gbts/smoke/fatras-muon-pt10-pitch0.5

python -B software/analysis/strixel_reconstruction/campaign.py launch \
  --output build/strixel-gbts-repeat1 --jobs 3 --write-root
python -B software/analysis/strixel_reconstruction/campaign.py check \
  --output build/strixel-gbts-repeat1 --jobs 3 --write-root
python -B software/analysis/strixel_reconstruction/campaign.py resume \
  --output build/strixel-gbts-repeat1 --jobs 3 --write-root
```

Commit/freeze all executing source before the production launch. `--case`
may be repeated on campaign commands for a bounded smoke or pilot; `list`
prints exact IDs. `--events` changes the explicit campaign plan for smoke.
`--jobs` bounds concurrent independent native processes (default 1); it is
recorded in the plan and must be supplied identically to check/resume.
`--write-root` additionally writes the existing CKF/ambiguity track summaries
and measurement ROOT file. Mandatory all-event audit and `hits.root` are
always retained.

Default suppliers are `../nodd-gen3-material-mapping` for existing detector,
native sidecars and baseline evidence, and `../nodd-software-layout` for
ACTS runtime/source. Override with `--supplier-root` and `--runtime-root`;
the imported ACTS binding must resolve inside the declared runtime build.
Each Geant4 case uses a fresh process and the established persistent adapter.
SafeFatras changes no shared ACTS module or physics parameter. No build or
dependency modification is performed.

`launch` requires an empty campaign directory. The plan records case settings,
supplier paths and launcher source hashes. `resume` requires that exact plan,
verifies completed output hashes and skips those cases. Failed, interrupted,
changed or nonempty cases are refused; preserve them and launch a fresh output
directory. No implicit overwrite or retry erases evidence. Case stdout/stderr
is retained outside the case directory as `<case-id>.log`.

Launch order uses descending per-event sequencer time from the 20 frozen
DES041 population/momentum summaries, with case ID as the deterministic tie
breaker. The plan records reference hashes, estimates and full launch order.
This starts expensive Geant4 100 GeV electron cases early; previous timing is
only a scheduling estimate and is not an ETA under current contention.

## Evidence and checks

Each case retains `run-report.json`, `campaign.json`, `native-report.json`,
geometry selection/material map, baseline and scaled error tables,
digitization/pixel-selection inputs and exact GBTS configuration files.
`events.jsonl.gz` contains every generated event and all native candidates,
states, seeds and measurement truth associations. The report records frozen
source hashes, actual source/supplier paths, native module/runtime and
prepared/output hashes, baseline semantic equivalence and postrun immutability.

An appended native `RootSimHitWriter` writes `hits.root` tree `hits` after every
frozen algorithm. Existing algorithm positions and random streams are
preserved. This supplies the ROOT writer's persisted hit representation for
independent per-event transport fingerprints; its floating fields have native
writer precision, which can be lower than in-memory precision. Retained full
hit data must be reduced before removing large local files. Event audit
`simhits` alone is only a count and cannot establish exact hit pairing.

The native runner checks complete event identities, species/hypotheses, the
complete CKF measurement subset and fewer-than-3 shared measurements for
every ambiguity survivor before quality cuts. The report also records whether
the old 1,000-removal budget was provably nonlimiting by raw candidate count.
Independent analysis remains responsible for full persisted-hit pairing,
pixel/seed comparisons, exact variance checks, efficiencies, residuals/pulls
and paired uncertainty. Formal review and scientific acceptance remain separate.

The separate baseline bridge compares fresh 0.5 mm portable event observables
to matching event IDs in the frozen 5,000-event population evidence:

```sh
python -B software/analysis/strixel_reconstruction/bridge.py \
  --data docs/validation/DES-042/gbts \
  --output docs/validation/DES-042/gbts/baseline-bridge.json
python -B software/analysis/strixel_reconstruction/bridge.py \
  --data docs/validation/DES-042/gbts \
  --output docs/validation/DES-042/gbts/baseline-bridge.json --verify
```

```sh
python3 -B -m unittest discover \
  -s software/analysis/strixel_reconstruction -p test_runtime.py -v
```


## Retain, compare and plot

Use a separate Python3.11 analysis environment with the existing pinned
`requirements.txt`. The recorded run reuses
`../nodd-gen3-material-mapping/build/truth-tracking-baseline/analysis-venv/bin/python`
(NumPy2.4.6, uproot5.7.7, Matplotlib3.11.2 and unrooted). Analysis does not need
ACTS imports; native execution uses the separate activated Python3.14 runtime.
No dependency is installed or changed by these scripts. Choose fresh evidence
and figure directories for a new native campaign or changed analysis source.
For example, after the complete native repeat above:

```sh
python software/analysis/strixel_reconstruction/analyze.py \
  --source build/strixel-gbts-repeat1 \
  --output build/strixel-gbts-repeat1-evidence --replicates 400 --jobs 3
python software/analysis/strixel_reconstruction/analyze.py \
  --output build/strixel-gbts-repeat1-evidence --replicates 400 --verify
python software/analysis/strixel_reconstruction/bridge.py \
  --data build/strixel-gbts-repeat1-evidence \
  --output build/strixel-gbts-repeat1-evidence/baseline-bridge.json
python software/analysis/strixel_reconstruction/root_audit.py \
  --native build/strixel-gbts-repeat1 --data build/strixel-gbts-repeat1-evidence \
  --output build/strixel-gbts-repeat1-evidence/root-audit.json
python software/analysis/strixel_reconstruction/plot.py \
  --data build/strixel-gbts-repeat1-evidence/profiles.json.gz \
  --output build/strixel-gbts-repeat1-evidence/figures
```

The initial full campaign is `build/strixel-gbts-production`, with source freeze
`8c45136098d1e4d407c4d2f96e3590bb78eb6b75`. Its portable evidence is retained
under `docs/validation/DES-042/gbts`. To replay retained statistics/bootstrap and
report text without ACTS or native ROOT files:

```sh
python software/analysis/strixel_reconstruction/analyze.py \
  --output docs/validation/DES-042/gbts --replicates 400 --verify
python software/analysis/strixel_reconstruction/bridge.py \
  --data docs/validation/DES-042/gbts \
  --output docs/validation/DES-042/gbts/baseline-bridge.json --verify
```

A full ROOT re-audit requires the original ignored native outputs and
`--write-root` at native launch. The audit composes the unchanged DES041 auditor
through temporary views, checks all80cases, every generated track event including
zero-track events, candidate counts, float32 measurement variances and complete
representative perigee/uncertainty tuples. Add `--verify` to its command for exact
re-audit. The underlying matrix/configuration validator is a pinned Git blob;
its source pin is separate from the corrected offline statistical analyzer.
Git history containing the documented source pins is required.

Offline `--jobs` bounds independent per-case retention workers (default1);
statistical reduction stays serial and deterministic. Native and offline jobs
are separate settings. Source guards reject changes to executing analyzer bytes;
failed retention preserves completed case artifacts and does not finalize the
inventory.

Retention first runs the unchanged independent native classifier and all its
response/space-point/covariance/ambiguity gates. It keeps all-event metricarrays,
compressed summaries/configurations, per-event transport/measurement/seed
fingerprints and original native source/input/output hashes. Known workspace
paths become distinct logical paths; unknown external paths retain opaque
identifiers so same-basename files cannot collapse. Hit pairing proves exact
persisted float32 all-hit payload equality, not native float64 bit identity.
Index-free physical coordinate multisets are separate from index-bearing ordered
pixel space points and seed membership. Net count deficits/excesses do not
count every removed/recovered hit when those cancel within one event.

Each population/momentum is scored separately. Headline efficiency uses every
generated primary; conditional reconstructability, fake/secondary/duplicate and
charge/covariance failures remain distinct. Widths use the central68.268949%
half-interval with at least30finite entries, all uncut tails and common-success
controls. Four hundred jointly resampled generated-event bootstraps preserve
pairing. Zero-discordance efficiency bootstraps are flagged degenerate with
an exact95% discordance upper bound and a conservative pointwise contrast bound;
none establishes equivalence or covers simultaneous multiple comparisons.

```sh
python -m unittest discover -s software/analysis/strixel_reconstruction \
  -p 'test_*.py' -v
```

Per the 2026-10-31 human publication instruction, portable arrays and compressed
case/profile/native data remain local and ignored. CI runs the focused synthetic
tests and verifies the published figure inventory, hashes and plotting-source
bindings. Full statistics/bootstrap/bridge/ROOT and figure replay remain local
checks requiring those files or a regenerated campaign. The original execution
and review revisions remain in the local archive ref documented by
`docs/validation/DES-042/local-artifacts.json`; the consolidated PR preserves their
scientific source bytes. A configured workflow is not a remote CI pass.
