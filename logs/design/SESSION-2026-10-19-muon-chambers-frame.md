# SESSION-2026-10-19-muon-chambers-frame — Modular muon chambers and connected frame

## Scope and evidence

Contemporaneous curated record for DES040, a new separate PR on PR87 commit
`fe372194038ed2af9617c27defffba09ae6d683f`. The parent chat directory is a worktree
container; all task commands use the dedicated nODD checkout below. Exact client
start time and root/child token observations are unavailable. Usage is unknown.

## Selected conversation

User (exact): “Ok, cool - looks like there's new reviwer comments. Follow them up
in a new PR - as they will concern the muon chamber layout more than the toroidal
magentic system.” PR87 comments4313407952 and4313456506 request rectangular barrel
and trapezoidal endcap chambers, realistic full-angle coverage, a connected frame
and feet. The user authorized a separate prototype PR; no design sign-off follows.

## User request and inherited inputs

The new branch `codex/muon-chamber-layout` uses the clean committed PR87 revision
in `/Users/salzburg/Documents/ChatGPT/agentic-detector/nodd-muon-chamber-layout`.
The old toroid worktree has an unrelated dirty DES039 chamber-outlines.json;
it was preserved and not copied. No inherited magnet source, map, energy,
MDT resolution or transport file was amended. Invariance inventory retains hashes.
The new PR is stacked on the still-unmerged PR87 branch.

## Bounded assignments recorded before dispatch

### M1 — MuonTech

```json
{
  "id": "M1",
  "role": "MuonTech",
  "task": "New human-authorized separate muon-layout PROTOTYPE PR from PR87. Reviewcomments4313407952 requests rectangularbarrel and trapezoidalendcap chambers;4313456506 asks realistic4pi coverage plusconnectedcoilframe/feet. Keep all36coilgeometry,currents,cold/warm widths and map immutable. Propose realistic finite modular chamber envelopes rather than cylinders/disks clipped into arbitrary shapes. Three nominalstations R5.2/6.7/8.2 and |z|8/9.5/11m,500mmdepth; allow stagger/segmentation/overlap with physical rationale and bounded parameter alternatives. Need rectangular barrels, trapezoid endcaps ONLY(outlines, no internaldetails). Investigate publicATLASsource actual chamber sizes/segmentation/edgeframes/overlaps as precedent; new parameters mustbeNODDchoices notfakeATLASfacts. Assess how to tilearoundfixedcoils while keeping wholeconvexchambers collisionfree; quantify fullsphere gaps and unavoidablebeamline openings honestly. Do not change targetacceptance silently or promiseperfect4pi. Read-only repository, scratch/private/tmp allowed; no nestedagents/externalmessages.",
  "deliverable": "Return sourced bounded panel-tiling proposal, exact ranges/choices, shape and collision validation strategy, geometry-vsresponse limits; primarysource locators and URLs. Scratch /private/tmp/muon-layout-M1-*.",
  "completion": "Concrete physically motivated panel layout strategy rootcan implement; explain impossibility/remainingholes, no engineeringapproval.",
  "input_revision": "fe372194038ed2af9617c27defffba09ae6d683f",
  "inputs": [
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-039/results.json",
    "docs/validation/DES-039/results.md",
    "tools/toroid_prototype/geometry.py",
    "tools/toroid_prototype/design.json",
    "docs/validation/DES-039/sources.md",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": []
}
```

### A1 — SysArch

