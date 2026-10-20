# CR-P1 — independent physics and performance assessment

Reviewed revision: **81eba5c59e811fc61eb6179526db70e61c717be5**. Explicit-fallback PhysVal mandate; no claim of native profile loading. I did not author the refinement. Read-only repository assignment; only this report, the standalone checker/results and extracted Git inputs were written under `/private/tmp/pr90-CR-P1-physics/`. No repository changes, native execution, dependency changes, commits, nested delegation or external messages.

**Recommendation:** the retained evidence supports the stated constrained chamber-outline prototype and its geometry-only crossing improvements. **The requested uniform middle-wheel coverage to |eta|=3 remains UNMET with the fixed ECT, station position and 500 mm depth.** This is a material open requirement, prominently disclosed in the target README; it must remain open when replying to the reviewer. No new implementation defect blocking the limited claims was found. This assessment grants neither engineering acceptance nor human design approval.

## Requirements and evidence

Paths below are relative to `docs/validation/DES-040/refined-wheels-2026-10-20/`, all read from the reviewed commit. Governing context is the pinned DES-040 reviewer-directed refinement and ADR-002/003/006; the working-tree AGENTS/PROJECT and review-validation procedure were also read. Initial dirty content was the coordinator's session Markdown log only; no dirty scientific input was used.

| Requested claim | Independent observable/result | Disposition |
|---|---|---|
| Close large inner fan openings with simple new types | Actual `candidate/geometry.json` contains 12 CORE + 12 PRE_SLOT + 12 POST_SLOT per end, three dimension families. Actual core/filler edge-line distance is 0.020000000000000 m. | Supported for outline geometry; physical BT slots remain. |
| Retain honest residual gaps | Integrating the actual world-coordinate core edge over BT local u=4.30–4.90 m, subtracting the 50 mm inflated warm box, gives **0.535996800447 m²/end**. Post-slot span is 0.520334445405 m. | Residual is extra localized affine reservation, not fully physically required coil material. Narrow bases/long cassettes remain unqualified. |
| Three middle shape families; outer unchanged count | Per end: 12 FULL + 12 BT_LOW + 12 BT_HIGH middle; 24 outer FULL. Independent dimensions give 3/3/1 endcap families, **192 endcaps + 1,056 barrels = 1,248**. | Supported. |
| Preserve fixed physical interfaces | Magnetic configuration, complete supports and all barrel panel JSON values equal the pinned baseline. All **369** listed prior files have identical baseline/target Git blobs and matching SHA-256. | Supported; historical barrel certificates remain historical. |
| Fresh finite-volume separation | Independently reconstructed prism SAT: 5,184 inflated coil-leg box tests, 92,928 support broad pairs/160 expanded-member SAT tests, 778,128 chamber broad pairs/1,448 SAT tests; zero conflicts. Analytic axial bounds exclude coil return regions. | Supported for reservation geometry and prescribed clearances. |
| Eta=3 aperture convention | Nominal near-face radii independently recomputed as 0.648400987941, 0.923349519437, 1.252760699344 m. Actual inner-base apothems are at least these radii. A ray with eta>3 has smaller radius at the near face and cannot cross both normal faces of the same cassette. | Supported as a circumscribed-hole/full-depth convention; side-entry or midplane-only hits are a different observable. |
| Uniform middle eta=3 coverage | At z=9.25 m, nearest ECT leg is within 15°. The eta=3 circle gives local u=0.891887147515–0.923349519437 m and |v|<=0.238980440916 m, wholly inside physical warm u=0.45–0.95 m, |v|<=0.30 m, within the straight-leg axial range. This continuous all-phi proof needs no clearance inflation. | **UNMET; physical obstruction, not a labeling issue.** |
| Move middle behind toroids | At trial centre z=12.35 m actual moved prisms have 72 expanded-frame conflicts and 36 outer-wheel conflicts on the positive end. | Does not fit the fixed layout. |
| Bending benefit | Present centre gaps 2.7544/3.3000 m and span 6.0544 m yield chord product 9.08952 m². Moving middle to 12.35 reduces this to 2.52198 m² (27.7460%). | Constant-curvature geometric proxy only; no momentum-resolution conclusion. |

Actual family near-face eta limits differ from the earlier illustrative interface witness:

| Station/family | Actual inner apothem [m] | Sector-centre eta | Inner-base corner eta |
|---|---:|---:|---:|
| Inner CORE | 0.648400987941 | 3.000000 | 2.976477 |
| Inner PRE_SLOT | 0.648400987941 | 3.000000 | 2.999913 |
| Middle FULL | 1.010000000000 | 2.910788 | 2.903484 |
| Middle BT_LOW | 1.066512492075 | 2.856684 | 2.849322 |
| Outer FULL | 1.252760699344 | 3.000000 | 2.992457 |

These corner values describe actual finite bases, not all-phi acceptance. The fixed three-family middle construction loses additional aperture beyond exact ECT shadows. The retained earlier `review/interface-report.md` correctly labels its 1.07 m base and nominal polygon illustrations as distinct from this final candidate.

## Checks actually executed

The standalone `physics-check.py` imports no repository code and reads evidence through `git show --revision`. Final successful command:

