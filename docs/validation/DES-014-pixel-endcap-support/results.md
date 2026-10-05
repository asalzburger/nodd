# DES-014 — Pixel endcap support screening

- Status: DRAFT / PROTOTYPE. **Mechanical concept B is proposed for development; thermal stress target FAILS.**
- No baseline sensor or DD4hep geometry was changed. B is an explicit placement amendment requiring review and a subsequent coverage/ACTS study.
- Reproduce with `MPLCONFIGDIR=/tmp/nodd-endcap-mpl python3 -B tools/pixel_endcap_support/report.py`.
- Exact inputs, source/code hashes, versions, timestamp and scope: [screening.json](screening.json).
- [Design and approval boundary](../../design/DES-014-pixel-endcap-support.md), [literature dossier](../../design/inputs/DES-014-literature.md), [drawing book](drawings.pdf).

## Geometry and commonality

All 18 baseline discs share the same x/y pattern: 112 quads/disc, five rows with 12, 16, 24, 28, 32 modules. Total: 2016 modules and 8064 active chip patches. No modules are removed.

A single backplate retaining current positions needs narrow central posts: the 4×4 mm trial clears by 0.218 mm; the 6×6 mm trial has 12 post/body conflicts per positive template. This is a test of those two centred-post designs, not a proof that no support retaining the layout could work.

B uses a common 6.3 mm carbon sandwich and short, broad outboard thermal feet. Rows 0/2/4 face the IP; rows 1/3 face away. Three heights on row 0 avoid next-nearest-neighbour body collisions; two suffice on other rows. The first disc and its collector move 3.5 mm outward on each end **only in the proposal**.

| Envelope comparison | Overlaps | Minimum gap [mm] |
| --- | ---: | ---: |
| body_body | 0 | 0.650 |
| pickup_body | 0 | 0.200 |
| foot_body | 0 | 0.345 |
| foot_pickup | 0 | 0.345 |
| pickup_pickup | 0 | 1.200 |
| foot_foot | 0 | 14.532 |

Tube-plane clearance is 0.200 mm; nominal tube-to-skin clearance 0.100 mm. These are tight fabrication targets, not qualified tolerances. First-disc clearance to the barrel extraction bay is 2.300 mm; module-to-pixel-trunk radial clearance remains 2.000 mm.

The OBB checks cover pickup and foot envelopes against modules and each other. Pipe transitions, tabs/pockets, clips and a fully routed flex/harness remain outside that proof. [Proposed module positions](proposed-module-placements.csv) retain old/new z and unchanged x/y; they are not an ACTS input baseline.

| Disc | Old nominal z [mm] | Proposed nominal z [mm] | Occupied absolute z [mm] |
| --- | ---: | ---: | --- |
| A-pixel-N1 | -611.700 | -615.200 | 607.300–621.450 |
| A-pixel-P1 | 611.700 | 615.200 | 607.300–621.450 |
| A-pixel-N2 | -794.414 | -794.414 | 786.514–800.664 |
| A-pixel-P2 | 794.414 | 794.414 | 786.514–800.664 |
| A-pixel-N3 | -1046.270 | -1046.270 | 1038.370–1052.520 |
| A-pixel-P3 | 1046.270 | 1046.270 | 1038.370–1052.520 |
| A-pixel-N4 | -1333.096 | -1333.096 | 1325.196–1339.346 |
| A-pixel-P4 | 1333.096 | 1333.096 | 1325.196–1339.346 |
| A-pixel-N5 | -1645.288 | -1645.288 | 1637.388–1651.538 |
| A-pixel-P5 | 1645.288 | 1645.288 | 1637.388–1651.538 |
| A-pixel-N6 | -1977.808 | -1977.808 | 1969.908–1984.058 |
| A-pixel-P6 | 1977.808 | 1977.808 | 1969.908–1984.058 |
| A-pixel-N7 | -2327.479 | -2327.479 | 2319.579–2333.729 |
| A-pixel-P7 | 2327.479 | 2327.479 | 2319.579–2333.729 |
| A-pixel-N8 | -2692.091 | -2692.091 | 2684.191–2698.341 |
| A-pixel-P8 | 2692.091 | 2692.091 | 2684.191–2698.341 |
| A-pixel-N9 | -3070.000 | -3070.000 | 3062.100–3076.250 |
| A-pixel-P9 | 3070.000 | 3070.000 | 3062.100–3076.250 |

