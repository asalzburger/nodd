# ADR-007 — RD53i pixel-module baseline

- Status: DRAFT; created / updated: 2026-09-17.
- Human owner: TBD; author: AI-assisted project coordination.
- Issue [#7](https://github.com/asalzburger/nodd/issues/7); draft [PR #8](https://github.com/asalzburger/nodd/pull/8).
- Related: [DES-001](../design/DES-001-rd53-pixel-modules.md), [ADR-006](ADR-006-global-envelope-and-field-hypotheses.md).
- Supersedes / superseded by: none; amends an unapproved working proposal.
- Human approval of an exact full design revision: pending.

## Context and notation

The user selected the chip family and revision on 2026-09-17 and subsequently
requested one consistent shorthand and module-only proposals. Use **RD53i** as
defined once in the [DES-001 glossary](../design/DES-001-rd53-pixel-modules.md#glossary).
The family/revision question is resolved; module qualification is not implied.
Prior choices and source-specific benchmark text remain traceable in Git history.

## Evidence and provenance

**FACT — SRC-RD53-OVERVIEW-2023**, slide5/PDF5: the selected revision is in the
RD53C generation; the ATLAS column lists 400 × 384 cells, 50 µm chip-cell pitch
and approximately 20 × 21 mm die dimensions. These overview values are not
procurement tolerances or certified operating limits. Source identity and
verification are in the [catalogue](../../reference/manifest.yaml).

**INFERENCE:** count times pitch yields 384 mm² nominal readout footprint per
chip, 768 mm² for two and 1536 mm² for four. Guard/seam response, gaps and module
termination do not follow from this arithmetic. The larger assembly can amortize
repeated module components but does not establish a material advantage.

## Options

Comparative assessments are **INFERENCE**, with incomplete qualification evidence.

| Chip option | Benefit | Limitation / direction |
| --- | --- | --- |
| RD53A demonstrator | Smaller chip and historical assembly studies | Mixed front ends; superseded benchmark, not current baseline |
| RD53i | User-selected larger chip with a fixed revision | Exact interface/thinning/qualification evidence still required |
| CMS successor | Alternative larger-chip shape | Different interface qualification; not selected |

## Design direction

**NODD DESIGN CHOICE — human-directed investigation:** use RD53i unchanged for
module design. This direction does not certify delivered stock or full module
approval. Redo compact and quad alternatives around a common proposed module
stack and component material account. Limit scope to sensor, chips, interconnect,
flex/adhesion, wire bonds, bias contact, local parts and module termination.
Mounting/cooling infrastructure and external distribution are excluded; the
boundary stops at electrical termination and bare die backs.

**NODD DESIGN CHOICE — proposed; approving humans pending:** study the nominal
thicknesses in [DES-001](../design/DES-001-rd53-pixel-modules.md) and its common
stack record. They are design-study values, not measured stock or vendor claims.
Unknown compositions and missing component layers remain explicit; a partial
local radiation-length subtotal must not be labeled a complete module budget.

## Consequences and validation

RD53i fixes the chip input for sensor mapping, bond access, module flex and
readout/configuration work. Before freeze obtain authoritative drawings and
load/interface evidence. Compare module outlines, routed material and qualified
assembly, keeping pixel volume deliberately open. Do not select detector placement
or complete infrastructure in this component task. Human design review and
sign-off precede a separate production implementation.

## Open questions and human review

Human inventory owner, sensor/electrical/material specialists and approvers are
unassigned. Delivered thickness, film/bump stacks, flex/adhesive grades, seams,
local BOM, operating requirements and qualification remain unresolved. Pixel
volume belongs to a later layout decision. No AI assessment grants approval;
this ADR remains DRAFT and exact full-design human review evidence is pending.
