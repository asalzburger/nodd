# Project session journal

Git is the canonical record. See [ADR-004](../docs/decisions/ADR-004-session-logging-and-traceability.md)
and the [repository instructions](../AGENTS.md). Logging is enabled by the user's
explicit request; the ADR remains a draft for human review.

## Start a session

Run from the repository root with Python 3.10 or newer (standard library only):

```sh
python3 tools/session_logging/session_log.py new --id SESSION-2026-09-15-example --title "Example task"
```

Choose a unique ID using the session date and a short task name. Use `--category
design` for design discussions; the default is `codex`. Use `--milestone M0` as
appropriate. `--repo PATH` explicitly selects a checkout. The command captures
HEAD, branch, initial modified/untracked paths, and recording time, then creates
a JSON record and a Markdown narrative. It never commits or overwrites files.
It does not claim that the actual conversation began at the recording time.

During work, keep the narrative's selected requests, outcomes, corrections,
commands, and open questions current. At session end, fill the JSON changed-file
inventory and checks; set status to `closed` and record an end timestamp only
if actually observed. A closed record means the bounded task is finished, not
that the design is approved. A later task in the same conversation gets a new
project session ID. Use [TEMPLATE.md](TEMPLATE.md) for narrative sections.

## Record evidence honestly

- Dates/times use UTC ISO 8601; unknown historical times are null.
- `collection` distinguishes retrospective reconstruction from contemporaneous
  recording. `completeness` describes the selected project record, not access to
  hidden client state. List known omissions in `limitations`.
- Client version, thread ID and model are null unless exposed by the client.
  Configured model names are not proof of the actual model used for every turn.
- Activities distinguish `tool` and `skill`; components are work tags. Invocation
  counts, failures, and durations are null unless measured. An empty activities
  list means no activity data recorded, not proof of no tools used.
- `usage` contains only disjoint, client-reported turns. Supply the client thread
  ID, turn ID, reported model when available, and evidence/source description.
  Do not enter cumulative counters or repeat a turn in a resumed session.
- Input, cached input, output, reasoning output, and total token fields are
  separately nullable. Cached input and reasoning output are subsets; total,
  when all relevant values exist, equals input plus output.
- An empty usage list means no token observations. It does not mean zero tokens.
  Every null counter needs an explanation in the entry's `limitations`.
- Record checks with command, exit code (when known), result and status. A zero
  exit alone is not detector acceptance. Preserve failed attempts and corrections.
- Review selected conversation text and command outputs before storing them.
  Never copy raw rollouts, private model state, credentials, personal information,
  private URLs, or confidential material. There is no automatic redaction claim.

## Validate and report

```sh
python3 tools/session_logging/session_log.py validate
python3 tools/session_logging/session_log.py summary
python3 tools/session_logging/session_log.py summary --format json --milestone M0
python3 -B -m unittest discover -s tools/session_logging -p 'test_*.py' -v
```

Validation checks every `logs/codex/*.json` and `logs/design/*.json` record,
including pairing, schema, path safety, and duplicate session/turn IDs. Reports
validate first, even when filtering by milestone, and are deterministic for the
same records. They print to stdout without silently replacing retained evidence.
Use Git to retain milestone reports when requested; identify their source commit.

Reports show observed sums and coverage for every token field, model labels,
and recorded tool/skill activities. A sum is null when no value was observed.
Model counts refer to recorded usage turns, not independently measured requests.
Component tags may overlap and must not be used to allocate tokens by addition.
No elapsed-work or cost estimates are generated. `closed` status, a passing
validator, and a token total are not measures of scientific correctness.

## Add token accounting

Record exact, client-reported usage for each completed turn when it is available.
Use the client's stable thread and turn IDs, including distinct child-thread IDs
for any separately reported subagent usage. Do not count a parent aggregate that
already includes those children. A project session can contain several turns,
but each turn belongs to exactly one project session.

For one turn, pass the observed counters to `record-usage`. This shell example
uses variables to be filled from real client evidence, not estimated values:

```sh
python3 tools/session_logging/session_log.py record-usage \
  --id "$project_session_id" \
  --thread-id "$client_thread_id" --turn-id "$client_turn_id" \
  --input-tokens "$reported_input_tokens" \
  --output-tokens "$reported_output_tokens" \
  --source "$usage_evidence_description" \
  --limitation "Cached input, reasoning output and total were not supplied."
```

