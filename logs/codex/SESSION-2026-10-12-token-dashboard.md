# SESSION-2026-10-12-token-dashboard — Cumulative token usage Pages

## Scope and selected requests

The user requested retirement of the unused project-progress dashboard and its
deployment, replacing GitHub Pages with cumulative token usage over time and
major features on the time axis. The user then asked about the October 6 cutoff
after switching to the ChatGPT app and Codex workspace.

Work is isolated on `codex/token-usage-dashboard`, stacked on repaired PR59.
The primary checkout and unrelated publication output are preserved.

## Outcome

The old UI, renderer and deployment workflow are removed. Canonical scientific
tracking/review JSON and semantic guards remain under `tools/project_records`.
The independent validation workflow retains all 17 previous scientific/software
unit-test commands, PR naming/tracking checks and session/preflight checks.
Historical dashboard documentation links remain valid via a retirement guide.

A standard-library builder creates a static cumulative usage site with combined,
input and output modes, seven linked merged-feature markers, accessible keyboard
point labels, exact daily table and aggregate JSON download. Parent/subset token
counters, unknown coverage, unmeasured carry-forward and source revision are
explicit. No chart package, installation, raw private content or live telemetry
is introduced. GitHub Actions publishes Pages artifacts from main only; PRs
build previews and generated site content is never pushed to a Git branch.

The app migration did not lose counters. Directory selection and stale recovery
inventories caused collection gaps. PR59 now carries the separate desktop
backfill and explicit-thread recovery fix, adding 15 closed turns through
October 10. The dashboard observes 552937331 tokens across 183 disjoint turns,
with cached input/reasoning as subsets. Earlier no-counting tasks remain excluded;
this active October 12 turn can only be collected after it closes.

## Validation and corrections

Eight usage tests, JavaScript mode/keyboard checks, 28 retained record-policy
checks and 33 logger/recovery/link checks pass. Project validation reports
58 tasks, 31 documents and 19 review rounds. The logger validates 152 pairs;
99 have usage. The built timeline reconciles all five fields with canonical
observations. Desktop preview totals and feature labels were visually inspected.
No separate mobile viewport check or deployed Pages result is claimed.

Initial fixture tests failed because their copied logger lacked TEMPLATE.md;
the fixture was corrected. Initial timeline validation required completed status;
that incorrectly excluded closed interrupted turns. It now requires a closed
accounting boundary and tests that case. The first sandbox preview bind failed;
the authorized local server then ran successfully. These corrections do not
weaken the scientific validation gates.

## Follow-up

Merge PR59 before this stacked infrastructure PR, then target the follow-up at
main. Pages publication occurs after merge. Capture the previous closed desktop
turn during a later task with explicit project attribution; the dashboard only
builds checked-in observations. Scientific design/review approvals are unchanged.

A staging attempt named the removed dashboard directory and failed. The first
commit consequently contains staged removals only. The replacement files are
added in a second ordinary commit before the PR; no shared history is rewritten.
