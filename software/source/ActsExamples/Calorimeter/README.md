# Calorimeter EDM4hep I/O

Issue [#114](https://github.com/asalzburger/nodd/issues/114) restores the
PR #80 hit/cluster plumbing on `main`. This standalone CMake project consumes
an existing ACTS build at `355ea68493b326956756c9386d2fd9eaf9328568` and the
existing Spack EDM4hep/podio environment. It does not rebuild or inject into
ACTS, move detector/tracker paths, or use FastJet.

Activate the node-specific environment as required by
[the Spack workflow](../../../../skills/acts-spack/SKILL.md), then run:

```sh
cmake -S software/source/ActsExamples/Calorimeter \
  -B build/calorimeter-io -G Ninja \
  -DNODD_ACTS_SOURCE=/path/to/pristine/acts355ea684 \
  -DNODD_ACTS_BUILD=/path/to/existing/acts/build
cmake --build build/calorimeter-io --parallel 4
ctest --test-dir build/calorimeter-io --output-on-failure
```

CMake checks the exact source commit, tracked-source cleanliness and the
existing build's source path. It needs the existing `ActsCore`,
`ActsExamplesFramework` and `ActsExamplesIoPodio` libraries. No dependency
fetching, installation or shared-build mutation occurs.

The input converter expands EDM4hep contributions into native deposits using
an explicit cell-centre callback by default. `useHitPosition=true`, with an empty
callback, explicitly asserts that the file's SimCalorimeterHit positions are
cell centres in mm. It never uses contribution step positions, and rejects
nonfinite or inconsistent positions for repeated cell IDs. Hit output preserves 64-bit cell IDs, units
and deposited-energy-fraction truth links. Cluster output preserves supplied
hit relations and index-aligned double-time/uint64-seed sidecars. Existing
mapping, finiteness, relation and float-range checks remain enforced. Metadata
schema version 2 records collection names, geometry provenance, units and
explicit `unimplemented skeleton` status for both processing stages; retired
threshold, time-window and neighbour-algorithm settings are absent.

With collection names alone, `CalorimeterDigitizationAlgorithm` and
`CalorimeterClusteringAlgorithm` still throw `std::logic_error` and never emit
output. Issue #117 adds an explicitly selected silicon energy-response
PROTOTYPE; clustering remains unimplemented.

The `nodd_calorimeter_io_fixture` executable writes three synthetic events,
reads them through ActsExamples, supplies fixed test hits/clusters, writes
EDM4hep ROOT output and verifies the complete persistent relation chain and
metadata. Its fixed values exercise I/O contracts; they supply no detector
simulation, calibration or response measurement. The native converter suites
also test malformed input/provenance, mapping mismatches, empty collections,
overflow, metadata collision and partial-output rejection. The skeleton suite
checks explicit failure.

[Executed results and limits](../../../../docs/validation/issue114/README.md)
record the pinned source/build and exact commands. [Source attribution](../../NOTICE.md)
retains the imported MPL-2.0 notice. Geometry, real response, calibrated clusters,
jets, EDM extensions and a cell-ID service remain outside issue #114.

## Issue #117 silicon energy-response PROTOTYPE

[DES-044](../../../../docs/design/DES-044-calorimeter-digitization.md) remains
DRAFT. The optional response reuses `RealisticCaloDigiSilicon` and the complete
`RealisticCaloDigi::EnergyDigi` method from
`iLCSoft/MarlinReco@255967eb855ebbc8f75ebaac190b268b63332e8b`. The silicon
translation unit and extracted method are unchanged; preparation checks their
full source SHA-256 values. Framework registration is replaced by a small
adapter. Original code and adapter form the separate GPL-3.0 executable
`nodd_marlin_silicon_backend`. It exchanges one JSON batch per event through
temporary files with the MPL framework adapter; it is never linked into ACTS
or the MPL libraries. See the [source notice](../../NOTICE.md).

Initialize the pinned public source submodule, then configure from the repository root:

```sh
git submodule update --init -- software/submodules/MarlinReco
software/env/run.sh cmake -S software/source/ActsExamples/Calorimeter \
  -B build/calorimeter-io -G Ninja \
  -DNODD_ACTS_SOURCE=/path/to/pristine/acts355ea684 \
  -DNODD_ACTS_BUILD=/path/to/existing/acts/build \
  -DNODD_MARLINRECO_SOURCE="$PWD/software/submodules/MarlinReco"
software/env/run.sh cmake --build build/calorimeter-io --parallel 4
software/env/run.sh ctest --test-dir build/calorimeter-io --output-on-failure
```

Configuration performs no downloading or installation. CLHEP comes from the
existing environment. The optional test target is present only when the actual
upstream backend is built; a build without it supplies no silicon validation.

Select the prototype explicitly:

```cpp
ActsExamples::CalorimeterDigitizationAlgorithm::Config config{"deposits", "hits"};
ActsExamples::SiliconDigitizationConfig silicon;
silicon.executable = "/absolute/path/to/nodd_marlin_silicon_backend";
silicon.mipEnergy = measuredMipEnergy;  // ACTS energy units; mandatory input
config.silicon = silicon;
```

`pairEnergyEv=3.6`, `noiseMip=0`, `dynamicRangeMip=2500` and
`thresholdMip=0.5` are upstream software defaults, not validated nODD detector
parameters. `mipEnergy` has no numerical default; obtain it from an independent
muon calibration sample matched to sensor thickness and geometry. The response
uses original silicon pair Poisson statistics, conversion to MIPs, electronics
clipping before Gaussian noise, and a strict `response > threshold` cut. Pair
statistics deliberately retain upstream's overestimated Poisson variance rather
than silently introducing a Fano model. Output cell energy is MIPs multiplied
by the configured MIP deposit energy: it is a deposit-equivalent scale, not an
incident-shower calibration or sampling-fraction correction.

The native adapter groups positive deposits by cell, keeps full uint64 IDs and
input indices, and retains the native EDM's deposited-energy-weighted time.
There is no upstream Standard/ROC timing integration, pulse shape, ADC/ToA,
out-of-time pileup, radiation dependence, gain variation or dead-cell model in
this subset. These exclusions prevent a full Marlin event-processing equivalence
claim. Each event seeds a fresh CLHEP engine deterministically from `seed` and
the ACTS event number; cell IDs are sorted before response, independent of
thread scheduling. This seed convention does not reproduce Marlin's event seeder.

An empty `channels` vector selects sparse input-cell mode. It adds noise only
to cells present in deposits and cannot establish detector-wide noise occupancy.
Supply the complete `{cellId, position}` inventory to evaluate empty channels;
duplicate IDs, unknown deposited cells and inconsistent cell centres fail.
Zero-energy channels explicitly bypass the upstream positive-energy pair division
then use its unchanged electronics response. This is an adapter extension, not
the original sparse Marlin event loop. `runMarlinSilicon` exposes signed,
unsuppressed MIP values for RMS/threshold diagnostics. Persisted noise-only hits
require `EDM4hepCalorimeterOutputConverter::Config::allowNoiseOnlyHits=true`;
they have no fabricated truth link and a zero placeholder time. Default I/O
continues rejecting missing signal provenance.

Tests exercise deterministic original-kernel MIP/range controls, 200000
noise-only values against Gaussian mean/RMS and one-sided threshold rates,
Poisson variance, strict selection, truth, empty-channel inventory and converter
failure paths. Those are software tests, not muon MIP-peak or shower validation.
Comparing the helper with itself is not an independent original-framework
reference comparison. [Issue #117 validation](../../../../docs/validation/issue117/validation-plan.md)
states the remaining original-Marlin/Key4hep and real-particle gates.
