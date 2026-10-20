# IB-P1 PhysVal independent assessment

Reviewed revision: `94d474906660619587b66e850019f0f0fb8e03bd`.
Role applied through the supplied explicit PhysVal mandate; native profile loading is not claimed. This reviewer did not author the reviewed proposal, checkers, geometry or figures. Repository mode was read-only. Only scratch files named `/private/tmp/pr90-IB-P1-*` were created. Initial HEAD matched the target; the paired session journal alone was dirty and was not scientific input.

The primary-artifact assessment supports the report's two main conclusions: the requested inward placement is obstructed by actual finite HCAL material at retained 500 mm depth and 50 mm margins, and the separately unselected outward option has a negative sampled three-station geometric tradeoff. No material correction to those conclusions was identified. Neither result selects a design or grants human sign-off. The active 888-chamber candidate remains byte-identical to the preceding input.

## Findings and disposition

1. **Physical blocker / high impact:** an outside-HCAL B1 chamber cannot fit beneath the fixed BT inner leg with the retained depth and margins. Primary magnetic geometry gives the inner straight-leg centre at 4.60 m and warm inner face at 4.35 m. Thus `R + 0.25 + 0.05 <= 4.35`, or `R <= 4.05 m`. The equality is a limiting contact, rejected by the touching-is-conflict clearance convention. The exact finite HCAL rear-cover projections require `R >= 4.458 m` on four coil planes and `R >= 4.5302525003 m` on the other eight for the retained 1.2833597261 m tangential footprint. These are incompatible by 408 or 480.2525 mm respectively. This is stronger than an argument using only the conservative corner circle.

   Independently reconstructed 36 steel plates plus rear cover in each of 16 sectors form 592 finite occupied prisms, using the pinned HCAL source's actual 1 mm sector seam, steel edge-rail inset, and usable half-z 4.4632 m. Full convex-prism SAT finds actual material intersections for all 48 moved coil-plane B1 cassettes, including their finite z limits. Strict interior witnesses at `(4.120,0,1.000) m` in `HCAL/S00/Steel35` and `(4.153,0,1.000) m` in `HCAL/S00/RearCover` also lie inside moved `B1/F00/Z02`. Available local depth after both 50 mm margins is only 92 mm on the aligned planes and 19.7475 mm on the other eight. Those numbers are upper geometric room bounds, not viable alternate chamber specifications. Redesigning HCAL, BT or chamber technology remains an open physical choice.

2. **Adverse tradeoff / high impact if adopted:** the outward inter-coil alternative is geometrically clear in the audited source model but lowers the three-station proxy. The final alternative has 144 B1 cassettes and 936 total, versus 96 and 888. Its 792 other cassettes are fixed, and 48 unchanged coil-plane B1 identities are retained. Actual dimensions independently give four families: 48 at `(0.937723541425, 0.78695) m`, 48 at `(1.283359726115, 3.2078) m`, 24 at `(1.895447082850, 1.5939) m`, and 24 at `(1.895447082850, 3.2078) m` in tangent width and z length. Its largest B1 corner radius is 6.0743872046 m. Independent angular derivation reproduces the 0.1 degree full-depth, 30 mm border target; projected closure alone is not used as a fit certificate.

   Full-volume SAT gives zero conflicts across all 437,580 pairs of 936 conditional cassettes, all 69,696 B1/support comparisons using 50 mm face-offset support envelopes, and 24 expanded adjacent full-z template comparisons at 20 mm. An independent exact coil check reduces the B1 domain to finite straight BT leg boxes: all B1 volume remains within |z| <= 6.4456 m, axially separated from ECT's 50 mm expanded start at |z|=7.0 m and from the BT returns. All 3,456 B1/expanded-straight-leg pairs are clear. This uses no repository rounded-distance or adaptive-certificate kernel. Certificate magnetic fingerprints and conditional checker input identities also match their pinned sources.

3. **Provenance limitation / low impact:** `views.json` pins plotting source revision, source hashes, displayed polygons and artifact hashes but lacks plotting runtime version metadata at the reviewed revision. Geometry and display identity are independently verified below. A later runtime note must distinguish recorded generating versions from a present-environment inspection; this review does not assert a byte-identical plot regeneration under an unspecified runtime.

## Independent full-4π coverage audit

The bank is exactly 65,536 iid directions, seed 40087, uniform independently in cos(theta) and phi over the full sphere. Rays are stationary straight IP directions with no mirroring, material veto, transport or response. Each cassette must contain both depth-face intersections within its own convex footprint; the 30 mm border is an inward normal offset of the footprint edges. Barrel and endcap cassettes OR within each of three station IDs, then all three station IDs are required. Multiple cassettes in one station cannot manufacture extra stations. The implementation uses independent polygon halfspace intersections and imports no repository kernel.

All counts below use denominator 65,536, including all directions outside the instrumented region.

| Observable | Before count | Conditional count | Gained | Lost | Delta [percentage points] | Paired MC SE [points] |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B1 barrel, outline | 42,086 | 43,264 | 5,511 | 4,333 | +1.797485 | 0.151231 |
| B1 barrel, 30 mm border | 39,333 | 41,894 | 6,883 | 4,322 | +3.907776 | 0.160798 |
| Station 1 union, outline | 54,079 | 55,257 | 5,511 | 4,333 | +1.797485 | 0.151231 |
| Station 1 union, border | 50,092 | 52,653 | 6,883 | 4,322 | +3.907776 | 0.160798 |
| Three station IDs, outline | 43,002 | 42,118 | 1,259 | 2,143 | −1.348877 | 0.088844 |
| Three station IDs, border | 37,644 | 36,961 | 1,245 | 1,928 | −1.042175 | 0.085856 |

