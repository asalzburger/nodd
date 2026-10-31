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
identical seeds alone do not establish identical measured pixels.

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
  --output build/strixel-gbts-production --jobs 3
python -B software/analysis/strixel_reconstruction/campaign.py check \
  --output build/strixel-gbts-production --jobs 3
python -B software/analysis/strixel_reconstruction/campaign.py resume \
  --output build/strixel-gbts-production --jobs 3
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