When exposed, also provide `--cached-input-tokens`, `--reasoning-output-tokens`,
`--total-tokens`, and `--model`. Omitted counters stay null; use repeatable
`--limitation` arguments to explain each missing counter. The model must be the
reported execution model, not an assumed configured default. `--source` should
identify the client/export and its version or observation time when known without
including credentials or private file paths. The command does not derive totals
or silently change historical limitations or narrative text.

For a batch, prepare a **curated JSON array** containing only usage entries with
the fields in [the usage schema](../tools/session_logging/session.schema.json).
Each entry has `client_thread_id`, `turn_id`, `model`, `source`, `limitations`,
and all five token fields (`input_tokens`, `cached_input_tokens`, `output_tokens`,
`reasoning_output_tokens`, `total_tokens`). Unknown values are null. Then run:

```sh
python3 tools/session_logging/session_log.py import-usage \
  --id "$project_session_id" --file "$curated_usage_file" --dry-run
python3 tools/session_logging/session_log.py import-usage \
  --id "$project_session_id" --file "$curated_usage_file"
python3 tools/session_logging/session_log.py summary
```

Both commands validate the complete batch before writing. An identical replay in
the same session is a no-op. Changed evidence/counters for an existing turn, or a
turn assigned to another session, are rejected for explicit reconciliation in
ordinary Git history. Malformed batches leave the record unchanged. Imports are
serialized by `logs/.usage-import.lock`; if a process is interrupted, check that
no importer is still running before removing its stale lock. Do not edit session
JSON concurrently with an import.

This is an ingestion workflow, **not automatic client telemetry**. It does not
open private client archives or intercept conversations. Native cumulative
thread counters must not be entered as per-turn usage. They need verified,
disjoint accounting boundaries first; a last-request count may omit other model
calls within a turn. Keep missing observations explicit when the client does not
provide suitable counters. Record unavailable usage in the session narrative and
JSON limitations, leaving `usage` empty. Never add fabricated IDs or estimates.

For historical backfill, match the exported thread/turn IDs to the bounded task
before importing, preserve the original narrative, and append a dated correction
explaining the new evidence. Do not allocate a shared-thread total across tasks
by message length, timestamps alone, or guesswork. Reports show observed sums
and coverage; they cannot establish a complete project total while sessions or
turns remain unobserved.

### Authorized local historical recovery

On 2026-09-24 the user authorized recovering this project's usage from the local
machine, with missing data potentially held on another computer. The separate,
opt-in recovery tool reads an explicitly selected Codex store in read-only mode:

```sh
python3 -B tools/session_logging/recover_usage.py \
  --codex-home "$client_data_directory" --project "$project_directory" \
  --output "$new_usage_inventory_file"
```

It supports the inspected `state_5.sqlite` / `thread_history_1.sqlite` layout
and associated token-count events. It selects the project's working directory
and descendants, reads thread/turn metadata, and decodes only `token_count`
event lines. It does not query conversation items or retain non-usage lines.
Other client layouts fail explicitly; this is not a stable vendor API.

Each cumulative increase must equal the last-request counters. Repeated
cumulative snapshots are ignored, including context-accounting snapshots that
change the last figure without increasing usage. Decreases, unexplained jumps,
invalid request totals and overlapping turn boundaries fail recovery. Requests
are grouped using persisted turn ordinals. Unclosed turns are marked in progress;
turns without observations remain unknown. The output never overwrites a file.

Task attribution is a separate curated step: compare user-visible requests and
existing session records, using direct session-ID evidence where available.
Child turns need recorded parent/child relationships and matching parent-turn
activity, not a timestamp guess. Never infer the actual model from a configured
default. The [first recovery inventory and continuation instructions](usage/README.md)
record verified assignments, pending branch records and gaps. Repeat this process
on the other computer; the same client thread/turn pair must be counted once.

## Git revisions and corrections

Before work, record the starting SHA and initial changes. Keep unrelated user
changes identified separately. Record the actual paths affected, including the
session pair. After a code commit exists, a later logging update may reference
its full SHA in `result_commits`. Leave the array empty until then.

```sh
git log --follow -- logs/codex/SESSION-2026-09-15-example.json
```

This resolves the enclosing record revision without a self-referential commit
hash. Use normal corrective commits and explain changes; never amend history to
make failed work disappear. A Git hash locates evidence but does not prove that
a narrated claim is true. Check actual tests and human review records.

## Initial records

- [Retrospective repository review and logging discussion](codex/SESSION-2026-09-15-project-bootstrap.md)
- [Logging infrastructure implementation](codex/SESSION-2026-09-15-logging-infrastructure.md)

Earlier unavailable conversations and exact usage are not reconstructed.
