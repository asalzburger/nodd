#!/bin/zsh
# Run through the existing runtime without invoking its install/copy helpers.
set -eu
runtime=${1:A}
detector=$2
output=${3:A}
shift 3
source_dir=${0:A:h}
mkdir -p "${output:h}"
case "$detector" in
  nodd)
    factory_dir="$runtime/build/dd4hep/detector"
    compact="$factory_dir/tracker/tracker.xml"
    factories=()
    for factory in nODDPixelBarrel nODDBeamPipe nODDShortStripBarrel nODDShortStripEndcap nODDLongStrip; do
      factories+=(--factory "$factory_dir/lib$factory.dylib")
    done
    ;;
  odd)
    compact="$output/odd-tracker.xml"
    python3 "$source_dir/prepare_odd.py" \
      "$runtime/software/submodules/OpenDataDetector/xml" "$compact"
    factories=(--factory "${ODD_FACTORY:-/Users/salzburg/Documents/work/installed/acts-nodd/lib/libOpenDataDetector.dylib}")
    ;;
  *) print -u2 'detector must be odd or nodd'; exit 2 ;;
esac
native_env=()
if [[ -n ${NATIVE_TIMING_LIBRARY:-} ]]; then
  view=${DEPENDENCY_VIEW:-/Users/salzburg/Documents/work/externals/ci-dependencies/.spack-env/view}
  native_env+=("DYLD_INSERT_LIBRARIES=$NATIVE_TIMING_LIBRARY:$view/lib/libDDG4.dylib" \
               "MATERIAL_NATIVE_TIMING=$output.native.jsonl" \
               "MATERIAL_ENERGY_CUT_CLIENT=$NATIVE_TIMING_LIBRARY.energy-client.dylib")
fi
exec "$runtime/software/env/run.sh" /bin/zsh "$runtime/software/env/acts-run.sh" \
  "$runtime/build/acts" /usr/bin/env "${native_env[@]}" "$runtime/build/pyvenv/bin/python" \
  "$source_dir/run.py" --runtime "$runtime" --compact "$compact" \
  "${factories[@]}" --output "$output" --events 100 --tracks 100 --seed 228 "$@"
