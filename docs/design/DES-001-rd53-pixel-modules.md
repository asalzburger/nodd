# DES-001 — Reusable RD53i pixel modules

- Status: DRAFT — first-review proposal; no production integration authorized.
- Created / updated: 2026-09-17.
- Author: AI-assisted Tracking Engineer synthesis; alternatives rewritten by separately commissioned Astra agents.
- Human owner / expert reviewers: TBD; issue [#7](https://github.com/asalzburger/nodd/issues/7); draft [PR #8](https://github.com/asalzburger/nodd/pull/8).
- Technology direction: [ADR-007](../decisions/ADR-007-itkpix-pixel-baseline.md).
- Human sign-off, implementation PR and hardware validation: pending.

## Glossary

**RD53i means ITkPix v2 (RD53C-ATLAS)** in this proposal and both alternatives.
This is a project shorthand, not a new chip or an official manufacturer name.
The user selected the family and revision and requested this notation on
2026-09-17. Subsequent component descriptions use RD53i; source titles retain
their published names. The chip choice is resolved; delivered thinning,
mechanical/pad drawings and known-good-die evidence are not yet verified.

## Scope and exclusions

Design the standalone module: planar sensor, bump interconnect, RD53i dies,
module flex and adhesives, wire bonds, sensor bias contact, local passives and
module electrical termination. Include any integral flex extension in its BOM.
The physical boundary stops at the module termination and the bare die backs.
Mounting structures, mounting adhesive, cooling infrastructure and external
power/data distribution are excluded from the proposals, drawings and budgets.

Alternative A contains a single-chip module (A1) and optional side-by-side
two-chip module (A2); alternative B is a four-chip module (B4). Compare reusable
sensor/hybrid/flex assemblies, a small number of production types, material and
credible manufacture. Pixel volume and placement remain deliberately open.
There is no DD4hep geometry or production detector change. A later unsigned
executable construction must remain isolated and labelled PROTOTYPE.

## Requirements and acceptance criteria

All requirements are **NODD DESIGN CHOICE — proposed**; human technical approval
is pending. Existing chip-selection direction does not approve the full module.

| ID | Requirement | Measurement / review criterion |
| --- | --- | --- |
| PM3-R01 | Use the selected RD53i without redesigning its interfaces | Check authoritative die, pad, pixel and bump mapping before dimensional freeze |
| PM3-R02 | Reuse structures and minimize module types | Compare A1/A2/B4 shared parts and qualification cost; no three-type family presumed |
| PM3-R03 | Account for every module constituent | Thickness/composition/coverage table, mass and spatial X/X₀ map; unknown entries cannot be zero |
| PM3-R04 | Realistic hybrid manufacture | Bump alignment, sensor handling, flex adhesion, bond access and electrical tests; tolerances pending expert review |
| PM3-R05 | Stay at module scope | No excluded infrastructure in stack, figures, BOM or recommendation |

## Sources and sourced facts

The [catalogue](../../reference/manifest.yaml) records public versions, access and
verification limits. These are selected facts, not adoption of an experiment layout.

| Claim | Classification | Fact | Source / precise locator |
| --- | --- | --- | --- |
| PM3-F01 | FACT | Chip overview lists 400 × 384 chip cells at 50 × 50 µm pitch and approximately 20 × 21 mm die dimensions | SRC-RD53-OVERVIEW-2023, slide 5 / physical PDF5, ATLAS column; source overview rather than procurement tolerances |
| PM3-F02 | FACT | Silicon X₀ = 93.70 mm | SRC-PDG-SILICON-2025, Radiation length row, 9.370 cm |
| PM3-F03 | FACT | Copper X₀ = 14.36 mm | SRC-PDG-COPPER-2025, Radiation length row, 1.436 cm |
| PM3-F04 | FACT | Specified polyimide film X₀ = 285.7 mm | SRC-PDG-POLYIMIDE-2020, Radiation length row, 28.57 cm; composition (C₂₂H₁₀N₂O₅)ₙ |
| PM3-F05 | FACT | Aluminum X₀ = 88.97 mm | SRC-PDG-ALUMINUM-2025, Radiation length row, 8.897 cm |

No published power/radiation target is claimed as measured stock performance.
Old RD53A benchmark claims and earlier infrastructure studies remain traceable
in Git history; they are superseded inputs, not current module requirements.
New PM3 claim IDs distinguish this scope revision from previous PM IDs.

## Proposed module construction

Every choice below is **NODD DESIGN CHOICE — proposed; human approvers pending**.

| Claim | Choice | Rationale / consequence |
| --- | --- | --- |
| PM3-C01 | Planar n-in-p sensor with qualified bump mapping | Common starting technology; process, guard/bias design and irradiation requirements remain open |
| PM3-C02 | 150 µm sensor and 150 µm thinned RD53i silicon study values | Balanced initial handling/material study; these are selected nominal hypotheses, not verified delivered thicknesses; thinning and sensor choice need evidence |
| PM3-C03 | Sensor-backside flex with 25 µm polyimide core, two 12.5 µm coverlay films and two 18 µm copper layers | Common comparative routing hypothesis; coverlay/lamination adhesive is additional material, and routed copper coverage remains unknown |
| PM3-C04 | 25 µm patterned flex-to-sensor epoxy bondline | Controlled nominal adhesion study; exact resin/filler, density, coverage and X₀ remain unresolved |
| PM3-C05 | 20 µm nominal bump standoff; no assumed full-area underfill | Separates sensitive sensor from chip; alloy, bump geometry and under-bump stack require vendor evidence; standoff is not metal thickness |
| PM3-C06 | Candidate 25 µm aluminum wire bonds to accessible flex pads | Low-mass module interconnect; actual pad compatibility, loop geometry, counts and pull qualification remain pending |
| PM3-C07 | Local bias/decoupling parts and a module-edge electrical termination | Keep necessary components inside the module BOM; link count, grounding, HV clearances and pinout need routed design |

The flex is on the opposite sensor face from bumps and chip active surfaces.
Bond-access tabs connect outward chip-pad peripheries to the sensor-backside
flex. Die backs remain bare in this proposal. Sensor silicon, matrix response,
guard regions, interchip gaps and seam implants are distinct descriptions.
A shared sensor does not imply seamless charge collection or new readout cells.

## Dimensions, material table and cross-sections

**INFERENCE PM3-I01:** matrix counts × pitch give 153,600 channels and a nominal
20.0 × 19.2 mm readout rectangle (384 mm²) per chip. A2 gives 307,200 channels /
768 mm²; B4 gives 614,400 channels / 1536 mm². These are readout bookkeeping,
not measured efficient area. Approximate die-only spans are A1 20 × 21 mm,
A2 40 × 21 mm and B4 40 × 42 mm before gaps, sensor edges, flex and bond clearance.
No certified sensor or finished-module outline is inferred from these spans.

[Machine-readable common study](DES-001-module-stack.json) retains proposed
inputs and unrounded arithmetic. This table applies to the compared module
stacks; patterned layouts and localized parts differ between alternatives.

| Module component | Proposed thickness / geometry | Material | Material X₀ [mm] | Local reference contribution [% X₀] | Basis / unresolved detail |
| --- | --- | --- | ---: | ---: | --- |
| Sensor substrate | 150 µm | Silicon | 93.70 | 0.1601 | PM3-C02, PM3-F02; full physical silicon, including non-sensitive regions |
| RD53i substrate | 150 µm | Silicon | 93.70 | 0.1601 | PM3-C02, PM3-F02; metallization/passivation additional |
| Flex core | 25 µm | Specified polyimide film | 285.7 | 0.00875 | PM3-C03, PM3-F04 |
| Flex coverlay films | 2 × 12.5 µm | Same polyimide film hypothesis | 285.7 | 0.00875 | PM3-C03; coverlay adhesive separately unresolved |
| Copper routing | 2 × 18 µm | Copper | 14.36 | 0.2507 where both layers cross | PM3-C03, PM3-F03; not whole-area fill or module-average contribution |
| Flex-to-sensor bondline | 25 µm nominal | Epoxy grade/filler TBD | TBD | TBD | PM3-C04; actual glue coverage and composition required |
| Flip-chip bumps | 20 µm standoff | Bump alloy TBD | TBD | TBD | PM3-C05; actual bump volume/path lengths, not a continuous 20 µm slab |
| Under-bump / sensor / chip films | TBD | Metallization and passivation stack TBD | TBD by constituent | TBD | Additional films cannot be silently included in pure-silicon estimate |
| Flex laminate / coverlay adhesives | TBD | Adhesive grades TBD | TBD | TBD | Additional to the 50 µm polyimide-film total |
| Wire bonds | 25 µm wire diameter; loops TBD | Aluminum candidate | 88.97 | TBD spatially | PM3-C06, PM3-F05; diameter is not area-equivalent layer thickness |
| Bias contact, local passives and module termination | Part heights / volumes TBD | Mixed spatial BOM TBD | TBD by constituent | TBD | PM3-C07; includes solder/pad finishes and localized packages |

**INFERENCE PM3-I02:** for a normal ray through a listed layer,
`percent X₀ = 100 × thickness_um / (1000 × X₀_mm)`.
The silicon, polyimide and both-copper-layer **partial local reference subtotal
is 0.5884% X₀**. It omits unresolved components and is neither a complete module
budget nor an area average or a bound on the completed module. Copper patterning
can reduce its contribution away from traces; local parts can increase the total.
For an area average use actual coverage/volumes over the same stated reference
area; off-normal rays require intersected paths, not a nominal slab sum.

Each proposal supplies its own module cross-section and plan view:

- [Compact A proposal and component table](inputs/DES-001-compact-modules.md):
  ![Compact module plan and cross-section](figures/DES-001-compact-modules.svg)
- [Quad B proposal and component table](inputs/DES-001-quad-modules.md):
  ![Quad module plan and cross-section](figures/DES-001-quad-modules.svg)

Figures distinguish layer thickness labels from schematic drawing scale.
Unknown films, glue grades, bumps and local components remain explicit.

## Module comparison and recommendation

Comparative statements are **INFERENCE**, conditional on the proposed construction.

| Criterion | Compact A1 / A2 | Quad B4 |
| --- | --- | --- |
| Reuse / type count | Smallest qualification unit; A2 requires its own sensor/flex | One common larger assembly, with four-chip routing and seam mapping |
| Module material | More repeated edges/terminations per nominal area | Potential amortization; larger flex, routing and local components can offset it |
| Manufacture / failure | Smaller handling and rejected-area unit | Larger sensor and correlated hybrid losses; independent-chip yield sensitivity is not measured yield |
| Electrical assembly | Fewer chip links per assembly | More links/current routing and bond access to qualify |

The [Coordinator assessment](inputs/DES-001-coordinator-review.md) gives an advisory
programme recommendation. **NODD DESIGN CHOICE — proposed:** qualify A1 first
and compare A2 with B4 before selecting a coverage module. A1 can remain a study
unit; no three-type production family is assumed. Equal nominal layer thickness
cannot establish a numerical material winner. Pixel volume remains open and
later placement suitability is deferred to its separate design task.

## Risks and open questions

| Question | Impact / owner | Resolution gate |
| --- | --- | --- |
| Delivered chip thickness, mask/pad/bump drawings and qualification | Tracking Engineer + human inventory owner TBD; prevents dimensional/pinout errors | Before dimensional freeze |
| Sensor technology/process, bias, irradiation and rate requirements | Sensor/readout experts TBD; nominal planar stack does not certify lifetime | Before design sign-off |
| Bump alloy, glue grades, film stacks and routing coverage | Materials/assembly experts TBD; partial table cannot become complete budget | Before numerical module-budget acceptance |
| Seam response, wire loops and local components | Hybridization/electrical experts TBD; assembly access and localized material | Technical/expert review |
| Pixel volume | Deliberately open, separate layout task | Before final deployment family choice |

## Validation plan and review tracking

Planned module evidence: authoritative-interface audit; bare-hybrid connectivity
and bump defect maps; sensor IV/bias and seam charge response; dimensional/film
audit; weighed BOM and spatial material map; bond inspection/pull samples;
module configuration, data integrity and electrical load tests; assembly thermal
cycling/irradiation appropriate to later operating requirements. Numeric sampling,
tolerances and acceptance criteria remain pending human expert review.

No hardware or detector simulation validation has run. Actual documentary and
arithmetic checks are recorded in the session journal and PR. Future executable
evidence must record commit/configuration/tools/commands and tolerances; production
geometry remains gated by separate human design approval and implementation work.
Human technical, domain and validation reviewers remain unassigned. No AI role
assessment grants sign-off or advances this DRAFT lifecycle.