## Cooling and the thermal blocker

Ten independently metered half-ring circuits/disc carry 1204.224 W nominal; the 18-disc total is 21.676 kW. Proposed flow is 18.2 g/s/disc (327.6 g/s total). These do not include the separate barrel flow.

| Row | Modules/circuit | Nominal/stress power [W] | Flow [g/s] | Stress exit quality |
| --- | ---: | ---: | ---: | ---: |
| 1 | 6 | 64.512 / 96.768 | 1.0 | 0.409 |
| 2 | 8 | 86.016 / 129.024 | 1.3 | 0.417 |
| 3 | 12 | 129.024 / 193.536 | 2.0 | 0.409 |
| 4 | 14 | 150.528 / 225.792 | 2.3 | 0.413 |
| 5 | 16 | 172.032 / 258.048 | 2.5 | 0.430 |

All ten circuits pass the 0.45 quality arithmetic ceiling at 1.5× load; this does not establish boiling stability or pressure drop. The thermal bottleneck is the module pickup, not the available latent heat. At −40 °C coolant, the edge-biased 1500 W/(m K), h=20 kW/(m² K) screen gives **-16.6 °C nominal and -4.9 °C stress**, against a −15 °C target. Total resistance is 2.178 K/W; it needs to be ≤1.550 K/W (28.8% lower). Do not solve this failure by declaring higher graphite conductivity or a better boiling coefficient without measurements.

Two-dimensional finite-volume heat spreading is coupled to explicit graphite c-axis, foot, contact and tube resistances. The uniform map is also retained; the edge-biased map is a hot-region sensitivity, not an RD53 power map. The coarser/finer 1.0/0.5 mm grids differ by 3.91% in sheet resistance. Heat balance is checked separately. No irradiated-sensor feedback or thermal-runaway claim is made.

The retained-position case A already reaches -12.0 °C in an optimistic post-plus-bond-only stress lower bound, before adding the spreader, electrical isolation or tube/boiling drop. It is not selected for development.

Next thermal step: a full-size powered quad/foot coupon, then a two-module overlap demonstrator, measuring the full resistance and the effective contact area. Test an additional thermal pickup path or revised local overlap; retain the 0.2 mm neighbour gap. Both require a geometry/material update and repeat of this screen. Raising flow alone cannot eliminate pickup spreading resistance.

## Material and stiffness

Per disc: **594.2 g** modelled local passive assembly, including full-liquid tube mass, provisional flex and clip/hardware allowances. Annulus-normalized equivalent passive inventory (including outer hardware) is **1.635% X0**. This exceeds the historic ideal-layer 1% proxy before silicon: do not reuse that proxy as a material validation result.

Shared rails, closed carrier shell and two end flanges add **2.169 kg/end**. The 18 local assemblies plus two carriers total 15.034 kg. Sensors/ASICs, external service trunks, real fittings and connector material are not included in this passive total. The stiffness screen adds the 4 g/module payload and a separate 5 kg/end service load allowance.

