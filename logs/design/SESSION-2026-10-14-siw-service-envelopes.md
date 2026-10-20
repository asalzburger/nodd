# SESSION-2026-10-14-siw-service-envelopes - LAYOUT-001 envelope parity

## Scope and selected request

Contemporaneous task starting from clean main e33ae62ce16592c26c581c5311c4dc493d9714b1
in a dedicated worktree, branch codex/layout001-service-envelopes.

User request (verbatim):

> This needs one more adaptation: layout-1 does not yet have the same level of envelope prototyping: service and cooling space for Si-W EM such as the routing through the HCAL is not defined, similar eventual FCAL envelopes are missing.
> Bring them en par with an additional PR, then update the overview document (and PR) you are currently drafting.

The additional prototype PR is independent of open Si-W PR70/71. It will pin
those sources, define service/forward reservations and amend the HCAL outline;
no unreviewed detector production integration or new external package. Existing
PR75 will retain identical common-source Markdown/PR-description/four-page PDF.
All PR70/71/73/74/75 remain open at inspected heads on 2026-10-14; main is e33ae62.

## Decisions and handoffs

Design/evidence stub precedes envelope implementation. Native source parameter
facts, inference and new choices remain separate. The SysArch assignment will
address cross-system interfaces; a separate PhysVal context will assess a frozen
implemented allocation before publication. Root owns implementation, documents,
records and PR75 synchronization. Generic role prompts are explicit assignments,
not native profile loading or human sign-off.

## Commands and checks

Initial upstream metadata and source inspection only; checks and results will be
curated as executed.

## Token accounting

Exact current parent/child completed-turn counters are unavailable. Usage remains
unknown; do not estimate or duplicate previous task observations.

## Prepared SIW-SERVICE-SysArch-input

```json
{
  "id": "SIW-SERVICE-SysArch-input",
  "role": "SysArch",
  "input_revision": "62b8b35765ff55163c504e3d551f4366a536948b",
  "inputs": [
    "docs/design/DES-034-siw-service-envelopes.md",
    "docs/design/inputs/DES-034-sources.json",
    "docs/layouts/LAYOUT-001.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess external service/cooling and prospective forward envelope requirements for LAYOUT-001, to reach the same ALLOCATION level as LAr LAYOUT-002. Read exact pinned DES030/031 inventories and LAr comparison sources. Propose source-based or explicitly chosen station counts, signal/data/power/water cable/pipe packing, bend/access corridors, HCAL route/envelope amendments retaining original HCAL depth and ECAL packages, and FCal empty-reservation topology that does not overlap the existing SiW endcap. Address circular corner radii versus polygon apothems and service endpoints blocked by current cassette materials. Distinguish backbone-space planning from engineered local collectors, and forward reservation from acceptance. Return numerical proposals with derivations/scenarios/risks and exact primary locators; no files, jobs, installs, new source imports, PRs, delegation or approval. Main coordinator implements; do not prescribe a performance target beyond the existing eta4 prototype exploration.",
  "deliverable": "Compact physical-interface and budget input for root; endpoints/owners/clearances, nominal and adverse assumptions, missing engineering evidence.",
  "completion": "Practical external-routing/HCAL/forward options and necessary limits established without claiming physical ports, installed mass or accepted coverage."
}
```

## SysArch handoff and implementation

SIW-SERVICE-SysArch-input examined source 62b8b35765ff55163c504e3d551f4366a536948b
and pinned PR70/71/73/74 sources. Separate generic child /root/siw_services_sysarch
returned service counts, area/heat/flow/power/length estimates, HCAL bounds and
non-overlapping forward options. It resolved the native interface role count:
passive PCBs and powered interface chips have one combined role. Six initial
source SHA bindings matched. No edits/native jobs/new dependencies/sign-off.

Root selected the outer circular backbone, unchanged ECAL and 400 mm rear break.
Root narrowed the proposed 900x220 mm merged junction to 880x220 mm to preserve
20 mm sector-edge clearance as well as radial clearance. Root selected a 25 mm
water bore (SysArch considered 20 mm) and 50 mm forward front clearance. These
are named new choices, not changed source facts or approvals. Retain the station
balance and digital link assumptions, +/-50% lengths, and absent local ports.

Actual controls: eight meaningful negative cases pass, source-bound report and
layout values reproduce, all eleven pinned primary SHA256 values match, updated
RZ SVG reproduces and PNG visually fits. An initial tuple/list serialization
mismatch made report --check fail; retained route points now use JSON lists and
reproduction passes. No geometry was changed to remove a physics failure.

## Prepared SIW-SERVICE-PhysVal-review

