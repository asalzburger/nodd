# R1 — Exact-revision PhysVal method/control review

**Target:** `85b044d2a5591828efe492a651b8aee11593a42b`.
**Scope:** code, method, retained native controls and bounded independent probes. Production arrays, plots and scientific fractions were not frozen for this assignment and were **not reviewed**. This uses the explicit fallback PhysVal mandate; native profile loading and human expertise/sign-off are not claimed. No repository or shared dependency files changed.

## Findings

1. **P1 — Summary construction fails at the reviewed revision.** `tools/muon_layout/acts/analyze.py`, the `audit=dict(**geocheck,...max_plane_residual_m=...)` construction, repeats a key already returned by `face_catalog`. Python raises `TypeError: dict() got multiple values for keyword argument 'max_plane_residual_m'`. This prevents the unmodified target from creating its summary after saving arrays. The coordinator independently discovered it and reports a fix at77c652e; that later change is outside this exact-revision review and requires R2 verification.
2. **P2 — Pure tangential contacts counted as literal large-face crossings.** `analyze.py:count_events` inserts the face into `large`/`active_large` before the tangent branch. An independent six-contact fixture produces6unique faces,0paired stations and6tangent events, despite no crossing. DES040 describes the literal metric as crossings. The coordinator accepted this finding and reports excluding tangents from crossing sets, adding a regression and finding no tangents in the production run. Those later code/result statements are not yet independently verified; R2 must check the fixed counter and final artifacts.

No additional blocking physics/method defect was identified in this bounded assessment. These findings concern the exact target, not a predetermined rejection of the prototype approach.

## Source and native method assessment

All1560 frozen rectangular/trapezoidal prisms are represented by actual Gen3 `TrackingVolume`/`GenericCuboidVolumeBounds` leaves. There are9360 native finite boundary faces,3120 large faces and9360 unique uint64 chamber-face IDs. The source transform/vertices are preserved. The geometry is a chamber-envelope vacuum tracking geometry; it does not contain the support frame, coil solids, chamber internals or material.

The primary method really propagates with ACTS EigenStepper/Navigator to native surface roots and checks actual finite native faces at those positions. Coplanar ownership fanout does not intersect a postprocessed trajectory polyline or move the root. The documentation correctly qualifies this as a support-root/finite-owner audit, **not chamber portal-transition qualification**. Legacy finite-portal mode is retained as an adverse control.

The C++ field provider preserves SI→ACTS position/field conversions, q/(total-p), the cylindrical trilinear grid and global Cartesian rotation. It wraps only the field by30degrees, retains both z signs and rejects any invalid stencil corner/out-of-domain query. Mask failure may arise at an RK query before a completed step; it is correctly an unavailable vacuum-field trajectory, not evidence of material absorption or detector inefficiency. No filled/extrapolated field was found.

The finite-AABB radius2*maxStep+2*tolerance conservatively covers faces reachable within one bounded step. Indexed/exhaustive controls compare grid enumeration to a linear scan with the **same reach bound**; they do not independently prove that shared bound or all root behavior. The global valid-node norm bounds the interpolated field norm, hence constant-momentum curvature. The planar no-forward-root guard uses a conservative step bound, changes no field or hit, and preserves pending native negative corrections. Cylinders are explicitly outside that planar proof; three independent native cylinder-edge probes below passed. Finite controls, native integration/target tolerances and explicit path/step limits remain limitations rather than global numerical guarantees.

The local2.65GeV stress point and5/10/100/1000GeV cases are honestly separate from MUON001's central5GeV-IP candidate. Closed entrance/caps, radial seed prescription and10µm forward offset are explicit. Full-sphere and finite-eta-display samples are separate, with correct solid-angle weights and common directions across p/q. No eta-dependent energy-loss correction or reconstruction/segment efficiency is claimed.

Unique large faces, paired same-chamber visits, distinct station IDs, side events, duplicate/reentry counters and border-inset results are otherwise separated appropriately. All generated rows remain in denominators; threshold witnesses before later field failure are retained, with unresolved-event availability bounds explicitly distinct from confidence intervals. A material-free envelope-face proxy does not certify multilayer response, measured resolution or the actual minimum IP momentum.

## Evidence actually checked

- Extracted exact committed source/evidence using `git show`; manifest retained in `/private/tmp/pr90-acts-R1-fixed/manifest.json`.
- Verified current controls' five recorded implementation/config hashes and governing-DES hash against exact target bytes. Both failed records remain present: initial binary5925240... and refinement-failure binary92ffcdf.... Current binary22b30c... controls pass their recorded gates.
- Reviewed recorded native evidence:4111field queries;1560prisms/9360faces;256distinct zero-field directions;160indexed/bounded-exhaustive tracks representing16common directions across10p/q cases;800-track half/quarter-step, tighter-target and tighter-RK comparisons. No event/count/status differences; worst recorded position delta1.187407µm versus unchanged10µm gate. These are captured execution records, not my rerun of the full control runner.
- Current unbounded witness explicitly has `expected_negative_observed=false` and matches the bounded primary after tighter RK. Its `passed=true` means diagnostic execution/accounting passed; it does not prove a reproduced failure. Earlier failures remain retained. The narrative's historical distinction is consistent.
- ACTS preflight warned that the registry setup/lock fingerprints changed and DD4hep/Geant4 sources were unavailable. Re-activated setup in a fresh shell; verified current setup/lock hashes, executable22b30c... and `libActsCore.dylib`f4c040... against committed rebuild/control records. Eigen5.0.1/Boost1.90.0 resolved. No ACTS installation or shared-source changes were made. I did not rerun the recorded385ACTS unit tests,3integration suites or Python rebuild checks.
- **Independent native geometry inspection:** reconstructed all source prisms from exact JSON; checked every native face corner set and ID. Max corner-set residual3.6621e−15m;9360unique IDs and3120large faces.
- **Independent field-provider queries:**1037new points, seed900531, against exact pinned Python reader.964valid,71masked,2outside; statuses identical, invalid fields remain NaN; max field residual9.1594e−15T.
- **Independent native cylinder/helix probes:** tangent inward-return seed recovered at path0.01351456m with3native negative corrections; radial outward seed returned at12.76511m; opposite-charge tangent seed exited world at6.12309m. Returned native points agree with analytic uniform-Bz helices within1.10e−12m. These cover limited cylindrical edge cases, not the entire joint-field phase space.
- Executed counter fixtures for nominal3stations, same-station overcount prevention, tangent finding and failure lower/upper bounds. The portable scratch script initially had its own CSV-column typo; corrected and rerun successfully. This was not a repository defect.

Portable new evidence: `/private/tmp/pr90-acts-R1-spotchecks.py` and paired `.json` (runtime requires the preflight-qualified installed executable/environment). The script reads immutable Git objects and writes only below its `--work`/`--output` destinations.

## Independence and next review

I authored P1's benchmark/counter proposals and entrance-domain check, and some earlier DES039 source/control dossiers. I did **not** author this C++/Python ACTS implementation or its native control runner. P1 overlap is disclosed; those recommendations are not their own independent implementation evidence. The new spotcheck script is my own control and is not independently reviewed.

R2 should review the final immutable source/artifact revision, verify both fixes, acquisition/postprocessing identities, final failure-aware denominators and plotted claims. Current review does not assess preliminary production fractions or certify installed-material transport, global portal navigation, reconstruction performance or human design acceptance.
