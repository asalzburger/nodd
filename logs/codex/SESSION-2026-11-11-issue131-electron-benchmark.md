# SESSION-2026-11-11-issue131-electron-benchmark — Post-PR129 electron benchmark

## Scope and selected public inputs

This contemporaneous, curated record covers issue
[#131](https://github.com/asalzburger/nodd/issues/131), request
`131-35766022791`. The supplied public snapshot identifies issue author and
label actor `asalzburger-review`; the issue was created at
2026-11-11T05:55:27Z and the `agent_task` label event at
2026-11-11T05:55:29Z. The issue snapshot has no comments. Exact issue request:

> Afrer #129 has merged, please run a gain a 100 event electron sample (without tracker, without magnetic field) and record:
> - initialization time
> - run time per electron
> - type size of the output per event

The current user supplied that snapshot and instructed work only in the isolated
task worktree at `3dab2346c4a08fd24898a7842906601884708a7d`. The host publisher
owns commit, push, draft-PR creation and the numbered PR interaction record;
this agent must return the draft title/body without publishing or posting.
This record does not identify the current client user with the GitHub actor.
No fresh remote discussion or hidden client history was collected. The connected
GitHub GET tool subsequently refreshed PR129 merge metadata only: merged at
2026-11-11T05:53:28Z, head `1fb0630ef4ef4dbc5d0f9dac5032ecedca258252`, merge
`3dab2346c4a08fd24898a7842906601884708a7d`. The selected evidence came from
`GET https://api.github.com/repos/asalzburger/nodd/pulls/129`; unrelated API
account/profile fields were not retained. The existing project entry is reconciled
to that metadata, without changing approval states.

The dedicated branch is `codex/agent-task-131-35766022791`; it started clean.
The input revision itself is the PR129 merge. The repository's earlier pilot
narrative supplies the beam settings omitted from issue131. Its run/audit recipe
was read from the retained local pilot directory and adapted into this PR's
reviewable files; no earlier event samples or counters were copied. All writes,
exports, builds and transport outputs for this task stay in this worktree.

## Decisions and execution

Use the same single-process four groups of 25 electrons as the earlier pilot:
nominal pT 50 GeV, eta 0.5/1.45/2.0/3.0, phi 0.123 rad, vertex at the origin,
matched seeds and native transport steering. Retain only maintained LAYOUT-001
ECAL systems 8/9, including local hardware; omit beam pipe and tracker.
These are benchmark conditions, not new detector choices. The existing
DES-030/DES-031 prototype approval boundaries remain intact. No geometry,
material, segmentation, sensitivity or reconstruction configuration is edited.
The main agent handles this small dependent run and its report; no separate
agent assessment or human physics/engineering approval is claimed.

The acts-spack preflight returned 2 for changed setup/lock fingerprints. Direct
readability checks found all required paths accessible. `software/env/run.sh
python3 -B software/env/doctor.py` then exited 0: DD4hep/DDG4 imports, actual
Spack environment, DD4hep 1.38 `/3yd4hz36kt6sj5eyvpgdlbi2aaux6ghv`,
Geant4 11.4.3 `/wfg55xionuknvzyoc24tu7er2xhapk2z` and all 12 dataset presence
checks succeeded. Sandbox `sysctl`/`ps` warnings did not prevent runtime setup;
no machine configuration, permissions or shared dependencies were changed.

The Release calorimeter factory configure/build passed. Existing upstream
CMake policy/CLHEP warnings were retained. A fresh maintained layout export
is used rather than borrowing an installed compact. The runner refuses to
overwrite an existing run directory and verifies input hashes, absent fields,
ECAL-only exclusions and both real wedge envelopes. It timestamps unbuffered
DDSim output. The readback checks every persisted event and final ROOT sizes.
See [the report and exact reproduction commands](../../docs/validation/issue131/README.md).

## Checks, corrections and limitations

The five existing compact-composition tests and three new benchmark input
controls passed. The first software-inventory refresh rejected a documentation
recipe directory entered as a discovered code family. The correction records
it as evidence/use in the existing calorimeter family, without changing family
discovery or its validator.

The initial project-record validator exited 1 because historical commit
`78bc60bb6da0c9d234baf00d37cadea9dd4964b4` is unavailable in the supplied Git
object store. No history fetch, gate relaxation or shared-checkout mutation was
performed. This limits the full project-record validation claim.

DDSim completed all four 25-event groups and exited 0, with all eight timing
markers and no detected macro errors. Saved-event readback exited 0 for all 100
primaries, event ordering, effective gun momenta and directions, hit collection
system IDs, unique IDs per collection and finite positive hit energies. All
four ROOT `events` TTrees contain 25 events; no event has zero calorimeter hits.
The initialized field audit is zero, and the retained cut/step checks pass.

Measured initialization to the first event was 205.629 s; first beamOn was reached
at 167.460 s. The four event loops total 1664.774 s, or 16.64774 s/electron. Whole
process wall was 1899.076 s (31.65 min), CPU 1890.169 s, child peak RSS 1.881 GiB.
The four closed ROOT/EDM4hep TTree files total 625,810,088 bytes, or 6.25810 MB per
persisted primary for this equal four-direction mix. Compression is ZLIB level 1.
The detailed report retains each direction's rate/size rather than treating the
mix as a universal electron cost. The run is inside the task sandbox; host load
and scheduling were not measured, and no controlled throughput ratio to the
older interactive pilot is claimed.

The compact result is copied only after successful readback. The full samples,
geometry, seeds/state files, build products and complete logs remain ignored
under `build/issue131/`. Independent standard-library checks confirm the saved
summary arithmetic, recipe hashes, source identity and count totals. The project
tracking schema/new task role/deliverable checks pass; these do not replace the
full historical-evidence gate. An interim full-validator call before the audited
summary was copied correctly rejected its missing deliverable; after copying,
the original missing historical commit remains the blocker. The first
supplemental schema import needed the local `tools/project_records` module path;
rerunning with that path passed without changing the validator.

All five existing composition tests and three benchmark-input controls pass.
The inventory refresh/check passes after reviewing its JSON and generated-page
diffs. Final session/interaction/token validation and the token-site build are
recorded in the paired JSON with actual results. No new PR number is invented;
the host must create and synchronize the new PR ledger after publication.

## Interaction and token accounting

The selected issue input, label event, current user's runner boundaries and
assistant outcomes are preserved here with named public provenance. Tools used
are the native command/patch wrapper and the read-only connected GitHub GET; instructed software is the existing
Spack-provided DD4hep/DDG4, Geant4, ROOT, EDM4hep/podio runtime. The
`nodd-review-validation` and `acts-spack` skills guide validation and runtime
verification. Skill instructions were read; no independent role loading is
claimed. Host publication must add the actual draft number/link and synchronize
its individual interaction record. This task does not create an interaction
file for issue131 under a guessed PR number.

The client exposes no exact per-turn input/output/cached/reasoning/total counters
or stable thread/turn identity in this task. The active turn is excluded from
finalized accounting. `usage` remains empty: observed input/output totals for
this session are unknown, not zero. No earlier pilot usage is duplicated. The completion `session_log.py summary`
reports 511 existing observed turns: project-wide input 2,788,479,704 and
output 12,147,127 tokens. These cumulative canonical project observations are
not allocated to this task. There are 93 sessions without usage, including this
one; this task's observed input/output totals remain unknown.

Session validation passed for 280 records; all 111 existing PR interaction ledgers
validate. Token validation and the token-site build succeeded. The ten proposed
files were inspected as text; the largest new evidence file is 13,446 bytes, and
all raw ROOT/log/site outputs are ignored. HEAD remains at the input revision,
with no task commit history or new commit objects to publish. Final staging and
new-object inspection belong to the host's authorized publication step.

## Follow-up

Review the recorded benchmark conditions and output content before generalizing
the rates. One process and one azimuth do not establish concurrency scaling or
shower equivalence. Human design sign-off and detector acceptance remain outside
this task. The host owns the final commit, object inspection, push, draft PR and
numbered interaction synchronization.
