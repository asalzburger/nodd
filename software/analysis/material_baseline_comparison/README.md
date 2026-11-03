# Baseline material comparison

The [result](../../../docs/validation/baseline-material-comparison/README.md)
compares the legacy0.5mm recording with current DES043/PR110 geometry, using
the PR112 palette. Native ACTS mapping is described in
[README_mapping.md](README_mapping.md). This is a material characterization,
without detector acceptance or tracking-performance qualification.

## Native build and recording

Follow `acts-spack` preflight. These are node-specific commands using the existing
ACTS355ea684 runtime. Run from this checkout in a fresh zsh; use new output
directories for repeated runs. No shared dependency installation is needed.

```sh
source software/env/truth_tracking.sh
material_runtime="$PWD/../nodd-software-layout"
material_out="$PWD/build/material-comparison"
material_view=/Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view
material_native="$material_out/recording-native"

cmake -S . -B "$material_out/dd4hep" -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_TESTING=OFF
cmake --build "$material_out/dd4hep" --parallel 4 --target \
  nODDPixelBarrel nODDBeamPipe nODDShortStripBarrel nODDShortStripEndcap nODDLongStrip
cmake --build "$material_out/dd4hep" --parallel 2 --target \
  detector/libnODDPixelBarrel.components detector/libnODDBeamPipe.components \
  detector/libnODDShortStripBarrel.components detector/libnODDShortStripEndcap.components \
  detector/libnODDLongStrip.components
python3 -B tools/tracker_dd4hep/export.py \
  --output "$material_out/dd4hep/detector/tracker"

cmake -S software/source/ActsExamples/MaterialRecording \
  -B "$material_native" -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DNODD_ACTS_SOURCE="$material_runtime/software/submodules/acts" \
  -DNODD_ACTS_BUILD="$material_runtime/build/acts" \
  -DPython_EXECUTABLE="$material_runtime/build/pyvenv/bin/python" \
  -Dpybind11_DIR=/Users/salzburg/Documents/work/externals/spack/opt/spack/__spack_path_placeholder__/__spack_path_placeholder__/__spack_path_plac/darwin-aarch64/py-pybind11-3.0.4-6zp63vmktd7ady6kjaecv6tc2m5s6qcn/share/cmake/pybind11
cmake --build "$material_native" --parallel 2

DYLD_INSERT_LIBRARIES="$material_view/lib/libDDG4.dylib" \
python -B software/running/nodd_geantino_recording.py \
  --compact "$material_out/dd4hep/detector/tracker/tracker.xml" \
  --factory-dir "$material_out/dd4hep/detector" \
  --native-module-dir "$material_native" --run-mode persistent \
  --events 1000 --tracks 100 --seed 228 --output "$material_out/geant4-current"
```

The executed campaign reused the identical native module from
`../nodd-pr109-geantinos/build/pr109-geantinos/native`. Its source and driver
are retained here unchanged. The producer's original steering revision is
e9548326e424f968cf9cd27d73588b6a17655eed; the geometry source is
62f6056395e0dfee0c7985cf24e88dc9919c4e2d. Exact compact/material/factory
hashes bind the actual geometry, rather than inferring it from a filename.
One persistent MaterialPhysicsList run processes1000 events, with unchanged
native per-event seeding and stepping; no shared ACTS patch is required.

## Classification and Geant4 boundary audit

The ordinary TGeo classifier retains its strict density gate. For this compact
it reports149 graphite/titanium CSG disagreements and exits1. Keep that result.
The subsequent native audit performs seven strict interior Geant4 lookups for
each failed step, checks recorded density/X0/L0, unique DD4hep logical-volume
name/material/sensitivity, and binds every label to the input hashes. No
navigation tolerance or physical material is changed.