These reproduce every corresponding recorded count and paired SE. SE is the sample standard deviation of paired changes in {-1,0,+1}, divided by sqrt(65,536), with ddof=1; it addresses this geometric sampling only. It does not cover detector-model uncertainty or establish significance for reconstructed performance. The four fixed quarter-bank three-station changes are all negative, but those quarters are diagnostics, not independent replication studies.

Loss attribution is independently reproduced using the analytically reconstructed 96 no-frame z-seeded templates and 24 continuous-z templates. All no-frame templates independently clear the fixed coils, so the frame classification does not hide coil rejection. Bordered three-station losses partition exhaustively into 565 frame/packing losses, 1,034 relocated z-seam or same-cassette traversal losses, and 329 finite barrel-end/reach losses. The corresponding outline partition is 711 / 1,038 / 394. First witness direction IDs and absolute eta ranges are retained in the results. Frame loss is a packing-policy counterfactual classification, not proof that every lost ray directly intersects frame material.

The larger standalone B1 fraction therefore cannot support an improvement claim for all-three-station geometry. This bank has a different domain from the earlier central-barrel bank and must not be compared directly to its percentages. No efficiency, fitted segment, pT threshold or momentum-resolution conclusion follows.

## Actual figure and preservation audit

The checker reconstructs 700 unique displayed polygons directly from actual prisms: all 72 transverse current/invalid/unselected B1 sections; 576 steel and 16 cover sections; 24 BT warm sections; and 12 longitudinal footprints. It then independently inverts the SVG axes transforms and matches 1,932 actual vector polygons, including repeated source subsets across the three transverse panels. All four PNG/SVG bytes match the recorded SHA-256 values and their pinned source/input hashes. The actual 3240×1800 feasibility PNG and 2700×900 longitudinal PNG were visually inspected. Labels clearly distinguish current, invalid inward counterfactual and unselected outward trial; common axes and longitudinal finite cuts agree with the metadata. The cropped transverse view explicitly omits the frame, while whole-volume checks retain it.

The complete historical file inventory in the five recorded source/evidence scopes was obtained independently from Git at `56f12ef5b2a9bd410cb77e95ac3140557d92f1b2`. All 687 inventory entries, including active geometry, OBJ, map and prior native evidence blobs, are byte-identical at the reviewed revision, and each retained SHA-256 matches. All 12 source-archive records match the archive bytes, manifest and exact Git objects, including HCAL revision `0e8530d56d171f38c9d53d3c60c8b48803680bbd`. The sibling HCAL working tree was never used. Preservation is a provenance check, not a rerun of prior native physics results.

## Sources, execution and limits

Primary geometry and HCAL sources were examined before the authored feasibility conclusions: target `candidate/geometry.json`, its finite magnetic configuration, the exact HCAL config/design/summary at `0e8530d...`, the existing MUON-001 HCAL identity record, and DES-039 sources. Governing context includes working-tree AGENTS/PROJECT/PhysVal instructions and `nodd-review-validation`, plus target DES-040 and ADR-002/003/006. Subsequent target inputs include the listed feasibility scripts/results/outlines, README, views metadata, source archive/manifest and preservation record. Every source byte used by the checker is read with `git show REV:path`; the results contain the complete locator/hash/size table. The checker neither imports nor executes authored geometry/checker code.

Successful final command, exit 0:

```sh
python3 -B /private/tmp/pr90-IB-P1-check.py \
 --repo /Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout \
 --revision 94d474906660619587b66e850019f0f0fb8e03bd \
 --output /private/tmp/pr90-IB-P1-results.json
```

Final runtime: Python 3.14.6, NumPy 2.5.1, 27.8191 s. Four independent controls pass: duplicate prism detection, remote prism separation, strict steel interior witness, and multiple same-station cassettes not satisfying three station IDs. No ACTS/DD4hep/Geant4, field solve, package installation, source change, optimization, commit, nested agent or external message was performed. Repository logging/closeout remains the coordinator's ownership.

Scratch deliverables:

- `/private/tmp/pr90-IB-P1-check.py`, SHA-256 `255431dd1014e9aa124042d7bbfaebbf2073a93571329939a372ea4c4023bead`.
- `/private/tmp/pr90-IB-P1-results.json`, SHA-256 `5c9e85b3b088d73a69c2c3894663336e745b6a1b1b7343ad408732540a1d7d4a`.
- `/private/tmp/pr90-IB-P1-run-summary.json` retains the actual successful final stdout.
- This report and pinned-input/figure inspection copies remain in the same scratch prefix.

Clearance is source-model geometry with conservative face-offset guards, not a manufacturing tolerance or engineering certificate. The occupied HCAL subset is sufficient to establish its collisions; absence of collisions with that subset alone would not certify clearance to unmodeled modules, rails, flanges or services. Chamber internals, tube segmentation/sag, readout/services, structural and thermal adequacy remain unqualified. Installed nonlinear HCAL magnetic response, material transport/scattering, field masks and reconstruction are not reassessed. The existing middle-wheel uniform eta=3 target remains unmet and unchanged. The evidence supports a bounded infeasibility/adverse-tradeoff response while preserving all unresolved physical choices for human direction.
