# DES-012 — Pixel barrel DD4hep validation

Status: PROTOTYPE; numerical software validation, no engineering acceptance.
Date: 2026-09-30. Governing [DES-012](../../design/DES-012-dd4hep-pixel-barrels.md).
Baseline PR #29: `c79c2194e23e99c4d2696ca2d6628a388b96f5e4`.
The standalone assembly implements the human-selected baseline while retaining
configurable provisional material and explicit effective-service hypotheses.

## Reproduction and provenance

Follow [the build and variant commands](../../../detector/README.md).
The [environment record](environment.json) records current package versions and
changed setup/lockfile fingerprints. The existing node-registry preflight returns
2 (unverified fingerprints); task-specific imports, compilation and construction
were performed against DD4hep 1.38 and ROOT 6.40.04 with Python 3.14.5/C++20.
No shared dependency was changed. Geant4 11.4.2 is installed but transport was
not run. The full ACTS source/runtime was not needed for this DD4hep-only check.

Runs use the stated starting Git revision plus uncommitted implementation whose
exact source SHA-256 hashes appear in each report. Source/input/configuration,
compact and compiled-library hashes distinguish the executed artifacts. The
retained report's command records the local invocation; the generated compact is
recreated from repository inputs rather than committed. Future rebuilds should
compare physics inventories and IDs, not compiler-dependent binary hashes.

## Required checks

Construction, physical inventory and exclusive-volume mass accounting cover every
expected entity. Sensitive centres and signed outward normals match the frozen
source placements; readout volume IDs must be unique and decode to their original
fields. Grid offsets align the 400 × 384 cells to the active patch boundaries.
ROOT checks overlaps/extrusions at 10⁻⁵ mm; transforms use the stricter executed
10⁻⁷ mm tolerance and mass/volume comparisons use relative 10⁻⁶.

The navigation sample contains 75 deterministic straight rays: origins
(0,0,0), (1,1,−150), (1,1,150) mm, eta −2,−1,0,1,2 and phi
0,0.37,1.11,2.29,4.73 radians. No random seed is used. ROOT boundary navigation
integrates radiation/interaction lengths through actual materials, excluding the
world medium. This sparse sample tests navigation; it is not a new hermeticity
or magnetic-field performance study.

## Material interpretation

The provisional cable outer-footprint composition is Cu/polyimide/air =
10/40/50% by volume. The inherited 50% longitudinal routing packing fraction
then yields an effective bundle of 5/20/75% by volume, density 0.7329 g/cm³.
Changing copper to 5% or 20% exchanges air at fixed 40% polyimide. The retained
[low](cable-cu05.json) and [high](cable-cu20.json) configurations preserve every
placement and identifier. These are sensitivity hypotheses, not supplier bounds.

Service cells conserve the original reference cable footprints (5,810,978.24 mm³
ancillary and 2,469,423.11 mm³ links), transport Ti (62,469.41 mm³) and liquid-CO₂
inventory (616,841.35 mm³). Longitudinal bundles and 96 end-bay cells count each
source route once. Local evaporators are separate. Each sector has four radial
bins, with 2 mm bay-boundary allowances; cells occupy |z|=557–603 mm, and the
outer bin reaches r=232 mm. Small transition lengths and collection arcs are
represented by their conserved material inventory inside those cells, rather
than literal continuously connected pipe turns. Remaining cell space is air.
This smearing affects directional material and needs review before detailed
tracking-performance conclusions.

Material radiation/interaction lengths are computed from the declared molecular
or mass composition. They need not match earlier DES-002 scalar screening X0
assumptions; the previous evidence is preserved. Contact shims add 0.255 mm of
graphite behind each ASIC; no sensitive surface or support plane is moved.
The effective foam/core preserves both foam mass and additional glue inventory.
The Air world medium, geometric voids, and unmodelled hardware must not be interpreted as
qualified zero-mass engineering. Bump metal, bonds, connectors, manifolds,
fasteners, end brackets and additional passives remain incomplete inventory.

## Failures and corrections

Initial compact loading failed because ROOT's mixture converter cannot use the
sparse eight-element table. The replacement is a complete 98-element table from
the pinned public ODD source, with license/provenance retained. The curved-foot
audit was corrected to recognize DD4hep's full-circle TGeoTubeSeg representation
while independently checking its dimensions and transform. An initial run passed
geometry checks but crashed during ROOT static cleanup; such a process is not
counted as a passing integration test. Explicit DD4hep singleton destruction followed by ROOT geometry deletion before
static teardown gives a clean process exit; final execution outcomes are below. No geometry tolerance was relaxed.

Geant4 execution, ACTS conversion, field navigation, manufacturing tolerances,
thermal/hydraulic performance, mechanical stiffness and full-detector integration
remain untested and outside this standalone software validation.

## Executed results

[Nominal report](nominal.json), [5% Cu](cu05.json), [20% Cu](cu20.json) and
[comparison](comparison.json) all report PASS; all three validator processes
exited 0. CTest passed 2/2 (ten pure Python controls and one full DD4hep validation).
The preserved CTest stdout is `ctest.txt`. The dashboard fixture/link/history
checks passed 2/2; dashboard validation/build and session validation also passed.

| Quantity | Verified result |
| --- | --- |
| Layers / staves / modules | 4 / 82 / 2,750 |
| Sensitive chip patches | 6,206 |
| Mounting rings / feet | 24 / 492 |
| Local cooling tubes / CO₂ volumes | 164 / 164 |
| Longitudinal cable steps / end cells | 2,750 / 96 |
| Expected audited entities / total physical placements | 39,386 / 39,388 |
| Overlaps / extrusions above 10⁻⁵ mm | 0 in all three runs |
| Maximum sensitive centre residual | 8.16 × 10⁻¹⁴ mm |
| Maximum sensitive normal residual | 2.48 × 10⁻¹⁶ |
| Unique volume IDs / pixel cell-address checks | 6,206 / 31,030 |
| Navigation rays / layers exercised | 75 / all four |
| Sensitive crossings per test ray | 1–5 (phi seams and overlap can change the count) |

The geometry remains unchanged in the material variants. Their masses include
all represented module/support/cooling/mount/cable materials, including mixture
air, and exclude the world Air volume:

| Cable Cu / polyimide / air, volume % | Modeled mass [kg] | Test-ray mean X/X0 | Test-ray maximum X/X0 |
| --- | ---: | ---: | ---: |
| 5 / 40 / 55 | 20.345 | 0.2146 | 0.5581 |
| 10 / 40 / 50 | 24.054 | 0.2859 | 0.7221 |
| 20 / 40 / 40 | 31.472 | 0.4284 | 1.0501 |

These means are unweighted summaries of the navigation sample, not acceptance-
weighted tracker material budgets. The large copper sensitivity is a reason to
replace the provisional recipe when expert input becomes available. The 20% case
exceeds one radiation length on the most material-rich sampled direction; it is
not evidence of a qualified low-material design. Neither a numerical PASS nor
inventory conservation approves this material hypothesis.

Selected nominal material properties computed by ROOT:

| Material | Density [g/cm³] | Radiation length [mm] | Interaction length [mm] |
| --- | ---: | ---: | ---: |
| Silicon | 2.329 | 93.701 | 457.728 |
| Graphite | 2.21 | 193.199 | 362.902 |
| CFRP | 1.73 | 243.421 | 444.171 |
| Epoxy | 2 | 205.335 | 356.473 |
| CO2 | 1.0964 | 330.127 | 807.141 |
| CableMix_0 | 0.7329 | 238.932 | 1481.217 |
