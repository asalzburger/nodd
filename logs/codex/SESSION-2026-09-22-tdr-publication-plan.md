# SESSION-2026-09-22-tdr-publication-plan — Outline TDR and publication plan with PubDoc

## Scope and evidence

Contemporaneous, curated record of the bounded PubDoc assignment and PR category
change. Starting revision: `bb1f2dd512cd56b8c7e52679350ea843d8e3f0ff`, branch
`documentation/tdr-publication-plan`. The pre-existing untracked tracker bytecode
was preserved. Exact token usage, client version and thread ID are unavailable.
Related work: TASK-B-PUB, DES-003, DES-005, ADR-002 and ADR-006. These references
do not change any design or ADR lifecycle state.

## Selected conversation

User, exact request: “Now, a publication plan: the PubDoc agent should start
outlining the TDR with subsections to give a documentation frame. Also
\"Documentation: \" is a new PR category to be added.”

Assistant, paraphrased outcome: delegated the chapter/subsection outline and
publication plan to PubDoc; integrated the naming category, evidence links,
dashboard tracking and a review PR.

## Decisions and outcomes

The parent repository carries the draft TDR frame and publication plan. The
existing Overleaf-backed submodule remains unchanged: its README reserves
pushes for a deliberate manual step. This makes the initial outline reviewable
without prematurely publishing a report or changing the report revision.

PubDoc owns editing and claim traceability; subsystem specialists retain
technical responsibility. Existing draft designs, prototypes and future
evidence are distinguished. Human review, later chapter writing, LaTeX migration
and final publication remain separate actions. The paused tracker study is not
resumed by this documentation task.

`Documentation:` is a valid PR category and requires a project tracking update.
Publication-plan paths and the TDR submodule pointer cannot use the
infrastructure exemption. Updated TASK-B-PUB for the bounded outline deliverable
and reconciled PR #16's observed merge metadata; neither implies design approval.

## Commands and validation

Read project instructions, the development-plan PubDoc mandate, TDR source
structure, existing designs and review policy. Read current issues and PR #16
metadata with GitHub CLI. Added a focused Documentation tracking-policy test.
Actual commands and validation results are listed in the paired JSON record.
No detector validation or LaTeX compilation is claimed for Markdown planning.

## Changes and revision links

See the paired JSON changed-file inventory. The principal deliverables are
`docs/publication/TDR-outline.md` and `docs/publication/publication-plan.md`.
Other changes update the naming rule/checks, discovery links and tracking.
The existing source catalogue and detector parameters are unchanged; provenance
is linked to existing design, source and validation records in the outline.
Result commits are recorded only after they exist.

## Follow-up

Review the proposed structure, input owners, evidence coverage and writing order.
Specialists need to supply the missing technical evidence and chapter claims;
the plan retains unresolved simulation, services, field, response and performance
inputs. Human reviewer assignments and publication details remain open. Final
sign-off authority remains `asalzburger-review`; no approval is recorded here.
