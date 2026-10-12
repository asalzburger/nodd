# DES-010 input — pixel supports and service routing

- Status: **PROTOTYPE research input; working hypothesis only.** PR #24 did not
  approve a tracker design. No production integration or human sign-off.
- Created: 2026-09-29.
- Scope: estimates for route reservation, using public TDR and later primary
  engineering evidence; not a completed cable schedule or thermal design.
- Module input: DES-001 at `214747a3c83c140caa6c4ae9c3fb6486ac5cb825`,
  as pinned in [DES-009](../DES-009-module-populated-layouts.md) and
  [review models](../../../tools/module_layout/review_models.json). The current
  module proposal excludes external supports and services. DES-002 is a planned
  support topic in PROJECT.md; no local DES-002 design exists at inspection.

## Source facts and their limits

All TDR references below mean **SRC-ATLAS-TDR-030**, the catalogue's local edition
with SHA-256
`14ec26bfb376c7a7a6fba2d06819a30b3ef6dc378508911ae7e90c3a8833dd12`.
PDF pages are one-based; printed page = PDF page − 22 for these locations.
The [official public TDR](https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/UPGRADE/CERN-LHCC-2017-021/)
is historical engineering evidence, not the current ITk production specification.

| ID | Class | Fact and exact locator |
| --- | --- | --- |
| PX-SF01 | FACT | TDR §11.1.1, PDF 282/printed 260: the proposed serial powering chain contains four-chip modules; the DCS bus limits the chain to 16 such modules. Single/double modules need their own electrical implementation; they must not be silently combined into virtual quads. |
| PX-SF02 | FACT | TDR §11.1.2, PDF 283–284/printed 261–262: bias can be shared, but voltage differences along a chain may require multiple HV lines; a dedicated HV return remained an option. §11.1.3 separates local Type-0 services, PP0 and Type-I services leading to PP1. |
| PX-SF03 | FACT | TDR Table 11.1, PDF 286/printed 264: nominal quad current 5.6 A and module voltage 1.4 V; chip dissipation 0.5 W/cm². §14.2.1 PDF 337–338/printed 315–316 budgets 0.5 W/cm² electronics +0.1 W/cm² sensor +0.1 W/cm² services. The last term assumes average chains longer than 7.5 modules. These are TDR estimates, not measured RD53i power. |
| PX-SF04 | FACT | TDR §10.3.1 PDF 263/printed 241 has one dedicated electrical clock/command stream per module. Table 10.2 PDF 266/printed 244 has 1, 2 or 4 FE chips per data link, depending on layer and trigger scenario. Aggregation depends on occupancy, electronics and bandwidth; it is not implied by geometrical grouping. |
| PX-SF05 | FACT | TDR §13.2.2 PDF 309/printed 287: prototype barrel titanium evaporator 2.5 mm ID, 150 µm wall; cooling cells use pyrolytic graphite and a cooling block. §13.3.2 PDF 320/printed 298: endcap prototype cooling pipe 2.275 mm OD. |
| PX-SF06 | FACT | TDR §13.2.3 PDF 313–314/printed 291–292: endcap half-rings are carbon-fibre/carbon-foam sandwiches with embedded pipe and bus tape, mounted in service-bearing half-cylinders. §13.4.2 PDF 325–326/printed 303–304 sends Type-I services along the cylinder to the high-z flange. |
| PX-SF07 | FACT | TDR §13.4.1 PDF 324/printed 302: example local flex uses 9 µm copper on 35 µm polyimide and a 20 mm width; the layout uses multilayer flexes and separate power/data connections. This does not specify total finished flex thickness or the present production design. |
| PX-SF08 | FACT | TDR §13.2.1 PDF 308/printed 286 requires pipe joints to accommodate orbital welding and distinguishes titanium internal pipes from external stainless-steel pipes/electrical breaks. §14.2.1/Table 14.2 PDF 338–339/printed 316–317 distinguishes 324 boiling channels from 32 grouped loops at PP1. Those are whole-ATLAS layout counts, not nODD requirements. |
| PX-SF09 | FACT | TDR Table 14.1 PDF 336/printed 314 explicitly labels its last four pixel entries as **total cross sections**, with no cable counts. They appear under a diameter column with ambiguous units. They cannot be used as individual cable diameters or converted to areas without additional evidence. |
| PX-SF10 | FACT | SRC-ATLAS-ITK-PIXEL-STATUS-2023, slides 15–16: Type-I LV uses coax; HV/monitoring use twisted pairs; data uses twinax to external optoboxes. The twinax drawing is 1.12±0.08 mm wide and 0.71±0.08 mm high. These are cable outer dimensions, not conductor diameters. |
| PX-SF11 | FACT | SRC-ATLAS-ITK-PIXEL-SERVICES-2022, slide 17: one illustrated power/HV/monitoring/interlock bundle has 6.35×4.3 mm bounding dimensions; another woven arrangement has 8.87×3.65 mm bounding dimensions. The slide explicitly reports prototype ribbonisation problems. Neither drawing supplies a certified final nODD or ITk cable schedule. |
| PX-SF12 | FACT | SRC-ATLAS-ITK-PIXEL-COOLING-2024, PDF 2 §3–4/Fig 1/Fig 3: tested endcap system has 0.6 mm-ID capillaries, 3 mm-ID exhaust lines, longest exhaust 2 m, evaporator length about 0.9 m; the illustrated operating point uses 300 W/evaporator. The 3 mm figure is **inner** diameter, not route envelope. |

