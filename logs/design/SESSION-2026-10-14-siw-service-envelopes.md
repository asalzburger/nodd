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
