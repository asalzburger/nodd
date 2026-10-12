# SESSION-2026-10-12-pr62-main-sync — PR62 after the token dashboard merge

## Request and inspected revisions

The user asked whether PR62 needs rebasing after PR63 merged. Started from
PR62 head `229e02aaddfe450af695dc221c624d7eaaf529c7` on
`infrastructure/device-accounting-sync-20261012`; the four unrelated untracked
token-gate files remain untouched. PR63 merged into main as
`2534ae86e89a10894ed3e7c47f3a83d451774de6`, including the PR61 calorimeter
ownership correction. GitHub showed PR62 as mergeable with passing old-dashboard
CI, but that did not validate the newly introduced token-site workflow.

Read the changed repository instructions and current token/project validation
guides. An ordinary merge in an isolated checkout was conflict-free but the new
token collector failed against the combined records. The branch therefore needs
a compatibility correction, despite having no textual merge conflict. The
repository requires ordinary merges, so shared history is preserved.

## Failure and correction

The September 25 device inventory retains an explicitly in-progress snapshot
for the recovery task: 45,825 tokens, no closing ordinal and no completion time.
PR62 recovers that same task's final observation, 1,562,843 tokens. The collector
compared the provisional snapshot to the final counters before checking its
boundary, producing a false conflict. The original inventory must remain intact.

Merged main into PR62 and changed the collector to recognize only explicitly
in-progress, unclosed, undated snapshots without an end ordinal as provisional.
Each available provisional counter must be a nonnegative integer no greater than
the corresponding known final counter. These snapshots supply no final counters
or dates. Finalized counter/time conflicts, duplicate ownership and contradictory
closed-boundary claims still fail. Canonical journal observations remain the sole
source of totals. Two new synthetic regression tests cover preserved totals and
dates, missing final dates, unchanged source bytes and oversized provisional
counters; existing strict checks are unchanged.

## Accounting and preservation

The now-completed PR-publication turn contributes 2,607,532 input and 9,208 output
tokens, or 2,616,740 total, to its original owner through a separate closeout
inventory. It contains 19 verified request increases. The current synchronization
turn remains active and uncounted. All earlier inventories and counters are
preserved; PR61's existing ownership correction remains authoritative.

The project now has **209 dated turns and 620,812,827 observed tokens**:
617,282,110 input plus 3,530,717 output. Cached input and reasoning output are
subsets. The pre-existing token-gate task remains pending, older ambiguous turns
remain unassigned, and these are partial project observations, not billing.
Only the collector, its tests/guide and accounting/session records are changed by
this task; main's independent changes are retained through the merge. ADR-004 and
all design/approval states remain unchanged.

## Actual verification

The isolated validator and initial 10-test suite reproduced the incompatibility.
After the correction, all 10 token-site tests, 22 logger tests and 11 recovery
tests passed. Project validation passed for 58 tasks, 31 documents and 19 reviews.
Token validation and the static-site build report all 209 turns dated. Session
validation and summary pass for 167 local records, including the untracked gate
journal; committed-tree record count is one lower. The project-record suite and
preservation checks are recorded in the paired JSON when complete.

Node is absent locally, so the unchanged JavaScript interaction test is left to
the hosted workflow. No dependencies are installed. Final commit/publication and
CI observations are appended when available. No design sign-off or merge of PR62
into main is authorized by this compatibility check.

## Final local checks

All **71 Python tests** passed: 10 token-site, 22 logger, 11 recovery and 28
project-record tests. The preservation audit verifies all 183 observations and
owners from main, all 208 earlier PR observations, every prior JSON inventory,
the scientific registers and the four unrelated local files. Session validation,
summary, token-site validation/build and whitespace checks passed after the
closed publication-turn import. The compatibility update uses a normal merge
commit and an ordinary push; both published histories are retained.