The TDR pages 268, 309, 320, 324, 336, 339 were rendered; 309, 320, 336 were
visually checked. The later cable drawings were rendered and visually checked.
Later power routing uses coax whereas the 2022 prototype bundle drawing uses an
LV pair: retain these as different engineering examples rather than combining
their conductors into a fictitious final design.

## Reusable estimate for the nODD working hypothesis

Every item in this section is a **NODD DESIGN CHOICE — proposed**, except the
explicit arithmetic labelled **INFERENCE**. Human approvers are pending.

Use actual module/chip counts per route and per detector end. Keep electronics
and hydraulic grouping separate. Recompute counts after any removed endcap row;
round at each physically independent group rather than rounding detector totals.

| Proposed study input | Rationale and sensitivity |
| --- | --- |
| Homogeneous chains capped at 32 chips **and 16 physical modules** | This means at most 8 quads, 16 doubles or 16 singles. The quad limit lies near the TDR service-loss assumption. A1/A2 serial powering is a new electrical hypothesis; do not assume 32 singles can be treated as 8 virtual quads. Short chains ending at an interface still require a full cable bundle. Keep every chain within one independently serviceable local structure; compare shorter chains. |
| Reference: one uplink per module plus one command link per module; conservative: one uplink per chip plus one command link per module | The reference assumes quad data aggregation and requires an explicit electronics/occupancy review. TDR aggregation is precedent, not evidence that a single link suffices for every nODD quad. The conservative case removes this aggregation; a future high-bandwidth scenario may need more than one uplink/chip and must be tested separately. |
| 1.0 mm² route footprint per differential link | **INFERENCE:** nominal bounding area is 1.12×0.71=0.7952 mm²; simultaneous upper drawing dimensions give 1.20×0.79=0.948 mm². Rounding to 1.0 mm² is the routing choice. Ribbon tape, connectors and external tray allowance are additional. |
| 35 mm² footprint per ancillary chain bundle | **INFERENCE:** two 2022 bounding boxes have areas 27.305 and 32.3755 mm². Rounding the larger to 35 mm² is an order-of-magnitude routing choice for LV supply **and return**, HV, monitoring and interlock together. It is not 35 mm² of copper and does not fix chain current or connector size. Do not add a second LV-return cable to this already paired bundle. |
| Two 4 mm-OD transport lines per hydraulic circuit | Deliberate inlet/exhaust envelope hypothesis: larger than the TDR evaporator and compatible in scale with a 3 mm-ID return plus wall. The inlet is conservatively oversized. **INFERENCE:** combined circular footprint=2π(4/2)²=25.1327 mm². Do not use the 2.8 mm evaporator OD for the return trunk. |
| 300 W per circuit as initial grouping ceiling; compare 150 W | Based on the scale of the later measured example, not a transfer of its hydraulic qualification. Impose separate circuits for independent half-staves/ring sectors and then split any group above this study ceiling. Long paths, elevation and power asymmetry may require further splitting. |
| 6 mm local support keep-out beyond the existing module body | A first reservation for a 2.8 mm evaporator, thermal foam/cell, facesheets and adhesive. It is a geometry allowance, not 6 mm of solid carbon or a verified support stack. The TDR does not give a universal support thickness. Compare 4–8 mm pending a mechanical design. |
| 1 mm tray/support skin on each side and 2 mm clearance to each neighbouring package | Together these add 6 mm to the filled routing depth. These dimensions are explicit assembly hypotheses, not measured tolerances. Tray ribs, clips, grounds and local patch panels need separate spatial envelopes. |
| 50% usable cable packing in reserved azimuthal sectors | This is an engineering reserve for mixed cable/tube shapes and assembly, not an empirical packing fraction. Keep the occupied azimuthal fraction separate; e.g. sectors covering half the circumference provide only half the annular area. Compare 40–70% packing. |
| 50 mm nominal cable/pipe bend pocket; compare 25–75 mm | Provisional space at radial-to-axial turns and patch-panel access. No checked source establishes a common minimum bend radius. A routed 3D harness and vendor bend rules must replace this allowance before approval. |

