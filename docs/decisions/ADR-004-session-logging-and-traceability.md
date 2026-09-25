# ADR-004 — Session logging and project traceability

- Status: DRAFT
- Created: 2026-09-15
- Human owner: TBD
- Issue: None; implementation requested directly in the project conversation
- Related decision: [ADR-003](ADR-003-validation-and-artifact-policy.md)
- Human approval evidence: Pending

## Context and authorization

[PROJECT.md](../../PROJECT.md) and [AGENTS.md](../../AGENTS.md) require Git-based
traceability and curated session records. The user explicitly requested implementing
logging infrastructure and starting logging, with Git as the source of truth.
That authorizes this M0 infrastructure work; it does not constitute formal ADR
sign-off, detector design approval, or completion of M0. The user confirmed that
no competing work exists; remote issue/PR inspection is unnecessary for this task.

## Options

| Option | Benefit | Limitation |
| --- | --- | --- |
| Narrative only | Easy to review | Difficult to aggregate and compare |
| Raw client archives | Extensive client-specific detail | May contain prohibited private state; unstable formats |
| Curated narrative and structured metadata | Reviewable history and reproducible statistics | Requires explicit curation and completeness tracking |

## Proposed decision

**NODD DESIGN CHOICE:** pair a Markdown narrative with a versioned JSON record for
each bounded work session. Maintain these in `logs/codex/` or `logs/design/`.
Use stable project session IDs independent of client threads. Multiple work
sessions may share a client thread; their accounting must not overlap.

Record available user-visible requests, outcomes, corrections, commands, tests,
Git revisions, changed paths, work attribution, model/tool/skill usage, and
limitations. Keep detector components separate from model and tool names.
Human identities and private URLs are excluded from session logs; formal human
review belongs in the project's designated review records.

Only client-exposed token counters may be recorded. Version 1 accepts disjoint
per-turn usage records, identified by unique `(client_thread_id, turn_id)` pairs.
It rejects duplicate pairs across sessions. Cumulative session snapshots must be
converted to verified disjoint turns outside this tool or left unrecorded.
Cached tokens are a subset of input; reasoning tokens are a subset of output.
Do not add these subsets again. Unknown fields remain null with limitations.
No costs, token counts, model identity, durations, or historical timestamps are
inferred from text length or the assistant's self-description.

Record the starting commit and initial changed paths. Result commits may be
added after committing. A log cannot contain the hash of its own enclosing
commit: use `git log --follow -- <record>` to find that revision. Preserve
corrections through normal Git history; do not rewrite historical evidence.

## Implementation and verification

The [logging guide](../../logs/README.md) defines the workflow. The Python
standard-library tool creates paired records, validates the published schema
and semantic invariants, and generates aggregate JSON or Markdown reports.
The validator deliberately supports only the schema features used here and
fails on unsupported schema keywords. It is not a general JSON Schema engine.

Version 1 captures Git metadata at creation and aggregates curated entries.
It does not intercept interactive chats, read private client archives, enable
telemetry, or automatically measure tool calls. Narratives and metrics must be
completed from available evidence. This limits coverage but avoids invented data.
Public records must be reviewed for confidential content before committing;
structural validation is not a privacy or factual-accuracy guarantee.

Tests cover malformed records, duplicate accounting, unknown versus zero,
token subsets, links escaping the repository, reporting, and command-line
creation without overwriting existing records. No detector checks apply.

## Human review and open questions

- Assign an owner and review the schema and retention policy.
- Decide whether a later client-specific collector is needed, after verifying
  that client's exposed events and their counting semantics.
- Decide whether cost accounting or a CI gate is useful after initial use.
- Historical conversations outside the available context remain unrecorded.

This ADR remains DRAFT. No external technical source claims or detector
parameters are introduced; the rationale is a project infrastructure choice.

## Implementation update — 2026-09-24

The user requested adding token accounting to the logs. The logging CLI now
provides `record-usage` for one client-reported turn and `import-usage` for a
curated JSON array. Both validate before writing, support preview, reject
cross-session double counting and conflicting evidence, and treat an identical
replay as a no-op. The existing version-1 schema and subset accounting remain
unchanged. Session summaries explicitly count sessions without observations.

These commands ingest supplied counters; they do not collect client telemetry.
Historical backfill needs a verified task-to-turn mapping and a dated correction.
No exact token measurements were available in the 36 existing records when this
work began. This implementation update does not grant ADR approval or imply that
missing historical usage has been recovered.

The user subsequently authorized historical recovery from this local machine,
noting that another computer may hold missing sessions. The opt-in
`tools/session_logging/recover_usage.py` exports usage-only evidence from the
explicitly selected local client store. It verifies cumulative-to-request
arithmetic and persisted turn boundaries before curated task matching and import.
The [2026-09-24 recovery inventory](../../logs/usage/README.md) records the imported
turns, pending branch-only matches and unmatched observations. Historical
narratives are preserved with dated corrections; no inference from token counts
grants scientific progress or human sign-off. The earlier absence-of-usage finding
describes the logs before this recovery, not the retained local client evidence.
