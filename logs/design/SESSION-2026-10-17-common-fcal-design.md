# SESSION-2026-10-17-common-fcal-design — Common forward calorimeter design

## Request and scope

User: “Ok design such a forward calorimeter and fit it into the two layouts.”

Isolated DRAFT / PROTOTYPE design and physical integration into both candidate layouts; no production integration or human sign-off. Starting revision 33a607b70214532cd265623241b0c250ca0da361. Clean dedicated worktree codex/common-fcal-design.

## Assignments recorded before dispatch

- FCAL-CaloTech-01 / CaloTech / input 33a607b70214532cd265623241b0c250ca0da361 / write only docs/design/inputs/DES-039-fcal-technology.md. Contract and full role prompt are retained under this session directory.
- FCAL-SysArch-01 / SysArch / input 33a607b70214532cd265623241b0c250ca0da361 / write only docs/design/inputs/DES-039-fcal-layout-interfaces.md. Contract and full role prompt are retained under this session directory.

Main agent coordinates, implements parameterized geometric/material/service checks, integration drawings, records and final design. Separate PhysVal assessment follows a fixed implementation revision.

## Design and delivered evidence

The common body is1.8m long at R50–290mm, with1.2m sampling. LAYOUT-001 places it at absolute z4.5332–6.3332m; LAYOUT-002 at4.850–6.650m. The latter also includes the440mm EM collar at4.400–4.840m, a collector before the cryostat and an explicit R298mm service neck. Current pipe outer radius27.8mm was independently verified; its described length ends at4m. The narrowed bore and service interfaces remain unsigned amendments.

Exact lattice inventories are24,324fibres/body/end and22,812/collar/end. Each component/end has96tower signals and1536physical SiPM pixels. Long and short populations give overlapping shower-depth weightings. Counts, exclusive material volumes, reference nuclear/radiation lengths, partial masses, cold/readout footprint, bend and power bounds are retained in DES039 and the machine-readable report. No optical efficiency, shower containment or high-luminosity performance was inferred.

CaloTech supplied the sourced technology/readout input, SysArch the pinned two-layout physical interfaces and collar amendment. SoftEng first reverified runtime after changed preflight fingerprints, then constructed and ran ROOT geometry. PhysVal separately reviewed exact science revision3c5eded29c1186e7dbd213ac5aab913376babc05: no blocking finding for scoped prototype fit, two P3 dossier issues corrected. Full role prompts/contracts and curated findings remain in the session directory and validation report. Native profile loading is not claimed.

## Actual checks and corrections

Ten FCAL adverse/conservation controls pass. Deterministic retained evidence matches under Python3.14.6 and3.12.14. ROOT checks both signs in both layouts, with zero overlaps at1e-5mm;72IP rays plus18axial controls agree within8.57e-11mm. The separate reviewer solved38finite-cylinder rays independently and checked sources, masses and heat/flow. Source and context hashes match executed scientific files.

Native validation is ROOT/TGeo-only with envelope guards. Omitted loom collisions, curved collector/manifold connections, detailed electronics/gas/cables, downstream machine pipe/shielding, full neighbours, DD4hep/readout and Geant4/optical/shower tests remain explicit. Mechanical assembly tolerances, radiation/EOL, beam heat and cooling/load engineering remain open.

Retained corrections: an initial PyROOT ownership teardown failed despite completed geometry checks; ownership was fixed and clean zero-exit runs retained. The project task initially used the wrong workstream and the token builder rejected an output outside _site; both were corrected and checks rerun. A first image-open attempt occurred while the font cache was still being built; completed PNGs were then inspected. Polygon drawing order and narrow package labels were corrected without changing geometry. Early broad reads used some absent helper paths; exact existing files were subsequently read. Initial GitHub network access failed in the sandbox; approved network commands succeeded.

The project validator, journal validator, specialist-profile validator and token-site build pass. A project-record regression suite was also started; its final result is recorded in the paired JSON. No detector production files or shared installations were changed. No human sign-off was entered.

## Token accounting

Exact client per-turn counters unavailable; usage remains empty, including child turns unless exact counters become available.

## Additional assignment before dispatch

FCAL-SoftEng-01 / SoftEng / 33a607b70214532cd265623241b0c250ca0da361 / read-only; establish native runtime capability, no shared-dependency edits. Full contract and role prompt retained.

## Bounded assignment continuation

CaloTech and SysArch retained their single owned files and assessed the additional 02 EM collar and explicit collector/service neck under their original assignments. The amendment was made to close a quantified EM transition gap, without changing ECAL/tracker/magnet source geometry.

## Native construction assignment before dispatch

FCAL-SoftEng-02 / SoftEng / 0964b60a3d19b13b91abc48e30bd18d66feb66d2 / write tools/forward_calorimeter/native.py and docs/validation/DES-039/native.json only; ignored exports allowed. Explicit ROOT-native geometry scope, no DD4hep or shower acceptance claim.

## Independent assessment before dispatch

FCAL-PhysVal-01 / PhysVal / 3c5eded29c1186e7dbd213ac5aab913376babc05 / read-only; fixed-revision scientific/physical claim assessment. Contract and full role prompt retained. Current project task/stream metadata mismatch is recorded for parent correction; not waived.

## Separate review and editorial reconciliation

The fixed-revision PhysVal report is retained at docs/validation/DES-039/physval.md. Stale support/service radial wording was aligned with R278mm sampling-shell boundary and the proper negative-side Rx(180degree) transform was stated explicitly. The scientific geometry/input/native source bytes reviewed by PhysVal remain unchanged.

## User-visible outcome

DES039, ADR010, source catalogue, component/interface inputs, two integrated candidate views, numerical evidence, native checks, tests, CI step and scientific task tracking are delivered on codex/common-fcal-design. A draft pull request is prepared for review; production integration and human approval remain separate.

The 28 project-record regression tests passed in109.108seconds. CI then exposed a journal schema mistake: the separate AI assessment was entered as a PASS command check with no observed process exit. It was removed from command checks and retained as an assessment in physval.md. Scientific source hashes did not change.

## Review delivery and final accounting

Draft [PR88](https://github.com/asalzburger/nodd/pull/88) was created and attached to the chat. Its initial head12613538b7cf70bed0423e89df8592d362db8ada is retained as the observed PR snapshot; this record-only closeout follows. All scientific lifecycle states remain DRAFT.

The journal validator passes184records after the metadata correction; token-site build succeeds. The summary contains118sessions with usage and66without; this session and its separate child turns have no exact observations. Its input/output sums are unknown, not zero. Hosted CI was started for the draft; its initial token-site failure was the corrected journal schema issue. No scientific source bytes changed in that repair.
