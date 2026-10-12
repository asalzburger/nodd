# PR #59 integration and token-accounting repair

## Request and scope

On 2026-10-12 the user requested conflict resolution for #59, a correct project
token count, and a separate replacement token dashboard PR.

## Findings and changes

GitHub already reported #59 mergeable and latest main was an ancestor of its
head. The outstanding CI failure was a link to an intentionally uninitialized
TDR submodule. The source path is now text, with a link to the retained publication
inventory. No TDR source, published PDF, geometry or scientific approval changed.

An existing prepared accounting branch held records not incorporated into main.
Its 94 shared observations match the PR journal exactly; 74 additional disjoint
observations add 191,567,410 tokens. An ordinary merge preserves both histories
and independent session records, producing an observed subtotal of 458,373,478:
455,721,428 input plus 2,652,050 output. Cached input and reasoning output remain
subsets. Existing exclusions, missing telemetry and canonical owners are retained.
The versioned audit records source commit and arithmetic; no private store or raw
client conversation was read for this task.

## Validation

Session validator: 150 records. Session/recovery/documentation tests: 32 passed.
Project validator: 58 tasks, 31 documents, 19 review rounds. Existing static site
build passed. Original dirty checkout and untracked output artifacts are preserved.

## Remaining coverage

This task's counters are unavailable and its usage is empty. The subtotal is
observed historical usage, not complete telemetry or billing. The separate
infrastructure PR will replace the dashboard and its deployment with the token
timeline while preserving scientific records and independent validation checks.

## Desktop backfill correction — 2026-10-12

The user asked about the post-migration cutoff. Explicit desktop-thread recovery
adds fifteen closed nODD turns through October 10 and verifies existing owners
unchanged. The new observed subtotal is 552,937,331 tokens across 183 turns.
See [backfill](SESSION-2026-10-12-desktop-usage-backfill.md) for task attribution
and exclusions; earlier merge-audit arithmetic remains a historical snapshot.
