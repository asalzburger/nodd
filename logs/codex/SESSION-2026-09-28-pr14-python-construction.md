# SESSION-2026-09-28-pr14-python-construction — Address expert review with Python-native ACTS module construction

## Scope and evidence

Contemporaneous software task, DES-005 / TRK-SE03 and ADR-003. PR #14 started at
`45f1a8b62dbb6e90069a875122e9721f3013ec03` on `study/pyacts-gen3-bindings`.
An isolated worktree preserves the original nODD main checkout's uncommitted
sister-checkout instructions/session pair. No detector design is implemented.

## Selected conversation

User requests (paraphrased): address the expert comment on PR #14; if the ACTS
wheel is insufficient, check the authorized acts-nodd local installation; add
missing functionality in a draft PR. Subsequently, explicitly post a PR reply
explaining the solution. The user undertook installing matplotlib/dependencies.

The expert comment questions the vector JSON route and recommends considering
Python-level module construction. The purpose is feasibility for later geometry
coverage studies, not approval of a detector specification language.

## Decisions and outcomes

Replaced the recommended JSON adapter with Python-generated module placements
and Python blueprint topology. Python construction makes finite planes and calls
assignIsSensitive, with no module JSON I/O. Explicit JSON remains a compatibility
and comparison control, including its version-specific kind/type encoding.
Structural topology edits remain explicit Python builder changes.

Both the installed wheel and source checkout lacked the sensitivity setter.
The source checkout already fixes the historical Transform3 constructor issue.
Added the existing C++ Surface::assignIsSensitive binding, with three surface
cases and a Gen-3 layer integration test. No C++ geometry behavior was changed.

ACTS draft: https://github.com/acts-project/acts/pull/6176
Patch revision: `95ece2188858a05dcb04efb4f09c75dfa26e7257`.
Its isolated branch starts at main `20f2e679d2fe8d500e1a810f0f138f395d4f6b9a`.
The runtime build uses corrected checkout `355ea68493b326956756c9386d2fd9eaf9328568`
with an identical uncommitted three-file patch mirror. The compiler correction
remains separate in ACTS PR #6174. The original acts-nodd branch, modified
.gitignore and two untracked requirements files were preserved. The pre-commit
codegen hook also generates those ignored/untracked requirements in the isolated
worktree; they are not part of the draft. Local ignored _work_diffs reporting is
maintained for the ACTS task.

The acts-spack skill reported changed setup/lockfile fingerprints. Task-required
activation, imports and incremental compilation succeeded with DD4hep 1.38 /
Geant4 11.4.2, but Geant4 setup warns about a missing data directory. No node
registry promotion or full-simulation claim. The installed binding was rebuilt
without running the full helper that recreates the Python virtual environment.

The new native/JSON comparison retains 1600 ray checks and 192 propagations,
including an alternating-z fixture. Counts reuse seeded samples, not independent
statistical draws. Original September 21 reports/figure remain unchanged.
Provenance added: SRC-ACTS-PYTHON-SENSITIVITY. Updated task tracking; no design,
review approval or sign-off status advanced.

## Commands and validation

See the paired JSON for exact check scopes, failures, corrections and results.
Four added tests fail before the binding and 20 focused tests pass afterwards.
All ACTS pre-commit hooks pass outside the sandbox. Full Python Core collection
initially failed on missing matplotlib; after user installation, 56 passed and
1 skipped. Wheel controls pass. Runner hashes match retained evidence.

Initial native attempts corrected an unsupported RectangleBounds overload and
the current JSON control's type key. No dimensions or tolerances were relaxed.
The initial dashboard test run found a prohibited Python-file evidence link;
the tracking entry was corrected to use the curated guide/report instead.

Git metadata writes and the initial runtime installation required normal
filesystem escalation. GitHub commands encountering sandbox network errors were
retried with authorized external execution. No force-push or history rewrite.

## Changes and revision links

nODD changed-file inventory is in the paired JSON. External ACTS files:
Python/Core/src/Surfaces.cpp, Python/Core/tests/test_surfaces.py and
Python/Core/tests/test_blueprint.py. Only these three files enter ACTS #6176.
Final nODD revision, posted reply and checks are appended after publication.

## Token accounting

Exact client-reported per-turn counters and stable thread/turn IDs are unavailable.
Usage is empty; this task's observed input/output are unknown, not zero. No raw
client state was accessed and no historical observation was duplicated.

## Follow-up

Await human review of the Python-first response and upstream draft binding.
Physical module masks/stereo, material, realistic fields, beamspot coverage,
response and reconstruction remain future work. No design sign-off requested.
