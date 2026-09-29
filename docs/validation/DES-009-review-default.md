# DES-009 — Reviewer-directed default and transverse views

Date: 2026-09-29. **PROTOTYPE; a working default for the next iteration.**
[Review request](https://github.com/asalzburger/nodd/pull/24#issuecomment-5886458913),
[design hypotheses](../design/DES-009-module-populated-layouts.md), and
[original comparison](DES-009-module-populated-layouts.md).

The default uses cobe's cylindrical layers, omitting pint's inclined barrel-end
sections. Local module tilts in phi are a separate choice. This interprets the
reviewer's “no tilt section” consistently with the explicit barrel tilt requests;
the unnamed third barrel bullet is taken to mean long strips.

| Region | Default | Separate option |
| --- | --- | --- |
| Pixel barrel | Tangential modules staggered in phi at alternating radii; no z staggering | Add z staggering |
| Short-strip barrel | Tangential modules staggered in phi at alternating radii, with z staggering | Local phi tilt on common-radius staves, retaining z staggering |
| Long-strip barrel | Local phi tilt on common-radius staves; no z staggering | Held fixed in this comparison |
| All endcaps | Existing clearance staggering in r/phi and normal depth | Engineering feasibility remains open |

The initial local tilt is the inherited 12 degree numerical hypothesis. The
single-plus-quad pixel policy and pinned sensor/module models from PRs #8/#21/#22
remain unchanged. Two binary switches give four comparable placements; this is
not a new pixel-family or sensor-outline optimization.

“No z staggering” means fixed phi, radius and local orientation along each stave.
Its uniform longitudinal pitch clears consecutive trial occupied bodies by at
least 0.2 mm. Full rows fit the nominal active-envelope endpoints; the largest
row count respecting the minimum body pitch is used. This avoids the 328
long-barrel/first-disc clashes found when adding an extra row at the minimum
pitch. The rejected alternative remains reproducible through the model input.
Full modules can extend beyond nominal ideal-layer endpoints; none is cropped.
Inactive longitudinal seams therefore remain real coverage losses. A phi tilt
and alternating phi radii are treated as different mechanisms, not silently
combined in the same alternative.

## Measurements and mechanical checks

Execution pending. New results use the same primary angular/vertex sample and
independent 4,096-direction sample as the original study, with straight tracks
and both charges at pT = 1 GeV in constant axial 3 T. A separate default-only
check fixes total momentum to 1 GeV. Native ACTS audits use unchanged sensitive
bounds and the supporting-plane propagation method established in the original
study. Mechanical clearance is limited to the trial occupied boxes and host.

## Transverse views

The repeatable view generator provides actual barrel cuts at stated z values,
including an adjacent row slice, and x-y projections of one positive reference
disc assembly per subsystem. Endcap modules on different stagger levels are
projected together deliberately and their normal offsets are shown explicitly.
A projected overlap is not by itself a three-dimensional solid overlap.

## Reproduce after a sensor or module update

```sh
python tools/module_layout/study.py run --native --jobs 3 \
  --models tools/module_layout/review_models.json \
  --config tools/module_layout/review_config.json --output reference/cache/NEW-review-main
python tools/module_layout/study.py run --native --jobs 3 \
  --models tools/module_layout/review_models.json \
  --config tools/module_layout/review_offgrid_config.json --output reference/cache/NEW-review-offgrid
python tools/module_layout/report.py --run reference/cache/NEW-review-main \
  --output reference/cache/NEW-review-report
python tools/module_layout/views.py --run reference/cache/NEW-review-main \
  --case cobe-review_default-mixed --output reference/cache/NEW-review-views
```

Use the [verified ACTS workflow](../../tools/module_layout/README.md). Each command
writes a fresh directory; model/layer/configuration/code hashes remain attached
to the evidence. Alternate supported shape inputs can be supplied with `--models`
and `--layouts`; changed physics inputs require a fresh scan and native audit.
The original study's evidence remains a historical comparison.