For each signed-end route, calculate:

```text
chain_length = min(16, floor(32 / chips_per_module))  # homogeneous groups
N_power = sum_over_compatible_local_groups ceil(N_modules_in_group / chain_length)
N_data = sum_over_modules ceil(N_chips_in_module / chips_per_uplink)
N_command = N_modules
P_group = 0.7 W/cm² × active_chip_matrix_area_in_group_cm²
N_cool = sum_over_independent_local_groups max(1, ceil(P_group / P_circuit_limit))
A_cables = (N_data + N_command) × 1.0 mm² + N_power × 35 mm²
A_pipes = N_cool × 25.1327 mm²
A_route = (A_cables + A_pipes) / packing_fraction
```

The 0.7 W/cm² estimate is an **INFERENCE** from PX-SF03 conditional on adopting
its heat-density model; it must be evaluated using chip matrix area, not gross
silicon including guards. For a DES-001 chip matrix of 384 mm², this is 2.688 W
per chip. Chip power already includes local services in this estimate: adding a
second 20% cable heat allowance would double count. Small modules and short
chains may have higher relative service loss; the 0.7 W/cm² estimate is not a bound.

For an annular axial route of inner radius R and radial depth g available over
azimuthal fraction f, the exact available transverse area is
`f × π × ((R+g)² − R²)` before skins and clearances. Solve for the cable-filled
depth rather than assuming the full 2πR circumference is usable. At a radial
turn use the transverse section of that **radial** route, not the longitudinal
annulus formula. Where barrel services join endcap services, their loads add.

As a count sanity check, the retained PR #24 working case has 4,838 pixel modules
and 14,558 active chip patches. Equal signed-end routing would carry 2,419 modules
and 7,279 chips/end before row removal. With unaggregated uplinks this gives 9,698
data+command links/end. The mixture is 799 singles and 1,620 quads/end; global family division gives
a **lower bound** of 50 chains serving single-chip modules plus 203 chains serving quad modules, or
253 power bundles/end. Real structure grouping can only increase it. These numbers
are not the final DES-010 routing inventory.


For the proposed removal of 576 quad pixel endcap modules, the corresponding
arithmetic example is 799 singles + 1,332 quads = 2,131 modules and 6,127 chips
per end. This gives at least 217 power bundles and 55 cooling circuits/end from
global family/thermal rounding alone. Local topology will increase those counts.
Reference data+command area is 4,262 mm²/end, versus 8,258 mm²/end without
quad aggregation. Including ancillary power bundles and pipes gives lower-bound
raw footprints of 13,239 mm²/end and 17,235 mm²/end. With a separately chosen
25% spare reserve these become 16,549 and 21,544 mm²/end. These are **INFERENCE**
under the explicit electronics/hydraulic assumptions; they do not authorize
removing a row or assert that a particular corridor fits. A high-demand case
that fails capacity should remain a recorded failure and constrain the later
optimization, rather than being reduced silently to fit the drawing.

