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
