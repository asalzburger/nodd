# SESSION-2026-11-18-lar-gap400-prototype — Reduced-gap study

## Request and scope

User exact request: “I see, stack those PRs you have right now, and then add
another one with a reduced gap on top of it”. Context identifies400mm warm
barrel/endcap gap. Keep the selected1m-gap restored LAr baseline as its parent;
new isolated PROTOTYPE, no hidden baseline replacement or engineering sign-off.
Starting source7a9da4490f3bbe89f9d55fbfcadc795a3889139b, clean dedicated worktree.
No unrelated edits.

## LAR-GAP400-CaloTech assignment

Exact7a9da4490f3bbe89f9d55fbfcadc795a3889139b. Read-only, explicit full-profile
fallback prepared through workflow.py. Inputs restored spec/builder, service
budget/config and physical barrel/endcap services, earlier side-neck gap note
and baseline selection. Question: minimal400mm-gap prototype preserving
sampling/material/readout/vessel budgets and >=4OD bends, with concrete
side-egress reservation and unqualified ports clearly separated. Return
quantitative requirements, risks and checks. No writes/native execution/private
state/publication/delegation. Coordinator owns implementation and closeout.

## Accounting

Current parent spans baseline stacking and this follow-up and remains active;
no estimate or split. Separately completed specialist turns may be retained in
this sole task account. Historical counters stay with their original owners.

### CaloTech result and bounded lane amendment

LAR-GAP400-CaloTech at7a9da449: conditional gap study defensible, no connected
physical port route or engineering qualification. Corrected restored S-bend
bounds834.082/854.082mm; densecontrol numbers896.8/916.8 were inherited in the
initial assignment and corrected to the user. Full endcap translation600mm
preserves650mm internal depth. Keep HCAL6260/6760 context fixed, distinguish
1100mm rear free interval from500mm radial exit window. Existing150mm lane plus
40mm faces exceeds181mm annulus; packed area alone is insufficient. Source
also flags populated board/ring neck band, closed rear support, and moved-endcap
conflict with prospective R301–450/|z|4500–4850 collar reservation.

LAR-GAP400-CaloTech-lanes amendment: same exact7a9da449 input set and full
read-only mandate; assess proposed bus3039.5mm,140mm radial annular-sector lanes
(700/1100mm tangential area budgets) with20mm faces, retaining fixed HCAL and
1000mm pre-end band. Evaluate annular area/angular margins without substituting
a flat rectangle whose corners cross HCAL. No claims of routed supports/ports,
no writes/native execution/private-state access/publication/delegation. Return
arithmetic/limits; coordinator retains conditional-route labels.

### Implementation and actual controls

Source design49b4326dbb7689b50d80f347c29298a44726b001 precedes implementation
ccc119813a918a694ed04d7a3fc087ce580677b2. Explicit400mm specification adds guarded
pre-end policy,140mm annular lanes/bus3039.5, distinct utility sectors0/8 and
fixed6260/6760HCAL context. Original front-S validator still rejects400mm.
External routes are empty/unconstructed; walls/board/ring connections remain
open and prospective collar conflict is retained. Baseline manifest unchanged.

All46calorimeter tests passed. Barrel XML/material byte-identical; endcap local
pieces/material/mass/rotations unchanged and complete replicas translate600mm
toward IP. Initial diagnostic used end IDs1/2 as signs; corrected to world-Z
sign without changing geometry. Native signed-endcap audit9856raw IDs/1203200
virtual cells/zero10nm overlaps; native ECAL union zero10nm overlaps/405rays.
No tracker/field/HCAL/FCAL or new external service material is constructed.

Matched24event controls with1and12workers passed transport/readback. All19568
cell IDs, energies and positions are exactly equal; all12workers audited.
Seed133812341,5mm cap,.7mm production cuts,B=0. Full events/JSONL/ROOT geometry
and runtime logs stay ignored. No new10k resolution or calibration-transfer
claim. Current named input/SVG/PNG shows actual ECAL envelopes and conditional
reservations; visual QA passed, baseline SVG remains byte-identical.

### Exact-candidate final assignments

LAR-GAP400-SysArch-final and LAR-GAP400-PhysVal-final target
9ec2558a8cf30d2e7e7ad5b2d07520ccd0138b95. Prepared explicit full-profile
fallback; read-only inputs: prototype spec/builder/service policy, design note,
geometry/native/transport receipts and report, named input/PNG. SysArch assesses
physical envelopes/reservations/guards/forward conflict and unchanged baseline;
PhysVal assesses source identity, transforms/counts, finite native/24-event
controls and interpretation. No writes/native activation/private-state access,
publication or delegation. Deliver exact revision/material findings/actual checks/
limits, stating blockers to publishing a conditional prototype draft.

### Named-input provenance correction during review

SysArch identified inherited1m tracker+ECAL compact/material/exporter fields in
otherwise current ECAL-only prototype metadata. Moved those and the tracker
visual-component hash into an explicitly named baseline_context, preserving
current prototype ECAL combined/component hashes and tracker/magnet context
sources. Regenerated the named input; physical SVG/PNG and native/transport
artifacts are unchanged. No geometry or statistical rerun is needed for this
metadata-only correction. Final reviewers receive the exact follow-up revision.

### Final independent assessments and publication

Published draftPR151 above150 and attached it to this task. SysArch and PhysVal
reviewed9ec2558a8cf30d2e7e7ad5b2d07520ccd0138b95 plus metadata correction
fcbc6a912038feb2cfe32a2b206bd582b6983d7b: no material blocker to publishing the
conditional prototype. SysArch verified all4928sampling replicas/36global
passive anchors,38210local passive children, unchanged materials/masses/counts,
route/HCAL bounds, seven negative cases and byte-identical prototype/baseline
SVGs. PhysVal verified27source hashes, translations, native records/405ray
grid,24event receipt/input/worker bindings and exact19568hit comparison; four
portable guards passed. Both inspected PNG and retained the physical-port/
board/ring/bundle/collar and performance limitations. Neither reran native or
transport, wrote files or granted engineering acceptance.

Four closed CaloTech/SysArch/PhysVal turns are recorded once in this task:
10,804,203input +33,257output =10,837,460observed tokens. Cached/reasoning
subsets are not added. Inventories:USAGE-2026-11-18-lar-gap400-calotech.json and
USAGE-2026-11-18-lar-gap400-final-reviews.json. Selected visible messages/
operation metadata retain exact thread/turn/parent identities without raw tool
arguments/results, hidden reasoning, images or private paths. Existing studies'
owners remain unchanged; active shared parent is excluded.

A fresh restored1m export under the extended code also reproduced all four
validated component XML/material files byte-for-byte. Thus default baseline
physical artifacts remain unchanged. Raw simulation/native files remain local.
Final project/inventory/session/interaction/token checks and preview are recorded
before final push. PRs remain drafts; no main merge/ready action was performed.
