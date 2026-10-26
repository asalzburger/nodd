# SESSION-2026-10-26-gen3-material-mapping

## Scope and evidence

New Tracker PR authorized by the user on 2026-10-26: r-z scatter of the 100k geantino material recording, native Gen3 portal overlay, orientation-aware mapping surface proposal and flags for material with no nearby carrier. Draft analysis only; detector geometry and production mapping remain unchanged. Clean start f0775a2dd3c30f405880a9e7323e4d230c3c4155 on codex/tracker-gen3-material-mapping. Storage input is ../storage/nodd-tracker.root. Prior PR99 is merged.

## Selected conversation

User requested a new Tracker PR for the first Gen3 material-mapping step. For inward-facing pixels with most material behind the sensitive sensor, choose the closest surface afterwards; otherwise choose the closest before. User also asked to flag material concentrations without nearby surfaces. Earlier requests to retain discussions and observed token usage remain applicable.

## Decisions and outcomes

Flight order is defined along the recorded geantino direction. Native DD4hep frames and material positions will determine sensor orientation and behind-sensor material. Configurable proximity criteria are analysis choices, not detector acceptance. Recording positions are pre-step; use pos + length*direction/2. No raw private client archives are retained.

## Specialist assignments

GEN3MAP-SoftEng-01: explicit SoftEng fallback; full contract, pinned inputs, mode, ownership, completion retained in SoftEng-01.assignment.json. Implement native finite portal/volume/sensor export, independent of material analysis. Coordinator retains integration responsibility. Read-only PhysVal assessment follows a fixed result revision.

## Runtime and checks

acts-spack preflight warns changed setup/lock fingerprints and unstaged DD4hep/G4 full sources. Runtime must be directly verified; ACTS source and installed toolkit headers are available. No shared dependency changes authorized or performed.

## Token accounting

Active parent counters are unavailable until completion; unknown is not zero. Completed child counters will be recovered and attributed without duplication.

## Follow-up

Complete native export, full-scan material survey, proposal/flags and figures; independent technical review; new Tracker PR with interaction and usage synchronization.

## Implemented result and validation

Native export includes121 actual portals (27cylinders,94discs),117 volumes,
45646 sensors,244 link subsurfaces,469 owners. Source/binary/runtime hashes in
geometry-summary.json distinguish the separate adapter build from this source.
DD4hep1.38,Geant4 11.4.3,ROOT6.40.04 directly verified. The env/run.sh → zsh
wrapper lost DYLD paths via macOS shell launch; direct same-process activation
succeeded. An initial set-e before setup stopped on sandbox ps detection;
activation before set-e restored the verified runtime. Shared packages unchanged.

Optional step labels preserve all54 prior profile means/variances exactly.
A first path-prefix depth retained one unnecessary descendant; corrected and
reran full classification. Final100000 tracks/17137021 steps match recorded
budgets;0 missing/density mismatches. Native geometry export had one corrected
provenance-module typo before its final successful native rerun. Six rounding
rescues include two nanometre active/guard ambiguities kept conservatively passive.

Survey checks exact zero vertices,straight-ray residual0.000171mm,full aligned
step coverage,finite bounds and per-track X0/lambdaI closure. Pixel local+w is
support-facing by factory/PD-C02 convention;do not infer physical front solely
from local normal. For matched same-ray/same-layer sensor crossings,inward
barrels have82.9–84.5% downstream passiveX0 and inward endcaps90.6–91.3%.
Otherwise before. No same-layer sensitive crossing exists for968999 pixel
passive steps (76.21% of pixel passiveX0):provisional before,face unresolved.

Threshold10mm is a configurable spatial proximity diagnostic.962351 steps,
62.58% passiveX0 are remote from every portal;5/20mm gives78.27/46.79%.
Selected directional carriers are too distant for74.41% passiveX0.33 connected
clusters and2745 exact native regions retained;heavy service routes need new
segmented carriers.118 candidate portals,101 with nearby assigned material.
Native sensors/pipe material retained separately to prevent double counting.
No map/geometry/acceptance changes. Material-order/binning/held-out replay and
tracking performance remain NOT RUN. Report and figures explain those limits.

14 portable controls passed. Full classifier and profile replay passed;all54
prior profiles equal. Four scientific figures exported to PNG/PDF/SVG;visual
inspection of overview and remote-material figure passed. Sourcehash,full-data
occupancy and deterministic scatter coverage verified. Project/session checks
passed after correcting the task's existing workstream role label.

## Observed accounting correction

GEN3MAP-SoftEng-01 closed turn01a177b3-f282-7fd2-8f2b-68631969c003:
2934828 input +17608 output =2952436 total tokens,37 request increases.
Cached2864768 and reasoning3150 are subsets. Canonical import dry-run,import
and identical replay passed. Parent is active;its counters remain unknown.
No prior PR99 turns reallocated. Review usage will be added only once closed.

GEN3MAP-PhysVal-01 recorded before dispatch:read-only assessment of full input revision a99b63cba68f8c66723df6ed5c55935e6675971a,primary code/data and bounded claims;complete input/ownership/deliverable contract in PhysVal-01.assignment.json. Coordinator separately adds portable table export from retained JSON.

## Independent review and PR

GEN3MAP-PhysVal-01 completed read-only at a99b63cba68f8c66723df6ed5c55935e6675971a.
No blocking defects for first-step plots/proposal. Independently streamed every
track using closed-form finite-cylinder/annulus distances;exact 5/10/20mm
counts and passiveX0 fractions reproduced. Replayed first5000 raw midpoint/
label/scatter flags,all budget partitions and hashes,14 controls from pinned
source and three visual figures. Verified recorder pre-step source and support
factory convention. Two medium production followups (unmatched pixel faces and
sensitive-plane ordering) and low unknown recording identity remain disclosed;
not blockers for this bounded survey and not evidence of a validated map.
Full completed report retained in PhysVal-01-result.md.

Added portable CSV export after reviewed commit;exact output comparison passed.
GitHub plugin create-PR call returned403 integration permission;authenticated
gh fallback created https://github.com/asalzburger/nodd/pull/100 and app attachment
succeeded. Initial sandbox git push and public ledger capture could not resolve/
reach GitHub;authorized escalated retries succeeded. Initial hosted unrooted
job passed;token-site initially lacked the newly assigned PR100 record. Final
packaging adds public/visible interaction records and resynchronizes the ledger.

## Completed-turn usage and conversation coverage

Two completed specialist turns:4441414 input +28311 output =4469725 total,
54 requests. Cached4197632 input and6247 reasoning output are subsets. Models
and client version unknown. Each exact turn imported once after dry-run;
identical replay adds0. Usage-only evidence is retained in
logs/usage/USAGE-2026-10-26-gen3-material-mapping.json. Active parent counters
remain unavailable until the current turn closes;this is partial PR coverage,
not a complete PR total. No prior task's counters have been reallocated.
Completed child visible messages and verified parent identity are retained;
active parent discussion is curated separately without finalized counters.
Reasoning,command arguments/results and private client archives are excluded.

## Remaining work

Human review of Tracker PR100 and the proposed extra carrier families. No
production map,extra native geometry,binning or reconstruction changes requested
in this first step. Current active turn counters can be finalized after closure;
scientific future work remains in project/tracking.json and the report.