```json
{
  "id": "A1",
  "role": "SysArch",
  "task": "New separate muonchamberlayoutPR atfixedPR87 magnets. Propose finite supportframe mechanically connecting/holding all36 warmcoilcases and feet as requested inreview4313456506. Keepcoilgeometry/currents and fieldmapfixed. Need coherent loadpath from12BT+12eachECT to outerframe and floor, clear chamber envelopes, finitecrosssections/material assumptions and explicit attachports. Credible conceptreservingactualspace, not decorativefloatinglines. Prefer nonferromagneticframe assumptions to retainvacuumfield input; separate gravity/geometricconnectivity from unqualifiedmagneticforce/stress/quench engineering. Read primarypublicATLAS support/case/feet precedent and existing pinnedsource dossier; classifynewdimensionchoices with rationale. Define struts/rings/rails/endcapcarrier interfaces, feet count/extent, contact-vs-unintendedoverlap policy, material/mass bookkeeping and collision checks. Fullsphere coveragemustincludeasymmetricfeet/frame shadows (C12cannotblindlyrepeat). Read-onlyrepo/scratch/tmp only, no nestedagents/externalmessages.",
  "deliverable": "Return exactbounded supporttopology/parameterproposal withsource locators, commonload graph and methods for actual volume/clashes/mass and chamberinterface assessment. Scratch /private/tmp/muon-layout-A1-*.",
  "completion": "Usable frame/feet concept connected to allcases andground, explicit numerical/designunknowns and genuine physicalconstraints; no mechanicalcertification.",
  "input_revision": "fe372194038ed2af9617c27defffba09ae6d683f",
  "inputs": [
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-039/results.json",
    "docs/validation/DES-039/results.md",
    "tools/toroid_prototype/geometry.py",
    "tools/toroid_prototype/design.json",
    "docs/validation/DES-039/sources.md",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": []
}
```

### P1 — PhysVal

```json
{
  "id": "P1",
  "role": "PhysVal",
  "task": "Independently derive requirements/observables for newseparate PR rectangularbarrel/trapezoidendcap chambers +frame/feet around fixedPR87 magnets. Reviewer asks4pi realisticcoverage; do not silentlyredefine this as |eta|<=3 or claimperfect4pi. Develop whole-sphere geometric coverage tests atallphi (feetbreaksymmetry), exact/weightedsolidangles and analyticpolaropening bounds; distinguish outerenvelope vs activeedge border, unique station count vs duplicatedpanels inastation, chamber hits vs coil/support pathmaterial and upstreamshadows. Need chamber-collision checks full thickness not just corners/centres, panel-panel designatedoverlap rules (overlap projections okay, not physicalsolids), connected supportgraph/contactgeometry. Assess possible future precision/3mspan interpretations without assuming35umguaranteed. Read-onlyrepo/scratchonly; laterexactrevisionreview afterimplementation. No nestedagents/externalmessages.",
  "deliverable": "Return independent validation criteria/mathematical checks and hiddenfailuremodes atfixedinputrevision; scratch /private/tmp/muon-layout-P1-*.",
  "completion": "Clear measurablewhole-sphere/shape/spacing/support criteria root can use, no invented humanacceptance or performanceclaim.",
  "input_revision": "fe372194038ed2af9617c27defffba09ae6d683f",
  "inputs": [
    "docs/design/DES-039-twelvefold-toroid.md",
    "docs/validation/DES-039/results.json",
    "docs/validation/DES-039/results.md",
    "tools/toroid_prototype/geometry.py",
    "tools/toroid_prototype/design.json",
    "docs/validation/DES-039/sources.md",
    "reference/manifest.yaml"
  ],
  "mode": "read-only",
  "writable_paths": []
}
```

## Implementation contracts after recorded DES040 choices

