# SESSION-2026-09-24-local-token-backfill — Recover and reconcile local project token usage

## Scope and evidence

Infrastructure work under ADR-004; no detector or scientific tracking change.
Starting revision: `bb1f2dd512cd56b8c7e52679350ea843d8e3f0ff` on main.
The preceding token-accounting and audit changes were present at task start and
are included in the requested PR. The unrelated tracker bytecode is preserved.
Work continues on `infrastructure/local-token-accounting`.

## Selected conversation

User (exact): “I have worked from two different computers, this is one. Try to
match & fill from this local machine - if you have misses, gaps, it's likely
because they are on anohter local database. Do your best.”

User (exact): “Make a PR when you are ready, commit and push it (permission granted)”

Assistant outcome: recovered usage-only evidence and matched tasks from curated
requests and client metadata, without copying raw conversations or private model
state. Current-branch logs are populated; pending branch matches and gaps remain
explicit.

## Decisions and outcomes

The [recovery report](../usage/README.md) and [machine-readable inventory](../usage/USAGE-2026-09-24-local.json)
retain counter evidence, exact thread/turn IDs, accounting boundaries, attribution
basis and pending records. The snapshot contains 18 threads, 1,735 usage events
and 1,675 request increases after removing 60 repeated cumulative snapshots.
Each increase equals its last-request counters; no reset, inherited prefix,
unexplained aggregate or outside-turn event was found.

Imported 61 disjoint turns into 33 existing session records: 86,460,827 input
and 389,669 output tokens. Another 47 turns match 14 task records on cached Git
branches and are retained for later import. Eleven closed orientation, status or
discussion turns lack a confident bounded-session match and remain unassigned.
Four dashboard tasks have no local match; the other computer may supply them.
One interrupted turn has no observations. The current recovery turn is active
and is not imported.

A single client turn contains stage-B roles plus physics-role/naming steering.
It is counted once in stage-b-roles, with a cross-reference in physics-validation-role.
Original narratives and limitations are retained, with dated accounting corrections.
Models and missing measurements are not guessed. Exact client IDs prevent
cross-machine double counting when overlapping history is later recovered.

The opt-in recovery tool is tested against synthetic fixtures. It reads selected
SQLite metadata in read-only mode and decodes only token-count event lines.
Manual task matching additionally inspected user-visible requests and selected
tool/session references; no private model state was retained. Parent/child
activity corroborates child-task attribution. Exact branch revisions for pending
records were read from local cached Git refs; scientific branch contents were
not merged into this infrastructure change.

## Commands and validation

Actual commands and results, including failed attempts and fixes, are recorded
in the paired JSON. Initial recovery rejected context-only last-counter snapshots;
these carried no cumulative increase, so they are now excluded before validating
real request totals. Tests verify that invalid positive increments still fail.
Batch import replay preserved totals. The earlier uncommitted implementation task
already documented its interrupted dashboard test run and successful clean-clone
retry. This task validates the final changes again before publication.

## Changes and revision links

The paired JSON lists all files included in the combined accounting/backfill PR:
logging tools/tests, workflow instructions/template, ADR-004 implementation notes,
dated historical corrections, three current session pairs and the recovery report.
No source-catalogue or detector provenance changed. Usage provenance is retained
in the numeric inventory and per-entry source hashes. Commit and PR references
will be recorded after they exist; no human approval is inferred from publication.

## Token accounting

The current task's usage is incomplete and intentionally excluded. The normal
project summary includes only imported session entries. The recovery inventory
also contains evidence copies and pending usage; its imported row must never be
added to the project summary a second time. Other-machine coverage is unknown.

## Follow-up

Recover usage from the other computer and reconcile by exact thread/turn IDs.
Import the pending branch matches when their target records are present, following
the report instructions. Resolve unmatched turns only with evidence. No design
sign-off or scientific acceptance is requested.
