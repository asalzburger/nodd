---
name: "nodd-review-validation"
description: "Review nODD proposals, implementation or scientific evidence at an exact revision, with reproducible checks and clear limitations."
---

# Review and validate nODD work

Read the checkout's `AGENTS.md`, the assigned role profile and relevant DES/ADR,
validation specification and evidence. Use `docs/AGENT_WORKFLOW.md` when creating
or resuming an assignment. Review the supplied full commit and file set; inspect
historical sources with `git show REV:path`, not substituted working-tree bytes.

Assess the question within the assigned mandate:

- SysArch: envelopes, clearances, interface ownership, shared services/budgets.
- PhysVal: benchmark definitions, response assumptions, uncertainty, controls,
  configuration identity and the scientific interpretation of evidence.
- SoftEng: implementation against the governing design, reproducibility,
  identifiers, environment requirements and meaningful regression checks.
- PubDoc: claim/source/version correspondence and accurate lifecycle wording.

Reviewers should examine primary inputs before reading the author's conclusions.
A separate agent context is evidence of a separate assessment, not proof of
expertise or human approval. State when the same agent authored and reviewed work.

Separate recorded claims, checks you actually ran, and checks still required.
Choose checks appropriate to the scope from the repository's existing tools.
Before using ACTS/DD4hep/Geant4, follow the existing acts-spack preflight; a
document-only assignment can identify missing runtime evidence without running
simulation. Do not install shared dependencies to make a review pass.

Report findings with exact files/locators, impact on the requested claim and
the evidence or correction needed. Retain adverse results and unresolved
assumptions. A read-only reviewer returns findings; remediation belongs to the
author/coordinator under a new or updated file-ownership assignment.

Return the assignment ID, reviewed commit, source set, findings, actual command
results and limits. Recommendations remain technical assessments. Only identified
humans grant design sign-off/acceptance through the existing workflow. Curate
the result into the session journal; enter formal project review records only
when the task requests that workflow and the record has the required evidence.
