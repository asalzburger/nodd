# SESSION-2026-09-25-device-token-backfill — Recover token usage from the second device

## Scope and evidence

Infrastructure accounting under ADR-004, following merged PR #18. Starting
revision: `7c0b8f51c41191e413a752c4297f9cdbdae6cca5` on main. Work is on
`infrastructure/device-token-accounting`. The three pre-existing untracked
tracker-layout bytecode files were left untouched. No detector parameters,
scientific sources, review decisions or design status changed.

## Selected conversation

User (exact): “PR#18 filled the logs with token information from the main computer,
now do the same from this device.”

## Decisions and outcomes

Used the existing opt-in recovery tool against this device's selected local
store, with read-only SQLite access. All 529 usage events reconciled against
last-request counters; 14 repeated snapshots left 515 requests. The capture
contains 12 threads, including nine child threads. Persisted turn boundaries
account for all requests. No reset, inherited prefix or unexplained parent
aggregate was observed. No thread/turn pair overlaps PR #18's inventory.

Imported four completed turns into the four dashboard sessions that had lacked
usage: 8,515,036 input and 64,602 output tokens. Previewed each batch and replayed
each import; every replay added zero entries. Historical narratives and original
limitations are preserved with dated corrections.

Retained 22 completed turns for ten branch-only session records as importable
pending evidence. These cover pixel modules, tracker review, magnetic expert
review and conflict repair. Cached Git revisions identify the target records;
those branches were not merged. Six short orientation/discussion turns remain
unassigned. Four failed child turns have no observations, not measured zeros.

Root attribution used selected user-visible requests and session-ID tool
references against curated narratives. Child attribution uses recorded
parent/child edges and parent spawn/followup targets, with activity ordinals
retained in the inventory. No conversation or collaboration-message bodies,
private model state or client-store paths are retained in repository artifacts.
Configured/requested models do not establish actual execution models.

## Commands and validation

Inspected PR #18 with `gh pr view 18`, repository guidance, logging workflow,
ADR-004, cached Git refs and existing session records. The first branch-creation
attempt was blocked by the sandbox; an escalated retry succeeded. One combined
documentation patch was rejected before writing because it targeted a file twice;
it was reapplied as a single update per file.

Ran `tools/session_logging/recover_usage.py` with explicit local-store, project
and temporary-output arguments. Curated only usage metadata and attribution into
the [second-device inventory](../usage/USAGE-2026-09-25-device.json). Imported the
four batches using `session_log.py import-usage --dry-run`, then `import-usage`,
and repeated imports to verify idempotence.

Extended retained-evidence tests to reconcile both inventories against session
entries, verify disposition/session totals, check cross-device disjointness and
validate child attribution boundaries. Actual test and validation results are
recorded in the paired JSON. Dashboard tests use a temporary clean local clone
with the task edits overlaid, avoiding the ignored reference cache.

## Changes and revision links

Changed four historical dashboard JSON/Markdown pairs, the usage recovery README,
the new usage-only inventory, the recovery test and this session pair. The paired
JSON lists exact paths. The original PR #18 inventory remains unchanged. New
usage provenance comprises exact client thread/turn IDs, counters, event hashes,
persisted ordinal boundaries and target-record identities. No scientific source
catalogue entry, design amendment or approval is required for this accounting.

## Token accounting

The session summary now observes 98,045,726 input and 477,200 output tokens in
67 turns across 38 of 41 sessions. Cached input and reasoning output are subsets.
Pending-branch and unassigned entries are excluded from that summary; inventory
copies must never be added again. This recovery turn remains active while the
work is performed, so its usage array stays empty. Its inventory snapshot is
explicitly incomplete. Full project coverage and billing equivalence are unknown.

## Follow-up

Later import the branch-only entries when their records are available. The
first-device recovery task also needs a later completed-turn capture from that
device. No human design sign-off is requested or inferred.

## Final local validation

32 logging/recovery tests and 27 dashboard tests passed. All 41 session records
and the dashboard records validated; the dashboard build and whitespace check
passed. Numeric capture evidence and historical-record preservation were checked.
Changes are prepared locally on the infrastructure branch; no commit, push or
new PR was made during this task.
