# Tracker module reuse comparison — PR132 follow-up

**PROTOTYPE, unsigned.** The [2026-11-11 review comment](https://github.com/asalzburger/nodd/pull/132#issuecomment-6790854055)
authorizes a tracker comparison prototype. Governing records: DES-025, DES-043,
ADR-003 and issue130. This experiment does not change the maintained detector,
its compact exporter, physical parameters or approval state.

The [initial investigation](README.md) and `results.json` retain their original
baseline-only identity. This follow-up tests the proposed short-strip barrel
experiment, where 8,064 modules have one strict local recipe. It does not apply
ECAL timing ratios to the tracker.

## Observed results

The [compact results](comparison-results.json) pass all bounded checks. Every
original constituent has the same native solid/material/local and global
transform/ID fingerprint: **617,018 original solid placements, zero missing/extra/changed**. Each
variant has **46,682 unique sensor IDs and per-instance DetElements**, 180,288
finite window/contact probes, 38 sampled material/crossing rays, and zero ROOT
overlaps/extrusions at 1e-5 mm. All six native Geant4 snapshots match the control
by packed ID, with **zero numerical differences** in centers, signed axes,
box dimensions and density; material and region match exactly. No total general-CSG mass or
stochastic response equivalence is asserted.

| Geant4 hierarchy observable | Control | A: cache | B: cache + mother |
| --- | ---: | ---: | ---: |
| Unique logical volumes | 617,019 | 488,011 | 488,012 |
| Physical-volume store entries | 617,019 | 617,019 | 496,075 |
| Direct world daughters | 604,000 | 604,000 | 483,040 |
| Expanded physical nodes incl. world | 617,019 | 617,019 | 625,083 |

B inserts 8,064 physical mothers in Geant4 while preserving every original
leaf; this explains the increase in expanded nodes alongside fewer unique
objects and direct world daughters. A retains flattened assembly imprints.

Two fresh sequential observations per variant, on the same node/build, give
the following **median (observed minimum–maximum)**. Times are seconds; peak
child resident memory is GiB (2³⁰ bytes). These ranges are not confidence intervals.

| Variant | DDG4 map [s] | G4 closure/voxelization [s] | Initial cuts [s] | Instrumented subprocess wall [s] | Peak RSS [GiB] |
| --- | ---: | ---: | ---: | ---: | ---: |
| Control | 3.543 (3.540–3.545) | 32.94 (32.91–32.96) | 7.30 (7.18–7.43) | 90.96 (90.62–91.30) | 7.76 (7.76–7.77) |
| A: cache | 3.571 (3.537–3.605) | 32.53 (32.53–32.53) | 13.42 (12.62–14.21) | 95.19 (94.50–95.88) | 7.28 (7.22–7.33) |
| B: cache + mother | 3.106 (3.080–3.133) | 29.27 (29.21–29.32) | 8.64 (5.45–11.84) | 86.49 (83.32–89.66) | 7.09 (7.06–7.13) |

**FACT, these observations:** B lowers median closure time by 11.1% and DDG4
map time by 12.3% versus control; B/A closure decreases by 10.0%. Its median
instrumented subprocess wall is 4.9% lower and peak RSS 8.6% lower. This is a
modest observed benefit, with only two runs. It does not establish an ECAL-like
large initialization speedup or a universal total-startup improvement.

The adverse A result is retained: median instrumented wall increases from
90.96 s to 95.19 s, while initial cuts increase from 7.18–7.43 s to
12.62–14.21 s. B's initial cuts span 5.45–11.84 s and account for much of its
wall-time spread. The cause of that cut-table timing variation is unresolved;
no physical material or region difference is observed, and no cut-couple
optimization is enabled. Initial-cut profiling and additional controlled
repetitions are appropriate before an integration performance claim.

**INFERENCE:** the observed closure/map reduction makes a real-mother
representation worth further software qualification, but cached assemblies
alone are not an initialization-speed improvement in this observation.
ACTS conversion/navigation, repeated BeamOn(1), response/boundary studies and
review of initial-cut behavior remain due before maintained integration.
No production entry point or design approval changes.

The new matched control retains the initial investigation's compact hash, but
its timing differs from the historical single 553 s observation. That older
record reported concurrent work; the cross-session timing difference is not
quantified here. No part of it is credited to the prototype. All reported
prototype timing comparisons use only the six new matched observations.

The compact receipt retains hashes of all three large native identity snapshots.
The curator independently compares their constituent and DetElement digests and
binds each snapshot to its native report. Future checker receipts also hash the
`--baseline` snapshot input; the historical raw native reports remain unchanged
at their executed source hashes. No geometry rerun is implied by this metadata
clarification.

## Experiment definition

Control: unchanged combined DES-025/DES-043 tracker exported at
`d6d2c510cf63209228790a95fd57d155a7b9787a` and built afresh locally.
A: strict module template cache, retaining assembly structure.
B: the same cache with a finite real module mother, subject to containment and
sibling-interface checks. The other tracker factories, materials, readouts,
IDs, cuts, physics, seeds and simulation controls remain matched.

Compare A/control for factory construction and unique-object costs. Compare B/A
for hierarchy, direct world daughters, DDG4 mapping and geometry closure. Do not
sum nested phase intervals. Full subprocess wall time includes inventory JIT,
I/O and teardown. Repeated observations characterize this node; they do not
select a detector acceptance threshold or establish a general speedup.

Required comparisons include all expanded sensors and original constituent
placements, material/shape/transform identity, contact/window probes, packed
IDs and per-instance DetElements. A real mother also needs finite containment,
sibling overlaps and sampled material-ray checks. ACTS and response qualification
remain separately identified; one geantino event cannot establish response
equivalence. Preserve adverse results.

## Representation and finite interfaces

A caches one exact local module recipe and places its assembly 8,064 times.
Names and outer module identity/pose are excluded from the cache key; child IDs,
material, sensitivity, cuts and all local geometry strings remain in it. Both
Python preparation and the C++ factory reject a mismatching recipe. Sensor
DetElements retain their original per-instance names and placements. The
instance-to-template map stays with the generated compact in the ignored run
area. Repeated XML is retained, so this is not an XML-size optimization.

B replaces only the cached assembly with a real mother in the actual enclosing
world material, checked by the factory. Its local bounds are u=±24.5 mm,
v=±51.5 mm, w=−1.025…0.1 mm. Two 20.1×64.1×0.2 mm³ notches at
(u,v,w)=(±12,0,−0.925) mm preserve the existing cold pickups. The module origin,
all children and instance transforms remain unchanged. These are **INFERENCE**
bounds derived from the current physical recipe, not new detector dimensions.
The **NODD DESIGN CHOICE** is to test this unsigned software representation.

SysArch PR132-SA01 found that plain boxes intersect 16,128 owning pickups.
The notches remove these intersections. The finite screen found zero hits in
165,312 cross-stave rectangle comparisons and 1,451,520 ancestor-sector
comparisons. Minimum same-stave mother separation is 0.375 mm; the conservative
ancestor-sector gap is 9.113452 mm. The separate session record retains the
source revision and full bounded assignment. These analytical results do not
replace the native checks below. No physical engineering requirement or
source-manifest entry changes.

## Validation and measurement boundaries

Native DD4hep checking fingerprints every expanded original constituent's
recursive solid parameters, material/density/X₀/interaction length, IDs and
local/global transforms, independently of shared logical names. It also checks
all sensor frames, packed IDs, per-instance DetElements and existing finite
contact/window probes. Only B's same-material mother is added to the comparison;
original physical material is not excluded. General intersecting CSG is never
claimed as an exact mass total. All candidate geometries require the full
ROOT overlap/extrusion check at the maintained 1e-5 mm tolerance and default
ROOT point sampling (no selected ROOT seed).

The baseline-only `--snapshot-only` mode reports `SNAPSHOT`, `overlaps: null`
and no overlap verdict. It permits independent identity extraction while the
fresh maintained baseline scan runs. It cannot be used for a candidate, and
is supplementary to that separate full baseline report. `--overlap-evidence`
can instead reuse a completed baseline PASS only after checking exact input,
factory, validator and ROOT-version identity. Neither mode removes a required
candidate scan or relaxes the tolerance.

The native Geant4 callback expands all sensitive placements and uses the DDG4
volume manager on actual touchable histories. It records packed IDs, centers,
three signed axes, box bounds, material/density and region. Compare by ID with
1e-7 mm position/size tolerance, 1e-10 axis-component tolerance and
1e-12 g/cm³ density tolerance; duplicate/missing IDs and nonfinite numbers fail.
These are numerical consistency checks, not human acceptance tolerances.
Region names are observed before first-run cuts are assigned; this is not a
per-volume cut-couple equivalence proof.

Material navigation uses 27 origin rays (eta −4…4, phi 0/0.37/1.11) and 11
short local rays through pickups, both sides of notch edges and flex edges.
It compares material path lengths including ambient Air and crossing-ID sets;
new same-material boundaries may change step segmentation. This sparse sample
cannot establish complete response or curved-track navigation equivalence.

The startup runner uses fresh sequential processes, with baseline/cache/mother
in round one and mother/cache/baseline in round two. Each transports one
10 GeV geantino from the origin in +x, seed130001, one thread, FTFP_BERT and
0.7 mm range cut. These are probe controls, not tracker requirements. Native
static cut-couple reuse and the optional energy-cut client are disabled.
Every run uses the same five maintained libraries, isolated sidecar, timing
helper, steering, inventory/sensor helpers and material bytes. The aggregator
rejects mismatched common hashes/normalized commands, changed variant compacts,
missing phases/events and fewer than two observations per variant.

Call the complete metric **instrumented subprocess wall**: interpreter startup,
JIT, inventories, sensor snapshots, I/O and teardown contribute. Export and
DD4hep factory construction are not timed independently. Only the recorded
native converter/map/initialization/closure/cut phases support phase-specific
claims. Named intervals can nest and must not be summed. Ranges across two
observations are descriptive, not confidence intervals. Other shared-host
workload is not measured. The earlier diagnostic run predates the sensor
callback and is excluded from matched observations.

ACTS conversion/navigation, repeated ACTS BeamOn(1), a complete directional
material study and stochastic response/transport equivalence remain separate
integration gates. A passing comparison prototype grants no design sign-off.

## Reproduction

Use a fresh `build/pr132/` directory. Raw compacts, manifests, identity snapshots,
logs and event outputs stay local and ignored. Run the acts-spack preflight,
then verify current runtime imports, versions and datasets; a stale registry
alone is not a passing environment check. The current observed environment is
DD4hep1.38 /3yd4hz3, Geant411.4.3 /wfg55xi, ROOT6.40.04, Python3.14.5,
AppleClang21 on acts-mac-studio-01.cern.ch. No shared dependency is changed.

```sh
python3 -B tools/tracker_dd4hep/export.py --output build/pr132/baseline
software/env/run.sh cmake -S . -B build/pr132/tracker -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
software/env/run.sh cmake --build build/pr132/tracker --parallel 3 --target \
  Components_nODDPixelBarrel Components_nODDBeamPipe \
  Components_nODDShortStripBarrel Components_nODDShortStripEndcap Components_nODDLongStrip
software/env/run.sh cmake -S prototypes/tracker_placement_reuse -B build/pr132/reuse \
  -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build build/pr132/reuse --parallel 3
python3 -B docs/validation/tracker-placement-reuse/prepare_comparison.py \
  build/pr132/baseline/tracker.xml build/pr132/cache --mode cache
python3 -B docs/validation/tracker-placement-reuse/prepare_comparison.py \
  build/pr132/baseline/tracker.xml build/pr132/mother --mode mother
software/env/run.sh python3 -B tools/tracker_dd4hep/validate.py \
  --compact build/pr132/baseline/tracker.xml --expected build/pr132/baseline/expected.json \
  --library-dir build/pr132/tracker/detector --output build/pr132/baseline-native.json
software/env/run.sh python3 -B docs/validation/tracker-placement-reuse/check_equivalence.py \
  --compact build/pr132/baseline/tracker.xml --expected build/pr132/baseline/expected.json \
  --library-dir build/pr132/tracker/detector --snapshot build/pr132/native-baseline-snapshot.json \
  --output build/pr132/native-baseline-snapshot-report.json --snapshot-only
for variant in cache mother; do
  software/env/run.sh python3 -B docs/validation/tracker-placement-reuse/check_equivalence.py \
    --compact "build/pr132/$variant/tracker.xml" --expected "build/pr132/$variant/expected.json" \
    --library-dir build/pr132/tracker/detector \
    --extra-library build/pr132/reuse/libnODDShortStripBarrelReuse.dylib \
    --manifest "build/pr132/$variant/reuse-manifest.json" \
    --baseline build/pr132/native-baseline-snapshot.json \
    --snapshot "build/pr132/native-$variant-snapshot.json" \
    --output "build/pr132/native-$variant.json"
done
zsh tools/material_recording_profile/build_native.sh \
  /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view \
  "$PWD/build/pr132/libNativeTiming.dylib"
software/env/run.sh python3 -B docs/validation/tracker-placement-reuse/run_comparison.py \
  --work build/pr132 --repeats 2 \
  --ddg4-library /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/lib/libDDG4.dylib
for variant in cache mother; do
  python3 -B docs/validation/tracker-placement-reuse/compare_geant4.py \
    build/pr132/matched-runs/baseline-1/geant4-sensors.json \
    "build/pr132/matched-runs/$variant-1/geant4-sensors.json" \
    --output "build/pr132/geant4-$variant.json"
done
python3 -B docs/validation/tracker-placement-reuse/curate_comparison.py \
  --work build/pr132 --output docs/validation/tracker-placement-reuse/comparison-results.json
python3 -B -m unittest discover -s docs/validation/tracker-placement-reuse -p 'test_*.py' -v
python3 -B -m unittest discover -s tools/tracker_dd4hep -p 'test_*.py' -v
```

The first generation/native checks may run concurrently when producing
correctness evidence. Finish all such work before the sequential matched timing
runner. Do not compare those concurrent check durations as timing observations.
The baseline-only snapshot command may run during the full baseline scan;
retain its `SNAPSHOT` status and the separate completed full report. The final evidence assembly must check their input identities.
Native overlap sampling and large snapshots require the local runtime and
regenerated geometry. Committed compact summaries permit review of reported
counts, phases and provenance; they do not replace those native checks.
