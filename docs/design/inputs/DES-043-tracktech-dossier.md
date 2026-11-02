# DES-043 TrackTech input — 2 mm strixel modules and services

> Coordinator note: this is the initial pinned input assessment. The final
> [DES043 prototype](../DES-043-short-strip-service-redesign.md) supersedes
> its91.5mm ring sketch, narrow endcap lands and6..24degree pipe path with
> a703mm target, central16x60mm saddle and3..27degree stadium routing.
> Preserve this input as evidence; its old thermal estimate is not validation
> of the final module.

- Status: **DRAFT / PROTOTYPE; engineering approval pending**.
- Date: 2026-11-02.
- Assignment: `DES043-TrackTech-01`, explicitly supplied TrackTech mandate.
- Examined input revision: `b564308fe2e76da42d0d62c6ba33f9c76876119c`.
- Ownership: this dossier only; no production geometry or shared input changed.
- Scope: a dimensioned short-strip service/module design contribution, with
  electrical, thermal and enthalpy screens. These are conditional engineering
  requirements, not a qualified sensor, ASIC, harness or hydraulic circuit.

## 1. Recommendation and interface to the layout study

**NODD DESIGN CHOICE:** retain the selected 75 µm × 2 mm readout, 48 × 96 mm²
active sensor, 200 µm silicon and 0.5 mm guard allowance. Use one protected
12 V feed per at most 14 modules, with two 8 mm² copper LV conductors inside an
8 mm outer-diameter cable reservation. Retain independent HV circuits and
module-level LV protection. Preserve the complete existing fibre allocation.
Reduce the local LV copper thickness from 0.20 to **0.17 mm**, keeping the
12 mm total width per polarity. Retain the 2.5 mm OD / 0.14 mm-wall local
titanium tubes and 8/12 mm OD bulk feed/return pipes. They are physical floors
pending hydraulic and pressure qualification, rather than channel-scaled items.

**NODD DESIGN CHOICE:** use two parallel cooling circuits per endcap petal,
each serving at most 20 modules. Budget 5 g/s nominal and 7 g/s adverse per
leaf, with maximum operating coolant temperature **−35 °C**. Preserve the
original finite barrel 20 × 64 mm² and endcap 6 × 60 mm² contact footprints.
The module thermal redesign below uses direct graphite inserts to the titanium
pipe, a 0.35 mm graphite spreader and a changed ASIC/hotspot arrangement.
It bypasses the original high-resistance backing/foam path inside those windows.
That change requires a new module/support thermal interface, instrumentation
and qualification; it is not a free benefit of the channel reduction.

For the coordinator's five-ring option with 33 modules per petal, partition
cooling as 17 + 16 modules and power as 11 + 11 + 11. The less demanding
unchanged 30-module petal can use 15 + 15 cooling and 10 + 10 + 10 power.
Do not collapse the three endcap power feeds onto one shared unprotected bus.
If the final layout differs, recompute discrete loads, radial tap positions,
per-sector trunk counts and heat. The dossier does not select the new annulus.

The module **does need redesign**: sensor/readout mask and interconnect mapping,
power/flex/connector and protection topology, ASIC placement/thermal contact,
spreader/backing and pickups. The proposed sensor outline and thickness remain
unchanged. A new sensor die size or new long-strip module is not required by
this proposal. Endcap carrier, local tube routing, manifolds, boards and mounting
interfaces must be redesigned for the extended radius and two circuits.

## 2. Evidence and classification

All repository locators in this section refer to the exact input revision above.
The standalone DES-020/021 inputs deliberately retain the historical 0.5 mm
control. Their engineering and occupied-volume assumptions are input evidence;
they are not a second current readout baseline.

