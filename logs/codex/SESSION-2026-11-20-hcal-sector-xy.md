# HCAL barrel-sector x–y view

## Request and outcome

User, exact: “Can you give me an x-y view of the HCAL barrel sector ?”

Created a true z=0 transverse section of the implemented DES045 sector0 centred on+x, with a full60-layer view and equal-scale front-five-layer detail. It uses actual exported trapezoids, carrier placements and original common-unit box/tube/CSG shapes. Radial/tangential packing, axial layer shifts, board/core gaps and all intersecting passive parts are retained. One axial row per layer intersects this cut; it contains241carriers/2892individual core sections. All60steel plates and3130/5720mm face apothems agree with source. PNG/PDF were rendered and visually inspected; label collisions were corrected. No geometry, materials, simulation data or scientific parameters were changed.

## Source and workflow

Dedicated codex/hcal-barrel-sector-xy worktree at a916bae18d5460a7c42dcfa0c0faccf33ac62798, preserving the prior155worktree. Read repository instructions, PROJECT, DES045, common module/export conventions and nODD coordination/evidence procedures. This small dependent illustration stayed with the coordinator; no separate specialist or native runtime activation was needed. Existing Matplotlib/analysis Python was reused without dependency changes. Source and render hashes are in barrel-xy/provenance.json; analytic curves are polygonized only for display. The image is a cut, not a projection of47axial rows.

## Actual validation

Generator export-graph assertions pass for all60absorber layers, each selected carrier count and identity-only sector-child frames. Independent summary assertions confirm241carriers,2892core sections and2590mm depth. Visual inspection confirmed complete sector, true scales, visible physical gaps and readable annotations. No new native geometry/transport result is claimed. Existing detector/hit evidence remains unchanged. Reproduction recipe and limits are in docs/validation/hcal50/barrel-xy/README.md.

## Publication and accounting

A separate draft PR targets codex/hcal-restored-pion50, following the standing human instruction in AGENTS.md. ParentPR155 is related source work, not duplicated token ownership. Exact client token counters are unavailable; usage stays empty, not zero. Final validator results and draft URL are recorded below when observed. No human sign-off, ready-for-review action or merge is granted.

Draft delivery: [PR156](https://github.com/asalzburger/nodd/pull/156), targeting the implemented HCAL branchPR155. Initial sourced drawing commitd4778f0fb961f89fb539662c93dbfbde97e40585. Source/render hashes, visible-section counts, visual layout, inventory, project/session/interaction/token validators and whitespace checks pass. Largest new blob is the1.394MB vectorPDF; no raw runs or geometry dumps are included. Exact task input/output token usage is unavailable. No native dependency activation or simulation rerun.
