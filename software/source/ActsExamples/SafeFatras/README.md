# Safe Fatras Bethe–Heitler evaluation

DES041 DRAFT / isolated PROTOTYPE. This sidecar addresses the observed
`std::exp(-u)` underflow in the pinned native Fatras Bethe–Heitler sampler.
No FPE check, mask, random draw, interaction, momentum cut or physics default is
changed. Human acceptance remains pending.

For binary64 round-to-nearest and `0 <= u < 2^-54`, `exp(-u)` rounds to 1
and `exp(-u)-1` is exactly `+0`. For `u > 40`,
`exp(-u) < exp(-40) < 2^-54`; therefore `exp(-u) - 1` rounds exactly to `-1`.
The sidecar directly uses those same rounded results. Tiny-argument libm
intermediates can underflow even when the final expression returns zero; the
initial large-only guard did not avoid that case. For all other values it
evaluates the original expression. Multiplication order remains
`abs(scaleFactor * particle.energy() * fraction)`. The original gamma draw and
four angular draws, in their original function-argument expression order, remain.
The inherited photon generator and particle update remain native ACTS.

Configure-time copies of the hash-pinned ACTS Fatras algorithm header/source
are written only into this sidecar's build directory and renamed
`ActsExamples::NoddSafeFatrasSimulation`. Its charged interaction list uses a
distinct `nodd::safe_fatras::SafeBetheHeitler` type; scattering, ionization,
selectors, neutral propagation, hit generation, per-event RNG spawning and
output ordering remain the pinned implementation. All module C++ symbols are
hidden except its Python initializer. No shared ACTS source/library is modified,
overridden or monkey-patched. The six upstream source hashes, generated algorithm
hashes and pybind ABI are exported by the module.
The algorithm instance and logger retain the original `FatrasSimulation` name.
Native random streams depend on the configured seed, absolute event number and
numeric algorithm slot. Integration adds exactly one simulation algorithm in the
original slot and preserves the preceding sequence and decorators.

The native Fatras object uses `-O2 -g -DNDEBUG -std=gnu++20 -fPIC
-D_GNU_SOURCE` and `ROOT_CORE_THREAD_TBB`, without LTO or special Eigen macros.
Configuration reads the actual object block from the existing `build.ninja`,
checks its numerical flags/macros and compiler, and applies those flags to this
module. Pybind LTO extras are disabled. Hidden module visibility remains the
isolation mechanism. Exported metadata records the native flags and object-block
hash. This removes the first sidecar's unintentional O0/NDEBUG mismatch; exact
full-event regression remains a separate required check.

After the node-specific acts-spack preflight, activate the existing matching
environment in the same shell. Use the existing pybind11 **3.0.4** CMake package
(ABI11), not an unrelated newer package:

```sh
source software/env/truth_tracking.sh
cmake -S software/source/ActsExamples/SafeFatras \
  -B build/tracker-reconstruction-species/native-safe-fatras \
  -DNODD_ACTS_SOURCE="$PWD/../nodd-software-layout/software/submodules/acts" \
  -DNODD_ACTS_BUILD="$PWD/../nodd-software-layout/build/acts" \
  -DPython_EXECUTABLE="$PWD/../nodd-software-layout/build/pyvenv/bin/python" \
  -Dpybind11_DIR="<existing pybind11-3.0.4 CMake directory>"
cmake --build build/tracker-reconstruction-species/native-safe-fatras --parallel 2
ctest --test-dir build/tracker-reconstruction-species/native-safe-fatras --output-on-failure
```

The configuration rejects mismatching ACTS revisions, all changed upstream
inputs, unexpected replacement anchors and a different pybind version. Numerical
tests stratify every positive finite binary64 exponent and threshold/extreme
values, compare rounded sampled losses bitwise, and compare original/safe parent
and photon states plus RNG state over thin/thick synthetic slabs. A native libm
underflow positive control covers both `u=1e-300` and `u=800`. Exponent-stratified
guarded hardware/ACTS FPE-monitor checks run with production-equivalent O2 flags
without a strict-FP pragma or option, and separately with strict FP enabled.
No global or function-local FENV pragma is added to production transport.
These controls do not replace full native campaign regression. The initial
module is retained under the ignored diagnostics before this replacement build.

Integration, after recording the exact amended source/config and binary hashes:

```python
import sys
sys.path.insert(0, "build/tracker-reconstruction-species/native-safe-fatras")
import acts.examples  # Register the matching IAlgorithm base and native types.
import nodd_safe_fatras
effective = nodd_safe_fatras.schedule(seq, geometry, field, rnd, level)
```

`schedule` adds the new algorithm and the same `particles` and
`particles_simulated_selected` aliases as native `addFatras`. Inputs/outputs are
`particles_generated`, `particles_simulated`, `simhits`. Returned JSON-compatible
metadata records actual native defaults, including all electromagnetic
interactions, `pMin = 0.5 GeV`, sensitive hits only, 1 m maximum step and 30 m path
limit. Scheduling rejects a changed floating-point rounding mode without changing
it. The caller must fingerprint this new module/source and retain existing
sequence FPE monitoring. This adapter does not repair the known Fatras electron
ionization approximation or certify electromagnetic-shower accuracy.
The helper's optional simulation writers are not requested in this benchmark;
no particle-selector, postselection or additional truth alias is introduced.
