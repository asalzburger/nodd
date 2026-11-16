# PR142-144 stacked merge preparation

2026-11-16. Infrastructure/accounting closeout; original scientific heads preserved.

## Order and merge policy

1. Merge PR142 into main with a merge commit at3fca74b7.
2. Retarget PR143 to main after142 merges (or verify automatic retargeting), let its checks settle, then merge with a merge commit at8dfa8573.
3. Retarget/check PR144 after143 merges, then merge with a merge commit at79a967aa.
4. Merge this separate accounting closeout after144; it carries newly finalized root usage and refreshed visible/public records without changing the three validated source heads.

Keep dependency branches until the stack lands. Avoid squash/rebase merges, which discard the ancestry on which the small incremental PR diffs depend. No merge is executed by this preparation task; source-head equality must be rechecked at execution.

## Observed token accounting

| PR | Unique closed work turns | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| 142 | 8 | 28,010,497 | 149,038 | 28,159,535 |
| 143 | 7 | 61,115,742 | 200,140 | 61,315,882 |
| 144 | 19 | 140,231,445 | 519,112 | 140,750,557 |

Per-PR rows use the canonical accounts listed in the JSON receipt; the34 original-work turn keys are pairwise disjoint. The three newly finalized coordinator turns add114,598,575 observed tokens, and previously owned counters remain untouched. Cached input and reasoning output are subsets, not additional totals. Shared preparation overhead has its own owner and is not allocated to a PR row. Missing/model/provider/active-turn coverage remains explicit. These are request-token observations, not monetary costs.

## Evidence

All six original hosted workflows pass at the exact listed source heads. No inline review threads or submitted reviews were present in the refreshed public snapshots. This is technical preparation, not a fabricated human review/approval.

All three merge-tree rehearsals exit0 and reproduce the exact target-head trees. Main is an ancestor of142,142 of143,143 of144. Repository allows merge commits; branch deletion after merge is disabled; classic main protection is absent and active branch rules return an empty list. Recheck remote state immediately before actual merges.

Thirty-four exact account-matched app-visible turns are refreshed. Allowlist curation excludes reasoning/context, arbitrary tool arguments/results, private paths and raw uploads. Interaction targets that are parents/siblings are not represented as child spawns; actual parent IDs and operation counts remain. The corresponding validation rejection was corrected in curated data, without weakening a ledger check.

Canonical current historical roots are in three dedicated SESSION-2026-11-16-prNNN-token-closeout records; older owner records stay unchanged. Refreshes of142/143/144 ledgers reference these owners. No native simulation, geometry/physics change, engineering signoff or production adoption is implied.

[Machine-readable receipt](preparation-2026-11-16.json) and the paired SESSION-2026-11-16-lar-stack-merge-prep record retain exact hashes, workflow IDs and checks.