```json
{
  "role": "SoftEng",
  "input_revision": "fe372194038ed2af9617c27defffba09ae6d683f",
  "inputs": [
    "docs/design/DES-039-twelvefold-toroid.md",
    "tools/toroid_prototype/geometry.py",
    "docs/validation/DES-039/results.json"
  ],
  "mode": "write",
  "id": "S1",
  "writable_paths": [
    "tools/muon_layout/support.py",
    "tools/muon_layout/test_support.py"
  ],
  "task": "Supplemental explicit coordinator working-tree prototype inputs (not baseline snapshots): {\"docs/design/DES-040-muon-chambers-frame.md\":\"bb85d331afcf3e7aa0cf9ac14e023660bbfc24eea5f9b71aea1b37ec643d2cb5\",\"tools/muon_layout/design.json\":\"ecb599bd70fe69a0b0901cd7407187f9dc2edf197d27201c332283786bcbf60d\",\"tools/muon_layout/geometry.py\":\"2915629ae840df3df6355f78abe2e5564ef7a3caa525f55691de8877fe0c21e8\",\"docs/validation/DES-040/support-input.json\":\"832791656d361e8410fa1b7d6f1148d5f41043f55812085b6ebfda2297c57f90\"}. Read these four current files in full before implementing. DES040 choices are already recorded before generation. Preserve all pinned magnetic files. Implement finite support proposal in support-input.json. API build_supports(config)->dict(members:prism list,ports,connections/graph,ground,choices/limits); material_parts(member)->list convex solid-wall prisms for hollow RHS/plates; support_mass(members,samples,seed)->gross stock plus unique per-material union/MC errors; validate_supports(model,magnetic_config)->actual port/case/contact/ground connectivity and unintended coil/cold/pack clashes. Use root geometry.py primitives; request any API change. Respect radial/axial section roll. All36 coil identities,156 warm-skin ports,braced frame/carriers/ten feet must connect. No individual case-wall solids or field edits. Same-material welded intersections are declared unions; Al/SS contacts must not penetrate. Derive/validate graph contacts with actual material walls, not only outer boxes or centres in cavities. Panel collision uses conservative installation envelopes; material shadows use hollow walls. Gross131t stock is an upper bound until union subtraction. Port contacts are declared skin interfaces; analytic separation at touching warm skin, cold/pack clearance separately. No force/stiffness certification. Root owns chambers/coverage/study/docs. No nested agents or external messages.",
  "deliverable": "Owned support module/tests only, exact schema communicated early, actual checks and limits. No other repository edits.",
  "completion": "Finite connected support geometry, grounded all36 cases, actual contact evidence, unique material accounting or explicit uncertainty; meaningful tests pass."
}
```

```json
{
  "role": "SoftEng",
  "input_revision": "fe372194038ed2af9617c27defffba09ae6d683f",
  "inputs": [
    "docs/design/DES-039-twelvefold-toroid.md",
    "tools/toroid_prototype/geometry.py",
    "docs/validation/DES-039/results.json"
  ],
  "mode": "write",
  "id": "S2",
  "writable_paths": [
    "tools/muon_layout/draw.py",
    "docs/validation/DES-040/layout-3d.png",
    "docs/validation/DES-040/xy-sections.png",
    "docs/validation/DES-040/rz-sections.png",
    "docs/validation/DES-040/coverage.png"
  ],
  "task": "Supplemental explicit coordinator working-tree prototype inputs (not baseline snapshots): {\"docs/design/DES-040-muon-chambers-frame.md\":\"bb85d331afcf3e7aa0cf9ac14e023660bbfc24eea5f9b71aea1b37ec643d2cb5\",\"tools/muon_layout/design.json\":\"ecb599bd70fe69a0b0901cd7407187f9dc2edf197d27201c332283786bcbf60d\",\"tools/muon_layout/geometry.py\":\"2915629ae840df3df6355f78abe2e5564ef7a3caa525f55691de8877fe0c21e8\",\"docs/validation/DES-040/support-input.json\":\"832791656d361e8410fa1b7d6f1148d5f41043f55812085b6ebfda2297c57f90\"}. Read these four current files in full before implementing. DES040 choices are already recorded before generation. Preserve all pinned magnetic files. Implement Matplotlib renderer, API draw(geometry,coverage,output). geometry has configuration(newdesign),magnetic_configuration(executedoldresults),panels(prism list),supports(dict with members); coverage has 1Dmu,phi_deg and2D outer_count,active_count,depth_count,support_between/support_upstream/support_any,coil_between/coil_upstream/coil_any,summary. Root may refine names; coordinate early. Prism schema vertices_m4x2,origin_m,basis(columns localx,y,normal),depth_m,station1..3/kindbarrel/endcap; support hollow parts via S1 material_parts(member). Draw finite warm toroid reservations, rectangular/trapezoidal chamber outlines and finite frame/feet. No chamber internals. Actual XY slices atz0,.5,6.3,8,9.5,11m; RZ atphi0,7.5,15,270(bottomfeet), distinguish slices from projections. Legible3D, explicit plotting cutaway if needed, preserve full geometry in data. Full sphere mu\u00b11/allphi coverage; footprint versus complete depth traversal and material tags separate, no C12 extension afterfeet. Optional joint vacuum|B|contours from verified pinned map, no zero invalid stencils. Root supplies generated data later. Installed plot Python pureNumPy/matplotlib, no ACTS setup. No nested agents/external messages.",
  "deliverable": "Owned renderer and final four figures after data ready; source/runtime checks and visual QA of every final figure.",
  "completion": "Finite chamber shapes/frame contacts/feet and full-sphere distinctions are readable and accurate; code parameterized until final root data."
}
```

