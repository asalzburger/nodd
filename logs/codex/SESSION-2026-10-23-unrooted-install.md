# SESSION-2026-10-23-unrooted-install — Install unrooted for documentation plots

## Scope and evidence

Contemporaneous, bounded software installation for
[issue #95](https://github.com/asalzburger/nodd/issues/95). Started from
`a35d57cc91bbc4e96756d3f37a37fe7ce2d35022` on the clean isolated worktree branch
`codex/issue95-unrooted`. Other nODD worktrees and the separately modified local
unrooted development checkout were preserved. Read repository instructions,
PROJECT.md, ADR-003, ADR-008, the software layout, logging and tracking workflows,
and the issue. This small dependent task stayed with the main agent; no separate
agent assessment is claimed.

## Selected conversation

- User request, exact: “There’s a software issue #95 - should do …”
- Issue request, exact: “This is an assignment for the `SoftEng` - install unrooted, in order to make plots for the further documentation.”
- Assistant outcome: installed and source-pinned unrooted, including Plotly, in a
  separate local Python environment; verified ROOT input and static/HTML output.

## Decisions and outcomes

Installed upstream `728465dce0c5cd5b876e67392e3858de6e982d05` (`0.1.0rc1`),
the public main revision observed at intake, rather than the locally modified
development checkout. Inspected its README, pyproject, source interfaces,
packaging smoke example and MIT license. The installation is under ignored
`software/build/unrooted-venv`, using CPython 3.11.15 on macOS arm64. The ACTS/Spack
environment is independent and was not needed for this ROOT-independent tool.

The requirement input pins the full Git revision; the universal generated file
pins transitive dependencies, including Python-version markers. Optional Plotly
provides self-contained HTML. Matplotlib provides PNG/PDF/SVG. The repeatable
smoke check uses arbitrary, deterministic fixture counts with no random seed or
physical detector interpretation. It verifies the installed Git origin, loaded
edges/counts/variances, bundled ODD styling, ratio overlay and CLI. Generated PNG
was visually inspected and has clear labels and a complete ratio panel.

Added a dedicated hosted Linux/Python 3.11 smoke job. Local results do not qualify
other Python versions or platforms. Added TASK-SOFT-UNROOTED and SRC-UNROOTED;
detector parameters and design approval states are unchanged.

## Commands and validation

- `git fetch origin main` and isolated `git worktree add`: successful.
- Initial sandboxed `git ls-remote` failed DNS resolution; the approved network
  retry succeeded. The default uv cache was sandbox-blocked; the approved retry
  used an explicit ignored project cache. Initial fontconfig cache warnings were
  resolved by directing `XDG_CACHE_HOME` into the smoke output directory.
- `uv pip compile --universal --python-version 3.11 ...`: succeeded with source
  revision and dependency pins retained in the requirements file.
- `uv pip sync --python software/build/unrooted-venv/bin/python ...`: installed
  24 packages. `uv pip check` passed for all 24.
- `software/build/unrooted-venv/bin/python -I software/analysis/unrooted_smoke.py`:
  passed; exact numerical ROOT round-trip, PNG/PDF/SVG, HTML and CLI checks.
  The retained [report](../../docs/validation/unrooted-installation.json) identifies
  package versions, script/requirements hashes and generated artifact hashes.
- `python3 -B software/env/check_layout.py`: passed.
- First project validation found an unknown task-document reference because
  ADR-008 was not registered. Removed that reference from the new task's governed
  document list; the existing software-layout context remains available.
- The initial project-record suite ran 28 tests with five failures and seven
  errors: its synthetic repository omitted software deliverables. Extended the
  fixture to copy software sources while excluding build environments and
  third-party submodules, retaining all strict evidence checks. All 28 tests
  passed on the final run (114.774 seconds).
- Final record, session, token-preview and whitespace checks are recorded in
  the paired JSON with their observed results. Hosted checks remain separate.

## Changes and revision links

The paired JSON lists all changed files. The installation instructions, source
and dependency pins, smoke program, compact validation report, CI job, source
catalogue, project task and this session pair form the reviewable deliverable.
Binary fixtures, generated plots, package caches and environment stay ignored.
Result commits are recorded only once they exist; ordinary Git history locates
the enclosing record revision.

## Token accounting

No exact client-reported per-turn counters are available for this active turn.
`usage` remains empty. Input/output observations for this task are unknown,
not zero, and no estimate or cumulative thread total is entered.
`session_log.py summary` is run at closeout to report available project coverage.
The observed project summary has 195 sessions, 124 with usage and 71 without;
233 recorded turns sum to 729,700,848 input and 4,129,685 output tokens. These
observations do not measure the current task and are not a complete project total.

## Follow-up

Review the proposed setup and hosted Linux check, then use the documented
environment for future figures. This installation check does not validate
detector performance or supply human design sign-off. Future upstream updates
require deliberate regeneration of dependency pins and another smoke run.
