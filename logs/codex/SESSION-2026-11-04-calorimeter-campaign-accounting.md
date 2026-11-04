# SESSION-2026-11-04-calorimeter-campaign-accounting — compressed archive recovery

## Assignment and scope

Explicit fallback SoftEng assignment `CAL114-Accounting`, from the campaign
coordinator, source main `cd3ec20da56537617ac6fbbcf28bd6f28104cc64`.
The worktree `codex/calorimeter-campaign-record` began clean. The paired journal
was created after this assignment's own recovery-tool edits, so its captured
`initial_changes` accurately lists those edits; no unrelated edits existed.
Read the full prepared mandate and relevant repository/logging/interaction
instructions. No delegation, remote mutation, scientific source edits, package
installation or human sign-off was performed.

The user asks to preserve work, tokens, interactions and PR identities when
consolidating ECAL70/71/73/74/75 with issue114, and to prepare HCAL/FCAL PRs.
The coordinator's initial historical recovery failed because the client had
compressed archived `.jsonl` paths into `.jsonl.zst` without updating the stored
plain paths. This assignment fixes that infrastructure boundary and recovers
only allowlisted usage evidence.

## Implementation and evidence

The reader prefers an existing recorded plain file, otherwise its exact `.zst`
sibling. It streams through Python3.14 `compression.zstd`, or an already-present
zstd executable on older Python. No decompressed raw file is created. Plain
files remain bounded snapshots; compressed input fingerprints must stay stable
through the read. Only `token_count` objects are decoded/exported; original
line ordinals, request reconciliation and per-turn event digests are preserved.
Synthetic privacy/failure controls cover unrelated non-UTF8/private lines,
invalid archives, missing decoders, changed archives and compressed database
path recovery.

Read-only selection used existing source journals plus actual parent edges.
Connected app reads reviewed visible user request boundaries and child final
assignment/source identities. No raw app response, hidden reasoning, private
model state, arbitrary command/output text or private URL is retained.
The [campaign inventory](../usage/USAGE-2026-11-04-calorimeter-campaign.json)
records exact matching bases, source revisions, parent thread/root-turn keys,
usage-only evidence digests and original restored-file hashes. Its
[report](../usage/CAMPAIGN-2026-11-04-calorimeters.md) explains the boundary.

## Coordinator decision and canonical import

The coordinator explicitly reviewed and accepted all 54 sole-owner proposals,
including the root turns spanning SiW barrel/main-page, both LAr PRs, service
PR76/overview PR75, software78–80 and both HCAL regions. These are agent
bookkeeping decisions, not scientific approvals. Shared turns remain whole in
one journal, with references from sibling PRs. No split/duplicate counters or
per-PR cost allocation is inferred.

Thirteen missing original historical journal pairs (26 files) were restored
byte-for-byte from immutable branch sources before modification. All original
narrative text and missing-usage statements were preserved; dated corrections
now state their earlier-capture boundary. The standard importer passed every
owner's dry-run, import and identical replay. All54 entries were added exactly
once; replay added zero. Twenty pre-existing observations exactly matched all
five canonical counters, so none were reimported. Fourteen earlier/predecessor
turns remain excluded/unassigned.

The new disjoint historical increment is **258,511,843 input + 1,432,322 output
=259,944,165 observed tokens** across 54 turns in 17 owners. Cached input
251,152,640 and reasoning output 661,224 are subsets. Models, client version,
complete history, cost and billing equivalence remain unknown. The FCAL
readiness turn is now closed and included once; its original 11-turn audit is
unchanged. The PR88 recommendation owner already existed and only needed a
ledger relationship. PR72/74/76/85 likewise gain explicit shared-owner links.

## Actual checks and limitations

Python3.14.6 passes 36 session controls; Python3.11 passes 14 recovery controls
through the existing zstd executable. Each of 16 streams independently
reconciles all 88 completed turns; 157 repeated snapshots and zero outside-turn
events are observed. Current campaign root/active accounting turns are excluded.

After imports and dated corrections, session validation reports 247 paired
journals. Interaction synchronization/validation covers 101 PR records, including
17 changed affected files. Token validation/build passes with 432 disjoint dated
observations and 2,085,608,014 cumulative observed project tokens. This headline
includes earlier work; it is not the cost of this PR. The standard summary
reports the exact input/output and still-missing coverage. No detector
geometry, native simulation or physics acceptance is assessed here.

Public GitHub snapshots remain their explicitly captured dates; the campaign
coordinator refreshes them before publication. A transient mid-import ledger
snapshot was stale while source owners changed; the final post-import sync and
validation pass. No failed snapshot was treated as final evidence.

## Finalized specialist usage

Exact completed accounting-child counters:12,867,619 input +36,722 output =12,904,341 tokens. One canonical owner, matched through the observed root/spawn edge. Current coordinator root turn remains excluded. Durable usage-only evidence is retained; no private rollout text is copied.
