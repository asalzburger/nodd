# ADR-007 — ITkPix pixel-module baseline

- Status: DRAFT; created / updated: 2026-09-17.
- Human owner: TBD; author: AI-assisted project coordination.
- Issue: [#7](https://github.com/asalzburger/nodd/issues/7).
- Related: [DES-001](../design/DES-001-rd53-pixel-modules.md), [ADR-006](ADR-006-global-envelope-and-field-hypotheses.md).
- Supersedes / superseded by: none. Replaces the unspecified-chip working assumption in DES-001, not an accepted design.
- Human approval evidence for an exact design revision: pending.

## Context

On 2026-09-17, after discussing RD53A, ITkPix and CROC consequences, the user
instructed: “Let's take ITkPix then”. This selects the chip family for design
work; it neither certifies the physical inventory nor signs off DES-001.
An ADR records the technology direction because it affects sensors, module
footprints, services, assembly and response modelling.

## Evidence and provenance

**FACT — SRC-RD53-OVERVIEW-2023**, slide 5 / physical PDF5: ITkPix v1 and
v1.1 belong to RD53B; v2 belongs to RD53C. The overview lists the ATLAS matrix
as 400 × 384 with 50 µm chip-cell pitch and an approximate 20 × 21 mm die.
The [source catalogue](../../reference/manifest.yaml) records selected-page
verification. These overview values are not a certified stock drawing or
revision-specific operating limits.

**INFERENCE:** pixel count times pitch gives a nominal 20.0 × 19.2 mm matrix
rectangle, or 384 mm² per chip. With identical cells, two and four chips provide
768 and 1536 mm² of nominal readout footprint. This counts readout cells, not
measured sensitive efficiency or seamless installed coverage. Guard structures,
seams, chip gaps and services require explicit spatial accounting.

## Options

Comparative judgments are **INFERENCE**; procurement and engineering evidence
are incomplete.

| Option | Benefit | Cost / limitation |
| --- | --- | --- |
| RD53A | Smaller demonstrator with public module-assembly experience | More chips for comparable matrix area; mixed front-end regions; not selected |
| ITkPix | Selected larger-area family; supports common high-area hybrid study | Larger rigid footprint; revision-specific mask, pad, power and response evidence needed |
| CROC | Alternative larger-area family and aspect ratio | Different chip/interface qualification; not selected |

## Design direction

**NODD DESIGN CHOICE — human-directed investigation:** use ITkPix for the nODD
pixel-module design baseline. Exact revision remains TBD. Do not silently
interpret the family selection as ITkPix v2 procurement, verified stock or full
design approval. Compare compact and quad modules around the selected family;
continue experiment-independent sensor, support and placement design.

## Consequences and validation

**INFERENCE:** changing the working chip changes sensor bump mapping, die and
bond-access envelopes, flex routing, thermal contacts, load budgets and
readout/calibration support. RD53A examples remain historical evidence and must
not govern ITkPix manufacturing or operating parameters. The larger footprint
can alter the compact/quad tradeoff; no material saving is established.

Review DES-001 and its drawings for consistent chip identity and arithmetic.
Before dimensional freeze obtain the exact revision manual, mechanical/pad
and bump drawings, thinning and qualification evidence. Before family selection,
compare occupied-envelope coverage and full spatial BOM/service/thermal accounts.
Production implementation follows separate human design review and sign-off.

## Open questions

- Tracking Engineer and human inventory owner: exact ITkPix revision, available
  stock, die thickness and authoritative interface dossier.
- Coordinator and tracking/physics: host volume, radiation/rate/lifetime and
  useful coverage requirements.
- Sensor/electrical/mechanical specialists: compatible sensor process, load,
  isolation, assembly and cooling interfaces with explicit tolerances.

## Human review

| Role | Assigned human | Exact revision | Date | Outcome | Evidence |
| --- | --- | --- | --- | --- | --- |
| Technology/design reviewer | TBD | Pending | — | Pending | Pending |

Only identified humans may authorize sign-off or acceptance. This DRAFT records
an investigation direction; it does not approve detector integration.
