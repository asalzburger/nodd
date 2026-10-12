# SESSION-2026-09-29-pr24-default-layout — PR24 default layout and transverse views

## Request and starting state

The user asked to address the new comment on PR #24. The [expert comment](https://github.com/asalzburger/nodd/pull/24#issuecomment-5886458913)
requests a concrete default per-subdetector placement and x-y barrel/endcap views.
Start revision: `a382a72f304c44d4316a60e9117cc760c141dbb7`, branch
`study/cobe-pint-module-coverage`. Four untracked files from the separate usage
summary task remain untouched and excluded from this response's commits.

## Interpretation and design boundary

A draft DES-009 amendment precedes implementation. The initial interpretation was
no pint inclined barrel ends, while retaining explicitly requested local module
tilts, and long strips for the unnamed third barrel bullet. An optional
clarification was requested. The user asked “What follow-up question is there?”;
the response explained these two points. The user then explicitly confirmed:
“no tilt section means no inclined section as default, the nunnamed barrel bullet
is long strips”. This matches the implemented and tested scope; no numerical
inputs or results changed. Cobe's complete cylindrical nominal layers avoid
removing pint end pieces while retaining its shortened cylinders.

Pixel phi staggering uses tangential staves at alternating radii, no z staggering
by default. Short strips stagger in phi and z; tangential alternating-radius staves
are the default, while a common-radius locally tilted option separates the two
phi-overlap mechanisms. Long strips use local phi tilt on constant-radius staves,
without z staggering. Endcaps retain clearance staggering pending engineering.
The two independent pixel-z and short-tilt switches form a 2x2 comparison.

No-z staves hold phi/radius/tilt fixed along their length, with a nonoverlapping
body-based longitudinal pitch. Full rows cover the nominal end extent without
cropping; inactive seams remain measured. Old variants and their retained evidence
remain unchanged. The new default is a working prototype, not detector sign-off.

## Delegation and runtime

Three existing, human-requested agents divide geometry, true section/endcap views,
and independent policy/report review. Root owns design, configuration, execution,
tracking, session records and PR response. The acts-spack preflight warns of
changed fingerprints; required ACTS capabilities were directly verified using
the preserved local installation and isolated PR6178 step-size overlay. No shared
ACTS source, build or install changes are needed. Two constructor mistakes in the
initial runtime probes were corrected and retained in the paired check history.

## Execution, results and revisions

The numerical and native source revision is `30ac28acaee5f8359acb1654de655a9760c7d704`.
All four policies clear trial occupied-body and host checks. Nine new scan cases
cover 169,344 trajectory evaluations; all nine native audits pass on 432 tracks,
382,142 candidate targets and 6,241 reached patches. Source/input/overlay hashes
and actual commands accompany the retained evidence.

The selected default has 24,855 assemblies, 33,128 physical sensors and
217.465 m² gross sensor surface. Independent-sample missing eligible station
fractions are 5.970/5.897/6.302% for straight/positive/negative tracks. The combined
long-barrel phi-tilt/no-z policy saves most of the 36.074 m² versus the previous
fully staggered cobe but misses 16.40/15.15/22.92% of eligible long-barrel stations.
That comparison changes both phi and z policies, so it does not isolate the
cost of removing z staggering alone. Pixel z staggering helps modestly. The
tested short-strip local tilt loses coverage and adds depth, so tangential
modules remain the default.

The primary grid has straight tracks with only two reached stations, whereas
the independent default sample has at least five. Independent review corrected
an initially incorrect attribution: those two-station tracks are forward
pixel-endcap directions (eta ±3.4, z ±150 mm) with seven eligible endcap stations
and no eligible barrel stations. They are not barrel z-seam losses. The raw
numerical evidence was correct and unchanged. These are finite geometric probes,
not reconstruction efficiency or continuous hermeticity.

A 26-row minimum-pitch long barrel collided 328 times with first-endcap trial
bodies. The rejected control is retained. The documented MP-C18 amendment uses
25 full rows at 112.667 mm pitch, preserving ideal unrotated endpoints and
leaving 7.890 mm body clearance. Rotated sensor corners overhang the nominal
extent by 0.950 mm. No sensors were cropped.

True x-y barrel cuts and positive reference-endcap tiled projections are exported
for the default and short-tilt option. Physical sensor outlines, active patches
and occupied bodies are distinguished. The z=0 outer-pixel inter-module gap
remains visible; a second cut shows all four pixel barrels. Geometry/view code
and input hashes accompany fresh exports. Full native navigation, material and
Geant4 validation remain outside this scope.

All 41 local module/native/view tests passed. A portability correction to the
new legacy test compares exact JSON against the frozen a382a72 generator on
the same machine, retaining the earlier 12 macOS hash checks as observed evidence.
All 27 dashboard, 32 logging and 14 JavaScript checks passed. Report exports and
dashboard build passed. Exact completed-turn counters remain unavailable and
are not estimated or copied from previous usage inventories.

## Runtime commands

Scans used the installed pyvenv and the existing isolated ACTS binding overlay:

```sh
source /Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/activate
source /Users/salzburg/Documents/work/installed/acts-nodd/bin/this_acts_withdeps.sh
export PYTHONPATH="/tmp/acts-python-step-size-overlay/python:${PYTHONPATH}"
python -B tools/module_layout/study.py run --native --jobs 4 \
  --models tools/module_layout/review_models.json \
  --config tools/module_layout/review_config.json \
  --output reference/cache/DES-009-review-main-20260929 \
  --acts-source /Users/salzburg/Documents/work/dev/acts-nodd \
  --runtime-manifest /tmp/acts-python-step-size-overlay/manifest.json
```

Offgrid and total-p runs substitute the explicit configs/output paths recorded
in the paired JSON. Each report/view export is fresh. Subsequent plot-label and
portable-test changes do not alter the frozen numerical geometry or evidence.

## Publication and clarification

Evidence commit `01b8e229663f117fb22d98f90af4b932312b6979` was pushed to PR #24.
The [hosted build passed](https://github.com/asalzburger/nodd/actions/runs/36545667460);
PR deployment is intentionally skipped. The title/body now describe the default,
options, figures and retained coverage limits. The [review reply](https://github.com/asalzburger/nodd/pull/24#issuecomment-5886989941)
records the user-confirmed interpretation and links the report, views and checks.
Only documentation/provenance/tracking/session metadata changed after this
evidence revision. Human re-review of the resulting prototype remains open.

Final dashboard validation/build and session validation passed. The local session
summary covers 56 records, 42 with usage and 14 without, with 79 historical turns:
134,594,309 observed input tokens and 674,111 observed output tokens. These are
partial historical observations, not a complete project total or this task's
usage, and overlap the separate usage inventory. No current root/subagent
completed-turn counters are exposed; this task retains an empty usage array.
