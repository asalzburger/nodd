# ADR-003 — Validation and artifact policy

- Status: DRAFT
- Created: 2026-09-15
- Human owner: TBD
- Issue: TBD
- Supersedes / superseded by: None
- Human approval evidence: Pending

## Context and evidence

[AGENTS.md](../../AGENTS.md) requires reproducible validation metadata and reviewed baseline changes. [PROJECT.md](../../PROJECT.md) lists characterization and integration gates. Tool versions, quantitative tolerances, artifact storage, and CI resource limits are not yet selected.

## Options

| Option | Benefits | Costs and risks |
| --- | --- | --- |
| Store all artifacts in Git | Direct version association | Large binary outputs can make repository history impractical |
| Store small summaries in Git and large artifacts in durable external storage | Keeps reviewable results alongside code | Requires retention, access, integrity, and recovery policy |
| Retain only transient CI outputs | Simple initial operation | Expiration can make accepted evidence unrecoverable |

## Proposed decision

**NODD DESIGN CHOICE — pending human approval:** keep specifications, compact result summaries, and artifact manifests in Git; retain large results in durable storage selected by maintainers. Transient CI output alone should not be the retained evidence for an accepted baseline.

Each report should identify project and upstream full commit SHAs, working-tree changes, configuration and input hashes, tool/build versions, environment, seeds where relevant, exact commands, units, tolerances, and exit status. Each external artifact should have a stable location, SHA-256, size, format, and generating check ID.

Define tolerances before acceptance decisions, with physical or numerical justification and identified human review. Missing tolerances prevent a pass/fail acceptance claim; measurements may still be reported as characterization. Do not invent thresholds or relax them to obtain passing results.

## Gates and baseline changes

Use the [M0 specification](../validation/M0-baseline-specification.md) to establish construction, overlap, count, material, acceptance, identifier, simulation, and ACTS checks. State applicability and limitations explicitly.

Preserve prior evidence when changing a baseline. Link the governing reviewed amendment or ADR, old and new revisions, comparison results, and human approval. Test failures alone never authorize reference regeneration.

## Verification and implementation

After approval, implement report metadata checks, integrity verification for retained artifacts, and CI entry points. Demonstrate reproduction from a fresh checkout using the supported version matrix. No tooling, storage service, or CI gate is implemented by this proposal.

## Open questions and human review

- Which DD4hep, Geant4, ACTS, compiler, and platform versions are supported?
- What tolerances, sampling grids, and seeds are justified for each check?
- Which checks run per PR, on schedule, and for release review?
- Where are large artifacts retained, for how long, and by whom?
- What evidence is required to review known upstream defects or unavailable checks?

Reviewer assignments, reviewed revision, review date, outcome, and approval evidence: **pending**.
