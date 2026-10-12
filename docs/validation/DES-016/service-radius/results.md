# DES016 — fixed service-radius revision

Status: **DRAFT / isolated PROTOTYPE. Radial interface/body/overlap screens pass; original-annulus hermeticity FAILS explicitly.**

The user required the radial layout to remain within cable/service bounds, removing the outermost row if needed. This supersedes the [nine-ring proposal](../radial-revision/results.md) while preserving its evidence and the [Cartesian control](../results.md). [DES016 DO-C08/09](../../../design/DES-016-pixel-disc-module-optimization.md) records the amendment before implementation.

## Fixed radial interfaces and surviving layout

Remove the complete outer **63-module ring**: **296 single modules/chips remain in 8 rings**. Keep all surviving centres, axial levels, axes and stable identifiers at every disc distance; the 18-single inner ring remains unchanged. No matrices, silicon outlines, nominal annulus or disc positions are resized. The independent PR40 movement table and production compact are unchanged.

| Ring | Single modules | Template radius [mm] |
| --- | ---: | ---: |
| 1 | 18 | 41.150000 |
| 2 | 22 | 59.283438 |
| 3 | 28 | 77.500314 |
| 4 | 34 | 95.778759 |
| 5 | 40 | 114.103911 |
| 6 | 46 | 132.465529 |
| 7 | 51 | 150.846077 |
| 8 | 57 | 169.252443 |

Maximum occupied/reserved radius across all distances is **183.388628 mm**, inside the inherited **r188.5 mm plate**, with **5.111372 mm clearance**. It clears the unchanged **r190 mm collector/service boundary by 6.611372 mm**, and effective **r192 mm trunk by 8.611372 mm**. The ≥2 mm radial collector gap is retained. Five inherited 1.2 mm axial levels keep ≥0.2 mm occupied-body separation; negative-side reflection preserves the outward periphery. The local OD2.8 mm circumferential tube bound reaches r172.904748 mm on the first disc.

The inherited quad-specific +16 mm pickup-land offset would reach **r191.716115 mm**, beyond the plate, so it is a rejected reuse control. An **18×8 mm provisional land reservation at +7.6 mm** is contained within the slim single-body silhouette, ending at its outboard edge. This dimension follows 0.9+21.4/2−8/2 mm; it is a NODD DESIGN CHOICE for bounding geometry. It does not qualify a thermal contact, foot manufacture or swept pipe/flex artwork. Contact, heat-transfer, stiffness, flexes and bends still require engineering within these fixed bounds; none is moved into the service trunk.

## Coverage and overlap — retained loss

The original nominal **r32.3..181.4550267061104 mm** annulus stays the comparison target. Whole-ring removal leaves outer-edge holes. Across all nine distances and the three sampled on-axis vertices, uncovered area bounds range **2528.658..3333.820 mm²**; covered area fractions range **96.6716..97.4755%**. Direct endpoint counterexamples disprove full-annulus hermeticity; no certificate is relabelled as passing and no reduced target is substituted. These are projected geometric areas, not tracking efficiency or momentum-resolution measurements.

First-disc silicon overlap is **16.690% whole / 16.704% annular**, with worst **18.476%** across all distances, under the authorized 20% maximum. Original guard/body assumptions remain unqualified; the 0.5 mm guard control is retained in the screening. Radial/tangential axes and the prior covariance scope are unchanged.

## Native ACTS and retained controls

Native acts-nodd constructs **5328 candidate sensitive planes** and compares **378 matched tracks per layout** with the actual staggered baseline. The original 324 probes span 18 discs, 0/2 T, pT 1 GeV, both charges and vertices −150/0/+150 mm; 54 added straight edge probes target r181 mm within the original annulus. Six exhaustive first-disc controls bypass the broad-phase filter. Native finite-plane IDs/intersections agree with the analytic oracle; candidate target-disc misses: **54**, baseline misses: **18**, explicitly retained in [acts.json](acts.json). Transport agreement is not hermeticity. No fitted resolution, global navigation, continuous helix or transverse-vertex certificate is asserted.

## Cable/cooling accounting with fixed service bounds

Conditional heat is **795.648 W/disc**; **26 chains** obey ≤16 physical modules and ≤32 chips, and **16 half-ring cooling circuits** count both feed and return: **32 radial legs**. Both OD4 mm transport legs consume 402.1 mm²/disc. Circumferential tube length is 5348.8 mm/disc before transport legs, bends and manifolds. These are spatial inventories, not routed/hydraulic qualification.

Use the existing **r192..231.7 mm trunk** and **r192..222 mm flange neck**, with inherited packing/phi fractions and barrel traffic. The smaller layout neither widens the outer service envelope nor moves its inner boundary inward.

| Scenario | Cables/disc [mm²] | Both pipe legs/disc [mm²] | Accumulated demand [mm²] | Trunk capacity [mm²] | Trunk utilization/status | Neck capacity [mm²] | Neck utilization/status |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| reference | 1502.0 | 402.1 | 26117.9 | 19816.6 | 1.318× / FAIL | 14632.0 | 1.785× / FAIL |
| conservative | 1502.0 | 402.1 | 34987.3 | 10568.9 | 3.310× / FAIL | 7803.7 | 4.483× / FAIL |
| stress | 2390.0 | 402.1 | 56669.8 | 10568.9 | 5.362× / FAIL | 7803.7 | 7.262× / FAIL |

Packing failures remain unresolved; clearance alone does not guarantee cable capacity or close inherited thermal/support failures. Guard qualification, engineering of the bounded single-module contact/routing, and any restoration of full-annulus acceptance require review. No design sign-off or production integration is recorded.

## Reproduction and provenance

[Inputs](inputs.json), [screening](screening.json), [retained surviving transforms](layout.json), [ACTS](acts.json) and [hashes](artifacts.json) pin the inherited interfaces, exact source control, code/runtime and acceptance-loss evidence. Follow the [README](../../../../tools/pixel_disc_optimization/README.md). Boundaries/envelopes are inherited NODD DESIGN CHOICES; whole-ring removal and land reservation follow the human-directed DO-C08/09 amendment; areas, clearances, counts and service arithmetic are INFERENCES. Edge-track values are numerical test controls. No new external technology or experimentally qualified performance claim is added.
