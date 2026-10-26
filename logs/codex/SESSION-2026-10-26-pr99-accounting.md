# SESSION-2026-10-26-pr99-accounting — PR99 usage and discussion correction

## Scope and evidence

User-requested accounting and public/visible discussion refresh for PR99 while
its creation turn is still active. Exact parent and verified PhysVal child only;
no neighbouring conversations or private contents. Usage-only recovery reads
metadata and token_count events, never conversation items. Visible discussions
come from exact app thread/turn matches, reduced through an allowlist in memory.

## Selected conversation

User input, exact: “Update the token usage of this PR, make sure the discussions
are recorded and go on.”

Assistant outcome: recovered three completed turns and kept their counters in
SESSION-2026-10-26-geantino-material-stacks, the sole canonical owner. Refreshed
PR99 public discussion, retained completed visible messages and current active
visible prompts/responses, named the parent and PhysVal child, and preserved
models/client versions as unknown. The current parent turn remains active.

## Decisions and outcomes

7314037 input +42419 output =7356456 completed observed tokens,67 requests/3 turns.
7013504 cached input and14272 reasoning output are subsets. No estimates and no
active-turn counters added. The parent stream reconciles independently of the
child's two request streams. Both exact turn boundaries and spawn metadata match.
Three additions imported once; idempotent replay finds0 additions/3 unchanged.

A completed child can outlive its still-active parent turn. The visible-message
format now optionally carries verified parent_thread_id, preventing assignment
prompts from being mislabeled as human input and avoiding a fabricated active
usage entry. Regression covers this precise case and rejects self-parent links.
The active parent's visible messages are separate curated discussion events,
without a finalized usage snapshot. This is a bounded recording correction,
not a change to detector analysis or scientific-progress accounting.

## Commands and validation

- recover_usage.py with exact parent and child IDs: one completed parent turn,
  one active parent turn, two completed child turns; repeated snapshots4+1,
  no outside-turn events. Full cumulative increases reconcile to last requests.
- session_log.py import-usage: dry-run3 added; import3; replay0 added/3 unchanged.
- Native visible-message allowlist excludes reasoning, commands/results, images,
  credentials and private path/URL contents; selected retained text reviewed.
- Interaction tests:15 passed, including completed-child/active-parent attribution.
- Final ledger/session/project/token/site checks and PR update recorded at closeout.

## Token accounting

This journal has no numeric usage owner entries. It references the three exact
entries in the material-profile session and does not duplicate or split them.
The same active parent turn contains PR creation and the accounting steering
message; current counters stay provisional and excluded. No child or thread
aggregate is added to an overlapping parent aggregate.

## Follow-up

Refresh PR99 public discussion and synchronize its ledger, push the correction,
then continue hosted checks. Current parent-turn usage can be finalized only
from a later completed boundary. No merge or human design approval is inferred.

## Final accounting and discussion checks

Refreshed public PR99 metadata/discussion: no public comments/reviews at capture.
Retained14 messages across3 completed visible turns plus9 active parent discussion
messages. All completed usage turns have matching visible records; no missing
account turns. Verified child-parent metadata attributes agent prompts correctly.
All92 PR ledgers validate and canonical import replay is idempotent.

The initial hosted token-site check failed because PR99 could not have its own
numbered interaction record before creation. This update adds that required file;
final hosted checks are rerun after push. No detector behavior changed here.

Current project observation:200 sessions,126 with usage/74 without;237 disjoint
turns,744152882 input+4196784 output=748349666 observed tokens. PR99 contributes
7356456 completed tokens. The active parent turn is excluded, not zero. These
are usage observations, not billing or a complete project total.

Site preview first rejected an output outside the required _site/ directory; rerun under _site/pr99 succeeded. This was a destination guard, not a data/ledger failure.
