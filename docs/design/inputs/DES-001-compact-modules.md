# DES-001 alternative A — compact RD53i modules

- Status: DRAFT; module-only design study, no production implementation or sign-off.
- Created / updated: 2026-09-17.
- Author: Tracking Engineer compact-module agent, Astra (`gpt-6-astra`, configured model); no token-usage measurement available.
- Parent: [DES-001](../DES-001-rd53-pixel-modules.md), [ADR-007](../../decisions/ADR-007-itkpix-pixel-baseline.md), [issue #7](https://github.com/asalzburger/nodd/issues/7).
- Human owner, technical reviewers and approvers: pending.

RD53i follows the [shared glossary](../DES-001-rd53-pixel-modules.md#glossary).
This proposal uses one RD53i per A1 module, with an optional two-chip A2 variant.
Its assembly consists of a sensor, bump interconnect, chips, sensor-backside
flex and its adhesion, wire bonds, local passives, sensor-bias contact and module
termination. Mounting joints, supports, cooling and external cables are outside
this module-only boundary. Their later integration cannot be certified here.

This rewrite introduces A3-* claim IDs. Earlier A-* claims remain historical
in Git; their identifiers are not reassigned to changed facts or assumptions.

![Compact module top views and physical stack](../figures/DES-001-compact-modules.svg)

The original vector drawing shows proposed topology and nominal thicknesses.
Lateral dimensions and vertical display heights are schematic; labels govern
this study. Bond access and routing require an exact RD53i drawing.

## Public evidence

Sources are registered in the [catalogue](../../../reference/manifest.yaml).
Public pages were inspected on 2026-09-17. Material constants describe the stated
substances, not a supplier-certified module composition or thickness.

| Claim | Classification | Fact and exact locator |
| --- | --- | --- |
| A3-F01 | FACT | SRC-RD53-OVERVIEW-2023, slide 5 / PDF 5, ATLAS column: nominal matrix 400 × 384, chip-cell pitch 50 × 50 µm, approximate chip dimensions 20 × 21 mm. The overview does not establish tolerances, final pad geometry or stock thinning. |
| A3-F02 | FACT | SRC-PDG-SILICON-2025, Radiation length row: silicon X0 = 9.370 cm = 93.70 mm. |
| A3-F03 | FACT | SRC-PDG-COPPER-2025, Radiation length row: copper X0 = 1.436 cm = 14.36 mm. |
| A3-F04 | FACT | SRC-PDG-POLYIMIDE-2020, Radiation length row: polyimide film X0 = 28.57 cm = 285.7 mm. Applies to the PDG film composition, not arbitrary filled adhesives. |
| A3-F05 | FACT | SRC-PDG-ALUMINUM-2025, Radiation length row: aluminum X0 = 8.897 cm = 88.97 mm. |

Primary references: [RD53 overview](https://indico.cern.ch/event/1335413/contributions/5621748/attachments/2731411/4764279/RD53%20Lessons%20Learned%20in%20Verification.pdf),
[PDG silicon](https://pdg.lbl.gov/2025/AtomicNuclearProperties/HTML/silicon_Si.html),
[copper](https://pdg.lbl.gov/2025/AtomicNuclearProperties/HTML/copper_Cu.html),
[polyimide film](https://pdg.lbl.gov/2020/AtomicNuclearProperties/HTML/polyimide_film.html)
and [aluminum](https://pdg.lbl.gov/2025/AtomicNuclearProperties/HTML/aluminum_Al.html).

## Assembly proposal

Every choice below is **NODD DESIGN CHOICE — proposed; human approvers pending**.
Thicknesses are candidate study inputs, not measured hardware or engineering
certification. The [common stack study](../DES-001-module-stack.json) keeps the
same assumptions for the competing module proposals.

| Claim | Proposed choice | Rationale, alternative and consequence |
| --- | --- | --- |
| A3-C01 | A1: one planar silicon sensor, one RD53i and one local flex. | Small independently assembled/tested unit. Repeated edges and terminations cost material; compare with larger modules before selecting a production family. |
| A3-C02 | A2, conditional: one sensor across two side-by-side RD53i chips, aligned accessible pad edges and a shared flex. | Can share local passives/termination. Two A1 units remain the alternative; A2 adds a sensor seam, placement tolerance and larger reject area. |
| A3-C03 | Study 150 µm sensor silicon and 150 µm chip substrate. | Concrete equal-stack comparison; thicker parts may improve handling. Depletion, thinning, irradiation and hybridization qualification remain open, so neither thickness is frozen. |
| A3-C04 | Flex on sensor backside: 25 µm polyimide core, two 12.5 µm polyimide coverlay films and two patterned 18 µm copper layers. | Separates bond-side access from flip-chip interconnects. Layer count and copper coverage must survive routing/current/insulation review; thinner conductors or another stack remain alternatives. Laminate adhesives are additional TBD material. |
| A3-C05 | Candidate 25 µm cured epoxy flex-to-sensor bondline, with actual bonded area recorded. | Explicit adhesion allowance; grade, filler, voids, coverage and X0 remain TBD. Do not substitute polyimide X0 for epoxy. |
| A3-C06 | Candidate 20 µm bump standoff, alloy/shape/metallization TBD; no blanket underfill selected. | Gives a visible assembly separation. Standoff is not a dense-metal thickness; process evidence may change it. Any later underfill requires its own budget and justification. |
| A3-C07 | Candidate 25 µm diameter aluminum bond wires from exposed chip pads to opened flex pads; bias contact separately represented. | Conventional candidate conductor and explicit bond access. Count, loop length/height, bonding compatibility, insulation and tool clearance require drawings; alternatives need their own qualification. |
| A3-C08 | Include local decoupling/bias passives and a module termination land bank in the flex BOM. | A compact boundary with explicit local material; package sizes, quantity, solder/finish and strain relief remain TBD. A connector would require an amended spatial BOM. External cable starts beyond this boundary. |

The physical stack, from sensor backside toward chip backside, is flex,
flex-to-sensor adhesive, sensor, discrete bumps and RD53i. Sensor and flex stop
short of the proposed exposed chip pad ledge; wire loops rise around that edge
to the flex pads. Windows in coverlay expose bond and component lands. Sensor
back-bias contact geometry and isolation are unresolved. No wire may pass
through sensor silicon, flex dielectric or a fictitious full bump slab.

**INFERENCE A3-I01:** A3-F01 gives a nominal matrix 20 × 19.2 mm = 384 mm² and
153,600 channels per chip. A1 has that nominal readout area; A2 totals 768 mm²
and 307,200 channels. Approximate chip-only spans are 20 × 21 mm and 40 × 21 mm,
respectively, before gaps. These are neither sensor/module extents nor efficient
coverage. Guard rings, pad ledges, flex extensions and A2 seam mapping remain
explicit unknowns. A2 physical chip adjacency does not prove seamless acceptance.

## Component thickness and radiation-length study

Thickness/material selections in this table are the proposed choices above;
X0 values are FACT A3-F02–F05. All numerical percentages are **INFERENCE A3-I02**:
100 × t[mm]/X0[mm] for a normal ray crossing that constituent at full thickness.
A fractional X/X0 is the percentage divided by 100.

| Component | Proposed thickness or geometry | Material; X0 [mm] | Local contribution [% X0] | Basis / qualification needed |
| --- | --- | --- | --- | --- |
| Sensor bulk | 150 µm | Silicon; 93.70 | 0.1601 | A3-C03; full physical silicon, including inactive edge |
| RD53i substrate | 150 µm | Silicon; 93.70 | 0.1601 | A3-C03; full die, including periphery |
| Flex core and coverlay films | 25 + 2 × 12.5 = 50 µm | PDG polyimide film; 285.7 | 0.0175 | A3-C04; excludes all laminate adhesives |
| Flex copper | 2 × 18 = 36 µm | Copper; 14.36 | 0.2507 | A3-C04; reference crossing both copper layers, not routed area average |
| Flex-to-sensor adhesion | 25 µm candidate bondline | Epoxy grade TBD; X0 TBD | TBD | A3-C05; actual footprint, cured composition and density needed |
| Bump interconnect | 20 µm candidate standoff | Alloy and under-bump films TBD; X0 TBD | TBD | A3-C06; bump count/volume per area needed |
| Wire bonds | 25 µm candidate wire diameter | Aluminum; 88.97 | TBD | A3-C07; nonplanar wire geometry, not a full-area slab |
| Flex laminate/coverlay adhesives | TBD | Composition and X0 TBD | TBD | Additional to the 50 µm films |
| Sensor/chip films | Metallization and passivation TBD | Layer compositions and X0 TBD | TBD | Additional to bulk silicon; avoid double counting under-bump films |
| Local passives, bias contact and module termination | Package/land/finish dimensions TBD | Spatial BOM and X0 TBD | TBD | A3-C08; count every part on the module side of the boundary |

**INFERENCE A3-I03:** the four calculable rows sum to **0.5884% X0**, only a
partial local reference subtotal where both bulk silicon layers, all proposed
polyimide films and both copper layers are crossed. It is not a complete module
budget, not a module area average and not a bound on the full module. Unknown
components are not zero. Patterned copper may lower its average contribution;
local parts or films omitted from this subtotal add material.

**INFERENCE A3-I04:** for copper coverages c1 and c2 referred to the same mapped
area, the mean copper contribution is 0.12535(c1 + c2)% X0. The actual flex,
sensor and die footprints differ, so this expression alone cannot average the
whole module. Use projected material maps and ΣρV/A with a stated area: nominal
matrix area, physical sensor area or complete module envelope. Wire material
requires count × length × πd²/4; bumps require actual metal volumes. Oblique
rays require physical paths rather than multiplication by chip count. A2 has
twice the silicon area at this common thickness, not twice the local stack X0.

## Compact-family tradeoff and review gates

**INFERENCE A3-I05:** A1 limits the area tied to a single module failure and
reduces rigid span. A2 can amortize local passives, flex perimeter and termination,
but larger routed copper coverage, seam losses and assembly rejects may erase
that benefit. The present equal-stack arithmetic establishes no material winner.
Compare actual component mass per nominal matrix area and accepted assembled
area, with uncertainty in process yield and rework explicitly reported.

The first useful deliverable is an A1 sensor/chip/flex drawing with verified pad
access, a spatial BOM and a bare-module electrical test plan. A2 remains optional
until that same accounting demonstrates a benefit over two A1 units. This is
**NODD DESIGN CHOICE A3-C09 — proposed; human approvers pending**.

Before dimensional freeze, obtain the exact RD53i mechanical, pad and bump
information, qualified thinning process, compatible sensor electrode map, guard
structure and isolation clearances. Before expert review, resolve flex routing,
bond loops, epoxy and bump composition, all local parts and termination mass.
Readout link allocation, bias, power/return and fault behavior must be specified
at the module boundary without assuming an unverified shared A2 data link.

Planned module qualification includes sensor IV, bump continuity, chip readout,
bond inspection/pull sampling, dimensional metrology, BOM mass, thermal cycling
and tests at a defined bias/load/environment. Test fixtures do not become module
components. Radiation and operating conditions, tolerances and human reviewers
remain pending. No hardware qualification, geometry validation or performance
measurement has been run for this draft; document/arithmetic checks do not
certify buildability. Any later executable model remains an isolated PROTOTYPE
until the required design review and human sign-off authorize integration.
