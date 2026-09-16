# Architecture decisions

Use an ADR for cross-cutting or difficult-to-reverse decisions: upstream import strategy, coordinates, technology selection, coverage, effective-material policy, tool support, validation, or review policy. Component designs belong in [DES documents](../design/TEMPLATE.md).

## Creating and reviewing an ADR

1. Inspect this register, existing files, and open issues/PRs; allocate the next unused `ADR-NNN` ID.
2. Copy [TEMPLATE.md](TEMPLATE.md) to `ADR-NNN-short-name.md` and add it to this register.
3. State context, alternatives, proposed decision, consequences, evidence, and unresolved questions. Label substantive claims using the repository provenance categories.
4. Link the issue and assign human reviewers. Begin at `DRAFT` and track applicable review stages from [PROJECT.md](../../PROJECT.md).
5. Record human approval evidence for an exact revision before treating the proposal as governing implementation. AI cannot sign off or accept an ADR.

For policy-only ADRs, reviewers should explain which implementation and validation stages apply. Detailed minimum review requirements remain proposed in ADR-002.

## Supersession

Preserve historical decisions and evidence. A replacement ADR must link the prior decision, explain the change and consequences, and obtain human approval. After approval, maintain reciprocal supersession links; do not silently rewrite accepted policy.

## Register

| ID | Decision | Status | Human owner |
| --- | --- | --- | --- |
| [ADR-001](ADR-001-upstream-baseline.md) | Upstream baseline and import strategy | DRAFT | TBD |
| [ADR-002](ADR-002-review-and-signoff-policy.md) | Review and sign-off policy | DRAFT | TBD |
| [ADR-003](ADR-003-validation-and-artifact-policy.md) | Validation and artifact policy | DRAFT | TBD |
| [ADR-004](ADR-004-session-logging-and-traceability.md) | Session logging and project traceability | DRAFT | TBD |
| [ADR-005](ADR-005-reference-reading-pilot.md) | Reusable reference reading pilot | DRAFT | TBD |
