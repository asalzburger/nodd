# DES-001 input — Alternative B: reusable planar quad module

- Status: DRAFT design input; human approval and production implementation pending.
- Updated: 2026-09-17; author role: independent Tracking engineer alternative study.
- Governing design: [DES-001](../DES-001-rd53-pixel-modules.md), [ADR-007](../../decisions/ADR-007-itkpix-pixel-baseline.md); issue [#7](https://github.com/asalzburger/nodd/issues/7).
- Terminology: [RD53i glossary](../DES-001-rd53-pixel-modules.md#glossary).
- Parameter authority for this comparison: [common proposed study stack](../DES-001-module-stack.json).
- Human technical reviewer and approving humans: pending.

![Draft quad module with outward bond access and sensor-back flex](../figures/DES-001-quad-modules.svg)

## Module concept and boundary

**NODD DESIGN CHOICE B-C20 — proposed:** use one rectangular planar silicon
sensor, four RD53i chips in a 2 × 2 arrangement, one common flex, bump
interconnects, flex adhesive, wire bonds, necessary local passives and one
module-side electrical termination. Keep the chip bond peripheries facing the
two opposite outer edges. This arrangement is conditional on the exact RD53i pad
and bump drawing; the schematic is an assembly proposal, not a qualified layout.
All B-C20–B-C25 choices below await human approval.

The module ends at its electrical termination and exposed chip backs. Mounting,
supports, cooling hardware, mounting adhesive and external service allocations
are outside this study. They require a separate boundary study and contribute
nothing to the module-only figures here; their eventual detector contribution
must be accounted elsewhere. This boundary does not claim thermal qualification.

**NODD DESIGN CHOICE B-C21 — proposed:** start with a 150 µm planar n-in-p
sensor and four chips thinned to 150 µm of silicon. These are comparison choices,
not facts about available stock or guarantees of radiation performance. Supplier
thinning capability, sensor depletion/bias requirements, flatness and handling
yield must be checked before freezing them. A thinner sensor or chip is a later
alternative requiring the same checks.

## Public evidence and geometrical inference

| Claim ID | Classification | Statement and precise source locator |
| --- | --- | --- |
| B-F20 | FACT | SRC-RD53-OVERVIEW-2023, slide 5 / physical PDF 5, gives the selected family reference matrix as 400 × 384 chip cells at 50 µm pitch, with an approximate 20 × 21 mm die. These overview values do not specify stock tolerances, supplied thickness or pad accessibility. |
| B-F21 | FACT | SRC-RD53A-MODULE-ASSEMBLY-2022, §1–2 / PDF 2–5, documents hybrid assembly using a sensor, bump-bonded chips, attached flex and wire bonds; §3 / PDF 5–7 describes testing. This is historical assembly precedent only; none of its chip dimensions or operating parameters governs RD53i. |
| B-I20 | INFERENCE | B-F20 gives 20.0 × 19.2 mm = 384 mm² and 153,600 channels per chip. Four chips give 1536 mm² nominal readout footprint and 614,400 channels. Approximate die-only 2 × 2 span is 40 × 42 mm before gaps. No installed acceptance or sensor efficiency follows. |
| B-I21 | INFERENCE | For die dimensions D_x,D_y, gaps g_x,g_y and outward envelope margins e_left,e_right,e_top,e_bottom, W = 2D_x + g_x + e_left + e_right and H = 2D_y + g_y + e_top + e_bottom. Margins include module-local bond loops, flex and termination. The sensor boundary must be derived separately so it does not cover bond pads. |

Sources and version metadata are in the [catalogue](../../../reference/manifest.yaml).
The chip reference is Stefano Esposito for RD53, *RD53: Lessons Learned —
A verification perspective*, 2023-10-23. The assembly precedent is A. Petrukhin
for the ATLAS ITk Pixel Collaboration, *RD53A pixel module assembly and testing
experience*, arXiv:2212.09392v1, 2022-12-19. Earlier benchmark claims remain in
Git history; the new IDs above do not redefine them.

**NODD DESIGN CHOICE B-C22 — proposed:** retain four distinct readout regions,
both inter-chip seams, sensor edge/guard structures and the bump-to-implant map.
A common sensor does not imply a seamless active plane. Any elongated seam
pixels require a compatible mask and measured charge response; they create no
extra electronic channels. Gap sizes, guard margins and bond-loop heights are
unresolved, so the 40 × 42 mm die reference cannot be used as a module envelope.

## Complete component account and provisional material calculation

**NODD DESIGN CHOICE B-C23 — proposed:** use the same study stack as alternative
A, with a polyimide/copper flex on the sensor back and bumps/chips on its opposite
face. The flex comprises a 25 µm core and two 12.5 µm coverlay films, two patterned
18 µm copper layers, and separately accounted laminate adhesives. Attach the
flex with a proposed 25 µm epoxy bondline. Study a 20 µm bump standoff and
25 µm diameter aluminium wire bonds. Thicknesses and wire diameter are proposed
values, not measured assemblies. Patterning, routing and a qualified assembly
process determine whether they are sufficient; adding necessary material must
update this account.

**FACT B-F22:** the PDG Atomic and Nuclear Properties tables give bulk radiation
lengths of 93.70 mm for silicon, 14.36 mm for copper and 88.97 mm for aluminium
(2025 element pages), and 285.7 mm for polyimide film (2020 film page). Precise
locator: the `Radiation length` row of SRC-PDG-SILICON-2025,
SRC-PDG-COPPER-2025, SRC-PDG-ALUMINUM-2025 and SRC-PDG-POLYIMIDE-2020.
The film value is a reference composition, not a certification of a selected flex.

**INFERENCE B-I22:** for a normal ray through a uniform layer, the contribution
in percent of a radiation length is 100 t/X0, with t and X0 in the same units.
The table applies B-F22 to the proposed B-C21/B-C23 dimensions. No unknown row
is assigned zero. Silicon substrate values exclude separately listed device
surface materials.

| Module constituent | Proposed thickness / geometry | Material | Bulk X0 (mm) | Local contribution (% X0) | Remaining definition |
| --- | --- | --- | --- | --- | --- |
| Common sensor bulk | 150 µm | Silicon | 93.70 | 0.1601 | Process, perimeter, thickness tolerance and active map |
| Four RD53i substrates | 150 µm per die | Silicon | 93.70 | 0.1601 through one die | Four lateral dies do not form four stacked layers; actual thinning and gaps pending |
| Flex dielectric core | 25 µm | Polyimide film reference | 285.7 | 0.0088 | Supplier composition and cutouts |
| Flex coverlay films | 2 × 12.5 µm | Polyimide film reference | 285.7 | 0.0088 combined | Adhesives excluded from film thickness |
| Flex conductor layer 1 | 18 µm where copper exists | Copper | 14.36 | 0.1253 where crossed | Routing and spatial coverage c1 pending |
| Flex conductor layer 2 | 18 µm where copper exists | Copper | 14.36 | 0.1253 where crossed | Routing and spatial coverage c2 pending |
| Flex-to-sensor bond | 25 µm proposed bondline | Epoxy grade/composition TBD | TBD | TBD | Density, coverage, fillers, cure and actual thickness |
| Flex laminate/coverlay adhesive | Thickness and coverage TBD | Adhesive grade TBD | TBD | TBD | Separate from the proposed 50 µm total polyimide |
| Bump interconnects | 20 µm proposed standoff; volume/diameter/count map TBD | Alloy and under-bump metallization TBD | TBD | TBD | Standoff is not a continuous metal layer; supplier geometry required |
| Chip-to-flex and sensor-bias bonds | 25 µm proposed wire diameter; counts/loop lengths TBD | Aluminium candidate | 88.97 | TBD | Nonplanar paths; include every required wire and contact |
| Sensor/chip surfaces | Thickness, composition and coverage TBD | Device metallization, dielectrics and passivation | TBD | TBD | Avoid counting bump metallization twice |
| Flex finishes, pads and vias | Thickness/volume map TBD | Plating/finish metals and via copper TBD | TBD | TBD | Add plating separately from nominal copper foils |
| Local passives and attachment | BOM, package volumes and masses TBD | Capacitors, resistors and other required parts; solder/adhesive | TBD | TBD | Routing and power/HV design determine count and locations |
| Module-side termination | Pad or connector choice and occupied volume TBD | Conductors, insulation and attachment TBD | TBD | TBD | Include any module-local reinforcement or retention needed by the selected termination |
| Any required bond protection or reinforcement | Necessity, geometry and mass TBD | Material TBD | TBD | TBD | No blanket potting, underfill or stiffener assumed; any required addition must enter the BOM |

**INFERENCE B-I23:** the partial local stack through sensor, one chip, all
50 µm of polyimide and both copper layers gives
100 × (0.150/93.70 + 0.150/93.70 + 0.050/285.7 + 0.036/14.36)
= **0.5884% X0**. Compute from unrounded values; individual rounded rows need
not sum exactly. The polyimide subtotal is 0.0175% X0 and the two-copper-layer
subtotal is 0.2507% X0. This is a partial reference crossing, **not the complete
module budget**, not its area average and not an upper bound including the
unknown components. A ray through one quad chip does not cross all four chips.

For an area average, integrate each component's actual material map over a
stated area. Over a fixed region with fractional conductor coverage c1 and c2,
the copper term is 0.12535(c1 + c2)% X0, assuming 18 µm uniform traces within
each covered area. Do not assume equal coverage or use the full-coverage value
as an average. Bump and wire contributions require their actual volumes or
intersected paths; the proposed standoff/diameter alone is insufficient. Compare
module mass and integrated material per 1536 mm² nominal readout area as one
explicit normalization, and separately report useful measured sensor area and
local concentrations. A full module material result remains pending.

## Assembly, reuse and alternative comparison

**NODD DESIGN CHOICE B-C24 — proposed:** use a single quad sensor/flex design
and repeated chip orientation pairs. Route only the required conductors and
local components; retain sufficient bondable flex land support within the module
assembly and expose chip pads without routing flex through the bump interface.
A routed flex must demonstrate power returns, signal integrity, bias clearance,
bond-tool access and termination retention before material can be minimized
credibly. The design does not assume that fewer module types makes one flex
compatible with every electrical topology.

**INFERENCE B-I24:** compared at equal nominal readout area, one B quad replaces
two A two-chip modules or four A one-chip modules. Common chip and sensor bulk
thicknesses therefore offer no intrinsic silicon material saving per readout
area. B may save duplicated sensor perimeter, flex edge and termination overhead.
Longer routing, additional local passives, a larger sensor, reinforcement or
assembly rejection can erase that saving. The unknown BOM prevents a numerical
ranking or a claim that B has the least material.

| Criterion | Quad opportunity | Constraint and deciding evidence |
| --- | --- | --- |
| Few module types | One common large planar sensor and flex for repeated units | Exact inventory mapping and module fit remain unresolved |
| Reuse | Four repeated chip placements and shared module test interface | A larger sensor/flex remains a separate part from compact alternatives |
| Minimum module material | Amortize module termination and repeated sensor/flex edges | Compare routed and weighed BOMs per useful area, including reinforcement if required |
| Realistic assembly | Conventional bump hybrid, sensor-back flex and outward wire bonding | Thin large-sensor handling, coplanarity, bond access and adhesive cure must be demonstrated |
| Failure exposure | Chip-by-chip testing can identify defective regions | A common sensor/flex defect may reject a whole quad; partial operation is not assumed to be a repair |

All comparisons in this table are **INFERENCE B-I25**, conditional on B-C20–B-C24.
For independent chip survival probability p, the all-four-survive factor is p⁴;
this sensitivity model excludes correlated, sensor and assembly failures and is
not a yield prediction.

**NODD DESIGN CHOICE B-C25 — proposed:** qualify the sensor, thinned dies and
flex independently; inspect/test the bare bump hybrid; measure glue mass and
post-cure flatness; inspect and sample-test bonds; perform per-chip connectivity,
noise/tuning and sensor IV tests; map charge response across both seams and
outer edges; repeat electrical and metrology checks after a reviewed thermal
cycle programme. Numerical criteria and cycle conditions require a validation
specification; none is implied by the drawing.

Retain B as the candidate for amortizing module overhead, pending a complete
module BOM and assembly evidence. Exact die/pad/bump drawings, sensor process
and seam response, routed flex, adhesive identities, passives and termination
are unresolved. Human review must approve the dimensions, material choices and
acceptance criteria before production implementation. This input changes no
production geometry or detector configuration.