```sh
material_factories=(
  --factory "$material_out/dd4hep/detector/libnODDBeamPipe.dylib"
  --factory "$material_out/dd4hep/detector/libnODDPixelBarrel.dylib"
  --factory "$material_out/dd4hep/detector/libnODDShortStripBarrel.dylib"
  --factory "$material_out/dd4hep/detector/libnODDShortStripEndcap.dylib"
  --factory "$material_out/dd4hep/detector/libnODDLongStrip.dylib"
)
# For the retained compact this diagnostic command exits1; inspect its report.
DYLD_INSERT_LIBRARIES="$material_view/lib/libDDG4.dylib" \
python -B software/analysis/material_profiles/categorize.py \
  --input "$material_out/geant4-current/tracks.root" \
  --compact "$material_out/dd4hep/detector/tracker/tracker.xml" \
  "${material_factories[@]}" --eta-max 4 \
  --output "$material_out/classify-current-all-diagnostics"

DYLD_INSERT_LIBRARIES="$material_view/lib/libDDG4.dylib" \
python -B software/analysis/material_baseline_comparison/audit_geant4.py \
  --recorder software/running/nodd_geantino_recording.py \
  --native-module-dir "$material_native" \
  --compact "$material_out/dd4hep/detector/tracker/tracker.xml" \
  --factory-dir "$material_out/dd4hep/detector" \
  --geant4-include "$material_view/include/Geant4" \
  --recording "$material_out/geant4-current/tracks.root" \
  --diagnostics "$material_out/classify-current-all-diagnostics/classification-diagnostics.csv" \
  --output "$material_out/geant4-final-audit"

DYLD_INSERT_LIBRARIES="$material_view/lib/libDDG4.dylib" \
python -B software/analysis/material_profiles/categorize.py \
  --input "$material_out/geant4-current/tracks.root" \
  --compact "$material_out/dd4hep/detector/tracker/tracker.xml" \
  "${material_factories[@]}" --eta-max 4 \
  --geant4-audit "$material_out/geant4-final-audit/provenance.json" \
  --output "$material_out/classify-current-certified"
```

The bounded audit only supports the observed passive short-strip graphite
pieces. Other failures remain errors and require investigation. The
Geant4/TGeo CSG discrepancy itself remains open, despite resolved assignment.

## Reduction and figures

Use the existing unrooted0.1.0rc1 environment (source commit728465dce0c5cd5b876e67392e3858de6e982d05).
The recipe below reads every validation ray and independently verifies the
native Geant4 profiles against every categorized ray. All rays, including zero
contributions to a component, enter every component mean.

```sh
material_python="$PWD/../nodd-unrooted/software/build/unrooted-venv/bin/python"
material_data=docs/validation/baseline-material-comparison
material_analysis=software/analysis/material_baseline_comparison

"$material_python" -B software/analysis/material_profiles/export_profiles.py \
  --input "$material_out/classify-current-certified/profiles.root" \
  --expected-tracks 100000 --output "$material_data/current-geant4.json"
"$material_python" -B "$material_analysis/reduce_validation.py" \
  --input "$material_out/agent-mapping/validation/material_validation.root" \
  --output "$material_data/current-acts.json"
"$material_python" -B "$material_analysis/control.py" \
  --pr109 ../storage/nodd-tracker-strixel-2_0.root \
  --current "$material_out/geant4-current/tracks.root" \
  --output "$material_data/pr109-control.json"
"$material_python" -B "$material_analysis/compare.py" \
  --old-truth docs/validation/geantino-material-profiles/profiles.json \
  --old-acts docs/validation/gen3-material-map-run/validation-profiles.json \
  --current-truth "$material_data/current-geant4.json" \
  --current-acts "$material_data/current-acts.json" \
  --output "$material_data/comparison.json"
"$material_python" -B "$material_analysis/plot.py" \
  --data "$material_data/comparison.json" --output "$material_data/figures"
"$material_python" -B -m unittest discover -s "$material_analysis" -p 'test_*.py' -v
```

Replotting and pure gates use committed binwise data without the full native
dataset. Regenerating classification, material mapping, native reload and
per-ray conservation checks requires the local ROOT files or a regenerated
campaign. Keep full ROOT/XML/native-geometry exports and bulky logs ignored.
The retained compressed map contains8650 averaged material bins, not events.