| ID | Classification | Evidence / boundary |
| --- | --- | --- |
| TT43-F01 | FACT — repository contract | `docs/design/inputs/DES-042-strixel-selection.json`: human-selected 2 mm; 30,720 channels/sensor, 8,064 barrel and 4,320 endcap sensors; hardware services unchanged. The human selection is [PR109 comment](https://github.com/asalzburger/nodd/pull/109#issuecomment-6573426341). |
| TT43-F02 | FACT — repository model | `tools/short_strip_barrel/inputs-phi-tilted.json` and `model.py::build`: 288 staves, 14 modules/half, 288 leaf loops and 576 legacy power/fibre harnesses per end. Local rails are two 12 × 0.20 mm² copper conductors; local tube is 2.5 mm OD, 0.14 mm wall. |
| TT43-F03 | FACT — repository model | `tools/short_strip_endcap/inputs.json`, `model.py::rings/build/cooling`: six stations/end, 12 petals/disc, five rings with 4/5/6/7/8 modules per petal, hence 30/petal, 360/disc, 216 legacy power/fibre harnesses and 72 serpentine loops/end. Original centre radii are 289.5, 373.1393, 456.7786, 540.4179, 624.0572 mm. |
| TT43-F04 | FACT — repository comparator | `docs/design/inputs/DES-010-strip-services.md`, SS-F04/F10–12, and DES-042 power model: 7.8 W CMS PS service-input comparator, 30,208 connected macropixels, separate 2 W sensor-leakage comparator, 5 W nODD end-board allowance; CMS outer cable envelopes 13.4/3.6 mm. CMS TDR §3.2.3 p34 and §3.3.2.2 p42; ATLAS Strip TDR §9.3.1 pp196–197 for <1 V local round-trip and <200 mV return-drop screens. These previously curated TDR assertions were read in the pinned repository input; their PDFs were not independently re-read in this assignment. |
| TT43-F05 | FACT — repository representation | `tools/short_strip_barrel/export.py` and `tools/short_strip_endcap/export.py`: legacy power-cable effective volume fractions are Cu 0.20, polyimide 0.30, air 0.50, while the fibre is silica/polyimide 0.50/0.50. These are simulation recipes, not manufacturer cable data. Both modules have eight 23.4 × 23.4 × 0.15 mm³ ASIC fixtures and a 0.20 mm full-area graphite spreader. |
| TT43-F06 | FACT — public source rechecked | `SRC-NIST-CO2-SATURATION-DES002`, [NIST saturation table](https://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID=C124389&Type=SatP&Digits=5&THigh=-30&TLow=-40&TInc=5&RefState=DEF&TUnit=C&PUnit=bar&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=uPa*s&STUnit=N%2Fm), −40/−35 °C rows: liquid/vapour enthalpies 112.90/435.32 and 123.05/436.23 kJ/kg; saturation pressures 10.045 and 12.024 bar. Retrieved bytes match catalogue SHA-256 `bdff4d9ae8c79f3dc6778a3479f1e7514b40723122af20c7ff3160c484d02eb4`. |
| TT43-F07 | FACT — public precedent, not transferred qualification | `SRC-ATLAS-ITK-PIXEL-COOLING-2024`, [CERN preprint ATL-UPGRADE-PROC-2024-001](https://cds.cern.ch/record/2901596/files/ATL-UPGRADE-PROC-2024-001.pdf), 20 June 2024, §1 p1 and §2–4 p2: ITk specifies −40 °C operation and a ≤5 °C loop temperature variation; BabyDEMO can supply −45 °C. Tests use titanium, welded/brazed lines and calibrated capillaries. This supports a colder CO₂ option, not nODD flow/pressure-drop adequacy. Retrieved SHA-256 matches catalogue `fa505e6d4b9d54a14b5228765bd50cc80682794bfb304199687ef68937be7e19`. |
| TT43-F08 | FACT — voltage-interface caution | Proposed catalogue ID `SRC-CERN-BPOL12V-V6-1P9`, [CERN bPOL12V V6 datasheet V1.9](https://power-distribution.web.cern.ch/assets/datasheets/bPOL12V_V6%20datasheet%20V1.9.pdf), pp1–2: 5.5–12 V input and 12 V absolute maximum. This is an available conversion precedent, not a selected part or an nODD qualification. A 12 V distribution name must not expose such a device to overvoltage/transients. |
| TT43-F09 | FACT — insulating interface precedent | Proposed catalogue ID `SRC-HENKEL-STYCAST2850FT-CAT11-2019`, [Henkel CAT11 technical datasheet](https://datasheets.tdx.henkel.com/LOCTITE-STYCAST-2850FT-CAT-11-en_GL.pdf), May 2019, p1 typical mixed material and p2 cured properties: density 2.29 g/cm³ before curing, thermal conductivity 1.28 W/m/K and dielectric strength 15 kV/mm. Typical bulk values do not establish a 0.10 mm, −35 °C, irradiated module bond. |

For TT43-F08 the coordinator must add the catalogue entry before adopting the
new citation: CERN authorship, version V1.9, publication date not established,
access 2026-11-02, temporary inspection file
`/private/tmp/DES043-bpol12v-v1.9.pdf`, 9,485,968 bytes, SHA-256
`c8e0238594cd2165fab9de24db7ec9e891b605a74f8b98902620e7a64021ecad`.
Redistribution terms unverified; do not commit the PDF. NIST and the cooling
preprint already have source entries. For TT43-F09 add Henkel, *LOCTITE STYCAST 2850FT CAT 11 Technical Data
Sheet*, May 2019 (retrieved PDF signature dated 2025-11-27), access 2026-11-02,
public URL as above, temporary file
`/private/tmp/DES043-Stycast2850FT-CAT11.pdf`, 88,842 bytes, SHA-256
`d49ca714a522ac2893214382a71015c45d6920355c75321fd55d4fe89ebb851d`.
Redistribution terms unverified; do not commit the PDF. No source establishes
a ready-made 2 mm nODD ASIC/module or the proposed 8 mm complete cable.

## 3. Electronics and load floors

**INFERENCE:** `640 × 48 = 30,720` channels per selected sensor; this is exactly
one quarter of the historical 640 × 192 control. For the same sensor population,
the channel reduction is 75%. The active area, incident hit flux, sensor leakage,
data/control endpoint count and module count do not fall by 75%.

**NODD DESIGN CHOICE:** retain DES-042's transparent sensitivity model rather
than invent measured ASIC power. Define the conservative channel-density
reference `P0 = 7.8 × 122880/30208 = 31.72881356 W/module` and
`P_e = P0 [(1−f) + f/4]`, including on-module conversion in this input-power
budget. Do not add an assumed converter efficiency a second time. Use `f=0.75`
nominal and `f=0.50` adverse; fixed electronics are respectively 7.9322 and
15.8644 W at the old pitch. Thus both scenarios retain substantial fixed power.
These fractions are design assumptions, not physical bounds. The unscaled
7.8 W comparator is not a measured lower bound either.

| Quantity | Nominal, f = 0.75 | Adverse, f = 0.50 |
| --- | ---: | ---: |
| Selected electronic service-input power / module | 13.88136 W | 19.83051 W |
| Separate sensor leakage heat / module | 2.00000 W | 2.00000 W |
| Heat / module, before local losses | 15.88136 W | 21.83051 W |
| Electronic reduction relative to P0 | 56.25% | 37.50% |
| Module-heat reduction relative to P0 + 2 W | 52.91% | 35.28% |
| Module heat for existing 12,384 sensors | 196.675 kW | 270.349 kW |
| Module heat for illustrative 12,816 sensors | 203.535 kW | 279.780 kW |

Board loads, local bus losses, external cable losses and plant/remote conversion
remain additional. The existing 576 half-stave boards plus 144 petal boards
give a 3.6 kW fixed board allowance at 5 W each. The new protection/aggregation
board must meet that allowance or its measured replacement must enter the model.
HV leakage is heat and HV-circuit current; it is not LV feeder current.

**INFERENCE:** a 396-module/disc extension adds 432 sensors overall. Its
393,707,520 channels are a **74.128%** reduction relative to the old 0.5 mm
12,384-sensor control, and a 3.488% increase relative to the same current
12,384-sensor population already at 2 mm. Report both denominators.

Retain an `f=0` adverse control: if power is entirely fixed, no electronic power
is saved by longer cells and the reduced services/thermal design can fail.
The proposal is conditional on an ASIC/module design meeting the stated loads.

## 4. LV, HV, data and cable architecture

### Local and external distribution

All numbers in this subsection are **NODD DESIGN CHOICE** unless marked as
derived. Retain a 12 V distribution handoff; require the actual protected
point-of-load interface to remain within the selected converter's static and
transient ratings. Screen current conservatively at **11 V minimum delivered
voltage**, rather than reducing current using the unloaded 12 V nameplate.
A CERN bPOL12V-class implementation would need a lower protected setpoint,
tolerance/transient control and a complete conversion design; it is not selected
simply by retaining the inherited 12 V label.

Use copper resistivity `0.0175 Ω mm²/m × 1.4 = 0.0245 Ω mm²/m`, carrying the
existing long-strip warm-resistivity factor as a declared nODD stress choice.
For an external cable of at most 3.5 m one-way with 8 mm² per LV conductor,
`R_pair = 2ρL/A = 0.0214375 Ω`. With 14 modules and the full 5 W board allowance,
adverse current is at most 25.6934 A at 11 V, giving **0.55080 V** drop and
**14.152 W** cable loss. A 13-module feed gives 23.8906 A, 0.51215 V and
12.236 W. This leaves a finite budget for connectors and local drops.
Route lengths and delivered-voltage closure must be checked together; remote
sense does not remove conductor loss or the return-potential shift.

**INFERENCE:** for the 14 actual barrel taps at
`z = (row−13.5) × 2304/27 mm`, rows 14–27, from the 1210 mm feed, summing
`R_segment × I_downstream` and `R_segment × I_downstream²` gives:

| Cu thickness at 12 mm width / polarity | Adverse return drop at warm ρ, 11 V | Bus I²R loss | Result against 200 mV local screen |
| --- | ---: | ---: | --- |
| 0.20 mm, old | 0.15785 V | 5.3917 W | passes screen |
| **0.17 mm, proposed** | **0.18571 V** | **6.3431 W** | passes screen, 14.3 mV margin |
| 0.15 mm | 0.21047 V | 7.1889 W | fails |
| 0.125 mm | 0.25256 V | 8.6267 W | fails |

The 0.17 mm choice reduces local rail Cu by **15% at unchanged length**.
It does not justify a 75% reduction in rail copper. The full local round-trip
drop is 0.37141 V. Together with the 0.55080 V external drop, the simple
adverse screen gives 11.0778 V at the furthest tap from a 12 V handoff, before
connector losses, consistent with the 11 V current assumption only if connector
and protection drop fits the remaining approximately 78 mV. This narrow
end-to-end allowance must be respected; use the 10 mm² cable variant or shorter
route if the connector/protection budget is larger. At 10 mm² the external drop
is 0.44064 V and that remaining allowance rises to about 188 mV.

For a 33-module petal retain three electrically isolated feed groups with
11 modules each; distribute each group across radial rings to control the
worst current-weighted radial path. Split the 12 mm total copper width per
polarity into three approximately 4 mm traces at 0.17 mm thickness. Add and
check real isolation gaps; do not assign the full 12 mm to each feed while
claiming the same copper mass. The electrical screen must use the selected
radii/board radius and explicit tap-to-group assignment. The barrel calculation
above is not proof for a different petal layout.

### Cable occupancy and material

**NODD DESIGN CHOICE:** reserve **8 mm OD** per new LV/HV/control cable,
with an 8 mm² conductor per LV polarity (10 mm² variant if voltage/ampacity
requires it), up to 14 independent HV circuits, control, shield, insulation and
strain relief. Use 0.14 mm²/HV conductor only as the existing DES-023 geometric
precedent; sensor bias, insulation voltage, returns and terminations need a
new circuit design. Copper in an 8 mm²-pair, 14-HV-conductor example is already
`16 + 14×0.14 = 17.96 mm²`, before control/shield copper. Record those additions
explicitly rather than inheriting the old 20% copper fraction blindly.
Eight-millimetre cable OD is an unqualified package target, not a procurement
specification or a demonstrated bend radius/ampacity.

**INFERENCE:** the occupied section drops from 141.026 to 50.2655 mm² per
power cable, while the old representation contains 28.2052 mm² effective Cu
per power cable. With unchanged barrel segmentation, power feeds per end
fall from 576 to 288, whereas the 576 barrel fibre cables remain. A 33-module
petal still needs three power feeds, preserving the old 216 endcap feeds per
end despite extra area. Combined power-cable count per end is then 504 versus
792; fibre count is at least the unchanged 792 benchmark and must increase if
the extended sensor area needs more bandwidth. Do not combine the two counts.

At fixed incident flux, longer strixels increase per-channel occupancy rather
than dividing the hit traffic by four. Preserve link/clock/control capacity;
additional area may increase data. Per-module switching/fusing preserves local
isolation, but one upstream cable failure now removes up to 14 modules. Review
that common failure domain, grounding, common-mode noise, fault energy,
ampacity, connector heating and inrush. No serial powering or increased voltage
is assumed to achieve the capacity reduction.

## 5. Thermal redesign that is needed at module level

### Why the inherited contact is insufficient

**INFERENCE from the pinned thermal equations:** at maximum lift, the inherited
barrel screen gives approximately **1.2568 K/W**; the endcap's narrow two
6 × 60 mm² pickups and 20 mm thin-graphite spreading give **4.4269 K/W**.
At the nominal 15.881 W/module, the latter temperature rise alone is about
70.3 K. Retaining that module/contact while thinning only external cables
cannot establish the requested baseline. Those models also omit a separate
pipe/boiling resistance, so their failure is not cured by a hydraulic claim.

### Preferred constructive option with retained finite contacts

Each row below is a **NODD DESIGN CHOICE / qualification requirement**.
No listed conductivity/contact value is a new public material fact.

| Item | Proposed dimension / requirement | Engineering consequence |
| --- | --- | --- |
| Contact footprints | Retain two 6 × 60 mm² endcap contacts at u = ±5 mm, total area 720 mm²; retain the original two 20 × 64 mm² barrel contacts | Wider endcap pickups can collide with a neighbouring module at small radius. Keep finite collision compatibility rather than increasing thermal area arbitrarily. |
| Direct inserts | Dense graphite with effective k ≥100 W/m/K along heat flow, maximum 6.6 mm heat-flow length, contacting a shaped shoe at the titanium tube | **Bypass the foam path**: the length includes module/stagger gap and penetration from the core front face to the tube. Existing 4.9 mm pickup height alone omits that penetration. Cut the displaced foam volume explicitly; do not overlap it with the insert. |
| Module spreader | 0.35 mm graphite over the module; k parallel ≥400 and k perpendicular ≥10 W/m/K | Increase from old 0.20 mm. Orientation, anisotropy and material grade require specification and verification. |
| Contact windows | Remove CFRP backing and polyimide from the local thermal windows; use 0.10 mm electrically insulating thermal bond, k ≥1.2 W/m/K in operation | Changes backing stiffness, HV clearance and bonding. A Henkel CAT11-like bulk material is a precedent only; cold/radiation/bondline performance and dielectric safety remain qualification gates. |
| Readout/hotspots | Two logical 23.4 × 23.4 mm² die envelopes centred at u =0, v =±18 mm, 15,360 channels each | Geometric heat-source edges are at |u| ≤11.7 mm and |v| ≤29.7 mm. The endcap lands end at |u| =8 mm, yielding ≤3.7 mm effective spreading. This is a new ASIC/interconnect/redistribution design, not a reused chip or an asserted manufacturable package. |
| Core/support | Retain the 5 mm foam sandwich except the explicit insert/cooling cut-outs and retain mechanical mounting load paths | The thermal calculation below bypasses the core foam locally. It does not remove the carrier or establish its stiffness. |
| Contacts | Total residual contact resistance ≤0.04 K/W per module | Measure under representative assembly, radiation and thermal cycling; do not double-count the separately explicit bond layer. |
| Tube-to-fluid | Allocate ≤0.08 K/W per module equivalent for pipe wall/shoe/boiling | Required additional resistance budget. A shaped tube contact with adequate spreading/area is essential; small tube surface area must not be hidden by using full pad area at the fluid boundary. |
| Operating temperatures | Maximum coolant −35 °C and sensor ≤−20 °C | A warmer −25 °C sensitivity case fails; instrumentation/interlocks and hydraulic temperature/pressure control are required. |

**INFERENCE:** the following series screen uses the smaller endcap contact area
`A = 2×6×60×10⁻⁶ m²`. It is a dimensioned resistance budget, not finite-element
validation or proof of a manufacturable interface:

| Contribution | Formula, dimensions in metres | R, K/W |
| --- | --- | ---: |
| Insulating thermal bond | 0.00010/(1.2 A) | 0.11574 |
| Through spreader | 0.00035/(10 A) | 0.04861 |
| In-plane spread | 0.0037/(400×0.00035×0.060×2) | 0.22024 |
| Direct insert, including core penetration | 0.0066/(100 A) | 0.09167 |
| Residual contacts | Required budget | 0.04000 |
| Tube/shoe/boiling | Required budget | 0.08000 |
| **Total** | Sum | **0.59626** |

At −35 °C coolant the lumped screen predicts −25.53 °C nominal and
−21.98 °C adverse sensor temperature before a distributed-leakage corner
allowance. Leakage heat is not confined to the ASIC die envelopes. For the
uniform 2 W sensor leakage, use an additional conservative sheet-spreading
allowance

`ΔT_leak = (2 W / 0.004608 m²) × (0.016² + 0.018²) /
             (2 × 400 W/m/K × 0.00035 m) = 0.89906 K`.

Here 16/18 mm are the largest u/v overhangs beyond the endcap contact lands.
This deliberately adds the entire leakage-sheet allowance even though the
lumped total heat already contains 2 W. It is a transparent conservative
screen, not a rigorous two-dimensional bound or substitute for thermal FEA.
The resulting nominal/adverse maxima are approximately **−24.63/−21.08 °C**.
The adverse margin is only **1.08 K**, so this does not establish a qualified
operating module. Local leakage nonuniformity and thermal runaway remain gates.

A 6 mm electronics spreading distance instead of 3.7 mm fails the sensor goal;
restoring the inherited 5 mm foam path adds 0.34722 K/W in series and also
fails. At −25 °C coolant the temperatures are ten degrees warmer and fail.
Retain those failed controls. The design needs the specified source layout,
fully bypassed core, material anisotropy, contact and tube/boiling performance.

The two-die envelope is consistent with channel-count arithmetic only. There
is no identified production ASIC with the required matrix, periphery, input
mapping and radiation/noise/power performance. A 640×48 sensor divided across
two 15,360-channel parts requires a new matrix or redistribution arrangement;
the fixture cannot establish electrical feasibility. Preserve the 75 µm fine
coordinate and evaluate longer-cell capacitance and added interconnect length.

The untouched eight-tile stack extends to |v| ≈47.7 mm and does not meet this
hotspot/land geometry. It cannot inherit the smaller spreading resistance.
For conservative material accounting, take **no ASIC-area/mass reduction credit**
until a physical die/package/interconnect layout has been established. Debit
extra spreader, bond material, graphite inserts, shaped shoes, displaced foam
and mechanical reinforcement explicitly.

A colder −40 °C operating option has a public CO₂ precedent and increases
thermal margin, but is not required by this selected screen. A larger contact
footprint is not a valid shortcut where it collides. Any colder operation or
changed pickup must be a separately checked design alternative rather than an
implicit rescue of a failed baseline.

## 6. Cooling topology, flow and hydraulic floors

**NODD DESIGN CHOICE:** retain 2.5 mm OD / 0.14 mm wall local tubes, so bore
is 2.22 mm; keep two parallel endcap circuits with independent flow balancing.
Re-route local tubes beneath the redesigned thermal lands. A geometric tube
centreline cannot by itself establish hotspot distance or contact conductance.
Retain 8/12 mm OD bulk pipes, 6/10 mm IDs and at most eight leaves/manifold.
Manifold counts must be rounded separately per actual disk/sector and include
upstream barrel demand. Splitting the old one-loop petal increases leaf/manifold
and fan demand; include this cost rather than scaling their number downward.

**INFERENCE:** NIST latent heat is 322.42 J/g at −40 °C and 313.18 J/g at
−35 °C. Retain the earlier deliberately reduced **200 J/g** transport allowance
and quality rise Δx =0.35, hence 70 W/(g/s), as a conservative enthalpy screen.
It does not solve inlet subcooling, pressure drop, local quality or dry-out.

| Leaf case | Nominal/adverse heat including 2.5 W board share +10 W local-loss allowance | Minimum flow at 70 W/(g/s) | Selected nominal/adverse |
| --- | --- | --- | --- |
| 14 modules, conservative illustrative split | 234.84 / 318.13 W | 3.355 / 4.545 g/s | 5 / 7 g/s |
| 17 modules, larger half of 33-module petal | 282.48 / 383.62 W | 4.035 / 5.480 g/s | 5 / 7 g/s |
| 20 modules, absolute design partition cap | 330.13 / 449.11 W | 4.716 / 6.416 g/s | 5 / 7 g/s |

The 14-module barrel actually carries its entire 5 W board; substitute that
load and the exact bus loss in final execution. The 10 W loss reserve per leaf
must cover the local electrical losses allocated there; external feeder heat
is counted on the actual external cable route and not silently removed from
the tracker heat/material budget. The table's worst 20-module case stays below
the 490 W adverse enthalpy allowance, but this is **not a hydraulic pass**.

At 5/7 g/s in a 2.22 mm bore, mass flux is approximately 1,292/1,808 kg/m²/s.
This and multi-metre routing require pressure-drop, flow stability, dry-out and
exhaust sizing analysis. Do not infer that the unchanged small local tube is
qualified, or that the old bulk tube can accept arbitrarily more parallel leaves.
Balancing capillary dimensions, control pressure, room-temperature/fault pressure,
connector/weld access, leak testing, relief and pressure safety are unresolved
engineering interfaces. Do not reduce pipe wall or diameter to force a radial fit.

## 7. Module redesign flags and material claims

| Assembly | Redesign flag | Retained contract / open qualification |
| --- | --- | --- |
| Sensor | **Yes: segmentation/electrode/interconnect design** | Keep active outline, 200 µm thickness and guard allowance; new mask or redistribution, cell capacitance/noise/radiation tests are required. |
| ASIC/readout | **Yes, or a newly qualified compatible part** | Two logical die envelopes and the power/thermal budgets are design targets; existing fixtures are not hardware. Threshold/noise, capacitance, occupancy, data and radiation are open. |
| Bumps/RDL/flex | **Yes** | Map 640×48 cells to ASICs, preserve 75 µm fine coordinate, bias and isolation; qualify extra trace capacitance, bump yield and grounding. |
| Module thermal/mechanical stack | **Yes** | 0.35 mm spreader, backing/insulation windows, direct graphite inserts, hard mounting load path and controlled cold operation change stiffness/CTE/contact. Preserve 48×96 mm² sensor footprint. |
| Local service board/bus | **Yes** | New 14-module feed fault domain, module protection, isolated petal feed groups, thinner patterned copper, connectors and strain relief. |
| Endcap carrier/cooling/frame | **Yes** | Extended radius, two leaves per petal, aligned thermal lands and moved outer boards/manifolds. Recheck supports, natural frequencies and assembly access. |
| Long-strip sensor/module | No change requested | SysArch must reconcile the retained inner support/frame and full short-strip service corridor; do not move it implicitly. |

**INFERENCE, scoped material screen:** the extra 0.15 mm full-area graphite
spreader alone adds **1.5276 g/module** at the inherited 2.21 g/cm³ density.
That debit must remain even if the ASIC drawing has two rather than eight die
fixtures. Keep the finite existing pickup footprints, and account for the
direct insert/shoe extension, thermal-window cuts, insulating bond, removed
foam and any reinforcement from their actual dimensions. Do not reuse a
wide-foam-pad mass saving that has not passed finite collision checks. Extra
sensors and carrier area in the larger endcap are additional real material.

Cable material must use the actual selected conductor/HV/control/shield schedule,
path lengths and discrete group counts. The old 20% Cu recipe is known, so a
comparison can be made to that representation; it is not an estimate of an
unseen experimental cable. Larger active coverage adds sensor, module, support
and cooling material. Two endcap loops add fittings/manifold demand. A lower
whole-tracker mass does not prove lower X/X0 for every track direction.
Publish constituent mass/volume changes by local module, carrier, leaf, fan,
collector and cumulative trunk, then obtain directional material scans before
claiming the complete tracker material improves.

## 8. Checks performed and handoff

Executed against pinned source content, using Python standard-library arithmetic
and `git show` (all successful calculation commands exit 0):

1. Read all nine assignment inputs at the exact revision. Evaluated the pinned
   barrel `build` function without loading native dependencies: 44/56/80/108
   staves by layer, 288 total and 8,064 modules; 25/25/22 stave loops repeating
   across twelve sectors. Recomputed endcap ring counts and 30 modules/petal.
2. Recomputed the f-dependent powers, per-sensor/all-sensor channel counts,
   discrete barrel warm-ρ voltage/loss sums, feeder resistances and heat/flow
   budgets above. Kept failed 0.15/0.125 mm rails, long spreading, restored foam
   path and −25 °C coolant as explicit controls; added the separate uniform-leakage
   sheet-spreading allowance.
3. Recomputed both thermal resistance budgets term by term, including contact
   and pipe/boiling allocations. These are screens; no native geometry, FEA,
   hydraulic, pressure, sensor-electronics or beam test was performed.
4. Retrieved and text-inspected the public NIST table, ATLAS two-page cooling
   preprint, CERN converter datasheet and Henkel insulating-epoxy datasheet.
   The first two match existing source hashes; both new datasheets have metadata
   supplied above for the coordinator.
   Temporary PDFs are not publication artifacts.

Coordinator handoff: select the annulus only after explicit per-sector capacity,
bend/connector, board and manifold reservations; carry the module redesign and
thermal-interface and controlled-temperature requirements into DES-043. Execute changed source material
and geometry in the isolated prototype, then check overlap, material direction,
sensitive acceptance and ACTS interfaces under the normal workflow. Required
engineering gates include actual ASIC power at occupancy/radiation/capacitance,
full cable circuit and electrical/grounding closure, thermal/contact/CTE and
structural tests, and two-phase pressure/drop/dry-out qualification. No human
approval, implementation sign-off or ACCEPTED lifecycle is granted here.
