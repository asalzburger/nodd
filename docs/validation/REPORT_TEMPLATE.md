# <validation report ID> — <title>

- Report status: DRAFT
- Created: <YYYY-MM-DD>
- Author: <name; identify AI assistance where applicable>
- Human reviewer: TBD
- Specification / design / ADR IDs and links: <references>
- Issue / PR: <references>
- Execution time span (UTC): <timestamps or not run>

Copy this template only when preparing an actual report. Placeholder entries are not results.

## Scope and summary

<What was measured, why, principal findings, and limitations. Distinguish characterization from acceptance.>

## Source and environment

| Field | Recorded value |
| --- | --- |
| Project full commit SHA and branch | <value> |
| Dirty-tree state and retained changes | <clean, or patch/inventory reference> |
| Upstream public repository and full commit SHA | <value> |
| Source catalogue IDs | <IDs> |
| Detector entry point / required assets | <paths and versions> |
| OS / architecture / compiler | <versions> |
| DD4hep / ROOT / Geant4 / ACTS | <versions; explain not applicable> |
| Other dependencies / environment image | <versions or digest> |
| Build options and environment setup | <commands/configuration reference> |
| Input and configuration hashes | <SHA-256 and artifact reference> |
| Seeds / sampling / units | <values or justified not applicable> |
| Tolerances and approval references | <values with rationale, or unresolved> |

## Commands and execution

| Check ID | Working directory | Exact command or retained script plus invocation | Start/end UTC | Exit code | Log |
| --- | --- | --- | --- | --- | --- |
| <ID> | <directory> | <command> | <timestamps> | <actual code or not run> | <artifact> |

Record required setup and input acquisition so another person can reproduce the run. Do not include secrets or private URLs.

## Results

Execution statuses: `COMPLETED`, `FAILED`, `NOT RUN`, `BLOCKED`, `NOT APPLICABLE`. Acceptance statuses: `PASS`, `FAIL`, `UNASSESSED`, `NOT APPLICABLE`.

| Check / requirement ID | Execution status | Measurement and uncertainty | Criterion / tolerance | Acceptance status | Evidence and explanation |
| --- | --- | --- | --- | --- | --- |
| <ID> | NOT RUN | — | <defined criterion or unresolved> | UNASSESSED | <reason> |

Never mark a check passed solely because its command exited successfully. Explain omissions, unavailable dependencies, and unresolved criteria.

## Artifact manifest

| Artifact ID | Generating check ID | Repository path or durable public location | Format | Size (bytes) | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| <ID> | <ID> | <location> | <format> | <size> | <hash> |

Storage and retention policy: <reference or unresolved>. Keep large artifacts out of Git pending an approved storage policy.

## Comparison and provenance

<Identify the prior approved reference revision and artifacts, or state that this is the initial baseline with no approved reference. Quantify differences. Link governing design amendments and human review for intentional changes. Preserve earlier evidence.>

<List sources added or changed, derived quantities and assumptions, and provenance limitations.>

## Limitations and follow-up

| Limitation / unresolved finding | Impact | Follow-up issue | Owner |
| --- | --- | --- | --- |
| <item> | <impact> | <issue or TBD> | TBD |

## Human review

- Exact report revision reviewed:
- Reviewer name and role:
- Review date (YYYY-MM-DD):
- Outcome and conditions:
- Evidence link:

Leave these fields for human review. A generated report is not baseline acceptance or M0 sign-off.
