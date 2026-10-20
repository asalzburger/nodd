# BO-P1 — final independent PhysVal artifact assessment

Reviewed revision: `0933e439a69e199fb17e250d792ba35d0feaf9ab`.
Assignment: BO-P1, explicit fallback PhysVal mandate. Reviewer authored none of the implementation. Native custom-profile loading was not claimed. Repository skill used: `.agents/skills/nodd-review-validation/SKILL.md`; governing context was AGENTS.md, PROJECT.md, DEVELOPMENT_PLAN §6, AGENT_WORKFLOW, ADR-002/003, and pinned DES-040. This is an independent automated assessment, with no human design or engineering acceptance.

**Recommendation: bounded no-new-blocker for presenting this isolated unsigned prototype and its restricted geometric/native event claims.** The actual frozen artifacts agree with the source and reported figures. The net geometric gain contains substantial local losses under the same-cassette observable and must be presented as a tradeoff. Mechanical/response/material/reconstruction qualification and uniform middle-wheel eta3 remain unresolved. This recommendation cannot advance a lifecycle state or establish buildability.

## Material scientific finding and acceptance boundary

**BO-P1-F1 — P2 interpretation / local-coverage tradeoff.** The published net three-station gain is correct but is not a pointwise improvement. In the 32,768 independent directions (each later mirrored), the outline proxy gains 6,198 previously failing directions and loses 2,009 previously passing directions: net +4,189, or **+12.783813 percentage points**. The 30 mm border proxy gains 6,655 and loses 2,223: net +4,432, or **+13.525391 points**. Outline losses are 508 B1-only, 605 B1+B3, and 896 B3-only; border losses are 430 B1-only, 724 B1+B3, and 1,069 B3-only. No previously all-three passing direction loses B2.

These are physically explained changes of this geometric proxy. Coarser longitudinal repacking relocates seams, while the full-depth definition requires *both faces of one finite cassette*. A ray crossing one large face in each of two adjacent cassettes fails that declared observable even when both station faces occur in the station’s union of envelopes. B3 radial relocation also changes longitudinal face crossings. Two actual-source examples establish the mechanism:

- Geometric bank row 13, eta=0.5799530646, phi=147.8578191511 degrees: before `B1/F10/Z05` contains both faces. After, the ray’s B1 depth-face z values are 3.0365462483 and 3.3432680916 m. `B1/F10/Z02` ends at 3.2178 m and the following cassette starts at 3.2378 m, so neither holds both.
- Geometric bank row 163, eta=0.2047202703, phi=316.7317625465 degrees: before `B3/F21/Z07` contains both faces. After, the odd-B3 crossings are at z=1.7531033719 and 1.8562270997 m, spanning the adjacent 1.7771428571–1.7971428571 m seam; `B3/F21/Z04` begins at 1.7971428571 m. Again, no same cassette contains both.

These row IDs belong to the recomputed `bank(32768)` at seed906320, **not** to the 1,024-track native bank, whose n512 RNG draw size produces different phi values. Evidence: pinned `tools/muon_layout/barrel_validation.py:38–60,163–180`, the before and after geometry panel IDs above, and checker JSON `paired_sampling` (which retains full exact crossing coordinates/bounds). The combined z-packing/stagger result should retain gained/lost counts and this explanation. No parameter retuning or acceptance change is recommended by this finding.

**BO-P1-F2 — P3 uncertainty / claim precision.** Mirrored partners are not independent trials. Using 32,768 iid directions, the ordinary binomial sampling SEs for before/after three-station outline fractions are 0.27379/0.25460 percentage points; for the border proxy 0.27605/0.26838 points. The paired improvement SEs are 0.26730 and 0.27767 points. These characterize Monte Carlo precision in the declared eta band, not geometric, manufacturing, response or reconstruction uncertainty. Four decimal percentage places are reproducible sample arithmetic, not physical accuracy. Evidence: `native-validation/validation.json#/geometric_bank`, source RNG construction, checker `geometric_bank` and `paired_sampling`.

**Preserved unresolved requirements, not new source defects:** 48 B2 and 96 B3 outlines are narrower than 0.5 m; B3 minimum width0.3184980216 m and minimum footprint area0.2782307717 m². They satisfy the existing area/longitudinal rules, which do not set a universal tangent-width floor. Their MDT internals, tube length/sag, alignment, readout/services, support/loading and installation feasibility remain unqualified. Native chamber-world R9.1 m leaves only0.0002024897 m radial numerical margin and contains vacuum chamber boundaries. Frame/feet extend outside that world/map; this is not a passive-material transport model. Uniform middle-wheel coverage to eta3 remains **UNMET**, unchanged with the retained endcaps and ECT obstruction. Evidence: pinned DES-040:417–430; README:49–59; actual source outlines and checker size/envelope results.

## Requirements-to-observables matrix and actual checks

All locators in this section refer to the reviewed revision. Report prefix `S` is `docs/validation/DES-040/barrel-overlap-2026-10-20/`.

