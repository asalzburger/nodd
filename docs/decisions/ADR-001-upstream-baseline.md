# ADR-001 — Upstream baseline and import strategy

- Status: DRAFT
- Created: 2026-09-15
- Human owner: TBD
- Issue: TBD
- Supersedes / superseded by: None
- Human approval evidence: Pending

## Context and evidence

[PROJECT.md](../../PROJECT.md) requires selection and pinning of an ODD baseline before characterization. This draft records import options; it does not select a repository, revision, or strategy. An initial [resource inspection](../../reference/guides/ODD-resources.md) now identifies the public ODD repository and its MPL-2.0 license, with source ID SRC-ODD-UPSTREAM. The recorded study revision is not a selected baseline.

## Options

| Option | Benefits | Costs and risks |
| --- | --- | --- |
| Fork | Retains upstream history and supports direct upstream comparison | Requires a policy for carrying nODD changes and synchronizing upstream |
| Subtree | Keeps upstream files in a self-contained checkout | Requires documented import/update commands and history policy |
| Submodule | Records an explicit upstream commit separately | Requires recursive checkout and availability of the upstream object |
| Curated import | Allows a deliberately limited set of files | Requires explicit file mapping, attribution, and evidence of completeness |

These are engineering tradeoffs for review, not an approved selection.

## Proposed decision

**NODD DESIGN CHOICE — pending human approval:** identify the upstream with a public repository URL and full commit SHA; record the import procedure, licenses, local modifications, and corresponding source-catalogue entry. Preserve a recoverable upstream state for comparison.

The import strategy and exact baseline remain unresolved. A tag or branch name alone is insufficient as the recorded revision.

## Required selection record

| Field | Value |
| --- | --- |
| Public upstream repository | TBD |
| Full upstream commit SHA | TBD |
| Release/tag, if applicable | TBD |
| Source catalogue ID | TBD |
| Import strategy and reproducible commands | TBD |
| License files and redistribution obligations | Study checkout LICENSE: MPL-2.0; selected import obligations pending review |
| Selected detector entry point and required assets | TBD |
| Local modifications | To be inventoried at import |
| DD4hep / Geant4 / ACTS versions | TBD; coordinate with ADR-003 |

## Consequences and verification

Demonstrate that a fresh checkout can reproduce the selected source state and locate all required assets. Record checksums for copied archives where applicable. Review licensing before redistribution. Run the [baseline specification](../validation/M0-baseline-specification.md) without production detector changes and retain the import revision in every report.

## Open questions and human review

- Which upstream repository and revision will govern M0?
- Which import strategy best fits maintenance and distribution?
- Who reviews licensing, import completeness, and reproducibility?
- What baseline tag naming and retention policy should be used?

Reviewer assignments, reviewed revision, review date, outcome, and approval evidence: **pending**.
