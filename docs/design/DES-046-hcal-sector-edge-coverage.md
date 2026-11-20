# DES-046 — HCAL barrel sector-edge coverage

- Status: **DRAFT / PROTOTYPE**; engineering sign-off and production acceptance pending.
- Date: 2026-11-20.
- Human direction: minimize barrel sector-edge gaps using smaller physical readout modules, then rerun the requested pion samples.
- Governing input: `b91b1d7969b94cccb4e0516e1c84246f4d2e2cd0`; parents [DES045](DES-045-hcal-restored-ecal-pion50.md), [DES036](DES-036-hcal-common-readout-module.md) and [DES037](DES-037-hcal-barrel-common-module.md).
- Integration owner: task coordinator; CaloTech supplies this physical contract, SoftEng implements it, SysArch assesses interfaces and PhysVal independently assesses the samples. No agent grants human sign-off.

## Scope and provenance

**FACT about the pinned implementation:** DES045 has 16 barrel sectors, 60 repeats of 30 mm sector-owned Steel235 + 12 mm carrier + 1 mm installation allowance, and a 10 mm rear cover. Barrel front/outer apothems are 3130/5720 mm, half-length 6260 mm. Endcaps occupy abs(z)=6760–9350 mm, inner/outer apothems 300/5710 mm. The existing common carrier is 380 × 240 × 12 mm with two 184 mm boards and 72 individually recessed scintillator cores. Its outermost core ends 7.15 mm inside the carrier boundary. Source: pinned `tools/hcal_response/{config.json,model.py,export.py}`, `prototypes/hcal_response/HCAL.cpp` and DES036/045.

**INFERENCE from those inputs:** a 20 mm continuous aluminium edge rail, 1 mm half-seam, whole-carrier packing and bounded tangential phase leave 28.171–306.342 mm from a nominal sector-face boundary to the nearest outer core edge at the carrier-front radius across the 60 layers and both sides. This is a geometric inactive-width screen; it is not particle efficiency. Staggering intact 380 mm carriers alone cannot eliminate this fixed edge band.

**NODD DESIGN CHOICE — this amendment:** keep every global envelope, all 60 steel plates, their 30 mm thickness, all axial sampling coordinates, existing 47 barrel rows and their 260 mm pitch, 20 mm axial collector strips, the axial phase cycle, endcap geometry, and the standalone transport physics/sample definitions. Retain the original common unit as unit 0. Add newly manufactured narrow edge units and replace the continuous 20 mm edge rail with a 2 mm aluminium guide. Repack the central common units only as required to reserve one complete edge cassette on each side of every row. The old common unit and old validation evidence remain unchanged historical controls.

The new widths, guide, service integration and placements below are unsigned project choices. Existing public sources in DES036 establish the scintillator/SiPM/readout technology and the specified component references; they do not certify these new board outlines, tile moulds, folded skins, connectors or mechanical loads. No new external device specification is asserted.

## Continuous guide and exact seam

**NODD DESIGN CHOICE:** retain the 1 mm sector half-seam and use a 2 mm full-depth aluminium guide instead of the 20 mm rail. Steel extends only to the inner guide face; steel and aluminium remain disjoint and the plate count/thickness are unchanged. The guide is represented explicitly, with its layer-spanning material and the unchanged end flanges/rear cover.

This withdraws any implication that the amended guide inherits the old proposed plate → rail → flange load path. Plate support, attachment, stiffness, buckling, gravity/magnetic loads and installation remain unqualified. A 2 mm transport guide is not a qualified support for the steel plates. The missing structural solution is an explicit engineering gate.

Place the outer face of each edge cassette 0.5 mm inside the guide's inner face at the narrow carrier front. Preserve the finite half-seam. A rectangular cassette safe at its front leaves a tangential taper shadow of `12 tan(pi/16) = 2.386948 mm` at its rear. At the core-plane coordinate 2 mm from the carrier front, the corresponding shadow is `2 tan(pi/16) = 0.397825 mm`. Report these separately from guide, installation and tile-border widths; no tapered active shape is introduced in this first amendment.

## New edge unit: physical stack and board family

Every dimension in this section is a **NODD DESIGN CHOICE**, except the unchanged sourced SiPM package reference retained from DES036.

