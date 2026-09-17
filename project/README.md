# Project tracking register

The dashboard is a read-only view of Git records. Start with the
[dashboard proposal](../docs/DASHBOARD_PLAN.md) and
[build and preview instructions](../tools/dashboard/README.md).
The user's 2026-09-17 implementation request authorizes this infrastructure;
it does not grant detector design sign-off or publication authorization.

`tracking.json` owns operational work state. `reviews.json` owns review requests
and round history. The adjacent JSON schemas document required fields; the builder
validates their supported subset and additional semantic constraints. Documents
own their declared lifecycle, formal sign-off records own human approval evidence,
and validation reports own execution and acceptance results.

Update records in the same PR as the relevant deliverable. Stable IDs must be
unique, references must resolve, and dependencies must be acyclic. Use null for
unassigned owners or unknown dates; do not invent measurements or assignments.
`updated` is the date of the curated record update, not the inferred start of work.
Stage A remains completed for progression while M0 governance remains pending.

Work states are planned, ready, active, blocked, completed and cancelled. A ready
or active task needs completed task dependencies. A blocked task needs a blocker
reason and next action; completed tasks need deliverables and an explicit
completion disposition. This never advances linked designs or ADRs.

To add a governed document, add its stable ADR/DES ID and path to `documents`,
then reference that ID from the relevant task. Link retained validation reports
in `validation_reports`; leave the list empty when none exist. Declared validation
without a report is shown as a discrepancy. A report link alone does not prove
its checks ran or that scientific acceptance was granted. The status adapter accepts the
existing `- Status:` Markdown field and the established lifecycle values. A
missing or unsupported format stops the build. Templates are excluded.

To request review, append a round with a unique ID, task and document IDs, exact
full target commit SHA, type, state, pending outcome, reviewer assignments (empty
if not assigned), requested date if known, null completed date, conditions and
evidence links. Supported types: technical, expert, sign-off, validation,
acceptance. Open/requested rounds cannot carry completed outcomes. Closed rounds
need a completion date and nonpending outcome. Withdrawn rounds convey no approval.

Reopening creates a new round referencing the earlier round in `supersedes`;
retain the earlier round. A closed changes-requested review remains an adverse
review, even if its issue or PR was closed. Approval of an unchanged document
survives unrelated commits; an amendment shows that the current content needs
review. Comparison uses actual historical file bytes, not repository HEAD alone.

Only humans may enter approval decisions and complete formal sign-off records.
Sign-off/acceptance rounds require identified human reviewers and an
`approval_record` under `docs/signoff/`, linking target ID/SHA, reviewer names,
review date, outcome and evidence. An approved round with unresolved conditions
cannot support lifecycle claims. `conditions_resolved` requires recorded human
confirmation when conditions exist. The dashboard checks consistency; it cannot
authenticate a reviewer or prove an approval is genuine. Humans remain responsible
for review evidence and repository protections.

Declared lifecycle states are displayed as written. Missing current-revision
sign-off or acceptance produces visible warnings. Technical/expert approval,
completed work, merged code and closed issues do not supply scientific sign-off.
Software execution and scientific acceptance stay separately described in the
linked reports; the dashboard does not infer either from exit codes.

Repository paths must exist, remain inside the checkout and refer to curated text
files; HTTPS evidence links are allowed. Only referenced Markdown/JSON/YAML files
are exported as escaped source pages. Downloaded PDFs and the TDR submodule are
not needed. Add a public TDR pointer when one is available; the current pointer
only describes revision management, not completed chapter coverage.
