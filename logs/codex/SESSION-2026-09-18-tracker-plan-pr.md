# SESSION-2026-09-18-tracker-plan-pr — Publish the tracker plan for human review and sign-off

## Scope and evidence

Contemporaneous publication record for DES-005 on 2026-09-18. Starting revision:
`9bc03865fa384dd4b19448b81bd9f86b29feb9f0`, branch `design/tracker-system-plan`.
The initial working tree contains the preceding task's plan, four role inputs,
documentation/tracking/provenance changes and paired session record. These are
the requested PR scope; no unrelated user changes were identified.

Exact token usage, client version, thread ID and actual conversation start time
are unavailable. Prior usage observations are not copied.

## Selected conversation

- User request (exact quote): “Make a PR with the plan for review and sign-off.”
- Assistant action: prepare DES-005 for human review, publish the branch and
  request review from the previously assigned final human sign-off authority.

## Decisions and outcomes

The requested decision concerns the staged programme, responsibilities,
dependencies and evidence gates. Numerical acceptance criteria, selected layers,
component choices, production implementation and physics acceptance retain their
later review requirements. DES-005 remains DRAFT with a pending review request; no approval outcome
or sign-off is recorded. Other human expertise/ownership assignments remain open.

The review register pins the plan commit and leaves the outcome pending. PR
metadata is a dated snapshot; metadata-only follow-up commits preserve the exact
plan bytes targeted by review. This is a project PR with tracking/review updates.

## Commands and validation

Inspected instructions, working tree, review schema, PR template and open PRs;
refreshed origin and confirmed no newer main commits. Reviewed the prior task's
successful 40 tests and validation evidence. New checks and publication results
are retained in the paired JSON only after execution. No detector studies are
executed as part of publication.

The first publication dashboard-suite run passed 24 tests and failed the
initialization test because changing the document lifecycle to TECHNICAL REVIEW
violated its expectation that current proposals remain DRAFT. Kept DES-005 at
DRAFT with the pending request represented in the review register; no tests or
gates were changed. The request will target the corrected document revision.

The corrected full run passed all 25 dashboard tests; all 15 logging/documentation
tests passed. Dashboard validation/build, session validation and exact-target
checks passed. The final plan review target is
`7d99d8c92815c7cf28736abfe08d37d2fd04b558`.

## Changes and revision links

The PR contains DES-005 and its four role inputs, documentation links, source
metadata, the tracker task register, the review request and both session pairs.
See the paired JSON for exact paths and commits once created.

## Follow-up

Opened [PR #11](https://github.com/asalzburger/nodd/pull/11), titled
“Plan whole-tracker design and staged performance studies”, and verified the
GitHub review request to the assigned final sign-off authority. The project PR
snapshot records head `db4ab22aab9041783c2889b731a9d79607234f43` when collected;
the subsequent publication-metadata commit preserves the reviewed plan bytes.

Await human review and explicit plan sign-off at the recorded revision. Merge,
approval and production implementation are not performed by this task. Hosted
CI was in progress when this publication record was closed; the final revision's
result is reported separately to the user after it completes.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **4,163,115 input** and **11,156 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
