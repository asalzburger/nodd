# DES-001 — Reusable RD53 pixel modules

- Status: DRAFT — design proposal; no production integration authorized.
- Created: 2026-09-17; updated: 2026-09-17.
- Author: Tracking Engineer AI agent, with independently delegated compact and quad studies.
- Human owner: TBD; issue: [#7](https://github.com/asalzburger/nodd/issues/7).
- Governing architecture: [DES-003](DES-003-global-envelopes.md), [ADR-006](../decisions/ADR-006-global-envelope-and-field-hypotheses.md); their baseline review does not sign off this module.
- Sign-off record: pending; implementation PR: pending; validation evidence: documentary checks only.

## Scope and exclusions

Develop a stand-alone hybrid pixel-module family around the **existing RD53 chip
in hand**. Its mask, pitch, pads and interfaces are fixed inputs, not redesign
opportunities. The exact inventory variant, revision, thinning and known-good-die
status remain unknown. No substitution by ITkPix, CROC or another production chip
is authorized. RD53A is used below only as a conditional, public reference case.

Two credible options are developed independently: compact one-/two-chip modules
and a four-chip module. Both preserve reusable subassemblies and expose a common
mounting/service contract. Pixel volume, radii, layers, endcap segmentation,
fluences, occupancy and operating lifetime are to be defined. This proposal
allocates no detector layers and implements no DD4hep geometry. Module cooling
interfaces are specified here; detailed support/cooling belongs to future DES-002.
Any later executable exploration must be isolated and labelled PROTOTYPE.

## Requirements and acceptance criteria

All requirements here are **NODD DESIGN CHOICE — proposed**, prompted by the user;
human technical approvers: none.

| ID | Requirement and rationale | Measurement | Acceptance criterion |
| --- | --- | --- | --- |
| PM-R01 | Use the chip inventory unchanged | Procurement drawing, mask/pad and electrical-interface audit | Exact stock variant and interface dossier before dimensional freeze |
| PM-R02 | Few reusable module types | Family/BOM inventory | Compare one/two-chip family against one quad family; final count pending pixel-volume study |
| PM-R03 | Minimize accounted material | Mass and spatial X0/lambda maps including service share | Select by total material per useful instrumented area; numeric limit unresolved |
| PM-R04 | Realistic manufacture and thermal operation | Supplier/hybridization evidence, assembly coupons, thermal/electrical tests | Process and worst-case thermal budget reviewed; tolerances/temperature limits unresolved |
| PM-R05 | Preserve inactive regions and routing clearances | Bump-mask, die, flex and bond-loop drawings | No concealed gap, guard ring, periphery or service contribution |
| PM-R06 | Remain experiment independent | Requirement/provenance review | Layout justified against nODD loads and host volume rather than copied TDR dimensions |

## Sources

Source identities and public links are in [the catalogue](../../reference/manifest.yaml).
TDR passages describe precedents and their maturity at publication, not nODD
requirements. Supporting memoranda retain additional claim-level locators.

| Source ID | Public reference/version | Precise locator | Claims |
| --- | --- | --- | --- |
| SRC-RD53A | RD53 Collaboration, CERN-RD53-PUB-17-001, manual v3.51, 2019-08-19 | Abstract PDF1; §1 PDF4 / printed3; Fig1 PDF5 / printed4; §2 PDF6 / printed5; §3/Table1 PDF8 / printed7; §4 PDF15 / printed14 | PM-F01–F05 |
| SRC-CMS-TDR-014 | CMS Phase-2 Tracker TDR, CERN-LHCC-2017-009 | §4.2 PDF74/Fig4.3; §10.1.1.1 PDF233; §4.2.2 PDF81–83; §10.2.2.6 PDF252–255 | Module/service precedent, retained guide observations |
| SRC-ATLAS-TDR-030 | ATLAS ITk Pixel TDR, CERN-LHCC-2017-021 | Chapters7–8; §8.2.2 printed199/PDF221; §8.2.5/Table8.2 printed202/PDF224 | Navigation for hybridization/flex/material review; no unchecked table values adopted |
| SRC-RD53A-MODULE-ASSEMBLY-2022 | A. Petrukhin for ATLAS ITk Pixel Collaboration, arXiv:2212.09392v1, 2022-12-19 | §1 PDF2; §2 PDF3–5; §3 PDF5–7 | PM-F06: RD53A quad assembly/testing precedent |

## Sourced facts

| Claim ID | Classification | Source-specific fact | Source/locator |
| --- | --- | --- | --- |
| PM-F01 | FACT | RD53A is a demonstrator with multiple front-end variants, not a uniform final experimental production chip | SRC-RD53A abstract/PDF1 and §1/PDF4 |
| PM-F02 | FACT | Manual v3.51 describes a 20.0 mm × 11.6 mm die | SRC-RD53A abstract and Fig1/PDF5 |
| PM-F03 | FACT | Matrix 400 columns × 192 rows; pitch 50 µm × 50 µm | SRC-RD53A §1/PDF4, §2/PDF6 |
| PM-F04 | FACT | Bottom wire-bond pads are separated from first bump row by 1.7 mm, permitting bonding after sensor flip-chip | SRC-RD53A §2/PDF6; §4/PDF15 for pad geometry |
| PM-F05 | FACT | RD53A supports shunt-regulated serial operation and direct internal rail supply for tests; separate PLL/output-driver pads require external rail connections | SRC-RD53A §3/PDF8 |
| PM-F06 | FACT | Published RD53A quad assemblies combine sensor, bump-bonded chips and glued flex; assembly includes metrology, wire bonding and module testing | SRC-RD53A-MODULE-ASSEMBLY-2022 §1–3/PDF2–7 |

**Source discrepancy:** the CERN CDS record abstract for SRC-RD53A describes
11.8 mm height; the opened v3.51 manual abstract and Fig1 describe 11.6 mm.
PM-F02 is a fact about that manual, not a certified inventory dimension or a
tolerance interval. No final fit may use either until the stock die/mechanical
drawing is identified. Catalogue metadata and any conditional illustrations must
retain this distinction.

## Inferences and uncertainties

| Claim ID | Classification | Derivation | Validity/uncertainty |
| --- | --- | --- | --- |
| PM-I01 | INFERENCE | For the conditional RD53A matrix, readout footprint = (400×0.050) mm × (192×0.050) mm = 20.0×9.6 mm² = 192 mm² | Pixel count×pitch; sensor guard/edge/seams and mapping not included |
| PM-I02 | INFERENCE | Conditional manual die area = 232 mm²; footprint/die-area ratio = 192/232 = 82.8% | Aggregate arithmetic; not module active fraction or measured detection efficiency |
| PM-I03 | INFERENCE | n identical chips give n×192 mm² readout footprint and n×232 mm² die silicon area in this reference case | n=1,2,4 are alternative design choices; no actual module dimensions implied |
| PM-I04 | INFERENCE | Larger modules can amortize connector/flex edge contributions; extra routing, assembly losses and support may reverse the benefit | Must evaluate actual spatial BOM and yields, not infer material from chip count |
| PM-I05 | INFERENCE | If independent chip/hybrid acceptance probability is y and other assembly steps succeed with probability a_n, module yield is approximately a_n y^n | Illustrative model only; no numerical yields claimed, correlations/rework can invalidate independence |

## Proposed nODD choices

Every choice is **NODD DESIGN CHOICE — proposed; human approvers: pending**.

| Claim ID | Proposed choice | Rationale/alternatives | Consequences |
| --- | --- | --- | --- |
| PM-C01 | Compare compact A and quad B before selecting family | Reuse and low material depend on host constraints | Keep both live through first technical review |
| PM-C02 | Start from conventional planar silicon sensor with inventory-compatible bump mapping; retain qualified 3D sensor as conditional high-fluence alternative | Planar offers simpler reusable tile path; irradiation/lifetime unknown | No sensor thickness, bias or depletion/fluence claim frozen |
| PM-C03 | Keep bond peripheries accessible; flex glued on sensor backside with cutouts/edge routing | Established hybrid-module assembly route; alternatives must demonstrate pad access | Include wire-loop and tool clearances explicitly |
| PM-C04 | Candidate flex uses polyimide dielectric and copper traces; glue is a separately characterized adhesive; avoid blanket protective potting or unqualified underfill | Remove unnecessary areal material without pretending components massless | BOM grades, coverage, density and radiation/thermal compatibility unresolved |
| PM-C05 | Conduct heat from chip backs through qualified adhesive/contact into local support; put pipes/optical conversion on shared structure | Avoid module-local pipes and bulky optical boards | DES-002 must demonstrate path, bend/strain relief and shared-service allocation |
| PM-C06 | Preserve electrical isolation, grounding and fault controls; compare serial power with independently supplied module test mode | Shunt-regulator capability is not qualification of a full chain | Chain choice, headroom, bypass and isolation unresolved |
| PM-C07 | Use the same named component/interface schema for both options | Enables reuse without forcing identical physical flex designs | One-chip harness is not automatically electrically identical to quad harness |

## Dimensions, materials, interfaces, and identifiers

The following are proposed symbolic parameters under PM-C01–C07, with SI/DD4hep
units at implementation. They are not missing material to be silently assigned
zero. Actual values require public evidence or an explicit reviewed design choice.

| Parameters | Meaning and units | Basis/gate |
| --- | --- | --- |
| D_x,D_y,t_die; N_col,N_row,p_x,p_y | Die dimensions/thickness [mm], counts and pitch [µm] | Exact inventory drawing/mask; PM-F02–03 only conditional reference |
| S_x,S_y,t_sensor; e_guard,g_chip | Sensor extent/thickness and guard/interchip clearances [mm] | Sensor vendor/process, bump map and rated bias; PM-C02 |
| t_bump,V_bump,N_bump | Standoff [µm], individual alloy volume [mm³], count | Actual hybridization process; PM-C03; no solid full-area bump layer |
| t_flex, t_Cu, c_Cu; A_flex | Dielectric/copper thickness [µm], copper coverage [fraction], flex area [mm²] | Layer stack, trace/current/link design; PM-C04 |
| t_glue,A_glue,rho_glue; V_passive | Bondline [µm], actual bonded area [mm²], density [g/cm³], components [mm³] | Coupon metrology and BOM; PM-C04 |
| h_bond,k_bond,V_bond | Loop height/tool clearance [mm], bond material volume [mm³] | Bond process/drawing; PM-C03 |
| A_contact,t_contact,R_contact; P_chip,max | Thermal area [mm²], layer [µm], resistance [K/W], worst operating dissipation [W] | Inventory mode, regulator losses, irradiation and coolant/load study; PM-C05–06 |
| C_mount,C_HV,C_power,C_data | Datum/contact, bias/isolation, power and data contracts | Reviewed pad map, tolerance/electrical load budget; PM-C07 |

Proposed local convention (PM-C07): x along chip columns, y along rows, +z
from chip backside toward sensor backside; die orientations are explicit transforms
so outer pad edges are preserved. Sensor active mapping is separate from sensor
silicon. Proposed stable identity tuple is module-family/module-instance/chip-index/
pixel-column/pixel-row, with orientation kept in transforms. Allocation/ranges and
ACTS/DD4hep mapping await the identifier ADR; this is not a production ID scheme.

Material identities are provisional choices, not facts: silicon sensor and ASIC,
supplier-selected bump alloy, dielectric/conductor flex, qualified adhesive,
qualified bond wire, passive components and mounting/contact material. No density,
X0, lambda or effective mixture is invented here. Do not homogenize until composition,
volume fractions, preserved areal mass/X0 and validation target are specified.

## Material budget and acceptance implications

Under PM-C04–05, compute an explicit BOM rather than infer the budget from the
sensor thickness alone. For each species j, mass is rho_j V_j; areal mass is
sum(rho_j V_j)/A_useful. Include silicon, real bump volume, patterned flex,
all adhesive coverage, wire bonds, decoupling/HV components, contact/mount pieces,
and an allocated share of support, pipe, coolant, power/data service and connectors.
These formulae are **INFERENCE PM-I06**, dimensional accounting from the
proposed BOM; uncertainties propagate from supplier dimensions and coverage.

For a specified ray, X/X0 = sum(l_j/X0_j) and lambda contribution = sum(l_j/lambda_j)
using physical path lengths and validated constituent material definitions
(**INFERENCE PM-I07**). Spatial copper/glue islands, module seams and oblique
crossings matter; an average budget alone conceals them. Report per-module total,
per-readout-footprint total and per-usefully-covered-host-area total separately.
Unknown fields remain unknown, and no numerical material reduction is claimed.

Worst-case module heat is sum chip electrical dissipation including shunt headroom,
sensor leakage heat V_bias I_leak and passive losses (**INFERENCE PM-I08**, energy
balance). Electrical test load is not an irradiated installed thermal envelope.
An initial contact network gives delta T ≈ P R_thermal (**INFERENCE PM-I09**,
steady linear approximation); thermal coupling, leakage feedback, contact variation
and coolant excursions require analysis and test. No allowable temperature is selected.

## Alternatives considered

- [Alternative A: compact one-/two-chip family](inputs/DES-001-compact-modules.md)
  and [drawing](figures/DES-001-compact-modules.svg).
- [Alternative B: reusable four-chip module](inputs/DES-001-quad-modules.md)
  and [drawing](figures/DES-001-quad-modules.svg).

| Criterion | Compact A | Quad B |
| --- | --- | --- |
| Reuse/type count | Common die/interface with one/two-chip sensor/flex variants | Single quad design, orientation reused; fewer assemblies for same footprint |
| Curvature/irregular boundaries | Smaller rigid footprint fits tight host constraints more readily | Larger footprint may need overlap/tilt or leave wedge-edge losses |
| Material | More repeated module-edge/service contributions | Potential edge amortization; larger flex/routing and support not free |
| Manufacturability | Smaller hybrid and test/replacement unit | Public RD53A assembly precedent; larger sensor and glue/metrology control |
| Yield/failure | Smaller lost area per rejected module | More chips/sensor area at risk in one hybrid; chip-level masking may retain partial use |
| Power/thermal | Fewer chips per contact/service unit | Higher total module heat/current; distributed chip contacts essential |
| Common sensor seams | One/two-chip layout must expose real edge mapping | Interchip discontinuities remain in common sensor; not four seamlessly active dies |

This is the Tracking Engineer comparison, not project approval.

### Project Coordinator recommendation

The [separate Coordinator assessment](inputs/DES-001-coordinator-review.md)
recommends A1 as the first isolated PROTOTYPE qualification study and B as the
parallel high-area coverage candidate. This is **NODD DESIGN CHOICE — proposed;
human approvers pending**, an order for obtaining evidence rather than a final
production selection. Keep A2 documented but introduce an additional production
type only when coverage/material evidence justifies its qualification cost.

Compare B alone with B plus a compact type at identical useful coverage and
operating conditions. Actual occupied-envelope tiling, full spatial BOM/service
allocation, thermal/electrical qualification and accepted-area yield decide the
family. No numerical material winner is demonstrated. Chip inventory and its
mechanical discrepancy, host volume and operating requirements remain selection
gates; AI Coordinator advice provides no human sign-off.

## Risks and open questions

| Risk/question | Impact | Owner | Gate |
| --- | --- | --- | --- |
| Exact RD53 inventory and die-size discrepancy | Wrong geometry, mask or electrical assumptions | Tracking Engineer + human inventory owner TBD | Before dimensional freeze |
| Pixel volume/fluence/rate/lifetime undefined | No final sensor, module size or data/power capacity | Coordinator + tracking/physics | Before family selection |
| Hybrid vendor, thinning, sensor edge/bump map | Bond access, yield, fragile dies and inactive areas | Tracking Engineer + supplier expert TBD | Technical/expert review |
| Flex routing/link integrity/serial faults and HV isolation | Added copper/parts and correlated failures | Readout/electrical reviewer TBD | Before sign-off |
| Thermal/support shared-service architecture | Material advantage may disappear; thermal runaway | Future DES-002 owner TBD | Before integration authorization |
| No qualified densities/coverage/tolerances yet | Budget and assembly fit unquantified | Materials/mechanical reviewer TBD | Before sign-off |

## Validation plan

No geometry, thermal certification, manufacturing or detector-performance tests
have been executed for this proposal. Documentary checks do not validate hardware.

| Stage | Requirements | Planned evidence/criterion |
| --- | --- | --- |
| Inventory/interface audit | PM-R01,R05 | Chip revision, supplier drawings, pixel/pad mapping, known quirks; reconcile source discrepancy without guessing |
| Comparative engineering | PM-R02–R04 | Dimensioned layouts and patterned BOM, total service shares, manufacturing/yield sensitivity, electrical capacity and worst-mode thermal network; limits set by human review |
| Coupons/assembly qualification | PM-R04,R05 | Hybrid continuity, opens/shorts, bond pulls, metrology, leakage/bias, configured-chip/source response, thermal cycles and link/power transients; sampling/tolerances TBD |
| Later isolated PROTOTYPE | PM-R03,R05 | Deterministic compact parsing/construction, counts, transforms, IDs, dimensions, mass and directional X0/lambda scans; agreed tolerances TBD |
| Later signed-off integration | All | Overlaps, sensitive crossings/eta-phi acceptance, Geant4 smoke, ACTS conversion/navigation, approved-reference regression |

Future results must identify exact commit, configuration, tool versions, commands,
seed where applicable and justified tolerances. No acceptance threshold or reference
output may be inferred from a visually plausible drawing.

## Review and implementation tracking

| Role | Assigned human | Scope | Evidence |
| --- | --- | --- | --- |
| Technical reviewer | TBD | Chip/mask/module/readout feasibility | Pending |
| Domain expert | TBD | Hybridization, sensor, power, thermal and material realism | Pending |
| Approver | TBD | Exact design revision and open conditions | Pending |
| Validation reviewer | TBD | Reproducible requirements-to-evidence mapping | Pending |

Use the [sign-off template](../signoff/TEMPLATE.md) for identified human approval
of an exact revision. Design approval and production implementation remain separate.
AI role assessments provide advice only and cannot grant human sign-off.
