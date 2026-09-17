# DES-001 — Project Coordinator assessment

- Status: DRAFT; AI advisory assessment, no human approval or sign-off.
- Date: 2026-09-17.
- Governing proposal: [DES-001](../DES-001-rd53-pixel-modules.md); issue [#7](https://github.com/asalzburger/nodd/issues/7).
- Inputs: [compact A](DES-001-compact-modules.md), [quad B](DES-001-quad-modules.md), and their linked original schematic drawings.
- Technology direction: [ADR-007](../../decisions/ADR-007-itkpix-pixel-baseline.md), DRAFT; ITkPix selected, exact revision pending.
- Human programme owner and technical approvers: pending.

## Recommendation

**NODD DESIGN CHOICE — proposed; approving humans pending:** use the single-chip
A1 as the first **PROTOTYPE qualification study**, and develop quad B in parallel
as the reusable high-area coverage candidate. This sets an order for learning,
not a final production module selection. A1 is the smallest unit that exercises
the selected ITkPix chip, bump mapping, sensor, bond access, flex, thermal contact and
assembly/test chain. Quad feasibility should be studied early enough that the
small demonstrator does not dictate a material-heavy full detector.

**NODD DESIGN CHOICE — proposed; approving humans pending:** do not freeze an
A1/A2/B three-type production family. Initially compare B as the sole coverage
module against a B-plus-compact family. Retain A2 as a documented alternative;
introduce it as a production type only if it improves coverage or total material
against both A1 and B sufficiently to justify another sensor/flex/BOM and its
qualification. A1 may remain only a test vehicle if the eventual volume and
operating requirements permit B throughout.

**INFERENCE:** neither input demonstrates a numerical material advantage or
measured nODD assembly yield. A larger hybrid can reduce repeated interfaces,
but routing, stiffness, overlap, rejected area and cooling can consume that
saving. Smaller modules can fit constrained regions, but additional tails,
perimeters and service/support allocations can increase installed material.
The correct selection therefore depends on occupied-envelope tiling and a
complete, spatially resolved bill of material at common operating conditions.

## Reassessment after the ITkPix family selection

The initial recommendation above was formed when the RD53 variant was unspecified.
The user subsequently selected ITkPix, recorded as an investigation direction in
DRAFT ADR-007. The following reassessment retains the qualification sequence but
reopens the eventual coverage-family choice around its larger nominal footprint.

**INFERENCE — DES-001 PM-I10–I12, from SRC-RD53-OVERVIEW-2023 slide5:**
one ITkPix matrix has nominal readout area 384 mm², equal to two historical
RD53A matrices. A2 and B provide 768 and 1536 mm² respectively. Their approximate
chip-only envelopes are 40 × 21 mm and 40 × 42 mm, before gaps, guard structures,
bond/service margins and tolerances. These are readout arithmetic and nominal die
bookkeeping, not measured sensitive coverage or certified module dimensions.

**NODD DESIGN CHOICE — proposed; approving humans pending:** retain A1 as the
first qualification study because it still exercises the minimum one-chip
assembly and interfaces, while providing substantially more nominal area than
the earlier benchmark. Retain B as a high-area candidate; its greater transverse
span makes its fit and support assumptions more consequential. Study A2 early
as a possible intermediate coverage module: it could fit regions that exclude
the quad while sharing interfaces over more area than A1. This remains a hypothesis,
not a reason to manufacture all three types.

**INFERENCE:** the greater ITkPix area per die strengthens the possibility that
A1 or A2 provides adequate coverage with acceptable interface overhead. It also
increases the quad's shared sensor area and rigid span; the older RD53A quad
precedent cannot establish its yield, flatness, thermal or curvature feasibility.
A2 can trade one shorter span against an additional chip, seam and routing burden.
No lower material or better accepted-area yield follows from these dimensions alone.

**NODD DESIGN CHOICE — proposed; approving humans pending:** compare A2-only
and B-only coverage families as well as B plus a compact type, and A1-only where
its service overhead is competitive. A2 may replace B as the common coverage
module if occupied-envelope and full installed-material studies favor it.
Use representative host studies to eliminate unnecessary variants, rather than
assuming the quad remains the default after the chip-family change.

## Balanced assessment

All comparative judgments below are **INFERENCE**, conditional on the proposed
layouts and the unresolved exact ITkPix revision, stock qualification, host volume
and engineering processes.
They are not hardware qualification results.

| Criterion | Compact A1 / optional A2 | Quad B | Deciding evidence |
| --- | --- | --- | --- |
| Reusable structures and few types | Small common chip/interface building block; A2 creates a distinct shared sensor and flex. | One repeated high-area hybrid can reduce assembly count; different support placements need not imply different sensors. | Family inventory with explicit shared and variant parts; compare achievable coverage before adding a type. |
| Material | Shorter local spans and smaller units; more boundaries and repeated tails per area. | Potentially amortizes edges, local parts and service landings; larger routing and support remain real material. | Patterned BOM and allocated services, including overlap and dead regions, per useful host area and directional X/X0. |
| Realistic assembly | Smaller qualification and replacement unit; A2 still requires custom seam mapping and multi-die assembly. | Published RD53A quad assembly supports plausibility, but does not establish this stock chip's compatibility or nODD process yield. | Chip drawing, supplier bump/sensor process, metrology, wire-bond access and electrical/thermal-cycle qualification. |
| Coverage | More adaptable to tight curvature, narrow chords or irregular boundaries. | Efficient repeated large-area footprint where the occupied corners, bonds and tails fit. | Representative barrel and disk tilings using the actual envelope and inactive-area maps. |
| Thermal and electrical operation | Smaller per-unit heat load; more distributed interfaces and possible service duplication. | Higher total load per assembly; chip contacts, routing and fault isolation must support it. | Same channel activity, leakage and coolant boundary conditions; worst-mode losses, hotspots, voltage drops and fault transients. |
| Failure and maintenance | Less area discarded per rejected unit; more units to assemble, connect and service. | Fewer units; a shared sensor/flex fault can affect more area, and partial operation must be defined. | Accepted-area yield and repair/access study, with correlated defects and rework explicitly treated. |

## Evidence and selection gates

**FACT — SRC-RD53-OVERVIEW-2023:** slide 5 / PDF5 lists ITkPix v1/v1.1
under RD53B and v2 under RD53C, with 400 × 384 chip pixels at 50 × 50 µm pitch
and approximately 20 × 21 mm chip dimensions. The selected family is ITkPix;
exact revision, supplied thinning, stock qualification and procurement drawing
remain gates before dimensional or sensor-mask freeze. No RD53A pad, supply,
power or qualification limit transfers to this interface.

**FACT — SRC-RD53A:** v3.51 abstract/PDF1 and Figure 1/PDF5 state
20.0 mm × 11.6 mm, whereas the CDS abstract states 11.8 mm. This retained
historical discrepancy concerns the superseded RD53A benchmark; it is not an
active ITkPix dimensional blocker or a tolerance allowance.

**FACT — SRC-RD53A-MODULE-ASSEMBLY-2022:** §1–3/PDF2–7 document
RD53A quad hybrid assembly, flex attachment, metrology, bonding and testing.
That precedent makes B credible to investigate; its sensor dimensions, material
stack, yield or experiment layout are not inherited as nODD requirements.

**NODD DESIGN CHOICE — proposed; approving humans pending:** require the following
selection dossier before recommending a final module family:

1. Exact inventory/interface audit and reconciliation of mechanical dimensions;
   defined pixel volume, fluence/lifetime, rate, bias and thermal requirements.
2. Dimensioned sensor/die/flex/bond/keep-out layouts and actual inactive/seam maps;
   consistent placement in representative host regions.
3. Full material and electrical/thermal accounting, including DES-002 shared
   support/cooling and external service allocations at equal useful coverage.
4. Manufacturing and accepted-area yield assessment, fault/repair strategy and
   planned qualification criteria reviewed by identified human specialists.

The final recommendation should favor the smallest number of module types that
meets these gates. If one candidate fits and qualifies everywhere with lower installed
material, prefer that single-type family. If constrained or demanding regions make B unsuitable,
retain a compact type with a documented regional need. If neither layout meets
the requirements, amend the proposal rather than concealing dead regions,
thermal weaknesses or service costs.

## Review limitations and consistency check

This assessment reviewed the draft text and SVG source structure. The drawings
are conceptual and not to scale; they establish neither assembly tolerance nor
coverage, material budget, thermal performance or manufacturability. No geometry,
hardware, irradiation, thermal or production-yield tests were run for this review.
TDR reading-map passages remain review leads where the design inputs do not
claim newly verified numerical facts.

The compact cross-section now identifies its lateral flex as a bond-access
tab of the proposed sensor-backside flex, with routing pending. Detailed design
must preserve the separate chip-back thermal contact. Both alternatives need dimensioned service-tail,
strain-relief and connector/splice routing before the coverage comparison.

This advice does not close M0, authorize production geometry, approve DES-001,
or advance its lifecycle state. Human technical and domain review, an exact
revision sign-off record and separate implementation authorization remain pending.
