# Reproduce old/current sensitive hit profiles

The [result](../../../docs/validation/baseline-hit-comparison/README.md) defines
hits as distinct positive-length sensitive physical-volume crossings. Native
Geant4 touchables avoid the material recording's rounded-position ambiguity.
This does not generate digitized or reconstructed hits.

Run the `acts-spack` preflight, then use a fresh zsh on the verified node. The
commands use the same legacy/current factories and compact files as the material
comparison. Their complete hashes are retained in the result provenance. To
rebuild them, export/build the old source530080c and current source62f6056
separately using the [material comparison recipe](../material_baseline_comparison/README.md).
Keep the node-specific compatible ACTS355ea684 runtime and pybind11 ABI11 native
persistent adapter; no shared dependency changes are needed.

```sh
source software/env/truth_tracking.sh
hit_view=/Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view
hit_native=../nodd-pr109-geantinos/build/pr109-geantinos/native
hit_acts=../nodd-software-layout/software/submodules/acts

run_hit_case() {
  DYLD_INSERT_LIBRARIES="$hit_view/lib/libDDG4.dylib" \
  python -B software/running/nodd_geantino_recording.py \
    --compact "$2/tracker/tracker.xml" --factory-dir "$2" \
    --native-module-dir "$hit_native" --run-mode persistent \
    --events 1000 --tracks 100 --seed 228 \
    --hit-counter software/analysis/hit_baseline_comparison/HitCounter.C \
    --expected-sensors "$3" --hit-include "$hit_view/include" \
    --hit-include "$hit_view/include/Geant4" \
    --hit-include "$hit_acts/Examples/Algorithms/Geant4/include" \
    --no-material-output --output "build/hit-comparison/$1"
}
# Separate processes. Existing output directories are rejected, not overwritten.
run_hit_case old ../nodd-software-layout/build/dd4hep/detector 45646
run_hit_case current build/material-comparison/dd4hep/detector 46682
```

For the executed noninterference control, use the current arguments with
`--events 3`, a new `--output build/hit-comparison/current-observer-smoke`, and
omit `--no-material-output`. Compare with the first300 rays of the retained
current material-only scan:

```sh
hit_python="$PWD/../nodd-unrooted/software/build/unrooted-venv/bin/python"
hit_analysis=software/analysis/hit_baseline_comparison
hit_data=docs/validation/baseline-hit-comparison

"$hit_python" -B "$hit_analysis/check_observer.py" \
  --observed build/hit-comparison/current-observer-smoke/tracks.root \
  --reference build/material-comparison/geant4-current/tracks.root \
  --output "$hit_data/observer-noninterference.json"
"$hit_python" -B "$hit_analysis/reduce.py" \
  --old build/hit-comparison/old --current build/hit-comparison/current \
  --output "$hit_data/profiles.json"
"$hit_python" -B "$hit_analysis/plot.py" --data "$hit_data/profiles.json" \
  --output "$hit_data/figures"
"$hit_python" -B -m unittest discover -s "$hit_analysis" -p 'test_*.py' -v
```

The independent finite-box control uses fresh/verified native Gen3 sensor
geometry with the identical compact/factories. Export the old geometry in the
native environment; current native geometry is from the completed mapping:

```sh
DYLD_INSERT_LIBRARIES="$hit_view/lib/libDDG4.dylib" \
python -B software/analysis/gen3_material_mapping/export_geometry.py \
  --nodd-dir ../nodd-software-layout \
  --build-dir ../nodd-software-layout/build/dd4hep \
  --output build/hit-comparison/old-native-geometry.json
"$hit_python" -B "$hit_analysis/check_boxes.py" \
  --hits build/hit-comparison/old/hits.csv \
  --geometry build/hit-comparison/old-native-geometry.json --rays 256 \
  --output "$hit_data/old-box-control.json"
"$hit_python" -B "$hit_analysis/check_boxes.py" \
  --hits build/hit-comparison/current/hits.csv \
  --geometry build/material-comparison/agent-mapping/geometry/geometry.json \
  --rays 256 --output "$hit_data/current-box-control.json"
```

The plot environment is pinned by `software/analysis/requirements-unrooted.txt`,
unrooted0.1.0rc1 commit728465dce0c5cd5b876e67392e3858de6e982d05.
Only replotting/tests of retained summaries work without native payloads. The
observer keeps the original material stepping action and one immutable
Geant4 process/thread; it rejects missing/duplicate sensitive identities,
unexpected secondary tracks, incomplete ray/event counts or nonpositive inventory.
