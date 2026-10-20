# SS-P1 — independent PhysVal assessment

**Reviewed revision:** `11ec9bb670bca2b882929d1d2b4ef7d9da534da6`. Assignment SS-P1 applies the explicitly supplied PhysVal mandate; no native role-profile loading is claimed. This is a separate assessment context, not human expertise, sign-off or acceptance.

**Recommendation:** the bounded scientific geometry claims are supported. Preserve the adverse tradeoffs and applicability limits. One minor global-scope metadata sentence needs clarification (F1 below); no numerical correction was identified.

Repository: `/Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout`. Every scientific input was obtained through `git show REV:PATH`, including the assigned files and further evidence under their exact commits. The working tree initially had only the coordinator-owned session Markdown dirty; it was not evidence. No repository file was written, no commit was made, no nested agent or external message was sent, and no installed dependency or native engine was executed or modified. Scratch outputs use `/private/tmp/pr90-SS-P1-*`. The coordinator owns journal/project-record reconciliation.

## Finding

**SS-P1-F1 — minor / non-blocking scope metadata.** At the reviewed revision, `docs/validation/DES-040/sketched-stagger-2026-10-20/native-validation/validation.json`, `limits[0]`, says “Geometric fractions use the declared barrel band, not full 4pi.” The report now also contains the `full_sphere` block. Its own sampling definition, the retained bank and the README correctly say full 4π. Scope this global sentence to `geometric_bank`; retain the original source/acquisition fingerprints and all numerical artifacts. This inconsistency does not change the reproduced result.

## Requirements and actual checks

| Requirement / observable | Evidence and assessment |
| --- | --- |
| Exact source, config and frozen field identity | All advertised source SHA-256 values in `artifacts.json`, `validation.json` and `views.json` match the target and the construction freeze `65cf2741bd697ddb8c4022a751f275b41f63241e`. The previous geometry matches the configured `a12efbb5f169e5e02cd1f36aee48c1e748b6ce6f` input. Magnetic configuration, supports, B3 and all endcaps remain value-identical. Retained field NPZ identity matches. |
| Counts and physical choice | Independently counted 936 finite prisms: B1/B2/B3 = 96/216/432; endcap stations = 72/72/48 across both ends. There are 744 barrel outlines, 15 barrel dimension families (2/4/9), 312 changed barrel objects and 484 supports. Actual B1 apothems are 5.20/4.63 m; B2 phase is 7.5°. The choice is a prototype design choice rather than a reviewer-prescribed exact radius. |
| Finite clearance and source interfaces | Independent SAT considered all 437,580 actual chamber pairs (1,236 AABB survivors) and all 151,008 changed-chamber/support combinations (280 conservative expanded-support AABB survivors). No conflicts; 24 neighboring B1 full-z templates clear 20 mm. Duplicate-solid and occupied-support controls conflict. R4.65 gives only 15.220676 mm supporting-plane gap and fails the 20 mm condition. R4.60 gives only 25 mm above the 4.325 m jacket reservation and fails 50 mm. |
| Whole-volume coil/support/source-HCAL proof reproduction | A scratch-prefix-only adapter replays the pinned SS-A1 checker: 312 uncached actual-orientation changed-panel coil audits, all 484 supports, 24 full-z B1/B2 templates and 592 actual finite HCAL steel/cover prisms. This reuses the pinned coil-distance kernel and is reproduction, not independent coil mathematics. Independent SAT/ray calculations use no repository helper. |
| Complete hardware qualification boundary | The source archive’s 20 blobs match both their SHA-256 and their stated Git objects; all 709 prior source/evidence files remain byte-exact. The known 4.325 m reservation is DES034 ECAL water egress, leaving 55 mm at the selected inner B1 plane. Complete external HCAL collectors/cabling/plant routing is absent and unqualified. A conservative HCAL cylinder is a bound, not filled material. |
| Full-sphere geometric availability | Independently reconstructed 65,536 iid unit directions from seed 40088, uniform in cosθ and φ, unmirrored and unselected. New oriented-edge cross-product mathematics tests both depth faces in the same finite cassette, takes the earliest mid-plane distance per distinct station, and ORs barrel/endcap alternatives. Every retained outline/border station and barrel distance finite mask and distance agrees; counters, paired uncertainty, component controls, spacing and loss-class IDs agree. |
| Entrance, world and map | Entire closed entrance plus 10 µm offset has 29.99 mm radial and 27.19 mm axial sufficient reserve. All sampled starts are outside chambers; the minimum sampled first-prism entry gap is 27.3259437 mm. An independent R4.60 inside-start witness rejects; selected R4.63 avoids it. Maximum chamber corner radius is 9.099797510275 m, only 0.202489725 mm inside the 9.1 m numerical world and 0.400202490 m inside the 9.5 m map bound. The world gap is numerical, not installation allowance; frame/feet are not all contained in that chamber-only navigation world. |
| Retained native zero-field events | Audited 5,616 unique native faces against source planes and finite bounds; all 1,024 generated rows complete. Actual contiguous same-cassette entry/exit pairs match independent finite-depth predictions exactly, including 30 mm border. Native barrel station counts are 968/838/920, border 940/804/890; all-three counts 738/674. |
| Retained native curved smoke | Audited finite native events and all 256 generated rows. Statuses remain 197 completed / 59 field-masked; both charges and 5/100 GeV inputs are retained. Actual pair counters agree with reported counters. Maximum plane residual is about 9.905 nm. This is retained surface-audit evidence; portal transitions and a new native execution are not claimed. |
| Export, inventory and figure identity | Native corners in inspection/straight/curved outputs match all 936 source prisms within 3.56e−15 m. Independently parsed four OBJ/MTL exports: 972/744/96/520 objects, all closed after coordinate welding, nonzero enclosed volume and declared material; every blue chamber’s corners/volume match source. Both ZIPs are byte-identical to their members; inventories match source dimensions/families. Actual SVG has 288 blue paths, 72 on each of four axes, matching exact source cuts to ~3.1e−6 SVG units. Retained PNG preview was inspected visually; no pixel regeneration or grey/support shape-math independence is claimed. |

