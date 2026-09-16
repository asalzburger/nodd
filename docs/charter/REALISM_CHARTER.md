# Realism charter

- Status: DRAFT
- Created: 2026-09-15
- Human owner: TBD
- Governing documents: [PROJECT.md](../../PROJECT.md), [AGENTS.md](../../AGENTS.md)
- Review issue: TBD

## Purpose and scope

nODD is an experiment-independent, publicly reproducible reference detector for DD4hep full simulation and ACTS-compatible reconstruction studies. Credible modern detector engineering informs its design; reproducing a particular experiment is not its objective.

Realism includes sensors, readout, module assembly, mechanical support, cooling, power and data services, layout, timing, material, sensitive response, and reconstruction compatibility. Each dimension needs explicit assumptions and quantitative validation appropriate to its scope.

## Successor and final report

ODD is the starting point for a new DD4hep detector. Components and code may be
modified, replaced or rewritten through reviewed designs, while preserving the
broad role and recognizable features of the TrackML → ODD successor chain.
Every subsystem, including passive material, electronics, services and magnetic
fields, needs a credible technical basis; a retained upstream value is not
automatically a validated hardware choice.

The intended result could plausibly have been built when judged from simulation
and performance. This is not a certification of detailed engineering buildability
or CAD completeness. Record the assumptions and deferred engineering studies.
A whole-detector TDR is a final deliverable, developed alongside implementation
and evidence. nODD remains a working title. See the
[development plan](../DEVELOPMENT_PLAN.md) for the proposed work and review gates.

## Modeling principles

Include a detail when it affects clearance, material, services, thermal or electrical architecture, sensitive response, reconstruction, or validation. Decorative CAD complexity alone is insufficient justification.

For an omitted or effective representation, document:

- the physical components represented or omitted;
- the quantities preserved, such as mass, composition, thickness, or directional material;
- the normalization procedure, assumptions, and uncertainty;
- the limits of validity and validation method.

Do not adjust geometry or material solely to improve a performance plot. Establish physical rationale and obtain the required design review first.

## Evidence and provenance

Classify each important parameter and claim as exactly one of:

- **FACT:** a public source supports it directly; record the source ID and precise locator.
- **INFERENCE:** record source facts, derivation, assumptions, and uncertainty.
- **NODD DESIGN CHOICE:** record rationale, alternatives, consequences, and human approvers.

Catalogue sources in the planned `reference/manifest.yaml`. Record source versions and explain supersession. Confidential material cannot be the sole normative basis of a public parameter. Large local reference PDFs remain ignored unless redistribution and repository policy explicitly permit committing them.

## Review and validation

Use [design proposals](../design/TEMPLATE.md) for components and [ADRs](../decisions/README.md) for cross-cutting choices. Define measurable acceptance criteria before production implementation. Preserve traceability from sources through design, human approval, code, and validation artifacts.

AI may assist drafting, research, implementation, and validation. It cannot supply human sign-off or acceptance.

## Current boundary

During M0, characterize the selected upstream detector without changing geometry, materials, segmentation, sensitive behavior, or reconstruction configuration. Any later unsigned exploration requires explicit prototype authorization and isolation from production.

## Questions for human review

- Who owns this charter and reviews changes to it?
- Does the scope adequately capture the intended scientific use cases?
- Which reviewer expertise is required for effective representations?