| Local component | Mass [g/disc] | Equivalent X0 [%] |
| --- | ---: | ---: |
| facesheets and tongues, thermal windows deducted | 53.64 | 0.1344 |
| foam core, tubes and inserts deducted | 117.67 | 0.2526 |
| graphite feet and through-core thermal inserts | 106.36 | 0.2278 |
| module pickup graphite | 141.79 | 0.3037 |
| module cradles, land windows deducted | 25.89 | 0.0649 |
| module isolation | 7.59 | 0.0171 |
| TIM and module bond films | 21.39 | 0.1090 |
| skin/core bond films, foam displaced | 17.68 | 0.0902 |
| local evaporators and radial legs | 32.51 | 0.1852 |
| local tubing: full-liquid mass bound | 31.07 | 0.0785 |
| inner/outer edge closeouts inside foam | 2.11 | 0.0053 |
| module clip allowance | 11.20 | 0.0281 |
| mounting hardware mass allowance (Ti equivalent) | 12.00 | 0.0684 |
| local flex polyimide, provisional 40% envelope fill | 5.18 | 0.0117 |
| local flex copper, provisional 10% envelope fill | 8.17 | 0.0581 |

| Laminate E [GPa] | Disc distributed/central-load beam [mm] | Closed-shell sag [mm] |
| ---: | ---: | ---: |
| 70 | 0.095 / 0.152 | 0.041 |
| 100 | 0.067 / 0.107 | 0.029 |
| 140 | 0.048 / 0.076 | 0.021 |

These beam estimates support a **closed carrier shell with rails bonded to it**. Standalone 8×8 mm rails over the full length leave the small-deflection regime and are rejected; metre-scale linear-model deflections are a failure indicator, not predictions. The disc beam bracket straddles the provisional 0.1 mm screen in some cases. No claim of stiffness qualification follows from the shell sag estimate: annular geometry, core shear, joints, shell ovalization, torsion and thermal-cycle/eigenmode FEA remain required.

## Cabling, collectors and mounting interfaces

Each disc has 16 independently grouped power chains (≤8 quads), separate from its ten cooling circuits. Front-face modules stay on front-face buses; rear modules stay on rear buses. Both wrap around the outer rim to the existing 50 mm collection bay. Keep clamps/lugs out of those routes. The last disc retains its conditional inner bypass and needs a dedicated routing adapter; a common mechanical disc does not make this external route identical.

| Pixel trunk after eight discs, positive end | Demand [mm²] | Capacity [mm²] | Utilization |
| --- | ---: | ---: | ---: |
| reference: PASS | 19167.5 | 19816.6 | 96.7% |
| conservative: FAIL | 29659.4 | 10568.9 | 280.6% |
| stress: FAIL | 55901.9 | 10568.9 | 528.9% |

This includes the current PR35 barrel handoff inventory, not the older PR25 module counts. Negative-end results are also retained. The reference passes only as an aggregate area inequality and has little headroom; the adverse scenarios fail. Fixed-sector redistribution and connector/weld pockets are not validated. No additional detector row is silently removed.

Use three disc tongues at 90°, 210°, 330° on common box rails. A cone/slot/plane coupling supplies 3+2+1 constraints; a spring latch provides preload without a second rigid datum. The carrier has one axial datum and a sliding opposite end interface. No six rigid bolts or unsupported long rails are assumed. The one-piece disc/cassette is installed axially; beam-pipe access and an eventual shell split need a separate swept-envelope review.

## Advance conditions

1. Review the proposed z/face amendment and the first-disc/collector shift; then run matched straight/helical coverage plus ACTS audit. No adoption is inferred from this design PR.
2. Close the thermal resistance gap with measured interfaces and 3D electrothermal analysis, including irradiated-sensor feedback and hydraulic/pressure tests.
3. Complete pipe transitions, flex artwork, cable voltage-drop/bandwidth and last-disc adapter; resolve the adverse service-capacity failures.
4. Verify annular-disc/core-shear and carrier modes/thermal motion with FEA and metrology; qualify assembly clearances.
5. Only after review, implement a separate DD4hep prototype and run overlaps, masses, directional material scans and material-aware tracking.

## Drawings

- [Common disc, front and rear](disc-xy.svg)
- [Stagger and local support section](sections.svg)
- [Cooling/cable routing concept](routing.svg)
- [Nine-disc carrier and mounting rails](carrier.svg)
- [Thermal/material diagnostics](diagnostics.svg)

All are original nODD drawings generated from the same input file. Dashed service paths are routing concepts, not validated fabrication centrelines.
