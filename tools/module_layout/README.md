# Repeatable finite-module layout study

**PROTOTYPE.** This tool populates the unsigned [DES-006 cobe/pint
layers](../../docs/design/DES-006-named-layouts.json) with active module patches
and compares placements. It does not modify the production detector, approve a
layout or simulate reconstruction. The [DES-005 programme](../../docs/design/DES-005-tracker-system-plan.md)
places this work in its finite active-coverage stage.

## Working default after the PR #24 review

The next-study default is **`cobe-review_default-mixed`**, defined in
[`review_models.json`](review_models.json) and described in the
[review response](../../docs/validation/DES-009-review-default.md). It uses
cylindrical cobe layers, tangential phi-staggered pixels without z staggering,
tangential phi/z-staggered short strips, tilted long-strip staves without z
staggering, and clearance-staggered endcaps. It remains an isolated prototype.

`review_config.json` runs a 2×2 comparison: pixel z staggering off/on, and
short-strip tangential/tilted phi placement. `review_offgrid_config.json` repeats
the four choices on the original independent random sample;
`review_total_p_config.json` checks the default with total p = 1 GeV.
The original configurations and evidence remain available unchanged.

PR #24 did not approve this tracker layout. It remains a working hypothesis.
The separate [DES-010 service-gap prototype](../../docs/design/DES-010-tracker-service-corridors.md)
uses it to reserve support, cooling and cable space while keeping all retained
module positions and identifiers. The separate DES-011 follow-up below explores
new placements. The [executed DES-010 report](../../docs/validation/DES-010-tracker-services.md)
retains the routing mockups, failed adverse capacity scenarios and coverage costs.

```sh
python tools/module_layout/services.py \
  --output reference/cache/NEW-service-gap-study --coverage --native \
  --acts-source /Users/salzburg/Documents/work/dev/acts-nodd \
  --runtime-manifest /tmp/acts-python-step-size-overlay/manifest.json
python tools/module_layout/services_views.py \
  --run reference/cache/NEW-service-gap-study \
  --output reference/cache/NEW-service-gap-views
```