| Part or property | Implementable contract |
| --- | --- |
| Complete cassette | Variable tangential width `W >= 32 mm`; 240 mm axial height; 12 mm depth |
| Board organization | Six axial tile rows; `N=1..12` total tangential columns; one PCB for `N<=6`, two for `N>6`, split as six columns plus `N−6` |
| Pitch | Common tangential pitch `p<=30 mm` within each unit; axial pitch stays 30 mm |
| PCB outline | Each board: `(n p + 4) × 184 × 1.2 mm`; 2 mm gap between two boards; outermost PCB edges 1 mm inside the cassette |
| Width closure | `W=N p+6 mm` for one board; `W=N p+12 mm` for two boards |
| Column selection | Choose the smallest integer `N` satisfying the width closure with `0<p<=30 mm`; reject more than 12 columns or any tile unable to contain its existing recess/package |
| Scintillator core | `(p−0.3) × 29.7 × 3 mm`; unchanged PSHost recipe; no cropped original tile |
| Wrapper/recess | Existing 0.1 mm reflector allowance and 3.5 mm-radius, 1.1 mm-deep rear recess; existing package/LED offsets and z coordinates |
| Front/rear skins | Existing 0.2 mm aluminium skins and rear polyimide insulation |
| Tangential sidewalls | 0.5 mm aluminium folded sidewalls; 0.5 mm clearance from PCB edge to sidewall inner face |
| Axial endwalls | Existing 2 mm aluminium endwall/port concept; keep actual cooling clearance cuts |
| Cold plate | `(W−1) × 236 × 3 mm` copper, same z=7–10 mm interval; tube bores subtract actual copper |
| Cooling | One existing Ti/water branch per PCB, along axial y at that PCB's tangential centre and z=8.5 mm; same 2/1.6 mm outer/inner diameter and 240 mm length; two external handoffs per branch |
| Front-end | One existing 20 × 20 × 1.5 mm package/contact stack per PCB, centred at its x coordinate and y=−12 mm; same materials and z stack |
| Shared interface | One existing interface package/contact stack per edge cassette, moved to the first PCB's x centre and y=45 mm, behind that PCB; it has a separate contact to the same cold plate |
| Service PCB | `(W−2) × 30 × 1.2 mm` at y=100 mm, same PCB/copper-equivalent recipe and front z=3.7 mm |
| External connector | One 20 × 12 × 2 mm combined connector envelope at (x,y,z)=(0,100,5.95) mm, same proxy recipe; logically carries LV, bias, DAQ, trigger and control allocations |

The shared-interface move to y=45 mm separates it from both the front-end at y=−12 mm and the connector at y=100 mm. All three package/contact stacks must be constructed and checked, not represented merely by a heat budget. The first PCB occupies y=−104..80 mm, so the interface and its 20 mm footprint have physical PCB backing. At minimum W=32 mm, the 30 mm-wide PCB leaves 5 mm per side around a 20 mm package. New narrow PCB masks, moulded tile profiles, copper plates and folded skins are new parts; existing 184 mm boards and 29.7 mm tiles are not clipped.

The combined connector is a reserved transport envelope, not a selected part or certified high-speed pinout. Six differential lane pairs for the one-chip case plus power/bias/control require an actual connector and routing design; the two-chip case scales its lane allocation. Keep the interface power/material once per cassette, include all powered front-end channels, and retain the 25 ns/latency/rate assumptions and nominal/stress cases from DES036. For `m=1 or 2` PCBs and `6N` tiles, nominal local input heat is `(m×78×0.015 + m×0.5 + 2)/0.9 + 6N×42×2e−6 W`; ideal water flow uses the same cp and 5 K rise. These are planning budgets, not thermal, hydraulic or EOL qualification.

## Deterministic packing contract

Let `r=3160+43 layer` mm be the carrier-front radius and `t=tan(pi/16)`. The usable tangential half-span inside the new guide is `h=r t−1−2` mm.

1. Reserve an edge cassette of at least 32 mm plus 0.5 mm guide clearance and 1 mm inner installation gap on each side. Choose the largest central common-carrier count `k` satisfying `H=(380k+(k−1)×1)/2` and `h−H>=33.5 mm`.
2. Retain the requested DES045 tangent phase cycle −90,−35,+35,+90 mm but clamp its magnitude to `h−H−33.5`. Retain the axial phase cycle −60,−20,+20,+60 mm without change. Record requested and actual phases.
3. For actual central shift `s`, manufacture the left/right complete edge cassettes with `Wleft=h−H+s−1.5` and `Wright=h−H−s−1.5` mm. Their outer faces are guide-anchored; their inner faces are 1 mm from the central common block. The central common-unit spacing stays 1 mm.
4. Derive each unit's board/tile pitch from the physical width closure above; place complete units and all physical contents. Check all eight cassette corners through the depth, all PCB/skin/package clearances, each original or new recess, tube bores and edge cells.

