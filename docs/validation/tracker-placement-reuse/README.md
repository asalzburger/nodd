# Tracker repeated-placement investigation — issue #130

Follow-up: the authorized [PR132 comparison prototype](comparison.md) tests the
cache and real-mother controls below. This initial investigation and its
`results.json` retain their original baseline-only identity.

Date: 2026-11-11. Input revision:
`3dab2346c4a08fd24898a7842906601884708a7d`.
Scope: characterization of the maintained **DRAFT / PROTOTYPE** DES-025 tracker,
including the DES-043 short-strip integration. No detector parameter, factory,
readout, material, reconstruction configuration or approval state changes.

The tracker has credible reuse opportunities. A comparable initialization
speedup to [PR129](https://github.com/asalzburger/nodd/pull/129) has **not** been
demonstrated: this investigation measures the unchanged baseline and identifies
the controlled experiments needed to test that claim. In this diagnostic,
geometry closure/voxelization takes about **187 s**, versus **25 s** for DDG4
mapping. Grouping physical daughters is therefore worth testing against closure,
as well as the mapping cost that motivated PR129.

## What carries over from PR129

**FACT, repository evidence:** the [ECAL report](../siw-real-wedge-default/README.md)
records an ECAL-only DDG4 volume-manager map build of 3,953.8 s before and
23.0 s after real reusable wedge mothers, for 531,936 sensitive paths. These
are historical measurements, not tracker measurements or whole-job timings.
`prototypes/calorimeter/SiWWedgeEnvelope.h` builds mothers with the enclosing
material and preserves instance IDs on their outer placements. The earlier
ECAL already reused assembly templates; see
`prototypes/calorimeter/BarrelCalorimeter.cpp` and the
[startup investigation](../../../logs/codex/SESSION-2026-11-10-ddg4-startup-profile.md).

**INFERENCE:** sharing solids or assemblies can reduce construction and memory
without eliminating the assembly-imprint path search that motivated PR129.
Real mothers could reduce flattened fanout, but add transport boundaries and
require containment, material and identifier proofs. None of the ECAL timing
ratio should be assigned to the tracker without a matched experiment.
Factory-side caching also leaves parsing of the repeated XML in place; reducing
that input duplication is a separate frontend representation change.

## Factory audit

SoftEng assignment I130-SE01 independently inspected the full input revision,
read-only. It found no module/stave/petal template cache in these factories.
The long-strip `groups` map groups placements; it does not cache templates.

| Family | Current representation | Candidate experiment |
| --- | --- | --- |
| Pixel barrel | Fresh stave/module assemblies; fresh module leaves | Share strict module recipes, then study a real module/stave mother |
| Pixel endcaps | Fresh disc/module assemblies and passive parts | Share single/quad recipes and compatible repeated disc parts |
| Short-strip barrel | Fresh module/stave assemblies and per-piece solids/volumes | Share module recipes as a control; study real module/stave mothers |
| Short-strip endcaps | Fresh module/petal/disc assemblies and pieces | Share module/petal recipes after retaining local face transforms |
| Long strips | Absolute piece placements in grouping assemblies | Cache matching leaves first; local module/stave/petal reconstruction is larger work |

Source locators at the input revision:
`detector/src/PixelComponents.cpp:51–145`, `PixelBarrel.cpp:18–45`,
`PixelEndcap.cpp:10–34`, `PixelEndcapParts.cpp:21–50`, `PixelServices.cpp:7–16`;
`prototypes/short_strip_barrel/ShortStripBarrel.cpp:31–74`,
`prototypes/short_strip_endcap/ShortStripEndcap.cpp:24–53`,
`prototypes/long_strip_barrel/LongStrip.cpp:11–13`.
These factories are incorporated by `detector/CMakeLists.txt`; historical
standalone-only comments do not describe the current combined entry point.

## Measurements and interpretation

The compact results and provenance are retained in `results.json`. Generated
compacts, full inventories, native phase logs and the one-event output stay
under ignored `build/issue130/`. The probe uses the fresh task-local factory
build, not a pre-existing installed nODD binary.

The exact local recipe screen of the fresh combined compact gives:

| System | Module instances | Strict local recipe classes |
| --- | ---: | ---: |
| Pixel barrel (1) | 3,050 | 3,050 |
| Pixel endcap, each sign (2/3) | 1,308 | 152 |
| Short-strip barrel (4) | 8,064 | 1 |

**FACT, generated compact evidence:** all 8,064 short-strip barrel modules have
the same local recipe even with descendant sensor IDs retained. This makes
them the clearest first cache control. Pixel-barrel patch IDs vary within
modules; 3,050 strict classes is not evidence of 3,050 different physical shapes.

The successful map stage resolved all **46,682 sensitive paths in about 25 s**.
The pre-run native inventory found 617,019 Geant4 logical volumes and 604,000
direct world daughters, consistent with extensive assembly flattening. This is
an opportunity to test hierarchy changes, not a prediction of their benefit.
The complete first-run diagnostic and phase data are retained in `results.json`.

| Observable in the single instrumented run | Wall time [s], rounded |
| --- | ---: |
| XML parsing, two observed calls | 89 |
| DD4hep → Geant4 converter | 15 |
| DDG4 sensitive-path mapping | 25 |
| Geant4 `Initialize`, inclusive | 42 |
| Initial cut-table update | 30 |
| First geometry closure / voxelization | 187 |
| First `RunInitialization`, inclusive | 308 |
| One native event-manager processing interval | 0.1 |
| Complete subprocess, including inventory/JIT/output and teardown | 553 |

These intervals have different boundaries and some nest; **do not sum them**.
The probe exited successfully, observed exactly one native event-processing
interval and checked the 46,682-path count. The 22 existing tracker tests and
three new measurement/recipe controls passed. This is construction/count and
execution evidence, not a full sensitive-ID, material or response validation.

**INFERENCE:** the maintained tracker does not reproduce the stock ECAL's
multi-thousand-second mapping interval in this observation. Its absolute map
time is already near PR129's optimized ECAL map time, for a different path count
and detector. This does not establish a normalized detector comparison, rule out
a tracker gain, or imply similar gains for total initialization.

A baseline alone cannot resolve
the effect of caching or real mothers. The historical
[material-recording study](../material-recording-profile/README.md) also identified
recurring Geant4 cut-table scans in ACTS's per-event `BeamOn(1)` lifecycle. That
is a separate cost from DDG4 map construction; its dated counts/timings do not
describe the current DES-043 geometry.
Here the initial update is measured once; recurring cost in the current ACTS
per-event lifecycle was not measured. Closure is the largest individually
measured placement-related interval in this run. The remaining inclusive
initialization time also contains physics-table work and other setup.

`recipe_counts.py` counts exact local XML recipes only for explicitly supported
pixel and short-strip barrel module forms. It excludes names and enumerated
outer instance/pose fields, retaining every descendant identifier, cut,
material, sensitivity and local transform. Numeric strings are not rounded.
It is a conservative repetition diagnostic, not a verified cache key or a
complete count of physically equivalent structures. Unsupported factory forms
remain outside this count. Pixel patch IDs can prevent strict sharing even
when dimensions match; changing their placement level needs a separate ID proof.

## Bounded next prototype and acceptance evidence

**NODD DESIGN CHOICE, proposed and unsigned:** start with the short-strip barrel,
whose local module structure is explicit. Keep the current compact and factories
as control. Build isolated alternatives: (A) strict module/leaf caching with
unchanged assembly structure; (B) the same caching plus a proven real mother.
Compare A/control and B/A separately. No candidate is wired into the maintained
detector by this task. Human review must choose whether to commission it.
Assess A primarily for construction/object-count cost and B for closure,
flattened fanout and mapping; retain adverse timing results as well as gains.

Before a real-mother prototype, assign SysArch the finite envelope and sibling
service-interface assessment. Use the actual enclosing material and preserve
regions/cuts; a guessed Air/Vacuum box can replace physical material or enclose
unrelated services. No new physical interface is introduced in this investigation.

For both alternatives:

- Preserve all **46,682 sensitive planes**, signed axes, bounds, centers,
  material, segmentation and packed IDs, including both long-strip faces.
  Preserve a per-instance DetElement tree for ACTS even when logical volumes share.
- Introduce an explicit instance-to-template provenance map. The existing
  `tools/tracker_dd4hep/validate.py` keys expectations and contact/window probes
  by logical volume name; template sharing requires equivalent expanded-path/ID
  checks. Do not disable those checks to accommodate renamed shared leaves.
- Check full ROOT overlaps/containment at the existing tolerance, dimensions,
  component/material inventory, all native DD4hep and Geant4 sensor IDs/transforms,
  material rays through supports/services and boundaries, ACTS conversion and
  navigation, and representative transport. New same-material boundaries require
  a response study before claiming full simulation equivalence.
- Time export, DD4hep construction, conversion, DDG4 mapping, geometry closure,
  cuts and full startup separately in fresh matched processes. Repeat runs
  sequentially on the same node/build with fixed physics/cuts/threads; report
  ranges and memory. Test repeated ACTS `BeamOn(1)` separately from DDSim startup.

This is a proposed software experiment, not engineering sign-off, detector
acceptance or a performance prediction.

## Reproduce the baseline

Run the acts-spack preflight first. Its historical registry fingerprints were
stale on this run; current imports, package versions and dataset presence were
checked separately. The setup emits sandbox host-detection warnings; no shared
installation or machine configuration is modified.

```sh
python3 /Users/salzburg/.codex/skills/acts-spack/scripts/preflight.py
python3 -B tools/tracker_dd4hep/export.py --output build/issue130/baseline
software/env/run.sh cmake -S . -B build/issue130/tracker -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
software/env/run.sh cmake --build build/issue130/tracker --parallel 3 --target \
  Components_nODDPixelBarrel Components_nODDBeamPipe \
  Components_nODDShortStripBarrel Components_nODDShortStripEndcap Components_nODDLongStrip
zsh tools/material_recording_profile/build_native.sh \
  /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view \
  "$PWD/build/issue130/libNativeTiming.dylib"
software/env/run.sh python3 -B docs/validation/tracker-placement-reuse/probe.py \
  build/issue130/baseline/tracker.xml build/issue130/tracker/detector \
  build/issue130/probe-2 --native-timing build/issue130/libNativeTiming.dylib \
  --ddg4-library /Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view/lib/libDDG4.dylib \
  --expected-sensors 46682
python3 -B docs/validation/tracker-placement-reuse/recipe_counts.py \
  build/issue130/baseline/tracker.xml > build/issue130/recipe-counts.json
python3 -B -m unittest discover -s docs/validation/tracker-placement-reuse -p 'test_*.py' -v
python3 -B -m unittest discover -s tools/tracker_dd4hep -p 'test_*.py' -v
```

The native interposition helper is macOS-specific. Static cut-couple reuse is
explicitly disabled. DDSim uses one geantino event, origin, +x direction,
10 GeV, seed 130001, one thread, FTFP_BERT and 0.7 mm range cut. That event
forces first-run initialization; it is not a tracker response/acceptance test.
These are probe test choices, not tracker requirements. DDG4 is preloaded before
the timing helper; preserve that order, interpreter and loaded binaries in A/B.
Native timer intervals are inclusive and may nest; do not sum them. Total wall
includes interpreter, inventory JIT/readout and output overhead. Mapping time
uses timestamped DDG4 begin/end log records and includes log delivery latency.
This is one instrumented diagnostic observation, with no measured run-to-run
dispersion or timing uncertainty. Repository export tests were active during
early startup; other shared-host workload was not measured. No timing acceptance
threshold is selected. The probe checks sensitive-path totals, not complete
per-sensor IDs/transforms or simulation-response equivalence. The native
inventory is captured after kernel initialization and before the first run;
its then-empty cut-couple table is not a claim that the event runs without cuts.

Checks from committed summaries: inspect source/count/phase claims and run the
parser controls. Native construction, inventories and startup reproduction need
the local runtime and regenerated compact; full logs and event files are not
committed. No new external scientific source or detector parameter is introduced;
provenance consists of the pinned repository inputs, runtime checks and hashes.
