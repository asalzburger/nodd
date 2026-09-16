# nODD documentation

## Current phase

**M0 — Baseline and Governance.** Production detector changes are prohibited until M0 is explicitly completed. The repository is the canonical record; see [repository instructions](../AGENTS.md) and [project scope](../PROJECT.md).

The documents below establish proposals and recording formats. Their presence does not constitute human approval or completion of M0.

## Index

- [Realism charter](charter/REALISM_CHARTER.md)
- [Design proposal template](design/TEMPLATE.md)
- [Architecture decision process and register](decisions/README.md)
- [Human sign-off template](signoff/TEMPLATE.md)
- [M0 baseline specification](validation/M0-baseline-specification.md)
- [Validation report template](validation/REPORT_TEMPLATE.md)
- [Project session journal](../logs/README.md)

The [source catalogue](../reference/README.md) now records the initial PDF acquisitions in `reference/manifest.yaml`. Five documents—the ATLAS Pixel TDR, CMS Tracker TDR, RD53A manual and ATLAS/CMS JINST overviews—now have verified identity metadata and reading guides; other entries remain pending. Normative source claims require verified catalogue entries and precise locators.

## Design lifecycle

`DRAFT -> TECHNICAL REVIEW -> EXPERT REVIEW -> SIGNED OFF -> IMPLEMENTED -> VALIDATED -> ACCEPTED`

Only identified humans may authorize sign-off and acceptance. Approval records must identify the exact reviewed revision and link to approval evidence. A merge alone is not sign-off. Production implementation normally follows design approval in a separate pull request.

## Open M0 decisions

- [ADR-001: upstream baseline](decisions/ADR-001-upstream-baseline.md): repository, revision, import strategy, and licensing.
- [ADR-002: review and sign-off](decisions/ADR-002-review-and-signoff-policy.md): reviewer assignments, minimum reviews, and enforcement.
- [ADR-003: validation and artifacts](decisions/ADR-003-validation-and-artifact-policy.md): gates, tolerances, supported tools, and artifact storage.
- [ADR-004: session logging](decisions/ADR-004-session-logging-and-traceability.md): curated records, accounting, and Git traceability. Infrastructure implementation was explicitly requested by the user.

- [ADR-005: reference reading](decisions/ADR-005-reference-reading-pilot.md): local extraction caches and source reading maps.

All five ADRs are drafts. Their proposals do not override existing repository instructions.

## M0 completion evidence

Track completion with linked issues, reviews, and immutable evidence. Required work includes an approved operating model, public source catalogue, pinned upstream baseline, reproducible characterization tools and CI, a reviewed baseline report, repository review protections, and a reproducible baseline tag. None is implied complete by these templates.