**INFERENCE — prospectively evaluated arithmetic:** the frozen 60 layers select 3 central common columns in 20 layers, four in 23 and five in 17. Edge widths span 32.000–305.574485 mm; the selected column counts span 1–10, pitch 15.856633–29.990774 mm and core width 15.556633–29.690774 mm. Even the narrowest selected core exceeds the 7 mm recess diameter with finite clearance. No shower result was used to choose these values.

With 47 rows and 16 sectors this predicts 178224 retained common carriers plus 90240 edge carriers and 2341728 edge tile channels, giving 15173856 barrel tile channels, versus 181232 common carriers and 13048704 barrel tile channels previously. These are arithmetic predictions to be checked against export/native inventories. Endcap carriers and cells remain unchanged.

## Readout and native hierarchy

Preserve bits 0–41 of the DES045 descriptor and append `unit:8` at bits 42–49. Unit 0 denotes the unchanged common carrier. Canonicalize each edge width to the nearest 1e−9 mm before constructing or identifying a unit, then sort the distinct canonical widths numerically and assign unit IDs 1–100 in that order. The board/column selection follows the same canonical width; no two IDs may denote the same unit. The width rounding is four orders of magnitude below the 10 nm overlap tolerance and must appear in the exported recipe. These 100 edge templates plus unit 0 fit the appended eight-bit field. System/side/sector/layer/carrier remain placement fields and uniquely identify a carrier; the unit field identifies its physical template. Each PCB has module 0 or 1. Tile sensor addresses are `row×6+column`; unused positions are invalid cells, not zero-energy physical tiles. x/y stay zero. Assert field capacity and global carrier/cell uniqueness.

Every unit manifest must contain its complete physical parts/material inventory, `channel_map`, exact core dimensions/cuts, front-face tile centres, cassette dimensions and explicit active-volume anchor. Unit 0 preserves its old internal geometry. New variable-pitch units use exact explicit table entries `(unit,module,sensor,active-local cx,cy,cz,sx,sy,sz)`; inference from a global 30 mm lattice or a hardcoded 29.7 mm core is forbidden.

Retain the exact disjoint-core compound representation and identity-left balanced Boolean contract. The final placed sensitive volume carries its first-core anchor. ROOT and Geant4 must each match the original physical core membership, including narrow-core edges, reflectors, all recesses, inactive PCB seams and service bays. Passively backing a sensitive extension and preserving native/saved energy closure are required gates, not optional illustrations.

## Quantified edge target and interfaces

**INFERENCE — geometric target:** at the carrier front, every outer edge core ends `1 mm half-seam + 2 mm guide + 0.5 mm fit + 3.15 mm core-to-cassette border = 6.65 mm` inside the nominal sector boundary. At the core plane the sum becomes **7.047825 mm per side** including the taper contribution. The two-sided tangential sum is 14.095649 mm at that plane; it is not an exact cylindrical arc width, a global angular-efficiency statement, or a promise that the seam is sensitive. Report actual angular intervals and directional sensitive depth separately.

The guide amendment changes explicit aluminium and steel volumes. SysArch's rail-only screen predicts approximately −50.075 tonnes aluminium and +101.573 tonnes Steel235, before changed cassette packing. Recompute the complete material/heat/flow ledger from the new inventory; reducing aluminium does not imply reducing total mass. All existing external routing, downstream interfaces and mechanical-load limitations remain. No spare cooling, bandwidth or support capacity is inferred from a smaller footprint.

## Required checks before new samples

Keep the old 10k cohort as its own control. Before transport, require deterministic export and expected counts/hashes; dimension, material, valid-cell and global-ID checks; all unit/compound core membership and cell-position checks in ROOT and converted Geant4; overlap checks at the existing 10 nm tolerance; finite sector-edge/guide/taper rays; and expanded material/path/coverage plots with fixed definitions. Retain exact seam probes even when insensitive. Geometry-only best-direction selection must be fixed before new shower results are examined and must report the actual depth/core-clearance criterion.

Then rerun the user-requested samples with their specified populations and independent reproducible seeds/primary identity as appropriate. Keep original samples/plots, every failed receipt and every new geometry/source/library hash distinct. Verify worker field/material/cut/physics state, serial-versus-MT controls, all raw-volume maps, and sensitive-step → native-hit → saved-hit energy closure. Report response, tails, zero counts, terminal-layer fractions and escape diagnostics; geometry improvement alone does not establish better energy resolution or sufficient containment. Human review of construction/support/routing and response assumptions remains open.
