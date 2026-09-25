# SESSION-2026-09-24-token-history-audit — Inspect retained project token usage metadata

## Scope and evidence

Read-only local usage-metadata audit under ADR-004. Starting revision and existing
uncommitted token-ingestion work are preserved in the paired JSON. This task only
adds its own session pair; the existing untracked tracker bytecode is untouched.
No scientific progress or human approval is recorded.

## Selected conversation

User request (exact): “Is there any way to get the token usage filled for the
sessions we missed? Is there a record ?”
Assistant finding: the local client does retain usage counters for project threads,
although the repository's curated session logs have no imported counters.

## Decisions and outcomes

Inspected database schemas and selected thread, turn and usage metadata only.
Local `state_5.sqlite` identifies project threads by working directory; retained
session event files contain `token_count` events. Only matching token-count event
objects were decoded for counter-field inspection. Conversation content and
private model state were not displayed or retained.

At the observed snapshot:

- 18 project threads had retained token-count records; 15 had recorded parent
  edges, identifying child threads.
- 1,724 usage events contained cumulative and last-request input, output, cached
  input, cache-write input, reasoning output and total token fields.
- Thread creation dates ranged from 2026-09-15 through 2026-09-24.
- Persisted metadata contained 112 completed turns, 7 interrupted turns and
  1 in-progress turn.
- None of the 37 curated project logs inspected had a client thread ID.

This establishes a historical recovery source, not a verified project total.
Event snapshots cannot simply be added. Recovering disjoint turn usage requires
checking cumulative boundaries, repeats, resets, forks, parent/child accounting,
and mapping turns to the repository's bounded task records. Threads from other
working directories, deleted history or other machines may be absent.

The previous answer concerned missing counters in the repository logs and lack
of a supplied export. This audit establishes that local retained usage metadata
is available and can support a dedicated backfill investigation.

## Commands and validation

Used read-only SQLite connections to inspect relevant schemas and select project
metadata, and streamed only token-count event lines for field/count inspection.
The paired JSON lists the observed query results and final repository validators.
No existing usage entry, historic evidence, client database or source catalogue
was changed. Installed generated protocol types were inspected for usage APIs;
no new provider adapter or telemetry collector was added.

## Changes and revision links

Only this Markdown/JSON pair was added by the audit. No commit or PR was created.

## Token accounting

No turn was imported: attribution and disjoint accounting boundaries remain
unverified, and the current turn is incomplete. Missing usage remains unknown,
not zero. No token sum is inferred from event counts.

## Follow-up

Extract usage-only records, establish disjoint counters, and map each turn to its
project task before importing. Preserve unmatched usage separately as unassigned
rather than guessing an allocation. Review completeness across machines and
worktrees before claiming a full project total.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **921,071 input** and **5,072 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
