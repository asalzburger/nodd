# SESSION-2026-09-22-pr-naming — PR prefixes and conflict reconciliation

## Scope and selected request

User requested these PR title forms: Magnet System, Tracker, Calorimeter,
Muon System, Global, Software and Infrastructure, each followed by a colon and
description. They asked to record the workflow rule, apply it to open PRs and
resolve conflicts, accepting both logging contributions by default.

The rule supersedes the old chore title convention by explicit human instruction.
Infrastructure remains excluded from project progress; new software capabilities
still require tracking. No design/ADR sign-off or production change is implied.
Initial unrelated tracker bytecode is preserved. Exact tokens and client details
are unavailable; this record contains no usage observations.

## Changes and outcomes

AGENTS.md now contains the canonical prefix/scope table and conflict-preservation
rule. The project guide and PR template link to it. CI requires exact prefixes
and nonempty descriptions, handles title edits, and retains the existing guard
against hiding scientific work as maintenance. Historical chore classification
remains available to the dashboard; closed PRs and historical titles are unchanged.

| PR | New title |
| --- | --- |
| #6 | Magnet System: Evaluate magnetic layouts with candidate-specific muon envelopes |
| #8 | Tracker: Propose reusable RD53i modules with component material accounts |
| #13 | Tracker: Study tracker layouts and inclined modules with independent controls |
| #14 | Software: Assess pyacts Gen-3 module geometry and propagation bindings |

Only #8 conflicted with current main. An isolated checkout merged main using
an ordinary merge, retaining independent entries by stable ID/path in tracking
and review JSON, both documentation-index additions and all session logs. No
ambiguous scientific or approval decision was needed. The exact pixel design
and ADR content, all review targets and all original review rounds were retained.
Merge 84f23f3f58cd289b90b9ac759efdc0e51dceb97b was pushed to the existing draft
PR. Its separate SESSION-2026-09-22-pixel-branch-reconciliation record is on that
branch. No main merge, force push or resumed tracker-layout study occurred.

## Validation

The paired JSON records actual checks. PR #8 passed 25 dashboard tests, 15
logging tests, dashboard validation/build and a preservation audit. Its initial
merge diff exposed existing whitespace in main's README/REVIEW files; these
unrelated files were preserved, and the final PR diff against main is clean.
The naming workflow has focused prefix/CI tests, full dashboard/log checks and
a successful dashboard build. Missing future CI and human decisions remain
unknown, not approvals.

## Publication

Published [PR #15](https://github.com/asalzburger/nodd/pull/15),
Infrastructure: Standardize PR naming and conflict preservation, with review
requested from asalzburger-review. Rule/test revision is
ddfd9826607efb5e98c8c48465e6a23a43c59853; the following commit only completes
this session record. It has no scientific progress entry. Existing PR renames and conflict resolution are
already applied; their immutable historical review evidence is unchanged.

All five open PRs were verified mergeable. The naming change passed 26 dashboard
tests, 15 logging/document-link tests, 14 JavaScript assertions, log validation,
the real-diff PR policy check and dashboard build. GitHub CI was in progress at
collection; no human review or approval is inferred.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **2,718,177 input** and **13,942 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
