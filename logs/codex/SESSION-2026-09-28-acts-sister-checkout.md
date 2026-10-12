# SESSION-2026-09-28-acts-sister-checkout — Record authorized ACTS sister checkout and local workflow

## Scope and evidence

Contemporaneous infrastructure record, 2026-09-28. Starting nODD revision:
`0d90d75d6f998f732adaad2f0a49787b5cbc46fa`, branch `main`, clean working tree.
Related workflow: ADR-004; no design, issue or approval state changes.

## Selected conversation

User request (paraphrase): record the sister repository at
`/Users/salzburg/Documents/work/dev/acts-nodd`, authorize its access for nODD,
and consult its build, test and runtime instructions. The user describes it
as a corrected ACTS main checkout. This explicitly supplied local path is
retained to make the requested environment discoverable in later sessions.

## Decisions and outcomes

Added the location, authorization and workflow to nODD's AGENTS.md. Read the
sister checkout's AGENTS.md and the local setup helper without executing it.
No ancestor AGENTS.md files were found for that checkout.

Observed ACTS HEAD: `355ea68493b326956756c9386d2fd9eaf9328568`, branch
`fix-clang21-on-macOs27-boost-nodiscard`. Local main and origin/main both point
to `20f2e679d2fe8d500e1a810f0f138f395d4f6b9a`; the correction changes
`Tests/UnitTests/Core/Geometry/PortalTests.cpp`. No fetch or upstream freshness
claim. Existing changes were preserved: modified `.gitignore` and untracked
`Detray/codegen/detray-sympy/requirements.txt` and
`Traccc/extras/benchmark/requirements.txt`.

The documented commands are `acts build acts-nodd`, `acts test acts-nodd`,
and `acts run acts-nodd` after sourcing the setup helper. Python jobs require
the installed acts-nodd virtual environment; pytest runs at the ACTS source
root. Its virtual-environment directory exists, but imports were not tested.
Build recreates that environment; runtime setup also copies ODD data/config
into the installation. Future dependent work requires the ACTS Spack skill
and node preflight, and actual filesystem permissions. No new node capability
was registered. No sister-repository files were written.

This is infrastructure documentation, excluded from scientific progress
tracking. No detector parameter, source-catalogue entry, design sign-off or
production dependency pin was introduced. No commit or PR was requested.

## Commands and validation

Read-only inspection used `git status --short --branch`, `git rev-parse HEAD`,
`git log`, `git diff --stat main...HEAD`, `rg`, and reads of the checkout
instructions and setup helper. A guessed older session filename did not exist;
that read exited 1 and was replaced with `rg --files logs/codex` and the current
session template. This had no effect on files or verification results.

Created this pair with `session_log.py new`. Final validation commands/results
are recorded in the paired JSON. Session validation passed (48 records),
dashboard validation passed (29 tasks, 9 documents, 10 review rounds), the
dashboard build succeeded in a temporary output directory, all 27 dashboard
tests passed, and `git diff --check` passed. No ACTS build, tests,
Spack setup or detector runtime checks were run for this documentation task.

## Changes and revision links

Changed AGENTS.md and this session's Markdown/JSON pair. Result commits remain
empty. The starting nODD tree was clean; existing ACTS local changes remain
untouched.

## Token accounting

Exact client-reported per-turn token counters are unavailable; usage is empty.
No private client state was inspected. This task's observed input/output totals
are unknown, not zero; repository-wide historical totals do not measure it.
The executed summary reports 134,594,309 observed input and 674,111 output tokens
across 79 recorded turns in 42 of 48 sessions; six sessions lack observations.

## Follow-up

Recheck ACTS HEAD, working tree and instructions before using it. Verify the
node and required build/runtime capabilities when an execution task needs them.
No human design review or sign-off is requested by this record.
