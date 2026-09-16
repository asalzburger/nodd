# nODD documentation

## Current phase

**Active work: stage B — full-detector architecture.** The user closed stage A for progression on 2026-09-16, relying on ODD/ColliderML evidence; see the [plan](DEVELOPMENT_PLAN.md). Outstanding governance and design sign-off requirements remain applicable before production changes. The repository is the canonical record; see [repository instructions](../AGENTS.md) and [project scope](../PROJECT.md).

The documents below establish proposals and recording formats. Their presence does not constitute human approval or completion of M0.

## Index

- [Full-detector development plan and TDR programme](DEVELOPMENT_PLAN.md)
- [DES-003: global envelope proposal, r–z drawing and review questions](design/DES-003-global-envelopes.md)
- [Envelope study tool and reproduction commands](../tools/envelope_study/README.md)
- [ODD realism assessment](validation/ODD-realism-assessment.md)

- [Realism charter](charter/REALISM_CHARTER.md)
- [Design proposal template](design/TEMPLATE.md)
- [Architecture decision process and register](decisions/README.md)
- [Human sign-off template](signoff/TEMPLATE.md)
- [M0 baseline specification](validation/M0-baseline-specification.md)
- [Validation report template](validation/REPORT_TEMPLATE.md)
- [Project session journal](../logs/README.md)

The [source catalogue](../reference/README.md) records acquisitions and verification
state in `reference/manifest.yaml`. Reading guides cover the initial tracker,
readout and whole-detector papers; DES-003 adds selected calorimeter/muon TDR
passages and PDG evidence. Identity verification or selected-page reading does
not imply a complete document review. Normative claims require precise locators.

## Design lifecycle

`DRAFT -> TECHNICAL REVIEW -> EXPERT REVIEW -> SIGNED OFF -> IMPLEMENTED -> VALIDATED -> ACCEPTED`

Only identified humans may authorize sign-off and acceptance. Approval records must identify the exact reviewed revision and link to approval evidence. A merge alone is not sign-off. Production implementation normally follows design approval in a separate pull request.

## Open M0 decisions

- [ADR-001: upstream baseline](decisions/ADR-001-upstream-baseline.md): repository, revision, import strategy, and licensing.
- [ADR-002: review and sign-off](decisions/ADR-002-review-and-signoff-policy.md): reviewer assignments, minimum reviews, and enforcement.
- [ADR-003: validation and artifacts](decisions/ADR-003-validation-and-artifact-policy.md): gates, tolerances, supported tools, and artifact storage.
- [ADR-004: session logging](decisions/ADR-004-session-logging-and-traceability.md): curated records, accounting, and Git traceability. Infrastructure implementation was explicitly requested by the user.

- [ADR-005: reference reading](decisions/ADR-005-reference-reading-pilot.md): local extraction caches and source reading maps.

The registered ADRs remain drafts. Their proposals do not override existing repository instructions.

## M0 completion evidence

Track completion with linked issues, reviews, and immutable evidence. Required work includes an approved operating model, public source catalogue, pinned upstream baseline, reproducible characterization tools and CI, a reviewed baseline report, repository review protections, and a reproducible baseline tag. None is implied complete by these templates.
