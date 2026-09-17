# DES-001 — Project Coordinator assessment

- Status: DRAFT; AI advisory assessment, no human approval or sign-off.
- Date: 2026-09-17.
- Governing proposal: [DES-001](../DES-001-rd53-pixel-modules.md); issue [#7](https://github.com/asalzburger/nodd/issues/7).
- Inputs: [compact A](DES-001-compact-modules.md), [quad B](DES-001-quad-modules.md), and their linked original schematic drawings.
- Human programme owner and technical approvers: pending.

## Recommendation

**NODD DESIGN CHOICE — proposed; approving humans pending:** use the single-chip
A1 as the first **PROTOTYPE qualification study**, and develop quad B in parallel
as the reusable high-area coverage candidate. This sets an order for learning,
not a final production module selection. A1 is the smallest unit that exercises
the existing chip, bump mapping, sensor, bond access, flex, thermal contact and
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

## Balanced assessment

All comparative judgments below are **INFERENCE**, conditional on the proposed
layouts and the unresolved stock chip, host volume and engineering processes.
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

**FACT — SRC-RD53A:** v3.51 abstract/PDF1 and Figure 1/PDF5 state a
20.0 mm × 11.6 mm die; §2/PDF6 describes the matrix and bottom-edge bond access.
These are source-version facts, not stock identification. The CDS abstract's
11.8 mm height is an unresolved discrepancy, not a tolerance allowance.
The exact RD53 variant, revision, supplied thinning and procurement drawing
must be established before dimensional or sensor-mask freeze. No recommendation
here authorizes replacing the chip in hand with another RD53-family device.

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
meets these gates. If B fits and qualifies everywhere with lower installed
material, select B alone. If constrained or demanding regions make B unsuitable,
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

The compact cross-section's lateral flex should be identified as a bond-access
tab of the sensor-backside flex, or retained as an explicit alternate routing
concept. It must not obscure the main proposal's sensor-backside attachment or
chip-back thermal contact. Both alternatives need dimensioned service-tail,
strain-relief and connector/splice routing before the coverage comparison.

This advice does not close M0, authorize production geometry, approve DES-001,
or advance its lifecycle state. Human technical and domain review, an exact
revision sign-off record and separate implementation authorization remain pending.