The [PR #25 service-gap review](../../docs/validation/DES-010-service-gap-review.md)
adds ATLAS/CMS comparisons and accumulated axial loads. The original axial gap
is constant and its budget uses the final whole-end load. Generate a separate
position-dependent diagnostic from any matching retained service run:

```sh
python3 tools/module_layout/services_profile.py \
  --run docs/validation/DES-010-services/main \
  --output reference/cache/NEW-service-load-profile \
  --pickup-policy near-edge-full-load
python tools/module_layout/services_profile_views.py \
  --run reference/cache/NEW-service-load-profile \
  --output reference/cache/NEW-service-load-profile-views
```

The first command uses the standard library only; plotting needs Matplotlib.
Input snapshots and original producer hashes are checked before using the
retained local groups. Each branch contributes once, with original chain and
per-layer manifold rounding. Finite pickup intervals and both signed ends are
retained; the final load must exactly reproduce the original trunk budget.
The equivalent annular width is diagnostic only. No existing gap, sensor row,
coverage evidence or downstream junction capacity is changed. After changing
module shapes or producer logic, create a fresh service run before profiling it.

Use the verified runtime/overlay setup below; the temporary overlay path is
machine-specific and must be recreated or replaced by an equivalent binding
when unavailable. Without `--native`, geometry, budget and coverage need no ACTS
import. Omit `--coverage` for a fast service-space and capacity-only probe.
`--config`, `--budget`, `--models`, `--layouts`, `--envelopes` and `--sampling`
select explicit inputs. The service inputs distinguish adopted reference
architecture, adverse packing/readout cases and an unqualified strixel stress.
Every run writes fresh byte-exact input snapshots and source hashes. Shape
updates regenerate the baseline before whole-row exclusions; no stale module
removal list is applied. Missing route capacity is retained as a scenario failure,
while physical clearance, disconnection or native audit failures stop execution.
Support envelopes reserve space only; the service tool does not add material,
thermal calculations, structural mechanics or a layer-position optimizer.

## Service-constrained placement follow-up

[DES-011](../../docs/design/DES-011-service-constrained-tracker-optimization.md)
implements the subsequent PR #25 review direction as a separate prototype.
It refills fixed sensor/module shapes into candidate annuli, derives uniform
service corridors from their actual inventories, and places the first disc at
the closest finite-body/service limit with at least 10 mm clearance. Optional
last-disc bypasses remain explicitly routed and included in downstream loads.
The compact 10 mm collector floor is an unqualified sensitivity assumption;
the original pocket floors are retained as a comparison.

```sh
python tools/module_layout/optimization.py --jobs 3 --native \
  --output reference/cache/NEW-service-optimization \
  --acts-source /Users/salzburg/Documents/work/dev/acts-nodd \
  --runtime-manifest /tmp/acts-python-step-size-overlay/manifest.json
python tools/module_layout/optimization_views.py \
  --run reference/cache/NEW-service-optimization \
  --output reference/cache/NEW-service-optimization-views
```

Use the verified runtime setup below when `--native` is requested. Without that
option the scan and finite-module intersections need Python/NumPy only. The
search configuration, sensor models, layout catalogue, service budget and
envelope inputs are explicit command-line inputs and snapshotted per fresh run.
`--search-only` omits final validation, and `--limit` is for development probes;
neither should be presented as the complete configured study.

The bounded search ranks training samples and freezes coverage/spacing/area
finalists before dense validation and an independently seeded random cohort.
It is not a proof of global optimality or continuum hermeticity. Reachable
stations and fixed-original-layer misses accompany physical path gaps; chip
islands and stereo faces cannot inflate the station count. Active area is the
sum of finite sensitive patches, including overlaps, not their projected union.
The revised selection also guards the central eta=0/z=0 cohort and rejects newly
fully blind eta/vertex strata. All smaller local regressions remain visible;
mean gains do not establish pointwise non-regression. The first even-row run
exposed a central long-strip seam and is preserved as rejected evidence.
Native checks include explicit central probes in all three trajectory modes.
Every rejected candidate and its parameters remain in `study.json`. Regenerate
the study after sensor-shape changes instead of reusing old service inventories.

```sh
python tools/module_layout/study.py run --jobs 3 --native \
  --models tools/module_layout/review_models.json \
  --config tools/module_layout/review_config.json \
  --output reference/cache/NEW-default-comparison
python tools/module_layout/views.py --run reference/cache/NEW-default-comparison \
  --case cobe-review_default-mixed --output reference/cache/NEW-default-views
```

Add `--cases cobe-review_default-mixed` to run only the default. The same explicit
inputs permit revised module dimensions without changing the scan or plotting
logic. `views.py` checks retained geometry and input hashes, then produces true
barrel cross sections at stated z positions and labelled endcap assembly
projections. Empty sections through longitudinal seams remain empty. All outputs
go to fresh directories; a projected endcap overlap is not a solid intersection.

## Inputs and rerunning

Run commands from the repository root. The independent numerical calculation
requires Python and NumPy. Native validation also requires the patched ACTS
Python installation, ROOT and the ACTS examples bindings; plotting requires
Matplotlib. Follow the [local ACTS workflow](../../AGENTS.md#local-acts-sister-checkout)
and [node preflight](../../skills/acts-spack/SKILL.md) before depending on that
installation. In one shell on the registered machine:

```sh
python3 skills/acts-spack/scripts/preflight.py
source /Users/salzburg/cernbox/configs/acts/acts_setup.sh
acts run acts-nodd
source /Users/salzburg/Documents/work/installed/acts-nodd/pyvenv/bin/activate
python -c 'import sys, acts, numpy, matplotlib; print(sys.executable); print(acts.__file__); print(hasattr(acts.Surface, "assignIsSensitive"))'
```

The runtime helper copies ODD data/configuration into the installation; it is
not a read-only preflight. Inspect warnings and verify the printed environment
and sensitivity capability. Do not rebuild or modify shared dependencies merely
to pass these checks.

Choose a **new output directory** for every run. This example executes the
configured matrix with three worker processes, then independently audits each
case through ACTS:

```sh
python tools/module_layout/study.py run \
  --output reference/cache/module-layout-example-run \
  --jobs 3 --native \
  --acts-source /Users/salzburg/Documents/work/dev/acts-nodd
```

`--acts-source` is optional and records checkout provenance when supplied; the
imported installation remains a distinct artifact. Without `--native`, the
bulk calculation needs no ACTS import, and `run.json` records that the native
audit has not run. Add the audit later without replacing an earlier audit:

```sh
python tools/module_layout/study.py validate-acts \
  --output reference/cache/module-layout-example-run \
  --acts-source /Users/salzburg/Documents/work/dev/acts-nodd
```

The driver checks retained geometry/intersection code hashes before regenerating
the audit geometry. After a physics-engine change, create a new run instead of
attaching results to old evidence. An ACTS disagreement stops validation and
leaves its diagnostics available for investigation.

Three explicit inputs control the workflow:

| Option/default | Meaning |
| --- | --- |
| `--config tools/module_layout/study_config.json` | Candidate/variant matrix, momentum convention, field, luminous samples, seed and native/control sample sizes |
| `--models tools/module_layout/sensor_models.json` | Active sensor dimensions, masks, stereo separation/angle, trial occupied bodies, placement parameters and pinned source provenance |
| `--layouts docs/design/DES-006-named-layouts.json` | Original layer positions, finite bounds, station groups and host envelope |

Pass alternate files to study revised dimensions without overwriting the input
fixtures or previous output. `--cases cobe-flat-mixed,pint-flat-mixed` restricts
a run to listed case IDs; unknown IDs are rejected. Keep new physical inputs
classified and documented under the design/provenance workflow.

`momentum_convention: "pt"` fixes transverse momentum; this study uses
`momentum_GeV: 1.0` and `field_T: 3.0`. `"p"` instead fixes total momentum and
sets `pT=p/cosh(eta)` for each direction. These are different physics samples.
The straight control uses zero field, while positive and negative charge modes
use the same directions in the configured axial field. A low-pT curling track
is stopped at its first transverse half-turn; later returns are outside this
coverage definition.

## Sampling and comparisons

The supplied configuration combines a central x/y grid at three z vertices,
all four x/y boundary corners at those three z vertices with an offset phi
phase, and seeded continuous samples throughout the luminous box. Its bounds
are x/y = 0..1 mm, z = -150..150 mm and signed eta = -4..4. The eta endpoints
are coverage-margin probes. With the supplied grid sizes there are 8,992
directions and 26,976 trajectories per main case across the three modes.

Fractions use this declared sampling measure; they are not collider event
weights, uniform solid-angle efficiencies or a proof about every point in the
box. A minimum is the worst sampled value. The random samples help reveal
grid-phase coincidences; they do not establish continuous hermeticity.

The single/double/quad pixel controls and gap sensitivities all use the same
1,536-direction subset. Compare them to the matching
`cobe-staggered-mixed-control` / `pint-staggered-mixed-control` case, which uses
that exact subset, rather than to the larger main sample. The native audit
includes seeded tracks in each of the three modes plus sampled worst-hole
cases; it is a smaller independent software check, not a second bulk scan.

## Geometry, intersections and counted quantities

`geometry.py` produces finite oriented rectangles. Multiple pixel chip-active
islands share a physical `sensor_id`; the two separated long-strip sensors
have distinct sensor IDs and a common `module_id`. `station_id` deduplicates
the original logical station, including pint's inclined segments. The two
long-strip faces retain their actual separation and stereo angle, so a track
can hit only one face.

`intersections.py` uses exact uniform-field helices and finite-plane roots.
It partitions each plane residual at its analytic derivative extrema and
brackets all roots in the first traversal, including tangencies. A conservative
voxel index uses sensor-corner boxes and helix-segment sagitta padding; it
only selects candidates and does not approximate their intersections. The
plane-root and active-bound tolerances are both 0.000001 mm. Transport ends
at the first outer cylindrical or longitudinal host boundary, or the first
transverse half-turn. Each physical sensor is counted at most once.

| Metric | Definition |
| --- | --- |
| `sensor_hits` | Unique physical active sensors reached; long-strip faces count separately; pixel active islands deduplicate |
| `complete_long_strip_pairs` | Both active faces of the same module reached; faces from different modules never form a pair |
| `orphan_long_strip_faces` | Reached long-strip faces minus twice the complete-pair count |
| `stations` | Unique logical stations with any pixel/short-strip sensor hit or a complete same-module long-strip pair |
| `ideal_stations` | Logical stations reached in the original continuous ideal layer geometry |
| `missing_stations` | Ideal station-ID set minus reached station-ID set; extra hits cannot hide another station's hole |
| `extra_stations` | Reached station-ID set minus ideal station-ID set, for example due to a full sensor extending beyond an original segment |
| `fraction_all_ideal_stations_hit` | Fraction with no missing ideal station among tracks eligible for at least one ideal station in that scope |
| `missing_ideal_station_fraction` | Total missing ideal stations divided by total reachable ideal stations in that scope |

Summaries retain count distributions, minimum, mean and quantiles for the total,
each subsystem, each region, and subsystem/region combinations. Per-layer
statistics keep their own eligible and missed counts. Eta and phi profiles
expose direction dependence. A layer's `tracks_with_hit` requires a complete
pair for long strips; its separate `sensor_hits` still records unpaired faces.

Silicon area is the sum of the complete physical sensor outlines, once per
sensor and twice for two-sensor strip modules. Active area sums the chip-active
patches. Neither is the area of an ideal cylinder/disc. Readout-chip silicon,
supports, cooling, power and service material are not included in sensor area.
Pixel sensor outlines, guard widths and inter-chip gaps remain conditional
fixtures where the source proposal has not established them.

`acts_validate.py` constructs every finite patch as a sensitive ACTS plane in
one Gen-3 cuboid leaf. When the ACTS binding exposes
`PropagatorPlainOptions.stepping.maxStepSize`, its primary audit propagates
directly to every conservative candidate's unbounded supporting plane with
`EigenVoidPropagator` and a maximum step of 10 mm, then applies the original
finite sensitive surface's native `RectangleBounds.inside` check. ACTS supplies
the intersection and returned geometry ID. Exact patch-ID
sets are compared to the independent oracle. The trajectory diagnostic
tolerance is 0.002 mm; boundary masks are not expanded by that tolerance.
Negative candidate trials are retained in the counts. The voxel broad phase
is shared with the oracle; small native controls also test every plane
exhaustively. The report states the selected method and fingerprints the
imported extension separately from its source checkout.

This validates native transport and finite intersections, not the full ACTS
navigation hierarchy. The retained [adverse control](../../docs/validation/DES-009-native-navigation-control.json)
shows that the global `Navigator` with one large `TryAllNavigationPolicy` leaf
loses candidates after bending: its five straight tracks agree, while all ten
curved tracks miss sensitive IDs. Those software misses are not layout holes.
The earlier target-propagation binding lacks a step-size control: a long first
tangent step can overshoot a nearby target beyond ACTS' recovery window. On
that older runtime the tool falls back to native double-precision guide states
at 10 mm intervals, reanchors target propagation before supporting-plane
crossings, and applies the real finite bounds. This fallback is explicitly
reported; unresolved tangencies or two crossings inside one guide interval
remain its stated limit. The direct mode removes that guide-bracketing limit.
The exact analytic bulk solver treats both cases independently.

A retained [off-grid control](../../docs/validation/DES-009-native-edge-control.json)
also exposes a finite-target boundary loss: at a 10 mm maximum step ACTS missed
a crossing 5.43 micrometres inside a strip edge, while 5 mm and 1 mm finite-target
runs recovered it. The supporting-plane approach recovers that crossing at all
three step sizes with the original strict finite bounds. This treatment applies
to every candidate; no oracle prediction selects an exception. A native
regression shifts a second patch by 10 micrometres and verifies that its genuine
miss remains rejected.

Reproduce the adverse control in a fresh directory with:

```sh
python tools/module_layout/acts_validate.py \
  --candidate cobe --variant flat --pixel-family mixed \
  --tracks docs/validation/DES-009-native-navigation-control.json \
  --full-navigation \
  --work reference/cache/DES-009-navigation-control-replay \
  --report reference/cache/DES-009-navigation-control-replay.json \
  --acts-source /Users/salzburg/Documents/work/dev/acts-nodd
```

An exit status of 1 is the expected failure-control outcome. The optional
`--full-navigation` path retains ROOT sensitive IDs and float32 CSV inputs;
the primary audit uses neither CSV input rounding nor ROOT hit inference.

## Retained artifacts and export

The run directory preserves:

| File | Contents |
| --- | --- |
| `run.json` | Command, revision, dirty working-tree record, Python/NumPy versions, code/input hashes, case list and native-audit state |
| `config.json`, `sensor_models.json`, `layouts.json` | Exact input snapshots |
| `<case>/summary.json` | Geometry area/count summary, host/body diagnostics and coverage summaries for all modes |
| `<case>/track_metrics.json.gz` | Directions/cohorts and per-track metric columns, including subsystem/region breakdowns |
| `<case>/native_tracks.json` | Exact selected audit trajectories, mode and original sample index |
| `<case>/acts_validation.json` | Native/independent comparison, per-track identities and residuals, runtime provenance and artifact fingerprints |
| `<case>/acts/native-target-audit.json` | Native target trials, selected method, reached positions/IDs, negative trials, fallback guide counts if used, and runtime hashes |

Export the comparison into another fresh directory:

```sh
python tools/module_layout/report.py \
  --run reference/cache/module-layout-example-run \
  --output reference/cache/module-layout-example-report
```

The exporter creates JSON/CSV summaries and figures for review. Preserve the
run directory and its native artifacts or record their retained storage and
hashes when publishing a compact report. Re-running into an existing evidence
directory is intentionally rejected; never regenerate accepted evidence merely
because a result changed.

Run the numerical/geometry/sampling controls with:

```sh
python -B -m unittest discover -s tools/module_layout -p 'test_*.py' -v
```

## Supported changes and limits

Updated rectangular active dimensions, explicit chip islands, guards,
separation, stereo angle, layer locations and placement fixtures can use the
same workflow. Native non-rectangular/trapezoidal/polygon bounds are not
implemented: unsupported `shape` values are rejected rather than silently
approximated. Add matching geometry, independent-intersection and ACTS adapters
and controls before studying another shape.

The ideal inclined denominator supports the current pint inward-sloping finite
r-z segments, with positive radial unit normals and longitudinal normal aligned
with the reachable track direction. Inconsistent endpoint geometry and
unsupported orientations are rejected. The finite-plane solver itself handles
arbitrary 3D tilts; broadening the ideal reference requires its own control.

Occupied-box collision and host-overhang diagnostics are screening tools.
They do not close support, thermal, electrical, routing, clearance or material
engineering. Modules are not cropped to hide overhangs or overlaps. No material,
energy loss, multiple scattering, efficiency, occupancy, fitting, pattern
recognition, DD4hep construction or Geant4 transport is simulated. Human design
review and eventual production validation remain separate requirements.

## Independent sampling, momentum convention and exact reruns

The preferred step-size API is proposed in draft
[ACTS PR #6178](https://github.com/acts-project/acts/pull/6178), commit
`9e3b59f638a38520abe9420fe8868eff3de6789f`. It exposes
`options.stepping.maxStepSize` without changing the ACTS defaults. This study
sets 10 mm explicitly. The existing sensitivity binding is
[ACTS PR #6176](https://github.com/acts-project/acts/pull/6176).

`offgrid_config.json` checks the four clearance candidates using 4,096 new
uniform eta/phi/x/y/z directions. `total_p_config.json` repeats those directions
with total momentum fixed at 1 GeV, instead of fixed pT. Each is a complete
configuration, so the same `study.py run --config ... --output NEW --native`
command applies. Neither sample is a physics event distribution.

To check a repeat execution without replacing the first result:

```sh
python tools/module_layout/study.py compare \
  --first reference/cache/original-run \
  --second reference/cache/repeated-run
```

Use `--cases cobe-staggered_clearance-mixed` to select a case explicitly when
the two directories contain different case sets. Comparison requires exact
geometry diagnostics, summaries, directions, per-track metrics and native track
selections; elapsed time and separate native-audit artifacts are excluded.
Gzip headers and runtime timestamps are not numerical results.

To rerun native validation with a changed ACTS version or audit implementation,
use `study.py validate-acts --output EXISTING_RUN --audit-label NEW_LABEL`.
The named report and artifacts are new files; earlier passes and failures remain.
The run metadata records the audit history and selects the latest passing report
for export. Geometry/oracle hashes must still match the numerical run; changed
sensor or layer inputs require a fresh full run instead.

For an isolated development build overlay, `--runtime-manifest PATH` records
its provenance with each native audit and requires its `acts_extension_sha256`
to match the actual imported extension. This is optional for ordinary ACTS
installations. Keep overlay source revisions and reused compiled objects distinct
from the original sister-checkout revision.

The public CI runs the geometry, intersection and sampling regression controls
with NumPy on every PR. The three native integration tests explicitly skip when
ACTS is unavailable there; run the same command in the verified ACTS environment
to include them:

```sh
python -B -m unittest discover -s tools/module_layout -p 'test_*.py' -v
```