```sh
python3 -B physics-check.py --repo /path/to/nodd \
  --revision 81eba5c59e811fc61eb6179526db70e61c717be5 \
  --output /tmp/physics-check.json
```

Python and NumPy versions and all read evidence SHA-256 are recorded in `physics-check.json`. The checker independently implements convex halfspaces/SAT, both-depth-face ray evaluation, raw finite-event traversal accounting, aperture/spacing math, artifact parsing and historical identity checks. Earlier scratch-only checker fixes corrected inventory field names and the actual SVG display color (`#0060fe`, consistent with the retained divisor-256 convention); neither was a scientific-data failure.

- **Raw straight events:** 1,024/1,024 rows complete; all 5,924 retained finite hits checked against source/native faces and IDs. Reconstructed same-chamber opposite-large-face station pairs are [976,878,1014], all-three 850; with 30 mm border [868,790,948], all-three 674. Independent analytic per-track/station masks have **zero outline and zero border mismatches**. No endcap orphan/open visits. Native input DAT rows equal the retained NPZ exactly; native straight hits also lie on their declared input rays.
- **Raw curved events:** all 256 rows retained; **93 completed, 163 field_masked**, four local momentum/charge cases, 908 finite hits. Independent pairs [248,98,84], all-three 78; border [192,89,78], all-three 35. Maximum face-plane residual 9.07e-9 m; no endcap orphan/open visits. This audits recorded events, not the accuracy or convergence of a newly executed transport run. No efficiency or momentum improvement follows.
- **Independent cap bank reproduction:** seed 906310, **32,768 independent iid directions mirrored to 65,536 rows**, uniform cos(theta) over 1.3<abs(eta)<3 and full phi. All before/refined station and all-three counts reproduce exactly. All-three outline counts: 29,174→53,604; 30 mm border: 23,698→43,332. Marginal outline sampling standard errors are 0.2745/0.2132 percentage points using N=32,768, not 65,536. These are restricted-cap geometric fractions, not full-sphere coverage, active response or efficiency; physical uncertainty and paired-difference errors are separate.
- **Source/native/export consistency:** all 7,488 native face IDs unique; native corners and actual chamber OBJ vertices agree with source within 3.56e-15 m. Four OBJ object counts match manifests (1,284/1,056/96/520). Both ZIP archives contain byte-identical sibling OBJ/MTL members. Inventory has all 192 endcap IDs/seven dimension families with dimensions matching actual vertices. Source/export figure hashes match.
- **Actual figure source and pixels:** independently parsed combined SVG blue polygons **36/36/24**, inverted the plotted metric transforms and matched them to retained source polygons (maximum roundtrip 5.53e-8 m). Section JSON/source corner differences <=6.36e-11 m. I opened and visually inspected the pinned `xy-sections/endcap-wheels-xy.png` and `inventory/after-endcap.png`: readable labels, common metric XY scale, clear blue chambers/gray obstructions, visible middle central warm-coil union, and seven correctly labeled shapes. No misleading hidden physical overlap was apparent.

## Author checks inspected, not rerun

`candidate/geometry-controls.json` records 192 adaptive audits and 343,392 cells with every accepted result clear. Occupied coil/support, incorrect rotated-bound, nominal eta aperture without ECT exclusion and duplicate-panel fixtures are rejected. I audited those records and their source strategies, including rejection of unresolved cells, and independently reran finite-volume SAT; I did not rerun adaptive subdivision or the six author unit tests. The author's 150,000 XY membership checks, OBJ closure/orientation checks and native execution are retained author evidence, not reruns by this reviewer. Installed ACTS binaries/libraries were not accessed or certified anew.

The reviewed revision is distinct from geometry/native acquisition **dcd49de80519a6d206599682f329f708b0e8465d** and export whitespace refinement **4cc2b08a824af5f8813e786a6845d7d1e42ee12f**. Current target source and figure hashes match the retained manifests. All 369 earlier blob/SHA identities were independently checked against baseline **5f42c4b9649619771e8d5ec70247c99b10d8e80f**.

## Findings, limitations and remaining decisions

1. **Material open requirement:** uniform |eta|<3 middle coverage cannot be marked satisfied. The target README already makes this prominent. Keep it explicit in the reviewer reply and project closeout; a physical magnet/station/depth-layout alternative and its validation require a separate human decision.
2. **No new blocking defect:** within the explicitly constrained outline prototype, topology, clearance, aperture descriptions and reported geometric/native observables are supported. The residual slot reservation must stay labeled conservative, and geometric area gains must not become momentum or efficiency claims.
3. **Low-severity metadata ambiguity:** refined `compartment.phi_deg` uses the 30° parent/repetition cell even for a 15° middle cassette or narrower filler; `radial_m` is similarly a parent reservation. Actual vertices are authoritative and every assessed export/crossing uses them, so this does not affect results. Consumers should not interpret these fields as exact active polygon bounds. No frozen-geometry rewrite is needed for the current review.

No material, scattering/loss, MDT internals/segment response, fitted reconstruction, field-mask extrapolation, structural/thermal/services qualification, production integration or full-sphere efficiency was established. Long cassette manufacturability and installed-field/material effects remain unresolved. This bounded independent review is complete; the coordinator owns retention, publication, journal and tracking closeout.
