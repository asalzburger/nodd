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
an explicit cell-centre callback. Hit output preserves 64-bit cell IDs, units
and deposited-energy-fraction truth links. Cluster output preserves supplied
hit relations and index-aligned double-time/uint64-seed sidecars. Existing
mapping, finiteness, relation and float-range checks remain enforced. Metadata
schema version 2 records collection names, geometry provenance, units and
explicit `unimplemented skeleton` status for both processing stages; retired
threshold, time-window and neighbour-algorithm settings are absent.

`CalorimeterDigitizationAlgorithm` and `CalorimeterClusteringAlgorithm` expose
collection-name configuration and data handles. Their `execute()` methods
throw `std::logic_error` and never emit output. Physical digitization and
clustering are follow-up work. They cannot be used as successful empty-event
producers.

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
