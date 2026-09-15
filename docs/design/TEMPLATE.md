# DES-NNN — <short title>

- Status: DRAFT
- Created: <YYYY-MM-DD>
- Updated: <YYYY-MM-DD>
- Author: <name; identify AI assistance where applicable>
- Human owner: <TBD>
- Issue: <TBD>
- Governing ADRs: <IDs and repository-relative links, or none>
- Sign-off record: <pending>
- Implementation PR: <pending>
- Validation evidence: <pending>

Copy this template to `DES-NNN-short-name.md`. Allocate a unique ID by inspecting existing documents and open work. Keep unresolved entries explicit. No template field constitutes approval.

## Scope and exclusions

<Describe the component, intended use, interfaces, and exclusions. State whether this is a design proposal or an explicitly authorized isolated PROTOTYPE. Production integration is prohibited during M0.>

## Requirements and acceptance criteria

| Requirement ID | Requirement and rationale | Provenance classification / claim ID | Measurement | Acceptance criterion and justification |
| --- | --- | --- | --- | --- |
| <ID> | <requirement> | <exactly one classification> | <method> | <value with units or explicitly unresolved> |

## Sources

Reference entries in `reference/manifest.yaml` once available. Include precise locators and versions; explain conflicting or superseded evidence.

| Source ID | Public reference and version | Locator | Claims supported |
| --- | --- | --- | --- |
| <ID> | <reference> | <page/section/table/figure/record> | <claim IDs> |

## Sourced facts

| Claim ID | Classification | Fact / value and units | Source ID and locator |
| --- | --- | --- | --- |
| <ID> | FACT | <statement> | <source and locator> |

## Inferences and uncertainties

| Claim ID | Classification | Result and units | Input claim IDs | Derivation and assumptions | Uncertainty / validity |
| --- | --- | --- | --- | --- | --- |
| <ID> | INFERENCE | <result> | <IDs> | <derivation> | <uncertainty> |

## Proposed nODD choices

| Claim ID | Classification | Proposed choice | Rationale and alternatives | Consequences | Human approvers / evidence |
| --- | --- | --- | --- | --- | --- |
| <ID> | NODD DESIGN CHOICE | <choice> | <rationale> | <consequences> | Pending |

## Dimensions, materials, interfaces, and identifiers

<List named parameters with SI/DD4hep units and provenance claim IDs. Define coordinate conventions, transforms, clearances, sensitive/passive boundaries, segmentation, and stable identifiers as applicable. No unexplained numbers.>

<For effective materials, specify composition, density, represented components, preserved quantities, normalization, and validation.>

## Material budget and acceptance implications

<Expected mass, radiation/interaction lengths, crossings, and coverage effects, with uncertainty. Distinguish predictions from measured results.>

## Alternatives considered

<Compare credible alternatives and explain the proposed selection.>

## Risks and open questions

| Question or risk | Impact | Owner | Resolution needed before |
| --- | --- | --- | --- |
| <item> | <impact> | TBD | <review/implementation stage> |

## Validation plan

<Map requirements to commands or planned tools, inputs, outputs, tolerances and their rationale. Consider construction, overlaps, counts/transforms, dimensions, mass/material, acceptance, identifiers, Geant4, ACTS, and regression evidence. Justify exclusions. Record revisions, versions, configuration, seeds, and commands in results.>

## Review and implementation tracking

| Role | Assigned human | Review scope | Evidence |
| --- | --- | --- | --- |
| Technical reviewer | TBD | <scope> | Pending |
| Domain expert | TBD | <scope> | Pending |
| Approver | TBD | <scope> | Pending |
| Validation reviewer | TBD | <scope> | Pending |

Use the [sign-off template](../signoff/TEMPLATE.md) for human approval of an exact revision. Design approval and production implementation normally require separate PRs. AI must not record human sign-off or advance this document to `SIGNED OFF` or `ACCEPTED`.
