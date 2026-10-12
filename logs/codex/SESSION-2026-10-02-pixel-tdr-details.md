# SESSION-2026-10-02-pixel-tdr-details — Expanded sensor and service routing

## Scope and selected request

User (paraphrase): add more sensor-design detail to the TDR and describe and show
cable/cooling routing; additional pages are permitted. The selected preliminary
PR36/37 configuration and exclusion of alternative-study history remain in force.
The existing PubDoc agent continues the manuscript and illustration work; the
coordinator handles source retrieval, independent review, parent records and the
previously authorized Overleaf push. No detector implementation changes are made.

Parent evidence revision: `db74bec126646fe225a4ec6c0f6cc57c75eb3140` on
`documentation/pixel-detector-section`. Starting TDR revision:
`5bded5b9f6bae8155b11f759ca0b22410cf2d136`. Existing documentation and logging
changes are preserved. The prior Overleaf attempt failed twice with HTTP 503;
its final remote read confirms `7783ea3e3235c0fe9da641db3d303a6f211b3073`.
The prior attempt is closed in its own record; no duplicate usage is imported.

## Evidence and editorial decisions

Fetched the exact historical DES001 commit
`214747a3c83c140caa6c4ae9c3fb6486ac5cb825` from the public repository. The earlier
missing-path diagnostic was a missing local Git object; retrieving it resolves
that limitation. The three original module documents match every SHA-256 recorded
in `tools/module_layout/review_models.json`. DES001 PM3-C01 supplies the preliminary
planar n-in-p choice; its glossary fixes RD53i to ITkPix v2/RD53C-ATLAS. Sensor and
ASIC thickness, backside-flex construction, bump standoff, candidate wire bonds
and local bias/decoupling interfaces are described without inventing a guard-ring
mask, process, operating bias or qualification result.

Read the existing public source SRC-PLANAR-SLIM-2013 at its public CDS PDF:
section 3.1.1, physical PDF page 2 explains the pixel-side junction/guard rings
and high-voltage edge insulation issue. It is historical engineering context,
not an nODD operating-voltage or coating specification. An attempted arXiv HTML
endpoint returned a cache miss; the public CDS PDF was accessible.

Cable and cooling diagrams use the selected reference routing and preserve the
separation between electrical chains and hydraulic circuits. Barrel sources:
DES002 PS-C15–19, DES010 pixel-service dossier and the PR34 routing snapshot
consumed by PR37. Endcap sources: DES014 selected disc and DES015 actual transport
cells. Illustrative path lines do not establish manufactured bends or flex artwork.

Independent arithmetic confirms 1508/1542 barrel modules and 3380/3414 chips at
negative/positive ends respectively, with 164 chains per end. Each end's twelve
sector populations are 6,7,7,7,7,7,6,7,7,7,7,7 staves. The 164 full-length tubes
are independent counterflow circuits; no central U-bend is introduced. Endcap
cooling-ring radii are read from the retained screening geometry, distinct from
sensor module-centre radii.

## Commands and validation

Actual final build, illustration, source-hash, PDF review, dashboard and logging
checks are recorded below and in the paired JSON after execution. No DD4hep,
Geant4 or ACTS run is needed or claimed for this editorial task.

## Changed records and accounting

Affected design references: DES001/002/010/012–015 and ADR007; issue #7,
PR36/37, PUB-PIXEL-001 and TASK-PUB-PIXEL. The public source catalogue remains the
source of external identities; the report snapshot gains exact original design
provenance and more detailed source-derived illustrations. The previous TDR commit
preserves the 14-page edition. The expanded edition supersedes its page-count
statements without changing selected detector geometry or sign-off states.

Exact client-reported token counters are unavailable for both parent and PubDoc.
Usage remains empty; no estimate or overlapping observation is recorded.

## Completed expansion and publication

PubDoc expanded the sensor technology, channel map, guards/seams, hybrid stack,
flex and readout/thermal interfaces; added electrical and hydraulic route detail
for half-staves, twelve-sector handoff, both disc faces, ten local circuits,
collectors, trunk, flange necks and last-disc bypass. Six new drawings replace the
former service overview: fourteen figures are included, with fifteen available
in the source bundle. Dense figures use 150–160 mm widths. The extract is 22 pages;
the full report is 26 pages. No alternate-layout study or test narrative is added.

The row table now reports mean module radii with explicit ±0.5 mm staggering;
it previously displayed the first module's radius as the row radius. This is a
presentation correction, preserving the source x/y placements. Cooling radii
remain the mean row radii plus the specified 16 mm pickup offset.

TDR source commit `0f3958c4eefe9aba7b6fe9e7d3a54c0367916545` preserves this edition.
The previously authorized ordinary Overleaf push succeeded, and a separate
`git ls-remote` verified that exact remote main revision. No force-push or design
approval was performed. Server-side compilation was not observed; both ordinary
local builds and independent packaged-source builds pass cleanly. The parent
review package retains all 38 source/PDF hashes and previous-edition hashes.

Checks actually run: 26 current-source and three historical-blob hashes;
reduced snapshot; 18 generated figure/table hashes and byte-identical regeneration;
22/26-page clean pdfLaTeX builds; full-page/figure review and numeric audit;
38 package hashes and independent clean builds; staging whitespace; 27 dashboard
unit tests; dashboard validation (40 tasks, 17 documents, 15 rounds) and build;
76 paired session-record validation and usage summary. A first package-build
command was run in the parent root and could not locate its wrapper (exit 11);
the corrected package-source builds passed. No detector runtime is claimed.

Historical observed input/output usage is 134,594,309 / 674,111 across 79 recorded
turns in 42 of 76 sessions. These are unchanged historical observations, not the
usage of this task. Thirty-four sessions, including this one and its PubDoc work,
have no exact usage observations. Current usage stays empty, not zero.

Human editorial review remains pending. Sensor fabrication/bias/edge details,
thermal and hydraulic qualification, coupling/assembly detail and rear-service
capacity remain preliminary interfaces; no sign-off state is advanced.

## Token-accounting correction — 2026-10-12

This historical session pair was restored from local branch revision
`7ec9d05dc5ee9aefdf6c0da30549615ebc06a0b0`. The original narrative and checks
remain historical evidence; its publication artifacts are not restored by this audit.

Imported 3 verified closed turns: **11,197,374 input** and
**38,038 output** tokens. The [device audit inventory](../usage/USAGE-2026-10-12-device-audit.json)
retains exact boundaries, request counts, event hashes and task attribution.
Parent and PubDoc observations reconcile independently from zero; the recorded
parent edge and child-turn completion activity establish the assignment.
Earlier missing-counter statements describe the original capture. Cached input
and reasoning output are subsets; execution model/client version and total project
coverage remain unknown. No design approval or scientific validation changes.
