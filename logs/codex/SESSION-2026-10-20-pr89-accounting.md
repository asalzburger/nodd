# SESSION-2026-10-20-pr89-accounting — PR89 usage and merge readiness

## Scope and evidence

User request: “That looks good, do the token accounting for this PR #89 and
make it ready to be merged.” This is an accounting/readiness follow-up, not a
request to merge. Starting branch `codex/odd-idres-comparison`, clean at
`460fcb0977cd6ed8054439d554d1dc6b81c947be`; fetched main remains
`33a607b70214532cd265623241b0c250ca0da361`. Existing scientific outputs and
unrelated checkouts are preserved.

Applied the repository's [nodd-review-validation](../../.agents/skills/nodd-review-validation/SKILL.md)
procedure under the SoftEng mandate, assignment PR89-READINESS-2026-10-20:
review the exact starting head and logging/usage evidence; write only the paired
journals, usage inventory/index, existing task metadata and PR description;
finish with validated accounting and the final PR's merge/CI status. This is
an author follow-up assessment, not an independent scientific review or human
sign-off. No new detector, material or response approval is recorded.

## Recovery and attribution

The existing opt-in usage-only recovery selected this chat explicitly, using
read-only client metadata and token-count events. No conversation-item database
query or raw model-state collection was used. Three closed turns match the
original IdRes request, expansion and continuation/PR89 closeout. A closed
interrupted turn and a client-labelled failed turn retain their observed usage;
client execution status does not erase consumption. Their exact boundaries and
match rationale are in the [curated inventory](../usage/USAGE-2026-10-20-pr89-accounting.json).

The original record SESSION-2026-10-19-odd-idres-comparison is the sole owner:
12,783,549 input +53,939 output =**12,837,488 observed tokens** from67 requests.
Cached input12,530,816 and reasoning output15,583 are subsets. All five counters
are observed, not estimated. Before import no canonical record owned these
thread/turn IDs. Dry-run passed; import added3 entries; replay added0 and found
3 unchanged. Two repeated cumulative snapshots are excluded. Inventories are
evidence and never an extra contribution to the site total.

The original journal's initial unknown-usage statement is preserved with a dated
correction; client version and executed model remain unknown. The active
accounting/readiness turn is excluded until it closes. This follow-up record
therefore has an empty usage array, meaning unknown rather than zero.

## Readiness and checks

GitHub inspection at the starting head: PR89 OPEN, isDraft=false,
mergeable=MERGEABLE, mergeStateStatus=CLEAN; no reviews or inline review comments.
Project validation and token-site checks both succeeded on460fcb0; deployment
is intentionally skipped for PR previews. No approval or merge is inferred.

Actual local checks after the accounting update:

- Read-only usage reconciliation and import dry-run/import/replay passed.
- Session logging/recovery tests:33 passed; token-site tests:10 passed.
- `session_log.py validate`:185 paired records valid.
- `session_log.py summary --format json`:213 unique observed turns; project
  input633,537,785 + output3,599,108 =637,136,893 observed tokens. This increases
  the earlier project total by exactly12,837,488; no duplicated ownership.
- `tools/token_usage/build.py validate` and `build --output _site/pr89-accounting`:
  213 dated turns and637,136,893 tokens; preview generated without publishing.
- `tools/odd_idres/verify.py`:all15 runs,64881 fit rows,7209 profiles,
  54 controls and7 SVGs still verify; scientific inputs/results unchanged.
- `tools/project_records/validate.py`:67 tasks,36 documents,21 review rounds valid.
- `git diff --check`:passed.

The ordinary follow-up commit supplies the accounting audit and PR description.
Hosted CI is rechecked on that pushed revision before the user-facing handoff.
No merge, auto-merge or reviewer approval is performed.

## Changed records and follow-up

Seven paths are inventoried in the paired JSON: original IdRes journal pair,
this follow-up pair, usage-only inventory/index, and existing task metadata.
Task TASK-PUB-ODD-IDRES links the new audit without adding an infrastructure
progress task. No scientific deliverable or design lifecycle changes.

Recover this accounting turn only after its final client boundary closes;
never allocate provisional counters or combine cached/reasoning subsets into
new totals. Exact model/client version and other device history remain gaps.