| Requirement / claim | Independent actual-artifact result | Evidence / limit |
|---|---|---|
| Fixed magnetic inputs, 484 supports, 192 refined endcaps | Source objects value-identical to the refined-wheel baseline; fixed interface fingerprints agree | `S/candidate/geometry.json`, config and baseline geometry; no field solve run |
| Final chamber count / dimension tradeoff |888 total;696barrel B1/B2/B3=96/168/432;192endcap=72/72/48. Barrel families7→13 (1/3/9 after) | Actual footprints, IDs, sizes; no manufacturing family qualification |
| Radial stagger / full-depth projected overlap | Actual B3 odd apothem8.75 versus even8.2m; half-widths reproduce0.1degree with30mm border | Uncut template statement only; actual finite z/hardware cuts retained |
| Physical nonintersection | All393,828 final panel pairs examined with AABB screening plus independent convex SAT;1,172 candidate SAT checks, no conflicts | Actual whole prisms, including barrel/endcap pairs |
| All actual barrel/support margins |696×484 members screened;1,548 candidate SAT tests with50mm face-expanded support envelopes; no conflicts | Independent convex-prism calculation; nominal exact source geometry, not engineering tolerances |
| Whole-volume coil / seam controls | All696 recorded barrel coil/support proofs clear;264 merges accounted; zero historical barrel certificates loaded | Inspected certificates/adverse tests/source math and identities; adaptive coil kernel was not independently rerun |
| Native finite construction |888 chamber volumes;5,328 unique faces;21,312 face-corner rows match source within3.55965e-15m | Actual inspector CSV; native library commit remains unknown in metadata, binary/library hashes are recorded |
| Native zero-field events |1,024complete,6,536hits; all actual station flags match independent full-depth rectangle calculations, outline and border |834/848/920 station pairs;770/804/890 border;710/628all-three. No orphan/open/duplicate/tangent events found |
| Native unchanged-map smoke |256rows,197complete and59field_masked retained;1,252hits; actual finite events reproduce all reported counters and IDs |146/153/175station pairs,134/132/174border;115/103all-three. Max plane residual9.69547e-9m; no efficiency inference |
| Seed/config/source identity | Seed906320; n512 native bank and fixed n32-per-end curved preselection match NPZ/input.dat;5/100GeV and both charges match. Recorded source hashes match target and7d8c51f source freeze | Pinned source and native files, not current dirty source |
| Actual geometric bank | Independent65536-row recomputation matches every station/all-three count:56.6040039→69.3878174% outline and48.2971191→61.8225098% border |32768iid central0<abs(eta)<1, fullphi, plus reflection. Same finite chamber at both depth faces |
| Native OBJ/MTL/ZIP | Four bundles:924/696/96/520objects with expected chamber/coil/frame roles; each closed with consistent outward winding and positive signed volume; finite chamber/frame vertices agree with source; ZIP members equal siblings | Actual OBJ/MTL/ZIP bytes; coils are nonconvex closed racetracks so positive signed volume/edge orientation, rather than global-centroid face tests, establish orientation |
| Final XY and longitudinal views | Actual72sections per before/after;50,000source membership points each with0mismatches;52/38longitudinal footprints match source phi15degrees | Both PNGs viewed; SVG valid and draft labels retained; section coordinates encode10decimal places (max6.69e-11m rounding residual) |
| Final visual/identity consistency | All four OBJ PNGs and after-barrel13-family inventory inspected; blue/grey objects and finite cuts are represented. Artifact hash entries agree | Preview transparency is display-only; frame OBJ contains reservations, not mass union |
| Historical evidence preservation |449baseline paths have identical Git blob IDs and SHA256values at target | Actual manifest set and every blob checked against baseline e0fd6ad0e4cd8df96356c00ab35095446c3e9ce3 |

The statistical observable is vacuum/straight finite geometric availability in a selected barrel band. It measures neither full4pi acceptance nor detector efficiency, and does not include scattering, energy loss, chamber response, reconstruction, momentum resolution or installed magnetic material. The 59 field-masked smoke rows cannot be dropped or interpreted as failures of chamber response. Old broad/native studies remain historical for their old geometries. The geometry, support, field and endcap boundaries inspected here support the bounded comparison without a new magnetic calculation.

## Commands, outputs and ownership

The final command actually executed successfully was:

```sh
python3 -B /private/tmp/pr90-BO-P1-check.py --repo /Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout --revision 0933e439a69e199fb17e250d792ba35d0feaf9ab --output /private/tmp/pr90-BO-P1-check.json
```

Final result: **39 checks passed, zero failed;495 pinned blobs read;18.067740 seconds**. The checker uses Python standard library/NumPy only, reads blobs through `git show`, writes only the requested JSON, and never imports or executes repository modules. Checks use pinned source, finite geometry and retained raw native event/mesh artifacts. They do not depend on the current working tree or a local ACTS installation. The source/artifact freeze is7d8c51f304dc79bd187279580b4e1cb5464f7974; the final reviewed artifact commit is0933e439a69e199fb17e250d792ba35d0feaf9ab. The executable/library fingerprints in artifacts were inspected as retained metadata, not rerun or remeasured from ignored binaries.

Before the final pass, checker development exposed one local NumPy API incompatibility (removed2D cross product) and two incorrect checker assumptions: using a global centroid to orient nonconvex racetrack surfaces, and requiring1e-12m agreement for view coordinates explicitly rounded to1e-10m. Those checker errors were corrected from primary source. No repository test, physics tolerance or input was changed. All original failures were checker development failures, not new geometry/native failures. Eight repository tests and the author's native executions were inspected as recorded evidence; this reviewer did not rerun them. No ACTS/performance/field study or dependency setup/install was performed.

Starting HEAD matched the reviewed commit. The only initial dirty tracked files were the paired barrel-overlap journal; their bytes were not task evidence. A later coordinator-only clarification of seed diagnostics is outside this reviewed revision and was not reviewed. No repository files, source, configuration, dependencies, commits, external messages or lifecycle records were changed by BO-P1. Scratch checker/results/report and extracted viewing inputs are under `/private/tmp/pr90-BO-P1-*`. The coordinator owns durable journal reconciliation. Exact per-turn token counters were unavailable; no usage was estimated.

Deliverables:
- `/private/tmp/pr90-BO-P1-check.py` — portable focused checker.
- `/private/tmp/pr90-BO-P1-check.json` — actual results, all checks, paired counts/examples and input SHA256/size inventory.
- `/private/tmp/pr90-BO-P1-report.md` — this assessment.
