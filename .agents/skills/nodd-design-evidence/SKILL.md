---
name: "nodd-design-evidence"
description: "Gather traceable evidence and draft nODD design alternatives or bounded subsystem inputs before implementation."
---

# Prepare evidence and design inputs

Read the checkout's `AGENTS.md`, `PROJECT.md`, relevant DES/ADR and source
manifest. Apply the assigned role from `.codex/agents/` and the bounded task
contract; role mandates are in `docs/DEVELOPMENT_PLAN.md` section 6.

For a pinned assignment, inspect sources at its full input revision using
`git show REV:path`. Name the examined revision in the result. Distinguish a
document's statement from independently verified public-source evidence.
If new literature is needed, inspect the actual public source and record its
precise locator; an unverified reference entry or search snippet is insufficient.

Classify nontrivial parameters and assumptions as FACT, INFERENCE or NODD DESIGN
CHOICE under the existing provenance rules. Facts need source IDs/locators;
inferences need derivation and uncertainty; choices need rationale and open
approval status. Use `reference/manifest.yaml` for newly cited scientific sources.
Keep unavailable or contradictory evidence visible rather than inventing values.

Produce the requested bounded input or draft in the established DES/ADR format.
Compare alternatives by the quantities the task actually needs: geometry,
clearances, material, services, response or validation. Identify affected physical
interfaces for SysArch and scientific claims/observables for PhysVal. State what
evidence would discriminate between unresolved alternatives.

Read-only assignments return a cited contribution to the coordinator. Write
assignments edit only owned files. Implementation follows the existing design
approval workflow; unsigned explorations must remain isolated PROTOTYPE work.
An agent must not grant sign-off or advance a document to SIGNED OFF or ACCEPTED.

Return the assignment ID, input revision, evidence locators, conclusion,
uncertainties, changed files and actual checks. The coordinator curates the
handoff into the session record and handles integration/tracking. Delegation
adds no authority to publish, message others or change detector parameters.