```json
{
  "id": "SIW-SERVICE-PhysVal-review",
  "role": "PhysVal",
  "input_revision": "78cfa3fe8ac56e4b48a11870ca2758bdae25ed6c",
  "inputs": [
    "docs/design/DES-034-siw-service-envelopes.md",
    "docs/design/inputs/DES-034-sources.json",
    "tools/siw_services/inputs.json",
    "tools/siw_services/study.py",
    "docs/validation/DES-034/allocations.json",
    "docs/validation/DES-034/results.md",
    "docs/layouts/LAYOUT-001.json"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Assess this exact implemented EMPTY-ENVELOPE proposal for Si-W service/forward parity with LAr. Check primary-count reconciliation, packing/merged junction, circular-vs-polygon clearances, HCAL depth/envelope/volume, single-pipe bend and reserved route scope, heat/flow/power and partial material/length assumptions, FCal non-overlap and acceptance wording. Inputs preserve actual source pointers; inspect pinned primary objects and report numerical or interpretation defects with severity and locators. Run relevant standard-library controls if helpful. No edits/native geometry jobs/installs/delegation or approval. Prior LAr work is disclosed, but this Si-W proposal is root-authored following a separate SysArch input. Return exact revision, actual checks and remaining limitations. Do not prescribe a conclusion.",
  "deliverable": "Read-only scientific claim and allocation review to root, curated in paired session record before publication.",
  "completion": "Material scientific/numerical/scope findings and missing evidence identified for the frozen source set, without treating allocation arithmetic as native geometry or engineering acceptance."
}
```

## Publication and CI diagnostics

Additional PR76 created on main at78cfa3fe, attached to the parent task. Its
initial project run38518977245 failed report replay on Linux after all eight
controls passed; token preview passed. The updated drawing producer had remained
unstaged although generated figures were committed, so it was retained in normal
commit66bb10d. Replay diagnostics were added without relaxing comparison to
identify actual differing fields. Local report and SVG replay pass; Linux result
is still pending at this checkpoint. Native/engineering checks are not claimed.

Project-record/documentation tests passed:28 tests in106.011s. Prototype project
validation passed65 tasks/36 documents/21 review rounds; paired journal validation
passed180 records before companion overview merge.

## PhysVal findings and correction

SIW-SERVICE-PhysVal-review, /root/lar_fit_physval, reviewed exact78cfa3fe read-only.
P2: endcap inventory used12m one-way while electrical loss used40m round-trip.
Root now derives each loop as twice its station length:40m barrel /24m endcap.
Cu remains0.917504t; endcap drop/loss become0.382V/17.7W and aggregate external
loss7.190kW. Added a regression cross-check between feed copper and voltage loops.
P3: the initial suite had seven negative tests plus one nominal, not eight
negative tests. Added a missing axial FCal/ECAL intrusion control; the final suite
has eight negative and two nominal tests, reported exactly. Existing bounds,
counts/area/flow/HCAL/FCal arithmetic otherwise agreed; reviewer independently
checked continuous single-elbow bounds and all11 source hashes. No native jobs,
edits or sign-off; earlier LAr contribution remains disclosed.

Diagnostic CI38519327533 at66bb10d identified only last-bit Linux/macOS libm
variation: e.g. previous HCAL barrel224.78264632630692 vs224.78264632630695m3.
Report serialization now declares nine decimal places per labelled unit;
physical constraints remain unrounded and exact source/producer hashes and
serialized replay remain strict. This changes numerical presentation, not
physical tolerances, capacities or proposal geometry.

## Prepared SIW-SERVICE-PhysVal-closure

```json
{
  "id": "SIW-SERVICE-PhysVal-closure",
  "role": "PhysVal",
  "input_revision": "0a26796518d690bf26934d2864d63ecad7582675",
  "inputs": [
    "tools/siw_services/study.py",
    "tools/siw_services/inputs.json",
    "tools/siw_services/test_study.py",
    "docs/validation/DES-034/allocations.json",
    "docs/design/DES-034-siw-service-envelopes.md"
  ],
  "mode": "read-only",
  "writable_paths": [],
  "task": "Narrow closure of your P2/P3 at78cfa3fe. Check that endcap feed Cu inventory and electrical drop now share12m one-way/24m loop while barrel uses20m/40m. Assess accurate ten-test/eight-negative wording, added axial FCal intrusion control and numeric report serialization9decimal places (physical constraints remain unrounded and exact hashes/replay retained). No full repeated source audit, edits, native jobs, installs or delegation. Return exact revision, correction findings and actual checks; no approval.",
  "deliverable": "Bounded P2/P3 and numerical-report closure to root for session record.",
  "completion": "Consistency and negative-control claims resolved or remaining concrete issue reported at this frozen revision."
}
```

## Closeout

SIW-SERVICE-PhysVal-closure reviewed0a26796518d690bf26934d2864d63ecad7582675.
P2/P3 addressed with no remaining narrow-scope finding. The feed calculation
now consistently gives0.381899V/17.665540W per endcap station and7.189820kW
external total, matching0.917504t Cu. Ten tests pass (eight negative, two nominal).
Reviewer confirmed a1e-10mm clearance violation still fails before report rounding.
No edits/native jobs/sign-off. Role assessments remain narrative, not fabricated
command exits. Linux CI38519491101's new Si-W allocation/replay/drawing step passed
at0a267965; broader inherited checks were still running at collection.

PR76 is the additional main-based prototype; PR75 consumes it as a dependency so
its review diff remains documentation. All changes stay public/reviewable, with
no new externals and no merge performed by the agent. Current exact usage stays
unavailable; the token-site build must retain observed sums without estimation.
