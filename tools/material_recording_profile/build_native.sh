#!/bin/zsh
set -eu
view=$1
output=$2
source_dir=${0:A:h}
clang++ -std=c++20 -O2 -g -DNDEBUG -fvisibility-inlines-hidden -dynamiclib "$source_dir/native_timing.cpp" \
  -I"$view/include" -I"$view/include/Geant4" -I"$view/include/root" \
  -L"$view/lib" -L"$view/lib/root" \
  -Wl,-rpath,"$view/lib" -Wl,-rpath,"$view/lib/root" \
  -undefined dynamic_lookup -lCore -o "$output"
