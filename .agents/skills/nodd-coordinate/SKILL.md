---
name: "nodd-coordinate"
description: "Coordinate substantial nODD tasks using bounded specialist assignments, revision-specific handoffs and repository records."
---

# Coordinate nODD work

Use the nODD checkout as the working root. Read its `AGENTS.md`, `PROJECT.md`
and the relevant task/design records. The eight mandates in
`docs/DEVELOPMENT_PLAN.md` section 6 are authoritative. Read
`docs/AGENT_WORKFLOW.md` for assignment fields and client setup when needed.

Keep a small, dependent change with the main agent. For substantial work,
delegate independent contributions to the relevant roles:

- ProRes: objectives, priorities and unresolved tradeoffs.
- SysArch: cross-system envelopes, physical interfaces and aggregate budgets.
- TrackTech, CaloTech, MuonTech: the affected subsystem's technology/design.
- SoftEng: implementation, runtime and reproducible execution.
- PhysVal: separate assessment of scientific assumptions, observables and results.
- PubDoc: TDR and claim/source/revision consistency.

Start only roles with a concrete deliverable. Run independent reading in parallel;
wait for an implementation or proposal before asking a reviewer to assess its
exact revision. A specialist may contribute without another nested delegation.
Keep the main agent responsible for reconciliation and final delivery.

Before spawning, record the assignment ID, role, full input commit, source files,
read/write mode, owned files, question, deliverable and completion condition in
the task's session record. `tools/agent_workflow/workflow.py prepare` validates
these fields and emits a prompt containing the role instructions. It does not
spawn agents or enforce a filesystem sandbox.

Use native role selection if the client exposes and confirms it. Otherwise pass
the complete prepared prompt to the available subagent tool, or direct the child
to read a saved copy in full before acting. Explicitly direct
the child to the checkout and relevant skill paths; inherited discovery may come
from a different working directory. Report this as explicit role assignment,
not verified native profile loading. If delegation is unavailable, do the work
sequentially and record that a separate agent review was not performed.

Give parallel writers disjoint files or isolated worktrees. Include owned output
files in each write assignment. Reviewers receive read-only assignments and
source revisions; a behavioral assignment does not override client permissions.
Do not infer a design decision from agent agreement or merge status.

Collect each role's result with its assignment ID, examined revision, citations,
changed files, actual checks and limitations. Reconcile disagreements against
evidence; route physical design choices to the existing human review workflow.
Store the curated handoffs in Git using `logs/README.md`. Update scientific
tracking/reviews when required by `AGENTS.md`; infrastructure tasks remain
excluded. Preserve observed token counters separately from missing measurements.

Use `nodd-design-evidence` for evidence-backed proposals and
`nodd-review-validation` for technical assessment. Follow existing validation
and session closeout commands rather than creating another progress registry.