## Scientific result and tradeoffs

The independent primary calculation reproduces:

| Full-4π three-station proxy | Before | After | Gains / losses | Paired Δ ± sampling SE [percentage points] |
| --- | ---: | ---: | ---: | ---: |
| Whole outline | 43,304 / 65,536 | 44,175 / 65,536 | 4,753 / 3,882 | +1.329040527 ± 0.141697848 |
| 30 mm border | 37,860 / 65,536 | 38,723 / 65,536 | 5,608 / 4,745 | +1.316833496 ± 0.155173659 |

The loss partition is exhaustive, mutually exclusive and exact per direction ID: outline 33 fixed-frame / 892 longitudinal-seam-or-coil-packing / 2,957 finite transverse-or-end-reach; border 21 / 798 / 3,926. The seamless full-z diagnostic is a counterfactual and does not define cleared installable chambers.

Border three-station availability is 59.1324% with changed B1 and old B2, 51.5656% with old B1 and changed B2, and 59.0866% with both. B2 rotation is not independently beneficial for this metric. A positive net change in all fixed quarter-bank diagnostics does not imply pointwise improvement. The quoted SE covers iid direction sampling for the fixed geometry; it does not cover geometry, service, field, response or reconstruction systematics.

The common bordered three-station cohort has exactly 33,115 directions. Its median first-to-third chord changes 3.677584→4.177411 m and median middle fraction 0.454942→0.498507. All accepted-cohort, common-cohort and barrel-only quantiles were independently checked. Those conditional straight-ray spacings are neither a constant lever arm nor a bending integral or momentum resolution. The central mirrored continuity bank is separately scoped in the README and is not substituted for the iid full-sphere observable.

Geometry, response and reconstruction remain distinct. These artifacts provide no material veto, scattering/energy loss, MDT internals or response, segment fit, backgrounds, sag/alignment, reconstructed efficiency or improved momentum measurement. Middle-wheel uniform η3 remains UNMET. Unknown external services, engineering installation tolerances and nonlinear/conductor/cryostat qualification remain unresolved.

## Reproduction and retained outputs

Run the portable exact-revision checker with NumPy and the cited Git objects present:

```sh
python3 -B /private/tmp/pr90-SS-P1-check.py \
  --repo /Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout \
  --output /private/tmp/pr90-SS-P1-results.json
```

The checker reads frozen objects and writes only its owned scratch prefix. `SS-P1-results.json` contains actual counters, finite-distance residuals, hashes, spacing quantiles, checks, runtime, limitations and F1. `SS-P1-interface-replayed.json` retains the reused helper audit, and `SS-P1-run.log` is the exact successful-run output. The structured result records the checker SHA-256 and exact input/artifact identities; final output-file hashes are supplied at handoff. The source freeze’s binary/writer/core fingerprints are checked only as retained identities; installed binaries were not reverified or rerun.

Review-parser diagnostics are transparent: an initial curved-border check incorrectly imposed exact 1e−12 m depth membership on native roots with allowed O(10 nm) plane residual. It was corrected to audit finite faces at 1 µm separately from footprint-only 30 mm border membership at 1e−12 m, then use contiguous source-normal entry/exit pairs. The corrected event results agree. A subsequent parser-only correction skips the `input.dat` count header. Neither correction changed source data, physical geometry or a validation tolerance.

Repository workflow instructions, PhysVal mandate, DES040 updated-sketch amendment and ADR002/003/006 were read. Live PR text was not fetched independently; the exact governed interpretation in the frozen DES/README and supplied assignment defines this assessment. No exact client token counters were exposed to this child; no estimates were recorded. No human acceptance is granted.
