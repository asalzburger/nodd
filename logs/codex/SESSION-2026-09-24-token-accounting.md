# SESSION-2026-09-24-token-accounting — Add token usage ingestion to project logs

## Scope and evidence

Contemporaneous infrastructure work under ADR-004, which remains DRAFT.
Starting revision: `bb1f2dd512cd56b8c7e52679350ea843d8e3f0ff` on `main`.
The existing untracked `tools/tracker_layout/__pycache__/covariance_control.cpython-314.pyc`
was preserved. No detector, scientific tracking or approval records were changed.

## Selected conversation

User request (exact): “Can you add the token accounting into the logs ?”
The preceding audit found 36 session records and zero usage observations.
The assistant implemented explicit ingestion of exact client-reported counters.
An optional clarification about historical recovery was asked; no answer or
usage export was available while implementing the ingestion workflow.

## Decisions and outcomes

- Added `record-usage` for a single disjoint client turn and `import-usage` for a
  curated JSON array, with dry-run previews and aggregate observed token output.
- Preserved the version-1 schema and distinction between unknown and zero.
  Cached input and reasoning output remain subsets of input/output.
- Exact replays are idempotent. Cross-session attribution and conflicting
  counters/evidence are rejected; invalid batches cannot partially update a log.
  Writes use an exclusive importer lock and atomic replacement.
- Updated the logging guide, narrative template, repository instructions and
  ADR-004 implementation history. Usage summaries expose sessions without usage.
- No current or historical counters were available for ingestion. No raw client
  archives, private model state, credentials or transcripts were collected.
  Client protocol inspection did not establish a usable per-turn historical
  source. No unattended collector or automatic client hookup is claimed.
- This is infrastructure maintenance, excluded from scientific progress tracking.
  No issue was created and no human design sign-off was recorded.

## Commands and validation

The paired JSON records actual test commands and results. Logging tests cover
valid ingestion, replay, invalid counters, cross-session duplicate prevention,
missing measurements, failed writes, CLI aggregation and documentation links.
Dashboard tests were interrupted in the original workspace because their fixture
copy included the large ignored reference cache. The retry uses a temporary local
Git clone with current edits overlaid, preserving tracked fixtures and Git history.
The dashboard build succeeded in the actual workspace.

Additional inspection: `codex --version` reported `codex-cli 0.156.1`;
`codex app-server generate-ts --out /tmp/nodd-token-protocol` generated protocol
bindings for inspection only. CLI commands warned that sandbox restrictions
prevented creating PATH aliases but returned success. `pgrep` could not list
processes; the test run was stopped through its existing command session.
The OpenAI Docs skill was consulted; no provider-specific adapter was added.

## Changes and revision links

See the paired JSON inventory. Changes remain uncommitted; no PR was published.
Earlier log records and reference provenance remain unchanged.

## Token accounting

Exact counters were unavailable, so this session's `usage` remains empty.
The project summary reports 0 of 37 sessions with usage and unknown input/output
totals. Synthetic counters appear only in tests. Real usage requires a curated
client export with stable thread/turn IDs and verified assignment to project tasks.

## Follow-up

Import real client observations when supplied and append dated evidence corrections
for historical backfill. An automatic collector needs a verified client interface
and disjoint accounting boundaries; manual import capability does not establish
complete telemetry. No scientific review or sign-off is requested by this change.

## Token usage recovered — 2026-09-24

Recovered local client-reported counters for 1 disjoint turns: **2,376,460 input** and **12,054 output** tokens. Cached input and reasoning output are subsets, not additions. Request-to-task matching and counter evidence are retained in [the recovery inventory](../usage/USAGE-2026-09-24-local.json).

This dated correction supersedes earlier statements that token counts were unavailable for these turns. Original narrative and limitations are preserved. It does not establish complete coverage across machines; unmatched and branch-only turns remain explicit in the inventory.
