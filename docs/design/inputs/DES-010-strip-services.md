# DES-010 input — Strip supports, cooling and service capacity

- Date: 2026-09-29.
- Status: **DRAFT / PROTOTYPE; PR #24 supplies an unapproved working hypothesis.**
- Scope: public TDR engineering precedents and explicit space-reservation scenarios.
  No electrical, hydraulic, thermal or mechanical qualification is claimed.
- Governing plan: [DES-005](../DES-005-tracker-system-plan.md), TT-P04–07;
  geometry input: [DES-009](../DES-009-module-populated-layouts.md).
- AI-assisted source contribution; human design approval remains pending.

## Source identity and reading boundary

`SRC-ATLAS-TDR-025`: ATLAS Collaboration, *Technical Design Report for the ATLAS
Inner Tracker Strip Detector*, CERN-LHCC-2017-005 / ATLAS-TDR-025, local cover
15 April 2017, [public record](https://cds.cern.ch/record/2257755). The inspected
556-page file is `reference/pdfs/ATLAS-ITk-Strip-TDR.pdf`, SHA-256
`f1ce247fb807a37b0e9065c02764f39f041fc66d266c824828cad9b2915d2bff`.
The public ATLAS index gives 13 April 2017; retain the local cover date for this
edition rather than silently reconciling submission and document dates.

`SRC-CMS-TDR-014`: CMS Collaboration, *The Phase-2 Upgrade of the CMS Tracker*,
CERN-LHCC-2017-009 / CMS-TDR-014, 1 July 2017,
[public record](https://cds.cern.ch/record/2272264). The inspected file is
`reference/pdfs/CMS-Phase2-Tracker-TDR.pdf`, SHA-256
`642f37707fbe2654c99ae3e9c116297c537d2f048370602ca7de92e5d79a1f54`.

Access date for this inspection is 2026-09-29. Public CDS record pages returned an
access challenge. Existing local catalogue copies were readable; live-public
byte equality is unverified. These are TDR-era design facts, not assertions
about final production hardware. No PDF is redistributed. Page references below
are **printed / one-based PDF**; CMS page numbers coincide in these sections.
ATLAS Table 9.5 and CMS Table 5.1 were also rendered and visually checked.

## FACT — dimensions and topology actually supported by the TDRs

| ID | Fact | Precise source locator |
| --- | --- | --- |
| SS-F01 | Stave/petal cores place cooling between two CFRP faces, with bus tapes and modules outside. The 5 mm core, 0.15 mm CFRP facing, 0.17 mm bus tape, 0.10 mm facing-to-foam adhesive and 0.10–0.20 mm sensor-to-bus adhesive are thermal-model inputs. These are distinct layers, not a 5 mm complete assembly. | ATLAS §9.2.1 pp189–191 / PDF215–217; Table 9.5 p200 / PDF226. |
| SS-F02 | The thermal model uses a titanium pipe with 2 mm ID and 0.14–0.15 mm wall; a manufactured prototype is reported as 2.275 mm OD. Connections use 2.5 mm OD, 0.2 mm wall interface tubes and two insulating breaks. | ATLAS Table 9.5 p200 / PDF226; §9.5.1 p203 / PDF229; §9.2.1 p191 / PDF217. The model and prototype dimensions are different representations, not an exact shared specification. |
| SS-F03 | A support has services at one end and an internal U-return. Stave services exit near z≈1.4 m; petal services near r≈1 m. Both arms contribute cooling. Petals have 18 modules, nine per face; the outer rings can have only one tube length beneath a module. | ATLAS §9.2.1 p190 / PDF216 and §9.2.3 p193 / PDF219. |
| SS-F04 | Bus tapes distribute LV, HV, data and control. Individual copper layers are 17 µm; polyimide and glue layers 25 µm. Differential data tracks have 100 µm width, 100 µm intra-pair gap and 250 µm gap between pairs. Target LV round-trip drop is <1 V; LV return drop <200 mV. | ATLAS §9.3.1 pp196–197 / PDF222–223, Fig. 9.6. Full tape thickness is the separate 0.17 mm thermal input above; copper is patterned, not a solid three-layer sheet everywhere. |
| SS-F05 | One strip bus-tape face has one LV and four HV supply channels. Table 17.3 uses 14 barrel modules per face; at 11 V the quoted worst-case bus currents are 8.2 A for inner short strips and 4.1 A for outer long strips. | ATLAS §17.2 p378 / PDF404; Table 17.3 p381 / PDF407. This architecture is not a power prediction for nODD strixels. |
| SS-F06 | Each short-strip barrel face uses two optical uplinks and one downlink; the long-strip/endcap face uses one lpGBT. Uplink raw rate is 10.24 Gbit/s, with 8.96 Gbit/s user data. The drawing of four fibres per complete stave in Fig. 11.4 cannot be applied universally to the later short-strip six-fibre case. | ATLAS §12.1 p270 / PDF296, Fig. 12.1; Fig. 11.4 p253 / PDF279. |
| SS-F07 | A barrel service module serves eight staves and contains cooling, cables and fibres; a proposed folded aluminium service duct wall is 0.5 mm. Cooling is manifolded by roughly 4–8; single fibres become ribbons with MT8/MT12 terminations. Endcap trays run along the outer radius and connect radially to petals. | ATLAS §11.4.2–3 pp262–267 / PDF288–293. |
| SS-F08 | Service patch pipes need stress relief and orbital-weld-head access. Endcap capillaries are coiled to absorb tension. Local cooling-loop fabrication specifies formed internal radii 0.7–2.0 mm, using filler against collapse; this is not a bend-centre radius for a complete external cable/pipe bundle. No universal qualified service bend radius or complete connector envelope follows. | ATLAS §9.5.1 p203 / PDF229 (rendered and checked); §11.4.2 p263 / PDF289; §11.4.3 p266 / PDF292; §17.8 pp389–390 / PDF415–416. |
| SS-F09 | CMS TB2S has 2.2 mm OD / 2.0 mm ID local cooling pipe, approximately 1.5 mm OD feed capillary, three ladders in series, and approximately 10 mm OD return pipes from end manifolds to the bulkheads. | CMS §9.3.1 p203 / PDF203. Small detector pipes do not bound the downstream return trunk. |
| SS-F10 | CMS bulkhead-to-PP1 estimates are 13.4 mm diameter power cable and 3.6 mm diameter multifibre cable; inlet/outlet cooling pipes are 8/12 mm OD and 6/10 mm ID. These are installed outer envelopes, not copper or coolant cross sections. | CMS §5.2, Table 5.1 p91 / PDF91. The table counts both detector ends. |
| SS-F11 | The CMS power grouping has 12 modules, 12 LV and 12 HV channels; the lighter inside-OT connection uses copper-clad aluminium conductors and fans out at PP0. A module is independently serviced. | CMS §3.2.4.1–2 p35 / PDF35. Optical cables upstream of the small service cable have additional aggregation; do not count the 144-fibre upstream cable as one per module. |
| SS-F12 | TDR service-input power is 5.4 W per 2S module and 7.8 W per PS module, assuming 66% two-stage converter efficiency; about 2 W additional HV power is cited for the most irradiated sensors at end of life. A PS sensor assembly has 30,208 connected macropixels. | CMS §3.2.3 p34 / PDF34; §3.3.2.2 p42 / PDF42. 2S power is per two-sensor module, not per face. |

Neither TDR supplies a qualified power/data cable for the exact nODD readout.
The ATLAS text describes conductor voltage-drop targets without enough finished
Type-I cable dimensions to reconstruct its complete routing envelope here.
Use the explicit CMS outer cable dimensions for the geometric benchmark; do not
invent an ATLAS cable diameter from a conductor resistance alone.

## INFERENCE — what scales and what does not

The pinned DES-007 model has 48×96 mm² active strixels at 75 µm×0.5 mm:
122,880 channels per module. It has about **4.068 times** the 30,208 connected
CMS PS macropixels, or 3.912 times their nominal cell density. Those ratios differ
because the active footprint and readout-edge definitions differ. The alternative
75 µm×1.5 mm hypothesis has 40,960 channels. These are channel counts, not ASIC
power or bandwidth predictions. ATLAS's much longer strips cannot supply the
nODD strixel load by simply relabelling an ITk stave.

A deliberately crude equal-power-per-connected-channel proxy multiplies the
complete 7.8 W PS service load by 122,880/30,208, giving **31.73 W per strixel
module**. The unscaled comparator is 7.8 W. Across the pre-cut 11,744 modules
these give 91.60 and 372.62 kW. Both remain **sensitivity scenarios**, not lower
and upper physical bounds: the PS includes a second strip sensor and stub logic,
while nODD's ASIC, operating conditions and link topology are unqualified.
Sensor leakage, extra converters and service losses remain separate. For long
strips use the 5.4 W complete CMS 2S module only as a comparator; multiplying by
two again would double-count its paired sensors.

Inserting the complete SS-F01 support between two 0.30 mm sensors requires
sensor mid-plane separation

`5 + 2×(0.10 + 0.15 + 0.17 + 0.10..0.20) + 0.30 = 6.34..6.54 mm`.

It therefore **does not fit** the retained DES-008 5 mm separation. A custom
thinner core or an external cold rail is needed. Adding the TDR core silently
inside the existing sandwich is invalid. Similarly DES-007's 2 mm trial body
omits this shared support. For reservation accounting the support stack excluding
sensor and sensor glue is 5.84 mm. Per square metre of two-faced projected support
area its two CFRP skins occupy 0.30 litres; its two bus-tape layers occupy
0.34 litres; its nominal 5 mm core occupies 5 litres. Core occupancy includes
pipes and foam and cannot all be assigned one honeycomb density. These are
volume identities, not a material budget or mass estimate.

## NODD DESIGN CHOICE — two reproducible routing benchmarks

The following choices are engineering-space **hypotheses, approving humans
pending**. They expose demand even while the electronics design is missing.
Keep the input switchable and retain failed high-demand cases. Recompute counts
after removing complete endcap rows; do not use removal as evidence of electrical
feasibility or improve the old coverage denominator silently.

1. Put barrel local-service terminations at each barrel end; route them radially
   through a reserved barrel/endcap interval and then longitudinally on the
   corresponding outer endcap corridor. Short-strip routes lie between short
   and long packages; long routes may use the existing outer tracker-services
   allocation only if the magnetic-vessel/support interface permits it.
2. Count one CMS-sized power plus multifibre bundle per at most **12 complete
   modules**. Round up per disk, barrel half-layer or other independently
   serviceable group; never average away partial groups. The two long-strip
   sensors are one complete module. Each bundle's outer occupied section is
   `π/4×(13.4²+3.6²) = 151.2049 mm²`.
3. For cooling, allow at most **14 short-strip modules per half-stave** or **13
   long-strip pairs per half-stave**, following the current row counts; subdivide
   if future layouts exceed these caps. Use at most **12 complete modules per
   endcap leaf loop**, rounded separately on each disk. This is capacity counting,
   not a claim that rectangular ring modules already form engineered petals.
4. Each leaf has inlet and outlet of 2.5 mm OD (SS-F02); manifold at most eight
   leaf loops into an 8 mm OD feed and 12 mm OD return pair (SS-F10). Their summed
   occupied section is `π/4×(8²+12²) = 163.3628 mm²`. The larger pair replaces
   the leaf pipes after the manifold; sum both only where they physically coexist.
   A manifold bank and its connectors need separate boxes/access allowance.
5. Reference benchmark: usable azimuth fraction `f_phi=0.75`, packing fraction
   `f_pack=0.50`, zero additional spare demand. Conservative benchmark:
   `f_phi=0.50`, `f_pack=0.40`, multiply demand by 1.25 for spare/installation
   allowance. All three parameters are declared nODD choices, not TDR measurements.
   Do not count packing void as solid material. Reserve a further 4 mm total
   for tray walls, separation and edge clearance; this is a coarse geometric
   allowance and does not qualify connectors, welding access or bend radius.
6. Local supports may be reserved as an **external 6.5 mm cold rail** behind the
   existing occupied module box: 5.84 mm comparison stack plus 0.20 mm mounting
   layer leaves 0.46 mm trial clearance. This avoids silently changing the frozen
   internal stereo gap; actual module-to-rail thermal paths and staggered contacts
   need design. This slab is a bounding reservation, not a homogeneous solid or
   an assertion that all overlapping modules can share one planar rail.
7. A radial barrel exit needs a bend/connector reserve as well as bundle area.
   For mockups use configurable 25/50 mm bend-centre-radius cases, explicitly
   **unsourced nODD construction allowances**. Allocate at least the maximum of
   the bend's swept tube/cable envelope, connector/manifold box and cross-section
   requirement. Do not label either value a manufacturer minimum bend radius.
   A 12 mm pipe turned through 90° at 50 mm centre radius needs 56 mm from the
   tangent reference to its extreme outer edge before tolerances/access.

For a corridor at mean radius `R`, required bare cross-section `A` and demand
multiplier `s`, the equivalent radial thickness is

`w = s A / (2π R f_phi f_pack) + 4 mm`.

A real selected annulus must use its exact sector area
`f_phi × π(r_outer²−r_inner²)`, then its packing factor; the mean-radius form is
identical for a uniform annulus. The estimate must be checked at every route
bottleneck and service handoff, not just at the outer end. Sector concentration,
unequal disk populations and manifold placement can dominate the global area.

For scale, the **pre-cut PR #24 hypothesis** has 6,776 barrel plus 4,968 endcap
short-strip modules and 3,425 barrel plus 4,848 endcap long-strip pairs. Its short
barrel has 242 azimuth columns, 28 rows; its long barrel has 137 columns, 25 rows.
Each end has six short disks of 414 modules and six long disks of 404 pairs.
The odd long barrel row is assigned wholly to an end in the actual route ledger;
taking ceil(total/2) below is only a global sizing estimate.

| One-end benchmark before row removal | Short strips | Long strips |
| --- | ---: | ---: |
| Complete modules, symmetric ceiling | 5,872 | 4,137 |
| Global lower-bound number of 12-module harnesses | 490 | 345 |
| Cooling leaf loops: barrel + endcap | 242 + 6×35 = 452 | 137 + 6×34 = 341 |
| Eight-leaf manifold pairs, global ceiling | 57 | 43 |
| Bare cable + trunk area, mm² | 83,402 | 59,190 |
| Example mean radius, mm (illustration only) | 750 | 1,150 |
| Reference equivalent corridor width including 4 mm allowance | 51.20 mm | 25.84 mm |
| Conservative equivalent corridor width including 4 mm allowance | 114.62 mm | 55.20 mm |

The global harness and manifold ceilings in this illustration are **lower than or
equal to** the counts after partitioning by disk/sector. Executable route budgets
must round within those partitions, include the detailed accumulated upstream
loads and display the resulting larger demand. This table is not an accepted
corridor dimension. In particular the second radius extends beyond the 1,140 mm
tracker envelope and refers only to the separate, conditional outer service zone.

As a separate stress case multiply the short-strip harness demand by **4.068**,
rounding upward. This mirrors the connected-channel ratio above and deliberately
scales both power and data housing as a geometry proxy, while retaining nominal
cooling trunks only as a known optimistic assumption. Report a capacity failure
where it does not fit. Do not silently shrink conductor sizes, assign a higher
supply voltage, change electronics topology, or declare the cooling adequate to
make it pass. Local optical aggregation, different supply voltage, serial power
and a 1.5 mm cell fallback are possible later comparisons, each requiring its own
qualified load and hardware interfaces.

## Handoff and remaining engineering questions

Reserve local support, longitudinal corridors, barrel radial exits, endcap radial
feed paths and endpoint manifold/connector space as distinct objects. Removing
inner rows of long-strip endcaps is a permissible geometric way to expose the
short-strip corridor, but carries a measurable active-area and coverage cost.
The parent study must retain each removed module ID/row and its reason.

The current task may establish geometric route continuity and an explicit
capacity scenario. It cannot establish power voltage-drop/current-density limits,
fibre bandwidth, link error margins, coolant heat capacity/pressure drop/dry-out,
service-force transmission, radiation lifetime, thermal expansion, structural
stiffness, assembly tooling or vessel feedthrough clearance. No layer-position
optimization or physical tracker approval follows from this input.

## Adopted executable hypothesis

The final DES-010 configuration reserves **6.6 mm** external strip support depth,
rounding the earlier 6.5 mm input proposal upward. The 25/50 mm illustrative
bend-radius cases above have **not** been implemented or qualified: the current
prototype checks finite joining pockets and declared flow continuity. Review
connector, manifold and bend envelopes before treating it as engineered routing.
The [executed report](../../validation/DES-010-tracker-services.md) is authoritative
for the implemented reservations and their measured consequences.
