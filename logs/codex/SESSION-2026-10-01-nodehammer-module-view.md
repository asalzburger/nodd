# SESSION-2026-10-01-nodehammer-module-view

## Request and scope

User: “Make a single module.nhproj which only shows the module components”.
Added an m1-only view to the existing repeatable nodehammer preparation workflow
on PR33. No new detector parameter or scientific sign-off. Governing DES-012 and
TASK-SOFT-NODEHAMMER; existing source provenance unchanged.

## Outcome and validation

Generated build/nodehammer/independent-colours/module.nhproj in the shared user
checkout with the current edited palette. The selection keeps m1 and descendants:
silicon substrate, active sensor, ASIC, flex glue, two copper layers, polyimide
and graphite contact shim. Eight physical placements are rendered. World and
assembly nodes are structural only. No stave, mounting or external services.

The existing descendant-selection audit now handles both stave and module views.
The complete workflow passes for all four views. Module GLB contains seven unique
meshes; all eight box dimensions, ten transforms and configured RGBA/BLEND values
pass. Project pack/info succeed. Retained hashes and upstream/runtime provenance
are in docs/validation/nodehammer/module-view.json; generated binaries stay ignored.
The archive retains the full semantic input plus the module-only selection,
consistent with the other project archives; it displays only module components.

The test harness imports the updated helper from its isolated worktree and sets
prepare.ROOT to the existing shared checkout. This uses the user's local palette
without committing it. Existing physical geometry and old evidence are unchanged.
This continues the verified acts-spack runtime from the immediately preceding
colour/transparency task. No new dependency build or broad upstream retest needed.

## Changes and follow-up

Updated tools/nodehammer/prepare.py and README, tracking/evidence and this session
pair. The user can replace full.nhproj with module.nhproj in the supplied viewer
command. PR33 will include both requested display refinements. Native transparency
remains unsupported by the pinned viewer.

## Token accounting

No exact client per-turn counters or stable turn IDs were exposed. Usage is empty;
input/output totals for this task are unknown, not zero. No estimates or repeated
historical observations were added.
