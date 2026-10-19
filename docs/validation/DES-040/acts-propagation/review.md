# R2 — Final PhysVal artifact assessment

**Exact target:** `b33403ac7476fd8392542d28f984a426660527b3`.
**Outcome:** no unresolved material findings within this bounded review. The results support the report's negative coverage conclusion and stated vacuum/local-momentum limits. This is an AI technical assessment under the explicit fallback PhysVal mandate, not native-profile verification, human expert review or design acceptance.

## R1 findings resolved

- **R1-F1:** `analyze.py:175–181` now constructs `dict(geocheck,...)`, avoiding the duplicate-keyword error. The final summary exists and its results independently reproduce.
- **R1-F2:** `analyze.py:68–75` excludes tangent contacts from crossing sets and pairing while retaining raw contacts. All11 exact committed counter/entrance tests passed, including the six-contact regression expecting0 crossings/0 pairs. Independent production analysis found0 tangents, confirming unchanged fractions.

## Checks actually performed

The portable reviewer-authored script reads immutable Git objects, derives prism halfspaces directly from frozen polygons/transforms, and implements a separate ordered-event counter. It does not import implementation geometry/counter functions to derive production results. The committed implementation is used separately for its11 unit tests.

- Verified all32 artifact-manifest entries, fixed geometry/map hashes, acquisition-stage hashes at `77c652e8b55a33d6fcfa897c2b250a81df9c52f1`, postprocessing hashes at `ff5ad3e467ae8f80c755c53289a78256c1478d50`, and both retained control records. All52 inherited magnetic-study files are unchanged. Current executable22b30c... and ActsCore libraryf4c040... fingerprints match committed evidence.
- Verified raw acquisition CSV hashes and exact equality of all464,397event rows and148,960track rows with committed NPZ data, including native IDs, owners, coordinates, directions, paths, statuses and diagnostics. Raw CSV comparison is optional for portable replay; NPZs remain committed evidence.
- Independently checked every native hit against its source face/prism, large/side classification, station and30 mm-border flag. All agree; maximum plane residual/prism excess is9.97332 nm. uint64 identities retain precision.8475 faces are observed, distinct from9360 constructed faces.
- Independently recomputed all10 counter arrays for every track: **zero mismatching rows**. There are22 reentries,0 duplicates/orphans/tangents, and nondecreasing event paths. One open chamber visit is on an already-incomplete track.
- Recomputed all80 case/sample/metric availability bounds and every rounded cell of the10-row report table. Verified10,800 display rays plus4096 sphere rays per p/q case, shared directions, all map cells/weights and entrance coordinates. The finite eta display excludes0.494525%of4π;15 sphere directions per shared case lie outside it. It is not used as the4π denominator.
- Confirmed71,126 completed and77,834 field-masked tracks across both samples, with no additional navigation-unqualified tracks. All failures remain in denominators.58 incomplete events already prove six faces; these remain passes without being added twice to upper bounds.
- Visually inspected all four frozen PNGs and read their plotting source. Native-hit plots include incomplete tracks and both samples; map slashes also mark incomplete passes. The momentum plot uses only the sphere sample. Scope, finite sampling and unfinished-event bounds are visible. Plotted hit totals91,733 at2.65 GeV,93,806 at100 GeV and93,920 at1 TeV match the arrays; all figure/input/source hashes verify.

No repository/shared-dependency files changed. R2 did not repeat the ACTS rebuild, full native acquisition or complete control runner. R1's1037 independent field queries and three native cylinder/helix probes remain applicable to the unchanged native source/executable/library. The final unbounded witness correctly records `expected_negative_observed=false`; historical failed controls remain distinct.

## Scientific interpretation

Across both charges at local 2.65–1000 GeV, full-sphere proven ≥6 outer-face fractions are **39.038–43.970%**, with possible upper fractions **77.246–79.810%**. Three border-inset paired stations have proven fractions **22.119–26.538%**. Even granting every unfinished track success leaves at least about 20%without six proxies in this finite study. The fixed layout therefore does not support consistent full-sphere coverage; required eta acceptance or a revised layout remains a separate design decision.

All unfinished cases are strict field-availability failures, not observed scattering, absorption or reconstruction failures. Their wide unresolved bounds dominate the smaller sampling errors. The native method is a supporting-surface root/finite-owner audit, not qualified chamber portal switching. Finite controls do not prove completeness for every possible joint-field graze or reentry.

The benchmark starts at a closed muon-system entrance with radial seeds and **local total momentum**. MUON001's central 5 GeV IP estimate motivates only the2.65 GeV local stress point. These results establish no universal IP/pT threshold, upstream material transport, installed HCAL-steel field, chamber response/precision, segment fit, momentum resolution or reconstructed efficiency.

## Independence and remaining scope

I authored P1 planning/entrance probes, some earlier DES039 dossiers, R1 probes and this artifact check; I did **not** author the reviewed ACTS implementation or native control runner. Planning overlap is disclosed and is not treated as independent implementation evidence. The new check itself has not been independently reviewed.

Masked field/material transport, required acceptance and future geometry changes remain open work. Human approval remains absent. The project record describes bounded prototype delivery rather than accepted detector performance.

Deliverables in `/private/tmp`: `pr90-acts-R2-final.md/.json`, portable `pr90-acts-R2-artifact-check.py` and paired `.json`. The script takes explicit root/revision/work/output paths and optional raw-CSV input; it never changes checkout files or invokes ACTS.
