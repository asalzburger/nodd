# Issue #38 — whole-millimetre pixel disc positions

Status: preliminary standalone PROTOTYPE, DRAFT design amendment.

The exact reviewer list replaces the implemented support datums; negative discs reflect it. The first datum was ±615.2 mm after the previous 3.5 mm outward shift. The new ±615 mm is final and receives no additional shift. These requested values differ from flooring all old positions: P2/P7 move outward. Future optimizer proposals are floored to whole millimetres after taking the ceiling of a feasibility lower bound.

| Disc | Previous z [mm] | New z [mm] | Signed movement Δz [mm] |
| --- | ---: | ---: | ---: |
| PixelP1 | 615.200000000 | 615 | -0.200000000 |
| PixelP2 | 794.414240676 | 795 | +0.585759324 |
| PixelP3 | 1046.270150048 | 1046 | -0.270150048 |
| PixelP4 | 1333.096391849 | 1333 | -0.096391849 |
| PixelP5 | 1645.287828809 | 1645 | -0.287828809 |
| PixelP6 | 1977.807585531 | 1977 | -0.807585531 |
| PixelP7 | 2327.479443848 | 2328 | +0.520556152 |
| PixelP8 | 2692.090909601 | 2692 | -0.090909601 |
| PixelP9 | 3070.000000000 | 3070 | +0.000000000 |
| PixelN1 | -615.200000000 | -615 | +0.200000000 |
| PixelN2 | -794.414240676 | -795 | -0.585759324 |
| PixelN3 | -1046.270150048 | -1046 | +0.270150048 |
| PixelN4 | -1333.096391849 | -1333 | +0.096391849 |
| PixelN5 | -1645.287828809 | -1645 | +0.287828809 |
| PixelN6 | -1977.807585531 | -1977 | +0.807585531 |
| PixelN7 | -2327.479443848 | -2328 | -0.520556152 |
| PixelN8 | -2692.090909601 | -2692 | +0.090909601 |
| PixelN9 | -3070.000000000 | -3070 | +0.000000000 |

All 91,484 entity names and sensitive identifiers are retained; module/chip counts remain 5,066/14,858. The barrel sensitive entities compare exactly. Local disc dimensions and inventories stay fixed; the moved collectors alter transport lengths and their masses. [Comparison](comparison.json) records those changes and executable input hashes against main 7b559d0fbe0287848c46cb1e05c833e0579c43d8. The first-disc/barrel-turn clearance is 2.1 mm, down from 2.3 mm.

[Native checks](native.json) pass: zero ROOT overlaps, exact entities/material accounting and retained sensitive elements. The [workflow](workflow.json) passed configure/build, all six CTests and Geant4 conversion/initialization (FTFP_BERT, seed 42, zero events). This is a construction smoke test, not a particle transport or reconstruction validation. Existing thermal and adverse service-capacity failures remain unresolved. Historical DES014/015 reports are preserved.
