#!/bin/zsh
# Build the pinned factory locally against the selected existing dependency view.
set -eu
runtime=${1:A}
output=${2:A}
"$runtime/software/env/run.sh" cmake \
  -S "$runtime/software/submodules/OpenDataDetector" -B "$output" \
  -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo
"$runtime/software/env/run.sh" cmake --build "$output" --parallel 2
