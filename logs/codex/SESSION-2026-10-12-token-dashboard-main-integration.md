# SESSION-2026-10-12-token-dashboard-main-integration — Integrate PR60 into main

## Scope and selected request

The user asked whether PR60 was contained in PR61, and requested preparation of
its integration into main if missing. A clean isolated branch starts from
`5d3cda65a4512fa88220f41f60d17d1f5ce56911`, the PR61 merge on main.
No unrelated changes were present. Work is infrastructure only.

## Git evidence and outcome

PR60 head `af5c824417a0fa7e857430f01b50d21e91188c16` and its recorded merge
`b2dc9e1504cb982a34d792225c4b00db472c4cd7` were both absent from main ancestry;
PR61 merge was present. PR60 targeted `codex/overleaf-online-sync`, after PR59
had already merged into main, so that merge did not deliver the dashboard to main.

The PR60 merge commit is integrated through an ordinary non-fast-forward merge
on `codex/token-dashboard-main`, preserving the original reviewed history and
current main. The merge is conflict-free. PR60 dashboard tools, milestone data
and workflows are identical to their reviewed versions. The former progress UI
and deployment are removed; main-only token Pages publication and the separate
scientific-record validation workflow are restored as requested by PR60.

All 328 existing main journal/evidence files are byte-identical after integration,
including PR61's dedicated eight-turn calorimeter owner and dated correction.
Tracking/review registers are unchanged. All 17 existing scientific/software
unit-test commands remain in validation.yml. No detector source, design status,
scientific approval or token observation is changed.

## Commands and validation

GitHub PR metadata, exact Git fetch and ancestry checks establish the missing
integration. The recorded PR60 merge is merged without rewriting shared history.
Logger/recovery tests, token-site arithmetic/interaction checks and retained
record-policy tests are run against the integrated snapshot. Validation, output
build, byte-preservation checks and final results are recorded in paired JSON.
Generated previews stay under ignored _site and are never committed.

## Token accounting

The observed project subtotal remains 552,937,331 tokens across 183 unique turns:
549,665,612 input and 3,271,719 output. Cached input 530,854,016 and reasoning
output 1,133,026 are subsets. The curve still has 183 dated observations.
This active integration turn has no final boundary, so no provisional count is
imported. Existing missing coverage and counting exclusions are preserved.

## Follow-up

Review and merge the integration PR directly into main. Its main push will use
the restored token-usage Pages workflow; PR runs only build preview artifacts.
Deployment has not occurred merely because the integration branch exists.

Local closeout: 28 retained record tests, 33 logger/recovery/link tests, eight
usage tests and JavaScript mode/keyboard checks passed. The logger validates
155 paired records; project records and token build pass. All existing journal
bytes and token owners are preserved. Whitespace checks pass.
