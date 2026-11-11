# Issue 131 — 100-electron benchmark after PR129

This is timing and storage characterization of the existing **PROTOTYPE**
Si–W ECAL in LAYOUT-001, at source revision
`3dab2346c4a08fd24898a7842906601884708a7d` (the PR129 merge).
[Issue #131](https://github.com/asalzburger/nodd/issues/131) requests another
100-event electron sample after that merge, with no tracker or magnetic field.
The retained [earlier pilot record](../../../logs/codex/SESSION-2026-11-10-siw-ecal-compute-pilot.md)
provides the otherwise unspecified beam settings. No detector parameters,
materials, readouts or production configuration are changed by this benchmark.
DES-030, DES-031 and the [PR129 implementation evidence](../siw-real-wedge-default/README.md)
retain their existing approval boundaries.

The sample contains 25 single-electron events at each of η = 0.50, 1.45,
2.00 and 3.00, all at φ = 0.123 rad, nominal pT = 50 GeV and vertex (0,0,0).
These are benchmark inputs inherited from the previous pilot, not new detector
requirements. Momentum magnitudes are approximately 56.38, 112.44, 188.11 and
503.38 GeV; the six-significant-figure native gun rounding is checked on readback.
Only barrel system 8 and endcap system 9 are retained from a fresh maintained
LAYOUT-001 export, including their local passive hardware. The beam pipe and
tracker are omitted. HCAL, FCAL and muon systems are absent from this export.
The native initialization audit checks zero magnetic field and the existing
5 mm sensitive-silicon maximum charged step. FTFP_BERT, a 0.7 mm production
range cut, one thread and raw EDM4hep output match the earlier pilot.

## Measurements

All **100 persisted electrons pass readback**, with no zero-hit events.
The native audit confirms zero magnetic field, both ECAL sensitive roles,
the 5 mm step policy and 0.7 mm range cuts. Effective per-group RNG seeds
are 220100–220103 with `MixMaxRng`; both requested seed pairs and native
pre-event state hashes are retained in [results.json](results.json).

- **Initialization: 205.629 s (3.43 min)** from DDSim launch to first event.
  Launch to first `/beamOn` was 167.460 s; initialization also includes
  38.169 s of first-run setup before the first event.
- **Event-loop time: 1664.774 s / 100 = 16.64774 s/electron.**
- **Total process wall: 1899.076 s (31.65 min)**, or
  18.99076 s/electron with this process startup and shutdown amortized over 100 events.
  Child process CPU was 1890.169 s; observed child peak RSS was
  1.881 GiB (the launcher parent is excluded).
- **Output: 625,810,088 bytes (625.810 MB) total; 6.25810 MB/event**
  (5.968 MiB/event). Sizes are whole-file means over 25 saved
  primaries per file. MB = 10⁶ bytes; MiB = 2²⁰ bytes.

| η | Events | Nominal momentum (GeV/c) | Event loop (s/electron) | ROOT file mean (MB/event) |
| ---: | ---: | ---: | ---: | ---: |
| 0.50 | 25 | 56.38 | 4.741 | 1.692 |
| 1.45 | 25 | 112.44 | 7.664 | 3.271 |
| 2.00 | 25 | 188.11 | 15.801 | 5.680 |
| 3.00 | 25 | 503.38 | 38.385 | 14.389 |

The output is **podio EDM4hep in a ROOT `TTree`**, with observed file-header
compression algorithm ID 1 (ZLIB), level 1. It contains event headers,
`edm4hep::MCParticleCollection` truth, `edm4hep::SimCalorimeterHitCollection`
barrel/endcap hits and their contributions; digitization and reconstruction are
not run. The four-direction average weights every group equally. The nominal
momentum increases with eta at fixed pT, so the individual rows are necessary
when using these results for a different sample mix.

The node was `acts-mac-studio-01.cern.ch`, macOS 27.0.1 arm64, using Python
3.14.5, DD4hep/DDG4 1.38, Geant4 11.4.3, ROOT 6.40.04, EDM4hep 1.1.1 and
podio 1.8. Full Spack package identities, setup/lock fingerprints, configuration,
factory and recipe hashes, raw-file hashes and the actual transport settings
are in the compact result. All 12 Geant4 datasets reported installed both in
preflight re-verification and the post-run presence check. No shared software
was installed or changed.

These are observed post-merge timings inside the task sandbox. The older
pilot supplies the sample definition; this is not a controlled before/after
throughput comparison or a measurement of an eta-uniform physics sample.

## Reproduce

Run in this checkout on the verified node after the
[acts-spack preflight](../../../skills/acts-spack/SKILL.md). A registry warning
requires runtime re-verification, not a dependency update. Generated geometry,
all event files, full transport logs and build products remain local in ignored
`build/issue131/` storage. Choose a fresh `run` directory on a repeat invocation;
the runner refuses to overwrite existing evidence.

```sh
python3 skills/acts-spack/scripts/preflight.py
software/env/run.sh python3 -B software/env/doctor.py
python3 -B tools/calorimeter_baselines/export.py --layout LAYOUT-001 --output build/issue131/layout001
software/env/run.sh cmake -S prototypes/calorimeter -B build/issue131/calo -G Ninja -DCMAKE_BUILD_TYPE=Release
software/env/run.sh cmake --build build/issue131/calo --target Components_nODDCalorimeterPrototype --parallel 3
software/env/run.sh python3 -B docs/validation/issue131/run_pilot.py \
  build/issue131/run build/issue131/layout001 \
  build/issue131/calo/libnODDCalorimeterPrototype.dylib \
  software/analysis/calorimeter_digitization/nodd_transport.py
software/env/run.sh python3 -B docs/validation/issue131/audit_pilot.py build/issue131/run
```

The macOS library suffix is shown. The runner timestamps the unbuffered DDSim
stdout/stderr with a monotonic wall clock; event-message timestamps are retained
to 1 ms. Initialization is child launch through the first event-initialization
message, including Python, geometry, native audit compilation/execution and
first-run physics setup, and excluding Spack activation, export and compilation. Event-loop time runs from each group's
first event-initialization message through its finished-run message. `/beamOn`
brackets separately capture run setup. Total process wall includes final output
closure and shutdown. Output size is the sum of four closed compressed ROOT
files divided by the 100 saved primaries; it includes file metadata, truth,
secondary particles, hit contributions and calorimeter hits.

[run_pilot.py](run_pilot.py) records source, package, configuration, factory and
recipe identities; the native pre-group RNG engine/state is also recorded.
[audit_pilot.py](audit_pilot.py) reads every saved event,
checks counts, event order, primary species, vertex, kinematics, hit IDs and
positive finite hit energies, and verifies the actual TTree event counts and
compression settings. It produces the compact `results.json` locally. Only this
aggregate summary is copied to this directory; it contains no event-level data.
The full ROOT files are required to repeat the readback and hash checks.

The standard-library controls run without native software or event data:

```sh
python3 -B -m unittest discover -s docs/validation/issue131 -p 'test_*.py' -v
python3 -B -m unittest discover -s tools/calorimeter_baselines -p 'test_*.py' -v
```

The measurement runs inside the scheduled task sandbox. Host load and scheduling
conditions are not measured or isolated. One process and one azimuth provide
no uncertainty on repeated startup timing,
concurrent-worker scaling or other detector configurations. File-size means
include four-file overhead and are specific to the persisted output content and
compression. This is raw transport/I/O characterization; it does not establish
shower equivalence, calibrated response, reconstruction performance, engineering
sign-off or detector acceptance.