## Mechanical and routing implications

The pixel extraction corridor should remain continuous outside all pixel
endcap module/support envelopes and inside the short-strip package. It must
carry the sum of pixel barrel and endcap services by the downstream end. A gap
that passes only one ring's cables is insufficient. Ring outer rows may need
removal to accommodate the corridor and local support lips; remove whole
assemblies, preserve identifiers, and record lost sensor area and counts.

Barrel pigtails run along their own staves to a barrel/endcap interface pocket,
then turn radially to the corridor and turn axially along the endcap outer rim.
Route drawings should show supply and exhaust separately, Type-0 connections,
the first aggregation/patch-panel region, and the proposed accessible optobox
position. Optical conversion must not be assumed inside the pixel package merely
to shrink cables. Keep HV/data cables, warm power conductors and subcooled
capillaries physically segregated where required by the later engineering design.

A mechanical mockup should expose support envelopes, service trays and turn
pockets independently. A pass of box/route overlap checks establishes only
geometric reservation; it cannot demonstrate stiffness, pressure integrity,
thermal stability, electrical losses, signal integrity or constructability.
Actual materials/masses remain unmodelled until their constituent BOM exists.

## Source catalogue additions for the parent design

The following are primary public sources inspected 2026-09-29. PDFs are retained
only in ignored `reference/cache/`; redistribution permission was not established.
The parent task must catalogue them before these claims become normative inputs.

| Proposed source ID | Bibliographic record and inspected local copy |
| --- | --- |
| SRC-ATLAS-ITK-PIXEL-STATUS-2023 | Stefano Passaggio for ATLAS ITk, *The ATLAS ITk Pixel Detector — Status and Roadmap*, HSTD13, 2023-12-04; [public slides](https://indico.cern.ch/event/1184921/contributions/5574639/attachments/2765210/4816495/Passaggio%20-%20The%20ATLAS%20ITk%20Pixel%20Detector%20-%20Status%20and%20Roadmap.pdf), slides 15–16. `reference/cache/DES-010-pixel-status-2023.pdf`; SHA-256 `ea1dc3fab0fae65b8d5f15b878d87c2caef0409d5492eb433371a6605a1d964e`. |
| SRC-ATLAS-ITK-PIXEL-SERVICES-2022 | Craig Buttar for ATLAS ITk Pixel, *Status of the ATLAS ITk Pixel Project*, Pixel2022, Santa Fe, 2022-12 (day unverified); [public slides](https://indico.cern.ch/event/829863/contributions/4479438/attachments/2565663/4433206/ATLAS-Pixel-Detector-Pixel2022-CMB-v5.pdf), slide 17. `reference/cache/DES-010-pixel-2022.pdf`; SHA-256 `063f92a79881bb64897016c24f9bca8b6e9f0b463b978fc2f323358521b4f0d1`. |
| SRC-ATLAS-ITK-PIXEL-COOLING-2024 | Sonia Carrà for ATLAS ITk, *ATLAS ITk Pixel Outer Endcap CO₂ cooling system prototypes*, ATL-UPGRADE-PROC-2024-001, 2024-06-20; [public preprint](https://cds.cern.ch/record/2901596/files/ATL-UPGRADE-PROC-2024-001.pdf), PDF 2 §3–4/Fig 1/Fig 3. Later journal DOI 10.1016/j.nima.2024.169813; the inspected copy is the preprint. `reference/cache/DES-010-pixel-cooling-2024.pdf`; SHA-256 `fa505e6d4b9d54a14b5228765bd50cc80682794bfb304199687ef68937be7e19`. |

Browser PDF fetching returned 403 for these sources; direct public HTTPS
downloads succeeded and their PDF contents were inspected locally. No
authentication or private collaboration source was used.
