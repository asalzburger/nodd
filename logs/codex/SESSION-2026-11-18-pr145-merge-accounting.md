# SESSION-2026-11-18-pr145-merge-accounting

## Scope and evidence

Prepare existing ready [PR145](https://github.com/asalzburger/nodd/pull/145)
for merging and complete available exact accounting. Start at
`d8fd70a7ffe08b5df913a17c3fe950b1a835e428` in a clean isolated worktree,
branch `codex/pr145-merge-accounting`; publish ordinary commits to its existing
`codex/emcal-findings-report` head. No history rewrite or merge of the PR.
Current main `ea311d72e722e00958a8cb76752895eae35a6fc6` includes merged PR147.
DES-030/031/032/033 and TASK-EMCAL-FINDINGS provide the existing source context.

## Selected conversation

User, exact: “can you make #145 mergable and make sure it's tokens are accounted for ?”

Assistant outcome, paraphrase: resolve current-main record conflicts, retain
the ready state, preserve the reviewed report and scientific sources, recover
only exact finalized task counters, and verify current-head CI before handoff.

## Decisions and outcomes

Ordinarily merge current main into the PR branch. Resolve project and software
inventory conflicts semantically: retain all tasks/PRs and both capability,
recipe, evidence and related-PR lists. Regenerate the inventory page and check
it. Update the public observation that PR147 merged into main, without claiming
engineering acceptance. Report, PDF, plots and editable sources remain frozen:
all 16 files under `docs/publication/emcal-findings/` are byte-identical to the
starting head. Their pinned source revisions and original scientific reviews
remain authoritative. No new geometry, transport, calibration, PDF or plotting.

The work is small and dependent, so the coordinator applies local
`nodd-coordinate` and `nodd-review-validation` without a new specialist
assignment. This is not a new independent scientific assessment. Keep PR145
ready under the user's explicit request; preserve its existing calorimeter and
baseline-scope labels. No design sign-off or PR merge is implied.

## Commands and validation

`git merge --no-commit --no-ff origin/main` initially reports conflicts in
`project/tracking.json`, `software/inventory.json` and the generated inventory
page. Reconcile the JSON by stable identity/additive content and regenerate the
page. No whole-side replacement of project or source records.

The unmodified usage-only recovery tool succeeds for explicitly selected thread
`01a1d197-9480-7751-af8c-0c21b576f5ac`: cumulative increases equal last-request
counters, 14 repeated snapshots are ignored and no usage lies outside recorded
turns. Audit the five selected task turns against app-visible requests,
continuations/outcomes and exact ID/status/start/end metadata. All other turns
are excluded. Oversized app reads are retried one turn at a time. Only
allowlisted user/assistant text and child-start metadata are retained, with
paths/URLs redacted; no reasoning, raw arguments/results or private archives.

Import dry runs and actual imports pass for each of the three original owners.
All18 existing `software/analysis/lar_response` tests pass. Verify the 10-file
historical report guard, 16 current report hashes, PDF/builder, historical input,
data/producer and 3 SVG receipts. Inventory refresh/check passes with 69
components, 104 code families, 55 reviewed inputs and 12 pins. Final session,
project, ledger-retention, token preview and whitespace checks are recorded in
the paired JSON after execution. Final hosted checks are checked at the pushed
head before handoff; local checks alone are not a hosted-CI claim.

## Changes and revision links

Current-main integration retains PR147's files. Focused follow-up files are the
project/inventory reconciliation, this paired record, three original journals,
five visible-turn snapshots, the usage receipt and PR145 interaction ledger.
The paired JSON inventories actual changed files. The enclosing commit records
the final merge revision; do not invent a self-referential result SHA.

## Token accounting

`logs/usage/USAGE-2026-11-18-pr145-parent-closure.json` records five newly
finalized coordinator turns, totaling 56,481,153 input + 216,138 output =
56,697,291 observed tokens. Their original canonical owners remain the only
owners. Nine existing specialist turns and all earlier receipts are unchanged.

| Canonical task | Distinct observed turns | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| Original report | 6 | 33,061,938 | 92,055 | 33,153,993 |
| Review response | 5 | 43,513,181 | 120,976 | 43,634,157 |
| Standalone SVGs and PNG preview | 3 | 10,359,262 | 65,597 | 10,424,859 |
| Direct PR145 work | 14 | 86,934,381 | 278,628 | 87,213,009 |

Cached input and reasoning output are subsets, not extra tokens. Model,
provider and client version remain unknown. Earlier simulation/dependency PRs
retain their own canonical accounts; none are copied into these direct-work
totals. The PR ledger and token-page generator reference those owners so the
merged history retains one global observation per thread/turn.

This separate preparation record owns no historical counters. Its current turn
`01a1ef54-f0e5-79b1-8b12-ac231f763bd4` is active and cannot yet have a finalized
counter total. Empty usage means unavailable, never zero or estimated. A later
closed-turn pass can add that exact observation once available.

## Follow-up

Merge PR145 only after final current-head hosted checks pass. Connected-service,
collar/FCAL and integrated geometry qualification remain outside this historical
report and accounting task. No human engineering approval is recorded here.

Artifact inspection initially attempted to treat a submodule gitlink as a local blob. Corrected the read-only audit to inspect blob objects, preserving all submodule pins and checks. Changed staged files contain no new raw event/archive payload; the existing PR147 image is already on main.
