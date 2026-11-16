# PR142–144 stacked merge preparation

2026-11-16. Infrastructure and accounting closeout; original scientific heads preserved.

## Merge order

1. Merge [#142](https://github.com/asalzburger/nodd/pull/142) into main with a merge commit at `3fca74b7`.
2. After #142 lands, retarget [#143](https://github.com/asalzburger/nodd/pull/143) to main (or verify automatic retargeting), recheck its current head and checks, then merge with a merge commit at `8dfa8573`.
3. After #143 lands, retarget and check [#144](https://github.com/asalzburger/nodd/pull/144), then merge with a merge commit at `79a967aa`.
4. Retarget and merge the separate accounting draft [#146](https://github.com/asalzburger/nodd/pull/146) after #144. It carries newly finalized root usage and refreshed interaction evidence without rewriting the validated scientific heads.

Keep dependency branches until the stack lands. Squash and rebase merges discard the ancestry supporting the incremental PR diffs. This task marked #142–144 ready for review; it executed no merges. Recheck remote state at execution.

## Observed token accounting

| PR | Unique closed work turns | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| 142 | 8 | 28,010,497 | 149,038 | 28,159,535 |
| 143 | 7 | 61,115,742 | 200,140 | 61,315,882 |
| 144 | 19 | 140,231,445 | 519,112 | 140,750,557 |

These 34 original-work turn keys are pairwise disjoint. Three newly finalized coordinator turns add **114,598,575** observed tokens; dedicated follow-up sessions own them and prior owners/counters remain unchanged. Canonical accounts are listed in the [JSON receipt](preparation-2026-11-16.json). Cached input and reasoning output are subsets, not additional totals. Counts describe observed request tokens, not monetary costs or complete history; model/provider and interrupted/unobserved coverage remain explicit.

Shared preparation overhead has its own owner, `SESSION-2026-11-16-lar-stack-merge-prep`. It currently holds one completed independent review turn: **4,113,186** observed tokens. Active coordinator counters remain unavailable. This partial overhead is excluded from the three rows above; PR references to shared accounts must never be summed as distinct usage.

## Evidence and limitations

All six original hosted workflows pass at the exact listed source heads. No review threads or submitted reviews were present in the refreshed public snapshots. All three merge-tree rehearsals exit successfully and reproduce the exact target-head trees; main is an ancestor of #142, #142 of #143, and #143 of #144. Repository settings allow merge commits and retain branches after merging. Classic main protection is absent and active branch rules returned an empty list.

Independent SoftEng assessment at `0f893f85e17303a6a35d57e2768540e8ac946b85` closed with no actionable findings. It verified accounting ownership/totals, exact-target ledger validation, source privacy and parent metadata, live heads/CI and merge-tree identities. This is technical preparation, with no human approval or new scientific validation implied.

Thirty-four exact account-matched app-visible original-work turns are refreshed. Allowlist curation excludes reasoning/context, arbitrary tool arguments/results, private paths and raw uploads. Parent/sibling interaction targets are not represented as child spawns; actual parent IDs and operation counts remain. An initial validation rejection was corrected in curated data without changing a validator or guard. A separate allowlisted snapshot records the new review turn for #146.

The three dedicated `SESSION-2026-11-16-prNNN-token-closeout` records own only the newly finalized historical coordinator turns. Older records remain unchanged. No simulation, geometry, physics or runtime source changed. The standalone routing prototype still requires integrated fit and canonical-cell boundary follow-up; merge readiness does not establish production or engineering acceptance.

The JSON receipt and paired preparation session retain exact hashes, workflow IDs, review identity and checks. The unrelated PDF/report task is outside this accounting scope.
