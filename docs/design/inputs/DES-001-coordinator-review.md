# DES-001 — Project Coordinator assessment

- Status: DRAFT — AI advisory assessment; no human approval or sign-off.
- Date: 2026-09-17.
- Governing proposal and notation: [DES-001](../DES-001-rd53-pixel-modules.md); technology direction [ADR-007](../../decisions/ADR-007-itkpix-pixel-baseline.md), DRAFT.
- Inputs: [compact A1/A2](DES-001-compact-modules.md), [quad B4](DES-001-quad-modules.md), their module schematics and [common stack](../DES-001-module-stack.json).
- Linked issue: [#7](https://github.com/asalzburger/nodd/issues/7); human programme owner and specialist reviewers: TBD.

## Recommendation and scope

**NODD DESIGN CHOICE — proposed; approving humans pending:** use A1 as the first
qualification study and compare A2 with B4 before recommending a coverage module.
A1 tests the minimum sensor–RD53i–flex assembly, bump mapping, bond access, bias
and module electrical termination. Success with A1 would establish useful
component evidence; it would not qualify either shared multi-chip sensor or its
seams. A1 may remain a study unit. A three-type production family is not assumed.

**INFERENCE:** A2 and B4 offer different ways to share sensor edges, flex and
local components across chips. Neither has demonstrated a complete material
budget, qualified manufacture or superior useful coverage. There is consequently
no current coverage winner. Pixel volume remains open; a later layout study can
use qualified module envelopes without treating their nominal readout rectangles
as measured sensitive area.

This assessment covers sensor, RD53i dies, bumps and films, flex and its integral
extensions, adhesives, bonds, bias contact, local passives and module electrical
termination. The boundary ends at that termination and the bare die backs.
Mounting, cooling infrastructure and allocated external-service material are
excluded from both the comparison and its material budget. The current
human-directed module scope supersedes broader interface language in the
original issue; it does not certify later integrated operation.

## Material assumptions and provenance

The claim IDs below refer to DES-001; the [source catalogue](../../../reference/manifest.yaml)
retains the cited public sources and their verification limits.

| Classification | Reviewed input | Meaning and unresolved dependency |
| --- | --- | --- |
| NODD DESIGN CHOICE — proposed | PM3-C02: 150 µm sensor and 150 µm RD53i silicon | Comparative study thicknesses; sensor process, delivered die thinning, handling and qualification remain unverified. |
| NODD DESIGN CHOICE — proposed | PM3-C03: 25 µm polyimide core plus two 12.5 µm coverlay films; two 18 µm copper layers | 50 µm polymer film and 36 µm copper reference totals; actual laminate grade, adhesive layers and routed coverage are pending. |
| NODD DESIGN CHOICE — proposed | PM3-C04–C07: 25 µm flex bondline, 20 µm bump standoff, candidate 25 µm aluminum wires and local electrical components | Nominal geometry is not a measured BOM. Bump alloy, adhesive composition, bond count/loops and component volumes remain unknown. |
| FACT | PM3-F02–F05: silicon, copper, specified polyimide film and aluminum radiation lengths | SRC-PDG-SILICON-2025, SRC-PDG-COPPER-2025, SRC-PDG-POLYIMIDE-2020 and SRC-PDG-ALUMINUM-2025, each Radiation length row. Pure-material tabulations do not characterize an unspecified laminate or filled adhesive. |
| INFERENCE | PM3-I02: 0.5884% X₀ partial local reference subtotal | Sum of the proposed silicon, polyimide and both copper layers at normal full crossing; not a completed-module budget, area average or bound. |

**INFERENCE:** the stored unrounded subtotal, 0.5883680116112957% X₀, agrees
with `100 × thickness_um / (1000 × X₀_mm)` summed over the four known entries.
Its equality across alternatives follows from their common nominal stack and
cannot rank their materials. Actual copper crossing depends on traces; glue,
metallization/passivation, laminate adhesives, bump metallurgy, wires, passives
and termination contribute additional spatially varying material. Unknown
entries are not zero. A bump standoff or wire diameter is not equivalent metal
thickness. A physical interchip gap also does not remove the shared sensor
silicon above it.

**NODD DESIGN CHOICE — proposed; approving humans pending:** compare a completed
module BOM and spatial material map for each alternative, reporting the chosen
reference area explicitly. Keep nominal readout-area normalization separate
from measured efficient-area normalization. Include all integral flex extensions
and termination parts even when outside the sensor projection. Directional
material requires actual intersections; a slab sum alone cannot represent
oblique rays or peripheral components.

## Balanced module comparison

All comparative entries are **INFERENCE**, conditional on the draft layouts and
unresolved interface, sensor, routing and assembly evidence.

| Criterion | A1 / A2 | B4 | Evidence needed to decide |
| --- | --- | --- | --- |
| Reusable assemblies and few types | A1 is the smallest learning unit; A2 needs a distinct shared sensor, seam mapping and flex. | Four chips share a larger sensor and flex; common parts may reduce repeated module interfaces. | Shared/variant part inventory and qualification effort; justify each retained production type. |
| Module material | Smaller units can simplify local routing, but repeat sensor edges and terminations more often per nominal readout area. | Shared edges and components may amortize overhead, while additional routing and local parts can offset savings. | Routed copper, all constituent volumes, inactive-area maps and the same normalization convention. |
| Credible assembly | Smaller sensor/hybrid handling unit; A2 still adds multi-die alignment and a seam. | Larger shared hybrid with more die placements, seam intersections and bond access to establish. | Supplier-compatible bump/pad drawings, assembly sequence, metrology and defect maps. |
| Electrical operation | Fewer chip links per module; A2 must qualify shared current paths and grounding. | More links and current paths in one flex; local fault effects may span more readout area. | Pinout, HV separation, voltage drop, signal integrity, configuration and partial-operation tests. |
| Yield and rejected area | Less nominal area per rejected assembly; more assemblies for equal nominal readout area. | Fewer assemblies, but a sensor/flex or correlated assembly defect can affect more nominal area. | Accepted-area yield with correlated defects, rework and partial operation defined; independent-die probabilities alone are inadequate. |
| Coverage information available now | PM3-I01 gives A1 384 mm² and A2 768 mm² nominal readout area. | PM3-I01 gives B4 1536 mm² nominal readout area. | Sensor-edge and seam response plus finished-module envelope; later pixel-volume work determines deployment suitability. |

No row establishes manufacturing certification, operating lifetime or placement
suitability. Nominal chip area and chip-only spans are bookkeeping derived from
PM3-F01 (SRC-RD53-OVERVIEW-2023, slide 5 / physical PDF5); they are not finished
sensor dimensions, assembly tolerances or efficient-area measurements.

## Next evidence and human review

**NODD DESIGN CHOICE — proposed; approving humans pending:** advance the module
comparison through these evidence gates, with numerical acceptance criteria
assigned by human specialists before qualification:

1. Confirm delivered RD53i thickness and authoritative die, bump, pad and
   electrical-interface information. Audit the proposed sensor mapping and bias
   arrangement without inferring interfaces from the overview dimensions.
2. Produce dimensioned sensor/die/flex/bond envelopes and assembly access,
   including sensor margins, seams, routing and termination. Check that backside
   flex tabs can actually reach chip pads without obscuring required bond access.
3. Complete constituent composition, thickness/volume and spatial material
   accounting, including unresolved films and localized parts. Review sensitivity
   to the proposed thinning and flex hypotheses before claiming material savings.
4. Obtain module-level electrical, hybridization, dimensional and sensor-response
   evidence, with assembly stress and irradiation conditions tied to explicit
   operating requirements. Assess accepted-area yield and defined fault behavior.
5. Recommend the minimum justified module family from that evidence; preserve
   final deployment selection for the separate pixel-volume/layout decision.

The rewritten A3-* compact and B-C20–B-C25 quad proposals and their SVG source
structure were checked against the common stack and scope. Both retain unresolved
sensor edges, pad access, seams and routing; their shared nominal stack supports
a controlled comparison, but supplies no completed-module material ranking.

This is a documentary design assessment. The common-stack arithmetic was
recomputed successfully; no hardware, irradiation, manufacturing-yield or
DD4hep/Geant4 validation was performed. Schematics remain conceptual and cannot
certify dimensions or bondability. Human technical/domain review, exact-revision
sign-off and separate production implementation authorization remain pending.