## Decisions, execution and outcomes

MuonTech M1 prepared bounded whole-module shapes and analytic packing controls.
SysArch A1 proposed finite frame/ports/feet and density assumptions. PhysVal P1
prepared independent full-sphere/finite-volume criteria and crosschecked the
racetrack offset identity against600000 random points. Those planning roles did
not implement the root chamber/coverage algorithms. Bounded SoftEng S1 implemented
only support.py/test_support.py; S2 implemented only draw.py and four PNGs. Root
implemented geometry, module packing, coverage, study, source/report/tracking and
integration. This division is not human engineering approval.

The complete study retains1560 whole modules,484 finite supports,1378 material
wall parts,156 case-skin ports and all36 coil identities grounded through actual
material contacts. Initial120x360/240x720 grids aliased narrow gaps (up to11.2pp),
so numerical sampling was amended in DES040 before the final run:240x720 and
480x1440 maps plus1048576 iid full-sphere rays. Headline three-station fractions
are74.35% outer,63.20% border inset and41.38% complete depth, with sampling errors
only. The maps are explicitly not converged. A paired no-frame repacking control
shows2.787pp active three-station loss. Mass union129.483±.009t is distinct from
131.193t gross stock and unknown engineering/material uncertainty.

No geometry was tuned to conceal the gaps. Complete-depth traversal, plane
availability, material-route tags and actual first-to-last path spans remain
separate. mu_r=1 support proxies preserve the inherited vacuum-map assumption;
installed HCAL B-H, response, chamber mounts/services/deadloads, magnetic forces,
strength/stiffness/anchors/quench qualification and forward technology remain open.

## Commands and validation

Final study exited0 in48.466s. All21 new geometry/packing/support controls and all49
inherited toroid/field controls passed. Source/artifact hash accounting passes.
All four figures were regenerated from final inputs; S2 and root inspected them.
Actual prism sections, hollow material, cutaway labels, off-plane feet and grid
sampling labels were checked. Project validation first rejected the noncanonical
status string“DRAFT / isolated PROTOTYPE”; it was corrected to canonical DRAFT
with an explicit prototype scope line.68tasks/38documents/21reviewrounds and190
session records then validated. Detailed successful commands/results are in the
paired JSON. Failed scratch/tool formatting attempts did not change scientific
inputs and were corrected before generation.

## Changes and revision links

The paired JSON inventories changed files. The first task commit freezes the
scientific source/evidence; a later technical-review/publication record commit
will point to that exact revision without treating it as engineering acceptance.

## Token accounting

No exact root/child turn counters are exposed; usage stays[]. MilestoneM1 summary
observed178024582 input and893575 output tokens across69 previously recorded
turns (35/77sessions with usage observations at this point). Those project totals
are not task usage. Cached/reasoning subsets were not added. Missing usage is
unknown, not zero.

## Follow-up

Review coverage losses and physical chamber/field envelope tradeoffs; qualify
chamber technology, services/mounts/deadloads and energized magnet supports before
production integration. A realistic full-angle study is not perfect4pi coverage.
