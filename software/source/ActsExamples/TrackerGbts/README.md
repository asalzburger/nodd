# Native GBTS geometry adapter (DES-041 PROTOTYPE)

This sidecar connects nODD Gen-3 pixel space points to the existing ACTS Core
`GbtsGeometry`, `GraphBasedTrackSeeder` and `GbtsTrackingFilter`. Graph building,
cellular automaton, filtering and seed extraction execute in the linked ACTS
Core library. The thin framework adaptation is attributed to ACTS355ea684's
`GraphBasedSeedingAlgorithm.cpp` under MPL2.0 in the source. It removes that
example's ITk volume exclusions, layer ranges and mapping-file assumptions.
No ITk geometry, connector table, custom seeder or truth trajectory input is used.

Build in the verified environment, against the **matching** installed ACTS source:

```sh
source software/env/truth_tracking.sh
cmake -S software/source/ActsExamples/TrackerGbts \
  -B build/tracker-reconstruction/native-gbts -G Ninja \
  -DNODD_ACTS_SOURCE=/path/to/matching/acts355ea684 \
  -DNODD_ACTS_BUILD=/path/to/existing/acts/build \
  -DPython_EXECUTABLE="$(command -v python)" \
  -Dpybind11_DIR=/path/to/installed/pybind11-3.0.4/share/cmake/pybind11
cmake --build build/tracker-reconstruction/native-gbts --parallel 4
```

CMake checks source revision355ea684 and pybind11 3.0.4; the source asserts
internals ABI11. The current shared view can expose newer incompatible headers.
Pass the already installed matching package explicitly; do not alter the shared
view or remove the guard. No ACTS rebuild/install or DD4hep/G4 source is required.
Record actual source/header/module/library fingerprints with each campaign.

`software/analysis/tracker_reconstruction/gbts.py` provides:

- `prepare(native_geometry_report, directory, settings)` writes sorted complete
  sensor mapping, physical layer extents, connections, configuration and hashes.
  It requires the current balanced46250-sensor report, mapping12410pixels onto
  four barrel and twenty signed endcap layers. Stable disk10 lies between2 and3
  in physical station order.
- `schedule(sequencer, acts, geometry, directory, settings, level)` checks the
  prepared file hashes/configuration and schedules `nodd_gbts.GbtsSeeding`.
  Input defaults to measured pixel `spacepoints`, output to `seeds`. Every point
  must carry exactly one source link matching a mapped pixel. Long-strip1D
  measurements are deliberately excluded from these pixel space points.
- `algorithm.statistics()` returns actual event, point, per-layer node and
  native produced/retained/capped seed counts. The default cap0 is unlimited.
  A positive cap chooses descending native quality, preserving ties' order.
- `json.loads(algorithm.effective_configuration_json())` records all effective
  native finder/filter defaults and configured overrides, not only supplied keys.

Settings expose the exact ACTS C++ members under `seed_finder` and
`tracking_filter`; unknown names fail. `b_field_T` is converted to native ACTS
Tesla in C++; lengths use mm, momenta GeV. `z0_range_mm`, finder `minZ0/maxZ0`
and ROI must agree. Cluster-width cuts and strip connection mode are forbidden
for this Gaussian pixel configuration. The remaining initial native defaults
are study controls whose performance must be measured and tuned independently.

The176 broad connections cover every outward barrel pair, same-endcap outward
|z| pair, and barrel-to-disk pair. Native GBTS derives compatible eta-bin pairs.
The topology is valid because every pixel disk is axially beyond the barrel;
preparation rejects an input violating that condition. Connections are outer
`src` to inner `dst`, with no cross-endcap edges. No simulated sample trains
these geometry-derived links. Actual holes and module acceptance remain the
simulation's responsibility.

Controls:

```sh
python3 -B -m unittest software/analysis/tracker_reconstruction/test_gbts.py -v
# After prepare() has created a directory from a real native geometry report:
source software/env/truth_tracking.sh
python -B software/source/ActsExamples/TrackerGbts/test_native.py \
  --module-dir build/tracker-reconstruction/native-gbts \
  --config-dir build/tracker-reconstruction/gbts-smoke \
  --output build/tracker-reconstruction/gbts-smoke/native-smoke.json
```

The native smoke covers synthetic helices at pT1/5/10/100GeV, eta0/±2/±3.5,
both charges. `_test_points` exists only for this helper and does not initialize
or replace pipeline seeds. It verifies native algorithm integration; it is not
an efficiency/fake-rate or detector response measurement. Full Fatras/Gaussian
reconstruction and independent scoring belong to the campaign runner.
