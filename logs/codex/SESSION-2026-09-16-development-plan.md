# SESSION-2026-09-16-development-plan — Successor objectives and development plan

## Scope and evidence

Contemporaneous curated record, 2026-09-16. Starting branch `main`, commit
`2f1cd77357568412780f53fef387693e23326330`. The paired JSON records the substantial
pre-existing resource, scope and assessment edits, all preserved. Exact tokens,
client version and conversation start are unavailable.

Read repository instructions, current PROJECT, charter, review policy, reading
policy, design template, logging instructions, source-coverage records and ODD
assessment. No new empirical source was required for this planning task.

## Selected conversation

User direction (paraphrase): modify/rewrite ODD into a new DD4hep detector retaining
recognizable features in the TrackML–ODD–nODD lineage; give all components,
electronics, fields, supports and cable routes more reliable technical grounding;
finish with a TDR, with final naming deferred. Aim for something plausibly built
from the simulation/performance perspective, without claiming complete technical
buildability or CAD engineering. Present a detailed approach and possible expert
agent/central planning roles.

Assistant outcome (summary): made these objectives explicit in PROJECT and the
charter, then drafted PLAN-NODD-001 with stages, dependencies, outputs, gates,
nine work packages, interfaces, provenance, agent roles and TDR programme.

## Decisions and outcomes

- Preserve broad purpose/features while permitting justified component/code
  replacement. Retained upstream values need technical justification too.
- Work on baseline characterization and evidence/interface requirements together;
  retain RD53 pixel modules as the first representative implementation without
  deferring other subsystem requirements.
- Include magnets and global services early. Use calo/muon assemblies to test
  generality before settling the generation architecture.
- Keep source facts, inference and proposed choices distinct, and do not confuse
  extracted or mapped literature with a completed scientific review.
- Maintain an immutable ODD control. Separate controlled geometry comparisons
  from each detector's best supported calibrated/reconstructed operation.
- Develop the TDR continuously and freeze it against accepted release evidence.
  nODD remains a working title; deferred engineering questions remain explicit.
- Propose bounded specialist-agent tasks coordinated through Git/interfaces;
  agents are not human experts or approvers. No agents launched in this task.
- PLAN-NODD-001 and the charter remain DRAFT. No ADR/design was signed off, no
  issues or PRs created, and no production geometry changed.

## Commands and validation

- Inspected current branch, dirty tree and relevant documentation.
- Corrected an initial ADR-005 filename lookup to the existing
  ADR-005-reference-reading-pilot.md and read it.
- Created session pair using `session_log.py new`.
- Ran the logging/documentation unittest suite: 15 tests passed.
- `git diff --check`: passed.
- Final session-schema validation result is recorded in the paired JSON.

No simulation/build/performance validation was performed; this is a plan.

## Changes and revision links

Updated PROJECT objectives/M7 deliverable, realism charter and documentation
index. Added docs/DEVELOPMENT_PLAN.md and this session pair. No new scientific
parameters or source-catalogue entries. No commit or branch change.

## Follow-up

Human review of the proposed plan and checkpoint decisions remains open. First
jobs are baseline/environment proposals, RD53 module comparison, material/readout
audit and source dossiers for other systems. M0 execution and completion, design
sign-off, implementation and TDR release remain future work.
